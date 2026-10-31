---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2026-10-31-jdk-10k-rps-architecture",
  "routeSlug": "2026-10-31-jdk-10k-rps-architecture",
  "kind": "post",
  "title": "最新JDKで10k RPS APIを設計する：容量と過負荷制御",
  "description": "JDK 27で10,000 RPS HTTP APIを計画し、容量・データベース・障害の予算を明確にします。仮想スレッドの受け入れ制御例を実行し、設計上の仮定と負荷試験の証拠を区別します。",
  "categories": [
    "jdk"
  ],
  "tags": [
    "java",
    "jdk27",
    "architecture",
    "capacity-planning",
    "virtual-threads",
    "load-testing"
  ],
  "sourcePath": "src/content/posts/en/2026-10-31-jdk-10k-rps-architecture.md",
  "sourceSha256": "c4bdc1984dacdabdaeabacf9e889b26a76991cbb44d19263a3a2bfb0b8e1e1bf",
  "draftSha256": "4a5b8ea4cb14e4d5fbc1052472811aabbd93278a1316065d5293aa11e633e6c8",
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
**毎秒10,000リクエストのHTTP APIには、新しいJDKより先に、リクエストと依存先の明示的な容量予算と過負荷時の動作が必要です**。アベイラビリティゾーンをまたぐステートレスAPIレプリカ、リクエスト受け入れ制限、依存先ごとの同時実行制限から始めます。キャッシュ、キュー、読み取りレプリカは、測定したボトルネックと整合性要件に従って追加します。これは計算例を含む設計ガイドであり、**10k RPS負荷試験の成功報告ではありません**。

