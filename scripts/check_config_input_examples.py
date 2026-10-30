#!/usr/bin/env python3
"""Execute article-derived YAML/command and Temurin metadata fixtures, offline."""
import copy
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

import yaml
from build_example_archives import extract_example


def extract(slug, expected):
    editions = []
    for language in ('en', 'ko'):
        text = Path(f'src/content/posts/{language}/{slug}.md').read_text()
        blocks = re.findall(r'^### `([^`]+)`\n\n```(?:python|sh|yaml)\n([\s\S]*?)\n```', text, re.M)
        files = dict(blocks)
        assert set(files) == expected and len(blocks) == len(expected), (language, slug)
        editions.append(files)
    assert editions[0] == editions[1], f'{slug}: language editions differ'
    return editions[0]


def main():
    assert yaml.__version__ == '6.0.3', 'Install scripts/requirements-config-examples.txt'
    files = extract('2021-07-27-parse-yaml', {'application.yml', 'read-port.py', 'run-with-port.sh'})
    files.update(extract('2023-10-10-temurin-jdk21-delay', {'select-temurin.py'}))
    yaml_cases = {
        'normal': ('server:\n  port: 8080\n', '8080'),
        'minimum': ('server: {port: 1}', '1'),
        'maximum': ('server: {port: 65535}', '65535'),
        'zero': ('server: {port: 0}', None),
        'negative': ('server: {port: -1}', None),
        'overflow': ('server: {port: 65536}', None),
        'string': ('server: {port: "8080"}', None),
        'bool': ('server: {port: true}', None),
        'implicit_bool': ('server: {port: on}', None),
        'float': ('server: {port: 8080.0}', None),
        'null_port': ('server: {port: null}', None),
        'port_list': ('server: {port: [8080]}', None),
        'missing_port': ('server: {}', None),
        'missing_server': ('other: 1', None),
        'server_sequence': ('server: [8080]', None),
        'root_sequence': ('[8080]', None),
        'empty': ('', None),
        'invalid': ('server: [', None),
        'multi_document': ('server: {port: 8080}\n---\nserver: {port: 9090}', None),
        'object_tag': ('!!python/object/apply:os.system ["touch SHOULD_NOT_EXIST"]', None),
        'shell_data': ('server: {port: "$(touch SHOULD_NOT_EXIST)"}', None),
    }
    with tempfile.TemporaryDirectory(prefix='youdozi-config-') as directory:
        root = Path(directory)
        extract_example('2021-07-27-parse-yaml',root,{name:text for name,text in files.items() if name!='select-temurin.py'})
        extract_example('2023-10-10-temurin-jdk21-delay',root,{'select-temurin.py':files['select-temurin.py']})

        def run(name, *args, env=None):
            command = ['sh', str(root / name)] if name.endswith('.sh') else [sys.executable, str(root / name)]
            return subprocess.run(command + list(args), cwd=root, env=env, text=True, capture_output=True, timeout=15)

        config = root / 'config with spaces.yml'
        for name, (text, expected) in yaml_cases.items():
            config.write_text(text)
            result = run('read-port.py', str(config))
            assert result.returncode == (0 if expected is not None else 2), (name, result)
            assert result.stdout == (expected + '\n' if expected is not None else ''), (name, result)
        assert not (root / 'SHOULD_NOT_EXIST').exists()
        # Test wrapper behavior independently of direct parser invocations.
        config.write_text('server: {port: 8080}')
        env = {**os.environ, 'PYTHON': sys.executable, 'SERVER_PORT': 'parent'}
        literal = 'two words $(touch SHOULD_NOT_EXIST)'
        child = 'import os,sys; print(os.environ["SERVER_PORT"]); print(sys.argv[1])'
        result = run('run-with-port.sh', str(config), sys.executable, '-c', child, literal, env=env)
        assert result.returncode == 0 and result.stdout.splitlines() == ['8080', literal], result
        assert env['SERVER_PORT'] == 'parent' and not (root / 'SHOULD_NOT_EXIST').exists()
        result = run('run-with-port.sh', str(config), sys.executable, '-c', 'raise SystemExit(37)', env=env)
        assert result.returncode == 37, result
        for bad in (str(root / 'missing.yml'), str(config)):
            config.write_text('server: {port: false}')
            result = run('run-with-port.sh', bad, sys.executable, '-c', 'open("COMMAND_RAN", "w").close()', env=env)
            assert result.returncode == 2 and not (root / 'COMMAND_RAN').exists(), result
        assert run('run-with-port.sh').returncode == 2
        assert run('read-port.py').returncode != 0

        valid = [{'binary': {'os': 'linux', 'architecture': 'x64', 'image_type': 'jdk', 'jvm_impl': 'hotspot', 'package': {
            'name': 'OpenJDK21-fixture.tar.gz', 'checksum': 'a' * 64,
            'link': 'https://github.com/adoptium/temurin21-binaries/releases/download/fixture/archive.tar.gz',
        }}, 'version': {'major': 21, 'semver': '21.0.1+12.0.LTS'}}]
        fixtures = [('valid', valid, True), ('empty', [], False), ('multiple', valid * 2, False),
                    ('object', {}, False), ('null_asset', [None], False), ('missing_fields', [{}], False)]
        mutations = [
            (('binary', 'os'), 'windows'), (('binary', 'architecture'), 'aarch64'),
            (('binary', 'image_type'), 'jre'), (('binary', 'jvm_impl'), 'openj9'),
            (('version', 'major'), 17), (('binary', 'package', 'checksum'), 'bad'),
            (('binary', 'package', 'link'), 'http://github.com/adoptium/temurin21-binaries/releases/download/f/a'),
            (('binary', 'package', 'link'), 'https://example.com/adoptium/temurin21-binaries/releases/download/f/a'),
            (('binary', 'package', 'link'), 'https://github.com/other/repo/releases/download/f/a'),
            (('binary', 'package', 'link'), 42),
        ]
        for keys, value in mutations:
            mutated = copy.deepcopy(valid)
            target = mutated[0]
            for key in keys[:-1]:
                target = target[key]
            target[keys[-1]] = value
            fixtures.append(('/'.join(keys) + '=' + str(value), mutated, False))
        metadata = root / 'assets.json'
        for name, data, success in fixtures:
            metadata.write_text(json.dumps(data))
            result = run('select-temurin.py', str(metadata))
            assert result.returncode == (0 if success else 2), (name, result)
            if success:
                assert json.loads(result.stdout)['sha256'] == 'a' * 64
            else:
                assert not result.stdout, (name, result)
        metadata.write_text('invalid JSON')
        assert run('select-temurin.py', str(metadata)).returncode == 2
        assert run('select-temurin.py', str(root / 'missing.json')).returncode == 2
    print(json.dumps({'yamlParserCases': len(yaml_cases), 'wrapperAndUsageCases': 6,
                      'temurinMetadataCases': len(fixtures) + 2, 'externalRequests': 0,
                      'binaryDownloads': 0, 'result': 'passed'}))


if __name__ == '__main__':
    main()
