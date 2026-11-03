import java.sql.SQLException;
import java.time.Duration;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.RejectedExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

public class DbBulkheadChecks {
    static int cases;
    static void check(boolean value) {
        if (!value) throw new AssertionError();
        cases++;
    }
    static void await(CountDownLatch latch) throws SQLException {
        try {
            if (!latch.await(10, TimeUnit.SECONDS)) throw new SQLException("test latch timeout");
        } catch (InterruptedException interrupted) {
            Thread.currentThread().interrupt();
            throw new SQLException(interrupted);
        }
    }
    static void free(DbBulkhead gate, int running, int slots) {
        check(gate.available() == running && gate.availableSlots() == slots);
    }
    public static void main(String[] args) throws Exception {
        try (var pool = Demo.pool(); var tasks = Executors.newVirtualThreadPerTaskExecutor()) {
            try (var c = pool.getConnection(); var s = c.createStatement()) {
                s.execute("CREATE TABLE IF NOT EXISTS bulkhead_example (id integer PRIMARY KEY)");
                s.execute("TRUNCATE bulkhead_example");
            }
            var gate = new DbBulkhead(pool, 1, 1);
            gate.transaction(Duration.ZERO, c -> {
                try (var s = c.createStatement()) { s.executeUpdate("INSERT INTO bulkhead_example VALUES (1)"); }
                return 1;
            });
            check(gate.transaction(Duration.ZERO, c -> {
                try (var s = c.createStatement(); var rows = s.executeQuery("SELECT count(*) FROM bulkhead_example")) {
                    rows.next(); return rows.getInt(1);
                }
            }) == 1);
            try {
                gate.transaction(Duration.ZERO, c -> {
                    try (var s = c.createStatement()) { s.executeUpdate("INSERT INTO bulkhead_example VALUES (2)"); }
                    throw new SQLException("rollback test");
                });
                throw new AssertionError();
            } catch (SQLException expected) { check(expected.getMessage().equals("rollback test")); }
            check(gate.transaction(Duration.ZERO, c -> {
                try (var s = c.createStatement(); var rows = s.executeQuery("SELECT count(*) FROM bulkhead_example")) {
                    rows.next(); return rows.getInt(1);
                }
            }) == 1);
            free(gate, 1, 2);

            var entered = new CountDownLatch(1);
            var release = new CountDownLatch(1);
            var held = tasks.submit(() -> gate.transaction(Duration.ZERO, c -> {
                entered.countDown(); await(release); return 1;
            }));
            try {
                check(entered.await(5, TimeUnit.SECONDS));
                try {
                    gate.transaction(Duration.ofMillis(30), c -> 0);
                    throw new AssertionError();
                } catch (RejectedExecutionException expected) { check(expected.getMessage().contains("timed out")); }
                check(gate.available() == 0 && gate.availableSlots() == 1);

                var interrupted = new AtomicInteger();
                Thread waiter = Thread.ofVirtual().start(() -> {
                    try { gate.transaction(Duration.ofSeconds(10), c -> 0); }
                    catch (InterruptedException expected) { interrupted.incrementAndGet(); }
                    catch (SQLException error) { throw new AssertionError(error); }
                });
                long deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(5);
                while (gate.availableSlots() != 0 && System.nanoTime() < deadline) Thread.sleep(1);
                check(gate.availableSlots() == 0);
                try {
                    gate.transaction(Duration.ZERO, c -> 0);
                    throw new AssertionError();
                } catch (RejectedExecutionException expected) { check(expected.getMessage().contains("full")); }
                waiter.interrupt(); waiter.join(5000);
                check(!waiter.isAlive() && interrupted.get() == 1);
                check(gate.available() == 0 && gate.availableSlots() == 1);
            } finally { release.countDown(); }
            check(held.get(5, TimeUnit.SECONDS) == 1);
            free(gate, 1, 2);
            var workStarted = new CountDownLatch(1);
            var finishWork = new CountDownLatch(1);
            var taskFinished = new CountDownLatch(1);
            var cancelled = tasks.submit(() -> {
                try {
                    return gate.transaction(Duration.ZERO, c -> {
                        workStarted.countDown();
                        boolean done = false;
                        while (!done) {
                            try { done = finishWork.await(10, TimeUnit.SECONDS); }
                            catch (InterruptedException ignored) { /* Model work that keeps running after cancellation. */ }
                        }
                        return 1;
                    });
                } finally { taskFinished.countDown(); }
            });
            try {
                check(workStarted.await(5, TimeUnit.SECONDS));
                check(cancelled.cancel(true));
                check(gate.available() == 0 && pool.getHikariPoolMXBean().getActiveConnections() == 1);
            } finally { finishWork.countDown(); }
            check(taskFinished.await(5, TimeUnit.SECONDS));
            free(gate, 1, 2);
            try {
                gate.transaction(Duration.ZERO, c -> {
                    try (var s = c.createStatement()) {
                        s.execute("SET LOCAL statement_timeout = '100ms'");
                        s.execute("SELECT pg_sleep(2)");
                    }
                    return 0;
                });
                throw new AssertionError();
            } catch (SQLException expected) { check("57014".equals(expected.getSQLState())); }
            free(gate, 1, 2);
            try {
                gate.transaction(Duration.ZERO, c -> { throw new IllegalStateException("runtime failure"); });
                throw new AssertionError();
            } catch (IllegalStateException expected) { check(expected.getMessage().equals("runtime failure")); }
            free(gate, 1, 2);
            // A separate caller occupies the shared pool; gate capacity does not reserve a connection.
            try (var c1 = pool.getConnection(); var c2 = pool.getConnection()) {
                try {
                    gate.transaction(Duration.ZERO, c -> 0);
                    throw new AssertionError();
                } catch (SQLException expected) { check(expected instanceof java.sql.SQLTransientConnectionException); }
            }
            free(gate, 1, 2);
            for (int i = 0; i < 20; i++) {
                try { gate.transaction(Duration.ZERO, c -> { throw new SQLException("repeat"); }); }
                catch (SQLException expected) { check("repeat".equals(expected.getMessage())); }
            }
            free(gate, 1, 2);
            System.out.println("checks=" + cases);
            System.out.println("connection-active=" + pool.getHikariPoolMXBean().getActiveConnections());
            System.out.println("available=" + gate.available() + ",slots=" + gate.availableSlots());
        }
    }
}
