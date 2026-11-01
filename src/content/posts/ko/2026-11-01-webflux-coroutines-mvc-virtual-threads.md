---
language: ko
translationKey: 2026-11-01-webflux-coroutines-mvc-virtual-threads
routeSlug: 2026-11-01-webflux-coroutines-mvc-virtual-threads
title: WebFlux·코루틴에서 MVC·가상 스레드로 전환하기
description: Kotlin 코루틴을 유지할 수 있는 Spring MVC의 범위와 WebFlux를 남길 조건, JDBC·JPA와 가상
  스레드로 옮기는 순서 및 검증 기준을 설명합니다.
categories:
  - springboot
tags:
  - spring
  - spring-webflux
  - spring-mvc
  - kotlin-coroutines
  - virtual-threads
  - migration
kind: post
publishedAt: 2026-11-01T05:15:00.000Z
updatedAt: 2026-11-01T05:15:00.000Z
reviewedAt: "2026-11-01"
reviewStatus: source-audited
reviewScope: 공식 Spring 문서 대조. 마이그레이션 코드 발췌와 운영 절차를 작성했으며 애플리케이션 통합 실행이나 성능 부하 시험은 수행하지 않음.
reviewSources:
  - https://docs.spring.io/spring-framework/reference/languages/kotlin/coroutines.html
  - https://docs.spring.io/spring-boot/reference/features/spring-application.html
  - https://docs.spring.io/spring-framework/reference/web/webflux/new-framework.html
---

WebFlux와 Kotlin 코루틴을 사용한다고 해서 반드시 코루틴을 걷어내야 하는 것은 아닙니다. **Spring MVC도 `suspend` 함수와 `Flow` 반환을 지원합니다.** 전환의 핵심은 코루틴 문법을 동기식으로 일괄 치환하는 것이 아니라, 리액티브 서버가 필요한 경로를 남기고 블로킹 JDBC/JPA 중심 경로를 MVC와 가상 스레드로 옮길지 검증하는 데 있습니다.

이 글은 Java 21 이상과 Spring Boot 3.2 이상을 대상으로 한 단계적 전환 가이드입니다. 처리량이나 지연이 개선된다는 보장은 다루지 않습니다. 실제 결과는 요청의 대기·CPU 비율, DB 연결 수, 하위 시스템 용량과 부하 시험으로 판단해야 합니다.

## 먼저 구분할 세 가지

