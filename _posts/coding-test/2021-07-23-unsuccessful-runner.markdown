---
layout: posts
title:  "[코딩테스트] 프로그래머스 - 완주하지 못한 선수(JAVA)"
date:   2021-07-23 01:40:30 +0900
categories: 
    - coding-test 
tags: 
    - 코딩테스트
    - 프로그래머스
---
문제 설명

수많은 마라톤 선수들이 마라톤에 참여하였습니다. 단 한 명의 선수를 제외하고는 모든 선수가 마라톤을 완주하였습니다.

마라톤에 참여한 선수들의 이름이 담긴 배열 participant와 완주한 선수들의 이름이 담긴 배열 completion이 주어질 때, 완주하지 못한 선수의 이름을 return 하도록 solution 함수를 작성해주세요.

---
제한사항
- 마라톤 경기에 참여한 선수의 수는 1명 이상 100,000명 이하입니다.
- completion의 길이는 participant의 길이보다 1 작습니다.
- 참가자의 이름은 1개 이상 20개 이하의 알파벳 소문자로 이루어져 있습니다.
- 참가자 중에는 동명이인이 있을 수 있습니다.

---
풀이
- 프로그래머스 처음으로 봤던 문제 -> 처음에는 너무 이상하게 풀어서 다시 풀었습니다.
- 참여한 사람과 counting을 key value map으로 구현..
- 완주하지 못한 사람들을 loop로 돌면서 위에서 생성한 map의 counting -1 계산
- map에서 counting > 0 filter를 걸어 return


```java
public String solution(String[] participant, String[] completion) {

    /**
     * 참여한 사람들과 기본적인 count를 걸어 Map으로 생성합니다.
     */
    Map<String, Long> participantMap = Arrays.stream(participant)
      .collect(Collectors.groupingBy(Function.identity(), Collectors.counting()));

    /**
     * 완주한 사람들을 stream.foreach로 돌도록 합니다.
     * participantMap.computeIfPresent을 이용합니다.
     * key가 있으면 key value를 새롭게 맵핑할 수 있습니다.
     * 여기서는 value(counting) -1 계산 로직 추가
     */
    Arrays.stream(completion)
      .forEach(item -> participantMap.computeIfPresent(item, (k, v) -> v - 1));

    /**
     * participantMap stream을 이용하여 count > 0 으로 filtering 합니다.
     */
    return participantMap.entrySet().stream()
        .filter(v -> v.getValue() > 0)
        .map(Entry::getKey)
        .collect(Collectors.joining());
    }
```