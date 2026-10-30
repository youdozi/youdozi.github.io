#!/usr/bin/env python3
"""Execute source-derived read-only PHP/Node collectors; no exploit or service changes."""
import json
from pathlib import Path
import re
import subprocess
import tempfile

from build_example_archives import extract_example

PHP_KEY = '2026-10-30-php2shell-runtime-patching'
NODE_KEY = '2026-10-30-node2shell-brotli-runtime-patching'
# Official multi-platform artifacts, checked on 2026-10-30. These are reproduction
# inputs, not latest production version recommendations or vulnerability probes.
PHP_IMAGE = 'php@sha256:54b467ede1db96c66675e7b78457dd43729d0e7be31978d4a1e5c069ceabcf76'
NODE_IMAGE = 'node@sha256:be8204d4bd327363357f532187b752ff62759c31bedf98e9e18fc08c9cbd605c'


def paired_files(key, languages):
    editions, commands = [], []
    for language in ('en', 'ko'):
        raw = Path(f'src/content/posts/{language}/{key}.md').read_text()
        pairs = re.findall(r'^### `([^`]+)`\n\n```(?:' + '|'.join(languages) + r')\n([\s\S]*?)\n```', raw, re.M)
        assert pairs and len(pairs) == len(dict(pairs)), 'Unique article file selectors required'
        editions.append(dict(pairs))
        commands.append(re.findall(r'^```sh\n([\s\S]*?)\n```', raw, re.M))
    assert editions[0] == editions[1] and commands[0] == commands[1], 'Paired code and commands must match'
    from build_example_archives import catalog
    assert commands[0] == [next(row for row in catalog() if row['key'] == key)['commands']]
    return editions[0]


def run(root, image, args):
    result = subprocess.run([
        'docker', 'run', '--rm', '--network', 'none', '--read-only',
        '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
        '--mount', f'type=bind,src={root},dst=/work,readonly', '--workdir', '/work',
        image, *args,
    ], check=True, capture_output=True, text=True, timeout=180)
    return json.loads(result.stdout)


def main():
    cases = []
    with tempfile.TemporaryDirectory(prefix='youdozi-runtime-evidence-') as directory:
        root = Path(directory)
        php = root / 'php'; php.mkdir()
        extract_example(PHP_KEY, php, paired_files(PHP_KEY, ['php']))
        first = run(php, PHP_IMAGE, ['php', 'runtime-evidence.php'])
        expected = {'scope', 'pid', 'version', 'sapi', 'binary', 'loadedIni', 'uploadProgress', 'serializeHandler'}
        assert set(first) == expected and first['scope'] == 'this-cli-process-only'
        assert first['sapi'] == 'cli' and first['version'] == '8.4.27'
        assert first['pid'] > 0 and first['binary'].startswith('/')
        cases.append('php-cli-json-schema-and-identity')
        clean = run(php, PHP_IMAGE, ['php', '-n', 'runtime-evidence.php'])
        assert clean['loadedIni'] is None and clean['uploadProgress'] == '1'
        cases.append('php-no-ini-default')
        disabled = run(php, PHP_IMAGE, ['php', '-n', '-d', 'session.upload_progress.enabled=0', 'runtime-evidence.php'])
        assert disabled['loadedIni'] is None and disabled['uploadProgress'] == '0'
        cases.append('php-per-invocation-override')
        again = run(php, PHP_IMAGE, ['php', '-n', 'runtime-evidence.php'])
        assert again['uploadProgress'] == clean['uploadProgress']
        cases.append('php-override-does-not-persist')
        # Loopback is available inside the network-isolated container. No host port
        # is published, and the child server is terminated in finally.
        web_guard = r'''
$p = proc_open([PHP_BINARY, '-n', '-S', '127.0.0.1:8080', '-t', '/work'],
    [0 => ['pipe', 'r'], 1 => ['file', '/dev/null', 'w'], 2 => ['file', '/dev/null', 'w']], $pipes);
if (!is_resource($p)) { throw new RuntimeException('server did not start'); }
try {
    fclose($pipes[0]);
    $context = stream_context_create(['http' => ['ignore_errors' => true, 'timeout' => 1]]);
    for ($i = 0; $i < 30; $i++) {
        $body = @file_get_contents('http://127.0.0.1:8080/runtime-evidence.php', false, $context);
        if ($body !== false) { break; }
        usleep(100000);
    }
    if ($body !== '' || !isset($http_response_header[0]) || !str_contains($http_response_header[0], ' 404 ')) {
        throw new RuntimeException('web guard failed');
    }
    echo json_encode(['webStatus' => 404, 'body' => $body], JSON_THROW_ON_ERROR);
} finally {
    proc_terminate($p);
    proc_close($p);
}
'''
        web = run(php, PHP_IMAGE, ['php', '-n', '-r', web_guard])
        assert web == {'webStatus': 404, 'body': ''}
        cases.append('php-web-sapi-returns-404-without-evidence')
        node = root / 'node'; node.mkdir()
        extract_example(NODE_KEY, node, paired_files(NODE_KEY, ['javascript']))
        record = run(node, NODE_IMAGE, ['node', 'app.mjs'])
        assert set(record) == {'scope', 'pid', 'executable', 'node', 'brotliLabel', 'platform', 'arch'}
        assert record['scope'] == 'this-process-only' and record['pid'] > 0
        assert record['node'] == 'v24.22.1' and record['brotliLabel'] == '1.2.0'
        assert record['executable'].startswith('/') and record['platform'] == 'linux'
        cases.append('node-fixed-runtime-retains-brotli-label')
        same_process = "import {runtimeEvidence} from './runtime-evidence.mjs'; const e=runtimeEvidence(); if(e.pid!==process.pid || e.executable!==process.execPath)throw Error('identity mismatch'); console.log(JSON.stringify({sameProcess:true}));"
        assert run(node, NODE_IMAGE, ['node', '--input-type=module', '-e', same_process]) == {'sameProcess': True}
        cases.append('node-import-is-quiet-and-collects-caller-process')
    print(json.dumps({'passed': True, 'cases': len(cases), 'names': cases,
                      'phpImage': PHP_IMAGE, 'nodeImage': NODE_IMAGE,
                      'externalNetworkDuringCodeExecution': False, 'exploitReproduction': False,
                      'productionServicesInspectedOrChanged': False}))


if __name__ == '__main__':
    main()
