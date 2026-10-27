---
title: "Java 음양 더하기: 인덱스별 부호를 적용해 합산하기"
language: ko
translationKey: 2021-07-22-plus-minus
routeSlug: 2021-07-22-plus-minus
kind: post
publishedAt: 2021-07-22T03:40:30.000Z
categories:
  - coding-test
tags:
  - 코딩테스트
  - 프로그래머스
legacyUrl: /coding-test/plus-minus/
legacySource: _posts/coding-test/2021-07-22-plus-minus.markdown
updatedAt: 2026-10-27T04:25:30.219Z
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Primary problem conditions and Java API checked; paired complete
  code compiled for Java11 and run on JDK17.
archiveBodySha256: 3d9fd33deca9cb8827c9696a87a5df201fa03357485d41c5438963847d7cb334
reviewSources:
  - https://school.programmers.co.kr/learn/courses/30/lessons/76501
  - https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/stream/IntStream.html
description: IntStream으로 절댓값 배열과 부호 배열을 연결해 합산합니다. 상쇄되는 값, 모두 음수인 입력, int 범위와 배열
  길이 전제를 설명합니다.
---
절댓값과 부호가 따로 주어지면, 같은 인덱스의 부호를 먼저 적용한 뒤 합산합니다. `signs[i]`가 true면 양수, false면 음수이므로 조건식 하나로 실제 값을 복원할 수 있습니다.

[음양 더하기 문제](https://school.programmers.co.kr/learn/courses/30/lessons/76501)는 두 배열의 길이가 같고 길이 1~1,000, 절댓값 1~1,000임을 보장합니다. 부호 배열을 따로 정렬하면 원래 수와의 대응이 깨지므로 입력 순서대로 처리합니다.

## 같은 인덱스를 함께 읽기

다음 전체 클래스를 `Solution.java`에 저장할 수 있습니다. Java 11 타깃으로 컴파일하고 JDK 17에서 실행했습니다.

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

[`IntStream.range`](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/stream/IntStream.html)는 시작 인덱스 0을 포함하고 끝 인덱스 `absolutes.length`는 제외합니다. `map`은 각 절댓값에 부호를 적용하고 `sum`은 그 결과를 더합니다. 배열 원소를 수정하거나 별도의 부호 적용 배열을 만들지 않습니다.

| 절댓값 | 부호 | 실제 값 |
| --- | --- | --- |
| 4 | true | 4 |
| 7 | false | -7 |
| 12 | true | 12 |

위 입력의 합은 9입니다. `[1,2,3]`과 `[false,false,true]`처럼 결과가 0으로 상쇄될 수도 있습니다. true의 개수에서 false의 개수를 빼는 것이 아니라, 각 원소의 **크기까지** 반영해야 합니다.

## int 범위와 적용 조건

최대 1,000개 항 각각의 절댓값이 1,000이므로 합의 절댓값 상한은 1,000,000입니다. 모든 부호가 양수 또는 음수인 경계에서도 int 범위 안입니다. 시간은 O(n), 추가 공간은 O(1)입니다.

이 코드는 문제에서 보장한 같은 길이와 올바른 절댓값을 전제로 하며, 임의 서비스 입력의 길이·null·값 범위 검증을 대신하지 않습니다. 입력 범위가 커지면 항과 누적값의 타입을 함께 다시 판단해야 합니다.

두 배열에서 항을 만드는 다른 예제는 [배열 내적](/ko/posts/2021-07-22-dot-product/), int를 넘는 결과를 만드는 예제는 [x 간격 수열과 long](/ko/posts/2021-07-29-interval-num/)에서 다룹니다. 전체 학습 순서는 [Java 코딩 문제 풀이](/ko/categories/coding-test/)에서 볼 수 있습니다.
