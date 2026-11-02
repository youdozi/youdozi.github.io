---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2026-11-02-ai-assisted-tdd",
  "routeSlug": "2026-11-02-ai-assisted-tdd",
  "kind": "post",
  "title": "TDD con ayuda de IA: verifique Red, Green y Refactor con Java",
  "description": "Combine IA y TDD con pruebas basadas en requisitos, fallos previstos, implementaciones mínimas y refactorización. Ejemplos Java y JUnit detectan pruebas debilitadas y regresiones de límites.",
  "categories": [
    "architecture"
  ],
  "tags": [
    "ai-agent",
    "tdd",
    "java",
    "junit",
    "testing",
    "refactoring"
  ],
  "sourcePath": "src/content/posts/en/2026-11-02-ai-assisted-tdd.md",
  "sourceSha256": "bfc69c72419b9b2b5ce2693c4111b12dd8f935ed3d1115dd350b837bed13bf80",
  "draftSha256": "534f39cd74dae10370574db1c6e799988d16ca54481d7749ec7def363a2f7405",
  "manifestPath": ".pipeline/technical-translations/batch-132/manifest.json",
  "manifestSha256": "9061c67686c9ea3bd8d21799f4c265ee716fee50940f1b6fc38c28a67de01dee",
  "publishedAt": "2026-11-02T03:04:44.245Z",
  "updatedAt": "2026-11-02T03:04:44.245Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 132,
    "approvedAt": "2026-11-02T03:04:44.245Z",
    "basis": "User requested completing missing multilingual technical posts, review, verification and deployment, then instructed continuing the next task on 2026-11-02, with standing blog PR merge/publication authorization. Human approval denotes user publication authorization; linguistic review is AI, not human/native review."
  }
}
---

**Al combinar IA con TDD, derive los resultados esperados de los requisitos, observe una prueba fallida y repita pequeños pasos de implementación y refactorización.** La IA puede proponer pruebas e implementaciones, pero ambas pueden pasar compartiendo el mismo malentendido. Compruebe de dónde procede cada expectativa y qué informa realmente el ejecutor de pruebas.

