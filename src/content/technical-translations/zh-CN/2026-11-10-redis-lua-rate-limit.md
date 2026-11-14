---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2026-11-10-redis-lua-rate-limit",
  "routeSlug": "2026-11-10-redis-lua-rate-limit",
  "kind": "post",
  "title": "用 Redis 实现请求限流：Lua 原子性与 429、503 响应",
  "description": "使用 Spring MVC 与 Redis Lua 实现多服务器共享的请求限流，说明固定窗口 TTL、并发请求、Retry-After 和 Redis 故障策略。",
  "categories": [
    "springboot"
  ],
  "tags": [
    "redis",
    "rate-limit",
    "lua",
    "spring-mvc",
    "distributed-systems"
  ],
  "sourcePath": "src/content/posts/en/2026-11-10-redis-lua-rate-limit.md",
  "sourceSha256": "bffe243d3ec0d2693086eb4d708c74490b34a27af7c1735cf6a41c81eea561d5",
  "draftSha256": "9913276a85d3a1e66da506bf5dc6497807a6e881871abfff26d8fafb11d00734",
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

**要限制同一用户跨应用服务器的请求次数，需要在 Redis 中一起完成限额判断和计数更新。** 本文以 Lua 实现固定窗口限流，超限返回 `429`，Redis 无法判断时返回 `503`。

示例策略为**每个账户从首次允许的请求开始，在 10 秒内最多三次**。固定窗口是这里最简单的起点，并不等同于令牌桶或滑动窗口。复现环境为 Spring Boot 3.5.16、JDK 21、Gradle 8.14.3 和 Redis 8.2.1。这些版本为复现而固定，并非对生产环境最新补丁的推荐。

## 为什么不在应用中先 GET 再 INCR？

如果服务器 A 和 B 同时读到计数器 `2`，即使限额是 `3`，也可能同时放行两个请求。JVM 的 `synchronized` 不能锁住其他进程。`INCR` 本身是原子操作，但不会自动包含此前的准入判断。

