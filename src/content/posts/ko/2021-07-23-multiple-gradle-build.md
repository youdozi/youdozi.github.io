---
title: "Gradle로 여러 Vue 앱을 Spring Boot JAR에 패키징하기"
language: "ko"
translationKey: "2021-07-23-multiple-gradle-build"
routeSlug: "2021-07-23-multiple-gradle-build"
kind: "post"
publishedAt: "2021-07-22T18:00:00.000Z"
categories:
  - "springboot"
tags:
  - "gradle"
  - "vue"
  - "build"
  - "SpringBoot"
legacyUrl: "/springboot/multiple-gradle-build/"
legacySource: "_posts/gradle/2021-07-23-multiple-gradle-build.markdown"
updatedAt: "2026-10-27T02:14:35+00:00"
reviewedAt: "2026-10-27"
reviewStatus: "revised"
reviewScope: "공식 문서 대조 및 원고 실행 예제 검증"
archiveBodySha256: "2237b16a9085e6bf2b6d52a2f67e59fe7e64e8cf6a170b564e74de62c9f45280"
reviewSources:
  - "https://vite.dev/guide/"
  - "https://vite.dev/guide/build.html"
  - "https://docs.gradle.org/current/userguide/working_with_files.html"
  - "https://docs.spring.io/spring-boot/3.5/gradle-plugin/packaging.html"
description: "Vue 앱별 npm ci·빌드 태스크를 분리하고 Gradle Sync와 bootJar로 패키징합니다. 경로별 자산 제공과 오래된 산출물 제거를 실행 예제로 확인합니다."
---
여러 Vue 앱을 Spring Boot JAR에 넣을 때는 앱별 `npm ci`와 빌드 태스크를 분리하고, 생성 파일을 `build/` 아래에 모은 뒤 `bootJar`에 추가합니다. 한 앱의 설치 태스크를 다른 앱들이 공유하게 하거나 빌드 결과를 `src/main/resources`에 직접 쓰지 않습니다.

