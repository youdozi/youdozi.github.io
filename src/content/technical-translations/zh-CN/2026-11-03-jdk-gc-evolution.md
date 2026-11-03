---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2026-11-03-jdk-gc-evolution",
  "routeSlug": "2026-11-03-jdk-gc-evolution",
  "kind": "post",
  "title": "JDK 垃圾回收：从 JDK 27 回溯至 1.4，了解 G1、ZGC、Shenandoah 和 CMS",
  "description": "从 JDK 27 和 28 EA 回溯到早期版本，梳理 HotSpot GC 的引入、默认设置和移除历程。比较各收集器，并运行可复现的 GC 日志示例。",
  "categories": [
    "java"
  ],
  "tags": [
    "jdk",
    "gc",
    "g1",
    "zgc",
    "shenandoah",
    "jvm",
    "performance"
  ],
  "sourcePath": "src/content/posts/en/2026-11-03-jdk-gc-evolution.md",
  "sourceSha256": "01667d7b4b2824ee749cd29f79a08f74627c3725ff551aa08ed090d48f9fd693",
  "draftSha256": "a2f2b10890b2e432f6fd9316929b802be940c6b43f5bf716fe021d1cd7b66a53",
  "manifestPath": ".pipeline/technical-translations/batch-137/manifest.json",
  "manifestSha256": "a47db22796f8ae3ce1acbdd6162e7da37c5147ddcf9399188f2018d3829bfcf4",
  "publishedAt": "2026-11-03T01:49:36.356Z",
  "updatedAt": "2026-11-03T01:49:36.356Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 137,
    "approvedAt": "2026-11-03T01:49:36.356Z",
    "basis": "사용자가 JDK GC 한영 글 게시 완료 후 다국어 지원도 진행해줘라고 요청하여 기존 지원 언어 여섯 개의 전체 번역과 현지화 그림 게시를 승인함. 별도 AI 검토는 사용자 게시 승인과 구분함."
  }
}
---

**对于现代 HotSpot，先通过测量建立 G1 基线；若延迟目标严格，则比较 ZGC 或 Shenandoah；若更看重吞吐量，则考虑 Parallel GC。** 复制旧的 JVM 参数之前，先确认实际 JDK 发行版使用哪个默认收集器，以及包含哪些实现。

