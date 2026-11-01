---
"language": "ko"
"translationKey": "2026-11-02-ai-assisted-tdd"
"routeSlug": "2026-11-02-ai-assisted-tdd"
"title": "AI와 TDD로 코드 작성하기: Red·Green·Refactor를 검증하는 방법"
"description": "AI와 TDD를 결합해 요구사항에서 테스트를 만들고 실패·최소 구현·리팩토링을 반복하는 방법입니다. 실행 가능한
  Java·JUnit 예제로 테스트 약화와 경계값 오류를 확인합니다."
"categories":
  - "architecture"
"tags":
  - "ai-agent"
  - "tdd"
  - "java"
  - "junit"
  - "testing"
  - "refactoring"
"kind": "post"
"publishedAt": "2026-11-01T23:10:14.691Z"
"updatedAt": "2026-11-01T23:10:14.691Z"
"reviewedAt": "2026-11-02"
"reviewStatus": "source-audited"
"reviewScope": "1차 자료 확인·영한 자체 대조; Red/Green/Refactor 단계 실행, 최종 JUnit 9개 테스트와 회귀
  변이 3개 검증. AI 제품 실험·통합·성능 시험은 수행하지 않음."
"reviewSources":
  - "https://www.martinfowler.com/bliki/TestDrivenDevelopment.html"
  - "https://docs.junit.org/5.12.2/user-guide/"
  - "https://docs.gradle.org/current/userguide/java_testing.html"
  - "https://docs.github.com/en/copilot/tutorials/review-ai-generated-code"
---

**AI와 TDD를 결합할 때는 요구사항에서 기대값을 먼저 정하고, 실패하는 테스트를 확인한 다음 작은 구현과 리팩토링을 반복합니다.** AI는 테스트 후보와 구현을 제안할 수 있지만, 테스트와 구현이 같은 오해를 담으면 둘 다 통과해도 잘못된 기능이 만들어집니다. 테스트의 기대값이 어디에서 왔는지와 실제 실행 결과를 함께 확인해야 합니다.

