---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2026-10-30-webclient-timeout-retry",
  "routeSlug": "2026-10-30-webclient-timeout-retry",
  "kind": "post",
  "title": "Probar los tiempos de espera y reintentos limitados de WebClient con Reactor",
  "description": "Separa los tiempos de conexión, respuesta, intento y operación completa. Prueba una política GET que reintenta solo HTTP 503 dos veces mediante HTTP local y tiempo virtual de Reactor.",
  "categories": [
    "springboot"
  ],
  "tags": [
    "springboot",
    "webclient",
    "test",
    "reactor"
  ],
  "sourcePath": "src/content/posts/en/2026-10-30-webclient-timeout-retry.md",
  "sourceSha256": "757c2335d2f6b40391fa299791d6c6e6bade0e499c599b451be06be4eee77e3b",
  "draftSha256": "7f7c27be38a4f974b2e39f4cf9b98191ff7c27dd80536d72cc6e23d88f74af50",
  "manifestPath": ".pipeline/technical-translations/batch-078/manifest.json",
  "manifestSha256": "e685b2de5dafd8cfff8e8e996fa2b09613becb072bdd575b58b9eca9651474a3",
  "publishedAt": "2026-10-31T02:49:44.828Z",
  "updatedAt": "2026-10-31T02:49:44.828Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 118,
    "approvedAt": "2026-10-31T02:49:44.828Z",
    "basis": "2026-10-31 user instruction “진행해줘” immediately following delivery of the reviewed 72 complete translations in PR #118; interpreted as authorization to publish exactly batch-078 in all six languages. Separate AI language review is recorded in the manifest; this does not claim a human line-by-line review. Excludes the older 120 technical drafts and 318 pending news translations."
  }
}
---
Coloca un `timeout` por intento antes de `retryWhen` y un `timeout` total después para incluir las demoras de reintento en el presupuesto global. Reintenta solo los fallos permitidos por el contrato de la API: este ejemplo GET reintenta HTTP 503 como máximo dos veces y se detiene ante tiempos de espera agotados u otros errores. Spring documenta los [tiempos de espera del transporte](https://docs.spring.io/spring-framework/reference/6.2/web/webflux-webclient/client-builder.html) por separado del [tiempo de espera del publicador de Reactor](https://projectreactor.io/docs/core/3.7.12/api/reactor/core/publisher/Mono.html).

## ¿Qué límite controla cada ajuste?

| Ajuste | Alcance en este ejemplo |
| --- | --- |
| `CONNECT_TIMEOUT_MILLIS` | Establecimiento de una conexión TCP; no es un presupuesto completo para DNS, obtención del pool o TLS |
| `responseTimeout` | Intervalo máximo entre lecturas de red al recibir una respuesta; no es un plazo para todo el cuerpo |
| Primer `timeout(attemptLimit)` | Una suscripción hasta la decodificación del cuerpo; vuelve a empezar en cada reintento |
| Último `timeout(totalLimit)` | La suscripción completa, con todos los intentos y demoras de reintento |
| `StepVerifier.verify(GUARD)` | Espera máxima del ejecutor de pruebas; no configura el cliente |

La [documentación de responseTimeout de Reactor Netty](https://projectreactor.io/docs/netty/1.2.11/api/reactor/netty/http/client/HttpClient.html) describe un intervalo de lectura, por lo que una respuesta que sigue entregando datos puede superar esa duración en total. El tiempo de espera externo del publicador establece un plazo global independiente. La cancelación detiene esta suscripción; no deshace el trabajo ya realizado por el servicio remoto.

## Limitar los reintentos antes de añadir más casos de fallo

![Aplicar un tiempo de espera por intento, reintentar solo errores 503 admitidos y limitar toda la operación](/assets/diagrams/technical/es-2026-10-30-webclient-timeout-retry.svg)

El diagrama resume el anidamiento de operadores, no cada evento HTTP. Cada intento termina correctamente o emite un error. Solo un error 503 con reintentos disponibles provoca una nueva suscripción tras una demora; los demás errores detienen la operación de inmediato. El tiempo de espera externo puede cancelar tanto un intento activo como una demora de reintento.

[`Retry.fixedDelay(2, delay)`](https://projectreactor.io/docs/core/release/api/reactor/util/retry/Retry.html) permite dos reintentos después del intento inicial: como máximo tres intentos de aplicación por suscripción. `.onRetryExhaustedThrow` propaga la última excepción 503 en lugar de envolverla en una excepción de reintentos agotados. `.disableRetry(true)` desactiva el reintento automático independiente de Reactor Netty ante una interrupción TCP, para que no añada un reintento de transporte oculto a estos recuentos.

El ejemplo realiza un GET y reintenta deliberadamente solo 503. Un tiempo de espera agotado no demuestra que el servidor no haya hecho nada. No copies esta política a pagos u otras escrituras sin un contrato explícito de idempotencia. No procesa `Retry-After`, no reintenta 429, no aplica espera exponencial ni variación aleatoria, ni coordina reintentos entre clientes. La demora fija corta acelera las pruebas; elige los límites y las demoras de producción según el contrato de tu API y el presupuesto de carga.

## Crear un proyecto independiente

Utiliza un directorio nuevo y vacío, JDK 17 y Gradle 8.4. El ejemplo fija Boot BOM 3.5.7 y MockWebServer 4.12.0 para coincidir con las [pruebas del contrato de respuesta](/en/posts/2023-09-19-springboot-test-webclient/). Son parámetros de reproducción, no recomendaciones de versiones actuales para producción. La resolución inicial de dependencias utiliza Maven Central; las pruebas HTTP solo utilizan loopback. No se incluye una aplicación Boot en ejecución ni un wrapper de Gradle.

### `settings.gradle`

```groovy
rootProject.name = 'webclient-timeout-retry'
```

### `build.gradle`

```groovy
plugins { id 'java' }
repositories { mavenCentral() }
dependencies {
    implementation platform('org.springframework.boot:spring-boot-dependencies:3.5.7')
    implementation 'org.springframework.boot:spring-boot-starter-webflux'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testImplementation 'io.projectreactor:reactor-test'
    testImplementation 'com.squareup.okhttp3:mockwebserver:4.12.0'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
test { useJUnitPlatform() }
```

## Mantener los dos plazos en posiciones distintas

Guarda la siguiente implementación. El constructor recibe duraciones positivas elegidas por quien lo llama; la prueba proporciona valores explícitos. El tiempo de espera de respuesta y el de conexión TCP de 1000 ms pertenecen a la factoría de transporte.

### `src/main/java/RetryClient.java`

```java
import java.time.Duration;
import io.netty.channel.ChannelOption;
import org.springframework.http.client.reactive.ReactorClientHttpConnector;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;
import reactor.core.publisher.Mono;
import reactor.netty.http.client.HttpClient;
import reactor.util.retry.Retry;

public class RetryClient {
    private final WebClient client;
    private final Duration attemptLimit;
    private final Duration totalLimit;
    private final Duration retryDelay;

    public RetryClient(WebClient client, Duration attemptLimit,
                       Duration totalLimit, Duration retryDelay) {
        this.client = client;
        this.attemptLimit = attemptLimit;
        this.totalLimit = totalLimit;
        this.retryDelay = retryDelay;
    }

    public static WebClient transport(String baseUrl, Duration responseLimit) {
        HttpClient http = HttpClient.create()
            .disableRetry(true)
            .option(ChannelOption.CONNECT_TIMEOUT_MILLIS, 1000)
            .responseTimeout(responseLimit);
        return WebClient.builder().baseUrl(baseUrl)
            .clientConnector(new ReactorClientHttpConnector(http)).build();
    }

    public Mono<String> get() {
        return Mono.defer(() -> client.get().uri("/value")
                .retrieve().bodyToMono(String.class))
            .timeout(attemptLimit)
            .retryWhen(Retry.fixedDelay(2, retryDelay)
                .filter(error -> error instanceof WebClientResponseException response
                    && response.getStatusCode().value() == 503)
                .onRetryExhaustedThrow((spec, signal) -> signal.failure()))
            .timeout(totalLimit);
    }
}
```

## Reproducir nueve contratos de la política

Siete pruebas utilizan un WebClient real y un MockWebServer local. Dos utilizan un intercambio sintético y el tiempo virtual de Reactor para verificar la temporización de los operadores sin depender de la planificación de la red. El tiempo virtual no prueba los tiempos de espera reales de los sockets de Reactor Netty. La prueba de transporte comprueba la causa anidada del tiempo de lectura agotado, mientras que el tiempo de espera del publicador produce `TimeoutException`.

### `src/test/java/RetryClientTest.java`

```java
import java.io.IOException;
import java.time.Duration;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.atomic.AtomicInteger;
import io.netty.handler.timeout.ReadTimeoutException;
import okhttp3.mockwebserver.MockResponse;
import okhttp3.mockwebserver.MockWebServer;
import okhttp3.mockwebserver.SocketPolicy;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpStatus;
import org.springframework.web.reactive.function.client.ClientResponse;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientRequestException;
import org.springframework.web.reactive.function.client.WebClientResponseException;
import reactor.core.publisher.Mono;
import reactor.netty.http.client.HttpClient;
import reactor.test.StepVerifier;
import static org.junit.jupiter.api.Assertions.*;

class RetryClientTest {
    private MockWebServer server;
    private WebClient client;
    private static final Duration GUARD = Duration.ofSeconds(10);

    @BeforeAll
    static void warmUp() {
        HttpClient.create().warmup().block(GUARD);
    }

    @BeforeEach
    void start() throws IOException {
        server = new MockWebServer();
        server.start();
        client = RetryClient.transport(server.url("/").toString(), Duration.ofSeconds(5));
    }

    @AfterEach
    void stop() throws IOException {
        server.shutdown();
    }

    RetryClient policy() {
        return new RetryClient(client, Duration.ofSeconds(3),
            Duration.ofSeconds(8), Duration.ofMillis(10));
    }

    void expectStatus(int status) {
        StepVerifier.create(policy().get())
            .expectErrorSatisfies(error -> assertEquals(status,
                assertInstanceOf(WebClientResponseException.class, error).getStatusCode().value()))
            .verify(GUARD);
    }

    @Test
    void successUsesOneRequest() {
        server.enqueue(new MockResponse().setBody("ok"));
        StepVerifier.create(policy().get()).expectNext("ok").expectComplete().verify(GUARD);
        assertEquals(1, server.getRequestCount());
    }

    @Test
    void two503ResponsesThenSuccessUseThreeRequests() {
        server.enqueue(new MockResponse().setResponseCode(503));
        server.enqueue(new MockResponse().setResponseCode(503));
        server.enqueue(new MockResponse().setBody("ok"));
        StepVerifier.create(policy().get()).expectNext("ok").expectComplete().verify(GUARD);
        assertEquals(3, server.getRequestCount());
    }

    @Test
    void exhausted503PreservesLastStatusAfterThreeRequests() {
        for (int i = 0; i < 3; i++) server.enqueue(new MockResponse().setResponseCode(503));
        expectStatus(503);
        assertEquals(3, server.getRequestCount());
    }

    @Test
    void notFoundIsNotRetried() {
        server.enqueue(new MockResponse().setResponseCode(404));
        expectStatus(404);
        assertEquals(1, server.getRequestCount());
    }

    @Test
    void otherServerErrorsAreNotRetried() {
        server.enqueue(new MockResponse().setResponseCode(500));
        expectStatus(500);
        assertEquals(1, server.getRequestCount());
    }

    @Test
    void attemptTimeoutIsNotRetried() {
        server.enqueue(new MockResponse().setSocketPolicy(SocketPolicy.NO_RESPONSE));
        RetryClient limited = new RetryClient(client, Duration.ofSeconds(1),
            Duration.ofSeconds(8), Duration.ofMillis(10));
        StepVerifier.create(limited.get()).expectError(TimeoutException.class).verify(GUARD);
        assertEquals(1, server.getRequestCount());
    }

    @Test
    void responseReadTimeoutIsNotRetried() {
        server.enqueue(new MockResponse().setSocketPolicy(SocketPolicy.NO_RESPONSE));
        WebClient shortRead = RetryClient.transport(server.url("/").toString(), Duration.ofMillis(250));
        RetryClient limited = new RetryClient(shortRead, Duration.ofSeconds(3),
            Duration.ofSeconds(8), Duration.ofMillis(10));
        StepVerifier.create(limited.get()).expectErrorSatisfies(error -> {
            assertInstanceOf(WebClientRequestException.class, error);
            assertInstanceOf(ReadTimeoutException.class, error.getCause());
        }).verify(GUARD);
        assertEquals(1, server.getRequestCount());
    }

    @Test
    void totalBudgetIncludesRetryDelay() {
        AtomicInteger attempts = new AtomicInteger();
        StepVerifier.withVirtualTime(() -> {
            WebClient synthetic = WebClient.builder().exchangeFunction(request -> Mono.defer(() -> {
                attempts.incrementAndGet();
                return Mono.just(ClientResponse.create(HttpStatus.SERVICE_UNAVAILABLE).build());
            })).build();
            return new RetryClient(synthetic, Duration.ofSeconds(1),
                Duration.ofMillis(1500), Duration.ofSeconds(1)).get();
        }).thenAwait(Duration.ofMillis(1500)).expectError(TimeoutException.class).verify(GUARD);
        assertEquals(2, attempts.get());
    }

    @Test
    void attemptBudgetRestartsAfterRetry() {
        AtomicInteger attempts = new AtomicInteger();
        StepVerifier.withVirtualTime(() -> {
            WebClient synthetic = WebClient.builder().exchangeFunction(request -> Mono.defer(() -> {
                int attempt = attempts.incrementAndGet();
                return Mono.delay(Duration.ofMillis(400)).map(tick -> attempt == 1
                    ? ClientResponse.create(HttpStatus.SERVICE_UNAVAILABLE).build()
                    : ClientResponse.create(HttpStatus.OK).body("ok").build());
            })).build();
            return new RetryClient(synthetic, Duration.ofMillis(500),
                Duration.ofSeconds(2), Duration.ofMillis(200)).get();
        }).thenAwait(Duration.ofSeconds(1)).expectNext("ok").expectComplete().verify(GUARD);
        assertEquals(2, attempts.get());
    }
}
```

## Ejecutar el proyecto e interpretar el resultado

```sh
gradle --no-daemon clean test
```

La reproducción local utilizó JDK 17.0.8.1 y Gradle 8.4. Las nueve pruebas pasaron. Consulta `build/reports/tests/test/index.html` o `build/test-results/test/TEST-RetryClientTest.xml` para ver las aserciones; `BUILD SUCCESSFUL` por sí solo no indica cuántas pruebas se ejecutaron.

| Escenario | Resultado comprobado |
| --- | --- |
| Éxito inmediato | Una solicitud HTTP, `ok` y finalización |
| 503 → 503 → éxito | Tres solicitudes HTTP, `ok` y finalización |
| 503 en todos los intentos | Tres solicitudes HTTP, se conserva el último 503 |
| 404 / 500 | Una solicitud HTTP para cada uno, se conserva el estado |
| Sin respuesta, límite por intento de un segundo | `TimeoutException`, una solicitud HTTP |
| Sin respuesta, límite de lectura de respuesta de 250 ms | `WebClientRequestException` con `ReadTimeoutException`, una solicitud |
| Presupuesto total de 1.5 s, demora de reintento de un segundo | Dos intentos sintéticos; el tiempo de espera cancela la demora antes del tercero |
| Intento de 400 ms, demora de 200 ms, intento de 400 ms | Cada intento cabe en 500 ms; se comprueban el éxito y la finalización tras avanzar el tiempo virtual 1 s |

Estas comprobaciones no reproducen el tiempo de espera al establecer TCP, fallos DNS, negociación TLS, agotamiento del pool, redirecciones ni efectos secundarios distribuidos. El límite de conexión está configurado, pero aquí no se valida experimentalmente. La planificación del SO puede afectar al tiempo real transcurrido; las pruebas verifican tipos de error y recuentos de solicitudes, no milisegundos exactos de reloj. Para el estado, el tipo de contenido y JSON, continúa con el [ejemplo del contrato de respuesta de WebClient](/en/posts/2023-09-19-springboot-test-webclient/).
