---
"language": "en"
"translationKey": "2026-11-02-ai-assisted-tdd"
"routeSlug": "2026-11-02-ai-assisted-tdd"
"title": "AI-Assisted TDD: Verify Red, Green and Refactor with Java"
"description": "Combine AI and TDD using requirements-based tests, intended
  failures, minimal implementations and refactoring. Run Java and JUnit examples
  that detect weakened tests and boundary regressions."
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
"reviewScope": "Primary sources checked; bilingual self-review, executed
  Red/Green/Refactor stages, 9 final JUnit tests and 3 targeted regression
  mutations. No AI product trial, integration or performance test."
"reviewSources":
  - "https://www.martinfowler.com/bliki/TestDrivenDevelopment.html"
  - "https://docs.junit.org/5.12.2/user-guide/"
  - "https://docs.gradle.org/current/userguide/java_testing.html"
  - "https://docs.github.com/en/copilot/tutorials/review-ai-generated-code"
---

**When combining AI with TDD, derive expected results from requirements, observe a failing test, then repeat small implementation and refactoring steps.** AI can suggest tests and implementations, but both can pass while sharing the same misunderstanding. Check where each expectation comes from and what the test runner actually reports.

The basic TDD cycle selects one next behavior from a test list and repeats Red → Green → Refactor. [Martin Fowler's explanation of TDD](https://www.martinfowler.com/bliki/TestDrivenDevelopment.html) emphasizes the test list, small cycles and refactoring. The Java example below adds AI to this process without depending on a particular tool. The prompts are authored examples, not a transcript from an AI product or a productivity measurement.

## Define expected behavior before showing an implementation

The example is a pure function that calculates remaining stock from stock and requested quantities. These are illustrative requirements, rather than an actual service policy. It does not update a database, persist reservations or provide atomicity across concurrent requests.

| Condition | Expected behavior |
| --- | --- |
| Stock 10, requested 3 | Return 7 |
| Stock 10, requested 10 | Return 0 |
| Request exceeds stock, including requesting 1 with stock 0 | `IllegalStateException("insufficient_stock")` |
| Negative stock | `IllegalArgumentException("stock")` |
| Requested quantity is zero or negative | `IllegalArgumentException("requested")` |
| Both inputs are invalid | Validate stock first |
| Stock `Integer.MAX_VALUE`, requested 1 | Return `Integer.MAX_VALUE - 1` |

This table is the test oracle. Reading an AI-generated implementation and copying its return value into an assertion can copy its bug too. Start with the requirements and API contract:

```text
Do not implement anything yet.
Suggest test cases for StockPolicy.remaining(int stock, int requested).
Connect each input, expected result or exception to a rule in the requirements table.

Do not introduce external storage or a database.
Separate normal, boundary and invalid inputs. In the first iteration,
write only one test: requesting 3 from stock 10 returns 7.
Do not invent policies where the requirements are unclear.
```

## Connect Red, Green and Refactor through small executions

![Choose one next test from the requirements, verify its intended failure, pass it with a minimal implementation, refactor while preserving tests, and return to the next test](/assets/diagrams/2026-11-02-ai-assisted-tdd-en.svg)

The diagram describes a workflow controlled by the developer, rather than AI internals. Observe the new behavior failing, then add a minimal implementation. After refactoring, rerun the same tests before selecting another case. If dependency downloads or the execution environment caused the failure, fix that issue and rerun the same stage.

The reproduction environment is **JDK 17.0.8.1, Gradle 8.4 and JUnit Jupiter 5.12.2**. This fixed combination records the environment used; it is not a recommendation of current production versions. Create the following files in an empty directory. The first run may download test dependencies from Maven Central; the tests themselves call no external API or database. In an existing project, follow its Gradle Wrapper and dependency-management policies.

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

JUnit's `@Test`, `assertEquals` and `assertThrows` check return values and exceptions. Capture the exception object to check its message too. See the [JUnit 5.12.2 user guide](https://docs.junit.org/5.12.2/user-guide/) and [Gradle's JVM testing guide](https://docs.gradle.org/current/userguide/java_testing.html).

### First test: `src/test/java/StockPolicyTest.java`

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

### First Red: `src/main/java/StockPolicy.java`

Create a callable API with an implementation that does not subtract anything yet. Run the test and verify that it fails because it expected `7` but received `10`.

```java
public class StockPolicy {
    public static int remaining(int stock, int requested) {
        return stock;
    }
}
```

Run this command from the project root. A test failure and nonzero exit are expected at this stage.

```sh
gradle --no-daemon --console=plain clean test
```

Distinguish download or compilation errors from a failure of the required behavior. The intended Red here is the assertion mismatch in `reservesPartOfStock()`. A broken runner is not evidence that the behavior was tested.

### First Green: replace the same `StockPolicy.java`

```java
public class StockPolicy {
    public static int remaining(int stock, int requested) {
        return stock - requested;
    }
}
```

Rerunning the same command passes the first test. This implementation still does not handle negative inputs or insufficient stock. Passing the first test does not complete the feature; add the next requirement.

You can give AI the following change boundary:

```text
The failing test is reservesPartOfStock: expected=7, actual=10.
Change only StockPolicy.java to pass this test.
Do not change tests, expected values or build settings.
Do not add an unrequested database, interface or configuration layer.
Report the command, exit code and test results you actually checked.
```

### Next Red: add methods inside the existing test class

Add these methods **inside** the final closing brace of `StockPolicyTest`. In actual TDD, add one case at a time and repeat the cycle. The article groups the remaining cases into one block to keep the reproduction files concise.

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

Running this additional block with the first Green implementation produces 6 failures out of 9 tests.

### Green for the additional cases: replace `StockPolicy.java`

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

Use the same command to verify that all 9 tests pass. This implementation now satisfies the specified behaviors. Next, simplify the nested branches while preserving the tests.

### Refactor: use guard clauses in the same file

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

The nesting is reduced while preserving validation order, return values and exceptions. Do not introduce a new policy during this stage. When asking AI to refactor, specify the behavior to preserve and the execution scope:

```text
All 9 tests currently pass.
Replace only the nested branches in StockPolicy.java with guard clauses.
Preserve stock validation before requested-quantity validation,
return values, exception types, messages and existing tests.
Run the same complete test suite before and after the change,
and report the results and diff.
```

Each source version from the first Red through Refactor was executed separately. The following results were read from JUnit XML reports:

| Stage | Tests | Failures | Skipped | Gradle exit code |
| --- | ---: | ---: | ---: | ---: |
| First Red | 1 | 1 | 0 | 1 |
| First Green | 1 | 0 | 0 | 0 |
| Additional cases Red | 9 | 6 | 0 | 1 |
| Additional cases Green | 9 | 0 | 0 | 0 |
| Refactor | 9 | 0 | 0 | 0 |

The HTML report is generated at `build/reports/tests/test/index.html`; machine-readable XML is under `build/test-results/test/`. These results verify a local policy function. They do not measure AI product quality, productivity or production-system correctness.

## Tests and implementations can be wrong together

The **validation precedence** for invalid stock combined with an invalid request is fixed by `validatesStockBeforeRequest()`. Without this case, a regression that reverses exception-message precedence could go unnoticed. Rather than merely adding more normal-input examples, check that the rules in the requirements table have corresponding tests.

You can also check that the tests detect boundary regressions. Incorrectly changing `requested > stock` to `requested >= stock` in the final implementation should fail `reservesAllStock()`. Changing `requested <= 0` to `requested < 0` should fail `rejectsZeroRequest()`. A mutation reversing input-validation order was also executed and failed `validatesStockBeforeRequest()`. All three mutations were actually run; this does not guarantee detection of every defect.

For an AI-assisted review, provide the original requirements again and ask which rule each test checks. Another agent can repeat the same mistake if it shares the same incorrect requirements. Separating roles and independently establishing the expected behavior are different concerns.

```text
Compare the original requirements table with the current tests.
Do not modify tests or implementation yet.
Identify verified rules, missing rules, boundaries and unobserved conditions.
Check whether any test simply copied the current implementation's output
as its expected result.
For proposed changes, first connect each change to its rule and evidence.
```

## Keep AI from weakening verification just to make tests pass

Deleting a failing test, skipping it with `@Disabled`, adjusting expectations to a faulty implementation or swallowing every exception can produce a green result without satisfying requirements. When requirements stay the same during refactoring, preserve expected behavior. If a test itself is wrong, establish the policy and evidence, then distinguish that correction from an implementation change. [GitHub's guidance on reviewing AI-generated code](https://docs.github.com/en/copilot/tutorials/review-ai-generated-code) also recommends checking for deleted or skipped tests and mismatches with the intended requirements.

Distinguish an AI's claim that tests passed from the runner's results. Inspect the actual command, exit code, JUnit reports and diff. Zero executed tests or a partial run is not a complete pass. In CI, execute the final implementation and complete test suite with ordinary success conditions. Keep the educational harness that verifies expected Red failures separate from normal CI, and do not make CI pass by unconditionally ignoring failing commands.

For existing code, first obtain tests that capture current behavior, then select one behavior to change. This sequence and its preservation criteria connect to [AI agent refactoring](/en/posts/2026-10-31-ai-agent-refactoring/). Tests and builds execute code too, so limit working directories and credentials as described in [AI agent permission boundaries](/en/posts/2026-11-01-ai-agent-permission-boundaries/).

Extending this example into actual stock reservations requires separate integration tests for concurrent requests, transactions, duplicate requests and retries. Passing these 9 unit-function tests does not establish protection against overselling.
