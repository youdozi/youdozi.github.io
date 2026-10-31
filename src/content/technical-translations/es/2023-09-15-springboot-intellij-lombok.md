---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2023-09-15-springboot-intellij-lombok",
  "routeSlug": "2023-09-15-springboot-intellij-lombok",
  "kind": "post",
  "title": "Corregir Lombok en IntelliJ: separar compilación Gradle y soporte del IDE",
  "description": "Configura Lombok para procesar anotaciones main y test, verifica los métodos generados y distingue fallos de compilación del reconocimiento del IDE.",
  "categories": [
    "springboot"
  ],
  "tags": [
    "springboot",
    "intellij community",
    "lombok"
  ],
  "sourcePath": "src/content/posts/en/2023-09-15-springboot-intellij-lombok.md",
  "sourceSha256": "9fe45995bdaea610316410d2b79746c008656c5d20256f9de7d66bc47499dda1",
  "draftSha256": "d82abb5e1ec89d4b96c2bea28280b18eb35ccabe6b04777b10d7213abbbd8a78",
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

Si parecen faltar métodos Lombok, ejecuta primero `./gradlew clean test` para saber si también falla la compilación. El soporte del IDE reconoce los miembros generados en el editor; el procesador de Gradle los genera al compilar. Ninguno sustituye al otro.

Este ejemplo continúa el [proyecto Initializr](/en/posts/2023-09-07-springboot-initializer/) y el [ejemplo HTTP](/en/posts/2023-09-10-springboot-intellij-import/). Usa Boot 4.1.2, Gradle 9.8.2 y JDK 17; el BOM seleccionó Lombok 1.18.48. Registra una combinación funcional sin garantizar todas las parejas JDK/Lombok.

## Flujo de procesamiento

![Compilar Lombok antes de corregir el IDE](/assets/diagrams/technical/es-2023-09-15-springboot-intellij-lombok.svg)

Comprueba constructores y getters generados por separado en main y test. Corrige el reconocimiento del IDE después de pasar las pruebas Wrapper.

## Configurar la compilación Gradle

Añade este bloque al `build.gradle` existente, evitando declaraciones duplicadas si ya existen.

```groovy
dependencies {
    compileOnly 'org.projectlombok:lombok'
    annotationProcessor 'org.projectlombok:lombok'
    testCompileOnly 'org.projectlombok:lombok'
    testAnnotationProcessor 'org.projectlombok:lombok'
}
```

La [configuración oficial Gradle](https://projectlombok.org/setup/gradle) separa dependencias de compilación y procesadores main y test. Las dos declaraciones de pruebas solo son necesarias si las fuentes de prueba usan anotaciones Lombok. Las pruebas siguientes también ejercitan esa ruta.

Las declaraciones sin versión funcionan porque el proyecto aplica el plugin Boot y `io.spring.dependency-management`, que [importa el BOM de Boot](https://docs.spring.io/spring-boot/4.1/gradle-plugin/managing-dependencies.html). En un proyecto Gradle normal, usa la misma versión explícita compatible en las declaraciones necesarias o configura aparte la gestión de dependencias para esas configuraciones.

## Usar el constructor y getter generados

Añade `Greeting`, sustituye el controlador por esta versión, conserva las pruebas HTTP y añade la clase de pruebas específica de Lombok.

### `src/main/java/example/demo/Greeting.java`

```java
package example.demo;

import lombok.Getter;
import lombok.RequiredArgsConstructor;

@Getter
@RequiredArgsConstructor
public class Greeting {
    private final String message;
}
```

### `src/main/java/example/demo/GreetingController.java`

```java
package example.demo;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class GreetingController {
    @GetMapping("/greeting")
    public Greeting greeting() {
        return new Greeting("Hello, Gradle");
    }
}
```

### `src/test/java/example/demo/LombokGenerationTest.java`

```java
package example.demo;

import lombok.Getter;
import lombok.RequiredArgsConstructor;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class LombokGenerationTest {
    @Getter
    @RequiredArgsConstructor
    static class Expected {
        private final String message;
    }

    @Test
    void mainSourceConstructorAndGetterAreGenerated() {
        assertEquals("Hello, Gradle", new Greeting("Hello, Gradle").getMessage());
    }

    @Test
    void testSourceConstructorAndGetterAreGenerated() {
        assertEquals("test fixture", new Expected("test fixture").getMessage());
    }
}
```

```sh
./gradlew clean test bootJar
./gradlew dependencyInsight --configuration annotationProcessor --dependency lombok
```

Hay ahora cinco pruebas: una de contexto, dos HTTP y dos de generación Lombok. Llaman a constructores y getters generados en fuentes principales y de prueba. `/greeting` debe seguir devolviendo el mismo JSON, comprobando también la serialización mediante el getter generado.

Como Lombok es `compileOnly`, el JAR ejecutable no lo incluye como biblioteca de ejecución. Instalar solo un plugin IDE no hace pasar Gradle. No se necesita añadir Lombok como dependencia de ejecución `implementation` para usar el getter ya compilado en esta configuración.

## Cuando solo el IDE muestra errores

Si pasan las pruebas Wrapper, recarga el proyecto Gradle. [JetBrains documenta](https://www.jetbrains.com/help/idea/annotation-processors-support.html) que importar procesadores desde archivos de compilación activa automáticamente las anotaciones. Cambiar manualmente una casilla no es un paso obligatorio universal.

Comprueba después el soporte Lombok y la activación del plugin de tu versión IDE con la [guía Lombok para IntelliJ](https://projectlombok.org/setup/intellij). No generalices que una edición siempre necesita instalación manual y otra siempre lo incluye. Determina también si el IDE usa su compilador o delega en Gradle.

Si Gradle también falla por miembros ausentes, busca `compileOnly` sin `annotationProcessor`. Si solo fallan las pruebas, inspecciona las dos configuraciones de test. El verificador confirma el fallo al retirar por separado el procesador principal o el de pruebas, los restaura y verifica que vuelven a pasar las cinco pruebas. La interacción con la interfaz IDE queda fuera de esas comprobaciones.
