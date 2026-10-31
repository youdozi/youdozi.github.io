---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2023-09-13-springboot-history",
  "routeSlug": "2023-09-13-springboot-history",
  "kind": "post",
  "title": "Spring Boot 发布历史与 Spring Framework 版本映射",
  "description": "回顾 Spring Boot 1.2 到 4.0 的关键版本，区分 Boot 与 Framework、Starter 和 BOM，并检查项目解析后的依赖版本。",
  "categories": [
    "springboot"
  ],
  "tags": [
    "springboot",
    "history"
  ],
  "sourcePath": "src/content/posts/en/2023-09-13-springboot-history.md",
  "sourceSha256": "8f97cfe96eb4ed1a36dae63a187c6f28960c327ff6cba276c45537a1e7745da2",
  "draftSha256": "ec52615443a2849a1ae11b8937814b498acf83d6b16a737790c7f764f0e70887",
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

Spring Boot 和 Spring Framework 是版本号不同的独立项目。Boot 在 Framework 之上增加自动配置、依赖管理和可执行打包。因此不能将 Boot 3.1 理解为 Framework 6.1；应检查所选 Boot 版本的 BOM 与解析后的依赖图。

## 处理流程

![确定实际组件版本的流程](/assets/diagrams/technical/zh-CN-2023-09-13-springboot-history.svg)

此流程概括依赖检查，并非发布时间线。Boot、Framework 和 Lombok 各有独立的版本标识和依赖配置。

## 部分正式版本的变化

此时间线突出功能转变，并未列出所有发布。应区分首次正式发布与后续补丁扩大的 JDK 兼容范围。

| Spring Boot | 首次正式发布 | 部分变化与官方公告 |
| --- | --- | --- |
| 1.2 | 2014-12-11 | [`@SpringBootApplication` 与 Servlet 3.1 支持](https://spring.io/blog/2014/12/11/spring-boot-1-2-0-released/) |
| 1.3 | 2015-11-16 | [DevTools、缓存自动配置与可直接执行的 JAR](https://spring.io/blog/2015/11/16/spring-boot-1-3-0-released/) |
| 1.4 | 2016-07-28 | [启动失败分析与改进的测试支持](https://spring.io/blog/2016/07/28/spring-boot-1-4-released/) |
| 2.0 | 2018-03-01 | [Framework 5.0、Java 8 基线与响应式 Web 支持](https://spring.io/blog/2018/03/01/spring-boot-2-0-goes-ga/) |
| 3.0 | 2022-11-24 | [Framework 6.0、Java 17 基线、Jakarta 与原生镜像](https://spring.io/blog/2022/11/24/spring-boot-3-0-goes-ga/) |
| 3.1 | 2023-05-18 | [开发期 Testcontainers 与 Docker Compose 集成](https://spring.io/blog/2023/05/18/spring-boot-3-1-0-available-now/) |
| 3.2 | 2023-11-23 | [虚拟线程、RestClient 与 JdbcClient 支持](https://spring.io/blog/2023/11/23/spring-boot-3-2-0-available-now/) |
| 4.0 | 2025-11-20 | [Framework 7、模块化、JSpecify 与 API 版本管理](https://spring.io/blog/2025/11/20/spring-boot-4-0-0-available-now/) |

例如，[Boot 3.1.0 管理的依赖列表](https://docs.spring.io/spring-boot/docs/3.1.0/reference/html/dependency-versions.html)指定 `spring-core` 6.0.9。Boot 与 Framework 的次版本号无需一致。将 Boot 2.4 映射为不存在的 Framework 5.4 分支同样错误。

## Starter、BOM 与构建插件

Starter 汇集某项功能所需的依赖。BOM 管理版本，不会自动将列表中的所有库添加到项目。Boot 构建插件提供 `bootRun` 等任务和可执行 JAR 打包。

对于 Gradle，[Boot 依赖管理指南](https://docs.spring.io/spring-boot/4.1/gradle-plugin/managing-dependencies.html)说明了依赖管理插件与原生 BOM 支持。仅应用 Boot 插件，不意味着所有 Gradle 配置都接受无版本依赖。还应检查注解处理器等独立配置。

## 检查项目实际版本

在 [Initializr](/en/posts/2023-09-07-springboot-initializer/) 与 [Lombok 指南](/en/posts/2023-09-15-springboot-intellij-lombok/)的最终项目中运行这些命令。

```sh
./gradlew dependencyInsight --configuration runtimeClasspath --dependency spring-core
./gradlew dependencyInsight --configuration annotationProcessor --dependency lombok
```

本地示例解析为 Boot 4.1.2、`spring-core` 7.0.10 和 Lombok 1.18.48。不同数字对应不同项目。`dependencyInsight` 显示选定版本及决定该版本的依赖路径或规则，适合调查冲突。这些值记录的是本例，并非未来默认值或通用项目组合。

此时间线不是当前支持生命周期表。创建或升级项目时，应单独检查所选版本的要求、依赖兼容性与支持政策。参见 [Java 17 与 Jakarta 迁移](/en/posts/2023-09-08-springboot3-migration/)以迁移到 Boot 3，本地运行请参见 [IntelliJ 与 Gradle 执行检查](/en/posts/2023-09-10-springboot-intellij-import/)。
