---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2026-10-31-cache-aside",
  "routeSlug": "2026-10-31-cache-aside",
  "kind": "post",
  "title": "API キャッシュ設計：キー、TTL、無効化と障害時のオリジン保護",
  "description": "Cache-Aside で配置、キー、TTL、無効化、同時ミスを説明する。Java で期限と容量を確認し、障害時の DB 保護を定義する。",
  "categories": [
    "architecture"
  ],
  "tags": [
    "caching",
    "cache-aside",
    "ttl",
    "cache-invalidation",
    "java",
    "resilience"
  ],
  "sourcePath": "src/content/posts/en/2026-10-31-cache-aside.md",
  "sourceSha256": "2c4422c55f14e7b5452f8b286bf5d6f986617fe624e229b7bd74462afe525ad9",
  "draftSha256": "0e192a977b9ea38cd42cc7c234c243dc4227a946352e752e56b37e47e913fcae",
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

**キャッシュは取得済みの結果を再利用し、オリジンの読取や計算を減らします。** 共有できるリクエスト、再利用期間、元データ変更時の更新方法を先に定めます。他人のデータを返したり古い価格で購入を確定したりするなら、高いヒット率でも正しくありません。

読取 API にキャッシュを検討する開発者向けに、商品説明など多少の遅延を許すデータで Cache-Aside を説明し、TTL と容量制限を Java で実行します。決済や在庫の確定など現在の状態が必要な操作は別です。障害時の古いデータの許可方針は[フォールバック設計](/ko/posts/2026-10-31-failure-fallback/)につながります。

## 何をどこにキャッシュするか？

繰返し読まれ、オリジン取得が高コストで、限られた古さを許す経路から始めます。一度限り、またはほぼユーザー固有のデータは、保存や無効化の費用がヒットの利益を上回る場合があります。

| 配置場所 | 減らせるコスト | 同時に定める条件 |
| --- | --- | --- |
| ブラウザー、CDN の HTTP キャッシュ | ネットワーク往復、API 到達数 | 共有可否、URL と `Vary`、`Cache-Control` |
| アプリ内ローカルキャッシュ | 遠隔キャッシュ往復、DB 読取、重複計算 | プロセス別メモリー上限、レプリカ間の値の差 |
| Redis 等の共有キャッシュ | レプリカをまたぐ重複オリジン読取 | 遅延、障害動作、直列化、保存容量 |

全層を一度に使う必要はありません。ローカルは速い一方で各レプリカが別コピーを持ちます。共有型は重複保存を減らせますが、ネットワークと運用への依存が増えます。多層なら無効化も全層に届けます。

## Cache-Aside の動作は？

先にキャッシュを調べ、未登録や期限切れならオリジンを読み結果を保存するのが **Cache-Aside** です。書込は通常、元の変更をコミットしてから該当キーを無効化します。キャッシュ消失でも元データは残り、唯一の記録として使う場合とは異なります。[Microsoft の説明](https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside)

結果を変える入力をキーに含めます。たとえば `Key(tenant, product, language)` はテナント、商品、言語別のエントリーを表します。通貨、権限、表現形式の版でも変わるならキーや範囲を分けます。区切りなしの連結は衝突し得るため構造化キーや一意に解釈できる符号化を使います。

テナント ID をキーに入れるだけでは認可は終わりません。信頼できる認証コンテキストからテナントを決め、検索前にアクセスを確認します。トークンやパスワードをキーやログへ直接入れません。

**TTL は値を再利用できる期間、容量制限は保存できる量です。** TTL だけなら期限まで蓄積し、容量だけなら古い値がヒットし続けます。件数と実バイト数は異なるため、大きな応答はオブジェクトや直列化後のサイズも考慮します。

## Java 例：キー分離、期限、無効化、容量制限

以下はテナント別商品説明の**ローカルキャッシュの意味を示す小さな例**です。TTL 5秒、最大2件は観察用で本番推奨ではありません。`LinkedHashMap` のアクセス順で最も長く未参照のものを先に追い出します。[Java 21 文書](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/LinkedHashMap.html)

![TTL 内ならキーの値を返し、ミスや期限切れなら元を読み成功値だけ保存し容量超過分を除いて返す](/assets/diagrams/technical/ja-2026-10-31-cache-aside.svg)

