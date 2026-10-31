---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2026-10-31-virtual-threads-jdk21-jdk25",
  "routeSlug": "2026-10-31-virtual-threads-jdk21-jdk25",
  "kind": "post",
  "title": "Java 虚拟线程：比较 JDK 21、25，并用 JFR 观察固定行为",
  "description": "了解虚拟线程载体与 I/O 等待，通过可运行的 JFR 探针比较 JDK 21 和 25 在 synchronized 中的载体固定行为，区分正式 API、预览与剩余瓶颈。",
  "categories": [
    "jdk"
  ],
  "tags": [
    "java",
    "virtual-threads",
    "jdk21",
    "jdk25",
    "jfr",
    "pinning"
  ],
  "sourcePath": "src/content/posts/en/2026-10-31-virtual-threads-jdk21-jdk25.md",
  "sourceSha256": "4b100d81b2721e31e0a765676927aa48165b4b60c224dff2ba5846ba70dec8db",
  "draftSha256": "55de7c26935c9020dcd0e21b7242efb99128030d1935018f1f879454a3f456e4",
  "manifestPath": ".pipeline/technical-translations/batch-078/manifest.json",
  "manifestSha256": "e685b2de5dafd8cfff8e8e996fa2b09613becb072bdd575b58b9eca9651474a3",
  "publishedAt": "2026-10-31T02:49:44.828Z",
  "updatedAt": "2026-10-31T02:49:44.828Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 118,
    "approvedAt": "2026-10-31T02:49:44.828Z",
    "basis": "2026-10-31 user instruction “진행해줘” immediately following delivery of the reviewed 72 complete translations in PR #118; interpreted as authorization to publish exactly batch-078 in all six languages. Separate AI language review is recorded in the manifest; this does not claim a human line-by-line review. Excludes the older 120 technical drafts and 318 pending news translations."
  }
}
---
虚拟线程是**让大量任务在等待 I/O 时共享较少操作系统线程的 Java 线程**。它们在 JDK 21 中通过 [JEP 444](https://openjdk.org/jeps/444)定稿，JDK 25 保留相同的基本 API。一个重要区别是在 `synchronized` 内阻塞时的载体固定： [JEP 491](https://openjdk.org/jeps/491)在 JDK 24 中改进了这一点，JDK 25 也包含该改进。

## 轻量体现在哪里？

虚拟线程执行时仍需要操作系统线程。JVM 将执行它的平台线程称为**载体（carrier）**。当受支持的阻塞操作让虚拟线程卸载时，载体就可以运行另一个虚拟线程。

这有助于处理大量并发等待的请求。它不会加速 CPU 计算，也不会自动降低单个请求的延迟。[官方采用指南](https://docs.oracle.com/en/java/javase/25/core/virtual-threads.html)建议每个任务使用一个虚拟线程，不鼓励在小型线程池中复用虚拟线程。数据库连接容量与外部 API 配额不会随线程数增长；应通过信号量、连接池等机制单独限制这些资源。

## JDK 21 与 25 的区别

| 项目 | JDK 21 | JDK 25 |
| --- | --- | --- |
| 虚拟线程 API | 已定稿；无需预览标志 | 已定稿；保留基本创建 API |
| 在 `synchronized` 内阻塞 | 可能固定载体，限制可扩展性 | 包含 JDK 24 的 JEP 491 改进 |
| 是否消除所有固定 | 否 | 否；原生代码回调到会阻塞的 Java 等路径仍然存在 |
| 诊断 | JFR 以及 `jdk.tracePinnedThreads` 等机制 | 保留并增强 JFR；`jdk.tracePinnedThreads` 不生效 |
| `ScopedValue` | 预览 | 通过 JEP 506 定稿 |
| 结构化并发 | 预览 | 仍是独立预览；不要假定与旧 API 兼容 |

结合阅读 [JDK 21 指南](https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html)、JEP 491 和 [ScopedValue 文章](/en/posts/2026-10-31-jdk25-scopedvalue/)，以区分这些变化。虚拟线程、ScopedValue 和结构化并发并非在同一时间表上定稿。

固定会阻止等待中的虚拟线程释放其载体。在 JDK 25 中，仅仅是普通使用 `synchronized`，并不构成将所有监视器替换为 `ReentrantLock` 的理由。不过，**释放载体与释放监视器锁不同**。`synchronized` 内的慢 I/O 仍会阻止其他任务取得该锁，因此临界区大小和锁争用仍然重要。

## 使用 JFR 观察同一段代码

![验证模式，启动 JFR，在虚拟线程上于监视器内外执行相同等待，然后仅统计该工作线程的固定事件](/assets/diagrams/technical/zh-CN-2026-10-31-virtual-threads-jdk21-jdk25.svg)

代码比较两种模式：`monitor` 在 `synchronized` 内执行 `Thread.sleep(100)`，`plain` 则不使用该代码块直接休眠。它不发送真实网络或数据库请求。通过 [Recording](https://docs.oracle.com/en/java/javase/21/docs/api/jdk.jfr/jdk/jfr/Recording.html)将事件阈值设为零，然后使用 [RecordingFile](https://docs.oracle.com/en/java/javase/21/docs/api/jdk.jfr/jdk/jfr/consumer/RecordingFile.html)仅统计工作线程的事件。

为每套 JDK 在新目录中保存文件，并使用同一安装中的 `javac` 和 `java`。需要包含 JFR 的 HotSpot JDK；不使用预览标志。程序创建 `monitor.jfr` 和 `plain.jfr`，如果目标文件已存在则拒绝运行。

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

以下输出是在 macOS AArch64 上使用 Eclipse Temurin `21.0.13+9` 观察到的。

```text
virtual=true
monitor-pinned-events=1
virtual=true
plain-pinned-events=0
```

同一平台上的 Eclipse Temurin `25.0.5+8` 产生以下输出：

```text
virtual=true
monitor-pinned-events=0
virtual=true
plain-pinned-events=0
```

`Future.get()` 等待完成，并将任务失败传播给调用方。录制在读取前停止并转储，因此聚合不会与正在进行的录制竞争。没有限制载体数量，也没有比较总执行时间。事件数描述的是这一个任务；未经检查，不要将确切次数推广到其他 JVM、补丁或插桩条件。

## 升级后仍需检查什么？

JDK 25 中的零事件专门适用于**本例在监视器内的等待**。它没有验证涉及原生调用、外部函数调用或类初始化的剩余路径。在 JDK 21 中有用的 `-Djdk.tracePinnedThreads=full` 在 JDK 25 中没有作用；应改用该版本的 JFR 事件和线程转储。

从以 I/O 等待为主的工作负载开始采用，并一并审查数据库连接池、外部调用并发、超时与取消。CPU 密集型工作、过长临界区和大型线程私有缓存仍可能成为瓶颈。应在有代表性的生产负载下测量吞吐量、尾延迟、内存和锁争用；不要根据这个小型观察程序计算性能提升比例。有关虚拟线程执行所关联的上下文，请继续阅读 ScopedValue 文章中的绑定与异步边界规则。
