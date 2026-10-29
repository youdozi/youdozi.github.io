#!/usr/bin/env python3
"""Build the bilingual Vue/Gradle example, inspect its JAR and serve its assets.

Require Gradle 8.4 and JDK/Node majors 17/24; record actual patches and npm version.
Exact JDK/Node/npm patch matching is not a prerequisite for this regression check.
"""
from pathlib import Path
from urllib.request import urlopen
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile

FILES = {
    'settings.gradle', 'build.gradle', 'src/main/java/example/Application.java',
    'frontend/project1/package.json', 'frontend/project2/package.json',
    'frontend/project1/index.html', 'frontend/project1/src/main.js', 'prepare.sh',
}


def extract(language):
    body = Path(f'src/content/posts/{language}/2021-07-23-multiple-gradle-build.md').read_text()
    blocks = re.findall(r'^### `([^`]+)`\n\n```(?:groovy|java|json|html|js|sh)\n([\s\S]*?)\n```', body, re.M)
    if len(blocks) != len(FILES) or set(dict(blocks)) != FILES:
        raise SystemExit(f'{language}: expected the eight documented project files.')
    return dict(blocks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser', action='store_true', help='Also verify the rendered Vue headings with installed Chrome')
    args = parser.parse_args()
    for tool in ('gradle', 'node', 'npm'):
        if not shutil.which(tool):
            raise SystemExit(f'{tool} is required.')
    english, korean = extract('en'), extract('ko')
    if english != korean:
        raise SystemExit('English and Korean Vue/Gradle project files must match.')
    env = os.environ.copy()
    if sys.platform == 'darwin':
        env['JAVA_HOME'] = subprocess.check_output(['/usr/libexec/java_home', '-v', '17'], text=True).strip()
    version = subprocess.check_output(['gradle', '--version'], env=env, text=True, timeout=30)
    gradle = re.search(r'^Gradle (\S+)', version, re.M)
    jvm = re.search(r'^JVM:\s+(\S+)', version, re.M)
    node = subprocess.check_output(['node', '--version'], text=True).strip()
    npm = subprocess.check_output(['npm', '--version'], text=True).strip()
    if not gradle or gradle.group(1) != '8.4' or not jvm or not jvm.group(1).startswith('17.') or not node.startswith('v24.'):
        raise SystemExit('This reproduction requires Gradle8.4/JDK17/Node24; actual tools differ.')
    print(f'[environment] Gradle8.4 JVM{jvm.group(1)} Node{node} npm{npm}', flush=True)
    chrome = shutil.which('google-chrome') or '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    if args.browser and not Path(chrome).is_file():
        raise SystemExit('--browser requires an installed Google Chrome binary.')
    with tempfile.TemporaryDirectory(prefix='youdozi-multi-frontend-') as directory:
        root = Path(directory)
        for name, code in english.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(code + '\n')
        obsolete = root / 'frontend/project1/public/obsolete.txt'
        obsolete.parent.mkdir(parents=True)
        obsolete.write_text('Fixture for stale output removal.\n')
        subprocess.run(['sh', 'prepare.sh'], cwd=root, env=env, check=True, timeout=180)
        for app in ('project1', 'project2'):
            lock = json.loads((root / f'frontend/{app}/package-lock.json').read_text())
            assert lock['packages']['']['name'] == app
            assert lock['packages']['node_modules/vue']['version'] == '3.5.44'
            assert lock['packages']['node_modules/vite']['version'] == '8.3.5'
        command = ['gradle', '-p', directory, '--no-daemon']
        subprocess.run([*command, 'clean', 'bootJar'], env=env, check=True, timeout=300)
        jar = root / 'build/libs/multi-frontend-1.0.0.jar'
        prefix = 'BOOT-INF/classes/static/'
        with zipfile.ZipFile(jar) as archive:
            assert prefix + 'project1/obsolete.txt' in archive.namelist()
        obsolete.unlink()
        subprocess.run([*command, 'bootJar'], env=env, check=True, timeout=300)
        with zipfile.ZipFile(jar) as archive:
            assert prefix + 'project1/obsolete.txt' not in archive.namelist()
            for app in ('project1', 'project2'):
                html = archive.read(prefix + app + '/index.html').decode()
                assert f'/{app}/assets/' in html
                assert (root / f'frontend/{app}/node_modules/vue/package.json').is_file()
        assert not (root / 'src/main/resources/static').exists(), 'Generated files must stay outside source resources.'
        java = str(Path(env['JAVA_HOME']) / 'bin/java') if env.get('JAVA_HOME') else shutil.which('java')
        with (root / 'boot.log').open('w') as log:
            process = subprocess.Popen([java, '-jar', str(jar), '--server.port=0'], cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT)
            try:
                deadline = time.monotonic() + 40
                port = None
                while time.monotonic() < deadline:
                    text = (root / 'boot.log').read_text()
                    match = re.search(r'Tomcat started on port (\d+)', text)
                    if match:
                        port = int(match.group(1))
                        break
                    if process.poll() is not None:
                        raise AssertionError('Packaged application exited before startup: ' + text[-2000:])
                    time.sleep(0.2)
                assert port, 'Packaged server did not start within 40 seconds.'
                for app in ('project1', 'project2'):
                    url = f'http://127.0.0.1:{port}/{app}/index.html'
                    with urlopen(url, timeout=10) as response:
                        assert response.status == 200
                        html = response.read().decode()
                    assets = re.findall(r'(?:src|href)="(/' + app + r'/assets/[^\"]+)"', html)
                    assert assets, (app, html)
                    for asset in assets:
                        with urlopen(f'http://127.0.0.1:{port}' + asset, timeout=10) as response:
                            assert response.status == 200 and response.read()
                    if args.browser:
                        rendered = subprocess.run([chrome, '--headless=new', '--disable-background-networking', '--no-first-run',
                            '--no-default-browser-check', '--virtual-time-budget=5000', '--dump-dom',
                            f'--user-data-dir={root / (app + "-chrome")}', url], capture_output=True, text=True, check=True, timeout=40)
                        assert f'<h1>Vue app at /{app}/</h1>' in rendered.stdout, app
            finally:
                process.terminate()
                try:
                    process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
    print('[ok] Two independent npm installs/builds; correct bootJar paths; stale file removed without clean; HTML and assets served over HTTP.')
    print('[browser] ' + ('Both Vue headings rendered in Chrome.' if args.browser else 'Not run; pass --browser to verify rendering.'))


if __name__ == '__main__':
    main()
