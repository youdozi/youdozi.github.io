---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ru",
  "translationKey": "2026-11-02-grafana-lgtm-log-trace",
  "routeSlug": "2026-11-02-grafana-lgtm-log-trace",
  "kind": "post",
  "title": "Корреляция логов и трасс в Grafana LGTM: от Loki к Tempo по trace_id",
  "description": "Собирайте логи и спаны с OpenTelemetry и связывайте Loki и Tempo в Grafana. Исполняемая лабораторная работа с Docker/Python и решения для отсутствующих ID и пустых результатов запросов.",
  "categories": [
    "architecture"
  ],
  "tags": [
    "grafana",
    "loki",
    "tempo",
    "opentelemetry",
    "observability",
    "tracing"
  ],
  "sourcePath": "src/content/posts/en/2026-11-02-grafana-lgtm-log-trace.md",
  "sourceSha256": "ea19472a99523fa3e56c758e753b8333671691c4efd6f1dec67f9e59c3eaf558",
  "draftSha256": "718dbe2b24692a09d3844950204f0e3d83a87f1fc22d9d7227d70aec94314440",
  "manifestPath": ".pipeline/technical-translations/batch-135/manifest.json",
  "manifestSha256": "7b0ee87cd56b365db57f3da54bd97961e76f22898e553e01c3f514dcad33abc9",
  "publishedAt": "2026-11-02T11:48:15.897Z",
  "updatedAt": "2026-11-02T11:48:15.897Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 135,
    "approvedAt": "2026-11-02T11:48:15.897Z",
    "basis": "사용자가 한국어·영어 LGTM 글 게시 후 다국어 지원도 해줘라고 요청하여 기존 지원 언어 6개의 전체 번역·현지화 그림 게시를 승인함. AI 번역 검토와 사용자 게시 승인은 별도임."
  }
}
---

**Чтобы связать логи и трассы в Grafana LGTM, отправляйте логи и спаны с одинаковым `trace_id`, затем настройте источники данных Loki и Tempo в Grafana.** Это позволит открыть путь выполнения, стоящий за записью об ошибке, и вернуться от спана к связанным логам.

LGTM означает Loki (логи), Grafana (запросы и визуализация), Tempo (трассы) и Mimir (метрики). В этом руководстве рассматривается корреляция логов и трасс. Более широкий рабочий процесс эксплуатации описан в статье [Эксплуатация AI-агентов](/en/posts/2026-10-31-ai-agent-operations/).

## Какие идентификаторы должны совпадать?

