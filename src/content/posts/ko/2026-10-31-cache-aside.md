---
kind: "post"
publishedAt: "2026-10-31T09:18:57.897116+00:00"
updatedAt: "2026-10-31T09:18:57.897116+00:00"
reviewedAt: "2026-10-31"
reviewStatus: "revised"
reviewScope: "Self-reviewed Korean cache-aside article; offline Java 21 sequential TTL, key isolation, invalidation, LRU eviction and loader-failure scenarios. No concurrent load test, Redis integration or production performance claim."
reviewSources: ["https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside", "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/LinkedHashMap.html", "https://github.com/ben-manes/caffeine/wiki/Eviction", "https://github.com/ben-manes/caffeine/wiki/Population", "https://www.rfc-editor.org/rfc/rfc9111.html"]
language: "ko"
translationKey: "2026-10-31-cache-aside"
routeSlug: "2026-10-31-cache-aside"
title: "API 캐싱 설계: 캐시 키, TTL, 무효화와 장애 시 원본 보호"
description: "Cache-Aside를 기준으로 캐시 위치·키·TTL·무효화·동시 미스 처리를 설명합니다. Java 예제로 만료와 용량 제한을 확인하고 캐시 장애 시 DB를 보호하는 기준을 정합니다."
categories: ["architecture"]
tags: ["caching", "cache-aside", "ttl", "cache-invalidation", "java", "resilience"]
---

**캐싱은 이전에 얻은 결과를 재사용해 원본 조회와 계산을 줄이는 방법입니다.** 제대로 적용하려면 같은 결과로 취급할 요청의 범위, 재사용을 허용할 시간, 원본 변경 시 갱신 방법을 먼저 정해야 합니다. 적중률이 높아도 다른 사용자의 데이터를 반환하거나 변경 전 가격을 확정에 사용한다면 올바른 캐시가 아닙니다.

이 글은 조회 API의 캐시 도입을 검토하는 개발자를 대상으로 합니다. 상품 설명처럼 일부 지연을 허용하는 데이터를 예로 들어 Cache-Aside를 설명하고, Java로 TTL과 용량 제한을 실행합니다. 결제·재고 확정처럼 최신 상태로 판단해야 하는 작업은 이 조회 캐시와 분리합니다. 장애 때 오래된 데이터를 허용하는 정책은 [fallback 설계 글](/ko/posts/2026-10-31-failure-fallback/)과 연결됩니다.

## 무엇을 어디에 캐시해야 하나요?

반복 조회가 많고 원본 접근 비용이 크며, 일정 시간의 오래된 응답을 허용할 수 있는 경로가 출발점입니다. 한 번만 쓰는 데이터나 사용자별로 거의 모두 다른 데이터는 적중 효과에 비해 저장·무효화 비용이 클 수 있습니다.

| 위치 | 줄일 수 있는 비용 | 함께 정할 조건 |
| --- | --- | --- |
| 브라우저·CDN의 HTTP 캐시 | 네트워크 왕복, API 도달 요청 | 공유 가능 여부, URL·`Vary`, `Cache-Control` |
| 애플리케이션 로컬 캐시 | 원격 캐시 왕복, DB 조회, 반복 계산 | 프로세스별 메모리 상한, 복제본 간 값 차이 |
| Redis 같은 공유 캐시 | 여러 복제본의 반복 원본 조회 | 네트워크 지연, 장애 동작, 직렬화, 저장 용량 |

모든 계층을 한 번에 넣을 필요는 없습니다. 로컬 캐시는 빠르지만 복제본마다 서로 다른 사본을 가집니다. 공유 캐시는 중복 저장을 줄일 수 있지만 네트워크와 운영할 의존성이 추가됩니다. 여러 계층을 겹치면 무효화도 각 계층에 도달해야 합니다.

## Cache-Aside는 어떻게 동작하나요?

애플리케이션이 먼저 캐시를 조회하고, 없거나 만료됐으면 원본에서 읽은 뒤 캐시에 저장합니다. 이 흐름을 **Cache-Aside**라고 합니다. 쓰기는 보통 원본 변경을 확정한 다음 해당 캐시를 무효화합니다. 캐시가 사라져도 원본 데이터가 보존되는 구성이며, 캐시 자체를 유일한 기록으로 사용하는 방식과 구분합니다. [Microsoft의 Cache-Aside 설명](https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside)

