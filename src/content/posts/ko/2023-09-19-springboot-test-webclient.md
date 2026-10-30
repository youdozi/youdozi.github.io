---
title: "Spring WebClient 테스트: MockWebServer와 JUnit 5로 응답 검증"
language: "ko"
translationKey: "2023-09-19-springboot-test-webclient"
routeSlug: "2023-09-19-springboot-test-webclient"
kind: "post"
publishedAt: "2023-09-18T15:00:00.000Z"
categories:
  - "springboot"
tags:
  - "springboot"
  - "test"
  - "webclient"
legacyUrl: "/springboot/springboot-test-webclient/"
legacySource: "_posts/spring/test/webclient/2023-09-19-springboot-test-webclient.markdown"
updatedAt: 2026-10-30T05:15:39.658659+00:00
reviewedAt: "2026-10-30"
reviewStatus: "revised"
reviewScope: "공식 문서 대조, 재현 절차와 버전별 적용 조건 보강"
archiveBodySha256: "2e7abc1e5f3ccd2ff3b59e43e886b2a5e6a6f582b1058f2d1cf726ba260e7964"
reviewSources:
  - "https://docs.spring.io/spring-framework/reference/6.2/web/webflux-webclient/client-testing.html"
  - "https://docs.spring.io/spring-framework/reference/6.2/web/webflux-webclient/client-exchange.html"
