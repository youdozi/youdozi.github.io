#!/usr/bin/env python3
"""Execute the bilingual shell examples with local HTTP and boundary fixtures."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading

ARTICLES = {
    'greet.sh': '2023-09-20-linux-shellscript-function-error',
    'version-compare.sh': '2023-11-17-linux-shellscript-version-compare',
    'latest-release.sh': '2023-09-23-linux-shellscript-github-latest',
}


def extract(filename, slug):
    versions = []
    for language in ('en', 'ko'):
        body = Path(f'src/content/posts/{language}/{slug}.md').read_text()
        found = re.findall(r'^### `' + re.escape(filename) + r'`\n\n```sh\n([\s\S]*?)\n```', body, re.M)
        if len(found) != 1:
            raise SystemExit(f'{language}/{slug}: expected one complete {filename}.')
        versions.append(found[0])
    if versions[0] != versions[1]:
        raise SystemExit(f'{slug}: English and Korean code must match.')
    return versions[0]


def main():
    for tool in ('sh', 'python3', 'curl', 'jq'):
        if not shutil.which(tool):
            raise SystemExit(f'{tool} is required.')
    counts = {'functions': 0, 'versions': 0, 'releaseHTTP': 0, 'releaseArguments': 0}
    with tempfile.TemporaryDirectory(prefix='youdozi-shell-examples-') as directory:
        root = Path(directory)
        for filename, slug in ARTICLES.items():
            (root / filename).write_text(extract(filename, slug) + '\n')
            subprocess.run(['sh', '-n', str(root / filename)], check=True, timeout=10)

        def run(filename, args=(), env=None):
            return subprocess.run(['sh', str(root / filename), *args], cwd=root, env=env, capture_output=True, text=True, timeout=30)

        for args, status, expected in [(['Ada Lovelace'], 0, 'Hello, Ada Lovelace\n'),
                                       (['Ada *'], 0, 'Hello, Ada *\n'), ([], 2, ''), (['a', 'b'], 2, '')]:
            result = run('greet.sh', args)
            assert result.returncode == status and result.stdout == expected, (args, result)
            if status:
                assert 'usage:' in result.stderr
            counts['functions'] += 1
        comparisons = [('1.10.5', '1.3.1', '>'), ('1.2', '1.2.0', '='), ('1.1000', '2.0', '<'),
                       ('1.2.0.0.1', '1.2', '>'), ('01.002', '1.2', '='), ('0', '0.0', '='),
                       ('99999999999999999999999', '2', '>'), ('1.0.0.0.0.1', '1.0.0.0.0.2', '<')]
        for left, right, operator in comparisons:
            result = run('version-compare.sh', [left, right])
            assert result.returncode == 0 and result.stdout == f'{left} {operator} {right}\n', result
            counts['versions'] += 1
        for args in [[], ['1'], ['1', '2', '3'], ['', '1'], ['1..2', '1.2'], ['v1.2', '1.2'],
                     ['1.2-rc1', '1.2'], ['1.2+build', '1.2'], ['-1', '0'], ['１.２', '1.2']]:
            result = run('version-compare.sh', args)
            assert result.returncode == 2 and not result.stdout and result.stderr, result
            counts['versions'] += 1
        if hasattr(sys, 'get_int_max_str_digits'):
            result = run('version-compare.sh', ['9' * 5000, '1'], {**os.environ, 'PYTHONINTMAXSTRDIGITS': '4300'})
            assert result.returncode == 2 and 'conversion limit' in result.stderr, result.returncode
            counts['versions'] += 1

        asset = {'name': 'OpenJDK17U-jdk_x64_linux_hotspot_fixture.tar.gz',
                 'browser_download_url': 'https://github.com/example/releases/download/fixture/jdk.tar.gz'}
        release = {'tag_name': 'fixture-17+1', 'assets': [asset]}
        fixtures = {
            'success': (200, json.dumps(release)),
            'forbidden': (403, '{"message":"rate limit exceeded"}'),
            'missing': (404, '{"message":"not found"}'),
            'bad-json': (200, '<html>not JSON</html>'), 'empty': (200, ''),
            'multiple-json': (200, '{}\n{}'), 'null': (200, 'null'),
            'no-assets': (200, json.dumps({**release, 'assets': []})),
            'ambiguous': (200, json.dumps({**release, 'assets': [asset, asset]})),
            'wrong-platform': (200, json.dumps({**release, 'assets': [{**asset, 'name': 'OpenJDK17U-jdk_aarch64_linux_hotspot_fixture.tar.gz'}]})),
            'no-tag': (200, json.dumps({**release, 'tag_name': ''})),
            'no-url': (200, json.dumps({**release, 'assets': [{**asset, 'browser_download_url': ''}]})),
        }

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass
            def do_GET(self):
                assert self.path.endswith('/repos/adoptium/temurin17-binaries/releases/latest'), self.path
                assert self.headers.get('Accept') == 'application/vnd.github+json'
                assert self.headers.get('X-GitHub-Api-Version') == '2026-03-10'
                case = self.path.split('/')[1]
                if case == 'drop':
                    self.connection.shutdown(socket.SHUT_RDWR)
                    self.close_connection = True
                    return
                status, data = fixtures[case]
                body = data.encode()
                self.send_response(status)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            for case in [*fixtures, 'drop']:
                env = {**os.environ, 'GITHUB_API_URL': f'http://127.0.0.1:{server.server_port}/{case}'}
                result = run('latest-release.sh', [] if case == 'success' else ['adoptium/temurin17-binaries'], env)
                if case == 'success':
                    assert result.returncode == 0, result.stderr
                    assert json.loads(result.stdout) == {'tag_name': release['tag_name'], 'download_url': asset['browser_download_url']}
                else:
                    assert result.returncode != 0 and not result.stdout, (case, result)
                counts['releaseHTTP'] += 1
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
        for args in [[''], ['owner'], ['a/b/c'], ['/repo'], ['owner/'], ['a b/repo'], ['a/b', 'extra']]:
            result = run('latest-release.sh', args)
            assert result.returncode == 2 and not result.stdout and 'usage:' in result.stderr, result
            counts['releaseArguments'] += 1
    print('[ok] Shell examples: ' + json.dumps(counts) + '; no live GitHub API or downloads used.')


if __name__ == '__main__':
    main()
