"""Check the article sources and execute Bucket4j with deterministic time."""
import argparse
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import tempfile
import time
from urllib.request import urlopen
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parent
FILES = {'settings.gradle': 'groovy', 'build.gradle': 'groovy',
         'src/main/resources/application.yml': 'yaml',
         'src/main/java/example/BucketPolicy.java': 'java',
         'src/main/java/example/RateLimitApplication.java': 'java'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--jdk', type=Path, required=True)
    parser.add_argument('--gradle', default='gradle')
    parser.add_argument('--result', type=Path)
    args = parser.parse_args()
    text = (ROOT / 'article.ko.md').read_text()
    for name, language in FILES.items():
        pattern = r'^### `' + re.escape(name) + r'`\n\n```' + language + r'\n([\s\S]*?)\n```'
        blocks = re.findall(pattern, text, re.M)
        assert len(blocks) == 1 and blocks[0] + '\n' == (ROOT / name).read_text(), name
    image = ElementTree.parse(ROOT / 'bucket4j-flow-ko.svg').getroot()
    assert image.attrib['{http://www.w3.org/XML/1998/namespace}lang'] == 'ko'
    published = ROOT.parents[2] / 'src/content/posts/ko/2026-11-11-bucket4j-token-bucket.md'
    if published.exists():
        body = lambda value: value.split('---\n', 2)[2]
        assert body(published.read_text()) == body(text).replace('./bucket4j-flow-ko.svg', '/assets/img/architecture/bucket4j-flow-ko.svg'), 'Published body differs from draft'
        assert (ROOT.parents[2] / 'assets/img/architecture/bucket4j-flow-ko.svg').read_bytes() == (ROOT / 'bucket4j-flow-ko.svg').read_bytes(), 'Published diagram differs'
    env = {**os.environ, 'JAVA_HOME': str(args.jdk)}
    subprocess.run([args.gradle, '-p', str(ROOT), '--no-daemon', 'clean', 'test', 'installDist'],
                   env=env, check=True, timeout=300)
    suites = [ElementTree.parse(path).getroot() for path in (ROOT / 'build/test-results/test').glob('TEST-*.xml')]
    tests = sum(int(s.get('tests', '0')) for s in suites)
    assert tests == 10 and not any(int(s.get(k, '0')) for s in suites for k in ('failures', 'errors', 'skipped'))
    with tempfile.TemporaryFile(mode='w+') as log:
        app = subprocess.Popen([str(ROOT / 'build/install/bucket4j-token-bucket/bin/bucket4j-token-bucket'),
                                '--server.port=0'], env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                log.seek(0); output = log.read()
                match = re.search(r'Tomcat started on port (\d+)', output)
                if match and 'Started RateLimitApplication' in output: break
                if app.poll() is not None: raise RuntimeError(output)
                time.sleep(0.1)
            else: raise RuntimeError('Application did not start within 30 seconds')
            with urlopen(f'http://127.0.0.1:{match[1]}/demo', timeout=5) as response:
                assert response.status == 200 and response.read() == b'ok\n'
        finally:
            if app.poll() is None:
                os.killpg(app.pid, signal.SIGTERM)
                try: app.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(app.pid, signal.SIGKILL); app.wait(timeout=5)
    result = {'passed': True, 'bucket4j': '8.22.0', 'tests': tests, 'httpSmokeStatus': 200,
              'concurrentCalls': 40, 'allowedWithFrozenClock': 5, 'clockControlledTests': True,
              'mvcStatusTests': 'MockMvc', 'distributedRedisTested': False, 'throughputMeasured': False}
    if args.result: args.result.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
