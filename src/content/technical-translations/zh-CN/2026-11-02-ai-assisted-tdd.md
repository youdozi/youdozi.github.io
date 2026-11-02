---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2026-11-02-ai-assisted-tdd",
  "routeSlug": "2026-11-02-ai-assisted-tdd",
  "kind": "post",
  "title": "AI 辅助 TDD：用 Java 验证 Red、Green 和 Refactor",
  "description": "结合 AI 与 TDD，以需求为依据编写测试，确认预期失败，再进行最小实现和重构。运行 Java 与 JUnit 示例，检测测试弱化和边界回归。",
  "categories": [
    "architecture"
  ],
  "tags": [
    "ai-agent",
    "tdd",
    "java",
    "junit",
    "testing",
    "refactoring"
  ],
  "sourcePath": "src/content/posts/en/2026-11-02-ai-assisted-tdd.md",
  "sourceSha256": "bfc69c72419b9b2b5ce2693c4111b12dd8f935ed3d1115dd350b837bed13bf80",
  "draftSha256": "2b7e250fe0d9081a15ba231dbb0a888c385416b19134e333ac4cc4051a0552f5",
  "manifestPath": ".pipeline/technical-translations/batch-132/manifest.json",
  "manifestSha256": "9061c67686c9ea3bd8d21799f4c265ee716fee50940f1b6fc38c28a67de01dee",
  "publishedAt": "2026-11-02T03:04:44.245Z",
  "updatedAt": "2026-11-02T03:04:44.245Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 132,
    "approvedAt": "2026-11-02T03:04:44.245Z",
    "basis": "User requested completing missing multilingual technical posts, review, verification and deployment, then instructed continuing the next task on 2026-11-02, with standing blog PR merge/publication authorization. Human approval denotes user publication authorization; linguistic review is AI, not human/native review."
  }
}
---

**结合 AI 与 TDD 时，应从需求推导预期结果，观察测试失败，再反复进行小步实现和重构。** AI 可以提出测试和实现，但二者可能共享同一种误解，却仍然通过测试。应检查每项预期的依据，以及测试运行器实际报告了什么。

