---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2026-11-01-webflux-coroutines-mvc-virtual-threads",
  "routeSlug": "2026-11-01-webflux-coroutines-mvc-virtual-threads",
  "kind": "post",
  "title": "Kotlin・WebFlux・コルーチンから Java・MVC・仮想スレッドへ移行する",
  "description": "納期の短さと既存チームの Kotlin 習得負担から Java を選んだ理由と、WebFlux・コルーチンの経路を MVC・仮想スレッドへ移す方法を解説します。",
  "categories": [
    "springboot"
  ],
  "tags": [
    "spring",
    "spring-webflux",
    "spring-mvc",
    "kotlin-coroutines",
    "kotlin",
    "java",
    "virtual-threads",
    "migration"
  ],
  "sourcePath": "src/content/posts/en/2026-11-01-webflux-coroutines-mvc-virtual-threads.md",
  "sourceSha256": "f0e4726741f1c91af86727ece0bfb5ff3cbd27354075d37e7de676b2e034f952",
  "draftSha256": "71ab84eacd1f709fe46c3f49eaf10b14c1147fb3735db236f300f2b7465fb0f4",
  "manifestPath": ".pipeline/technical-translations/batch-132/manifest.json",
  "manifestSha256": "9061c67686c9ea3bd8d21799f4c265ee716fee50940f1b6fc38c28a67de01dee",
  "publishedAt": "2026-11-02T03:04:44.245Z",
  "updatedAt": "2026-11-02T03:04:44.245Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 132,
    "approvedAt": "2026-11-02T03:04:44.245Z",
    "basis": "User requested completing missing multilingual technical posts, review, verification and deployment, then instructed continuing the next task on 2026-11-02, with standing blog PR merge/publication authorization. Human approval denotes user publication authorization; linguistic review is AI, not human/native review."
  }
}
---

**この移行では、Kotlin・WebFlux・コルーチンから、Java・Spring MVC・仮想スレッドへ切り替えます。** Kotlin から Java に移る理由は、納期が短く、既存チームに Kotlin の習得負担がかかるためでした。言語の選択では納期とチームの学習負担を考慮し、サーバーの実行モデルは仮想スレッドを使う MVC へ移しました。

言語を選んだ納品上の事情と、仮想スレッドによる性能への影響は、分けて説明する必要があります。以下のコードは移行の形を示すもので、実際の本番コードや測定結果を再現したものではありません。

本ガイドでは、Java 21 以降と Spring Boot 3.2 以降を対象に、段階的な移行を説明します。スループットの向上やレイテンシーの低下を約束するものではありません。リクエストの待機時間と CPU 使用の特性、データベース接続上限、下流サービスの処理能力、代表的な負荷テストを踏まえて、実際の結果を測定してください。

<span id="separate-the-three-choices"></span>

## 言語の選択と実行モデルを分ける

