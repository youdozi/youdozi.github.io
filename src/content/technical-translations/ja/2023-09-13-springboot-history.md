---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2023-09-13-springboot-history",
  "routeSlug": "2023-09-13-springboot-history",
  "kind": "post",
  "title": "Spring Boot のリリース履歴と Spring Framework の版の対応",
  "description": "Spring Boot 1.2 から 4.0 の主な版をたどり、Boot と Framework、Starter、BOM を区別して、解決された依存版を調べる。",
  "categories": [
    "springboot"
  ],
  "tags": [
    "springboot",
    "history"
  ],
  "sourcePath": "src/content/posts/en/2023-09-13-springboot-history.md",
  "sourceSha256": "8f97cfe96eb4ed1a36dae63a187c6f28960c327ff6cba276c45537a1e7745da2",
  "draftSha256": "95f0f87e56134e312322b0c843b6636b810580ffeaf2246d66fd339e09695aca",
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

Spring Boot と Spring Framework は、異なる版番号を持つ別のプロジェクトです。Boot は Framework に自動設定、依存管理、実行可能なパッケージ化を加えます。Boot 3.1 を Framework 6.1 と読むのは不確実なので、選んだ Boot の BOM と解決済み依存グラフを確認します。

## 処理の流れ

![実際のコンポーネントの版を調べる流れ](/assets/diagrams/technical/ja-2023-09-13-springboot-history.svg)

図はリリース年表ではなく依存確認を示します。Boot、Framework、Lombok は、それぞれ版と依存設定が別です。

## 主な正式リリースの変更

この年表はすべてのリリースではなく機能の変化を示します。最初の正式版と、その後のパッチで拡大された JDK 対応を区別します。

| Spring Boot | 最初の正式版 | 主な変更と公式発表 |
| --- | --- | --- |
| 1.2 | 2014-12-11 | [`@SpringBootApplication` と Servlet 3.1 対応](https://spring.io/blog/2014/12/11/spring-boot-1-2-0-released/) |
| 1.3 | 2015-11-16 | [DevTools、キャッシュ自動設定、直接実行可能な JAR](https://spring.io/blog/2015/11/16/spring-boot-1-3-0-released/) |
| 1.4 | 2016-07-28 | [起動失敗分析とテスト支援の改善](https://spring.io/blog/2016/07/28/spring-boot-1-4-released/) |
| 2.0 | 2018-03-01 | [Framework 5.0、Java 8 基準、リアクティブ Web 対応](https://spring.io/blog/2018/03/01/spring-boot-2-0-goes-ga/) |
| 3.0 | 2022-11-24 | [Framework 6.0、Java 17 基準、Jakarta、ネイティブイメージ](https://spring.io/blog/2022/11/24/spring-boot-3-0-goes-ga/) |
| 3.1 | 2023-05-18 | [開発時の Testcontainers と Docker Compose 統合](https://spring.io/blog/2023/05/18/spring-boot-3-1-0-available-now/) |
| 3.2 | 2023-11-23 | [仮想スレッド、RestClient、JdbcClient 対応](https://spring.io/blog/2023/11/23/spring-boot-3-2-0-available-now/) |
| 4.0 | 2025-11-20 | [Framework 7、モジュール化、JSpecify、API バージョニング](https://spring.io/blog/2025/11/20/spring-boot-4-0-0-available-now/) |

たとえば [Boot 3.1.0 の管理依存一覧](https://docs.spring.io/spring-boot/docs/3.1.0/reference/html/dependency-versions.html)は `spring-core` 6.0.9 を指定します。Boot と Framework のマイナー番号が一致する必要はありません。Boot 2.4 を存在しない Framework 5.4 系列へ対応させるのも誤りです。

## Starter、BOM、ビルドプラグイン

Starter は機能に必要な依存をまとめます。BOM は版を管理し、一覧の全ライブラリを自動でプロジェクトに追加はしません。Boot のビルドプラグインは `bootRun` などのタスクと実行可能 JAR の作成を提供します。

Gradle 向けの [Boot 依存管理ガイド](https://docs.spring.io/spring-boot/4.1/gradle-plugin/managing-dependencies.html)は依存管理プラグインとネイティブ BOM 対応を説明します。Boot プラグインの適用だけで全 Gradle 設定が版なしの依存を受け付けるとは限りません。注釈プロセッサーなど別の設定も確認します。

## プロジェクトの実際の版を調べる

[Initializr](/en/posts/2023-09-07-springboot-initializer/) と [Lombok ガイド](/en/posts/2023-09-15-springboot-intellij-lombok/)の完成したプロジェクトで次を実行します。

```sh
./gradlew dependencyInsight --configuration runtimeClasspath --dependency spring-core
./gradlew dependencyInsight --configuration annotationProcessor --dependency lombok
```

ローカルの例は Boot 4.1.2、`spring-core` 7.0.10、Lombok 1.18.48 に解決されます。番号が違うのはプロジェクトが別だからです。`dependencyInsight` は選択版とその依存経路や規則を示すため、競合調査に役立ちます。これはこの例の記録であり、将来の既定値や全プロジェクト共通の組み合わせではありません。

年表は現在のサポート期間表ではありません。作成や更新時は、選ぶ版の要件、依存互換性、サポート方針を別に確認します。[Java 17 と Jakarta の移行](/en/posts/2023-09-08-springboot3-migration/)で Boot 3 への手順を確認し、ローカル実行は [IntelliJ と Gradle の実行確認](/en/posts/2023-09-10-springboot-intellij-import/)を参照してください。
