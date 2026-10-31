"""Execute the source-derived cache example and check its published flow asset."""
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / '.pipeline/drafts/2026-10-31-cache-aside'
article = (DRAFT / 'article.ko.md').read_text()
published = (ROOT / 'src/content/posts/ko/2026-10-31-cache-aside.md').read_text()


def body(text):
    return re.sub(r'^---\n.*?\n---\n', '', text, count=1, flags=re.S)


assert body(published) == body(article).replace(
    '(./cache-aside-ko.svg)', '(/assets/img/architecture/cache-aside-ko.svg)')
blocks = re.findall(r'```java\n(.*?)\n```', published, re.S)
outputs = re.findall(r'```text\n(.*?)\n```', published, re.S)
assert len(blocks) == len(outputs) == 1
with tempfile.TemporaryDirectory(prefix='cache-example-') as directory:
    source = Path(directory) / 'CacheDemo.java'
    source.write_text(blocks[0] + '\n')
    subprocess.run(['javac', '--release', '21', str(source)], check=True)
    result = subprocess.run(['java', '-cp', directory, 'CacheDemo'],
                            capture_output=True, text=True, check=True, timeout=15)
    assert result.stdout == outputs[0] + '\n', result.stdout

spec = importlib.util.spec_from_file_location(
    'diagrams', ROOT / 'scripts/build_algorithm_diagrams.py')
diagrams = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diagrams)
data = diagrams.validate(json.loads((DRAFT / 'diagram.json').read_text()))
assert len(data['diagrams']) == 1
item = data['diagrams'][0]
for contract in item['codeContract']:
    assert contract['contains'] in blocks[0]
expected_svg = diagrams.render(item, 'ko')
assert (DRAFT / 'cache-aside-ko.svg').read_text() == expected_svg
assert (ROOT / 'assets/img/architecture/cache-aside-ko.svg').read_text() == expected_svg
print('PASS: published cache example output, draft parity and flow asset.')
