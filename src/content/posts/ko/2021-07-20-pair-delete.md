---
title: "Java 짝지어 제거하기: ArrayDeque 스택의 불변식"
language: ko
translationKey: 2021-07-20-pair-delete
routeSlug: 2021-07-20-pair-delete
kind: post
publishedAt: 2021-07-19T22:40:30.000Z
categories:
  - coding-test
tags:
  - 코딩테스트
  - 프로그래머스
legacyUrl: /coding-test/pair-delete/
legacySource: _posts/coding-test/2021-07-20-pair-delete.markdown
updatedAt: 2026-10-27T04:11:15.275Z
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Problem conditions and Java APIs checked; complete paired solutions
  compiled for Java11 and run on JDK17.
archiveBodySha256: 7da325a5fa6e09ce0b7dda410c94b404c23d9ff503fa8fe5325d9077c21cac9b
reviewSources:
  - https://school.programmers.co.kr/learn/courses/30/lessons/12973
  - https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/ArrayDeque.html
description: 같은 인접 문자 쌍을 스택으로 제거합니다. 접두사 결과를 유지하는 원리와 연쇄 제거, 백만 자 입력, 시간·공간 복잡도를 설명합니다.
---
인접한 같은 문자 두 개를 지우는 문제는, 지금까지 읽은 문자열의 정리 결과를 스택에 남기면 한 번의 순회로 풀 수 있습니다. 새 문자가 맨 위와 같으면 둘을 제거하고, 다르면 새 문자를 쌓습니다.

[문제](https://school.programmers.co.kr/learn/courses/30/lessons/12973)의 입력은 길이 1~1,000,000인 영문 소문자 문자열입니다. 모두 제거할 수 있으면 1, 문자가 남으면 0을 반환합니다. 단순히 각 문자의 총개수가 짝수인지 확인하는 조건만으로는 인접성 규칙을 표현할 수 없습니다.

## 접두사의 정리 결과를 보관

전체 코드를 `Solution.java`에 저장합니다. JDK 17에서 Java 11 타깃으로 컴파일하고 실행한 예제입니다.

```java
import java.util.ArrayDeque;
import java.util.Deque;

public class Solution {
    public int solution(String s) {
        Deque<Character> stack = new ArrayDeque<>();
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (!stack.isEmpty() && stack.peek() == c) stack.pop();
            else stack.push(c);
        }
        return stack.isEmpty() ? 1 : 0;
    }
}
```

스택에는 처리한 접두사에서 더 이상 같은 문자가 연속하지 않는 결과가 남습니다. 새 문자가 맨 위와 같으면 경계에서 제거할 쌍이 생기므로 pop합니다. 다르면 기존 결과와 새 문자 사이에 제거할 쌍이 없으므로 push합니다. 이 성질이 다음 문자에서도 유지됩니다.

| 읽은 문자 | 스택 내용: 바닥 → 맨 위 |
| --- | --- |
| b | b |
| a | ba |
| a | b |
| b | 빈 스택 |
| a | a |
| a | 빈 스택 |

따라서 `baabaa`는 1입니다. 반면 `abab`는 a와 b가 각각 짝수 번 나오지만 인접한 같은 문자가 없어 0입니다. 전체 문자열을 여러 번 다시 치환할 필요 없이, 제거로 연결된 경계를 스택 맨 위에서 처리합니다.

## ArrayDeque와 복잡도

[`ArrayDeque`](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/ArrayDeque.html)를 Deque 인터페이스의 `push`·`peek`·`pop`으로 사용합니다. 비교 대상 `c`는 primitive char이므로 `stack.peek() == c`에서는 Character가 char로 풀립니다. 객체 참조가 같은지를 비교하는 코드로 해석하면 안 됩니다.

각 문자는 최대 한 번 추가되고 최대 한 번 제거됩니다. deque 연산의 분할 상환 비용을 기준으로 시간 O(n), 제거되지 않는 입력의 최악 추가 공간 O(n)입니다. 백만 자의 같은 문자 반복과 인접 쌍이 없는 교대 입력을 실행했지만, 이를 속도 벤치마크나 모든 환경의 메모리 보장으로 확대하지 않습니다.

같은 선형 순회라도 무엇을 저장해야 하는지는 문제에 따라 다릅니다. [미완주 선수](/ko/posts/2021-07-23-unsuccessful-runner/)는 인접 순서가 아니라 이름별 빈도를 저장합니다.
