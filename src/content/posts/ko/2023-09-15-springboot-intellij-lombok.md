---
title: "IntelliJ Lombok 오류 해결: Gradle 컴파일과 IDE 인식 구분하기"
language: ko
translationKey: 2023-09-15-springboot-intellij-lombok
routeSlug: 2023-09-15-springboot-intellij-lombok
kind: post
publishedAt: 2023-09-15T15:00:00.000Z
categories:
  - springboot
tags:
  - springboot
  - intellij community
  - lombok
legacyUrl: /springboot/springboot-intellij-lombok/
legacySource: _posts/spring/intellij-ce/2023-09-15-springboot-intellij-lombok.markdown
updatedAt: 2026-10-27T03:26:14.141Z
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Official documentation checked; CLI/project execution distinguished
  from IDE UI verification.
archiveBodySha256: 8a4674360edd715adc120d7ac95fbd3c194aa0b71e6d8ea194349e304c922930
reviewSources:
  - https://projectlombok.org/setup/gradle
  - https://projectlombok.org/setup/intellij
  - https://www.jetbrains.com/help/idea/annotation-processors-support.html
  - https://docs.spring.io/spring-boot/4.1/gradle-plugin/managing-dependencies.html
description: Lombok의 compileOnly·annotationProcessor와 테스트 설정을 구성하고,
  생성자·getter·JSON 응답을 검증해 Gradle 오류와 IDE 인식 문제를 구분합니다.
---
Lombok 메서드가 보이지 않으면 먼저 `./gradlew clean test`로 빌드도 실패하는지 확인하세요. IDE 플러그인은 편집기의 코드 인식을 돕고, Gradle의 annotation processor 설정은 컴파일 시 코드를 생성합니다. 한쪽 설정이 다른 쪽을 대신하지 않습니다.

여기서는 [Initializr 프로젝트](/ko/posts/2023-09-07-springboot-initializer/)와 [HTTP 예제](/ko/posts/2023-09-10-springboot-intellij-import/)를 이어서 사용합니다. 실행 환경은 Boot 4.1.2·Gradle 9.8.2·JDK 17이며, 실제 BOM에서 선택된 Lombok은 1.18.48입니다. 이 조합의 실행 근거이며 모든 JDK와 Lombok 조합의 호환성 보장은 아닙니다.

## Gradle의 컴파일 경로 구성

기존 `build.gradle`에 다음 블록을 추가합니다. 이미 같은 선언이 있으면 중복 추가하지 않습니다.

```groovy
dependencies {
    compileOnly 'org.projectlombok:lombok'
    annotationProcessor 'org.projectlombok:lombok'
    testCompileOnly 'org.projectlombok:lombok'
    testAnnotationProcessor 'org.projectlombok:lombok'
}
```

[공식 Gradle 설정](https://projectlombok.org/setup/gradle)에 따라 main과 test의 컴파일 의존성·프로세서를 나눕니다. 테스트 소스에서도 Lombok 애너테이션을 사용할 때만 test 쪽 두 선언이 필요합니다. 아래 테스트는 그 경로까지 확인합니다.

버전을 생략할 수 있는 이유는 기존 프로젝트가 Boot 플러그인과 `io.spring.dependency-management`를 적용해 [Boot BOM을 가져오기](https://docs.spring.io/spring-boot/4.1/gradle-plugin/managing-dependencies.html) 때문입니다. 일반 Gradle 프로젝트라면 필요한 각 선언에 같은 호환 버전을 명시하거나 해당 구성에 적용되는 의존성 관리를 별도로 설정해야 합니다.

## 생성자와 getter를 사용하는 코드

`Greeting`을 추가하고 기존 컨트롤러를 아래 내용으로 교체합니다. HTTP 테스트는 그대로 유지하며 별도의 Lombok 테스트도 추가합니다.

### `src/main/java/example/demo/Greeting.java`

```java
package example.demo;

import lombok.Getter;
import lombok.RequiredArgsConstructor;

@Getter
@RequiredArgsConstructor
public class Greeting {
    private final String message;
}
```

### `src/main/java/example/demo/GreetingController.java`

```java
package example.demo;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class GreetingController {
    @GetMapping("/greeting")
    public Greeting greeting() {
        return new Greeting("Hello, Gradle");
    }
}
```

### `src/test/java/example/demo/LombokGenerationTest.java`

```java
package example.demo;

import lombok.Getter;
import lombok.RequiredArgsConstructor;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class LombokGenerationTest {
    @Getter
    @RequiredArgsConstructor
    static class Expected {
        private final String message;
    }

    @Test
    void mainSourceConstructorAndGetterAreGenerated() {
        assertEquals("Hello, Gradle", new Greeting("Hello, Gradle").getMessage());
    }

    @Test
    void testSourceConstructorAndGetterAreGenerated() {
        assertEquals("test fixture", new Expected("test fixture").getMessage());
    }
}
```

```sh
./gradlew clean test bootJar
./gradlew dependencyInsight --configuration annotationProcessor --dependency lombok
```

전체 테스트는 컨텍스트 1개·HTTP 2개·Lombok 생성 2개, 총 5개입니다. main 소스의 생성자·getter와 test 소스의 생성자·getter를 실제로 호출합니다. `/greeting`의 JSON 응답도 유지돼야 합니다. Lombok이 컴파일 시 만든 getter를 직렬화기가 사용하는 경로를 함께 확인하는 것입니다.

Lombok은 `compileOnly`이므로 이 예제의 실행 JAR 라이브러리에는 Lombok을 넣지 않습니다. 플러그인만 설치했다고 Gradle 컴파일이 통과하는 것은 아니며, 컴파일된 getter를 사용하기 위해 Lombok을 런타임 `implementation`으로 추가하는 것도 이 구성에서는 필요하지 않습니다.

## IDE에서만 오류가 남을 때

Wrapper 테스트가 통과하면 Gradle 프로젝트를 다시 동기화합니다. [JetBrains 문서](https://www.jetbrains.com/help/idea/annotation-processors-support.html)는 빌드 파일에 설정한 프로세서를 가져올 때 annotation processing을 자동 활성화한다고 설명합니다. 수동 체크박스 변경을 모든 프로젝트의 필수 단계로 제시할 수는 없습니다.

그다음 IDE 버전에 맞는 Lombok 지원과 플러그인 활성화 상태를 [Lombok의 IntelliJ 안내](https://projectlombok.org/setup/intellij)에서 확인하세요. 특정 에디션은 항상 수동 설치, 다른 에디션은 항상 기본 제공이라고 일반화하지 않습니다. IntelliJ 자체 빌드와 Gradle에 위임한 빌드 중 어느 경로로 실행하는지도 확인해야 합니다.

Gradle에서도 생성 메서드가 없다고 실패하면 `compileOnly`만 있고 `annotationProcessor`가 빠졌는지 확인합니다. test에서만 실패하면 test 쪽 두 구성을 점검하세요. 재현 검사에서는 main 프로세서 또는 test 프로세서를 각각 제거했을 때 컴파일 실패가 발생하고, 복원하면 5개 테스트가 다시 통과하는 것을 확인했습니다. IDE 화면 조작은 이 실행 검사의 범위에 포함하지 않습니다.
