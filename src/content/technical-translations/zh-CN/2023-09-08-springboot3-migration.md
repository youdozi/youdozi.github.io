---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2023-09-08-springboot3-migration",
  "routeSlug": "2023-09-08-springboot3-migration",
  "kind": "post",
  "title": "Spring Boot 3 迁移：Java 17、Jakarta 与验证步骤",
  "description": "从 Java 17、Jakarta 依赖和运行时测试开始 Spring Boot 2.7 到 3.0 的迁移。区分历史版本边界与当前生产选型。",
  "categories": [
    "springboot"
  ],
  "tags": [
    "springboot",
    "springboot3",
    "springboot3 migration"
  ],
  "sourcePath": "src/content/posts/en/2023-09-08-springboot3-migration.md",
  "sourceSha256": "4939fec22f416da9344b529b0e428c91a700920a27c10fdba00bdfd32e8a53a7",
  "draftSha256": "303ede0f7b2375c8b4dca43138a6781bf402f1b9c571ac1adc00c9abb3c216d8",
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

从 Spring Boot 2.7 迁移到 3.0 时，先建立可工作的 2.7 基线，再检查 Java 17 要求、Java EE 到 Jakarta 的命名空间变化以及库和运行时兼容性。[官方 3.0 迁移指南](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.0-Migration-Guide)说明了此顺序。仅编译通过不能证明数据库映射、授权或配置正确。

本文是 **2.7 到 3.0 的迁移指南**，保留了最初的 2023 年主题，并非建议现在部署 Boot 3.0。实际升级时应选择受支持的目标版本，并遵循中间各版本的迁移指南。

## 处理流程

![Boot 3 迁移检查流程](/assets/diagrams/technical/zh-CN-2023-09-08-springboot3-migration.svg)

这是本文建议的迁移检查顺序。这些命令检查环境，不会自动迁移应用或数据库。

## 1. 建立可工作的 2.7 基线

尝试主版本迁移前，先将较旧的 2.x 应用升级至最新 2.7.x。保存通过的测试结果，记录 wrapper、构建 JVM 和依赖。已有 wrapper 的 Gradle 项目可从以下命令开始：

```sh
java -version
./gradlew --version
./gradlew clean test
./gradlew dependencies --configuration runtimeClasspath
```

升级后执行同样的检查。多项目构建中，应对应用模块运行依赖报告，例如 `./gradlew :app:dependencies --configuration runtimeClasspath`。模块名称必须与实际项目一致。

有用的基线应覆盖持久化、身份认证、序列化、定时作业和出站 HTTP 调用。对于最后一项边界，[使用本地 MockWebServer 的 WebClient 测试](/en/posts/2023-09-19-springboot-test-webclient/)提供了可复现的起点。

## 2. 同时修改 Java EE 导入与依赖

Boot 3.0 要求 Java 17 和 Spring Framework 6。`javax.persistence`、`javax.servlet` 等 Java EE 包改为 `jakarta.persistence`、`jakarta.servlet`。`javax.sql`、`javax.crypto` 等 Java SE 包保持原名。

| 现有用法 | 迁移动作 |
| --- | --- |
| `javax.persistence.Entity` | 使用 `jakarta.persistence.Entity` 和兼容的 JPA 依赖。 |
| `javax.servlet.Filter` | 使用 `jakarta.servlet.Filter` 和兼容的 servlet 依赖。 |
| `javax.sql.DataSource` | 保留 Java SE 包名。 |
| `javax.crypto.Cipher` | 保留 Java SE 包名。 |

除导入外，还应检查解析后的依赖图。例如 `./gradlew dependencyInsight --dependency javax.servlet-api --configuration runtimeClasspath` 可定位旧 servlet 制品。报告为空并不证明整个应用已迁移：还需检查实际使用的其他库和配置。参见 [Gradle 依赖报告](https://docs.gradle.org/current/userguide/viewing_debugging_dependencies.html)。

对于 Querydsl JPA，应[对齐 JPA 与注解处理器制品](/en/posts/2023-09-09-springboot3-querydsl/)，并按该制品分支要求选择 Jakarta 变体。确认注解处理生成预期 Q 类型，且代表性查询可执行。Gradle 的 `configureEach` 控制任务配置，无法将不兼容的 Java EE 依赖转换为 Jakarta 依赖。

## 3. 检查更名的属性与授权行为

对 Boot 管理依赖的 Gradle 项目，官方迁移指南提供临时属性辅助工具：

```groovy
dependencies {
    runtimeOnly 'org.springframework.boot:spring-boot-properties-migrator'
}
```

在测试环境启动应用，阅读启动诊断并更新受影响属性。迁移完成后移除此工具。它不能替代阅读目标版本的配置变化。

Boot 3.0 还使用 Spring Security 6。迁移指南建议先过渡到 Spring Security 5.8（在 Boot 2.7 上），再迁移到 6.0。测试允许、拒绝和未认证请求，以及 servlet 应用实际使用的 error/forward 分派；不要以启动成功替代授权测试。

## 4. 将虚拟线程作为独立变更

Boot 的虚拟线程设置在 **Boot 3.2 和 JDK 21** 中引入，并非 Boot 3.0 功能：

```properties
spring.threads.virtual.enabled=true
```

这是历史版本边界，并非建议现在选择 Boot 3.2。先确认命名空间与依赖迁移正常，再结合所选版本、连接池和线程局部变量假设评估虚拟线程。仅设置此项不能证明性能提升。[Spring 的 Boot 3.2 说明](https://spring.io/blog/2023/09/09/all-together-now-spring-boot-3-2-graalvm-native-images-java-21-and-virtual)。

JDK 语言预览功能也有独立的版本约束。[String Templates 兼容性示例](/en/posts/2023-09-23-jdk-21-string-templates/)说明了为何开启预览标志并非通用升级修复方法。

<span id="decide-whether-the-application-is-ready"></span>

## 如何判断迁移已就绪？

| 检查 | 应收集的证据 |
| --- | --- |
| 构建与生成代码 | Wrapper 构建通过、预期 Q 类型和解析后的依赖版本。 |
| 运行时行为 | 持久化、身份认证和代表性 HTTP 测试通过。 |
| 配置 | 属性已更新，不再需要迁移辅助工具。 |
| 部署 | 部署制品在代表性环境中通过检查。 |

这些命令是针对项目的诊断步骤，并非已在您的应用上执行迁移的结果。保留升级前的制品和配置以便回滚。主版本迁移有助于维护，但安全性仍取决于实际部署的确切版本和配置。
