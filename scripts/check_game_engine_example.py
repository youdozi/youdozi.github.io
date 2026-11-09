#!/usr/bin/env python3
"""Execute the published Godot movement example with an explicit, versioned runtime."""
import argparse
import hashlib
from pathlib import Path
import re
import shlex
import subprocess
import tempfile
from urllib.request import urlopen
from urllib.error import HTTPError
import zipfile

ROOT = Path(__file__).resolve().parents[1]
KEY = '2026-11-02-open-source-game-engines'
ASSET = 'Godot_v4.7.2-stable_linux.x86_64.zip'
DIGEST = 'cadd3204e728a35d3f13adb7fd0d7902636b79f6b95c40c265eb73b6c35329e4'


def example():
    editions = []
    for lang in ('en', 'ko'):
        raw = (ROOT / f'src/content/posts/{lang}/{KEY}.md').read_text()
        blocks = re.findall(r'^```([^\n]*)\n(.*?)^```[ \t]*$', raw, re.S | re.M)
        if [language for language, _ in blocks] != ['ini', 'gdscript', 'sh', 'text']:
            raise ValueError('Expected complete project, script, command and observed output')
        editions.append(blocks)
    if editions[0] != editions[1]:
        raise ValueError('Native executable editions differ')
    return [code for _, code in editions[0]]


def execute(runtime, project, script, command, output):
    with tempfile.TemporaryDirectory(prefix='godot-movement-') as directory:
        folder = Path(directory)
        (folder / 'project.godot').write_text(project)
        (folder / 'movement.gd').write_text(script)
        args = shlex.split(command)
        if args[0] != 'godot':
            raise ValueError('Expected the declared Godot command')
        result = subprocess.run([str(runtime), *args[1:], '--log-file', str(folder / 'run.log')],
                                cwd=folder, text=True, capture_output=True, timeout=30)
        return result.returncode == 0 and result.stdout == output and not result.stderr, result



def download_runtime(url):
    try:
        with urlopen(url, timeout=120) as response:
            return response.read()
    except HTTPError as error:
        if error.code not in (502, 503, 504):
            raise
    # Request the same pinned release asset through a fresh public download URL.
    with urlopen(url + '?download=1', timeout=120) as response:
        return response.read()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    runtime = parser.add_mutually_exclusive_group(required=True)
    runtime.add_argument('--godot', type=Path, help='Existing standard Godot 4.7.2 editor binary')
    runtime.add_argument('--download', action='store_true', help='Download and verify Linux x86_64 runtime in a temporary directory')
    args = parser.parse_args()
    project, script, command, output = example()
    with tempfile.TemporaryDirectory(prefix='godot-runtime-') as directory:
        if args.download:
            url = 'https://github.com/godotengine/godot-builds/releases/download/4.7.2-stable/' + ASSET
            raw = download_runtime(url)
            if hashlib.sha256(raw).hexdigest() != DIGEST:
                raise ValueError('Godot archive checksum mismatch')
            archive = Path(directory) / ASSET
            archive.write_bytes(raw)
            binary = Path(directory) / ASSET.removesuffix('.zip')
            with zipfile.ZipFile(archive) as zipped:
                binary.write_bytes(zipped.read(binary.name))
            binary.chmod(0o700)
        else:
            binary = args.godot.expanduser().resolve(strict=True)
        version = subprocess.check_output([str(binary), '--headless', '--version'], text=True, timeout=30).strip()
        if not version.startswith('4.7.2.stable.'):
            raise ValueError('Expected standard Godot 4.7.2')
        passed, result = execute(binary, project, script, command, output)
        if not passed:
            raise RuntimeError(f'Published example failed: {result.stdout} {result.stderr}')
        print(f'[ok] {version}: native articles match; nine headless movement cases passed.')
        mutations = [
            ('direction magnitude', 'direction.limit_length(1.0)', 'direction'),
            ('elapsed time', 'bounded * SPEED * delta', 'bounded * SPEED'),
            ('point bounds', 'return next.clamp(Vector2.ZERO, LIMIT)', 'return next'),
        ]
        for name, before, after in mutations:
            if script.count(before) != 1:
                raise ValueError('Ambiguous mutation target')
            passed, result = execute(binary, project, script.replace(before, after), command, output)
            if passed or 'movement mismatch' not in result.stderr:
                raise ValueError('Regression mutation did not fail on a movement assertion: ' + name)
            print('[ok] Movement checks detect regression: ' + name)
    print('[ok] No rendered-game, export, performance or other-engine hands-on result claimed.')


if __name__ == '__main__':
    main()
