---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2026-10-31-cache-aside",
  "routeSlug": "2026-10-31-cache-aside",
  "kind": "post",
  "title": "Diseño de caché API: claves, TTL, invalidación y protección del origen",
  "description": "Explica ubicación, claves, TTL, invalidación y fallos de caché simultáneos con Cache-Aside. Comprueba caducidad y capacidad con Java y define cómo proteger la base si falla la caché.",
  "categories": [
    "architecture"
  ],
  "tags": [
    "caching",
    "cache-aside",
    "ttl",
    "cache-invalidation",
    "java",
    "resilience"
  ],
  "sourcePath": "src/content/posts/en/2026-10-31-cache-aside.md",
  "sourceSha256": "2c4422c55f14e7b5452f8b286bf5d6f986617fe624e229b7bd74462afe525ad9",
  "draftSha256": "353ab8835dcf70bae1b3bd354e02cc3b9ab95c9d8a0f5aa835db31c4bb887709",
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

**La caché reutiliza resultados anteriores para reducir lecturas del origen y cálculos.** Para aplicarla correctamente, define qué solicitudes pueden compartir resultado, cuánto tiempo se permite reutilizarlo y cómo actualizarlo cuando cambia el origen. Muchos aciertos no hacen correcta una caché que devuelve datos ajenos o usa un precio antiguo para finalizar una compra.

El artículo se dirige a desarrolladores que valoran una caché para una API de lectura. Explica Cache-Aside con datos que toleran retraso, como descripciones de productos, y ejecuta TTL y límites de capacidad en Java. Operaciones que requieren estado actual, como confirmar pagos o existencias, quedan separadas. Las políticas de datos antiguos durante fallos conectan con el [artículo de fallback](/ko/posts/2026-10-31-failure-fallback/).

## ¿Qué guardar en caché y dónde?

Empieza por rutas con lecturas repetidas, origen costoso y tolerancia temporal a respuestas antiguas. Datos usados una vez o casi completamente distintos por usuario pueden costar más en almacenamiento e invalidación de lo que ahorran.

| Ubicación | Costes que reduce | Condiciones por definir |
| --- | --- | --- |
| Caché HTTP del navegador o CDN | Viajes de red y solicitudes que llegan a la API | Si puede compartirse, URL y `Vary`, `Cache-Control` |
| Caché local de aplicación | Viajes a caché remota, lecturas DB, cálculos repetidos | Memoria por proceso, diferencias entre réplicas |
| Caché compartida como Redis | Lecturas repetidas del origen entre réplicas | Latencia de red, fallos, serialización, capacidad |

No necesitas todas las capas a la vez. La local es rápida, pero cada réplica mantiene una copia distinta. La compartida reduce duplicación, pero añade dependencia de red y operación. Con varias capas, la invalidación debe alcanzar todas.

## ¿Cómo funciona Cache-Aside?

La aplicación consulta primero la caché. Si falta la entrada o caducó, lee el origen y guarda el resultado. Es **Cache-Aside**. Las escrituras suelen confirmar el origen antes de invalidar la entrada correspondiente. Los datos sobreviven a perder la caché; difiere de usarla como único registro. [Explicación Microsoft de Cache-Aside](https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside)

La clave debe incluir entradas que cambian el resultado. Por ejemplo, `Key(tenant, product, language)` representa entradas distintas por tenant, producto e idioma. Si moneda, permisos o versión del formato cambian la respuesta, separa claves o ámbito. Concatenar sin separadores puede provocar colisiones: usa claves estructuradas o codificación inequívoca.

Incluir el ID del tenant no completa la autorización. Determínalo desde un contexto de autenticación fiable y comprueba acceso antes de consultar. No pongas tokens ni contraseñas directamente en claves o logs.

**TTL es el tiempo de reutilización; capacidad es cuánto puede guardarse.** Solo con TTL pueden acumularse entradas hasta caducar. Solo con límite de tamaño pueden seguir acertando valores antiguos. Número de entradas y bytes difieren: considera tamaño de objetos y serialización para respuestas grandes.

## Ejemplo Java: separar claves, caducidad, invalidación y capacidad

El código es una pequeña **demostración de semántica de caché local** para descripciones por tenant. TTL de 5 segundos y máximo de 2 entradas muestran comportamiento, no son recomendaciones productivas. Usa el orden de acceso `LinkedHashMap` para expulsar primero la menos recientemente consultada. [Documentación Java 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/LinkedHashMap.html)

![Devolver la entrada dentro del TTL; si falta o caduca, leer origen, guardar solo el valor correcto, expulsar el exceso y devolver](/assets/diagrams/technical/es-2026-10-31-cache-aside.svg)