**WebFlux と MVC は Web ランタイムの選択です。** WebFlux は Reactive Streams と非同期・ノンブロッキング I/O を中心とし、MVC は Servlet のリクエストモデルを使います。**コルーチンは Kotlin の非同期プログラミングモデル**なので、MVC を選んでも `suspend` 関数を残せます。Spring は MVC と WebFlux の両方のアノテーション付きコントローラーで Kotlin コルーチンをサポートしています。コルーチンのサポートには `kotlinx-coroutines-core` と `kotlinx-coroutines-reactor` が必要です。[Spring Framework のコルーチンサポート](https://docs.spring.io/spring-framework/reference/languages/kotlin/coroutines.html)

仮想スレッドは軽量な Java スレッドです。ブロッキング呼び出しを使い、リクエストごとにスレッドを割り当てる設計で、プラットフォームスレッドが待機するコストを減らせます。有効にしても JDBC がノンブロッキングになったり、データベース接続プールが増えたりはしません。Spring Boot 3.2 以降は JDK 21 以降で `spring.threads.virtual.enabled=true` を指定すると、仮想スレッドによる実行を有効にできます。Boot は最適な利用のために Java 24 以降を推奨し、ピン留め、既存のスレッドプール設定、デーモンスレッドの動作を確認事項として挙げています。[Spring Boot の仮想スレッド設定と注意点](https://docs.spring.io/spring-boot/reference/features/spring-application.html)

この移行では、言語、Web ランタイム、並行実行モデルを同時に変えます。それぞれを別々に検証してください。表に示すとおり、ストレージの移行は別の判断です。実際のサービスが R2DBC を使っていた、または JPA に移ったと示すものではありません。

| 変更 | 変わる内容 | 別途検証する内容 |
| --- | --- | --- |
| Kotlin → Java | 実装言語と非同期 API の形 | null 処理、データオブジェクト、例外、キャンセル、既存 API 契約 |
| WebFlux → MVC | サーバーのリクエスト処理モデル | フィルター、セキュリティ、例外マッピング、SSE、WebSocket |
| R2DBC → JDBC/JPA（必要な場合） | データベースアクセスモデル | トランザクション境界、クエリ、接続上限、タイムアウト |
| コルーチンによる実行 → 同期呼び出しと仮想スレッド | 実行と待機のモデル | ライブラリ互換性、ThreadLocal の利用、ピン留め、運用上のシグナル |

## どの経路を移すか

通常のリクエストとレスポンスの経路が JPA や JDBC を使い、時間の大部分をデータベースや下流の HTTP 応答待ちに費やすなら、仮想スレッドを使う MVC を評価する価値があります。一方、高い並行性を持つストリーム、Server-Sent Events（SSE）、WebSocket、Reactive Streams の需要制御が中心的な契約となる経路は、WebFlux に残すか、専用の経路として分けたほうがよい場合があります。`Flow` を MVC の戻り値にできることは、あらゆる環境でストリーミング、キャンセル、バックプレッシャーの動作が同じになる保証ではありません。

![納期と学習負担から Java を選び、リアクティブ専用経路を識別し、アダプターと同期ストレージを通じて通常のリクエスト経路を移行し、仮想スレッドと契約を検証して段階的に拡大する流れ](/assets/diagrams/technical/ja-2026-11-01-webflux-coroutines-mvc-virtual-threads.svg)

図は、通常のリクエスト経路の移行順序を示しています。ストリーミングが引き続き必要な経路は移行を後回しにし、維持するか分離します。テストと観測が基準を満たしてからトラフィックを増やし、ベースラインより悪化した場合に旧経路へ戻れるようにします。

<span id="you-can-keep-coroutine-controllers"></span>

## Kotlin コルーチンコントローラーを Java MVC へ移す

以下の抜粋は、注文を一件取得するエンドポイントを示します。移行前の Kotlin コントローラーは `suspend` 関数を通じてサービスを待ちます。

```kotlin
@RestController
class OrderController(private val orders: OrderService) {
    @GetMapping("/orders/{id}")
    suspend fun get(@PathVariable id: Long): OrderDto = orders.get(id)
}
```

移行後の Java MVC コントローラーは同期サービスメソッドを呼び、同じレスポンス DTO を返します。ここでは `orders.get(id)` も、Java から呼べる同期契約に変わっていると仮定します。Java から Kotlin の `suspend` メソッドを直接呼ぶコードではありません。

```java
@RestController
public class OrderController {
    private final OrderService orders;

    public OrderController(OrderService orders) {
        this.orders = orders;
    }

    @GetMapping("/orders/{id}")
    public OrderDto get(@PathVariable("id") Long id) {
        return orders.get(id);
    }
}
```

Spring のアノテーションは `org.springframework.web.bind.annotation` に含まれ、`OrderService` と `OrderDto` はアプリケーションのサービス型とレスポンス型です。これらの抜粋は、実行可能な完全なアプリケーションではありません。以下の Boot 設定で仮想スレッドを有効にし、実際の HTTP リクエスト中に実行を検証してください。

Kotlin の nullable 型が Java にどう対応するか、`data class` の等価性とシリアライズ契約をどう維持するかを確認します。コルーチンの `async` 呼び出しを逐次的な Java 呼び出しに置き換えると、下流リクエストの順序や応答時間が変わる可能性があるため、並列性、タイムアウト、キャンセルを別々に検証してください。既存のコルーチン呼び出しを `runBlocking` で包むだけでは、同期 Java サービスへの移行は完了しません。

Spring MVC 自体も Kotlin の `suspend` と `Flow` をサポートするので、MVC を使うためにコルーチンを除去する必要はありません。この事例では、**短い納期と既存チームの Kotlin 習得負担を理由に Java を移行先言語に選んだ**ため、コントローラーとサービスの契約もその方向に変えます。

## リポジトリの移行を別途検証する

データベースアクセスモデルも変更する必要がある場合、以下は Kotlin の R2DBC `CoroutineCrudRepository` を Java の Spring Data JPA に移す別の例です。全行をメモリに集めずに結果数を制限し、既存 API のソート、ページサイズ、認可フィルターを維持します。

```kotlin
interface OrderRepository : CoroutineCrudRepository<Order, Long> {
    fun findByCustomerId(customerId: Long): Flow<Order>
}
```

同期 JPA リポジトリでは、ページ単位で取得できます。

```java
public interface OrderRepository extends JpaRepository<Order, Long> {
    Page<Order> findByCustomerId(Long customerId, Pageable pageable);
}
```

これらの断片はリポジトリの形を示すもので、完全なアプリケーションではありません。実際のプロジェクトでは、エンティティのフェッチ戦略、トランザクション範囲、N+1 クエリ、安定したページ順序、従来の `Flow` のキャンセルや一部だけを消費する場合の意味も確認します。有限のレスポンスを返す API を一つ選び、契約テストとクエリの観測を加えてから、移行を広げてください。

## 仮想スレッドを有効にして検証する

Spring Boot 3.2 以降と JDK 21 以降では、この設定を適用できます。

```yaml
spring:
  threads:
    virtual:
      enabled: true
```

適用後、リクエストを処理するスレッドが実際に仮想スレッドか確認します。一時的な診断として、MVC インターセプターやコントローラーから `Thread.currentThread().isVirtual()` を記録します。これはそのリクエスト経路だけの確認であり、アプリケーションのすべてのタスクやコルーチンディスパッチャーが仮想スレッドを使う証明ではありません。

Java コントローラーの経路では、この式で現在のリクエストスレッドを確認します。

```java
public class RequestThreadProbe {
    public static boolean isVirtual() {
        return Thread.currentThread().isVirtual();
    }
}
```

Boot は、仮想スレッドではスレッドプールのプロパティが従来の効果を持たなくなる場合や、一部の同期処理やネイティブ呼び出しでのピン留めがスループットに影響する場合があると説明しています。仮想スレッドを増やしてデータベース接続上限や下流の並行実行上限を回避しないでください。データベースが処理できる範囲に接続プールを制限し、接続取得、クエリ、下流呼び出し、リクエスト全体の期限を設定します。

## 段階的に移行し、ロールバック基準を決める

1. **ベースラインを記録します。** 同じ負荷条件で、代表的なエンドポイントのリクエストレート、p50/p95/p99 レイテンシー、エラー率、CPU、ヒープ、データベースプールの待機、下流呼び出しのレイテンシーを収集します。
2. **リアクティブ専用経路を明示します。** SSE、WebSocket、無限ストリーム、バックプレッシャー、Reactive Streams の操作に依存する経路を列挙し、初期移行の対象外にします。
3. **有限の API を一つ移します。** Kotlin を Java に変換しつつ、サーバーランタイムの変更と必要なストレージ変更を別々に検証し、リクエスト、レスポンス、エラー、キャンセル、認可の契約をテストします。
4. **仮想スレッドによる実行を確認します。** デプロイ用プロパティだけでなく、実行時のスレッドと JDBC 呼び出し経路を調べます。バックグラウンドタスクのエグゼキューターは別途確認します。
5. **同じ負荷で比較します。** 同じデータ量と負荷で、レイテンシー分布、エラー、CPU、データベースの待機、接続使用量を比較します。仮想スレッドは CPU バウンドな処理の CPU 能力を増やさないため、CPU 飽和にも注意します。
6. **少量のトラフィックから拡大します。** 業務エラー、レイテンシー、データベースプールの待機、リソース使用量が事前の基準を超えたら、拡大を止めて調査するか旧経路へ戻します。しきい値はチームがサービスの SLO とベースラインに基づいて設定します。

対象環境で測定していないスループットやレイテンシーの改善を報告しないでください。まず同じ入力で変更後の経路を測定します。結果が改善しないなら、MVC への移行自体を目的にする理由はありません。

## 判断基準

通常のリクエストとレスポンスのトラフィックが JDBC/JPA を使い、並行するブロッキング待機がボトルネックになり得るなら、小さな経路で MVC と仮想スレッドを評価します。この事例で Java を選んだ理由は、短い納期と既存チームの Kotlin 習得負担です。言語変更を、仮想スレッドによるスループット向上と同一視しないでください。ストリーミングや Reactive Streams の動作が製品要件なら、スレッドモデルを変えるために契約を弱めず、WebFlux を維持します。同じ負荷でレイテンシー、エラー、データベースの待機、運用の複雑さを比較して判断してください。
