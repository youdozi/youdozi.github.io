---
layout: posts
title: "[jdk] jdk21 string templates"
date: 2023-09-23 00:00:00 +0900
categories:
  - jdk
tags:
  - jdk21
  - openjdk
  - string templates
---

## 개요

jdk 21의 미리보기 중 하나인 string templates에 대해 이야기 해보겠습니다.

## 문자열 템플릿
java 에서 문자열을 처리하는 방법은 타 언어에 비해 상당히 까다롭습니다.  
그 예를 들자면 아래와 같습니다.

### +연산자를 사용한 문자열 연결
```java
String s = x + " plus " + y + " equals " + (x + y);
```
### StringBuilder
```java
String s = new StringBuilder()
    .append(x)
    .append(" plus ")
    .append(y)
    .append(" equals ")
    .append(x + y)
    .toString();
```
### String.format && formatted
```java
String s = String.format("%2$d plus %1$d equals %3$d", x, y, x + y);
String t = "%2$d plus %1$d equals %3$d".formatted(x, y, x + y);
```
### java.text.MessageFormat
```java
MessageFormat mf = new MessageFormat("{0} plus {1} equals {2}");
String s = mf.format(x, y, x + y);
```
### 문자열 보간
많은 프로그래밍 언어는 문자열 연결 대신 문자열 보간을 제공합니다. 
일반적으로 텍스트뿐만 아니라 표현식을 포함하는 문자열 형태를 취합니다.  
표현식을 넣을 수 있다는 것은 의도한 결과를 쉽게 식별할 수 있다는 것을 의미하죠.   
런타임 시 표현식은 해당 (문자열화된) 값으로 대체됩니다.  
즉, 값이 문자열에 보간 된다고 합니다.

다른 언어에서의 문자열 보간은 어떻게 사용할까요?
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
일부는 모든 문자열 리터럴에 대해 보간을 활성화하는 반면, 다른 언어에서는 원할 때 보간을 활성화해야 합니다.

코드를 작성할 때 문자열 보간은 문자열 연결보다 더 편리할 뿐만 아니라 코드를 읽을 때 더 명확성을 제공합니다.  
문자열이 크면 클 수록 더 큰 힘을 발휘합니다.  
javascript를 예로 들어 보겠습니다.
```html
const title = "My Web Page";
const text  = "Hello, world";

var html = `<html>
              <head>
                <title>${title}</title>
              </head>
              <body>
                <p>${text}</p>
              </body>
            </html>`;
```

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