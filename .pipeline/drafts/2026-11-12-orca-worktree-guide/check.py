"""Validate the guide's red/green example without launching an AI agent."""
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
         'shipping.mjs': ('starter/shipping.mjs', 'javascript'),
         'shipping.test.mjs': ('starter/shipping.test.mjs', 'javascript'),
         'index.html': ('starter/index.html', 'html'),
         'reference/shipping.mjs': ('reference/shipping.mjs', 'javascript')}


def tests(root):
    p = subprocess.run(['node', '--test', '--test-reporter=tap', 'shipping.test.mjs'], cwd=root,
                       capture_output=True, text=True, timeout=30)
    counts = {name: int(re.search(r'^# ' + name + r' (\d+)$', p.stdout, re.M)[1])
              for name in ('tests', 'pass', 'fail')}
    return p.returncode, counts


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
        image = ElementTree.parse(ROOT / 'orca-flow-ko.svg').getroot()
        assert image.attrib['{http://www.w3.org/XML/1998/namespace}lang'] == 'ko'
    published = ROOT.parents[2] / 'src/content/posts/ko/2026-11-12-orca-worktree-guide.md'
    if published.exists():
        body = lambda value: value.split('---\n', 2)[2]
        assert body(published.read_text()) == body(text).replace('./orca-flow-ko.svg', '/assets/img/architecture/orca-flow-ko.svg'), 'Published body differs from draft'
        assert (ROOT.parents[2] / 'assets/img/architecture/orca-flow-ko.svg').read_bytes() == (ROOT / 'orca-flow-ko.svg').read_bytes(), 'Published diagram differs'
    with tempfile.TemporaryDirectory(prefix='orca-guide-example-') as directory:
        p = Path(directory)
        for path in (ROOT / 'starter').iterdir(): shutil.copyfile(path, p / path.name)
        protected = {name: (p / name).read_bytes() for name in ('package.json', 'shipping.test.mjs', 'index.html')}
        status, broken = tests(p)
        assert status != 0 and broken == {'tests': 10, 'pass': 3, 'fail': 7}
        shutil.copyfile(ROOT / 'reference/shipping.mjs', p / 'shipping.mjs')
        status, fixed = tests(p)
        assert status == 0 and fixed == {'tests': 10, 'pass': 10, 'fail': 0}
        assert all((p / name).read_bytes() == data for name, data in protected.items())
    result = {'passed': True, 'node': subprocess.check_output(['node', '--version'], text=True).strip(),
              'starter': broken, 'reference': fixed, 'protectedFilesUnchanged': True,
              'aiAgentLaunched': False, 'newManagedWorktreeCreated': False, 'externalNetworkInExample': False}
    if args.result: args.result.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
