#!/usr/bin/env python3
"""Run the WebClient test class directly extracted from the published article."""
from pathlib import Path
import os
import re
import shutil
import subprocess
import sys
import tempfile
from xml.etree import ElementTree


def main():
    if not shutil.which('gradle'):
        raise SystemExit('Gradle is required; use JDK 17 and a compatible Gradle 8.x release.')
    env=os.environ.copy()
    if sys.platform=='darwin':
        env['JAVA_HOME']=subprocess.check_output(['/usr/libexec/java_home','-v','17'],text=True).strip()
    examples=[]
    for language in ('en','ko'):
        article=Path(f'src/content/posts/{language}/2023-09-19-springboot-test-webclient.md').read_text()
        examples.append((re.findall(r'```java\n([\s\S]*?)\n```',article)[0],
                         re.findall(r'```groovy\n([\s\S]*?)\n```',article)[0]))
    if examples[0] != examples[1]:
        raise SystemExit('English and Korean WebClient code and build files must match.')
    code,build=examples[0]
    with tempfile.TemporaryDirectory(prefix='youdozi-webclient-') as directory:
        root=Path(directory);(root/'src/test/java').mkdir(parents=True)
        (root/'src/test/java/ExternalApiTest.java').write_text(code)
        (root/'settings.gradle').write_text("rootProject.name = 'article-webclient-regression'\n")
        (root/'build.gradle').write_text(build+'\n')
        subprocess.run(['gradle','-p',directory,'--no-daemon','test'],env=env,check=True,timeout=240)
        suites=[ElementTree.parse(path).getroot() for path in (root/'build/test-results/test').glob('TEST-*.xml')]
        tests=sum(int(suite.get('tests','0')) for suite in suites)
        unsuccessful=sum(int(suite.get(key,'0')) for suite in suites for key in ('failures','errors','skipped'))
        if tests != 8 or unsuccessful:
            raise SystemExit(f'Expected eight passing published tests; got {tests} tests and {unsuccessful} unsuccessful.')
        print('[ok] Eight WebClient response contracts passed using the exact Java and Gradle blocks in both editions.')

if __name__=='__main__':main()
