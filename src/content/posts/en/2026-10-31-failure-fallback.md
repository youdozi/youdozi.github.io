---
kind: "post"
publishedAt: "2026-10-31T15:05:02.489019+00:00"
updatedAt: "2026-10-31T15:05:02.489019+00:00"
reviewedAt: "2026-10-31"
reviewStatus: "revised"
reviewScope: "Self-reviewed English translation of the Korean article; offline Java 21 policy scenarios and diagram alignment. No HTTP integration, concurrent load test or production capacity claim."
reviewSources: ["https://aws.amazon.com/builders-library/avoiding-fallback-in-distributed-systems/", "https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/", "https://sre.google/sre-book/handling-overload/", "https://www.rfc-editor.org/rfc/rfc9110.html", "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/Semaphore.html"]
language: "en"
translationKey: "2026-10-31-failure-fallback"
routeSlug: "2026-10-31-failure-fallback"
title: "Designing fallback during failures: stale responses, reduced functionality, and rejection"
description: "Define when fallback is acceptable during external API, cache, and payment failures. Use Java to check data freshness and concurrency limits, then connect retries, recovery, and observability."
categories: ["architecture"]
tags: ["fallback", "resilience", "java", "timeout", "circuit-breaker", "load-shedding"]
---

During an outage, **fallback should provide a response at a predefined, acceptable level of quality and at a cost the system can afford**. You might omit a recommendation section or return public read data within an agreed age limit. Reporting success when a payment result is unknown, or sending every request to the DB when the cache fails, creates other problems.

This article is a design guide for developers operating HTTP APIs. Following the overload controls in the [10k RPS architecture article](/ko/posts/2026-10-31-jdk-10k-rps-architecture/), it addresses which responses to return during failures. The Java example runs a fallback policy without an external server; it does not measure throughput or recovery from a production outage.

## Different failures allow different outcomes

First decide what can be reduced from the normal result. The following are design examples; actual age limits and the scope of reduced functionality must follow your service contract.

| Failure | Acceptable alternative | When to stop or limit it |
| --- | --- | --- |
| Recommendation API delay or failure | Omit optional recommendations or use prepared general recommendations | Do not put core product reads in the same queue |
| Failure to read a public product description | Return the last successful data for the same product and language, with its update time | Maximum age exceeded, no data, or incorrect key |
| Entire cache unavailable | Limited origin reads, an approved local copy, or rejection of excess requests | No unlimited bypass beyond the DB connection and concurrency budgets |
| Authentication or authorization check fails | Return a temporary error without performing the protected operation | Do not confuse failure with lack of permission or replace it with access approval |
| Response lost after a payment or order request | Query status and reconcile using the same operation identifier | Do not assume failure and create a new payment, or fabricate success |
| Alternative server uses the same DB | Switch only within separately verified capacity | Switching servers does not resolve a bottleneck in the shared DB |

Separate correctness-critical paths, such as authorization, final pricing, and stock deduction, from simple stale reads. A payment status of “being checked” is meaningful only if you can actually track and query the request. Renaming a message or response does not manage an unresolved outcome.

