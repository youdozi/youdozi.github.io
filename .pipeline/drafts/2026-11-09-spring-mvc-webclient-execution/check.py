"""Compare embedded sources, then run the actual Servlet/Netty contracts in both modes."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parent
FILES = {'settings.gradle': 'groovy', 'build.gradle': 'groovy',
         'src/main/resources/application.yml': 'yaml',
         'src/main/java/example/DemoApplication.java': 'java', 'upstream.py': 'python'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--gradle', default='gradle')
    parser.add_argument('--jdk', type=Path, required=True)
    parser.add_argument('--result', type=Path)
    args = parser.parse_args()
    article = (ROOT / 'article.ko.md').read_text()
    for path, language in FILES.items():
        pattern = r'^### `' + re.escape(path) + r'`\n\n```' + language + r'\n([\s\S]*?)\n```'
        blocks = re.findall(pattern, article, re.M)
        assert len(blocks) == 1 and blocks[0] + '\n' == (ROOT / path).read_text(), path
    image = ElementTree.parse(ROOT / 'mvc-webclient-flow-ko.svg').getroot()
    assert image.attrib['{http://www.w3.org/XML/1998/namespace}lang'] == 'ko'
    assert './mvc-webclient-flow-ko.svg' in article
    env = {**os.environ, 'JAVA_HOME': str(args.jdk)}
    rows = []
    for virtual in (False, True):
        command = [args.gradle, '-p', str(ROOT), '--no-daemon', 'clean', 'test',
                   '-Pvirtual=' + str(virtual).lower()]
        result = subprocess.run(command, env=env, text=True, capture_output=True, timeout=300)
        if result.returncode:
            print(result.stdout, result.stderr)
            result.check_returncode()
        suites = [ElementTree.parse(p).getroot() for p in (ROOT / 'build/test-results/test').glob('TEST-*.xml')]
        tests = sum(int(s.get('tests', '0')) for s in suites)
        unsuccessful = sum(int(s.get(key, '0')) for s in suites for key in ('failures', 'errors', 'skipped'))
        assert tests == 8 and unsuccessful == 0, (virtual, tests, unsuccessful)
        text = '\n'.join(s.findtext('system-out', '') for s in suites)
        observations = [json.loads(line.removeprefix('OBSERVATION ')) for line in text.splitlines() if line.startswith('OBSERVATION ')]
        assert len(observations) == 2
        assert {r['mode'] for r in observations} == {'block', 'async'}
        assert all(r['requestVirtual'] == virtual and r['callbackNonBlocking'] and not r['callbackVirtual'] for r in observations)
        rows.append({'virtual': virtual, 'tests': tests, 'unsuccessful': unsuccessful, 'observations': observations})
    summary = {'embeddedFiles': len(FILES), 'totalTests': 16, 'modes': rows}
    if args.result:
        args.result.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        args.result.write_text(json.dumps(summary, ensure_ascii=False, indent=2))
        args.result.chmod(0o600)
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
