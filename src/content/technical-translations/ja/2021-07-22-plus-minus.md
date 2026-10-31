---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2021-07-22-plus-minus",
  "routeSlug": "2021-07-22-plus-minus",
  "kind": "post",
  "title": "Java の IntStream で符号付きの値を合計する",
  "description": "絶対値と対応する真偽値の符号を IntStream で組み合わせます。相殺、全要素が負の場合、int の範囲、配列の長さが等しいという契約を確認します。",
  "categories": [
    "coding-test"
  ],
  "tags": [
    "java",
    "algorithms"
  ],
  "sourcePath": "src/content/posts/en/2021-07-22-plus-minus.md",
  "sourceSha256": "63f6b289759a3487a5cb548baedd43054c6fa803aa1dbd58a39dd4d088a413bc",
  "draftSha256": "e9b8b4ceb095fa004e17653d10bc9a6e52663f865e20d64dc02ecfd5a5560124",
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
絶対値と符号が別々に与えられた場合は、対応する添字で符号を適用してから合計します。`signs[i]` は true なら正、false なら負を意味するため、一つの条件式で各値を復元できます。

この[問題](https://school.programmers.co.kr/learn/courses/30/lessons/76501)では、配列の長さが等しく 1 から 1,000、絶対値が 1 から 1,000 であることが保証されています。符号だけを並べ替えると元の値との対応が崩れるため、配列は与えられた順序で処理します。

## 処理の流れ

![両配列の同じ添字を読み、符号を適用してから、符号付きの値を合計します。](/assets/diagrams/technical/ja-2021-07-22-plus-minus.svg)

両配列の同じ添字を読み、符号を適用してから、符号付きの値を合計します。

## 対応する添字を一緒に読む

次の完全なクラスを `Solution.java` として保存します。Java 11 向けにコンパイルし、JDK 17 で実行済みです。

```java
import java.util.stream.IntStream;

public class Solution {
    public int solution(int[] absolutes, boolean[] signs) {
        return IntStream.range(0, absolutes.length)
                .map(i -> signs[i] ? absolutes[i] : -absolutes[i])
                .sum();
    }
}
```

[`IntStream.range`](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/stream/IntStream.html) は添字 0 を含み、`absolutes.length` を含みません。`map` で各絶対値に符号を適用し、`sum` でその結果を足します。このメソッドは入力を変更せず、符号付きの値を格納する別の配列も作りません。

| 絶対値 | 符号 | 実際の値 |
| --- | --- | --- |
| 4 | true | 4 |
| 7 | false | -7 |
| 12 | true | 12 |

これらの合計は 9 です。入力が `[1,2,3]` と `[false,false,true]` なら、相殺されて 0 になります。正と負のフラグの数を数えるだけでは不十分です。各項の**絶対値**も関係します。

## 整数の範囲と契約

項数は最大 1,000、各項の絶対値は最大 1,000 なので、合計の絶対値は 1,000,000 以下です。すべて正、またはすべて負の境界値も int に収まります。時間計算量は O(n)、追加領域は O(1) です。

このメソッドは、問題に従った有効な絶対値と同じ長さを前提としています。任意のアプリケーション入力に必要な null、長さ、値の検証を代替するものではありません。範囲が広がる場合は、項と累積用の変数の両方について型を再検討する必要があります。

別の二つの配列の計算として[配列の内積](/en/posts/2021-07-22-dot-product/)を、int を超える結果については[long を使った x 間隔の数列](/en/posts/2021-07-29-interval-num/)を参照してください。学習の順序は [Java コーディング問題ガイド](/en/categories/coding-test/)にまとめています。
