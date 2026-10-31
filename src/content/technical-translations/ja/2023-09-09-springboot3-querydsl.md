---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2023-09-09-springboot3-querydsl",
  "routeSlug": "2023-09-09-springboot3-querydsl",
  "kind": "post",
  "title": "Spring Boot 3 と Querydsl：Jakarta 設定と Q 型生成",
  "description": "Jakarta 依存関係と注釈処理をそろえて Spring Boot 3 で Querydsl Q 型を生成し、クリーンビルドと H2 クエリテストで確認する。",
  "categories": [
    "springboot"
  ],
  "tags": [
    "springboot",
    "springboot3",
    "querydsl"
  ],
  "sourcePath": "src/content/posts/en/2023-09-09-springboot3-querydsl.md",
  "sourceSha256": "17f0353d5a048f80291207543b7abbb29e1d987ab0435009b82a4e1c16a7d953",
  "draftSha256": "7bc73038e32fd8a9b7c649dbbffe1bb49b465c60e6d4186feabd58e298fe48ca",
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

Spring Boot 3 で Querydsl JPA の Q 型を生成するには、`querydsl-jpa` と `querydsl-apt` の版と `jakarta` 分類子をそろえ、注釈処理を設定してクリーンビルドと DB クエリテストを確認します。Querydsl の [5.0 リリースノート](https://github.com/querydsl/querydsl/releases/tag/QUERYDSL_5_0_0)に Jakarta 分類子対応が記載されています。Gradle 既定の生成パスを使えば、main と test のコンパイルが同じディレクトリへ書く設定を避けられます。

このガイドは 2023 年の韓国語の例を実行可能な設定に発展させたものです。以下の版は再現環境を固定するもので、現在の本番依存関係の推奨ではありません。

## 処理の流れ

![Q 型を生成してクエリを実行する流れ](/assets/diagrams/technical/ja-2023-09-09-springboot3-querydsl.svg)

main のコンパイル時にプロセッサーが QEmployee を生成します。その後、H2 テストが生成した型でクエリを実行します。

## 再現環境と完全な Gradle 設定

| コンポーネント | 再現バージョン |
| --- | --- |
| JDK / Gradle | 17.0.8.1 / 8.4 |
| Spring Boot BOM | 3.5.7 |
| Querydsl JPA / APT | 5.1.0、両方とも `jakarta` 分類子 |
| Hibernate / H2 | 6.6.33.Final / 2.3.232、BOM が管理 |

新しいディレクトリにこの五ファイルを作ります。テストプロジェクトは Java プラグインと Boot BOM を使い、Boot Gradle プラグインは不要です。既存の Boot アプリでは、選択済みの依存管理に必要な依存だけを追加します。

### `settings.gradle`

```groovy
rootProject.name = 'querydsl-jakarta-example'
```

### `build.gradle`

```groovy
plugins { id 'java' }
repositories { mavenCentral() }
dependencies {
    implementation platform('org.springframework.boot:spring-boot-dependencies:3.5.7')
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    implementation 'com.querydsl:querydsl-jpa:5.1.0:jakarta'

    annotationProcessor platform('org.springframework.boot:spring-boot-dependencies:3.5.7')
    annotationProcessor 'com.querydsl:querydsl-apt:5.1.0:jakarta'
    annotationProcessor 'jakarta.persistence:jakarta.persistence-api'
    annotationProcessor 'jakarta.annotation:jakarta.annotation-api'

    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testRuntimeOnly 'com.h2database:h2'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
test { useJUnitPlatform() }
```

Gradle は `annotationProcessor` を通常のコンパイル、実行時クラスパスとは別に解決します。そのため例ではプロセッサー設定にも BOM を適用し、Jakarta Persistence と Annotation API を明示的に与えます。`implementation` の依存は自動ではプロセッサーに渡りません。[Gradle Java プラグインの文書](https://docs.gradle.org/current/userguide/java_plugin.html)を参照してください。

## アプリとエンティティを作る

アプリのクラスにより JPA テストが Boot 設定を見つけられます。別のサーバープロセスを起動する必要はありません。

### `src/main/java/example/Application.java`

```java
package example;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

### `src/main/java/example/Employee.java`

```java
package example;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;

@Entity
public class Employee {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;

    public String getName() { return name; }

    protected Employee() {}

    public Employee(String name) {
        this.name = name;
    }
}
```

`Employee` は `jakarta.persistence` を使います。`QEmployee` は手書きしません。下のテストが参照する型は注釈プロセッサーが生成します。

## 生成した Q 型で問い合わせる

### `src/test/java/example/EmployeeQueryTest.java`

```java
package example;

import com.querydsl.jpa.impl.JPAQueryFactory;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.boot.test.autoconfigure.orm.jpa.TestEntityManager;

import static org.assertj.core.api.Assertions.assertThat;

@DataJpaTest
class EmployeeQueryTest {
    @Autowired
    private TestEntityManager entityManager;

    @Test
    void findsEmployeeByName() {
        entityManager.persistAndFlush(new Employee("Alice"));
        entityManager.persistAndFlush(new Employee("Bob"));
        QEmployee employee = QEmployee.employee;
        var names = new JPAQueryFactory(entityManager.getEntityManager())
            .select(employee.name).from(employee)
            .where(employee.name.eq("Alice")).fetch();
        assertThat(names).containsExactly("Alice");
    }

    @Test
    void returnsNoRowsForMissingName() {
        entityManager.persistAndFlush(new Employee("Alice"));
        QEmployee employee = QEmployee.employee;
        var names = new JPAQueryFactory(entityManager.getEntityManager())
            .select(employee.name).from(employee)
            .where(employee.name.eq("Missing")).fetch();
        assertThat(names).isEmpty();
    }
}
```

`@DataJpaTest` はこの例のクラスパス上の H2 を使います。各テストはトランザクション内で実行し、終了後にロールバックします。`persistAndFlush` で挿入した後、生成された `QEmployee` で名前の完全一致と結果が空のクエリを確認します。[Spring Boot の JPA テストガイド](https://docs.spring.io/spring-boot/3.5/reference/testing/spring-boot-applications.html#testing.spring-boot-applications.autoconfigured-spring-data-jpa-tests)を参照してください。

このテストは H2 上のこのエンティティとクエリを確認します。本番 DB の SQL 方言、照合順序、ロック、移行動作は検証しません。

## 実行して生成ファイルを確認する

JDK 17 を選び、インストール済みの Gradle 8.4 を使って、ルートから実行します。

```sh
java -version
gradle --version
gradle --no-daemon clean test
```

次の生成物とテストレポートを確認します。

```text
build/generated/sources/annotationProcessor/java/main/example/QEmployee.java
build/classes/java/main/example/QEmployee.class
build/reports/tests/test/index.html
```

この設定で両テストが成功しました。`clean test` を繰り返しても Q 型が再生成され、両方が再度通りました。既存の Gradle Wrapper があるプロジェクトでは、`./gradlew clean test` で選択済みの版を使います。

この例の Q 型は Java SE の `java.compiler` API である `javax.annotation.processing.Generated` を import します。Jakarta への置き換えは不要です。[JDK 17 Generated API](https://docs.oracle.com/en/java/javase/17/docs/api/java.compiler/javax/annotation/processing/Generated.html)。

<span id="troubleshoot-missing-or-duplicate-q-types"></span>

## Q 型が見つからない、または重複生成される理由は？

| 症状 | 最初の確認 |
| --- | --- |
| `QEmployee` がない | CLI の `clean compileJava` 結果、プロセッサー依存、エンティティの `jakarta.persistence` import。 |
| Persistence API が見つからない | 通常のクラスパスと別のプロセッサーパスに必要な Jakarta API があるか。 |
| 非互換な `javax.persistence.EntityManager` 型が出る | 両 Querydsl アーティファクトの版と Jakarta 分類子の一致。 |
| Q 型が重複、または clean 後しか通らない | 手書き Q ソースと共有生成パスを除去し、main/test 出力設定を調べる。 |
| CLI は通るが IDE で見えない | Gradle 同期、委任ビルド設定、IDE の注釈処理。 |

この例は生成ファイル用に `sourceSets`、`JavaCompile`、`clean` をカスタマイズしません。独自パスが必要なら main と test を分離します。`configureEach` は遅延タスク設定の制御であり、Jakarta 依存の互換性は直しません。[Gradle の設定回避](https://docs.gradle.org/current/userguide/lazy_configuration.html)。

更新全体の順序は [Spring Boot 3 移行ガイド](/en/posts/2023-09-08-springboot3-migration/)、外向き HTTP の境界は [WebClient と MockWebServer のテスト](/en/posts/2023-09-19-springboot-test-webclient/)を参照してください。

## クエリツールの変更前に比較する

完全な Employee クラスには getter があり、リポジトリ結果を名前で比較できます。[Querydsl と Specification の比較](/en/posts/2023-09-05-querydsl-no-release/)の三ファイルを加えると、同じエンティティで追加八件を実行できます。元の二件も計十件のプロジェクトに残ります。比較対象は選んだ H2 述語であり、全 DB 動作ではありません。[Spring Boot ガイド](/en/categories/springboot/)が前後の設定とテストをつなぎます。
