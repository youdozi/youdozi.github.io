---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2023-09-07-springboot-initializer",
  "routeSlug": "2023-09-07-springboot-initializer",
  "kind": "post",
  "title": "Spring Initializr で Gradle プロジェクトを作成してテストする",
  "description": "Spring Boot プロジェクトを生成し、Java と Gradle の設定を調べ Wrapper でテストする。動作する Boot 4.1.2 の主要ファイルも掲載する。",
  "categories": [
    "springboot"
  ],
  "tags": [
    "springboot",
    "springboot initializer"
  ],
  "sourcePath": "src/content/posts/en/2023-09-07-springboot-initializer.md",
  "sourceSha256": "97a876012a6c3d2dbf40856ed6360dc850f12741aecbd5ee7bd96023fb05275f",
  "draftSha256": "1949e36c36428aad5407162ae219432807b7bc94e36168a06ac8c33c4a4b04d5",
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

Spring Initializr でプロジェクトを作ったら、IDE に頼る前に生成された Gradle Wrapper でテストします。生成、依存解決、JDK 互換性、アプリ起動を別々に確認すると、失敗箇所を絞れます。

この例は Boot 4.1.2、Java 17、Gradle Groovy のプロジェクトで、[start.spring.io](https://start.spring.io/)により2026年10月27日に実際に生成しました。Wrapper は Gradle 9.8.2 を選択しました。サービスの既定値や提供版は変わるため、この組み合わせが常に使えるとは限りません。

## 処理の流れ

![生成、確認、テストの流れ](/assets/diagrams/technical/ja-2023-09-07-springboot-initializer.svg)

Wrapper を実行する前に完全なアーカイブを生成します。コンテキストテストと、別に起動した HTTP アプリが確認する内容は異なります。

## プロジェクトの設定を選ぶ

| 設定 | 例 | 意味 |
| --- | --- | --- |
| Project / Language | Gradle - Groovy / Java | ビルドツールとソース言語 |
| Spring Boot | 4.1.2 | 生成時に利用できた正式リリース |
| Java / Packaging | 17 / Jar | ソースのツールチェーンとパッケージ形式 |
| Group / Artifact | example / demo | プロジェクトの識別子 |
| Package name | example.demo | アプリのパッケージ |
| Dependencies | Spring Web | HTTP エンドポイント用の依存関係 |

UI の Generate を押すか、この URL でアーカイブを取得します。**各コマンドの成功を確認してから次を実行してください。** 既存のプロジェクトを上書きしないよう、空の作業ディレクトリを使います。

```sh
curl --fail --show-error --location 'https://start.spring.io/starter.zip?type=gradle-project&language=java&bootVersion=4.1.2&baseDir=demo&groupId=example&artifactId=demo&name=Demo&packageName=example.demo&packaging=jar&javaVersion=17&dependencies=web' --output demo.zip
unzip demo.zip
cd demo
./gradlew --version
./gradlew test
```

サービスがある版の提供を終えると、生成 API がその版を拒否する場合があります。[現行メタデータ](https://start.spring.io/metadata/client)と [Initializr リファレンス](https://docs.spring.io/initializr/docs/current/reference/html/)を確認し、互換性のある Boot、JDK、Gradle を組み合わせて選びます。説明なしに最新の既定値へ置き換えると再現条件が変わります。

## 生成された主要四ファイルを確認する

以下は書式を簡略化した主要四ファイルです。完全なアーカイブには Wrapper のスクリプト、JAR と設定、リソースもあります。この四ファイルだけを空のディレクトリにコピーしても `./gradlew` はできません。

### `settings.gradle`

```groovy
rootProject.name = 'demo'
```

### `build.gradle`

```groovy
plugins {
    id 'java'
    id 'org.springframework.boot' version '4.1.2'
    id 'io.spring.dependency-management' version '1.1.7'
}
group = 'example'
version = '0.0.1-SNAPSHOT'
java {
    toolchain { languageVersion = JavaLanguageVersion.of(17) }
}
repositories { mavenCentral() }
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-webmvc'
    testImplementation 'org.springframework.boot:spring-boot-starter-webmvc-test'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
tasks.named('test') { useJUnitPlatform() }
```

### `src/main/java/example/demo/DemoApplication.java`

```java
package example.demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}
```

### `src/test/java/example/demo/DemoApplicationTests.java`

```java
package example.demo;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
class DemoApplicationTests {
    @Test
    void contextLoads() {}
}
```

生成された Boot 4.1.2 は `spring-boot-starter-webmvc` と `spring-boot-starter-webmvc-test` を使います。異なる世代の断片を混ぜず、選んだリリースが生成する設定を起点にします。[Boot 4.1.2 の要件](https://docs.spring.io/spring-boot/4.1/system-requirements.html)は Java 17 以降と、Gradle 8.x（8.14 以降）または 9.x です。

## テストとアプリ起動を区別する

`contextLoads()` が通るのはテストのコンテキストが起動するという意味です。まだコントローラーがなければ、`/` の 404 は起動失敗を意味しません。アプリを別に実行し、その端末で Ctrl+C を押して止めます。

```sh
./gradlew bootRun
```

生成された `build.gradle` と [Gradle Wrapper のファイル](https://docs.gradle.org/current/userguide/gradle_wrapper.html)を一緒にコミットします。Gradle の版は `java.toolchain` の Java バージョンとは別です。`./gradlew --version` で Gradle を動かす JVM を調べ、コンパイルやアプリ実行に選ぶ JDK と区別します。

続いて [IntelliJ でプロジェクトを開き HTTP を提供する手順](/en/posts/2023-09-10-springboot-intellij-import/)へ進みます。Boot と Framework の版番号が異なる理由は [Spring Boot のリリース履歴とバージョン関係](/en/posts/2023-09-13-springboot-history/)を参照してください。
