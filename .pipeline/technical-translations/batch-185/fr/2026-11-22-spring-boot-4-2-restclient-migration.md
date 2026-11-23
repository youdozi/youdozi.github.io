---
{
  "state": "draft",
  "language": "fr",
  "translationKey": "2026-11-22-spring-boot-4-2-restclient-migration",
  "title": "Migrer RestTemplate et TestRestTemplate dans Spring Boot 4.2",
  "description": "Passez à RestClient et RestTestClient dans Spring Boot 4.2 et vérifiez les réponses 200 et 404 sur un serveur en cours d’exécution.",
  "sourcePath": "src/content/posts/en/2026-11-22-spring-boot-4-2-restclient-migration.md",
  "sourceSha256": "8859ad29e5643a2fc5112004d1582dceddbd10ea1ccfdc3bd1bfb21aacff6b33"
}
---

**Utilisez `RestClient` pour appeler des API externes et `RestTestClient` pour les tests qui envoient des requêtes à votre application et vérifient ses réponses.** Spring Boot 4.2 déprécie l’autoconfiguration et le builder de `RestTemplate`, ainsi que la prise en charge de `TestRestTemplate`. Lors de la migration, reprenez les assertions d’erreur et les cas de réussite. Si un test vérifiait le statut HTTP 404, conservez la même assertion dans le nouveau test. [Notes de version de Spring Boot 4.2](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.2-Release-Notes#deprecation-of-testresttemplate-support)

## Quelles API remplacent les API existantes ?

| Code existant | Remplacement | Comportement à vérifier |
| --- | --- | --- |
| `RestTemplateBuilder` et `getForObject()` | `RestClient.Builder` et `get().uri().retrieve().body()` | URL de base, en-têtes de requête et traitement des réponses 4xx et 5xx |
| `RestTemplateCustomizer` | `RestClientCustomizer` | Intercepteurs, délais d’expiration et fabrique de requêtes |
| `@AutoConfigureTestRestTemplate` et `TestRestTemplate` | `@AutoConfigureRestTestClient` et `RestTestClient` | Démarrage du serveur, codes de statut et corps de réponse |

Par défaut, `RestClient.retrieve()` lève une exception pour les réponses 4xx et 5xx, tout comme `RestTemplate` avec la configuration par défaut. `TestRestTemplate` renvoie la réponse pour que le test puisse vérifier ces statuts. Avec `RestTestClient`, appelez `expectStatus()` après `exchange()` pour conserver l’assertion. Si le client existant utilise un gestionnaire d’erreurs personnalisé, reproduisez les mêmes règles de statut avec `defaultStatusHandler()` ou avec `onStatus()` pour chaque requête. [Référence des clients REST de Spring Framework](https://docs.spring.io/spring-framework/reference/integration/rest-clients.html) · [API de TestRestTemplate](https://docs.spring.io/spring-boot/api/java/org/springframework/boot/resttestclient/TestRestTemplate.html)

## Tester les deux interfaces HTTP avec une API de recherche de produits

![RestTestClient envoie un identifiant de produit à l’application Spring MVC, qui utilise RestClient pour appeler l’API en amont. Sur un 200 en amont, l’application renvoie le nom du produit avec le statut 200. Sur un 404 en amont, le client lève une exception que l’application transforme en réponse 404.](2026-11-22-spring-boot-4-2-restclient-migration.svg)

Pour le produit d’identifiant `42`, l’API en amont renvoie le nom `Keyboard`. Tous les autres identifiants donnent un 404. Le schéma suit les deux tests d’intégration qui envoient des requêtes par l’application. Les tests démarrent un serveur HTTP local à la place de l’API en amont.

### `pom.xml`

L’exemple utilise Spring Boot 4.2.0 et JDK 21. Le starter de test MVC inclut le module d’autoconfiguration de `RestTestClient`.

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

Si l’appel existant était `restTemplate.getForObject("/items/{id}", String.class, id)`, conservez le modèle d’URI et le type de réponse dans le nouvel appel. Injectez le builder configuré par Boot et définissez l’URL de base de l’API en amont. Dans cet exemple, lorsque le produit est absent, le contrôleur convertit le 404 en amont en un 404 de l’application.

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

Conservez `RANDOM_PORT` pour envoyer les requêtes HTTP à un serveur embarqué en cours d’exécution. Le `RestTestClient` injecté par Boot résout les chemins relatifs à partir de l’adresse de ce serveur. Si l’ancien test utilisait `getForEntity("/products/99", String.class).getStatusCode()` pour vérifier un 404, vérifiez le même statut avec `exchange().expectStatus().isNotFound()`. [Documentation Spring Boot sur les tests avec un serveur en cours d’exécution](https://docs.spring.io/spring-boot/reference/testing/spring-boot-applications.html#testing.spring-boot-applications.with-running-server)

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

## Exécuter les tests

Enregistrez les trois fichiers et lancez la commande suivante à la racine du projet.

```sh
mvn test
```

L’exécution a utilisé JDK 21.0.1 et Maven 3.9.11. Le Tomcat embarqué et le serveur HTTP local qui remplace l’API en amont ont tous deux utilisé des ports aléatoires. Les trois tests ont réussi.

| Vérification du test | Résultat observé |
| --- | --- |
| `GET /products/42` | `200 OK` avec `Keyboard` dans le corps |
| `GET /products/99` | `404 Not Found` avec un corps vide |
| `catalog.findName(99)` | Lève `HttpClientErrorException.NotFound` |

```text
Tests run: 3, Failures: 0, Errors: 0, Skipped: 0
BUILD SUCCESS
```

Avant de migrer un projet, répertoriez les statuts et les corps de réponse que vérifient vos tests. Par exemple, un client qui convertit un 404 en amont en résultat vide et un contrôleur qui renvoie son propre 404 ont des contrats distincts. Testez chaque interface pour repérer les changements de comportement. Pour comparer les appels synchrones et réactifs, consultez [WebClient et RestClient, comparaison](/en/posts/2026-10-31-webclient-restclient-comparison/).
