"""Run the article against an ephemeral Redis with no persistent volume."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import time
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parent
IMAGE = 'redis:8.2.1-alpine@sha256:987c376c727652f99625c7d205a1cba3cb2c53b92b0b62aade2bd48ee1593232'
FILES = {'settings.gradle': 'groovy', 'build.gradle': 'groovy',
         'src/main/resources/application.yml': 'yaml', 'src/main/resources/rate-limit.lua': 'lua',
         'src/main/java/example/RedisRateLimiter.java': 'java',
         'src/main/java/example/RateLimitApplication.java': 'java'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--gradle', default='gradle')
    parser.add_argument('--jdk', type=Path, required=True)
    parser.add_argument('--result', type=Path)
    args = parser.parse_args()
    article = ROOT / 'article.ko.md'
    if article.exists():
        text = article.read_text()
        for name, language in FILES.items():
            pattern = r'^### `' + re.escape(name) + r'`\n\n```' + language + r'\n([\s\S]*?)\n```'
            blocks = re.findall(pattern, text, re.M)
            assert len(blocks) == 1 and blocks[0] + '\n' == (ROOT / name).read_text(), name
        image = ElementTree.parse(ROOT / 'redis-rate-limit-ko.svg').getroot()
        assert image.attrib['{http://www.w3.org/XML/1998/namespace}lang'] == 'ko'
    container = subprocess.check_output(['docker', 'run', '--rm', '-d', '-p', '127.0.0.1::6379',
                                         IMAGE, 'redis-server', '--save', '', '--appendonly', 'no'], text=True).strip()
    try:
        for _ in range(50):
            ready = subprocess.run(['docker', 'exec', container, 'redis-cli', 'ping'], capture_output=True, text=True)
            if ready.returncode == 0 and ready.stdout.strip() == 'PONG': break
            time.sleep(0.1)
        else: raise RuntimeError('Redis did not become ready')
        address = subprocess.check_output(['docker', 'port', container, '6379/tcp'], text=True).strip()
        port = int(address.rsplit(':', 1)[1])
        command = [args.gradle, '-p', str(ROOT), '--no-daemon', 'clean', 'test', f'-PredisPort={port}']
        subprocess.run(command, env={**os.environ, 'JAVA_HOME': str(args.jdk)}, check=True)
        suites = [ElementTree.parse(path).getroot() for path in (ROOT / 'build/test-results/test').glob('TEST-*.xml')]
        tests = sum(int(s.get('tests', '0')) for s in suites)
        assert tests == 11 and not any(int(s.get(k, '0')) for s in suites for k in ('failures', 'errors', 'skipped'))
        result = {'passed': True, 'cases': tests, 'redisImage': IMAGE, 'jdk': str(args.jdk),
                  'concurrencyCase': {'callers': 40, 'accepted': 3}, 'clusterFailoverTested': False,
                  'unresponsiveEndpointTested': True, 'primaryFailureTested': False, 'throughputMeasured': False}
        if args.result: args.result.write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps(result))
    finally:
        subprocess.run(['docker', 'rm', '-f', container], check=True, stdout=subprocess.DEVNULL)


if __name__ == '__main__':
    main()
