---
{
  "state": "draft",
  "language": "ru",
  "translationKey": "2026-11-10-redis-lua-rate-limit",
  "title": "Ограничение запросов с Redis и Lua в Spring MVC",
  "description": "Реализуйте фиксированное окно с Redis Lua, различайте ответы 429 и 503 и учитывайте конкуренцию, TTL и ошибки.",
  "sourcePath": "src/content/posts/en/2026-11-10-redis-lua-rate-limit.md",
  "sourceSha256": "bffe243d3ec0d2693086eb4d708c74490b34a27af7c1735cf6a41c81eea561d5"
}
---

**Чтобы ограничить запросы одного пользователя между серверами приложений, принимайте решение и обновляйте счётчик совместно в Redis.** В статье реализовано фиксированное окно на Lua: при превышении возвращается `429`, а если Redis не может определить результат — `503`.

Пример политики разрешает **не более трёх запросов на аккаунт за 10 секунд с первого разрешённого запроса**. Фиксированное окно здесь — простая отправная точка; оно не эквивалентно token bucket или скользящему окну. Среда: Spring Boot 3.5.16, JDK 21, Gradle 8.14.3 и Redis 8.2.1. Версии закреплены для воспроизведения, а не рекомендованы как последние production-патчи.

## Почему не стоит выполнять GET, а затем INCR в приложении?

Если серверы A и B прочитают счётчик `2`, они могут оба разрешить запрос при лимите `3`. `synchronized` в JVM не блокирует другие процессы. `INCR` атомарен, но автоматически не включает предшествующее решение о допуске.

