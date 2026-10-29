---
title: "Java 실패율 정렬: 분모·동률·long 교차곱 처리하기"
language: ko
translationKey: 2021-07-24-fail-percentage
routeSlug: 2021-07-24-fail-percentage
kind: post
publishedAt: 2021-07-23T15:00:00.000Z
categories:
  - coding-test
tags:
  - 코딩테스트
  - 프로그래머스
legacyUrl: /coding-test/fail-percentage/
legacySource: _posts/coding-test/2021-07-24-fail-percentage.markdown
updatedAt: 2026-10-27T04:56:35.582+00:00
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Problem conditions and Java APIs checked; complete paired solutions
  compiled for Java11 and run on JDK17.
archiveBodySha256: 725a7e1bd40bafced94a4df87e78689a5b7d6458d48ef868b6cf83940d460769
reviewSources:
  - https://school.programmers.co.kr/learn/courses/30/lessons/42889
  - https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Comparator.html
description: 스테이지별 실패 인원과 도달 인원을 계산하고, long 교차곱으로 비율을 정렬합니다. 미도달 스테이지·전체 클리어·동률
  순서를 함께 설명합니다.
---
실패율의 분모는 전체 이용자 수가 아니라 해당 스테이지에 도달한 인원입니다. 스테이지별 정지 인원을 세고 남은 도달 인원을 갱신한 뒤, 실패율 내림차순·번호 오름차순으로 정렬해야 합니다.

[문제](https://school.programmers.co.kr/learn/courses/30/lessons/42889)는 스테이지 N≤500, 이용자 M≤200,000을 보장합니다. 입력 값 N+1은 모든 스테이지를 통과한 이용자이며 정렬 대상 스테이지가 아닙니다. 도달자가 없는 스테이지의 실패율은 0입니다.

## 처리 흐름

![멈춘 인원을 빼기 전에 도달 인원을 저장합니다. long 교차곱으로 비율을 비교하고 동률이면 스테이지 번호로 정렬합니다.](/assets/diagrams/2021-07-24-fail-percentage-ko.svg)

멈춘 인원을 빼기 전에 도달 인원을 저장합니다. long 교차곱으로 비율을 비교하고 동률이면 스테이지 번호로 정렬합니다.

## 빈도와 도달 인원 계산

전체 코드를 `Solution.java`에 저장합니다. Java 11 타깃으로 컴파일하고 JDK 17에서 실행했습니다.

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

`remaining`은 현재 스테이지에 도달한 인원입니다. `reached[stage]`를 저장한 **다음** 해당 스테이지에 멈춘 인원을 빼야 다음 스테이지의 분모가 됩니다. N+1의 이용자는 끝까지 분모에 남습니다.

N=5, 입력 `[2,1,2,6,2,4,3,3]`의 비율은 다음과 같습니다.

| 스테이지 | 멈춘 인원 | 도달 인원 | 실패율 |
| --- | --- | --- | --- |
| 1 | 1 | 8 | 1/8 |
| 2 | 3 | 7 | 3/7 |
| 3 | 2 | 4 | 2/4 |
| 4 | 1 | 2 | 1/2 |
| 5 | 0 | 1 | 0/1 |

3번과 4번의 비율이 같으므로 작은 번호인 3번이 먼저입니다. 최종 순서는 `[3,4,2,1,5]`입니다.

## 비율 비교와 수치 범위

양의 분모에서는 두 비율을 교차곱으로 비교할 수 있습니다. 내림차순 비교이므로 코드의 `Long.compare`는 b의 분자와 a의 분모를 곱한 값을 먼저 받습니다. 비율이 같으면 `Integer.compare(a, b)`로 번호를 비교합니다. [Comparator 계약](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Comparator.html)에 맞는 정렬 기준을 직접 지정하는 것입니다.

도달 인원이 0이면 유효 입력에서 멈춘 인원도 0이므로 계산용 분모를 1로 바꿔 0/1로 비교합니다. 두 인원이 모두 최대 200,000일 수 있어 곱의 상한은 40,000,000,000입니다. 이 값은 int를 넘으므로 배열과 곱셈을 long으로 유지합니다. 곱한 뒤 int로 바꾸어 차를 반환하면 안 됩니다.

빈도 계산은 O(M), 도달 인원 계산은 O(N), 정렬은 O(N log N)입니다. 전체 시간 O(M + N log N), 추가 공간 O(N)이며 입력을 수정하지 않습니다. 모든 이용자가 클리어했다면 모든 실패율이 0이어서 번호 순으로 나옵니다.

입력 범위에 맞춘 곱셈 타입 선택은 [배열 내적의 int·long 범위](/ko/posts/2021-07-22-dot-product/)와도 연결됩니다.
