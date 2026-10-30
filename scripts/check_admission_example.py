#!/usr/bin/env python3
"""Execute admission semantics from the published ZIP; never generate HTTP load."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from build_example_archives import catalog, extract_example

KEY = '2026-10-31-jdk-10k-rps-architecture'
EXPECTED = ['admitted=2', 'overload=rejected', 'completed=ok,ok', 'failure=propagated', 'available=2']
NAMES = ['zero-limit-rejected', 'negative-limit-rejected', 'result-and-permit-returned',
         'checked-failure-restores-permit', 'error-restores-permit', 'interrupt-restores-after-exit',
         'dependency-gates-independent', 'rejected-work-never-executed']
CONTRACT = r'''import java.io.IOException;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.RejectedExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;

public class AdmissionContracts {
    static void check(String name, boolean condition) {
        if (!condition) throw new AssertionError(name);
        System.out.println(name);
    }
    public static void main(String[] args) throws Exception {
        for (int value : new int[]{0, -1}) {
            boolean refused = false;
            try { new AdmissionDemo.Gate(value); }
            catch (IllegalArgumentException expected) { refused = true; }
            check(value == 0 ? "zero-limit-rejected" : "negative-limit-rejected", refused);
        }
        var gate = new AdmissionDemo.Gate(1);
        check("result-and-permit-returned", gate.call(() -> "ok").equals("ok") && gate.available() == 1);
        boolean failed = false;
        try { gate.call(() -> { throw new IOException("expected"); }); }
        catch (IOException expected) { failed = expected.getMessage().equals("expected"); }
        check("checked-failure-restores-permit", failed && gate.available() == 1);
        boolean errored = false;
        try { gate.call(() -> { throw new AssertionError("expected"); }); }
        catch (AssertionError expected) { errored = expected.getMessage().equals("expected"); }
        check("error-restores-permit", errored && gate.available() == 1);

        var entered = new CountDownLatch(1);
        var exited = new CountDownLatch(1);
        var interrupted = new AtomicBoolean();
        Thread worker = Thread.ofVirtual().start(() -> {
            try {
                gate.call(() -> { entered.countDown(); new CountDownLatch(1).await(); return null; });
            } catch (InterruptedException expected) { interrupted.set(true); }
            catch (Exception unexpected) { throw new AssertionError(unexpected); }
            finally { exited.countDown(); }
        });
        if (!entered.await(5, TimeUnit.SECONDS)) throw new AssertionError("worker entry");
        worker.interrupt();
        if (!exited.await(5, TimeUnit.SECONDS)) throw new AssertionError("worker exit");
        worker.join();
        check("interrupt-restores-after-exit", interrupted.get() && gate.available() == 1);

        var independent = new AdmissionDemo.Gate(1);
        var holding = new CountDownLatch(1);
        var release = new CountDownLatch(1);
        var called = new AtomicBoolean();
        try (var tasks = Executors.newVirtualThreadPerTaskExecutor()) {
            var held = tasks.submit(() -> gate.call(() -> { holding.countDown(); release.await(); return "done"; }));
            try {
                if (!holding.await(5, TimeUnit.SECONDS)) throw new AssertionError("held entry");
                check("dependency-gates-independent", independent.call(() -> "ok").equals("ok"));
                boolean refused = false;
                try { gate.call(() -> { called.set(true); return "unexpected"; }); }
                catch (RejectedExecutionException expected) { refused = true; }
                check("rejected-work-never-executed", refused && !called.get() && gate.available() == 0);
            } finally { release.countDown(); }
            if (!held.get(5, TimeUnit.SECONDS).equals("done") || gate.available() != 1)
                throw new AssertionError("held result");
        }
    }
}
'''


def execute(args, root, env=None):
    return subprocess.run(args, cwd=root, env=env, check=True, text=True,
                          capture_output=True, timeout=60)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jdk', type=Path, help='JDK 27 home; otherwise JAVA_HOME or javac on PATH')
    args = parser.parse_args()
    jdk = args.jdk or (Path(os.environ['JAVA_HOME']) if os.environ.get('JAVA_HOME') else None)
    if not jdk:
        compiler = shutil.which('javac')
        if not compiler: raise SystemExit('JDK 27 required.')
        jdk = Path(compiler).resolve().parents[1]
    jdk = jdk.resolve(); java, javac = [str(jdk / 'bin' / tool) for tool in ['java', 'javac']]
    version = execute([javac, '-version'], Path.cwd()).stdout.strip()
    if not re.match(r'javac 27(?:[ .]|$)', version): raise SystemExit('Use JDK 27 for the recorded example.')
    code, commands = [], []
    for language in ['en', 'ko']:
        raw = Path(f'src/content/posts/{language}/{KEY}.md').read_text()
        files = re.findall(r'^### `AdmissionDemo.java`\n\n```java\n([\s\S]*?)\n```', raw, re.M)
        shell = re.findall(r'^```sh\n([\s\S]*?)\n```', raw, re.M)
        output = re.findall(r'^```text\n([\s\S]*?)\n```', raw, re.M)
        assert len(files) == len(shell) == len(output) == 1 and output[0].splitlines() == EXPECTED
        code.append(files[0]); commands.append(shell[0])
    assert code[0] == code[1] and commands[0] == commands[1]
    assert commands[0] == next(r for r in catalog() if r['key'] == KEY)['commands']
    env = os.environ.copy(); env['JAVA_HOME'] = str(jdk)
    env['PATH'] = str(jdk / 'bin') + os.pathsep + env.get('PATH', '')
    with tempfile.TemporaryDirectory(prefix='youdozi-admission-') as temporary:
        root = Path(temporary)
        extract_example(KEY, root, {'AdmissionDemo.java': code[0]})
        result = execute(['sh', '-c', commands[0]], root, env)
        assert result.stdout.splitlines() == EXPECTED and not result.stderr, result
        (root / 'AdmissionContracts.java').write_text(CONTRACT)
        execute([javac, '--release', '27', 'AdmissionContracts.java'], root)
        contracts = execute([java, 'AdmissionContracts'], root)
        assert contracts.stdout.splitlines() == NAMES and not contracts.stderr, contracts
        runtime = execute([java, '--version'], root).stdout.strip()
    print(json.dumps({'passed': True, 'cases': 1 + len(EXPECTED) + len(NAMES),
                      'articleObservations': EXPECTED, 'separateGateContracts': NAMES, 'jdk': runtime,
                      'actualZIPCodeExecuted': True, 'networkRequests': 0, 'httpLoadTestExecuted': False,
                      'tenThousandRPSAchieved': False, 'infrastructureDeployed': False,
                      'globalJDKConfigurationChanged': False}))


if __name__ == '__main__':
    main()
