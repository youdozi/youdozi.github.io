---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2023-09-09-springboot3-querydsl",
  "routeSlug": "2023-09-09-springboot3-querydsl",
  "kind": "post",
  "title": "Spring Boot 3 与 Querydsl：Jakarta 配置和 Q 类型生成",
  "description": "对齐 Jakarta 依赖并配置注解处理，在 Spring Boot 3 上生成 Querydsl Q 类型，再用干净构建和 H2 查询测试验证。",
  "categories": [
    "springboot"
  ],
  "tags": [
    "springboot",
    "springboot3",
    "querydsl"
  ],
  "sourcePath": "src/content/posts/en/2023-09-09-springboot3-querydsl.md",
  "sourceSha256": "17f0353d5a048f80291207543b7abbb29e1d987ab0435009b82a4e1c16a7d953",
  "draftSha256": "8e22d456d887cbe38c99d10ec298903dacdd7eaecd1f4aadc278b08d6f157339",
  "manifestPath": ".pipeline/technical-translations/batch-125/manifest.json",
  "manifestSha256": "1934910c02dbe893b786124f1d296d7adf9efbe921d40b3d2cfbceb8f70b4b33",
  "publishedAt": "2026-10-31T15:35:43.034Z",
  "updatedAt": "2026-10-31T15:35:43.034Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 125,
    "approvedAt": "2026-10-31T15:35:43.034Z",
    "basis": "User explicitly requested applying all missing technical-post languages, review, verification and deployment on 2026-11-01, with standing PR merge authorization. Human approval denotes publication authorization; linguistic review is performed by AI, not human/native review."
  }
}
---

