---
language: en
translationKey: 2021-07-22-dot-product
routeSlug: 2021-07-22-dot-product
kind: post
categories:
  - coding-test
tags:
  - java
  - algorithms
publishedAt: 2026-10-27T03:54:18.369Z
title: "Java Array Dot Product: IntStream and Integer Bounds"
description: Multiply matching array elements and sum them with IntStream.
  Understand signs, int bounds, and why wider multiplication must promote
  operands before overflow.
updatedAt: 2026-10-27T03:54:18.369Z
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Problem conditions and Java APIs checked; paired solutions compiled
  for Java11 and executed on JDK17.
reviewSources:
  - https://school.programmers.co.kr/learn/courses/30/lessons/70128
  - https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/stream/IntStream.html
---
The dot product of two arrays is the sum of products at matching indices. Adding the elements first, or multiplying the two array sums, computes something different.

The [exercise](https://school.programmers.co.kr/learn/courses/30/lessons/70128) supplies equal-length integer arrays of length 1–1,000 with elements from -1,000 to 1,000. Within those bounds, an `int` result is sufficient.

## Sum the products by index

Save this complete class as `Solution.java`. It was compiled for Java 11 and assumes the equal-length input contract.

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

[`IntStream.range(0, a.length)`](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/stream/IntStream.html) excludes the end index. Map each index to `a[i] * b[i]`, then combine the products with `sum()`. The primitive index stream does not require building a boxed Integer list.

For `[1, 2, 3, 4]` and `[-3, -1, 0, 2]`, the products are `-3, -2, 0, 8`, giving 3. Preserve negative signs: taking absolute values changes the dot product.

## When int is sufficient

Each product has absolute value at most 1,000,000, and there are at most 1,000 terms. The absolute sum is therefore bounded by 1,000,000,000, within Java's int range. Boundary checks also cover the largest positive and negative sums across 1,000 terms.

For larger inputs, changing only the accumulator to long may be insufficient. `(long) (a[i] * b[i])` converts after int multiplication has already overflowed. Promote **before** multiplication with `(long) a[i] * b[i]`, and design the sum and return type as long too. The submitted method here retains the exercise's int contract.

Time is O(n) and additional storage is O(1). This is not a general vector library with validation for unequal lengths, null arrays, or out-of-range elements.

For converting fixed English digit names into an integer, see [digit words and numeric strings](/en/posts/2021-07-23-number-word/).
