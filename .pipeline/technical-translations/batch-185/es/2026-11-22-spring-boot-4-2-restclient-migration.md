---
{
  "state": "draft",
  "language": "es",
  "translationKey": "2026-11-22-spring-boot-4-2-restclient-migration",
  "title": "Cómo migrar RestTemplate y TestRestTemplate en Spring Boot 4.2",
  "description": "Migra a RestClient y RestTestClient en Spring Boot 4.2 y verifica las respuestas 200 y 404 en un servidor en ejecución.",
  "sourcePath": "src/content/posts/en/2026-11-22-spring-boot-4-2-restclient-migration.md",
  "sourceSha256": "8859ad29e5643a2fc5112004d1582dceddbd10ea1ccfdc3bd1bfb21aacff6b33"
}
---

**Usa `RestClient` para llamar a API externas y `RestTestClient` para las pruebas que envían solicitudes a tu aplicación y verifican sus respuestas.** Spring Boot 4.2 declara obsoletos la configuración automática y el constructor de `RestTemplate`, además de la compatibilidad con `TestRestTemplate`. Conserva las comprobaciones de errores y los casos de éxito al migrar. Si una prueba existente comprobaba HTTP 404, conserva la misma comprobación en la nueva prueba. [Notas de la versión Spring Boot 4.2](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.2-Release-Notes#deprecation-of-testresttemplate-support)

## ¿Qué API sustituyen a las existentes?

| Código existente | Sustitución | Comportamiento que debes comprobar |
| --- | --- | --- |
| `RestTemplateBuilder` y `getForObject()` | `RestClient.Builder` y `get().uri().retrieve().body()` | URL base, encabezados de solicitud y tratamiento de respuestas 4xx y 5xx |
| `RestTemplateCustomizer` | `RestClientCustomizer` | Interceptores, tiempos de espera y fábrica de solicitudes |
| `@AutoConfigureTestRestTemplate` y `TestRestTemplate` | `@AutoConfigureRestTestClient` y `RestTestClient` | Cómo arranca el servidor, códigos de estado y cuerpos de respuesta |

De forma predeterminada, `RestClient.retrieve()` lanza una excepción ante respuestas 4xx y 5xx, igual que `RestTemplate` con su configuración predeterminada. `TestRestTemplate` devuelve la respuesta para que la prueba pueda comprobar esos códigos. Con `RestTestClient`, usa `expectStatus()` después de `exchange()` para mantener la comprobación. Si el cliente anterior tenía un manejador de errores personalizado, reproduce las mismas reglas con `defaultStatusHandler()` o con `onStatus()` para una solicitud concreta. [Referencia de clientes REST de Spring Framework](https://docs.spring.io/spring-framework/reference/integration/rest-clients.html) · [API de TestRestTemplate](https://docs.spring.io/spring-boot/api/java/org/springframework/boot/resttestclient/TestRestTemplate.html)

## Prueba ambas interfaces HTTP con una API de consulta de productos

![RestTestClient envía un ID de producto a la aplicación Spring MVC, que llama a la API externa con RestClient. Si la API externa responde 200, la aplicación devuelve el nombre del producto con estado 200. Si responde 404, el cliente lanza una excepción que la aplicación convierte en una respuesta 404.](2026-11-22-spring-boot-4-2-restclient-migration.svg)

Para el ID de producto `42`, la API externa devuelve el nombre `Keyboard`. Todos los demás ID reciben un 404. El diagrama sigue las dos pruebas de integración que envían solicitudes a través de la aplicación. Las pruebas arrancan un servidor HTTP local en lugar de la API externa.

### `pom.xml`

El ejemplo usa Spring Boot 4.2.0 y JDK 21. El starter de pruebas de MVC incluye el módulo de configuración automática de `RestTestClient`.

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

Si la llamada existente era `restTemplate.getForObject("/items/{id}", String.class, id)`, conserva la plantilla de URI y el tipo de respuesta en la nueva llamada. Inyecta el constructor configurado por Boot y establece la URL base de la API externa. En este ejemplo, el controlador convierte el 404 de la API externa para un producto que no existe en un 404 de la aplicación.

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

Conserva `RANDOM_PORT` para enviar solicitudes HTTP a un servidor embebido en ejecución. El `RestTestClient` que inyecta Boot resuelve las rutas relativas según la dirección de ese servidor. Si la prueba anterior usaba `getForEntity("/products/99", String.class).getStatusCode()` para comprobar un 404, comprueba el mismo estado con `exchange().expectStatus().isNotFound()`. [Documentación de Spring Boot sobre pruebas con un servidor en ejecución](https://docs.spring.io/spring-boot/reference/testing/spring-boot-applications.html#testing.spring-boot-applications.with-running-server)

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

## Ejecuta las pruebas

Guarda los tres archivos y ejecuta este comando desde la raíz del proyecto.

```sh
mvn test
```

La ejecución usó JDK 21.0.1 y Maven 3.9.11. Tanto el Tomcat embebido como el servidor HTTP local que sustituía a la API externa se ejecutaron en puertos aleatorios. Las tres pruebas pasaron.

| Qué comprueba la prueba | Resultado observado |
| --- | --- |
| `GET /products/42` | `200 OK` con `Keyboard` en el cuerpo |
| `GET /products/99` | `404 Not Found` con un cuerpo vacío |
| `catalog.findName(99)` | Lanza `HttpClientErrorException.NotFound` |

```text
Tests run: 3, Failures: 0, Errors: 0, Skipped: 0
BUILD SUCCESS
```

Antes de migrar un proyecto, enumera los estados y cuerpos que comprueban tus pruebas actuales. Por ejemplo, un cliente que convierte el 404 de la API externa en un resultado vacío y un controlador que envía su propio 404 tienen contratos distintos. Prueba cada interfaz para detectar dónde cambia el comportamiento. Para comparar llamadas síncronas y reactivas, consulta [Comparación de WebClient y RestClient](/en/posts/2026-10-31-webclient-restclient-comparison/).