在 Spring Boot 3 上生成 Querydsl JPA 的 Q 类型时，应对齐 `querydsl-jpa` 和 `querydsl-apt` 的版本及 `jakarta` 分类器，配置注解处理，再检查干净构建与数据库查询测试。Querydsl [5.0 发布说明](https://github.com/querydsl/querydsl/releases/tag/QUERYDSL_5_0_0)记录了 Jakarta 分类器支持。保留 Gradle 默认的生成源码路径，可避免主代码和测试编译写入同一目录。

本指南将最初的 2023 年韩文示例扩展为可运行配置。以下版本用于固定复现环境，并非当前生产依赖的推荐版本。

## 处理流程

![生成 Q 类型并执行查询的流程](/assets/diagrams/technical/zh-CN-2023-09-09-springboot3-querydsl.svg)

处理器在主代码编译时生成 QEmployee。随后 H2 测试使用生成的类型执行查询。

## 复现环境与完整 Gradle 配置

| 组件 | 复现版本 |
| --- | --- |
| JDK / Gradle | 17.0.8.1 / 8.4 |
| Spring Boot BOM | 3.5.7 |
| Querydsl JPA / APT | 5.1.0，均使用 `jakarta` 分类器 |
| Hibernate / H2 | 6.6.33.Final / 2.3.232，由 BOM 管理 |

在新目录创建这五个文件。测试项目使用 Java 插件和 Boot BOM，不需要 Boot Gradle 插件。对于现有 Boot 应用，只在已有依赖管理基础上添加所需依赖。

### `settings.gradle`

```groovy
rootProject.name = 'querydsl-jakarta-example'
```

### `build.gradle`

```groovy
plugins { id 'java' }
repositories { mavenCentral() }
dependencies {
    implementation platform('org.springframework.boot:spring-boot-dependencies:3.5.7')
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    implementation 'com.querydsl:querydsl-jpa:5.1.0:jakarta'

    annotationProcessor platform('org.springframework.boot:spring-boot-dependencies:3.5.7')
    annotationProcessor 'com.querydsl:querydsl-apt:5.1.0:jakarta'
    annotationProcessor 'jakarta.persistence:jakarta.persistence-api'
    annotationProcessor 'jakarta.annotation:jakarta.annotation-api'

    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testRuntimeOnly 'com.h2database:h2'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
test { useJUnitPlatform() }
```

Gradle 单独解析 `annotationProcessor`，与普通编译和运行时类路径分开。因此示例也将 BOM 应用于处理器配置，并显式提供 Jakarta Persistence 和 Annotation API。`implementation` 上的依赖不会自动对处理器可用。参见 [Gradle Java 插件文档](https://docs.gradle.org/current/userguide/java_plugin.html)。

## 创建应用与实体

应用类让 JPA 测试能够发现 Boot 配置。测试无需另行启动服务进程。

### `src/main/java/example/Application.java`

```java
package example;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

### `src/main/java/example/Employee.java`

```java
package example;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;

@Entity
public class Employee {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;

    public String getName() { return name; }

    protected Employee() {}

    public Employee(String name) {
        this.name = name;
    }
}
```

`Employee` 使用 `jakarta.persistence`。不要手写 `QEmployee`：注解处理器会生成下面测试引用的类型。

## 通过生成的 Q 类型查询

### `src/test/java/example/EmployeeQueryTest.java`

```java
package example;

import com.querydsl.jpa.impl.JPAQueryFactory;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.boot.test.autoconfigure.orm.jpa.TestEntityManager;

import static org.assertj.core.api.Assertions.assertThat;

@DataJpaTest
class EmployeeQueryTest {
    @Autowired
    private TestEntityManager entityManager;

    @Test
    void findsEmployeeByName() {
        entityManager.persistAndFlush(new Employee("Alice"));
        entityManager.persistAndFlush(new Employee("Bob"));
        QEmployee employee = QEmployee.employee;
        var names = new JPAQueryFactory(entityManager.getEntityManager())
            .select(employee.name).from(employee)
            .where(employee.name.eq("Alice")).fetch();
        assertThat(names).containsExactly("Alice");
    }

    @Test
    void returnsNoRowsForMissingName() {
        entityManager.persistAndFlush(new Employee("Alice"));
        QEmployee employee = QEmployee.employee;
        var names = new JPAQueryFactory(entityManager.getEntityManager())
            .select(employee.name).from(employee)
            .where(employee.name.eq("Missing")).fetch();
        assertThat(names).isEmpty();
    }
}
```

`@DataJpaTest` 使用此示例类路径中的 H2。每项测试在事务中运行，结束后回滚。用 `persistAndFlush` 插入数据后，生成的 `QEmployee` 支持两项检查：名称精确匹配和查询无结果。参见 [Spring Boot JPA 测试指南](https://docs.spring.io/spring-boot/3.5/reference/testing/spring-boot-applications.html#testing.spring-boot-applications.autoconfigured-spring-data-jpa-tests)。

这些测试仅检查 H2 上的此实体和查询，不验证生产数据库的 SQL 方言、排序规则、锁定或迁移行为。

## 运行并检查生成文件

选中 JDK 17 并使用已安装的 Gradle 8.4。在项目根目录运行：

```sh
java -version
gradle --version
gradle --no-daemon clean test
```

检查以下生成产物与测试报告：

```text
build/generated/sources/annotationProcessor/java/main/example/QEmployee.java
build/classes/java/main/example/QEmployee.class
build/reports/tests/test/index.html
```

两项测试均在此配置下通过。再次执行 `clean test` 后重新生成了 Q 类型，两项测试再次通过。现有项目有 Gradle wrapper 时，通过 `./gradlew clean test` 使用其选定版本。

此示例生成的 Q 类型导入 `javax.annotation.processing.Generated`，这是 Java SE 的 `java.compiler` API，无需替换为 Jakarta。[JDK 17 Generated API](https://docs.oracle.com/en/java/javase/17/docs/api/java.compiler/javax/annotation/processing/Generated.html)。

<span id="troubleshoot-missing-or-duplicate-q-types"></span>

## 为何 Q 类型缺失或重复生成？

| 症状 | 首先检查 |
| --- | --- |
| 找不到 `QEmployee` | CLI 的 `clean compileJava` 结果、处理器依赖以及实体的 `jakarta.persistence` 导入。 |
| 处理器找不到 Persistence API | 所需 Jakarta API 是否在独立于普通类路径的处理器路径上。 |
| 出现不兼容的 `javax.persistence.EntityManager` 类型 | 两个 Querydsl 制品的版本与 Jakarta 分类器是否匹配。 |
| Q 类型重复，或仅在 clean 后构建成功 | 移除手写 Q 源码与共用生成路径；检查 main/test 输出配置。 |
| CLI 通过但 IDE 看不到 Q 类型 | Gradle 同步、委托构建设置与 IDE 注解处理。 |

示例未为生成文件添加自定义 `sourceSets`、`JavaCompile` 或 `clean` 配置。如需自定义路径，保持 main 和 test 输出分离。`configureEach` 控制延迟任务配置，无法修复 Jakarta 依赖兼容性。[Gradle 配置规避](https://docs.gradle.org/current/userguide/lazy_configuration.html)。

升级的整体顺序参见 [Spring Boot 3 迁移指南](/en/posts/2023-09-08-springboot3-migration/)。出站 HTTP 边界请使用 [WebClient 和 MockWebServer 测试](/en/posts/2023-09-19-springboot-test-webclient/)。

## 更换查询工具前先比较

完整 Employee 类包含 getter，可将仓库结果转换为名称进行比较。添加 [Querydsl 与 Specification 比较](/en/posts/2023-09-05-querydsl-no-release/)中的三个文件，可在相同实体上运行另外八项检查。上述原有两项测试仍属于十项测试项目。这里比较的是部分 H2 谓词，而非全部数据库行为。[Spring Boot 指南](/en/categories/springboot/)串联周边的配置与测试步骤。
