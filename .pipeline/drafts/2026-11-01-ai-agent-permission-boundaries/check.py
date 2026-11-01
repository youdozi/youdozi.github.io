from pathlib import Path
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
from xml.etree import ElementTree as ET

DRAFT = Path(__file__).resolve().parent
ROOT = DRAFT.parents[2]
article = (DRAFT / 'article.ko.md').read_text()
blocks = re.findall(r'^```python\n(.*?)^```', article, re.S | re.M)
outputs = re.findall(r'^```text\n(.*?)^```', article, re.S | re.M)
assert len(blocks) == len(outputs) == 1
code, expected = blocks[0], outputs[0]
for language in ('en', 'ko'):
    draft = (DRAFT / f'article.{language}.md').read_text()
    assert re.findall(r'^```python\n(.*?)^```', draft, re.S | re.M) == blocks
    assert re.findall(r'^```text\n(.*?)^```', draft, re.S | re.M) == outputs
    published = (ROOT / f'src/content/posts/{language}/2026-11-01-ai-agent-permission-boundaries.md').read_text()
    draft_body = draft.split('\n---\n', 1)[1]
    published_body = published.split('\n---\n', 1)[1]
    assert published_body == draft_body.replace(
        f'](./ai-agent-permission-gate-{language}.svg)',
        f'](/assets/diagrams/2026-11-01-ai-agent-permission-boundaries-{language}.svg)')


def execute(source):
    with tempfile.TemporaryDirectory(prefix='agent-permission-') as directory:
        target = Path(directory) / 'permission_gate.py'
        target.write_text(source)
        return subprocess.run([sys.executable, str(target)], capture_output=True,
                              text=True, timeout=10)


result = execute(code)
assert result.returncode == 0 and result.stdout == expected, result
mutations = {
    'scope': ('grant.subject != subject or grant.request != request', 'False'),
    'expiry': ('now >= grant.expires_at', 'now > grant.expires_at'),
    'replay': ('grant.nonce in self.used', 'False'),
}
for name, (before, after) in mutations.items():
    assert before in code
    result = execute(code.replace(before, after))
    assert result.returncode != 0, f'Undetected {name} regression'

spec = importlib.util.spec_from_file_location('diagrams', ROOT / 'scripts/build_algorithm_diagrams.py')
diagrams = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diagrams)
data = diagrams.validate(json.loads((DRAFT / 'diagram.json').read_text()))
item = data['diagrams'][0]
assert item['codeContract'][0]['contains'] in code
for language in ('en', 'ko'):
    svg = (DRAFT / f'ai-agent-permission-gate-{language}.svg').read_text()
    assert svg == diagrams.render(item, language)
    ET.fromstring(svg)
    assert f'(./ai-agent-permission-gate-{language}.svg)' in (DRAFT / f'article.{language}.md').read_text()
assert len(expected.strip().splitlines()) == 10
print('PASS: 10 synthetic authorization cases; 3 regression mutations; paired publication and SVG/source parity. No external action executed.')
