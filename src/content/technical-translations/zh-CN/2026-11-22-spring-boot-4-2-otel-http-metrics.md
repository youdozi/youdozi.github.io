---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2026-11-22-spring-boot-4-2-otel-http-metrics",
  "routeSlug": "2026-11-22-spring-boot-4-2-otel-http-metrics",
  "kind": "post",
  "title": "OpenTelemetry 约定如何改变 Spring Boot 4.2 的 HTTP 指标",
  "description": "比较 Spring Boot 4.2.0 中 Spring MVC 和 RestClient 的 Prometheus 指标，并按 OpenTelemetry 约定更新 404 查询。",
  "categories": [
    "springboot"
  ],
  "tags": [
    "spring-boot",
    "opentelemetry",
    "prometheus",
    "micrometer",
    "restclient"
  ],
  "sourcePath": "src/content/posts/en/2026-11-22-spring-boot-4-2-otel-http-metrics.md",
  "sourceSha256": "184d3ca3476cfc05571ad97d60ef35f2d4c93f54cb152df388401376edc0ef57",
  "draftSha256": "6a35d008247ecb0e37e56aa4387cdae1bd43de1ad8fae7c58261713994672875",
  "manifestPath": ".pipeline/technical-translations/batch-185/manifest.json",
  "manifestSha256": "3281e1d3e7c9b3abbb6c101d911dd0fcdee7dd54f7034838135f391123b6fb44",
  "publishedAt": "2026-11-23T00:19:14.218Z",
  "updatedAt": "2026-11-23T00:19:14.218Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 185,
    "approvedAt": "2026-11-23T00:19:14.218Z",
    "basis": "The site owner explicitly requested missing supported locales for the eight articles published in PRs #177–#184. This authorizes publication of the 48 editions enumerated in this batch."
  }
}
---

