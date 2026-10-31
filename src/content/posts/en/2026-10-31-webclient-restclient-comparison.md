---
language: "en"
translationKey: "2026-10-31-webclient-restclient-comparison"
routeSlug: "2026-10-31-webclient-restclient-comparison"
kind: "post"
categories: ["springboot"]
tags: ["spring", "webclient", "restclient", "http-client", "reactive", "virtual-threads"]
publishedAt: "2026-10-30T23:49:15.271160+00:00"
updatedAt: "2026-10-30T23:49:15.271160+00:00"
title: "WebClient vs RestClient: Choosing Synchronous, Reactive and Streaming Calls"
socialImage: {"src": "/assets/img/social/webclient-restclient-en.png", "alt": "RestClient synchronous response waiting compared with WebClient reactive and streaming use", "width": 1200, "height": 630}
description: "Compare Spring WebClient and RestClient execution timing, blocking, errors and virtual-thread use. A local HTTP example checks per-subscription requests and 404/503 handling."
reviewedAt: "2026-10-31"
reviewStatus: "revised"
reviewScope: "Spring Framework 7.0.10/JDK 17 console HTTP contracts; not a throughput benchmark, server-stack test or production policy."
reviewSources: ["https://docs.spring.io/spring-framework/reference/integration/rest-clients.html", "https://spring.io/blog/2025/09/30/the-state-of-http-clients-in-spring/", "https://docs.spring.io/spring-framework/reference/web/webflux-webclient/client-synchronous.html", "https://docs.spring.io/spring-framework/reference/web/webflux-webclient/client-retrieve.html", "https://docs.spring.io/spring-framework/reference/web/webflux/new-framework.html", "https://docs.spring.io/spring-framework/docs/7.0.10/javadoc-api/org/springframework/http/client/JdkClientHttpRequestFactory.html", "https://docs.spring.io/spring-framework/docs/7.0.10/javadoc-api/org/springframework/http/client/reactive/JdkClientHttpConnector.html"]
---
**Start with RestClient when synchronous service code needs one HTTP response before continuing. Consider WebClient when you need reactive composition or streaming.** Both offer fluent APIs, but [RestClient is synchronous and WebClient is a non-blocking, reactive client](https://docs.spring.io/spring-framework/reference/integration/rest-clients.html). Match the client to the application’s execution model rather than its request count.


RestClient was introduced in Spring Framework 6.1; WebClient has been available since 5.0. First check whether your Framework version supports the client you choose. When upgrading a Boot project, follow a compatible combination managed by Boot. The runnable example below pins Framework 7.0.10.

## Which client fits which requirement?

| Criterion | RestClient | WebClient |
| --- | --- | --- |
| Result | A terminal operation such as body extraction waits for the response and returns a value | Mono or Flux represents the result; subscription triggers the request |
| Natural fit | Sequential, synchronous code in Spring MVC or batch jobs | WebFlux, reactive composition and streaming such as SSE |
| Error delivery | Default retrieve handling raises RestClientResponseException for 4xx and 5xx | Default retrieve handling emits a WebClientResponseException error for 4xx and 5xx |
| Additional cost | Easier to follow through a conventional call stack | Requires understanding operators, subscription, cancellation and context propagation |
| Concurrency control | Design executors or virtual-thread concurrency separately | Bound composition concurrency, such as flatMap, and connection and waiting budgets separately |

This table starts with ordinary API calls that aggregate a response in memory. RestClient can also read byte streams through low-level response handling, but WebClient is the natural fit for reactive element streams and demand control. Using WebClient does not require converting the server to WebFlux: Spring MVC can also use reactive return types. [Spring’s HTTP client guidance](https://spring.io/blog/2025/09/30/the-state-of-http-clients-in-spring/) makes the same distinction between typical synchronous calls and reactive or streaming requirements.

A synchronous service using virtual threads can retain sequential RestClient code. Virtual threads do not turn its API into a non-blocking one or increase downstream capacity or connection limits. Consider [the scope of virtual threads](/en/posts/2026-10-31-virtual-threads-jdk21-jdk25/) alongside [dependency capacity limits](/en/posts/2026-10-31-jdk-10k-rps-architecture/).

## Compare execution timing with the same HTTP responses

![The main flow completes a RestClient terminal operation, creates a WebClient Mono, subscribes twice for separate requests, and checks both clients’ 404 and 503 errors](/assets/diagrams/2026-10-31-webclient-restclient-comparison-en.svg)

The diagram shows the main method’s core checks; it omits local-server setup, client configuration and cleanup. **RestClient does not send a request merely by calling retrieve().** Here, body(String.class) performs the request and waits for its result. WebClient executes its default request Mono on subscription. Subscribing twice to this Mono, without caching or sharing operators, sends two requests.

This standalone console example was executed with Spring Framework 7.0.10, Reactor Core 3.8.8, JDK 17 and Gradle 8.4. It is not a Spring Boot application. Both clients explicitly use JDK HttpClient to remove differences in default connector selection. In a Boot project, prefer the dependencies managed by that Boot version rather than overriding them with this BOM.

### `settings.gradle`

```groovy
rootProject.name = 'http-client-comparison'
```

### `build.gradle`

```groovy
plugins { id 'application' }
repositories { mavenCentral() }
dependencies {
    implementation platform('org.springframework:spring-framework-bom:7.0.10')
    implementation 'org.springframework:spring-webflux'
}
java {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
}
application { mainClass = 'ClientComparison' }
```

### `src/main/java/ClientComparison.java`

```java
import com.sun.net.httpserver.HttpServer;
import java.net.InetSocketAddress;
import java.net.http.HttpClient;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.concurrent.atomic.AtomicInteger;
import org.springframework.http.client.JdkClientHttpRequestFactory;
import org.springframework.http.client.reactive.JdkClientHttpConnector;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientResponseException;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;
import reactor.core.publisher.Mono;

public class ClientComparison {
    static void check(boolean condition) {
        if (!condition) throw new AssertionError("HTTP contract failed");
    }
    public static void main(String[] args) throws Exception {
        var requests = new AtomicInteger();
        var server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        server.createContext("/", exchange -> {
            requests.incrementAndGet();
            String path = exchange.getRequestURI().getPath();
            int status = path.equals("/missing") ? 404 : path.equals("/unavailable") ? 503 : 200;
            byte[] body = (status == 200 ? "hello" : "error").getBytes(StandardCharsets.UTF_8);
            exchange.getResponseHeaders().set("Content-Type", "text/plain;charset=UTF-8");
            exchange.sendResponseHeaders(status, body.length);
            try (var output = exchange.getResponseBody()) { output.write(body); }
        });
        server.start();
        try {
            String base = "http://127.0.0.1:" + server.getAddress().getPort();
            var jdk = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(2)).build();
            var factory = new JdkClientHttpRequestFactory(jdk);
            factory.setReadTimeout(Duration.ofSeconds(2));
            var connector = new JdkClientHttpConnector(jdk);
            connector.setReadTimeout(Duration.ofSeconds(2));
            var rest = RestClient.builder().baseUrl(base).requestFactory(factory).build();
            var web = WebClient.builder().baseUrl(base).clientConnector(connector).build();

            var response = rest.get().uri("/hello").retrieve();
            check(requests.get() == 0);
            System.out.println("before-rest-terminal=" + requests.get());
            String sync = response.body(String.class);
            check("hello".equals(sync) && requests.get() == 1);
            System.out.println("rest=" + sync);

            Mono<String> pending = web.get().uri("/hello").retrieve().bodyToMono(String.class);
            check(requests.get() == 1);
            System.out.println("before-subscribe=" + requests.get());
            String first = pending.block(Duration.ofSeconds(5));
            check("hello".equals(first) && requests.get() == 2);
            System.out.println("web=" + first);
            System.out.println("after-first-subscribe=" + requests.get());
            String second = pending.block(Duration.ofSeconds(5));
            check("hello".equals(second) && requests.get() == 3);
            System.out.println("web-again=" + second);
            System.out.println("after-second-subscribe=" + requests.get());

            for (int status : new int[]{404, 503}) {
                String path = status == 404 ? "/missing" : "/unavailable";
                try {
                    rest.get().uri(path).retrieve().body(String.class);
                    throw new AssertionError("RestClient should fail");
                } catch (RestClientResponseException error) {
                    check(error.getStatusCode().value() == status);
                    System.out.println("rest-" + status + "=" + error.getStatusCode().value());
                }
                try {
                    web.get().uri(path).retrieve().bodyToMono(String.class).block(Duration.ofSeconds(5));
                    throw new AssertionError("WebClient should fail");
                } catch (WebClientResponseException error) {
                    check(error.getStatusCode().value() == status);
                    System.out.println("web-" + status + "=" + error.getStatusCode().value());
                }
            }
            check(requests.get() == 7);
            System.out.println("requests=" + requests.get());
        } finally { server.stop(0); }
    }
}
```

### Run and check

```sh
gradle --no-daemon --console=plain -q clean run
```

The first dependency download requires network access. Runtime HTTP requests go only to a 127.0.0.1 server on a temporary port. The following is the application’s observed standard output in the stated environment; Gradle or logging implementations may emit separate diagnostics.

```text
before-rest-terminal=0
rest=hello
before-subscribe=1
web=hello
after-first-subscribe=2
web-again=hello
after-second-subscribe=3
rest-404=404
web-404=404
rest-503=503
web-503=503
requests=7
```

The change from 0 to 1 shows that RestClient’s terminal operation completed the first request. The count remains 1 just after constructing the Mono. Each block subscribes, increasing it to 2 and then 3. Four subsequent requests check 404 and 503 handling, for a total of 7. These counts verify execution and error contracts; they do not compare throughput, latency or event-loop performance.

## Does block make the clients behave the same way?

Adding block to WebClient makes **the caller wait for the result**. It does not make the underlying transport implementation identical to RestClient’s. As the [synchronous-use documentation](https://docs.spring.io/spring-framework/reference/web/webflux-webclient/client-synchronous.html) explains, return Mono or Flux from a reactive controller and let the framework subscribe. The block calls above are confined to a console main that observes behavior. Calling RestClient or waiting with block on an event loop can occupy its processing thread or raise an exception prohibiting blocking on a non-blocking thread.

If an application already operates WebClient filters, authentication and instrumentation, synchronous calls alone do not require an immediate replacement. Compare the cost of introducing reactive dependencies and subscription handling for a new synchronous call with the cost of retaining existing configuration. Avoid unbounded subscriptions when combining several remote calls. [Reactive demand control in WebFlux](https://docs.spring.io/spring-framework/reference/web/webflux/new-framework.html) coordinates production and consumption rates; it does not automatically enforce a downstream service’s RPS or connection limits.

## What should you check before production?

Both clients need budgets for connecting, reading responses and the entire call, plus an error-status policy. The example’s 2-second connection limit, 2-second read limits and 5-second block wait are reproduction settings, not equivalent timeout semantics or recommended production values. Consult the [request-factory](https://docs.spring.io/spring-framework/docs/7.0.10/javadoc-api/org/springframework/http/client/JdkClientHttpRequestFactory.html) and [reactive-connector](https://docs.spring.io/spring-framework/docs/7.0.10/javadoc-api/org/springframework/http/client/reactive/JdkClientHttpConnector.html) documentation for the scope of each read timeout. These fast local responses do not validate timeouts, TLS or cancellation propagation.

The example checks default retrieve handling of 4xx and 5xx responses for both clients. Use onStatus for explicit status policies. Do not assume low-level exchange APIs apply retrieve’s default status handling. The [WebClient response-handling](/en/posts/2023-09-19-springboot-test-webclient/) and [timeouts and bounded retries](/en/posts/2026-10-30-webclient-timeout-retry/) examples provide follow-up contracts. Bound retries by idempotency, attempt count and total time budget; test empty bodies, large responses and connection failures separately.

Existing RestTemplate code is a separate migration concern. Spring Framework 7.0 recommends RestClient and marks RestTemplate deprecated; WebClient is not deprecated. After choosing a client, validate authentication, instrumentation and connection settings against the actual request mix.