description: "MockWebServer로 WebClient의 상태·Content-Type·JSON 디코딩·완료 신호를 함께 검증합니다. HTTP 200의 HTML 응답이 계약을 위반하는 경우를 확인합니다."
---
로컬 MockWebServer로 WebClient를 테스트하면서 HTTP 상태·응답 Content-Type·본문 디코딩·완료 또는 오류 신호를 함께 확인하세요. HTTP 200에 HTML이 들어오면 상태는 성공이어도 클라이언트의 응답 계약을 위반할 수 있습니다. `Accept: application/json`을 보내도 JSON 응답이 보장되지는 않습니다. Spring은 실제 HTTP 클라이언트를 사용하는 [모의 웹 서버 테스트](https://docs.spring.io/spring-framework/reference/6.2/web/webflux-webclient/client-testing.html)를 안내합니다.

fluent API 체인을 모킹하는 대신 실제 WebClient로 로컬 HTTP 서버에 요청합니다. 아래의 응답 계약을 검증하며, 운영 타임아웃과 재시도 정책은 별도 테스트가 필요합니다.

## 처리 흐름

![HTTP 응답 계약 확인 흐름도](/assets/diagrams/2023-09-19-springboot-test-webclient-ko.svg)

클라이언트는 상태 코드 다음에 미디어 타입을 검사하고 거절한 본문을 해제합니다. StepVerifier는 값뿐 아니라 완료·오류 신호도 확인합니다.

## 독립적인 테스트 프로젝트 만들기

재현 환경은 JDK 17.0.8.1, Gradle 8.4, Spring Boot **3.5.7 BOM**, MockWebServer **4.12.0**입니다. 예제의 의존성을 고정한 조합이며 현재 운영 버전의 권장은 아닙니다. 일반 Java 테스트 프로젝트이므로 실행 중인 Spring Boot 애플리케이션은 필요하지 않습니다.

새 디렉터리에서 `settings.gradle`에 `rootProject.name = 'webclient-example'`을 적고, 다음 내용으로 `build.gradle`을 만듭니다.

```groovy
plugins { id 'java' }
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
```

Boot Gradle 플러그인이 없어도 Spring·Reactor 의존성의 버전이 정해지도록 BOM을 명시했습니다. 이미 Boot로 의존성을 관리하는 애플리케이션이라면 해당 애플리케이션의 BOM에 맞춰 테스트 의존성을 적용하세요.

## 응답 계약 여덟 가지 테스트하기

다음 클래스를 `src/test/java/ExternalApiTest.java`로 저장합니다.

```java
import java.io.IOException;
import java.time.Duration;
import java.util.concurrent.TimeUnit;
import okhttp3.mockwebserver.MockResponse;
import okhttp3.mockwebserver.MockWebServer;
import okhttp3.mockwebserver.RecordedRequest;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.MediaType;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;
import reactor.test.StepVerifier;
import static org.junit.jupiter.api.Assertions.*;

class ExternalApiTest {
    private MockWebServer server;
    private WebClient client;
    record Payload(String message) {}

    @BeforeEach
    void start() throws IOException {
        server = new MockWebServer();
        server.start();
        client = WebClient.builder().baseUrl(server.url("/").toString()).build();
    }

    @AfterEach
    void stop() throws IOException {
        server.shutdown();
    }

    private Mono<Payload> fetch() {
        return client.get().uri("/employee/100")
            .accept(MediaType.APPLICATION_JSON)
            .exchangeToMono(response -> {
                if (response.statusCode().isError()) {
                    return response.createException().flatMap(Mono::error);
                }
                boolean json = response.headers().contentType()
                    .map(type -> "application".equals(type.getType())
                        && ("json".equals(type.getSubtype())
                            || type.getSubtype().endsWith("+json")))
                    .orElse(false);
                if (!json) {
                    return response.releaseBody().then(Mono.<Payload>error(
                        new IllegalStateException("Expected JSON response")));
                }
                return response.bodyToMono(Payload.class);
            });
    }

    @Test
    void rejectsHtmlEvenWhenStatusIs200() throws Exception {
        server.enqueue(new MockResponse().setResponseCode(200)
            .setHeader("Content-Type", "text/html; charset=UTF-8")
            .setBody("<html><body>Unknown failure</body></html>"));
        StepVerifier.create(fetch())
            .expectErrorMatches(error -> error instanceof IllegalStateException
                && error.getMessage().equals("Expected JSON response"))
            .verify(Duration.ofSeconds(5));
        RecordedRequest request = server.takeRequest(1, TimeUnit.SECONDS);
        assertNotNull(request);
        assertEquals("GET", request.getMethod());
        assertEquals("/employee/100", request.getPath());
        assertEquals("application/json", request.getHeader("Accept"));
    }

    @Test
    void preservesHttp500Error() {
        server.enqueue(new MockResponse().setResponseCode(500)
            .setHeader("Content-Type", "text/html")
            .setBody("<html>Unknown failure</html>"));
        StepVerifier.create(fetch())
            .expectError(org.springframework.web.reactive.function.client.WebClientResponseException.InternalServerError.class)
            .verify(Duration.ofSeconds(5));
    }

    @Test
    void decodesJson() {
        server.enqueue(new MockResponse().setResponseCode(200)
            .setHeader("Content-Type", "application/json")
            .setBody("{\"message\":\"ok\"}"));
        StepVerifier.create(fetch())
            .expectNextMatches(payload -> payload.message().equals("ok"))
            .expectComplete().verify(Duration.ofSeconds(5));
    }

    @Test
    void rejectsMissingContentType() {
        server.enqueue(new MockResponse().setResponseCode(200)
            .setBody("{\"message\":\"ok\"}"));
        StepVerifier.create(fetch())
            .expectErrorMatches(error -> error instanceof IllegalStateException
                && error.getMessage().equals("Expected JSON response"))
            .verify(Duration.ofSeconds(5));
    }

    @Test
    void rejectsMalformedJson() {
        server.enqueue(new MockResponse().setResponseCode(200)
            .setHeader("Content-Type", "application/json").setBody("{broken"));
        StepVerifier.create(fetch())
            .expectError(org.springframework.core.codec.DecodingException.class)
            .verify(Duration.ofSeconds(5));
    }

    @Test
    void decodesStructuredJsonSubtype() {
        server.enqueue(new MockResponse().setResponseCode(200)
            .setHeader("Content-Type", "application/vnd.example+json")
            .setBody("{\"message\":\"ok\"}"));
        StepVerifier.create(fetch())
            .expectNextMatches(payload -> payload.message().equals("ok"))
            .expectComplete().verify(Duration.ofSeconds(5));
    }

    @Test
    void completesWithoutPayloadForEmptyJsonBody() {
        server.enqueue(new MockResponse().setResponseCode(200)
            .setHeader("Content-Type", "application/json"));
        StepVerifier.create(fetch())
            .expectComplete().verify(Duration.ofSeconds(5));
    }

    @Test
    void rejectsNonApplicationJsonSubtype() {
        server.enqueue(new MockResponse().setResponseCode(200)
            .setHeader("Content-Type", "text/example+json")
            .setBody("{\"message\":\"ok\"}"));
        StepVerifier.create(fetch())
            .expectErrorMatches(error -> error instanceof IllegalStateException
                && error.getMessage().equals("Expected JSON response"))
            .verify(Duration.ofSeconds(5));
    }
}
```

JDK 17을 선택하고 Gradle 8.4가 설치된 환경에서 실행합니다.

```sh
java -version
gradle --version
gradle --no-daemon test
```

여덟 테스트가 모두 통과해야 합니다. 개별 결과는 `build/reports/tests/test/index.html`에서 확인할 수 있습니다. Gradle의 태스크 출력에 통과한 테스트 이름이 모두 표시되는 것은 아닙니다.

| 응답 | 이 예제가 요구하는 결과 |
| --- | --- |
| HTTP 200, JSON 본문 | payload 디코딩 |
| HTTP 200, HTML 본문 | 예상과 다른 응답 형식으로 거부 |
| HTTP 500, HTML 본문 | HTTP 오류 타입 유지 |
| HTTP 200, Content-Type 누락 | 응답 형식이 명시되지 않아 거부 |
| HTTP 200, 잘못된 JSON | 디코딩 오류 |
| HTTP 200, `application/vnd.example+json` | 호환되는 JSON payload 디코딩 |
| HTTP 200, 빈 JSON 본문 | payload를 방출하지 않고 완료 |
| HTTP 200, `text/example+json` | application 계열이 아닌 미디어 타입 거부 |

빈 본문 처리는 이 예제에서 선택한 계약입니다. 반드시 payload가 있어야 하는 API라면 `switchIfEmpty(Mono.error(...))`를 추가하고 빈 JSON 본문 테스트도 애플리케이션 오류를 기대하도록 바꿔야 합니다.

<span id="상태와-디코딩을-나눠-확인하는-이유"></span>

## HTTP 200 응답을 클라이언트가 거부하는 이유는 무엇인가요?

`fetch()`는 오류 상태를 먼저 처리한 뒤 성공 응답의 형식을 검사합니다. `createException()`은 HTTP 500을 `WebClientResponseException.InternalServerError`로 유지합니다. 연결 실패는 보통 `WebClientRequestException` 경로이며 서버가 보낸 HTTP 오류 응답과 구분해야 합니다.

오류 상태가 아니면 `application/json`과 `application/*+json` 미디어 타입을 허용하고, 실제 본문은 디코더가 검사하게 합니다. 잘못된 Content-Type과 잘못된 JSON을 서로 다른 오류로 구분할 수 있습니다. 이는 예제의 계약이며 리다이렉트나 모든 성공 상태를 다루는 완전한 정책은 아닙니다.

성공 응답의 형식을 거부할 때는 본문을 해제한 뒤 애플리케이션 오류를 반환합니다. `exchangeToMono`에서는 콜백 안에서 본문을 소비하거나 처리해야 합니다. [Spring의 exchange 안내](https://docs.spring.io/spring-framework/reference/6.2/web/webflux-webclient/client-exchange.html)는 완료 후 소비하지 않은 본문을 해제하는 동작을 설명합니다.

`setBody(html)`은 HTML 원문을 보냅니다. 먼저 JSON 문자열로 직렬화하면 테스트하려던 응답 자체가 바뀝니다. 기록된 요청으로 실제 전송한 메서드·경로·`Accept` 헤더도 확인합니다.

`verify(Duration.ofSeconds(5))`는 각 테스트의 대기를 제한합니다. 운영 클라이언트의 연결·응답 시간 제한을 설정하는 것은 아닙니다. 타임아웃과 재시도는 API 계약에 맞춰 별도 테스트해야 하며, 이 여덟 테스트에는 포함하지 않았습니다.

위 재현 환경에서 여덟 테스트가 모두 통과했습니다. 저장소에서는 `python3 scripts/check_webclient_example.py`로 반복할 수 있습니다. Jakarta 전환을 함께 진행한다면 클라이언트 동작을 바꾸기 전에 [Spring Boot 마이그레이션 기준선](/ko/posts/2023-09-08-springboot3-migration/)부터 확인하세요.

이 클라이언트 테스트는 로컬 모의 서버를 사용하므로 배포 애플리케이션의 정적 파일을 확인하지 않습니다. Vue 앱을 함께 패키징한다면 [Gradle 프런트엔드 패키징 예제](/ko/posts/2021-07-23-multiple-gradle-build/)에서 실행 JAR과 HTML·JavaScript 응답을 확인할 수 있습니다. 두 예제의 고정 환경이 다르므로 의존성을 맞추지 않고 하나의 프로젝트로 합치면 안 됩니다.

MockWebServer API는 [OkHttp 4.12.0 소스와 예제](https://github.com/square/okhttp/tree/parent-4.12.0/mockwebserver)를 참고할 수 있습니다.
