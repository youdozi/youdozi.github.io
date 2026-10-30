#!/usr/bin/env python3
"""Run source-derived offline comparisons and JSSE inventories, never live targets."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

from build_example_archives import catalog, extract_example

GITLAB = '2026-10-30-gitlab2shell-cve-2026-110264'
JDK = '2026-10-30-jdk-emudhra-truststore'


def paired(key, language):
    editions, commands = [], []
    for locale in ('en', 'ko'):
        raw = Path(f'src/content/posts/{locale}/{key}.md').read_text()
        pairs = re.findall(r'^### `([^`]+)`\n\n```' + language + r'\n([\s\S]*?)\n```', raw, re.M)
        assert len(pairs) == 1, 'One exact source project expected'
        editions.append(dict(pairs))
        commands.append(re.findall(r'^```sh\n([\s\S]*?)\n```', raw, re.M))
    assert editions[0] == editions[1] and commands[0] == commands[1]
    assert commands[0] == [next(row for row in catalog() if row['key'] == key)['commands']]
    return editions[0], commands[0][0]


def execute(args, root, env=None, check=True):
    return subprocess.run(args, cwd=root, env=env, check=check, text=True,
                          capture_output=True, timeout=60)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--java-home', type=Path)
    args = parser.parse_args()
    if args.java_home:
        java_home = args.java_home.resolve()
    elif sys.platform == 'darwin':
        java_home = Path(subprocess.check_output(['/usr/libexec/java_home', '-v', '17'], text=True).strip())
    else:
        javac = shutil.which('javac')
        if not javac: raise SystemExit('JDK 17 or later required')
        java_home = Path(javac).resolve().parents[1]
    java, javac, keytool = [str(java_home / 'bin' / name) for name in ['java', 'javac', 'keytool']]
    env = os.environ.copy(); env['JAVA_HOME'] = str(java_home)
    env['PATH'] = str(java_home / 'bin') + os.pathsep + env.get('PATH', '')
    cases = []
    with tempfile.TemporaryDirectory(prefix='youdozi-gitlab-jdk-') as directory:
        root = Path(directory)
        release = root / 'release'; release.mkdir()
        files, shell = paired(GITLAB, 'python'); extract_example(GITLAB, release, files)

        def version(name, value, status, state, baseline):
            result = execute([sys.executable, 'release-threshold.py', value], release, check=False)
            assert result.returncode == status and not result.stderr, (name, result)
            assert result.stdout == (f'release-threshold={state}\nbaseline={baseline}\n'
                                     'deployment-and-release-provenance=not-verified\n'), (name, result)
            cases.append(name)

        # Independent published thresholds, not imported from the article program.
        for branch, fix in [('18.11', 13), ('19.0', 10), ('19.1', 9), ('19.2', 9), ('19.3', 6), ('19.4', 3), ('19.5', 1)]:
            baseline = f'{branch}.{fix}'
            version(branch + '-below', f'{branch}.{fix-1}', 1, 'below', baseline)
            for suffix in ['', '-ee.0', '-ce']:
                version(branch + '-at' + suffix, baseline + suffix, 0, 'met', baseline)
            version(branch + '-later-numeric-only', f'{branch}.{fix+1}', 0, 'met', baseline)
        for value in ['7.0.0', '18.10.9']:
            version(value, value, 1, 'below', 'upgrade-path-required')
        for value in ['6.9.9', '19.6.0', '20.0.0']:
            version(value, value, 2, 'outside-table', 'not-covered')
        invalid = ['', '19.05.1', '019.5.1', '19.5', '19.5.1-rc1', '19.5.1+build',
                   '19.5.1-ee.0 trailing', '１９.5.1', '19.5.1000', '9' * 200, '19.5.1\n', '$(false)']
        for index, value in enumerate(invalid):
            result = execute([sys.executable, 'release-threshold.py', value], release, check=False)
            assert result.returncode == 2 and not result.stdout and result.stderr.startswith('usage:'), result
            cases.append('invalid-version-' + str(index))
        for index, extra in enumerate([[], ['19.5.1', 'extra'], ['19.5.1', 'extra', 'more']]):
            result = execute([sys.executable, 'release-threshold.py', *extra], release, check=False)
            assert result.returncode == 2 and not result.stdout and result.stderr.startswith('usage:'), result
            cases.append('argument-count-' + str(index))
        result = execute(['sh', '-c', shell], release, env)
        assert result.stdout.startswith('release-threshold=met\nbaseline=19.5.1\n') and not result.stderr
        cases.append('literal-python-shell-command')

        trust = root / 'trust'; trust.mkdir()
        files, shell = paired(JDK, 'java'); extract_example(JDK, trust, files)
        default = execute(['sh', '-c', shell], trust, env)
        assert 'configuredTrustStore=<default JSSE lookup>\n' in default.stdout
        assert 'assessment=inventory-only; no validation verdict\n' in default.stdout
        assert re.search(r'^acceptedIssuers=\d+$', default.stdout, re.M)
        cases.append('literal-java-compile-and-default-inventory')
        password = 'fixture-only-password'
        fixtures = trust / 'fixture stores'; fixtures.mkdir()
        fingerprints = []
        for i, name in enumerate(['emSign Fixture CA', 'AAA Certificate Services Fixture', 'Unrelated Fixture CA']):
            keys = fixtures / f'key-{i}.p12'; cert = fixtures / f'ca-{i}.der'
            execute([keytool, '-genkeypair', '-alias', 'ca', '-dname', f'CN={name},O=Example',
                     '-keyalg', 'RSA', '-keysize', '2048', '-validity', '2', '-ext', 'bc=ca:true',
                     '-storetype', 'PKCS12', '-keystore', str(keys), '-storepass', password, '-keypass', password], trust)
            execute([keytool, '-exportcert', '-alias', 'ca', '-keystore', str(keys), '-storepass', password, '-file', str(cert)], trust)
            fingerprints.append(hashlib.sha256(cert.read_bytes()).hexdigest().upper())
            for name_of_store in ['mixed.p12', *(['unrelated.p12'] if i == 2 else [])]:
                execute([keytool, '-importcert', '-noprompt', '-alias', f'ca-{i}', '-file', str(cert),
                         '-storetype', 'PKCS12', '-keystore', str(fixtures / name_of_store), '-storepass', password], trust)
        empty = fixtures / 'empty.p12'
        shutil.copyfile(fixtures / 'unrelated.p12', empty)
        execute([keytool, '-delete', '-alias', 'ca-2', '-keystore', str(empty), '-storepass', password], trust)

        def inventory(path, secret=password, check=True):
            return execute([java, f'-Djavax.net.ssl.trustStore={path}',
                            f'-Djavax.net.ssl.trustStorePassword={secret}', 'TrustInventory'], trust, env, check)

        mixed = inventory(fixtures / 'mixed.p12')
        assert 'acceptedIssuers=3\n' in mixed.stdout and 'nameMatches=2\n' in mixed.stdout
        found = re.findall(r'^candidate=.*\tSHA256=([A-F0-9]{64})$', mixed.stdout, re.M)
        assert sorted(found) == sorted(fingerprints[:2]) and password not in mixed.stdout
        assert 'assessment=inventory-only; no validation verdict\n' in mixed.stdout
        cases.append('synthetic-ca-names-and-independent-der-fingerprints')
        unrelated = inventory(fixtures / 'unrelated.p12')
        assert 'acceptedIssuers=1\n' in unrelated.stdout and 'nameMatches=0\n' in unrelated.stdout
        assert 'assessment=inventory-only; no validation verdict\n' in unrelated.stdout
        cases.append('unrelated-ca-is-not-a-protection-verdict')
        empty_result = inventory(empty)
        assert 'acceptedIssuers=0\n' in empty_result.stdout and 'nameMatches=0\n' in empty_result.stdout
        assert 'assessment=inventory-only; no validation verdict\n' in empty_result.stdout
        cases.append('empty-store-retains-no-verdict')
        # Missing-path behavior varies across providers/builds: fallback, empty or failure.
        missing = inventory(fixtures / 'does-not-exist.p12', check=False)
        if missing.returncode == 0:
            assert 'assessment=inventory-only; no validation verdict\n' in missing.stdout
            assert re.search(r'^acceptedIssuers=\d+$', missing.stdout, re.M)
        else:
            assert 'Exception' in missing.stderr and 'assessment=' not in missing.stdout
        assert password not in missing.stdout + missing.stderr
        cases.append('missing-explicit-store-is-not-a-protection-verdict')
        wrong = inventory(fixtures / 'mixed.p12', 'wrong-fixture-password', check=False)
        assert wrong.returncode != 0 and 'assessment=' not in wrong.stdout
        assert 'Exception' in wrong.stderr and 'wrong-fixture-password' not in wrong.stdout + wrong.stderr
        cases.append('wrong-password-fails-initialization')
        java_version = execute([java, '-version'], trust).stderr.splitlines()[0]
    print(json.dumps({'passed': True, 'cases': len(cases), 'names': cases, 'java': java_version,
                      'actualZIPCodeExecuted': True, 'networkTargets': 0,
                      'productionChanges': False, 'actualAffectedTLSChainsValidated': False}))


if __name__ == '__main__':
    main()
