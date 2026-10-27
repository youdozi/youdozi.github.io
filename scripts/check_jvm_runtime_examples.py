#!/usr/bin/env python3
"""Extract and execute both editions' JDK 21 and fresh-schema Batch 5 examples."""
import argparse
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from xml.etree import ElementTree


def extract(slug, expected):
    editions = []
    for language in ('en', 'ko'):
        text = Path(f'src/content/posts/{language}/{slug}.md').read_text()
        blocks = re.findall(r'^### `([^`]+)`\n\n```(?:java|groovy)\n([\s\S]*?)\n```', text, re.M)
        files = dict(blocks)
        if set(files) != expected or len(blocks) != len(expected):
            raise SystemExit(f'{language}/{slug}: unexpected project files')
        editions.append(files)
    if editions[0] != editions[1]:
        raise SystemExit(f'{slug}: English and Korean code differs')
    return editions[0]


def java_home(major):
    if sys.platform == 'darwin':
        return subprocess.check_output(['/usr/libexec/java_home', '-v', str(major)], text=True).strip()
    home = os.environ.get(f'JDK{major}_HOME') or os.environ.get('JAVA_HOME')
    if not home:
        raise SystemExit(f'Set JDK{major}_HOME or JAVA_HOME to JDK {major}')
    return home


def run_jdk():
    files = extract('2023-09-20-jdk-21-release', {'Jdk21Example.java'})
    home = Path(java_home(21))
    java, javac = str(home / 'bin/java'), str(home / 'bin/javac')
    version = subprocess.check_output([java, '-version'], stderr=subprocess.STDOUT, text=True)
    if not re.search(r'version "21\.', version):
        raise SystemExit('JDK 21 is required for the JDK example')
    print('[environment]', version.splitlines()[0], flush=True)
    with tempfile.TemporaryDirectory(prefix='youdozi-jdk21-') as directory:
        source = Path(directory) / 'Jdk21Example.java'
        source.write_text(files['Jdk21Example.java'] + '\n')
        subprocess.run([javac, '--release', '21', '-d', directory, str(source)], check=True, timeout=45)
        result = subprocess.check_output([java, '-cp', directory, 'Jdk21Example'], text=True, timeout=30)
        assert result.splitlines() == ['ALPHA/gamma', '[gamma, beta, ALPHA]', 'point=2,3', 'missing', 'virtual=true'], result
        # A lower release must reject these language features/APIs; no preview flag is used.
        older = subprocess.run([javac, '--release', '17', '-d', directory, str(source)], capture_output=True, timeout=45)
        assert older.returncode != 0, 'This source unexpectedly compiled for Java 17'
    print('[ok] JDK 21: five output lines, no preview flags; Java 17 target rejected.', flush=True)


def run_batch():
    files = extract('2023-10-27-springbatch5-migration', {
        'settings.gradle', 'build.gradle', 'src/test/java/example/BatchRestartTest.java',
    })
    env = {**os.environ, 'JAVA_HOME': java_home(17)}
    version = subprocess.check_output(['gradle', '--version'], text=True, env=env, timeout=30)
    gradle = re.search(r'^Gradle (\S+)', version, re.M)
    jvm = re.search(r'^JVM:\s+(\S+)', version, re.M)
    if not gradle or gradle[1] != '8.4' or not jvm or not jvm[1].startswith('17.'):
        raise SystemExit('The Batch reproduction requires Gradle 8.4 on JDK 17')
    print(f'[environment] Gradle {gradle[1]}, JVM {jvm[1]}', flush=True)
    with tempfile.TemporaryDirectory(prefix='youdozi-batch5-') as directory:
        root = Path(directory)
        for name, code in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(code + '\n')
        subprocess.run(['gradle', '-p', directory, '--no-daemon', 'clean', 'test'], env=env, check=True, timeout=240)
        suites = [ElementTree.parse(p).getroot() for p in root.glob('build/test-results/test/TEST-*.xml')]
        tests = sum(int(s.get('tests', 0)) for s in suites)
        failures = sum(int(s.get(k, 0)) for s in suites for k in ('failures', 'errors', 'skipped'))
        assert tests == 3 and failures == 0, (tests, failures)
    print('[ok] Three fresh-schema H2 tests: typed persistence, completed-instance rejection, failed-step restart.', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--part', choices=('all', 'jdk', 'batch'), default='all')
    args = parser.parse_args()
    if args.part in ('all', 'batch'):
        run_batch()
    if args.part in ('all', 'jdk'):
        run_jdk()
