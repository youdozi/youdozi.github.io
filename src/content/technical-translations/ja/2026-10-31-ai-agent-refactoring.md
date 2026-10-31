---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2026-10-31-ai-agent-refactoring",
  "routeSlug": "2026-10-31-ai-agent-refactoring",
  "kind": "post",
  "title": "AI エージェントでコードをリファクタリングする：動作維持と検証可能な変更",
  "description": "対象範囲、維持する動作、検証コマンドをエージェントに渡す。前後の Java 例とプロンプトで境界、例外、変更範囲、テストの信頼性を確かめる。",
  "categories": [
    "architecture"
  ],
  "tags": [
    "ai-agent",
    "refactoring",
    "java",
    "testing",
    "code-review",
    "developer-workflow"
  ],
  "sourcePath": "src/content/posts/en/2026-10-31-ai-agent-refactoring.md",
  "sourceSha256": "efd733fd275675221deef4ebffa545ba2f54a6819e72fed217917d6708e3e4b9",
  "draftSha256": "a2a8dfb0f507f3db34e16024d512c8479a4f17dfdd338917f5d738f0a367a41c",
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

**AI エージェントとのリファクタリングは、維持する動作と変更範囲を定め、実行証拠と差分で確認することから始まります。** 関数が短い、または「テスト成功」という申告だけでは完了できません。戻り値、例外、外部効果の維持と、検証の弱体化を見ます。

Git とテストに慣れた開発者向けの製品非依存ガイドです。特定 UI やモデルは前提にしません。プロンプトはコピーして調整できる作例で、特定製品の記録や性能実測ではありません。Java の実行結果は別に示します。

## 最初の依頼に何を含めるか？

