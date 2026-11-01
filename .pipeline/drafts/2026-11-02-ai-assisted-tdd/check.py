from pathlib import Path
from xml.etree import ElementTree as ET
import argparse
import importlib.util
import json
import os
import re
import subprocess
import tempfile

DRAFT = Path(__file__).resolve().parent
ROOT = DRAFT.parents[2]
article = (DRAFT / 'article.ko.md').read_text()
java = re.findall(r'^```java\n(.*?)^```', article, re.S | re.M)
groovy = re.findall(r'^```groovy\n(.*?)^```', article, re.S | re.M)
assert len(java) == 6 and len(groovy) == 2
initial_test, stub, first_green, added_tests, green, refactored = java
assert initial_test.rstrip().endswith('}')
full_test = initial_test.rstrip()[:-1] + added_tests + '}\n'

parser = argparse.ArgumentParser()
parser.add_argument('--java-home', default=os.environ.get('JAVA_HOME'))
args = parser.parse_args()
env = os.environ.copy()
if args.java_home:
    if not (Path(args.java_home) / 'bin/java').is_file():
        parser.error('Set --java-home to the JDK 17 directory')
    env['JAVA_HOME'] = args.java_home
    env['PATH'] = str(Path(args.java_home) / 'bin') + os.pathsep + env['PATH']
version = subprocess.run(['gradle', '--version'], env=env, capture_output=True,
                         text=True, check=True, timeout=30).stdout
assert 'Gradle 8.4' in version and re.search(r'JVM:\s+17\.', version), version

summaries = []
with tempfile.TemporaryDirectory(prefix='ai-tdd-stock-') as directory:
    work = Path(directory)
    (work / 'src/main/java').mkdir(parents=True)
    (work / 'src/test/java').mkdir(parents=True)
    (work / 'settings.gradle').write_text(groovy[0])
    (work / 'build.gradle').write_text(groovy[1])

    def run(label, implementation, tests, count, failing):
        (work / 'src/main/java/StockPolicy.java').write_text(implementation)
        (work / 'src/test/java/StockPolicyTest.java').write_text(tests)
        result = subprocess.run(['gradle', '--no-daemon', '--console=plain',
                                 'clean', 'test'], cwd=work, env=env,
                                capture_output=True, text=True, timeout=180)
        reports = list((work / 'build/test-results/test').glob('TEST-*.xml'))
        assert reports, (label, 'Missing test XML; this is not a valid Red', result.stdout, result.stderr)
        suites = [ET.parse(path).getroot() for path in reports]
        actual_count = sum(int(suite.get('tests')) for suite in suites)
        failures = [case.get('name').removesuffix('()') for suite in suites
                    for case in suite.findall('testcase')
                    if case.find('failure') is not None]
        errors = sum(int(suite.get('errors', '0')) for suite in suites)
        skipped = sum(int(suite.get('skipped', '0')) for suite in suites)
        expected_exit = 1 if failing else 0
        assert (result.returncode, actual_count, set(failures), errors, skipped) == (
            expected_exit, count, set(failing), 0, 0), (label, result.stdout, result.stderr, failures)
        row = {'stage': label, 'tests': actual_count, 'failures': len(failures),
               'skipped': skipped, 'exitCode': result.returncode}
        summaries.append(row)
        print(json.dumps(row), flush=True)

    run('first-red', stub, initial_test, 1, ['reservesPartOfStock'])
    run('first-green', first_green, initial_test, 1, [])
    run('expanded-red', first_green, full_test, 9, [
        'rejectsInsufficientStock', 'rejectsEmptyStock', 'rejectsNegativeStock',
        'rejectsZeroRequest', 'rejectsNegativeRequest', 'validatesStockBeforeRequest'])
    run('expanded-green', green, full_test, 9, [])
    run('refactor', refactored, full_test, 9, [])
    run('mutant-equal-stock', refactored.replace('requested > stock', 'requested >= stock'),
        full_test, 9, ['reservesAllStock'])
    run('mutant-zero-request', refactored.replace('requested <= 0', 'requested < 0'),
        full_test, 9, ['rejectsZeroRequest'])
    before = ('        if (stock < 0) throw new IllegalArgumentException("stock");\n'
              '        if (requested <= 0) throw new IllegalArgumentException("requested");')
    after = ('        if (requested <= 0) throw new IllegalArgumentException("requested");\n'
             '        if (stock < 0) throw new IllegalArgumentException("stock");')
    assert before in refactored
    run('mutant-validation-order', refactored.replace(before, after), full_test, 9,
        ['validatesStockBeforeRequest'])

spec = importlib.util.spec_from_file_location('diagrams', ROOT / 'scripts/build_algorithm_diagrams.py')
diagrams = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diagrams)
data = diagrams.validate(json.loads((DRAFT / 'diagram.json').read_text()))
item = data['diagrams'][0]
assert item['codeContract'][0]['contains'] in initial_test
svg = (DRAFT / 'ai-assisted-tdd-cycle-ko.svg').read_text()
assert svg == diagrams.render(item, 'ko')
ET.fromstring(svg)
assert '(./ai-assisted-tdd-cycle-ko.svg)' in article
assert article.count('| 첫 Red | 1 | 1 | 0 | 1 |') == 1
assert article.count('| 추가 사례 Red | 9 | 6 | 0 | 1 |') == 1
assert article.count('| Refactor | 9 | 0 | 0 | 0 |') == 1
print('PASS: staged Red/Green/Refactor, three targeted regression mutations and SVG/source parity. No AI product, DB or load test.')

for lang in ('en', 'ko'):
    draft = (DRAFT / f'article.{lang}.md').read_text()
    for fence in ('java', 'groovy', 'sh'):
        assert re.findall(r'^```' + fence + r'\n(.*?)^```', draft, re.S | re.M) == re.findall(
            r'^```' + fence + r'\n(.*?)^```', article, re.S | re.M), (lang, fence)
    body = draft.split('---\n', 2)[2]
    published = (ROOT / f'src/content/posts/{lang}/{item["key"]}.md').read_text()
    assert published.split('---\n', 2)[2] == body.replace(
        f'](./ai-assisted-tdd-cycle-{lang}.svg)',
        f'](/assets/diagrams/{item["key"]}-{lang}.svg)')
    expected_svg = diagrams.render(item, lang)
    assert (DRAFT / f'ai-assisted-tdd-cycle-{lang}.svg').read_text() == expected_svg
    assert (ROOT / f'public/assets/diagrams/{item["key"]}-{lang}.svg').read_text() == expected_svg
    rows = re.findall(r'^\| [^|]+ \| (\d+) \| (\d+) \| (\d+) \| (\d+) \|$', draft, re.M)
    assert rows == [(str(row['tests']), str(row['failures']), str(row['skipped']), str(row['exitCode']))
                    for row in summaries[:5]], (lang, rows)
print('PASS: bilingual executable blocks, measured tables, published bodies and localized diagrams match.')
