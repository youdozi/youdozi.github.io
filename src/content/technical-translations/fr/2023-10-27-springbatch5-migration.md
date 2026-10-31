---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2023-10-27-springbatch5-migration",
  "routeSlug": "2023-10-27-springbatch5-migration",
  "kind": "post",
  "title": "Migrer vers Spring Batch 5 : vérifier métadonnées et redémarrages",
  "description": "Distinguer les métadonnées Batch existantes des tests v5 neufs et vérifier paramètres, contextes d’exécution et règles de redémarrage.",
  "categories": [
    "spring"
  ],
  "tags": [
    "spring batch 5",
    "migration"
  ],
  "sourcePath": "src/content/posts/en/2023-10-27-springbatch5-migration.md",
  "sourceSha256": "688dd3a4a3f176f0d94406dbc3c73979ece0d8a4e0f23ca31a65de298e922d77",
  "draftSha256": "aa764e8cf37953b8c0ce875d84358245d0249c91a7916bd19383ea9285108ada",
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
Migrer vers Spring Batch 5 nécessite de vérifier le schéma de métadonnées, le format des paramètres de Job persistés, les contextes d’exécution et la politique de redémarrage en plus des dépendances. Supprimer d’abord des colonnes peuplées ou simplement remplacer les codes de type par des noms de classe ne suffit pas à réaliser une migration des données.

Cet article traite du passage à Batch 5 plutôt que de l’adoption de la dernière version majeure. Le [guide officiel de migration 5.0](https://github.com/spring-projects/spring-batch/wiki/Spring-Batch-5.0-Migration-Guide) définit les points de migration ; l’exemple ci-dessous vérifie le comportement d’exécution dans un environnement Batch 5.

## Déroulement du traitement

![Redémarrer l’instance v5 en échec](/assets/diagrams/technical/fr-2023-10-27-springbatch5-migration.svg)

Cela résume le test de redémarrage v5 sur schéma neuf, et non une migration de base v4. Une seconde exécution de la même instance relance l’étape en échec ; l’étape achevée le reste.

## Avant de modifier un repository existant

Batch 5 nécessite Java 17 ou ultérieur. Migrez les API Java EE `javax.*` vers leurs équivalents Jakarta sans remplacer les API Java SE telles que `javax.sql.DataSource`.

Le `TYPE_CD` et les colonnes de valeur par type de l’ancienne table de paramètres diffèrent de la nouvelle représentation `PARAMETER_TYPE` et `PARAMETER_VALUE`. Remplacer seulement `LONG` par `java.lang.Long` ne préserve ni ne réinterprète correctement les valeurs LONG, DOUBLE et DATE existantes. Répétez la conversion sur une copie de la base avec la base cible et la version Batch visée. Retrouvez les [scripts de schéma et de migration propres à chaque base dans le JAR Core](https://docs.spring.io/spring-batch/reference/5.2/schema-appendix.html). Réexécuter un script de schéma neuf sur des tables de production ne remplace pas une migration.

Le guide officiel documente aussi les [restrictions d’accès aux données historiques](https://github.com/spring-projects/spring-batch/wiki/Spring-Batch-5.0-Migration-Guide#historical-data-access-implications) : certains appels JobExplorer v5 peuvent échouer en lisant des exécutions v4. Il prévoit de redémarrer avec succès les instances v4 en échec sous v4 ou de les abandonner sur décision métier avant la migration. Ne supposez pas que v5 peut redémarrer directement une exécution v4 existante en échec. Vérifiez la compatibilité de sérialisation des contextes séparément de la conversion des paramètres.

## Choisir le point de départ de la migration

- **Repository Batch 4 existant :** sauvegardez et répétez la conversion du schéma, des paramètres et des contextes d’exécution sur une copie de base. Traitez les instances v4 en échec sous v4. L’exemple ci-dessous ne convertit ni ne redémarre un repository v4.
- **Nouveau repository Batch 5 :** exécutez les tests de paramètres typés, d’instance achevée et d’étape en échec. Ils vérifient trois comportements dans un schéma H2 neuf, au sein d’un seul processus.
- **Application Boot avec jobs Batch :** décidez si Boot ou une configuration Batch explicite gère l’installation et l’initialisation du schéma. L’exemple utilise une configuration Spring explicite, pas la configuration automatique de Boot.

S’il s’agit aussi d’un changement de version majeure Boot, établissez la [base de migration Java et Jakarta](/en/posts/2023-09-08-springboot3-migration/) séparément de la migration du repository.

## Vérifier le comportement dans un nouveau repository Batch 5

La reproduction utilise Gradle 8.4/JDK 17.0.8.1, avec Batch 5.2.4 et H2 2.3.232 gérés par la BOM Boot 3.5.7. Ces versions figent les preuves d’exécution ; elles ne constituent pas des recommandations actuelles pour la production. Enregistrez les trois fichiers suivants dans un répertoire vide.

Ce projet crée directement un contexte de test Spring plutôt que de démarrer une application Boot. Il utilise `@EnableBatchProcessing` et fournit son DataSource et son gestionnaire de transactions. Il n’étend pas aussi `DefaultBatchConfiguration` ; la [documentation de configuration Java](https://docs.spring.io/spring-batch/reference/5.2/job/java-config.html) les décrit comme des approches alternatives.

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

## Exécuter et interpréter les contrôles

```sh
gradle --no-daemon clean test
```

Les trois tests vérifient la persistance de paramètres typés dans un schéma H2 neuf, le refus d’une instance achevée avec les mêmes paramètres identifiants et une nouvelle exécution de la même instance en échec ne relançant que son Step en échec. Le cas de redémarrage exécute le premier Step une fois et le second deux fois. Ses compteurs vivent dans un seul processus : cela ne prouve ni la reprise après redémarrage JVM ni des effets externes exactement une fois.

Cet exemple **ne convertit pas une base v4 en v5**. Pour une migration de production, établissez d’abord sauvegarde et récupération, puis vérifiez les valeurs par type, l’accès historique, les contextes d’exécution et les procédures métier de redémarrage sur une copie de base. Réussir les tests sur schéma neuf n’établit pas la compatibilité avec les données existantes.

Un autre point intervient pour appliquer cette configuration à Boot : le [guide Batch de Boot](https://docs.spring.io/spring-boot/3.5/how-to/batch.html) indique qu’ajouter `@EnableBatchProcessing` ou étendre `DefaultBatchConfiguration` désactive la configuration automatique Batch et son initialisation de schéma. Décidez de conserver la configuration automatique de Boot ou de prendre directement le contrôle.

Pour les décisions d’exécution liées, voir les [fonctionnalités finales et preview du JDK 21](/en/posts/2023-09-20-jdk-21-release/). Pour les entrées de configuration typées, voir [la lecture d’un port YAML depuis un script shell](/en/posts/2021-07-27-parse-yaml/).
