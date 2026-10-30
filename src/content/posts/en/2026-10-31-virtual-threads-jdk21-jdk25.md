---
language: "en"
translationKey: "2026-10-31-virtual-threads-jdk21-jdk25"
routeSlug: "2026-10-31-virtual-threads-jdk21-jdk25"
kind: "post"
categories: ["jdk"]
tags: ["java", "virtual-threads", "jdk21", "jdk25", "jfr", "pinning"]
publishedAt: "2026-10-30T16:28:45.702813+00:00"
updatedAt: "2026-10-30T16:28:45.702813+00:00"
title: "Java Virtual Threads: JDK 21 vs 25 and Pinning with JFR"
description: "Understand virtual-thread carriers and I/O waits, compare JDK 21 and 25 synchronized pinning with a runnable JFR probe, and distinguish final APIs from previews and remaining bottlenecks."
reviewedAt: "2026-10-31"
reviewStatus: "revised"
reviewScope: "Primary JEP and JDK documentation; source-derived HotSpot JFR observation on JDK 21 and 25, monitor/plain control. No throughput, latency, production migration or remaining-native-path benchmark."
reviewSources: ["https://openjdk.org/jeps/444", "https://openjdk.org/jeps/491", "https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html", "https://docs.oracle.com/en/java/javase/25/core/virtual-threads.html", "https://openjdk.org/jeps/506", "https://openjdk.org/jeps/505", "https://docs.oracle.com/en/java/javase/21/docs/api/jdk.jfr/jdk/jfr/Recording.html", "https://docs.oracle.com/en/java/javase/21/docs/api/jdk.jfr/jdk/jfr/consumer/RecordingFile.html"]
---
Virtual threads are **Java threads that let many tasks share a smaller set of OS threads while waiting for I/O**. They became final in JDK 21 through [JEP 444](https://openjdk.org/jeps/444), and JDK 25 retains the same basic APIs. An important difference is pinning while blocking inside `synchronized`: [JEP 491](https://openjdk.org/jeps/491) improved this in JDK 24, and JDK 25 includes that improvement.

## What becomes lightweight?

A virtual thread still needs an OS thread to execute. The JVM calls the platform thread executing it a **carrier**. When a supported blocking operation lets the virtual thread unmount, the carrier can run another virtual thread.

This helps request processing with many concurrent waits. It does not make CPU calculations faster or automatically reduce a single request’s latency. The [official adoption guide](https://docs.oracle.com/en/java/javase/25/core/virtual-threads.html) recommends a virtual thread per task and discourages reusing virtual threads in a small pool. Database connection capacity and external API allowances do not grow with thread count; limit those resources separately through mechanisms such as semaphores and connection pools.

## Differences between JDK 21 and 25

| Area | JDK 21 | JDK 25 |
| --- | --- | --- |
| Virtual-thread APIs | Final; no preview flags | Final; basic creation APIs retained |
| Blocking inside `synchronized` | Can pin the carrier and limit scalability | Includes JDK 24’s JEP 491 improvement |
| Elimination of all pinning | No | No; paths such as native code calling back into Java that blocks remain |
| Diagnostics | JFR and mechanisms such as `jdk.tracePinnedThreads` | JFR retained and enhanced; `jdk.tracePinnedThreads` has no effect |
| `ScopedValue` | Preview | Final through JEP 506 |
| Structured concurrency | Preview | Still a separate preview; do not assume compatibility with earlier APIs |

Read the [JDK 21 guide](https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html), JEP 491 and the [ScopedValue article](/en/posts/2026-10-31-jdk25-scopedvalue/) together to distinguish these changes. Finalization of virtual threads, ScopedValue and structured concurrency does not occur on a single shared schedule.

Pinning prevents a waiting virtual thread from releasing its carrier. In JDK 25, ordinary `synchronized` use alone is not a reason to replace every monitor with `ReentrantLock`. However, **releasing a carrier is different from releasing a monitor lock**. Slow I/O inside `synchronized` still prevents other tasks from acquiring that lock, so critical-section size and lock contention still matter.

## Observe the same code with JFR

![Validate the mode, start JFR, perform the same wait inside or outside a monitor on a virtual thread, then count only that worker’s pinning events](/assets/diagrams/2026-10-31-virtual-threads-jdk21-jdk25-en.svg)

The code compares a `monitor` mode that executes `Thread.sleep(100)` inside `synchronized` with a `plain` mode that sleeps without the block. It makes no real network or database requests. It sets the event threshold to zero through [Recording](https://docs.oracle.com/en/java/javase/21/docs/api/jdk.jfr/jdk/jfr/Recording.html), then uses [RecordingFile](https://docs.oracle.com/en/java/javase/21/docs/api/jdk.jfr/jdk/jfr/consumer/RecordingFile.html) to count only the worker thread’s events.

For each JDK, save the file in a new directory and use `javac` and `java` from the same installation. A HotSpot JDK including JFR is required; no preview flags are used. The program creates `monitor.jfr` and `plain.jfr` and refuses to run when the destination already exists.

### `VirtualThreadProbe.java`

```java
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.concurrent.Executors;
import jdk.jfr.Recording;
import jdk.jfr.consumer.RecordingFile;

public class VirtualThreadProbe {
    public static void main(String[] args) throws Exception {
        if (args.length != 1 || !(args[0].equals("monitor") || args[0].equals("plain"))) {
            throw new IllegalArgumentException("Usage: VirtualThreadProbe monitor|plain");
        }
        String mode = args[0];
        Path destination = Path.of(mode + ".jfr");
        if (Files.exists(destination)) {
            throw new IllegalStateException("Use a new directory: recording already exists");
        }
        Object monitor = new Object();
        long workerId;
        try (var recording = new Recording()) {
            recording.enable("jdk.VirtualThreadPinned").withThreshold(Duration.ZERO);
            recording.start();
            try (var tasks = Executors.newVirtualThreadPerTaskExecutor()) {
                workerId = tasks.submit(() -> {
                    Thread current = Thread.currentThread();
                    System.out.println("virtual=" + current.isVirtual());
                    if (mode.equals("monitor")) {
                        synchronized (monitor) { Thread.sleep(100); }
                    } else {
                        Thread.sleep(100);
                    }
                    return current.threadId();
                }).get();
            }
            recording.stop();
            recording.dump(destination);
        }
        long pinnedEvents = 0;
        try (var events = new RecordingFile(destination)) {
            while (events.hasMoreEvents()) {
                var event = events.readEvent();
                if (event.getEventType().getName().equals("jdk.VirtualThreadPinned")
                        && event.getThread() != null
                        && event.getThread().getJavaThreadId() == workerId) {
                    pinnedEvents++;
                }
            }
        }
        System.out.println(mode + "-pinned-events=" + pinnedEvents);
    }
}
```

```sh
javac --release 21 VirtualThreadProbe.java
java VirtualThreadProbe monitor
java VirtualThreadProbe plain
```

This output was observed on Eclipse Temurin `21.0.13+9` for macOS AArch64.

```text
virtual=true
monitor-pinned-events=1
virtual=true
plain-pinned-events=0
```

Eclipse Temurin `25.0.5+8` on the same platform produced:

```text
virtual=true
monitor-pinned-events=0
virtual=true
plain-pinned-events=0
```

`Future.get()` waits for completion and propagates task failures to the caller. The recording is stopped and dumped before reading, so aggregation does not race with an active recording. Carrier count was not constrained, and total execution times were not compared. Event counts describe this one task; do not generalize exact counts to other JVMs, patches or instrumentation conditions without checking them.

## What still needs checking after an upgrade?

Zero events on JDK 25 applies specifically to **this example’s wait inside a monitor**. It does not verify remaining paths involving native or foreign-function calls or class initialization. Setting `-Djdk.tracePinnedThreads=full`, useful in JDK 21, has no effect in JDK 25; use that version’s JFR events and thread dumps instead.

Start adoption with workloads dominated by I/O waits and review database pools, external-call concurrency, timeouts and cancellation together. CPU-heavy work, long critical sections and large per-thread caches can remain bottlenecks. Measure throughput, tail latency, memory and lock contention under representative production load; do not calculate a performance improvement ratio from this small observation program. For context associated with virtual-thread execution, continue with the ScopedValue article’s binding and asynchronous-boundary rules.
