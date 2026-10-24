---
title: "[코딩테스트] 프로그래머스 - 내적(JAVA)"
language: "ko"
translationKey: "2021-07-22-dot-product"
routeSlug: "2021-07-22-dot-product"
kind: "post"
publishedAt: "2021-07-21T22:40:30.000Z"
categories:
  - "coding-test"
tags:
  - "코딩테스트"
  - "프로그래머스"
legacyUrl: "/coding-test/dot-product/"
legacySource: "_posts/coding-test/2021-07-22-dot-product.markdown"
updatedAt: "2026-10-24T09:00:00+09:00"
reviewedAt: "2026-10-24"
reviewStatus: "revised"
reviewScope: "문제 조건 대조 및 Java 예제 실행 검증"
archiveBodySha256: "2e45b814b9fc5c057a9888b865185a2cdb5e0cf5ed9311409a381b6b41fc3874"
reviewSources:
  - "https://school.programmers.co.kr/learn/courses/30/lessons/70128"
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
        .map(i -> a[i] * b[i])
        .sum();
    }
```

## 검증 및 보강 — 2026-10-24

기존 예제의 `a[i] + b[i]`는 내적이 아니므로 `a[i] * b[i]`로 수정했습니다. `[1,2,3,4]`, `[-3,-1,0,2]`의 결과는 `3`입니다. 길이 n에 대해 시간 O(n), 추가 공간 O(1)입니다. 문제의 최댓값은 절댓값 기준 1,000 × 1,000 × 1,000 = 1,000,000,000으로 `int` 범위 안입니다. 더 큰 입력에 일반화할 때는 곱셈 전에 `(long) a[i]`로 승격해야 합니다.

메서드 예제는 `Solution` 클래스 내부에 넣는 형태이며, 사용한 클래스는 `java.util.stream.IntStream`입니다. 필요한 import를 클래스 선언 위에 추가하세요.

### 확인한 자료

- [공식 자료 1](https://school.programmers.co.kr/learn/courses/30/lessons/70128)