在 `INCR` 之后另行发送 `EXPIRE` 还有一个问题：如果客户端在两条命令之间停止，键可能没有 TTL。Redis 的[官方 INCR 限流示例](https://redis.io/docs/latest/commands/incr/)也说明了这一竞态及 Lua 的用途。

下方脚本在首次请求时使用 `SET ... PX` 同时创建值和 TTL。后续请求在 Lua 中检查限额，只对允许的请求递增计数。被拒绝的请求既不改变计数，也不改变过期时间。

## 限流按什么顺序执行？

![服务器选择限流键，Redis Lua 检查计数和 TTL。允许时以 SET PX 或 INCR 记录请求，应用返回 200；超限时不改变状态，返回 429 与 Retry-After。连接或状态错误返回 503。](/assets/diagrams/technical/zh-CN-2026-11-10-redis-lua-rate-limit.svg)

蓝色区域表示 Redis 内部判断；HTTP 响应由应用生成。键不存在时开始新窗口；已存在的键必须包含正整数计数器和有效 TTL。限额统计准入次数，准入后的工作失败也不退还计数。

## 使用 Spring MVC 和 Redis Lua 实现限流

将以下六个文件保存到同一个 Gradle 项目。示例没有实现认证。`/demo` 把每个请求都视作单一 `demo-account`，该键是复现每用户策略的固定示例。服务器只绑定本地地址。

实际服务应根据**服务器验证过的主体**（例如已认证的 `Principal`）生成键。若信任任意 `userId` 请求头，调用方可通过更改它绕过限额。例如 `rl:orders:v1:<tenant-and-subject-digest>` 可以区分操作范围、策略版本与主体；可考虑使用基于服务器密钥的 HMAC 作为标识，而非个人信息原文。只在可信代理边界内解释转发的 IP 请求头。

### `settings.gradle`

```groovy
rootProject.name = 'redis-lua-rate-limit'
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
    implementation 'org.springframework.boot:spring-boot-starter-data-redis'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
application { mainClass = 'example.RateLimitApplication' }
test {
    useJUnitPlatform()
    systemProperty 'demo.redis.port', providers.gradleProperty('redisPort').getOrElse('6379')
}
```

### `src/main/resources/application.yml`

```yaml
server:
  address: 127.0.0.1
spring:
  data:
    redis:
      host: 127.0.0.1
      port: ${REDIS_PORT:6379}
      connect-timeout: 200ms
      timeout: 200ms
```

### `src/main/resources/rate-limit.lua`

```lua
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
if not limit or limit < 1 or limit > 1000000 or limit ~= math.floor(limit)
   or not window or window < 1 or window > 3600000 or window ~= math.floor(window) then
    return redis.error_reply('invalid rate limit policy')
end

local raw = redis.call('GET', KEYS[1])
if raw then
    local count = tonumber(raw)
    local ttl = redis.call('PTTL', KEYS[1])
    if not count or count < 1 or count ~= math.floor(count) or ttl < 0 then
        return redis.error_reply('invalid counter state')
    end
    if count >= limit then
        return {0, 0, ttl}
    end
    local updated = redis.call('INCR', KEYS[1])
    return {1, limit - updated, ttl}
end

redis.call('SET', KEYS[1], 1, 'PX', window)
return {1, limit - 1, window}
```

### `src/main/java/example/RedisRateLimiter.java`

```java
package example;

import java.time.Duration;
import java.util.List;
import org.springframework.core.io.ClassPathResource;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.script.DefaultRedisScript;
import org.springframework.stereotype.Component;

@Component
public class RedisRateLimiter {
    private static final DefaultRedisScript<List> SCRIPT = new DefaultRedisScript<>();
    static {
        SCRIPT.setLocation(new ClassPathResource("rate-limit.lua"));
        SCRIPT.setResultType(List.class);
    }
    private final StringRedisTemplate redis;

    public RedisRateLimiter(StringRedisTemplate redis) {
        this.redis = redis;
    }

    public Decision check(String key, int limit, Duration window) {
        long milliseconds = window.toMillis();
        if (key == null || key.isBlank() || key.length() > 160 || limit < 1 || limit > 1_000_000
                || milliseconds < 1 || milliseconds > 3_600_000) {
            throw new IllegalArgumentException("Invalid rate limit policy");
        }
        List<?> result = redis.execute(SCRIPT, List.of(key),
                Integer.toString(limit), Long.toString(milliseconds));
        if (result == null || result.size() != 3) {
            throw new IllegalStateException("Invalid limiter result");
        }
        return new Decision(((Number) result.get(0)).longValue() == 1,
                ((Number) result.get(1)).longValue(), ((Number) result.get(2)).longValue());
    }

    public record Decision(boolean allowed, long remaining, long ttlMillis) {
        public long retryAfterSeconds() {
            return Math.max(1, (ttlMillis + 999) / 1000);
        }
    }
}
```

### `src/main/java/example/RateLimitApplication.java`

```java
package example;

import java.time.Duration;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.dao.DataAccessException;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
@RestController
public class RateLimitApplication {
    private final RedisRateLimiter limiter;

    public RateLimitApplication(RedisRateLimiter limiter) {
        this.limiter = limiter;
    }

    public static void main(String[] args) {
        SpringApplication.run(RateLimitApplication.class, args);
    }

    @GetMapping("/demo")
    public ResponseEntity<String> demo() {
        try {
            var decision = limiter.check("rl:demo:v1:demo-account", 3, Duration.ofSeconds(10));
            if (!decision.allowed()) {
                return ResponseEntity.status(429)
                        .header("Retry-After", Long.toString(decision.retryAfterSeconds()))
                        .body("rate limit exceeded\n");
            }
            return ResponseEntity.ok("ok\n");
        } catch (DataAccessException | IllegalStateException unavailable) {
            return ResponseEntity.status(503).body("limiter unavailable\n");
        }
    }
}
```

此脚本使用一个键。在 Redis Cluster 中，它在该键所在的槽位运行。将一个脚本扩展为限制多个键时，需要围绕同槽约束重新设计。

`StringRedisTemplate` 使用字符串键和参数；脚本的数字数组以 `List` 返回。复用 `DefaultRedisScript` 的原因，以及默认执行器先用 `EVALSHA`、缓存未命中时再用 `EVAL` 的行为，见 [Spring Data Redis 脚本文档](https://docs.spring.io/spring-data/redis/reference/redis/scripting.html)。

## 应该看到什么响应？

运行前确保 Docker 可用，Redis 端口 `16379` 和应用端口 `8080` 未被其他进程占用。Redis 只暴露在主机回环地址；持久化和持久卷均已禁用。首次运行需下载 Redis 镜像和 Maven 依赖，因此需要网络。

```sh
docker run --rm -d --name redis-rate-limit-demo \
  -p 127.0.0.1:16379:6379 \
  redis:8.2.1-alpine@sha256:987c376c727652f99625c7d205a1cba3cb2c53b92b0b62aade2bd48ee1593232 \
  redis-server --save '' --appendonly no
REDIS_PORT=16379 gradle run
```

服务器就绪后，在另一个终端内的 10 秒内调用四次。

```sh
for attempt in 1 2 3 4; do
  curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8080/demo
done
curl -i http://127.0.0.1:8080/demo
```

在新窗口中连续发送这四个请求，预期状态码如下：

```text
200
200
200
429
```

拒绝响应的 `Retry-After` 是剩余 TTL 向上取整为整秒，最少一秒，具体值随调用时刻变化。`429` 和可选的 `Retry-After` 遵循 [RFC 6585 第 4 节](https://www.rfc-editor.org/rfc/rfc6585#section-4)。它不是考虑其他请求后的预留额度：等待期间如果其他请求用完额度，重试仍可能被拒绝。

停止 `gradle run` 并移除测试容器。

```sh
docker stop redis-rate-limit-demo
```

## 并发和错误方面验证了什么？

单独的复现测试使用本地 Docker 中的真实 Redis 和嵌入式 Tomcat。这些检查验证行为，而非吞吐量。

| 条件 | 观察结果 |
| --- | --- |
| 线程池对同一键同时发起 40 次调用 | 允许 3 次；Redis 计数器为 3 |
| 两个限制器对象使用同一 Redis 和键 | 共享限额。对象共享一个客户端 bean；测试没有启动两个独立 JVM。 |
| 允许三次后的请求 | 拒绝；计数器不递增，TTL 不延长 |
| 不同账户的键与已过期的键 | 其他键独立放行；过期后开启新窗口 |
| 值无效或键没有 TTL | 返回错误，不做任意修复 |
| 连续实际 HTTP 调用 | 三次 200 后返回 429，并带有 `Retry-After` |
| 计数器无效的 HTTP 请求 | 503 |
| 独立 TCP 端点接受连接但不返回 Redis 响应 | 限制器错误映射为 503 |

验证过的计数器必须有 TTL。[PTTL 文档](https://redis.io/docs/latest/commands/pttl/)定义 `-1` 表示没有 TTL，`-2` 表示键不存在。现有状态无效时静默添加 TTL 并放行可能掩盖策略错误，因此本实现返回错误。

**Lua 的原子执行不意味着出错时写入会自动回滚。** 应按[官方脚本文档](https://redis.io/docs/latest/develop/programmability/eval-intro/)区分执行隔离与错误处理。复现测试还确认，另一个脚本执行 `SET` 后故意返回错误时，写入的值仍然存在。本文脚本在写入前验证输入和现有状态，唯一的写入是最后的 `SET` 或 `INCR`。

## 生产环境应选择什么限制和故障策略？

**固定窗口不保证任意连续 10 秒内最多三次请求。** 如果在窗口结束前用完剩余额度，并在新窗口开始后立即请求，短时间内可能集中出现请求。需要某个时段的精确移动总量时可考虑滑动日志或滑动窗口；需要分别设置平均到达速率和允许突发时可考虑令牌桶。本文没有实现或比较这些算法的性能。

示例采用 **fail-closed**：Redis 出错时不放行请求。对支付等绕过限额代价高的操作，这可能合适，但 Redis 问题也会降低 API 可用性。对读取 API 等更重视可用性的场景，可考虑暂时使用受限的本地令牌桶放行。总额度可能随服务器数量增长，因此不等同于全局限额的保证。

200ms 设置是连接及命令超时，不保证整个 HTTP 请求在 200ms 内结束。排队、重连和调度时间也要分别考虑。代码未添加应用层重试；还需检查客户端的重连与命令重发策略。如果 Redis 已记录准入但响应丢失，调用方看到失败时次数仍可能已消耗。若重试的同一请求只能计一次，需要请求标识和单独的幂等策略。

如果 Redis 键因内存压力被淘汰，或重启、故障转移时计数器丢失，后续请求可能开启新窗口并被允许。原子 Lua 本身无法提供涵盖复制与恢复的全局限额。应共同管理专用实例、内存限额、淘汰策略、带策略版本的键、拒绝数、Redis 错误数和限流判断延迟。将每个键的标识直接放入指标标签，也会增加基数。

本次复现覆盖单个 Redis 实例的正常运行和部分错误处理。未测试 Redis Cluster 故障转移、多区域、真实 Redis 进程中断后的恢复或生产负载性能。限制请求启动次数也不能限制并发占用的数据库资源或长时间运行的请求数，需要时应另设并发限制。