基本 TDD 循环从测试清单中选择下一个行为，重复 Red → Green → Refactor。[Martin Fowler 对 TDD 的说明](https://www.martinfowler.com/bliki/TestDrivenDevelopment.html)强调测试清单、小循环和重构。下面的 Java 示例将 AI 加入这个过程，但不依赖特定工具。提示词是自行编写的示例，并非 AI 产品对话实录或生产力测量。

## 在展示实现之前定义预期行为

示例是一个根据库存量和请求数量计算剩余库存的纯函数。这里的需求用于演示，不是实际服务策略。它不会更新数据库、持久化预留记录，也不提供并发请求之间的原子性。

| 条件 | 预期行为 |
| --- | --- |
| 库存 10，请求 3 | 返回 7 |
| 库存 10，请求 10 | 返回 0 |
| 请求超过库存，包括请求 1 但库存为 0 的情况 | `IllegalStateException("insufficient_stock")` |
| 库存为负数 | `IllegalArgumentException("stock")` |
| 请求数量为零或负数 | `IllegalArgumentException("requested")` |
| 两个输入都无效 | 先验证库存 |
| 库存为 `Integer.MAX_VALUE`，请求 1 | 返回 `Integer.MAX_VALUE - 1` |

这张表就是测试判定依据。阅读 AI 生成的实现，再将其返回值复制到断言中，也可能复制它的缺陷。应从需求和 API 契约出发：

```text
暂时不要实现任何内容。
为 StockPolicy.remaining(int stock, int requested) 提出测试用例。
将每项输入、预期结果或异常与需求表中的规则关联起来。

不要引入外部存储或数据库。
区分正常、边界和无效输入。第一轮只编写一个测试：
请求 3，从库存 10 中扣除后返回 7。
需求不明确的地方，不要自行编造策略。
```

## 通过小步执行连接 Red、Green 和 Refactor

![从需求中选择下一个测试，验证其预期失败，以最小实现使其通过，在保留测试的情况下重构，再返回下一个测试](/assets/diagrams/technical/zh-CN-2026-11-02-ai-assisted-tdd.svg)

图中描述的是开发者控制的工作流，而非 AI 内部机制。先观察新增行为失败，再补充最小实现。重构后重新运行相同测试，再选择下一个用例。如果失败源于依赖下载或执行环境，应先修复该问题，再重新运行同一阶段。

复现环境为 **JDK 17.0.8.1、Gradle 8.4 和 JUnit Jupiter 5.12.2**。这一固定组合用于记录实际使用的环境，并非当前生产版本推荐。在空目录中创建以下文件。首次运行可能从 Maven Central 下载测试依赖；测试本身不会调用任何外部 API 或数据库。在已有项目中，应遵循其 Gradle Wrapper 和依赖管理策略。

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

JUnit 的 `@Test`、`assertEquals` 和 `assertThrows` 用于检查返回值与异常。还应捕获异常对象，检查其消息。参阅 [JUnit 5.12.2 用户指南](https://docs.junit.org/5.12.2/user-guide/)和 [Gradle JVM 测试指南](https://docs.gradle.org/current/userguide/java_testing.html)。

### 第一个测试：`src/test/java/StockPolicyTest.java`

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

### 首次 Red：`src/main/java/StockPolicy.java`

创建一个可调用 API，但实现暂时不执行减法。运行测试，确认它因为预期 `7` 却得到 `10` 而失败。

```java
public class StockPolicy {
    public static int remaining(int stock, int requested) {
        return stock;
    }
}
```

在项目根目录运行此命令。此阶段预期出现测试失败和非零退出码。

```sh
gradle --no-daemon --console=plain clean test
```

应将下载或编译错误与所需行为的失败区分开。这里预期的 Red 是 `reservesPartOfStock()` 中的断言不匹配。运行器损坏，不能证明已测试该行为。

### 首次 Green：替换同一个 `StockPolicy.java`

```java
public class StockPolicy {
    public static int remaining(int stock, int requested) {
        return stock - requested;
    }
}
```

重新运行同一命令，第一个测试会通过。此实现仍未处理负数输入或库存不足。第一个测试通过并不代表功能完成；应添加下一项需求。

可以向 AI 提供以下变更边界：

```text
失败测试为 reservesPartOfStock：expected=7, actual=10。
仅修改 StockPolicy.java，让此测试通过。
不要修改测试、预期值或构建设置。
不要添加未要求的数据库、接口或配置层。
报告你实际检查的命令、退出码和测试结果。
```

### 下一次 Red：在现有测试类中添加方法

将这些方法添加到 `StockPolicyTest` 最后一个右花括号**内部**。实际 TDD 应一次添加一个用例并重复循环。本文将其余用例集中在一个代码块中，以保持复现文件简洁。

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

使用首次 Green 的实现运行这些新增用例，会产生 6 个失败，共运行 9 个测试。

### 新增用例的 Green：替换 `StockPolicy.java`

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

用相同命令验证全部 9 个测试通过。该实现现在满足规定的行为。接下来，在保留测试的同时简化嵌套分支。

### Refactor：在同一个文件中使用卫语句

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

嵌套层数减少，同时保留验证顺序、返回值和异常。此阶段不要引入新策略。要求 AI 重构时，应说明需要保留的行为与执行范围：

```text
当前全部 9 个测试都通过。
仅将 StockPolicy.java 中的嵌套分支替换为卫语句。
保留先验证 stock、再验证请求数量的顺序，
以及返回值、异常类型、消息和现有测试。
变更前后都运行同一套完整测试，
并报告结果与差异。
```

从首次 Red 到 Refactor，每个源代码版本都分别执行过。以下结果来自 JUnit XML 报告：

| 阶段 | 测试数 | 失败数 | 跳过数 | Gradle 退出码 |
| --- | ---: | ---: | ---: | ---: |
| 首次 Red | 1 | 1 | 0 | 1 |
| 首次 Green | 1 | 0 | 0 | 0 |
| 新增用例 Red | 9 | 6 | 0 | 1 |
| 新增用例 Green | 9 | 0 | 0 | 0 |
| Refactor | 9 | 0 | 0 | 0 |

HTML 报告生成于 `build/reports/tests/test/index.html`；机器可读 XML 位于 `build/test-results/test/`。这些结果验证的是本地策略函数，并不衡量 AI 产品质量、生产力或生产系统的正确性。

## 测试与实现可能一起出错

库存无效且请求也无效时的**验证优先级**，由 `validatesStockBeforeRequest()` 固定。缺少这个用例，颠倒异常消息优先级的回归可能不会被发现。不要只是增加更多正常输入示例，应检查需求表中的规则是否都有对应测试。

也可以检查测试能否检测边界回归。在最终实现中，错误地将 `requested > stock` 改为 `requested >= stock`，应使 `reservesAllStock()` 失败。将 `requested <= 0` 改为 `requested < 0`，应使 `rejectsZeroRequest()` 失败。还实际执行了颠倒输入验证顺序的变异，并使 `validatesStockBeforeRequest()` 失败。这三项变异都实际运行过，但不保证检测到所有缺陷。

进行 AI 辅助审查时，应再次提供原始需求，询问每个测试检查哪条规则。如果另一个智能体也使用相同的错误需求，它可能重复同样的错误。分离角色与独立确立预期行为，是不同的问题。

```text
将原始需求表与当前测试进行对照。
暂时不要修改测试或实现。
指出已验证的规则、缺失规则、边界和未观察到的条件。
检查是否有测试只是把当前实现的输出
复制为预期结果。
提出修改前，先将每项修改与其规则和证据关联起来。
```

## 防止 AI 为了让测试通过而削弱验证

删除失败测试、用 `@Disabled` 跳过、将预期改成有缺陷实现的结果，或吞掉所有异常，都可能在不满足需求的情况下产生绿色结果。重构时需求不变，就应保留预期行为。如果测试本身有误，应先确定策略和证据，再将测试修正与实现变更区分开。[GitHub 关于审查 AI 生成代码的指南](https://docs.github.com/en/copilot/tutorials/review-ai-generated-code)也建议检查被删除或跳过的测试，以及与预期需求不符之处。

应区分 AI 声称测试通过与运行器的实际结果。检查真实命令、退出码、JUnit 报告和差异。执行了零个测试或仅运行部分测试，都不算完整通过。在 CI 中，以正常成功条件执行最终实现和完整测试套件。用于验证预期 Red 失败的教学执行框架应与普通 CI 分开，不要通过无条件忽略失败命令让 CI 通过。

对于现有代码，应先取得覆盖当前行为的测试，再选择要改变的一个行为。这个顺序及其保留标准，与 [AI 智能体重构](/en/posts/2026-10-31-ai-agent-refactoring/)相衔接。测试和构建也会执行代码，因此应按 [AI 智能体权限边界](/en/posts/2026-11-01-ai-agent-permission-boundaries/)中的说明，限制工作目录和凭证。

将本示例扩展为实际库存预留，需要为并发请求、事务、重复请求和重试单独编写集成测试。这 9 个单元函数测试通过，并不能证明能够防止超卖。
