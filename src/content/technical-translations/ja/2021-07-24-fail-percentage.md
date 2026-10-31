---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2021-07-24-fail-percentage",
  "routeSlug": "2021-07-24-fail-percentage",
  "kind": "post",
  "title": "Java の失敗率ソート：分母・同率・long の積",
  "description": "停止人数と到達人数を数え、long の交差積で失敗率を正確に比較します。未到達のステージ、全クリア、同率時の番号順を扱います。",
  "categories": [
    "coding-test"
  ],
  "tags": [
    "java",
    "algorithms"
  ],
  "sourcePath": "src/content/posts/en/2021-07-24-fail-percentage.md",
  "sourceSha256": "c684945a1636e85bfe7ce5165815a7785215f97a78fa784c21dd34e8f275d30b",
  "draftSha256": "6f5b734c721fbed31a6a24422540d3ac61181395ef490ee57e6270f3efc75cd2",
  "manifestPath": ".pipeline/technical-translations/batch-056/manifest.json",
  "manifestSha256": "5c3bd2ee5ccb0b59bad65322a026d7b2ef52cfac963e0236a497f74510717e42",
  "publishedAt": "2026-10-31T15:21:36.846Z",
  "updatedAt": "2026-10-31T15:21:36.846Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 125,
    "approvedAt": "2026-10-31T15:21:36.846Z",
    "basis": "User explicitly requested applying all missing technical-post languages, review, verification and deployment on 2026-11-01, with standing PR merge authorization. Human approval denotes publication authorization; linguistic review is performed by AI, not human/native review."
  }
}
---
ステージの失敗率の分母は、全プレイヤー数ではなく、そのステージに到達した人数です。停止した場所を数え、残りの到達人数を更新し、失敗率の降順・ステージ番号の昇順に並べます。

[問題](https://school.programmers.co.kr/learn/courses/30/lessons/42889)ではステージ数 N は最大 500、プレイヤー数 M は最大 200,000 です。入力の N+1 は全ステージをクリアした人を表し、それ自体は順位付けするステージではありません。誰も到達していないステージの失敗率は 0 です。

## 処理の流れ

![停止人数を引く前に到達人数を保存します。long の交差積で比率を比較し、同率ならステージ番号順に並べます。](/assets/diagrams/technical/ja-2021-07-24-fail-percentage.svg)

停止人数を引く前に到達人数を保存します。long の交差積で比率を比較し、同率ならステージ番号順に並べます。

## 停止人数と到達人数を数える

完全なクラスを `Solution.java` として保存します。原文のコードは Java 11 向けにコンパイルされ、JDK 17 で実行されています。

```java
import java.util.Arrays;
import java.util.stream.IntStream;

public class Solution {
    public int[] solution(int N, int[] stages) {
        long[] stopped = new long[N + 2];
        for (int stage : stages) stopped[stage]++;
        long[] reached = new long[N + 1];
        long remaining = stages.length;
        for (int stage = 1; stage <= N; stage++) {
            reached[stage] = remaining;
            remaining -= stopped[stage];
        }
        Integer[] order = IntStream.rangeClosed(1, N).boxed().toArray(Integer[]::new);
        Arrays.sort(order, (a, b) -> {
            long denominatorA = reached[a] == 0 ? 1 : reached[a];
            long denominatorB = reached[b] == 0 ? 1 : reached[b];
            int byRate = Long.compare(stopped[b] * denominatorA, stopped[a] * denominatorB);
            return byRate != 0 ? byRate : Integer.compare(a, b);
        });
        return Arrays.stream(order).mapToInt(Integer::intValue).toArray();
    }
}
```

`remaining` は現在のステージに到達した人数です。停止人数を引く**前に** `reached[stage]` を保存すると、更新後の値が次のステージの分母になります。N+1 の人は、すべてのステージで分母に残ります。

N=5、入力が `[2,1,2,6,2,4,3,3]` の場合、失敗率は次のとおりです。

| ステージ | 停止人数 | 到達人数 | 失敗率 |
| --- | --- | --- | --- |
| 1 | 1 | 8 | 1/8 |
| 2 | 3 | 7 | 3/7 |
| 3 | 2 | 4 | 2/4 |
| 4 | 1 | 2 | 1/2 |
| 5 | 0 | 1 | 0/1 |

ステージ 3 と 4 は同率なので、小さい番号を先にします。最終順序は `[3,4,2,1,5]` です。

## 数値範囲内で比率を比較する

分母が正なら、二つの比率は交差乗算で比較できます。降順にするため、`Long.compare` の最初の引数には b の分子と a の分母の積を渡します。同率なら `Integer.compare(a, b)` でステージ番号を並べます。これは [Comparator の契約](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Comparator.html)に従い、順序を明示するものです。

誰も到達していなければ、有効な入力ではそのステージの停止人数もゼロです。比較用の分母を 1 にし、率を 0/1 として表します。両方の人数は 200,000 に達し得るため、積の上限は 40,000,000,000 です。int の範囲を超えるので、配列も乗算も long のままにします。積の差を int にキャストして比較結果にしてはいけません。

人数の集計は O(M)、到達人数の計算は O(N)、ソートは O(N log N) です。全体は O(M + N log N) 時間、追加領域 O(N) で、入力は変更しません。全員が全ステージをクリアした場合、すべての率がゼロになり、ステージ番号順になります。

入力範囲から乗算の型を選ぶ別の例は、[配列の内積における int と long](/en/posts/2021-07-22-dot-product/)を参照してください。
