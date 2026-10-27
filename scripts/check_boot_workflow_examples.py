#!/usr/bin/env python3
"""Run the paired Boot project through generation, HTTP, and Lombok stages.

Initializr/IDE UI are not exercised. Bootstrap a pinned Gradle distribution with
the installed Gradle, or pass --gradle to an existing Gradle 9.8.2 executable.
"""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
from urllib.error import HTTPError
from urllib.request import urlopen
from xml.etree import ElementTree
from zipfile import ZipFile


def extract(slug, expected):
    editions = []
    dependency_blocks = []
    for language in ('en', 'ko'):
        text = Path(f'src/content/posts/{language}/{slug}.md').read_text()
        blocks = re.findall(r'^### `([^`]+)`\n\n```(?:groovy|java)\n([\s\S]*?)\n```', text, re.M)
        files = dict(blocks)
        assert set(files) == expected and len(files) == len(blocks), (slug, language, files.keys())
        editions.append(files)
        dependency_blocks.append(re.findall(r'^```groovy\n(dependencies \{[\s\S]*?)\n```', text, re.M))
    assert editions[0] == editions[1], f'{slug}: English and Korean project files differ'
    assert dependency_blocks[0] == dependency_blocks[1], f'{slug}: dependency blocks differ'
    return editions[0], dependency_blocks[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--gradle', help='Existing Gradle 9.8.2 executable; otherwise bootstrap a Wrapper')
    args = parser.parse_args()
    base, _ = extract('2023-09-07-springboot-initializer', {
        'settings.gradle', 'build.gradle', 'src/main/java/example/demo/DemoApplication.java',
        'src/test/java/example/demo/DemoApplicationTests.java',
    })
    http, _ = extract('2023-09-10-springboot-intellij-import', {
        'src/main/java/example/demo/GreetingController.java', 'src/test/java/example/demo/GreetingHttpTest.java',
    })
    lombok, dependencies = extract('2023-09-15-springboot-intellij-lombok', {
        'src/main/java/example/demo/Greeting.java', 'src/main/java/example/demo/GreetingController.java',
        'src/test/java/example/demo/LombokGenerationTest.java',
    })
    assert len(dependencies) == 1
    env = os.environ.copy()
    if sys.platform == 'darwin':
        env['JAVA_HOME'] = subprocess.check_output(['/usr/libexec/java_home', '-v', '17'], text=True).strip()
    elif env.get('JDK17_HOME'):
        env['JAVA_HOME'] = env['JDK17_HOME']
    if not env.get('JAVA_HOME'):
        raise SystemExit('Set JAVA_HOME or JDK17_HOME to JDK 17')
    java = str(Path(env['JAVA_HOME']) / 'bin/java')
    java_version = subprocess.check_output([java, '-version'], stderr=subprocess.STDOUT, text=True)
    assert re.search(r'version "17\.', java_version), java_version
    with tempfile.TemporaryDirectory(prefix='youdozi-boot-workflow-') as directory:
        root = Path(directory)
        project = root / 'project'
        project.mkdir()
        if args.gradle:
            launcher = [str(Path(args.gradle).resolve())]
        else:
            bootstrap = root / 'bootstrap'
            bootstrap.mkdir()
            (bootstrap / 'settings.gradle').write_text("rootProject.name = 'wrapper-bootstrap'\n")
            (bootstrap / 'build.gradle').write_text('')
            subprocess.run(['gradle', '-p', str(bootstrap), '--no-daemon', 'wrapper', '--gradle-version',
                            '9.8.2', '--distribution-type', 'bin'], env=env, check=True, timeout=180)
            launcher = ['sh', str(bootstrap / 'gradlew')]
        version = subprocess.check_output(launcher + ['--version'], text=True, env=env, timeout=240)
        assert re.search(r'^Gradle 9\.8\.2$', version, re.M), version
        print('[environment] Gradle 9.8.2;', java_version.splitlines()[0], flush=True)

        def write(files):
            for name, code in files.items():
                path = project / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(code + '\n')

        def run(*tasks, expected_failure=None):
            result = subprocess.run(launcher + ['-p', str(project), '--no-daemon', '--console=plain', *tasks],
                                    env=env, capture_output=True, text=True, timeout=240)
            output = result.stdout + result.stderr
            if expected_failure:
                assert result.returncode != 0 and expected_failure in output and 'error:' in output, output
                print('[ok] Expected compilation failure:', expected_failure, flush=True)
            elif result.returncode:
                raise SystemExit(output)
            return output

        def test_count(count):
            suites = [ElementTree.parse(p).getroot() for p in project.glob('build/test-results/test/TEST-*.xml')]
            tests = sum(int(s.get('tests', 0)) for s in suites)
            unsuccessful = sum(int(s.get(k, 0)) for s in suites for k in ('failures', 'errors', 'skipped'))
            assert tests == count and unsuccessful == 0, (tests, unsuccessful, count)
            print(f'[ok] Stage with {count} tests passed.', flush=True)

        write(base)
        run('clean', 'test')
        test_count(1)
        write(http)
        run('clean', 'test')
        test_count(3)
        write(lombok)
        final_build = base['build.gradle'] + '\n' + dependencies[0]
        write({'build.gradle': final_build})
        run('clean', 'test')
        test_count(5)

        write({'build.gradle': final_build.replace("    annotationProcessor 'org.projectlombok:lombok'\n", '')})
        run('clean', 'compileJava', expected_failure=':compileJava FAILED')
        write({'build.gradle': final_build.replace("    testAnnotationProcessor 'org.projectlombok:lombok'\n", '')})
        run('clean', 'test', expected_failure=':compileTestJava FAILED')
        write({'build.gradle': final_build})
        run('clean', 'test', 'bootJar')
        test_count(5)

        framework = run('dependencyInsight', '--configuration', 'runtimeClasspath', '--dependency', 'spring-core')
        processor = run('dependencyInsight', '--configuration', 'annotationProcessor', '--dependency', 'lombok')
        assert 'org.springframework:spring-core:7.0.10' in framework, framework
        assert 'org.projectlombok:lombok:1.18.48' in processor, processor
        for language in ('en', 'ko'):
            history = Path(f'src/content/posts/{language}/2023-09-13-springboot-history.md').read_text()
            assert 'spring-core' in history and '7.0.10' in history and '1.18.48' in history

        jar = project / 'build/libs/demo-0.0.1-SNAPSHOT.jar'
        with ZipFile(jar) as archive:
            assert not any(n.startswith('BOOT-INF/lib/lombok-') for n in archive.namelist())
            assert 'BOOT-INF/classes/example/demo/Greeting.class' in archive.namelist()
        log_path = root / 'server.log'
        with log_path.open('w') as log:
            process = subprocess.Popen([java, '-jar', str(jar), '--server.port=0'], stdout=log,
                                       stderr=subprocess.STDOUT, env=env)
            try:
                deadline = time.monotonic() + 50
                port = None
                while time.monotonic() < deadline:
                    content = log_path.read_text()
                    match = re.search(r'Tomcat started on port (\d+)', content)
                    if match:
                        port = int(match[1])
                        break
                    if process.poll() is not None:
                        raise SystemExit(content)
                    time.sleep(0.2)
                assert port, 'Packaged server did not start in time'
                with urlopen(f'http://127.0.0.1:{port}/greeting', timeout=10) as response:
                    assert response.status == 200
                    assert json.loads(response.read()) == {'message': 'Hello, Gradle'}
                try:
                    urlopen(f'http://127.0.0.1:{port}/missing', timeout=10)
                    raise AssertionError('Missing path unexpectedly returned success')
                except HTTPError as error:
                    assert error.code == 404
            finally:
                process.terminate()
                try:
                    process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
    print(json.dumps({'stageTests': [1, 3, 5], 'processorFailuresConfirmed': 2,
                      'restoredTests': 5, 'packagedHttp': [200, 404], 'lombokInRuntimeJar': False,
                      'initializrRequestsInChecker': 0, 'ideUiVerified': False, 'result': 'passed'}))


if __name__ == '__main__':
    main()
