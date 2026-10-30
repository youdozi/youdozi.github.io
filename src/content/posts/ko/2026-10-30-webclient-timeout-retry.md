---
language: "ko"
translationKey: "2026-10-30-webclient-timeout-retry"
routeSlug: "2026-10-30-webclient-timeout-retry"
kind: "post"
categories: ["springboot"]
tags: ["springboot", "webclient", "test", "reactor"]
publishedAt: "2026-10-30T13:00:04.233793+00:00"
updatedAt: "2026-10-30T13:00:04.233793+00:00"
title: "WebClient 타임아웃과 제한된 재시도를 Reactor로 테스트하기"
description: "연결·응답·시도별·전체 타임아웃을 구분합니다. 503만 최대 두 번 재시도하는 GET 정책을 로컬 HTTP 서버와 Reactor 가상 시간으로 검증합니다."
reviewedAt: "2026-10-30"
reviewStatus: "revised"
reviewScope: "Official API references; paired code, policy tests and flow. Local HTTP and virtual time only; no TCP connect timeout or production policy validation."
reviewSources: ["https://docs.spring.io/spring-framework/reference/6.2/web/webflux-webclient/client-builder.html", "https://projectreactor.io/docs/core/3.7.12/api/reactor/core/publisher/Mono.html", "https://projectreactor.io/docs/core/release/api/reactor/util/retry/Retry.html", "https://projectreactor.io/docs/netty/1.2.11/api/reactor/netty/http/client/HttpClient.html"]
---
`retryWhen` 앞에 시도별 `timeout`을, 뒤에 전체 `timeout`을 두면 재시도 대기까지 전체 제한에 포함할 수 있습니다. 재시도할 오류는 API 계약에 맞춰 고릅니다. 이 GET 예제는 HTTP 503만 최대 두 번 재시도하고, 타임아웃과 다른 오류는 즉시 전달합니다. Spring의 [전송 계층 타임아웃](https://docs.spring.io/spring-framework/reference/6.2/web/webflux-webclient/client-builder.html)과 Reactor의 [Publisher 타임아웃](https://projectreactor.io/docs/core/3.7.12/api/reactor/core/publisher/Mono.html)은 적용 범위가 다릅니다.

## 각 시간 제한은 어디에 적용되나요?

| 설정 | 이 예제의 적용 범위 |
| --- | --- |
| `CONNECT_TIMEOUT_MILLIS` | TCP 연결 수립. DNS·풀 획득·TLS 전체 제한이 아님 |
| `responseTimeout` | 응답을 받는 동안 네트워크 읽기 사이의 최대 간격. 본문 전체의 완료 기한이 아님 |
| 첫 번째 `timeout(attemptLimit)` | 본문 디코딩까지 한 구독. 재시도할 때마다 다시 시작 |
| 마지막 `timeout(totalLimit)` | 모든 시도와 재시도 대기를 포함한 전체 구독 |
| `StepVerifier.verify(GUARD)` | 테스트 실행기의 최대 대기. 클라이언트 설정이 아님 |

Reactor Netty의 [responseTimeout 문서](https://projectreactor.io/docs/netty/1.2.11/api/reactor/netty/http/client/HttpClient.html)는 읽기 간격을 설명합니다. 데이터가 계속 도착하면 전체 응답 시간은 이 값보다 길 수 있습니다. 바깥쪽 Publisher 타임아웃으로 전체 완료 기한을 따로 제한합니다. 취소는 이 구독을 중단하지만, 원격 서비스가 이미 수행한 작업을 되돌리지는 않습니다.

## 재시도 범위를 먼저 제한하세요

![시도별 타임아웃을 적용하고 조건에 맞는 503만 재시도하며 전체 작업 시간을 제한하는 흐름](/assets/diagrams/2026-10-30-webclient-timeout-retry-ko.svg)

그림은 개별 HTTP 이벤트 대신 연산자의 중첩 관계를 요약합니다. 각 시도는 성공하거나 오류를 전달합니다. 재시도가 남은 503 오류만 대기 후 다시 구독하고, 다른 오류는 즉시 종료합니다. 바깥쪽 타임아웃은 진행 중인 시도와 재시도 대기 모두를 취소할 수 있습니다.

[`Retry.fixedDelay(2, delay)`](https://projectreactor.io/docs/core/release/api/reactor/util/retry/Retry.html)는 최초 시도 뒤에 재시도 두 번을 허용합니다. 구독 하나당 애플리케이션 시도는 최대 세 번입니다. `.onRetryExhaustedThrow`는 재시도 소진을 감싼 예외 대신 마지막 503 예외를 전달합니다. `.disableRetry(true)`는 TCP 연결 중단 시 Reactor Netty가 별도로 수행하는 자동 재시도를 꺼서 전송 계층의 숨은 재시도가 횟수에 추가되지 않게 합니다.

예제는 GET을 사용하고 의도적으로 503만 재시도합니다. 타임아웃이 발생했다고 서버가 아무 작업도 하지 않았다고 판단할 수는 없습니다. 명시적인 멱등성 계약 없이 결제 등 쓰기 요청에 이 정책을 복사하지 마세요. `Retry-After` 처리, 429 재시도, 지수 백오프·지터, 여러 호출자 사이의 재시도 조율은 포함하지 않습니다. 짧은 고정 대기는 테스트를 빠르게 실행하기 위한 값입니다. 운영 제한과 백오프는 API 계약과 부하 예산에 맞춰 정해야 합니다.

## 독립 테스트 프로젝트 만들기

새 빈 디렉터리에서 JDK 17과 Gradle 8.4를 사용합니다. [응답 계약 테스트](/ko/posts/2023-09-19-springboot-test-webclient/)와 같은 Boot BOM 3.5.7·MockWebServer 4.12.0을 고정합니다. 현재 운영 버전 추천이 아닌 재현 입력입니다. 최초 의존성 해결은 Maven Central에 접근하며 HTTP 테스트는 루프백만 사용합니다. 실행 중인 Boot 애플리케이션은 필요하지 않고 Gradle wrapper는 포함하지 않습니다.

### `settings.gradle`

```groovy
rootProject.name = 'webclient-timeout-retry'
```

### `build.gradle`

```groovy
plugins { id 'java' }
repositories { mavenCentral() }
dependencies {
    implementation platform('org.springframework.boot:spring-boot-dependencies:3.5.7')
    implementation 'org.springframework.boot:spring-boot-starter-webflux'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testImplementation 'io.projectreactor:reactor-test'
    testImplementation 'com.squareup.okhttp3:mockwebserver:4.12.0'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
test { useJUnitPlatform() }
```

## 두 시간 제한을 다른 위치에 두기

아래 구현을 저장합니다. 생성자에는 호출자가 선택한 양수 Duration을 전달하며 테스트는 값을 명시합니다. 응답 타임아웃과 1,000 ms TCP 연결 타임아웃은 전송 계층을 만드는 팩터리에서 설정합니다.

### `src/main/java/RetryClient.java`

```java
import java.time.Duration;
import io.netty.channel.ChannelOption;
import org.springframework.http.client.reactive.ReactorClientHttpConnector;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;
import reactor.core.publisher.Mono;
import reactor.netty.http.client.HttpClient;
import reactor.util.retry.Retry;

public class RetryClient {
    private final WebClient client;
    private final Duration attemptLimit;
    private final Duration totalLimit;
    private final Duration retryDelay;

    public RetryClient(WebClient client, Duration attemptLimit,
                       Duration totalLimit, Duration retryDelay) {
        this.client = client;
        this.attemptLimit = attemptLimit;
        this.totalLimit = totalLimit;
        this.retryDelay = retryDelay;
    }

    public static WebClient transport(String baseUrl, Duration responseLimit) {
        HttpClient http = HttpClient.create()
            .disableRetry(true)
            .option(ChannelOption.CONNECT_TIMEOUT_MILLIS, 1000)
            .responseTimeout(responseLimit);
        return WebClient.builder().baseUrl(baseUrl)
            .clientConnector(new ReactorClientHttpConnector(http)).build();
    }

    public Mono<String> get() {
        return Mono.defer(() -> client.get().uri("/value")
                .retrieve().bodyToMono(String.class))
            .timeout(attemptLimit)
            .retryWhen(Retry.fixedDelay(2, retryDelay)
                .filter(error -> error instanceof WebClientResponseException response
                    && response.getStatusCode().value() == 503)
                .onRetryExhaustedThrow((spec, signal) -> signal.failure()))
            .timeout(totalLimit);
    }
}
```

## 정책 계약 아홉 가지 재현하기

일곱 테스트는 실제 WebClient와 로컬 MockWebServer를 사용합니다. 나머지 두 테스트는 합성 exchange와 Reactor 가상 시간으로 네트워크 스케줄링에 의존하지 않고 연산자 시간을 확인합니다. 가상 시간은 Reactor Netty의 실제 소켓 타임아웃을 검증하지 않습니다. 전송 계층 테스트는 감싸진 읽기 타임아웃 원인을 확인하고, Publisher 타임아웃은 `TimeoutException`을 발생시킵니다.

### `src/test/java/RetryClientTest.java`

```java
import java.io.IOException;
import java.time.Duration;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.atomic.AtomicInteger;
import io.netty.handler.timeout.ReadTimeoutException;
import okhttp3.mockwebserver.MockResponse;
import okhttp3.mockwebserver.MockWebServer;
import okhttp3.mockwebserver.SocketPolicy;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpStatus;
import org.springframework.web.reactive.function.client.ClientResponse;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientRequestException;
import org.springframework.web.reactive.function.client.WebClientResponseException;
import reactor.core.publisher.Mono;
import reactor.netty.http.client.HttpClient;
import reactor.test.StepVerifier;
import static org.junit.jupiter.api.Assertions.*;

class RetryClientTest {
    private MockWebServer server;
    private WebClient client;
    private static final Duration GUARD = Duration.ofSeconds(10);

    @BeforeAll
    static void warmUp() {
        HttpClient.create().warmup().block(GUARD);
    }

    @BeforeEach
    void start() throws IOException {
        server = new MockWebServer();
        server.start();
        client = RetryClient.transport(server.url("/").toString(), Duration.ofSeconds(5));
    }

    @AfterEach
    void stop() throws IOException {
        server.shutdown();
    }

    RetryClient policy() {
        return new RetryClient(client, Duration.ofSeconds(3),
            Duration.ofSeconds(8), Duration.ofMillis(10));
    }

    void expectStatus(int status) {
        StepVerifier.create(policy().get())
            .expectErrorSatisfies(error -> assertEquals(status,
                assertInstanceOf(WebClientResponseException.class, error).getStatusCode().value()))
            .verify(GUARD);
    }

    @Test
    void successUsesOneRequest() {
        server.enqueue(new MockResponse().setBody("ok"));
        StepVerifier.create(policy().get()).expectNext("ok").expectComplete().verify(GUARD);
        assertEquals(1, server.getRequestCount());
    }

    @Test
    void two503ResponsesThenSuccessUseThreeRequests() {
        server.enqueue(new MockResponse().setResponseCode(503));
        server.enqueue(new MockResponse().setResponseCode(503));
        server.enqueue(new MockResponse().setBody("ok"));
        StepVerifier.create(policy().get()).expectNext("ok").expectComplete().verify(GUARD);
        assertEquals(3, server.getRequestCount());
    }

    @Test
    void exhausted503PreservesLastStatusAfterThreeRequests() {
        for (int i = 0; i < 3; i++) server.enqueue(new MockResponse().setResponseCode(503));
        expectStatus(503);
        assertEquals(3, server.getRequestCount());
    }

    @Test
    void notFoundIsNotRetried() {
        server.enqueue(new MockResponse().setResponseCode(404));
        expectStatus(404);
        assertEquals(1, server.getRequestCount());
    }

    @Test
    void otherServerErrorsAreNotRetried() {
        server.enqueue(new MockResponse().setResponseCode(500));
        expectStatus(500);
        assertEquals(1, server.getRequestCount());
    }

    @Test
    void attemptTimeoutIsNotRetried() {
        server.enqueue(new MockResponse().setSocketPolicy(SocketPolicy.NO_RESPONSE));
        RetryClient limited = new RetryClient(client, Duration.ofSeconds(1),
            Duration.ofSeconds(8), Duration.ofMillis(10));
        StepVerifier.create(limited.get()).expectError(TimeoutException.class).verify(GUARD);
        assertEquals(1, server.getRequestCount());
    }

    @Test
    void responseReadTimeoutIsNotRetried() {
        server.enqueue(new MockResponse().setSocketPolicy(SocketPolicy.NO_RESPONSE));
        WebClient shortRead = RetryClient.transport(server.url("/").toString(), Duration.ofMillis(250));
        RetryClient limited = new RetryClient(shortRead, Duration.ofSeconds(3),
            Duration.ofSeconds(8), Duration.ofMillis(10));
        StepVerifier.create(limited.get()).expectErrorSatisfies(error -> {
            assertInstanceOf(WebClientRequestException.class, error);
            assertInstanceOf(ReadTimeoutException.class, error.getCause());
        }).verify(GUARD);
        assertEquals(1, server.getRequestCount());
    }

    @Test
    void totalBudgetIncludesRetryDelay() {
        AtomicInteger attempts = new AtomicInteger();
        StepVerifier.withVirtualTime(() -> {
            WebClient synthetic = WebClient.builder().exchangeFunction(request -> Mono.defer(() -> {
                attempts.incrementAndGet();
                return Mono.just(ClientResponse.create(HttpStatus.SERVICE_UNAVAILABLE).build());
            })).build();
            return new RetryClient(synthetic, Duration.ofSeconds(1),
                Duration.ofMillis(1500), Duration.ofSeconds(1)).get();
        }).thenAwait(Duration.ofMillis(1500)).expectError(TimeoutException.class).verify(GUARD);
        assertEquals(2, attempts.get());
    }

    @Test
    void attemptBudgetRestartsAfterRetry() {
        AtomicInteger attempts = new AtomicInteger();
        StepVerifier.withVirtualTime(() -> {
            WebClient synthetic = WebClient.builder().exchangeFunction(request -> Mono.defer(() -> {
                int attempt = attempts.incrementAndGet();
                return Mono.delay(Duration.ofMillis(400)).map(tick -> attempt == 1
                    ? ClientResponse.create(HttpStatus.SERVICE_UNAVAILABLE).build()
                    : ClientResponse.create(HttpStatus.OK).body("ok").build());
            })).build();
            return new RetryClient(synthetic, Duration.ofMillis(500),
                Duration.ofSeconds(2), Duration.ofMillis(200)).get();
        }).thenAwait(Duration.ofSeconds(1)).expectNext("ok").expectComplete().verify(GUARD);
        assertEquals(2, attempts.get());
    }
}
```

## 실행하고 결과 확인하기

```sh
gradle --no-daemon clean test
```

로컬 재현에는 JDK 17.0.8.1과 Gradle 8.4를 사용했고 아홉 테스트가 모두 통과했습니다. `build/reports/tests/test/index.html` 또는 `build/test-results/test/TEST-RetryClientTest.xml`에서 단언 결과를 확인하세요. `BUILD SUCCESSFUL`만으로는 실행된 테스트 수를 알 수 없습니다.

| 시나리오 | 확인한 결과 |
| --- | --- |
| 즉시 성공 | HTTP 요청 한 번, `ok` 후 완료 |
| 503 → 503 → 성공 | HTTP 요청 세 번, `ok` 후 완료 |
| 모든 시도에서 503 | HTTP 요청 세 번, 마지막 503 유지 |
| 404 / 500 | 각각 HTTP 요청 한 번, 상태 유지 |
| 무응답·시도 제한 1초 | `TimeoutException`, HTTP 요청 한 번 |
| 무응답·응답 읽기 제한 250 ms | 원인이 `ReadTimeoutException`인 `WebClientRequestException`, 요청 한 번 |
| 전체 제한 1.5초·재시도 대기 1초 | 합성 시도 두 번. 세 번째 시도 전 대기 중 타임아웃 |
| 시도 400 ms·대기 200 ms·시도 400 ms | 각 시도는 500 ms 이내. 가상 시간을 1초 진행한 뒤 성공·완료 확인 |

TCP 연결 수립 타임아웃, DNS 오류, TLS 협상, 풀 고갈, 리디렉션, 분산된 부수 효과는 재현하지 않았습니다. 연결 제한은 설정했지만 여기서 실험으로 검증한 항목은 아닙니다. OS 스케줄링은 실제 경과 시간에 영향을 줄 수 있으므로 정확한 밀리초 대신 오류 타입과 요청 수를 단언합니다. 상태·미디어 타입·JSON 처리는 [WebClient 응답 계약 예제](/ko/posts/2023-09-19-springboot-test-webclient/)에서 이어서 확인할 수 있습니다.
