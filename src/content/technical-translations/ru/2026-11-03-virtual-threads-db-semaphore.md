---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ru",
  "translationKey": "2026-11-03-virtual-threads-db-semaphore",
  "routeSlug": "2026-11-03-virtual-threads-db-semaphore",
  "kind": "post",
  "title": "Виртуальные потоки и семафоры БД: управление допуском перед пулом соединений",
  "description": "Когда пулу JDBC нужен дополнительный семафор? Ограничиваем допуск и выполнение, возвращаем разрешения после завершения транзакции и освобождения ресурсов, проверяем тайм-ауты и отмену с PostgreSQL.",
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
  "draftSha256": "a5f9e30cd8ef3fd2c4cb8aabc20974d8daf43e81d5b95ba80eac82e647873e78",
  "manifestPath": ".pipeline/technical-translations/batch-142/manifest.json",
  "manifestSha256": "c9980c2893c26f4f01a8f1991ea314755050840c12c102f2e907891193acc59a",
  "publishedAt": "2026-11-03T09:13:33.711Z",
  "updatedAt": "2026-11-03T09:13:33.711Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 142,
    "approvedAt": "2026-11-03T09:13:33.711Z",
    "basis": "User explicitly requested multilingual support for the already published article (다국어 지원도 해줘), within the continuing publication task and standing merge/deploy instruction. This records user publication authorization; it does not claim human or native-speaker proofreading."
  }
}
---