**WebFlux와 MVC는 웹 런타임 선택**입니다. WebFlux는 Reactive Streams와 비동기 논블로킹 I/O를 중심으로 하고, MVC는 Servlet 요청 처리 모델을 사용합니다. **코루틴은 Kotlin의 비동기 프로그래밍 모델**이므로 MVC를 택해도 `suspend` 함수를 계속 사용할 수 있습니다. Spring은 MVC와 WebFlux 양쪽의 애노테이션 컨트롤러에서 Kotlin 코루틴을 지원합니다. 코루틴 지원에는 `kotlinx-coroutines-core`와 `kotlinx-coroutines-reactor`가 필요합니다. [Spring Framework의 코루틴 지원 문서](https://docs.spring.io/spring-framework/reference/languages/kotlin/coroutines.html)

가상 스레드는 Java의 경량 스레드입니다. 블로킹 호출을 사용하는 thread-per-request 코드가 대기 중 플랫폼 스레드를 오래 점유하는 부담을 줄이는 데 도움이 될 수 있습니다. 이를 켜도 JDBC가 논블로킹으로 바뀌거나 DB 커넥션 풀이 늘지는 않습니다. Spring Boot 3.2 이상은 JDK 21 이상에서 `spring.threads.virtual.enabled=true`로 가상 스레드 기반 실행을 활성화할 수 있습니다. Boot 문서는 더 나은 경험을 위해 Java 24 이상을 권장하고, pinning·기존 스레드 풀 설정·daemon thread 동작을 확인하도록 안내합니다. [Spring Boot 가상 스레드 설정과 주의점](https://docs.spring.io/spring-boot/reference/features/spring-application.html)

따라서 다음 세 가지 변경을 한 번에 묶지 마세요.

| 변경 | 바뀌는 것 | 별도 검증할 점 |
| --- | --- | --- |
| WebFlux → MVC | 서버 요청 처리 모델 | 필터, 보안, 예외 변환, SSE·WebSocket 등 |
| R2DBC → JDBC/JPA | DB 접근 모델 | 트랜잭션 경계, 쿼리, 커넥션 상한과 타임아웃 |
| 플랫폼 스레드 → 가상 스레드 | 작업 실행 스레드 | 라이브러리 호환성, ThreadLocal, pinning과 운영 지표 |

## 어느 경로를 옮길까?

일반적인 요청·응답에서 JPA 또는 JDBC를 사용하고, 처리 중 대부분을 DB나 외부 HTTP 응답 대기에 쓴다면 MVC와 가상 스레드는 검토할 만한 선택입니다. 반대로 높은 동시성 스트림, 서버 발행 이벤트(SSE), WebSocket, Reactive Streams의 수요 제어를 핵심 계약으로 쓰는 경로는 WebFlux를 유지하거나 전용 경로로 분리하는 편이 자연스러울 수 있습니다. `Flow`를 MVC 반환 타입으로 사용할 수 있다는 사실만으로 두 스택의 스트리밍·취소·압력 제어 동작이 모든 환경에서 같다고 가정하면 안 됩니다.

![리액티브 전용 기능을 먼저 분류하고 일반 요청 경로를 어댑터·동기 저장소로 옮긴 뒤 가상 스레드와 계약 테스트를 확인하고 점진 배포하는 흐름도](/assets/diagrams/2026-11-01-webflux-coroutines-mvc-virtual-threads-ko.svg)

흐름도는 일반 요청 경로의 전환 순서를 보여줍니다. 스트리밍 요구가 남은 경로는 전환을 보류하고 별도로 유지·분리합니다. 배포 확대는 테스트와 관측 결과를 확인한 뒤 진행하며, 기준선을 벗어나면 이전 경로로 되돌릴 수 있어야 합니다.

## 코루틴 컨트롤러는 유지할 수 있다

기존 WebFlux 코드가 다음과 같은 컨트롤러라고 가정해 봅시다. `Flow`는 여러 결과를 비동기 흐름으로 반환합니다.

```kotlin
@RestController
class OrderController(private val orders: OrderService) {
    @GetMapping("/orders/{id}")
    suspend fun get(@PathVariable id: Long): OrderDto = orders.get(id)

    @GetMapping("/orders")
    fun list(): Flow<OrderDto> = orders.list()
}
```

MVC 전환은 같은 컨트롤러 시그니처를 반드시 동기 함수로 바꾸는 작업이 아닙니다. Spring MVC에서도 `suspend`와 `Flow`를 사용할 수 있습니다. 먼저 런타임과 의존성을 바꾼 뒤, 각 반환 타입의 완료·취소·스트리밍 동작을 통합 테스트로 확인하세요.

```kotlin
@RestController
class OrderController(private val orders: OrderService) {
    @GetMapping("/orders/{id}")
    suspend fun get(@PathVariable id: Long): OrderDto = orders.get(id)

    @GetMapping("/orders")
    fun list(): Flow<OrderDto> = orders.list()
}
```

양쪽 코드가 같아 보이더라도 내부 저장소가 R2DBC인지 JDBC인지는 별개의 문제입니다. 동기 JDBC 호출을 코루틴 함수 안에서 실행한다고 논블로킹이 되는 것은 아닙니다. 반대로 suspend 함수가 있다는 이유만으로 MVC 요청이 자동으로 가상 스레드에 매핑된다고 생각해서도 안 됩니다. Boot의 가상 스레드 설정과 코루틴 디스패처는 각각 실제 실행 경로에서 확인해야 합니다.

## 저장소 전환은 별도 변경으로 검증한다

기존 `CoroutineCrudRepository`와 R2DBC를 Spring Data JPA로 바꾸는 예를 보겠습니다. 목록을 전부 메모리에 모으지 않도록 결과 크기를 제한하고, 기존 API 계약의 정렬·페이지 크기·권한 필터도 보존해야 합니다.

```kotlin
interface OrderRepository : CoroutineCrudRepository<Order, Long> {
    fun findByCustomerId(customerId: Long): Flow<Order>
}
```

동기식 JPA 저장소에서는 페이지 단위로 조회할 수 있습니다.

```kotlin
interface OrderRepository : JpaRepository<Order, Long> {
    fun findByCustomerId(customerId: Long, pageable: Pageable): Page<Order>
}
```

이 코드는 저장소 형태를 보여주는 발췌입니다. 실제 프로젝트에서는 엔티티 로딩 전략, 트랜잭션 범위, N+1 쿼리, 페이지 정렬 안정성과 기존 `Flow`의 취소·부분 소비 의미를 함께 점검해야 합니다. 한 번에 모두 바꾸기보다 한 유한 응답 API를 선택하고, 계약 테스트와 쿼리 관측을 먼저 붙이세요.

## 가상 스레드를 켜고 확인하기

Spring Boot 3.2 이상과 JDK 21 이상에서는 다음 설정을 적용할 수 있습니다.

```yaml
spring:
  threads:
    virtual:
      enabled: true
```

설정을 적용한 뒤 요청을 처리하는 스레드가 실제 가상 스레드인지 간단한 계측으로 확인할 수 있습니다. 예를 들어 임시 진단용 MVC 인터셉터나 컨트롤러에서 `Thread.currentThread().isVirtual()`을 기록합니다. 이 확인은 해당 요청 경로의 실행 스레드를 확인할 뿐, 전체 애플리케이션의 모든 작업·코루틴 dispatcher가 가상 스레드라는 뜻은 아닙니다.

Java 컨트롤러 경로를 임시 진단할 때는 다음 표현으로 현재 요청 스레드를 기록할 수 있습니다.

```java
public class RequestThreadProbe {
    public static boolean isVirtual() {
        return Thread.currentThread().isVirtual();
    }
}
```

Boot 문서는 가상 스레드 사용 시 스레드 풀 관련 설정이 기존과 다르게 작동할 수 있고, 일부 동기화·네이티브 호출 구간의 pinning이 처리량에 영향을 줄 수 있다고 안내합니다. 가상 스레드 개수를 늘리는 방식으로 DB 커넥션 풀이나 외부 API 동시 호출 한도를 풀지 마세요. DB 풀은 DB가 처리할 수 있는 연결 수에 맞게 제한하고, 연결 획득 대기·쿼리 timeout·외부 호출 timeout과 전체 요청 deadline을 함께 설정해야 합니다.

## 단계적 전환과 롤백 기준

1. **기준선을 기록합니다.** 대표 엔드포인트의 요청률, p50/p95/p99 지연, 오류율, CPU, 힙, DB 풀 대기와 외부 호출 지연을 같은 부하 조건에서 수집합니다.
2. **리액티브 전용 경로를 표시합니다.** SSE, WebSocket, 무제한 스트림, backpressure 또는 Reactive Streams 연산에 의존하는 경로를 목록화하고 전환 대상에서 분리합니다.
3. **한 개의 유한 API를 옮깁니다.** 서버 런타임과 해당 경로의 저장소 변경을 명시적으로 나누고, 요청·응답·오류·취소·인증 계약을 테스트합니다.
4. **가상 스레드 실행을 확인합니다.** 배포 설정뿐 아니라 런타임 스레드와 JDBC 호출 경로를 확인합니다. 실행되지 않는 백그라운드 작업은 별도 executor 설정을 점검합니다.
5. **같은 입력으로 비교합니다.** 동일한 데이터 크기와 부하에서 지연 분포, 오류, CPU, DB 대기, 연결 사용량을 비교합니다. 가상 스레드는 CPU 집약 작업의 CPU 용량을 늘려 주지 않으므로 CPU 포화도 함께 봅니다.
6. **작은 트래픽부터 확대합니다.** 업무 오류, 지연, DB 풀 대기 또는 자원 사용이 사전에 정한 기준을 넘으면 확대를 멈추고 원인을 확인하거나 기존 경로로 롤백합니다. 임계값은 서비스 SLO와 기준선에 맞춰 팀이 정해야 합니다.

실제 처리량·지연 개선 수치는 환경에서 측정하지 않았다면 글이나 설계 검토에 넣지 마세요. 먼저 바꾼 경로와 같은 입력으로 측정하고, 결과가 개선되지 않으면 MVC 전환 자체를 목표로 삼지 않는 것이 맞습니다.

## 결정 기준

JDBC/JPA 기반의 일반 요청·응답이 중심이고 동시 블로킹 대기가 병목 후보라면 MVC와 가상 스레드를 작은 경로에서 시험할 수 있습니다. 코루틴은 API 경계와 코드의 필요에 따라 유지해도 됩니다. 스트리밍·Reactive Streams 계약이 제품 요구사항이라면 WebFlux를 남기고, 스레드 모델만 바꾸려는 이유로 그 계약을 약화시키지 마세요. 어떤 선택이 유리한지는 동일 부하에서의 지연, 오류, DB 대기와 운영 복잡도를 비교해 결정합니다.