**在 Spring Boot 4.2.0 中启用 OpenTelemetry 观测约定后，Spring MVC 服务器的 Prometheus 指标会从 `http_server_requests_seconds_count` 改为 `http_server_request_duration_seconds_count`。** 用来查找 404 响应的标签也会从 `status` 变为 `http_response_status_code`。在同一应用中，`RestClient` 对上游 API 的调用仍沿用原有指标名称和标签。更新仪表板与告警时，请分别检查入站和出站请求指标。 [Spring Boot 4.2 发行说明](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.2-Release-Notes#semantic-conventions)

## 用两种配置各跑一遍同样的请求

采用 [上一篇的商品查询示例](/en/posts/2026-11-22-spring-boot-4-2-restclient-migration/)。应用收到 `GET /products/{id}` 时，通过 `RestClient` 调用上游 API 的 `GET /items/{id}`。本练习中，ID `42` 返回 `200` 和商品名 `Keyboard`，ID `99` 则返回响应体为空的 `404`。

![同一应用在每种约定下运行一次。每次都请求商品 42 和 99，然后保存 Prometheus 输出，以比较 Spring MVC 服务器和 RestClient 的指标。](/assets/diagrams/technical/zh-CN-2026-11-22-spring-boot-4-2-otel-http-metrics.svg)

图中展示两次运行的流程。两次运行发出同样的请求，并分别保存 Prometheus 输出以供比较。

使用 Spring Boot 4.2.0 和 JDK 21。复制上一篇中的 `pom.xml` 和 `src/main/java/example/CatalogApplication.java`。移除本练习用不到的 `spring-boot-starter-webmvc-test` 依赖，再将下列两个依赖加入 Maven 依赖列表。`CatalogApplication.java` 已注入由 Boot 配置的 `RestClient.Builder`。 [Spring Boot HTTP 客户端指标文档](https://docs.spring.io/spring-boot/reference/actuator/metrics.html#actuator.metrics.supported.http-clients)

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>
```

要把应用打包成可执行 JAR，请在 `pom.xml` 的 `<project>` 下加入以下配置。

```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-maven-plugin</artifactId>
        </plugin>
    </plugins>
</build>
```

在一个终端中启动本地服务器来模拟上游 API。它提供 `/items/42` 对应的文件。由于 `/items/99` 对应文件不存在，该路径返回 404。使用两个端口均空闲的本地开发环境。

```sh
upstream_dir=$(mktemp -d)
mkdir -p "$upstream_dir/items"
printf '%s' Keyboard > "$upstream_dir/items/42"
python3 -m http.server 18081 --bind 127.0.0.1 --directory "$upstream_dir"
```

另开一个终端，在 Maven 项目根目录构建应用，并按默认约定启动。暴露供抓取的 Actuator 端点，并将应用绑定到环回地址。

```sh
mvn package

java -jar target/restclient-migration-1.0.0.jar \
  --server.address=127.0.0.1 \
  --server.port=18080 \
  --catalog.base-url=http://127.0.0.1:18081 \
  --management.endpoints.web.exposure.include=health,prometheus
```

应用启动后，在第三个终端发出以下请求。检查前两个响应，再保存 Prometheus 输出。输出包含统计累计请求数的 `_count` 序列。

```sh
curl -sS -i http://127.0.0.1:18080/products/42
curl -sS -i http://127.0.0.1:18080/products/99
curl -fsS http://127.0.0.1:18080/actuator/prometheus > default.prom
```

停止应用后，用同一个 `java -jar` 命令加上 `--management.observations.conventions=open-telemetry` 重启。再次发送全部三个请求，将最后一个响应保存为 `open-telemetry.prom`。启动新进程会重置首次运行的计数器。

```sh
grep -E '^http_(server|client).*_count\{.*(/products/|/items/)' \
  default.prom open-telemetry.prom
```

## 采集到的指标发生了哪些变化？

我使用 JDK 21.0.1、Maven 3.9.11、Spring Boot 4.2.0 和嵌入式 Tomcat 分别运行了两种配置。每次运行都有一次请求返回 `200`，另一次返回 `404`。四次响应的状态和响应体都符合预期。

| MVC 服务器指标 | 默认约定 | OpenTelemetry 约定 |
| --- | --- | --- |
| Prometheus 请求计数 | `http_server_requests_seconds_count` | `http_server_request_duration_seconds_count` |
| HTTP 方法标签 | `method` | `http_request_method` |
| 响应状态标签 | `status` | `http_response_status_code` |
| 路由标签 | `uri` | `http_route` |
| 本例中的路由值 | `/products/{id}` | `/products/{id}` |

路由标签包含带 `{id}` 的路由模板。下面是采集到的 404 时间序列，只保留查询用到的标签。每次运行中，服务器端的 404 计数均为 `1`。

```text
http_server_requests_seconds_count{status="404",uri="/products/{id}"} 1
http_server_request_duration_seconds_count{http_response_status_code="404",http_route="/products/{id}"} 1
```

同一批数据中，两种配置都将出站请求计入 `http_client_requests_seconds_count`，标签为 `method="GET"`、`uri="/items/{id}"`，以及 `status="200"` 或 `status="404"`。这个结果适用于示例中的 Boot 自动配置与 `RestClient.Builder` 的组合。本练习通过 Micrometer 的 Prometheus 注册表读取指标。观测约定和数据导出方式分别设置。 [Spring Boot 可观测性文档](https://docs.spring.io/spring-boot/reference/actuator/observability.html#actuator.observability.semantic-conventions)

## 更新 404 查询

采用默认约定时，Grafana 面板可以用以下查询统计这条路由的累计 404 次数。

```text
sum(http_server_requests_seconds_count{uri="/products/{id}",status="404"})
```

采用 OpenTelemetry 约定时，更改指标名称和两个标签。

```text
sum(http_server_request_duration_seconds_count{http_route="/products/{id}",http_response_status_code="404"})
```

我用 Prometheus 3.5.0 的 `promtool` 对采集的序列测试了这些查询。查询与约定匹配时返回 `1`，使用另一种约定的数据时结果为空。

这些查询比较单个应用的累计次数。如果生产面板已经显示近期时间窗口内的每秒请求数，请保留原有计算（如 `rate(...[5m])`），只更新内部的指标选择器。如果 Prometheus 同时抓取新旧版本，请按部署目标查询，确认各目标仍在上报哪个指标名称。 [Prometheus 查询基础](https://prometheus.io/docs/prometheus/latest/querying/basics/) · [Prometheus `rate()` 文档](https://prometheus.io/docs/prometheus/latest/querying/functions/#rate)

如果用 `management.observations.http.server.requests.name` 设置了服务器指标名称，请先检查引用自定义名称的面板和告警。该设置在 OpenTelemetry 约定下无效。如需从指标追查单个请求的日志和链路，请参见 [在 Grafana LGTM 中关联日志与链路追踪](/en/posts/2026-11-02-grafana-lgtm-log-trace/)。 [Spring Boot 4.2 发行说明](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.2-Release-Notes#semantic-conventions)
