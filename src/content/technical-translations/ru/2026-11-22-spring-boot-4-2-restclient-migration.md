---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ru",
  "translationKey": "2026-11-22-spring-boot-4-2-restclient-migration",
  "routeSlug": "2026-11-22-spring-boot-4-2-restclient-migration",
  "kind": "post",
  "title": "Переход с RestTemplate и TestRestTemplate в Spring Boot 4.2",
  "description": "Перейдите на RestClient и RestTestClient в Spring Boot 4.2 и проверьте ответы 200 и 404 на работающем сервере.",
  "categories": [
    "springboot"
  ],
  "tags": [
    "spring-boot",
    "resttemplate",
    "testresttemplate",
    "restclient",
    "resttestclient",
    "http-client"
  ],
  "sourcePath": "src/content/posts/en/2026-11-22-spring-boot-4-2-restclient-migration.md",
  "sourceSha256": "8859ad29e5643a2fc5112004d1582dceddbd10ea1ccfdc3bd1bfb21aacff6b33",
  "draftSha256": "3a20c623b4302046c132ec69aa9cfece7d4ebfeec4a2fc576b8ddbd8348872fa",
  "manifestPath": ".pipeline/technical-translations/batch-185/manifest.json",
  "manifestSha256": "3281e1d3e7c9b3abbb6c101d911dd0fcdee7dd54f7034838135f391123b6fb44",
  "publishedAt": "2026-11-23T00:19:14.218Z",
  "updatedAt": "2026-11-23T00:19:14.218Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 185,
    "approvedAt": "2026-11-23T00:19:14.218Z",
    "basis": "The site owner explicitly requested missing supported locales for the eight articles published in PRs #177–#184. This authorizes publication of the 48 editions enumerated in this batch."
  }
}
---

