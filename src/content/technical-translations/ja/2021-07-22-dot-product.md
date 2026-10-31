---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2021-07-22-dot-product",
  "routeSlug": "2021-07-22-dot-product",
  "kind": "post",
  "title": "Java の配列の内積：IntStream と整数の範囲",
  "description": "IntStream で配列の同じ位置の要素を掛けて合計します。符号、int の範囲、乗算でオーバーフローする前に型を拡張する理由を説明します。",
  "categories": [
    "coding-test"
  ],
  "tags": [
    "java",
    "algorithms"
  ],
  "sourcePath": "src/content/posts/en/2021-07-22-dot-product.md",
  "sourceSha256": "aa027f07c568f5c9d25dc08d3ee21ea8c23917f73f1409b25b221ad21be86463",
  "draftSha256": "092530c40fbacc8d05b70655c6f57989c8c0b6c370215c95eefb06221f0099dc",
  "manifestPath": ".pipeline/technical-translations/batch-050/manifest.json",
  "manifestSha256": "e57f8d6a3aeeb6da0cb9abf684356147993428fb695af669351ebfcfd6c865aa",
  "publishedAt": "2026-10-31T15:21:35.938Z",
  "updatedAt": "2026-10-31T15:21:35.938Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 125,
    "approvedAt": "2026-10-31T15:21:35.938Z",
    "basis": "User explicitly requested applying all missing technical-post languages, review, verification and deployment on 2026-11-01, with standing PR merge authorization. Human approval denotes publication authorization; linguistic review is performed by AI, not human/native review."
  }
}
---
二つの配列の内積は、同じ添字の要素を掛けた値の合計です。先に要素を足したり、各配列の合計同士を掛けたりすると、別の計算になります。

この[問題](https://school.programmers.co.kr/learn/courses/30/lessons/70128)では、長さが等しい整数配列が与えられます。長さは 1–1,000、要素は -1,000 から 1,000 です。この範囲なら、結果は `int` に収まります。

## 処理の流れ

![共通の添字ごとに要素の積を求め、その積を合計します。問題の制約では int に収まります。](/assets/diagrams/technical/ja-2021-07-22-dot-product.svg)

共通の添字ごとに要素の積を求め、その積を合計します。問題の制約では int に収まります。

## 添字ごとに積を求めて合計する

次の完全なクラスを `Solution.java` として保存します。Java 11 向けにコンパイル済みで、入力配列の長さが等しいことを前提としています。

```java
import java.util.stream.IntStream;

public class Solution {
    public int solution(int[] a, int[] b) {
        return IntStream.range(0, a.length)
                .map(i -> a[i] * b[i])
                .sum();
    }
}
```

[`IntStream.range(0, a.length)`](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/stream/IntStream.html) は終端の添字を含みません。各添字を `a[i] * b[i]` に変換し、`sum()` で積を合計します。プリミティブ型の添字ストリームなので、ボックス化した Integer のリストを作る必要はありません。

`[1, 2, 3, 4]` と `[-3, -1, 0, 2]` の場合、積は `-3, -2, 0, 8` となり、結果は 3 です。負の符号は保持してください。絶対値を取ると内積が変わります。

## int で十分な範囲

各積の絶対値は最大 1,000,000、項数は最大 1,000 です。したがって合計の絶対値は 1,000,000,000 以下で、Java の int の範囲内です。境界値の確認では、1,000 項での正負それぞれの最大の合計も対象としています。

入力の範囲が広がる場合、累積用の変数を long に変えるだけでは不十分なことがあります。`(long) (a[i] * b[i])` は、int の乗算でオーバーフローした後に変換します。`(long) a[i] * b[i]` として乗算の**前に**型を拡張し、合計と戻り値の型も long に設計します。ここで提出するメソッドは、問題の int という契約を維持しています。

時間計算量は O(n)、追加領域は O(1) です。長さの不一致、null 配列、範囲外の要素を検証する汎用ベクトルライブラリではありません。

決められた英語の数字名を整数に変換する方法は、[数字の単語と数値文字列](/en/posts/2021-07-23-number-word/)を参照してください。