El ciclo básico de TDD selecciona el siguiente comportamiento de una lista de pruebas y repite Red → Green → Refactor. [La explicación de TDD de Martin Fowler](https://www.martinfowler.com/bliki/TestDrivenDevelopment.html) destaca la lista, los ciclos pequeños y la refactorización. El ejemplo Java siguiente añade IA a este proceso sin depender de una herramienta concreta. Los prompts son ejemplos redactados para el artículo, no una transcripción de un producto de IA ni una medición de productividad.

## Defina el comportamiento esperado antes de mostrar una implementación

El ejemplo es una función pura que calcula el stock restante a partir del stock y la cantidad solicitada. Son requisitos ilustrativos, no la política de un servicio real. No actualiza una base de datos, persiste reservas ni proporciona atomicidad entre solicitudes concurrentes.

| Condición | Comportamiento esperado |
| --- | --- |
| Stock 10, solicitado 3 | Devolver 7 |
| Stock 10, solicitado 10 | Devolver 0 |
| La solicitud supera el stock, incluido solicitar 1 con stock 0 | `IllegalStateException("insufficient_stock")` |
| Stock negativo | `IllegalArgumentException("stock")` |
| Cantidad solicitada cero o negativa | `IllegalArgumentException("requested")` |
| Ambas entradas son inválidas | Validar primero el stock |
| Stock `Integer.MAX_VALUE`, solicitado 1 | Devolver `Integer.MAX_VALUE - 1` |

Esta tabla es el oráculo de pruebas. Leer una implementación generada por IA y copiar su valor de retorno en una aserción también puede copiar su error. Empiece por los requisitos y el contrato de API:

```text
No implemente nada todavía.
Proponga casos de prueba para StockPolicy.remaining(int stock, int requested).
Relacione cada entrada, resultado esperado o excepción con una regla de la tabla de requisitos.

No introduzca almacenamiento externo ni una base de datos.
Separe entradas normales, de límite e inválidas. En la primera iteración,
escriba solo una prueba: solicitar 3 con stock 10 devuelve 7.
No invente políticas cuando los requisitos no estén claros.
```

## Conecte Red, Green y Refactor mediante ejecuciones pequeñas

![Elegir la siguiente prueba de los requisitos, comprobar su fallo previsto, superarla con una implementación mínima, refactorizar conservando las pruebas y volver a la siguiente prueba](/assets/diagrams/technical/es-2026-11-02-ai-assisted-tdd.svg)

El diagrama describe un flujo controlado por el desarrollador, no el funcionamiento interno de la IA. Observe el fallo del nuevo comportamiento y añada una implementación mínima. Tras refactorizar, repita las mismas pruebas antes de elegir otro caso. Si el fallo procede de descargas de dependencias o del entorno, resuelva ese problema y repita la misma etapa.

El entorno de reproducción es **JDK 17.0.8.1, Gradle 8.4 y JUnit Jupiter 5.12.2**. Esta combinación fija registra el entorno utilizado; no recomienda versiones actuales de producción. Cree los archivos siguientes en un directorio vacío. La primera ejecución puede descargar dependencias de prueba de Maven Central; las pruebas no llaman a API externas ni bases de datos. En proyectos existentes, siga sus políticas de Gradle Wrapper y gestión de dependencias.

### `settings.gradle`

```groovy
rootProject.name = 'ai-tdd-stock'
```

### `build.gradle`

```groovy
plugins { id 'java' }
repositories { mavenCentral() }
dependencies {
    testImplementation platform('org.junit:junit-bom:5.12.2')
    testImplementation 'org.junit.jupiter:junit-jupiter'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
java {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
}
test {
    useJUnitPlatform()
    testLogging { events 'passed', 'failed' }
}
```

`@Test`, `assertEquals` y `assertThrows` de JUnit comprueban valores de retorno y excepciones. Capture el objeto de excepción para comprobar también su mensaje. Consulte la [guía de JUnit 5.12.2](https://docs.junit.org/5.12.2/user-guide/) y la [guía de pruebas JVM de Gradle](https://docs.gradle.org/current/userguide/java_testing.html).

### Primera prueba: `src/test/java/StockPolicyTest.java`

```java
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class StockPolicyTest {
    @Test
    void reservesPartOfStock() {
        assertEquals(7, StockPolicy.remaining(10, 3));
    }
}
```

### Primer Red: `src/main/java/StockPolicy.java`

Cree una API invocable con una implementación que aún no resta nada. Ejecute la prueba y verifique que falla porque esperaba `7` y recibió `10`.

```java
public class StockPolicy {
    public static int remaining(int stock, int requested) {
        return stock;
    }
}
```

Ejecute este comando desde la raíz del proyecto. En esta etapa se esperan un fallo de prueba y una salida distinta de cero.

```sh
gradle --no-daemon --console=plain clean test
```

Distinga errores de descarga o compilación de un fallo del comportamiento requerido. El Red previsto aquí es la discrepancia de la aserción de `reservesPartOfStock()`. Un ejecutor averiado no demuestra que se probara el comportamiento.

### Primer Green: sustituya el mismo `StockPolicy.java`

```java
public class StockPolicy {
    public static int remaining(int stock, int requested) {
        return stock - requested;
    }
}
```

Al repetir el mismo comando pasa la primera prueba. Esta implementación aún no trata entradas negativas ni stock insuficiente. Superar la primera prueba no completa la funcionalidad; añada el siguiente requisito.

Puede dar a la IA el siguiente límite de cambios:

```text
La prueba que falla es reservesPartOfStock: expected=7, actual=10.
Cambie solo StockPolicy.java para superar esta prueba.
No cambie pruebas, valores esperados ni configuración de compilación.
No añada una base de datos, interfaz o capa de configuración no solicitadas.
Informe del comando, código de salida y resultados de pruebas que comprobó realmente.
```

### Siguiente Red: añada métodos dentro de la clase de pruebas existente

Añada estos métodos **dentro** de la última llave de cierre de `StockPolicyTest`. En TDD real, añada un caso cada vez y repita el ciclo. El artículo agrupa los casos restantes en un bloque para mantener concisos los archivos de reproducción.

```java
    @Test
    void reservesAllStock() {
        assertEquals(0, StockPolicy.remaining(10, 10));
    }

    @Test
    void rejectsInsufficientStock() {
        var error = assertThrows(IllegalStateException.class,
                () -> StockPolicy.remaining(2, 3));
        assertEquals("insufficient_stock", error.getMessage());
    }

    @Test
    void rejectsEmptyStock() {
        var error = assertThrows(IllegalStateException.class,
                () -> StockPolicy.remaining(0, 1));
        assertEquals("insufficient_stock", error.getMessage());
    }

    @Test
    void rejectsNegativeStock() {
        var error = assertThrows(IllegalArgumentException.class,
                () -> StockPolicy.remaining(-1, 1));
        assertEquals("stock", error.getMessage());
    }

    @Test
    void rejectsZeroRequest() {
        var error = assertThrows(IllegalArgumentException.class,
                () -> StockPolicy.remaining(10, 0));
        assertEquals("requested", error.getMessage());
    }

    @Test
    void rejectsNegativeRequest() {
        var error = assertThrows(IllegalArgumentException.class,
                () -> StockPolicy.remaining(10, -1));
        assertEquals("requested", error.getMessage());
    }

    @Test
    void validatesStockBeforeRequest() {
        var error = assertThrows(IllegalArgumentException.class,
                () -> StockPolicy.remaining(-1, 0));
        assertEquals("stock", error.getMessage());
    }

    @Test
    void supportsMaximumStock() {
        assertEquals(Integer.MAX_VALUE - 1,
                StockPolicy.remaining(Integer.MAX_VALUE, 1));
    }
```

Ejecutar este bloque adicional con la primera implementación Green produce 6 fallos de 9 pruebas.

### Green de los casos adicionales: sustituya `StockPolicy.java`

```java
public class StockPolicy {
    public static int remaining(int stock, int requested) {
        if (stock >= 0) {
            if (requested > 0) {
                if (requested <= stock) {
                    return stock - requested;
                }
                throw new IllegalStateException("insufficient_stock");
            }
            throw new IllegalArgumentException("requested");
        }
        throw new IllegalArgumentException("stock");
    }
}
```

Use el mismo comando para verificar que pasan las 9 pruebas. La implementación ya satisface los comportamientos especificados. A continuación, simplifique las ramas anidadas conservando las pruebas.

### Refactor: use cláusulas de guarda en el mismo archivo

```java
public class StockPolicy {
    public static int remaining(int stock, int requested) {
        if (stock < 0) throw new IllegalArgumentException("stock");
        if (requested <= 0) throw new IllegalArgumentException("requested");
        if (requested > stock) throw new IllegalStateException("insufficient_stock");
        return stock - requested;
    }
}
```

Se reduce el anidamiento conservando el orden de validación, los valores de retorno y las excepciones. No introduzca una política nueva en esta etapa. Al pedir a la IA que refactorice, especifique el comportamiento que debe conservar y el alcance de ejecución:

```text
Actualmente pasan las 9 pruebas.
Sustituya solo las ramas anidadas de StockPolicy.java por cláusulas de guarda.
Conserve la validación de stock antes de la cantidad solicitada,
los valores de retorno, tipos de excepción, mensajes y pruebas existentes.
Ejecute la misma suite completa antes y después del cambio
e informe de los resultados y del diff.
```

Cada versión del código, desde el primer Red hasta Refactor, se ejecutó por separado. Los siguientes resultados se leyeron de los informes XML de JUnit:

| Etapa | Pruebas | Fallos | Omitidas | Código de salida de Gradle |
| --- | ---: | ---: | ---: | ---: |
| Primer Red | 1 | 1 | 0 | 1 |
| Primer Green | 1 | 0 | 0 | 0 |
| Red de casos adicionales | 9 | 6 | 0 | 1 |
| Green de casos adicionales | 9 | 0 | 0 | 0 |
| Refactor | 9 | 0 | 0 | 0 |

El informe HTML se genera en `build/reports/tests/test/index.html`; el XML legible por máquinas está en `build/test-results/test/`. Estos resultados verifican una función de política local. No miden la calidad de un producto de IA, la productividad ni la corrección del sistema de producción.

## Las pruebas y las implementaciones pueden equivocarse juntas

La **precedencia de validación** cuando el stock y la solicitud son inválidos queda fijada por `validatesStockBeforeRequest()`. Sin este caso, podría pasar inadvertida una regresión que invierta la precedencia de los mensajes de excepción. En vez de añadir solo ejemplos de entradas normales, compruebe que las reglas de la tabla de requisitos tienen pruebas correspondientes.

También puede comprobar que las pruebas detectan regresiones en los límites. Cambiar incorrectamente `requested > stock` por `requested >= stock` en la implementación final debería hacer fallar `reservesAllStock()`. Cambiar `requested <= 0` por `requested < 0` debería hacer fallar `rejectsZeroRequest()`. También se ejecutó una mutación que invertía el orden de validación y falló `validatesStockBeforeRequest()`. Las tres mutaciones se ejecutaron realmente; esto no garantiza detectar todos los defectos.

Para una revisión con ayuda de IA, proporcione de nuevo los requisitos originales y pregunte qué regla comprueba cada prueba. Otro agente puede repetir el mismo error si comparte los mismos requisitos incorrectos. Separar funciones y establecer de forma independiente el comportamiento esperado son cuestiones diferentes.

```text
Compare la tabla de requisitos original con las pruebas actuales.
No modifique todavía las pruebas ni la implementación.
Identifique reglas verificadas, reglas ausentes, límites y condiciones no observadas.
Compruebe si alguna prueba simplemente copió la salida de la implementación actual
como resultado esperado.
Para los cambios propuestos, relacione primero cada uno con su regla y evidencia.
```

## Evite que la IA debilite la verificación solo para superar las pruebas

Eliminar una prueba fallida, omitirla con `@Disabled`, ajustar expectativas a una implementación defectuosa o absorber todas las excepciones puede producir un resultado verde sin cumplir los requisitos. Cuando estos no cambien al refactorizar, conserve el comportamiento esperado. Si la propia prueba es incorrecta, establezca la política y la evidencia y distinga esa corrección de un cambio de implementación. [La guía de GitHub para revisar código generado por IA](https://docs.github.com/en/copilot/tutorials/review-ai-generated-code) también recomienda buscar pruebas eliminadas u omitidas y discrepancias con los requisitos previstos.

Distinga la afirmación de la IA de que las pruebas pasaron de los resultados del ejecutor. Inspeccione el comando real, el código de salida, los informes JUnit y el diff. Cero pruebas ejecutadas o una ejecución parcial no constituyen un éxito completo. En CI, ejecute la implementación final y la suite completa con condiciones normales de éxito. Mantenga el arnés educativo que verifica los fallos Red previstos separado del CI normal y no haga pasar CI ignorando incondicionalmente comandos fallidos.

Para código existente, obtenga primero pruebas que capturen el comportamiento actual y después elija un comportamiento que cambiar. Esta secuencia y sus criterios de conservación se relacionan con la [refactorización con agentes de IA](/en/posts/2026-10-31-ai-agent-refactoring/). Las pruebas y compilaciones también ejecutan código, así que limite directorios y credenciales como explica [Límites de permisos de agentes de IA](/en/posts/2026-11-01-ai-agent-permission-boundaries/).

Extender este ejemplo a reservas reales de stock requiere pruebas de integración aparte para solicitudes concurrentes, transacciones, solicitudes duplicadas y reintentos. Superar estas 9 pruebas unitarias de función no demuestra protección contra la sobreventa.