이 예제는 두 앱을 `/project1/index.html`, `/project2/index.html`에서 제공하는 실행 가능한 구성을 다룹니다. 재현 환경은 JDK 17.0.8.1, Gradle 8.4, Node 24.13.0/npm 11.6.2, Boot 3.5.7, Vue 3.5.44, Vite 8.3.5입니다. 버전을 고정한 재현 예제이며 현재 운영 조합의 권장은 아닙니다. [Vite 실행 조건](https://vite.dev/guide/)과 선택한 Boot 릴리스의 조건은 별도로 확인하세요.

## 앱별 태스크와 패키징 구성

빈 프로젝트에 다음 파일을 저장합니다. 두 앱은 별도 `package.json`·lockfile·`node_modules`·`dist`를 가집니다. `prepare.sh`가 공통 HTML·JS를 두 번째 앱에 복사하고 두 lockfile을 생성합니다.

### `settings.gradle`

```groovy
rootProject.name = 'multi-frontend'
```

### `build.gradle`

```groovy
plugins {
    id 'java'
    id 'org.springframework.boot' version '3.5.7'
}
group = 'example'
version = '1.0.0'
repositories { mavenCentral() }
dependencies {
    implementation platform('org.springframework.boot:spring-boot-dependencies:3.5.7')
    implementation 'org.springframework.boot:spring-boot-starter-web'
}

def apps = ['project1', 'project2']
def npmCommand = System.getProperty('os.name').toLowerCase().contains('windows') ? 'npm.cmd' : 'npm'
def frontendBuilds = apps.collect { app ->
    def frontend = layout.projectDirectory.dir("frontend/${app}")
    def install = tasks.register("${app}NpmCi", Exec) {
        workingDir frontend
        commandLine npmCommand, 'ci', '--no-audit', '--no-fund'
        inputs.files(frontend.file('package.json'), frontend.file('package-lock.json'))
        outputs.dir(frontend.dir('node_modules'))
    }
    tasks.register("${app}Build", Exec) {
        dependsOn install
        workingDir frontend
        commandLine npmCommand, 'run', 'build'
        inputs.files(fileTree(frontend) {
            exclude 'node_modules/**', 'dist/**'
        })
        outputs.dir(frontend.dir('dist'))
    }
}
def collectFrontend = tasks.register('collectFrontend', Sync) {
    dependsOn frontendBuilds
    into layout.buildDirectory.dir('frontend-resources')
    apps.each { app ->
        from("frontend/${app}/dist") { into "static/${app}" }
    }
}
tasks.named('bootJar') {
    dependsOn collectFrontend
    from(collectFrontend) { into 'BOOT-INF/classes' }
}
```

### `src/main/java/example/Application.java`

```java
package example;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

### `frontend/project1/package.json`

```json
{
  "name": "project1",
  "private": true,
  "type": "module",
  "scripts": {
    "build": "vite build --base=/project1/"
  },
  "dependencies": {
    "vue": "3.5.44"
  },
  "devDependencies": {
    "vite": "8.3.5"
  }
}
```

### `frontend/project2/package.json`

```json
{
  "name": "project2",
  "private": true,
  "type": "module",
  "scripts": {
    "build": "vite build --base=/project2/"
  },
  "dependencies": {
    "vue": "3.5.44"
  },
  "devDependencies": {
    "vite": "8.3.5"
  }
}
```

### `frontend/project1/index.html`

```html
<!doctype html>
<html lang="en"><head><meta charset="UTF-8"><title>Vue build example</title></head>
<body><div id="app"></div><script type="module" src="/src/main.js"></script></body></html>
```

### `frontend/project1/src/main.js`

```js
import { createApp, h } from 'vue';
createApp({ render: () => h('h1', `Vue app at ${import.meta.env.BASE_URL}`) }).mount('#app');
```

### `prepare.sh`

```sh
#!/bin/sh
set -eu
mkdir -p frontend/project2/src
cp frontend/project1/index.html frontend/project2/index.html
cp frontend/project1/src/main.js frontend/project2/src/main.js
for app in project1 project2; do
    (cd "frontend/$app" && npm install --package-lock-only --ignore-scripts --no-audit --no-fund)
done
```

`prepare.sh`는 처음 예제를 준비할 때 실행하고, 생성된 두 `package-lock.json`을 저장소에 보관합니다. 이후 CI의 빌드는 고정된 lockfile로 `npm ci`를 실행합니다. 매 빌드마다 lockfile을 다시 만드는 구성이 아닙니다.

## 빌드하고 실행하기

프로젝트 루트에서 다음 순서로 실행합니다. Node/npm은 PATH에 있어야 합니다.

```sh
node --version
npm --version
sh prepare.sh
gradle --no-daemon clean bootJar
java -jar build/libs/multi-frontend-1.0.0.jar
```

기존 wrapper 프로젝트에서는 선택한 Gradle 버전의 `./gradlew`를 사용합니다. 서버가 시작되면 `http://localhost:8080/project1/index.html`, `http://localhost:8080/project2/index.html`을 확인하세요. 각 화면은 `Vue app at /project1/`, `Vue app at /project2/`를 표시합니다.

[Vite의 base 설정](https://vite.dev/guide/build.html#public-base-path)이 각 앱의 자산 URL을 해당 경로로 만듭니다. `base`가 서버의 SPA 라우팅까지 설정하는 것은 아닙니다. 여기서는 명시적인 `index.html` 주소를 사용하며, history router의 직접 진입이나 다른 context path는 별도 구성이 필요합니다.

## 실제로 JAR에 들어가는 경로

```text
BOOT-INF/classes/static/project1/index.html
BOOT-INF/classes/static/project1/assets/...
BOOT-INF/classes/static/project2/index.html
BOOT-INF/classes/static/project2/assets/...
```

앱별 빌드가 끝나면 `collectFrontend`가 `Sync`로 현재 산출물만 모읍니다. `bootJar`가 그 결과를 실행 JAR의 클래스패스 아래에 추가합니다. [Gradle 파일 처리](https://docs.gradle.org/current/userguide/working_with_files.html), [Boot 실행 JAR 패키징](https://docs.spring.io/spring-boot/3.5/gradle-plugin/packaging.html).

원고의 구성으로 두 앱을 빌드하고 패키징했으며, 실행 JAR에서 HTML·JS 자산이 HTTP로 제공되는 것을 확인했습니다. 또한 앱의 `public` 파일을 제거한 뒤 `clean` 없이 재빌드해 이전 파일이 새 JAR에 남지 않는지 검사했습니다. 두 앱의 lockfile도 각각 존재하는지 확인했습니다.

## 기존 프로젝트에 적용할 때

- `apps` 목록과 디렉터리 이름을 맞추고 각 앱의 lockfile을 준비합니다.
- 생성 자산이 들어갈 `static/project1`, `static/project2`를 수동 리소스와 겹치지 않게 사용합니다.
- Vue SFC를 사용한다면 해당 앱에 맞는 플러그인과 Vite 설정을 추가합니다. 이 작은 예제는 렌더 함수로 Vue를 사용합니다.
- 일반 `jar`가 아닌 실행 `bootJar`에 연결한 예제입니다. 배포할 아티팩트의 내용을 확인하세요.

릴리스 메타데이터를 빌드 자동화에 연결하려면 [GitHub 릴리스·자산 조회](/ko/posts/2023-09-23-linux-shellscript-github-latest/)와 [숫자 버전 비교의 입력 범위](/ko/posts/2023-11-17-linux-shellscript-version-compare/)를 함께 확인하세요. 준비 스크립트의 인터프리터 선택은 [POSIX sh 함수](/ko/posts/2023-09-20-linux-shellscript-function-error/)에서 다룹니다.
