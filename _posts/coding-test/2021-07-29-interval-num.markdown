---
layout: posts
title:  "[코딩테스트] 프로그래머스 - x만큼 간격이 있는 n개의 숫자(JAVA)"
date:   2021-07-29 01:00:00 +0900
categories: 
    - coding-test 
tags: 
    - 코딩테스트
    - 프로그래머스
---
문제 설명

함수 solution은 정수 x와 자연수 n을 입력 받아, x부터 시작해 x씩 증가하는 숫자를 n개 지니는 리스트를 리턴해야 합니다. 
다음 제한 조건을 보고, 조건을 만족하는 함수, solution을 완성해주세요.

---

제한사항
- x는 -10000000 이상, 10000000 이하인 정수입니다.
- n은 1000 이하인 자연수입니다.

---

풀이 
- IntStream.range()를 이용하여 풀었습니다.
- mapToLong을 이용하면 int -> long으로 간편하게 return 할 수 있습니다.
- x를 int로 변환하면 테스트 케이스에서 걸리는 부분이 발생합니다.
  - long casting으로 해결 가능!!


```java
public long[] solution(int x, int n) {
    return IntStream.range(0, n)
        .mapToLong(i -> (long) x * (i + 1))
        .toArray();
}
```