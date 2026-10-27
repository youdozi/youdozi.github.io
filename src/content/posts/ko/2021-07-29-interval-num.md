---
title: "Java x 간격 수열 만들기: 곱셈 전에 long으로 변환하기"
language: ko
translationKey: 2021-07-29-interval-num
routeSlug: 2021-07-29-interval-num
kind: post
publishedAt: 2021-07-28T16:00:00.000Z
categories:
  - coding-test
tags:
  - 코딩테스트
  - 프로그래머스
legacyUrl: /coding-test/interval-num/
legacySource: _posts/coding-test/2021-07-29-interval-num.markdown
updatedAt: 2026-10-27T04:25:30.219Z
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Primary problem conditions and Java API checked; paired complete
  code compiled for Java11 and run on JDK17.
archiveBodySha256: f30452c3ef0503e7fd7521e201075a40adf222841fb80c60b0e81c444ee3c27c
reviewSources:
  - https://school.programmers.co.kr/learn/courses/30/lessons/12954
  - https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/stream/IntStream.html
description: x부터 시작해 x 간격의 n개 값을 만드는 Java 풀이입니다. mapToLong 안에서 int 곱셈이 넘치는 이유와
  양수·음수·0의 경계값을 설명합니다.
---
x부터 시작하는 n개 값은 `x × 1`부터 `x × n`까지입니다. 결과가 int 범위를 넘을 수 있으므로 배열의 타입뿐 아니라 **곱셈이 수행되는 타입**도 long이어야 합니다.

[문제 조건](https://school.programmers.co.kr/learn/courses/30/lessons/12954)은 x가 -10,000,000~10,000,000이고 n은 1~1,000입니다. 따라서 마지막 값의 절댓값은 최대 10,000,000,000이어서 long 배열로 반환합니다.

## 인덱스를 항 번호로 바꾸기

전체 코드를 `Solution.java`에 저장합니다. Java 11 타깃으로 컴파일하고 JDK 17에서 실행했습니다.

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

[`IntStream.range(0, n)`](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/stream/IntStream.html)의 인덱스는 0~n-1입니다. `i + 1`을 곱하므로 첫 값은 x이고 마지막은 x×n입니다. x×0부터 만들면 문제의 시작값이 달라집니다.

| x | n | 결과 |
| --- | --- | --- |
| 2 | 5 | `[2,4,6,8,10]` |
| -4 | 2 | `[-4,-8]` |
| 0 | 3 | `[0,0,0]` |

음수 x는 값이 감소하는 수열을 만들고, x가 0이면 모든 항이 0입니다. 반환 순서는 항 번호 순서이며 값을 정렬하는 문제가 아닙니다.

## mapToLong만으로 곱셈이 안전해지는 것은 아님

`mapToLong`의 결과가 long이라고 해도, 그 안에서 `x * (i + 1)`을 먼저 계산하면 두 피연산자가 int이므로 int 곱셈이 수행됩니다. `(long) (x * (i + 1))`도 넘친 결과를 나중에 변환합니다.

예제는 `(long) x * (i + 1)`로 피연산자를 먼저 승격합니다. x=10,000,000·n=1,000의 마지막 값 10,000,000,000과 음수 경계 -10,000,000,000을 전체 결과 배열의 기준값과 함께 확인했습니다. 반복 덧셈으로 만든 기준 배열과 작은 양수·음수·0 입력도 비교했습니다.

시간 O(n), 반환 배열을 포함한 공간 O(n)입니다. n의 범위 등 임의 입력 정책을 검증하는 범용 수열 API는 아니며 문제의 입력 조건을 사용합니다.

범위 안에서 int로 합산하는 사례는 [음양 더하기](/ko/posts/2021-07-22-plus-minus/)와 [배열 내적](/ko/posts/2021-07-22-dot-product/)을 참고하세요. [Java 코딩 문제 풀이 안내](/ko/categories/coding-test/)에서 배열 계산부터 자료구조까지 이어 읽을 수 있습니다.
