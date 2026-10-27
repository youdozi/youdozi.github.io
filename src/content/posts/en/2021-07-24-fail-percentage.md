---
language: en
translationKey: 2021-07-24-fail-percentage
routeSlug: 2021-07-24-fail-percentage
kind: post
categories:
  - coding-test
tags:
  - java
  - algorithms
publishedAt: "2026-10-27T04:21:24+00:00"
title: "Sort Failure Rates in Java: Denominators, Ties, and Long Products"
description: Count stopped and reached players, sort exact rates with long
  cross-products, and handle unreachable stages, full completion, and
  stage-number tie-breaking.
updatedAt: "2026-10-27T04:21:24+00:00"
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Problem conditions and Java APIs checked; complete paired solutions
  compiled for Java11 and run on JDK17.
reviewSources:
  - https://school.programmers.co.kr/learn/courses/30/lessons/42889
  - https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Comparator.html
---
A stage's failure-rate denominator is the number of players who reached it, not the total player count. Count where players stopped, update the remaining reached population, then sort by descending rate and ascending stage number.

The [exercise](https://school.programmers.co.kr/learn/courses/30/lessons/42889) bounds stages N at 500 and players M at 200,000. Input N+1 represents players who cleared every stage and is not itself a stage to rank. A stage reached by nobody has failure rate 0.

## Count stopped and reached players

Save the full class as `Solution.java`. It was compiled for Java 11 and executed on JDK 17.

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

`remaining` counts players who reached the current stage. Save `reached[stage]` **before** subtracting players stopped there, so the updated value is the next stage's denominator. Players at N+1 remain in the denominator throughout.

For N=5 and `[2,1,2,6,2,4,3,3]`, the rates are:

| Stage | Stopped | Reached | Failure rate |
| --- | --- | --- | --- |
| 1 | 1 | 8 | 1/8 |
| 2 | 3 | 7 | 3/7 |
| 3 | 2 | 4 | 2/4 |
| 4 | 1 | 2 | 1/2 |
| 5 | 0 | 1 | 0/1 |

Stages 3 and 4 tie, so the smaller number comes first. The final order is `[3,4,2,1,5]`.

## Compare ratios within numeric bounds

With positive denominators, compare two ratios by cross-multiplication. To sort descending, `Long.compare` receives b's numerator times a's denominator first. On equal rates, `Integer.compare(a, b)` orders stage numbers. This explicitly defines ordering according to the [Comparator contract](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Comparator.html).

If nobody reached a stage, valid input also gives zero stopped players there. Use denominator 1 for comparison, representing the rate as 0/1. Both counts can reach 200,000, so products are bounded by 40,000,000,000. Keep the arrays and multiplication as long; this exceeds int range. Do not cast a product difference to int as a comparison result.

Counting costs O(M), reached populations cost O(N), and sorting costs O(N log N). Overall time is O(M + N log N), with O(N) additional space and no input mutation. If everyone cleared every stage, all rates are zero and stage-number order wins.

For another example of choosing multiplication types from input bounds, see [int and long in array dot products](/en/posts/2021-07-22-dot-product/).