TDD의 기본 흐름은 테스트 목록에서 다음 동작 하나를 고르고 Red → Green → Refactor를 반복하는 것입니다. [Martin Fowler의 TDD 설명](https://www.martinfowler.com/bliki/TestDrivenDevelopment.html)도 테스트 목록과 작은 반복, 리팩토링을 핵심으로 정리합니다. 아래는 이 흐름에 AI를 참여시키는 도구 독립적인 Java 예제입니다. 프롬프트는 작성 예시이며 특정 AI 제품을 사용한 대화 기록이나 생산성 측정 결과가 아닙니다.

## 구현을 보여 주기 전에 기대 동작을 정하기

예제는 재고와 요청 수량을 받아 차감 후 수량을 계산하는 순수 함수입니다. 실제 서비스의 정책이 아닌 설명용 요구사항이며, DB 갱신·예약 상태 저장·동시 요청 간 원자성은 구현하지 않습니다.

| 조건 | 기대 동작 |
| --- | --- |
| 재고 10개, 요청 3개 | 7 반환 |
| 재고 10개, 요청 10개 | 0 반환 |
| 요청이 재고보다 많거나 재고가 0인데 1개 요청 | `IllegalStateException("insufficient_stock")` |
| 재고가 음수 | `IllegalArgumentException("stock")` |
| 요청 수량이 0 이하 | `IllegalArgumentException("requested")` |
| 두 입력이 모두 잘못됨 | 재고 검증을 먼저 수행 |
| 재고 `Integer.MAX_VALUE`, 요청 1개 | `Integer.MAX_VALUE - 1` 반환 |

이 표가 테스트의 판정 기준입니다. AI가 만든 구현을 읽고 그 반환값을 기대값으로 복사하면 오류도 함께 복사할 수 있습니다. 다음처럼 요구사항과 API 계약부터 전달합니다.

```text
아직 구현하지 마.
StockPolicy.remaining(int stock, int requested)의 테스트 후보를 제안해줘.
위 요구사항 표를 근거로 입력, 기대값·예외, 근거가 되는 규칙을 연결해줘.

외부 저장소나 DB는 도입하지 않는다.
정상·경계·오류 입력을 나누고, 첫 번째 반복에서는
재고 10개에서 3개를 요청하면 7을 반환하는 테스트 하나만 작성해줘.
불명확한 정책은 추정해서 추가하지 마.
```

## Red·Green·Refactor를 작은 실행으로 연결하기

![요구사항에서 다음 테스트 하나를 선택하고 의도한 실패를 확인한 뒤 최소 구현으로 통과시키고, 테스트를 유지하며 리팩토링한 다음 다음 테스트로 돌아가는 흐름](/assets/diagrams/2026-11-02-ai-assisted-tdd-ko.svg)

그림은 AI 내부 동작이 아니라 개발자가 제어하는 작업 순서입니다. 새 동작의 실패를 확인하고 최소 구현을 추가합니다. 리팩토링 뒤에도 같은 테스트가 통과하면 다음 사례로 넘어갑니다. 실패 원인이 의존성 다운로드나 실행 환경이라면 그 문제를 해결하고 같은 단계를 다시 실행합니다.

재현 환경은 **JDK 17.0.8.1·Gradle 8.4·JUnit Jupiter 5.12.2**입니다. 재현에 사용한 고정 조합이며 운영 환경의 최신 버전 추천을 뜻하지 않습니다. 빈 작업 폴더에 아래 파일을 만듭니다. 첫 실행은 Maven Central에서 테스트 의존성을 내려받을 수 있고, 테스트 자체는 외부 API나 DB에 접속하지 않습니다. 기존 프로젝트에 적용할 때는 해당 프로젝트의 Wrapper와 의존성 관리 정책을 따릅니다.

### `settings.gradle`

```groovy
rootProject.name = 'ai-tdd-stock'
```

### `build.gradle`

```groovy
plugins { id 'java' }
repositories { mavenCentral() }
dependencies {
    testImplementation platform('org.junit:junit-bom:5.12.2')
    testImplementation 'org.junit.jupiter:junit-jupiter'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
java {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
}
test {
    useJUnitPlatform()
    testLogging { events 'passed', 'failed' }
}
```

JUnit의 `@Test`와 `assertEquals`·`assertThrows`로 반환값과 예외를 검사합니다. 예외 객체를 받아 메시지도 확인할 수 있습니다. [JUnit 5.12.2 사용자 가이드](https://docs.junit.org/5.12.2/user-guide/), [Gradle의 JVM 테스트 안내](https://docs.gradle.org/current/userguide/java_testing.html)

### 첫 테스트: `src/test/java/StockPolicyTest.java`

```java
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class StockPolicyTest {
    @Test
    void reservesPartOfStock() {
        assertEquals(7, StockPolicy.remaining(10, 3));
    }
}
```

### 첫 Red: `src/main/java/StockPolicy.java`

호출 가능한 API를 만들고, 아직 차감하지 않는 구현으로 시작합니다. 이 상태에서 테스트를 실행해 `7`을 기대했는데 `10`이 나와 실패하는지 확인합니다.

```java
public class StockPolicy {
    public static int remaining(int stock, int requested) {
        return stock;
    }
}
```

프로젝트 루트에서 다음 명령을 실행합니다. 이 단계의 테스트 실패와 비정상 종료는 의도한 결과입니다.

```sh
gradle --no-daemon --console=plain clean test
```

다운로드·컴파일 오류와 요구 동작의 실패를 구분합니다. 이번 예제에서 확인할 Red는 `reservesPartOfStock()`의 기대값 불일치입니다. 실행기를 고장 낸 상태를 기능 검증이 됐다는 증거로 기록하지 않습니다.

### 첫 Green: 같은 `StockPolicy.java` 교체

```java
public class StockPolicy {
    public static int remaining(int stock, int requested) {
        return stock - requested;
    }
}
```

같은 명령을 다시 실행하면 첫 테스트가 통과합니다. 아직 이 구현은 음수나 부족한 재고를 처리하지 않습니다. 첫 테스트의 통과를 전체 기능의 완료로 해석하지 않고 다음 요구사항을 추가합니다.

AI에게는 수정 범위를 다음처럼 전달할 수 있습니다.

```text
실패한 테스트는 reservesPartOfStock이고 expected=7, actual=10이다.
StockPolicy.java만 수정해서 이 테스트를 통과시켜줘.
테스트·기대값·빌드 설정은 바꾸지 마.
지금 요구되지 않은 DB, 인터페이스, 설정 계층은 추가하지 마.
실행한 명령과 종료 코드, 확인한 테스트 결과를 알려줘.
```

### 다음 Red: 기존 테스트 클래스 안에 메서드 추가

아래 메서드들을 `StockPolicyTest`의 마지막 닫는 중괄호 **안쪽**에 추가합니다. 실제 TDD 작업에서는 사례 하나씩 추가하며 반복합니다. 본문은 재현 파일을 간결하게 보여 주기 위해 다음 사례들을 한 블록으로 모았습니다.

```java
    @Test
    void reservesAllStock() {
        assertEquals(0, StockPolicy.remaining(10, 10));
    }

    @Test
    void rejectsInsufficientStock() {
        var error = assertThrows(IllegalStateException.class,
                () -> StockPolicy.remaining(2, 3));
        assertEquals("insufficient_stock", error.getMessage());
    }

    @Test
    void rejectsEmptyStock() {
        var error = assertThrows(IllegalStateException.class,
                () -> StockPolicy.remaining(0, 1));
        assertEquals("insufficient_stock", error.getMessage());
    }

    @Test
    void rejectsNegativeStock() {
        var error = assertThrows(IllegalArgumentException.class,
                () -> StockPolicy.remaining(-1, 1));
        assertEquals("stock", error.getMessage());
    }

    @Test
    void rejectsZeroRequest() {
        var error = assertThrows(IllegalArgumentException.class,
                () -> StockPolicy.remaining(10, 0));
        assertEquals("requested", error.getMessage());
    }

    @Test
    void rejectsNegativeRequest() {
        var error = assertThrows(IllegalArgumentException.class,
                () -> StockPolicy.remaining(10, -1));
        assertEquals("requested", error.getMessage());
    }

    @Test
    void validatesStockBeforeRequest() {
        var error = assertThrows(IllegalArgumentException.class,
                () -> StockPolicy.remaining(-1, 0));
        assertEquals("stock", error.getMessage());
    }

    @Test
    void supportsMaximumStock() {
        assertEquals(Integer.MAX_VALUE - 1,
                StockPolicy.remaining(Integer.MAX_VALUE, 1));
    }
```

이 추가 블록을 함께 실행하면 첫 Green 구현에서 9건 중 6건이 실패합니다.

### 추가 사례의 Green: `StockPolicy.java` 교체

```java
public class StockPolicy {
    public static int remaining(int stock, int requested) {
        if (stock >= 0) {
            if (requested > 0) {
                if (requested <= stock) {
                    return stock - requested;
                }
                throw new IllegalStateException("insufficient_stock");
            }
            throw new IllegalArgumentException("requested");
        }
        throw new IllegalArgumentException("stock");
    }
}
```

같은 명령으로 전체 9개 테스트가 통과하는지 확인합니다. 여기까지는 요구 동작을 충족하는 구현을 만들었습니다. 이어서 테스트를 유지한 채 중첩 분기를 정리합니다.

### Refactor: 같은 파일에서 조기 검증으로 정리

```java
public class StockPolicy {
    public static int remaining(int stock, int requested) {
        if (stock < 0) throw new IllegalArgumentException("stock");
        if (requested <= 0) throw new IllegalArgumentException("requested");
        if (requested > stock) throw new IllegalStateException("insufficient_stock");
        return stock - requested;
    }
}
```

검증 순서·반환값·예외를 유지하면서 중첩을 줄였습니다. 이 단계에서는 새 정책을 추가하지 않습니다. AI에 맡길 때도 보존할 동작과 실행 범위를 구체적으로 전달합니다.

```text
현재 9개 테스트가 모두 통과한다.
StockPolicy.java의 중첩 분기만 조기 검증 형태로 정리해줘.
재고 검증이 요청 수량 검증보다 먼저라는 순서,
반환값·예외 타입·메시지와 기존 테스트를 유지해줘.
수정 전후 같은 전체 테스트를 실행하고 결과와 diff를 알려줘.
```

첫 Red부터 Refactor까지 각 소스를 별도로 실행하고 JUnit XML 보고서에서 확인한 결과는 다음과 같습니다.

| 단계 | 테스트 수 | 실패 | 건너뜀 | Gradle 종료 코드 |
| --- | ---: | ---: | ---: | ---: |
| 첫 Red | 1 | 1 | 0 | 1 |
| 첫 Green | 1 | 0 | 0 | 0 |
| 추가 사례 Red | 9 | 6 | 0 | 1 |
| 추가 사례 Green | 9 | 0 | 0 | 0 |
| Refactor | 9 | 0 | 0 | 0 |

테스트 보고서는 `build/reports/tests/test/index.html`, 기계가 읽을 XML은 `build/test-results/test/`에 생성됩니다. 이 결과는 로컬 정책 함수의 동작 확인이며 AI 제품의 품질·생산성이나 운영 시스템의 정확성을 측정한 결과가 아닙니다.

## 테스트도 구현과 함께 틀릴 수 있다

재고가 음수이면서 요청도 잘못됐을 때의 **검증 우선순위**는 `validatesStockBeforeRequest()`로 고정했습니다. 이 사례가 없으면 예외 메시지 우선순위를 뒤집는 회귀를 놓칠 수 있습니다. 정상 입력의 기대값만 늘리기보다 요구사항 표에 있는 규칙이 실제로 테스트에 연결됐는지 확인해야 합니다.

테스트가 실제로 경계를 잡는지도 확인할 수 있습니다. 최종 구현에서 `requested > stock`을 `requested >= stock`으로 잘못 바꾸면 `reservesAllStock()`이 실패해야 합니다. `requested <= 0`을 `requested < 0`으로 바꾸면 `rejectsZeroRequest()`가 실패해야 합니다. 입력 검증 순서를 뒤집는 변이도 실행해 `validatesStockBeforeRequest()`의 실패를 확인했습니다. 세 변이를 실제로 실행한 결과이며, 모든 결함을 검출한다는 보장은 아닙니다.

AI에게 재검사를 맡길 때는 구현의 설명보다 원래 요구사항을 다시 제공하고, 각 테스트가 어떤 규칙을 검증하는지 대조하게 합니다. 다른 에이전트를 쓰더라도 같은 잘못된 요구사항을 공유하면 같은 오류를 반복할 수 있습니다. 역할을 나누는 것과 기대 동작의 근거를 독립적으로 확인하는 것은 구분해야 합니다.

```text
원래 요구사항 표와 현재 테스트를 대조해줘.
아직 테스트·구현을 수정하지 마.
검증된 규칙, 빠진 규칙, 경계값, 관찰하지 못한 조건을 구분해줘.
테스트가 현재 구현의 결과를 그대로 기대값으로 복사했는지도 확인해줘.
필요한 수정은 먼저 규칙과 근거를 연결해서 제안해줘.
```

## AI가 통과를 만들기 위해 검증을 약하게 바꾸지 않도록 하기

실패한 테스트를 삭제하거나 `@Disabled`로 건너뛰고, 기대값을 잘못된 구현에 맞추거나 예외를 모두 삼키면 초록색 결과가 나와도 요구사항은 충족되지 않습니다. 요구사항이 유지되는 리팩토링에서는 기대 동작도 보존합니다. 테스트 자체에 오류가 있다면 정책·근거를 확인해 그 수정과 구현 수정을 명확히 구분합니다. [GitHub의 AI 생성 코드 검토 안내](https://docs.github.com/en/copilot/tutorials/review-ai-generated-code)도 테스트 삭제·건너뜀과 요구 의도 불일치를 점검하도록 권고합니다.

AI가 설명한 ‘통과’와 실행기가 보고한 결과도 구분합니다. 실제 명령·종료 코드·JUnit 보고서와 diff를 확인하고, 테스트가 0건이거나 일부만 실행된 상태를 전체 통과로 기록하지 않습니다. CI에서는 최종 구현과 전체 테스트를 정상적인 성공 조건으로 실행합니다. 본문처럼 Red의 실패를 확인하는 교육용 실행과 일반 CI를 구분하고, 실패 명령을 무조건 무시하는 설정으로 CI를 통과시키지 않습니다.

기존 코드에 적용할 때는 먼저 현재 동작을 고정하는 테스트를 확보하고, 변경할 동작 하나를 선택합니다. 이 순서와 동작 보존 기준은 [AI 에이전트 리팩토링 글](/ko/posts/2026-10-31-ai-agent-refactoring/)과 연결됩니다. 테스트·빌드도 코드를 실행하므로 작업 폴더와 자격증명 범위는 [AI 에이전트 권한 설계](/ko/posts/2026-11-01-ai-agent-permission-boundaries/)처럼 제한합니다.

이 예제를 실제 재고 예약으로 확장한다면 동시 요청, 트랜잭션, 중복 요청과 재시도에 대한 통합 테스트가 별도로 필요합니다. 단위 함수의 9개 테스트 통과를 재고 초과 판매 방지의 근거로 사용할 수는 없습니다.
