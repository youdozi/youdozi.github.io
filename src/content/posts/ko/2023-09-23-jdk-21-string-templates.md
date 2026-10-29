---
title: "Java String Templates: JDK 21 실행과 JDK 23 제거 대응"
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
updatedAt: 2026-10-27T05:23:47.316+00:00
reviewedAt: "2026-10-27"
reviewStatus: "revised"
reviewScope: "공식 문서 대조, 재현 절차와 버전별 적용 조건 보강"
archiveBodySha256: "4411bddc3034ae15549b487f6da92df57e43372c6636d8c75d9f33711e7f23ff"
reviewSources:
  - "https://inside.java/2024/06/20/newscast-71/"
  - "https://docs.oracle.com/en/java/javase/21/language/string-templates.html"
  - "https://docs.oracle.com/en/java/javase/21/language/preview-language-and-vm-features.html"
  - "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/text/MessageFormat.html"
  - "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/String.html"
description: "JDK 21 String Templates의 전체 실행 예제와 preview 옵션, JDK 23에서 STR을 사용할 수 없는 이유, 표준 문자열 API로 교체하는 방법을 정리합니다."
---
String Templates는 JDK 21·22의 미리보기 기능이었고 JDK 23에서 제거됐습니다. JDK 23에 `--enable-preview`를 붙여도 `STR`을 사용할 수 없습니다. 해당 미리보기를 벗어나야 하는 코드는 표준 문자열 API나 출력 형식에 맞는 직렬화기로 바꿔야 합니다. 변경 배경은 [Oracle의 제거 설명](https://inside.java/2024/06/20/newscast-71/)에서 확인할 수 있습니다.

## 처리 흐름

![표준 문자열 포맷 API 사용 흐름도](/assets/diagrams/2023-09-23-jdk-21-string-templates-ko.svg)

과거 preview 예제가 아닌 표준 FormattingExample의 흐름입니다. 세 표현을 비교하고 MessageFormat의 작은따옴표 처리를 확인합니다.

## 예전 코드는 어느 JDK에서 실행할 수 있을까?

| JDK | String Templates 상태 | 실행 또는 이전 방법 |
| --- | --- | --- |
| 21 | 미리보기 | JDK 21 컴파일러·런타임에서 preview 옵션을 사용합니다. |
| 22 | 두 번째 미리보기 | JDK 22 컴파일러·런타임과 그 버전에 맞는 preview 설정을 사용합니다. |
| 23 | 제거 | 미리보기 문법을 교체합니다. 옵션으로 제거된 기능을 복원할 수 없습니다. |

최신 컴파일러에 `--release`를 지정하는 것만으로 예전 미리보기를 되살릴 수는 없습니다. [Oracle의 preview 안내](https://docs.oracle.com/en/java/javase/21/language/preview-language-and-vm-features.html)는 해당 미리보기와 같은 버전의 컴파일러를 사용하도록 설명합니다.

## JDK 21 미리보기 실행하기

다음 클래스를 `Example.java`로 저장합니다. 다른 JDK가 기본으로 설정돼 있다면 이 예제를 실행할 때는 JDK 21을 선택해야 합니다.

```java
public class Example {
    public static void main(String[] args) {
        int x = 2;
        int y = 3;
        String result = STR."\{x} plus \{y} equals \{x + y}";
        System.out.println(result);
    }
}
```

파일이 있는 디렉터리에서 선택된 도구의 버전을 확인한 뒤 컴파일·실행합니다.

```sh
javac -version
java -version
javac --enable-preview --release 21 Example.java
java --enable-preview Example
```

출력은 `2 plus 3 equals 5`입니다. 컴파일할 때 미리보기 기능을 사용한다는 안내도 나옵니다. JDK 21의 이 미리보기에서는 `STR`이 암묵적으로 import됩니다. 이후 JDK에서 processor를 찾지 못하는 문제를 import 추가로 해결할 수는 없습니다. [JDK 21 String Templates 안내](https://docs.oracle.com/en/java/javase/21/language/string-templates.html)를 함께 참고하세요.

## 표준 문자열 API로 교체하기

다음은 `FormattingExample.java`로 저장합니다. preview 옵션이 필요 없는 완전한 클래스이며 Java 17에서 실행할 수 있습니다. 숫자 출력을 일정하게 재현하도록 `String.format`과 `MessageFormat`에 로케일을 명시했습니다.

```java
import java.text.MessageFormat;
import java.util.Locale;

public class FormattingExample {
    public static void main(String[] args) {
        int x = 2;
        int y = 3;
        System.out.println(x + " plus " + y + " equals " + (x + y));
        System.out.println(String.format(Locale.ROOT, "%1$d plus %2$d equals %3$d", x, y, x + y));
        MessageFormat format = new MessageFormat("{0} plus {1} equals {2}", Locale.ROOT);
        System.out.println(format.format(new Object[] {x, y, x + y}));
        System.out.println(new MessageFormat("It''s {0}", Locale.ROOT)
            .format(new Object[] {"ready"}));
    }
}
```

```sh
javac FormattingExample.java
java FormattingExample
```

실행 결과는 다음과 같습니다.

```text
2 plus 3 equals 5
2 plus 3 equals 5
2 plus 3 equals 5
It's ready
```

| 필요한 작업 | 사용할 API | 확인할 점 |
| --- | --- | --- |
| 짧은 문자열 연결 | `+` | `x + y`를 괄호로 감싸 산술 연산을 먼저 수행합니다. |
| 반복해서 문자열 추가 | `StringBuilder` | 문자열을 단계적으로 구성할 때 사용할 수 있습니다. |
| 형식 지정 문자열 | `String.format` 또는 `.formatted` | `%d`, `%s`는 Formatter 규칙을 따릅니다. 로케일을 고정하려면 `String.format(Locale.ROOT, ...)`를 사용합니다. |
| 다국어 메시지 패턴 | `MessageFormat` | 번호가 있는 인자와 객체 배열을 사용하며 따옴표 규칙도 다릅니다. |

`MessageFormat`에서 작은따옴표는 패턴 문법입니다. 예제의 `It''s {0}`처럼 두 번 적으면 출력에는 작은따옴표 하나가 들어갑니다. `%s`를 `{0}`으로 바꿀 때는 호출 API와 로케일 동작도 함께 확인해야 합니다. [MessageFormat API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/text/MessageFormat.html), [String API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/String.html).

## 문자열 포매팅과 인코딩 구분하기

`STR`과 일반 포매팅은 임의의 값을 안전한 JSON·SQL·HTML로 바꿔주지 않습니다. JSON은 직렬화기, SQL은 파라미터 바인딩, HTML은 렌더링 시스템의 이스케이프 규칙을 적용해야 합니다. 단순한 값에서 정상으로 보이는 문자열도 값에 따옴표나 역슬래시가 들어가면 달라질 수 있습니다.

두 클래스는 위 명령으로 컴파일·실행했습니다. 미리보기는 JDK 21.0.1, 표준 대안은 JDK 17.0.8.1과 21.0.1에서 확인했습니다. 표의 JDK 22·23 행은 문서로 확인한 기능 이력이며 이 환경에서 실행한 결과는 아닙니다.

JDK를 올릴 때는 프레임워크의 호환 조건도 확인해야 합니다. 기존 Spring 애플리케이션이라면 [Spring Boot 2.7에서 3.0으로 옮기는 순서](/ko/posts/2023-09-08-springboot3-migration/)를 참고하세요.
