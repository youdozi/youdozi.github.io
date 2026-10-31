---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2021-07-24-fail-percentage",
  "routeSlug": "2021-07-24-fail-percentage",
  "kind": "post",
  "title": "Java 失败率排序：分母、并列与 long 交叉乘积",
  "description": "统计停留和到达人数，用 long 交叉乘积精确比较失败率，处理无人到达、全部通关和关卡编号的并列规则。",
  "categories": [
    "coding-test"
  ],
  "tags": [
    "java",
    "algorithms"
  ],
  "sourcePath": "src/content/posts/en/2021-07-24-fail-percentage.md",
  "sourceSha256": "c684945a1636e85bfe7ce5165815a7785215f97a78fa784c21dd34e8f275d30b",
  "draftSha256": "1ae941fb06e7e4d616b7a1fcd72ad394adcf33ba1a53bfa4b59c40e844eff9c3",
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
某关卡失败率的分母是到达该关卡的玩家人数，而非全部玩家人数。先统计玩家停留在哪一关，再更新剩余到达人数，最后按失败率降序、关卡编号升序排序。

[题目](https://school.programmers.co.kr/learn/courses/30/lessons/42889)规定关卡数 N 最多为 500，玩家数 M 最多为 200,000。输入中的 N+1 表示通关全部关卡的玩家，本身不是要参与排序的关卡。无人到达的关卡失败率为 0。

## 处理流程

![先保存到达人数，再扣除停留人数。用 long 交叉乘积比较比例，相同时按关卡编号排序。](/assets/diagrams/technical/zh-CN-2021-07-24-fail-percentage.svg)

先保存到达人数，再扣除停留人数。用 long 交叉乘积比较比例，相同时按关卡编号排序。

## 统计停留和到达人数

将完整类保存为 `Solution.java`。原文代码已按 Java 11 目标编译，并在 JDK 17 上执行。

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

`remaining` 表示到达当前关卡的人数。必须在扣除该关停留人数**之前**保存 `reached[stage]`，更新后的值才是下一关的分母。位于 N+1 的玩家始终保留在分母中。

N=5，输入为 `[2,1,2,6,2,4,3,3]` 时，各失败率如下：

| 关卡 | 停留人数 | 到达人数 | 失败率 |
| --- | --- | --- | --- |
| 1 | 1 | 8 | 1/8 |
| 2 | 3 | 7 | 3/7 |
| 3 | 2 | 4 | 2/4 |
| 4 | 1 | 2 | 1/2 |
| 5 | 0 | 1 | 0/1 |

关卡 3 和 4 失败率相同，因此编号较小者在前。最终顺序为 `[3,4,2,1,5]`。

## 在数值范围内比较比例

分母为正时，可通过交叉相乘比较两个比例。为了降序排列，`Long.compare` 的第一个参数是 b 的分子乘以 a 的分母。失败率相同时，用 `Integer.compare(a, b)` 排列关卡编号。这按 [Comparator 约定](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Comparator.html)明确规定了顺序。

若无人到达某关卡，有效输入也保证该关停留人数为零。比较时将分母设为 1，把失败率表示为 0/1。两个人数都可能达到 200,000，因此乘积上限为 40,000,000,000。数组与乘法都应使用 long，因为这个值超出了 int 范围。不要将乘积之差转换为 int 作为比较结果。

统计人数需要 O(M)，计算到达人数需要 O(N)，排序需要 O(N log N)。总时间为 O(M + N log N)，额外空间为 O(N)，且不修改输入。如果所有玩家都通关，全部失败率为零，此时按关卡编号排序。

关于根据输入范围选择乘法类型的另一示例，可参阅[数组内积中的 int 与 long](/en/posts/2021-07-22-dot-product/)。
