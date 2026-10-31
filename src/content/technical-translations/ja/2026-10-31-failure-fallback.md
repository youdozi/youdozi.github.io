---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2026-10-31-failure-fallback",
  "routeSlug": "2026-10-31-failure-fallback",
  "kind": "post",
  "title": "障害時のフォールバック設計：古い応答、機能縮小、拒否",
  "description": "外部 API、キャッシュ、決済障害で許容できる代替を定める。Java で鮮度と同時数を確認し、再試行、復旧、観測へつなぐ。",
  "categories": [
    "architecture"
  ],
  "tags": [
    "fallback",
    "resilience",
    "java",
    "timeout",
    "circuit-breaker",
    "load-shedding"
  ],
  "sourcePath": "src/content/posts/en/2026-10-31-failure-fallback.md",
  "sourceSha256": "93196b5c0ce64194996df961642c87053d74ea5be5c63b2b776cdd598dc7effd",
  "draftSha256": "df9e3d7fa8adbaea717055090b9d10fc8c53d2bb008d1e50d4805f366ddce007",
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

障害時の**フォールバックは、事前に定めた許容品質を、システムが負担できるコストで返すべきです**。推薦欄の省略や合意した古さ内の公開データが例です。決済結果不明なのに成功としたり、キャッシュ障害で全要求を DB に送ったりすると別の問題を生みます。

HTTP API 運用者向けに、[10k RPS 構成の記事](/ko/posts/2026-10-31-jdk-10k-rps-architecture/)の過負荷制御に続いて障害時の応答を扱います。Java 例は外部サーバーなしで方針を実行し、スループットや本番障害からの復旧は測りません。

## 障害により許せる結果は異なる

通常結果の何を減らせるか先に決めます。以下は設計例で、実際の鮮度上限と機能縮小範囲はサービス契約に従います。

| 障害 | 許容できる代替 | 停止、制限する条件 |
| --- | --- | --- |
| 推薦 API の遅延、失敗 | 任意の推薦を省くか準備済みの一般推薦 | 中核となる商品読取を同じキューに入れない |
| 公開商品説明の読取失敗 | 同商品、同言語の最終成功値と更新日時 | 古さ超過、データなし、誤ったキー |
| キャッシュ全停止 | 限定した元読取、承認済みコピー、超過拒否 | DB 接続、同時数予算を超す無制限 bypass はしない |
| 認証、認可確認の失敗 | 保護操作をせず一時エラー | 権限不足との混同や許可への置換はしない |
| 決済、注文後の応答消失 | 同じ操作 ID で照会、照合 | 失敗と決めて別決済を作らず成功も捏造しない |
| 代替サーバーも同じ DB | 別途検証した容量内だけ切替 | 共有 DB のボトルネックは解消しない |

認可、価格確定、在庫減算など正確性が重要な経路と単純な旧値読取を分けます。決済「確認中」は実際に追跡、照会できる場合だけ意味があります。文言の変更だけでは未確定結果を管理できません。

