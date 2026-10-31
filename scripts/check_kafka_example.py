"""Check published Kafka source parity, shell syntax and generated flow asset."""
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / '.pipeline/drafts/2026-10-31-kafka-event-streaming'
article = (DRAFT / 'article.ko.md').read_text()
published = (ROOT / 'src/content/posts/ko/2026-10-31-kafka-event-streaming.md').read_text()


def body(text):
    return re.sub(r'^---\n.*?\n---\n', '', text, count=1, flags=re.S)


assert body(published) == body(article).replace(
    '(./kafka-event-streaming-ko.svg)',
    '(/assets/img/architecture/kafka-event-streaming-ko.svg)')
blocks = re.findall(r'```sh\n(.*?)\n```', published, re.S)
assert len(blocks) == 1
with tempfile.TemporaryDirectory(prefix='kafka-source-') as directory:
    source = Path(directory) / 'kafka-demo.sh'
    source.write_text(blocks[0] + '\n')
    subprocess.run(['bash', '-n', str(source)], check=True)

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
assert (DRAFT / 'kafka-event-streaming-ko.svg').read_text() == expected_svg
assert (ROOT / 'assets/img/architecture/kafka-event-streaming-ko.svg').read_text() == expected_svg
print('PASS: Kafka draft/public source parity, Bash syntax and flow asset. No broker run by this check.')
