"""Verify the documented broken fixture and reference without an AI provider."""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parent
FILES = {'package.json': ('starter/package.json', 'json'),
         'retry-after.mjs': ('starter/retry-after.mjs', 'javascript'),
         'retry-after.test.mjs': ('starter/retry-after.test.mjs', 'javascript'),
         'reference/retry-after.mjs': ('reference/retry-after.mjs', 'javascript')}


def run_tests(root):
    result = subprocess.run(['node', '--test', '--test-reporter=tap', 'retry-after.test.mjs'],
                            cwd=root, capture_output=True, text=True, timeout=30)
    counts = {key: int(re.search(r'^# ' + key + r' (\d+)$', result.stdout, re.M)[1])
              for key in ('tests', 'pass', 'fail')}
    return result.returncode, counts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--result', type=Path)
    args = parser.parse_args()
    article = ROOT / 'article.ko.md'
    if article.exists():
        text = article.read_text()
        for heading, (name, language) in FILES.items():
            blocks = re.findall(r'^### `' + re.escape(heading) + r'`\n\n```' + language + r'\n([\s\S]*?)\n```', text, re.M)
            assert len(blocks) == 1 and blocks[0] + '\n' == (ROOT / name).read_text(), heading
        assert '```text\n' + (ROOT / 'prompt.txt').read_text() + '```' in text
        image = ElementTree.parse(ROOT / 't3-code-flow-ko.svg').getroot()
        assert image.attrib['{http://www.w3.org/XML/1998/namespace}lang'] == 'ko'
    with tempfile.TemporaryDirectory(prefix='t3-code-example-') as directory:
        project = Path(directory)
        for path in (ROOT / 'starter').iterdir():
            shutil.copyfile(path, project / path.name)
        before = (project / 'retry-after.test.mjs').read_bytes()
        broken_status, broken = run_tests(project)
        assert broken_status != 0 and broken['tests'] == 19 and broken['fail'] > 0
        shutil.copyfile(ROOT / 'reference/retry-after.mjs', project / 'retry-after.mjs')
        fixed_status, fixed = run_tests(project)
        assert fixed_status == 0 and fixed == {'tests': 19, 'pass': 19, 'fail': 0}
        assert (project / 'retry-after.test.mjs').read_bytes() == before
    report = {'passed': True, 'node': subprocess.check_output(['node', '--version'], text=True).strip(),
              'starter': broken, 'reference': fixed, 'testFileUnchanged': True,
              'aiProviderInvoked': False, 't3AgentTurnExecuted': False, 'networkRequestsInExample': 0}
    if args.result: args.result.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
