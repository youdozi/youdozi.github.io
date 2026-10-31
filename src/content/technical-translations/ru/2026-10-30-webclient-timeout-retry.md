---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ru",
  "translationKey": "2026-10-30-webclient-timeout-retry",
  "routeSlug": "2026-10-30-webclient-timeout-retry",
  "kind": "post",
  "title": "Проверка тайм-аутов WebClient и ограниченных повторов с Reactor",
  "description": "Разделите тайм-ауты соединения, ответа, отдельной попытки и всей операции. Проверьте политику GET с двумя повторами только при HTTP 503 через локальный HTTP и виртуальное время Reactor.",
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
  "draftSha256": "a7e78009c0f10eb96655dcc537ae87607a2122e9669dec9468e3524bf448d45d",
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
Разместите `timeout` отдельной попытки перед `retryWhen`, а общий `timeout` — после него, чтобы задержки повторов входили в общий бюджет. Повторяйте только ошибки, разрешённые контрактом API: этот пример GET повторяет HTTP 503 не более двух раз и останавливается при тайм-аутах или других ошибках. Spring описывает [транспортные тайм-ауты](https://docs.spring.io/spring-framework/reference/6.2/web/webflux-webclient/client-builder.html) отдельно от [тайм-аута издателя Reactor](https://projectreactor.io/docs/core/3.7.12/api/reactor/core/publisher/Mono.html).

## Что ограничивает каждая настройка?

| Настройка | Область действия в примере |
| --- | --- |
| `CONNECT_TIMEOUT_MILLIS` | Установка TCP-соединения; не полный бюджет DNS, получения соединения из пула или TLS |
| `responseTimeout` | Максимальный интервал между сетевыми чтениями при получении ответа; не срок получения всего тела |
| Первый `timeout(attemptLimit)` | Одна подписка до завершения декодирования тела; отсчёт начинается заново при каждом повторе |
| Последний `timeout(totalLimit)` | Вся подписка, включая все попытки и задержки повторов |
| `StepVerifier.verify(GUARD)` | Максимальное ожидание средства запуска тестов; клиент не настраивает |

[Документация responseTimeout Reactor Netty](https://projectreactor.io/docs/netty/1.2.11/api/reactor/netty/http/client/HttpClient.html) описывает интервал чтения, поэтому общая длительность ответа, непрерывно передающего данные, может превышать это значение. Внешний тайм-аут издателя задаёт отдельный общий срок. Отмена прекращает эту подписку; уже выполненную удалённым сервисом работу она не отменяет.

## Ограничьте повторы до добавления других ошибок

![Применение тайм-аута попытки, повтор только подходящих ошибок 503 и ограничение всей операции](/assets/diagrams/technical/ru-2026-10-30-webclient-timeout-retry.svg)

Схема показывает вложенность операторов, а не каждое событие HTTP. Каждая попытка завершается успехом или ошибкой. Только ошибка 503 при оставшихся повторах вызывает повторную подписку после задержки; другие ошибки немедленно останавливают выполнение. Внешний тайм-аут может отменить как активную попытку, так и задержку повтора.

[`Retry.fixedDelay(2, delay)`](https://projectreactor.io/docs/core/release/api/reactor/util/retry/Retry.html) допускает два повтора после первоначальной попытки: не более трёх попыток приложения на подписку. `.onRetryExhaustedThrow` передаёт последнее исключение 503 вместо обёртки об исчерпании повторов. `.disableRetry(true)` отключает отдельный автоматический повтор Reactor Netty при обрыве TCP, чтобы скрытый транспортный повтор не увеличивал это количество.

Пример выполняет GET и намеренно повторяет только 503. Тайм-аут не доказывает, что сервер ничего не сделал. Не переносите эту политику на платежи и другие операции записи без явного контракта идемпотентности. Она не обрабатывает `Retry-After`, не повторяет 429, не применяет экспоненциальную задержку или случайный разброс и не координирует повторы между вызывающими сторонами. Короткая фиксированная задержка ускоряет тесты; рабочие ограничения и задержки выбирайте по контракту API и бюджету нагрузки.

## Создание самостоятельного проекта

Используйте новый пустой каталог, JDK 17 и Gradle 8.4. Пример фиксирует Boot BOM 3.5.7 и MockWebServer 4.12.0 в соответствии с [тестами контракта ответа](/en/posts/2023-09-19-springboot-test-webclient/). Это параметры воспроизведения, а не рекомендации актуальных версий для эксплуатации. При первоначальном разрешении зависимостей используется Maven Central; HTTP-тесты используют только loopback. Работающее приложение Boot и Gradle wrapper в комплект не входят.

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

## Разместите два срока в разных позициях

Сохраните следующую реализацию. Конструктор принимает положительные длительности, выбранные вызывающей стороной; тест задаёт явные значения. Тайм-аут ответа и тайм-аут TCP-соединения 1 000 ms относятся к транспортной фабрике.

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

## Воспроизведение девяти контрактов политики

Семь тестов используют настоящий WebClient и локальный MockWebServer. Два используют синтетический обмен и виртуальное время Reactor, чтобы проверить временные характеристики операторов независимо от планирования сети. Виртуальное время не проверяет реальные тайм-ауты сокетов Reactor Netty. Транспортный тест проверяет вложенную причину ошибки чтения по тайм-ауту, тогда как тайм-аут издателя выдаёт `TimeoutException`.

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

## Запуск проекта и чтение результата

```sh
gradle --no-daemon clean test
```

Для локального воспроизведения использовались JDK 17.0.8.1 и Gradle 8.4. Все девять тестов прошли. Проверяйте утверждения в `build/reports/tests/test/index.html` или `build/test-results/test/TEST-RetryClientTest.xml`; само по себе `BUILD SUCCESSFUL` не сообщает количество запущенных тестов.

| Сценарий | Проверенный результат |
| --- | --- |
| Немедленный успех | Один HTTP-запрос, `ok`, затем завершение |
| 503 → 503 → успех | Три HTTP-запроса, `ok`, затем завершение |
| 503 при каждой попытке | Три HTTP-запроса, последняя ошибка 503 сохранена |
| 404 / 500 | По одному HTTP-запросу, статус сохранён |
| Нет ответа, предел попытки одна секунда | `TimeoutException`, один HTTP-запрос |
| Нет ответа, предел чтения ответа 250 ms | `WebClientRequestException` с `ReadTimeoutException`, один запрос |
| Общий бюджет 1.5 s, задержка повтора одна секунда | Две синтетические попытки; тайм-аут отменяет задержку до третьей |
| Попытка 400 ms, задержка 200 ms, попытка 400 ms | Каждая попытка укладывается в 500 ms; успех и завершение проверены после продвижения виртуального времени на 1 s |

Эти проверки не воспроизводят тайм-аут установки TCP-соединения, сбой DNS, согласование TLS, исчерпание пула, перенаправления или распределённые побочные эффекты. Ограничение соединения настроено, но экспериментально здесь не проверено. Планирование ОС может влиять на реальное время; тесты проверяют типы ошибок и количество запросов, а не точные миллисекунды настенных часов. Обработку статуса, типа содержимого и JSON см. в [примере контракта ответа WebClient](/en/posts/2023-09-19-springboot-test-webclient/).