AWS describes insufficient testing of rarely used paths and additional problems introduced by alternatives among the [risks of fallback in distributed systems](https://aws.amazon.com/builders-library/avoiding-fallback-in-distributed-systems/). Run fallback paths as you do normal paths, and check whether they depend on the same resources.

## What do timeouts, retries, and circuit breakers each do?

A timeout limits how long the caller waits. **The end of that wait does not mean the remote operation or payment was canceled.** A retry attempts the same operation again, while failover switches to another replica. Fallback switches to a reduced response or a different processing method. A circuit breaker blocks calls to a dependency under specified conditions after failures accumulate; a separate policy determines which alternative response is safe.

The overall request deadline must include connection establishment, connection-pool waits, response waits, retries, and alternative processing. For example, if the total budget is 300ms and the first call used 250ms, you cannot wait another 250ms. These numbers illustrate the idea; they are not recommended settings. Also check what each stage's timeout actually includes in your client.

As the [AWS retry guidance](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) explains, retries add load, and side effects may have occurred even when a response fails. Assign retry responsibility to one layer, and bound the remaining time and attempt count for transient failures only when repeating the operation is safe. Exponential backoff and jitter spread simultaneous retries, but they do not increase a saturated DB's capacity.

## Java example: return only approved public data for a limited time

The following example reads **one fixed public product description**. It prefers the normal response and uses the last successful copy only for dependency failures classified as `Unavailable`. The copy must be no more than 60 seconds old, and a future timestamp is rejected. The limit of 2 and the 60-second window are demonstration policies. Multiple products, languages, or tenants require separate keys; do not reuse this fixed-data example unchanged as a cache of authenticated user data.

![Reject immediately without an admission permit; with a permit, read the primary and return its result, or check snapshot existence and age only for the designated failure before returning a fallback](/assets/img/architecture/fallback-en.svg)

The diagram shows the decisions in `read()`. Every path that acquires a permit releases it through `finally`, whether it returns a primary result or throws an exception. Timeouts, circuit breakers, and cache refresh are not implemented. A real HTTP adapter must translate only approved failures, such as connection failures and timeouts, into `Unavailable`. Converting 401, 403, 404, schema errors, and programming errors into the same exception changes the meaning of this policy.

Save this as `FallbackDemo.java`. It runs on JDK 21 or later without external dependencies.

```java
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.concurrent.Semaphore;
import java.util.function.Supplier;

public class FallbackDemo {
    record Snapshot(String value, Instant observedAt) {}
    record Reply(String value, String source, long ageSeconds) {}
    static class Unavailable extends RuntimeException {}
    static class Rejected extends RuntimeException {
        Rejected(String reason) { super(reason); }
    }

    static final class Catalog {
        private final Semaphore slots = new Semaphore(2);
        private final Clock clock;
        private final Duration maxAge = Duration.ofSeconds(60);

        Catalog(Clock clock) { this.clock = clock; }

        Reply read(Supplier<String> primary, Snapshot snapshot) {
            if (!slots.tryAcquire()) throw new Rejected("capacity");
            try {
                try {
                    return new Reply(primary.get(), "primary", 0);
                } catch (Unavailable failure) {
                    if (snapshot == null) throw new Rejected("missing");
                    Duration age = Duration.between(
                            snapshot.observedAt(), clock.instant());
                    if (age.isNegative() || age.compareTo(maxAge) > 0) {
                        throw new Rejected("age");
                    }
                    return new Reply(snapshot.value(), "snapshot", age.toSeconds());
                }
            } finally {
                slots.release();
            }
        }
    }

    static void rejected(String reason, Runnable action) {
        try {
            action.run();
        } catch (Rejected e) {
            if (!reason.equals(e.getMessage())) throw new AssertionError(e);
            System.out.println("rejected=" + reason);
            return;
        }
        throw new AssertionError("Expected rejection: " + reason);
    }

    public static void main(String[] args) {
        Instant now = Instant.parse("2026-10-31T00:00:00Z");
        Catalog catalog = new Catalog(Clock.fixed(now, ZoneOffset.UTC));
        Snapshot recent = new Snapshot("saved-description", now.minusSeconds(30));
        Supplier<String> down = () -> { throw new Unavailable(); };

        System.out.println(catalog.read(() -> "live-description", recent));
        System.out.println(catalog.read(down, recent));
        System.out.println(catalog.read(down,
                new Snapshot("boundary", now.minusSeconds(60))));
        rejected("age", () -> catalog.read(down,
                new Snapshot("old", now.minusSeconds(60).minusNanos(1))));
        rejected("age", () -> catalog.read(down,
                new Snapshot("future", now.plusSeconds(1))));
        rejected("missing", () -> catalog.read(down, null));

        try {
            catalog.read(() -> { throw new IllegalStateException("schema"); }, recent);
            throw new AssertionError("Unexpected fallback");
        } catch (IllegalStateException expected) {
            System.out.println("propagated=" + expected.getMessage());
        }

        // Hold both permits through nested calls; the third call must not run.
        catalog.read(() -> catalog.read(() -> {
            rejected("capacity", () -> catalog.read(() -> {
                throw new AssertionError("Primary ran without a permit");
            }, recent));
            return "inner";
        }, recent).value(), recent);
        System.out.println(catalog.read(() -> "recovered", recent));
    }
}
```

```sh
javac --release 21 FallbackDemo.java
java FallbackDemo
```

The following output was obtained with Zulu JDK `21.0.1+12-LTS`.

```text
Reply[value=live-description, source=primary, ageSeconds=0]
Reply[value=saved-description, source=snapshot, ageSeconds=30]
Reply[value=boundary, source=snapshot, ageSeconds=60]
rejected=age
rejected=age
rejected=missing
propagated=schema
rejected=capacity
Reply[value=recovered, source=primary, ageSeconds=0]
```

`source=snapshot` and `ageSeconds` are application metadata that communicate degraded quality to the client. They do not implement the HTTP `Age` header. The maximum-age comparison uses a precise `Duration`; only the displayed age is reduced to whole seconds.

[Semaphore's `tryAcquire()`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/Semaphore.html) fails without waiting when no permit is available. This example includes fallback responses in the same admission limit, so it does not even return a copy when already saturated. To allow a cheap path dedicated to copies in production, give that path its own limit as well. The nested calls demonstrate deterministic permit exhaustion; they are not a concurrent load test.

The example does not implement storing and refreshing successful reads, storage limits and eviction, request coalescing, or restoring copies after a restart. In production, update copies only from successful reads, and **do not rewrite the stored timestamp when returning a copy**. Updating it for every fallback response can make an old value acceptable forever. Long-lived copies also need a freshness policy that accounts for clock adjustments.

## Define the conditions for ending the outage too

[Google SRE's guidance on handling overload](https://sre.google/sre-book/handling-overload/) explains that returning an error may be necessary when even a degraded response is unaffordable. If admission rejection or the absence of a valid copy makes the service temporarily unavailable, you can use 503 according to the HTTP contract. You can send `Retry-After` if there is a reliable time to retry, but the header alone does not prevent a client surge. 504 means a gateway or proxy did not receive a timely response from an upstream server; it is not a code for every application timeout. [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html#name-server-error-5xx)

Sending all requests back to the primary as soon as a circuit breaker closes can overwhelm a recovering server again. Check its state with limited half-open probe calls, then increase traffic gradually while also limiting snapshot refresh and cache refill requests. Define in advance when to stop expansion or return to the previous stage if normal-response latency, failure rate, DB connection waits, or queue backlog exceed acceptable ranges. Determine specific proportions and observation periods through actual load testing.

For an initial rollout, choose one optional read path and inject dependency failures. Then check missing copies, the permitted-age boundary, future timestamps, full admission saturation, unclassified exceptions, and dependency recovery. On real servers, also test slow responses and connection-pool exhaustion, complete cache failure, simultaneous failures of primary and fallback paths, and simultaneous retries during recovery.

Separate normal results, fallback results, rejections, and failures in operational metrics. Looking only at the HTTP 200 rate can hide an outage in which most responses are stale. Track the fallback-response ratio, data age, failures by dependency, admission rejections, and in-flight requests together. **Distinguish requests that actually complete the business function from requests handled with reduced quality** to judge whether fallback reduced the impact of the outage.
