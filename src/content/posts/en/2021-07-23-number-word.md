---
language: en
translationKey: 2021-07-23-number-word
routeSlug: 2021-07-23-number-word
kind: post
categories:
  - coding-test
tags:
  - java
  - algorithms
publishedAt: "2026-10-27T04:06:49+00:00"
title: Convert English Digit Words in Java with String.replace
description: Normalize valid mixtures of digits and zero-to-nine words using
  literal replacement. Distinguish replace from replaceAll and explain integer
  bounds and scope.
updatedAt: "2026-10-27T04:06:49+00:00"
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Problem conditions and Java APIs checked; paired solutions compiled
  for Java11 and executed on JDK17.
reviewSources:
  - https://school.programmers.co.kr/learn/courses/30/lessons/81301
  - https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/lang/String.html
---
For valid input mixing digits with digit words, replace the fixed words `zero` through `nine` with digits, then parse the resulting integer. The search terms are literals, so `String.replace` is sufficient without `replaceAll`.

The [exercise](https://school.programmers.co.kr/learn/courses/30/lessons/81301) guarantees valid lowercase digit words and digits, a result from 1 to 2,000,000,000, and no leading zero. This is not a parser for general English number expressions.

## Replace the ten fixed words

Save the full class as `Solution.java`. No additional imports are needed; it was compiled and executed with a Java 11 target.

```java
public class Solution {
    public int solution(String s) {
        String[] words = {"zero", "one", "two", "three", "four",
                "five", "six", "seven", "eight", "nine"};
        for (int digit = 0; digit < words.length; digit++) {
            s = s.replace(words[digit], Integer.toString(digit));
        }
        return Integer.parseInt(s);
    }
}
```

[`String.replace(CharSequence, CharSequence)`](https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/lang/String.html) performs literal replacement. `replaceAll` interprets its first argument as a regular expression. None of the ten words requires regex syntax here.

For example, `one4seveneight` becomes `1478`, and `23four5six7` becomes `234567`. Input already containing only digits, such as `123`, still yields 123. `two` followed by nine `zero` words yields 2,000,000,000, within int range.

Replacement digits cannot introduce another digit word, and none of these ten words contains another word in the set, so this order works. Invalid words, spaces, uppercase input, and out-of-range numbers are outside the exercise's guarantees. A parse failure on arbitrary input is not repaired into a valid integer by this method.

With ten fixed words, time is O(n) in input length. Strings are immutable, so intermediate replacement strings may be allocated; additional space is O(n). No benchmark establishes this method as faster than other parsers for these small inputs.

Compare [new ID normalization](/en/posts/2021-07-19-new-id/) for a transformation where regular expressions are useful.
