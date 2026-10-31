---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ru",
  "translationKey": "2021-07-20-http-status-test",
  "routeSlug": "2021-07-20-http-status-test",
  "kind": "post",
  "title": "Локальное тестирование HTTP-статусов небольшим сервером Python",
  "description": "Локальный сервер для JSON-статусов, HTML со статусом 200 и 204 без тела. Проверка заголовков и тела отдельно от кода статуса.",
  "categories": [
    "util"
  ],
  "tags": [
    "http",
    "testing",
    "python"
  ],
  "sourcePath": "src/content/posts/en/2021-07-20-http-status-test.md",
  "sourceSha256": "6a0015675b8a80249e52069a1e2ba364408570bbf983db78a56b13b3ebf0b721",
  "draftSha256": "a512b56b73971f939b3dc24d0779bd078ff5a6231e6d3ceb8d96f83e34ce4874",
  "manifestPath": ".pipeline/technical-translations/batch-056/manifest.json",
  "manifestSha256": "5c3bd2ee5ccb0b59bad65322a026d7b2ef52cfac963e0236a497f74510717e42",
  "publishedAt": "2026-10-31T15:21:36.846Z",
  "updatedAt": "2026-10-31T15:21:36.846Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 125,
    "approvedAt": "2026-10-31T15:21:36.846Z",
    "basis": "User explicitly requested applying all missing technical-post languages, review, verification and deployment on 2026-11-01, with standing PR merge authorization. Human approval denotes publication authorization; linguistic review is performed by AI, not human/native review."
  }
}
---
Один код статуса не подтверждает пригодность ответа. Клиент может получить HTML со статусом 200 или успешный 204 без тела для декодирования. Локальный тестовый сервер воспроизводит эти случаи без внешнего сервиса ответов.

Пример использует Python 3.11 или новее и только стандартную библиотеку. Он привязывается к 127.0.0.1 и реализует GET для небольшого фиксированного набора маршрутов. Это средство разработки, а не сервер приложения.

## Ход обработки

![Обработчик выбирает статус и представление до записи заголовков. Ветка 204 завершается без тела и Content-Length, остальные записывают объявленное число байтов.](/assets/diagrams/technical/ru-2021-07-20-http-status-test.svg)

Обработчик выбирает статус и представление до записи заголовков. Ветка 204 завершается без тела и Content-Length, остальные записывают объявленное число байтов.

## Сохраните полный сервер в status_server.py

```python
import argparse
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

SUPPORTED = {200, 201, 204, 400, 404, 429, 500, 503}

class StatusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlsplit(self.path).path
        match = re.fullmatch(r"/status/([0-9]{3})", path)
        requested = int(match.group(1)) if match else None
        status = requested if requested in SUPPORTED else 404
        content_type = "application/json; charset=utf-8"
        body = json.dumps({"status": status}).encode("utf-8")
        if path == "/html/200":
            status = 200
            content_type = "text/html; charset=utf-8"
            body = b"<html><body>not JSON</body></html>"
        self.send_response(status)
        if status == 204:
            self.end_headers()
            return
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass

def make_server(port=8089):
    return ThreadingHTTPServer(("127.0.0.1", port), StatusHandler)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8089)
    args = parser.parse_args()
    if not 0 <= args.port <= 65535:
        parser.error("port must be from 0 through 65535")
    with make_server(args.port) as server:
        print(f"http://127.0.0.1:{server.server_port}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass

```

[API HTTP-сервера Python](https://docs.python.org/3/library/http.server.html) предоставляет обработку запросов и многопоточный слушатель. Неподдерживаемые пути или номера статусов возвращают JSON 404 тестового сервера. Маршрут `/html/200` намеренно возвращает HTML с успешным статусом.

Запустите сервер в одном терминале, а запросы отправляйте из другого:

```sh
python3 status_server.py --port 8089
```

```sh
curl -i http://127.0.0.1:8089/status/500
curl -i http://127.0.0.1:8089/html/200
curl -i http://127.0.0.1:8089/status/204
```

Используйте порт 0, чтобы ОС выбрала свободный порт; сервер выведет фактический URL. Остановите его через Ctrl+C. Эти команды curl намеренно не включают `--fail`, чтобы можно было проверить и ответ с ошибкой.

| Запрос | Статус | Представление |
| --- | --- | --- |
| `/status/200` | 200 | JSON со статусом 200 |
| `/html/200` | 200 | HTML, а не JSON |
| `/status/500` | 500 | JSON со статусом 500 |
| `/status/204` | 204 | Нет тела и Content-Length |

[RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html#section-8.6) запрещает Content-Length в ответах 204. Проверяйте доступность тела отдельно от проверки 2xx. Этот сервер проверяет статус, тип представления и границы сообщения, но не моделирует медленные ответы, TLS, аутентификацию или время повторных попыток. Для декодирования и сигналов ошибок на клиенте см. [тесты ответов WebClient](/en/posts/2023-09-19-springboot-test-webclient/).
