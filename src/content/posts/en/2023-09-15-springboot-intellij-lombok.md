---
language: en
translationKey: 2023-09-15-springboot-intellij-lombok
routeSlug: 2023-09-15-springboot-intellij-lombok
kind: post
categories:
  - springboot
tags:
  - springboot
  - intellij community
  - lombok
publishedAt: "2026-10-27T03:48:55+00:00"
title: "Fix Lombok in IntelliJ: Separate Gradle Compilation from IDE Support"
updatedAt: "2026-10-27T03:48:55+00:00"
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Official documentation checked; CLI/project execution distinguished
  from IDE UI verification.
reviewSources:
  - https://projectlombok.org/setup/gradle
  - https://projectlombok.org/setup/intellij
  - https://www.jetbrains.com/help/idea/annotation-processors-support.html
  - https://docs.spring.io/spring-boot/4.1/gradle-plugin/managing-dependencies.html
description: Configure Lombok for main and test annotation processing, verify
  generated constructors, getters, and JSON output, and isolate Gradle failures
  from IDE errors.
---
If Lombok methods appear missing, first run `./gradlew clean test` to determine whether the build fails too. IDE support helps the editor recognize generated members; Gradle's annotation processor configuration generates them during compilation. Neither replaces the other.

This example continues the [Initializr project](/en/posts/2023-09-07-springboot-initializer/) and [HTTP example](/en/posts/2023-09-10-springboot-intellij-import/). It uses Boot 4.1.2, Gradle 9.8.2, and JDK 17; the BOM selected Lombok 1.18.48. This records one working combination without guaranteeing compatibility for every JDK/Lombok pairing.

## Configure Gradle compilation

Append this block to the existing `build.gradle`, avoiding duplicate declarations if they already exist.

```groovy
dependencies {
    compileOnly 'org.projectlombok:lombok'
    annotationProcessor 'org.projectlombok:lombok'
    testCompileOnly 'org.projectlombok:lombok'
    testAnnotationProcessor 'org.projectlombok:lombok'
}
```

The [official Gradle setup](https://projectlombok.org/setup/gradle) separates main and test compile dependencies and processors. The two test declarations are needed only when test sources themselves use Lombok annotations. The tests below exercise that path too.

Versionless declarations work here because the project applies the Boot plugin and `io.spring.dependency-management`, which [imports Boot's BOM](https://docs.spring.io/spring-boot/4.1/gradle-plugin/managing-dependencies.html). In a plain Gradle project, use the same compatible explicit version in the required declarations or configure dependency management for those configurations separately.

## Use the generated constructor and getter

Add `Greeting`, replace the existing controller with this version, retain the HTTP tests, and add the Lombok-specific test class.

### `src/main/java/example/demo/Greeting.java`

```java
package example.demo;

import lombok.Getter;
import lombok.RequiredArgsConstructor;

@Getter
@RequiredArgsConstructor
public class Greeting {
    private final String message;
}
```

### `src/main/java/example/demo/GreetingController.java`

```java
package example.demo;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class GreetingController {
    @GetMapping("/greeting")
    public Greeting greeting() {
        return new Greeting("Hello, Gradle");
    }
}
```

### `src/test/java/example/demo/LombokGenerationTest.java`

```java
package example.demo;

import lombok.Getter;
import lombok.RequiredArgsConstructor;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class LombokGenerationTest {
    @Getter
    @RequiredArgsConstructor
    static class Expected {
        private final String message;
    }

    @Test
    void mainSourceConstructorAndGetterAreGenerated() {
        assertEquals("Hello, Gradle", new Greeting("Hello, Gradle").getMessage());
    }

    @Test
    void testSourceConstructorAndGetterAreGenerated() {
        assertEquals("test fixture", new Expected("test fixture").getMessage());
    }
}
```

```sh
./gradlew clean test bootJar
./gradlew dependencyInsight --configuration annotationProcessor --dependency lombok
```

There are now five tests: one context test, two HTTP tests, and two Lombok generation tests. They call generated constructors and getters in both main and test sources. `/greeting` must continue returning the same JSON, also checking serialization through the generated getter.

Because Lombok is `compileOnly`, this example's executable JAR does not include it as a runtime library. Installing an IDE plugin alone does not make Gradle compilation pass. Adding Lombok as a runtime `implementation` dependency is not needed to use the already-compiled getter in this setup.

## When only the IDE reports errors

If Wrapper tests pass, reload the Gradle project. [JetBrains documents](https://www.jetbrains.com/help/idea/annotation-processors-support.html) that importing processors from build files automatically enables annotation processing. Manually changing a checkbox is therefore not a universal required step.

Next, check Lombok support and plugin activation for your IDE version using the [Lombok IntelliJ guide](https://projectlombok.org/setup/intellij). Do not generalize that one edition always needs manual installation while another always bundles it. Also determine whether the IDE uses its own compiler or delegates builds to Gradle.

If Gradle also fails with missing generated members, check for `compileOnly` without `annotationProcessor`. If only tests fail, inspect the two test configurations. The reproduction checker confirms compilation failure when the main processor or test processor is removed separately, then restores them and verifies all five tests pass again. IDE UI interaction is outside those execution checks.
