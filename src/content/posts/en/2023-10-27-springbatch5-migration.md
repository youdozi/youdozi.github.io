---
language: en
translationKey: 2023-10-27-springbatch5-migration
routeSlug: 2023-10-27-springbatch5-migration
kind: post
categories:
  - spring
tags:
  - spring batch 5
  - migration
publishedAt: "2026-10-27T03:19:18+00:00"
title: "Spring Batch 5 Migration: Schema, Parameters, and Restart Checks"
updatedAt: "2026-10-27T03:19:18+00:00"
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Official sources checked; runnable examples checked separately from
  migration and production claims.
reviewSources:
  - https://github.com/spring-projects/spring-batch/wiki/Spring-Batch-5.0-Migration-Guide
  - https://docs.spring.io/spring-batch/reference/5.2/job/java-config.html
  - https://docs.spring.io/spring-batch/reference/5.2/schema-appendix.html
  - https://docs.spring.io/spring-boot/3.5/how-to/batch.html
description: Review Spring Batch 5 metadata changes and run H2 tests for typed
  parameters, completed-instance rejection, and failed-step restart with
  explicit infrastructure.
---
Migrating to Spring Batch 5 requires checking the metadata schema, persisted Job parameter format, execution contexts, and restart policy alongside dependencies. Dropping populated columns first, or merely replacing type codes with class names, does not complete a data migration.

This article covers moving to Batch 5 rather than adopting the newest major version. The [official 5.0 migration guide](https://github.com/spring-projects/spring-batch/wiki/Spring-Batch-5.0-Migration-Guide) defines the migration concerns; the example below checks execution behavior in a Batch 5 environment.

## Before changing an existing repository

Batch 5 requires Java 17 or later. Migrate Java EE `javax.*` APIs to their Jakarta counterparts without replacing Java SE APIs such as `javax.sql.DataSource`.

The old parameter table's `TYPE_CD` and per-type value columns differ from the new `PARAMETER_TYPE` and `PARAMETER_VALUE` representation. Changing `LONG` to `java.lang.Long` alone neither preserves nor correctly reinterprets existing LONG, DOUBLE, and DATE values. Rehearse conversion on a database copy using the target database and Batch version. Locate the [database-specific schema and migration scripts in the Core JAR](https://docs.spring.io/spring-batch/reference/5.2/schema-appendix.html). Re-running a fresh-schema script against production tables is not a substitute for migration.

The official guide also documents [historical data access restrictions](https://github.com/spring-projects/spring-batch/wiki/Spring-Batch-5.0-Migration-Guide#historical-data-access-implications): some v5 JobExplorer calls can fail while reading v4 executions. It expects failed v4 instances to be restarted successfully under v4 or abandoned following a business decision before migration. Do not assume v5 can directly restart an existing failed v4 execution. Check execution-context serialization compatibility separately from parameter conversion.

## Check behavior in a new Batch 5 repository

The reproduction uses Gradle 8.4/JDK 17.0.8.1, with Batch 5.2.4 and H2 2.3.232 managed by Boot BOM 3.5.7. These versions pin execution evidence; they are not current production recommendations. Save the following three files in an empty directory.

This project creates a Spring test context directly rather than starting a Boot application. It uses `@EnableBatchProcessing` and provides its DataSource and transaction manager. It does not also extend `DefaultBatchConfiguration`; the [Java configuration documentation](https://docs.spring.io/spring-batch/reference/5.2/job/java-config.html) describes these as alternative approaches.

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

## Run and interpret the checks

```sh
gradle --no-daemon clean test
```

The three tests check typed parameter persistence in a fresh H2 schema, rejection of a completed instance with the same identifying parameters, and a new execution of the same failed instance that reruns only its failed Step. The restart case runs the first Step once and the second Step twice. Its counters live in one process, so it does not prove JVM restart recovery or exactly-once external side effects.

This example **does not convert a v4 database to v5**. For production migration, establish backup and recovery first, then check per-type values, historical access, execution contexts, and business restart procedures on a database copy. Passing fresh-schema tests does not establish compatibility with existing data.

There is another consideration when applying the configuration to Boot: [Boot's Batch guide](https://docs.spring.io/spring-boot/3.5/how-to/batch.html) states that adding `@EnableBatchProcessing` or extending `DefaultBatchConfiguration` disables Batch auto-configuration and its schema initialization support. Decide whether to retain Boot's auto-configuration or take direct control.

For related runtime decisions, see [JDK 21 final and preview features](/en/posts/2023-09-20-jdk-21-release/). For typed configuration input, see [reading a YAML port from a shell script](/en/posts/2021-07-27-parse-yaml/).
