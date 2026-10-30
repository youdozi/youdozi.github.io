#!/usr/bin/env python3
"""Execute the exact paired timeout/retry article ZIP and check all JUnit results."""
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from xml.etree import ElementTree
from build_example_archives import extract_example

KEY = '2026-10-30-webclient-timeout-retry'


def main():
    if not shutil.which('gradle'):
        raise SystemExit('JDK 17 and Gradle 8.4 are required.')
    editions, commands = [], []
    for language in ('en', 'ko'):
        article = Path(f'src/content/posts/{language}/{KEY}.md').read_text()
        pairs = re.findall(r'^### `([^`]+)`\n\n```(?:java|groovy)\n([\s\S]*?)\n```', article, re.M)
        assert len(pairs) == 4 and len(dict(pairs)) == 4, 'Four unique project files required'
        editions.append(dict(pairs))
        commands.append(re.findall(r'^```sh\n([\s\S]*?)\n```', article, re.M))
    assert editions[0] == editions[1], 'EN/KO implementation and tests must match'
    assert commands[0] == commands[1] == ['gradle --no-daemon clean test']
    env = os.environ.copy()
    if sys.platform == 'darwin':
        env['JAVA_HOME'] = subprocess.check_output(['/usr/libexec/java_home', '-v', '17'], text=True).strip()
    with tempfile.TemporaryDirectory(prefix='youdozi-webclient-retry-') as directory:
        root = Path(directory)
        extract_example(KEY, root, editions[0])
        subprocess.run(['gradle', '--no-daemon', 'clean', 'test'], cwd=root, env=env, check=True, timeout=240)
        suites = [ElementTree.parse(path).getroot() for path in (root / 'build/test-results/test').glob('TEST-*.xml')]
        tests = sum(int(suite.get('tests', '0')) for suite in suites)
        unsuccessful = sum(int(suite.get(key, '0')) for suite in suites for key in ('failures', 'errors', 'skipped'))
        assert tests == 9 and not unsuccessful, f'Expected nine passing tests, got {tests} and {unsuccessful} unsuccessful'
        names = [case.get('name') for suite in suites for case in suite.findall('testcase')]
        print('[ok] Nine published timeout/retry tests executed from paired ZIP members: ' + ', '.join(sorted(names)))


if __name__ == '__main__':
    main()
