---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2023-10-27-springbatch5-migration",
  "routeSlug": "2023-10-27-springbatch5-migration",
  "kind": "post",
  "title": "Spring Batch 5 migrieren: Metadaten und Neustarts getrennt prüfen",
  "description": "Bestehende Batch-Metadaten von neuen v5-Tests unterscheiden und Parameter, Ausführungskontexte und Neustartregeln prüfen.",
  "categories": [
    "spring"
  ],
  "tags": [
    "spring batch 5",
    "migration"
  ],
  "sourcePath": "src/content/posts/en/2023-10-27-springbatch5-migration.md",
  "sourceSha256": "688dd3a4a3f176f0d94406dbc3c73979ece0d8a4e0f23ca31a65de298e922d77",
  "draftSha256": "d2311634479800870d92bd31e48f70c11687d8dd0386fd219a74280063c686c5",
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
Eine Migration auf Spring Batch 5 erfordert neben den Abhängigkeiten auch die Prüfung von Metadatenschema, gespeichertem Jobparameterformat, Ausführungskontexten und Neustartrichtlinie. Das vorherige Löschen befüllter Spalten oder der bloße Ersatz von Typcodes durch Klassennamen schließt keine Datenmigration ab.

Dieser Artikel behandelt den Wechsel zu Batch 5, nicht die Übernahme der neuesten Hauptversion. Der [offizielle Migrationsleitfaden für 5.0](https://github.com/spring-projects/spring-batch/wiki/Spring-Batch-5.0-Migration-Guide) definiert die Migrationsaspekte; das folgende Beispiel prüft Ausführungsverhalten in einer Batch-5-Umgebung.

## Verarbeitungsablauf

![Fehlgeschlagene v5-Instanz neu starten](/assets/diagrams/technical/de-2023-10-27-springbatch5-migration.svg)

Dies fasst den v5-Neustarttest mit neuem Schema zusammen, keine v4-Datenbankmigration. Eine zweite Ausführung derselben Instanz wiederholt den fehlgeschlagenen Schritt; der abgeschlossene Schritt bleibt abgeschlossen.

## Vor Änderungen an einem bestehenden Repository

Batch 5 benötigt Java 17 oder neuer. Migrieren Sie Java-EE-APIs unter `javax.*` zu ihren Jakarta-Entsprechungen, ohne Java-SE-APIs wie `javax.sql.DataSource` zu ersetzen.

`TYPE_CD` und die typspezifischen Wertspalten der alten Parametertabelle unterscheiden sich von der neuen Darstellung durch `PARAMETER_TYPE` und `PARAMETER_VALUE`. Allein `LONG` in `java.lang.Long` zu ändern bewahrt und interpretiert vorhandene LONG-, DOUBLE- und DATE-Werte nicht korrekt. Proben Sie die Umwandlung auf einer Datenbankkopie mit der Zieldatenbank und Batch-Version. Suchen Sie die [datenbankspezifischen Schema- und Migrationsskripte in der Core-JAR](https://docs.spring.io/spring-batch/reference/5.2/schema-appendix.html). Ein Skript für ein neues Schema erneut auf Produktionstabellen auszuführen ersetzt keine Migration.

Der offizielle Leitfaden dokumentiert außerdem [Einschränkungen beim Zugriff auf historische Daten](https://github.com/spring-projects/spring-batch/wiki/Spring-Batch-5.0-Migration-Guide#historical-data-access-implications): Manche v5-JobExplorer-Aufrufe können beim Lesen von v4-Ausführungen scheitern. Fehlgeschlagene v4-Instanzen sollen vor der Migration unter v4 erfolgreich neu gestartet oder aufgrund einer fachlichen Entscheidung aufgegeben werden. Nehmen Sie nicht an, dass v5 eine bestehende fehlgeschlagene v4-Ausführung direkt neu starten kann. Prüfen Sie die Serialisierungskompatibilität der Ausführungskontexte getrennt von der Parameterumwandlung.

## Ausgangspunkt der Migration wählen

- **Bestehendes Batch-4-Repository:** Sichern Sie es und proben Sie Schema-, Parameter- und Ausführungskontextumwandlung auf einer Datenbankkopie. Klären Sie fehlgeschlagene v4-Instanzen unter v4. Das folgende Beispiel konvertiert kein v4-Repository und startet es nicht neu.
- **Neues Batch-5-Repository:** Führen Sie die Tests für typisierte Parameter, abgeschlossene Instanzen und fehlgeschlagene Schritte aus. Sie prüfen drei Verhaltensweisen in einem neuen H2-Schema innerhalb eines Prozesses.
- **Boot-Anwendung mit Batch-Jobs:** Legen Sie fest, ob Boot oder eine explizite Batch-Konfiguration Einrichtung und Schema-Initialisierung übernimmt. Das Beispiel verwendet explizite Spring-Konfiguration, keine automatische Boot-Konfiguration.

Wenn dies zugleich ein Boot-Hauptversionswechsel ist, stellen Sie die [Java- und Jakarta-Migrationsbasis](/en/posts/2023-09-08-springboot3-migration/) getrennt von der Repository-Migration her.

## Verhalten in einem neuen Batch-5-Repository prüfen

Die Reproduktion verwendet Gradle 8.4/JDK 17.0.8.1 sowie Batch 5.2.4 und H2 2.3.232, verwaltet durch die Boot-BOM 3.5.7. Diese Versionen fixieren die Ausführungsnachweise; sie sind keine aktuellen Produktionsempfehlungen. Speichern Sie die folgenden drei Dateien in einem leeren Verzeichnis.

Dieses Projekt erstellt direkt einen Spring-Testkontext, statt eine Boot-Anwendung zu starten. Es verwendet `@EnableBatchProcessing` und stellt DataSource sowie Transaktionsmanager bereit. Es erweitert nicht zusätzlich `DefaultBatchConfiguration`; die [Dokumentation zur Java-Konfiguration](https://docs.spring.io/spring-batch/reference/5.2/job/java-config.html) beschreibt diese als alternative Ansätze.

### `settings.gradle`

```groovy
rootProject.name = 'batch5-restart-example'
```

### `build.gradle`

```groovy
plugins { id 'java' }
repositories { mavenCentral() }
dependencies {
    testImplementation platform('org.springframework.boot:spring-boot-dependencies:3.5.7')
    testImplementation 'org.springframework.batch:spring-batch-core'
    testImplementation 'org.springframework:spring-jdbc'
    testImplementation 'com.h2database:h2'
    testImplementation 'org.junit.jupiter:junit-jupiter'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
test { useJUnitPlatform() }
```

### `src/test/java/example/BatchRestartTest.java`

```java
package example;

import java.util.Date;
import java.util.Set;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import javax.sql.DataSource;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.batch.core.BatchStatus;
import org.springframework.batch.core.Job;
import org.springframework.batch.core.JobExecution;
import org.springframework.batch.core.JobParameters;
import org.springframework.batch.core.JobParametersBuilder;
import org.springframework.batch.core.Step;
import org.springframework.batch.core.configuration.annotation.EnableBatchProcessing;
import org.springframework.batch.core.job.builder.JobBuilder;
import org.springframework.batch.core.launch.JobLauncher;
import org.springframework.batch.core.repository.JobInstanceAlreadyCompleteException;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.batch.core.step.builder.StepBuilder;
import org.springframework.batch.repeat.RepeatStatus;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.AnnotationConfigApplicationContext;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DataSourceTransactionManager;
import org.springframework.jdbc.datasource.embedded.EmbeddedDatabase;
import org.springframework.jdbc.datasource.embedded.EmbeddedDatabaseBuilder;
import org.springframework.jdbc.datasource.embedded.EmbeddedDatabaseType;
import org.springframework.transaction.PlatformTransactionManager;

import static org.junit.jupiter.api.Assertions.*;

class BatchRestartTest {
    AnnotationConfigApplicationContext context;
    Config config;
    JobLauncher launcher;
    Job job;

    @BeforeEach
    void open() {
        context = new AnnotationConfigApplicationContext(Config.class);
        config = context.getBean(Config.class);
        launcher = context.getBean(JobLauncher.class);
        job = context.getBean(Job.class);
    }

    @AfterEach
    void close() { context.close(); }

    JobParameters parameters() {
        return new JobParametersBuilder()
                .addLong("run.id", 1L)
                .addString("source", "example")
                .addDouble("ratio", 1.5)
                .addDate("day", new Date(0))
                .toJobParameters();
    }

    @Test
    void completedJobPersistsTypedParameters() throws Exception {
        JobExecution execution = launcher.run(job, parameters());
        assertEquals(BatchStatus.COMPLETED, execution.getStatus());
        var jdbc = new JdbcTemplate(context.getBean(DataSource.class));
        var types = jdbc.queryForList("select PARAMETER_TYPE from BATCH_JOB_EXECUTION_PARAMS", String.class);
        assertEquals(Set.of("java.lang.Long", "java.lang.String", "java.lang.Double", "java.util.Date"), Set.copyOf(types));
        assertEquals(4, types.size());
        assertEquals("1", jdbc.queryForObject("select PARAMETER_VALUE from BATCH_JOB_EXECUTION_PARAMS where PARAMETER_NAME = 'run.id'", String.class));
    }

    @Test
    void completedInstanceRejectsSameIdentifyingParameters() throws Exception {
        assertEquals(BatchStatus.COMPLETED, launcher.run(job, parameters()).getStatus());
        assertThrows(JobInstanceAlreadyCompleteException.class, () -> launcher.run(job, parameters()));
        assertEquals(1, config.firstRuns.get());
        assertEquals(1, config.secondRuns.get());
    }

    @Test
    void failedInstanceRestartsOnlyItsFailedStep() throws Exception {
        config.failOnce.set(true);
        JobExecution failed = launcher.run(job, parameters());
        assertEquals(BatchStatus.FAILED, failed.getStatus());
        JobExecution restarted = launcher.run(job, parameters());
        assertEquals(BatchStatus.COMPLETED, restarted.getStatus());
        assertEquals(failed.getJobInstance().getInstanceId(), restarted.getJobInstance().getInstanceId());
        assertNotEquals(failed.getId(), restarted.getId());
        assertEquals(1, config.firstRuns.get());
        assertEquals(2, config.secondRuns.get());
    }

    @Configuration
    @EnableBatchProcessing
    static class Config {
        final AtomicInteger firstRuns = new AtomicInteger();
        final AtomicInteger secondRuns = new AtomicInteger();
        final AtomicBoolean failOnce = new AtomicBoolean();

        @Bean(destroyMethod = "shutdown")
        EmbeddedDatabase dataSource() {
            return new EmbeddedDatabaseBuilder().generateUniqueName(true)
                    .setType(EmbeddedDatabaseType.H2)
                    .addScript("org/springframework/batch/core/schema-h2.sql").build();
        }

        @Bean
        PlatformTransactionManager transactionManager(DataSource dataSource) {
            return new DataSourceTransactionManager(dataSource);
        }

        @Bean
        Step firstStep(JobRepository repository, PlatformTransactionManager transactionManager) {
            return new StepBuilder("first", repository).tasklet((contribution, chunkContext) -> {
                firstRuns.incrementAndGet();
                return RepeatStatus.FINISHED;
            }, transactionManager).build();
        }

        @Bean
        Step secondStep(JobRepository repository, PlatformTransactionManager transactionManager) {
            return new StepBuilder("second", repository).tasklet((contribution, chunkContext) -> {
                secondRuns.incrementAndGet();
                if (failOnce.getAndSet(false)) throw new IllegalStateException("fixture failure");
                return RepeatStatus.FINISHED;
            }, transactionManager).build();
        }

        @Bean
        Job job(JobRepository repository, @Qualifier("firstStep") Step first,
                @Qualifier("secondStep") Step second) {
            return new JobBuilder("migrationCheck", repository).start(first).next(second).build();
        }
    }
}
```

## Prüfungen ausführen und auswerten

```sh
gradle --no-daemon clean test
```

Die drei Tests prüfen die Speicherung typisierter Parameter in einem neuen H2-Schema, die Ablehnung einer abgeschlossenen Instanz mit denselben identifizierenden Parametern sowie eine neue Ausführung derselben fehlgeschlagenen Instanz, die nur ihren fehlgeschlagenen Step wiederholt. Im Neustartfall läuft der erste Step einmal und der zweite zweimal. Die Zähler leben in einem Prozess; dies belegt daher weder Wiederherstellung nach JVM-Neustart noch genau einmalige externe Nebenwirkungen.

Dieses Beispiel **konvertiert keine v4-Datenbank nach v5**. Stellen Sie für eine Produktionsmigration zuerst Sicherung und Wiederherstellung her und prüfen Sie dann typspezifische Werte, historischen Zugriff, Ausführungskontexte und fachliche Neustartverfahren auf einer Datenbankkopie. Bestandene Tests mit neuem Schema belegen keine Kompatibilität mit vorhandenen Daten.

Bei der Übernahme der Konfiguration in Boot ist ein weiterer Punkt zu beachten: [Boots Batch-Leitfaden](https://docs.spring.io/spring-boot/3.5/how-to/batch.html) erklärt, dass `@EnableBatchProcessing` oder das Erweitern von `DefaultBatchConfiguration` die automatische Batch-Konfiguration und ihre Schema-Initialisierung deaktiviert. Entscheiden Sie, ob Boots automatische Konfiguration erhalten bleiben oder die direkte Kontrolle übernommen werden soll.

Für verwandte Laufzeitentscheidungen siehe [endgültige und Preview-Funktionen des JDK 21](/en/posts/2023-09-20-jdk-21-release/). Für typisierte Konfigurationseingaben siehe [einen YAML-Port aus einem Shell-Skript lesen](/en/posts/2021-07-27-parse-yaml/).
