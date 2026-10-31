---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2023-10-27-springbatch5-migration",
  "routeSlug": "2023-10-27-springbatch5-migration",
  "kind": "post",
  "title": "Spring Batch 5 移行：スキーマ、ジョブパラメーター、再実行",
  "description": "Spring Batch 5 のスキーマとジョブパラメーター移行を計画し、新規 H2 で型付きパラメーター、完了済みインスタンス、失敗 Step の再実行をテストする。",
  "categories": [
    "spring"
  ],
  "tags": [
    "spring batch 5",
    "migration"
  ],
  "sourcePath": "src/content/posts/en/2023-10-27-springbatch5-migration.md",
  "sourceSha256": "688dd3a4a3f176f0d94406dbc3c73979ece0d8a4e0f23ca31a65de298e922d77",
  "draftSha256": "d571b028238562b7c32a30c45d762374c30b1baa1bfa835a9cc78e034490f2da",
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

Spring Batch 5 への移行では、依存に加え、メタデータのスキーマ、保存済みジョブパラメーター形式、実行コンテキスト、再実行方針を確認します。値のある列を先に落としたり、型コードだけをクラス名に変えたりしても移行は完了しません。

本記事は最新メジャー版の採用ではなく Batch 5 への移行を扱います。[公式 5.0 移行ガイド](https://github.com/spring-projects/spring-batch/wiki/Spring-Batch-5.0-Migration-Guide)が論点を定め、以下の例は Batch 5 での実行動作を確認します。

## 処理の流れ

![失敗した v5 インスタンスを再実行する流れ](/assets/diagrams/technical/ja-2023-10-27-springbatch5-migration.svg)

これは新規スキーマの v5 再実行テストで、v4 DB の移行ではありません。同じインスタンスの二回目は失敗 Step を再実行し、完了済み Step は完了のままです。

## 既存リポジトリを変える前に

Batch 5 は Java 17 以降を必要とします。Java EE の `javax.*` API を対応する Jakarta に移し、`javax.sql.DataSource` のような Java SE API は置き換えません。

旧表の `TYPE_CD` と型別の値の列は、新しい `PARAMETER_TYPE`、`PARAMETER_VALUE` の表現とは異なります。`LONG` を `java.lang.Long` に変えるだけでは既存の LONG、DOUBLE、DATE を保持、正しく解釈し直せません。対象 DB と Batch 版でコピー上の変換を演習し、[Core JAR の DB 別スキーマと移行スクリプト](https://docs.spring.io/spring-batch/reference/5.2/schema-appendix.html)を探します。本番表で新規作成スクリプトを再実行するのは移行の代わりになりません。

公式ガイドには[履歴データのアクセス制限](https://github.com/spring-projects/spring-batch/wiki/Spring-Batch-5.0-Migration-Guide#historical-data-access-implications)もあり、一部の v5 JobExplorer は v4 実行の読込で失敗する場合があります。失敗した v4 インスタンスは移行前に v4 で再実行を成功させるか、業務判断で破棄する前提です。v5 が既存の失敗 v4 を直接再実行できるとは考えないでください。コンテキストの直列化互換性はパラメーター変換と別に調べます。

## 移行の出発点を選ぶ

- **既存 Batch 4 リポジトリ：** バックアップし、コピーでスキーマ、パラメーター、コンテキスト変換を演習します。失敗した v4 は v4 で処理します。以下の例は v4 を変換、再実行しません。
- **新規 Batch 5 リポジトリ：** 型付きパラメーター、完了済みインスタンス、失敗 Step をテストします。単一プロセスの新規 H2 で三動作を確認します。
- **Batch ジョブを持つ Boot アプリ：** 準備とスキーマ初期化を Boot か明示的 Batch 設定のどちらが担うか決めます。例は Boot 自動設定でなく明示的 Spring 設定です。

Boot のメジャー更新も伴うなら、リポジトリ移行とは別に [Java と Jakarta の移行基準](/en/posts/2023-09-08-springboot3-migration/)を作ります。

## 新規 Batch 5 リポジトリの動作を確認する

再現は Gradle 8.4/JDK 17.0.8.1 と、Batch 5.2.4、H2 2.3.232（Boot BOM 3.5.7 管理） です。実行証拠を固定した版で、現在の本番推奨ではありません。空のディレクトリに次の三ファイルを保存します。

Boot を起動せず Spring テストコンテキストを直接作ります。`@EnableBatchProcessing` と独自の DataSource、トランザクションマネージャーを使い、`DefaultBatchConfiguration` は同時に継承しません。[Java 設定文書](https://docs.spring.io/spring-batch/reference/5.2/job/java-config.html)では代替の方法とされています。

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

## 確認を実行し結果を読む

```sh
gradle --no-daemon clean test
```

三件は新規 H2 の型付きパラメーター保存、同じ識別パラメーターでの完了済みインスタンス拒否、同じ失敗インスタンスの新実行で失敗 Step だけを再実行することを確認します。第一 Step は一回、第二 Step は二回動きます。カウンターは一プロセス内なので JVM 再起動復旧や外部効果の exactly-once は証明しません。

この例は **v4 DB を v5 に変換しません**。本番移行では先にバックアップと復旧を整え、コピーで型別値、履歴アクセス、コンテキスト、業務上の再実行を確認します。新規スキーマの成功は既存データとの互換性を証明しません。

Boot に適用する際は、[Boot Batch ガイド](https://docs.spring.io/spring-boot/3.5/how-to/batch.html)のとおり、`@EnableBatchProcessing` の追加または `DefaultBatchConfiguration` の継承で Batch 自動設定とスキーマ初期化が無効になります。Boot に任せるか直接管理するか決めます。

関連する実行環境の判断は [JDK 21 の正式機能とプレビュー](/en/posts/2023-09-20-jdk-21-release/)、型付き設定入力は [シェルから YAML のポートを読む手順](/en/posts/2021-07-27-parse-yaml/)を参照してください。
