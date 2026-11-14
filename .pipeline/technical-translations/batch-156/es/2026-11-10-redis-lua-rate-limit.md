---
{
  "state": "draft",
  "language": "es",
  "translationKey": "2026-11-10-redis-lua-rate-limit",
  "title": "Límites de solicitudes con Redis y Lua en Spring MVC",
  "description": "Implementa un límite de ventana fija con Redis Lua, distingue las respuestas 429 y 503 y analiza concurrencia, caducidad y fallos.",
  "sourcePath": "src/content/posts/en/2026-11-10-redis-lua-rate-limit.md",
  "sourceSha256": "bffe243d3ec0d2693086eb4d708c74490b34a27af7c1735cf6a41c81eea561d5"
}
---

**Para limitar las solicitudes de un mismo usuario entre servidores de aplicaciones, decide el límite y actualiza el contador conjuntamente en Redis.** Este artículo implementa una ventana fija con Lua: devuelve `429` si se supera el límite y `503` si Redis no puede determinar el resultado.

La política de ejemplo permite **un máximo de tres solicitudes por cuenta durante los 10 segundos que comienzan con la primera solicitud permitida**. La ventana fija es aquí el punto de partida más sencillo; no equivale a un token bucket ni a una ventana deslizante. El entorno usa Spring Boot 3.5.16, JDK 21, Gradle 8.14.3 y Redis 8.2.1. Las versiones se fijan para reproducir el ejemplo, no como recomendación de los últimos parches de producción.

## ¿Por qué no usar GET seguido de INCR en la aplicación?

Si los servidores A y B leen un contador de `2`, pueden permitir ambos solicitudes aunque el límite sea `3`. `synchronized` de la JVM no bloquea otros procesos. `INCR` es atómico, pero no incluye automáticamente la decisión de admisión anterior.

