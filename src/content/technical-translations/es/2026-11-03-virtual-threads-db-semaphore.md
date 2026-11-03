---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2026-11-03-virtual-threads-db-semaphore",
  "routeSlug": "2026-11-03-virtual-threads-db-semaphore",
  "kind": "post",
  "title": "Hilos virtuales y semáforos de BD: controlar la admisión antes del pool de conexiones",
  "description": "¿Cuándo necesita un pool JDBC un semáforo adicional? Limitar la admisión y la ejecución, liberar permisos tras completar la transacción y liberar sus recursos, y verificar tiempos de espera y cancelación con PostgreSQL.",
  "categories": [
    "jdk"
  ],
  "tags": [
    "java",
    "virtual-threads",
    "jdbc",
    "hikaricp",
    "semaphore",
    "postgresql"
  ],
  "sourcePath": "src/content/posts/en/2026-11-03-virtual-threads-db-semaphore.md",
  "sourceSha256": "103d90ef1cccefaa0b1dd31120b1813c5ded6536bcd76a9ae5a0f75388d3584a",
  "draftSha256": "37c6d5cd2f512647020b6bc23f3af46bf003e859c391653efa4c1fb856fc90c6",
  "manifestPath": ".pipeline/technical-translations/batch-142/manifest.json",
  "manifestSha256": "5fe9109b95b95e2b8170cf69c0858a600703961ffcef9978dece770bde39c49e",
  "publishedAt": "2026-11-03T09:05:06.170Z",
  "updatedAt": "2026-11-03T09:05:06.170Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 142,
    "approvedAt": "2026-11-03T09:05:06.170Z",
    "basis": "User explicitly requested multilingual support for the already published article (다국어 지원도 해줘), within the continuing publication task and standing merge/deploy instruction. This records user publication authorization; it does not claim human or native-speaker proofreading."
  }
}
---

