---
title: "Spring Batch 5 마이그레이션: 스키마·Job 파라미터·재시작"
language: ko
translationKey: 2023-10-27-springbatch5-migration
routeSlug: 2023-10-27-springbatch5-migration
kind: post
publishedAt: 2023-10-26T15:00:00.000Z
categories:
  - spring
tags:
  - spring batch 5
  - migration
legacyUrl: /spring/springbatch5-migration/
legacySource: _posts/spring/migration/2023-10-27-springbatch5-migration.markdown
updatedAt: 2026-10-30T05:22:10.381026+00:00
reviewedAt: "2026-10-30"
reviewStatus: revised
reviewScope: Official sources checked; runnable examples checked separately from
  migration and production claims.
archiveBodySha256: 9c0428486a2f50071a983c45ec66d388aa33f1d204f4c3d84bdd923aa5f73b75
reviewSources:
  - https://github.com/spring-projects/spring-batch/wiki/Spring-Batch-5.0-Migration-Guide
  - https://docs.spring.io/spring-batch/reference/5.2/job/java-config.html
  - https://docs.spring.io/spring-batch/reference/5.2/schema-appendix.html
  - https://docs.spring.io/spring-boot/3.5/how-to/batch.html
description: "Spring Batch 5 스키마와 Job 파라미터 이관 조건을 정리합니다. 새 H2 스키마에서 타입별 파라미터·완료 인스턴스·실패 Step 재시작을 확인합니다."
---
Spring Batch 5로 옮길 때는 의존성뿐 아니라 메타데이터 스키마, Job 파라미터의 저장 형식, 실행 컨텍스트와 재시작 정책을 함께 확인해야 합니다. 특히 기존 값이 남아 있는 컬럼을 먼저 삭제하거나 타입 코드만 클래스 이름으로 바꾸는 SQL은 데이터 이관을 완성하지 못합니다.

