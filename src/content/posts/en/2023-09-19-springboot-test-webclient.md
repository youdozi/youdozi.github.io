---
title: "Spring WebClient Tests with MockWebServer and JUnit 5"
language: "en"
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
updatedAt: "2026-10-30T13:01:05.739661+00:00"
reviewedAt: "2026-10-30"
reviewStatus: "revised"
reviewScope: "Official documentation checked; runnable examples and version boundaries clarified."
reviewSources:
  - "https://docs.spring.io/spring-framework/reference/6.2/web/webflux-webclient/client-testing.html"
  - "https://docs.spring.io/spring-framework/reference/6.2/web/webflux-webclient/client-exchange.html"
description: "Test WebClient with MockWebServer for HTTP status, Content-Type, JSON decoding and completion signals. Check why HTTP 200 with HTML can violate the response contract."
---
Test WebClient with a local MockWebServer and check HTTP status, response Content-Type, body decoding and completion or error together. A `200 OK` response containing HTML can fail the client’s response contract even though the status indicates success; sending `Accept: application/json` does not require a JSON response. Spring documents [mock web server testing](https://docs.spring.io/spring-framework/reference/6.2/web/webflux-webclient/client-testing.html) with the real HTTP client.

The tests use a real WebClient over local HTTP rather than a mock of its fluent method chain. They cover the response contracts shown below; production timeout and retry policies require separate tests.

## Processing flow

![Validate the HTTP response workflow](/assets/diagrams/2023-09-19-springboot-test-webclient-en.svg)

The client checks status before media type, releases rejected bodies and decodes supported JSON. StepVerifier checks completion or error as well as emitted values.

## Set up a standalone test project

The reproduction environment is JDK 17.0.8.1, Gradle 8.4, Spring Boot **3.5.7 BOM** and MockWebServer **4.12.0**. These pin the example's dependencies; they are not a recommendation of current production versions. This is a plain Java test project, so no running Spring Boot application is needed.

In a new directory, create `settings.gradle` containing `rootProject.name = 'webclient-example'`, and this complete `build.gradle`:

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

The BOM is explicit so that the Spring and Reactor dependencies have versions even without the Spring Boot Gradle plugin. For an application already managed by Boot, adapt the test dependencies to that application's selected BOM.

## Test eight response contracts

Save this complete class as `src/test/java/ExternalApiTest.java`:

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

Run with JDK 17 selected and Gradle 8.4 installed:

```sh
java -version
gradle --version
gradle --no-daemon test
```

All eight tests should pass. Open `build/reports/tests/test/index.html` for the per-test result; the Gradle task output need not list each passing test.

| Response | Result required by this example |
| --- | --- |
| HTTP 200, JSON body | Decode the payload. |
| HTTP 200, HTML body | Reject the unexpected content type. |
| HTTP 500, HTML body | Preserve the HTTP error type. |
| HTTP 200, missing Content-Type | Reject the unspecified response format. |
| HTTP 200, malformed JSON | Report a decoding error. |
| HTTP 200, `application/vnd.example+json` | Decode the compatible JSON payload. |
| HTTP 200, empty JSON body | Complete without emitting a payload. |
| HTTP 200, `text/example+json` | Reject the non-application media type. |

The empty-body behavior is a deliberate contract in this sample. If your endpoint requires a payload, add `switchIfEmpty(Mono.error(...))` and change that test to expect the application error.

<span id="why-status-and-decoding-are-checked-separately"></span>

## Why can HTTP 200 still fail response validation?

`fetch()` handles error statuses before inspecting the successful-response format. `createException()` preserves an HTTP 500 as `WebClientResponseException.InternalServerError`. A connection failure usually follows the `WebClientRequestException` path instead; it is not an HTTP response from the server.

For a non-error status, the code accepts `application/json` and `application/*+json` media types, then lets the decoder validate the body. An incorrect Content-Type and malformed JSON therefore produce different errors. This is a sample contract, not a complete policy for redirects or every successful status.

When rejecting a successful response, it releases the body before reporting the application error. With `exchangeToMono`, consume or handle the body within the callback; [Spring's exchange documentation](https://docs.spring.io/spring-framework/reference/6.2/web/webflux-webclient/client-exchange.html) explains that an unconsumed body is released after completion.

`setBody(html)` sends HTML directly. Serializing that string as JSON first would change the response being tested. The recorded-request assertions also check the method, path and `Accept` header actually sent.

`verify(Duration.ofSeconds(5))` bounds each test's wait. It does not configure the production client's connection or response timeouts. Add transport timeout and retry tests according to your API contract; they are not covered by these eight cases.

All eight tests passed in the reproduction environment above. In this repository, `python3 scripts/check_webclient_example.py` repeats that check. For a project crossing the Jakarta boundary, establish the [Spring Boot migration baseline](/en/posts/2023-09-08-springboot3-migration/) before changing client behavior.

These client tests use a local mock server; they do not check static files in a deployed application. If the application packages Vue apps, the [Gradle frontend packaging example](/en/posts/2021-07-23-multiple-gradle-build/) checks the executable JAR and its HTML/JavaScript responses. The two examples pin different environments and should not be combined without aligning their dependencies.

MockWebServer API reference: [OkHttp 4.12.0 source and examples](https://github.com/square/okhttp/tree/parent-4.12.0/mockwebserver).

For time limits and retry counts, continue with [WebClient timeout and bounded retry tests](/en/posts/2026-10-30-webclient-timeout-retry/). That example retries only GET responses with status 503 and separates per-attempt limits from the total retry budget.
