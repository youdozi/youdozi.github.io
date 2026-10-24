---
title: "[코딩테스트] 프로그래머스 - x만큼 간격이 있는 n개의 숫자(JAVA)"
language: "ko"
translationKey: "2021-07-29-interval-num"
routeSlug: "2021-07-29-interval-num"
kind: "post"
publishedAt: "2021-07-28T16:00:00.000Z"
categories:
  - "coding-test"
tags:
  - "코딩테스트"
  - "프로그래머스"
legacyUrl: "/coding-test/interval-num/"
legacySource: "_posts/coding-test/2021-07-29-interval-num.markdown"
updatedAt: "2026-10-24T09:00:00+09:00"
reviewedAt: "2026-10-24"
reviewStatus: "revised"
reviewScope: "문제 조건 대조 및 Java 예제 실행 검증"
archiveBodySha256: "f30452c3ef0503e7fd7521e201075a40adf222841fb80c60b0e81c444ee3c27c"
reviewSources:
  - "https://school.programmers.co.kr/learn/courses/30/lessons/12954"
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
- int 곱셈의 결과가 범위를 넘으면 오버플로가 발생합니다.
  - long casting으로 해결 가능!!


```java
public long[] solution(int x, int n) {
    return IntStream.range(0, n)
        .mapToLong(i -> (long) x * (i + 1))
        .toArray();
}
```

## 검증 및 보강 — 2026-10-24

문제는 `long[]` 결과를 요구합니다. `(long) (x * (i + 1))`은 이미 `int`에서 오버플로한 뒤 변환하므로 잘못된 접근입니다. `(long) x * (i + 1)`처럼 곱셈 전에 변환합니다. `x=-4,n=2 → [-4,-8]`, `x=0,n=3 → [0,0,0]`, `x=10,000,000,n=1000`의 마지막 값 `10,000,000,000`을 확인하세요. 시간과 반환 배열 공간은 O(n)입니다.

메서드 예제는 `Solution` 클래스 내부에 넣는 형태이며, 사용한 클래스는 `java.util.stream.IntStream`입니다. 필요한 import를 클래스 선언 위에 추가하세요.

### 확인한 자료

- [공식 자료 1](https://school.programmers.co.kr/learn/courses/30/lessons/12954)
