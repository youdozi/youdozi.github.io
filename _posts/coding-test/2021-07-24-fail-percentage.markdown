---
layout: posts
title:  "[코딩테스트] 프로그래머스 - 실패율(JAVA)"
date:   2021-07-24 00:00:00 +0900
categories: 
    - coding-test 
tags: 
    - 코딩테스트
    - 프로그래머스
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
- 실패율 계산하는 코드는 메소드를 따로 뺴내서 호출하도록 하였습니다.


```java
public int[] solution(int N, int[] stages) {

    /**
     * IntStream을 이용하여 loop 시작
     * boxed() 메소드는 int -> Integer로 랩핑한다. mapToObj()와 같은 기능을 합니다.
     * Collectors.toMap(i -> i, i -> calcPercentage(i, stages))
     * calcPercentage를 따로 메소드로 분리하였습니다.
     */
    Map<Integer, Double> resultMap = IntStream.rangeClosed(1, N)
        .boxed()
        .collect(Collectors
        .toMap(i -> i, i -> calcPercentage(i, stages)));

    /**
     * Map.entrySet().stream() 호출
     * Map.Entry를 이용하여 sort. value 기준으로 내림차순으로..
     */
    return resultMap.entrySet().stream()
        .sorted(Map.Entry.<Integer, Double>comparingByValue().reversed())
        .map(Entry::getKey)
        .mapToInt(i -> i)
        .toArray();
}

/**
 * index i, stages를 인자값으로 받아 total, current 값을 Stream으로 계산합니다.
 * 퍼센테이지를 구하는 코드니 double 로 형변환 합니다.
 * current 가 0일 경우 그대로 return 해야 테스트 케이스에 걸리지 않습니다.
 */
private Double calcPercentage(Integer i, int[] stages){
    long total = Arrays.stream(stages).filter(stage->stage>=i).count();
    long current = Arrays.stream(stages).filter(stage->stage==i).count();

    return current > 0 ? (double)current / (double)total : (double)current;
}
```