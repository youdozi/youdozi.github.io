---
language: "en"
translationKey: "2026-11-01-webflux-coroutines-mvc-virtual-threads"
routeSlug: "2026-11-01-webflux-coroutines-mvc-virtual-threads"
title: "Moving from WebFlux and Coroutines to MVC and Virtual Threads"
description: "Learn where Spring MVC can keep Kotlin coroutines, when to retain WebFlux, and how to migrate JDBC/JPA paths to virtual threads with staged validation."
categories: ["springboot"]
tags: ["spring", "spring-webflux", "spring-mvc", "kotlin-coroutines", "virtual-threads", "migration"]
---

Using WebFlux with Kotlin coroutines does not mean you must remove coroutines. **Spring MVC also supports Kotlin `suspend` functions and `Flow` return values.** The migration is not a wholesale syntax rewrite. It is a decision about which paths still need a reactive server and whether blocking JDBC/JPA paths should move to MVC with virtual threads.

This guide describes a staged migration for Java 21 or later and Spring Boot 3.2 or later. It does not promise higher throughput or lower latency. Measure the actual result against the request's wait/CPU profile, database connection limit, downstream capacity, and a representative load test.

## Separate the three choices

**WebFlux and MVC are web runtime choices.** WebFlux centers on Reactive Streams and asynchronous, non-blocking I/O; MVC uses the Servlet request model. **Coroutines are Kotlin's asynchronous programming model**, so you can keep `suspend` functions when choosing MVC. Spring supports Kotlin coroutines in annotated controllers for both MVC and WebFlux. Coroutine support requires `kotlinx-coroutines-core` and `kotlinx-coroutines-reactor`. [Spring Framework coroutine support](https://docs.spring.io/spring-framework/reference/languages/kotlin/coroutines.html)

Virtual threads are lightweight Java threads. They can reduce the cost of platform threads waiting in a thread-per-request design that uses blocking calls. Enabling them does not make JDBC non-blocking or increase the database connection pool. Spring Boot 3.2 and later can enable virtual-thread-based execution on JDK 21 or later with `spring.threads.virtual.enabled=true`. Boot recommends Java 24 or later for the best experience and calls out pinning, existing thread-pool settings, and daemon-thread behavior as items to review. [Spring Boot virtual-thread settings and caveats](https://docs.spring.io/spring-boot/reference/features/spring-application.html)

Do not bundle these three changes into one:

| Change | What changes | What to validate separately |
| --- | --- | --- |
| WebFlux → MVC | Server request-processing model | Filters, security, exception mapping, SSE and WebSocket |
| R2DBC → JDBC/JPA | Database access model | Transaction boundaries, queries, connection limits and timeouts |
| Platform → virtual threads | Execution threads | Library compatibility, ThreadLocal use, pinning and operational signals |

## Which paths should move?

MVC with virtual threads is worth evaluating when an ordinary request/response path uses JPA or JDBC and spends much of its time waiting on a database or downstream HTTP response. In contrast, paths whose core contract is a highly concurrent stream, server-sent events (SSE), WebSocket, or Reactive Streams demand control may be better left on WebFlux or separated into a dedicated path. The fact that `Flow` can be an MVC return type does not guarantee identical streaming, cancellation, or backpressure behavior in every environment.

![Flow for identifying reactive-only paths, migrating an ordinary request path through adapters and synchronous storage, validating virtual threads and contracts, then expanding gradually](/assets/diagrams/2026-11-01-webflux-coroutines-mvc-virtual-threads-en.svg)

The diagram shows the migration sequence for an ordinary request path. Defer migration for paths that still require streaming and keep or separate them. Expand traffic only after tests and observations meet the criteria; preserve a way to return to the previous path if the baseline regresses.

## You can keep coroutine controllers

Assume a WebFlux controller like this. `Flow` returns a stream of results.

```kotlin
@RestController
class OrderController(private val orders: OrderService) {
    @GetMapping("/orders/{id}")
    suspend fun get(@PathVariable id: Long): OrderDto = orders.get(id)

    @GetMapping("/orders")
    fun list(): Flow<OrderDto> = orders.list()
}
```

Moving to MVC does not require changing these controller signatures to synchronous functions. Spring MVC supports `suspend` and `Flow` too. After changing the runtime and dependencies, use integration tests to verify the completion, cancellation, and streaming behavior of each return type.

```kotlin
@RestController
class OrderController(private val orders: OrderService) {
    @GetMapping("/orders/{id}")
    suspend fun get(@PathVariable id: Long): OrderDto = orders.get(id)

    @GetMapping("/orders")
    fun list(): Flow<OrderDto> = orders.list()
}
```

The identical-looking controller does not tell you whether its repository uses R2DBC or JDBC. Calling synchronous JDBC from a coroutine function does not make the call non-blocking. Likewise, the presence of a `suspend` function does not automatically map an MVC request to a virtual thread. Verify Boot's virtual-thread setting and the coroutine dispatcher on the actual execution path.

## Validate the repository migration separately

Here is an example of replacing R2DBC's `CoroutineCrudRepository` with Spring Data JPA. Bound the result size rather than collecting every row in memory, and preserve the existing API's sorting, page-size, and authorization filters.

```kotlin
interface OrderRepository : CoroutineCrudRepository<Order, Long> {
    fun findByCustomerId(customerId: Long): Flow<Order>
}
```

A synchronous JPA repository can query page by page:

```kotlin
interface OrderRepository : JpaRepository<Order, Long> {
    fun findByCustomerId(customerId: Long, pageable: Pageable): Page<Order>
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
Thread.currentThread().isVirtual()
```

Boot notes that thread-pool properties may no longer have their previous effect with virtual threads, and that pinning in some synchronized or native-call sections can affect throughput. Do not use a larger virtual-thread count to bypass database connection limits or downstream concurrency caps. Bound the database pool to what the database can handle, and configure connection-acquisition, query, downstream-call, and overall request deadlines.

## Migrate in stages and define rollback criteria

1. **Record a baseline.** Collect request rate, p50/p95/p99 latency, error rate, CPU, heap, database-pool waits, and downstream-call latency for representative endpoints under the same load conditions.
2. **Mark reactive-only paths.** List paths that depend on SSE, WebSocket, unbounded streams, backpressure, or Reactive Streams operations, and keep them out of the initial migration.
3. **Move one finite API.** Make the server-runtime change and that path's storage change explicit, then test request, response, error, cancellation, and authorization contracts.
4. **Verify virtual-thread execution.** Check runtime threads and the JDBC call path, not just the deployment property. Review executors for background tasks separately.
5. **Compare under equal load.** Compare latency distribution, errors, CPU, database waits, and connection use with the same data size and load. Virtual threads do not add CPU capacity for CPU-bound work, so watch for CPU saturation too.
6. **Expand from a small traffic share.** If business errors, latency, database-pool waits, or resource use exceed criteria defined in advance, stop expansion and investigate or roll back to the previous path. The team should set thresholds based on its service SLO and baseline.

Do not report throughput or latency gains that were not measured in the target environment. Measure the changed path with the same inputs first. If the result does not improve, there is no reason to treat the MVC migration itself as the goal.

## Decision criteria

If ordinary request/response traffic uses JDBC/JPA and concurrent blocking waits are a plausible bottleneck, evaluate MVC and virtual threads on a small path. Keep coroutines at the API boundary when they still fit the code. If streaming or Reactive Streams behavior is a product requirement, retain WebFlux rather than weakening that contract to change the thread model. Decide by comparing latency, errors, database waits, and operational complexity under equal load.
