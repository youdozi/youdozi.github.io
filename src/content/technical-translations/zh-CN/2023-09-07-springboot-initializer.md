---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2023-09-07-springboot-initializer",
  "routeSlug": "2023-09-07-springboot-initializer",
  "kind": "post",
  "title": "用 Spring Initializr 创建并测试 Gradle 项目",
  "description": "生成 Spring Boot 项目，检查 Java 和 Gradle 设置，并用 Wrapper 测试。包含可工作的 Boot 4.1.2 项目核心文件。",
  "categories": [
    "springboot"
  ],
  "tags": [
    "springboot",
    "springboot initializer"
  ],
  "sourcePath": "src/content/posts/en/2023-09-07-springboot-initializer.md",
  "sourceSha256": "97a876012a6c3d2dbf40856ed6360dc850f12741aecbd5ee7bd96023fb05275f",
  "draftSha256": "09ba18393cbf0040b28f7adc82be8ecfde58dc358232bfd67c872fba77d483d4",
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

用 Spring Initializr 创建项目后，先通过生成的 Gradle Wrapper 测试，再依赖 IDE。将生成、依赖解析、JDK 兼容性和应用启动分别检查，便于定位失败原因。

此示例使用 Boot 4.1.2、Java 17 和 Gradle Groovy，由 [start.spring.io](https://start.spring.io/)于2026年10月27日实际生成。Wrapper 选择了 Gradle 9.8.2。服务的默认值和可用版本会变化，不要假设此组合永远可用。

## 处理流程

![生成、检查和测试的流程](/assets/diagrams/technical/zh-CN-2023-09-07-springboot-initializer.svg)

运行 Wrapper 前先生成完整归档。上下文测试和独立运行的 HTTP 应用分别验证不同内容。

## 选择项目设置

| 设置 | 示例 | 含义 |
| --- | --- | --- |
| Project / Language | Gradle - Groovy / Java | 构建工具和源语言 |
| Spring Boot | 4.1.2 | 生成此示例时可用的正式版本 |
| Java / Packaging | 17 / Jar | 源码工具链和打包方式 |
| Group / Artifact | example / demo | 项目标识 |
| Package name | example.demo | 应用包名 |
| Dependencies | Spring Web | HTTP 端点所需依赖 |

在 UI 中点击 Generate，或通过此 URL 下载归档。**确认每条命令成功后再运行下一条。** 使用空工作目录，避免覆盖现有项目。

```sh
curl --fail --show-error --location 'https://start.spring.io/starter.zip?type=gradle-project&language=java&bootVersion=4.1.2&baseDir=demo&groupId=example&artifactId=demo&name=Demo&packageName=example.demo&packaging=jar&javaVersion=17&dependencies=web' --output demo.zip
unzip demo.zip
cd demo
./gradlew --version
./gradlew test
```

服务停止提供某版本后，生成 API 可能拒绝该版本。检查[当前服务元数据](https://start.spring.io/metadata/client)和 [Initializr 参考文档](https://docs.spring.io/initializr/docs/current/reference/html/)，再共同选择兼容的 Boot、JDK 和 Gradle 版本。悄悄将示例替换为最新默认值会改变复现条件。

## 检查生成的四个核心文件

以下为简化格式后的四个核心文件。完整归档还包含 Wrapper 脚本、Wrapper JAR 及设置，以及资源文件。只把这四个文件复制到空目录不会生成 `./gradlew`。

### `settings.gradle`

```groovy
rootProject.name = 'demo'
```

### `build.gradle`

```groovy
plugins {
    id 'java'
    id 'org.springframework.boot' version '4.1.2'
    id 'io.spring.dependency-management' version '1.1.7'
}
group = 'example'
version = '0.0.1-SNAPSHOT'
java {
    toolchain { languageVersion = JavaLanguageVersion.of(17) }
}
repositories { mavenCentral() }
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-webmvc'
    testImplementation 'org.springframework.boot:spring-boot-starter-webmvc-test'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
tasks.named('test') { useJUnitPlatform() }
```

### `src/main/java/example/demo/DemoApplication.java`

```java
package example.demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}
```

### `src/test/java/example/demo/DemoApplicationTests.java`

```java
package example.demo;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
class DemoApplicationTests {
    @Test
    void contextLoads() {}
}
```

生成的 Boot 4.1.2 项目使用 `spring-boot-starter-webmvc` 和 `spring-boot-starter-webmvc-test`。以所选版本生成的配置为起点，不要混用不同 Boot 世代的片段。[Boot 4.1.2 要求](https://docs.spring.io/spring-boot/4.1/system-requirements.html)规定 Java 17 或更高版本，以及Gradle 8.x（从 8.14 开始）或 9.x。

## 区分测试与应用启动

`contextLoads()` 通过表示测试上下文能启动。尚无控制器时，`/` 返回 404 并不表示启动失败。另行运行应用，并在对应终端按 Ctrl+C 停止。

```sh
./gradlew bootRun
```

将生成的 `build.gradle` 与 [Gradle Wrapper 文件](https://docs.gradle.org/current/userguide/gradle_wrapper.html)一起提交。Gradle 版本与 `java.toolchain` 中的 Java 版本独立。使用 `./gradlew --version` 检查运行 Gradle 的 JVM，并将其与编译、执行应用所选的 JDK 区分。

接着阅读[在 IntelliJ 中打开项目并提供 HTTP 服务](/en/posts/2023-09-10-springboot-intellij-import/)。关于 Boot 与 Framework 版本号不同的原因，参见 [Spring Boot 发布历史与版本关系](/en/posts/2023-09-13-springboot-history/)。
