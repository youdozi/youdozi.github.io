---
layout: posts
title:  "[코딩테스트] 프로그래머스 - 내적(JAVA)"
date:   2021-07-22 07:40:30 +0900
categories: 
    - CodingTest 
    - Programmers
tags: 
    - 코딩테스트
    - 프로그래머스
---
문제 설명

길이가 같은 두 1차원 정수 배열 a, b가 매개변수로 주어집니다. a와 b의 내적을 return 하도록 solution 함수를 완성해주세요.
이때, a와 b의 내적은 a[0]*b[0] + a[1]*b[1] + ... + a[n-1]*b[n-1] 입니다. (n은 a, b의 길이)
제한사항
a, b의 길이는 1 이상 1,000 이하입니다.
a, b의 모든 수는 -1,000 이상 1,000 이하입니다.

---
입출력 예 설명
입출력 예 #1

a와 b의 내적은 1*(-3) + 2*(-1) + 3*0 + 4*2 = 3 입니다.
입출력 예 #2

a와 b의 내적은 (-1)*1 + 0*0 + 1*(-1) = -2 입니다.

---
풀이 
- 난이도가 있어보이는 문제는 아닌것 같습니다..
- 문제 설명만 잘 들어도 풀수 있음!!
- IntStream을 이용하여 문제 처리


```java
public int solution(int[] a, int[] b) {
    return IntStream.range(0, a.length)
        .map(i -> a[i] + b[i])
        .sum();
    }
```