2026年10月31日時点の最新GAリリースは[JDK 27](https://openjdk.org/projects/jdk/27/)です。以下のコードはTemurin `27.0.1.0.2+1`で確認しました。機能の新しさとサポート期間は分けて考えます。[Oracleのサポートロードマップ](https://www.oracle.com/java/technologies/java-se-support-roadmap.html)は、JDK 25をLTS、27を非LTSとしています。他の供給元のサポート方針やフレームワーク互換性は、それぞれのドキュメントで確認してください。

## 10kの境界と成功条件を定義する

ここで10kは、静的なCDNヒットを除き、**APIロードバランサーに到達する毎秒リクエスト数**を意味します。同時接続数や仮想スレッド数ではありません。投入RPS、完了した業務成功RPS、拒否、失敗を分けて記録します。速いエラー応答だけでは容量を証明できません。

以下は計算を説明するための仮定です。実際のサービスの測定値でも、推奨設定値でもありません。

| 項目 | 計算例の仮定 |
| --- | --- |
| 投入目標 | 10,000 RPS |
| 読み取り／書き込み比率 | 90% / 10% |
| 読み取りキャッシュのヒット率 | 80% |
| 定常状態の平均API滞在時間 | 50ms |
| 応答目標 | p99が200ms未満、失敗率が0.1%未満 |
| データベース利用 | 読み取りミス・書き込みごとに一回アクセス、平均接続保持時間10ms |

[リトルの法則](https://web.mit.edu/2.810/www/files/lectures/lec1-intro-2019.pdf#page=56)、`L = λ × W`は、安定したシステムの同じ境界における**平均**に適用します。通常のスループットを10,000/s、平均滞在時間を0.05秒と仮定すると、全体で処理中のリクエストは平均約500件です。平均同時実行数の計算にp99の200msを代入したり、500をそのままハード上限にしたりしないでください。バースト、レイテンシ分布、障害時の余裕は別に検証する必要があります。

データベースへのアクセスは`9,000 × (1 − 0.8) + 1,000 = 2,800/s`、平均使用接続数は`2,800 × 0.01 = 28`です。**これはプールサイズ28を推奨するものではありません。** 複数のSQL文、ロック、トランザクション、キャッシュ障害で仮定は変わります。帯域予算には、応答のバイト数、TLS、レプリケーション、ログも含めます。

## 構成例：小さなサービスを水平に複製する

![エッジとロードバランサーから複数ゾーンのJDK APIレプリカへ分散し、任意の読み取りキャッシュ、DBプール、外部サービス制限、任意のDBアウトボックスからワーカーへの配送を組み合わせます](/assets/diagrams/technical/ja-2026-10-31-jdk-10k-rps-architecture-architecture.svg)

これは提案する構成です。以下のJava例が実装するのは、受け入れ制御の原則だけで、インフラ全体ではありません。10k RPSという目標だけでは、マイクロサービスやシャーディングの必要性は示せません。ステートレスなモジュール型アプリケーションを複製し、測定で明らかになったボトルネックを分離します。

- **エッジとロードバランサー：** クライアントごとのリクエストレート、接続数、リクエスト本文サイズ、遅い接続を制限します。CDNでは適切な公開応答だけをキャッシュし、認証済みデータのキーと範囲は別に設計します。ヘルスチェックとドレイニングで、準備のできていないレプリカへ新規リクエストが流れないようにします。
- **APIレプリカ：** リクエスト境界で処理中の作業を制限し、読みやすいブロッキングI/Oコードに仮想スレッドを使います。仮想スレッドはデータベース容量を増やしたり、CPU計算を高速化したりしません。[JDK 27ガイド](https://docs.oracle.com/en/java/javase/27/core/virtual-threads.html)が説明するように、希少なリソースはセマフォなどで別途制約します。
- **キャッシュとデータベース：** 読み取りキャッシュは任意です。TTLの分散、ミスの集約、キャッシュ障害時のデータベーストラフィックをテストします。まずインデックス、クエリ計画、トランザクション時間を調べます。読み取りレプリカは、レプリケーション遅延を許容できる場所だけで使います。
- **外部呼び出しと非同期処理：** 依存先ごとに固有の同時実行予算を設けます。応答前に完了する必要のない作業だけをキューへ入れます。データベース書き込みとメッセージ配送を調整する必要がある場合は、再試行可能な配送と冪等なコンシューマーを持つ[トランザクショナルアウトボックス](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)を設計します。キューも有限のリソースです。滞留件数、最古メッセージの経過時間、処理失敗を監視します。

[Google SREの過負荷対策](https://sre.google/sre-book/handling-overload/)が説明するように、速やかな拒否とリソース保護を通常の運用動作として設計します。CPUだけによるスケーリングではI/O停滞を見逃す可能性があります。処理中のリクエスト、拒否率、接続取得待ち、依存先の飽和をまとめて観測します。

## レプリカとデータベース接続はいくつ必要ですか？

ハードウェア、ヒープ、コンテナCPU制限、リクエスト構成を固定し、`q_safe`を測定します。これは、**SLOと合意済みの運用上の余裕を満たす、レプリカ単位のスループット**です。この記事では測定していません。

試験で実際に`q_safe = 2,500 RPS`が確認できれば、四つのレプリカで通常目標を計算上は満たします。五つあれば、一つのレプリカ障害後も10kを維持するための出発点になります。ゾーン障害時の容量を保証するものではありません。三つのゾーンに二つずつ、計六つのレプリカを置けば、一つのゾーン障害後に四つが残り、机上では10kを満たしますが、ロードバランサーの再分散、ゾーン偏り、データベース・キャッシュのフェイルオーバーもテストする必要があります。自動スケーリング完了前の期間にも余裕を残します。

レプリカごとのデータベースプールを独立に増やさないでください。各データベースエンドポイントについて、`maximum simultaneously existing API replicas × per-replica pool limit + worker connections + operational reserve`を利用可能な接続予算内に収めます。スケールアウト、ローリングデプロイ、終了猶予期間で重複して存在するレプリカも数えます。[PostgreSQLのドキュメント](https://www.postgresql.org/docs/18/runtime-config-connection.html)は、`max_connections`を増やすと、共有メモリなどのリソース割り当ても増えると説明しています。接続数を増やしても、遅いクエリは直りません。

## 最小限の仮想スレッド受け入れ制御例

![ゲートは取得失敗を拒否するか同期処理を実行し、finallyで許可を戻した後、結果を返すか例外を伝えます](/assets/diagrams/technical/ja-2026-10-31-jdk-10k-rps-architecture.svg)

図は`Gate.call()`に対応しています。`main()`メソッドは、二つの処理と一つの拒否を作る、**HTTPサーバーなしの受け入れ動作デモ**です。上限の二つはテスト用であり、10k RPS向け設定ではありません。実際のサーバーでは、高コストな処理より前に受け入れ制御を適用し、エッジとサーバー側の制御により、ゲートより前の接続、サーバーキュー、仮想スレッド作成も制限します。

### `AdmissionDemo.java`

```java
import java.util.concurrent.Callable;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.RejectedExecutionException;
import java.util.concurrent.Semaphore;

public class AdmissionDemo {
    static final class Gate {
        private final Semaphore permits;
        Gate(int limit) {
            if (limit <= 0) throw new IllegalArgumentException("limit must be positive");
            permits = new Semaphore(limit);
        }
        <T> T call(Callable<T> work) throws Exception {
            if (!permits.tryAcquire()) throw new RejectedExecutionException("busy");
            try {
                return work.call();
            } finally {
                permits.release();
            }
        }
        int available() { return permits.availablePermits(); }
    }

    public static void main(String[] args) throws Exception {
        Gate gate = new Gate(2);
        CountDownLatch entered = new CountDownLatch(2);
        CountDownLatch release = new CountDownLatch(1);
        Callable<String> request = () -> gate.call(() -> {
            if (!Thread.currentThread().isVirtual()) throw new AssertionError("virtual thread required");
            entered.countDown();
            release.await();
            return "ok";
        });
        try (var tasks = Executors.newVirtualThreadPerTaskExecutor()) {
            var first = tasks.submit(request);
            var second = tasks.submit(request);
            try {
                entered.await();
                System.out.println("admitted=2");
                try {
                    gate.call(() -> "unexpected");
                    throw new AssertionError("capacity exceeded");
                } catch (RejectedExecutionException expected) {
                    System.out.println("overload=rejected");
                }
            } finally {
                release.countDown();
            }
            System.out.println("completed=" + first.get() + "," + second.get());
        }
        try {
            gate.call(() -> { throw new IllegalStateException("demonstration"); });
        } catch (IllegalStateException expected) {
            System.out.println("failure=propagated");
        }
        System.out.println("available=" + gate.available());
    }
}
```

```sh
javac --release 27 AdmissionDemo.java
java AdmissionDemo
```

この出力は、同じJDK 27インストール先の`javac`と`java`で観測しました。プレビューフラグは不要です。

```text
admitted=2
overload=rejected
completed=ok,ok
failure=propagated
available=2
```

[`tryAcquire()`](https://docs.oracle.com/en/java/javase/27/docs/api/java.base/java/util/concurrent/Semaphore.html#tryAcquire())の失敗は、キューに入れずに作業を拒否します。実際の処理が終わると`finally`で許可を戻し、例外は呼び出し元へ伝わります。これは、**毎秒リクエスト数の制限ではなく、同時実行数の制限**です。HTTPアダプターでは、サービス容量による拒否を、クライアント別の割り当て制限とは分けて503などの応答に対応付けられます。このコードは、HTTPステータスへの対応付け、認証、期限、データベースプールを実装していません。

## 期限と再試行による過負荷の増幅を防ぐ

エンドツーエンドの期限を設定し、残りの時間予算をデータベース接続取得、クエリ、HTTP接続、応答読み取りに配分します。各段階のp99を足しても、エンドツーエンドのp99にはなりません。呼び出し元がタイムアウトしても、実際のデータベースやHTTP処理が即座に停止するわけではありません。ドライバーやクライアントのキャンセルとリソース返却を検証します。基礎となる処理が続いている間に同時実行許可を戻すと、制限が破られます。

再試行は一つの層で行い、回数上限、全体の期限、指数バックオフ、ジッターを設け、適切なエラーと冪等性が確立された操作に限定します。[Amazonのタイムアウトと再試行ガイド](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)が説明するように、再試行は負荷を増やす可能性があります。決済や注文では、先に重複防止と結果照会の動作を定義します。

## 10kの容量を主張する前に、何に合格する必要がありますか？

実際のHTTPサーバー、本番に近いデータ、TLS、認証、応答サイズを用意し、次の順にテストします。

1. 一つのレプリカへの負荷を上げて`q_safe`を確定します。CPU、GC、割り当て、ソケット、ロック、データベース待ち、成功RPS、エンドツーエンドp99をまとめて記録します。
2. 準備とウォームアップの後、構成全体への投入トラフィックを1k→3k→5k→10kと増やし、合意した期間にわたって目標を維持します。結果には継続時間とデータ分布を含めます。
3. [k6 constant-arrival-rate](https://grafana.com/docs/k6/latest/using-k6/scenarios/executors/constant-arrival-rate/)などのオープンワークロードモデルでは、**一反復につきHTTPリクエスト一回で、自動リダイレクトと再試行が無効**と確認した後に限り、10,000 iterations/sを10k HTTP RPSに結び付けます。生成側のCPU、ネットワーク、VUの余裕、[dropped_iterations](https://grafana.com/docs/k6/latest/using-k6/scenarios/concepts/dropped-iterations/)を確認します。目標の入力を生成できていない試験は、サーバー容量を証明しません。
4. レプリカ・ゾーン喪失、コールドキャッシュやキャッシュ障害、遅いデータベース・依存先、ローリングデプロイ、バーストをテストします。拒否応答を業務成功から除外し、飽和後の復旧、キューの解消、接続リークを確認します。

この記事で実行したのは、ゲートの拒否と、正常・失敗処理後の許可返却だけです。構成全体の負荷試験は実施していません。本番構成の検証とは分けて、[JDK 21/25の仮想スレッド比較](/en/posts/2026-10-31-virtual-threads-jdk21-jdk25/)と[ScopedValueのリクエストコンテキスト境界](/en/posts/2026-10-31-jdk25-scopedvalue/)を参照してください。