Трасса представляет одно выполнение, а спаны — отдельные операции внутри него. В примере родительский спан `checkout` и дочерний спан `inventory.lookup` имеют одинаковый ID трассы, но разные ID спанов. Если записывать лог внутри активного спана, запись может содержать контекст этого спана. Для корреляции между отдельными сервисами также необходимо передавать контекст, например через HTTP-заголовок `traceparent`. [Передача контекста OpenTelemetry](https://opentelemetry.io/docs/concepts/context-propagation/)

![Пример на Python записывает логи внутри активных спанов; OpenTelemetry Collector направляет логи в Loki, а трассы в Tempo; Grafana запрашивает оба хранилища по одному trace_id](/assets/diagrams/technical/ru-2026-11-02-grafana-lgtm-log-trace.svg)

Связь между хранилищами обеспечивает функция запросов Grafana. Loki не пересылает логи в Tempo, а Grafana не создаёт отсутствующие трассы. В этом примере спаны создаются вручную в одном процессе. HTTP-сервер, вызовы между сервисами и база данных складских остатков здесь не реализованы.

## Подготовка локальной среды сбора

Создайте следующие четыре файла в пустом каталоге в среде с поддержкой Docker и виртуальных окружений Python. Проверенная комбинация: **Python 3.13.0, OpenTelemetry Python 1.45.2 и `grafana/otel-lgtm` 0.39.0**. Образ содержит Grafana 13.3.0, Loki 3.7.9, Tempo 3.1.1 и Collector 0.164.0.

[Официальный образ Docker LGTM](https://grafana.com/docs/opentelemetry/docker-lgtm/) предназначен для разработки, демонстраций и тестирования. Его хранилище метрик — Prometheus; в этом руководстве производственный кластер Mimir не разворачивается. Для логов и трасс мы используем входящие в образ Collector, Loki, Tempo и Grafana.

### `compose.yaml`

```yaml
services:
  lgtm:
    image: grafana/otel-lgtm:0.39.0@sha256:4c8056c9c05fcb3c8fd93800e85334bfd79b4d0271b47a54a121a64af41fe1fe
    ports:
      - '127.0.0.1:13000:3000'
      - '127.0.0.1:14318:4318'
    environment:
      GF_AUTH_ANONYMOUS_ENABLED: 'true'
      GF_AUTH_ANONYMOUS_ORG_ROLE: Editor
    volumes:
      - ./datasources.yaml:/otel-lgtm/grafana/conf/provisioning/datasources/grafana-datasources.yaml:ro
```

Это локальная лабораторная среда. Анонимные пользователи получают права Editor для Explore, а Grafana и OTLP привязаны к `127.0.0.1` хоста. Для эксплуатации в производственной среде нужны аутентификация, TLS и ограничения доступа. Python на хосте использует порт `14318`, а Collector в контейнере — `4318`. URL источников данных используют loopback внутри контейнера Grafana. Если Loki и Tempo работают в отдельных контейнерах, используйте вместо него DNS-имена сервисов.

### `datasources.yaml`

```yaml
apiVersion: 1
datasources:
  - name: Tempo
    type: tempo
    uid: tempo
    url: http://127.0.0.1:3200
    jsonData:
      tracesToLogsV2:
        datasourceUid: loki
        spanStartTimeShift: '-2s'
        spanEndTimeShift: '2s'
        tags:
          - key: service.name
            value: service_name
        customQuery: true
        query: '{$${__tags}} | trace_id = "$${__trace.traceId}"'
  - name: Loki
    type: loki
    uid: loki
    url: http://127.0.0.1:3100
    jsonData:
      derivedFields:
        - name: trace_id
          matcherType: label
          matcherRegex: '^trace_id$'
          datasourceUid: tempo
          url: '$${__value.raw}'
          urlDisplayLabel: View trace
```

`tracesToLogsV2` формирует запрос от спана к логам; `derivedFields` создаёт ссылку от лога к Tempo. Сопоставьте `service.name` с `service_name` в Loki, затем отфильтруйте записи по ID трассы. При включённом `customQuery` этот фильтр явно входит в запрос. Настройка обоих направлений описана в [параметрах корреляции Grafana](https://grafana.com/docs/grafana/latest/datasources/tempo/configure-tempo-data-source/configure-trace-to-logs/).

`$${...}` сохраняет переменные в **файле provisioning Grafana**. На этот отдельно подключённый файл не распространяется интерполяция строк Compose. При вводе значений непосредственно в интерфейсе Grafana используйте `${...}`. Эта конфигурация ограничивает [настройки источников данных официального образа](https://github.com/grafana/docker-otel-lgtm/blob/v0.39.0/docker/grafana-datasources.yaml) корреляцией логов и трасс.

При приёме по OTLP `trace_id` запрашивается как структурированные метаданные Loki, а не как JSON-поле в теле лога, поэтому в этом примере не нужен `| json`. Параметр Grafana `matcherType: label` определяет способ поиска поля; он не превращает ID трассы в индексную метку Loki. [Правила хранения OTLP в Loki](https://grafana.com/docs/loki/latest/send-data/otel/)

### `requirements.txt`

```text
opentelemetry-sdk==1.45.2
opentelemetry-exporter-otlp-proto-http==1.45.2
```

### `demo.py`

```python
import logging

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import ALWAYS_ON
from opentelemetry.trace import Status, StatusCode

resource = Resource.create({"service.name": "checkout-demo"})
traces = TracerProvider(resource=resource, sampler=ALWAYS_ON)
traces.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(
    endpoint="http://127.0.0.1:14318/v1/traces")))
trace.set_tracer_provider(traces)
logs = LoggerProvider(resource=resource)
logs.add_log_record_processor(BatchLogRecordProcessor(OTLPLogExporter(
    endpoint="http://127.0.0.1:14318/v1/logs")))
handler = LoggingHandler(logger_provider=logs)
logger = logging.getLogger("checkout-demo")
logger.setLevel(logging.INFO)
logger.propagate = False
logger.addHandler(handler)
tracer = trace.get_tracer("checkout-demo")

try:
    with tracer.start_as_current_span("checkout") as checkout:
        trace_id = f"{checkout.get_span_context().trace_id:032x}"
        logger.info("checkout_started")
        with tracer.start_as_current_span("inventory.lookup") as inventory:
            logger.error("inventory_unavailable")
            inventory.set_status(Status(StatusCode.ERROR, "demo failure"))
        checkout.set_status(Status(StatusCode.ERROR, "inventory unavailable"))
    assert logs.force_flush(timeout_millis=10000), "log flush timed out"
    assert traces.force_flush(timeout_millis=10000), "trace flush timed out"
    print(f"trace_id={trace_id}")
finally:
    logger.removeHandler(handler)
    logs.shutdown()
    traces.shutdown()
```

`inventory_unavailable` — намеренно заданное сообщение об ошибке. Оно не воспроизводит реальный отказ системы складских остатков и не измеряет производительность сервиса. В примере оба спана явно отмечены как ошибочные. `LoggingHandler` и экспортёр OTLP передают в логи идентификаторы активного спана. [Инструментирование Python](https://opentelemetry.io/docs/languages/python/instrumentation/)

В примере зафиксирована проверенная версия SDK. В [сведениях о поддержке Python](https://opentelemetry.io/docs/languages/python/) логи имеют статус Development, поэтому при обновлении повторно проверяйте совместимость API логов и экспортёра. `ALWAYS_ON` записывает каждый спан примера в учебных целях; это не рекомендуемая политика семплирования для производственной среды.

## Запрос обоих хранилищ по полученному ID трассы

Выполните эти команды в каталоге с четырьмя файлами. При первом запуске данные загружаются из Docker Hub и PyPI. Команды рассчитаны на оболочку в стиле Unix.

```sh
docker compose -p blog-lgtm-lab up -d --wait --wait-timeout 180
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python demo.py
```

Запускайте Python после перехода контейнера в состояние healthy. Загрузка образа и инициализация Grafana могут занять время. Экспорт до готовности среды может завершиться ошибкой. `force_flush()` ожидает обработки экспорта; это не окончательное подтверждение наличия данных в хранилищах.

Вот ID трассы, полученный в лабораторной работе. Каждый запуск создаёт новый ID, поэтому подставьте **собственный результат** в запрос ниже.

```text
trace_id=b95b8ec2e8c6fa5a608f197d1cfe3691
```

1. Откройте `http://127.0.0.1:13000`, выберите **Explore → Loki** и установите диапазон за последний час.
2. Запросите две записи лога с помощью этого выражения LogQL.

```text
{service_name="checkout-demo"} | trace_id = "b95b8ec2e8c6fa5a608f197d1cfe3691"
```

3. Разверните `inventory_unavailable` и перейдите по ссылке **View trace** для `trace_id`. В Tempo найдите `inventory.lookup` под `checkout`.
4. Нажмите **Related logs** на панели Tempo, чтобы вернуться в Loki. В зависимости от версии эта функция доступна как ссылка спана **Logs for this span**. Запрос не фильтрует по `span_id`, поэтому при совпадении временного диапазона и сервиса могут отобразиться обе записи лога этой трассы.

Локальные запросы вернули **две записи лога и два спана** с совпадающими родительско-дочерними связями и ID спанов в логах. В API серий Loki ни `trace_id`, ни `span_id` не присутствовали в качестве индексных меток, а запрос по несуществующему ID трассы не вернул логов. Проверки в браузере также подтвердили переход от записи об ошибке в Tempo и обратно к связанным логам Loki. Эти результаты относятся к примеру сбора и корреляции в одном процессе, а не к производственной нагрузке или восстановлению.

## Если ссылка не возвращает данных

| Симптом | Что проверить сначала | Следующее действие |
| --- | --- | --- |
| В логах нет ID трассы | Записывался ли лог внутри активного спана? | Проверьте передачу контекста между потоками, корутинами и через асинхронные границы |
| Запрос Loki работает, но ссылка на Tempo не появляется | Имя поля `derivedFields` и UID Tempo | Настройте сопоставление с фактическим полем `trace_id` |
| У спана нет ссылки на логи | `service.name` и сопоставление тегов источника данных | Согласуйте их со значением `service_name` в Loki |
| Запрос логов по ссылке возвращает ноль записей | Временной диапазон, сервис и ID трассы | Выполните LogQL напрямую; проверьте задержку приёма и рассинхронизацию часов |
| Логи есть, но трасса не находится по запросу | Экспортёр трасс, семплирование и срок хранения в Tempo | Проверьте ошибки экспорта Collector и политики хранения |

Не включайте `trace_id`, `user_id` и номера заказов в индексные метки производственной среды. Различные значения умножают число потоков Loki. Сначала сужайте выборку по значениям с ограниченным набором вариантов, например сервису и окружению, затем фильтруйте ID в теле или структурированных метаданных. [Кардинальность Loki](https://grafana.com/docs/loki/latest/get-started/labels/cardinality/)

Если логи или трасса не найдены, это не подтверждает исправность системы. Трасса могла быть исключена при семплировании, сроки хранения могут различаться, а экспорт из Collector может задерживаться. Не помещайте токены и персональные данные в тела логов и baggage; перед использованием в производственной среде настройте оповещения о сбоях сбора, сроки хранения и маскирование чувствительных данных.

После лабораторной работы удалите её контейнер и подключённые анонимные тома. Этот пример не сохраняет данные.

```sh
docker compose -p blog-lgtm-lab down -v
```
