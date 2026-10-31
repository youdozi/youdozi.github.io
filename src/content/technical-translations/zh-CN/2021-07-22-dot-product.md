---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2021-07-22-dot-product",
  "routeSlug": "2021-07-22-dot-product",
  "kind": "post",
  "title": "Java 数组点积：IntStream 与整数范围",
  "description": "使用 IntStream 将两个数组对应元素相乘后求和，理解符号、int 范围，以及为何必须在乘法溢出前提升操作数类型。",
  "categories": [
    "coding-test"
  ],
  "tags": [
    "java",
    "algorithms"
  ],
  "sourcePath": "src/content/posts/en/2021-07-22-dot-product.md",
  "sourceSha256": "aa027f07c568f5c9d25dc08d3ee21ea8c23917f73f1409b25b221ad21be86463",
  "draftSha256": "eceb5c70f7671f49f937a110790152460598f8c4cccd8adf05aab662ae0630a2",
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
两个数组的点积，是相同下标处元素乘积的总和。先把元素相加，或把两个数组各自的总和相乘，得到的是不同的结果。

这道[练习题](https://school.programmers.co.kr/learn/courses/30/lessons/70128)提供两个长度相同的整数数组，长度为 1–1000，元素取值为 -1000 到 1000。在这些限制下，结果使用 `int` 即可。

## 处理流程

![将每个共同下标映射为对应元素的乘积，再将这些乘积求和。题目的取值范围不会超出 int。](/assets/diagrams/technical/zh-CN-2021-07-22-dot-product.svg)

将每个共同下标映射为对应元素的乘积，再将这些乘积求和。题目的取值范围不会超出 int。

## 按下标计算乘积并求和

将以下完整类保存为 `Solution.java`。它已按 Java 11 编译，并以输入数组长度相同为前提。

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

[`IntStream.range(0, a.length)`](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/stream/IntStream.html)不包含结束下标。将每个下标映射为 `a[i] * b[i]`，再通过 `sum()` 合并乘积。这个基本类型下标流不需要先构建装箱后的 Integer 列表。

对于 `[1, 2, 3, 4]` 和 `[-3, -1, 0, 2]`，各项乘积为 `-3, -2, 0, 8`，结果是 3。必须保留负号：取绝对值会改变点积。

## 何时使用 int 就足够

每个乘积的绝对值最多为 1000000，最多有 1000 项。因此，总和的绝对值不超过 1000000000，处于 Java 的 int 范围内。边界检查也覆盖了 1000 项全部达到最大正值或最大负值的情况。

对于更大的输入，只把累加器改为 long 可能仍然不够。`(long) (a[i] * b[i])` 是在 int 乘法已经溢出后才转换类型。应当在乘法**之前**使用 `(long) a[i] * b[i]` 提升类型，同时将求和与返回类型设计为 long。这里提交的方法仍遵守题目要求的 int 约定。

时间复杂度为 O(n)，额外空间复杂度为 O(1)。这不是一个会校验数组长度不等、数组为 null 或元素超出范围等情况的通用向量库。

要把固定的英文数字单词转换为整数，请参阅[数字单词与数字字符串](/en/posts/2021-07-23-number-word/)。
