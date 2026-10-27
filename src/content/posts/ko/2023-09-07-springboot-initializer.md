---
title: Spring Initializr로 Gradle 프로젝트 만들고 테스트하기
language: ko
translationKey: 2023-09-07-springboot-initializer
routeSlug: 2023-09-07-springboot-initializer
kind: post
publishedAt: 2023-09-06T15:00:00.000Z
categories:
  - springboot
tags:
  - springboot
  - springboot initializer
legacyUrl: /springboot/springboot-initializer/
legacySource: _posts/spring/initializer/2023-09-07-springboot-initializer.markdown
updatedAt: 2026-10-27T05:23:47.316+00:00
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Official documentation checked; CLI/project execution distinguished
  from IDE UI verification.
archiveBodySha256: 0993c35936346a8878deb7cd9af793ce441c78a471c1561b0d5afbd196424f79
reviewSources:
  - https://start.spring.io/
  - https://start.spring.io/metadata/client
  - https://docs.spring.io/initializr/docs/current/reference/html/
  - https://docs.spring.io/spring-boot/4.1/system-requirements.html
  - https://docs.gradle.org/current/userguide/gradle_wrapper.html
description: Spring Initializr에서 Boot·Java·Gradle 설정을 확인하고, 생성한 프로젝트를 Wrapper로
  테스트합니다. Boot 4.1.2의 실행 가능한 파일 구성도 제공합니다.
---
Spring Initializr로 프로젝트를 만든 뒤에는 IDE보다 먼저 생성된 Gradle Wrapper로 테스트하세요. 생성 성공, 의존성 다운로드, JDK 호환성, 애플리케이션 실행을 나누어 확인하면 어느 단계에서 막혔는지 찾기 쉽습니다.

이 예제는 2026년 10월 27일 [start.spring.io](https://start.spring.io/)에서 실제로 생성한 Boot 4.1.2·Java 17·Gradle Groovy 프로젝트를 기준으로 합니다. 당시 Wrapper는 Gradle 9.8.2였습니다. 서버의 기본값과 선택 가능한 버전은 바뀌므로 이 조합이 계속 제공된다고 가정하지 마세요.

## 처리 흐름

![생성·설정 확인·테스트 흐름도](/assets/diagrams/2023-09-07-springboot-initializer-ko.svg)

전체 프로젝트를 생성한 뒤 포함된 Wrapper를 실행합니다. 컨텍스트 테스트 통과와 HTTP 애플리케이션 실행은 별도로 확인합니다.

## 생성할 항목 정하기

| 항목 | 예제 값 | 의미 |
| --- | --- | --- |
| Project / Language | Gradle - Groovy / Java | 빌드 도구와 소스 언어 |
| Spring Boot | 4.1.2 | 예제를 생성했을 때 제공된 정식 버전 |
| Java / Packaging | 17 / Jar | 소스 toolchain과 패키징 |
| Group / Artifact | example / demo | 프로젝트 식별자 |
| Package name | example.demo | 애플리케이션 패키지 |
| Dependencies | Spring Web | HTTP 엔드포인트를 만들기 위한 의존성 |

화면에서 Generate를 누르거나 아래 URL로 압축 파일을 받을 수 있습니다. **각 명령의 성공을 확인한 뒤 다음 명령을 실행하세요.** 같은 이름의 기존 폴더를 덮어쓰지 않도록 빈 작업 디렉터리를 사용합니다.

```sh
curl --fail --show-error --location 'https://start.spring.io/starter.zip?type=gradle-project&language=java&bootVersion=4.1.2&baseDir=demo&groupId=example&artifactId=demo&name=Demo&packageName=example.demo&packaging=jar&javaVersion=17&dependencies=web' --output demo.zip
unzip demo.zip
cd demo
./gradlew --version
./gradlew test
```

버전이 더 이상 제공되지 않으면 생성 API가 실패할 수 있습니다. 그때는 [현재 서비스 메타데이터](https://start.spring.io/metadata/client)와 [Initializr 문서](https://docs.spring.io/initializr/docs/current/reference/html/)에서 지원 항목을 확인하고 Boot·JDK·Gradle 조합을 함께 선택하세요. 기존 예제를 최신 기본값으로 조용히 바꾸면 재현 조건도 달라집니다.

## 생성 결과에서 확인할 네 파일

아래는 생성 결과의 핵심 네 파일을 공백·구성만 정리한 것입니다. 전체 생성물에는 Wrapper 스크립트, Wrapper JAR·설정, 리소스 파일도 포함됩니다. 아래 네 파일만 새 폴더에 복사해서는 `./gradlew`가 생기지 않습니다.

### `settings.gradle`

```groovy
rootProject.name = 'demo'
```

### `build.gradle`

```groovy
plugins {
    id 'java'
    id 'org.springframework.boot' version '4.1.2'
    id 'io.spring.dependency-management' version '1.1.7'
}
group = 'example'
version = '0.0.1-SNAPSHOT'
java {
    toolchain { languageVersion = JavaLanguageVersion.of(17) }
}
repositories { mavenCentral() }
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-webmvc'
    testImplementation 'org.springframework.boot:spring-boot-starter-webmvc-test'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
tasks.named('test') { useJUnitPlatform() }
```

### `src/main/java/example/demo/DemoApplication.java`

```java
package example.demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}
```

### `src/test/java/example/demo/DemoApplicationTests.java`

```java
package example.demo;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
class DemoApplicationTests {
    @Test
    void contextLoads() {}
}
```

Boot 4.1.2의 웹 의존성은 생성된 `spring-boot-starter-webmvc`와 `spring-boot-starter-webmvc-test`를 사용합니다. 다른 Boot 세대의 파일 일부와 섞기보다 선택한 버전에서 생성된 구성을 기준으로 하세요. [Boot 4.1.2 요구 사항](https://docs.spring.io/spring-boot/4.1/system-requirements.html)은 Java 17 이상, Gradle 8.14 이상인 8.x 또는 9.x를 명시합니다.

## 테스트와 실행 구분하기

기본 `contextLoads()`가 통과하면 테스트 컨텍스트가 시작됐다는 의미입니다. 아직 컨트롤러가 없으므로 `/`의 응답이 404여도 서버 시작 실패라고 판단하지 않습니다. 다음 명령은 별도로 실행하고, 종료하려면 해당 터미널에서 Ctrl+C를 누릅니다.

```sh
./gradlew bootRun
```

프로젝트를 보관할 때는 생성한 `build.gradle`과 [Gradle Wrapper 파일](https://docs.gradle.org/current/userguide/gradle_wrapper.html)을 함께 커밋하세요. Gradle 버전은 `java.toolchain`의 Java 버전과 다른 설정입니다. `./gradlew --version`에서 Gradle을 실행하는 JVM을 확인하고, 컴파일·실행에 선택한 JDK와 구분해야 합니다.

다음 단계인 [IntelliJ에서 프로젝트 열기와 HTTP 실행](/ko/posts/2023-09-10-springboot-intellij-import/)에서는 이 프로젝트에 엔드포인트를 추가합니다. Boot와 Framework 버전 번호가 다른 이유는 [Spring Boot 릴리스와 버전 관계](/ko/posts/2023-09-13-springboot-history/)에서 확인할 수 있습니다.
