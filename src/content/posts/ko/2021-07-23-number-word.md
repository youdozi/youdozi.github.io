---
title: "Java 숫자 영단어 변환: replace와 replaceAll 구분하기"
language: ko
translationKey: 2021-07-23-number-word
routeSlug: 2021-07-23-number-word
kind: post
publishedAt: 2021-07-22T16:40:30.000Z
categories:
  - coding-test
tags:
  - 코딩테스트
  - 프로그래머스
legacyUrl: /coding-test/number-word/
legacySource: _posts/coding-test/2021-07-23-number-word.markdown
updatedAt: 2026-10-27T03:54:18.369Z
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Problem conditions and Java APIs checked; paired solutions compiled
  for Java11 and executed on JDK17.
archiveBodySha256: ba839b771906b77824503f370c411957b63b0618468d62fccd976afe2ee7db7c
reviewSources:
  - https://school.programmers.co.kr/learn/courses/30/lessons/81301
  - https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/lang/String.html
description: 숫자와 zero~nine 영단어가 섞인 유효 입력을 String.replace로 정규화합니다. 정규식이 필요 없는 이유와
  int 변환·복잡도·적용 범위를 설명합니다.
---
숫자와 영단어가 섞인 유효 입력은 `zero`부터 `nine`까지 고정 문자열을 숫자로 치환한 뒤 정수로 읽으면 됩니다. 찾을 대상이 정규식이 아니므로 `replaceAll` 대신 `String.replace`를 사용할 수 있습니다.

[문제](https://school.programmers.co.kr/learn/courses/30/lessons/81301)는 소문자 숫자 영단어와 숫자로 구성된 올바른 입력을 보장합니다. 결과는 1~2,000,000,000이고 맨 앞 0은 주어지지 않습니다. 일반적인 영어 수 표현을 해석하는 파서는 아닙니다.

## 고정된 열 단어 치환

전체 코드를 `Solution.java`에 저장할 수 있습니다. 별도 import가 필요 없으며 Java 11 타깃으로 컴파일·실행했습니다.

```java
public class Solution {
    public int solution(String s) {
        String[] words = {"zero", "one", "two", "three", "four",
                "five", "six", "seven", "eight", "nine"};
        for (int digit = 0; digit < words.length; digit++) {
            s = s.replace(words[digit], Integer.toString(digit));
        }
        return Integer.parseInt(s);
    }
}
```

[`String.replace(CharSequence, CharSequence)`](https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/lang/String.html)는 일치하는 문자열을 리터럴로 치환합니다. `replaceAll`은 첫 인자를 정규식으로 처리하므로 규칙이 다릅니다. 여기서는 열 단어 어디에도 정규식 문법이 필요하지 않습니다.

예를 들어 `one4seveneight`는 `1478`, `23four5six7`은 `234567`이 됩니다. 이미 숫자로만 된 `123`도 그대로 정수 123이 됩니다. `two` 뒤에 `zero`가 아홉 번 이어진 입력은 2,000,000,000으로 int 범위 안입니다.

치환 결과의 숫자는 다른 영단어를 새로 만들지 않고, 열 단어 중 다른 단어를 내부에 포함하는 항목도 없으므로 이 순서대로 처리할 수 있습니다. 잘못된 단어·공백·대문자·범위 밖 숫자의 처리는 문제의 보장 범위에 포함되지 않습니다. 예를 들어 임의 입력에서 파싱 실패가 나면 이를 유효한 정수라고 보정해 주는 코드는 아닙니다.

단어 수가 10개로 고정돼 있어 길이 n에 대해 시간은 O(n)입니다. 문자열은 불변이므로 중간 치환 결과를 만들 수 있고, 추가 공간도 O(n)으로 봅니다. 이 작은 입력에서 다른 파서보다 빠르다는 성능 측정은 하지 않았습니다.

정규식이 실제로 유용한 문자열 변환은 [신규 아이디 정규화](/ko/posts/2021-07-19-new-id/)와 비교할 수 있습니다.