図は `get()` です。ローダー失敗時は例外を伝播し新値は保存しません。`invalidate()` は元の変更後に呼ぶ別操作です。

`CacheDemo.java` に保存し JDK 21 以降で動かします。外部サーバーやライブラリは不要です。

```java
import java.time.Duration;
import java.util.LinkedHashMap;
import java.util.Objects;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Function;
import java.util.function.LongSupplier;

public class CacheDemo {
    record Key(String tenant, String product, String language) {}
    record Entry(String value, long loadedAt) {}

    static final class LocalCache {
        private final LinkedHashMap<Key, Entry> entries =
                new LinkedHashMap<>(16, 0.75f, true);
        private final LongSupplier ticker;
        private final long ttl = Duration.ofSeconds(5).toNanos();
        private final int maximumSize = 2;

        LocalCache(LongSupplier ticker) { this.ticker = ticker; }

        synchronized String get(Key key, Function<Key, String> loader) {
            Entry entry = entries.get(key);
            long now = ticker.getAsLong();
            if (entry != null && now - entry.loadedAt() < ttl) {
                return entry.value();
            }
            entries.remove(key);
            String value = Objects.requireNonNull(loader.apply(key));
            entries.put(key, new Entry(value, ticker.getAsLong()));
            if (entries.size() > maximumSize) {
                entries.remove(entries.keySet().iterator().next());
            }
            return value;
        }

        synchronized void invalidate(Key key) { entries.remove(key); }
    }

    static void expect(String actual, String expected) {
        if (!actual.equals(expected)) throw new AssertionError(actual);
        System.out.println(actual);
    }

    public static void main(String[] args) {
        AtomicLong clock = new AtomicLong();
        AtomicInteger loads = new AtomicInteger();
        LocalCache cache = new LocalCache(clock::get);
        Function<Key, String> loader = key ->
                key.tenant() + "/" + key.language() + "/v" + loads.incrementAndGet();
        Key ko = new Key("shop-a", "p1", "ko");
        Key en = new Key("shop-a", "p1", "en");
        Key other = new Key("shop-b", "p1", "ko");

        expect(cache.get(ko, loader), "shop-a/ko/v1");
        expect(cache.get(ko, loader), "shop-a/ko/v1");
        clock.set(Duration.ofSeconds(5).toNanos() - 1);
        expect(cache.get(ko, loader), "shop-a/ko/v1");
        clock.incrementAndGet();
        expect(cache.get(ko, loader), "shop-a/ko/v2");
        cache.invalidate(ko);
        expect(cache.get(ko, loader), "shop-a/ko/v3");
        expect(cache.get(en, loader), "shop-a/en/v4");
        expect(cache.get(ko, loader), "shop-a/ko/v3");
        expect(cache.get(other, loader), "shop-b/ko/v5");
        expect(cache.get(en, loader), "shop-a/en/v6");

        Key failing = new Key("shop-c", "p1", "ko");
        try {
            cache.get(failing, key -> { throw new IllegalStateException("origin"); });
            throw new AssertionError("Failure was swallowed");
        } catch (IllegalStateException expected) {
            expect(expected.getMessage(), "origin");
        }
        expect(cache.get(failing, loader), "shop-c/ko/v7");
    }
}
```

```sh
javac --release 21 CacheDemo.java
java CacheDemo
```

以下は Zulu JDK `21.0.1+12-LTS` で得た出力です。

```text
shop-a/ko/v1
shop-a/ko/v1
shop-a/ko/v1
shop-a/ko/v2
shop-a/ko/v3
shop-a/en/v4
shop-a/ko/v3
shop-b/ko/v5
shop-a/en/v6
origin
shop-c/ko/v7
```

同じキーの最初の三読取は元を一回だけ読みます。期限の 1ns 前は同じ値、ちょうど5秒で再読込です。その後は明示無効化、言語、テナント分離、アクセス順の追出し、失敗後の成功読取を確認します。`v1` 等はテストローダーの呼出順で実 DB の版ではありません。

sleep せず手動で進める単調時計で時間を再現します。実プロセスでは `new LocalCache(System::nanoTime)` を経過時間計として渡せます。期限切れは参照時に処理し即時の背景削除はしません。上限は件数でバイト数ではありません。

