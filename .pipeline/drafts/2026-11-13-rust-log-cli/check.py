"""Run the draft's Rust stream tests and black-box CLI contracts."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parent


def run(command, *, expected=0, env=None):
    result = subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True, timeout=120)
    assert result.returncode == expected, (command, result.returncode, result.stdout, result.stderr)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--result', type=Path)
    args = parser.parse_args()
    article = (ROOT / 'article.ko.md').read_text()
    for name, language in [('Cargo.toml', 'toml'), ('rust-toolchain.toml', 'toml'),
                           ('src/lib.rs', 'rust'), ('src/main.rs', 'rust'),
                           ('tests/stream.rs', 'rust'), ('examples/access.log', 'text')]:
        pattern = r'^### `' + re.escape(name) + r'`\n\n```' + language + r'\n([\s\S]*?)\n```'
        blocks = re.findall(pattern, article, re.M)
        assert len(blocks) == 1 and blocks[0] + '\n' == (ROOT / name).read_text(), name
    svg = ElementTree.parse(ROOT / 'log-cli-flow-ko.svg').getroot()
    assert svg.attrib['{http://www.w3.org/XML/1998/namespace}lang'] == 'ko'
    assert re.search(r'!\[[^\]]+\]\(\./log-cli-flow-ko.svg\)', article)
    published = ROOT.parents[2] / 'src/content/posts/ko/2026-11-13-rust-log-cli.md'
    if published.exists():
        body = lambda value: value.split('---\n', 2)[2]
        assert body(published.read_text()) == body(article).replace('./log-cli-flow-ko.svg', '/assets/img/architecture/log-cli-flow-ko.svg'), 'Published body differs from draft'
        assert (ROOT.parents[2] / 'assets/img/architecture/log-cli-flow-ko.svg').read_bytes() == (ROOT / 'log-cli-flow-ko.svg').read_bytes(), 'Published diagram differs'
    version = run(['rustc', '--version']).stdout.strip()
    assert version.startswith('rustc 1.100.0 '), version
    with tempfile.TemporaryDirectory(prefix='rust-log-guide-') as directory:
        scratch = Path(directory)
        env = {**os.environ, 'CARGO_TARGET_DIR': str(scratch / 'target')}
        run(['cargo', 'check', '--offline'], env=env)
        run(['cargo', 'fmt', '--check'], env=env)
        run(['cargo', 'clippy', '--offline', '--all-targets', '--', '-D', 'warnings'], env=env)
        mixed = 'valid=4 invalid=2\nstatus=200 count=2\nstatus=404 count=1\nstatus=503 count=1\n'
        files = {
            'normal.log': b'503 /b\n200 /a\n200 /a\n',
            'empty.log': b'', 'blank.log': b'\n',
            'crlf.log': b'200 /a\r\n503 /b',
            'utf8.log': b'200 /a\n\xff\n',
            'long.log': b'200 /' + b'a' * 4091 + b'\n',
            'limit.log': b'200 /' + b'a' * 4090 + b'\n',
            'many.log': b'200 /health\n' * 100_000,
            'invalid.log': b'099 /a\n600 /a\n+20 /a\n200 relative\n200 /a extra\n200\n',
        }
        for name, data in files.items():
            (scratch / name).write_bytes(data)
        cases = [
            ([str(ROOT / 'examples/access.log')], 1, mixed, ''),
            ([str(scratch / 'normal.log')], 0, 'valid=3 invalid=0\nstatus=200 count=2\nstatus=503 count=1\n', ''),
            ([str(scratch / 'empty.log')], 0, 'valid=0 invalid=0\n', ''),
            ([str(scratch / 'blank.log')], 1, 'valid=0 invalid=1\n', ''),
            ([str(scratch / 'crlf.log')], 0, 'valid=2 invalid=0\nstatus=200 count=1\nstatus=503 count=1\n', ''),
            ([], 2, '', 'usage: access-summary <file>'),
            (['one', 'two'], 2, '', 'usage: access-summary <file>'),
            ([str(scratch / 'missing.log')], 2, '', None),
            ([str(scratch / 'utf8.log')], 2, '', 'input is not UTF-8'),
            ([str(scratch / 'long.log')], 2, '', 'line exceeds 4096 bytes'),
            ([str(scratch / 'limit.log')], 0, 'valid=1 invalid=0\nstatus=200 count=1\n', ''),
            ([str(scratch / 'many.log')], 0, 'valid=100000 invalid=0\nstatus=200 count=100000\n', ''),
            ([str(scratch / 'invalid.log')], 1, 'valid=0 invalid=6\n', ''),
        ]
        for profile in ['debug', 'release']:
            test_command = ['cargo', 'test', '--offline']
            build_command = ['cargo', 'build', '--offline']
            if profile == 'release':
                test_command.append('--release')
                build_command.append('--release')
            test = run(test_command, env=env)
            assert '8 passed; 0 failed' in test.stdout
            run(build_command, env=env)
            binary = scratch / 'target' / profile / ('access-summary.exe' if os.name == 'nt' else 'access-summary')
            for inputs, status, stdout, stderr in cases:
                result = run([str(binary), *inputs], expected=status, env=env)
                assert result.stdout == stdout, (profile, inputs, result.stdout)
                if stderr == '':
                    assert result.stderr == ''
                else:
                    assert result.stderr.startswith('error: ')
                    if stderr is not None:
                        assert stderr in result.stderr
            if os.name == 'posix':
                read_fd, write_fd = os.pipe()
                os.close(read_fd)
                try:
                    result = subprocess.run([str(binary), str(scratch / 'normal.log')], cwd=ROOT,
                                            stdout=write_fd, stderr=subprocess.PIPE, text=True, timeout=10)
                    assert result.returncode == 2 and result.stderr.startswith('error: '), result
                finally:
                    os.close(write_fd)
                read_fd, write_fd = os.pipe()
                os.close(read_fd)
                try:
                    result = subprocess.run([str(binary)], cwd=ROOT, stdout=subprocess.PIPE,
                                            stderr=write_fd, text=True, timeout=10)
                    assert result.returncode == 2 and result.stdout == '', result
                finally:
                    os.close(write_fd)
    result = {'passed': True, 'rustc': version, 'streamTestsPerProfile': 8,
              'cliCasesPerProfile': len(cases), 'profiles': ['debug', 'release'],
              'brokenStdoutAndStderrTested': os.name == 'posix', 'largeFixtureRecords': 100_000,
              'embeddedSourcesMatch': True, 'lineLimitBytes': 4096,
              'readLimitConsumedVerifiedByCursor': 4097, 'performanceMeasured': False,
              'externalDependencies': False}
    if args.result:
        args.result.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
