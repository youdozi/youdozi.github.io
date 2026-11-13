"""Execute the draft's Rust examples and compare the embedded source contracts."""
import argparse
import atexit
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parent


def run(command, *, cwd=ROOT, expected=0):
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, timeout=120)
    assert result.returncode == expected, (command, result.returncode, result.stdout, result.stderr)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--result', type=Path)
    args = parser.parse_args()
    scratch = tempfile.TemporaryDirectory(prefix='rust-guide-target-')
    atexit.register(scratch.cleanup)
    os.environ['CARGO_TARGET_DIR'] = scratch.name
    text = (ROOT / 'article.ko.md').read_text()
    for name, language in [('Cargo.toml', 'toml'), ('rust-toolchain.toml', 'toml'), ('src/main.rs', 'rust')]:
        pattern = r'^### `' + re.escape(name) + r'`\n\n```' + language + r'\n([\s\S]*?)\n```'
        blocks = re.findall(pattern, text, re.M)
        assert len(blocks) == 1 and blocks[0] + '\n' == (ROOT / name).read_text(), name
    for name in ['move_error.rs', 'borrow_ok.rs']:
        assert '```rust\n' + (ROOT / 'snippets' / name).read_text() + '```' in text
    svg = ElementTree.parse(ROOT / 'rust-flow-ko.svg').getroot()
    assert svg.attrib['{http://www.w3.org/XML/1998/namespace}lang'] == 'ko'
    assert re.search(r'!\[[^\]]+\]\(\./rust-flow-ko.svg\)', text)
    published = ROOT.parents[2] / 'src/content/posts/ko/2026-11-13-rust-ownership-guide.md'
    if published.exists():
        body = lambda value: value.split('---\n', 2)[2]
        assert body(published.read_text()) == body(text).replace('./rust-flow-ko.svg', '/assets/img/architecture/rust-flow-ko.svg'), 'Published body differs from draft'
        assert (ROOT.parents[2] / 'assets/img/architecture/rust-flow-ko.svg').read_bytes() == (ROOT / 'rust-flow-ko.svg').read_bytes(), 'Published diagram differs'
    version = run(['rustc', '--version']).stdout.strip()
    assert version.startswith('rustc 1.100.0 '), version
    run(['cargo', 'check', '--offline'])
    run(['cargo', 'fmt', '--check'])
    run(['cargo', 'clippy', '--offline', '--', '-D', 'warnings'])
    cases = [
        (['12000', '8000', '0'], 0, 'count=3, total=20000\n', ''),
        (['0'], 0, 'count=1, total=0\n', ''),
        ([], 1, '', 'error: EmptyInput\n'),
        (['12000', 'abc'], 1, '', 'error: InvalidAmount\n'),
        (['-1'], 1, '', 'error: InvalidAmount\n'),
        (['1.5'], 1, '', 'error: InvalidAmount\n'),
        (['18446744073709551616'], 1, '', 'error: InvalidAmount\n'),
        (['18446744073709551615', '0'], 0, 'count=2, total=18446744073709551615\n', ''),
        (['18446744073709551615', '1'], 1, '', 'error: TotalOverflow\n'),
        (['1', '2', '3'], 0, 'count=3, total=6\n', ''),
        ([' 1'], 1, '', 'error: InvalidAmount\n'),
        ([''], 1, '', 'error: InvalidAmount\n'),
    ]
    with tempfile.TemporaryDirectory(prefix='rust-guide-') as directory:
        build = Path(directory)
        for profile in ['debug', 'release']:
            command = ['cargo', 'build', '--offline', '--target-dir', directory]
            if profile == 'release':
                command.append('--release')
            run(command)
            binary = build / profile / ('expense-summary.exe' if os.name == 'nt' else 'expense-summary')
            for inputs, status, stdout, stderr in cases:
                result = run([str(binary), *inputs], expected=status)
                assert (result.stdout, result.stderr) == (stdout, stderr), (profile, inputs, result)
        for inputs, status, stdout, stderr in cases[:9]:
            result = run(['cargo', 'run', '--offline', '--quiet', '--', *inputs], expected=status)
            assert (result.stdout, result.stderr) == (stdout, stderr)
        result = run(['rustc', '--edition', '2024', 'snippets/move_error.rs', '-o', str(build / 'move_error')], expected=1)
        assert 'E0382' in result.stderr and 'borrow of moved value' in result.stderr
        run(['rustc', '--edition', '2024', 'snippets/borrow_ok.rs', '-o', str(build / 'borrow_ok')])
        assert run([str(build / 'borrow_ok')]).stdout == 'Rust\nRust language\n'
        overlap = build / 'borrow_overlap.rs'
        overlap.write_text((ROOT / 'snippets/borrow_ok.rs').read_text().replace('println!("{name}");', 'println!("{name}, {borrowed}");'))
        result = run(['rustc', '--edition', '2024', str(overlap), '-o', str(build / 'overlap')], expected=1)
        assert 'E0502' in result.stderr
    result = {'passed': True, 'rustc': version, 'cliCasesPerProfile': len(cases),
              'profiles': ['debug', 'release'], 'cargoRunCases': 9,
              'expectedCompileErrors': ['E0382', 'E0502'], 'borrowingExamplePassed': True,
              'embeddedSourcesMatch': True, 'diagramLanguage': 'ko',
              'performanceMeasured': False, 'externalDependencies': False}
    if args.result:
        args.result.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
