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
assert len(blocks) == 1
code = blocks[0]
with tempfile.TemporaryDirectory(prefix='attack-defense-') as directory:
    path = Path(directory) / 'correlate.py'
    path.write_text(code)
    result = subprocess.run([sys.executable, str(path)], text=True, capture_output=True,
                            check=True, timeout=10)
    assert result.stdout == "[('agent-a', 'run-1', 20)]\n" and not result.stderr
    output = re.findall(r'^```text\n(.*?)^```', article, re.S | re.M)
    assert output == [result.stdout]


def evaluate(source):
    scope = {'__name__': 'article_example'}
    exec(compile(source, 'correlate.py', 'exec'), scope)
    event, correlate = scope['Event'], scope['correlate']
    def read(at=0, actor='a', run='1'):
        return event(at, actor, run, 'untrusted_read')
    def denied(at=20, actor='a', run='1'):
        return event(at, actor, run, 'egress_denied')
    cases = [
        ('empty', [], [], 300),
        ('timestamp-zero', [read(), denied()], [('a', '1', 20)], 300),
        ('inclusive-boundary', [read(), denied(300)], [('a', '1', 300)], 300),
        ('outside-window', [read(), denied(301)], [], 300),
        ('different-actor', [read(), denied(actor='b')], [], 300),
        ('different-run', [read(), denied(run='2')], [], 300),
        ('missing-read', [denied()], [], 300),
        ('denied-before-read', [read(30), denied(20)], [], 300),
        ('unordered-input', [denied(), read()], [('a', '1', 20)], 300),
        ('latest-read', [read(), read(200), denied(400)], [('a', '1', 400)], 300),
        ('allowed-egress', [read(), event(20, 'a', '1', 'egress_allowed')], [], 300),
        ('zero-window', [read(1), denied(1)], [('a', '1', 1)], 0),
    ]
    failing = []
    for name, events, expected, window in cases:
        if correlate(events, window) != expected:
            failing.append(name)
    try:
        correlate([], -1)
    except ValueError as error:
        if str(error) != 'window':
            failing.append('negative-window')
    else:
        failing.append('negative-window')
    return failing, len(cases) + 1

failing, count = evaluate(code)
assert not failing, failing
print(f'PASS: exact article output and {count} synthetic event cases.')
mutations = {
    'exclusive-boundary': ('<= window', '< window', {'inclusive-boundary', 'zero-window'}),
    'ignore-actor': ('key = (event.actor, event.run)', 'key = ("any", event.run)', {'different-actor'}),
    'ignore-time-zero': ('read_at is not None', 'read_at', {'timestamp-zero', 'inclusive-boundary', 'unordered-input'}),
}
for name, (before, after, expected) in mutations.items():
    assert code.count(before) == 1
    failing, _ = evaluate(code.replace(before, after))
    assert set(failing) == expected, (name, failing)
    print(json.dumps({'mutation': name, 'detectedBy': failing}))

spec = importlib.util.spec_from_file_location('diagrams', ROOT / 'scripts/build_algorithm_diagrams.py')
diagrams = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diagrams)
data = diagrams.validate(json.loads((DRAFT / 'diagram.json').read_text()))
svg = (DRAFT / 'ai-attack-signal-correlation-ko.svg').read_text()
assert svg == diagrams.render(data['diagrams'][0], 'ko')
ET.fromstring(svg)
assert '](./ai-attack-signal-correlation-ko.svg)' in article
print('PASS: localized diagram source parity. Offline synthetic correlation only; no LLM or enforcement tested.')

for lang in ('en', 'ko'):
    draft = (DRAFT / f'article.{lang}.md').read_text()
    for fence in ('python', 'sh', 'text'):
        assert re.findall(r'^```' + fence + r'\n(.*?)^```', draft, re.S | re.M) == re.findall(
            r'^```' + fence + r'\n(.*?)^```', article, re.S | re.M), (lang, fence)
    item = data['diagrams'][0]
    body = draft.split('---\n', 2)[2]
    published = (ROOT / f'src/content/posts/{lang}/{item["key"]}.md').read_text()
    assert published.split('---\n', 2)[2] == body.replace(
        f'](./ai-attack-signal-correlation-{lang}.svg)',
        f'](/assets/diagrams/{item["key"]}-{lang}.svg)')
    expected_svg = diagrams.render(item, lang)
    assert (DRAFT / f'ai-attack-signal-correlation-{lang}.svg').read_text() == expected_svg
    assert (ROOT / f'public/assets/diagrams/{item["key"]}-{lang}.svg').read_text() == expected_svg
print('PASS: bilingual code, commands, output, published bodies and diagram parity.')