캐시 키는 결과를 바꾸는 입력을 포함해야 합니다. 예를 들어 `Key(tenant, product, language)`는 테넌트·상품·언어가 다르면 다른 항목입니다. 통화·사용자 권한·표현 형식 버전도 응답을 바꾼다면 키나 캐시 범위를 분리해야 합니다. 문자열을 구분자 없이 붙이면 충돌할 수 있으므로 구조화된 키나 모호하지 않은 인코딩을 사용합니다.

테넌트 ID를 키에 넣었다고 권한 검사가 완료되는 것은 아닙니다. 신뢰할 수 있는 인증 맥락에서 테넌트를 결정하고 접근을 확인한 뒤 캐시를 조회해야 합니다. 접근 토큰·비밀번호를 키나 로그에 그대로 넣지 않습니다.

**TTL은 값을 재사용할 수 있는 기간이고, 용량 제한은 보관할 수 있는 양입니다.** TTL만 두면 만료 전까지 항목이 계속 쌓일 수 있습니다. 반대로 크기 제한만 두면 오래된 값이 계속 적중할 수 있습니다. 항목 개수와 실제 바이트 수는 다르므로 큰 응답을 저장한다면 객체 크기·직렬화 크기까지 고려합니다.

## Java 예제: 키 분리, 만료, 무효화, 용량 제한

아래 코드는 테넌트별 상품 설명을 위한 작은 **로컬 캐시의 의미 시연**입니다. TTL 5초와 최대 2개 항목은 동작을 확인하기 위한 값이며 운영 권장값이 아닙니다. `LinkedHashMap`의 접근 순서를 이용해 가장 오래 접근하지 않은 항목을 먼저 제거합니다. [Java 21 문서](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/LinkedHashMap.html)

![키로 조회한 항목이 TTL 안이면 즉시 반환하고, 미스나 만료이면 원본을 읽어 성공한 값만 저장한 뒤 용량 초과 항목을 제거하고 반환하는 흐름](/assets/img/architecture/cache-aside-ko.svg)

그림은 `get()`의 흐름입니다. 원본 로더가 실패하면 예외를 전달하고 새 값을 저장하지 않습니다. `invalidate()`는 원본 변경 후 별도로 호출하는 동작입니다.

`CacheDemo.java`로 저장하고 JDK 21 이상에서 실행합니다. 외부 서버나 라이브러리는 필요하지 않습니다.

```java
import java.time.Duration;
import java.util.LinkedHashMap;
import java.util.Objects;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Function;
import java.util.function.LongSupplier;

public class CacheDemo {
    record Key(String tenant, String product, String language) {}
    record Entry(String value, long loadedAt) {}

    static final class LocalCache {
        private final LinkedHashMap<Key, Entry> entries =
                new LinkedHashMap<>(16, 0.75f, true);
        private final LongSupplier ticker;
        private final long ttl = Duration.ofSeconds(5).toNanos();
        private final int maximumSize = 2;

        LocalCache(LongSupplier ticker) { this.ticker = ticker; }

        synchronized String get(Key key, Function<Key, String> loader) {
            Entry entry = entries.get(key);
            long now = ticker.getAsLong();
            if (entry != null && now - entry.loadedAt() < ttl) {
                return entry.value();
            }
            entries.remove(key);
            String value = Objects.requireNonNull(loader.apply(key));
            entries.put(key, new Entry(value, ticker.getAsLong()));
            if (entries.size() > maximumSize) {
                entries.remove(entries.keySet().iterator().next());
            }
            return value;
        }

        synchronized void invalidate(Key key) { entries.remove(key); }
    }

    static void expect(String actual, String expected) {
        if (!actual.equals(expected)) throw new AssertionError(actual);
        System.out.println(actual);
    }

    public static void main(String[] args) {
        AtomicLong clock = new AtomicLong();
        AtomicInteger loads = new AtomicInteger();
        LocalCache cache = new LocalCache(clock::get);
        Function<Key, String> loader = key ->
                key.tenant() + "/" + key.language() + "/v" + loads.incrementAndGet();
        Key ko = new Key("shop-a", "p1", "ko");
        Key en = new Key("shop-a", "p1", "en");
        Key other = new Key("shop-b", "p1", "ko");

        expect(cache.get(ko, loader), "shop-a/ko/v1");
        expect(cache.get(ko, loader), "shop-a/ko/v1");
        clock.set(Duration.ofSeconds(5).toNanos() - 1);
        expect(cache.get(ko, loader), "shop-a/ko/v1");
        clock.incrementAndGet();
        expect(cache.get(ko, loader), "shop-a/ko/v2");
        cache.invalidate(ko);
        expect(cache.get(ko, loader), "shop-a/ko/v3");
        expect(cache.get(en, loader), "shop-a/en/v4");
        expect(cache.get(ko, loader), "shop-a/ko/v3");
        expect(cache.get(other, loader), "shop-b/ko/v5");
        expect(cache.get(en, loader), "shop-a/en/v6");

        Key failing = new Key("shop-c", "p1", "ko");
        try {
            cache.get(failing, key -> { throw new IllegalStateException("origin"); });
            throw new AssertionError("Failure was swallowed");
        } catch (IllegalStateException expected) {
            expect(expected.getMessage(), "origin");
        }
        expect(cache.get(failing, loader), "shop-c/ko/v7");
    }
}
```

