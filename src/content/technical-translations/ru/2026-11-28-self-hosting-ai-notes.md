---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ru",
  "translationKey": "2026-11-28-self-hosting-ai-notes",
  "routeSlug": "2026-11-28-self-hosting-ai-notes",
  "kind": "post",
  "title": "Как запустить приложение от ИИ на своём сервере: начнём с API для заметок",
  "description": "Попросите ИИ написать API для заметок и проверьте, можно ли после остановки процесса прочитать первую запись из того же файла SQLite.",
  "categories": [
    "tips"
  ],
  "tags": [
    "self-hosting",
    "python",
    "sqlite"
  ],
  "sourcePath": "src/content/posts/en/2026-11-28-self-hosting-ai-notes.md",
  "sourceSha256": "005a0679c6742c842941ba2d57b180427e876b2615a48d4c7bb23d42503f8597",
  "draftSha256": "b84c86156fd0260a54117523f717a696854ffb8b8117a99f2b12f5dfea3a09aa",
  "manifestPath": ".pipeline/technical-translations/batch-1541/manifest.json",
  "manifestSha256": "8f721bd5cb7f5080972863e41fd8b88e4647254d61c5ff9efa0b5978519f6e99",
  "publishedAt": "2026-11-28T02:42:03.473Z",
  "updatedAt": "2026-11-28T02:42:03.473Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 228,
    "approvedAt": "2026-11-28T02:42:03.473Z",
    "basis": "Explicit item 154 publication instruction for the revised item 153 self-hosted notes article in all nine site languages."
  }
}
---

Приложение, которое написал ИИ, сохранило первую заметку. Закройте его и запустите снова. Заметка на месте? Когда вы впервые запускаете приложение у себя, стоит проверить и доступность приложения, и сохранность данных после перезапуска. Попросим ИИ написать небольшое приложение для заметок и инструкции к нему, а затем проверим результат на своём компьютере. Для примера нужны только Python и SQLite.

## Опишите функции и условия работы

Если просто попросить «сделай приложение для заметок», модель может сама решить, где хранить записи и кому разрешить подключение. Заранее укажите место хранения, круг пользователей и признаки, по которым вы примете результат.

> Напиши личный API для заметок на стандартной библиотеке Python и SQLite. Слушай только `127.0.0.1` и храни заметки в `data/notes.db`. Пусть `GET /healthz` возвращает состояние, а `GET /notes` — список заметок. Пусть `POST /notes` принимает `{"text":"첫 메모"}` и возвращает `400`, если текст состоит только из пробельных символов. Дай файл `app.py`, команды запуска и остановки и примеры проверок с curl. Порядок проверки: запросить состояние → сохранить заметку → завершить процесс → запустить с той же базой → прочитать заметку. Укажи адрес сервера и файл, который создаёт приложение.

## Перед запуском проверьте адрес и путь к базе

Убедитесь, что сервер слушает `127.0.0.1`, а SQLite открывает файл `data/notes.db` на диске. Относительный путь может привести к другой базе при запуске из другого каталога. В примере путь отсчитывается от файла приложения. Модуль Python `http.server` здесь используется для локального учебного примера. [http.server](https://docs.python.org/3/library/http.server.html) · [sqlite3](https://docs.python.org/3/library/sqlite3.html)

Сохраните следующий код в файле `app.py` в пустом учебном каталоге.

```python
import json
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

db_path = Path(__file__).resolve().parent / "data" / "notes.db"


class Notes(BaseHTTPRequestHandler):
    def reply(self, status, value):
        body = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/healthz":
            self.reply(200, {"status": "ok"})
        elif self.path == "/notes":
            rows = db.execute("SELECT text FROM notes ORDER BY id")
            self.reply(200, [{"text": text} for (text,) in rows])
        else:
            self.reply(404, {"error": "unknown path"})

    def do_POST(self):
        if self.path != "/notes":
            self.reply(404, {"error": "unknown path"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 8192:
                raise ValueError
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict):
                raise ValueError
            text = data.get("text")
            if not isinstance(text, str) or not text.strip():
                raise ValueError
        except ValueError:
            self.reply(400, {"error": "invalid note"})
            return
        with db:
            db.execute("INSERT INTO notes (text) VALUES (?)", (text,))
        self.reply(201, {"text": text})


if __name__ == "__main__":
    db_path.parent.mkdir(exist_ok=True)
    db = sqlite3.connect(db_path)
    try:
        db.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, text TEXT NOT NULL)")
        with HTTPServer(("127.0.0.1", 0), Notes) as server:
            print(f"http://127.0.0.1:{server.server_port}", db_path, sep="\n", flush=True)
            server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        db.close()
```

## Проверьте инструкции ИИ реальными запросами

![Проверить состояние и пустой список → отклонить текст из пробелов → сохранить первую заметку → завершить процесс → запустить с той же базой → прочитать сохранённую заметку.](/assets/diagrams/technical/ru-2026-11-28-self-hosting-ai-notes.svg)

Чтобы проверить запись на диск, завершите процесс, который сохранил заметку, и прочитайте её из нового процесса.

Выполните `python3 app.py` из каталога приложения. В первой строке появится адрес с временным портом, во второй — путь к базе. В другом терминале выполните команды ниже и вставьте адрес из первой строки, когда `read` будет ждать ввода.

```sh
read -r base
```

```sh
curl -i "$base/healthz"
curl -i "$base/notes"
curl -i -H 'Content-Type: application/json' -d '{"text":"   "}' "$base/notes"
curl -i -H 'Content-Type: application/json' -d '{"text":"첫 메모"}' "$base/notes"
```

В терминале приложения нажмите `Ctrl+C` и дождитесь приглашения командной оболочки. Снова выполните `python3 app.py`, убедитесь, что путь к базе тот же, и введите новый адрес во втором терминале.

```sh
read -r base
```

```sh
curl -i "$base/notes"
```

Мы проверили запросы в локальной временной среде на Python `3.13.0`, используя петлевой интерфейс и временный порт. Запрос состояния и получение первоначально пустого списка вернули `200`, текст из одних пробелов — `400`, а сохранение первой заметки — `201`. Мы убедились, что процесс завершился, и запустили приложение с той же базой. В ответ на запрос списка пришли `200` и сохранённая заметка. Если список пуст, сравните фактические пути к базе при обоих запусках. Покажите ИИ команды запуска, пути к базе и ответы HTTP.

## Если приложение пригодится надолго, подготовьте резервное копирование и восстановление

«Смогу ли я открыть заметки в другом месте, если компьютер сломается?» Попросите ИИ указать путь к данным и объяснить, как восстановить копию в новом каталоге и прочитать заметки. При переносе на сервер проверьте, как приложение запускается после перезагрузки машины и у кого есть доступ. В этом опыте мы проверили локальные запросы, сохранение и чтение после перезапуска. Внешний доступ и восстановление из копии не испытывались. [Как использовать MacBook в качестве личного сервера в частной сети](https://youdozi.github.io/ko/posts/2026-11-23-macbook-personal-server/)