**Вызывайте внешние API через `RestClient`. В тестах, которые отправляют запросы приложению и проверяют ответы, используйте `RestTestClient`.** В Spring Boot 4.2 автоконфигурация и билдер для `RestTemplate`, а также поддержка `TestRestTemplate` объявлены устаревшими. При миграции перенесите проверки ошибок и успешных ответов. Если старый тест проверял HTTP 404, сохраните эту проверку и в новом тесте. [Примечания к выпуску Spring Boot 4.2](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.2-Release-Notes#deprecation-of-testresttemplate-support)

## Какие API использовать вместо прежних?

| Существующий код | Замена | Что проверить |
| --- | --- | --- |
| `RestTemplateBuilder` и `getForObject()` | `RestClient.Builder` и `get().uri().retrieve().body()` | Базовый URL, заголовки запроса и обработку ответов 4xx и 5xx |
| `RestTemplateCustomizer` | `RestClientCustomizer` | Перехватчики, тайм-ауты и фабрику запросов |
| `@AutoConfigureTestRestTemplate` и `TestRestTemplate` | `@AutoConfigureRestTestClient` и `RestTestClient` | Как запускается сервер, коды состояния и тела ответов |

По умолчанию `RestClient.retrieve()` выбрасывает исключение для ответов 4xx и 5xx, как и `RestTemplate` в стандартной конфигурации. `TestRestTemplate` возвращает ответ, чтобы тест мог проверить код состояния. Для такой проверки с `RestTestClient` вызовите `expectStatus()` после `exchange()`. Если в прежнем клиенте был собственный обработчик ошибок, воспроизведите правила обработки статусов через `defaultStatusHandler()` или через `onStatus()` для отдельного запроса. [Справочник по REST-клиентам Spring Framework](https://docs.spring.io/spring-framework/reference/integration/rest-clients.html) · [API TestRestTemplate](https://docs.spring.io/spring-boot/api/java/org/springframework/boot/resttestclient/TestRestTemplate.html)

## Проверка обеих границ HTTP на примере поиска товара

![RestTestClient передаёт идентификатор товара приложению Spring MVC, которое вызывает вышестоящий API через RestClient. При ответе 200 вышестоящего API приложение возвращает название товара со статусом 200. При ответе 404 клиент выбрасывает исключение, которое приложение преобразует в ответ 404.](/assets/diagrams/technical/ru-2026-11-22-spring-boot-4-2-restclient-migration.svg)

Для товара с идентификатором `42` вышестоящий API возвращает название `Keyboard`. Для всех остальных идентификаторов он возвращает 404. На схеме показаны два интеграционных теста, которые отправляют запросы через приложение. Вместо вышестоящего API тесты запускают локальный HTTP-сервер.

### `pom.xml`

В примере используются Spring Boot 4.2.0 и JDK 21. Стартер тестов MVC включает модуль автоконфигурации `RestTestClient`.

```xml
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>4.2.0</version>
    </parent>
    <groupId>example</groupId>
    <artifactId>restclient-migration</artifactId>
    <version>1.0.0</version>
    <properties>
        <java.version>21</java.version>
    </properties>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-webmvc</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-restclient</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-webmvc-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>
```

### `src/main/java/example/CatalogApplication.java`

Если прежний вызов выглядел как `restTemplate.getForObject("/items/{id}", String.class, id)`, сохраните шаблон URI и тип ответа в новом вызове. Внедрите настроенный Boot билдер и задайте базовый URL вышестоящего API. В примере контроллер преобразует ответ 404 об отсутствующем товаре в ответ приложения с кодом 404.

```java
package example;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestClient;

@SpringBootApplication
public class CatalogApplication {
    public static void main(String[] args) {
        SpringApplication.run(CatalogApplication.class, args);
    }
}

@Service
class CatalogClient {
    private final RestClient http;

    CatalogClient(RestClient.Builder builder, @Value("${catalog.base-url}") String baseUrl) {
        this.http = builder.baseUrl(baseUrl).build();
    }

    String findName(long id) {
        return http.get()
            .uri("/items/{id}", id)
            .retrieve()
            .body(String.class);
    }
}

@RestController
class ProductController {
    private final CatalogClient catalog;

    ProductController(CatalogClient catalog) {
        this.catalog = catalog;
    }

    @GetMapping("/products/{id}")
    ResponseEntity<String> product(@PathVariable("id") long id) {
        try {
            return ResponseEntity.ok(catalog.findName(id));
        } catch (HttpClientErrorException.NotFound ex) {
            return ResponseEntity.notFound().build();
        }
    }
}
```

### `src/test/java/example/CatalogApplicationTests.java`

Оставьте `RANDOM_PORT`, чтобы отправлять HTTP-запросы работающему встроенному серверу. Внедрённый Boot экземпляр `RestTestClient` разрешает относительные пути по адресу этого сервера. Если прежний тест вызывал `getForEntity("/products/99", String.class).getStatusCode()` для проверки 404, проверьте тот же статус через `exchange().expectStatus().isNotFound()`. [Документация Spring Boot о тестировании с работающим сервером](https://docs.spring.io/spring-boot/reference/testing/spring-boot-applications.html#testing.spring-boot-applications.with-running-server)

```java
package example;

import java.io.IOException;
import java.io.UncheckedIOException;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;

import com.sun.net.httpserver.HttpServer;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.resttestclient.autoconfigure.AutoConfigureRestTestClient;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.web.servlet.client.RestTestClient;
import org.springframework.web.client.HttpClientErrorException;

import static org.assertj.core.api.Assertions.assertThatThrownBy;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureRestTestClient
class CatalogApplicationTests {
    private static final HttpServer upstream = startUpstream();

    @Autowired
    private RestTestClient app;

    @Autowired
    private CatalogClient catalog;

    @DynamicPropertySource
    static void configureUpstream(DynamicPropertyRegistry properties) {
        properties.add("catalog.base-url",
            () -> "http://127.0.0.1:" + upstream.getAddress().getPort());
    }

    @AfterAll
    static void stopUpstream() {
        upstream.stop(0);
    }

    @Test
    void returnsProductName() {
        app.get().uri("/products/42").exchange()
            .expectStatus().isOk()
            .expectBody(String.class).isEqualTo("Keyboard");
    }

    @Test
    void returnsNotFoundForMissingProduct() {
        app.get().uri("/products/99").exchange()
            .expectStatus().isNotFound()
            .expectBody().isEmpty();
    }

    @Test
    void turnsUpstream404IntoAnException() {
        assertThatThrownBy(() -> catalog.findName(99))
            .isInstanceOf(HttpClientErrorException.NotFound.class);
    }

    private static HttpServer startUpstream() {
        try {
            HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
            server.createContext("/items/", exchange -> {
                try (exchange) {
                    if (exchange.getRequestURI().getPath().equals("/items/42")) {
                        byte[] body = "Keyboard".getBytes(StandardCharsets.UTF_8);
                        exchange.getResponseHeaders().set("Content-Type", "text/plain; charset=UTF-8");
                        exchange.sendResponseHeaders(200, body.length);
                        exchange.getResponseBody().write(body);
                    } else {
                        exchange.sendResponseHeaders(404, -1);
                    }
                }
            });
            server.start();
            return server;
        } catch (IOException ex) {
            throw new UncheckedIOException(ex);
        }
    }
}
```

## Запуск тестов

Сохраните три файла и выполните следующую команду из корня проекта.

```sh
mvn test
```

При запуске использовались JDK 21.0.1 и Maven 3.9.11. Встроенный Tomcat и локальный HTTP-сервер, который заменял вышестоящий API, работали на случайных портах. Все три теста прошли.

| Что проверяет тест | Наблюдаемый результат |
| --- | --- |
| `GET /products/42` | `200 OK` с `Keyboard` в теле ответа |
| `GET /products/99` | `404 Not Found` с пустым телом |
| `catalog.findName(99)` | Выбрасывает `HttpClientErrorException.NotFound` |

```text
Tests run: 3, Failures: 0, Errors: 0, Skipped: 0
BUILD SUCCESS
```

Перед миграцией проекта перечислите статусы и тела ответов, которые проверяют старые тесты. Например, у клиента, который превращает входящий от вышестоящего сервиса 404 в пустой результат, и контроллера, который сам отправляет 404, разные контракты. Проверьте каждую границу, чтобы увидеть, где изменилось поведение. Синхронные и реактивные вызовы сопоставлены в статье [Сравнение WebClient и RestClient](/en/posts/2026-10-31-webclient-restclient-comparison/).
