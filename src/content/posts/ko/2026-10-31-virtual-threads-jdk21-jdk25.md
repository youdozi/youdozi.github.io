---
language: "ko"
translationKey: "2026-10-31-virtual-threads-jdk21-jdk25"
routeSlug: "2026-10-31-virtual-threads-jdk21-jdk25"
kind: "post"
categories: ["jdk"]
tags: ["java", "virtual-threads", "jdk21", "jdk25", "jfr", "pinning"]
publishedAt: "2026-10-30T16:28:45.702813+00:00"
updatedAt: "2026-10-30T16:28:45.702813+00:00"
title: "Java 가상 스레드: JDK 21·25의 차이와 pinning 관측"
description: "가상 스레드의 캐리어·I/O 대기 모델을 설명하고 JDK 21·25의 synchronized pinning 차이를 같은 JFR 예제로 확인합니다. 정식 API·미리보기 상태와 남은 병목도 구분합니다."
reviewedAt: "2026-10-31"
reviewStatus: "revised"
reviewScope: "Primary JEP and JDK documentation; source-derived HotSpot JFR observation on JDK 21 and 25, monitor/plain control. No throughput, latency, production migration or remaining-native-path benchmark."
reviewSources: ["https://openjdk.org/jeps/444", "https://openjdk.org/jeps/491", "https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html", "https://docs.oracle.com/en/java/javase/25/core/virtual-threads.html", "https://openjdk.org/jeps/506", "https://openjdk.org/jeps/505", "https://docs.oracle.com/en/java/javase/21/docs/api/jdk.jfr/jdk/jfr/Recording.html", "https://docs.oracle.com/en/java/javase/21/docs/api/jdk.jfr/jdk/jfr/consumer/RecordingFile.html"]
---
가상 스레드는 **많은 작업이 I/O를 기다리는 동안 적은 수의 OS 스레드를 공유하도록 만드는 Java 스레드**입니다. [JEP 444](https://openjdk.org/jeps/444)로 JDK 21에서 정식화됐으며 JDK 25에서도 같은 기본 API를 사용합니다. 두 버전의 중요한 차이는 `synchronized` 안에서 대기할 때의 pinning입니다. [JEP 491](https://openjdk.org/jeps/491)이 JDK 24에서 이를 개선했고 JDK 25에도 반영됐습니다.

## 무엇을 가볍게 만드는 스레드인가요?

가상 스레드도 실행할 때는 OS 스레드가 필요합니다. JVM이 가상 스레드를 실행하는 플랫폼 스레드를 **캐리어(carrier)**라고 부릅니다. 지원되는 블로킹 동작에서 가상 스레드를 캐리어로부터 분리하면, 캐리어는 다른 가상 스레드를 실행할 수 있습니다.

이 구조는 동시 대기가 많은 요청 처리에 유용합니다. CPU 연산 자체를 빠르게 만들거나 단일 요청의 지연 시간을 자동으로 줄이지는 않습니다. [공식 도입 안내](https://docs.oracle.com/en/java/javase/25/core/virtual-threads.html)는 작업마다 가상 스레드를 만드는 방식을 권장하며 가상 스레드를 작은 풀에 재사용하는 방식을 피하도록 설명합니다. DB 연결 수·외부 API 허용량까지 늘어나는 것은 아니므로, 그런 자원은 세마포어나 연결 풀 등으로 별도 제한해야 합니다.

## JDK 21과 25의 차이

| 항목 | JDK 21 | JDK 25 |
| --- | --- | --- |
| 가상 스레드 API | 정식, 미리보기 옵션 불필요 | 정식, 기본 생성 API 유지 |
| `synchronized` 안의 블로킹 | 캐리어에 고정돼 확장성을 제한할 수 있음 | JDK 24의 JEP 491 개선 반영 |
| 모든 pinning 제거 여부 | 제거되지 않음 | 네이티브 코드에서 Java로 되돌아와 대기하는 경로 등은 남음 |
| 진단 | JFR·`jdk.tracePinnedThreads` 등 | JFR 유지·개선, `jdk.tracePinnedThreads`는 효과 없음 |
| `ScopedValue` | 미리보기 | JEP 506으로 정식 |
| 구조적 동시성 | 미리보기 | 여전히 별도 미리보기, 이전 API와 호환된다고 가정하면 안 됨 |

버전 차이는 [JDK 21 가이드](https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html), JEP 491과 [ScopedValue 글](/ko/posts/2026-10-31-jdk25-scopedvalue/)을 함께 보면 구분하기 쉽습니다. `ScopedValue`와 구조적 동시성의 상태 변화가 가상 스레드의 정식화 시점과 같은 것은 아닙니다.

pinning은 가상 스레드가 대기해도 캐리어를 놓지 못하는 상태입니다. JDK 25에서는 일반 `synchronized`만을 이유로 잠금을 전부 `ReentrantLock`으로 바꿀 필요는 없습니다. 다만 **캐리어를 놓는 것과 모니터 잠금을 놓는 것은 다릅니다.** `synchronized` 안의 느린 I/O는 다른 작업이 같은 잠금을 얻지 못하게 하므로, 임계 구역의 범위와 잠금 경쟁은 계속 점검해야 합니다.

## 같은 코드의 pinning을 JFR로 관측하기

![모드를 확인하고 JFR을 시작한 뒤 가상 스레드의 동일한 대기를 모니터 안팎에서 실행하고 작업 스레드의 pinning 이벤트만 집계](/assets/diagrams/2026-10-31-virtual-threads-jdk21-jdk25-ko.svg)

아래 코드는 한 가상 스레드의 `Thread.sleep(100)`을 `synchronized` 안에서 실행하는 `monitor` 모드와 블록 없이 실행하는 `plain` 모드를 비교합니다. 실제 네트워크·DB 요청은 하지 않습니다. [Recording](https://docs.oracle.com/en/java/javase/21/docs/api/jdk.jfr/jdk/jfr/Recording.html)으로 이벤트 임계값을 0으로 설정하고, [RecordingFile](https://docs.oracle.com/en/java/javase/21/docs/api/jdk.jfr/jdk/jfr/consumer/RecordingFile.html)에서 해당 작업 스레드의 이벤트만 셉니다.

각 JDK마다 새 디렉터리에 파일을 저장하고, 같은 설치의 `javac`·`java`로 실행합니다. JFR을 포함한 HotSpot JDK가 필요하며 미리보기 옵션은 쓰지 않습니다. `monitor.jfr`·`plain.jfr`를 만들고 기존 파일이 있으면 실행을 거부합니다.

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

macOS AArch64의 Eclipse Temurin `21.0.13+9`에서 확인한 출력입니다.

```text
virtual=true
monitor-pinned-events=1
virtual=true
plain-pinned-events=0
```

같은 플랫폼의 Eclipse Temurin `25.0.5+8`에서는 다음을 확인했습니다.

```text
virtual=true
monitor-pinned-events=0
virtual=true
plain-pinned-events=0
```

`Future.get()`은 작업 완료를 기다리고 실패를 호출자에게 전달합니다. 기록을 정지·저장한 뒤 읽으므로 집계가 실행 중인 녹화와 경합하지 않습니다. 캐리어 수를 제한하거나 전체 실행 시간을 비교하지 않았으며, 이벤트 수는 이 한 작업의 관측값입니다. 다른 JVM·패치·계측 조건에서 같은 숫자가 나오는지 확인 없이 일반화하지 않습니다.

## JDK를 올린 뒤에도 확인할 것

JDK 25에서 이벤트 0건이라는 결과는 **이 예제의 모니터 내부 대기 경로**에 한정됩니다. 네이티브·외부 함수 호출이나 클래스 초기화와 관련된 남은 경로까지 검증한 것은 아닙니다. JDK 21에서 유용했던 `-Djdk.tracePinnedThreads=full`을 JDK 25에서 지정해도 효과가 없으므로, 해당 버전의 JFR 이벤트와 스레드 덤프를 사용합니다.

실제 도입은 I/O 대기 비중이 높은 작업부터 시작하고, DB 연결 풀·외부 호출 동시성·타임아웃·취소 정책을 함께 확인합니다. CPU 중심 작업, 긴 임계 구역, 스레드별 대형 캐시는 별도 병목이 될 수 있습니다. 운영에서는 대표 부하로 처리량·꼬리 지연·메모리·잠금 경쟁을 측정해야 하며, 이 작은 관측 코드에서 성능 향상 비율을 계산하면 안 됩니다. 가상 스레드 작업에 요청 컨텍스트를 전달하려면 앞의 ScopedValue 글에서 비동기 경계와 바인딩 규칙을 이어 확인할 수 있습니다.
