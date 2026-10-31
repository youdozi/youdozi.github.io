---
kind: "post"
publishedAt: "2026-10-31T15:05:47.408853+00:00"
updatedAt: "2026-10-31T15:05:47.408853+00:00"
reviewedAt: "2026-10-31"
reviewStatus: "revised"
reviewScope: "Self-reviewed English translation of the Korean cache-aside article; offline Java 21 sequential TTL, key isolation, invalidation, LRU eviction and loader-failure scenarios. No concurrent load test, Redis integration or production performance claim."
reviewSources: ["https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside", "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/LinkedHashMap.html", "https://github.com/ben-manes/caffeine/wiki/Eviction", "https://github.com/ben-manes/caffeine/wiki/Population", "https://www.rfc-editor.org/rfc/rfc9111.html"]
language: "en"
translationKey: "2026-10-31-cache-aside"
routeSlug: "2026-10-31-cache-aside"
title: "API caching design: cache keys, TTL, invalidation, and protecting the origin during failures"
description: "Explain cache placement, keys, TTL, invalidation, and concurrent misses with Cache-Aside. Use Java to check expiry and capacity limits, and define how to protect the DB when the cache fails."
categories: ["architecture"]
tags: ["caching", "cache-aside", "ttl", "cache-invalidation", "java", "resilience"]
---

**Caching reuses previously obtained results to reduce origin reads and computation.** To apply it correctly, first define which requests can share a result, how long reuse is allowed, and how to refresh the result when the origin changes. A high hit rate does not make a cache correct if it returns another user's data or uses an old price to finalize a purchase.

This article is for developers considering a cache for a read API. It explains Cache-Aside using data that tolerates some delay, such as product descriptions, and runs TTL and capacity limits in Java. Operations that must use current state, such as finalizing payment or stock, are separate from this read cache. Policies for permitting stale data during failures connect to the [fallback design article](/ko/posts/2026-10-31-failure-fallback/).

## What should you cache, and where?

Start with paths that have repeated reads, expensive origin access, and room to tolerate stale responses for a limited time. Data used only once, or data that differs almost entirely by user, may cost more to store and invalidate than its cache hits save.

| Location | Costs it can reduce | Conditions to define alongside it |
| --- | --- | --- |
| HTTP cache in a browser or CDN | Network round trips and requests reaching the API | Whether sharing is allowed, URL and `Vary`, `Cache-Control` |
| Application-local cache | Remote-cache round trips, DB reads, repeated computation | Memory limit per process, differences between replicas' values |
| Shared cache such as Redis | Repeated origin reads across replicas | Network latency, failure behavior, serialization, storage capacity |

You do not need every layer at once. A local cache is fast, but each replica holds a different copy. A shared cache can reduce duplicate storage, but adds a network and operational dependency. With multiple layers, invalidation must reach every layer too.

## How does Cache-Aside work?

