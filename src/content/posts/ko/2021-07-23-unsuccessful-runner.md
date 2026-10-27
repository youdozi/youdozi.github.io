---
title: "Java 미완주 선수 찾기: Set 대신 이름별 빈도 세기"
language: ko
translationKey: 2021-07-23-unsuccessful-runner
routeSlug: 2021-07-23-unsuccessful-runner
kind: post
publishedAt: 2021-07-22T16:40:30.000Z
categories:
  - coding-test
tags:
  - 코딩테스트
  - 프로그래머스
legacyUrl: /coding-test/unsuccessful-runner/
legacySource: _posts/coding-test/2021-07-23-unsuccessful-runner.markdown
updatedAt: 2026-10-27T04:56:35.582+00:00
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Problem conditions and Java APIs checked; complete paired solutions
  compiled for Java11 and run on JDK17.
archiveBodySha256: 590ef17b5a6615238c635162403e70993ca5a6d97d62fd6d8ffb109384b85d45
reviewSources:
  - https://school.programmers.co.kr/learn/courses/30/lessons/42576
  - https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/HashMap.html
description: 동명이인이 있는 참가자·완주자 목록의 차이를 HashMap 빈도로 계산합니다. 정확히 한 명이 빠진다는 전제와 순서
  독립성, 복잡도를 설명합니다.
---
미완주 선수를 찾을 때는 이름이 있는지만 확인하지 말고 이름별 인원수를 세어야 합니다. 참가자 빈도에서 완주자 빈도를 빼면, 문제 조건상 정확히 한 이름의 값만 1로 남습니다.

[문제 조건](https://school.programmers.co.kr/learn/courses/30/lessons/42576)은 참가자가 최대 100,000명이고 완주자는 한 명 적으며, 동명이인이 있을 수 있다는 것입니다. 이름은 길이 1~20의 소문자 영문입니다. 완료 목록은 참가자 목록에서 한 사람을 제외한 올바른 입력을 전제로 합니다.

## 처리 흐름

![참가자의 이름별 인원수를 세고 완주자를 한 명씩 뺀 뒤, 남은 인원수가 1인 이름을 반환합니다.](/assets/diagrams/2021-07-23-unsuccessful-runner-ko.svg)

참가자의 이름별 인원수를 세고 완주자를 한 명씩 뺀 뒤, 남은 인원수가 1인 이름을 반환합니다.

## 이름별 차이를 저장

다음 전체 클래스를 `Solution.java`에 저장합니다. Java 11 타깃으로 컴파일하고 JDK 17에서 실행했습니다.

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

`merge(name, 1, Integer::sum)`은 처음 본 이름을 1로 넣고 같은 이름이면 증가시킵니다. 완주자 한 명마다 같은 이름의 값을 하나 줄입니다. 예를 들어 참가자 `[ana, bob, ana]`, 완주자 `[bob, ana]`이면 ana의 값은 `2 - 1 = 1`로 남습니다.

Set으로 두 목록의 차집합을 구하면 ana가 두 명이었다는 정보를 잃습니다. 빈도는 사람의 수를 표현하므로 이름이 중복돼도 한 명만 빠진 상황을 보존합니다. 완주 배열의 순서도 결과에 영향을 주지 않습니다.

## HashMap 순서에 기대지 않기

[`HashMap`](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/HashMap.html)은 순회 순서를 보장하지 않습니다. 이 풀이가 처음 찾은 양수 항목을 반환할 수 있는 이유는 순서가 정해져 있어서가 아니라, 유효 입력에서 그런 항목이 정확히 하나이기 때문입니다. 코드에서는 남는 빈도가 1인 이름을 반환합니다.

마지막 예외 처리가 잘못된 입력을 모두 검증하는 것은 아닙니다. 참가하지 않은 완주자가 있거나 여러 명이 빠진 데이터를 처리하는 범용 정산 API로 사용하려면 입력 정책과 검증을 별도로 설계해야 합니다.

이름 길이가 최대 20으로 제한되고 해시 연산의 평균 비용을 상수로 볼 때 시간은 O(n), 추가 공간은 서로 다른 이름 수 u에 대해 O(u)입니다. 별도 성능 비교 없이 stream 또는 반복문이 항상 더 빠르다고 결론 내리지는 않습니다.

서로 다른 종류의 수만 필요할 때는 빈도 맵이 아니라 Set으로 충분합니다. [폰켓몬의 선택 상한](/ko/posts/2021-07-29-ponkemon/)에서 두 상황을 비교할 수 있습니다.
