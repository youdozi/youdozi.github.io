---
language: en
translationKey: 2021-07-20-pair-delete
routeSlug: 2021-07-20-pair-delete
kind: post
categories:
  - coding-test
tags:
  - java
  - algorithms
publishedAt: "2026-10-27T04:21:24+00:00"
title: Remove Adjacent Duplicate Pairs in Java with an ArrayDeque Stack
description: Reduce adjacent equal-character pairs with a stack. Explain the
  prefix invariant, cascading removal, million-character boundaries, and time
  and space costs.
updatedAt: 2026-10-27T04:56:35.582+00:00
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Problem conditions and Java APIs checked; complete paired solutions
  compiled for Java11 and run on JDK17.
reviewSources:
  - https://school.programmers.co.kr/learn/courses/30/lessons/12973
  - https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/ArrayDeque.html
---
A stack solves adjacent equal-character pair removal in one traversal by retaining the reduced result of the prefix already read. If the next character matches the top, remove the pair; otherwise push it.

The [exercise](https://school.programmers.co.kr/learn/courses/30/lessons/12973) accepts 1–1,000,000 lowercase English letters and returns 1 if everything can be removed, or 0 otherwise. Even total counts for each character are insufficient because removal depends on adjacency.

## Processing flow

![The stack stores the reduced prefix. Each new character removes the equal top or becomes the new top.](/assets/diagrams/2021-07-20-pair-delete-en.svg)

The stack stores the reduced prefix. Each new character removes the equal top or becomes the new top.

## Retain the reduced prefix

Save the full class as `Solution.java`. It was compiled for Java 11 and executed on JDK 17.

```java
import java.util.ArrayDeque;
import java.util.Deque;

public class Solution {
    public int solution(String s) {
        Deque<Character> stack = new ArrayDeque<>();
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (!stack.isEmpty() && stack.peek() == c) stack.pop();
            else stack.push(c);
        }
        return stack.isEmpty() ? 1 : 0;
    }
}
```

The stack contains the processed prefix with no remaining equal adjacent pair. A matching next character creates a removable pair at the boundary, so pop. A different character creates no such pair, so push. The same invariant then holds for the next step.

| Character read | Stack: bottom → top |
| --- | --- |
| b | b |
| a | ba |
| a | b |
| b | empty |
| a | a |
| a | empty |

Thus `baabaa` returns 1. In contrast, `abab` returns 0 despite both characters having even counts: no equal characters are adjacent. The stack handles boundaries exposed by removal without repeatedly replacing text across the whole string.

## ArrayDeque and complexity

Use [`ArrayDeque`](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/ArrayDeque.html) through Deque's `push`, `peek`, and `pop` operations. Because `c` is a primitive char, `stack.peek() == c` unboxes Character for comparison; it does not compare object identity.

Each character is pushed at most once and popped at most once. With amortized deque operations, time is O(n), and worst-case additional space is O(n) when characters remain. Execution checks include a million repeated characters and a million alternating characters with no removable pairs. These are boundary checks, not a speed benchmark or a memory guarantee for every environment.

What you retain depends on the problem: [the missing runner exercise](/en/posts/2021-07-23-unsuccessful-runner/) needs name frequencies rather than adjacent order.
