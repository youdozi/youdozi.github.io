---
language: en
translationKey: 2023-09-10-springboot-intellij-import
routeSlug: 2023-09-10-springboot-intellij-import
kind: post
categories:
  - springboot
tags:
  - springboot
  - intellij community
  - project import
  - RUN/DEBUG configurations
publishedAt: "2026-10-27T03:48:55+00:00"
title: Open and Run a Spring Boot Gradle Project in IntelliJ IDEA
updatedAt: "2026-10-27T03:48:55+00:00"
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Official documentation checked; CLI/project execution distinguished
  from IDE UI verification.
reviewSources:
  - https://www.jetbrains.com/help/idea/gradle.html
  - https://www.jetbrains.com/help/idea/gradle-jvm-selection.html
  - https://www.jetbrains.com/help/idea/running-applications.html
  - https://docs.gradle.org/current/userguide/compatibility.html
description: Check Gradle sync, SDK and run settings in IntelliJ IDEA, then use
  real HTTP tests to separate IDE configuration failures from application
  behavior.
---
When opening a Spring Boot project in IntelliJ, check Gradle synchronization first and compare the Wrapper build with IDE execution. A missing run button does not always require creating a manual configuration. You can also run a valid Java main method from the [editor gutter icon](https://www.jetbrains.com/help/idea/running-applications.html).

This guide continues the Boot 4.1.2, Gradle 9.8.2, Java 17 [Initializr example](/en/posts/2023-09-07-springboot-initializer/). The build and HTTP behavior ran locally; the IDE steps were checked against JetBrains documentation. This does not claim hands-on UI verification in a particular IDE release.

## Check the project and JDK

1. Use File → Open on the extracted project root containing `settings.gradle` and `build.gradle`.
2. Complete Gradle synchronization. Resolve dependency download or synchronization failures first.
3. Select the project's Wrapper distribution, then check the Gradle JVM and Project SDK. This example uses JDK 17 for both.
4. Run `./gradlew --version` and `./gradlew test` in a terminal to establish a result outside the IDE.

See the [Gradle integration guide](https://www.jetbrains.com/help/idea/gradle.html) and [Gradle JVM selection rules](https://www.jetbrains.com/help/idea/gradle-jvm-selection.html). Menu labels vary with IDE version and OS. Project SDK, the JVM running Gradle, the Java toolchain, and the run configuration's JRE are distinct settings and do not always match automatically.

## Add an endpoint and real HTTP tests

Keep the four existing files and add these two. Placing the controller in the application's `example.demo` package keeps it within component scanning.

### `src/main/java/example/demo/GreetingController.java`

```java
package example.demo;

import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class GreetingController {
    @GetMapping("/greeting")
    public Map<String, String> greeting() {
        return Map.of("message", "Hello, Gradle");
    }
}
```

### `src/test/java/example/demo/GreetingHttpTest.java`

```java
package example.demo;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.core.env.Environment;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class GreetingHttpTest {
    @Autowired Environment environment;

    HttpResponse<String> get(String path) throws Exception {
        String port = environment.getRequiredProperty("local.server.port");
        var request = HttpRequest.newBuilder(URI.create("http://127.0.0.1:" + port + path))
                .timeout(Duration.ofSeconds(10)).GET().build();
        return HttpClient.newHttpClient().send(request, HttpResponse.BodyHandlers.ofString());
    }

    @Test
    void greetingReturnsJson() throws Exception {
        var response = get("/greeting");
        assertEquals(200, response.statusCode());
        assertTrue(response.headers().firstValue("content-type").orElse("").contains("application/json"));
        assertEquals("{\"message\":\"Hello, Gradle\"}", response.body());
    }

    @Test
    void missingPathIsNotAnApplicationStartupFailure() throws Exception {
        assertEquals(404, get("/missing").statusCode());
    }
}
```

`./gradlew test` now runs the existing context test and two HTTP tests. The HTTP tests start a real server on a random port and check JSON output and a missing path's 404 response. They do not require local port 8080 to be free.

## Compare Gradle and Application execution

Start the server with the first command, then run the second command in another terminal.

```sh
./gradlew bootRun --args='--server.port=8081'
```

```sh
curl --fail --show-error http://localhost:8081/greeting
```

```json
{"message":"Hello, Gradle"}
```

In the IDE, try the run icon beside `DemoApplication.main()` first. If you need an explicit configuration, create an Application configuration under Run → Edit Configurations and check these values.

| Setting | Example |
| --- | --- |
| Main class | `example.demo.DemoApplication` |
| Classpath module | The project's main source module, such as `demo.main` |
| JRE | JDK 17 |
| Program arguments | `--server.port=8081` |

If an existing process occupies 8081, stop it or choose another port. Availability of Boot-specific tool windows or configurations is separate from running a normal Java Application configuration.

| Observation | Check first |
| --- | --- |
| The Wrapper build also fails | JDK/Gradle compatibility, dependencies, and source errors |
| Wrapper passes but IDE fails | Gradle reload, module classpath, run JRE and arguments |
| Server starts but `/greeting` returns 404 | Controller package and mapping path |
| Port-in-use failure | Existing processes and run instances |

If compilation succeeds but the IDE marks generated methods as errors, continue with [Lombok and annotation processor checks](/en/posts/2023-09-15-springboot-intellij-lombok/).
