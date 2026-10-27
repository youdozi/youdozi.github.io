#!/usr/bin/env python3
"""Run the Querydsl/Jakarta project extracted from both article editions."""
from pathlib import Path
import os
import re
import shutil
import subprocess
import sys
import tempfile
from xml.etree import ElementTree


FILES = {
    'settings.gradle', 'build.gradle',
    'src/main/java/example/Application.java',
    'src/main/java/example/Employee.java',
    'src/test/java/example/EmployeeQueryTest.java',
}


def extract(language):
    article = Path(f'src/content/posts/{language}/2023-09-09-springboot3-querydsl.md').read_text()
    blocks = re.findall(r'^### `([^`]+)`\n\n```(?:groovy|java)\n([\s\S]*?)\n```', article, re.M)
    files = dict(blocks)
    if set(files) != FILES or len(blocks) != len(FILES):
        raise SystemExit(f'{language}: expected exactly the five documented project files.')
    return files


def main():
    if not shutil.which('gradle'):
        raise SystemExit('Gradle is required; the reproduction uses Gradle 8.4 and JDK 17.')
    english, korean = extract('en'), extract('ko')
    if english != korean:
        raise SystemExit('English and Korean Querydsl project files must match.')
    env = os.environ.copy()
    if sys.platform == 'darwin':
        env['JAVA_HOME'] = subprocess.check_output(['/usr/libexec/java_home', '-v', '17'], text=True).strip()
    version = subprocess.check_output(['gradle', '--version'], env=env, text=True, timeout=30)
    gradle = re.search(r'^Gradle (\S+)', version, re.M)
    jvm = re.search(r'^JVM:\s+(\S+)', version, re.M)
    if not gradle or gradle.group(1) != '8.4' or not jvm or not jvm.group(1).startswith('17.'):
        raise SystemExit('This reproduction requires Gradle 8.4 running on JDK 17. Check gradle --version.')
    print(f'[environment] Gradle {gradle.group(1)}; JVM {jvm.group(1)} (actual patch version).', flush=True)
    with tempfile.TemporaryDirectory(prefix='youdozi-querydsl-') as directory:
        root = Path(directory)
        for name, code in english.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(code + '\n')
        for iteration in range(1, 3):
            subprocess.run(['gradle', '-p', directory, '--no-daemon', 'clean', 'test'], env=env, check=True, timeout=240)
            generated = root / 'build/generated/sources/annotationProcessor/java/main/example/QEmployee.java'
            compiled = root / 'build/classes/java/main/example/QEmployee.class'
            if not generated.is_file() or not compiled.is_file():
                raise SystemExit('The documented Q-type source and class were not generated.')
            if list((root / 'src').rglob('QEmployee.*')):
                raise SystemExit('Generated Q types must remain outside the handwritten source tree.')
            suites = [ElementTree.parse(path).getroot() for path in (root / 'build/test-results/test').glob('TEST-*.xml')]
            tests = sum(int(suite.get('tests', '0')) for suite in suites)
            unsuccessful = sum(int(suite.get(key, '0')) for suite in suites for key in ('errors', 'failures', 'skipped'))
            if tests != 2 or unsuccessful:
                raise SystemExit(f'Expected two passing H2 query tests; got {tests} tests and {unsuccessful} unsuccessful.')
            print(f'[ok] Clean run {iteration}: generated and compiled QEmployee; both H2 query tests passed.')


if __name__ == '__main__':
    main()
