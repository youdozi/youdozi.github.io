---
title: "Spring Boot 3 Migration: Java 17, Jakarta and Verification Steps"
language: "en"
translationKey: "2023-09-08-springboot3-migration"
routeSlug: "2023-09-08-springboot3-migration"
kind: "post"
publishedAt: "2023-09-07T15:00:00.000Z"
categories:
  - "springboot"
tags:
  - "springboot"
  - "springboot3"
  - "springboot3 migration"
updatedAt: "2026-10-27T01:24:58+00:00"
reviewedAt: "2026-10-27"
reviewStatus: "revised"
reviewScope: "Official migration documentation checked; diagnostic steps clarified without claiming an application migration."
reviewSources:
  - "https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.0-Migration-Guide"
  - "https://docs.gradle.org/current/userguide/viewing_debugging_dependencies.html"
  - "https://spring.io/blog/2023/09/09/all-together-now-spring-boot-3-2-graalvm-native-images-java-21-and-virtual"
description: "Migrate Spring Boot 2.7 to 3.0 with Java 17, Jakarta dependencies, Gradle checks, property migration and runtime tests. Separate virtual threads from the upgrade."
---
For a Spring Boot 2.7 application moving to 3.0, separate three checks: the Java 17 baseline, the Java EE to Jakarta namespace change, and library/runtime compatibility. A successful compilation does not establish that database mappings, authorization or configuration still work.

This is a **2.7 to 3.0 migration guide**, preserving the original 2023 topic. It is not a recommendation to deploy Boot 3.0 today. Choose a supported target release for a real upgrade and follow the intervening migration guides. The [official 3.0 guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.0-Migration-Guide) documents this historical step.

## 1. Establish a working 2.7 baseline

Update an older 2.x application to the latest 2.7.x release before attempting the major-version change. Save a passing test result and record the wrapper, build JVM and dependencies. For a Gradle project with its existing wrapper, start with:

```sh
java -version
./gradlew --version
./gradlew clean test
./gradlew dependencies --configuration runtimeClasspath
```

Run the same checks after the upgrade. In a multi-project build, run dependency reports on the application module, for example `./gradlew :app:dependencies --configuration runtimeClasspath`. The module name must match your project.

A useful baseline exercises persistence, authentication, serialization, scheduled jobs and outbound HTTP calls. For the last boundary, the [WebClient tests with a local MockWebServer](/en/posts/2023-09-19-springboot-test-webclient/) provide a reproducible starting point.

## 2. Change Java EE imports and dependencies together

Boot 3.0 requires Java 17 and Spring Framework 6. Java EE packages such as `javax.persistence` and `javax.servlet` move to `jakarta.persistence` and `jakarta.servlet`. Java SE packages such as `javax.sql` and `javax.crypto` keep their names.

| Existing use | Migration action |
| --- | --- |
| `javax.persistence.Entity` | Use `jakarta.persistence.Entity` and compatible JPA dependencies. |
| `javax.servlet.Filter` | Use `jakarta.servlet.Filter` and compatible servlet dependencies. |
| `javax.sql.DataSource` | Keep the Java SE package name. |
| `javax.crypto.Cipher` | Keep the Java SE package name. |

Inspect the resolved graph as well as imports. For example, `./gradlew dependencyInsight --dependency javax.servlet-api --configuration runtimeClasspath` helps locate a legacy servlet artifact. An empty report does not prove the whole application has migrated: inspect the other libraries and configurations it actually uses. See [Gradle's dependency reports](https://docs.gradle.org/current/userguide/viewing_debugging_dependencies.html).

For Querydsl JPA, [align the JPA and annotation-processor artifacts](/en/posts/2023-09-09-springboot3-querydsl/) and select their Jakarta variant where required by that artifact line. Confirm that annotation processing generates the expected Q types and that representative queries execute. Gradle's `configureEach` controls task configuration; it cannot convert an incompatible Java EE dependency into a Jakarta dependency.

## 3. Check renamed properties and authorization behavior

For a Boot-managed Gradle project, the official migration guide offers a temporary properties helper:

```groovy
dependencies {
    runtimeOnly 'org.springframework.boot:spring-boot-properties-migrator'
}
```

Start the application in a test environment, read the startup diagnostics and update the affected properties. Remove the helper when the migration is complete. It is not a replacement for reading the target release's configuration changes.

Boot 3.0 also uses Spring Security 6. The migration guide suggests a Spring Security 5.8 transition on Boot 2.7 before moving to 6.0. Test allowed, denied and unauthenticated requests, plus error/forward dispatches where the servlet application uses them; do not use a successful startup as the authorization test.

## 4. Treat virtual threads as a separate change

Boot's virtual-thread setting arrived in **Boot 3.2 with JDK 21**, rather than as a Boot 3.0 feature:

```properties
spring.threads.virtual.enabled=true
```

That is a historical version boundary, not a recommendation to choose Boot 3.2 today. First establish that the namespace and dependency migration works. Then assess virtual threads against the selected release, connection pools and thread-local assumptions. The setting alone proves no performance improvement. [Spring's Boot 3.2 explanation](https://spring.io/blog/2023/09/09/all-together-now-spring-boot-3-2-graalvm-native-images-java-21-and-virtual).

JDK language previews have separate release constraints too. The [String Templates compatibility example](/en/posts/2023-09-23-jdk-21-string-templates/) shows why enabling preview flags is not a general upgrade fix.

## Decide whether the application is ready

| Check | Evidence to collect |
| --- | --- |
| Build and generated code | Passing wrapper build, expected Q types and resolved dependency versions. |
| Runtime behavior | Passing persistence, authentication and representative HTTP tests. |
| Configuration | Updated properties and no remaining need for the migration helper. |
| Deployment | The deployment artifact passes checks in a representative environment. |

The commands are a diagnostic sequence for your project, not the result of a migration performed on your application. Keep the pre-upgrade artifact and configuration available for rollback. Major-version migration supports maintenance, but security still depends on the exact versions and configuration deployed.
