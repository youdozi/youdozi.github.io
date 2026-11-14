---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ru",
  "translationKey": "2026-11-09-spring-mvc-webclient-execution",
  "routeSlug": "2026-11-09-spring-mvc-webclient-execution",
  "kind": "post",
  "title": "Как работает WebClient в Spring MVC: block, Mono и виртуальные потоки",
  "description": "Разберите HTTP через WebClient и Reactor Netty в Spring MVC, сравните block и Mono и проверьте влияние виртуальных потоков.",
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
  "draftSha256": "a377223ae255c8d93773f07869a9aaf7b3a742b3f15c666412bbdb31958bc252",
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

**WebClient может выполнять неблокирующее HTTP-взаимодействие в Spring MVC, но вызов `.block()` в контроллере заставляет поток запроса MVC ждать результат.** Возврат `Mono` позволяет MVC адаптировать его к асинхронной обработке Servlet и освободить начальный поток запроса. Взаимодействие клиента и обработка серверного запроса — разные задачи.

Статья рассматривает **Spring MVC на Tomcat и WebClient с Reactor Netty**. Другой HTTP-коннектор может использовать другие имена потоков и ресурсы. Пример воспроизводится на Spring Boot 3.5.16, JDK 21 и Gradle 8.14.3; это не проверка всех текущих версий Boot.

## Превращает ли добавление WebClient сервер в WebFlux?

Серверный MVC и WebClient для исходящих вызовов выполняют разные роли. Здесь Tomcat и `DispatcherServlet` обрабатывают входящие запросы, а коннектор Reactor Netty WebClient — исходящий HTTP.

