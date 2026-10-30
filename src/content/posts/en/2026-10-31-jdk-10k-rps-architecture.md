---
language: "en"
translationKey: "2026-10-31-jdk-10k-rps-architecture"
routeSlug: "2026-10-31-jdk-10k-rps-architecture"
kind: "post"
categories: ["jdk"]
tags: ["java", "jdk27", "architecture", "capacity-planning", "virtual-threads", "load-testing"]
publishedAt: "2026-10-30T23:21:33.758647+00:00"
updatedAt: "2026-10-30T23:21:33.758647+00:00"
title: "Designing a 10k RPS API on Modern JDK: Capacity and Overload Control"
description: "Plan a 10,000 RPS HTTP API on JDK 27 with explicit capacity, database and failure budgets. Run a virtual-thread admission demo and distinguish design assumptions from load-test evidence."
reviewedAt: "2026-10-31"
reviewStatus: "revised"
reviewScope: "Primary JDK, SRE, PostgreSQL, retry, queueing and load-generator sources; offline JDK 27 admission semantics. Calculations illustrative. No 10k HTTP benchmark, infrastructure deployment, database/cache/queue integration or production capacity validation."
reviewSources: ["https://openjdk.org/projects/jdk/27/", "https://www.oracle.com/java/technologies/java-se-support-roadmap.html", "https://docs.oracle.com/en/java/javase/27/core/virtual-threads.html", "https://docs.oracle.com/en/java/javase/27/docs/api/java.base/java/util/concurrent/Semaphore.html", "https://web.mit.edu/2.810/www/files/lectures/lec1-intro-2019.pdf", "https://sre.google/sre-book/handling-overload/", "https://www.postgresql.org/docs/18/runtime-config-connection.html", "https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/", "https://grafana.com/docs/k6/latest/using-k6/scenarios/executors/constant-arrival-rate/", "https://grafana.com/docs/k6/latest/using-k6/scenarios/concepts/dropped-iterations/", "https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html"]
---
A **10,000-requests-per-second HTTP API needs explicit request and dependency capacity budgets and overload behavior before it needs a newer JDK**. Start with stateless API replicas across availability zones, request admission limits and per-dependency concurrency limits. Add caches, queues and read replicas according to measured bottlenecks and consistency requirements. This is a design guide with illustrative calculations, **not a report of a successful 10k RPS load test**.