Отдельный `EXPIRE` после `INCR` создаёт другую проблему: если клиент остановится между командами, ключ может остаться без TTL. [Официальный пример ограничения с INCR](https://redis.io/docs/latest/commands/incr/) Redis также описывает эту гонку и применение Lua.

При первом запросе скрипт ниже создаёт значение и TTL совместно через `SET ... PX`. При следующих запросах он проверяет лимит внутри Lua и увеличивает счётчик только для разрешённых запросов. Отказанные запросы не меняют ни счётчик, ни срок истечения.

## В каком порядке применяется лимит?

![Сервер выбирает ключ лимита, затем Redis Lua проверяет счётчик и TTL. При допуске SET PX или INCR записывает запрос, а приложение возвращает 200; при превышении возвращаются 429 и Retry-After без изменения состояния. Ошибки соединения или состояния дают 503.](2026-11-10-redis-lua-rate-limit.svg)

Синяя область показывает решение внутри Redis; HTTP-ответ формирует приложение. Отсутствующий ключ начинает новое окно. Существующий ключ должен содержать положительный целый счётчик и действующий TTL. Лимит считает допуски; если работа после допуска завершилась ошибкой, счётчик не возвращается.

## Реализуем лимит с Spring MVC и Redis Lua

Сохраните шесть файлов в одном проекте Gradle. Аутентификация не реализована. `/demo` обрабатывает каждый запрос как один аккаунт `demo-account`, поэтому ключ — фиксированный пример политики на пользователя. Сервер слушает только локальный адрес.

В реальном сервисе выводите ключ из **проверенного сервером субъекта**, например аутентифицированного `Principal`. Доверие произвольному заголовку `userId` позволяет обойти лимит изменением значения. Например, `rl:orders:v1:<tenant-and-subject-digest>` позволяет различать область операции, версию политики и субъекта; вместо открытых персональных данных рассмотрите идентификатор вроде HMAC на секрете сервера. Интерпретируйте заголовки переданного IP только внутри границы доверенных прокси.

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

Скрипт использует один ключ. В Redis Cluster он выполняется в слоте этого ключа. Расширение одного скрипта на несколько ключей требует пересмотра ограничения на один слот.

`StringRedisTemplate` использует строковые ключи и аргументы; числовой массив скрипта возвращается как `List`. Причина повторного использования `DefaultRedisScript` и поведение стандартного исполнителя — `EVALSHA` с последующим `EVAL` при отсутствии в кеше — описаны в [документации Spring Data Redis по скриптам](https://docs.spring.io/spring-data/redis/reference/redis/scripting.html).

## Какие ответы ожидать?

Запустите пример при доступном Docker и свободных портах Redis `16379` и приложения `8080`. Redis доступен только на loopback-адресе хоста; постоянное хранение и постоянные тома выключены. При первом запуске загружаются образ Redis и зависимости Maven, поэтому нужна сеть.

```sh
docker run --rm -d --name redis-rate-limit-demo \
  -p 127.0.0.1:16379:6379 \
  redis:8.2.1-alpine@sha256:987c376c727652f99625c7d205a1cba3cb2c53b92b0b62aade2bd48ee1593232 \
  redis-server --save '' --appendonly no
REDIS_PORT=16379 gradle run
```

После готовности сервера выполните четыре вызова за 10 секунд из другого терминала.

```sh
for attempt in 1 2 3 4; do
  curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8080/demo
done
curl -i http://127.0.0.1:8080/demo
```

При последовательной отправке этих четырёх запросов в новом окне ожидаются следующие коды:

```text
200
200
200
429
```

`Retry-After` при отказе — оставшийся TTL, округлённый вверх до целых секунд, не менее одной секунды. Значение зависит от момента вызова. Значение `429` и необязательного `Retry-After` следует [RFC 6585, раздел 4](https://www.rfc-editor.org/rfc/rfc6585#section-4). Это не резервирование с учётом других запросов: повтор может снова получить отказ, если другой запрос за это время исчерпает лимит.

Остановите `gradle run` и удалите тестовый контейнер.

```sh
docker stop redis-rate-limit-demo
```

## Что проверено для конкуренции и ошибок?

Отдельные воспроизводимые тесты использовали реальный Redis в локальном Docker и встроенный Tomcat. Проверялось поведение, а не пропускная способность.

| Условие | Наблюдаемый результат |
| --- | --- |
| 40 одновременных вызовов одного ключа из пула потоков | 3 допущены; счётчик Redis 3 |
| Два объекта ограничителя с одним Redis и ключом | Разделяют лимит. Объекты используют один bean клиента; две отдельные JVM не запускались. |
| Запрос после трёх разрешённых вызовов | Отказ без увеличения счётчика и продления TTL |
| Другой ключ аккаунта и ключ с истёкшим TTL | Другой ключ разрешается независимо; после истечения начинается новое окно |
| Недопустимое значение или ключ без TTL | Ошибка без произвольного исправления |
| Последовательные реальные HTTP-вызовы | Три ответа 200, затем 429 с `Retry-After` |
| HTTP-запрос с некорректным счётчиком | 503 |
| Отдельный TCP endpoint принимает соединения, но Redis не отвечает | Ошибка ограничителя преобразуется в 503 |

Проверенный счётчик должен иметь TTL. [Документация PTTL](https://redis.io/docs/latest/commands/pttl/) определяет `-1` как отсутствие TTL, а `-2` — как отсутствие ключа. Если при неверном состоянии молча добавить TTL и разрешить запрос, можно скрыть ошибку политики, поэтому реализация возвращает ошибку.

**Атомарное выполнение Lua не означает автоматического отката записей при ошибке.** Различайте изоляцию выполнения и обработку ошибок из [официальной документации по скриптам](https://redis.io/docs/latest/develop/programmability/eval-intro/). В отдельном тесте также подтвердили, что значение сохраняется после `SET`, если затем скрипт намеренно возвращает ошибку. Скрипт статьи проверяет вход и состояние до записи и ограничивает запись последним `SET` или `INCR`.

## Какие лимиты и политики отказа выбрать в эксплуатации?

**Фиксированное окно не гарантирует максимум трёх запросов в любом последовательном интервале 10 секунд.** Если использовать оставшийся лимит непосредственно перед концом окна и снова запросить сразу после начала следующего, запросы могут сконцентрироваться за короткий период. Для точной скользящей суммы рассмотрите скользящий журнал или окно, а для отдельной настройки средней частоты и допустимого всплеска — token bucket. Эти алгоритмы здесь не реализованы и не измерены сравнительно.

Пример использует **fail-closed**: при ошибке Redis запросы не пропускаются. Это подходит для рассмотрения при высокой цене обхода, например платежах, но сбой Redis также снижает доступность API. Если доступность важнее, например для API чтения, можно временно разрешать запросы по ограниченной локальной корзине. Общий лимит может расти с числом серверов, поэтому он не эквивалентен глобальному.

Настройка 200ms задаёт тайм-аут соединения и команды, но не гарантирует завершение всего HTTP-запроса за 200ms. Отдельно учитывайте очереди, переподключение и планирование. В коде нет повторов уровня приложения; проверьте также переподключение клиента и повторную отправку команд. Если Redis записал допуск, но ответ потерян, счётчик может быть израсходован, хотя вызывающая сторона увидит ошибку. Чтобы повторный запрос учитывался один раз, нужны идентификатор запроса и отдельная политика идемпотентности.

Если ключ Redis вытеснен при нехватке памяти или счётчик утрачен при перезапуске либо failover, следующий запрос может начать новое окно и получить допуск. Один атомарный Lua не обеспечивает глобальный лимит с учётом репликации и восстановления. Управляйте выделенными инстансами, лимитами памяти, политикой вытеснения, версиями ключей политики, числом отказов и ошибок Redis и задержкой решения. Добавление идентификаторов отдельных ключей в метки метрик увеличивает кардинальность.

Эта проверка охватывает нормальную работу одного Redis и некоторые ошибки. Failover Redis Cluster, несколько регионов, восстановление после реальной остановки процесса Redis и производственная нагрузка не тестировались. Лимит числа начинаемых запросов не ограничивает одновременное занятие БД или число длительных запросов; при необходимости задавайте отдельное ограничение конкурентности.
