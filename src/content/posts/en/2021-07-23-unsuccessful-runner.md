---
language: en
translationKey: 2021-07-23-unsuccessful-runner
routeSlug: 2021-07-23-unsuccessful-runner
kind: post
categories:
  - coding-test
tags:
  - java
  - algorithms
publishedAt: "2026-10-27T04:21:24+00:00"
title: Find the Missing Runner in Java with Name Frequencies
description: Subtract completion counts from participant counts with HashMap.
  Handle duplicate names without Set subtraction and explain the
  one-missing-runner contract.
updatedAt: "2026-10-27T04:21:24+00:00"
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Problem conditions and Java APIs checked; complete paired solutions
  compiled for Java11 and run on JDK17.
reviewSources:
  - https://school.programmers.co.kr/learn/courses/30/lessons/42576
  - https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/HashMap.html
---
To find the missing runner, count people per name rather than checking only whether a name exists. Subtract completion frequencies from participant frequencies; the exercise guarantees that exactly one name remains with count 1.

The [input contract](https://school.programmers.co.kr/learn/courses/30/lessons/42576) allows up to 100,000 participants, one fewer finisher, and duplicate names. Names contain 1–20 lowercase English letters. The completion list is assumed to be a valid participant list with one person removed.

## Store the count difference

Save this full class as `Solution.java`. It was compiled for Java 11 and executed on JDK 17.

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

`merge(name, 1, Integer::sum)` starts a new name at 1 and increments existing names. Each finisher reduces that name's count by one. For participants `[ana, bob, ana]` and finishers `[bob, ana]`, ana remains at `2 - 1 = 1`.

Set subtraction would lose the fact that two people were named ana. Counts retain multiplicity while representing one missing person. Reordering the completion array does not change the result.

## Do not rely on HashMap order

[`HashMap`](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/HashMap.html) does not guarantee iteration order. Returning the first positive entry works because valid input leaves exactly one such entry, not because iteration has a particular order. The code returns the name with remaining count 1.

The final exception is not complete input validation. A general reconciliation API would need additional policies and checks for unknown finishers or multiple missing people.

With name length bounded by 20 and average constant-time hash operations, time is O(n), with O(u) additional space for u distinct names. No benchmark establishes streams or loops as universally faster.

When only distinct kinds matter, a Set is sufficient; compare [the selection bound in the Ponketmon exercise](/en/posts/2021-07-29-ponkemon/).
