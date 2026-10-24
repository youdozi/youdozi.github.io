---
title: "[코딩테스트] 프로그래머스 - 짝지어 제거하기(JAVA)"
language: "ko"
translationKey: "2021-07-20-pair-delete"
routeSlug: "2021-07-20-pair-delete"
kind: "post"
publishedAt: "2021-07-19T22:40:30.000Z"
categories:
  - "coding-test"
tags:
  - "코딩테스트"
  - "프로그래머스"
legacyUrl: "/coding-test/pair-delete/"
legacySource: "_posts/coding-test/2021-07-20-pair-delete.markdown"
updatedAt: "2026-10-24T09:00:00+09:00"
reviewedAt: "2026-10-24"
reviewStatus: "revised"
reviewScope: "문제 조건 대조 및 Java 예제 실행 검증"
archiveBodySha256: "7da325a5fa6e09ce0b7dda410c94b404c23d9ff503fa8fe5325d9077c21cac9b"
reviewSources:
  - "https://school.programmers.co.kr/learn/courses/30/lessons/12973"
---
문제 설명

짝지어 제거하기는, 알파벳 소문자로 이루어진 문자열을 가지고 시작합니다. 먼저 문자열에서 같은 알파벳이 2개 붙어 있는 짝을 찾습니다. 그다음, 그 둘을 제거한 뒤, 앞뒤로 문자열을 이어 붙입니다. 이 과정을 반복해서 문자열을 모두 제거한다면 짝지어 제거하기가 종료됩니다. 문자열 S가 주어졌을 때, 짝지어 제거하기를 성공적으로 수행할 수 있는지 반환하는 함수를 완성해 주세요. 성공적으로 수행할 수 있으면 1을, 아닐 경우 0을 리턴해주면 됩니다.

예를 들어, 문자열 S = baabaa 라면

b aa baa → bb aa → aa → 의 순서로 문자열을 모두 제거할 수 있으므로 1을 반환합니다.

---
제한사항
- 문자열의 길이 : 1,000,000이하의 자연수
- 문자열은 모두 소문자로 이루어져 있습니다.

---
풀이
- 처음에는 Array로 접근할려고 했으나 Stack으로 손쉽게 처리 가능합니다.


```java
public static int solution(String s) {
    Stack<Character> stack = new Stack<>();

    /**
     * toCharArray는 String을 쪼개 char로 변환합니다.
     */
    for(Character character : s.toCharArray()){

    /**
     * stack이 비어있지 않고(!isEmpty())
     * stack 최근 추가된 데이터를 조회(peek())하여 같은 값이 있으면 -> 삭제 pop()
     */
      if (!stack.isEmpty() && stack.peek() == character) stack.pop();

    /**
     * 그 외에는 데이터 추가(push())
     */
      else stack.push(character);
    }

    /**
     * 남는 데이터가 없으면 1, 있으면 0 return
     */
    return stack.isEmpty() ? 1 : 0;
  }
```

## 검증 및 보강 — 2026-10-24

스택에는 지금까지 읽은 접두사에서 더 이상 인접한 같은 문자 쌍이 없는 결과가 남습니다. 새 문자가 스택 맨 위와 같으면 제거하고, 다르면 추가합니다. 시간 복잡도는 O(n), 최악의 추가 공간은 O(n)입니다. `baabaa → 1`, `cdcd → 0`, `aa → 1`, `a → 0`을 확인하세요. 일반 코드에서는 레거시 `Stack` 대신 `ArrayDeque`를 스택으로 사용할 수 있습니다.

메서드 예제는 `Solution` 클래스 내부에 넣는 형태이며, 사용한 클래스는 `java.util.Stack`입니다. 필요한 import를 클래스 선언 위에 추가하세요.

### 확인한 자료

- [공식 자료 1](https://school.programmers.co.kr/learn/courses/30/lessons/12973)
