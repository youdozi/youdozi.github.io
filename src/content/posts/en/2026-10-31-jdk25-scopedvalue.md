---
language: "en"
translationKey: "2026-10-31-jdk25-scopedvalue"
routeSlug: "2026-10-31-jdk25-scopedvalue"
kind: "post"
categories: ["jdk"]
tags: ["java", "jdk25", "scopedvalue", "threadlocal", "virtual-threads"]
publishedAt: "2026-10-30T16:01:02.378409+00:00"
updatedAt: "2026-10-30T16:01:02.378409+00:00"
title: "JDK 25 ScopedValue: Request Context Beyond ThreadLocal"
description: "Run the finalized ScopedValue API on virtual threads. Observe nested bindings, exception restoration and plain-child non-inheritance, with clear ThreadLocal and structured-concurrency boundaries."
reviewedAt: "2026-10-31"
reviewStatus: "revised"
reviewScope: "JDK 25 primary JEP/API sources; source-derived example and separate API contracts without preview. No StructuredTaskScope inheritance execution, framework integration, production rollout or performance measurement."
reviewSources: ["https://openjdk.org/jeps/506", "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/ScopedValue.html", "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/ScopedValue.Carrier.html", "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/ThreadLocal.html", "https://openjdk.org/jeps/505"]
---
In JDK 25, **`ScopedValue` is a finalized API for binding data such as request context to a bounded execution scope and passing it from callers to callees**. It was finalized by [JEP 506](https://openjdk.org/jeps/506), so no preview flags are needed. A binding applies while the operation supplied to `run()` or `call()` executes; normal completion or an exception restores the previous state.

## How does it differ from ThreadLocal?

Consider it when passing a tenant or trace ID deep into service code would otherwise require adding a parameter to every intermediate method. Ordinary parameters can remain clearer when the value is an explicit input to business logic.

[`ThreadLocal`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/ThreadLocal.html) changes the current thread’s value through `set()` and removes it through `remove()`. Request-scoped use requires careful cleanup, typically in `finally`. Instead of leaving a value set, `ScopedValue` runs the operation that needs it inside a binding.

| Comparison | ThreadLocal | ScopedValue |
| --- | --- | --- |
| Data access | Read and change a value stored for the current thread | Read the binding in the current dynamic execution scope |
| End of scope | Manage request-scoped cleanup explicitly | Restore the previous binding when `run()` or `call()` ends |
| Different value in a callee | `set()` can change the existing stored value | Rebind in a nested scope, then restore the outer value |
| Suitable uses | Mutable per-thread state, among others | Request context passed from callers to callees, among others |

`ScopedValue` neither replaces every use of `ThreadLocal` nor deprecates it. A `private static final` field stores **an access key, not the context value itself**. The same key can resolve to different values depending on the executing thread and scope.

## Observe scope and restoration in a virtual thread

![Bind an outer value in a virtual thread, restore it after nested execution and failure, check a plain child thread’s lack of inheritance, then leave the scope](/assets/diagrams/2026-10-31-jdk25-scopedvalue-en.svg)

The diagram follows the example below. The outer tenant is `tenant-a`; the nested scope reads `tenant-b`. A failing nested scope is caught outside that scope before restoration is checked. This example demonstrates request-context semantics without an HTTP server or framework integration.

Run it in a directory where `javac` and `java` point to the same JDK 25 installation. The local verification environment was Eclipse Temurin `25.0.5+8` on macOS AArch64. `ScopedValue` belongs to `java.lang` and needs no explicit import.

### `ScopedContextExample.java`

```java
import java.util.NoSuchElementException;
import java.util.concurrent.Executors;

public class ScopedContextExample {
    private static final ScopedValue<RequestContext> CONTEXT = ScopedValue.newInstance();
    record RequestContext(String tenant, String traceId) {}

    public static void main(String[] args) throws Exception {
        try (var tasks = Executors.newVirtualThreadPerTaskExecutor()) {
            tasks.submit(ScopedContextExample::handleRequest).get();
        }
    }

    private static String handleRequest() throws InterruptedException {
        System.out.println("virtual=" + Thread.currentThread().isVirtual());
        System.out.println("before=" + CONTEXT.isBound());
        String result = ScopedValue.where(CONTEXT,
                new RequestContext("tenant-a", "trace-123")).call(() -> {
            System.out.println("outer=" + service());
            ScopedValue.where(CONTEXT,
                    new RequestContext("tenant-b", "trace-123")).run(() ->
                System.out.println("nested=" + service()));
            System.out.println("restored=" + service());

            try {
                ScopedValue.where(CONTEXT,
                        new RequestContext("tenant-fail", "trace-123")).run(() -> {
                    throw new IllegalStateException("demonstration");
                });
            } catch (IllegalStateException expected) {
                System.out.println("after-failure=" + service());
            }

            Thread child = Thread.ofVirtual().start(() ->
                System.out.println("plain-child-bound=" + CONTEXT.isBound()));
            child.join();
            return service();
        });
        System.out.println("result=" + result);
        System.out.println("after=" + CONTEXT.isBound());
        try {
            CONTEXT.get();
        } catch (NoSuchElementException expected) {
            System.out.println("outside=" + expected.getClass().getSimpleName());
        }
        return result;
    }

    private static String service() {
        RequestContext context = CONTEXT.get();
        return context.tenant() + "/" + context.traceId();
    }
}
```

```sh
javac --release 25 ScopedContextExample.java
java ScopedContextExample
```

This standard output was observed without preview options. Calling `get()` on the `Future` propagates task failures to the caller; `join()` waits for the child thread’s output.

```text
virtual=true
before=false
outer=tenant-a/trace-123
nested=tenant-b/trace-123
restored=tenant-a/trace-123
after-failure=tenant-a/trace-123
plain-child-bound=false
result=tenant-a/trace-123
after=false
outside=NoSuchElementException
```

`service()` reads the current binding without a context parameter. Use `run()` for an operation without a result and [`Carrier.call()`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/ScopedValue.Carrier.html#call(java.lang.ScopedValue.CallableOp)) for an operation that returns a result or propagates an exception. Merely creating a `Carrier` with `where()` does not activate a binding.

Both `restored` and `after-failure` show the outer value. After the outer `call()` finishes, `isBound()` is false, and an unbound `get()` throws `NoSuchElementException`. Leaving a binding neither guarantees immediate garbage collection of the referent nor automatically closes an `AutoCloseable` resource.

## Does creating a virtual thread inherit the value?

**An ordinary `Thread.ofVirtual().start()` does not automatically inherit its parent’s binding.** The example demonstrates this with `plain-child-bound=false`. Do not assume that handing work to an `ExecutorService` or `CompletableFuture` automatically propagates context either. The first virtual thread in the example establishes its binding inside the task rather than inheriting one.

The [official inheritance rules](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/ScopedValue.html#inheritance) describe capturing bindings when a `StructuredTaskScope` is created and inheriting them in children started through that scope’s `fork()`. **Structured concurrency is a separate preview API in JDK 25**, covered by [JEP 505](https://openjdk.org/jeps/505), and is not used by this article’s code. Do not interpret the example as verifying that inheritance mechanism.

## Boundaries when adopting request context

An unchangeable binding does not make its referent deeply immutable. The example uses a record containing two strings; a mutable collection would require a separate concurrency design. Keep access to the key narrow too.

Check the JDK 25 API instead of copying older preview examples from JDK 21 and similar releases unchanged. In particular, JDK 25 does not permit `orElse(null)`. A binding to `null` is also distinct from having no binding.

First distinguish a `ThreadLocal` that passes request data down the call chain from one that maintains mutable state during execution. For the former, design both the entry-point binding and asynchronous boundaries. Framework transactions, MDC and security context are not connected automatically; this example does not verify those integrations or performance. Continue with the [JDK 21 feature article](/en/posts/2023-09-20-jdk-21-release/) for virtual-thread behavior itself.
