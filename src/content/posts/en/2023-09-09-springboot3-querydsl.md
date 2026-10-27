---
title: "Spring Boot 3 and Querydsl: Jakarta Setup and Q-Type Generation"
language: "en"
translationKey: "2023-09-09-springboot3-querydsl"
routeSlug: "2023-09-09-springboot3-querydsl"
kind: "post"
publishedAt: "2026-10-27T02:02:40+00:00"
updatedAt: 2026-10-27T06:13:10.631Z
reviewedAt: "2026-10-27"
reviewStatus: "revised"
reviewScope: "Official documentation checked; Q-type generation and H2 query tests reproduced."
categories: ["springboot"]
tags: ["springboot", "springboot3", "querydsl"]
reviewSources: ["https://github.com/querydsl/querydsl/releases/tag/QUERYDSL_5_0_0", "https://docs.gradle.org/current/userguide/java_plugin.html", "https://docs.gradle.org/current/userguide/lazy_configuration.html", "https://docs.spring.io/spring-boot/3.5/reference/testing/spring-boot-applications.html", "https://docs.oracle.com/en/java/javase/17/docs/api/java.compiler/javax/annotation/processing/Generated.html"]
description: "Configure Querydsl Jakarta with Spring Boot 3, generate Q types with Gradle, and run H2-backed JPA tests using a complete reproducible example."
---
For Querydsl JPA on Spring Boot 3, align the versions and `jakarta` classifiers of `querydsl-jpa` and `querydsl-apt`, then check both Q-type generation and a real query. Keeping Gradle's default generated-source paths avoids configuring main and test compilation to write to the same directory.

This guide develops the original 2023 Korean example into a runnable configuration. [Querydsl's 5.0 release notes](https://github.com/querydsl/querydsl/releases/tag/QUERYDSL_5_0_0) document Jakarta classifier support. The versions below pin the reproduction environment; they are not a recommendation of current production dependencies.

## Processing flow

![Generate Q types and query workflow](/assets/diagrams/2023-09-09-springboot3-querydsl-en.svg)

The processor generates QEmployee during main compilation. The H2 test then executes a query with those generated types.

## Reproduction environment and complete Gradle setup

| Component | Reproduction version |
| --- | --- |
| JDK / Gradle | 17.0.8.1 / 8.4 |
| Spring Boot BOM | 3.5.7 |
| Querydsl JPA / APT | 5.1.0, both with the `jakarta` classifier |
| Hibernate / H2 | 6.6.33.Final / 2.3.232, managed by the BOM |

Create these five files in a new directory. This test project uses the Java plugin and Boot BOM; it does not need the Boot Gradle plugin. In an existing Boot application, add only the dependencies needed alongside its selected dependency management.

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

Gradle resolves `annotationProcessor` separately from the normal compile and runtime classpaths. The example therefore applies the BOM to the processor configuration too and explicitly supplies the Jakarta Persistence and Annotation APIs. A dependency on `implementation` is not automatically available to the processor. See the [Gradle Java plugin documentation](https://docs.gradle.org/current/userguide/java_plugin.html).

## Create the application and entity

The application class lets the JPA test discover its Boot configuration. There is no need to start a separate server process for the test.

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

`Employee` uses `jakarta.persistence`. Do not write `QEmployee` yourself: the annotation processor generates the type referenced by the test below.

## Query through the generated Q type

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

`@DataJpaTest` uses H2 from this example's classpath. Each test runs in a transaction and rolls back afterward. After inserting data with `persistAndFlush`, the generated `QEmployee` supports two checks: an exact-name match and a query returning no rows. See [Spring Boot's JPA testing guide](https://docs.spring.io/spring-boot/3.5/reference/testing/spring-boot-applications.html#testing.spring-boot-applications.autoconfigured-spring-data-jpa-tests).

These tests check this entity and query on H2. They do not verify your production database's SQL dialect, collation, locking or migration behavior.

## Run and inspect the generated files

Select JDK 17 and use an installed Gradle 8.4. Run from the project root:

```sh
java -version
gradle --version
gradle --no-daemon clean test
```

Check these generated artifacts and the test report:

```text
build/generated/sources/annotationProcessor/java/main/example/QEmployee.java
build/classes/java/main/example/QEmployee.class
build/reports/tests/test/index.html
```

Both tests passed with this configuration. Repeating `clean test` regenerated the Q type and passed both tests again. For an existing project with a Gradle wrapper, use its selected version through `./gradlew clean test`.

The generated Q type in this example imports `javax.annotation.processing.Generated`, a Java SE `java.compiler` API. That import does not need a Jakarta replacement. [JDK 17 Generated API](https://docs.oracle.com/en/java/javase/17/docs/api/java.compiler/javax/annotation/processing/Generated.html).

## Troubleshoot missing or duplicate Q types

| Symptom | First check |
| --- | --- |
| `QEmployee` cannot be found | Check the CLI `clean compileJava` result, processor dependencies, and the entity's `jakarta.persistence` imports. |
| The processor cannot find Persistence APIs | Check that the required Jakarta APIs are on the processor path, separately from the normal classpath. |
| An incompatible `javax.persistence.EntityManager` type appears | Check matching versions and Jakarta classifiers for both Querydsl artifacts. |
| Duplicate Q types, or a build that works only after clean | Remove hand-written Q sources and shared generated paths; inspect main/test output configuration. |
| CLI passes but the IDE cannot see Q types | Check Gradle synchronization, delegated build settings and IDE annotation processing. |

The example does not add custom `sourceSets`, `JavaCompile` or `clean` configuration for generated files. If you need a custom path, keep main and test outputs separate. `configureEach` controls lazy task configuration; it does not fix Jakarta dependency compatibility. [Gradle configuration avoidance](https://docs.gradle.org/current/userguide/lazy_configuration.html).

For the surrounding upgrade sequence, see the [Spring Boot 3 migration guide](/en/posts/2023-09-08-springboot3-migration/). For outbound HTTP boundaries, use the [WebClient and MockWebServer tests](/en/posts/2023-09-19-springboot-test-webclient/).

## Compare before changing query tools

The complete Employee class includes a getter so repository results can be compared as names. Add the three files from the [Querydsl and Specification comparison](/en/posts/2023-09-05-querydsl-no-release/) to run eight additional checks on the same entity. The two original tests above remain part of that ten-test project. This compares selected H2 predicates, not all database behavior. The [Spring Boot guide](/en/categories/springboot/) connects the surrounding setup and testing steps.
