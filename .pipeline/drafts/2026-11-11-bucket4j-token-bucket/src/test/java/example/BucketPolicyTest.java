package example;

import java.time.Duration;
import java.util.ArrayList;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicLong;
import io.github.bucket4j.Bucket;
import io.github.bucket4j.TimeMeter;
import org.junit.jupiter.api.Test;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

class BucketPolicyTest {
    static final class Clock implements TimeMeter {
        final AtomicLong now = new AtomicLong();
        public long currentTimeNanos() { return now.get(); }
        public boolean isWallClockBased() { return false; }
        void advance(Duration duration) { now.addAndGet(duration.toNanos()); }
    }

    @Test void initialBurstHasFiveTokensAndSixthNeedsTwoSeconds() {
        var bucket = BucketPolicy.local(new Clock());
        for (int i = 0; i < 5; i++) {
            var probe = bucket.tryConsumeAndReturnRemaining(1);
            assertTrue(probe.isConsumed());
            assertEquals(4 - i, probe.getRemainingTokens());
        }
        var denied = bucket.tryConsumeAndReturnRemaining(1);
        assertFalse(denied.isConsumed());
        assertEquals(2_000_000_000L, denied.getNanosToWaitForRefill());
    }

    @Test void greedyRefillsOneTokenAtTwoSeconds() {
        var clock = new Clock(); var bucket = BucketPolicy.local(clock);
        assertTrue(bucket.tryConsume(5));
        clock.advance(Duration.ofNanos(1_999_999_999L));
        assertFalse(bucket.tryConsume(1));
        clock.advance(Duration.ofNanos(1));
        assertTrue(bucket.tryConsume(1));
        assertFalse(bucket.tryConsume(1));
    }

    @Test void unusedRefillCannotExceedCapacity() {
        var clock = new Clock(); var bucket = BucketPolicy.local(clock);
        assertTrue(bucket.tryConsume(5));
        clock.advance(Duration.ofDays(1));
        assertEquals(5, bucket.getAvailableTokens());
        assertTrue(bucket.tryConsume(5));
        assertFalse(bucket.tryConsume(1));
    }

    @Test void sharedBucketAllowsExactlyFiveOfFortyConcurrentCallers() throws Exception {
        var bucket = BucketPolicy.local(new Clock());
        try (var pool = Executors.newFixedThreadPool(8)) {
            var calls = new ArrayList<Callable<Boolean>>();
            for (int i = 0; i < 40; i++) calls.add(() -> bucket.tryConsume(1));
            int accepted = 0;
            for (var result : pool.invokeAll(calls)) if (result.get()) accepted++;
            assertEquals(5, accepted);
            assertEquals(0, bucket.getAvailableTokens());
        }
    }

    @Test void independentBucketsDoNotShareQuota() {
        var clock = new Clock();
        var one = BucketPolicy.local(clock); var two = BucketPolicy.local(clock);
        assertTrue(one.tryConsume(5)); assertTrue(two.tryConsume(5));
        assertFalse(one.tryConsume(1)); assertFalse(two.tryConsume(1));
    }

    @Test void recreatingBucketOnEveryRequestRestoresTheBurst() {
        var clock = new Clock();
        for (int i = 0; i < 40; i++) assertTrue(BucketPolicy.local(clock).tryConsume(1));
    }

    @Test void greedyAndIntervallyRefillAtDifferentTimes() {
        var clock = new Clock();
        var greedy = BucketPolicy.local(clock);
        var intervally = Bucket.builder().withCustomTimePrecision(clock)
                .addLimit(limit -> limit.capacity(5).refillIntervally(5, Duration.ofSeconds(10))).build();
        assertTrue(greedy.tryConsume(5)); assertTrue(intervally.tryConsume(5));
        clock.advance(Duration.ofSeconds(2));
        assertEquals(1, greedy.getAvailableTokens());
        assertEquals(0, intervally.getAvailableTokens());
        clock.advance(Duration.ofSeconds(8));
        assertEquals(5, greedy.getAvailableTokens());
        assertEquals(5, intervally.getAvailableTokens());
    }

    @Test void rejectionDoesNotRestartRefillPeriod() {
        var clock = new Clock(); var bucket = BucketPolicy.local(clock);
        assertTrue(bucket.tryConsume(5));
        clock.advance(Duration.ofSeconds(1));
        assertFalse(bucket.tryConsume(1));
        clock.advance(Duration.ofSeconds(1));
        assertTrue(bucket.tryConsume(1));
    }

    @Test void everyBandwidthMustHaveEnoughTokens() {
        var bucket = Bucket.builder().withCustomTimePrecision(new Clock())
                .addLimit(limit -> limit.capacity(5).refillGreedy(5, Duration.ofSeconds(10)))
                .addLimit(limit -> limit.capacity(2).refillGreedy(2, Duration.ofMinutes(1))).build();
        assertTrue(bucket.tryConsume(2));
        var denied = bucket.tryConsumeAndReturnRemaining(1);
        assertFalse(denied.isConsumed());
        assertEquals(30_000_000_000L, denied.getNanosToWaitForRefill());
    }

    @Test void mvcMapsAdmissionAndRoundedRetryAfterWithoutSleeping() throws Exception {
        var clock = new Clock(); var bucket = BucketPolicy.local(clock);
        var mvc = MockMvcBuilders.standaloneSetup(new RateLimitApplication.DemoController(bucket)).build();
        for (int i = 0; i < 5; i++) mvc.perform(get("/demo")).andExpect(status().isOk());
        mvc.perform(get("/demo")).andExpect(status().isTooManyRequests()).andExpect(header().string("Retry-After", "2"));
        clock.advance(Duration.ofMillis(1500));
        mvc.perform(get("/demo")).andExpect(status().isTooManyRequests()).andExpect(header().string("Retry-After", "1"));
        clock.advance(Duration.ofMillis(500));
        mvc.perform(get("/demo")).andExpect(status().isOk());
    }
}
