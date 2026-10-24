---
title: "[jdk] jdk21 string templates"
language: "ko"
translationKey: "2023-09-23-jdk-21-string-templates"
routeSlug: "2023-09-23-jdk-21-string-templates"
kind: "post"
publishedAt: "2023-09-22T15:00:00.000Z"
categories:
  - "jdk"
tags:
  - "jdk21"
  - "openjdk"
  - "string templates"
legacyUrl: "/jdk/jdk-21-string-templates/"
legacySource: "_posts/jdk/jdk21-string-templates/2023-09-23-jdk-21-string-templates.markdown"
updatedAt: "2026-10-24T09:00:00+09:00"
reviewedAt: "2026-10-24"
reviewStatus: "revised"
reviewScope: "공식 문서 대조 및 예제 코드 검토"
archiveBodySha256: "4411bddc3034ae15549b487f6da92df57e43372c6636d8c75d9f33711e7f23ff"
reviewSources:
  - "https://inside.java/2024/06/20/newscast-71/"
  - "https://openjdk.org/jeps/430"
  - "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/text/MessageFormat.html"
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
String s = String.format("%1$d plus %2$d equals %3$d", x, y, x + y);
String t = "%1$d plus %2$d equals %3$d".formatted(x, y, x + y);
```
### java.text.MessageFormat
```java
MessageFormat mf = new MessageFormat("{0} plus {1} equals {2}");
String s = mf.format(new Object[] {x, y, x + y});
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

## 검증 및 보강 — 2026-10-24

이 글의 `STR` 문법은 JDK 21 Preview와 JDK 22의 두 번째 Preview에 관한 기록입니다. JDK 23에서는 문자열 템플릿이 제거됐으며 `--enable-preview`만 추가해서 사용할 수 없습니다. JDK 21에서 재현하려면 해당 JDK의 컴파일러와 런타임 모두에 preview 옵션을 적용합니다. 예를 들어 `javac --enable-preview --release 21 Example.java`, `java --enable-preview Example`입니다. 본문의 `|`로 시작하는 줄은 JShell 출력 예시이며 Java 소스에 복사하면 안 됩니다. `STR`로 JSON이나 SQL 문자열을 조립해도 자동으로 escaping되거나 파라미터 바인딩되는 것은 아닙니다. JSON 직렬화기와 SQL 바인딩을 별도로 사용해야 합니다. `MessageFormat` 예제도 배열을 받는 실제 API에 맞춰 수정했습니다.

### 확인한 자료

- [공식 자료 1](https://inside.java/2024/06/20/newscast-71/)
- [공식 자료 2](https://openjdk.org/jeps/430)
- [공식 자료 3](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/text/MessageFormat.html)
