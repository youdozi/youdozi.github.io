package example;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.ArrayList;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import static org.junit.jupiter.api.Assertions.*;
import static org.awaitility.Awaitility.await;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class RateLimitTest {
    @Autowired RedisRateLimiter limiter;
    @Autowired StringRedisTemplate redis;
    @LocalServerPort int port;
    static final Duration WINDOW = Duration.ofSeconds(10);

    @DynamicPropertySource
    static void redisProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.data.redis.port", () -> System.getProperty("demo.redis.port"));
    }
    String key() { return "rl:test:v1:" + UUID.randomUUID(); }

    @Test void fourthRequestIsRejectedWithoutChangingCountOrExtendingWindow() throws Exception {
        String key = key();
        for (int i = 0; i < 3; i++) assertTrue(limiter.check(key, 3, WINDOW).allowed());
        long before = redis.getExpire(key, TimeUnit.MILLISECONDS);
        Thread.sleep(30);
        var denied = limiter.check(key, 3, WINDOW);
        assertFalse(denied.allowed());
        assertEquals(0, denied.remaining());
        assertEquals("3", redis.opsForValue().get(key));
        assertTrue(denied.ttlMillis() < before);
        assertTrue(denied.retryAfterSeconds() >= 1);
    }

    @Test void concurrentCallersShareExactlyThreePermits() throws Exception {
        String key = key();
        var second = new RedisRateLimiter(redis);
        try (var pool = Executors.newFixedThreadPool(8)) {
            var calls = new ArrayList<Callable<Boolean>>();
            for (int i = 0; i < 40; i++) {
                var client = i % 2 == 0 ? limiter : second;
                calls.add(() -> client.check(key, 3, WINDOW).allowed());
            }
            int accepted = 0;
            for (var result : pool.invokeAll(calls)) if (result.get()) accepted++;
            assertEquals(3, accepted);
            assertEquals("3", redis.opsForValue().get(key));
        }
    }

    @Test void accountsHaveSeparateKeys() {
        String one = key(), two = key();
        assertTrue(limiter.check(one, 1, WINDOW).allowed());
        assertFalse(limiter.check(one, 1, WINDOW).allowed());
        assertTrue(limiter.check(two, 1, WINDOW).allowed());
    }

    @Test void expiredWindowCanStartAgain() {
        String key = key();
        assertTrue(limiter.check(key, 1, Duration.ofMillis(100)).allowed());
        await().atMost(Duration.ofSeconds(3)).until(() -> !Boolean.TRUE.equals(redis.hasKey(key)));
        assertTrue(limiter.check(key, 1, WINDOW).allowed());
    }

    @Test void malformedStateFailsWithoutWritingOrRepairingIt() {
        for (String value : new String[]{"bad", "-1", "1.5"}) {
            String key = key();
            redis.opsForValue().set(key, value, WINDOW);
            assertThrows(org.springframework.dao.DataAccessException.class, () -> limiter.check(key, 3, WINDOW));
            assertEquals(value, redis.opsForValue().get(key));
        }
    }

    @Test void missingTtlFailsInsteadOfSilentlyExtendingQuota() {
        String key = key();
        redis.opsForValue().set(key, "1");
        try {
            assertThrows(org.springframework.dao.DataAccessException.class, () -> limiter.check(key, 3, WINDOW));
            assertEquals("1", redis.opsForValue().get(key));
        } finally { redis.delete(key); }
    }

    @Test void invalidPolicyNeverCreatesAKey() {
        String key = key();
        assertThrows(IllegalArgumentException.class, () -> limiter.check(key, 0, WINDOW));
        assertFalse(Boolean.TRUE.equals(redis.hasKey(key)));
    }

    @Test void httpResponsesDistinguishAllowedRejectedAndBrokenLimiter() throws Exception {
        String key = "rl:demo:v1:demo-account";
        redis.delete(key);
        try (var client = HttpClient.newHttpClient()) {
            var request = HttpRequest.newBuilder(URI.create("http://127.0.0.1:" + port + "/demo")).build();
            try {
                for (int i = 0; i < 3; i++) assertEquals(200, client.send(request, HttpResponse.BodyHandlers.ofString()).statusCode());
                var denied = client.send(request, HttpResponse.BodyHandlers.ofString());
                assertEquals(429, denied.statusCode());
                assertTrue(Long.parseLong(denied.headers().firstValue("Retry-After").orElseThrow()) >= 1);
                redis.opsForValue().set(key, "broken", WINDOW);
                assertEquals(503, client.send(request, HttpResponse.BodyHandlers.ofString()).statusCode());
            } finally { redis.delete(key); }
        }
    }

    @Test void lostReplyCanConsumeQuotaEvenWhenCallerDoesNotUseTheDecision() {
        String key = key();
        limiter.check(key, 1, WINDOW);
        assertFalse(limiter.check(key, 1, WINDOW).allowed());
    }

    @Test void unresponsiveRedisEndpointReturns503() throws Exception {
        try (var stalled = new java.net.ServerSocket(0, 1, java.net.InetAddress.getByName("127.0.0.1"))) {
            var configuration = org.springframework.data.redis.connection.lettuce.LettuceClientConfiguration.builder()
                    .commandTimeout(Duration.ofMillis(200)).shutdownTimeout(Duration.ZERO).build();
            var factory = new org.springframework.data.redis.connection.lettuce.LettuceConnectionFactory(
                    new org.springframework.data.redis.connection.RedisStandaloneConfiguration("127.0.0.1", stalled.getLocalPort()),
                    configuration);
            factory.afterPropertiesSet();
            try {
                var unavailable = new RedisRateLimiter(new StringRedisTemplate(factory));
                assertEquals(503, new RateLimitApplication(unavailable).demo().getStatusCode().value());
            } finally { factory.destroy(); }
        }
    }

    @Test void scriptErrorsDoNotRollbackEarlierWrites() {
        String key = key();
        var script = new org.springframework.data.redis.core.script.DefaultRedisScript<Long>(
                "redis.call('SET', KEYS[1], 'written', 'PX', 1000); return redis.error_reply('deliberate error')", Long.class);
        try {
            assertThrows(org.springframework.dao.DataAccessException.class,
                    () -> redis.execute(script, java.util.List.of(key)));
            assertEquals("written", redis.opsForValue().get(key));
        } finally { redis.delete(key); }
    }
}
