---
language: en
translationKey: 2021-07-29-interval-num
routeSlug: 2021-07-29-interval-num
kind: post
categories:
  - coding-test
tags:
  - java
  - algorithms
publishedAt: 2026-10-27T04:25:30.219Z
title: "Generate an x-Spaced Sequence in Java: Promote Before Multiplication"
description: Build n values from x through x*n with IntStream. Explain why
  mapToLong alone does not prevent int overflow, and check positive, negative,
  and zero steps.
updatedAt: 2026-10-27T04:25:30.219Z
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Primary problem conditions and Java API checked; paired complete
  code compiled for Java11 and run on JDK17.
reviewSources:
  - https://school.programmers.co.kr/learn/courses/30/lessons/12954
  - https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/stream/IntStream.html
---
The n values starting at x are `x × 1` through `x × n`. Because results can exceed int range, both the result array and **the multiplication itself** must use long.

The [exercise](https://school.programmers.co.kr/learn/courses/30/lessons/12954) bounds x from -10,000,000 to 10,000,000 and n from 1 to 1,000. The final value can therefore have magnitude 10,000,000,000, requiring a long array.

## Convert an index to a term number

Save this complete class as `Solution.java`. It was compiled for Java 11 and executed on JDK 17.

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

[`IntStream.range(0, n)`](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/stream/IntStream.html) generates indices from 0 through n-1. Multiplying by `i + 1` makes the first value x and the last x×n. Starting at x×0 would change the required sequence.

| x | n | Result |
| --- | --- | --- |
| 2 | 5 | `[2,4,6,8,10]` |
| -4 | 2 | `[-4,-8]` |
| 0 | 3 | `[0,0,0]` |

A negative x produces decreasing values, while x=0 produces only zeros. Preserve term order; this is not a sorting problem.

## mapToLong alone does not protect the product

Even inside `mapToLong`, evaluating `x * (i + 1)` first uses int multiplication because both operands are ints. `(long) (x * (i + 1))` also converts after overflow has occurred.

The example promotes an operand first with `(long) x * (i + 1)`. Checks cover the full reference arrays ending at 10,000,000,000 and -10,000,000,000 for the positive and negative bounds. Smaller positive, negative, and zero inputs are also compared against arrays constructed by repeated addition.

Time is O(n), and space including the returned array is O(n). This follows the exercise contract rather than implementing general validation of sequence size or arbitrary API input.

Compare [signed sums](/en/posts/2021-07-22-plus-minus/) and [array dot products](/en/posts/2021-07-22-dot-product/) for calculations that fit int under their bounds. The [Java coding exercise guide](/en/categories/coding-test/) connects array calculations with strings and collections.