[Martin Fowler の定義](https://refactoring.com/)は、外部から観測可能な動作を維持し内部構造を変えることです。方針変更や不具合修正は別にし、前後の差を評価します。

対象ファイルに加え呼出元、関連テスト、慣例、実際の検証コマンドを渡します。全リポジトリを無条件に読ませず判断に必要な経路から始めます。まず編集なしで現動作と根拠を説明させると、誤解による拡大を減らせます。

送料方針は以下の**説明用に定めた要件**であり、実サービスの方針や障害報告ではありません。

| 条件 | 維持する動作 |
| --- | --- |
| 注文小計が負 | `IllegalArgumentException("subtotal")` を送出 |
| 会員または小計 50,000 KRW 以上 | 基本送料 0 KRW |
| その他 | 基本送料 3,000 KRW |
| 離島、遠隔地 | 基本送料の無料に関係なく 3,000 KRW 追加 |

最初の依頼は次のように書けます。完全なコードを `ShippingRefactorDemo.java` に保存した前提です。編集を練習するなら先に `before()` の本体を `after()` にコピーします。以下の完全コードは比較用に完成版も含みます。

```text
ShippingRefactorDemo.java の before()、after()、main() を読み、分析だけ行ってください。
まだファイルを変更しないでください。

目的：before() の送料動作を保ちながら after() の分岐の入れ子を減らします。
入力金額は KRW 単位の long です。
負の金額の例外型とメッセージ、50,000 KRW の境界、
基本送料無料と遠隔地加算の組合せを確認してください。

現動作のコード上の根拠、既存のテスト範囲、
追加すべき境界、after() だけを変える最小変更を示してください。
不明な方針を推測して変えないでください。
```

この段階で有用なのは条件別の現動作と変更箇所で、抽象的な品質改善計画ではありません。「会員は常に送料 0 KRW」は遠隔地加算と矛盾するため実装前に直します。

## 小さく変えて動作を比較する

重複分岐から**基本送料と加算の計算を分離**します。入力、出力、例外を保ち戦略インターフェースや設定層は足しません。小さな変更なら構造だけが変わり方針が保たれるかに集中できます。[Google の小変更ガイド](https://google.github.io/eng-practices/review/developer/small-cls.html)

![負の小計は同じ例外とし、会員と無料条件から基本送料を計算し、遠隔地加算後の合計を返す](/assets/diagrams/technical/ja-2026-10-31-ai-agent-refactoring.svg)

図は下の `after()` の順序で、AI 内部ではありません。`before()`、`after()` は作例で、`main()` が明示期待値と相互結果を確認します。JDK 21 以降で外部依存なしに動きます。

```java
public class ShippingRefactorDemo {
    static final long FREE_THRESHOLD = 50_000;
    record Case(long subtotal, boolean member, boolean remote, long expected) {}

    static long before(long subtotal, boolean member, boolean remote) {
        if (subtotal < 0) throw new IllegalArgumentException("subtotal");
        if (member) {
            if (remote) return 3_000;
            return 0;
        }
        if (subtotal >= 50_000) {
            if (remote) return 3_000;
            return 0;
        }
        if (remote) return 6_000;
        return 3_000;
    }

    static long after(long subtotal, boolean member, boolean remote) {
        if (subtotal < 0) throw new IllegalArgumentException("subtotal");
        long base = (member || subtotal >= FREE_THRESHOLD) ? 0 : 3_000;
        long surcharge = remote ? 3_000 : 0;
        return base + surcharge;
    }

    static void equal(long actual, long expected) {
        if (actual != expected) {
            throw new AssertionError("expected=" + expected + ", actual=" + actual);
        }
    }

    public static void main(String[] args) {
        Case[] examples = {
            new Case(0, false, false, 3_000),
            new Case(49_999, false, false, 3_000),
            new Case(50_000, false, false, 0),
            new Case(0, true, false, 0),
            new Case(49_999, false, true, 6_000),
            new Case(50_000, false, true, 3_000),
            new Case(0, true, true, 3_000),
            new Case(Long.MAX_VALUE, false, true, 3_000)
        };
        for (Case c : examples) {
            equal(before(c.subtotal(), c.member(), c.remote()), c.expected());
            equal(after(c.subtotal(), c.member(), c.remote()), c.expected());
        }
        System.out.println("examples=" + examples.length);

        int comparisons = 0;
        long[] amounts = {0, 1, 49_999, 50_000, 50_001, Long.MAX_VALUE};
        for (long subtotal : amounts) {
            for (boolean member : new boolean[] {false, true}) {
                for (boolean remote : new boolean[] {false, true}) {
                    equal(after(subtotal, member, remote), before(subtotal, member, remote));
                    comparisons++;
                }
            }
        }
        System.out.println("comparisons=" + comparisons);

        int rejected = 0;
        for (boolean refactored : new boolean[] {false, true}) {
            try {
                if (refactored) after(-1, false, false);
                else before(-1, false, false);
                throw new AssertionError("Negative amount was accepted");
            } catch (IllegalArgumentException e) {
                if (!"subtotal".equals(e.getMessage())) throw new AssertionError(e);
                rejected++;
            }
        }
        System.out.println("negative-inputs=" + rejected);
    }
}
```

```sh
javac --release 21 ShippingRefactorDemo.java
java ShippingRefactorDemo
```

次は Zulu JDK `21.0.1+12-LTS` の出力です。`after()` と `before()` が同じ本体の初期版も、下の完成版も同じ出力でした。

```text
examples=8
comparisons=24
negative-inputs=2
```

`-ea` オプション次第で無効になる Java `assert` ではなく、違いがあれば直接 `AssertionError` を投げます。数は指定ケースと入力組合せで、本番全体の網羅率ではありません。

実装依頼では確認済み条件と編集範囲、実行コマンドをつなぎます。

```text
前述の送料契約を保ち、after() だけをリファクタリングしてください。
before()、main()、期待値、FREE_THRESHOLD は変えないでください。
公開入力と出力、例外型とメッセージを保ち、依存や層を追加しないでください。
ファイル外の変更が必要なら適用せず理由を説明してください。

javac --release 21 ShippingRefactorDemo.java と java ShippingRefactorDemo を実行してください。
実際のコマンド、終了値、観測出力、変更 diff を示してください。
失敗時は条件と原因を絞って直し、検査削除や期待値変更で通さないでください。
```

編集や実行できない環境なら、自分でパッチを適用し同じコマンドを動かします。「変更しない」という指示は範囲の伝達で、ツール権限やファイル制限の代わりではありません。

## テスト成功と動作維持は同じか？

8 期待値、24 入力組合せ、両メソッドの負入力例外を調べますが、全 `long` の同等性証明ではありません。`before()` だけを正解にすると既存欠陥を保つ場合があるため独立期待値と業務要件も使います。欠陥発見時は修正可否と変える動作を別に決めます。

反例で差異検出を試せます。`after()` の `subtotal >= FREE_THRESHOLD` を `subtotal > FREE_THRESHOLD` にすると、非会員のちょうど 50,000 KRW が無料対象外になり期待値検査が失敗するはずです。

一時コピーでこの境界だけ誤変更すると `AssertionError: expected=0, actual=3000` で失敗することを確認しました。特定の誤りの検出で、全誤変更の保証ではありません。完成コードには適用していません。

実際は戻り値以外の例外、DB 問合せとトランザクション境界、外部呼出数と順序、直列化、資源解放も確認します。純粋関数の成功は DB/HTTP を検証しません。性能目標には入力と環境を固定した別測定が必要です。

## 最終レビューは説明より差分から始める

説明より先に差分と実行結果を見て、不要な変更、テスト削除や skip、例外の握り潰し、無関係な依存を探します。`git diff --check` は空白等の確認で業務テストではありません。

別レビュー環境があれば、成功申告でなく元要件、前後コード、diff、実行証拠を渡します。レビューも誤るため各指摘を証拠と照合します。[GitHub の制約文書](https://docs.github.com/en/copilot/responsible-use/agents)も生成コードや指摘の不正確さを説明しています。

```text
変更せずにレビューしてください。
入力：送料要件、前後コード、diff、テストコマンド、実際の結果。

戻り値、例外、50,000 KRW 境界、遠隔地料金を変える反例を探してください。
範囲外変更とテスト弱体化も確認してください。
各指摘に場所、入力例、観測できる違い、根拠を付けてください。
未実行の検査を実行したと主張しないでください。
```

引継ぎは構造変更、維持動作、実施検査、残る範囲を短く伝えます。失敗なら入力と期待を強めて修正を絞り、膨らめば分割します。**動作維持の理由をレビュー者が説明できる小さな変更**は AI とも有用な完了単位です。
