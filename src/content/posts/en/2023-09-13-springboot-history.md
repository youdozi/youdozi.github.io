---
language: en
translationKey: 2023-09-13-springboot-history
routeSlug: 2023-09-13-springboot-history
kind: post
categories:
  - springboot
tags:
  - springboot
  - history
publishedAt: "2026-10-27T03:48:55+00:00"
title: Spring Boot Release History and Spring Framework Version Mapping
updatedAt: "2026-10-27T03:48:55+00:00"
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Official documentation checked; CLI/project execution distinguished
  from IDE UI verification.
reviewSources:
  - https://spring.io/blog/2014/12/11/spring-boot-1-2-0-released/
  - https://spring.io/blog/2015/11/16/spring-boot-1-3-0-released/
  - https://spring.io/blog/2016/07/28/spring-boot-1-4-released/
  - https://spring.io/blog/2018/03/01/spring-boot-2-0-goes-ga/
  - https://spring.io/blog/2022/11/24/spring-boot-3-0-goes-ga/
  - https://spring.io/blog/2023/05/18/spring-boot-3-1-0-available-now/
  - https://spring.io/blog/2023/11/23/spring-boot-3-2-0-available-now/
  - https://spring.io/blog/2025/11/20/spring-boot-4-0-0-available-now/
  - https://docs.spring.io/spring-boot/docs/3.1.0/reference/html/dependency-versions.html
  - https://docs.spring.io/spring-boot/4.1/gradle-plugin/managing-dependencies.html
description: Trace key Spring Boot releases from 1.2 to 4.0, distinguish Boot
  from Framework, starters, and BOMs, and inspect the dependency versions your
  project resolves.
---
Spring Boot and Spring Framework are separate projects with different version numbers. Boot adds auto-configuration, dependency management, and executable packaging around Framework. Reading Boot 3.1 as Framework 6.1 is therefore unreliable; inspect the selected Boot release's BOM and resolved dependency graph instead.

## Changes in selected final releases

This timeline highlights feature transitions rather than listing every release. Distinguish the first final release from expanded JDK compatibility in later patches.

| Spring Boot | First final release | Selected changes and official announcement |
| --- | --- | --- |
| 1.2 | 2014-12-11 | [`@SpringBootApplication` and Servlet 3.1 support](https://spring.io/blog/2014/12/11/spring-boot-1-2-0-released/) |
| 1.3 | 2015-11-16 | [DevTools, caching auto-configuration, and directly executable JARs](https://spring.io/blog/2015/11/16/spring-boot-1-3-0-released/) |
| 1.4 | 2016-07-28 | [Startup failure analysis and improved testing support](https://spring.io/blog/2016/07/28/spring-boot-1-4-released/) |
| 2.0 | 2018-03-01 | [Framework 5.0, a Java 8 baseline, and reactive web support](https://spring.io/blog/2018/03/01/spring-boot-2-0-goes-ga/) |
| 3.0 | 2022-11-24 | [Framework 6.0, a Java 17 baseline, Jakarta, and native images](https://spring.io/blog/2022/11/24/spring-boot-3-0-goes-ga/) |
| 3.1 | 2023-05-18 | [Development-time Testcontainers and Docker Compose integration](https://spring.io/blog/2023/05/18/spring-boot-3-1-0-available-now/) |
| 3.2 | 2023-11-23 | [Virtual threads, RestClient, and JdbcClient support](https://spring.io/blog/2023/11/23/spring-boot-3-2-0-available-now/) |
| 4.0 | 2025-11-20 | [Framework 7, modularization, JSpecify, and API versioning](https://spring.io/blog/2025/11/20/spring-boot-4-0-0-available-now/) |

For example, the [Boot 3.1.0 managed dependency list](https://docs.spring.io/spring-boot/docs/3.1.0/reference/html/dependency-versions.html) specifies `spring-core` 6.0.9. There is no requirement for Boot and Framework minor version numbers to match. Mapping Boot 2.4 to a nonexistent Framework 5.4 line is also incorrect.

## Starters, BOMs, and build plugins

A starter groups dependencies needed for a feature. A BOM manages versions; it does not automatically add every library in that list to your project. Boot's build plugin provides tasks such as `bootRun` and executable JAR packaging.

For Gradle, the [Boot dependency management guide](https://docs.spring.io/spring-boot/4.1/gradle-plugin/managing-dependencies.html) describes the dependency-management plugin and native BOM support. Applying the Boot plugin alone does not establish that all Gradle configurations accept versionless dependencies. Check separate configurations such as annotation processors too.

## Inspect your project's actual versions

Run these commands in the final project from the [Initializr](/en/posts/2023-09-07-springboot-initializer/) and [Lombok guides](/en/posts/2023-09-15-springboot-intellij-lombok/).

```sh
./gradlew dependencyInsight --configuration runtimeClasspath --dependency spring-core
./gradlew dependencyInsight --configuration annotationProcessor --dependency lombok
```

The local example resolves Boot 4.1.2, `spring-core` 7.0.10, and Lombok 1.18.48. Different numbers reflect different projects. `dependencyInsight` shows the selected version and the dependency paths or rules responsible for it, making it useful for investigating conflicts. These values record this example, not future defaults or a universal project combination.

The timeline is not a current support-lifecycle table. When creating or upgrading a project, check the selected release's requirements, dependency compatibility, and support policy separately. See [Java 17 and Jakarta migration](/en/posts/2023-09-08-springboot3-migration/) for moving to Boot 3, or [IntelliJ and Gradle execution checks](/en/posts/2023-09-10-springboot-intellij-import/) for running locally.