El diagrama muestra `get()`. Si falla el cargador, propaga la excepción y no guarda valor nuevo. `invalidate()` es una operación separada tras cambiar el origen.

Guarda como `CacheDemo.java` y ejecuta con JDK 21 o posterior. No requiere servidor ni biblioteca externa.

```java
import java.time.Duration;
import java.util.LinkedHashMap;
import java.util.Objects;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Function;
import java.util.function.LongSupplier;

public class CacheDemo {
    record Key(String tenant, String product, String language) {}
    record Entry(String value, long loadedAt) {}

    static final class LocalCache {
        private final LinkedHashMap<Key, Entry> entries =
                new LinkedHashMap<>(16, 0.75f, true);
        private final LongSupplier ticker;
        private final long ttl = Duration.ofSeconds(5).toNanos();
        private final int maximumSize = 2;

        LocalCache(LongSupplier ticker) { this.ticker = ticker; }

        synchronized String get(Key key, Function<Key, String> loader) {
            Entry entry = entries.get(key);
            long now = ticker.getAsLong();
            if (entry != null && now - entry.loadedAt() < ttl) {
                return entry.value();
            }
            entries.remove(key);
            String value = Objects.requireNonNull(loader.apply(key));
            entries.put(key, new Entry(value, ticker.getAsLong()));
            if (entries.size() > maximumSize) {
                entries.remove(entries.keySet().iterator().next());
            }
            return value;
        }

        synchronized void invalidate(Key key) { entries.remove(key); }
    }

    static void expect(String actual, String expected) {
        if (!actual.equals(expected)) throw new AssertionError(actual);
        System.out.println(actual);
    }

    public static void main(String[] args) {
        AtomicLong clock = new AtomicLong();
        AtomicInteger loads = new AtomicInteger();
        LocalCache cache = new LocalCache(clock::get);
        Function<Key, String> loader = key ->
                key.tenant() + "/" + key.language() + "/v" + loads.incrementAndGet();
        Key ko = new Key("shop-a", "p1", "ko");
        Key en = new Key("shop-a", "p1", "en");
        Key other = new Key("shop-b", "p1", "ko");

        expect(cache.get(ko, loader), "shop-a/ko/v1");
        expect(cache.get(ko, loader), "shop-a/ko/v1");
        clock.set(Duration.ofSeconds(5).toNanos() - 1);
        expect(cache.get(ko, loader), "shop-a/ko/v1");
        clock.incrementAndGet();
        expect(cache.get(ko, loader), "shop-a/ko/v2");
        cache.invalidate(ko);
        expect(cache.get(ko, loader), "shop-a/ko/v3");
        expect(cache.get(en, loader), "shop-a/en/v4");
        expect(cache.get(ko, loader), "shop-a/ko/v3");
        expect(cache.get(other, loader), "shop-b/ko/v5");
        expect(cache.get(en, loader), "shop-a/en/v6");

        Key failing = new Key("shop-c", "p1", "ko");
        try {
            cache.get(failing, key -> { throw new IllegalStateException("origin"); });
            throw new AssertionError("Failure was swallowed");
        } catch (IllegalStateException expected) {
            expect(expected.getMessage(), "origin");
        }
        expect(cache.get(failing, loader), "shop-c/ko/v7");
    }
}
```

```sh
javac --release 21 CacheDemo.java
java CacheDemo
```

La salida siguiente se obtuvo con Zulu JDK `21.0.1+12-LTS`.

```text
shop-a/ko/v1
shop-a/ko/v1
shop-a/ko/v1
shop-a/ko/v2
shop-a/ko/v3
shop-a/en/v4
shop-a/ko/v3
shop-b/ko/v5
shop-a/en/v6
origin
shop-c/ko/v7
```

Las tres primeras lecturas de la misma clave leen el origen una vez. A 1ns de caducar devuelve lo mismo; exactamente a 5 segundos vuelve a cargar. Los casos siguientes comprueban invalidación explícita, separación por idioma y tenant y expulsión por acceso. Incluyen lectura correcta tras fallo del cargador. Valores como `v1` indican orden de llamadas de prueba, no versiones DB reales.

El tiempo usa un contador monótono avanzado manualmente, sin dormir. En un proceso real puedes proporcionar un temporizador transcurrido con `new LocalCache(System::nanoTime)`. Las entradas caducadas se tratan al acceder, no se borran inmediatamente en segundo plano. Limita entradas, no bytes.

