---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2026-11-09-spring-mvc-webclient-execution",
  "routeSlug": "2026-11-09-spring-mvc-webclient-execution",
  "kind": "post",
  "title": "Spring MVC の WebClient：.block() と Mono 返却時のスレッド",
  "description": "Spring MVC と Reactor Netty の役割を分け、実際の Tomcat 例で WebClient の .block()、Mono 返却、仮想スレッドを比較します。",
  "categories": [
    "springboot"
  ],
  "tags": [
    "spring-mvc",
    "webclient",
    "reactor-netty",
    "servlet-async",
    "virtual-threads"
  ],
  "sourcePath": "src/content/posts/en/2026-11-09-spring-mvc-webclient-execution.md",
  "sourceSha256": "6f81dd9e98a391f7b05ca1d0fef8c01ca8288550531caf852ae518c60843dba8",
  "draftSha256": "b9650ece5ad04e4f0adb9be4c9b33d702ef86c02b7fc4d27da7e29c83ddabfcd",
  "manifestPath": ".pipeline/technical-translations/batch-156/manifest.json",
  "manifestSha256": "ed48dc20825daff8725d8eba3418b1ad885276b52c9752ba958f7a1705b24430",
  "publishedAt": "2026-11-14T15:16:43.783Z",
  "updatedAt": "2026-11-14T15:16:43.783Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 158,
    "approvedAt": "2026-11-14T15:16:43.783Z",
    "basis": "User requested all 63 language editions and instructed completed PRs to be merged; AI translation and independent AI review were performed, with no claim of human text review."
  }
}
---

**Spring MVC でも WebClient はノンブロッキング HTTP 通信を使えますが、コントローラーで `.block()` を呼ぶと MVC リクエストスレッドは結果を待ちます。** `Mono` を返せば MVC が Servlet 非同期処理に適応し、初期リクエストスレッドを解放できます。クライアント通信とサーバーのリクエスト処理は別の責務です。

対象は **Tomcat 上の Spring MVC と Reactor Netty を使う WebClient** です。別の HTTP コネクターではスレッド名や資源が異なる場合があります。例は Spring Boot 3.5.16、JDK 21、Gradle 8.14.3 で再現し、現在の Boot 全リリースを検証したものではありません。

## WebClient を追加するとサーバーも WebFlux になるか？

サーバー側 MVC と外部呼び出し用 WebClient の役割は異なります。ここでは Tomcat と `DispatcherServlet` が受信要求を、WebClient の Reactor Netty コネクターが送信 HTTP を扱います。

