---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2026-11-03-virtual-threads-db-semaphore",
  "routeSlug": "2026-11-03-virtual-threads-db-semaphore",
  "kind": "post",
  "title": "Virtuelle Threads und DB-Semaphore: Zulassung vor dem Verbindungspool steuern",
  "description": "Wann braucht ein JDBC-Pool einen zusätzlichen Semaphor? Zulassung und Ausführung begrenzen, Berechtigungen nach der Transaktionsbereinigung freigeben und Timeouts sowie Abbruchverhalten mit PostgreSQL prüfen.",
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
  "draftSha256": "f4cbce956c04be52e57fe3ddc81952cc9d38477cf3054f76f7389f5e451bfe19",
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

Virtuelle Threads bedeuten nicht, dass vor der Datenbank ein zusätzlicher Semaphor erforderlich ist. Der Verbindungspool begrenzt die Anzahl der Verbindungen bereits. Ein zusätzlicher Semaphor ist sinnvoll, wenn **DB-Arbeit früher abgewiesen, die Anzahl zugelassener Operationen begrenzt oder bestimmten Arbeitslasten eigene Nebenläufigkeitsbudgets zugeteilt werden sollen**. Auch Oracles Leitfaden zu virtuellen Threads erklärt, dass ein Datenbank-Verbindungspool selbst wie ein Semaphor wirkt. [Oracles Leitfaden zu virtuellen Threads](https://docs.oracle.com/en/java/javase/25/core/virtual-threads.html)

Dieser Artikel setzt den [Vergleich virtueller Threads in JDK 21–25](/en/posts/2026-10-31-virtual-threads-jdk21-jdk25/) bei Datenbankverbindungen fort. Er konkretisiert die Grenze für DB-Arbeit innerhalb der umfassenderen Zulassungssteuerung aus der [10k-RPS-Architektur](/en/posts/2026-10-31-jdk-10k-rps-architecture/). Betrachtet wird Java 21 oder höher mit einer synchronen JDBC-Transaktion, die eine Verbindung verwendet. Der Semaphor muss innerhalb einer Anwendungsinstanz gemeinsam genutzt werden; für jede Anfrage einen neuen zu erstellen, verfehlt diesen Zweck.

## Was sollte begrenzt werden, wenn bereits ein Verbindungspool vorhanden ist?

Virtuelle Threads können viele wartende Aufgaben mit vergleichsweise geringem Thread-Aufwand vorhalten. Sie erhöhen für sich genommen weder die Abfragekapazität der Datenbank noch verringern sie Konflikte um Sperren. Anfragen, die auf eine Verbindung aus einem ausgelasteten Pool warten, belegen weiterhin Speicher und halten ihren Anfragezustand vor.

| Situation | Zuerst anzuwendende Maßnahme |
| --- | --- |
| Verbindungsgrenzen und Wartezeitlimit des Pools reichen aus | Konfiguration des Verbindungspools beibehalten |
| Überlastete Anfragen sollen vor dem Eintritt in den Pool abgewiesen werden | Zulassungssteuerung ergänzen |
| Eine Batch-Last oder aufwendige Abfragen beanspruchen die Verbindungen allein | Budgets pro Arbeitslast festlegen; bei Bedarf Pools trennen |
| Langsames SQL oder Sperren halten Verbindungen zu lange | Zuerst Abfragen, Indizes, Transaktionen und Datenbankgrenzen prüfen |

HikariCP begrenzt mit `maximumPoolSize` die Anzahl der Verbindungen im Pool. Ist keine verfügbar, wartet `getConnection()` bis zu `connectionTimeout` und löst danach eine Ausnahme aus. Der Mindestwert beträgt 250ms. Eine Semaphor-Wartezeit von 20ms bewirkt nicht, dass auch das Warten auf den Pool innerhalb von 20ms endet. [HikariCP-Konfiguration](https://github.com/brettwooldridge/HikariCP#configuration-knobs-baby)

## Ausführung und gesamte Zulassung begrenzen

Das Beispiel verwendet zwei Semaphore.

- **B Ausführungsberechtigungen:** begrenzen laufende Operationen vom Anfordern der Verbindung über die Transaktion bis zum Aufräumen der Verbindung.
- **B+Q Zulassungsberechtigungen:** begrenzen alle Operationen innerhalb dieser Zugangsschranke, einschließlich derer, die auf eine Ausführungsberechtigung warten. Ist keine Zulassungsberechtigung mehr verfügbar, wird sofort abgewiesen.

Sind alle B Ausführungsberechtigungen belegt, können höchstens Q weitere zugelassene Operationen verbleiben. Aufgaben können jedoch auch schon vor dem Erwerb einer Ausführungsberechtigung zur Ausführung eingeplant sein. Daher bedeutet dies nicht, dass die Anzahl der Wartenden zu jedem Zeitpunkt exakt durch Q begrenzt ist. Ein einzelner Semaphor, der nur die Wartezeit begrenzt, begrenzt nicht die Anzahl zugelassener Wartender.

![Zulassungs- und Ausführungsberechtigung nacheinander erwerben und nach DB-Transaktion und Verbindungsbereinigung nur erworbene Berechtigungen freigeben](/assets/diagrams/technical/de-2026-11-03-virtual-threads-db-semaphore.svg)

Der Kasten für DB-Ressourcen fasst die internen Ausnahmewege zusammen. Scheitert das Anfordern der Verbindung, wird die Arbeit übersprungen und mit der Freigabe der Berechtigungen fortgefahren. Scheitert die Einrichtung der Transaktion, wird versucht, die erhaltene Verbindung zu bereinigen. Scheitert die Arbeit oder der Commit, wird ein Rollback versucht.

Scheitert die Zulassung, gibt es keine Berechtigung freizugeben. Scheitert der Erwerb der Ausführungsberechtigung oder wird der wartende Thread unterbrochen, wird nur die Zulassungsberechtigung freigegeben. Nach dem Erwerb beider Berechtigungen werden diese erst freigegeben, wenn Verbindungsanforderung, Transaktionsverarbeitung und Bereinigung normal oder mit einer Ausnahme abgewickelt sind. **Berechtigungen dürfen nicht allein deshalb von einem anderen Thread freigegeben werden, weil beim Aufrufer ein Timeout aufgetreten ist.** Läuft die eigentliche DB-Arbeit weiter, kann dadurch das konfigurierte Ausführungslimit überschritten werden.

## Wie werden B, Q und Poolgröße gewählt?

B zählt gleichzeitige DB-Operationen, keine Anfragen pro Sekunde. Dazu gehören das Warten auf eine Verbindung, der Commit und die Bereinigung. Die tatsächliche SQL-Nebenläufigkeit kann daher unter B liegen. Zur Wahl dienen Messungen der Datenbanksättigung, der Verbindungsbelegungsdauer und der Budgets anderer Arbeitslasten. Q bezeichnet die Anzahl zusätzlicher Operationen, die bei Überlast zugelassen werden; dabei sind sowohl das Wartebudget als auch der Speicherbedarf zu berücksichtigen.

Bei einem Pool mit P=24 und einer Zugangsschranke mit B=16 können beispielsweise höchstens 16 Operationen über diese Schranke laufen. Die verbleibenden 8 Verbindungen sind nicht für andere Arbeit reserviert. Aufrufer außerhalb der Schranke, die denselben Pool nutzen, könnten sämtliche Verbindungen belegen. Selbst bei getrennten Pools zur Isolation müssen deren Verbindungsbudgets auf Datenbankebene zusammengerechnet werden.

Bei der Planung der Verbindungsgrenzen ist `peak simultaneous instances × pool size per instance + batch, operations and other client connections ≤ DB connection budget` zu prüfen. Die maximale Instanzanzahl umfasst Autoscaling sowie die Überlappung alter und neuer Instanzen bei einem Rolling Deployment. `instance count × B` begrenzt nur Arbeit, die diese Zugangsschranke passiert. Die Zahlen veranschaulichen die Berechnung; sie sind weder empfohlene Einstellungen noch Leistungsmessungen.

## Ein ausführbares JDBC-Beispiel

Die Zugangsschranke im Beispiel verwaltet ihre Transaktion und Verbindung selbst. Der Callback muss synchron ausgeführt werden und darf nur einen vollständig materialisierten Wert zurückgeben. Im Callback dürfen weder Commit noch Rollback ausgeführt oder Auto-Commit-Einstellungen verändert werden. Die Rückgabe einer `Connection`, eines `ResultSet` oder eines erst bei Bedarf ausgewerteten Abfragestreams sowie das Starten separater asynchroner DB-Arbeit im Callback umgehen den Schutz dieser Grenze.

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

Der Code gibt `running` nur frei, wenn die Berechtigung erworben wurde. Ein erfolgloses Warten oder eine Unterbrechung kann die Anzahl der Berechtigungen daher nicht erhöhen. SQL-Ausnahmen, Laufzeitausnahmen und Fehler lösen einen Rollback-Versuch aus; scheitert dieser, wird sein Fehler der ursprünglichen Ausnahme als unterdrückte Ausnahme hinzugefügt. Der Aufrufer erhält den Rückgabewert erst nach Abschluss des Commits und von `close()` auf der Verbindung. Scheitert der Commit oder schlägt nach dem Commit die Verbindungsbereinigung fehl, kann ein Schreibvorgang wirksam geworden sein, obwohl der Aufrufer eine Ausnahme erhält. Schreibvorgänge dürfen nicht bedingungslos wiederholt werden.

Auch ein fairer Semaphor garantiert nicht für jede Anfrage eine durchgängige Reihenfolge. Das Beispiel nutzt für die Ausführung einen fairen Semaphor mit zeitbegrenztem Erwerb, für die Zulassung dagegen einen sofortigen Erwerbsversuch. `tryAcquire()` ohne Zeitlimit berücksichtigt die Fairness-Einstellung nicht. Die `available()`-Methoden dienen der Beobachtung im Versuch; das getrennte Lesen dieser Werte und Entscheiden über die Zulassung erzeugt eine Race Condition. [Semaphore-API](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/Semaphore.html)

Die Demo konfiguriert Poolgröße 2, B=1 und Q=0. Sie prüft, dass eine zweite Operation abgewiesen wird, während die erste Transaktion ihre Berechtigung hält. Das kurze Anhalten der Transaktion mit einer Latch koordiniert die Reproduktion; es ist kein empfohlenes Muster für die Verarbeitung im Dienst.

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

### Lokal ausführen

Die vier obigen Dateien werden in einem separaten Versuchsverzeichnis gespeichert; Docker, JDK 21 und Gradle 8.14.3 müssen installiert sein. Gradle läuft zum Herunterladen der Abhängigkeiten unter JDK 21. Kompilierung und Ausführung verwenden anschließend direkt `javac` und `java` des ausgewählten JDK. Ein Test unter JDK 25 erfordert daher nicht, Gradle 8.14.3 unter JDK 25 auszuführen. Gradle selbst unter JDK 21 auszuführen erfordert Version 8.5 oder höher; dieser Versuch verwendet 8.14.3. [Gradles Laufzeitunterstützung für Java 21](https://docs.gradle.org/8.5/release-notes.html)

Die folgenden Befehle werden in einer POSIX-Shell ausgeführt. `JAVA_HOME` muss auf das auszuführende JDK zeigen; für das Herunterladen der Abhängigkeiten ist JDK 21 auszuwählen. Das Beispielpasswort ist ausschließlich für die temporäre lokale Datenbank bestimmt. Ist Port 55432 bereits belegt, muss ein anderer Port gewählt werden.

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

Lokal wurde die folgende Standardausgabe beobachtet. Die Start- und Stoppmeldungen von HikariCP können separat erscheinen.

```text
overload=rejected
query=42
available=1
```

Die Prüfumgebung bestand aus Temurin 21.0.13+9 und 25.0.5+8, PostgreSQL 17.11, HikariCP 7.1.0 und pgJDBC 42.7.14. Ergänzende Prüfungen bestätigten auf jedem JDK 45 Bedingungen: Commit und Rollback, überzählige Zulassungen, abgelaufene und unterbrochene Wartevorgänge, weiterlaufende Arbeit nach einem Abbruch, Erholung nach einem serverseitigen Statement-Timeout, Pool-Erschöpfung sowie die Wiederherstellung der Berechtigungen nach wiederholten Fehlern. Es wurden weder HTTP-Lasttests noch Messungen des Produktionsdurchsatzes durchgeführt.

## Grenzen bei Timeouts und Spring-Transaktionen

**Wartezeitlimits und Zeitlimits für die Arbeit trennen.** `queueWait` im Beispiel begrenzt nur das Warten auf eine Ausführungsberechtigung. Für Poolzugriff, SQL- und Sperrwartezeiten, Netzwerk und Bereinigung gelten eigene Budgets. Eine Gesamtfrist für die Anfrage erfordert ein zusätzliches Konzept, das die verbleibende Zeit an jede Stufe weitergibt. Diese durchgängige Weitergabe der Frist implementiert das Beispiel nicht.

In PostgreSQL begrenzt `statement_timeout` die Ausführungszeit eines Statements auf dem Server, während `lock_timeout` das Warten auf Sperren begrenzt. Im Versuch wurde innerhalb einer Transaktion `SET LOCAL statement_timeout = '100ms'` gesetzt, geprüft, dass `pg_sleep(2)` mit SQLState `57014` fehlschlug, und bestätigt, dass nachfolgende Arbeit fortgesetzt werden konnte. Die tatsächlichen Werte sind passend zu Abfragen und Fristen zu wählen. [Timeout-Einstellungen in PostgreSQL 17](https://www.postgresql.org/docs/17/runtime-config-client.html)

Weder `Future.cancel(true)` noch das Beenden einer HTTP-Anfrage garantiert das sofortige Ende einer JDBC-Abfrage. pgJDBC hat getrennte Limits für Abfragen, das Übermitteln des Abbruchsignals und Socket-Lesevorgänge. Eine Verbindung nach einem Socket-Timeout zu schließen ist ebenfalls etwas anderes, als zu bestätigen, dass die serverseitige Arbeit beendet ist. Die ausführende Grenze behält während Abbruch und Bereinigung die Verantwortung für die Berechtigungen. Ist das Ergebnis eines Schreibvorgangs ungewiss, sollte anhand eines Idempotenzschlüssels oder einer Abfrage des Ergebnisses über eine Wiederholung entschieden werden. [pgJDBC-Verbindungseigenschaften](https://jdbc.postgresql.org/documentation/use/)

**Bei Spring muss die Zulassung vor Beginn der Transaktion erfolgen.** Eine nichttransaktionale Einstiegsmethode in einer separaten Bean kann die Zugangsschranke passieren, bevor sie einen transaktionalen Proxy aufruft. Alternativ lässt sich ein `TransactionTemplate` innerhalb des zugelassenen Bereichs ausführen. Berechtigungen werden freigegeben, nachdem Proxy-Aufruf oder Template Commit und Bereinigung abgeschlossen haben und zurückgekehrt sind. Das Warten innerhalb einer Methode, deren Transaktion bereits begonnen hat, kann Ressourcen der äußeren Transaktion weiter belegen. Der obige Code zur eigenen Verwaltung von JDBC-Verbindungen und -Transaktionen darf nicht direkt mit einer bestehenden Spring-Transaktion vermischt werden.

`REQUIRES_NEW` kann eine weitere Verbindung benötigen und dabei die Verbindung der äußeren Transaktion beibehalten. Das verletzt die Annahme dieses Beispiels, dass jede Operation eine Verbindung nutzt, und kann zur Erschöpfung des Pools oder zu Deadlock-Wartezuständen führen. Die Zugangsschranke ist außerdem nicht reentrant; dieselbe Schranke darf nicht rekursiv erworben werden. [Spring-Transaktionspropagation und Warnung vor Pool-Erschöpfung](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/tx-propagation.html)

Im Produktionsbetrieb sollten Abweisungen wegen voller Zulassung getrennt von Wartezeitüberschreitungen gezählt und Wartezeit an der Schranke, Poolwartezeit, Verbindungsbelegungsdauer, SQL-Dauer und Sperrwartezeiten gemeinsam betrachtet werden. Werden Abweisungen auf HTTP 503 oder eine andere Antwort abgebildet, sind Wiederholungsbudgets für Clients festzulegen, damit unbegrenzte Wiederholungen die Last nicht verstärken. B sollte nicht allein aufgrund der Abweisungsanzahl erhöht werden; ausschlaggebend sind Datenbanklatenz und -sättigung.