Usar hilos virtuales no implica que haya que añadir un semáforo delante de la base de datos. El pool de conexiones ya limita el número de conexiones. Un semáforo adicional resulta útil cuando se quiere **rechazar antes el trabajo con la BD, limitar el número de operaciones admitidas o asignar presupuestos de concurrencia a cargas concretas**. La guía de Oracle sobre hilos virtuales también explica que un pool de conexiones a la base de datos actúa por sí mismo como un semáforo. [Guía de Oracle sobre hilos virtuales](https://docs.oracle.com/en/java/javase/25/core/virtual-threads.html)

Este artículo continúa la [comparación de hilos virtuales entre JDK 21–25](/en/posts/2026-10-31-virtual-threads-jdk21-jdk25/) en el ámbito de las conexiones a la base de datos. Concreta el límite del trabajo con la BD dentro del control de admisión más amplio tratado en la [arquitectura para 10k RPS](/en/posts/2026-10-31-jdk-10k-rps-architecture/). Su alcance es Java 21 o posterior, con una transacción JDBC síncrona que usa una conexión. El semáforo debe compartirse en toda la instancia de la aplicación; no se debe crear uno nuevo para cada solicitud.

## ¿Qué conviene limitar si ya existe un pool de conexiones?

Los hilos virtuales permiten mantener muchas tareas en espera con un coste relativamente bajo por hilo. Por sí solos no aumentan la capacidad de la base de datos para procesar consultas ni reducen la contención de bloqueos. Las solicitudes que esperan una conexión de un pool lleno siguen ocupando memoria y conservando su estado.

| Situación | Control que aplicar primero |
| --- | --- |
| Los límites de conexiones y de espera del pool son suficientes | Mantener la configuración del pool de conexiones |
| Se quiere rechazar solicitudes por sobrecarga antes de que lleguen al pool | Añadir control de admisión |
| Una carga por lotes o consultas costosas monopolizan las conexiones | Asignar presupuestos por carga; separar los pools si hace falta |
| El SQL lento o los bloqueos retienen las conexiones demasiado tiempo | Revisar primero consultas, índices, transacciones y límites de la base de datos |

El parámetro `maximumPoolSize` de HikariCP limita el número de conexiones del pool. Si no hay ninguna disponible, `getConnection()` espera hasta `connectionTimeout` y después lanza una excepción. Su valor mínimo es 250 ms. Esperar 20 ms por un semáforo no hace que la espera en el pool también termine en 20 ms. [Configuración de HikariCP](https://github.com/brettwooldridge/HikariCP#configuration-knobs-baby)

## Limitar tanto la ejecución como la admisión total

El ejemplo utiliza dos semáforos.

- **B permisos de ejecución:** limitan las operaciones en curso desde la obtención de la conexión hasta que terminan la transacción y la liberación de recursos de la conexión.
- **B+Q permisos de admisión:** limitan todas las operaciones dentro de esta puerta de acceso, incluidas las que esperan un permiso de ejecución. Si no queda ningún permiso de admisión, la operación se rechaza de inmediato.

Cuando todos los permisos de ejecución B están en uso, pueden quedar como máximo Q operaciones adicionales admitidas. Sin embargo, las tareas también pueden estar pendientes de planificación antes de adquirir un permiso de ejecución, por lo que esto no significa que el número de tareas en espera esté estrictamente limitado a Q en todo momento. Un único semáforo que solo limita el tiempo de espera no limita el número de operaciones admitidas en espera.

![Adquirir por orden los permisos de admisión y ejecución, y liberar solo los adquiridos después de la transacción de BD y de liberar los recursos de la conexión](/assets/diagrams/technical/es-2026-11-03-virtual-threads-db-semaphore.svg)

El bloque de recursos de BD resume las rutas internas de excepción. Si falla la obtención de la conexión, se omite el trabajo y se pasa a liberar los permisos. Si falla la preparación de la transacción, se intenta liberar los recursos de la conexión obtenida. Si falla el trabajo o la confirmación de la transacción, se intenta revertirla.

Si falla la admisión, no hay ningún permiso que liberar. Si falla la adquisición del permiso de ejecución o se interrumpe el hilo en espera, se libera solo el permiso de admisión. Una vez adquiridos ambos permisos, se liberan cuando la obtención de la conexión, el procesamiento de la transacción y la liberación de recursos hayan terminado, de forma normal o con una excepción. **No se deben liberar permisos desde otro hilo solo porque haya vencido el tiempo de espera del llamador.** Si el trabajo real con la BD continúa, hacerlo puede superar el límite de ejecución configurado.

## ¿Cómo elegir B, Q y el tamaño del pool?

B cuenta operaciones concurrentes con la BD, no solicitudes por segundo. Incluye las esperas para obtener conexiones, la confirmación de la transacción y la liberación de recursos, de modo que la concurrencia SQL real puede ser menor que B. Su valor debe elegirse midiendo la saturación de la base de datos, el tiempo de retención de las conexiones y los presupuestos de otras cargas. Q es el número de operaciones adicionales que se admitirán durante una sobrecarga; al elegirlo, hay que tener en cuenta tanto el presupuesto de espera como la memoria.

Por ejemplo, con un pool P=24 y una puerta de acceso B=16, puede haber como máximo 16 operaciones en curso a través de esta puerta. Las 8 conexiones restantes no están reservadas para otros trabajos. Los llamadores que comparten el pool y no pasan por la puerta podrían ocupar todas las conexiones. Incluso si se separan los pools para aislar las cargas, hay que sumar sus presupuestos de conexiones en el ámbito de la base de datos.

Al calcular los límites de conexiones, se debe comprobar `peak simultaneous instances × pool size per instance + batch, operations and other client connections ≤ DB connection budget`. El pico de instancias incluye el escalado automático y la coexistencia de instancias antiguas y nuevas durante un despliegue gradual. `instance count × B` limita solo el trabajo que pasa por esta puerta. Estos números ilustran el cálculo; no son configuraciones recomendadas ni mediciones de rendimiento.

## Un ejemplo JDBC ejecutable

En el ejemplo, la puerta de acceso gestiona su propia transacción y conexión. La función callback debe ejecutarse de forma síncrona y devolver únicamente un valor completamente materializado. Dentro de ella no se debe confirmar ni revertir la transacción ni cambiar la configuración de confirmación automática. Devolver un `Connection`, un `ResultSet` o un flujo de consulta con evaluación diferida, o iniciar trabajo asíncrono independiente con la BD dentro de la función callback, escapa a la protección de este límite.

### `DbBulkhead.java`

```java
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Duration;
import java.util.Objects;
import java.util.concurrent.RejectedExecutionException;
import java.util.concurrent.Semaphore;
import java.util.concurrent.TimeUnit;
import javax.sql.DataSource;

public final class DbBulkhead {
    @FunctionalInterface
    public interface SqlWork<T> {
        T run(Connection connection) throws SQLException;
    }

    private final DataSource source;
    private final Semaphore slots;
    private final Semaphore running;

    public DbBulkhead(DataSource source, int concurrent, int extraSlots) {
        this.source = Objects.requireNonNull(source);
        if (concurrent < 1 || extraSlots < 0) {
            throw new IllegalArgumentException("invalid capacity");
        }
        slots = new Semaphore(Math.addExact(concurrent, extraSlots));
        running = new Semaphore(concurrent, true);
    }

    public <T> T transaction(Duration queueWait, SqlWork<T> work)
            throws SQLException, InterruptedException {
        Objects.requireNonNull(work);
        long nanos = queueWait.toNanos();
        if (nanos < 0) throw new IllegalArgumentException("negative wait");
        if (!slots.tryAcquire()) {
            throw new RejectedExecutionException("db admission full");
        }
        boolean acquired = false;
        try {
            acquired = running.tryAcquire(nanos, TimeUnit.NANOSECONDS);
            if (!acquired) {
                throw new RejectedExecutionException("db admission timed out");
            }
            try (Connection connection = source.getConnection()) {
                connection.setAutoCommit(false);
                try {
                    T value = work.run(connection);
                    connection.commit();
                    return value;
                } catch (SQLException | RuntimeException | Error failure) {
                    try {
                        connection.rollback();
                    } catch (SQLException rollbackFailure) {
                        failure.addSuppressed(rollbackFailure);
                    }
                    throw failure;
                }
            }
        } finally {
            if (acquired) running.release();
            slots.release();
        }
    }

    int available() { return running.availablePermits(); }
    int availableSlots() { return slots.availablePermits(); }
}
```

El código libera `running` solo si se ha adquirido, por lo que una espera fallida o una interrupción no pueden aumentar el número de permisos. Las excepciones SQL, las excepciones de ejecución y los errores provocan un intento de reversión; si este falla, su excepción se añade a la original como excepción suprimida. El llamador recibe el valor de retorno solo después de que terminen la confirmación y el `close()` de la conexión. Si falla la confirmación, o falla la liberación de recursos de la conexión después de confirmar, una escritura puede haber surtido efecto aunque el llamador reciba una excepción. No se deben reintentar escrituras incondicionalmente.

Ni siquiera un semáforo con política de equidad garantiza el orden de extremo a extremo para todas las solicitudes. El ejemplo usa una adquisición con tiempo límite en un semáforo de ejecución con equidad, pero una adquisición inmediata para la admisión. `tryAcquire()` sin tiempo límite no respeta la configuración de equidad. Los métodos `available()` sirven para observar el experimento; leer sus valores y decidir la admisión por separado crea una condición de carrera. [API de Semaphore](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/Semaphore.html)

La demostración configura un tamaño de pool de 2, B=1 y Q=0. Comprueba que una segunda operación se rechaza mientras la primera transacción mantiene su permiso. Retener brevemente la transacción mediante un latch coordina la reproducción; no es un patrón recomendado para el procesamiento en un servicio.

### `Demo.java`

```java
import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import java.sql.SQLException;
import java.time.Duration;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.RejectedExecutionException;
import java.util.concurrent.TimeUnit;

public class Demo {
    static HikariDataSource pool() {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl(System.getenv("DB_URL"));
        config.setUsername(System.getenv("DB_USER"));
        config.setPassword(System.getenv("DB_PASSWORD"));
        config.setMaximumPoolSize(2);
        config.setMinimumIdle(0);
        config.setConnectionTimeout(500);
        config.setValidationTimeout(250);
        return new HikariDataSource(config);
    }

    public static void main(String[] args) throws Exception {
        try (var pool = pool(); var tasks = Executors.newVirtualThreadPerTaskExecutor()) {
            var gate = new DbBulkhead(pool, 1, 0);
            var entered = new CountDownLatch(1);
            var release = new CountDownLatch(1);
            var first = tasks.submit(() -> gate.transaction(Duration.ZERO, connection -> {
                if (!Thread.currentThread().isVirtual()) throw new AssertionError();
                try (var statement = connection.createStatement()) {
                    statement.setQueryTimeout(2);
                    try (var rows = statement.executeQuery("SELECT 42")) {
                        rows.next();
                        int value = rows.getInt(1);
                        entered.countDown();
                        try {
                            if (!release.await(5, TimeUnit.SECONDS)) {
                                throw new SQLException("demo coordination timed out");
                            }
                        } catch (InterruptedException interrupted) {
                            Thread.currentThread().interrupt();
                            throw new SQLException("demo interrupted", interrupted);
                        }
                        return value;
                    }
                }
            }));
            try {
                if (!entered.await(5, TimeUnit.SECONDS)) throw new AssertionError("not entered");
                var second = tasks.submit(() -> gate.transaction(Duration.ZERO, c -> 0));
                try {
                    second.get(5, TimeUnit.SECONDS);
                    throw new AssertionError("must reject");
                } catch (ExecutionException failure) {
                    if (!(failure.getCause() instanceof RejectedExecutionException)) throw failure;
                    System.out.println("overload=rejected");
                }
            } finally {
                release.countDown();
            }
            System.out.println("query=" + first.get(5, TimeUnit.SECONDS));
            System.out.println("available=" + gate.available());
        }
    }
}
```

### `build.gradle`

```groovy
plugins { id 'application' }
repositories { mavenCentral() }
dependencies {
    implementation 'com.zaxxer:HikariCP:7.1.0'
    runtimeOnly 'org.postgresql:postgresql:42.7.14'
    runtimeOnly 'org.slf4j:slf4j-simple:2.0.20'
}
sourceSets.main.java {
    srcDirs = ['.']
    include 'DbBulkhead.java', 'Demo.java', 'DbBulkheadChecks.java'
}
tasks.withType(JavaCompile).configureEach { options.release = 21 }
application { mainClass = 'Demo' }
tasks.register('copyDependencies', Copy) {
    from configurations.runtimeClasspath
    into layout.buildDirectory.dir('deps')
}
tasks.register('contracts', JavaExec) {
    classpath = sourceSets.main.runtimeClasspath
    mainClass = 'DbBulkheadChecks'
}
```

### `settings.gradle`

```groovy
rootProject.name = 'virtual-threads-db-semaphore'
```

### Ejecutar en local

Hay que guardar los cuatro archivos anteriores en un directorio de pruebas separado y tener instalados Docker, JDK 21 y Gradle 8.14.3. Gradle se ejecuta sobre JDK 21 para descargar las dependencias. Después, la compilación y la ejecución usan directamente `javac` y `java` del JDK seleccionado, por lo que probar JDK 25 no requiere ejecutar Gradle 8.14.3 sobre JDK 25. Para ejecutar el propio Gradle sobre JDK 21 se necesita la versión 8.5 o posterior; este experimento usa 8.14.3. [Compatibilidad de Gradle con Java 21 como entorno de ejecución](https://docs.gradle.org/8.5/release-notes.html)

Los siguientes comandos se ejecutan en un intérprete POSIX. `JAVA_HOME` debe apuntar al JDK que se utilizará para ejecutar; para descargar las dependencias hay que seleccionar JDK 21. La contraseña del ejemplo es solo para la base de datos local temporal. Si el puerto 55432 ya está en uso, hay que elegir otro.

```sh
(
  set -eu
  gradle --no-daemon -q copyDependencies
  db_container=$(docker run -d --rm -p 127.0.0.1:55432:5432 \
    -e POSTGRES_USER=demo -e POSTGRES_DB=demo \
    -e POSTGRES_PASSWORD=example-only \
    postgres@sha256:839fbb5a4942a7758dd93e18b42ea5649807491a0545b5eeeb8f0b8bb11857a5)
  trap 'docker stop "$db_container" >/dev/null' EXIT
  ready=false
  for attempt in $(seq 1 30); do
    if docker exec "$db_container" pg_isready -h 127.0.0.1 -U demo -d demo >/dev/null 2>&1; then
      ready=true
      break
    fi
    sleep 1
  done
  if [ "$ready" != true ]; then exit 1; fi
  mkdir -p build/classes
  "$JAVA_HOME/bin/javac" --release 21 -cp 'build/deps/*' \
    -d build/classes DbBulkhead.java Demo.java
  DB_URL='jdbc:postgresql://127.0.0.1:55432/demo?connectTimeout=2&socketTimeout=5' \
    DB_USER=demo DB_PASSWORD=example-only \
    "$JAVA_HOME/bin/java" -cp 'build/classes:build/deps/*' Demo
)
```

La salida estándar observada en local fue la siguiente. Los registros de inicio y cierre de HikariCP pueden aparecer por separado.

```text
overload=rejected
query=42
available=1
```

El entorno de verificación fue Temurin 21.0.13+9 y 25.0.5+8, PostgreSQL 17.11, HikariCP 7.1.0 y pgJDBC 42.7.14. Las comprobaciones complementarias verificaron 45 condiciones en cada JDK: confirmación y reversión, exceso de admisión, esperas agotadas e interrumpidas, trabajo que continúa tras la cancelación, recuperación después de un tiempo límite de sentencia en el servidor, agotamiento del pool y recuperación de permisos tras fallos repetidos. No se realizó ninguna prueba de carga HTTP ni se midió el rendimiento en producción.

## Límites que preservar con los tiempos de espera y las transacciones de Spring

**Separar los tiempos límite de espera de los tiempos límite del trabajo.** El parámetro `queueWait` del ejemplo solo limita la espera de un permiso de ejecución. La obtención de conexiones del pool, el SQL y las esperas por bloqueos, la red y la liberación de recursos tienen presupuestos separados. Un plazo global para la solicitud requiere un diseño adicional que propague el tiempo restante a cada etapa. Este ejemplo no implementa esa propagación del plazo de extremo a extremo.

El parámetro `statement_timeout` de PostgreSQL limita el tiempo de ejecución de las sentencias en el servidor, mientras que `lock_timeout` limita la espera para adquirir bloqueos. En el experimento se estableció `SET LOCAL statement_timeout = '100ms'` dentro de una transacción, se comprobó que `pg_sleep(2)` fallaba con SQLState `57014` y se verificó que el trabajo posterior podía continuar. Los valores reales deben elegirse según las consultas y los plazos de cada caso. [Configuración de tiempos límite de PostgreSQL 17](https://www.postgresql.org/docs/17/runtime-config-client.html)

Ni `Future.cancel(true)` ni la finalización de una solicitud HTTP garantizan que una consulta JDBC termine de inmediato. pgJDBC tiene límites separados para las consultas, la transmisión de la señal de cancelación y las lecturas del socket. Cerrar una conexión después de un tiempo de espera del socket tampoco equivale a confirmar que el trabajo en el servidor se ha detenido. El bloque que ejecuta el trabajo conserva la propiedad de los permisos durante la cancelación y la liberación de recursos. Cuando el resultado de una escritura es incierto, se debe usar una clave de idempotencia o consultar el resultado para decidir si se reintenta. [Propiedades de conexión de pgJDBC](https://jdbc.postgresql.org/documentation/use/)

**Con Spring, obtener la admisión antes de iniciar la transacción.** Un método de entrada no transaccional en un bean separado puede pasar por la puerta antes de llamar a un proxy transaccional, o se puede ejecutar un `TransactionTemplate` dentro del ámbito admitido. Los permisos se liberan después de que la llamada al proxy o la plantilla haya completado la confirmación y la liberación de recursos y haya retornado. Esperar dentro de un método cuya transacción ya ha comenzado puede retener recursos de la transacción externa. No se debe mezclar el código anterior de gestión de JDBC directamente con una transacción Spring existente.

`REQUIRES_NEW` puede necesitar otra conexión mientras conserva la de la transacción externa. Eso rompe la suposición de este ejemplo de una conexión por operación y puede agotar el pool o provocar esperas con interbloqueo. La puerta tampoco es reentrante; no se debe adquirir la misma puerta de forma recursiva. [Propagación de transacciones de Spring y advertencia sobre agotamiento del pool](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/tx-propagation.html)

En producción, hay que contar por separado los rechazos por admisión llena y los tiempos de espera agotados, y observar conjuntamente la espera en la puerta, la espera en el pool, el tiempo de retención de conexiones, la duración del SQL y las esperas por bloqueos. Al convertir los rechazos en HTTP 503 u otra respuesta, se deben definir presupuestos de reintentos del cliente para que los reintentos sin límite no amplifiquen la carga. No se debe aumentar B basándose solo en el número de rechazos; la decisión debe apoyarse en la latencia y la saturación de la base de datos.