AWS は[分散システムのフォールバックのリスク](https://aws.amazon.com/builders-library/avoiding-fallback-in-distributed-systems/)として、希少経路のテスト不足と代替が生む追加問題を挙げます。通常経路同様に実行し、同じ資源に依存していないか確認します。

## タイムアウト、再試行、遮断器の役割は？

タイムアウトは呼出側の待機を制限します。**待機終了は遠隔操作や決済の取消を意味しません。** 再試行は同じ操作、failover は別レプリカ、fallback は縮小応答や別処理への切替です。遮断器は失敗蓄積後の条件で依存呼出を止め、安全な代替は別方針で決めます。

全体期限には接続、プール待機、応答待機、再試行、代替処理を含めます。予算 300ms で初回が 250ms なら、さらに 250ms は待てません。説明用の数字で推奨ではありません。各段のタイムアウト範囲も調べます。

[AWS の再試行ガイド](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)のとおり負荷は増え、応答失敗でも副作用は生じている場合があります。責任を一層に置き、安全に繰返せる一時障害だけ残り時間と回数を制限して再試行します。指数 backoff と jitter は分散しても飽和 DB の容量は増やしません。

## Java 例：承認した公開データだけを期限内で返す

**固定の公開商品説明一件**を読み、通常応答を優先し、`Unavailable` に分類した依存障害のみ最終成功コピーを使います。古さは60秒以下で、未来日時は拒否します。上限2と60秒は説明用の方針です。複数商品、言語、テナントはキーを分け、この固定例を認証済みユーザーデータに流用しません。

![許可がなければ拒否し、あれば主系を読み、指定障害だけでコピーの存在と古さを確認して代替を返す](/assets/diagrams/technical/ja-2026-10-31-failure-fallback.svg)

図は `read()` の判断です。許可取得後は主結果でも例外でも `finally` で解放します。タイムアウト、遮断器、更新は未実装です。実 HTTP アダプターは接続失敗や時間切れなど承認したものだけ `Unavailable` にします。401、403、404、スキーマ、プログラム誤りまで同じ例外にすると意味が変わります。

`FallbackDemo.java` に保存し JDK 21 以降で動かします。外部依存はありません。

```java
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.concurrent.Semaphore;
import java.util.function.Supplier;

public class FallbackDemo {
    record Snapshot(String value, Instant observedAt) {}
    record Reply(String value, String source, long ageSeconds) {}
    static class Unavailable extends RuntimeException {}
    static class Rejected extends RuntimeException {
        Rejected(String reason) { super(reason); }
    }

    static final class Catalog {
        private final Semaphore slots = new Semaphore(2);
        private final Clock clock;
        private final Duration maxAge = Duration.ofSeconds(60);

        Catalog(Clock clock) { this.clock = clock; }

        Reply read(Supplier<String> primary, Snapshot snapshot) {
            if (!slots.tryAcquire()) throw new Rejected("capacity");
            try {
                try {
                    return new Reply(primary.get(), "primary", 0);
                } catch (Unavailable failure) {
                    if (snapshot == null) throw new Rejected("missing");
                    Duration age = Duration.between(
                            snapshot.observedAt(), clock.instant());
                    if (age.isNegative() || age.compareTo(maxAge) > 0) {
                        throw new Rejected("age");
                    }
                    return new Reply(snapshot.value(), "snapshot", age.toSeconds());
                }
            } finally {
                slots.release();
            }
        }
    }

    static void rejected(String reason, Runnable action) {
        try {
            action.run();
        } catch (Rejected e) {
            if (!reason.equals(e.getMessage())) throw new AssertionError(e);
            System.out.println("rejected=" + reason);
            return;
        }
        throw new AssertionError("Expected rejection: " + reason);
    }

    public static void main(String[] args) {
        Instant now = Instant.parse("2026-10-31T00:00:00Z");
        Catalog catalog = new Catalog(Clock.fixed(now, ZoneOffset.UTC));
        Snapshot recent = new Snapshot("saved-description", now.minusSeconds(30));
        Supplier<String> down = () -> { throw new Unavailable(); };

        System.out.println(catalog.read(() -> "live-description", recent));
        System.out.println(catalog.read(down, recent));
        System.out.println(catalog.read(down,
                new Snapshot("boundary", now.minusSeconds(60))));
        rejected("age", () -> catalog.read(down,
                new Snapshot("old", now.minusSeconds(60).minusNanos(1))));
        rejected("age", () -> catalog.read(down,
                new Snapshot("future", now.plusSeconds(1))));
        rejected("missing", () -> catalog.read(down, null));

        try {
            catalog.read(() -> { throw new IllegalStateException("schema"); }, recent);
            throw new AssertionError("Unexpected fallback");
        } catch (IllegalStateException expected) {
            System.out.println("propagated=" + expected.getMessage());
        }

        // Hold both permits through nested calls; the third call must not run.
        catalog.read(() -> catalog.read(() -> {
            rejected("capacity", () -> catalog.read(() -> {
                throw new AssertionError("Primary ran without a permit");
            }, recent));
            return "inner";
        }, recent).value(), recent);
        System.out.println(catalog.read(() -> "recovered", recent));
    }
}
```

```sh
javac --release 21 FallbackDemo.java
java FallbackDemo
```

次は Zulu JDK `21.0.1+12-LTS` で得た出力です。

```text
Reply[value=live-description, source=primary, ageSeconds=0]
Reply[value=saved-description, source=snapshot, ageSeconds=30]
Reply[value=boundary, source=snapshot, ageSeconds=60]
rejected=age
rejected=age
rejected=missing
propagated=schema
rejected=capacity
Reply[value=recovered, source=primary, ageSeconds=0]
```

`source=snapshot` と `ageSeconds` は品質低下を伝えるアプリのメタデータで、HTTP `Age` ヘッダーを実装しません。上限の比較は正確な `Duration` を使い、表示だけ秒単位にします。

[Semaphore の `tryAcquire()`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/Semaphore.html)は許可がなければ待たず失敗します。代替応答も同じ上限内なので、飽和時はコピーさえ返しません。本番でコピー専用の軽い経路を許すならそれにも上限を設けます。入れ子呼出は決定的な枯渇の実演で同時負荷テストではありません。

成功読取の保存、更新、容量、追出し、集約、再起動後の復元は未実装です。本番では成功だけで更新し、**コピー返却時に保存日時を書き換えません**。毎回更新すると旧値が永遠に許容され得ます。長期コピーには時計調整を含む鮮度方針も必要です。

## 障害終了の条件も定める

[Google SRE の過負荷対応](https://sre.google/sre-book/handling-overload/)では代替さえ負担できなければエラーが必要です。受付拒否や有効コピー不足で一時利用不能なら契約に沿って 503 を使えます。確実な再試行時刻があれば `Retry-After` を送れますが集中は防ぎません。504 は gateway/proxy が上流応答を時間内に得られない意味で、全アプリの時間切れ用ではありません。[RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html#name-server-error-5xx)

遮断器が閉じた瞬間に全要求を戻すと再び圧倒し得ます。制限付き半開プローブで確認して徐々に増やし、コピー更新とキャッシュ再充填も制限します。通常応答の遅延、失敗率、DB 待機、滞留が範囲を超えた際の拡大停止や後退を事前に定め、比率と観測期間は実負荷試験で決めます。

初回は任意の読取経路に障害を注入し、コピーなし、鮮度境界、未来日時、満杯、未分類例外、復旧を確認します。実サーバーでは遅い応答、プール枯渇、全キャッシュ停止、主系と代替の同時失敗、復旧時の同時再試行も試します。

指標は通常、代替、拒否、失敗を分けます。HTTP 200 率だけでは大半が古い応答の障害を隠せます。代替率、古さ、依存別失敗、受付拒否、進行中要求を追います。**実際に業務を完了した要求と品質を落として処理した要求を区別**して影響低減を判断します。
