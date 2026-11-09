package example;

import java.net.InetSocketAddress;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.Arrays;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;

import com.sun.net.httpserver.HttpServer;
import jakarta.servlet.DispatcherType;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.boot.web.servlet.context.ServletWebServerApplicationContext;
import org.springframework.context.ApplicationContext;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.servlet.AsyncHandlerInterceptor;
import org.springframework.web.servlet.DispatcherServlet;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;
import reactor.core.publisher.Mono;

import static org.junit.jupiter.api.Assertions.*;
import static org.awaitility.Awaitility.await;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
        properties = "spring.threads.virtual.enabled=${demo.virtual:false}")
@Import(ExecutionTest.ProbeConfiguration.class)
class ExecutionTest {
    static final AtomicInteger requests = new AtomicInteger();
    static volatile int upstreamStatus = 200;
    static volatile CountDownLatch arrived = new CountDownLatch(1);
    static volatile CountDownLatch release = new CountDownLatch(0);
    static volatile CountDownLatch finished = new CountDownLatch(0);
    static volatile CountDownLatch asyncStarted = new CountDownLatch(1);
    static final AtomicReference<Thread> requestThread = new AtomicReference<>();
    static final HttpServer upstream;
    static {
        try {
            upstream = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
            upstream.createContext("/value", exchange -> {
                CountDownLatch requestFinished = finished;
                requests.incrementAndGet();
                arrived.countDown();
                try {
                    if (!release.await(10, TimeUnit.SECONDS)) throw new IllegalStateException("gate timeout");
                    byte[] bytes = "hello".getBytes(java.nio.charset.StandardCharsets.UTF_8);
                    exchange.getResponseHeaders().set("Content-Type", "text/plain; charset=utf-8");
                    exchange.sendResponseHeaders(upstreamStatus, bytes.length);
                    exchange.getResponseBody().write(bytes);
                } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
                finally { exchange.close(); requestFinished.countDown(); }
            });
            upstream.start();
        } catch (Exception e) { throw new ExceptionInInitializerError(e); }
    }

    @DynamicPropertySource
    static void properties(DynamicPropertyRegistry registry) {
        registry.add("upstream.base-url", () -> "http://127.0.0.1:" + upstream.getAddress().getPort());
    }

    @TestConfiguration
    static class ProbeConfiguration implements WebMvcConfigurer {
        @Override public void addInterceptors(InterceptorRegistry registry) {
            registry.addInterceptor(new AsyncHandlerInterceptor() {
                @Override public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
                    if (request.getDispatcherType() == DispatcherType.REQUEST) requestThread.set(Thread.currentThread());
                    return true;
                }
                @Override public void afterConcurrentHandlingStarted(HttpServletRequest request, HttpServletResponse response, Object handler) {
                    assertTrue(request.isAsyncStarted());
                    asyncStarted.countDown();
                }
            });
        }
    }

    @LocalServerPort int port;
    @Autowired ApplicationContext context;
    @Autowired WebClient upstreamClient;
    final HttpClient caller = HttpClient.newHttpClient();

    HttpRequest request(String path) {
        return HttpRequest.newBuilder(URI.create("http://127.0.0.1:" + port + path))
                .timeout(Duration.ofSeconds(8)).build();
    }
    @BeforeEach void reset() {
        release.countDown();
        upstreamStatus = 200;
        release = new CountDownLatch(0);
        arrived = new CountDownLatch(1);
        asyncStarted = new CountDownLatch(1);
        requestThread.set(null);
        assertEquals("hello", upstreamClient.get().uri("/value").retrieve().bodyToMono(String.class).block(Duration.ofSeconds(5)));
        arrived = new CountDownLatch(1);
    }
    @AfterAll static void stop() { release.countDown(); upstream.stop(0); }

    @Test void bothStartersStillSelectServletTomcat() {
        assertInstanceOf(ServletWebServerApplicationContext.class, context);
        assertNotNull(context.getBean(DispatcherServlet.class));
        assertTrue(((ServletWebServerApplicationContext) context).getWebServer().getClass().getName().contains("Tomcat"));
    }
    @Test void assemblingMonoDoesNotSendRequest() {
        int before = requests.get();
        Mono<String> result = upstreamClient.get().uri("/value").retrieve().bodyToMono(String.class);
        assertEquals(before, requests.get());
        assertEquals("hello", result.block(Duration.ofSeconds(5)));
        assertEquals(before + 1, requests.get());
    }
    @Test void resubscribingFreshPipelineSendsAnotherRequest() {
        Mono<String> result = upstreamClient.get().uri("/value").retrieve().bodyToMono(String.class);
        int before = requests.get();
        result.block(Duration.ofSeconds(5)); result.block(Duration.ofSeconds(5));
        assertEquals(before + 2, requests.get());
    }
    @Test void blockWaitsOnRequestThread() throws Exception {
        release = new CountDownLatch(1);
        var response = caller.sendAsync(request("/block"), HttpResponse.BodyHandlers.ofString());
        try {
            assertTrue(arrived.await(2, TimeUnit.SECONDS));
            await().atMost(Duration.ofSeconds(2)).until(() -> requestThread.get() != null &&
                    Arrays.stream(requestThread.get().getStackTrace()).anyMatch(frame -> frame.getClassName().contains("BlockingSingleSubscriber")));
            assertEquals(1, asyncStarted.getCount());
            assertFalse(response.isDone());
        } finally { release.countDown(); }
        assertEquals(200, response.get(5, TimeUnit.SECONDS).statusCode());
    }
    @Test void monoReturnEntersServletAsyncWhileUpstreamIsPending() throws Exception {
        release = new CountDownLatch(1);
        var response = caller.sendAsync(request("/async"), HttpResponse.BodyHandlers.ofString());
        try {
            assertTrue(arrived.await(2, TimeUnit.SECONDS));
            assertTrue(asyncStarted.await(2, TimeUnit.SECONDS));
            assertFalse(response.isDone());
        } finally { release.countDown(); }
        assertEquals(200, response.get(5, TimeUnit.SECONDS).statusCode());
    }
    @Test void callbacksStayOnNonBlockingThreadsInBothControllerStyles() throws Exception {
        for (String path : new String[]{"/block", "/async"}) {
            var response = caller.send(request(path), HttpResponse.BodyHandlers.ofString());
            assertEquals(200, response.statusCode());
            var json = new com.fasterxml.jackson.databind.ObjectMapper().readTree(response.body());
            assertEquals("hello", json.path("value").asText());
            assertTrue(json.path("callbackNonBlocking").asBoolean());
            assertFalse(json.path("callbackVirtual").asBoolean());
            assertEquals(Boolean.getBoolean("demo.virtual"), json.path("requestVirtual").asBoolean());
            System.out.println("OBSERVATION " + response.body());
        }
    }
    @Test void upstreamStatusMapsTo502ForBothStyles() throws Exception {
        upstreamStatus = 503;
        for (String path : new String[]{"/block", "/async"})
            assertEquals(502, caller.send(request(path), HttpResponse.BodyHandlers.ofString()).statusCode());
    }
    @Test void deadlineMapsTo504ForBothStyles() throws Exception {
        for (String path : new String[]{"/block", "/async"}) {
            release = new CountDownLatch(1);
            finished = new CountDownLatch(1);
            try { assertEquals(504, caller.send(request(path), HttpResponse.BodyHandlers.ofString()).statusCode()); }
            finally { release.countDown(); }
            assertTrue(finished.await(2, TimeUnit.SECONDS));
        }
    }
}