이 글은 Batch 5로의 전환을 다룹니다. 현재 최신 주 버전의 도입 안내는 아닙니다. [5.0 공식 이관 가이드](https://github.com/spring-projects/spring-batch/wiki/Spring-Batch-5.0-Migration-Guide)를 기준으로 변경 범위를 정리하고, 아래 예제는 Batch 5 환경에서 실행 동작을 검사합니다.

## 처리 흐름

![v5 실패 인스턴스 재시작 흐름도](/assets/diagrams/2023-10-27-springbatch5-migration-ko.svg)

새 스키마에서 실행한 v5 재시작 테스트 흐름입니다. v4 DB 이관이 아니며 같은 인스턴스의 새 실행은 실패한 Step을 다시 수행합니다.

## 기존 저장소를 바꾸기 전에

Batch 5는 Java 17 이상을 요구합니다. Java EE API의 `javax.*`는 해당 Jakarta API로 옮기되, Java SE의 `javax.sql.DataSource`까지 일괄 치환하지 않습니다.

파라미터 테이블의 이전 `TYPE_CD`와 타입별 값 컬럼은 새로운 `PARAMETER_TYPE`·`PARAMETER_VALUE` 표현과 다릅니다. `LONG`을 `java.lang.Long`으로 바꾸는 것만으로 기존 LONG·DOUBLE·DATE 값의 보존과 재해석이 해결되지는 않습니다. 대상 DB와 Batch 버전에 맞는 변환 절차를 복제 DB에서 확인해야 합니다. DB별 초기 스키마와 이관 스크립트는 [Core JAR 안의 경로](https://docs.spring.io/spring-batch/reference/5.2/schema-appendix.html)를 확인하세요. 새 스키마 생성 스크립트를 기존 운영 테이블에 재실행하는 절차로 대체하면 안 됩니다.

[공식 가이드의 이력 접근 제한](https://github.com/spring-projects/spring-batch/wiki/Spring-Batch-5.0-Migration-Guide#historical-data-access-implications)도 중요합니다. v4 실행 기록은 v5의 일부 JobExplorer 조회에서 읽기 실패가 생길 수 있습니다. 실패한 v4 인스턴스는 이관 전에 v4에서 성공하도록 재시작하거나 업무 판단을 거쳐 abandon 처리하는 것을 전제로 합니다. v5에서 기존 실패 작업을 그대로 재시작할 수 있다고 가정하지 마세요. 파라미터 외에도 실행 컨텍스트 직렬화 방식의 호환성을 별도로 확인해야 합니다.

## 시작 상태에 맞는 이관 경로 고르기

- **기존 Batch 4 저장소:** 백업 후 DB 복사본에서 스키마·파라미터·실행 컨텍스트 변환을 예행하고, 실패한 v4 인스턴스는 v4에서 처리합니다. 아래 예제는 v4 저장소를 변환하거나 재시작하지 않습니다.
- **새 Batch 5 저장소:** 타입별 파라미터·완료 인스턴스·실패 Step 테스트를 실행합니다. 새 H2 스키마의 세 동작을 한 프로세스에서 확인합니다.
- **Batch Job이 있는 Boot 애플리케이션:** Boot와 명시적 Batch 구성 중 누가 설정과 스키마 초기화를 맡을지 정합니다. 예제는 Boot 자동 구성 대신 명시적 Spring 구성을 사용합니다.

Boot 주 버전도 함께 바꾼다면 저장소 이관과 별도로 [Java·Jakarta 마이그레이션 기준선](/ko/posts/2023-09-08-springboot3-migration/)부터 확인하세요.

## 새 Batch 5 저장소에서 동작 확인하기

재현 환경은 Gradle 8.4/JDK 17.0.8.1, Boot BOM 3.5.7이 관리하는 Batch 5.2.4와 H2 2.3.232입니다. 이 버전은 실행 근거를 고정하기 위한 것으로 현재 운영 버전 추천이 아닙니다. 빈 디렉터리에 아래 세 파일을 저장합니다.

이 프로젝트는 Boot 애플리케이션이 아니라 Spring의 테스트 컨텍스트를 직접 만듭니다. `@EnableBatchProcessing`을 사용하고, 그 컨텍스트에 DataSource와 트랜잭션 매니저를 제공합니다. `DefaultBatchConfiguration`을 함께 상속하지 않습니다. [Java 구성 문서](https://docs.spring.io/spring-batch/reference/5.2/job/java-config.html)의 두 구성 방식 중 하나를 고르는 예제입니다.

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

## 실행 결과와 확인 범위

```sh
gradle --no-daemon clean test
```

세 테스트는 새 H2 스키마에서 파라미터 타입과 값을 저장하는지, 완료된 인스턴스가 같은 식별 파라미터의 재실행을 거부하는지, 실패 후 같은 인스턴스의 새 실행이 실패한 Step만 다시 수행하는지 검사합니다. 재시작 사례의 실행 횟수는 첫 Step 1회·둘째 Step 2회입니다. 같은 프로세스의 카운터로 관찰하므로 JVM 재시작이나 외부 부수 효과의 정확히 한 번 처리를 증명하지 않습니다.

이 예제는 **v4 DB를 v5로 변환하지 않습니다.** 운영 이관에서는 백업과 복구 방법을 먼저 확보하고, 복제 DB에서 타입별 값·이력 조회·실행 컨텍스트·업무 재시작 절차를 점검해야 합니다. 통과한 새 스키마 테스트를 기존 데이터 호환성의 증거로 대신할 수 없습니다.

Boot 애플리케이션에 이 구성을 적용할 때는 주의할 점이 하나 더 있습니다. [Boot의 Batch 안내](https://docs.spring.io/spring-boot/3.5/how-to/batch.html)에 따르면 `@EnableBatchProcessing` 또는 `DefaultBatchConfiguration`으로 직접 구성하면 Batch 자동 구성과 스키마 초기화 지원이 비활성화됩니다. 기존 Boot 자동 구성을 유지할지 직접 구성할지 먼저 정하세요.

런타임 전환의 다른 확인 항목은 [JDK 21 기능과 Preview 구분](/ko/posts/2023-09-20-jdk-21-release/)에서, 설정 파일의 타입 검사는 [셸에서 YAML 포트 읽기](/ko/posts/2021-07-27-parse-yaml/)에서 이어서 볼 수 있습니다.