```sh
javac --release 21 CacheDemo.java
java CacheDemo
```

Zulu JDK `21.0.1+12-LTS`에서 실행한 결과입니다.

```text
shop-a/ko/v1
shop-a/ko/v1
shop-a/ko/v1
shop-a/ko/v2
shop-a/ko/v3
shop-a/en/v4
shop-a/ko/v3
shop-b/ko/v5
shop-a/en/v6
origin
shop-c/ko/v7
```

처음 세 번의 같은 키 조회는 원본을 한 번만 읽습니다. 만료 1ns 전에는 같은 값이 나오고, 정확히 5초가 되면 다시 읽습니다. 이어서 명시적 무효화, 언어·테넌트별 키 분리, 접근 순서에 따른 축출을 확인합니다. 로더 실패 후 다음 조회가 성공하는 경우도 포함합니다. `v1` 등의 값은 테스트 로더의 호출 순서이며 실제 DB 버전이 아닙니다.

시간은 잠들며 기다리는 대신 직접 증가시키는 단조 증가 타이머로 재현했습니다. 실제 프로세스에서는 `new LocalCache(System::nanoTime)`처럼 경과 시간용 타이머를 연결할 수 있습니다. 예제는 만료 항목을 접근 시 처리하며 백그라운드에서 즉시 삭제하지 않습니다. 항목 수 상한은 있지만 바이트 상한은 아닙니다.

코드를 작게 유지하기 위해 `synchronized` 범위 안에서 로더까지 실행합니다. 같은 인스턴스의 호출은 키가 달라도 직렬화되고, 느린 로더를 기다리는 요청 수도 제한하지 않습니다. 따라서 이 코드는 운영용 고성능 캐시 구현이 아닙니다. 아래에서 설명하는 키별 single-flight, 원본 호출 상한, 시간 제한, 여러 복제본의 무효화 전파는 구현하지 않았습니다. 실행 검사는 순차 시나리오이며 동시 부하 시험은 하지 않았습니다.

## TTL과 무효화만으로 최신 값을 보장할 수 있나요?

보장할 수 없습니다. 예제의 TTL은 **원본 조회가 끝나 캐시에 저장된 시점부터** 셉니다. 원본 자체가 지연된 읽기 복제본이거나 오래된 스냅샷이라면 TTL 5초라고 해서 원본 변경 후 5초 안에 최신 값이 보인다는 뜻은 아닙니다. 조회 지연·복제 지연·무효화 전파까지 따로 고려해야 합니다.

여러 복제본이 공유 캐시를 사용하는 구성에서는 DB를 갱신한 다음 캐시를 지우더라도 경합이 생길 수 있습니다. 읽기 A가 이전 값을 읽기 시작하고, 쓰기 B가 새 값을 커밋한 뒤 캐시를 지웠는데, 늦게 끝난 A가 이전 값을 다시 저장하는 순서입니다. TTL은 그 값이 남는 시간을 줄이지만 경합 자체를 없애지 않습니다.

최신 상태가 필요한 경로는 원본 트랜잭션에서 다시 검증하거나, 데이터 버전과 조건부 저장 등으로 늦은 결과의 덮어쓰기를 막아야 합니다. 이벤트로 무효화한다면 커밋과 이벤트 전달 사이의 유실·중복·지연도 다룹니다. 목록·상세·집계처럼 한 번의 변경이 여러 키에 영향을 주는 경우에는 해당 키들의 무효화 범위도 정해야 합니다.

