---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2023-09-10-springboot-intellij-import",
  "routeSlug": "2023-09-10-springboot-intellij-import",
  "kind": "post",
  "title": "Abrir y ejecutar un proyecto Gradle de Spring Boot en IntelliJ IDEA",
  "description": "Comprueba sincronización Gradle, SDK y ejecución en IntelliJ IDEA; usa después el Wrapper y pruebas HTTP para separar errores del proyecto y del IDE.",
  "categories": [
    "springboot"
  ],
  "tags": [
    "springboot",
    "intellij community",
    "project import",
    "RUN/DEBUG configurations"
  ],
  "sourcePath": "src/content/posts/en/2023-09-10-springboot-intellij-import.md",
  "sourceSha256": "5b3c970364e92d3672967197986ea67769f45094ca27f6c9f8bfbd0779645bc2",
  "draftSha256": "15a87fdcf9abbad2dfa84a2119ab72a77383116150bf62ccb3ede16ce75bafac",
  "manifestPath": ".pipeline/technical-translations/batch-125/manifest.json",
  "manifestSha256": "1934910c02dbe893b786124f1d296d7adf9efbe921d40b3d2cfbceb8f70b4b33",
  "publishedAt": "2026-10-31T15:35:43.034Z",
  "updatedAt": "2026-10-31T15:35:43.034Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 125,
    "approvedAt": "2026-10-31T15:35:43.034Z",
    "basis": "User explicitly requested applying all missing technical-post languages, review, verification and deployment on 2026-11-01, with standing PR merge authorization. Human approval denotes publication authorization; linguistic review is performed by AI, not human/native review."
  }
}
---

Al abrir un proyecto Spring Boot en IntelliJ, comprueba primero la sincronización Gradle y compara la compilación del Wrapper con la ejecución del IDE. Una ausencia del botón de ejecución no siempre exige configuración manual. También puedes ejecutar un main Java válido desde el [icono del margen del editor](https://www.jetbrains.com/help/idea/running-applications.html).

Esta guía continúa el [ejemplo Initializr](/en/posts/2023-09-07-springboot-initializer/) con Boot 4.1.2, Gradle 9.8.2 y Java 17. La compilación y el comportamiento HTTP se ejecutaron localmente; los pasos del IDE se contrastaron con documentación de JetBrains. No se afirma una verificación práctica de la interfaz de una versión concreta del IDE.

## Flujo de procesamiento

![Flujo para separar fallos de compilación y del IDE](/assets/diagrams/technical/es-2023-09-10-springboot-intellij-import.svg)

Usa la compilación del Wrapper para distinguir fallos del proyecto y configuración del IDE. Las pruebas HTTP usan un puerto aleatorio; bootRun manual usa el configurado.

## Comprobar el proyecto y JDK

1. Usa File → Open en la raíz extraída que contiene `settings.gradle` y `build.gradle`.
2. Completa la sincronización Gradle. Resuelve primero fallos de descarga de dependencias o sincronización.
3. Selecciona la distribución Wrapper del proyecto y comprueba Gradle JVM y Project SDK. Aquí ambos usan JDK 17.
4. Ejecuta `./gradlew --version` y `./gradlew test` en un terminal para obtener un resultado fuera del IDE.

Consulta la [guía de integración Gradle](https://www.jetbrains.com/help/idea/gradle.html) y las [reglas de selección de Gradle JVM](https://www.jetbrains.com/help/idea/gradle-jvm-selection.html). Los menús varían según la versión del IDE y el sistema. Project SDK, la JVM de Gradle, la toolchain Java y el JRE de ejecución son ajustes distintos que no siempre coinciden automáticamente.

## Añadir un endpoint y pruebas HTTP reales

Conserva los cuatro archivos existentes y añade estos dos. Colocar el controlador en el paquete `example.demo` de la aplicación lo mantiene dentro del escaneo de componentes.

### `src/main/java/example/demo/GreetingController.java`

```java
package example.demo;

import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class GreetingController {
    @GetMapping("/greeting")
    public Map<String, String> greeting() {
        return Map.of("message", "Hello, Gradle");
    }
}
```

### `src/test/java/example/demo/GreetingHttpTest.java`

```java
package example.demo;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.core.env.Environment;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class GreetingHttpTest {
    @Autowired Environment environment;

    HttpResponse<String> get(String path) throws Exception {
        String port = environment.getRequiredProperty("local.server.port");
        var request = HttpRequest.newBuilder(URI.create("http://127.0.0.1:" + port + path))
                .timeout(Duration.ofSeconds(10)).GET().build();
        return HttpClient.newHttpClient().send(request, HttpResponse.BodyHandlers.ofString());
    }

    @Test
    void greetingReturnsJson() throws Exception {
        var response = get("/greeting");
        assertEquals(200, response.statusCode());
        assertTrue(response.headers().firstValue("content-type").orElse("").contains("application/json"));
        assertEquals("{\"message\":\"Hello, Gradle\"}", response.body());
    }

    @Test
    void missingPathIsNotAnApplicationStartupFailure() throws Exception {
        assertEquals(404, get("/missing").statusCode());
    }
}
```

`./gradlew test` ejecuta ahora la prueba de contexto existente y dos pruebas HTTP. Estas arrancan un servidor real en un puerto aleatorio y comprueban JSON y la respuesta 404 de una ruta ausente. No necesitan que el puerto local 8080 esté libre.

## Comparar la ejecución Gradle y Application

Arranca el servidor con el primer comando y ejecuta después el segundo en otro terminal.

```sh
./gradlew bootRun --args='--server.port=8081'
```

```sh
curl --fail --show-error http://localhost:8081/greeting
```

```json
{"message":"Hello, Gradle"}
```

En el IDE, prueba primero el icono junto a `DemoApplication.main()`. Si necesitas configuración explícita, crea una de tipo Application en Run → Edit Configurations y comprueba estos valores.

| Ajuste | Ejemplo |
| --- | --- |
| Main class | `example.demo.DemoApplication` |
| Classpath module | Módulo fuente principal, como `demo.main` |
| JRE | JDK 17 |
| Program arguments | `--server.port=8081` |

Si otro proceso ocupa 8081, detenlo o elige otro puerto. La disponibilidad de ventanas o configuraciones específicas de Boot es independiente de ejecutar una configuración Java Application normal.

| Observación | Primera comprobación |
| --- | --- |
| También falla la compilación Wrapper | Compatibilidad JDK/Gradle, dependencias y errores de código |
| Wrapper pasa pero el IDE falla | Recarga Gradle, classpath del módulo, JRE y argumentos |
| El servidor arranca pero `/greeting` devuelve 404 | Paquete del controlador y ruta de mapeo |
| Fallo por puerto ocupado | Procesos e instancias existentes |

Si compila pero el IDE marca errores en métodos generados, continúa con las [comprobaciones de Lombok y procesadores de anotaciones](/en/posts/2023-09-15-springboot-intellij-lombok/).