The application first checks the cache. If the entry is absent or expired, it reads from the origin and stores the result in the cache. This flow is called **Cache-Aside**. Writes typically commit the origin change before invalidating the corresponding cache entry. Origin data survives the loss of the cache; this differs from using the cache itself as the only record. [Microsoft's explanation of Cache-Aside](https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside)

A cache key must include inputs that change the result. For example, `Key(tenant, product, language)` represents different entries for different tenants, products, and languages. If currency, user permissions, or representation-format version also changes the response, separate the keys or cache scope accordingly. Concatenating strings without delimiters can cause collisions, so use structured keys or an unambiguous encoding.

Putting a tenant ID in the key does not complete authorization. Determine the tenant from trusted authentication context and verify access before querying the cache. Do not put access tokens or passwords directly into keys or logs.

**TTL is the period for which a value can be reused; a capacity limit is how much can be stored.** With TTL alone, entries may keep accumulating until they expire. With only a size limit, stale values may keep producing hits. Entry counts and actual byte sizes differ, so account for object and serialized sizes when storing large responses.

## Java example: key isolation, expiry, invalidation, and capacity limits

The code below is a small **demonstration of local-cache semantics** for product descriptions by tenant. Its 5-second TTL and maximum of 2 entries are values for observing behavior, not production recommendations. It uses `LinkedHashMap` access order to evict the least recently accessed entry first. [Java 21 documentation](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/LinkedHashMap.html)

![Return a keyed entry immediately if it is within TTL; on a miss or expiry, read the origin, store only a successful value, evict any entry beyond capacity, and return the value](/assets/img/architecture/cache-aside-en.svg)

The diagram shows `get()`. If the origin loader fails, the exception propagates and no new value is stored. `invalidate()` is a separate operation called after an origin change.

Save this as `CacheDemo.java` and run it on JDK 21 or later. No external server or library is required.

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

The following output was obtained with Zulu JDK `21.0.1+12-LTS`.

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

The first three reads of the same key read the origin only once. The same value is returned 1ns before expiry; at exactly 5 seconds it is loaded again. The following cases check explicit invalidation, key isolation by language and tenant, and eviction by access order. They also include a successful read after loader failure. Values such as `v1` indicate the test loader's call sequence, not actual DB versions.

Time is reproduced with a manually advanced monotonic timer instead of sleeping. In a real process, you can supply an elapsed-time timer with `new LocalCache(System::nanoTime)`. The example handles expired entries on access rather than immediately removing them in the background. It limits entry count, not bytes.

To keep the code small, the loader also runs inside the `synchronized` scope. Calls to the same instance are serialized even for different keys, and the number of requests waiting for a slow loader is not limited. This is therefore not a high-performance production cache implementation. It does not implement the per-key single-flight, origin-call limits, timeouts, or invalidation propagation across replicas discussed below. The execution checks are sequential scenarios; no concurrent load test was performed.

## Do TTL and invalidation guarantee current values?

They do not. This example measures TTL **from when the origin read finishes and the value is stored in the cache**. If the origin itself is a delayed read replica or an old snapshot, a 5-second TTL does not mean the latest value becomes visible within 5 seconds of an origin change. Read latency, replication delay, and invalidation propagation require separate consideration.

With multiple replicas using a shared cache, a race can occur even if you update the DB and then delete the cache entry. Read A starts fetching the old value; write B commits a new value and deletes the cache entry; then A finishes late and stores the old value again. TTL reduces how long that value remains but does not eliminate the race.

Paths that require current state must revalidate within the origin transaction, or prevent late results from overwriting newer ones using data versions and conditional writes, for example. If invalidation uses events, handle loss, duplicates, and delay between commit and event delivery. If one change affects multiple keys, such as lists, details, and aggregates, define the invalidation scope for those keys as well.

Distinguish `expire-after-write` from `expire-after-access`. Extending validity on every access can keep frequently read stale values around for a long time. To recheck a value after a fixed time from storage regardless of read count, assess whether write-based expiry meets your goal. [Caffeine's expiry and eviction policies](https://github.com/ben-manes/caffeine/wiki/Eviction)

## What happens when entries expire together or the cache fails?

If every request reads the origin the moment a popular key expires, a **cache stampede** can occur. Reduce duplicate reads with single-flight, which combines reads of the same key into one in-flight operation, and limit the concurrency and waiting time of origin calls too. Deduplication in one process does not mean deduplication across all replicas. In Java, you can consider features such as [Caffeine's atomic lookup and loading API](https://github.com/ben-manes/caffeine/wiki/Population), but that alone does not establish a service-wide limit on origin load.

Jitter can spread expiry times when many keys' TTLs would end together. If the freshness limit is 60 seconds, distribute expiry within a range that does not exceed 60 seconds. Jitter does not solve requests concentrated on a single popular key. Apply stale-while-revalidate, which returns an old value while refreshing it, only to paths that allow stale responses, and set a separate maximum age for continued refresh failures.

Sending every request to the DB during cache failure is also risky. For illustration, at 10,000 RPS of reads and a normal hit rate of 90%, origin traffic is about 1,000 RPS. Losing all hits raises that to 10,000 RPS even with the same request distribution. This is a calculation example, not a measurement, and excludes retries and refresh calls.

If the origin cannot handle that load, limit bypass requests, use approved local copies or reduced functionality, or reject excess requests. Observe cache failures separately from cache misses, and limit bulk reloading during recovery. Brief negative caching may help paths that repeatedly request nonexistent IDs, but do not cache an origin failure as “no data.” Define TTL and invalidation for that cache too so that newly created data can be read.

## Separate HTTP caches from application caches

Browser and CDN HTTP caches communicate reuse policies through response headers. They are a separate layer from the TTL of objects stored inside the JVM.

| Directive | Meaning |
| --- | --- |
| `max-age=60` | Specifies that the response is fresh while its age is less than 60 seconds |
| `s-maxage=60` | Specifies freshness lifetime for shared caches, overriding `max-age` and related settings there |
| `private` | Restricts storage by shared caches; private caches such as browsers may store it |
| `no-cache` | Allows storage but requires successful origin validation before reuse |
| `no-store` | Directs caches not to store this request or response; it is not a command to delete existing copies |

If language is selected with `Accept-Language`, `Vary` and the actual cache configuration must reflect that difference. If the URL itself separates languages, that URL is also part of the key. `ETag` and conditional requests can reduce transfer volume when content has not changed, but do not always eliminate origin validation cost. `private` and `no-store` do not replace authentication, authorization, or encryption. [RFC 9111: HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111.html)

Start adoption checks with one read path. Besides normal hits, check TTL boundaries, reads immediately after writes, the same ID across tenants and languages, maximum capacity, concurrent misses, cache failure, and recovery. In production, track origin-call count, latency, failure rate, in-flight loads, evictions, memory use, and invalidation delay alongside hit rate. You can judge the benefit only after checking **whether responses are correct and whether the origin survives without the cache**.
