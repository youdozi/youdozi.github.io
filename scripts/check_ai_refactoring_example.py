"""Execute the published refactoring example, initial state and boundary mutation."""
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / '.pipeline/drafts/2026-10-31-ai-agent-refactoring'
article = (DRAFT / 'article.ko.md').read_text()
published = (ROOT / 'src/content/posts/ko/2026-10-31-ai-agent-refactoring.md').read_text()


def body(text):
    return re.sub(r'^---\n.*?\n---\n', '', text, count=1, flags=re.S)


def execute(code):
    with tempfile.TemporaryDirectory(prefix='ai-refactoring-example-') as directory:
        source = Path(directory) / 'ShippingRefactorDemo.java'
        source.write_text(code + '\n')
        subprocess.run(['javac', '--release', '21', str(source)], check=True)
        return subprocess.run(['java', '-cp', directory, 'ShippingRefactorDemo'],
                              capture_output=True, text=True, timeout=15)


assert body(published) == body(article).replace(
    '(./ai-agent-refactoring-ko.svg)',
    '(/assets/img/architecture/ai-agent-refactoring-ko.svg)')
blocks = re.findall(r'```java\n(.*?)\n```', published, re.S)
outputs = re.findall(r'```text\n(.*?)\n```', published, re.S)
assert len(blocks) == 1
code = blocks[0]
expected = 'examples=8\ncomparisons=24\nnegative-inputs=2\n'
assert expected.rstrip('\n') in outputs
result = execute(code)
assert result.returncode == 0 and result.stdout == expected, result

before = re.search(r'    static long before\(.*?\n    }\n', code, re.S).group(0)
after = re.search(r'    static long after\(.*?\n    }\n', code, re.S).group(0)
initial = code.replace(after, before.replace('static long before(', 'static long after('))
assert initial != code
result = execute(initial)
assert result.returncode == 0 and result.stdout == expected, result

mutant = code.replace('subtotal >= FREE_THRESHOLD', 'subtotal > FREE_THRESHOLD')
assert mutant != code
result = execute(mutant)
assert result.returncode != 0 and 'expected=0, actual=3000' in result.stderr, result

spec = importlib.util.spec_from_file_location(
    'diagrams', ROOT / 'scripts/build_algorithm_diagrams.py')
diagrams = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diagrams)
data = diagrams.validate(json.loads((DRAFT / 'diagram.json').read_text()))
assert len(data['diagrams']) == 1
item = data['diagrams'][0]
for contract in item['codeContract']:
    assert contract['contains'] in code
expected_svg = diagrams.render(item, 'ko')
assert (DRAFT / 'ai-agent-refactoring-ko.svg').read_text() == expected_svg
assert (ROOT / 'assets/img/architecture/ai-agent-refactoring-ko.svg').read_text() == expected_svg
print('PASS: initial/refactored outputs, detected boundary mutation, source parity and SVG. No AI-product trial.')
