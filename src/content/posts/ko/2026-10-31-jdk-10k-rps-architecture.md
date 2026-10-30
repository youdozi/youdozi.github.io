---
language: "ko"
translationKey: "2026-10-31-jdk-10k-rps-architecture"
routeSlug: "2026-10-31-jdk-10k-rps-architecture"
kind: "post"
categories: ["jdk"]
tags: ["java", "jdk27", "architecture", "capacity-planning", "virtual-threads", "load-testing"]
publishedAt: "2026-10-30T23:21:33.758647+00:00"
updatedAt: "2026-10-30T23:21:33.758647+00:00"
title: "최신 JDK로 10k RPS API 설계하기: 용량 계산과 과부하 제어"
description: "JDK 27 환경의 10,000 RPS HTTP API를 위한 참조 아키텍처입니다. 평균 동시성·DB 예산·장애 여유를 계산하고 가상 스레드 입장 제어와 부하 검증 절차를 구분합니다."
reviewedAt: "2026-10-31"
reviewStatus: "revised"
reviewScope: "Primary JDK, SRE, PostgreSQL, retry, queueing and load-generator sources; offline JDK 27 admission semantics. Calculations illustrative. No 10k HTTP benchmark, infrastructure deployment, database/cache/queue integration or production capacity validation."
reviewSources: ["https://openjdk.org/projects/jdk/27/", "https://www.oracle.com/java/technologies/java-se-support-roadmap.html", "https://docs.oracle.com/en/java/javase/27/core/virtual-threads.html", "https://docs.oracle.com/en/java/javase/27/docs/api/java.base/java/util/concurrent/Semaphore.html", "https://web.mit.edu/2.810/www/files/lectures/lec1-intro-2019.pdf", "https://sre.google/sre-book/handling-overload/", "https://www.postgresql.org/docs/18/runtime-config-connection.html", "https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/", "https://grafana.com/docs/k6/latest/using-k6/scenarios/executors/constant-arrival-rate/", "https://grafana.com/docs/k6/latest/using-k6/scenarios/concepts/dropped-iterations/", "https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html"]
---
초당 **10,000요청(RPS)의 HTTP API는 최신 JDK를 설치하는 것보다 요청·의존성의 용량 예산과 과부하 동작을 먼저 설계해야 합니다.** 기본 출발점은 여러 가용 영역에 배치한 상태 없는 API 복제본, 요청 입장 제한, 의존성별 동시성 제한입니다. 캐시·큐·읽기 복제본은 병목과 일관성 요구에 따라 추가합니다. 이 글은 구성 방법과 계산 예시이며 **10k RPS를 달성한 부하 시험 보고서는 아닙니다.**

