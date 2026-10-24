---
title: "[springboot] springboot test webclient"
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
updatedAt: "2026-10-24T09:00:00+09:00"
reviewedAt: "2026-10-24"
reviewStatus: "revised"
reviewScope: "공식 WebClient 문서 대조 및 HTTP 상태·미디어 타입 테스트 재작성"
archiveBodySha256: "2e7abc1e5f3ccd2ff3b59e43e886b2a5e6a6f582b1058f2d1cf726ba260e7964"
reviewSources:
  - "https://docs.spring.io/spring-framework/reference/web/webflux-webclient/client-testing.html"
  - "https://docs.spring.io/spring-framework/reference/web/webflux-webclient/client-exchange.html"
  - "https://github.com/square/okhttp/tree/parent-4.12.0/mockwebserver"
---
## 무엇을 검증할 것인가

외부 API가 JSON 대신 HTML을 반환하면 HTTP 상태와 Content-Type을 별도로 처리해야 합니다. HTTP 500을 반환하는 것과 HTTP 200에 HTML 오류 페이지를 담는 것은 다른 실패입니다. `Accept: application/json`은 요청자의 선호를 표현할 뿐 상대 서버의 응답 형식을 보장하지 않습니다.

기존 예제는 선언되지 않은 Mockito 필드, 초기화되지 않은 final 필드, HTML을 JSON 문자열로 감싼 본문, `RuntimeException`을 만들고 `ConnectException`을 기대하는 검증이 섞여 있었습니다. 아래 예제는 fluent API 체인 대신 실제 로컬 HTTP 서버를 사용하도록 다시 구성했습니다.

## 의존성과 실행 조건

Java 17 이상, Spring Boot 3.x 계열의 의존성 관리가 적용된 Gradle 프로젝트를 기준으로 합니다. 아래 MockWebServer 4.12.0은 예제 API를 고정하기 위한 버전이며 최신 권장 버전이라는 뜻은 아닙니다.

```groovy
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-webflux'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testImplementation 'io.projectreactor:reactor-test'
    testImplementation 'com.squareup.okhttp3:mockwebserver:4.12.0'
}
tasks.named('test') { useJUnitPlatform() }
```

## HTTP 경계를 포함하는 테스트

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
                    .map(type -> MediaType.APPLICATION_JSON.isCompatibleWith(type)
                        || type.getSubtype().endsWith("+json"))
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
}
```

## 실패 종류를 나누는 이유

HTTP 오류는 `WebClientResponseException`, 연결 실패 등 요청 자체의 오류는 보통 `WebClientRequestException`으로 구분됩니다. 연결 예외의 내부 원인을 HTTP 500과 혼동하지 않아야 합니다. HTML을 응답할 때는 `setBody(html)`로 원문을 넣으며 `ObjectMapper.writeValueAsString(html)`로 JSON 문자열을 만들지 않습니다.

예제의 `verify(Duration...)`는 테스트가 무한 대기하지 않게 하는 제한입니다. 실제 클라이언트의 연결·응답 시간 제한을 설정한 것은 아니므로 운영 구성에서 별도로 정해야 합니다. 빈 JSON 본문, 잘못된 JSON, Content-Type 누락, `application/problem+json`, 타임아웃도 계약에 맞게 테스트를 추가할 수 있습니다. 오류 본문에는 개인 정보가 있을 수 있으므로 실제 서비스 로그에는 그대로 출력하지 않습니다.

## 실행 검증

2026-10-24에 본문의 테스트 클래스를 그대로 추출해 JDK 17, Gradle 8.4, Spring Boot 3.5.7 BOM과 MockWebServer 4.12.0으로 컴파일·실행했습니다. JSON 200, HTML 200, HTML 500의 세 테스트가 통과했습니다. 저장소의 `python3 scripts/check_webclient_example.py`로 같은 검증을 반복할 수 있습니다. 이 조합은 예제 재현 조건이며 운영 의존성의 최신성·보안 상태를 보증하지 않습니다.

## 확인한 자료

- [공식 자료 1](https://docs.spring.io/spring-framework/reference/web/webflux-webclient/client-testing.html)
- [공식 자료 2](https://docs.spring.io/spring-framework/reference/web/webflux-webclient/client-exchange.html)
- [공식 자료 3](https://github.com/square/okhttp/tree/parent-4.12.0/mockwebserver)