Para mantenerlo pequeño, el cargador ejecuta dentro de `synchronized`. Las llamadas a la misma instancia se serializan incluso con claves distintas, sin límite de solicitudes esperando. No es una caché productiva de alto rendimiento. No implementa single-flight por clave, límites de origen, timeouts ni propagación entre réplicas descritos después. Las comprobaciones son secuenciales; no hubo prueba de carga concurrente.

## ¿Garantizan TTL e invalidación valores actuales?

No. Aquí el TTL empieza **al terminar la lectura y guardar en caché**. Si el origen es una réplica retrasada o una instantánea antigua, TTL de 5 segundos no significa ver lo último en 5 segundos desde el cambio. Considera aparte latencia de lectura, replicación e invalidación.

Con varias réplicas y caché común puede haber una carrera aun actualizando DB y borrando después. A empieza a leer lo antiguo; B confirma lo nuevo y borra; A termina tarde y vuelve a guardarlo. TTL reduce su permanencia, no elimina la carrera.

Las rutas que exigen actualidad deben revalidar en la transacción del origen o impedir que resultados tardíos sobrescriban los nuevos, por ejemplo con versiones y escritura condicional. Si invalidas por eventos, trata pérdida, duplicación y retraso entre commit y entrega. Si afecta a varias claves, como listas, detalles y agregados, define su ámbito de invalidación.

Distingue `expire-after-write` y `expire-after-access`. Renovar en cada acceso puede conservar mucho tiempo valores antiguos frecuentes. Para revalidar tras un tiempo fijo desde el almacenamiento sin depender de lecturas, valora caducidad desde escritura. [Políticas Caffeine](https://github.com/ben-manes/caffeine/wiki/Eviction)

## ¿Qué ocurre al caducar todo o fallar la caché?

Si todas las solicitudes leen el origen al caducar una clave popular, puede haber **cache stampede**. Usa single-flight para reunir lecturas de una clave en una operación y limita concurrencia y espera del origen. Deduplicar un proceso no cubre todas las réplicas. Considera las [API atómicas de consulta y carga Caffeine](https://github.com/ben-manes/caffeine/wiki/Population), que solas no fijan un límite global.

El jitter distribuye caducidades de muchas claves. Si el límite es 60 segundos, distribuye sin superar 60 segundos. No resuelve la concentración sobre una clave popular. Aplica stale-while-revalidate, que devuelve lo antiguo mientras actualiza, solo donde se permita y fija una edad máxima separada si persisten los fallos.

Enviar todo a DB al fallar también es peligroso. Como ejemplo, con 10,000 RPS y 90% de aciertos, el origen recibe unos 1,000 RPS. Perder todos los aciertos lo eleva a 10,000 RPS con igual distribución. Es un cálculo, no una medida, y excluye reintentos y actualizaciones.

Si el origen no soporta eso, limita desvíos, usa copias locales permitidas o funcionalidad reducida, o rechaza excesos. Observa fallos aparte de misses y limita recargas masivas. Una caché negativa breve ayuda con ID inexistentes repetidos, pero no guardes un fallo como «sin datos». Define su TTL e invalidación para permitir leer datos nuevos.

## Separar caché HTTP y de aplicación

La caché HTTP del navegador y CDN comunica reutilización mediante cabeceras. Es una capa separada del TTL de objetos JVM.

| Directiva | Significado |
| --- | --- |
| `max-age=60` | La respuesta es fresca con edad inferior a 60 segundos |
| `s-maxage=60` | Vigencia en cachés compartidas, sustituyendo `max-age` y ajustes relacionados |
| `private` | Restringe almacenamiento compartido; uno privado como navegador puede guardar |
| `no-cache` | Permite guardar, pero exige validación correcta del origen antes de reutilizar |
| `no-store` | Ordena no guardar esta solicitud o respuesta; no borra copias existentes |

Si eliges idioma con `Accept-Language`, `Vary` y la configuración real deben reflejarlo. Si lo separa la URL, forma parte de la clave. `ETag` y solicitudes condicionales reducen transferencia sin cambios, pero no siempre validación del origen. `private` y `no-store` no sustituyen autenticación, autorización ni cifrado. [RFC 9111: HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111.html)

Empieza con una ruta de lectura. Además de aciertos, prueba límites TTL, lectura tras escritura, mismo ID entre tenants e idiomas, capacidad máxima, misses simultáneos, fallo y recuperación. En producción observa llamadas, latencia y errores del origen, cargas en curso, expulsiones, memoria e invalidación junto a aciertos. Evalúa beneficios tras comprobar **corrección de respuestas y resistencia del origen sin caché**.