В Boot 3.5 совместное подключение `spring-boot-starter-web` и `spring-boot-starter-webflux` по умолчанию выбирает MVC. Это поддерживает приложения, добавляющие стартер WebFlux ради WebClient. Если тип приложения явно изменён или используется другая конфигурация сервера, проверьте выбор отдельно. [Выбор MVC и WebFlux в Boot](https://docs.spring.io/spring-boot/3.5/reference/web/reactive.html#web.reactive.webflux)

## Где расходятся `.block()` и возврат `Mono`?

![В пути block поток запроса Servlet ждёт, пока Netty выполняет HTTP-взаимодействие. В пути возврата Mono после подписки MVC взаимодействие Netty и асинхронная обработка Servlet могут перекрываться, после чего MVC повторно диспетчеризует результат.](/assets/diagrams/technical/ru-2026-11-09-spring-mvc-webclient-execution.svg)

Зелёным отмечены обязанности Servlet и MVC, синим — Reactor Netty. Две ветви асинхронного пути могут выполняться параллельно, и внешний ответ не обязательно приходит после освобождения начального потока. Диаграмма показывает сигналы успеха; сигналы ошибок в коде преобразуются в HTTP-статусы до обработки ошибок MVC.

| Этап | Вернуть значение после `.block()` | Вернуть `Mono` |
| --- | --- | --- |
| Подписка | Выполняет `.block()` | MVC подписывается на возвращённый тип |
| Ожидание исходящего HTTP | Поток запроса ожидает | Асинхронная обработка Servlet может освободить начальный поток |
| После получения тела ответа | Callback клиента передаёт результат и завершает ожидание | Сигнал результата передаётся асинхронной обработке MVC |
| Итоговый HTTP-ответ | MVC сериализует и записывает возвращённое значение | MVC повторно диспетчеризует, сериализует и записывает |

`retrieve().bodyToMono(...)` собирает конвейер запроса. На вновь созданный конвейер WebClient ниже нужно подписаться, чтобы начался HTTP-запрос. Повторная подписка может вызвать ещё один запрос, поэтому будьте осторожны с кодом, который сначала читает через `.block()`, а затем снова возвращает конвейер.

MVC адаптирует `Mono` с одним значением подобно `DeferredResult`. Когда результат готов, он повторно диспетчеризуется в контейнер Servlet для завершения ответа. Пул может повторно использовать тот же поток, поэтому не предполагайте, что поток повторной диспетчеризации обязательно отличается от исходного. Пока ответ открыт, соединение и ресурсы асинхронного запроса также сохраняются. Возврат `Mono` не делает всю запись ответа Servlet неблокирующей. Пример возвращает JSON с одним значением; потоковая передача и SSE — другие случаи. [Асинхронная обработка MVC и реактивные возвращаемые типы](https://docs.spring.io/spring-framework/reference/6.2/web/webmvc/mvc-ann-async.html)

## Два способа вызвать один внешний API

Сохраните файлы ниже в одном проекте. Он использует плагин `application`, а не Gradle-плагин Boot, и фиксирует Java toolchain на 21. Локальные проверки выполнены на Azul JDK 21.0.1; этот исторический патч не рекомендуется для новых production-сред.

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

`WebClient` повторно используется как bean и явно применяет коннектор Reactor Netty. `HttpClient.create()` в примере использует общие event loop и пул соединений по умолчанию; отдельный поток Netty для каждого исходящего запроса не создаётся. `callbackThread` — поток выполнения `map` после формирования тела ответа, не обязательно поток записи итогового Servlet-ответа. Переключение scheduler, например через `publishOn`, здесь не добавлено. [Коннекторы WebClient и общие ресурсы](https://docs.spring.io/spring-framework/reference/6.2/web/webflux-webclient/client-builder.html)

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

`/block` — путь для сравнения. Контроллер, способный завершиться асинхронным возвратом, может вернуть результирующий `Mono`, как `/async`, чтобы MVC подписался на него. Прямой вызов `.subscribe()` с немедленным ответом отделяет результат и ошибку исходящего вызова от первоначального HTTP-запроса. [Синхронный WebClient и возврат контроллера](https://docs.spring.io/spring-framework/reference/web/webflux-webclient/client-synchronous.html)

Трёхсекундный `timeout` ограничивает период от подписки до получения значения. Он не настраивает отдельно ожидание соединения из пула, подключение или каждый тайм-аут чтения ответа. HTTP-ошибки преобразуются в 502, а тайм-аут конвейера — в 504. Для ошибок соединения, пустого тела и бизнес-ошибок нужны отдельные контракты. `retrieve()` по умолчанию обрабатывает HTTP 4xx и 5xx как ошибки. [Ошибки retrieve](https://docs.spring.io/spring-framework/reference/6.2/web/webflux-webclient/client-retrieve.html)

### Локальный запуск

Вместо внешнего сервиса запустите локальный HTTP-сервер Python 3. `/value` возвращает `hello` через 0.2 секунды. Эта задержка задана для наблюдения за поведением, а не является измерением производительности.

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

Запустите сервер в первом терминале.

```sh
python3 upstream.py
```

Во втором терминале выберите JDK 21 и выполните проект с Gradle 8.14.3.

```sh
gradle run
```

В третьем терминале вызовите оба пути:

```sh
curl --fail --show-error --silent http://127.0.0.1:8080/block
curl --fail --show-error --silent http://127.0.0.1:8080/async
```

Оба возвращают JSON с `hello`. При обычных потоках запроса наблюдалось `requestVirtual=false`; callback Netty в этом примере имел `callbackVirtual=false` и `callbackNonBlocking=true`. Точные имена и номера потоков различаются между запусками. Один `mode` в JSON не доказывает освобождение потока запроса во время ожидания.

## Что изменится при включении виртуальных потоков?

После остановки предыдущего приложения выполните тот же код с настройкой виртуальных потоков.

```sh
gradle run --args='--spring.threads.virtual.enabled=true'
```

При этой настройке `requestVirtual` стал `true` в обоих путях. В пути `.block()` вызывающий виртуальный поток по-прежнему ждёт результат, однако обычное ожидание с возможностью park отличается от непрерывного занятия несущего платформенного потока. Отдельно проверьте pinning и особенности используемой JDK. [Планирование и pinning виртуальных потоков JDK 21](https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html) **Включение виртуальных потоков не превратило callback Reactor Netty этого примера в виртуальный поток.** [Настройка виртуальных потоков Boot](https://docs.spring.io/spring-boot/3.5/reference/features/spring-application.html#features.spring-application.virtual-threads)

Виртуальные потоки не увеличивают мощность внешнего сервиса, число HTTP-соединений или подключений к БД. Отдельно задавайте предел накопленных запросов, как в статье о [семафорах БД и контроле допуска](/ko/posts/2026-11-03-virtual-threads-db-semaphore/).

## Можно ли вызывать JDBC внутри callback?

Вызов WebClient из MVC не означает, что следующий `map` тоже выполнится в потоке запроса MVC. JDBC-запрос или длительное чтение файла внутри `map` этого примера могут заблокировать event loop Netty. И наоборот, не каждый `Mono` выполняется в отдельном потоке. Место выполнения оператора зависит от подписки, сигналов и переключений scheduler. [Потоки и schedulers Reactor](https://projectreactor.io/docs/core/release/reference/coreFeatures/schedulers.html)

В сервисе с большим количеством синхронных операций сравните ограничение ресурсов в синхронном потоке MVC с изоляцией блокирующей работы на отдельном исполнителе при сохранении асинхронной цепочки. Для простых синхронных HTTP-вызовов см. также [выбор RestClient или WebClient](/ko/posts/2026-10-31-webclient-restclient-comparison/). Само переключение scheduler не устраняет перегрузку БД или зависимых сервисов.

## Что действительно проверено

[Проверочные тесты](https://github.com/youdozi/youdozi.github.io/blob/main/.pipeline/drafts/2026-11-09-spring-mvc-webclient-execution/src/test/java/example/ExecutionTest.java) выполнялись с **реальными Tomcat и локальным HTTP-сервером** на случайных портах. Прошли шестнадцать проверок: по восемь с обычными и виртуальными потоками запроса.

- Выбор контекста Servlet, Tomcat и DispatcherServlet при наличии обоих стартеров
- Отсутствие запроса при сборке конвейера; запросы при подписке и повторной подписке
- Ожидание потока для `.block()` и вход в асинхронную обработку Servlet для `Mono` при удержании внешнего ответа
- Являются ли потоки запроса виртуальными, а callbacks — неблокирующими или виртуальными
- Преобразование HTTP-ошибок в 502 и тайм-аутов конвейера в 504 на обоих путях

Для самостоятельного запуска сохраните проверочный код выше как `src/test/java/example/ExecutionTest.java` и выполните его.

```sh
gradle clean test
gradle test -Pvirtual=true --rerun-tasks
```

Тесты наблюдают состояние с помощью latch, удерживающего ответ; они не определяют асинхронность по короткому времени выполнения. Не проверялись сравнение пропускной способности, реальные внешние сервисы, БД или TLS, отключения клиента и отмена удалённых побочных эффектов. В частности, отмена конвейера не гарантирует отмену работы или откат транзакции удалённого сервера.
