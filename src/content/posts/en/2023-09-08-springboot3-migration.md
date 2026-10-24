---
title: "Spring Boot 3 Migration: Java 17 and Jakarta Checklist"
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
updatedAt: "2026-10-24T06:00:52.185Z"
reviewedAt: "2026-10-24"
reviewStatus: "revised"
reviewScope: "English edition based on the reviewed Korean article; technical
  references and reproduction conditions retained."
reviewSources:
  - "https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.0-Migrat\
    ion-Guide"
  - "https://spring.io/blog/2023/09/09/all-together-now-spring-boot-3-2-graalvm\
    -native-images-java-21-and-virtual"
description: "A practical Spring Boot 2.7 to 3.0 migration checklist covering
  Java 17, Jakarta imports, Querydsl compatibility, and virtual-thread version
  requirements."
---
## Scope and baseline

This guide covers the migration from Spring Boot 2.7 to Spring Boot 3.0. Its original publication dates from 2023, and the compatibility notes were reviewed on October 24, 2026. For a new application, choose a currently supported Spring Boot release and review its own system requirements.

Spring Boot 3.0 introduced a Java 17 baseline, Spring Framework 6.0, the transition to Jakarta EE APIs, and integrated support for GraalVM native images. An application that builds successfully can still have runtime incompatibilities in persistence, security, configuration, and third-party libraries.

## Prepare before changing the major version

First bring an older Boot 2.x application to a working Boot 2.7 baseline, as recommended by the official migration guide. Record the JDK, Gradle or Maven version, dependency graph, and the tests that exercise the application’s important behavior.

Run those tests before the upgrade. A passing baseline makes it easier to distinguish an existing failure from a migration regression. Include integration tests for database mappings, authentication, serialization, scheduled work, and outbound HTTP calls.

## Change the right javax packages

The Jakarta namespace change applies to Java EE APIs such as `javax.persistence` and `javax.servlet`. Their Jakarta counterparts use `jakarta.persistence` and `jakarta.servlet`.

Do not perform a blanket replacement of every `javax` import. Java SE APIs such as `javax.sql` and `javax.crypto` retain their names. Check direct and transitive dependencies as well as source imports: an old servlet API pulled in by a library can still cause a mismatch.

## Check the dependency combination

Use the versions managed by the chosen Spring Boot release as the starting point. When overriding a dependency, check the resulting combination explicitly.

For Querydsl JPA, align the JPA and annotation-processor artifacts and select the Jakarta classifier when required by that artifact line. A successful annotation-processing task should produce the expected Q types. Release history has changed since the original post: Querydsl subsequently published version 5.1.0, so the old statement about no releases after 2021 is historical context.

Do not treat a change to `configureEach` as a Jakarta compatibility fix. It controls Gradle’s lazy task configuration. Main and test annotation-processing tasks also need separate output locations if their defaults are overridden.

## Keep virtual threads separate from the Boot 3.0 migration

Virtual-thread support arrived with Spring Boot 3.2 and Spring Framework 6.1 and requires JDK 21 for that feature. It was not a Boot 3.0 baseline feature. Validate the initial namespace and dependency migration before adding a concurrency change.

For a supported Boot 3.2 configuration, the property is:

```properties
spring.threads.virtual.enabled=true
```

Assess application behavior, downstream connection pools, and thread-local assumptions when enabling it. The setting alone does not establish that an application will run faster.

## Verification checklist

1. Compare the command-line JDK with the IDE and build-tool JVM.
2. Build and run tests using the project’s Gradle or Maven wrapper.
3. Check generated source files and persistence mappings.
4. Test authentication and representative HTTP requests.
5. Review changed configuration properties and third-party integration points.
6. Test the deployment artifact in a representative environment before rollout.

Upgrading a major version supports ongoing maintenance, but security depends on the actual dependency versions and configuration you deploy. Follow the migration guide for the exact target version.

## Sources

- [Spring Boot 3.0 migration guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.0-Migration-Guide)
- [Spring Boot 3.0 GA announcement](https://spring.io/blog/2022/11/24/spring-boot-3-0-goes-ga/)
- [Spring Boot 3.2, Java 21, and virtual threads](https://spring.io/blog/2023/09/09/all-together-now-spring-boot-3-2-graalvm-native-images-java-21-and-virtual)
- [Querydsl 5.1.0 release](https://github.com/querydsl/querydsl/releases/tag/QUERYDSL_5_1_0)
- [Gradle lazy task configuration](https://docs.gradle.org/current/userguide/lazy_configuration.html)