2026년 10월 31일 기준 최신 정식 버전은 [JDK 27](https://openjdk.org/projects/jdk/27/)입니다. 아래 코드는 Temurin `27.0.1.0.2+1`에서 확인했습니다. 운영에서는 최신 기능과 지원 기간을 구분합니다. [Oracle 지원 로드맵](https://www.oracle.com/java/technologies/java-se-support-roadmap.html)상 JDK 25는 LTS, 27은 비LTS이며, 다른 공급자의 지원 기간·프레임워크 호환성은 해당 공급자 문서에서 따로 확인해야 합니다.

## 10k의 경계와 성공 조건부터 정하기

여기서 10k는 정적 CDN 적중을 제외하고 **API 로드밸런서에 도달하는 초당 요청 수**입니다. 동시 접속 수나 가상 스레드 수가 아닙니다. 시험에서는 입력 RPS, 실제 사업 기능을 완료한 RPS, 거부·실패를 따로 기록합니다. 빠른 오류 응답만으로 처리량을 달성했다고 판단하지 않습니다.

다음은 계산을 설명하기 위한 가정입니다. 실제 서비스의 측정값이나 권장 설정값은 아닙니다.

| 항목 | 예시 가정 |
| --- | --- |
| 목표 입력 | 10,000 RPS |
| 읽기·쓰기 비율 | 90% / 10% |
| 읽기 캐시 적중률 | 80% |
| 정상 상태 평균 API 체류 시간 | 50ms |
| 응답 목표 | p99 200ms 미만·실패율 0.1% 미만 |
| DB 사용 | 읽기 미스·쓰기마다 1회, 연결 보유 평균 10ms |

안정 상태에서 같은 경계의 **평균** 값에 적용하는 [Little의 법칙](https://web.mit.edu/2.810/www/files/lectures/lec1-intro-2019.pdf#page=56)은 `L = λ × W`입니다. 정상 처리율을 10,000/s, 평균 체류 시간을 0.05초로 가정하면 전체 평균 진행 중 요청은 약 500개입니다. p99 200ms를 이 식에 넣어 평균 동시성을 계산하거나, 500을 그대로 하드 제한으로 정하면 안 됩니다. 폭주·지연 분포·장애 여유는 별도로 검증합니다.

DB 접근률은 `9,000 × (1 − 0.8) + 1,000 = 2,800/s`, 평균 점유 연결은 `2,800 × 0.01 = 28`입니다. **풀 크기 28을 추천하는 계산이 아닙니다.** 여러 SQL·잠금·트랜잭션·캐시 장애가 있으면 가정이 달라집니다. 응답 바이트 수와 TLS·복제·로그 트래픽도 대역폭 예산에 포함합니다.

## 참조 아키텍처: 작은 서비스를 수평으로 복제하기

![엣지와 로드밸런서 뒤의 다중 영역 JDK API 복제본, 선택적 읽기 캐시, DB 풀, 외부 API 제한, DB outbox 기반 비동기 워커](/assets/img/architecture/10k-rps-ko.svg)

그림은 제안 구성입니다. 아래 Java 예제가 이 전체 인프라를 구현하는 것은 아니며, 요청 입장 제한의 원리만 실행합니다. 10k RPS라는 숫자만으로 마이크로서비스·샤딩이 필요하다고 결론 내리지 않습니다. 상태 없는 모듈형 애플리케이션을 복제한 뒤 측정한 병목부터 분리할 수 있습니다.

- **엣지·로드밸런서:** 클라이언트별 요청률, 연결 수, 요청 본문 크기와 느린 연결을 제한합니다. CDN에는 캐시 가능한 공개 응답만 맡기고, 인증된 데이터의 캐시 키·범위는 별도로 설계합니다. 상태 확인과 드레이닝으로 준비되지 않은 복제본에 새 요청이 가지 않게 합니다.
- **API 복제본:** 요청 진입점에서 동시 처리량을 제한하고, 가상 스레드로 블로킹 I/O를 읽기 쉬운 코드로 처리합니다. 가상 스레드가 DB 용량을 늘리거나 CPU 연산을 가속하지는 않습니다. [JDK 27 안내](https://docs.oracle.com/en/java/javase/27/core/virtual-threads.html)처럼 제한 대상 자원은 세마포어 등으로 별도 제어합니다.
- **캐시·DB:** 읽기 캐시는 선택 사항입니다. TTL 분산·캐시 미스 합치기와 캐시 장애 시의 DB 유입을 시험합니다. 인덱스·쿼리 계획·트랜잭션 시간을 먼저 확인하고, 읽기 복제본은 복제 지연을 허용하는 경로에만 사용합니다.
- **외부 호출·비동기 작업:** 의존성마다 별도 동시성 예산을 둡니다. 응답 전에 완료할 필요 없는 작업만 큐로 옮깁니다. DB 쓰기와 메시지 발행을 함께 보장해야 한다면 같은 트랜잭션의 [outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)와 재시도 가능한 전달·멱등 소비를 설계합니다. 큐는 무한 버퍼가 아니며 적체량·가장 오래된 메시지 나이·처리 실패를 관측합니다.

[Google SRE의 과부하 처리 설명](https://sre.google/sre-book/handling-overload/)처럼 빠른 거부와 자원 보호는 정상적인 운영 동작으로 설계합니다. CPU만 보고 증설하면 I/O 정체를 놓칠 수 있으므로 진행 중 요청, 거부율, 연결 획득 대기와 의존성 포화를 함께 봅니다.

## 복제본 수와 DB 풀을 어떻게 정하나요?

하드웨어·힙·컨테이너 CPU 제한·요청 분포를 고정한 시험에서, **SLO와 합의한 운영 여유를 지키는 복제본당 처리량**을 `q_safe`로 구합니다. 이 글에서 그 값을 측정하지는 않았습니다.

가령 `q_safe = 2,500 RPS`가 실제로 검증됐다면 정상 부하만 놓고는 4개가 필요합니다. 한 복제본 손실에도 10k를 유지하려면 5개가 출발점입니다. 이것이 가용 영역 장애를 보장하지는 않습니다. 3개 영역에 2개씩 총 6개를 배치하면 한 영역 손실 후 남은 4개가 계산상 10k를 담당하지만, LB 재분배·영역별 편차·DB와 캐시의 장애 전환까지 시험해야 합니다. 자동 증설이 완료되기 전의 여유도 필요합니다.

DB 풀은 복제본별 값을 독립적으로 늘리지 않습니다. 각 DB 접속 대상에 대해 `동시에 존재할 수 있는 API 복제본 수 × 복제본당 풀 상한 + 워커 연결 + 운영 예약`을 가용 연결 예산 이내로 맞춥니다. 증설·롤링 배포·종료 유예로 겹치는 복제본도 셉니다. [PostgreSQL 문서](https://www.postgresql.org/docs/18/runtime-config-connection.html)는 `max_connections` 증가가 공유 메모리 등 자원 할당을 늘린다고 설명합니다. 연결 수 증가는 느린 쿼리의 해결책이 아닙니다.

## 가상 스레드에서 입장을 제한하는 최소 예제

![tryAcquire 실패 시 거부하고 성공 시 동기 작업 실행·finally 허가 반환·결과 또는 예외 전달을 수행하는 게이트 흐름](/assets/diagrams/2026-10-31-jdk-10k-rps-architecture-ko.svg)

그림은 `Gate.call()` 메서드의 흐름입니다. 아래 `main()`은 HTTP 서버 없이 두 작업과 거부 상황을 만드는 **입장 제어 의미 시연**입니다. 제한값 2는 테스트용이며 10k RPS 설정값이 아닙니다. 실제 서버에서는 값비싼 처리 전에 게이트를 적용하고, 게이트에 도달하기 전의 연결·서버 큐·가상 스레드 생성 폭주도 엣지와 서버 설정에서 제한해야 합니다.

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

JDK 27의 `javac`·`java`를 같은 설치에서 선택해 실행한 출력입니다. 미리보기 옵션은 필요하지 않습니다.

```text
admitted=2
overload=rejected
completed=ok,ok
failure=propagated
available=2
```

[`tryAcquire()`](https://docs.oracle.com/en/java/javase/27/docs/api/java.base/java/util/concurrent/Semaphore.html#tryAcquire()) 실패는 대기열에 넣지 않고 거부합니다. `finally`는 실제 작업이 끝날 때 허가를 반환하며 예외는 호출자에게 전달합니다. 이것은 **동시 실행 수 제한이지 초당 요청률 제한이 아닙니다.** HTTP 어댑터에서는 서비스 용량 거부를 503 같은 응답으로 매핑하고 클라이언트별 할당량 제한과 구분할 수 있습니다. 이 코드는 HTTP 상태 매핑·인증·기한·DB 풀을 구현하지 않습니다.

## 기한·재시도가 과부하를 키우지 않도록 하기

종단 요청 기한을 정하고 DB 연결 획득·쿼리·HTTP 연결·응답 읽기에 남은 예산을 나눕니다. 단계별 p99를 더해서 종단 p99라고 부르지 않습니다. 호출자가 시간 초과했다고 실제 DB·HTTP 작업이 즉시 중단되는 것도 아니므로, 드라이버·클라이언트의 취소와 자원 반환을 확인합니다. 실제 작업이 계속 실행 중인데 동시성 허가만 먼저 돌려주면 상한이 깨집니다.

재시도는 한 계층에서 제한된 횟수·전체 기한·지수 백오프와 jitter를 적용하고, 재시도 가능한 오류와 멱등성이 확보된 작업으로 좁힙니다. [Amazon의 타임아웃·재시도 설명](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)처럼 재시도는 부하를 늘릴 수 있습니다. 결제·주문 등은 중복 실행 방지와 결과 조회 규칙을 먼저 설계합니다.

## 무엇을 통과해야 10k 처리라고 말할 수 있나요?

실제 HTTP 서버·운영과 동등한 데이터·TLS·인증·응답 크기를 준비하고 다음 순서로 시험합니다.

1. 단일 복제본에서 부하를 단계적으로 올려 `q_safe`를 구합니다. CPU·GC·할당률·소켓·잠금·DB 대기·성공 RPS와 종단 p99를 함께 기록합니다.
2. 전체 구성에서 준비·워밍업 후 1k→3k→5k→10k로 입력률을 올리고, 목표 부하를 합의한 시간 동안 유지합니다. 이 단계의 시간과 데이터 분포도 결과에 남깁니다.
3. [k6의 constant-arrival-rate](https://grafana.com/docs/k6/latest/using-k6/scenarios/executors/constant-arrival-rate/) 같은 열린 부하 모델을 사용한다면, **반복당 HTTP 요청 1회·자동 리다이렉트와 재시도 없음**을 확인해야 10,000 iterations/s를 10k HTTP RPS와 연결할 수 있습니다. 부하 발생기의 CPU·네트워크·VU 여유와 [dropped_iterations](https://grafana.com/docs/k6/latest/using-k6/scenarios/concepts/dropped-iterations/)를 확인합니다. 목표 입력을 못 만든 시험은 서버의 10k 통과로 해석하지 않습니다.
4. 복제본·영역 손실, 캐시 냉각·중단, 느린 DB·외부 API, 롤링 배포와 순간 폭주를 시험합니다. 거부 응답을 성공에서 제외하고, 포화 후 회복·큐 배출·연결 누수가 없는지도 봅니다.

이 글에서 실행한 것은 게이트의 용량 초과 거부와 정상·실패 후 반환뿐입니다. 전체 구성의 부하 시험은 아직 수행하지 않았습니다. [가상 스레드의 JDK 21·25 차이](/ko/posts/2026-10-31-virtual-threads-jdk21-jdk25/)와 [ScopedValue의 요청 컨텍스트 범위](/ko/posts/2026-10-31-jdk25-scopedvalue/)도 운영 구성과 별개로 확인할 수 있습니다.
