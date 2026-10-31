---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2026-10-30-webclient-timeout-retry",
  "routeSlug": "2026-10-30-webclient-timeout-retry",
  "kind": "post",
  "title": "Reactor で WebClient のタイムアウトと上限付きリトライをテストする",
  "description": "接続、応答、試行ごと、全体のタイムアウトを分けます。ローカル HTTP と Reactor の仮想時間で、HTTP 503 だけを最大 2 回再試行する GET ポリシーをテストします。",
  "categories": [
    "springboot"
  ],
  "tags": [
    "springboot",
    "webclient",
    "test",
    "reactor"
  ],
  "sourcePath": "src/content/posts/en/2026-10-30-webclient-timeout-retry.md",
  "sourceSha256": "757c2335d2f6b40391fa299791d6c6e6bade0e499c599b451be06be4eee77e3b",
  "draftSha256": "5f63bbbc87607eb3b7dc2c608d5e9afb1891a2ac20918227b0147dd3f32b35c8",
  "manifestPath": ".pipeline/technical-translations/batch-078/manifest.json",
  "manifestSha256": "e685b2de5dafd8cfff8e8e996fa2b09613becb072bdd575b58b9eca9651474a3",
  "publishedAt": "2026-10-31T02:49:44.828Z",
  "updatedAt": "2026-10-31T02:49:44.828Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 118,
    "approvedAt": "2026-10-31T02:49:44.828Z",
    "basis": "2026-10-31 user instruction “진행해줘” immediately following delivery of the reviewed 72 complete translations in PR #118; interpreted as authorization to publish exactly batch-078 in all six languages. Separate AI language review is recorded in the manifest; this does not claim a human line-by-line review. Excludes the older 120 technical drafts and 318 pending news translations."
  }
}
---
試行ごとの `timeout` を `retryWhen` の前に、全体の `timeout` をその後に配置し、再試行の待機時間も全体の予算に含めます。API 契約で許される失敗だけを再試行します。この GET の例は HTTP 503 を最大二回再試行し、タイムアウトやその他のエラーでは停止します。Spring は[トランスポートのタイムアウト](https://docs.spring.io/spring-framework/reference/6.2/web/webflux-webclient/client-builder.html)を Reactor の[Publisher のタイムアウト](https://projectreactor.io/docs/core/3.7.12/api/reactor/core/publisher/Mono.html)と分けて説明しています。

## 各設定は何を制限するか

| 設定 | この例での対象範囲 |
| --- | --- |
| `CONNECT_TIMEOUT_MILLIS` | TCP 接続の確立。DNS、プールからの取得、TLS 全体の予算ではない |
| `responseTimeout` | 応答の受信中にネットワークから読み取る間隔の最大値。本文全体の期限ではない |
| 最初の `timeout(attemptLimit)` | 本文のデコードまでを含む 一回の購読。再試行ごとに計時し直す |
| 最後の `timeout(totalLimit)` | すべての試行と再試行の待機時間を含む購読全体 |
| `StepVerifier.verify(GUARD)` | テストランナーの最大待機時間。クライアントの設定ではない |

Reactor Netty の [responseTimeout のドキュメント](https://projectreactor.io/docs/netty/1.2.11/api/reactor/netty/http/client/HttpClient.html)は読み取り間隔を説明しています。そのため、継続的にデータが届く応答の総時間は、この値を超えることがあります。外側の Publisher のタイムアウトは、全体に対する別の期限を設けます。キャンセルはこの購読を止めますが、リモートサービスがすでに行った処理は取り消しません。

## 失敗ケースを増やす前に再試行の上限を決める

![試行のタイムアウトを適用し、条件に合う 503 だけを再試行して、操作全体にも上限を設ける](/assets/diagrams/technical/ja-2026-10-30-webclient-timeout-retry.svg)

図は個々の HTTP イベントではなく、オペレーターの入れ子をまとめたものです。各試行は成功するか、エラーを通知します。再試行回数が残っている 503 エラーだけが、待機後の再購読を引き起こします。それ以外のエラーではすぐに停止します。外側のタイムアウトは実行中の試行も、再試行の待機もキャンセルできます。

[`Retry.fixedDelay(2, delay)`](https://projectreactor.io/docs/core/release/api/reactor/util/retry/Retry.html)は、最初の試行の後に 二回の再試行を許可します。一回の購読につきアプリケーションの試行は最大三回です。`.onRetryExhaustedThrow` は再試行上限のラッパー例外ではなく、最後の 503 例外を伝播します。`.disableRetry(true)` は TCP 切断時に Reactor Netty が別途行う自動再試行を無効にし、この回数に隠れたトランスポートの再試行が加わらないようにします。

この例は GET を実行し、意図的に 503 だけを再試行します。タイムアウトしても、サーバーが何もしていないとは限りません。明示的な冪等性の契約がないまま、決済やその他の書き込みにこのポリシーを流用しないでください。`Retry-After` の処理、429 の再試行、指数バックオフやジッター、呼び出し元間での再試行の調整は行いません。短い固定待機時間はテストを速くするためのものです。本番の制限とバックオフは API 契約と負荷の予算から選んでください。

## 単独で動くプロジェクトを作る

新しい空のディレクトリ、JDK 17、Gradle 8.4 を使います。Boot BOM 3.5.7 と MockWebServer 4.12.0 に固定し、[応答契約のテスト](/en/posts/2023-09-19-springboot-test-webclient/)に合わせています。これは再現用の条件であり、現時点の本番推奨バージョンではありません。最初の依存解決は Maven Central を利用し、HTTP テストはループバックだけを使います。起動済みの Boot アプリケーションや Gradle wrapper は含みません。

### `settings.gradle`

```groovy
rootProject.name = 'webclient-timeout-retry'
```

### `build.gradle`

```groovy
plugins { id 'java' }
repositories { mavenCentral() }
dependencies {
    implementation platform('org.springframework.boot:spring-boot-dependencies:3.5.7')
    implementation 'org.springframework.boot:spring-boot-starter-webflux'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testImplementation 'io.projectreactor:reactor-test'
    testImplementation 'com.squareup.okhttp3:mockwebserver:4.12.0'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
test { useJUnitPlatform() }
```

## 二つの期限を異なる位置に置く

次の実装を保存します。コンストラクターは呼び出し元が選ぶ正の期間を受け取り、テストでは値を明示します。応答のタイムアウトと 1,000 ms の TCP 接続タイムアウトは、トランスポートファクトリーの設定です。

### `src/main/java/RetryClient.java`

```java
import java.time.Duration;
import io.netty.channel.ChannelOption;
import org.springframework.http.client.reactive.ReactorClientHttpConnector;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;
import reactor.core.publisher.Mono;
import reactor.netty.http.client.HttpClient;
import reactor.util.retry.Retry;

public class RetryClient {
    private final WebClient client;
    private final Duration attemptLimit;
    private final Duration totalLimit;
    private final Duration retryDelay;

    public RetryClient(WebClient client, Duration attemptLimit,
                       Duration totalLimit, Duration retryDelay) {
        this.client = client;
        this.attemptLimit = attemptLimit;
        this.totalLimit = totalLimit;
        this.retryDelay = retryDelay;
    }

    public static WebClient transport(String baseUrl, Duration responseLimit) {
        HttpClient http = HttpClient.create()
            .disableRetry(true)
            .option(ChannelOption.CONNECT_TIMEOUT_MILLIS, 1000)
            .responseTimeout(responseLimit);
        return WebClient.builder().baseUrl(baseUrl)
            .clientConnector(new ReactorClientHttpConnector(http)).build();
    }

    public Mono<String> get() {
        return Mono.defer(() -> client.get().uri("/value")
                .retrieve().bodyToMono(String.class))
            .timeout(attemptLimit)
            .retryWhen(Retry.fixedDelay(2, retryDelay)
                .filter(error -> error instanceof WebClientResponseException response
                    && response.getStatusCode().value() == 503)
                .onRetryExhaustedThrow((spec, signal) -> signal.failure()))
            .timeout(totalLimit);
    }
}
```

## 九つのポリシー契約を再現する

七つのテストは実際の WebClient とローカルの MockWebServer を使います。二つは合成した exchange と Reactor の仮想時間を使い、ネットワークのスケジューリングに依存せずオペレーターのタイミングを検証します。仮想時間は Reactor Netty の実際のソケットタイムアウトをテストしません。トランスポートのテストはラップされた読み取りタイムアウトの原因を検査し、Publisher のタイムアウトは `TimeoutException` を生成します。

### `src/test/java/RetryClientTest.java`

```java
import java.io.IOException;
import java.time.Duration;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.atomic.AtomicInteger;
import io.netty.handler.timeout.ReadTimeoutException;
import okhttp3.mockwebserver.MockResponse;
import okhttp3.mockwebserver.MockWebServer;
import okhttp3.mockwebserver.SocketPolicy;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpStatus;
import org.springframework.web.reactive.function.client.ClientResponse;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientRequestException;
import org.springframework.web.reactive.function.client.WebClientResponseException;
import reactor.core.publisher.Mono;
import reactor.netty.http.client.HttpClient;
import reactor.test.StepVerifier;
import static org.junit.jupiter.api.Assertions.*;

class RetryClientTest {
    private MockWebServer server;
    private WebClient client;
    private static final Duration GUARD = Duration.ofSeconds(10);

    @BeforeAll
    static void warmUp() {
        HttpClient.create().warmup().block(GUARD);
    }

    @BeforeEach
    void start() throws IOException {
        server = new MockWebServer();
        server.start();
        client = RetryClient.transport(server.url("/").toString(), Duration.ofSeconds(5));
    }

    @AfterEach
    void stop() throws IOException {
        server.shutdown();
    }

    RetryClient policy() {
        return new RetryClient(client, Duration.ofSeconds(3),
            Duration.ofSeconds(8), Duration.ofMillis(10));
    }

    void expectStatus(int status) {
        StepVerifier.create(policy().get())
            .expectErrorSatisfies(error -> assertEquals(status,
                assertInstanceOf(WebClientResponseException.class, error).getStatusCode().value()))
            .verify(GUARD);
    }

    @Test
    void successUsesOneRequest() {
        server.enqueue(new MockResponse().setBody("ok"));
        StepVerifier.create(policy().get()).expectNext("ok").expectComplete().verify(GUARD);
        assertEquals(1, server.getRequestCount());
    }

    @Test
    void two503ResponsesThenSuccessUseThreeRequests() {
        server.enqueue(new MockResponse().setResponseCode(503));
        server.enqueue(new MockResponse().setResponseCode(503));
        server.enqueue(new MockResponse().setBody("ok"));
        StepVerifier.create(policy().get()).expectNext("ok").expectComplete().verify(GUARD);
        assertEquals(3, server.getRequestCount());
    }

    @Test
    void exhausted503PreservesLastStatusAfterThreeRequests() {
        for (int i = 0; i < 3; i++) server.enqueue(new MockResponse().setResponseCode(503));
        expectStatus(503);
        assertEquals(3, server.getRequestCount());
    }

    @Test
    void notFoundIsNotRetried() {
        server.enqueue(new MockResponse().setResponseCode(404));
        expectStatus(404);
        assertEquals(1, server.getRequestCount());
    }

    @Test
    void otherServerErrorsAreNotRetried() {
        server.enqueue(new MockResponse().setResponseCode(500));
        expectStatus(500);
        assertEquals(1, server.getRequestCount());
    }

    @Test
    void attemptTimeoutIsNotRetried() {
        server.enqueue(new MockResponse().setSocketPolicy(SocketPolicy.NO_RESPONSE));
        RetryClient limited = new RetryClient(client, Duration.ofSeconds(1),
            Duration.ofSeconds(8), Duration.ofMillis(10));
        StepVerifier.create(limited.get()).expectError(TimeoutException.class).verify(GUARD);
        assertEquals(1, server.getRequestCount());
    }

    @Test
    void responseReadTimeoutIsNotRetried() {
        server.enqueue(new MockResponse().setSocketPolicy(SocketPolicy.NO_RESPONSE));
        WebClient shortRead = RetryClient.transport(server.url("/").toString(), Duration.ofMillis(250));
        RetryClient limited = new RetryClient(shortRead, Duration.ofSeconds(3),
            Duration.ofSeconds(8), Duration.ofMillis(10));
        StepVerifier.create(limited.get()).expectErrorSatisfies(error -> {
            assertInstanceOf(WebClientRequestException.class, error);
            assertInstanceOf(ReadTimeoutException.class, error.getCause());
        }).verify(GUARD);
        assertEquals(1, server.getRequestCount());
    }

    @Test
    void totalBudgetIncludesRetryDelay() {
        AtomicInteger attempts = new AtomicInteger();
        StepVerifier.withVirtualTime(() -> {
            WebClient synthetic = WebClient.builder().exchangeFunction(request -> Mono.defer(() -> {
                attempts.incrementAndGet();
                return Mono.just(ClientResponse.create(HttpStatus.SERVICE_UNAVAILABLE).build());
            })).build();
            return new RetryClient(synthetic, Duration.ofSeconds(1),
                Duration.ofMillis(1500), Duration.ofSeconds(1)).get();
        }).thenAwait(Duration.ofMillis(1500)).expectError(TimeoutException.class).verify(GUARD);
        assertEquals(2, attempts.get());
    }

    @Test
    void attemptBudgetRestartsAfterRetry() {
        AtomicInteger attempts = new AtomicInteger();
        StepVerifier.withVirtualTime(() -> {
            WebClient synthetic = WebClient.builder().exchangeFunction(request -> Mono.defer(() -> {
                int attempt = attempts.incrementAndGet();
                return Mono.delay(Duration.ofMillis(400)).map(tick -> attempt == 1
                    ? ClientResponse.create(HttpStatus.SERVICE_UNAVAILABLE).build()
                    : ClientResponse.create(HttpStatus.OK).body("ok").build());
            })).build();
            return new RetryClient(synthetic, Duration.ofMillis(500),
                Duration.ofSeconds(2), Duration.ofMillis(200)).get();
        }).thenAwait(Duration.ofSeconds(1)).expectNext("ok").expectComplete().verify(GUARD);
        assertEquals(2, attempts.get());
    }
}
```

## プロジェクトを実行して結果を読む

```sh
gradle --no-daemon clean test
```

ローカルでの再現には JDK 17.0.8.1 と Gradle 8.4 を使用し、九つすべてのテストに成功しました。アサーションは `build/reports/tests/test/index.html` または `build/test-results/test/TEST-RetryClientTest.xml` で確認します。`BUILD SUCCESSFUL` だけでは実行されたテスト数は分かりません。

| シナリオ | 確認した結果 |
| --- | --- |
| 即時成功 | HTTP リクエスト一回、`ok`、完了 |
| 503 → 503 → 成功 | HTTP リクエスト三回、`ok`、完了 |
| すべての試行で 503 | HTTP リクエスト三回、最後の 503 を保持 |
| 404 / 500 | それぞれ HTTP リクエスト一回、ステータスを保持 |
| 応答なし、試行の上限は一秒 | `TimeoutException`、HTTP リクエスト一回 |
| 応答なし、応答読み取りの上限は 250 ms | `WebClientRequestException`。原因は `ReadTimeoutException`、リクエスト一回 |
| 全体の予算 1.5 s、再試行の待機一秒 | 合成した試行二回。三回目の前にタイムアウトが待機をキャンセル |
| 試行 400 ms、待機 200 ms、試行 400 ms | 各試行は 500 ms 以内。仮想時間を 1 s 進めた後に成功と完了を確認 |

これらの検査は、TCP 接続確立のタイムアウト、DNS 障害、TLS ネゴシエーション、プールの枯渇、リダイレクト、分散した副作用を再現しません。接続の上限は設定してありますが、ここで実験的に検証してはいません。OS のスケジューリングは実際の経過時間に影響します。テストは正確な実時間のミリ秒数ではなく、エラーの種類とリクエスト数をアサートします。ステータス、メディアタイプ、JSON の扱いは、[WebClient の応答契約の例](/en/posts/2023-09-19-springboot-test-webclient/)を参照してください。