本文的参考日期为 **2026-11-03**。[JDK 27](https://jdk.java.net/27/) 是最新的正式发布功能版本；[JDK 28 处于 Early Access 阶段](https://jdk.java.net/28/)。本文涵盖 **OpenJDK HotSpot**，并非所有 JVM 实现。Oracle 的 LTS 版本线——8、11、17、21 和 25——是常见的部署选择，但支持期限和更新条款取决于发行商。[Oracle 支持路线图](https://www.oracle.com/java/technologies/java-se-support-roadmap.html)

## 从最新 JDK 回溯到早期版本

| JDK | 主要 GC 变化 | 现有部署需要检查的事项 |
| --- | --- | --- |
| **28 EA** | 将 Shenandoah 的分代模式设为默认模式的 [JEP 535](https://openjdk.org/jeps/535) 处于 Targeted 状态 | 不要将其视为已在 GA 版本中交付。这并不会使 Shenandoah 成为 JVM 全局默认收集器 |
| **27** | [JEP 523](https://openjdk.org/jeps/523) 不再考虑 CPU 数量和内存大小，默认选择 G1 | 对于过去在小型环境中选择 Serial 的服务，重新检查其默认设置 |
| **26** | [JEP 522](https://openjdk.org/jeps/522) 减少 G1 的同步开销，以提高吞吐量 | 上游的改进并不意味着你的服务也能获得相同比例的提升 |
| **25** | [JEP 521](https://openjdk.org/jeps/521) 将分代 Shenandoah 从实验性功能提升为正式功能 | 模式可用与默认选择该模式是不同的变化 |
| **24 / 23** | 24 移除非分代 ZGC（[JEP 490](https://openjdk.org/jeps/490)）；23 在选择 ZGC 时默认使用分代模式（[JEP 474](https://openjdk.org/jeps/474)）。24 还引入实验性的分代 Shenandoah（[JEP 404](https://openjdk.org/jeps/404)） | ZGC 内部的默认模式发生变化，并不等于 JVM 默认收集器发生变化 |
| **21 / 17 / 15** | 21 引入分代 ZGC（[JEP 439](https://openjdk.org/jeps/439)）。ZGC 和 Shenandoah 在 15 中成为正式功能（[JEP 377](https://openjdk.org/jeps/377)、[379](https://openjdk.org/jeps/379)），因此在 17 中也属于正式功能 | 在 21 中显式选择分代 ZGC。分别检查平台和发行版是否提供支持 |
| **14 / 12 / 11** | 14 移除 CMS（[JEP 363](https://openjdk.org/jeps/363)）。12 添加实验性 Shenandoah（[JEP 189](https://openjdk.org/jeps/189)）；11 引入实验性 ZGC 和 Epsilon（[JEP 333](https://openjdk.org/jeps/333)、[318](https://openjdk.org/jeps/318)） | 区分历史上的实验状态与目前的正式功能状态；最初的支持并未覆盖所有平台 |
| **9** | G1 成为服务器配置的默认收集器（[JEP 248](https://openjdk.org/jeps/248)）；CMS 被弃用（[JEP 291](https://openjdk.org/jeps/291)）；统一 GC 日志引入（[JEP 271](https://openjdk.org/jeps/271)） | 不要原样迁移 JDK 8 的日志解析器和选项 |
| **8** | Parallel 是服务器级机器以吞吐量为目标时的默认收集器；G1 和 CMS 是可选项。PermGen 被移除（[JEP 122](https://openjdk.org/jeps/122)） | Parallel 并非所有环境中的默认收集器。不要把 PermGen 参数带入新部署 |
| **7u4 / 6 / 5 / 1.4.1** | Oracle JDK 对 G1 的支持始于 7u4。并行 Full GC 在 5u6 中引入，并在 6 中得到改进。1.4.1 文档介绍了并行年轻代回收和并发老年代回收 | 区分早期 Parallel 的年轻代并行回收与后来引入的老年代并行回收 |

理解 JDK 8 的默认设置时，应结合其[自适应调优指南](https://docs.oracle.com/javase/8/docs/technotes/guides/vm/gctuning/ergonomics.html)。更早的里程碑记录在 [G1 支持历史](https://docs.oracle.com/javase/8/docs/technotes/guides/vm/G1.html)、[Parallel Compaction 说明](https://docs.oracle.com/javase/8/docs/technotes/guides/vm/par-compaction-6.html)和 [JDK 1.4.1 GC 文章](https://www.oracle.com/technical-resources/articles/java/garbagecollection-in-java-applications-using-jdk141.html)中。历史上的堆大小建议和暂停目标反映的是当时的情况，并非当前的部署默认值。

表格选取了重要里程碑，既不是每次更新修复的完整清单，也不表示本文实际运行了所有历史版本。

## 选择收集器之前，先区分三个概念

GC 回收的是 **GC Roots 无法到达的对象**所占用的内存；GC Roots 的例子包括运行中线程持有的引用。即使应用已不再需要某些对象，缓存或全局集合仍可能使它们保持可达。分代回收利用了这样一种观察：许多对象很快死亡，而部分对象存活更久，因此对年轻对象和年老对象采用不同的回收方式。[HotSpot GC 实现](https://docs.oracle.com/en/java/javase/27/gctuning/garbage-collector-implementation.html)

**并行（parallel）**是指多个 GC 线程协同工作；**并发（concurrent）**是指部分 GC 工作与应用执行在时间上重叠。两者属于不同维度。**Stop-the-world（STW）**阶段会暂停应用执行。并发收集器仍可能发生短暂停顿或分配停滞；并发并不会消除请求延迟。

标记用于识别存活对象；清扫使可回收空间能够再次使用。压缩通过移动存活对象来合并空闲空间，而转移则把选定区域中的存活对象复制到其他位置。各收集器在分代、区域划分、并行工作和并发工作方面，以不同方式组合这些任务。

| 收集器 | 主要方式 | 比较时需关注的条件 |
| --- | --- | --- |
| Serial | 使用一个 GC 线程；较低的协调开销可能适合小型任务 | 即便堆较小或 CPU 受限，也要测量吞吐量和暂停 |
| Parallel | 使用多个回收线程，优先考虑吞吐量 | 比较批处理完成时间和可容忍的暂停 |
| G1 | 使用区域划分、并发标记和暂停期间的转移 | 可作为通用服务器基线；暂停目标不是实时保证 |
| ZGC | 以并发方式执行大量对象重定位和引用处理，以实现短暂停顿 | 同时观察 CPU 和堆的余量、分配速率以及应用延迟 |
| Shenandoah | 采用并发重定位的低暂停收集器；分代模式的状态因版本而异 | 首先检查发行版是否提供该收集器，以及所选模式 |
| CMS / Epsilon | CMS 是历史上的并发标记清扫收集器；实验性 Epsilon 不回收内存 | 最新 JDK 中已没有 CMS。Epsilon 不能作为通用服务 GC 的替代品 |

对于 Serial 和 Parallel，可从[当前收集器选择指南](https://docs.oracle.com/en/java/javase/27/gctuning/available-collectors.html)入手。[G1 调优指南](https://docs.oracle.com/en/java/javase/27/gctuning/garbage-first-garbage-collector-tuning.html)说明了 G1 的行为和暂停目标。[历史 CMS 文档](https://docs.oracle.com/en/java/javase/13/gctuning/concurrent-mark-sweep-cms-collector.html)描述了并发阶段和碎片化限制；[JEP 318](https://openjdk.org/jeps/318)明确说明 Epsilon 不进行内存回收。

## 除了收集器，也要检查分代模式

对于 JDK 21 中的 ZGC，`-XX:+UseZGC -XX:+ZGenerational` 选择分代模式。在 23 中，`-XX:+UseZGC` 默认采用分代模式；24 移除了非分代实现。将参数标为过时及移除参数，与移除实现是不同的步骤。本实验中的 JDK 27 拒绝了 `-XX:+ZGenerational`，因此不要将其附加到当前配置中。[当前 ZGC 指南](https://docs.oracle.com/en/java/javase/27/gctuning/z-garbage-collector.html)

Shenandoah 需要单独检查。25 中引入的正式分代模式通过 `-XX:+UseShenandoahGC -XX:ShenandoahGCMode=generational` 选择。**在 27 中仅选择 Shenandoah，并不能确定已选择分代模式。** JEP 535 的目标版本是 28，在参考日期仍处于 Targeted 状态。构建选项和向后移植可能影响发行版提供哪些收集器；请检查实际使用的可执行文件。

## 读取同一个分配程序生成的日志

这个**单线程实验**用于展示对象生命周期和 GC 日志。程序分配 8192 个大小为 128 KiB 的数组，数组载荷合计为 1 GiB，同时循环替换 64 个槽位中的引用。最终保留的载荷为 8 MiB；数组头、引用以及 JVM 内存另计。它并未实现生产负载，也不是 GC 基准测试。

![创建 64 个引用槽位，反复分配 128 KiB 数组、替换槽位引用并累加校验和，执行 8192 次后输出结果](/assets/diagrams/technical/zh-CN-2026-11-03-jdk-gc-evolution.svg)

图中展示了代码中的分配和引用替换过程。不可达对象何时被回收由 JVM 决定；代码并未调用 `System.gc()`。不要假设每个被替换的对象都会立即被回收。

### `GcProbe.java`

```java
import java.lang.management.GarbageCollectorMXBean;
import java.lang.management.ManagementFactory;

public final class GcProbe {
    private static volatile byte[][] retained;
    private static volatile long checksum;

    public static void main(String[] args) {
        System.out.println("runtime=" + System.getProperty("java.runtime.version"));
        for (GarbageCollectorMXBean gc : ManagementFactory.getGarbageCollectorMXBeans()) {
            System.out.println("collector=" + gc.getName());
        }
        retained = new byte[64][];
        for (int i = 0; i < 8192; i++) {
            byte[] block = new byte[128 * 1024];
            block[0] = (byte) i;
            retained[i % retained.length] = block;
            checksum += block[0] & 0xff;
        }
        System.out.println("iterations=8192 retainedSlots=" + retained.length
                + " checksum=" + checksum);
    }
}
```

这些数组通过 `retained` 保持从外部可达。这个小程序仍不足以确定生产服务的对象生命周期分布或瓶颈。

### 在 JDK 27 中选择四种收集器并检查日志

这些命令使用 Unix 风格的 shell。将 `GC_JDK` 替换为你的 **JDK 主目录**，把 Java 文件保存到新的工作目录中，并在该目录运行命令。无需外部库或网络请求。每次运行的最大堆为 128 MiB，并使用有大小和数量限制的滚动日志。

```sh
GC_JDK="/path/to/jdk-27"
"$GC_JDK/bin/java" -version
mkdir -p out logs
"$GC_JDK/bin/javac" -d out GcProbe.java
for gc in G1 Parallel Serial Z; do
  "$GC_JDK/bin/java" "-XX:+Use${gc}GC" -Xms128m -Xmx128m \
    '-Xlog:gc*,safepoint:file=logs/gc-%p.log:time,uptime,level,tags:filecount=3,filesize=5M' \
    -cp out GcProbe
done
```

`%p` 会展开为 JVM PID，从而区分不同运行生成的日志。确认四次运行均以下列行结束。前面的运行时和收集器行取决于 JDK 和收集器。

```text
iterations=8192 retainedSlots=64 checksum=1044480
```

实际运行环境为 **macOS arm64、Zulu 8u392-b08，以及 Temurin 21.0.13+9、25.0.5+8 和 27.0.1.0.2+1**。归档版本用于展示历史行为，并非推荐当前采用这些安全更新组合。实际执行范围如下：

| JDK | 已检查的执行情况 |
| --- | --- |
| 8 | 默认 Parallel、显式选择的 G1 和 CMS，包括运行完成及旧式 GC 日志 |
| 21 | 非分代 ZGC 和显式选择的分代 ZGC，包括运行完成和日志 |
| 25 | 通过 ZGC 参数选择的分代 ZGC，包括运行完成和日志 |
| 27 | Serial、Parallel、G1、ZGC、非分代 Shenandoah 和显式选择的分代 Shenandoah，包括运行完成和日志 |

全部 **12 种执行配置**均生成了相同的校验和及 GC 日志。这些执行并未控制各 JDK 之间的实现、优化和安全差异，因此运行耗时或 GC 次数不能用于给收集器排名。28 EA 以及 1.4.1–7、9–20、22–24 和 26 的里程碑已对照上述官方资料核查。

### 一行日志能说明什么

下面是实际发生的 G1 事件，来自 JDK 27，仅移除了时间戳和标签修饰。

```text
GC(0) Pause Young (Normal) (G1 Evacuation Pause) 47M->10M(128M) 1.468ms
```

`47M->10M` 是本次 GC 前后的堆使用量；`(128M)` 是该时刻的堆容量。括号中的值并非总是最大堆。本实验将 `-Xms` 和 `-Xmx` 设为相同值。`1.468ms` 是本次事件的暂停时间，并非服务的 p99，也不是 GC 的总 CPU 开销。单凭这一行既不能排除内存泄漏，也不能确立暂停时间保证。

### JDK 8 还需要不同的日志选项

不要将 JDK 9 的统一日志配置原样应用于 8。使用该 JDK 的编译器重新编译同一源文件，以避免 class 文件版本不匹配。

```sh
GC_JDK="/path/to/jdk-8"
mkdir -p out8 logs
"$GC_JDK/bin/javac" -d out8 GcProbe.java
"$GC_JDK/bin/java" -Xms128m -Xmx128m -XX:+UseConcMarkSweepGC \
  -XX:+PrintGCDetails -XX:+PrintGCDateStamps -Xloggc:logs/jdk8-cms.log \
  -cp out8 GcProbe
```

JDK 27 还拒绝了 `-XX:+UseConcMarkSweepGC`。支持、过时和移除阶段因版本而异；升级时请检查实际的启动消息和退出状态。

按以下方式检查默认收集器的选择。这会向一个**新 JVM**报告一个 CPU，并不会更改运行中服务的 CPU 分配。

```sh
GC_JDK="/path/to/jdk-27"
"$GC_JDK/bin/java" -XX:ActiveProcessorCount=1 -Xms128m -Xmx128m \
  -XX:+PrintCommandLineFlags -version
```

在相同条件下，Temurin 21 输出 `UseSerialGC`，Temurin 27 输出 `UseG1GC`。显式选择收集器会覆盖默认设置。关键在于 JVM 可见的 CPU 和内存；仅凭宿主机规格无法确定容器会选择哪个收集器。

## 生产环境中的比较应该测量什么？

对于现有服务，先记录当前 JDK、发行版、参数和工作负载。在相同请求模式及 CPU/内存预算下，同时观察**应用吞吐量、p95/p99、错误、RSS、堆使用量、分配速率、GC 暂停和并发 GC 的 CPU 使用情况**。如果 GC 线程与应用线程的 CPU 竞争更激烈，即使暂停缩短，应用延迟仍可能变差。

对于 G1，先使用默认设置建立基线，不要固定沿用其他收集器的年轻代大小，再根据需要调整整体堆大小和暂停目标。ZGC 需要为存活对象集和并发回收期间的新分配预留空间。`-Xmx` 并不是进程 RSS，也不是整个容器的内存上限；还应为元空间、线程栈和直接缓冲区预留预算。

如果可达对象持续增长，应先检查保留的引用、缓存边界和请求生命周期。切换收集器不会自动移除可达对象。将服务侧证据与 [LGTM 日志–追踪工作流](/en/posts/2026-11-02-grafana-lgtm-log-trace/)结合分析，同时不要因请求延迟和 GC 事件恰好同时发生，就认定两者存在因果关系。
