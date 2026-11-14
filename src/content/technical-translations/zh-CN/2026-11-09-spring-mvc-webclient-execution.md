---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2026-11-09-spring-mvc-webclient-execution",
  "routeSlug": "2026-11-09-spring-mvc-webclient-execution",
  "kind": "post",
  "title": "Spring MVC 中的 WebClient：.block() 与返回 Mono 的线程行为",
  "description": "区分 Spring MVC 与 Reactor Netty 的职责，通过真实 Tomcat 示例比较 WebClient 的 .block()、Mono 返回和虚拟线程。",
  "categories": [
    "springboot"
  ],
  "tags": [
    "spring-mvc",
    "webclient",
    "reactor-netty",
    "servlet-async",
    "virtual-threads"
  ],
  "sourcePath": "src/content/posts/en/2026-11-09-spring-mvc-webclient-execution.md",
  "sourceSha256": "6f81dd9e98a391f7b05ca1d0fef8c01ca8288550531caf852ae518c60843dba8",
  "draftSha256": "1a001beb0f13fcba3b340813ba9105cadd10c7722823186905ee29b98f32e4dd",
  "manifestPath": ".pipeline/technical-translations/batch-156/manifest.json",
  "manifestSha256": "ed48dc20825daff8725d8eba3418b1ad885276b52c9752ba958f7a1705b24430",
  "publishedAt": "2026-11-14T15:16:43.783Z",
  "updatedAt": "2026-11-14T15:16:43.783Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 158,
    "approvedAt": "2026-11-14T15:16:43.783Z",
    "basis": "User requested all 63 language editions and instructed completed PRs to be merged; AI translation and independent AI review were performed, with no claim of human text review."
  }
}
---

**在 Spring MVC 中，WebClient 也能使用非阻塞 HTTP 通信；但控制器调用 `.block()` 会使 MVC 请求线程等待结果。** 返回 `Mono` 可让 MVC 将其适配到 Servlet 异步处理并释放初始请求线程。客户端通信与服务器请求处理是不同的问题。

本文讨论 **Tomcat 上的 Spring MVC 与使用 Reactor Netty 的 WebClient**。其他 HTTP 连接器可能使用不同线程名称与资源。示例使用 Spring Boot 3.5.16、JDK 21 和 Gradle 8.14.3 复现；这不意味着验证了当前所有 Boot 版本。

## 添加 WebClient 会让服务器使用 WebFlux 吗？

服务端 MVC 和用于外部调用的 WebClient 职责不同。这里 Tomcat 与 `DispatcherServlet` 处理传入请求，WebClient 的 Reactor Netty 连接器处理出站 HTTP。

