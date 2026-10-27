---
title: IntelliJ에서 Spring Boot Gradle 프로젝트 열고 실행하기
language: ko
translationKey: 2023-09-10-springboot-intellij-import
routeSlug: 2023-09-10-springboot-intellij-import
kind: post
publishedAt: 2023-09-09T15:00:00.000Z
categories:
  - springboot
tags:
  - springboot
  - intellij community
  - project import
  - RUN/DEBUG configurations
legacyUrl: /springboot/springboot-intellij-import/
legacySource: _posts/spring/intellij-ce/2023-09-10-springboot-intellij-import.markdown
updatedAt: 2026-10-27T05:23:47.316+00:00
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Official documentation checked; CLI/project execution distinguished
  from IDE UI verification.
archiveBodySha256: 8cca65e7155f668af7bca85e7798c11f97705d4a53a0063ad582d8756b189d81
reviewSources:
  - https://www.jetbrains.com/help/idea/gradle.html
  - https://www.jetbrains.com/help/idea/gradle-jvm-selection.html
  - https://www.jetbrains.com/help/idea/running-applications.html
  - https://docs.gradle.org/current/userguide/compatibility.html
description: Spring Boot 프로젝트의 Gradle 동기화·JDK·Application 실행 구성을 확인하고, 실제 HTTP
  테스트로 IDE 문제와 애플리케이션 문제를 구분합니다.
---
IntelliJ에서 Spring Boot 프로젝트를 열 때는 Gradle 동기화가 끝났는지 먼저 확인하고, 터미널의 Wrapper 빌드와 IDE 실행을 비교하세요. 실행 버튼이 없다고 해서 항상 수동 구성부터 만들어야 하는 것은 아닙니다. [일반 Java main 메서드 옆 실행 아이콘](https://www.jetbrains.com/help/idea/running-applications.html)으로도 실행할 수 있습니다.

아래는 [Initializr 예제](/ko/posts/2023-09-07-springboot-initializer/)의 Boot 4.1.2·Gradle 9.8.2·Java 17 프로젝트를 이어서 사용합니다. 빌드·HTTP 동작은 로컬에서 실행했고, IDE 메뉴는 JetBrains 공식 문서를 대조했습니다. 특정 IDE 버전의 화면을 직접 조작해 검증했다는 의미는 아닙니다.

## 처리 흐름

![빌드와 IDE 오류 구분 흐름도](/assets/diagrams/2023-09-10-springboot-intellij-import-ko.svg)

Wrapper 빌드로 프로젝트 오류와 IDE 설정을 구분합니다. HTTP 테스트는 임의 포트, 수동 bootRun은 지정 포트를 사용합니다.

## 프로젝트와 JDK 확인

1. File → Open으로 압축을 푼 프로젝트 루트를 엽니다. `settings.gradle`·`build.gradle`이 있는 디렉터리입니다.
2. Gradle 프로젝트로 인식되면 동기화를 완료합니다. 의존성을 받지 못하면 동기화 오류부터 해결합니다.
3. Gradle 배포는 프로젝트의 Wrapper를 사용하고, Gradle JVM과 Project SDK를 확인합니다. 이 예제는 둘 다 JDK 17로 맞춥니다.
4. 터미널에서 `./gradlew --version`과 `./gradlew test`를 실행해 IDE 밖의 기준 결과를 확보합니다.

[Gradle 통합 문서](https://www.jetbrains.com/help/idea/gradle.html)와 [Gradle JVM 선택 규칙](https://www.jetbrains.com/help/idea/gradle-jvm-selection.html)을 참고하세요. 메뉴 이름은 IDE 버전과 OS에 따라 달라질 수 있습니다. Project SDK, Gradle을 실행하는 JVM, Java toolchain, 실행 구성의 JRE는 같은 개념이 아니며 자동으로 항상 일치하지도 않습니다.

## 엔드포인트와 실제 HTTP 테스트 추가

기존 네 파일을 유지하고 다음 두 파일을 추가합니다. 컨트롤러를 애플리케이션과 같은 `example.demo` 패키지에 두어 컴포넌트 스캔 범위에 포함합니다.

### `src/main/java/example/demo/GreetingController.java`

```java
package example.demo;

import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class GreetingController {
    @GetMapping("/greeting")
    public Map<String, String> greeting() {
        return Map.of("message", "Hello, Gradle");
    }
}
```

### `src/test/java/example/demo/GreetingHttpTest.java`

```java
package example.demo;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.core.env.Environment;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class GreetingHttpTest {
    @Autowired Environment environment;

    HttpResponse<String> get(String path) throws Exception {
        String port = environment.getRequiredProperty("local.server.port");
        var request = HttpRequest.newBuilder(URI.create("http://127.0.0.1:" + port + path))
                .timeout(Duration.ofSeconds(10)).GET().build();
        return HttpClient.newHttpClient().send(request, HttpResponse.BodyHandlers.ofString());
    }

    @Test
    void greetingReturnsJson() throws Exception {
        var response = get("/greeting");
        assertEquals(200, response.statusCode());
        assertTrue(response.headers().firstValue("content-type").orElse("").contains("application/json"));
        assertEquals("{\"message\":\"Hello, Gradle\"}", response.body());
    }

    @Test
    void missingPathIsNotAnApplicationStartupFailure() throws Exception {
        assertEquals(404, get("/missing").statusCode());
    }
}
```

`./gradlew test`는 기존 컨텍스트 테스트 1개와 HTTP 테스트 2개를 실행합니다. HTTP 테스트는 임의 포트로 실제 서버를 시작해 JSON 응답과 없는 경로의 404를 확인합니다. 포트를 고정한 테스트가 아니므로 로컬 8080 점유와 구분할 수 있습니다.

## Gradle 실행과 Application 실행 비교

터미널에서 아래 첫 명령으로 서버를 시작하고, 다른 터미널에서 두 번째 명령을 실행합니다.

```sh
./gradlew bootRun --args='--server.port=8081'
```

```sh
curl --fail --show-error http://localhost:8081/greeting
```

```json
{"message":"Hello, Gradle"}
```

IDE에서는 `DemoApplication.main()` 옆 실행 아이콘을 먼저 사용합니다. 직접 구성이 필요하면 Run → Edit Configurations에서 Application 유형을 만들고 다음 값을 확인하세요.

| 항목 | 예제 값 |
| --- | --- |
| Main class | `example.demo.DemoApplication` |
| Classpath module | 프로젝트의 main 소스 모듈, 예: `demo.main` |
| JRE | JDK 17 |
| Program arguments | `--server.port=8081` |

기존 프로세스가 8081을 사용 중이면 먼저 종료하거나 다른 포트를 선택하세요. Boot 전용 도구 창이나 실행 구성의 제공 범위와 일반 Java Application 실행은 구분해야 합니다.

| 관찰 | 먼저 확인할 것 |
| --- | --- |
| Wrapper 빌드도 실패 | JDK·Gradle 호환성, 의존성, 소스 오류 |
| Wrapper는 통과하고 IDE만 실패 | Gradle 재동기화, 모듈 classpath, 실행 JRE와 인자 |
| 서버는 시작했지만 `/greeting`이 404 | 컨트롤러 패키지와 매핑 경로 |
| 포트 사용 중 오류 | 기존 프로세스와 실행 인스턴스 |

컴파일은 통과하지만 IDE가 생성 메서드만 오류로 표시한다면 [Lombok과 annotation processor 점검](/ko/posts/2023-09-15-springboot-intellij-lombok/)을 이어서 확인할 수 있습니다.
