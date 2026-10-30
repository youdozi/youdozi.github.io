---
language: "en"
translationKey: "2026-10-30-webclient-timeout-retry"
routeSlug: "2026-10-30-webclient-timeout-retry"
kind: "post"
categories: ["springboot"]
tags: ["springboot", "webclient", "test", "reactor"]
publishedAt: "2026-10-30T13:00:04.233793+00:00"
updatedAt: "2026-10-30T13:00:04.233793+00:00"
title: "Test WebClient Timeouts and Bounded Retries with Reactor"
description: "Separate connection, response, per-attempt and total timeouts. Test a GET policy that retries only HTTP 503 twice, using local HTTP and Reactor virtual time."
reviewedAt: "2026-10-30"
reviewStatus: "revised"
reviewScope: "Official API references; paired code, policy tests and flow. Local HTTP and virtual time only; no TCP connect timeout or production policy validation."
reviewSources: ["https://docs.spring.io/spring-framework/reference/6.2/web/webflux-webclient/client-builder.html", "https://projectreactor.io/docs/core/3.7.12/api/reactor/core/publisher/Mono.html", "https://projectreactor.io/docs/core/release/api/reactor/util/retry/Retry.html", "https://projectreactor.io/docs/netty/1.2.11/api/reactor/netty/http/client/HttpClient.html"]
---
Place a per-attempt `timeout` before `retryWhen`, and a total `timeout` after it to include retry delays in the overall budget. Retry only failures permitted by the API contract: this GET example retries HTTP 503 at most twice and stops on timeouts or other errors. Spring documents [transport timeouts](https://docs.spring.io/spring-framework/reference/6.2/web/webflux-webclient/client-builder.html) separately from Reactor’s [publisher timeout](https://projectreactor.io/docs/core/3.7.12/api/reactor/core/publisher/Mono.html).

## Which limit does each setting control?

| Setting | Scope in this example |
| --- | --- |
| `CONNECT_TIMEOUT_MILLIS` | Establishing a TCP connection; not a complete DNS, pool acquisition or TLS budget |
| `responseTimeout` | Maximum interval between network reads while receiving a response; not a deadline for the complete body |
| First `timeout(attemptLimit)` | One subscription through body decoding; starts again on each retry |
| Last `timeout(totalLimit)` | The complete subscription, including all attempts and retry delays |
| `StepVerifier.verify(GUARD)` | The test runner’s maximum wait; it does not configure the client |

Reactor Netty’s [responseTimeout documentation](https://projectreactor.io/docs/netty/1.2.11/api/reactor/netty/http/client/HttpClient.html) describes a read interval, so a response that keeps delivering data can exceed that duration in total. The outer publisher timeout supplies a separate overall deadline. Cancellation stops this subscription; it does not undo work already performed by the remote service.

## Bound retries before adding more failure cases

![Apply an attempt timeout, retry only eligible 503 failures and bound the complete operation](/assets/diagrams/2026-10-30-webclient-timeout-retry-en.svg)

The diagram summarizes the operator nesting, rather than every HTTP event. Each attempt succeeds or emits an error. Only a 503 error with retries remaining triggers a delayed resubscription; other errors stop immediately. The outer timeout can cancel either an active attempt or a retry delay.

[`Retry.fixedDelay(2, delay)`](https://projectreactor.io/docs/core/release/api/reactor/util/retry/Retry.html) permits two retries after the initial attempt: at most three application attempts per subscription. `.onRetryExhaustedThrow` propagates the last 503 exception rather than a retry-exhausted wrapper. `.disableRetry(true)` disables Reactor Netty’s separate automatic retry on a TCP abort, so it does not add a hidden transport retry to these counts.

The example performs a GET and deliberately retries only 503. A timeout does not prove that the server did nothing. Do not copy this policy to payments or other writes without an explicit idempotency contract. It does not process `Retry-After`, retry 429, apply exponential backoff or jitter, or coordinate retries across callers. The short fixed delay makes tests quick; choose production limits and backoff from your API contract and load budget.

## Create a standalone project

Use a new empty directory, JDK 17 and Gradle 8.4. The example pins Boot BOM 3.5.7 and MockWebServer 4.12.0 to match the [response-contract tests](/en/posts/2023-09-19-springboot-test-webclient/). These are reproduction inputs, not current production version recommendations. Initial dependency resolution uses Maven Central; the HTTP tests use loopback only. No running Boot application or Gradle wrapper is bundled.

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

## Keep the two deadlines in different positions

Save the following implementation. The constructor takes positive durations selected by the caller; the test supplies explicit values. The response timeout and the 1,000 ms TCP connection timeout belong to the transport factory.

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

## Reproduce nine policy contracts

Seven tests use a real WebClient and a local MockWebServer. Two use a synthetic exchange and Reactor virtual time to verify operator timing without depending on network scheduling. Virtual time does not test Reactor Netty’s real socket timeouts. The transport test checks the wrapped read-timeout cause, whereas the publisher timeout produces `TimeoutException`.

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

## Run the project and read the result

```sh
gradle --no-daemon clean test
```

The local reproduction used JDK 17.0.8.1 and Gradle 8.4. All nine tests passed. Inspect `build/reports/tests/test/index.html` or `build/test-results/test/TEST-RetryClientTest.xml` for the assertions; `BUILD SUCCESSFUL` alone does not state how many tests ran.

| Scenario | Checked outcome |
| --- | --- |
| Immediate success | One HTTP request, `ok`, then completion |
| 503 → 503 → success | Three HTTP requests, `ok`, then completion |
| 503 on every attempt | Three HTTP requests, final 503 preserved |
| 404 / 500 | One HTTP request each, status preserved |
| No response, one-second attempt limit | `TimeoutException`, one HTTP request |
| No response, 250 ms response-read limit | `WebClientRequestException` with `ReadTimeoutException`, one request |
| 1.5 s total budget, one-second retry delay | Two synthetic attempts; timeout cancels the delay before a third |
| 400 ms attempt, 200 ms delay, 400 ms attempt | Each attempt fits 500 ms; success and completion checked after advancing virtual time by 1 s |

These checks do not reproduce TCP connection-establishment timeout, DNS failure, TLS negotiation, pool exhaustion, redirects or distributed side effects. The connection limit is configured, not experimentally validated here. OS scheduling can affect real elapsed time; the tests assert error types and request counts, not exact wall-clock milliseconds. For status, media type and JSON handling, continue with the [WebClient response-contract example](/en/posts/2023-09-19-springboot-test-webclient/).
