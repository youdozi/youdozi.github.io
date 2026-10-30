#!/usr/bin/env python3
"""Run the actual paired ScopedValue ZIP and separate JDK 25 API contracts."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from build_example_archives import catalog, extract_example

KEY = '2026-10-31-jdk25-scopedvalue'
EXPECTED = [
    'virtual=true', 'before=false', 'outer=tenant-a/trace-123',
    'nested=tenant-b/trace-123', 'restored=tenant-a/trace-123',
    'after-failure=tenant-a/trace-123', 'plain-child-bound=false',
    'result=tenant-a/trace-123', 'after=false', 'outside=NoSuchElementException',
]
CONTRACT_NAMES = [
    'carrier-does-not-bind', 'null-binding-distinct-from-unbound', 'orElse-null-rejected',
    'checked-exception-propagated', 'checked-exit-unbound',
    'simultaneous-virtual-bindings-isolated', 'reused-worker-unbound-after-failure',
]
# Separate API tests; not extra code claimed to be part of the article/ZIP.
CONTRACT = r'''import java.io.IOException;
import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class ScopedValueContracts {
    private static final ScopedValue<String> KEY = ScopedValue.newInstance();
    private static void check(String name, boolean condition) {
        if (!condition) throw new AssertionError(name);
        System.out.println(name);
    }
    public static void main(String[] args) throws Exception {
        var carrier = ScopedValue.where(KEY, "unused");
        check("carrier-does-not-bind", !KEY.isBound() && carrier.get(KEY).equals("unused"));
        check("null-binding-distinct-from-unbound",
            ScopedValue.where(KEY, null).call(() -> KEY.isBound() && KEY.get() == null)
                && !KEY.isBound());
        boolean nullRejected = false;
        try { KEY.orElse(null); }
        catch (NullPointerException expected) { nullRejected = true; }
        check("orElse-null-rejected", nullRejected);
        boolean checkedPropagated = false;
        try {
            ScopedValue.where(KEY, "checked").call(() -> { throw new IOException("expected"); });
        } catch (IOException expected) { checkedPropagated = expected.getMessage().equals("expected"); }
        check("checked-exception-propagated", checkedPropagated);
        check("checked-exit-unbound", !KEY.isBound());

        var barrier = new CyclicBarrier(2);
        try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
            var left = executor.submit(() -> ScopedValue.where(KEY, "left").call(() -> {
                barrier.await(10, TimeUnit.SECONDS);
                return KEY.get();
            }));
            var right = executor.submit(() -> ScopedValue.where(KEY, "right").call(() -> {
                barrier.await(10, TimeUnit.SECONDS);
                return KEY.get();
            }));
            check("simultaneous-virtual-bindings-isolated",
                left.get(10, TimeUnit.SECONDS).equals("left") &&
                right.get(10, TimeUnit.SECONDS).equals("right"));
        }
        try (var worker = Executors.newSingleThreadExecutor()) {
            long id = worker.submit(() -> {
                try {
                    ScopedValue.where(KEY, "failed").run(() -> { throw new IllegalStateException("expected"); });
                } catch (IllegalStateException expected) {
                    if (!expected.getMessage().equals("expected")) throw expected;
                }
                if (KEY.isBound()) throw new AssertionError("failure cleanup");
                return Thread.currentThread().threadId();
            }).get(10, TimeUnit.SECONDS);
            check("reused-worker-unbound-after-failure", worker.submit(() ->
                Thread.currentThread().threadId() == id && !KEY.isBound()
            ).get(10, TimeUnit.SECONDS));
        }
    }
}
'''


def execute(args, root, env=None):
    return subprocess.run(args, cwd=root, env=env, check=True, text=True,
                          capture_output=True, timeout=60)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jdk', type=Path, help='JDK 25 home; otherwise JAVA_HOME or javac on PATH')
    args = parser.parse_args()
    configured = args.jdk or (Path(os.environ['JAVA_HOME']) if os.environ.get('JAVA_HOME') else None)
    if not configured:
        compiler = shutil.which('javac')
        if not compiler: raise SystemExit('JDK 25 is required.')
        configured = Path(compiler).resolve().parents[1]
    jdk = configured.resolve()
    java, javac = [str(jdk / 'bin' / name) for name in ['java', 'javac']]
    version = execute([javac, '-version'], Path.cwd()).stdout.strip()
    if not re.match(r'javac 25(?:[ .]|$)', version): raise SystemExit('Use JDK 25 for the recorded final API checks.')
    code, commands = [], []
    for language in ('en', 'ko'):
        text = Path(f'src/content/posts/{language}/{KEY}.md').read_text()
        files = re.findall(r'^### `ScopedContextExample.java`\n\n```java\n([\s\S]*?)\n```', text, re.M)
        shell = re.findall(r'^```sh\n([\s\S]*?)\n```', text, re.M)
        output = re.findall(r'^```text\n([\s\S]*?)\n```', text, re.M)
        assert len(files) == len(shell) == len(output) == 1
        assert output[0].splitlines() == EXPECTED and '--enable-preview' not in shell[0]
        code.append(files[0]); commands.append(shell[0])
    assert code[0] == code[1] and commands[0] == commands[1]
    assert commands[0] == next(r for r in catalog() if r['key'] == KEY)['commands']
    env = os.environ.copy(); env['JAVA_HOME'] = str(jdk)
    env['PATH'] = str(jdk / 'bin') + os.pathsep + env.get('PATH', '')
    with tempfile.TemporaryDirectory(prefix='youdozi-scopedvalue-') as directory:
        root = Path(directory)
        extract_example(KEY, root, {'ScopedContextExample.java': code[0]})
        result = execute(['sh', '-c', commands[0]], root, env)
        assert result.stdout.splitlines() == EXPECTED and not result.stderr, result
        (root / 'ScopedValueContracts.java').write_text(CONTRACT)
        execute([javac, '--release', '25', 'ScopedValueContracts.java'], root, env)
        contracts = execute([java, 'ScopedValueContracts'], root, env)
        assert contracts.stdout.splitlines() == CONTRACT_NAMES and not contracts.stderr, contracts
        runtime = execute([java, '--version'], root, env).stdout.strip()
    print(json.dumps({'passed': True, 'cases': 1 + len(EXPECTED) + len(CONTRACT_NAMES),
                      'articleCases': ['literal-compile-and-run-without-preview', *EXPECTED],
                      'separateAPIContracts': CONTRACT_NAMES, 'jdk': runtime,
                      'actualZIPCodeExecuted': True, 'previewFlags': False,
                      'structuredTaskScopeInheritanceExecuted': False, 'frameworkIntegrationTested': False,
                      'performanceMeasured': False, 'networkRequests': 0, 'globalJDKConfigurationChanged': False}))


if __name__ == '__main__':
    main()
