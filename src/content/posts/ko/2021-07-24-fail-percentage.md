---
title: "[코딩테스트] 프로그래머스 - 실패율(JAVA)"
language: "ko"
translationKey: "2021-07-24-fail-percentage"
routeSlug: "2021-07-24-fail-percentage"
kind: "post"
publishedAt: "2021-07-23T15:00:00.000Z"
categories:
  - "coding-test"
tags:
  - "코딩테스트"
  - "프로그래머스"
legacyUrl: "/coding-test/fail-percentage/"
legacySource: "_posts/coding-test/2021-07-24-fail-percentage.markdown"
updatedAt: "2026-10-24T09:00:00+09:00"
reviewedAt: "2026-10-24"
reviewStatus: "revised"
reviewScope: "문제 조건 대조 및 Java 예제 실행 검증"
archiveBodySha256: "725a7e1bd40bafced94a4df87e78689a5b7d6458d48ef868b6cf83940d460769"
reviewSources:
  - "https://school.programmers.co.kr/learn/courses/30/lessons/42889"
---
문제 설명

슈퍼 게임 개발자 오렐리는 큰 고민에 빠졌다. 그녀가 만든 프랜즈 오천성이 대성공을 거뒀지만, 요즘 신규 사용자의 수가 급감한 것이다. 원인은 신규 사용자와 기존 사용자 사이에 스테이지 차이가 너무 큰 것이 문제였다.

이 문제를 어떻게 할까 고민 한 그녀는 동적으로 게임 시간을 늘려서 난이도를 조절하기로 했다. 역시 슈퍼 개발자라 대부분의 로직은 쉽게 구현했지만, 실패율을 구하는 부분에서 위기에 빠지고 말았다. 오렐리를 위해 실패율을 구하는 코드를 완성하라.

실패율은 다음과 같이 정의한다.
- 스테이지에 도달했으나 아직 클리어하지 못한 플레이어의 수 / 스테이지에 도달한 플레이어 수

전체 스테이지의 개수 N, 게임을 이용하는 사용자가 현재 멈춰있는 스테이지의 번호가 담긴 배열 stages가 매개변수로 주어질 때, 실패율이 높은 스테이지부터 내림차순으로 스테이지의 번호가 담겨있는 배열을 return 하도록 solution 함수를 완성하라.

---
제한사항
- 스테이지의 개수 N은 1 이상 500 이하의 자연수이다.
- stages의 길이는 1 이상 200,000 이하이다.
- stages에는 1 이상 N + 1 이하의 자연수가 담겨있다.
    - 각 자연수는 사용자가 현재 도전 중인 스테이지의 번호를 나타낸다.
    - 단, N + 1 은 마지막 스테이지(N 번째 스테이지) 까지 클리어 한 사용자를 나타낸다.
- 만약 실패율이 같은 스테이지가 있다면 작은 번호의 스테이지가 먼저 오도록 하면 된다.
- 스테이지에 도달한 유저가 없는 경우 해당 스테이지의 실패율은 0 으로 정의한다.

---
풀이
- 해쉬를 이용하면 좀 더 편하게 풀 수 있습니다.
- Stream을 이용하면 기존보다 훨씬 좋은 가독성을 가질 수 있습니다.
- 스테이지별 빈도와 남아 있는 도달자 수로 실패율을 계산합니다.


```java
public int[] solution(int N, int[] stages) {
    int[] stopped = new int[N + 2];
    for (int stage : stages) stopped[stage]++;
    double[] rates = new double[N + 1];
    int reached = stages.length;
    for (int stage = 1; stage <= N; stage++) {
        rates[stage] = reached == 0 ? 0.0 : (double) stopped[stage] / reached;
        reached -= stopped[stage];
    }
    Integer[] order = IntStream.rangeClosed(1, N).boxed().toArray(Integer[]::new);
    Arrays.sort(order, Comparator.<Integer>comparingDouble(stage -> rates[stage])
        .reversed().thenComparingInt(Integer::intValue));
    return Arrays.stream(order).mapToInt(Integer::intValue).toArray();
}
```

## 검증 및 보강 — 2026-10-24

실패율이 같으면 스테이지 번호 오름차순이라는 두 번째 정렬 기준이 필요합니다. 기존 코드는 `HashMap` 순회 순서에 기대고 있어 이 조건을 보장하지 못했습니다. 또한 스테이지마다 전체 이용자를 다시 조회하는 O(N×M) 계산을 빈도 배열로 변경했습니다. 수정 예제는 시간 O(M + N log N), 추가 공간 O(N)입니다. `N=5, stages=[2,1,2,6,2,4,3,3] → [3,4,2,1,5]`, 모든 사용자가 클리어한 경우 `[1,2,…,N]`을 확인하세요.

메서드 예제는 `Solution` 클래스 내부에 넣는 형태이며, 사용한 클래스는 `java.util.Arrays`, `java.util.Comparator`, `java.util.stream.IntStream`입니다. 필요한 import를 클래스 선언 위에 추가하세요.

### 확인한 자료

- [공식 자료 1](https://school.programmers.co.kr/learn/courses/30/lessons/42889)