簡略化のためローダーも `synchronized` 内です。別キーでも同インスタンスへの呼出は直列化され、遅いローダーへの待機件数は無制限です。高性能な本番実装ではなく、後述のキー別 single-flight、呼出上限、タイムアウト、レプリカ間無効化は未実装です。順次シナリオを確認し、同時負荷テストはしていません。

## TTL と無効化で最新値を保証できるか？

できません。TTL は**元の読取完了後に保存した時点**から測ります。元が遅延レプリカや旧スナップショットなら TTL 5秒でも変更から5秒以内の最新化ではありません。読取、複製、無効化伝播の遅延も考慮します。

共有キャッシュの複数レプリカでは DB 更新後に削除しても競合します。読取 A が旧値を取り始め、書込 B が新値を確定して削除した後、遅れた A が旧値を再保存します。TTL は残存時間を減らしても競合をなくしません。

現在状態が必須なら元のトランザクションで再確認するか、版と条件付き書込等で遅延結果の上書きを防ぎます。イベント無効化は欠落、重複、コミットから配信までの遅延を扱います。一変更が一覧、詳細、集計など複数キーへ影響するなら無効化範囲も定めます。

`expire-after-write` と `expire-after-access` を区別します。参照ごとの延長は頻繁に読まれる旧値を長期間残し得ます。回数に関係なく保存後の固定時間で再確認したいなら、書込基準の期限が目的に合うか検討します。[Caffeine の期限と追出し](https://github.com/ben-manes/caffeine/wiki/Eviction)

## 同時期限切れや障害時は？

人気キーの期限直後に全要求が元を読むと **cache stampede** が起きます。同キー読取を一つの進行中処理にまとめる single-flight と、元への同時数、待機時間の制限を使います。一プロセスの集約は全レプリカの集約ではありません。[Caffeine の原子的検索、ロード API](https://github.com/ben-manes/caffeine/wiki/Population)も選べますが、それだけで全サービスの元負荷を制限はできません。

多数の TTL が重なる場合はジッターで分散します。鮮度上限が60秒なら60秒を超えない範囲に収めます。単一人気キーへの集中は解決しません。古い応答を許す経路だけで stale-while-revalidate を使い、更新失敗継続時の最大経過時間も別に設定します。

障害時の全 DB 転送も危険です。例として読取 10,000 RPS、通常ヒット率90% なら元は約 1,000 RPS、全ヒット消失で同じ分布でも 10,000 RPS になります。計算例で実測ではなく、再試行や更新は含みません。

元が耐えられなければ bypass を制限し、承認済みのローカルコピー、機能縮小、超過拒否を使います。障害とミスを別観測し復旧時の一括ロードを制限します。不存在 ID の繰返しには短い負キャッシュも有効ですが、元の障害を「データなし」と保存しません。新規データを読めるよう TTL と無効化も定めます。

## HTTP とアプリのキャッシュを分ける

ブラウザーや CDN は応答ヘッダーで再利用方針を伝え、JVM 内オブジェクトの TTL とは別の層です。

| 指令 | 意味 |
| --- | --- |
| `max-age=60` | age が60秒未満の間は新鮮 |
| `s-maxage=60` | 共有キャッシュの鮮度期間を指定し、そこで `max-age` 等を上書き |
| `private` | 共有キャッシュの保存を制限。ブラウザー等の私有型は保存可 |
| `no-cache` | 保存可だが再利用前に元の検証成功が必要 |
| `no-store` | 要求、応答を保存しない指示。既存コピーの削除命令ではない |

`Accept-Language` で言語を選ぶなら `Vary` と実設定に反映します。URL が言語別ならそれもキーです。変更なしの場合 `ETag` と条件付き要求は転送量を減らせますが、元の検証費用を常になくせません。`private`、`no-store` は認証、認可、暗号化を代替しません。[RFC 9111：HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111.html)

一読取経路から検証します。通常ヒットに加え、TTL 境界、書込直後、テナントと言語をまたぐ同 ID、容量上限、同時ミス、障害、復旧を確認します。本番はヒット率とともに元呼出数、遅延、失敗率、進行中ロード、追出し、メモリー、無効化遅延を追います。**応答が正しく、キャッシュなしでも元が耐えるか**を確認して初めて効果を判断できます。