Использование виртуальных потоков не означает, что перед базой данных обязательно нужен семафор. Пул соединений уже ограничивает число соединений. Дополнительный семафор полезен, если нужно **раньше отклонять обращения к БД, ограничивать число допущенных операций или выделять отдельным нагрузкам бюджет параллельного выполнения**. В руководстве Oracle по виртуальным потокам также объясняется, что пул соединений с базой данных сам выполняет роль семафора. [Руководство Oracle по виртуальным потокам](https://docs.oracle.com/en/java/javase/25/core/virtual-threads.html)

Эта статья продолжает [сравнение виртуальных потоков в JDK 21–25](/en/posts/2026-10-31-virtual-threads-jdk21-jdk25/) применительно к соединениям с базой данных. Она уточняет границу работы с БД в рамках более общего управления допуском, рассмотренного в статье об [архитектуре для 10k RPS](/en/posts/2026-10-31-jdk-10k-rps-architecture/). Область рассмотрения — Java 21 или новее, одна синхронная JDBC-транзакция и одно соединение. Используйте общий семафор для всего экземпляра приложения; не создавайте новый для каждого запроса.

## Что ограничивать, если пул соединений уже есть?

Виртуальные потоки позволяют поддерживать много ожидающих задач с относительно небольшими накладными расходами на потоки. Сами по себе они не повышают пропускную способность базы данных при обработке запросов и не уменьшают конкуренцию за блокировки. Запросы, ожидающие соединения из заполненного пула, по-прежнему занимают память и сохраняют своё состояние.

| Ситуация | Что применить в первую очередь |
| --- | --- |
| Ограничений числа соединений и времени ожидания в пуле достаточно | Сохранить настройки пула соединений |
| Нужно отклонять запросы при перегрузке до обращения к пулу | Добавить управление допуском |
| Пакетная обработка или дорогие запросы монополизируют соединения | Выделить бюджеты для отдельных нагрузок; при необходимости разделить пулы |
| Медленные SQL-запросы или блокировки слишком долго удерживают соединения | Сначала проверить запросы, индексы, транзакции и ограничения базы данных |

Параметр HikariCP `maximumPoolSize` ограничивает число соединений в пуле. Если свободных соединений нет, `getConnection()` ожидает не дольше `connectionTimeout`, а затем выбрасывает исключение. Минимальное значение этого параметра — 250 мс. Ожидание семафора в течение 20 мс не означает, что ожидание в пуле тоже закончится за 20 мс. [Настройки HikariCP](https://github.com/brettwooldridge/HikariCP#configuration-knobs-baby)

## Ограничьте и выполнение, и общее число допущенных операций

В примере используются два семафора.

- **B разрешений на выполнение:** ограничивают число операций, находящихся в работе с начала получения соединения до завершения транзакции и освобождения ресурсов соединения.
- **B+Q разрешений на допуск:** ограничивают все операции внутри этого шлюза, включая ожидающие разрешения на выполнение. Если разрешений на допуск не осталось, операция немедленно отклоняется.

Когда все B разрешений на выполнение заняты, может оставаться не более Q дополнительных допущенных операций. Однако задачи могут ожидать планирования ещё до получения разрешения на выполнение, поэтому это не означает, что в каждый момент число ожидающих строго ограничено Q. Один семафор, ограничивающий лишь время ожидания, не ограничивает число допущенных ожидающих операций.

![Последовательно получить разрешения на допуск и выполнение, затем вернуть только полученные разрешения после транзакции БД и освобождения ресурсов соединения](/assets/diagrams/technical/ru-2026-11-03-virtual-threads-db-semaphore.svg)

Блок ресурсов БД обобщает внутренние пути обработки исключений. Если получить соединение не удалось, работа пропускается и управление переходит к возврату разрешений. Если не удалось подготовить транзакцию, предпринимается попытка освободить ресурсы полученного соединения. Если работа или фиксация транзакции завершается с ошибкой, предпринимается попытка отката.

Если допуск не получен, возвращать нечего. Если получить разрешение на выполнение не удалось или ожидающий поток был прерван, возвращается только разрешение на допуск. После получения обоих разрешений верните их, когда получение соединения, обработка транзакции и освобождение ресурсов завершатся штатно или с исключением. **Не возвращайте разрешения из другого потока только потому, что у вызывающей стороны истёк тайм-аут.** Если фактическая работа с БД продолжается, это может привести к превышению заданного лимита выполнения.

## Как выбрать B, Q и размер пула?

B обозначает число одновременно обрабатываемых операций с БД, а не запросов в секунду. В него входят ожидание соединения, фиксация транзакции и освобождение ресурсов, поэтому фактическое число параллельных SQL-запросов может быть меньше B. Выбирайте значение по результатам измерений насыщения базы данных, времени удержания соединений и с учётом бюджетов других нагрузок. Q — число дополнительных операций, которые допускаются при перегрузке; выбирайте его с учётом как допустимого ожидания, так и памяти.

Например, при размере пула P=24 и лимите шлюза B=16 через этот шлюз может одновременно обрабатываться не более 16 операций. Оставшиеся 8 соединений не зарезервированы для другой работы. Вызывающие стороны вне шлюза, использующие тот же пул, могут занять все соединения. Даже если для изоляции используются отдельные пулы, суммируйте их бюджеты соединений на уровне базы данных.

При расчёте лимита соединений проверьте условие `peak simultaneous instances × pool size per instance + batch, operations and other client connections ≤ DB connection budget`. Пиковое число экземпляров включает автомасштабирование и одновременную работу старых и новых экземпляров при постепенном развёртывании. `instance count × B` ограничивает только работу, проходящую через этот шлюз. Эти числа иллюстрируют расчёт; они не являются ни рекомендуемыми настройками, ни результатами измерения производительности.

## Исполняемый пример JDBC

В примере шлюз управляет своей транзакцией и соединением. Функция обратного вызова должна выполняться синхронно и возвращать только полностью сформированное значение. Внутри неё нельзя фиксировать или откатывать транзакцию либо менять настройки автоматической фиксации. Возврат `Connection`, `ResultSet` или ленивого потока результатов запроса, как и запуск отдельной асинхронной работы с БД внутри функции обратного вызова, выводит работу за пределы защиты этой границы.

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

Код возвращает разрешение `running`, только если оно было получено, поэтому неудачное ожидание или прерывание не может увеличить число разрешений. SQL-исключения, исключения времени выполнения и ошибки приводят к попытке отката; если откат не удался, его исключение добавляется к исходному как подавленное исключение. Вызывающая сторона получает возвращаемое значение только после завершения фиксации транзакции и вызова `close()` для соединения. Если фиксация завершается с ошибкой или после неё не удаётся освободить ресурсы соединения, запись могла вступить в силу, хотя вызывающая сторона получает исключение. Не повторяйте операции записи безусловно.

Даже семафор со справедливым порядком обслуживания не гарантирует сквозного сохранения порядка всех запросов. В примере разрешение на выполнение запрашивается с тайм-аутом у справедливого семафора, а допуск — немедленно. Вызов `tryAcquire()` без тайм-аута не учитывает настройку справедливости. Методы `available()` предназначены для наблюдений в лабораторном примере; чтение их значений и отдельное решение о допуске создают состояние гонки. [API Semaphore](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/Semaphore.html)

В демонстрации настроены размер пула 2, B=1 и Q=0. Проверяется, что вторая операция отклоняется, пока первая транзакция удерживает разрешение. Кратковременное удержание транзакции с помощью защёлки согласует действия при воспроизведении; это не рекомендуемый способ обработки в сервисе.

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

### Локальный запуск

Сохраните четыре приведённых выше файла в отдельном каталоге для эксперимента; должны быть установлены Docker, JDK 21 и Gradle 8.14.3. Gradle запускается на JDK 21 для загрузки зависимостей. Затем компиляция и выполнение напрямую используют `javac` и `java` выбранной JDK, поэтому для проверки на JDK 25 не нужно запускать Gradle 8.14.3 на JDK 25. Для запуска самого Gradle на JDK 21 требуется версия 8.5 или новее; в этом эксперименте используется 8.14.3. [Поддержка запуска Gradle на Java 21](https://docs.gradle.org/8.5/release-notes.html)

Выполните следующие команды в оболочке POSIX. `JAVA_HOME` должен указывать на JDK, которая будет использоваться для выполнения; для загрузки зависимостей выберите JDK 21. Пароль в примере предназначен только для временной локальной базы данных. Если порт 55432 уже занят, выберите другой.

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

При локальном запуске наблюдался следующий стандартный вывод. Сообщения HikariCP о запуске и остановке могут выводиться отдельно.

```text
overload=rejected
query=42
available=1
```

Проверка проводилась с Temurin 21.0.13+9 и 25.0.5+8, PostgreSQL 17.11, HikariCP 7.1.0 и pgJDBC 42.7.14. Дополнительные проверки подтвердили 45 условий на каждой JDK: фиксацию и откат, превышение лимита допуска, истечение тайм-аута и прерывание ожидания, продолжение работы после отмены, восстановление после серверного тайм-аута SQL-оператора, исчерпание пула и восстановление разрешений после повторных сбоев. Нагрузочный HTTP-тест и измерение пропускной способности в рабочей среде не проводились.

## Границы, которые нужно сохранять при тайм-аутах и транзакциях Spring

**Разделяйте тайм-ауты ожидания и тайм-ауты работы.** Параметр `queueWait` в примере ограничивает только ожидание разрешения на выполнение. Получение соединения из пула, SQL-запросы и ожидание блокировок, сетевой обмен и освобождение ресурсов имеют отдельные бюджеты времени. Для общего предельного срока запроса требуется дополнительное проектирование, чтобы передавать оставшееся время на каждый этап. В этом примере такая сквозная передача срока не реализована.

Параметр PostgreSQL `statement_timeout` ограничивает время выполнения SQL-оператора на сервере, а `lock_timeout` — ожидание получения блокировок. В эксперименте внутри транзакции задавалось `SET LOCAL statement_timeout = '100ms'`, проверялось, что `pg_sleep(2)` завершается с SQLState `57014`, и подтверждалась возможность продолжить последующую работу. Выбирайте реальные значения в соответствии со своими запросами и предельными сроками. [Настройки тайм-аутов PostgreSQL 17](https://www.postgresql.org/docs/17/runtime-config-client.html)

Ни `Future.cancel(true)`, ни завершение HTTP-запроса не гарантирует немедленной остановки JDBC-запроса. В pgJDBC предусмотрены отдельные ограничения для запросов, передачи сигнала отмены и чтения из сокета. Закрытие соединения после тайм-аута сокета также не равнозначно подтверждению остановки работы на сервере. Во время отмены и освобождения ресурсов разрешения остаются у участка кода, выполняющего работу. Если результат записи неизвестен, используйте ключ идемпотентности или запросите результат, чтобы решить, нужен ли повтор. [Свойства соединения pgJDBC](https://jdbc.postgresql.org/documentation/use/)

**В Spring получайте допуск до начала транзакции.** Нетранзакционный входной метод в отдельном бине может пройти через шлюз до вызова транзакционного прокси; другой вариант — выполнить `TransactionTemplate` внутри области полученного допуска. Верните разрешения после того, как вызов прокси или шаблон завершит фиксацию и освобождение ресурсов и вернёт управление. Ожидание внутри метода с уже начатой транзакцией может удерживать ресурсы внешней транзакции. Не встраивайте приведённый выше код управления JDBC-транзакцией и соединением напрямую в существующую транзакцию Spring.

`REQUIRES_NEW` может потребовать ещё одно соединение, сохраняя соединение внешней транзакции. Это нарушает предположение примера об одном соединении на операцию и может вызвать исчерпание пула или ожидание с взаимной блокировкой. Шлюз также не допускает повторного входа; не захватывайте тот же шлюз рекурсивно. [Распространение транзакций Spring и предупреждение об исчерпании пула](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/tx-propagation.html)

В рабочей среде считайте отказы из-за исчерпания допуска отдельно от тайм-аутов ожидания и совместно наблюдайте время ожидания в шлюзе, ожидания в пуле, удержания соединения, выполнения SQL и ожидания блокировок. При преобразовании отказов в HTTP 503 или другой ответ задайте бюджеты повторных попыток клиента, чтобы неограниченные повторы не усиливали нагрузку. Не увеличивайте B только по числу отказов; принимайте решение с учётом задержек и насыщения базы данных.