在 Boot 3.5 中，同时添加 `spring-boot-starter-web` 与 `spring-boot-starter-webflux` 时默认选择 MVC。这支持为了使用 WebClient 而添加 WebFlux starter 的应用。如果显式更改应用类型或使用其他服务器配置，需要另行确认。[Boot 的 MVC 与 WebFlux 选择](https://docs.spring.io/spring-boot/3.5/reference/web/reactive.html#web.reactive.webflux)

## `.block()` 和返回 `Mono` 从哪里分开？

![block 路径中 Servlet 请求线程等待，Netty 处理 HTTP 通信。返回 Mono 的路径中，MVC 订阅后 Netty 通信与 Servlet 异步处理可以重叠，随后 MVC 对结果重新派发。](/assets/diagrams/technical/zh-CN-2026-11-09-spring-mvc-webclient-execution.svg)

绿色表示 Servlet 和 MVC 的职责，蓝色表示 Reactor Netty。异步路径中的两个分支可能重叠；外部响应不一定在初始请求线程返回之后才到达。图主要表示成功信号，代码中的错误信号映射为 HTTP 状态后进入 MVC 错误处理。

| 阶段 | `.block()` 后返回值 | 返回 `Mono` |
| --- | --- | --- |
| 订阅 | 由 `.block()` 执行 | MVC 订阅返回类型 |
| 等待出站 HTTP | 请求线程等待 | Servlet 异步处理可能释放初始请求线程 |
| 接收响应体后 | 客户端回调提供结果并解除等待 | 结果信号交给 MVC 异步处理 |
| 最终 HTTP 响应 | MVC 序列化并写入返回值 | MVC 重新派发后序列化并写入 |

`retrieve().bodyToMono(...)` 组装请求管道。下方新建的 WebClient 管道必须被订阅才会发起 HTTP 请求。订阅两次可能再次发出请求，因此应注意使用 `.block()` 读取一次后又返回该管道的代码。

MVC 对单值 `Mono` 的适配类似 `DeferredResult`。结果准备好后，MVC 向 Servlet 容器重新派发以完成响应。线程池可能复用同一线程，因此不要假设重新派发线程一定不同于初始线程。响应未关闭时，连接和异步请求资源也会保留。返回 `Mono` 不会使整个 Servlet 响应写入都变为非阻塞。此例返回单值 JSON；流式传输和 SSE 是不同情况。[MVC 异步处理与 reactive 返回类型](https://docs.spring.io/spring-framework/reference/6.2/web/webmvc/mvc-ann-async.html)

## 用两种方式调用同一个外部 API

将以下文件保存到同一项目。它使用 `application` 插件而非 Boot Gradle 插件，并将 Java toolchain 固定为 21。本地检查使用 Azul JDK 21.0.1；这一历史补丁版本不作为新生产环境的推荐。

### `settings.gradle`

```groovy
rootProject.name = 'mvc-webclient-execution'
```

### `build.gradle`

```groovy
plugins {
    id 'java'
    id 'application'
}
repositories { mavenCentral() }
java { toolchain { languageVersion = JavaLanguageVersion.of(21) } }
dependencies {
    implementation platform('org.springframework.boot:spring-boot-dependencies:3.5.16')
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.boot:spring-boot-starter-webflux'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
application { mainClass = 'example.DemoApplication' }
test {
    useJUnitPlatform()
    systemProperty 'demo.virtual', providers.gradleProperty('virtual').getOrElse('false')
}
```

### `src/main/resources/application.yml`

```yaml
upstream:
  base-url: http://127.0.0.1:9091
  timeout: 3s
spring:
  mvc:
    async:
      request-timeout: 5s
```

`WebClient` 作为 bean 复用，并显式使用 Reactor Netty 连接器。示例的 `HttpClient.create()` 使用默认共享事件循环和连接池，不会为每个出站请求创建专属 Netty 线程。`callbackThread` 是响应体生成后执行 `map` 的线程，不一定是写入最终 Servlet 响应的线程。这里没有添加 `publishOn` 等调度器切换。[WebClient 连接器和共享资源](https://docs.spring.io/spring-framework/reference/6.2/web/webflux-webclient/client-builder.html)

### `src/main/java/example/DemoApplication.java`

```java
package example;

import java.time.Duration;
import java.util.concurrent.TimeoutException;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.http.HttpStatus;
import org.springframework.http.client.reactive.ReactorClientHttpConnector;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;
import org.springframework.web.server.ResponseStatusException;

import reactor.core.publisher.Mono;
import reactor.core.scheduler.Schedulers;
import reactor.netty.http.client.HttpClient;

@SpringBootApplication
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }

    @Bean
    WebClient upstreamClient(WebClient.Builder builder,
                             @Value("${upstream.base-url}") String baseUrl) {
        return builder.baseUrl(baseUrl)
                .clientConnector(new ReactorClientHttpConnector(HttpClient.create()))
                .build();
    }

    public record Observation(String mode, String requestThread, boolean requestVirtual,
                              String callbackThread, boolean callbackVirtual, boolean callbackNonBlocking,
                              String value) {}

    @RestController
    static class DemoController {
        private final WebClient client;
        private final Duration deadline;

        DemoController(WebClient client, @Value("${upstream.timeout}") Duration deadline) {
            this.client = client;
            this.deadline = deadline;
        }

        private Mono<Observation> fetch(String mode) {
            Thread request = Thread.currentThread();
            String name = request.getName();
            boolean virtual = request.isVirtual();
            return client.get().uri("/value").retrieve().bodyToMono(String.class)
                    .timeout(deadline)
                    .map(value -> new Observation(mode, name, virtual,
                            Thread.currentThread().getName(), Thread.currentThread().isVirtual(),
                            Schedulers.isInNonBlockingThread(), value))
                    .onErrorMap(WebClientResponseException.class, error ->
                            new ResponseStatusException(HttpStatus.BAD_GATEWAY,
                                    "upstream HTTP error", error))
                    .onErrorMap(TimeoutException.class, error ->
                            new ResponseStatusException(HttpStatus.GATEWAY_TIMEOUT,
                                    "upstream deadline", error));
        }

        @GetMapping("/block")
        Observation blocking() {
            return fetch("block").block();
        }

        @GetMapping("/async")
        Mono<Observation> asynchronous() {
            return fetch("async");
        }
    }
}
```

`/block` 是用于比较的路径。能够以异步返回结束的控制器可像 `/async` 一样返回结果 `Mono`，交给 MVC 订阅。直接调用 `.subscribe()` 并先返回响应，会使出站调用的结果和错误脱离原始 HTTP 请求。[同步使用 WebClient 和控制器返回值](https://docs.spring.io/spring-framework/reference/web/webflux-webclient/client-synchronous.html)

示例中三秒的 `timeout` 限制从订阅到收到值的时间，没有分别配置连接池获取、连接或单次响应读取的超时。HTTP 错误映射为 502，管道超时映射为 504。连接失败、空响应体和业务错误需要单独定义契约。`retrieve()` 默认将 HTTP 4xx 和 5xx 视为错误。[retrieve 错误处理](https://docs.spring.io/spring-framework/reference/6.2/web/webflux-webclient/client-retrieve.html)

### 本地运行

使用本地 Python 3 HTTP 服务器代替外部服务。`/value` 在 0.2 秒后返回 `hello`。该延迟是观察行为的输入，并非性能测量。

### `upstream.py`

```python
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from time import sleep


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != '/value':
            self.send_error(404)
            return
        sleep(0.2)
        body = b'hello'
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


ThreadingHTTPServer(('127.0.0.1', 9091), Handler).serve_forever()
```

在第一个终端运行。

```sh
python3 upstream.py
```

在第二个终端选择 JDK 21，并使用 Gradle 8.14.3 运行。

```sh
gradle run
```

在第三个终端调用两个路径：

```sh
curl --fail --show-error --silent http://127.0.0.1:8080/block
curl --fail --show-error --silent http://127.0.0.1:8080/async
```

两个路径都返回含 `hello` 的 JSON。使用普通请求线程时，我们观察到 `requestVirtual=false`；此例的 Netty 回调为 `callbackVirtual=false` 和 `callbackNonBlocking=true`。线程名称和编号每次可能不同，仅看响应 JSON 中的 `mode` 无法证明等待时请求线程已释放。

## 启用虚拟线程后有什么变化？

停止前面的应用，再以虚拟线程设置运行相同代码。

```sh
gradle run --args='--spring.threads.virtual.enabled=true'
```

此设置下两个路径的 `requestVirtual` 均变为 `true`。在 `.block()` 路径中，调用的虚拟线程仍等待结果，但通常可 park 的等待不同于持续占用载体平台线程。需要另行确认 pinning 与所运行 JDK 的差异。[JDK 21 虚拟线程调度和 pinning](https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html) **启用虚拟线程没有使此例的 Reactor Netty 回调变成虚拟线程。** [Boot 虚拟线程配置](https://docs.spring.io/spring-boot/3.5/reference/features/spring-application.html#features.spring-application.virtual-threads)

虚拟线程不会增加外部服务处理能力、HTTP 连接数或 DB 连接数。积压请求的上限需要另行设计，例如[数据库信号量和准入控制](/ko/posts/2026-11-03-virtual-threads-db-semaphore/)。

## 可以在回调中调用 JDBC 吗？

从 MVC 调用 WebClient 不意味着后续 `map` 也运行在 MVC 请求线程。此例中若在 `map` 里执行 JDBC 查询或长时间文件读取，可能阻塞 Netty 事件循环。反过来，并非每个 `Mono` 都运行在专用线程。操作符的执行位置取决于订阅、信号和调度器切换。[Reactor 线程和调度器](https://projectreactor.io/docs/core/release/reference/coreFeatures/schedulers.html)

对于同步操作较多的服务，可比较在 MVC 同步调用流程中限定资源，与保持异步链并把阻塞工作隔离到独立执行器两种方式。简单同步 HTTP 调用也可参考[选择 RestClient 或 WebClient](/ko/posts/2026-10-31-webclient-restclient-comparison/)。仅切换调度器不能解决 DB 或下游服务过载。

## 实际验证范围

[验证测试](https://github.com/youdozi/youdozi.github.io/blob/main/.pipeline/drafts/2026-11-09-spring-mvc-webclient-execution/src/test/java/example/ExecutionTest.java)在随机端口上的**真实 Tomcat 和本地 HTTP 服务器**运行。共通过十六项检查：普通请求线程和虚拟线程各八项。

- 同时存在两个 starter 时选择 Servlet 上下文、Tomcat 和 DispatcherServlet
- 组装管道时不发请求；订阅和重新订阅时发出请求
- 外部响应被暂缓时 `.block()` 请求线程等待，以及 `Mono` 进入 Servlet 异步处理
- 请求线程是否为虚拟线程，以及响应回调是否非阻塞、是否为虚拟线程
- 两条路径的 HTTP 错误映射为 502、管道超时映射为 504

若自行运行测试，将上述验证代码保存为 `src/test/java/example/ExecutionTest.java` 后执行。

```sh
gradle clean test
gradle test -Pvirtual=true --rerun-tasks
```

测试使用暂缓响应的 latch 观察状态，不根据短运行时间推断异步。未验证吞吐量比较、真实外部服务、DB 或 TLS、客户端断开或远程副作用取消。尤其是，管道取消不保证远程服务器工作取消或事务回滚。
