#!/usr/bin/env python3
"""Run the source-derived JFR probe on JDK 21 or 25; never benchmark throughput."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from build_example_archives import catalog, extract_example

KEY = '2026-10-31-virtual-threads-jdk21-jdk25'


def execute(args, root, env=None, check=True):
    return subprocess.run(args, cwd=root, env=env, check=check, text=True,
                          capture_output=True, timeout=60)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jdk', type=Path, help='HotSpot JDK 21/25 home; defaults to JAVA_HOME or javac on PATH')
    args = parser.parse_args()
    jdk = args.jdk or (Path(os.environ['JAVA_HOME']) if os.environ.get('JAVA_HOME') else None)
    if not jdk:
        compiler = shutil.which('javac')
        if not compiler: raise SystemExit('JDK 21 or 25 with JFR required.')
        jdk = Path(compiler).resolve().parents[1]
    jdk = jdk.resolve()
    java, javac, jfr = [str(jdk / 'bin' / name) for name in ['java', 'javac', 'jfr']]
    version = execute([javac, '-version'], Path.cwd()).stdout.strip()
    match = re.match(r'javac (21|25)(?:[ .]|$)', version)
    if not match: raise SystemExit('Use JDK 21 or 25 for this recorded comparison.')
    major = int(match[1]); editions, commands = [], []
    for language in ('en', 'ko'):
        text = Path(f'src/content/posts/{language}/{KEY}.md').read_text()
        code = re.findall(r'^### `VirtualThreadProbe.java`\n\n```java\n([\s\S]*?)\n```', text, re.M)
        shell = re.findall(r'^```sh\n([\s\S]*?)\n```', text, re.M)
        output = re.findall(r'^```text\n([\s\S]*?)\n```', text, re.M)
        assert len(code) == len(shell) == 1 and len(output) == 2
        assert output[0].splitlines() == ['virtual=true', 'monitor-pinned-events=1', 'virtual=true', 'plain-pinned-events=0']
        assert output[1].splitlines() == ['virtual=true', 'monitor-pinned-events=0', 'virtual=true', 'plain-pinned-events=0']
        editions.append(code[0]); commands.append(shell[0])
    assert editions[0] == editions[1] and commands[0] == commands[1]
    assert '--enable-preview' not in commands[0]
    assert commands[0] == next(row for row in catalog() if row['key'] == KEY)['commands']
    env = os.environ.copy(); env['JAVA_HOME'] = str(jdk)
    env['PATH'] = str(jdk / 'bin') + os.pathsep + env.get('PATH', '')
    cases = []
    with tempfile.TemporaryDirectory(prefix='youdozi-virtual-thread-') as directory:
        root = Path(directory)
        extract_example(KEY, root, {'VirtualThreadProbe.java': editions[0]})
        result = execute(['sh', '-c', commands[0]], root, env)
        lines = result.stdout.splitlines()
        assert len(lines) == 4 and lines[0] == lines[2] == 'virtual=true' and not result.stderr, result
        observed = {}
        for mode, index in [('monitor', 1), ('plain', 3)]:
            matched = re.fullmatch(mode + r'-pinned-events=(\d+)', lines[index]); assert matched
            observed[mode] = int(matched[1])
        assert observed['plain'] == 0 and (observed['monitor'] >= 1 if major == 21 else observed['monitor'] == 0)
        cases.append('literal-commands-and-monitor-plain-observations')
        for mode in ['monitor', 'plain']:
            recording = root / (mode + '.jfr')
            assert recording.stat().st_size > 0
            report = execute([jfr, 'print', '--json', '--events', 'jdk.VirtualThreadPinned', recording.name], root)
            events = json.loads(report.stdout)['recording']['events']
            assert len(events) == observed[mode]
            assert all(e['type'] == 'jdk.VirtualThreadPinned' and e['values']['eventThread']['virtual'] for e in events)
            cases.append(mode + '-recording-independently-read-by-jfr-cli')
            before = hashlib.sha256(recording.read_bytes()).hexdigest()
            refused = execute([java, 'VirtualThreadProbe', mode], root, check=False)
            assert refused.returncode != 0 and 'recording already exists' in refused.stderr
            assert not refused.stdout and hashlib.sha256(recording.read_bytes()).hexdigest() == before
            cases.append(mode + '-existing-file-preserved')
        for number, invalid in enumerate([[], ['wrong'], ['monitor', 'extra']]):
            isolated = root / f'invalid-{number}'; isolated.mkdir()
            rejected = execute([java, '-cp', str(root), 'VirtualThreadProbe', *invalid], isolated, check=False)
            assert rejected.returncode != 0 and 'Usage: VirtualThreadProbe monitor|plain' in rejected.stderr
            assert not list(isolated.glob('*.jfr')) and not rejected.stdout
            cases.append('invalid-arguments-' + str(number))
        runtime = execute([java, '--version'], root).stdout.strip()
    print(json.dumps({'passed': True, 'cases': len(cases), 'names': cases, 'jdk': runtime,
                      'monitorPlainCounts': observed, 'actualZIPCodeExecuted': True,
                      'independentJFRCLIRead': True, 'previewFlags': False, 'networkRequests': 0,
                      'performanceMeasured': False, 'remainingNativePathsTested': False,
                      'globalJDKConfigurationChanged': False}))


if __name__ == '__main__':
    main()
