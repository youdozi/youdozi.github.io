---
language: en
translationKey: 2026-11-01-webflux-coroutines-mvc-virtual-threads
routeSlug: 2026-11-01-webflux-coroutines-mvc-virtual-threads
title: Moving from Kotlin, WebFlux and Coroutines to Java, MVC and Virtual Threads
description: Why a tight schedule and the existing team’s Kotlin learning curve led to Java, and how to move WebFlux and coroutine paths to MVC and virtual threads.
categories:
  - springboot
tags:
  - spring
  - spring-webflux
  - spring-mvc
  - kotlin-coroutines
  - kotlin
  - java
  - virtual-threads
  - migration
kind: post
publishedAt: 2026-11-01T05:15:00.000Z
updatedAt: 2026-11-01T05:48:44.744214+00:00
reviewedAt: "2026-11-01"
reviewStatus: source-audited
reviewScope: Official Spring documentation checked. Migration snippets and operational guidance are not a runnable application or a performance load test.
reviewSources:
  - https://docs.spring.io/spring-framework/reference/languages/kotlin/coroutines.html
  - https://docs.spring.io/spring-boot/reference/features/spring-application.html
  - https://docs.spring.io/spring-framework/reference/web/webflux/new-framework.html
---

**This migration moves from Kotlin, WebFlux and coroutines to Java, Spring MVC and virtual threads.** The move from Kotlin to Java was driven by a tight delivery schedule and the learning curve the existing team would face with Kotlin. The language decision considered delivery time and the team's learning burden; the server execution model moved to MVC with virtual threads.

The delivery context behind the language choice and the performance effects of virtual threads need separate explanations. The code below illustrates the migration shape; it does not reproduce production code or measured outcomes.

This guide describes a staged migration for Java 21 or later and Spring Boot 3.2 or later. It does not promise higher throughput or lower latency. Measure the actual result against the request's wait/CPU profile, database connection limit, downstream capacity, and a representative load test.

<span id="separate-the-three-choices"></span>

## Separate the language choice from the execution model

**WebFlux and MVC are web runtime choices.** WebFlux centers on Reactive Streams and asynchronous, non-blocking I/O; MVC uses the Servlet request model. **Coroutines are Kotlin's asynchronous programming model**, so you can keep `suspend` functions when choosing MVC. Spring supports Kotlin coroutines in annotated controllers for both MVC and WebFlux. Coroutine support requires `kotlinx-coroutines-core` and `kotlinx-coroutines-reactor`. [Spring Framework coroutine support](https://docs.spring.io/spring-framework/reference/languages/kotlin/coroutines.html)

