"""Execute the source-derived offline operations gate and validate both diagrams."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import re
import runpy
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / '.pipeline/drafts/2026-10-31-ai-agent-operations'
article = (DRAFT / 'article.ko.md').read_text()
published = (ROOT / 'src/content/posts/ko/2026-10-31-ai-agent-operations.md').read_text()


def body(text):
    return re.sub(r'^---\n.*?\n---\n', '', text, count=1, flags=re.S)


expected_body = body(article)
for asset in DRAFT.glob('*.svg'):
    expected_body = expected_body.replace(
        '(./' + asset.name + ')', '(/assets/img/architecture/' + asset.name + ')')
assert body(published) == expected_body
blocks = re.findall(r'```python\n(.*?)\n```', published, re.S)
outputs = re.findall(r'```text\n(.*?)\n```', published, re.S)
assert len(blocks) == 1
expected = '\n'.join([
    'complete=READY_FOR_REVIEW', 'user-impact=STOP:signal',
    'missing-rdb=HOLD:coverage', 'stale=HOLD:freshness',
    'unknown=HOLD:unknown', 'wrong-image=HOLD:identity',
    'future=HOLD:freshness', 'invalid-time=HOLD:freshness',
    'wrong-scope=HOLD:identity', 'test-failure=STOP:signal',
]) + '\n'
assert expected.rstrip('\n') in outputs
with tempfile.TemporaryDirectory(prefix='ai-operations-example-') as directory:
    source = Path(directory) / 'evidence_gate.py'
    source.write_text(blocks[0] + '\n')
    result = subprocess.run([sys.executable, '-B', str(source)],
                            capture_output=True, text=True, check=True, timeout=15)
    assert result.stdout == expected, result.stdout
    module = runpy.run_path(str(source))

decide, target, now = module['decide'], module['EXPECTED'], module['NOW']
good = {name: dict(target, status='ok', observed_at=now - 60,
                  source='fixture:' + name) for name in module['TTL']}
for invalid, expected_result in [(None, 'HOLD:coverage'), ({}, 'HOLD:coverage')]:
    assert decide(invalid, target, now) == expected_result
for domain, ttl in module['TTL'].items():
    boundary = deepcopy(good)
    boundary[domain]['observed_at'] = now - ttl
    assert decide(boundary, target, now) == 'READY_FOR_REVIEW'
    boundary[domain]['observed_at'] -= 1
    assert decide(boundary, target, now) == 'HOLD:freshness'
for key, value, expected_result in [
    ('source', None, 'HOLD:shape'), ('status', 'skipped', 'HOLD:shape'),
    ('observed_at', True, 'HOLD:freshness'), ('commit', 'other', 'HOLD:identity'),
]:
    changed = deepcopy(good)
    changed['lgtm'][key] = value
    assert decide(changed, target, now) == expected_result
mixed = deepcopy(good)
mixed['lgtm']['status'], mixed['rdb']['status'] = 'fail', 'unknown'
assert decide(mixed, target, now) == 'STOP:signal'

spec = importlib.util.spec_from_file_location(
    'diagrams', ROOT / 'scripts/build_algorithm_diagrams.py')
diagrams = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diagrams)
data = diagrams.validate(json.loads((DRAFT / 'diagram.json').read_text()))
assert len(data['diagrams']) == 2
for item in data['diagrams']:
    for contract in item.get('codeContract', []):
        assert contract['contains'] in blocks[0]
    name = item['key'].removeprefix('2026-10-31-') + '-ko.svg'
    expected_svg = diagrams.render(item, 'ko')
    assert (DRAFT / name).read_text() == expected_svg
    assert (ROOT / 'assets/img/architecture' / name).read_text() == expected_svg
print('PASS: 10 synthetic scenarios, TTL boundaries and malformed evidence; body and two SVGs match. No live service calls.')
