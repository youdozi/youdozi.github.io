---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2021-07-23-unsuccessful-runner",
  "routeSlug": "2021-07-23-unsuccessful-runner",
  "kind": "post",
  "title": "Java 用姓名频次找出未完成比赛的选手",
  "description": "使用 HashMap 将完赛频次从参赛频次中扣除，处理重名，说明为什么不能用 Set 差集及只有一名未完赛者的条件。",
  "categories": [
    "coding-test"
  ],
  "tags": [
    "java",
    "algorithms"
  ],
  "sourcePath": "src/content/posts/en/2021-07-23-unsuccessful-runner.md",
  "sourceSha256": "a8c9e485842a9d8718e6cec7f5d0bcbda5a716bad751608cc67094ac938487d6",
  "draftSha256": "5326c33f1beeb0beefa8fbbc36126d6d85d289c8ae428d9965f73a7a740b46ec",
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
要找出未完成比赛的选手，需要按姓名统计人数，而非只检查姓名是否存在。将完赛频次从参赛频次中扣除；题目保证最终恰好只有一个姓名的剩余人数为 1。

[输入约束](https://school.programmers.co.kr/learn/courses/30/lessons/42576)允许最多 100,000 名参赛者，完赛者少一人，并允许重名。姓名由 1–20 个小写英文字母组成。假设完赛名单是从有效参赛名单中移除一人后得到的。

## 处理流程

![统计每位参赛者，逐一扣除完赛者，再返回剩余人数为一的姓名。](/assets/diagrams/technical/zh-CN-2021-07-23-unsuccessful-runner.svg)

统计每位参赛者，逐一扣除完赛者，再返回剩余人数为一的姓名。

## 保存人数差

将完整类保存为 `Solution.java`。原文中的代码已按 Java 11 目标编译，并在 JDK 17 上执行。

```java
import java.util.HashMap;
import java.util.Map;

public class Solution {
    public String solution(String[] participant, String[] completion) {
        Map<String, Integer> counts = new HashMap<>();
        for (String name : participant) counts.merge(name, 1, Integer::sum);
        for (String name : completion) counts.put(name, counts.get(name) - 1);
        for (Map.Entry<String, Integer> entry : counts.entrySet()) {
            if (entry.getValue() == 1) return entry.getKey();
        }
        throw new IllegalArgumentException("Expected exactly one missing runner");
    }
}
```

`merge(name, 1, Integer::sum)` 将新姓名的计数设为 1，并递增已有姓名的计数。每位完赛者使相应计数减一。参赛者为 `[ana, bob, ana]`，完赛者为 `[bob, ana]` 时，ana 剩余 `2 - 1 = 1`。

Set 差集会丢失有两人名叫 ana 这一信息。计数保留重复次数，从而表示一个人未完赛。改变完赛数组的顺序不会影响结果。

## 不依赖 HashMap 的顺序

[`HashMap`](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/HashMap.html)不保证迭代顺序。能够返回第一个正计数项，是因为有效输入只会留下一个这样的项，而非因为迭代有特定顺序。代码返回剩余计数为 1 的姓名。

最后的异常并不构成完整的输入验证。通用对账 API 还需要针对未知完赛者或多名未完赛者制定额外策略并实施检查。

姓名长度最多为 20，且假设哈希操作平均为常数时间，则时间复杂度为 O(n)，u 个不同姓名的额外空间为 O(u)。没有基准测试证明流或循环在所有情况下更快。

如果只关心不同的种类，Set 就足够了；可对照 [Ponketmon 题目的选择上限](/en/posts/2021-07-29-ponkemon/)。
