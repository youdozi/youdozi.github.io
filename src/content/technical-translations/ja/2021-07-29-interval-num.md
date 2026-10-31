---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2021-07-29-interval-num",
  "routeSlug": "2021-07-29-interval-num",
  "kind": "post",
  "title": "Java で x 間隔の数列を生成する：乗算前の型拡張",
  "description": "IntStream で x から x*n までの n 個の値を生成します。mapToLong だけでは int のオーバーフローを防げない理由と、正・負・ゼロの間隔を確認します。",
  "categories": [
    "coding-test"
  ],
  "tags": [
    "java",
    "algorithms"
  ],
  "sourcePath": "src/content/posts/en/2021-07-29-interval-num.md",
  "sourceSha256": "4674cdefcccdc5107e92b9fe49ee186426b25a096d2687d60d42724c51d29cf4",
  "draftSha256": "392a40b02ad20f3e2732819911e571de7be54d0c2dede755a0fd33db42bed1f1",
  "manifestPath": ".pipeline/technical-translations/batch-055/manifest.json",
  "manifestSha256": "1fe8bbde2d19f5780ba08f158519bd2d55fdec1dc863ec3bd9126705ddda372f",
  "publishedAt": "2026-10-31T15:21:36.540Z",
  "updatedAt": "2026-10-31T15:21:36.540Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 125,
    "approvedAt": "2026-10-31T15:21:36.540Z",
    "basis": "User explicitly requested applying all missing technical-post languages, review, verification and deployment on 2026-11-01, with standing PR merge authorization. Human approval denotes publication authorization; linguistic review is performed by AI, not human/native review."
  }
}
---
x から始まる n 個の値は、`x × 1` から `x × n` までです。結果が int の範囲を超えることがあるため、結果の配列と**乗算そのもの**の両方に long を使う必要があります。

[問題](https://school.programmers.co.kr/learn/courses/30/lessons/12954)では、x は -10,000,000 から 10,000,000、n は 1 から 1,000 です。最後の値の絶対値は 10,000,000,000 に達することがあるため、long の配列が必要です。

## 処理の流れ

![ゼロ始まりの添字を項番号に変え、乗算前に x を long に拡張してから順番に集めます。](/assets/diagrams/technical/ja-2021-07-29-interval-num.svg)

ゼロ始まりの添字を項番号に変え、乗算前に x を long に拡張してから順番に集めます。

## 添字を項番号に変換する

完全なクラスを `Solution.java` として保存します。原文のコードは Java 11 向けにコンパイルされ、JDK 17 で実行されています。

```java
import java.util.stream.IntStream;

public class Solution {
    public long[] solution(int x, int n) {
        return IntStream.range(0, n)
                .mapToLong(i -> (long) x * (i + 1))
                .toArray();
    }
}
```

[`IntStream.range(0, n)`](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/stream/IntStream.html) は 0 から n-1 までの添字を生成します。`i + 1` を掛けることで最初の値が x、最後が x×n になります。x×0 から始めると、求められる数列が変わってしまいます。

| x | n | 結果 |
| --- | --- | --- |
| 2 | 5 | `[2,4,6,8,10]` |
| -4 | 2 | `[-4,-8]` |
| 0 | 3 | `[0,0,0]` |

x が負なら値は減少し、x=0 ならすべてゼロになります。項の順番を保ってください。これはソートの問題ではありません。

## mapToLong だけでは積を保護できない

`mapToLong` の中でも、先に `x * (i + 1)` を評価すると、両オペランドが int なので int の乗算になります。`(long) (x * (i + 1))` も、オーバーフローが起きた後の型変換です。

この例では `(long) x * (i + 1)` により、先にオペランドの型を拡張します。原文の検証では、正負の境界について、それぞれ 10,000,000,000 と -10,000,000,000 で終わる参照配列全体を比較しています。より小さい正・負・ゼロの入力も、加算の繰り返しで作った配列と比較しています。

時間計算量は O(n)、戻り値の配列を含む空間計算量は O(n) です。問題の入力条件に従う実装であり、数列の長さや任意の API 入力を汎用的に検証するものではありません。

条件内で int に収まる計算は、[符号付きの合計](/en/posts/2021-07-22-plus-minus/)と[配列の内積](/en/posts/2021-07-22-dot-product/)を比較してください。[Java コーディング演習ガイド](/en/categories/coding-test/)では、配列の計算から文字列・コレクションへと学べます。
