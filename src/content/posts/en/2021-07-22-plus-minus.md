---
language: en
translationKey: 2021-07-22-plus-minus
routeSlug: 2021-07-22-plus-minus
kind: post
categories:
  - coding-test
tags:
  - java
  - algorithms
publishedAt: 2026-10-27T04:25:30.219Z
title: Sum Signed Values in Java with IntStream
description: Combine absolute values and matching boolean signs with IntStream.
  Check cancellation, all-negative input, int bounds, and the equal-length array
  contract.
updatedAt: 2026-10-27T04:25:30.219Z
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Primary problem conditions and Java API checked; paired complete
  code compiled for Java11 and run on JDK17.
reviewSources:
  - https://school.programmers.co.kr/learn/courses/30/lessons/76501
  - https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/stream/IntStream.html
---
When magnitudes and signs arrive separately, apply the sign at each matching index before summing. `signs[i]` means positive when true and negative when false, so one conditional expression reconstructs each value.

The [exercise](https://school.programmers.co.kr/learn/courses/30/lessons/76501) guarantees equal array lengths from 1 to 1,000 and magnitudes from 1 to 1,000. Sorting the signs separately would break their association with the original values; process the arrays in their given order.

## Read matching indices together

Save this complete class as `Solution.java`. It was compiled for Java 11 and executed on JDK 17.

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

[`IntStream.range`](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/stream/IntStream.html) includes index 0 and excludes `absolutes.length`. `map` applies the sign to each magnitude, and `sum` adds the resulting values. The method neither modifies the input nor creates a separate array of signed values.

| Magnitude | Sign | Actual value |
| --- | --- | --- |
| 4 | true | 4 |
| 7 | false | -7 |
| 12 | true | 12 |

These values sum to 9. Input `[1,2,3]` with `[false,false,true]` cancels to 0. Counting positive versus negative flags alone is insufficient: each term's **magnitude** matters too.

## Integer bounds and contract

There are at most 1,000 terms with magnitude at most 1,000, so the absolute sum is bounded by 1,000,000. Even the all-positive and all-negative boundaries fit int. Time is O(n), with O(1) additional space.

The method assumes the exercise's valid magnitudes and equal lengths. It does not replace null, length, and value validation for arbitrary application input. Larger bounds require reconsidering both term and accumulator types.

Compare [array dot products](/en/posts/2021-07-22-dot-product/) for another two-array calculation and [an x-spaced sequence using long](/en/posts/2021-07-29-interval-num/) for results beyond int. Browse the [Java coding exercise guide](/en/categories/coding-test/) for a learning path.
