---
title: "[코딩테스트] 프로그래머스 - 숫자 문자열과 영단어(JAVA)"
language: "ko"
translationKey: "2021-07-23-number-word"
routeSlug: "2021-07-23-number-word"
kind: "post"
publishedAt: "2021-07-22T16:40:30.000Z"
categories:
  - "coding-test"
tags:
  - "코딩테스트"
  - "프로그래머스"
legacyUrl: "/coding-test/number-word/"
legacySource: "_posts/coding-test/2021-07-23-number-word.markdown"
updatedAt: "2026-10-24T09:00:00+09:00"
reviewedAt: "2026-10-24"
reviewStatus: "revised"
reviewScope: "문제 조건 대조 및 Java 예제 실행 검증"
archiveBodySha256: "ba839b771906b77824503f370c411957b63b0618468d62fccd976afe2ee7db7c"
reviewSources:
  - "https://school.programmers.co.kr/learn/courses/30/lessons/81301"
---
문제 설명

네오와 프로도가 숫자놀이를 하고 있습니다. 네오가 프로도에게 숫자를 건넬 때 일부 자릿수를 영단어로 바꾼 카드를 건네주면 프로도는 원래 숫자를 찾는 게임입니다.

다음은 숫자의 일부 자릿수를 영단어로 바꾸는 예시입니다.

1478 → "one4seveneight"

234567 → "23four5six7"

10203 → "1zerotwozero3"

이렇게 숫자의 일부 자릿수가 영단어로 바뀌어졌거나, 혹은 바뀌지 않고 그대로인 문자열 s가 매개변수로 주어집니다. s가 의미하는 원래 숫자를 return 하도록 solution 함수를 완성해주세요.

---
제한사항
- 1 ≤ s의 길이 ≤ 50
- s가 "zero" 또는 "0"으로 시작하는 경우는 주어지지 않습니다.
- return 값이 1 이상 2,000,000,000 이하의 정수가 되는 올바른 입력만 s로 주어집니다.

---
풀이
- 프로그래머스 level 1단계 문제
- 정통적인 for loop를 이용하는게 정신건강 상 좋습니다..
- 뭔가 아쉽긴 한 문제...


```java
public int solution(String s){

    /**
     * 미리 숫자 & 영단어를 array로 선언하도록 합니다.
     */
    String[] strArray = {"zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
    "nine"};
    String[] numArray = {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"};

    /**
     * strArray for loop를 돌면서 s.replaceAll 메서드 실행
     */
    for (int i = 0; i < strArray.length; i++) {
      s = s.replace(strArray[i], numArray[i]);
    }

    /**
     * String -> Integer 변환
     */
    return Integer.parseInt(s);
}
```

## 검증 및 보강 — 2026-10-24

숫자 영단어는 정규식이 아닌 고정 문자열이므로 `replaceAll` 대신 `replace`로 충분합니다. 원문 코드에 빠져 있던 메서드 닫는 중괄호도 보완했습니다. `one4seveneight → 1478`, `23four5six7 → 234567`, `123 → 123`을 확인하세요. 치환 대상은 10개로 고정되어 있어 시간은 입력 길이에 선형이고, 각 치환은 새 문자열을 만들 수 있습니다.

메서드 예제는 `Solution` 클래스 내부에 넣는 형태이며, 사용한 클래스는 추가 import 없이 `java.lang`의 기본 클래스입니다. 필요한 import를 클래스 선언 위에 추가하세요.

### 확인한 자료

- [공식 자료 1](https://school.programmers.co.kr/learn/courses/30/lessons/81301)
