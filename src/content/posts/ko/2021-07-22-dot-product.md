---
title: "Java 배열 내적: IntStream으로 계산하고 int 범위 확인하기"
language: ko
translationKey: 2021-07-22-dot-product
routeSlug: 2021-07-22-dot-product
kind: post
publishedAt: 2021-07-21T22:40:30.000Z
categories:
  - coding-test
tags:
  - 코딩테스트
  - 프로그래머스
legacyUrl: /coding-test/dot-product/
legacySource: _posts/coding-test/2021-07-22-dot-product.markdown
updatedAt: 2026-10-27T04:56:35.582+00:00
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Problem conditions and Java APIs checked; paired solutions compiled
  for Java11 and executed on JDK17.
archiveBodySha256: 2e45b814b9fc5c057a9888b865185a2cdb5e0cf5ed9311409a381b6b41fc3874
reviewSources:
  - https://school.programmers.co.kr/learn/courses/30/lessons/70128
  - https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/stream/IntStream.html
description: 같은 인덱스의 배열 원소를 곱해 합산하는 Java 풀이입니다. 덧셈과 내적의 차이, 음수 입력, int 범위와 long
  승격 위치를 설명합니다.
---
두 배열의 내적은 같은 인덱스의 원소를 곱한 뒤 모두 더한 값입니다. 배열의 각 원소를 먼저 더하거나 두 배열의 전체 합을 곱하면 다른 계산이 됩니다.

[문제 조건](https://school.programmers.co.kr/learn/courses/30/lessons/70128)은 길이가 같은 정수 배열, 길이 1~1,000, 원소 -1,000~1,000입니다. 이 범위에서는 결과를 `int`로 반환할 수 있습니다.

## 처리 흐름

![같은 인덱스의 두 원소를 곱하고 그 결과를 합산합니다. 문제 범위의 결과는 int에 들어갑니다.](/assets/diagrams/2021-07-22-dot-product-ko.svg)

같은 인덱스의 두 원소를 곱하고 그 결과를 합산합니다. 문제 범위의 결과는 int에 들어갑니다.

## 인덱스별 곱을 합산

다음 전체 코드를 `Solution.java`에 저장합니다. Java 11 타깃으로 컴파일해 동작을 확인했으며 입력 길이가 같다는 문제의 전제를 사용합니다.

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

[`IntStream.range(0, a.length)`](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/stream/IntStream.html)은 끝 인덱스를 포함하지 않습니다. 각 인덱스의 `a[i] * b[i]`를 만든 뒤 `sum()`으로 합칩니다. 정수 인덱스 스트림을 사용하므로 boxed Integer 리스트를 만들 필요가 없습니다.

예를 들어 `[1, 2, 3, 4]`와 `[-3, -1, 0, 2]`에서는 항별 값이 `-3, -2, 0, 8`이 되어 결과가 3입니다. 음수를 절댓값으로 바꾸면 원래 내적이 아니므로 부호를 그대로 보존해야 합니다.

## int로 충분한 조건

항 하나의 절댓값은 최대 1,000,000이고 항은 최대 1,000개입니다. 합의 절댓값 상한 1,000,000,000은 Java int 범위 안입니다. 실제 경계값에서도 1,000개 항의 최대 양수·최대 음수 합을 확인했습니다.

더 큰 입력을 처리한다면 누적 변수만 long으로 바꾸는 것으로는 부족할 수 있습니다. `(long) (a[i] * b[i])`는 int 곱셈에서 넘친 뒤 형을 바꿉니다. `(long) a[i] * b[i]`처럼 곱하기 **전**에 승격하고, 합산과 반환 타입도 long으로 설계해야 합니다. 이 글의 제출 코드는 원래 문제의 int 조건을 따릅니다.

시간은 길이 n에 대해 O(n), 추가 저장 공간은 O(1)입니다. 서로 다른 길이, null, 문제 범위 밖의 원소에 대한 검증을 추가한 범용 벡터 라이브러리는 아닙니다.

고정된 숫자 영단어를 정수로 바꾸는 예제는 [숫자 문자열과 영단어](/ko/posts/2021-07-23-number-word/)에서 확인할 수 있습니다.
