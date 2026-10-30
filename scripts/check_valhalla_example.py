#!/usr/bin/env python3
"""Execute source-derived Valhalla ZIP code with a separate JDK 28 EA."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import tarfile
import tempfile

from build_example_archives import catalog, extract_example

KEY = '2026-10-31-project-valhalla-value-objects'
# Official jdk.java.net/28 Build 21 download checksums, checked 2026-10-31.
ARCHIVES = {
    ('Darwin', 'arm64'): ('macos-aarch64', 'cab7242cb132eb32c33f376817db91ca0c44f18d22633752f6f31d32a7714166'),
    ('Linux', 'x86_64'): ('linux-x64', 'b32bf773d02fff73d4a2da78cf590459879963b3dbffd18dcc9d6c6756ee4549'),
}
EXPECTED = [
    'record == false', 'record equals true', 'value == true', 'value equals true',
    'record identity true', 'value identity false', 'label == false',
    'label equals true', 'array slot null true', 'monitor IdentityException',
]


def execute(args, root, env=None):
    return subprocess.run(args, cwd=root, env=env, text=True, capture_output=True, timeout=60)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--jdk', type=Path, help='Existing JDK 28 home, without changing global configuration')
    group.add_argument('--download-jdk', action='store_true', help='Download checksum-pinned official EA into a temporary directory')
    args = parser.parse_args()
    editions, commands = [], []
    for language in ('en', 'ko'):
        source = Path(f'src/content/posts/{language}/{KEY}.md').read_text()
        code = re.findall(r'^### `ValhallaExample.java`\n\n```java\n([\s\S]*?)\n```', source, re.M)
        shell = re.findall(r'^```sh\n([\s\S]*?)\n```', source, re.M)
        output = re.findall(r'^```text\n([\s\S]*?)\n```', source, re.M)
        assert len(code) == len(shell) == len(output) == 1
        assert output[0].splitlines() == EXPECTED
        editions.append(code[0]); commands.append(shell[0])
    assert editions[0] == editions[1] and commands[0] == commands[1]
    assert commands[0] == next(r for r in catalog() if r['key'] == KEY)['commands']
    with tempfile.TemporaryDirectory(prefix='youdozi-valhalla-') as directory:
        root = Path(directory)
        download = None
        if args.download_jdk:
            target = ARCHIVES.get((platform.system(), platform.machine()))
            if not target: raise SystemExit('Pinned downloads support macOS arm64 and Linux x86_64; otherwise pass --jdk.')
            name, expected = target
            url = f'https://download.java.net/java/early_access/jdk28/21/GPL/openjdk-28-ea+21_{name}_bin.tar.gz'
            archive = root / 'jdk.tar.gz'
            subprocess.run(['curl', '--fail', '--location', '--silent', '--show-error', '--max-time', '180',
                            '--output', str(archive), url], check=True, timeout=190)
            digest = hashlib.sha256()
            with archive.open('rb') as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b''): digest.update(block)
            assert digest.hexdigest() == expected, 'JDK download checksum mismatch'
            unpacked = root / 'jdk'; unpacked.mkdir()
            with tarfile.open(archive) as bundle: bundle.extractall(unpacked, filter='data')
            homes = [p.parent.parent for p in unpacked.rglob('bin/javac')]
            assert len(homes) == 1
            jdk = homes[0]
            download = {'url': url, 'sha256': expected}
        else:
            jdk = args.jdk.resolve()
        java, javac = [str(jdk / 'bin' / name) for name in ['java', 'javac']]
        version = execute([java, '--version'], root)
        assert version.returncode == 0 and re.match(r'openjdk 28(?:-ea|[ .])', version.stdout), version
        env = os.environ.copy(); env['JAVA_HOME'] = str(jdk)
        env['PATH'] = str(jdk / 'bin') + os.pathsep + env.get('PATH', '')
        project = root / 'example'; project.mkdir()
        extract_example(KEY, project, {'ValhallaExample.java': editions[0]})
        result = execute(['sh', '-c', commands[0]], project, env)
        assert result.returncode == 0 and result.stdout.splitlines() == EXPECTED, result
        cases = ['literal-compile-and-run', *EXPECTED]
        no_runtime_preview = execute([java, 'ValhallaExample'], project)
        assert no_runtime_preview.returncode != 0 and 'UnsupportedClassVersionError' in no_runtime_preview.stderr
        cases.append('runtime-preview-flag-required')
        rejected = root / 'rejected'; rejected.mkdir()
        no_compile_preview = execute([javac, '--release', '28', '-d', str(rejected), 'ValhallaExample.java'], project)
        assert no_compile_preview.returncode != 0 and not list(rejected.rglob('*.class'))
        cases.append('compile-preview-flag-required')
        failures = {
            'BadMonitor': 'class BadMonitor { void lock(ValhallaExample.ValuePoint p) { synchronized (p) {} } }',
            'BadMutation': 'value class BadMutation { int x; BadMutation() { x = 1; } void mutate() { x = 2; } }',
            'PrimitiveGeneric': 'class PrimitiveGeneric { java.util.List<int> values; }',
        }
        for name, text in failures.items():
            (project / f'{name}.java').write_text(text + '\n')
            result = execute([javac, '--enable-preview', '--release', '28', f'{name}.java'], project)
            assert result.returncode != 0 and not (project / f'{name}.class').exists(), (name, result)
            cases.append(name + '-rejected')
    print(json.dumps({'passed': True, 'cases': len(cases), 'names': cases,
                      'jdk': version.stdout.strip(), 'download': download,
                      'actualZIPCodeExecuted': True, 'performanceOrLayoutMeasured': False,
                      'programNetworkRequests': 0, 'globalJDKConfigurationChanged': False}))


if __name__ == '__main__':
    main()
