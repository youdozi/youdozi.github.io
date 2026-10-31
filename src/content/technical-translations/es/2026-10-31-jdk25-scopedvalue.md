---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2026-10-31-jdk25-scopedvalue",
  "routeSlug": "2026-10-31-jdk25-scopedvalue",
  "kind": "post",
  "title": "ScopedValue de JDK 25: contexto de solicitud más allá de ThreadLocal",
  "description": "Ejecuta la API definitiva ScopedValue en hilos virtuales. Observa enlaces anidados, restauración tras excepciones y ausencia de herencia en un hilo hijo ordinario, con límites claros respecto a ThreadLocal y la concurrencia estructurada.",
  "categories": [
    "jdk"
  ],
  "tags": [
    "java",
    "jdk25",
    "scopedvalue",
    "threadlocal",
    "virtual-threads"
  ],
  "sourcePath": "src/content/posts/en/2026-10-31-jdk25-scopedvalue.md",
  "sourceSha256": "b1b2085e75caffb25a2838a9d99da8e4b63dd107657a94ad5e08730bb04fbf66",
  "draftSha256": "eddffa4d1d526647f890976034555329211cd0a4af415e907690bd559370619a",
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
En JDK 25, **`ScopedValue` es una API definitiva para vincular datos como el contexto de una solicitud a un ámbito de ejecución delimitado y pasarlos de los llamadores a los métodos llamados**. Se hizo definitiva mediante [JEP 506](https://openjdk.org/jeps/506), por lo que no se necesitan opciones de funciones preliminares. Un enlace se aplica mientras se ejecuta la operación proporcionada a `run()` o `call()`; la finalización normal o una excepción restaura el estado anterior.

## ¿En qué se diferencia de ThreadLocal?

Considérala cuando pasar un identificador de inquilino o de traza hasta lo más profundo del código del servicio exigiría añadir un parámetro a cada método intermedio. Los parámetros ordinarios pueden seguir siendo más claros cuando el valor es una entrada explícita de la lógica de negocio.

[`ThreadLocal`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/ThreadLocal.html) cambia el valor del hilo actual mediante `set()` y lo elimina mediante `remove()`. Su uso con alcance de solicitud requiere una limpieza cuidadosa, normalmente en `finally`. En lugar de dejar un valor establecido, `ScopedValue` ejecuta la operación que lo necesita dentro de un enlace.

| Comparación | ThreadLocal | ScopedValue |
| --- | --- | --- |
| Acceso a datos | Leer y cambiar un valor almacenado para el hilo actual | Leer el enlace en el ámbito dinámico de ejecución actual |
| Fin del ámbito | Gestionar explícitamente la limpieza con alcance de solicitud | Restaurar el enlace anterior cuando termina `run()` o `call()` |
| Valor distinto en un método llamado | `set()` puede cambiar el valor almacenado existente | Crear un enlace nuevo en un ámbito anidado y restaurar después el valor exterior |
| Usos adecuados | Estado mutable por hilo, entre otros | Contexto de solicitud pasado de los llamadores a los métodos llamados, entre otros |

`ScopedValue` no sustituye todos los usos de `ThreadLocal` ni lo marca como obsoleto. Un campo `private static final` almacena **una clave de acceso, no el propio valor del contexto**. La misma clave puede resolverse a valores distintos según el hilo y el ámbito en ejecución.

## Observar el ámbito y la restauración en un hilo virtual

![Vincular un valor exterior en un hilo virtual, restaurarlo tras una ejecución anidada y un fallo, comprobar la ausencia de herencia en un hilo hijo ordinario y salir del ámbito](/assets/diagrams/technical/es-2026-10-31-jdk25-scopedvalue.svg)

El diagrama sigue el ejemplo siguiente. El inquilino exterior es `tenant-a`; el ámbito anidado lee `tenant-b`. El fallo de un ámbito anidado se captura fuera de ese ámbito antes de comprobar la restauración. Este ejemplo demuestra la semántica del contexto de solicitud sin servidor HTTP ni integración con un framework.

Ejecútalo en un directorio donde `javac` y `java` apunten a la misma instalación de JDK 25. El entorno de verificación local fue Eclipse Temurin `25.0.5+8` en macOS AArch64. `ScopedValue` pertenece a `java.lang` y no necesita una importación explícita.

### `ScopedContextExample.java`

```java
import java.util.NoSuchElementException;
import java.util.concurrent.Executors;

public class ScopedContextExample {
    private static final ScopedValue<RequestContext> CONTEXT = ScopedValue.newInstance();
    record RequestContext(String tenant, String traceId) {}

    public static void main(String[] args) throws Exception {
        try (var tasks = Executors.newVirtualThreadPerTaskExecutor()) {
            tasks.submit(ScopedContextExample::handleRequest).get();
        }
    }

    private static String handleRequest() throws InterruptedException {
        System.out.println("virtual=" + Thread.currentThread().isVirtual());
        System.out.println("before=" + CONTEXT.isBound());
        String result = ScopedValue.where(CONTEXT,
                new RequestContext("tenant-a", "trace-123")).call(() -> {
            System.out.println("outer=" + service());
            ScopedValue.where(CONTEXT,
                    new RequestContext("tenant-b", "trace-123")).run(() ->
                System.out.println("nested=" + service()));
            System.out.println("restored=" + service());

            try {
                ScopedValue.where(CONTEXT,
                        new RequestContext("tenant-fail", "trace-123")).run(() -> {
                    throw new IllegalStateException("demonstration");
                });
            } catch (IllegalStateException expected) {
                System.out.println("after-failure=" + service());
            }

            Thread child = Thread.ofVirtual().start(() ->
                System.out.println("plain-child-bound=" + CONTEXT.isBound()));
            child.join();
            return service();
        });
        System.out.println("result=" + result);
        System.out.println("after=" + CONTEXT.isBound());
        try {
            CONTEXT.get();
        } catch (NoSuchElementException expected) {
            System.out.println("outside=" + expected.getClass().getSimpleName());
        }
        return result;
    }

    private static String service() {
        RequestContext context = CONTEXT.get();
        return context.tenant() + "/" + context.traceId();
    }
}
```

```sh
javac --release 25 ScopedContextExample.java
java ScopedContextExample
```

Esta salida estándar se observó sin opciones de funciones preliminares. Llamar a `get()` en el `Future` propaga los fallos de la tarea al llamador; `join()` espera la salida del hilo hijo.

```text
virtual=true
before=false
outer=tenant-a/trace-123
nested=tenant-b/trace-123
restored=tenant-a/trace-123
after-failure=tenant-a/trace-123
plain-child-bound=false
result=tenant-a/trace-123
after=false
outside=NoSuchElementException
```

`service()` lee el enlace actual sin un parámetro de contexto. Utiliza `run()` para una operación sin resultado y [`Carrier.call()`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/ScopedValue.Carrier.html#call(java.lang.ScopedValue.CallableOp)) para una operación que devuelve un resultado o propaga una excepción. Crear simplemente un `Carrier` con `where()` no activa un enlace.

Tanto `restored` como `after-failure` muestran el valor exterior. Después de que termine el `call()` exterior, `isBound()` es false y un `get()` sin enlace lanza `NoSuchElementException`. Salir de un enlace no garantiza la recolección inmediata de basura del objeto referenciado ni cierra automáticamente un recurso `AutoCloseable`.

## ¿Crear un hilo virtual hereda el valor?

**Un `Thread.ofVirtual().start()` ordinario no hereda automáticamente el enlace de su padre.** El ejemplo lo demuestra con `plain-child-bound=false`. Tampoco supongas que entregar trabajo a un `ExecutorService` o a `CompletableFuture` propaga automáticamente el contexto. El primer hilo virtual del ejemplo establece su enlace dentro de la tarea en lugar de heredarlo.

Las [reglas oficiales de herencia](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/ScopedValue.html#inheritance) describen la captura de enlaces al crear un `StructuredTaskScope` y su herencia en los hijos iniciados mediante el `fork()` de ese ámbito. **La concurrencia estructurada es una API preliminar independiente en JDK 25**, descrita en [JEP 505](https://openjdk.org/jeps/505), y no se utiliza en el código de este artículo. No interpretes que el ejemplo verifica ese mecanismo de herencia.

## Límites al adoptar el contexto de solicitud

Un enlace inmodificable no vuelve inmutable en profundidad al objeto referenciado. El ejemplo utiliza un record con dos cadenas; una colección mutable requeriría un diseño de concurrencia independiente. Restringe también el acceso a la clave.

Consulta la API de JDK 25 en lugar de copiar sin cambios ejemplos preliminares antiguos de JDK 21 y versiones similares. En particular, JDK 25 no permite `orElse(null)`. Un enlace a `null` también es distinto de no tener enlace.

Distingue primero un `ThreadLocal` que pasa datos de solicitud por la cadena de llamadas de otro que mantiene estado mutable durante la ejecución. Para el primero, diseña tanto el enlace en el punto de entrada como los límites asíncronos. Las transacciones del framework, MDC y el contexto de seguridad no se conectan automáticamente; este ejemplo no verifica esas integraciones ni el rendimiento. Continúa con el [artículo sobre funciones de JDK 21](/en/posts/2023-09-20-jdk-21-release/) para conocer el comportamiento de los propios hilos virtuales.