Enviar `EXPIRE` como comando separado después de `INCR` tiene otro problema: si el cliente se detiene entre ambos, la clave puede quedar sin TTL. El [ejemplo oficial de límite con INCR](https://redis.io/docs/latest/commands/incr/) de Redis también explica esta condición de carrera y el uso de Lua.

En la primera solicitud, el script siguiente crea conjuntamente el valor y su TTL mediante `SET ... PX`. En las siguientes comprueba el límite dentro de Lua e incrementa solo las solicitudes permitidas. Las rechazadas no cambian ni el contador ni la caducidad.

## ¿En qué orden se aplica el límite?

![El servidor elige una clave de límite y Redis Lua comprueba contador y TTL. Si se permite, SET PX o INCR registra la solicitud y la aplicación devuelve 200; si se supera el límite devuelve 429 y Retry-After sin cambiar el estado. Los errores de conexión o estado devuelven 503.](2026-11-10-redis-lua-rate-limit.svg)

La zona azul representa la decisión dentro de Redis; la aplicación crea la respuesta HTTP. Una clave ausente inicia una nueva ventana. Una clave existente debe tener un contador entero positivo y un TTL válido. El límite cuenta admisiones y no devuelve el conteo si el trabajo falla después de admitirse.

## Implementar el límite con Spring MVC y Redis Lua

Guarda estos seis archivos en un proyecto Gradle. La autenticación no está implementada. `/demo` trata cada solicitud como la única cuenta `demo-account`, por lo que la clave es un ejemplo fijo para reproducir una política por usuario. El servidor escucha solo en una dirección local.

En un servicio real, deriva la clave de un **principal verificado por el servidor**, como un `Principal` autenticado. Confiar en una cabecera `userId` arbitraria permite evadir el límite cambiando su valor. Por ejemplo, `rl:orders:v1:<tenant-and-subject-digest>` puede distinguir alcance de la operación, versión de la política y sujeto; considera un identificador como un HMAC con secreto del servidor en lugar de datos personales sin procesar. Interpreta las cabeceras de IP reenviada solo dentro de un límite de proxy confiable.

### `settings.gradle`

```groovy
rootProject.name = 'redis-lua-rate-limit'
```

### `build.gradle`

```groovy
plugins {
    id 'java'
    id 'application'
}
repositories { mavenCentral() }
java { toolchain { languageVersion = JavaLanguageVersion.of(21) } }
dependencies {
    implementation platform('org.springframework.boot:spring-boot-dependencies:3.5.16')
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.boot:spring-boot-starter-data-redis'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
application { mainClass = 'example.RateLimitApplication' }
test {
    useJUnitPlatform()
    systemProperty 'demo.redis.port', providers.gradleProperty('redisPort').getOrElse('6379')
}
```

### `src/main/resources/application.yml`

```yaml
server:
  address: 127.0.0.1
spring:
  data:
    redis:
      host: 127.0.0.1
      port: ${REDIS_PORT:6379}
      connect-timeout: 200ms
      timeout: 200ms
```

### `src/main/resources/rate-limit.lua`

```lua
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
if not limit or limit < 1 or limit > 1000000 or limit ~= math.floor(limit)
   or not window or window < 1 or window > 3600000 or window ~= math.floor(window) then
    return redis.error_reply('invalid rate limit policy')
end

local raw = redis.call('GET', KEYS[1])
if raw then
    local count = tonumber(raw)
    local ttl = redis.call('PTTL', KEYS[1])
    if not count or count < 1 or count ~= math.floor(count) or ttl < 0 then
        return redis.error_reply('invalid counter state')
    end
    if count >= limit then
        return {0, 0, ttl}
    end
    local updated = redis.call('INCR', KEYS[1])
    return {1, limit - updated, ttl}
end

redis.call('SET', KEYS[1], 1, 'PX', window)
return {1, limit - 1, window}
```

### `src/main/java/example/RedisRateLimiter.java`

```java
package example;

import java.time.Duration;
import java.util.List;
import org.springframework.core.io.ClassPathResource;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.script.DefaultRedisScript;
import org.springframework.stereotype.Component;

@Component
public class RedisRateLimiter {
    private static final DefaultRedisScript<List> SCRIPT = new DefaultRedisScript<>();
    static {
        SCRIPT.setLocation(new ClassPathResource("rate-limit.lua"));
        SCRIPT.setResultType(List.class);
    }
    private final StringRedisTemplate redis;

    public RedisRateLimiter(StringRedisTemplate redis) {
        this.redis = redis;
    }

    public Decision check(String key, int limit, Duration window) {
        long milliseconds = window.toMillis();
        if (key == null || key.isBlank() || key.length() > 160 || limit < 1 || limit > 1_000_000
                || milliseconds < 1 || milliseconds > 3_600_000) {
            throw new IllegalArgumentException("Invalid rate limit policy");
        }
        List<?> result = redis.execute(SCRIPT, List.of(key),
                Integer.toString(limit), Long.toString(milliseconds));
        if (result == null || result.size() != 3) {
            throw new IllegalStateException("Invalid limiter result");
        }
        return new Decision(((Number) result.get(0)).longValue() == 1,
                ((Number) result.get(1)).longValue(), ((Number) result.get(2)).longValue());
    }

    public record Decision(boolean allowed, long remaining, long ttlMillis) {
        public long retryAfterSeconds() {
            return Math.max(1, (ttlMillis + 999) / 1000);
        }
    }
}
```

### `src/main/java/example/RateLimitApplication.java`

```java
package example;

import java.time.Duration;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.dao.DataAccessException;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
@RestController
public class RateLimitApplication {
    private final RedisRateLimiter limiter;

    public RateLimitApplication(RedisRateLimiter limiter) {
        this.limiter = limiter;
    }

    public static void main(String[] args) {
        SpringApplication.run(RateLimitApplication.class, args);
    }

    @GetMapping("/demo")
    public ResponseEntity<String> demo() {
        try {
            var decision = limiter.check("rl:demo:v1:demo-account", 3, Duration.ofSeconds(10));
            if (!decision.allowed()) {
                return ResponseEntity.status(429)
                        .header("Retry-After", Long.toString(decision.retryAfterSeconds()))
                        .body("rate limit exceeded\n");
            }
            return ResponseEntity.ok("ok\n");
        } catch (DataAccessException | IllegalStateException unavailable) {
            return ResponseEntity.status(503).body("limiter unavailable\n");
        }
    }
}
```

Este script usa una clave. En Redis Cluster se ejecuta en el slot que contiene esa clave. Extenderlo para limitar varias claves requiere rediseñar teniendo en cuenta la restricción de compartir slot.

`StringRedisTemplate` usa claves y argumentos de cadena; el array numérico del script se recibe como `List`. La razón de reutilizar `DefaultRedisScript` y el uso de `EVALSHA` seguido de `EVAL` ante una ausencia en caché por el ejecutor predeterminado se explican en la [documentación de scripting de Spring Data Redis](https://docs.spring.io/spring-data/redis/reference/redis/scripting.html).

## ¿Qué respuestas se esperan?

Ejecuta el ejemplo con Docker disponible y los puertos `16379` de Redis y `8080` de la aplicación libres. Redis solo se expone en la dirección loopback del host; la persistencia y los volúmenes persistentes están desactivados. La primera ejecución descarga la imagen de Redis y dependencias Maven, por lo que necesita red.

```sh
docker run --rm -d --name redis-rate-limit-demo \
  -p 127.0.0.1:16379:6379 \
  redis:8.2.1-alpine@sha256:987c376c727652f99625c7d205a1cba3cb2c53b92b0b62aade2bd48ee1593232 \
  redis-server --save '' --appendonly no
REDIS_PORT=16379 gradle run
```

Cuando el servidor esté listo, haz cuatro llamadas en 10 segundos desde otra terminal.

```sh
for attempt in 1 2 3 4; do
  curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8080/demo
done
curl -i http://127.0.0.1:8080/demo
```

Enviar esas cuatro solicitudes consecutivas en una ventana nueva debería producir estos códigos:

```text
200
200
200
429
```

El `Retry-After` del rechazo es el TTL restante redondeado hacia arriba a segundos enteros, con un mínimo de un segundo. Su valor depende del momento de la llamada. El significado de `429` y del `Retry-After` opcional sigue la [RFC 6585, sección 4](https://www.rfc-editor.org/rfc/rfc6585#section-4). No reserva la admisión frente a otras solicitudes: el reintento puede volver a rechazarse si otra solicitud consume el límite mientras tanto.

Detén `gradle run` y elimina el contenedor de prueba.

```sh
docker stop redis-rate-limit-demo
```

## ¿Qué se verificó sobre concurrencia y errores?

Pruebas independientes de reproducción usaron Redis real en Docker local y Tomcat integrado. Comprueban el comportamiento, no la capacidad de procesamiento.

| Condición | Resultado observado |
| --- | --- |
| 40 llamadas simultáneas para una clave desde un pool de hilos | 3 permitidas; contador Redis 3 |
| Dos limitadores con el mismo Redis y clave | Comparten el límite. Ambos objetos comparten un bean de cliente; no se iniciaron dos JVM separadas. |
| Solicitud tras tres llamadas permitidas | Rechazada, sin incrementar el contador ni ampliar el TTL |
| Otra clave de cuenta y una clave caducada | La otra clave se permite de forma independiente; tras la caducidad comienza una ventana nueva |
| Valor inválido o clave sin TTL | Error sin reparación arbitraria |
| Llamadas HTTP reales consecutivas | Tres respuestas 200 seguidas de 429 con `Retry-After` |
| Solicitud HTTP con contador inválido | 503 |
| Un endpoint TCP separado acepta conexiones pero no responde como Redis | Error del limitador convertido en 503 |

Un contador validado debe tener TTL. La [documentación de PTTL](https://redis.io/docs/latest/commands/pttl/) define `-1` como ausencia de TTL y `-2` como clave inexistente. Añadir silenciosamente un TTL y permitir una solicitud con estado inválido podría ocultar un error de política, por lo que esta implementación devuelve un error.

**La ejecución atómica de Lua no significa que las escrituras se reviertan automáticamente ante un error.** Distingue el aislamiento de ejecución del tratamiento de errores descrito en la [documentación oficial de scripting](https://redis.io/docs/latest/develop/programmability/eval-intro/). Una prueba también confirmó que un valor permanecía después de que otro script ejecutara `SET` y devolviera intencionadamente un error. El script de este artículo valida entrada y estado antes de escribir y limita la escritura al `SET` o `INCR` final.

## ¿Qué límites y políticas de fallo elegir en producción?

**Una ventana fija no garantiza como máximo tres solicitudes en cada intervalo consecutivo de 10 segundos.** Agotar el límite justo antes de terminar una ventana y volver a solicitar al comenzar la siguiente puede concentrar solicitudes en un periodo corto. Considera registros deslizantes o ventanas deslizantes para un total móvil exacto, o un token bucket para separar la tasa media y la ráfaga permitida. Este artículo no implementa ni compara el rendimiento de esos algoritmos.

El ejemplo usa **fail-closed**: los errores de Redis no dejan pasar solicitudes. Puede convenir cuando evadir un límite tiene alto coste, como en pagos, pero un problema de Redis reduce también la disponibilidad de la API. Si la disponibilidad importa más, por ejemplo en una API de consulta, puede permitirse temporalmente una política con buckets locales limitados. El total permitido puede crecer con el número de servidores, así que no ofrece la misma garantía que un límite global.

El ajuste de 200ms es un tiempo límite de conexión y comando, no una garantía de que la solicitud HTTP completa termine en 200ms. Considera por separado colas, reconexión y planificación. El código no añade reintentos de aplicación; revisa también la reconexión y retransmisión del cliente. Si Redis registra una admisión y se pierde la respuesta, el contador puede consumirse aunque el llamador observe un fallo. Para contar un reintento una sola vez se necesitan un identificador de solicitud y una política de idempotencia separada.

Si una clave Redis se expulsa por presión de memoria o se pierde su contador durante reinicio o conmutación, una solicitud posterior puede iniciar una ventana nueva y permitirse. Lua atómico por sí solo no proporciona un límite global que abarque replicación y recuperación. Gestiona instancias dedicadas, límites de memoria, expulsión, versiones de claves, recuentos de rechazo y error Redis, y latencia de decisión. Añadir identificadores por clave directamente como etiquetas de métricas aumenta la cardinalidad.

Esta reproducción cubre funcionamiento normal con una sola instancia Redis y algunos errores. No prueba conmutación de Redis Cluster, múltiples regiones, recuperación tras una caída real del proceso Redis ni rendimiento bajo carga de producción. Limitar el inicio de solicitudes tampoco limita la ocupación simultánea de la base de datos ni el número de solicitudes largas; aplica límites de concurrencia separados cuando sean necesarios.
