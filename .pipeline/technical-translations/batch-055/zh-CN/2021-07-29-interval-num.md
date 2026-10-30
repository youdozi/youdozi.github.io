---
language: "zh-CN"
translationKey: "2021-07-29-interval-num"
title: "Java 等差数列：乘法前先提升类型"
description: "使用 IntStream 生成从 x 到 x*n 的 n 个值，说明为什么仅用 mapToLong 不能避免 int 溢出，并检查正、负和零步长。"
state: "draft"
sourcePath: "src/content/posts/en/2021-07-29-interval-num.md"
sourceSha256: "4674cdefcccdc5107e92b9fe49ee186426b25a096d2687d60d42724c51d29cf4"
---
从 x 开始的 n 个值是 `x × 1` 到 `x × n`。结果可能超出 int 范围，因此结果数组和**乘法运算本身**都必须使用 long。

[题目](https://school.programmers.co.kr/learn/courses/30/lessons/12954)规定 x 的范围为 -10,000,000 到 10,000,000，n 为 1 到 1,000。因此，最后一项的绝对值可能达到 10,000,000,000，需要使用 long 数组。

## 处理流程

![把从零开始的下标转换为项号，在乘法前将 x 提升为 long，再按顺序收集。](2021-07-29-interval-num.svg)

把从零开始的下标转换为项号，在乘法前将 x 提升为 long，再按顺序收集。

## 把下标转换为项号

将完整类保存为 `Solution.java`。原文中的代码已按 Java 11 目标编译，并在 JDK 17 上执行。

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

[`IntStream.range(0, n)`](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/stream/IntStream.html)生成 0 到 n-1 的下标。乘以 `i + 1` 后，第一项是 x，最后一项是 x×n。从 x×0 开始会改变题目要求的数列。

| x | n | 结果 |
| --- | --- | --- |
| 2 | 5 | `[2,4,6,8,10]` |
| -4 | 2 | `[-4,-8]` |
| 0 | 3 | `[0,0,0]` |

负的 x 生成递减的值，x=0 则只生成零。必须保留项的顺序；这不是排序问题。

## 仅使用 mapToLong 不能保护乘法结果

即使在 `mapToLong` 内，先计算 `x * (i + 1)` 仍会执行 int 乘法，因为两个操作数都是 int。`(long) (x * (i + 1))` 也在溢出发生后才转换类型。

示例通过 `(long) x * (i + 1)` 先提升一个操作数的类型。原文的检查比较了正、负边界下分别以 10,000,000,000 和 -10,000,000,000 结尾的完整参考数组。较小的正、负和零输入也与通过重复加法构造的数组进行了比较。

时间复杂度为 O(n)，包含返回数组的空间复杂度为 O(n)。实现遵循题目约束，没有对数列长度或任意 API 输入进行通用验证。

对于在给定范围内可用 int 完成的计算，可对照[带符号求和](/en/posts/2021-07-22-plus-minus/)和[数组内积](/en/posts/2021-07-22-dot-product/)。[Java 编程练习指南](/en/categories/coding-test/)将数组运算与字符串、集合练习连接起来。
