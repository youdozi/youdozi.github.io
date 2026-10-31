"""Check the draft's embedded Java example and regenerate its private SVG."""
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
article = (HERE / 'article.ko.md').read_text()
blocks = re.findall(r'```java\n(.*?)\n```', article, re.S)
assert len(blocks) == 1
expected = (HERE / 'execution.txt').read_text()
assert f'```text\n{expected}```' in article
with tempfile.TemporaryDirectory(prefix='fallback-demo-') as directory:
    source = Path(directory) / 'FallbackDemo.java'
    source.write_text(blocks[0] + '\n')
    subprocess.run(['javac', '--release', '21', str(source)], check=True)
    result = subprocess.run(
        ['java', '-cp', directory, 'FallbackDemo'],
        capture_output=True, text=True, check=True, timeout=15)
    assert result.stdout == expected, result.stdout

spec = importlib.util.spec_from_file_location(
    'diagrams', ROOT / 'scripts/build_algorithm_diagrams.py')
diagrams = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diagrams)
data = diagrams.validate(json.loads((HERE / 'diagram.json').read_text()))
assert len(data['diagrams']) == 1
item = data['diagrams'][0]
for contract in item['codeContract']:
    assert contract['contains'] in blocks[0]
(HERE / 'fallback-ko.svg').write_text(diagrams.render(item, 'ko'))
published = ROOT / 'src/content/posts/ko/2026-10-31-failure-fallback.md'
if published.exists():
    body = lambda text: re.sub(r'^---\n.*?\n---\n', '', text, count=1, flags=re.S)
    assert body(published.read_text()) == body(article).replace(
        '(./fallback-ko.svg)', '(/assets/img/architecture/fallback-ko.svg)')
    assert (ROOT / 'assets/img/architecture/fallback-ko.svg').read_text() == diagrams.render(item, 'ko')
print('PASS: Java output matches all nine lines; diagram source is valid.')