Boot 3.5 では `spring-boot-starter-web` と `spring-boot-starter-webflux` を両方追加するとデフォルトで MVC が選択されます。WebClient のために WebFlux starter を加えるアプリを支援する動作です。アプリ種別を明示的に変えた場合や別のサーバー設定では個別に確認します。[Boot の MVC と WebFlux の選択](https://docs.spring.io/spring-boot/3.5/reference/web/reactive.html#web.reactive.webflux)

## `.block()` と `Mono` の返却はどこで分かれるか？

![block 経路では Servlet リクエストスレッドが待つ間に Netty が HTTP 通信を処理する。Mono 返却経路では MVC が購読した後、Netty 通信と Servlet 非同期処理が重なり、MVC が結果を再ディスパッチする。](/assets/diagrams/technical/ja-2026-11-09-spring-mvc-webclient-execution.svg)

緑は Servlet と MVC、青は Reactor Netty の役割です。非同期経路の二つの分岐は重なり得るため、外部応答が初期リクエストスレッドの返却後に必ず到着するわけではありません。図は成功信号を中心に示し、コードのエラー信号は HTTP ステータスに変換されてから MVC のエラー処理へ進みます。

| 段階 | `.block()` 後に値を返す | `Mono` を返す |
| --- | --- | --- |
| 購読 | `.block()` が実行 | MVC が返却型を購読 |
| 外部 HTTP の待機中 | リクエストスレッドが待機 | Servlet 非同期処理により初期スレッドを返せる |
| 応答本文の受信後 | クライアントのコールバックが結果を渡して待機を解除 | 結果信号を MVC の非同期処理へ渡す |
| 最終 HTTP 応答 | MVC が戻り値をシリアライズして書き込む | MVC が再ディスパッチ後にシリアライズして書き込む |

`retrieve().bodyToMono(...)` はリクエストのパイプラインを組み立てます。以下の新しい WebClient パイプラインは、購読されて初めて HTTP リクエストを開始します。二回購読すると再びリクエストが発生し得るため、`.block()` で一度読み取ってから同じパイプラインを返すコードに注意します。

MVC は単一値 `Mono` を `DeferredResult` と同様に適応します。結果が準備できると Servlet コンテナへ再ディスパッチして応答を完了します。プールは同じスレッドを再利用し得るため、再ディスパッチのスレッドが初期スレッドと必ず異なるとは限りません。応答が開いている間は接続と非同期リクエストの資源も残ります。`Mono` を返しても Servlet 応答の書き込み全体がノンブロッキングになるわけではありません。この例は単一値 JSON であり、ストリーミングや SSE とは異なります。[MVC 非同期処理と reactive 戻り値](https://docs.spring.io/spring-framework/reference/6.2/web/webmvc/mvc-ann-async.html)

## 同じ外部 API を二つの方法で呼び出す

以下のファイルを同じプロジェクトに保存します。Boot Gradle プラグインではなく `application` プラグインを使い、Java toolchain を 21 に固定します。ローカル検証は Azul JDK 21.0.1 で行いました。この過去のパッチ版を新しい本番環境に推奨するものではありません。

### `settings.gradle`

```groovy
rootProject.name = 'mvc-webclient-execution'
```

### `build.gradle`

```groovy
plugins {
    id 'java'
    id 'application'
}
repositories { mavenCentral() }
java { toolchain { languageVersion = JavaLanguageVersion.of(21) } }
dependencies {
    implementation platform('org.springframework.boot:spring-boot-dependencies:3.5.16')
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.boot:spring-boot-starter-webflux'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
application { mainClass = 'example.DemoApplication' }
test {
    useJUnitPlatform()
    systemProperty 'demo.virtual', providers.gradleProperty('virtual').getOrElse('false')
}
```

### `src/main/resources/application.yml`

```yaml
upstream:
  base-url: http://127.0.0.1:9091
  timeout: 3s
spring:
  mvc:
    async:
      request-timeout: 5s
```

`WebClient` は bean として再利用し、Reactor Netty コネクターを明示します。例の `HttpClient.create()` はデフォルトの共有イベントループと接続プールを使い、外部要求ごとに専用 Netty スレッドを作るわけではありません。`callbackThread` は応答本文の生成後に `map` を実行するスレッドであり、最終 Servlet 応答を書き込むスレッドとは限りません。ここでは `publishOn` のようなスケジューラー切り替えは加えていません。[WebClient コネクターと共有資源](https://docs.spring.io/spring-framework/reference/6.2/web/webflux-webclient/client-builder.html)

### `src/main/java/example/DemoApplication.java`

```java
package example;

import java.time.Duration;
import java.util.concurrent.TimeoutException;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.http.HttpStatus;
import org.springframework.http.client.reactive.ReactorClientHttpConnector;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;
import org.springframework.web.server.ResponseStatusException;

import reactor.core.publisher.Mono;
import reactor.core.scheduler.Schedulers;
import reactor.netty.http.client.HttpClient;

@SpringBootApplication
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }

    @Bean
    WebClient upstreamClient(WebClient.Builder builder,
                             @Value("${upstream.base-url}") String baseUrl) {
        return builder.baseUrl(baseUrl)
                .clientConnector(new ReactorClientHttpConnector(HttpClient.create()))
                .build();
    }

    public record Observation(String mode, String requestThread, boolean requestVirtual,
                              String callbackThread, boolean callbackVirtual, boolean callbackNonBlocking,
                              String value) {}

    @RestController
    static class DemoController {
        private final WebClient client;
        private final Duration deadline;

        DemoController(WebClient client, @Value("${upstream.timeout}") Duration deadline) {
            this.client = client;
            this.deadline = deadline;
        }

        private Mono<Observation> fetch(String mode) {
            Thread request = Thread.currentThread();
            String name = request.getName();
            boolean virtual = request.isVirtual();
            return client.get().uri("/value").retrieve().bodyToMono(String.class)
                    .timeout(deadline)
                    .map(value -> new Observation(mode, name, virtual,
                            Thread.currentThread().getName(), Thread.currentThread().isVirtual(),
                            Schedulers.isInNonBlockingThread(), value))
                    .onErrorMap(WebClientResponseException.class, error ->
                            new ResponseStatusException(HttpStatus.BAD_GATEWAY,
                                    "upstream HTTP error", error))
                    .onErrorMap(TimeoutException.class, error ->
                            new ResponseStatusException(HttpStatus.GATEWAY_TIMEOUT,
                                    "upstream deadline", error));
        }

        @GetMapping("/block")
        Observation blocking() {
            return fetch("block").block();
        }

        @GetMapping("/async")
        Mono<Observation> asynchronous() {
            return fetch("async");
        }
    }
}
```

`/block` は比較用の経路です。非同期返却で完了できるコントローラーは `/async` のように結果の `Mono` を返し、MVC に購読させられます。`.subscribe()` を直接呼んで先に応答すると、外部呼び出しの結果とエラーは元の HTTP リクエストから切り離されます。[同期的な WebClient の利用とコントローラーの返却](https://docs.spring.io/spring-framework/reference/web/webflux-webclient/client-synchronous.html)

例の三秒の `timeout` は購読から値が届くまでの区間を制限します。接続プールの取得、接続、各応答読み取りのタイムアウトを別々に設定したものではありません。HTTP エラーは 502、パイプラインのタイムアウトは 504 に変換します。接続失敗、空の応答本文、業務エラーの契約は別途決めます。`retrieve()` はデフォルトで HTTP 4xx と 5xx をエラーとして扱います。[retrieve のエラー処理](https://docs.spring.io/spring-framework/reference/6.2/web/webflux-webclient/client-retrieve.html)

### ローカルで実行する

外部サービスの代わりにローカルの Python 3 HTTP サーバーを起動します。`/value` は 0.2 秒後に `hello` を返します。この遅延は動作観察用の入力であり性能測定ではありません。

### `upstream.py`

```python
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from time import sleep


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != '/value':
            self.send_error(404)
            return
        sleep(0.2)
        body = b'hello'
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


ThreadingHTTPServer(('127.0.0.1', 9091), Handler).serve_forever()
```

最初の端末で実行します。

```sh
python3 upstream.py
```

二つ目の端末で JDK 21 を選び、Gradle 8.14.3 で実行します。

```sh
gradle run
```

三つ目の端末で両方の経路を呼び出します。

```sh
curl --fail --show-error --silent http://127.0.0.1:8080/block
curl --fail --show-error --silent http://127.0.0.1:8080/async
```

両方とも `hello` を含む JSON を返します。通常のリクエストスレッドでは `requestVirtual=false`、この例の Netty コールバックでは `callbackVirtual=false`、`callbackNonBlocking=true` を観測しました。スレッド名と番号は実行ごとに変わります。応答 JSON の `mode` だけでは、待機中にリクエストスレッドが解放されたことは証明できません。

## 仮想スレッドを有効にすると何が変わるか？

先ほどのアプリを停止し、同じコードを仮想スレッド設定で再実行します。

```sh
gradle run --args='--spring.threads.virtual.enabled=true'
```

この設定では両経路の `requestVirtual` が `true` になりました。`.block()` 経路では呼び出し元の仮想スレッドが依然として結果を待ちますが、通常 park 可能な待機はキャリアのプラットフォームスレッドを占有し続けることとは異なります。pinning と実行中の JDK の違いは別途確認します。[JDK 21 の仮想スレッドのスケジューリングと pinning](https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html) **仮想スレッドを有効にしても、この例の Reactor Netty コールバックは仮想スレッドになりませんでした。** [Boot の仮想スレッド設定](https://docs.spring.io/spring-boot/3.5/reference/features/spring-application.html#features.spring-application.virtual-threads)

仮想スレッドは外部サービスの処理能力、HTTP 接続数、DB 接続数を増やしません。蓄積するリクエストの上限は、[DB セマフォアと入場制御](/ko/posts/2026-11-03-virtual-threads-db-semaphore/)のように別途設計します。

## コールバック内で JDBC を呼んでもよいか？

MVC から WebClient を呼んだからといって、その後の `map` も MVC リクエストスレッドで動くとは限りません。この例の `map` に JDBC クエリや長いファイル読み取りを入れると、Netty のイベントループをブロックすることがあります。逆に、すべての `Mono` が専用スレッドで動くわけでもありません。オペレーターの実行位置は購読、信号、スケジューラー切り替えに依存します。[Reactor のスレッドとスケジューラー](https://projectreactor.io/docs/core/release/reference/coreFeatures/schedulers.html)

同期処理が多いサービスでは、MVC の同期呼び出しフローで資源上限を設ける方法と、非同期チェーンを維持してブロッキング処理を別の実行器へ隔離する方法を比較します。単純な同期 HTTP 呼び出しについては [RestClient と WebClient の選択](/ko/posts/2026-10-31-webclient-restclient-comparison/)も参照できます。スケジューラーの切り替えだけでは DB や下流サービスの過負荷は解決しません。

## 実際に検証した範囲

[検証テスト](https://github.com/youdozi/youdozi.github.io/blob/main/.pipeline/drafts/2026-11-09-spring-mvc-webclient-execution/src/test/java/example/ExecutionTest.java)はランダムポートの**実 Tomcat とローカル HTTP サーバー**で実行しました。通常のリクエストスレッドと仮想スレッドで各八件、計十六件が通過しました。

- 両 starter がある場合の Servlet コンテキスト、Tomcat、DispatcherServlet の選択
- パイプラインの組み立て時には要求せず、購読と再購読で要求すること
- 外部応答を保留した状態での `.block()` の要求スレッド待機と `Mono` の Servlet 非同期処理への移行
- リクエストスレッドが仮想か、応答コールバックがノンブロッキングまたは仮想か
- 両経路の HTTP エラーを 502、パイプラインタイムアウトを 504 に変換

自分でテストを実行するには、上記の検証コードを `src/test/java/example/ExecutionTest.java` に保存して実行します。

```sh
gradle clean test
gradle test -Pvirtual=true --rerun-tasks
```

テストは応答を保留する latch で状態を観測し、短い実行時間から非同期と推測しません。スループット比較、実際の外部サービス、DB や TLS、クライアント切断、遠隔の副作用の取り消しは検証していません。特にパイプラインのキャンセルは、遠隔サーバーの処理中止やトランザクションのロールバックを保証しません。