Virtual threads are lightweight Java threads. They can reduce the cost of platform threads waiting in a thread-per-request design that uses blocking calls. Enabling them does not make JDBC non-blocking or increase the database connection pool. Spring Boot 3.2 and later can enable virtual-thread-based execution on JDK 21 or later with `spring.threads.virtual.enabled=true`. Boot recommends Java 24 or later for the best experience and calls out pinning, existing thread-pool settings, and daemon-thread behavior as items to review. [Spring Boot virtual-thread settings and caveats](https://docs.spring.io/spring-boot/reference/features/spring-application.html)

This migration changes the language, web runtime and concurrency model together. Validate each change separately. A storage migration is a separate decision, as the table shows; this does not establish that the actual service used R2DBC or moved to JPA.

| Change | What changes | What to validate separately |
| --- | --- | --- |
| Kotlin → Java | Implementation language and asynchronous API shape | Null handling, data objects, exceptions, cancellation and existing API contracts |
| WebFlux → MVC | Server request-processing model | Filters, security, exception mapping, SSE and WebSocket |
| R2DBC → JDBC/JPA (if needed) | Database access model | Transaction boundaries, queries, connection limits and timeouts |
| Coroutine-based execution → synchronous calls and virtual threads | Execution and waiting model | Library compatibility, ThreadLocal use, pinning and operational signals |

## Which paths should move?

MVC with virtual threads is worth evaluating when an ordinary request/response path uses JPA or JDBC and spends much of its time waiting on a database or downstream HTTP response. In contrast, paths whose core contract is a highly concurrent stream, server-sent events (SSE), WebSocket, or Reactive Streams demand control may be better left on WebFlux or separated into a dedicated path. The fact that `Flow` can be an MVC return type does not guarantee identical streaming, cancellation, or backpressure behavior in every environment.

![Flow for choosing Java based on schedule and learning burden, identifying reactive-only paths, migrating an ordinary request path through adapters and synchronous storage, validating virtual threads and contracts, then expanding gradually](/assets/diagrams/2026-11-01-webflux-coroutines-mvc-virtual-threads-en.svg)

The diagram shows the migration sequence for an ordinary request path. Defer migration for paths that still require streaming and keep or separate them. Expand traffic only after tests and observations meet the criteria; preserve a way to return to the previous path if the baseline regresses.

<span id="you-can-keep-coroutine-controllers"></span>

## Move a Kotlin coroutine controller to Java MVC

These excerpts illustrate a single-order lookup endpoint. Before migration, the Kotlin controller waits for the service through a `suspend` function.

```kotlin
@RestController
class OrderController(private val orders: OrderService) {
    @GetMapping("/orders/{id}")
    suspend fun get(@PathVariable id: Long): OrderDto = orders.get(id)
}
```

After migration, a Java MVC controller calls a synchronous service method and returns the same response DTO. This assumes `orders.get(id)` has also become a synchronous contract callable from Java. It does not call a Kotlin `suspend` method directly from Java.

```java
@RestController
public class OrderController {
    private final OrderService orders;

    public OrderController(OrderService orders) {
        this.orders = orders;
    }

    @GetMapping("/orders/{id}")
    public OrderDto get(@PathVariable("id") Long id) {
        return orders.get(id);
    }
}
```

The Spring annotations come from `org.springframework.web.bind.annotation`; `OrderService` and `OrderDto` are application service and response types. These excerpts are not a complete runnable application. Enable virtual threads through the Boot setting below and verify execution during a real HTTP request.

Check how Kotlin nullable types map to Java and how to preserve `data class` equality and serialization contracts. Replacing coroutine `async` calls with sequential Java calls can change downstream request ordering and response time, so validate parallelism, timeouts and cancellation separately. Wrapping existing coroutine calls in `runBlocking` alone does not complete a migration to synchronous Java services.

Spring MVC itself also supports Kotlin `suspend` and `Flow`, so removing coroutines is not a prerequisite for MVC. In this case, **Java was the target language because of the tight schedule and the existing team's Kotlin learning curve**, so controller and service contracts move in that direction too.

## Validate the repository migration separately

If the database access model must also change, the following is a separate example of moving Kotlin's R2DBC `CoroutineCrudRepository` to Spring Data JPA in Java. Bound the result size rather than collecting every row in memory, and preserve the existing API's sorting, page-size, and authorization filters.

```kotlin
interface OrderRepository : CoroutineCrudRepository<Order, Long> {
    fun findByCustomerId(customerId: Long): Flow<Order>
}
```

A synchronous JPA repository can query page by page:

```java
public interface OrderRepository extends JpaRepository<Order, Long> {
    Page<Order> findByCustomerId(Long customerId, Pageable pageable);
}
```

These snippets illustrate repository shapes; they are not a complete application. In a real project, also check entity-fetch strategy, transaction scope, N+1 queries, stable page ordering, and the cancellation or partial-consumption semantics of the previous `Flow`. Start with one finite-response API and add contract tests and query observations before migrating further.

## Enable virtual threads and verify them

With Spring Boot 3.2 or later and JDK 21 or later, you can apply this setting:

```yaml
spring:
  threads:
    virtual:
      enabled: true
```

After applying it, verify whether the thread handling a request is actually virtual. For a temporary diagnostic, record `Thread.currentThread().isVirtual()` from an MVC interceptor or controller. This only checks that request path; it does not prove that every application task or coroutine dispatcher uses virtual threads.

For a Java controller path, this expression checks the current request thread:

```java
public class RequestThreadProbe {
    public static boolean isVirtual() {
        return Thread.currentThread().isVirtual();
    }
}
```

Boot notes that thread-pool properties may no longer have their previous effect with virtual threads, and that pinning in some synchronized or native-call sections can affect throughput. Do not use a larger virtual-thread count to bypass database connection limits or downstream concurrency caps. Bound the database pool to what the database can handle, and configure connection-acquisition, query, downstream-call, and overall request deadlines.

## Migrate in stages and define rollback criteria

1. **Record a baseline.** Collect request rate, p50/p95/p99 latency, error rate, CPU, heap, database-pool waits, and downstream-call latency for representative endpoints under the same load conditions.
2. **Mark reactive-only paths.** List paths that depend on SSE, WebSocket, unbounded streams, backpressure, or Reactive Streams operations, and keep them out of the initial migration.
3. **Move one finite API.** Translate Kotlin to Java while validating the server-runtime change and any required storage change separately, then test request, response, error, cancellation, and authorization contracts.
4. **Verify virtual-thread execution.** Check runtime threads and the JDBC call path, not just the deployment property. Review executors for background tasks separately.
5. **Compare under equal load.** Compare latency distribution, errors, CPU, database waits, and connection use with the same data size and load. Virtual threads do not add CPU capacity for CPU-bound work, so watch for CPU saturation too.
6. **Expand from a small traffic share.** If business errors, latency, database-pool waits, or resource use exceed criteria defined in advance, stop expansion and investigate or roll back to the previous path. The team should set thresholds based on its service SLO and baseline.

Do not report throughput or latency gains that were not measured in the target environment. Measure the changed path with the same inputs first. If the result does not improve, there is no reason to treat the MVC migration itself as the goal.

## Decision criteria

If ordinary request/response traffic uses JDBC/JPA and concurrent blocking waits are a plausible bottleneck, evaluate MVC and virtual threads on a small path. In this case, Java was chosen because of the tight schedule and the existing team's Kotlin learning curve. Do not equate the language change with a throughput improvement from virtual threads. If streaming or Reactive Streams behavior is a product requirement, retain WebFlux rather than weakening that contract to change the thread model. Decide by comparing latency, errors, database waits, and operational complexity under equal load.
