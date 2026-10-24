---
title: "[코딩테스트] 프로그래머스 - 완주하지 못한 선수(JAVA)"
language: "ko"
translationKey: "2021-07-23-unsuccessful-runner"
routeSlug: "2021-07-23-unsuccessful-runner"
kind: "post"
publishedAt: "2021-07-22T16:40:30.000Z"
categories:
  - "coding-test"
tags:
  - "코딩테스트"
  - "프로그래머스"
legacyUrl: "/coding-test/unsuccessful-runner/"
legacySource: "_posts/coding-test/2021-07-23-unsuccessful-runner.markdown"
updatedAt: "2026-10-24T09:00:00+09:00"
reviewedAt: "2026-10-24"
reviewStatus: "revised"
reviewScope: "문제 조건 대조 및 Java 예제 실행 검증"
archiveBodySha256: "590ef17b5a6615238c635162403e70993ca5a6d97d62fd6d8ffb109384b85d45"
reviewSources:
  - "https://school.programmers.co.kr/learn/courses/30/lessons/42576"
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

## 검증 및 보강 — 2026-10-24

동명이인을 구분하려면 이름의 존재 여부가 아니라 빈도를 저장해야 합니다. `[leo,kiki,eden]`에서 `[eden,kiki]`가 완주하면 `leo`, `[mislav,stanko,mislav,ana]`에서 `[stanko,ana,mislav]`가 완주하면 `mislav`입니다. 해시 충돌의 평균적 조건에서 시간 O(n), 추가 공간 O(u)이며 u는 서로 다른 이름 수입니다. 문제는 미완주자가 정확히 한 명이라고 보장합니다. `Entry::getKey`를 쓰려면 `java.util.Map.Entry`도 import해야 합니다.

메서드 예제는 `Solution` 클래스 내부에 넣는 형태이며, 사용한 클래스는 `java.util.Arrays`, `java.util.Map`, `java.util.Map.Entry`, `java.util.function.Function`, `java.util.stream.Collectors`입니다. 필요한 import를 클래스 선언 위에 추가하세요.

### 확인한 자료

- [공식 자료 1](https://school.programmers.co.kr/learn/courses/30/lessons/42576)
