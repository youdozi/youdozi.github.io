---
title: "[코딩테스트] 프로그래머스 - 음양 더하기(JAVA)"
language: "ko"
translationKey: "2021-07-22-plus-minus"
routeSlug: "2021-07-22-plus-minus"
kind: "post"
publishedAt: "2021-07-22T03:40:30.000Z"
categories:
  - "coding-test"
tags:
  - "코딩테스트"
  - "프로그래머스"
legacyUrl: "/coding-test/plus-minus/"
legacySource: "_posts/coding-test/2021-07-22-plus-minus.markdown"
updatedAt: "2026-10-24T09:00:00+09:00"
reviewedAt: "2026-10-24"
reviewStatus: "revised"
reviewScope: "문제 조건 대조 및 Java 예제 실행 검증"
archiveBodySha256: "3d9fd33deca9cb8827c9696a87a5df201fa03357485d41c5438963847d7cb334"
reviewSources:
  - "https://school.programmers.co.kr/learn/courses/30/lessons/76501"
---
문제 설명

어떤 정수들이 있습니다. 이 정수들의 절댓값을 차례대로 담은 정수 배열 absolutes와 이 정수들의 부호를 차례대로 담은 불리언 배열 signs가 매개변수로 주어집니다. 
실제 정수들의 합을 구하여 return 하도록 solution 함수를 완성해주세요.

---
제한사항
- absolutes의 길이는 1 이상 1,000 이하입니다.
- absolutes의 모든 수는 각각 1 이상 1,000 이하입니다.
- signs의 길이는 absolutes의 길이와 같습니다.
- signs[i] 가 참이면 absolutes[i] 의 실제 정수가 양수임을, 그렇지 않으면 음수임을 의미합니다.

---
풀이 
- 그냥 아무 문제씩 풀고 있는데... level 1인듯..
- 매우 쉽다고 합니다.
- IntStream을 이용하여 문제 처리


```java
public int solution(int[] absolutes, boolean[] signs) {
    return IntStream.range(0, absolutes.length)
        .map(i -> signs[i] ? absolutes[i] : absolutes[i] * -1)
        .sum();
    }
```

## 검증 및 보강 — 2026-10-24

같은 인덱스의 부호를 적용한 다음 합산합니다. `[4,7,12]`, `[true,false,true]`는 `9`, 모두 음수이면 절댓값 합의 음수가 됩니다. 시간 O(n), 추가 공간 O(1)이며 주어진 범위의 합은 `int`로 표현할 수 있습니다. 실제 서비스 입력이라면 두 배열의 길이가 같은지도 검사해야 합니다.

메서드 예제는 `Solution` 클래스 내부에 넣는 형태이며, 사용한 클래스는 `java.util.stream.IntStream`입니다. 필요한 import를 클래스 선언 위에 추가하세요.

### 확인한 자료

- [공식 자료 1](https://school.programmers.co.kr/learn/courses/30/lessons/76501)