`expire-after-write`와 `expire-after-access`도 구분합니다. 접근할 때마다 유효 기간을 연장하면 자주 읽는 오래된 값은 오랫동안 남을 수 있습니다. 조회 횟수와 무관하게 저장 후 일정 시간에 다시 확인하려면 쓰기 기준 만료가 목적에 맞는지 검토합니다. [Caffeine의 만료·축출 정책](https://github.com/ben-manes/caffeine/wiki/Eviction)

## 동시에 만료되거나 캐시가 고장 나면 어떻게 하나요?

인기 키가 만료되는 순간 모든 요청이 원본을 읽으면 **cache stampede**가 발생할 수 있습니다. 같은 키의 조회를 하나의 진행 중 작업으로 합치는 single-flight로 중복 조회를 줄이고, 원본 호출의 동시성·대기 시간도 제한합니다. 한 프로세스의 중복 제거가 여러 복제본 전체의 중복 제거를 뜻하지는 않습니다. Java에서는 [Caffeine의 원자적 조회·적재 API](https://github.com/ben-manes/caffeine/wiki/Population) 같은 기능을 검토할 수 있지만, 그것만으로 서비스 전체의 원본 부하 상한이 생기지는 않습니다.

여러 키의 TTL이 같은 시점에 끝나는 문제에는 만료 시간을 분산하는 지터를 사용할 수 있습니다. 신선도 상한이 60초라면 60초를 넘기지 않는 범위에서 분산해야 합니다. 지터가 하나의 인기 키에 몰리는 요청까지 해결하는 것은 아닙니다. 오래된 값을 먼저 반환하며 갱신하는 stale-while-revalidate 방식은 오래된 응답을 허용한 경로에만 적용하고, 갱신 실패가 계속될 때의 최대 허용 나이를 따로 둡니다.

캐시 장애 때 모든 요청을 DB로 우회시키는 것도 위험합니다. 설명용으로 조회 요청이 10,000 RPS이고 정상 적중률이 90%라면 원본 유입은 약 1,000 RPS입니다. 적중이 모두 사라지면 같은 요청 분포에서도 10,000 RPS로 늘어납니다. 실제 측정값이 아닌 계산 예시이며 재시도·갱신 호출은 포함하지 않았습니다.

원본이 이 부하를 감당하지 못한다면 우회 요청을 제한하고, 허용된 로컬 사본이나 기능 축소를 사용하거나 초과 요청을 거절해야 합니다. 캐시 장애와 캐시 미스는 구분해 관측하고, 복구 때의 대량 재적재도 제한합니다. 존재하지 않는 ID를 반복 조회하는 경로는 짧은 negative caching을 고려할 수 있으나, 원본 장애를 ‘데이터 없음’으로 저장하지 않습니다. 새 데이터 생성 후 조회가 막히지 않도록 이 캐시의 TTL과 무효화도 정해야 합니다.

## HTTP 캐시와 애플리케이션 캐시는 구분하기

브라우저·CDN의 HTTP 캐시는 응답 헤더로 재사용 정책을 전달합니다. JVM 안에 저장한 객체의 TTL과는 별도 계층입니다.

| 지시어 | 의미 |
| --- | --- |
| `max-age=60` | 응답 나이가 60초 미만인 동안 신선한 것으로 취급하도록 지정 |
| `s-maxage=60` | 공유 캐시의 신선도 기간 지정. 공유 캐시에서 `max-age` 등을 대체 |
| `private` | 공유 캐시 저장 제한. 브라우저 같은 전용 캐시는 저장 가능 |
| `no-cache` | 저장은 가능하지만 재사용 전에 원본의 성공적인 검증 필요 |
| `no-store` | 해당 요청·응답을 저장하지 않도록 지시. 이미 저장된 사본의 삭제 명령은 아님 |

언어를 `Accept-Language`로 선택한다면 `Vary`와 실제 캐시 설정이 그 차이를 반영해야 합니다. URL 자체로 언어가 나뉜다면 그 URL도 키의 일부입니다. `ETag`와 조건부 요청은 내용이 바뀌지 않았을 때 전송량을 줄일 수 있지만 원본 검증 비용이 항상 사라지는 것은 아닙니다. `private`나 `no-store`는 인증·인가와 암호화를 대신하지 않습니다. [RFC 9111: HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111.html)

도입 검증은 조회 경로 하나에서 시작합니다. 정상 적중 외에도 TTL 경계, 쓰기 직후 읽기, 다른 테넌트·언어의 같은 ID, 최대 용량 도달, 동시 미스, 캐시 장애와 복구를 확인합니다. 운영에서는 적중률과 함께 원본 호출 수·지연·실패율, 적재 중 요청 수, 축출량, 메모리 사용량, 무효화 지연을 봅니다. **응답이 정확한지와 캐시가 없을 때 원본이 버티는지**까지 확인해야 도입 효과를 판단할 수 있습니다.
