---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2026-10-31-webclient-restclient-comparison",
  "routeSlug": "2026-10-31-webclient-restclient-comparison",
  "kind": "post",
  "title": "WebClientとRestClient：同期・リアクティブ・ストリーミング呼び出しを選ぶ",
  "description": "Spring WebClientとRestClientの実行タイミング、ブロック、エラー、仮想スレッド利用を比較します。ローカルHTTPの例で購読ごとのリクエストと404/503処理を確認します。",
  "categories": [
    "springboot"
  ],
  "tags": [
    "spring",
    "webclient",
    "restclient",
    "http-client",
    "reactive",
    "virtual-threads"
  ],
  "sourcePath": "src/content/posts/en/2026-10-31-webclient-restclient-comparison.md",
  "sourceSha256": "66635549fdfb330bbeabd658046b28dcb1566bef58dbf033b35e22e387806d15",
  "draftSha256": "e88d6b76b26bfbc125f28db9d04c25afd999d83a3fef43bb97b0250b75619737",
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
**同期サービスのコードで、次へ進む前にHTTP応答を一つ必要とする場合は、RestClientから検討します。リアクティブな合成やストリーミングが必要なら、WebClientを検討します。** どちらも流れるように記述できるAPIを提供しますが、[RestClientは同期クライアント、WebClientはノンブロッキングのリアクティブクライアント](https://docs.spring.io/spring-framework/reference/integration/rest-clients.html)です。リクエスト数ではなく、アプリケーションの実行モデルに合わせて選びます。


RestClientはSpring Framework 6.1で導入され、WebClientは5.0から利用できます。まず、使用中のFrameworkバージョンが選択したクライアントをサポートするか確認します。Bootプロジェクトのアップグレードでは、Bootが管理する互換性のある組み合わせに従います。以下の実行例はFramework 7.0.10に固定しています。

## どの要件にどのクライアントが合いますか？

| 基準 | RestClient | WebClient |
| --- | --- | --- |
| 結果 | 本文抽出などの終端操作が応答を待ち、値を返します | MonoまたはFluxが結果を表し、購読でリクエストが開始します |
| 適した用途 | Spring MVCやバッチジョブの逐次・同期コードです | WebFlux、リアクティブな合成、SSEなどのストリーミングです |
| エラーの通知 | retrieveの既定処理は4xxと5xxでRestClientResponseExceptionを投げます | retrieveの既定処理は4xxと5xxでWebClientResponseExceptionのエラーを発行します |
| 追加の負担 | 従来のコールスタックで追いやすくなります | 演算子、購読、キャンセル、コンテキスト伝播の理解が必要です |
| 同時実行制御 | Executorや仮想スレッドの同時実行数を別途設計します | flatMapなどの合成の同時実行数、接続、待機の予算を別途制限します |

この表は、応答をメモリ上に集約する通常のAPI呼び出しを出発点にしています。RestClientでも低水準の応答処理でバイトストリームを読めますが、リアクティブな要素ストリームや需要制御にはWebClientが適しています。WebClientを使うためにサーバーをWebFluxへ変更する必要はありません。Spring MVCでもリアクティブな戻り値型を使えます。[SpringのHTTPクライアントガイド](https://spring.io/blog/2025/09/30/the-state-of-http-clients-in-spring/)も、一般的な同期呼び出しと、リアクティブ・ストリーミング要件を同様に区別しています。

仮想スレッドを使う同期サービスは、逐次的なRestClientコードを維持できます。仮想スレッドによってAPIがノンブロッキングになったり、下流の容量や接続上限が増えたりはしません。[仮想スレッドの適用範囲](/en/posts/2026-10-31-virtual-threads-jdk21-jdk25/)と[依存先の容量制限](/en/posts/2026-10-31-jdk-10k-rps-architecture/)を併せて検討してください。

## 同じHTTP応答で実行タイミングを比較する

![mainの流れでRestClientの終端操作を完了し、WebClientのMonoを作成して二回購読し別々のリクエストを送り、両クライアントの404と503を確認します](/assets/diagrams/technical/ja-2026-10-31-webclient-restclient-comparison.svg)

図はmainメソッドの主要な確認を示し、ローカルサーバーの準備、クライアント設定、後始末は省略しています。**RestClientは、retrieve()を呼ぶだけではリクエストを送りません。** ここではbody(String.class)がリクエストを実行し、結果を待ちます。WebClientの既定のリクエストMonoは、購読時に実行されます。このMonoをキャッシュや共有の演算子なしに二回購読すると、二つのリクエストを送信します。

この独立したコンソール例は、Spring Framework 7.0.10、Reactor Core 3.8.8、JDK 17、Gradle 8.4で実行しました。Spring Bootアプリケーションではありません。両クライアントは明示的にJDK HttpClientを使用し、既定コネクターの選択による違いを除いています。Bootプロジェクトでは、このBOMで上書きするより、そのBootバージョンが管理する依存関係を優先してください。

### `settings.gradle`

```groovy
rootProject.name = 'http-client-comparison'
```

### `build.gradle`

```groovy
plugins { id 'application' }
repositories { mavenCentral() }
dependencies {
    implementation platform('org.springframework:spring-framework-bom:7.0.10')
    implementation 'org.springframework:spring-webflux'
}
java {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
}
application { mainClass = 'ClientComparison' }
```

### `src/main/java/ClientComparison.java`

```java
import com.sun.net.httpserver.HttpServer;
import java.net.InetSocketAddress;
import java.net.http.HttpClient;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.concurrent.atomic.AtomicInteger;
import org.springframework.http.client.JdkClientHttpRequestFactory;
import org.springframework.http.client.reactive.JdkClientHttpConnector;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientResponseException;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;
import reactor.core.publisher.Mono;

public class ClientComparison {
    static void check(boolean condition) {
        if (!condition) throw new AssertionError("HTTP contract failed");
    }
    public static void main(String[] args) throws Exception {
        var requests = new AtomicInteger();
        var server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        server.createContext("/", exchange -> {
            requests.incrementAndGet();
            String path = exchange.getRequestURI().getPath();
            int status = path.equals("/missing") ? 404 : path.equals("/unavailable") ? 503 : 200;
            byte[] body = (status == 200 ? "hello" : "error").getBytes(StandardCharsets.UTF_8);
            exchange.getResponseHeaders().set("Content-Type", "text/plain;charset=UTF-8");
            exchange.sendResponseHeaders(status, body.length);
            try (var output = exchange.getResponseBody()) { output.write(body); }
        });
        server.start();
        try {
            String base = "http://127.0.0.1:" + server.getAddress().getPort();
            var jdk = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(2)).build();
            var factory = new JdkClientHttpRequestFactory(jdk);
            factory.setReadTimeout(Duration.ofSeconds(2));
            var connector = new JdkClientHttpConnector(jdk);
            connector.setReadTimeout(Duration.ofSeconds(2));
            var rest = RestClient.builder().baseUrl(base).requestFactory(factory).build();
            var web = WebClient.builder().baseUrl(base).clientConnector(connector).build();

            var response = rest.get().uri("/hello").retrieve();
            check(requests.get() == 0);
            System.out.println("before-rest-terminal=" + requests.get());
            String sync = response.body(String.class);
            check("hello".equals(sync) && requests.get() == 1);
            System.out.println("rest=" + sync);

            Mono<String> pending = web.get().uri("/hello").retrieve().bodyToMono(String.class);
            check(requests.get() == 1);
            System.out.println("before-subscribe=" + requests.get());
            String first = pending.block(Duration.ofSeconds(5));
            check("hello".equals(first) && requests.get() == 2);
            System.out.println("web=" + first);
            System.out.println("after-first-subscribe=" + requests.get());
            String second = pending.block(Duration.ofSeconds(5));
            check("hello".equals(second) && requests.get() == 3);
            System.out.println("web-again=" + second);
            System.out.println("after-second-subscribe=" + requests.get());

            for (int status : new int[]{404, 503}) {
                String path = status == 404 ? "/missing" : "/unavailable";
                try {
                    rest.get().uri(path).retrieve().body(String.class);
                    throw new AssertionError("RestClient should fail");
                } catch (RestClientResponseException error) {
                    check(error.getStatusCode().value() == status);
                    System.out.println("rest-" + status + "=" + error.getStatusCode().value());
                }
                try {
                    web.get().uri(path).retrieve().bodyToMono(String.class).block(Duration.ofSeconds(5));
                    throw new AssertionError("WebClient should fail");
                } catch (WebClientResponseException error) {
                    check(error.getStatusCode().value() == status);
                    System.out.println("web-" + status + "=" + error.getStatusCode().value());
                }
            }
            check(requests.get() == 7);
            System.out.println("requests=" + requests.get());
        } finally { server.stop(0); }
    }
}
```

### 実行と確認

```sh
gradle --no-daemon --console=plain -q clean run
```

最初の依存関係のダウンロードには、ネットワークアクセスが必要です。実行時のHTTPリクエストは、一時ポートの127.0.0.1サーバーだけに送ります。以下は、記載した環境で観測したアプリケーションの標準出力です。Gradleやログ実装は、別の診断情報を出力する場合があります。

```text
before-rest-terminal=0
rest=hello
before-subscribe=1
web=hello
after-first-subscribe=2
web-again=hello
after-second-subscribe=3
rest-404=404
web-404=404
rest-503=503
web-503=503
requests=7
```

0から1への変化は、RestClientの終端操作が最初のリクエストを完了したことを示します。Monoを構築した直後も件数は1のままです。各blockは購読を行い、件数が2、その後3へ増えます。続く四つのリクエストで404と503の処理を確認し、合計は7です。これらの件数は実行とエラーの契約を検証するもので、スループット、レイテンシ、イベントループの性能を比較しません。

## blockを使うと両クライアントは同じ動作になりますか？

WebClientにblockを追加すると、**呼び出し元が結果を待ちます**。基礎となる通信実装がRestClientと同じになるわけではありません。[同期利用のドキュメント](https://docs.spring.io/spring-framework/reference/web/webflux-webclient/client-synchronous.html)が説明するように、リアクティブコントローラーからはMonoやFluxを返し、購読をフレームワークに任せます。上のblock呼び出しは、動作を観察するコンソールのmainに限定しています。イベントループ上でRestClientを呼んだりblockで待ったりすると、処理スレッドを占有したり、ノンブロッキングスレッドでのブロックを禁じる例外が発生したりする可能性があります。

既にWebClientのフィルター、認証、計測を運用している場合は、同期呼び出しという理由だけで即座に置き換える必要はありません。新たな同期呼び出しへリアクティブ依存関係と購読処理を導入する負担を、既存設定を維持する負担と比較します。複数のリモート呼び出しを合成するときは、無制限の購読を避けます。[WebFluxのリアクティブ需要制御](https://docs.spring.io/spring-framework/reference/web/webflux/new-framework.html)は、生成速度と消費速度を調整します。下流サービスのRPSや接続上限を自動的に守るものではありません。

## 本番前に何を確認すべきですか？

両クライアントとも、接続、応答読み取り、呼び出し全体の時間予算と、エラーステータスの方針が必要です。この例の接続上限2秒、読み取り上限2秒、block待機5秒は再現用設定であり、同じタイムアウトの意味でも本番推奨値でもありません。各読み取りタイムアウトの範囲は、[リクエストファクトリー](https://docs.spring.io/spring-framework/docs/7.0.10/javadoc-api/org/springframework/http/client/JdkClientHttpRequestFactory.html)と[リアクティブコネクター](https://docs.spring.io/spring-framework/docs/7.0.10/javadoc-api/org/springframework/http/client/reactive/JdkClientHttpConnector.html)のドキュメントを確認してください。これらの速いローカル応答では、タイムアウト、TLS、キャンセルの伝播を検証できません。

この例は、両クライアントの4xxと5xx応答に対するretrieveの既定処理を確認します。明示的なステータス方針にはonStatusを使います。低水準のexchange APIにもretrieveの既定ステータス処理が適用されると仮定しないでください。[WebClientの応答処理](/en/posts/2023-09-19-springboot-test-webclient/)と[タイムアウトと回数制限付き再試行](/en/posts/2026-10-30-webclient-timeout-retry/)の例では、続けて確認すべき契約を示します。冪等性、試行回数、総時間予算で再試行を制限し、空の本文、大きな応答、接続失敗は別途テストします。

既存のRestTemplateコードは、別の移行課題です。Spring Framework 7.0はRestClientを推奨し、RestTemplateを非推奨としています。WebClientは非推奨ではありません。クライアント選択後は、実際のリクエスト構成に対して認証、計測、接続設定を検証します。
