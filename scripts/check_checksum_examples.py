#!/usr/bin/env python3
"""Run the paired article's actual ZIP members against local byte fixtures."""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from unittest.mock import patch

from build_example_archives import extract_example

KEY = '2026-10-30-verify-sha256-download'
ABC = 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
EMPTY = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'


def main():
    editions, shell_editions = [], []
    for language in ('en', 'ko'):
        article = Path(f'src/content/posts/{language}/{KEY}.md').read_text()
        pairs = re.findall(r'^### `([^`]+)`\n\n```python\n([\s\S]*?)\n```', article, re.M)
        assert len(pairs) == 2 and {name for name, _ in pairs} == {'verify-sha256.py', 'make-samples.py'}
        editions.append(dict(pairs))
        shell_editions.append(re.findall(r'^```sh\n([\s\S]*?)\n```', article, re.M))
    assert editions[0] == editions[1], 'Paired executable code must be identical'
    assert shell_editions[0] == shell_editions[1] and len(shell_editions[0]) == 1, 'Paired commands must match'
    cases = []
    with tempfile.TemporaryDirectory(prefix='youdozi-checksum-') as directory:
        root = Path(directory)
        extract_example(KEY, root, editions[0])
        subprocess.run([sys.executable, 'make-samples.py'], cwd=root, check=True)
        assert (root / 'sample.bin').read_bytes() == b'abc'
        assert (root / 'changed.bin').read_bytes() == b'abcd'

        def check(name, args, status, message):
            result = subprocess.run([sys.executable, 'verify-sha256.py', *args], cwd=root, text=True,
                                    capture_output=True, timeout=10)
            assert result.returncode == status, (name, result)
            if status == 0:
                assert result.stdout == 'OK\n' and not result.stderr, (name, result)
            else:
                assert not result.stdout and message in result.stderr and 'Traceback' not in result.stderr, (name, result)
            cases.append(name)

        check('known-abc', [ABC, 'sample.bin'], 0, '')
        check('uppercase-expected', [ABC.upper(), 'sample.bin'], 0, '')
        check('changed-byte', [ABC, 'changed.bin'], 1, 'MISMATCH')
        check('missing-file', [ABC, 'missing.bin'], 2, 'READ ERROR')
        check('directory', [ABC, '.'], 2, 'READ ERROR')
        for name in ['sample with spaces.bin', '한글 文件.bin', '-leading-dash.bin']:
            (root / name).write_bytes(b'abc')
            check(name, [ABC, name], 0, '')
        for name, payload, expected in [
            ('empty', b'', EMPTY),
            ('lf', b'abc\n', hashlib.sha256(b'abc\n').hexdigest()),
            ('crlf', b'abc\r\n', hashlib.sha256(b'abc\r\n').hexdigest()),
            ('binary', bytes(range(256)), hashlib.sha256(bytes(range(256))).hexdigest()),
        ]:
            (root / name).write_bytes(payload)
            check(name, [expected, name], 0, '')
        check('line-ending-difference', [ABC, 'lf'], 1, 'MISMATCH')
        for size in [1024 * 1024 - 1, 1024 * 1024, 1024 * 1024 + 1, 2 * 1024 * 1024 + 17]:
            payload = b'x' * size
            (root / 'large.bin').write_bytes(payload)
            expected = hashlib.sha256(payload).hexdigest()
            check(f'chunk-boundary-{size}', [expected, 'large.bin'], 0, '')
        (root / 'large.bin').write_bytes(payload[:-1] + b'y')
        check('large-file-changed', [expected, 'large.bin'], 1, 'MISMATCH')
        for i, invalid in enumerate(['', 'a' * 63, 'a' * 65, 'g' * 64, ' ' + ABC, ABC + '\n', '０' * 64, ABC + ' sample.bin']):
            check(f'invalid-checksum-{i}', [invalid, 'missing.bin'], 2, 'usage:')
        for i, args in enumerate([[], [ABC], [ABC, 'sample.bin', 'extra']]):
            check(f'argument-count-{i}', args, 2, 'usage:')
        if hasattr(Path, 'symlink_to'):
            (root / 'link.bin').symlink_to('sample.bin')
            check('regular-symlink', [ABC, 'link.bin'], 0, '')
            (root / 'broken-link.bin').symlink_to('missing.bin')
            check('broken-symlink', [ABC, 'broken-link.bin'], 2, 'READ ERROR')
        if hasattr(os, 'mkfifo'):
            os.mkfifo(root / 'pipe')
            check('named-pipe-rejected-without-blocking', [ABC, 'pipe'], 2, 'READ ERROR')
        # Inject a failure after opening: this is separate from OS permission tests.
        spec = importlib.util.spec_from_file_location('checksum_article', root / 'verify-sha256.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        class BrokenReader:
            def __init__(self): self.reads = 0
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self, size):
                self.reads += 1
                if self.reads == 1: return b'abc'
                raise OSError('injected mid-read failure')

        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.object(module.Path, 'is_file', return_value=True), patch.object(module.Path, 'open', return_value=BrokenReader()), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            assert module.main(['verify-sha256.py', ABC, 'sample.bin']) == 2
        assert not stdout.getvalue() and 'READ ERROR: injected mid-read failure' in stderr.getvalue()
        cases.append('injected-mid-read-error')
        # Execute the exact shell block in both articles, not a reconstructed command list.
        commands = shell_editions[0][0]
        from build_example_archives import catalog
        assert next(row for row in catalog() if row['key'] == KEY)['commands'] == commands, 'Download instructions must match the article'
        result = subprocess.run(['sh', '-c', commands], cwd=root, text=True, capture_output=True, timeout=10)
        assert result.returncode == 0 and result.stdout == 'OK\nexit=1\n' and result.stderr == 'MISMATCH\n', result
    print(json.dumps({'cases': len(cases), 'names': cases, 'pairedZIPMembersExecuted': True,
                      'articleShellBlockExecuted': True, 'python': sys.version.split()[0], 'networkRequests': 0}))


if __name__ == '__main__':
    main()
