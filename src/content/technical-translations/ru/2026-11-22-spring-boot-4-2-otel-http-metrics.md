---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ru",
  "translationKey": "2026-11-22-spring-boot-4-2-otel-http-metrics",
  "routeSlug": "2026-11-22-spring-boot-4-2-otel-http-metrics",
  "kind": "post",
  "title": "Как соглашения OpenTelemetry меняют метрики HTTP в Spring Boot 4.2",
  "description": "Сравните метрики Prometheus для Spring MVC и RestClient в Spring Boot 4.2.0 и обновите запрос для ответов 404 по соглашениям OpenTelemetry.",
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
  "draftSha256": "a5abf34296a3dbc001f98d007a2fe36746c18793188880f0492615d130242cba",
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

**Если в Spring Boot 4.2.0 включить соглашения OpenTelemetry для наблюдений, метрика Prometheus для сервера Spring MVC меняется с `http_server_requests_seconds_count` на `http_server_request_duration_seconds_count`.** Метка для поиска ответов 404 также меняется с `status` на `http_response_status_code`. В том же приложении вызовы вышестоящего API через `RestClient` сохранили прежнее имя метрики и прежние метки. При обновлении панелей и оповещений проверяйте метрики входящих и исходящих запросов отдельно. [Примечания к выпуску Spring Boot 4.2](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.2-Release-Notes#semantic-conventions)

## Отправьте те же два запроса в обеих конфигурациях

Возьмите [пример поиска товара из предыдущей статьи](/en/posts/2026-11-22-spring-boot-4-2-restclient-migration/). Когда приложение получает `GET /products/{id}`, через `RestClient` оно вызывает `GET /items/{id}` у вышестоящего API. В этом упражнении для ID `42` приходят `200` и название `Keyboard`, а для ID `99` приходит `404` с пустым телом.

![Одно и то же приложение запускается с каждым набором соглашений. При каждом запуске запрашиваются товары 42 и 99, после чего вывод Prometheus сохраняется для сравнения метрик сервера Spring MVC и RestClient.](/assets/diagrams/technical/ru-2026-11-22-spring-boot-4-2-otel-http-metrics.svg)

На схеме показаны оба запуска. В каждом отправляются одни и те же запросы и отдельно сохраняется вывод Prometheus для сравнения.

Используйте Spring Boot 4.2.0 и JDK 21. Скопируйте `pom.xml` и `src/main/java/example/CatalogApplication.java` из предыдущей статьи. Удалите зависимость `spring-boot-starter-webmvc-test`, которая здесь не нужна, и добавьте в Maven две зависимости ниже. В `CatalogApplication.java` уже внедряется настроенный Boot `RestClient.Builder`. [Документация Spring Boot по метрикам HTTP-клиента](https://docs.spring.io/spring-boot/reference/actuator/metrics.html#actuator.metrics.supported.http-clients)

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

Чтобы упаковать приложение в исполняемый JAR, добавьте следующую конфигурацию в элемент `<project>` файла `pom.xml`.

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

В одном терминале запустите локальный сервер вместо вышестоящего API. Он отдаёт файл по адресу `/items/42` и возвращает 404 для `/items/99`, потому что такого файла нет. Используйте локальное окружение разработки, где оба порта свободны.

```sh
upstream_dir=$(mktemp -d)
mkdir -p "$upstream_dir/items"
printf '%s' Keyboard > "$upstream_dir/items/42"
python3 -m http.server 18081 --bind 127.0.0.1 --directory "$upstream_dir"
```

В другом терминале соберите приложение из корня проекта Maven и запустите с соглашениями по умолчанию. Откройте для сбора метрик конечную точку Actuator и привяжите приложение к адресу loopback.

```sh
mvn package

java -jar target/restclient-migration-1.0.0.jar \
  --server.address=127.0.0.1 \
  --server.port=18080 \
  --catalog.base-url=http://127.0.0.1:18081 \
  --management.endpoints.web.exposure.include=health,prometheus
```

Когда приложение запустится, отправьте следующие запросы из третьего терминала. Проверьте оба ответа и сохраните вывод Prometheus, в котором есть серии `_count` с накопленными счётчиками запросов.

```sh
curl -sS -i http://127.0.0.1:18080/products/42
curl -sS -i http://127.0.0.1:18080/products/99
curl -fsS http://127.0.0.1:18080/actuator/prometheus > default.prom
```

Остановите приложение и запустите его той же командой `java -jar`, добавив `--management.observations.conventions=open-telemetry`. Повторите все три запроса и сохраните последний ответ как `open-telemetry.prom`. Новый процесс обнуляет счётчики первого запуска.

```sh
grep -E '^http_(server|client).*_count\{.*(/products/|/items/)' \
  default.prom open-telemetry.prom
```

## Что изменилось в собранных метриках

Я запустил обе конфигурации с JDK 21.0.1, Maven 3.9.11, Spring Boot 4.2.0 и встроенным Tomcat. При каждом запуске один запрос вернул `200`, а другой — `404`. Статус и тело каждого из четырёх ответов соответствовали ожидаемым.

| Метрика сервера MVC | Соглашения по умолчанию | Соглашения OpenTelemetry |
| --- | --- | --- |
| Счётчик запросов Prometheus | `http_server_requests_seconds_count` | `http_server_request_duration_seconds_count` |
| Метка метода HTTP | `method` | `http_request_method` |
| Метка статуса ответа | `status` | `http_response_status_code` |
| Метка маршрута | `uri` | `http_route` |
| Значение маршрута в примере | `/products/{id}` | `/products/{id}` |

Метка маршрута содержит шаблон с `{id}`. Ниже приведены собранные серии для 404 с метками, которые используются в запросах. Счётчик ответов 404 со стороны сервера в каждом запуске составил `1`.

```text
http_server_requests_seconds_count{status="404",uri="/products/{id}"} 1
http_server_request_duration_seconds_count{http_response_status_code="404",http_route="/products/{id}"} 1
```

В тех же выгрузках обе конфигурации записали исходящие запросы в `http_client_requests_seconds_count` с метками `method="GET"`, `uri="/items/{id}"` и либо `status="200"`, либо `status="404"`. Результат относится к сочетанию автоконфигурации Boot и `RestClient.Builder` из примера. В упражнении метрики читаются из реестра Prometheus в Micrometer. Соглашение для наблюдений и способ экспорта данных задаются отдельно. [Документация Spring Boot по наблюдаемости](https://docs.spring.io/spring-boot/reference/actuator/observability.html#actuator.observability.semantic-conventions)

## Обновите запрос для ответов 404

Панель Grafana с соглашениями по умолчанию может получить накопленное число ответов 404 для маршрута следующим запросом.

```text
sum(http_server_requests_seconds_count{uri="/products/{id}",status="404"})
```

Для соглашений OpenTelemetry измените имя метрики и обе метки.

```text
sum(http_server_request_duration_seconds_count{http_route="/products/{id}",http_response_status_code="404"})
```

Я проверил запросы на собранных сериях через `promtool` из Prometheus 3.5.0. Каждый запрос вернул `1` при соответствующем наборе соглашений и пустой результат при другом наборе.

Запросы сравнивают накопленные счётчики одного приложения. Если панель в рабочей среде уже показывает число запросов в секунду за недавнее окно, сохраните существующее вычисление, например `rate(...[5m])`, и обновите селектор метрики внутри. Пока Prometheus собирает метрики и со старых, и с новых версий, проверяйте запросом по каждой цели развёртывания, какое имя она сообщает. [Основы запросов Prometheus](https://prometheus.io/docs/prometheus/latest/querying/basics/) · [Документация Prometheus по `rate()`](https://prometheus.io/docs/prometheus/latest/querying/functions/#rate)

Если вы задали имя серверной метрики через `management.observations.http.server.requests.name`, сначала проверьте панели и оповещения, которые ссылаются на это имя. При соглашениях OpenTelemetry параметр не действует. Как перейти от метрик к журналам и трассировке отдельного запроса, читайте в статье [Как связать журналы и трассировки в Grafana LGTM](/en/posts/2026-11-02-grafana-lgtm-log-trace/). [Примечания к выпуску Spring Boot 4.2](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.2-Release-Notes#semantic-conventions)
