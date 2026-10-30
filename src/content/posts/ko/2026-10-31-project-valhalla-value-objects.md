---
language: "ko"
translationKey: "2026-10-31-project-valhalla-value-objects"
routeSlug: "2026-10-31-project-valhalla-value-objects"
kind: "post"
categories: ["jdk"]
tags: ["java", "jdk", "valhalla", "value-objects", "jep-401"]
publishedAt: "2026-10-30T15:22:17.028660+00:00"
updatedAt: "2026-10-30T15:22:17.028660+00:00"
title: "Java Project Valhalla: 값 객체와 record의 차이, JDK 28 미리보기"
description: "Project Valhalla와 JEP 401의 현재 상태를 확인합니다. JDK 28 EA 예제로 value record의 정체성·동등성·잠금 제한을 비교하고 메모리 최적화의 범위를 설명합니다."
reviewedAt: "2026-10-31"
reviewStatus: "revised"
reviewScope: "Primary OpenJDK project/JEP/specification/API sources; JDK 28 EA Build 21 semantic example. No memory-layout, allocation, GC or throughput measurements; preview is not a finalized feature."
reviewSources: ["https://openjdk.org/projects/valhalla/", "https://openjdk.org/jeps/401", "https://openjdk.org/jeps/539", "https://jdk.java.net/28/", "https://docs.oracle.com/en/java/javase/17/language/records.html", "https://download.java.net/java/early_access/jdk28/docs/api/java.base/java/util/Objects.html", "https://openjdk.org/jeps/401#Comparing-value-objects"]
---
Project Valhalla는 **객체의 정체성(identity)이 필요 없는 데이터를 값 객체로 표현하고, JVM이 더 효율적으로 배치·전달할 수 있게 하는 OpenJDK 프로젝트**입니다. [공식 프로젝트 페이지](https://openjdk.org/projects/valhalla/)와 [JEP 401](https://openjdk.org/jeps/401)을 2026년 10월 31일 확인한 기준으로, 첫 값 객체 미리보기는 JDK 28에 통합됐습니다. 정식 기능으로 확정된 상태는 아니며, 아래 예제는 JDK 28 EA Build 21에서 실행했습니다.

## record가 있는데 왜 값 클래스가 필요한가요?

일반 객체는 필드가 같아도 서로 다른 객체라는 정체성을 가집니다. 변경 가능한 계좌나 잠금 객체는 이 구분이 필요하지만, 좌표 `(3, 4)`처럼 값 자체가 관심사인 데이터에는 별도 정체성이 불필요할 수 있습니다.

[`record`](https://docs.oracle.com/en/java/javase/17/language/records.html)는 데이터 구성 요소를 선언하면 접근자·생성자·`equals()` 등을 제공하는 표현 방식입니다. 기존의 일반 레코드는 같은 구성 요소를 가져도 `new`로 만든 두 객체를 `==`로 구분할 수 있습니다. `value`는 객체의 정체성을 없애는 별도 선택이며, `value record`처럼 레코드와 함께 쓸 수 있습니다.

| 선언 | 이 예제에서의 의미 |
| --- | --- |
| `record IdentityPoint(int x, int y)` | 구성 요소는 같아도 별도 객체의 정체성을 유지 |
| `value record ValuePoint(int x, int y)` | 같은 클래스·필드 상태라면 정체성으로 구분하지 않음 |
| `value record Label(String text)` | 정체성이 없어도 `==`와 `equals()`가 항상 같지는 않음 |

값 클래스의 인스턴스 필드는 `final`입니다. 참조 필드가 가리키는 객체까지 자동으로 깊은 불변이 되는 것은 아니므로, 변경 가능한 컬렉션을 담으면 그 내용은 여전히 바뀔 수 있습니다. 값 객체도 객체 참조로 다루며 원시 타입이 되는 것은 아닙니다.

## JDK 28 미리보기에서 직접 비교하기

![일반 레코드와 값 레코드를 만들고 비교·정체성·참조 필드·null 배열·잠금 제한을 순서대로 확인](/assets/diagrams/2026-10-31-project-valhalla-value-objects-ko.svg)

그림은 아래 코드의 실행 순서입니다. `Label`에는 내용이 같은 서로 다른 `String`을 넣어, 참조 필드의 비교까지 드러냅니다. 마지막에는 값 객체를 `Object` 변수로 옮겨도 모니터 잠금에 사용할 수 없는지 확인하고 예상 예외를 처리합니다.

[JDK 28 EA](https://jdk.java.net/28/)의 `javac`와 `java`가 같은 빌드를 가리키는 별도 실험 디렉터리에서 실행합니다. 다운로드 파일은 공식 SHA-256과 대조하고 `java --version`으로 빌드를 확인합니다. JDK 17·21에서는 이 구문을 컴파일할 수 없으며, 미리보기 플래그는 컴파일과 실행 양쪽에 필요합니다.

### `ValhallaExample.java`

```java
import java.util.Objects;

public class ValhallaExample {
    record IdentityPoint(int x, int y) {}
    value record ValuePoint(int x, int y) {}
    value record Label(String text) {}

    public static void main(String[] args) {
        IdentityPoint a = new IdentityPoint(3, 4);
        IdentityPoint b = new IdentityPoint(3, 4);
        ValuePoint p = new ValuePoint(3, 4);
        ValuePoint q = new ValuePoint(3, 4);
        System.out.println("record == " + (a == b));
        System.out.println("record equals " + a.equals(b));
        System.out.println("value == " + (p == q));
        System.out.println("value equals " + p.equals(q));
        System.out.println("record identity " + Objects.hasIdentity(a));
        System.out.println("value identity " + Objects.hasIdentity(p));

        Label first = new Label(new String(new char[] {'x'}));
        Label second = new Label(new String(new char[] {'x'}));
        System.out.println("label == " + (first == second));
        System.out.println("label equals " + first.equals(second));

        ValuePoint[] points = new ValuePoint[1];
        System.out.println("array slot null " + (points[0] == null));
        Object monitor = p;
        try {
            synchronized (monitor) {
                throw new AssertionError("A value object must not be a monitor");
            }
        } catch (IdentityException expected) {
            System.out.println("monitor " + expected.getClass().getSimpleName());
        }
    }
}
```

```sh
javac --enable-preview --release 28 ValhallaExample.java
java --enable-preview ValhallaExample
```

macOS AArch64용 OpenJDK `28-ea+21-1707`에서 확인한 출력입니다. 컴파일러의 미리보기 안내는 아래 표준 출력과 별도로 나옵니다.

```text
record == false
record equals true
value == true
value equals true
record identity true
value identity false
label == false
label equals true
array slot null true
monitor IdentityException
```

일반 레코드는 `equals()`가 참이어도 `==`는 거짓입니다. 정수 필드만 있는 값 레코드는 같은 필드 상태이므로 두 비교가 모두 참입니다. [`Objects.hasIdentity()`](https://download.java.net/java/early_access/jdk28/docs/api/java.base/java/util/Objects.html#hasIdentity(java.lang.Object))의 결과도 그 차이를 보여줍니다.

## 값 객체라면 ==를 써도 되나요?

업무상 동등성은 계속 `equals()`로 비교합니다. 값 객체의 `==`는 같은 값 클래스의 필드 상태를 비교하며, 참조 필드에는 `==`를 재귀적으로 적용합니다. 정체성이 있는 참조 대상은 내용이 같아도 별도 객체라면 구분됩니다. 원시 필드는 비트 패턴이 기준이므로 부동소수점의 의미상 동등성과도 차이가 날 수 있습니다. 세부 규칙은 [JEP 401의 값 객체 비교 규칙](https://openjdk.org/jeps/401#Comparing-value-objects)을 따릅니다.

예제의 두 `Label`은 내부 문자열 내용이 같아 레코드의 `equals()`는 참이지만, 서로 다른 정체성 객체인 문자열을 담아 `==`는 거짓입니다. `value`가 모든 참조 필드를 내용 기반 비교로 바꾼다고 해석하면 안 됩니다.

새 값 배열의 슬롯은 `null`이며, 값 객체를 잠금 대상으로 사용하면 동적으로 `IdentityException`이 발생합니다. 명백한 값 클래스 타입을 직접 잠그려 하면 컴파일 단계에서 거부될 수도 있습니다. 잠금·정체성 기반 캐시처럼 객체 구분에 의존하는 용도는 전환 전에 따로 점검해야 합니다.

## 메모리가 바로 줄거나 List<int>를 쓸 수 있나요?

정체성을 없애면 JVM은 참조를 포인터 대신 필드 상태로 표현하는 **flattening**, 값을 레지스터 등에 나누어 전달하는 **scalarization**을 적용할 여지가 생깁니다. 특정 메모리 배치·할당 제거·속도 향상을 언어가 보장하지는 않습니다. 위 출력은 의미 검증이며 힙 크기나 처리량을 측정한 결과가 아닙니다.

Valhalla는 여러 JDK에 걸친 작업입니다. [공식 로드맵](https://openjdk.org/projects/valhalla/)은 값 객체 외에도 null 제한 저장, 배열 확장, 원시 타입과 클래스의 통합, 제네릭 특수화를 위한 Parametric JVM을 구분합니다. JEP 401 하나로 `List<int>`나 모든 배열의 연속 저장이 완성됐다고 볼 수 없습니다. 함께 통합된 [JEP 539](https://openjdk.org/jeps/539)는 엄격한 필드 초기화를 위한 JVM 기반이며 Java 코드에 임의의 `strict` 필드 수식어를 추가하는 기능이 아닙니다.

실험을 시작한다면 좌표·금액처럼 정체성이 필요 없는 작은 데이터부터 골라 같은 빌드에서 동작을 비교합니다. 프레임워크·직렬화·잠금 의존성을 확인한 뒤, 대표 워크로드로 할당량·GC·처리량을 측정해야 도입 이점을 판단할 수 있습니다. 현재 미리보기를 정식 지원 기능으로 간주해 운영 JDK를 교체하지는 않습니다. 정식 기능과 미리보기의 구분은 [JDK 기능 안내](/ko/posts/2023-09-20-jdk-21-release/)에서 이어 볼 수 있습니다.
