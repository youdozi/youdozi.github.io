#!/usr/bin/env python3
"""Execute paired source-derived RestClient/WebClient ZIP contracts on loopback HTTP."""
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from build_example_archives import catalog, extract_example

KEY = '2026-10-31-webclient-restclient-comparison'
COMMAND = 'gradle --no-daemon --console=plain -q clean run'
EXPECTED = '''before-rest-terminal=0
rest=hello
before-subscribe=1
web=hello
after-first-subscribe=2
web-again=hello
after-second-subscribe=3
rest-404=404
web-404=404
rest-503=503
web-503=503
requests=7'''


def main():
    if not shutil.which('gradle'):
        raise SystemExit('JDK 17 and Gradle 8.4 are required.')
    editions = []
    for language in ('en', 'ko'):
        article = Path(f'src/content/posts/{language}/{KEY}.md').read_text()
        files = re.findall(r'^### `([^`]+)`\n\n```(?:java|groovy)\n([\s\S]*?)\n```', article, re.M)
        assert len(files) == len(dict(files)) == 3, 'Three unique project files required'
        editions.append(dict(files))
        assert re.findall(r'^```sh\n([\s\S]*?)\n```', article, re.M) == [COMMAND]
        assert re.findall(r'^```text\n([\s\S]*?)\n```', article, re.M) == [EXPECTED]
    assert editions[0] == editions[1], 'Full paired project sources must match'
    assert next(item for item in catalog() if item['key'] == KEY)['commands'] == COMMAND
    env = os.environ.copy()
    if sys.platform == 'darwin':
        env['JAVA_HOME'] = subprocess.check_output(['/usr/libexec/java_home', '-v', '17'], text=True).strip()
    print('JDK:', subprocess.check_output([str(Path(env['JAVA_HOME']) / 'bin/java') if env.get('JAVA_HOME') else 'java', '-version'], stderr=subprocess.STDOUT, text=True).splitlines()[0], flush=True)
    with tempfile.TemporaryDirectory(prefix='youdozi-http-clients-') as directory:
        root = Path(directory)
        extract_example(KEY, root, editions[0])
        result = subprocess.run(COMMAND.split(), cwd=root, env=env, check=True,
                                text=True, capture_output=True, timeout=240)
        assert result.stdout.strip() == EXPECTED, result.stdout + result.stderr
        print(EXPECTED)
        print('[ok] Exact ZIP project executed: seven loopback HTTP requests, terminal/subscription timing and both 404/503 error contracts. No performance or timeout test.')


if __name__ == '__main__':
    main()
