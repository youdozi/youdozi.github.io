#!/usr/bin/env python3
"""Run the WebClient test class directly extracted from the published article."""
from pathlib import Path
import os
import re
import shutil
import subprocess
import sys
import tempfile


def main():
    if not shutil.which('gradle'):
        raise SystemExit('Gradle is required; use JDK 17 and a compatible Gradle 8.x release.')
    env=os.environ.copy()
    if sys.platform=='darwin':
        env['JAVA_HOME']=subprocess.check_output(['/usr/libexec/java_home','-v','17'],text=True).strip()
    article=Path('src/content/posts/ko/2023-09-19-springboot-test-webclient.md').read_text()
    code=re.findall(r'```java\n([\s\S]*?)\n```',article)[0]
    with tempfile.TemporaryDirectory(prefix='youdozi-webclient-') as directory:
        root=Path(directory);(root/'src/test/java').mkdir(parents=True)
        (root/'src/test/java/ExternalApiTest.java').write_text(code)
        (root/'settings.gradle').write_text("rootProject.name = 'article-webclient-regression'\n")
        (root/'build.gradle').write_text("""plugins { id 'java' }
repositories { mavenCentral() }
dependencies {
    testImplementation platform('org.springframework.boot:spring-boot-dependencies:3.5.7')
    testImplementation 'org.springframework.boot:spring-boot-starter-webflux'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testImplementation 'io.projectreactor:reactor-test'
    testImplementation 'com.squareup.okhttp3:mockwebserver:4.12.0'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
test { useJUnitPlatform() }
""")
        subprocess.run(['gradle','-p',directory,'--no-daemon','test'],env=env,check=True,timeout=240)
        print('[ok] Published WebClient tests passed for JSON 200, HTML 200 and HTML 500.')

if __name__=='__main__':main()
