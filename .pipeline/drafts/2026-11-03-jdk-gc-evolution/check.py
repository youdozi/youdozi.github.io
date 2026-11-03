import argparse
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
EXPECTED = 'iterations=8192 retainedSlots=64 checksum=1044480'


def run(script, home, placeholder, directory):
    text = (ROOT / script).read_text()
    text = text.replace('GC_JDK="' + placeholder + '"',
                        'GC_JDK=' + shlex.quote(str(home)))
    subprocess.run(['sh', '-n'], input=text, text=True, check=True)
    result = subprocess.run(['sh', '-e'], input=text, cwd=directory,
                            text=True, capture_output=True, timeout=120)
    if result.returncode:
        raise RuntimeError(result.stderr)
    return result


def main():
    parser = argparse.ArgumentParser(description='Verify draft code parity and its shell examples.')
    parser.add_argument('--jdk27', required=True, type=Path)
    parser.add_argument('--jdk8', type=Path)
    args = parser.parse_args()
    blocks = []
    for language in ['ko', 'en']:
        article = (ROOT / f'article.{language}.md').read_text()
        blocks.append(re.findall(r'^```([^\n]*)\n(.*?)^```', article, re.M | re.S))
    for language, draft_blocks in zip(['ko', 'en'], blocks):
        published = ROOT.parents[2] / 'src/content/posts' / language / (ROOT.name + '.md')
        if published.is_file():
            assert re.findall(r'^```([^\n]*)\n(.*?)^```', published.read_text(), re.M | re.S) == draft_blocks, 'Published code differs from draft'
    assert blocks[0] == blocks[1], 'Code fences differ between languages'
    assert len(blocks[0]) == 6
    for index, artifact in [(0, 'GcProbe.java'), (1, 'run-modern.sh'),
                            (4, 'run-jdk8.sh'), (5, 'inspect-default.sh')]:
        assert blocks[0][index][1] == (ROOT / artifact).read_text(), artifact
    for home in filter(None, [args.jdk27, args.jdk8]):
        assert (home / 'bin/java').is_file() and (home / 'bin/javac').is_file(), home
    with tempfile.TemporaryDirectory(prefix='jdk-gc-draft-') as temporary:
        work = Path(temporary)
        shutil.copy2(ROOT / 'GcProbe.java', work)
        result = run('run-modern.sh', args.jdk27.resolve(), '/path/to/jdk-27', work)
        assert result.stdout.count(EXPECTED) == 4
        logs = list((work / 'logs').glob('gc-*.log'))
        assert len(logs) == 4 and all(log.stat().st_size > 0 for log in logs)
        default = run('inspect-default.sh', args.jdk27.resolve(), '/path/to/jdk-27', work)
        assert '-XX:+UseG1GC' in default.stdout
        if args.jdk8:
            old = run('run-jdk8.sh', args.jdk8.resolve(), '/path/to/jdk-8', work)
            assert EXPECTED in old.stdout
            assert (work / 'logs/jdk8-cms.log').stat().st_size > 0
    print('Code parity, shell syntax, collector completion and GC logs verified.')


if __name__ == '__main__':
    main()
