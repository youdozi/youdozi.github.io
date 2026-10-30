---
language: "ko"
translationKey: "2026-10-31-jdk25-scopedvalue"
routeSlug: "2026-10-31-jdk25-scopedvalue"
kind: "post"
categories: ["jdk"]
tags: ["java", "jdk25", "scopedvalue", "threadlocal", "virtual-threads"]
publishedAt: "2026-10-30T16:01:02.378409+00:00"
updatedAt: "2026-10-30T16:01:02.378409+00:00"
title: "JDK 25 ScopedValue: ThreadLocal과 다른 요청 컨텍스트의 범위"
description: "JDK 25 정식 ScopedValue를 가상 스레드에서 실행합니다. 중첩 바인딩·예외 후 복원·일반 자식 스레드의 미상속을 확인하고 ThreadLocal 및 구조적 동시성과의 경계를 설명합니다."
reviewedAt: "2026-10-31"
reviewStatus: "revised"
reviewScope: "JDK 25 primary JEP/API sources; source-derived example and separate API contracts without preview. No StructuredTaskScope inheritance execution, framework integration, production rollout or performance measurement."
reviewSources: ["https://openjdk.org/jeps/506", "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/ScopedValue.html", "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/ScopedValue.Carrier.html", "https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/ThreadLocal.html", "https://openjdk.org/jeps/505"]
---
JDK 25의 **`ScopedValue`는 요청 컨텍스트처럼 호출자에서 하위 메서드로 전달하는 데이터를 실행 범위에 묶는 정식 API**입니다. [JEP 506](https://openjdk.org/jeps/506)으로 확정됐으므로 미리보기 플래그 없이 사용할 수 있습니다. 바인딩은 `run()`·`call()`이 실행하는 작업 동안 유효하며, 작업이 정상 종료하거나 예외를 던지면 이전 상태로 돌아갑니다.

## ThreadLocal과 무엇이 다른가요?

테넌트·추적 ID를 서비스 계층 깊숙이 전달하려고 모든 중간 메서드에 매개변수를 추가하기 어려울 때 사용을 검토할 수 있습니다. 값이 업무 로직의 명시적인 입력이라면 일반 매개변수로 전달하는 방식이 더 분명할 수 있습니다.

[`ThreadLocal`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/ThreadLocal.html)은 현재 스레드의 값을 `set()`으로 바꾸고 `remove()`로 지웁니다. 요청 단위로 사용할 때는 `finally`에서 정리하는 패턴이 중요합니다. `ScopedValue`는 값을 설정한 채 두는 대신, 값이 필요한 작업을 바인딩 안에서 실행합니다.

| 비교 | ThreadLocal | ScopedValue |
| --- | --- | --- |
| 값 전달 | 현재 스레드의 저장값을 읽고 변경 | 현재 동적 실행 범위의 바인딩을 읽음 |
| 범위 종료 | 요청 단위 정리를 직접 관리 | `run()`·`call()` 종료 시 이전 바인딩 복원 |
| 하위 호출의 다른 값 | `set()`으로 기존 저장값 변경 가능 | 중첩 범위로 재바인딩하고 종료 시 외부 값 복원 |
| 적합한 용도 | 변경 가능한 스레드별 상태 등 | 호출자에서 하위 호출로 전달하는 요청 컨텍스트 등 |

`ScopedValue`는 `ThreadLocal`의 모든 용도를 대체하거나 폐기하는 API가 아닙니다. `private static final` 필드는 **값 자체가 아니라 접근 키**를 보관합니다. 같은 키라도 실행 중인 스레드와 범위에 따라 읽는 값이 달라집니다.

## 가상 스레드에서 범위와 복원을 확인하기

![가상 스레드에서 외부 값을 바인딩하고 중첩·예외 후 복원, 일반 자식 스레드의 미상속과 범위 종료를 확인](/assets/diagrams/2026-10-31-jdk25-scopedvalue-ko.svg)

그림은 아래 예제의 순서입니다. 외부 테넌트는 `tenant-a`, 중첩 범위에서는 `tenant-b`를 읽습니다. 실패하는 중첩 범위는 예외를 외부에서 처리한 뒤 복원을 확인합니다. 이 예제는 HTTP 서버나 프레임워크 연동 없이 요청 컨텍스트의 전달 의미만 보여줍니다.

JDK 25의 `javac`와 `java`가 같은 설치를 가리키는 디렉터리에서 실행합니다. 로컬 검증 환경은 macOS AArch64의 Eclipse Temurin `25.0.5+8`입니다. `ScopedValue`는 `java.lang`에 있으므로 별도 import가 필요하지 않습니다.

### `ScopedContextExample.java`

```java
import java.util.NoSuchElementException;
import java.util.concurrent.Executors;

public class ScopedContextExample {
    private static final ScopedValue<RequestContext> CONTEXT = ScopedValue.newInstance();
    record RequestContext(String tenant, String traceId) {}

    public static void main(String[] args) throws Exception {
        try (var tasks = Executors.newVirtualThreadPerTaskExecutor()) {
            tasks.submit(ScopedContextExample::handleRequest).get();
        }
    }

    private static String handleRequest() throws InterruptedException {
        System.out.println("virtual=" + Thread.currentThread().isVirtual());
        System.out.println("before=" + CONTEXT.isBound());
        String result = ScopedValue.where(CONTEXT,
                new RequestContext("tenant-a", "trace-123")).call(() -> {
            System.out.println("outer=" + service());
            ScopedValue.where(CONTEXT,
                    new RequestContext("tenant-b", "trace-123")).run(() ->
                System.out.println("nested=" + service()));
            System.out.println("restored=" + service());

            try {
                ScopedValue.where(CONTEXT,
                        new RequestContext("tenant-fail", "trace-123")).run(() -> {
                    throw new IllegalStateException("demonstration");
                });
            } catch (IllegalStateException expected) {
                System.out.println("after-failure=" + service());
            }

            Thread child = Thread.ofVirtual().start(() ->
                System.out.println("plain-child-bound=" + CONTEXT.isBound()));
            child.join();
            return service();
        });
        System.out.println("result=" + result);
        System.out.println("after=" + CONTEXT.isBound());
        try {
            CONTEXT.get();
        } catch (NoSuchElementException expected) {
            System.out.println("outside=" + expected.getClass().getSimpleName());
        }
        return result;
    }

    private static String service() {
        RequestContext context = CONTEXT.get();
        return context.tenant() + "/" + context.traceId();
    }
}
```

```sh
javac --release 25 ScopedContextExample.java
java ScopedContextExample
```

미리보기 옵션 없이 확인한 표준 출력입니다. `Future.get()`으로 작업의 실패를 호출자에게 전달하고, `join()`으로 자식 스레드의 출력을 기다립니다.

```text
virtual=true
before=false
outer=tenant-a/trace-123
nested=tenant-b/trace-123
restored=tenant-a/trace-123
after-failure=tenant-a/trace-123
plain-child-bound=false
result=tenant-a/trace-123
after=false
outside=NoSuchElementException
```

`service()`는 컨텍스트 매개변수 없이 현재 바인딩을 읽습니다. `run()`은 반환값 없는 작업에, [`Carrier.call()`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/ScopedValue.Carrier.html#call(java.lang.ScopedValue.CallableOp))은 결과를 반환하거나 예외를 전달하는 작업에 사용합니다. `where()`로 `Carrier`를 만드는 것만으로 바인딩이 활성화되지는 않습니다.

`restored`와 `after-failure`는 모두 외부 값입니다. 외부 `call()`까지 끝나면 `isBound()`는 거짓이 되고, 바인딩 없이 `get()`하면 `NoSuchElementException`이 발생합니다. 바인딩이 풀린다고 참조 대상이 즉시 GC되거나 `AutoCloseable` 자원이 자동으로 닫히는 것은 아닙니다.

## 가상 스레드를 만들면 값도 상속되나요?

**일반 `Thread.ofVirtual().start()`는 부모의 바인딩을 자동 상속하지 않습니다.** 예제의 `plain-child-bound=false`가 그 경우입니다. `ExecutorService`·`CompletableFuture`로 작업을 넘긴다는 이유만으로 컨텍스트가 자동 전달된다고 가정해서도 안 됩니다. 예제의 첫 가상 스레드는 상속을 이용한 것이 아니라 작업 안에서 직접 값을 바인딩합니다.

[공식 상속 규칙](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/ScopedValue.html#inheritance)은 `StructuredTaskScope`를 만들 때 캡처한 바인딩을 해당 범위의 `fork()`로 시작한 자식 작업이 상속하는 구조를 설명합니다. **구조적 동시성은 JDK 25에서 별도의 미리보기 API**인 [JEP 505](https://openjdk.org/jeps/505)이며, 이 글의 코드는 사용하지 않습니다. 위 예제에 그 상속 검증까지 포함됐다고 해석하면 안 됩니다.

## 요청 컨텍스트에 적용할 때의 경계

바인딩을 바꿀 수 없다는 말은 대상 객체가 깊은 불변이라는 뜻이 아닙니다. 예제는 문자열 두 개를 가진 레코드를 사용하지만, 변경 가능한 컬렉션을 담는다면 동시 접근을 별도로 설계해야 합니다. 키의 접근 범위도 좁게 유지합니다.

JDK 21 등의 미리보기 예제를 그대로 복사하기보다 JDK 25 API를 확인합니다. 특히 JDK 25의 `orElse(null)`은 허용되지 않습니다. `null` 값이 바인딩된 상태와 바인딩이 없는 상태도 서로 다릅니다.

먼저 기존 `ThreadLocal`이 요청 데이터를 아래로 전달하는 용도인지, 작업 중 변경하는 상태인지 구분합니다. 전자라면 요청 진입점의 바인딩과 비동기 경계를 함께 설계합니다. 프레임워크의 트랜잭션·MDC·보안 컨텍스트가 자동 연결되는 것은 아니며, 이 예제는 그런 통합이나 성능을 검증하지 않았습니다. 가상 스레드 자체의 동작은 [JDK 21 기능 글](/ko/posts/2023-09-20-jdk-21-release/)에서 이어 볼 수 있습니다.
