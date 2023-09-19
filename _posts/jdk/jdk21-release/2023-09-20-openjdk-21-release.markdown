---
layout: posts
title: "[openjdk] jdk21 release"
date: 2023-09-20 00:00:00 +0900
categories:
  - jdk
tags:
  - jdk21
  - openjdk
  - release
---

## 개요

2023년 9월 19일. 드디어 jdk 21이 release 되었습니다.
jdk 17 lts 이후 2년 만에 만나 보는 lts이기 때문에 반갑기 그지 없습니디.
이제 마주할 jdk 21에 대해 살짝 알아보는 시간을 가져보도록 하겠습니다.

## 특징
* JEP 430 - 문자열 템플릿 (Preview)
* JEP 431 -	순차 컬렉션
* JEP 439 -	세대별 ZGC
* JEP 440 -	레코드 패턴
* JEP 441 -	스위치 패턴 매칭
* JEP 442 -	외부 함수 및 메모리 API (Third Preview)
* JEP 443 -	명명 되지 않은 패턴 및 변수 (Preview)
* JEP 444 -	가상 스레드
* JEP 445 -	명명 되지 않은 클래스 및 인스턴스 Main 메서드 (Preview)
* JEP 446 -	범위 값 (Preview)
* JEP 448 -	벡터 API (Sixth Incubator)
* JEP 449 -	제거를 위해 windows 32비트 x86 포트 중단 
* JEP 451 -	에이전트의 동적 로드를 허용 되지 않도록 준비
* JEP 452 -	키 캡슐화 매커니즘
* JEP 453 -	구조적 동시성 (Preview)

## 문자열 템플릿
java에서 문자열을 처리하는 방법은 타 언어에 비해 상당히 까다롭습니다.  
그 예를 들자면 아래와 같습니다.

+연산자를 사용한 문자열 연결
```java
String s = x + " plus " + y + " equals " + (x + y);
```

StringBuilder

```java
String s = new StringBuilder()
    .append(x)
    .append(" plus ")
    .append(y)
    .append(" equals ")
    .append(x + y)
    .toString();
```
String.format && formatted
```java
String s = String.format("%2$d plus %1$d equals %3$d", x, y, x + y);
String t = "%2$d plus %1$d equals %3$d".formatted(x, y, x + y);
```
java.text.MessageFormat
```java
MessageFormat mf = new MessageFormat("{0} plus {1} equals {2}");
String s = mf.format(x, y, x + y);
```

위에 나열된 예를 봐도 문자열 접근에 상당한 애로 사항이 있는 것을 확인할 수 있습니다.  
또한 문자열 보간 기능은 찾아볼 수 없었죠.  
다른 언어들의 문자열 보간을 보도록 할까요?
```
C#             $"{x} plus {y} equals {x + y}"
Visual Basic   $"{x} plus {y} equals {x + y}"
Python         f"{x} plus {y} equals {x + y}"
Scala          s"$x plus $y equals ${x + y}"
Groovy         "$x plus $y equals ${x + y}"
Kotlin         "$x plus $y equals ${x + y}"
JavaScript     `${x} plus ${y} equals ${x + y}`
Ruby           "#{x} plus #{y} equals #{x + y}"
Swift          "\(x) plus \(y) equals \(x + y)"
```
변수를 문자열에 쉽게 표현할 수 있도록 제공 해주고 있습니다.  
이러한 기능은 유연하며 가독성에도 긍정적인 영향을 줍니다. 

텍스트가 단일 소스 줄에 들어가든(문자열 리터럴의 경우) 여러 소스 줄에 걸쳐 있는지(텍스트 블록의 경우) 텍스트와 표현식을 혼합하는 표현식의 가독성을 향상시킵니다.

템플릿과 포함된 표현식 값 모두의 유효성 검사 및 변환을 지원하여 사용자가 제공한 값에서 문자열을 구성하고 이를 다른 시스템에 전달하는 Java 프로그램의 보안을 향상합니다(예: 데이터베이스에 대한 쿼리 작성).

Java 라이브러리가 문자열 템플릿에 사용되는 형식 지정 구문을 정의하도록 허용하여 유연성을 유지합니다.

Java가 아닌 언어(예: SQL, XML, JSON)로 작성된 문자열을 허용하는 API의 사용을 단순화합니다.

중간 문자열 표현을 거치지 않고도 리터럴 텍스트와 포함된 표현식에서 계산된 문자열이 아닌 값을 생성할 수 있습니다.
```java
String title = "My Web Page";
String text  = "Hello, world";
String html = STR."""
        <html>
          <head>
            <title>\{title}</title>
          </head>
          <body>
            <p>\{text}</p>
          </body>
        </html>
        """;
| """
| <html>
|   <head>
|     <title>My Web Page</title>
|   </head>
|   <body>
|     <p>Hello, world</p>
|   </body>
| </html>
| """

String name    = "Joan Smith";
String phone   = "555-123-4567";
String address = "1 Maple Drive, Anytown";
String json = STR."""
    {
        "name":    "\{name}",
        "phone":   "\{phone}",
        "address": "\{address}"
    }
    """;
| """
| {
|     "name":    "Joan Smith",
|     "phone":   "555-123-4567",
|     "address": "1 Maple Drive, Anytown"
| }
| """
```