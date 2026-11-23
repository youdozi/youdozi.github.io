---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2026-11-22-spring-boot-4-2-restclient-migration",
  "routeSlug": "2026-11-22-spring-boot-4-2-restclient-migration",
  "kind": "post",
  "title": "RestTemplate und TestRestTemplate in Spring Boot 4.2 migrieren",
  "description": "In Spring Boot 4.2 auf RestClient und RestTestClient umsteigen und die Antworten 200 und 404 am laufenden Server prüfen.",
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
  "draftSha256": "cff19c52be99ac20dfd260d02fe9f2031e816bc31abe9605e796fdc154fab183",
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

**Für Aufrufe externer APIs eignet sich `RestClient`. Mit `RestTestClient` können Tests Anfragen an die Anwendung senden und die Antworten prüfen.** Spring Boot 4.2 stuft die Autokonfiguration und den Builder für `RestTemplate` sowie die Unterstützung für `TestRestTemplate` als veraltet ein. Übernehmen Sie bei der Migration die Prüfungen für Fehler- und Erfolgsfälle. Prüft ein Test bislang auf HTTP 404, sollte dieselbe Statusprüfung im neuen Test stehen. [Versionshinweise zu Spring Boot 4.2](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.2-Release-Notes#deprecation-of-testresttemplate-support)

## Welche APIs ersetzen die bisherigen?

| Bestehender Code | Ersatz | Zu prüfendes Verhalten |
| --- | --- | --- |
| `RestTemplateBuilder` und `getForObject()` | `RestClient.Builder` und `get().uri().retrieve().body()` | Basis-URL, Anfrage-Header und Behandlung von 4xx- und 5xx-Antworten |
| `RestTemplateCustomizer` | `RestClientCustomizer` | Interceptoren, Timeouts und Request-Factory |
| `@AutoConfigureTestRestTemplate` und `TestRestTemplate` | `@AutoConfigureRestTestClient` und `RestTestClient` | Start des laufenden Servers, Statuscodes und Antwortinhalte |

`RestClient.retrieve()` löst standardmäßig bei 4xx- und 5xx-Antworten eine Ausnahme aus. Dasselbe gilt für ein standardmäßig konfiguriertes `RestTemplate`. `TestRestTemplate` gibt die Antwort zurück, damit der Test die Statuscodes prüfen kann. Bei `RestTestClient` verwenden Sie dazu `expectStatus()` nach `exchange()`. Wenn Ihr Client bisher eine eigene Fehlerbehandlung nutzte, bilden Sie dieselben Regeln für Statuscodes mit `defaultStatusHandler()` oder pro Anfrage mit `onStatus()` ab. [Referenz der REST-Clients in Spring Framework](https://docs.spring.io/spring-framework/reference/integration/rest-clients.html) · [TestRestTemplate-API](https://docs.spring.io/spring-boot/api/java/org/springframework/boot/resttestclient/TestRestTemplate.html)

## Beide HTTP-Schnittstellen mit einer Produktabfrage testen

![RestTestClient sendet eine Produkt-ID an die Spring-MVC-Anwendung. Diese ruft mit RestClient die Upstream-API auf. Antwortet diese mit 200, gibt die Anwendung den Produktnamen mit Status 200 zurück. Antwortet die API mit 404, löst der Client eine Ausnahme aus, aus der die Anwendung eine 404-Antwort erzeugt.](/assets/diagrams/technical/de-2026-11-22-spring-boot-4-2-restclient-migration.svg)

Für die Produkt-ID `42` liefert die Upstream-API den Namen `Keyboard`. Bei allen anderen IDs antwortet sie mit 404. Das Diagramm zeigt den Ablauf der beiden Integrationstests, die Anfragen über die Anwendung senden. Für die Upstream-API starten die Tests einen lokalen HTTP-Server.

### `pom.xml`

Das Beispiel nutzt Spring Boot 4.2.0 und JDK 21. Der MVC-Test-Starter enthält das Modul zur Autokonfiguration von `RestTestClient`.

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

Wenn Ihre Anwendung bisher `restTemplate.getForObject("/items/{id}", String.class, id)` verwendet hat, behalten Sie die URI-Vorlage und den Antworttyp im neuen Aufruf bei. Injizieren Sie den von Boot konfigurierten Builder und setzen Sie die Basis-URL der Upstream-API. Antwortet diese im Beispiel mit 404, weil es das Produkt nicht gibt, lässt der Controller die Anwendung ebenfalls mit 404 antworten.

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

Behalten Sie `RANDOM_PORT` bei, um HTTP-Anfragen an einen laufenden eingebetteten Server zu senden. Der von Boot injizierte `RestTestClient` löst relative Pfade anhand der Adresse dieses Servers auf. Wenn der alte Test mit `getForEntity("/products/99", String.class).getStatusCode()` auf 404 geprüft hat, prüfen Sie denselben Status mit `exchange().expectStatus().isNotFound()`. [Spring-Boot-Dokumentation zum Testen mit laufendem Server](https://docs.spring.io/spring-boot/reference/testing/spring-boot-applications.html#testing.spring-boot-applications.with-running-server)

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

## Tests ausführen

Speichern Sie die drei Dateien und führen Sie im Projektstamm folgenden Befehl aus.

```sh
mvn test
```

Der Testlauf verwendete JDK 21.0.1 und Maven 3.9.11. Der eingebettete Tomcat und der lokale HTTP-Server, der die Upstream-API ersetzte, liefen auf zufällig gewählten Ports. Alle drei Tests waren erfolgreich.

| Prüfgegenstand | Beobachtetes Ergebnis |
| --- | --- |
| `GET /products/42` | `200 OK` mit `Keyboard` im Antwortinhalt |
| `GET /products/99` | `404 Not Found` mit leerem Antwortinhalt |
| `catalog.findName(99)` | Löst `HttpClientErrorException.NotFound` aus |

```text
Tests run: 3, Failures: 0, Errors: 0, Skipped: 0
BUILD SUCCESS
```

Listen Sie vor der Migration auf, welche Statuscodes und Antwortinhalte Ihre Tests prüfen. Ein Client, der aus einem 404 der Upstream-API ein leeres Ergebnis macht, und ein Controller, der selbst einen 404 zurückgibt, haben jeweils einen eigenen Vertrag. Testen Sie beide Schnittstellen, um Änderungen im Verhalten zu erkennen. Einen Vergleich synchroner und reaktiver Aufrufe bietet [WebClient im Vergleich zu RestClient](/en/posts/2026-10-31-webclient-restclient-comparison/).
