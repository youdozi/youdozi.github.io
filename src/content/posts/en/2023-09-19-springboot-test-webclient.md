---
title: "Testing Spring WebClient with MockWebServer"
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
updatedAt: "2026-10-24T06:00:52.173Z"
reviewedAt: "2026-10-24"
reviewStatus: "revised"
reviewScope: "English edition based on the reviewed Korean article; technical
  references and reproduction conditions retained."
reviewSources:
  - "https://docs.spring.io/spring-framework/reference/web/webflux-webclient/cl\
    ient-testing.html"
  - "https://docs.spring.io/spring-framework/reference/web/webflux-webclient/cl\
    ient-exchange.html"
  - "https://github.com/square/okhttp/tree/parent-4.12.0/mockwebserver"
description: "Test JSON and HTML responses with Spring WebClient and
  MockWebServer. Includes runnable JUnit tests for HTTP 200, HTTP 500, and
  content-type errors."
---
## Test the HTTP boundary

An external API can return HTML when your client expects JSON. A response with HTTP 500 and a response with HTTP 200 containing an HTML error page are different failures. Sending `Accept: application/json` expresses a preference; the server can still send another format.

A local MockWebServer lets a test control the status, headers, and body while exercising the real WebClient. This avoids mocking every method in WebClient's fluent interface and keeps the test independent of an external service.

The revised example below covers three contracts:

- JSON with HTTP 200 is decoded successfully.
- HTML with HTTP 200 is rejected as an unexpected response format.
- HTTP 500 remains an HTTP error, including when its body contains HTML.

## Dependencies and reproduction environment

Use Java 17 or later and a Gradle application with Spring Boot 3.x dependency management. The example was executed with JDK 17, Gradle 8.4, the Spring Boot 3.5.7 BOM, and MockWebServer 4.12.0. These versions describe the reproduction environment; check the supported dependency versions for your production application separately.

```groovy
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-webflux'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testImplementation 'io.projectreactor:reactor-test'
    testImplementation 'com.squareup.okhttp3:mockwebserver:4.12.0'
}
tasks.named('test') { useJUnitPlatform() }
```

## A complete JUnit test class

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

## Why these details matter

`setBody(html)` sends an HTML document. Serializing that string with Jackson first would wrap it as a JSON string, changing the response you intended to test.

The client checks the HTTP status before decoding a successful response. `response.createException()` preserves an HTTP 500 as a `WebClientResponseException.InternalServerError`. A connection failure belongs to the request-failure path, usually represented by `WebClientRequestException`; it should not be confused with an HTTP error returned by a server.

For a successful status, the example requires JSON or a structured `+json` subtype. If that contract fails, it releases the response body before reporting an application error. `exchangeToMono` gives the test control over how the response is consumed.

`verify(Duration.ofSeconds(5))` bounds the test's waiting time. Configure connection and response timeouts separately for the production HTTP client. Additional tests should cover an empty body, malformed JSON, a missing Content-Type, a problem-details response, and timeouts according to your API's contract.

## Run the published example

The three tests passed after extracting this exact class from the Korean article. In this repository, run `python3 scripts/check_webclient_example.py` with Gradle and JDK 17 installed. The verification does not require a running Spring application or a live external API.

## Sources

- [Spring Framework: testing WebClient](https://docs.spring.io/spring-framework/reference/web/webflux-webclient/client-testing.html)
- [Spring Framework: exchangeToMono and response handling](https://docs.spring.io/spring-framework/reference/web/webflux-webclient/client-exchange.html)
- [OkHttp MockWebServer 4.12.0](https://github.com/square/okhttp/tree/parent-4.12.0/mockwebserver)