As of October 31, 2026, the latest GA release is [JDK 27](https://openjdk.org/projects/jdk/27/). The code below was checked on Temurin `27.0.1.0.2+1`. Separate feature freshness from support duration: the [Oracle support roadmap](https://www.oracle.com/java/technologies/java-se-support-roadmap.html) lists JDK 25 as LTS and 27 as non-LTS. Check other suppliers’ support policies and framework compatibility in their own documentation.

## Define the 10k boundary and success criteria

Here, 10k means **requests per second reaching the API load balancer**, excluding static CDN hits. It does not mean concurrent connections or virtual-thread count. Record offered RPS, completed business-success RPS, rejections and failures separately. Fast error responses alone do not establish capacity.

These assumptions illustrate the calculations. They are neither measurements of a real service nor recommended configuration values.

| Item | Illustrative assumption |
| --- | --- |
| Offered target | 10,000 RPS |
| Read/write mix | 90% / 10% |
| Read-cache hit rate | 80% |
| Steady-state mean API residence time | 50ms |
| Response objective | p99 below 200ms; failure rate below 0.1% |
| Database use | One visit per read miss/write; mean connection hold time 10ms |

[Little’s law](https://web.mit.edu/2.810/www/files/lectures/lec1-intro-2019.pdf#page=56), `L = λ × W`, applies to **averages** across the same boundary in a stable system. Assuming normal throughput of 10,000/s and mean residence time of 0.05 seconds gives about 500 requests in progress on average across the fleet. Do not substitute p99 200ms to calculate mean concurrency or turn 500 directly into a hard cap. Bursts, latency distributions and failure headroom need separate validation.

Database visits are `9,000 × (1 − 0.8) + 1,000 = 2,800/s`; mean occupied connections are `2,800 × 0.01 = 28`. **This does not recommend a pool size of 28.** Multiple statements, locks, transactions and cache failure change the assumptions. Include response bytes, TLS, replication and logging in the bandwidth budget too.

## Reference architecture: replicate a small service horizontally

![Edge and load balancer feeding multi-zone JDK API replicas, optional read cache, DB pools, external-service limits and optional DB-outbox delivery to workers](/assets/img/architecture/10k-rps-en.svg)

This is a proposed layout. The Java example below implements only the admission-control principle, not the whole infrastructure. A target of 10k RPS alone does not establish a need for microservices or sharding. Replicate a stateless modular application, then separate the bottlenecks measurements reveal.

- **Edge and load balancer:** Bound per-client request rates, connections, request-body sizes and slow connections. Cache only suitable public responses at the CDN; design keys and scope separately for authenticated data. Use health checks and draining to keep new requests away from unready replicas.
- **API replicas:** Limit in-flight work at the request boundary and use virtual threads for readable blocking-I/O code. Virtual threads do not enlarge database capacity or accelerate CPU calculations. As the [JDK 27 guide](https://docs.oracle.com/en/java/javase/27/core/virtual-threads.html) explains, constrain scarce resources separately with mechanisms such as semaphores.
- **Cache and database:** A read cache is optional. Test TTL spreading, miss coalescing and database traffic during cache failure. Inspect indexes, query plans and transaction duration first. Use read replicas only where replication lag is acceptable.
- **External calls and asynchronous work:** Give each dependency its own concurrency budget. Queue only work that need not finish before the response. When database writes and message delivery must be coordinated, design a [transactional outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html) with retryable delivery and idempotent consumers. Queues are bounded resources too: observe backlog, oldest-message age and processing failures.

Design fast rejection and resource protection as normal operational behavior, as described in [Google SRE’s overload guidance](https://sre.google/sre-book/handling-overload/). CPU-only scaling can miss I/O stalls; observe in-flight requests, rejection rate, connection-acquisition waits and dependency saturation together.

## How many replicas and database connections?

On fixed hardware, heap, container CPU limits and request mix, measure `q_safe`: **per-replica throughput that meets the SLO and agreed operational headroom**. This article has not measured it.

If tests actually establish `q_safe = 2,500 RPS`, four replicas cover the normal target arithmetically. Five provide a starting point for retaining 10k after one replica fails. That does not guarantee zone-failure capacity. Six replicas, two in each of three zones, leave four after one zone fails and thus cover 10k on paper, but load-balancer redistribution, zone skew and database/cache failover must also be tested. Keep headroom for the period before autoscaling completes.

Do not increase database pools independently per replica. For each database endpoint, keep `maximum simultaneously existing API replicas × per-replica pool limit + worker connections + operational reserve` within its available connection budget. Count overlapping replicas during scale-out, rolling deployment and termination grace periods. [PostgreSQL’s documentation](https://www.postgresql.org/docs/18/runtime-config-connection.html) explains that raising `max_connections` increases resource allocations, including shared memory. More connections do not fix slow queries.

## A minimal virtual-thread admission example

![The gate rejects failed acquisition or runs synchronous work, returns the permit in finally and then returns a result or propagates an exception](/assets/diagrams/2026-10-31-jdk-10k-rps-architecture-en.svg)

The diagram follows `Gate.call()`. The `main()` method is an **admission-semantics demonstration without an HTTP server**, creating two operations and a rejection. The limit of two is for testing, not a 10k RPS configuration. In a real server, apply admission before expensive work and also bound connections, server queues and virtual-thread creation before the gate through edge and server controls.

### `AdmissionDemo.java`

```java
import java.util.concurrent.Callable;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.RejectedExecutionException;
import java.util.concurrent.Semaphore;

public class AdmissionDemo {
    static final class Gate {
        private final Semaphore permits;
        Gate(int limit) {
            if (limit <= 0) throw new IllegalArgumentException("limit must be positive");
            permits = new Semaphore(limit);
        }
        <T> T call(Callable<T> work) throws Exception {
            if (!permits.tryAcquire()) throw new RejectedExecutionException("busy");
            try {
                return work.call();
            } finally {
                permits.release();
            }
        }
        int available() { return permits.availablePermits(); }
    }

    public static void main(String[] args) throws Exception {
        Gate gate = new Gate(2);
        CountDownLatch entered = new CountDownLatch(2);
        CountDownLatch release = new CountDownLatch(1);
        Callable<String> request = () -> gate.call(() -> {
            if (!Thread.currentThread().isVirtual()) throw new AssertionError("virtual thread required");
            entered.countDown();
            release.await();
            return "ok";
        });
        try (var tasks = Executors.newVirtualThreadPerTaskExecutor()) {
            var first = tasks.submit(request);
            var second = tasks.submit(request);
            try {
                entered.await();
                System.out.println("admitted=2");
                try {
                    gate.call(() -> "unexpected");
                    throw new AssertionError("capacity exceeded");
                } catch (RejectedExecutionException expected) {
                    System.out.println("overload=rejected");
                }
            } finally {
                release.countDown();
            }
            System.out.println("completed=" + first.get() + "," + second.get());
        }
        try {
            gate.call(() -> { throw new IllegalStateException("demonstration"); });
        } catch (IllegalStateException expected) {
            System.out.println("failure=propagated");
        }
        System.out.println("available=" + gate.available());
    }
}
```

```sh
javac --release 27 AdmissionDemo.java
java AdmissionDemo
```

This output was observed with `javac` and `java` from the same JDK 27 installation. No preview flags are needed.

```text
admitted=2
overload=rejected
completed=ok,ok
failure=propagated
available=2
```

Failure of [`tryAcquire()`](https://docs.oracle.com/en/java/javase/27/docs/api/java.base/java/util/concurrent/Semaphore.html#tryAcquire()) rejects work instead of queuing it. `finally` returns the permit when the actual operation ends, and exceptions propagate to the caller. This is **a concurrency limit, not a requests-per-second limiter**. An HTTP adapter can map service-capacity rejection to a response such as 503, separately from per-client quotas. This code does not implement HTTP status mapping, authentication, deadlines or database pools.

## Keep deadlines and retries from amplifying overload

Set an end-to-end deadline and allocate the remaining budget to database acquisition, queries, HTTP connection and response reads. Adding stage p99 values does not produce end-to-end p99. A caller timing out does not instantly stop real database or HTTP work; verify driver/client cancellation and resource return. Returning a concurrency permit while the underlying operation still runs breaks the limit.

Retry at one layer with bounded attempts, an overall deadline, exponential backoff and jitter, restricting retries to suitable errors and operations with established idempotency. As [Amazon’s timeout and retry guidance](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) explains, retries can add load. Define duplicate prevention and result-lookup behavior first for payments and orders.

## What must pass before claiming 10k capacity?

Prepare the actual HTTP server, production-like data, TLS, authentication and response sizes, then test in this order.

1. Raise load on one replica to establish `q_safe`. Record CPU, GC, allocation, sockets, locks, database waits, successful RPS and end-to-end p99 together.
2. After preparation and warmup, raise offered traffic across the complete layout through 1k→3k→5k→10k and sustain the target for an agreed duration. Include duration and data distribution in the results.
3. With an open workload model such as [k6 constant-arrival-rate](https://grafana.com/docs/k6/latest/using-k6/scenarios/executors/constant-arrival-rate/), connect 10,000 iterations/s to 10k HTTP RPS only after confirming **one HTTP request per iteration, with automatic redirects and retries disabled**. Check generator CPU, networking, VU headroom and [dropped_iterations](https://grafana.com/docs/k6/latest/using-k6/scenarios/concepts/dropped-iterations/). A test that never generated its target input does not prove server capacity.
4. Test replica/zone loss, cold or failed caches, slow databases/dependencies, rolling deployment and bursts. Exclude rejected responses from business successes and check recovery, queue drainage and connection leaks after saturation.

Only gate rejection and permit return after normal/failing operations were executed for this article. The complete architecture has not undergone a load test. See the [JDK 21/25 virtual-thread comparison](/en/posts/2026-10-31-virtual-threads-jdk21-jdk25/) and [ScopedValue request-context boundaries](/en/posts/2026-10-31-jdk25-scopedvalue/) separately from production architecture validation.
