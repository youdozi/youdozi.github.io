---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2026-11-28-self-hosting-ai-notes",
  "routeSlug": "2026-11-28-self-hosting-ai-notes",
  "kind": "post",
  "title": "从笔记 API 入手，在自己的服务器上运行 AI 写的应用",
  "description": "让 AI 写一个笔记 API，停止进程后再检查能否从同一个 SQLite 文件中读到第一条笔记。",
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
  "draftSha256": "351ae0b4324daf447583979dd4e9d6af81abc91176ae8728073268d893136115",
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

AI 写的笔记应用刚刚保存了第一条笔记。关掉应用再启动，笔记还在吗？开始自托管时，除了看应用能否响应，还要看程序重启后数据是否保留。这次我们让 AI 编写一个小型笔记应用并给出运行步骤，然后在自己的电脑上验证。示例只用到 Python 和 SQLite。

## 把功能和运行条件一起告诉 AI

只说“帮我做个笔记应用”，模型可能会自行决定如何存储数据、允许谁连接。先写清楚数据放在哪里、谁可以访问，以及满足哪些条件才算完成。

> 用 Python 标准库和 SQLite 写一个个人笔记 API。只监听 `127.0.0.1`，把笔记保存在 `data/notes.db`。让 `GET /healthz` 返回状态，`GET /notes` 列出笔记。`POST /notes` 接收 `{"text":"첫 메모"}`，对只有空白字符的输入返回 `400`。请提供 `app.py`、启动和停止命令，以及 curl 验证示例。按这个顺序检查：查看状态 → 保存笔记 → 停止进程 → 用同一个数据库重新启动 → 读取笔记。请注明监听地址和生成的文件。

## 运行前检查地址和存储路径

确认服务器绑定到 `127.0.0.1`，SQLite 打开磁盘上的 `data/notes.db`。如果只给相对路径，换个目录启动就可能打开另一个数据库。下面的代码以应用文件的位置为基准确定路径。Python 的 `http.server` 在这里用于本地学习。 [http.server](https://docs.python.org/3/library/http.server.html) · [sqlite3](https://docs.python.org/3/library/sqlite3.html)

在一个空的练习目录里，把以下代码保存为 `app.py`。

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

## 用实际请求验证 AI 的说明

![查看状态和空列表 → 拒绝空白笔记 → 保存第一条笔记 → 停止进程 → 用同一数据库重启 → 读取已存笔记。](/assets/diagrams/technical/zh-CN-2026-11-28-self-hosting-ai-notes.svg)

要确认笔记已写入磁盘，就结束写入笔记的进程，再从新进程读取。

在应用目录执行 `python3 app.py`。第一行是带临时端口的地址，第二行是数据库路径。在另一个终端执行以下命令，等 `read` 等待输入时粘贴第一行的地址。

```sh
read -r base
```

```sh
curl -i "$base/healthz"
curl -i "$base/notes"
curl -i -H 'Content-Type: application/json' -d '{"text":"   "}' "$base/notes"
curl -i -H 'Content-Type: application/json' -d '{"text":"첫 메모"}' "$base/notes"
```

在运行应用的终端按 `Ctrl+C`，等到命令提示符再次出现。重新执行 `python3 app.py`，确认数据库路径一致，再在第二个终端输入新地址。

```sh
read -r base
```

```sh
curl -i "$base/notes"
```

我们在 Python `3.13.0` 临时本地环境中，用回环地址和临时端口测试了这些请求。状态查询和初始空列表均返回 `200`，只有空白字符的输入返回 `400`，保存第一条笔记返回 `201`。确认进程退出并用同一数据库重启后，列表请求返回 `200` 和已保存的笔记。如果列表为空，先比较两次启动时的实际数据库路径。向 AI 求助时，提供启动命令、数据库路径和 HTTP 响应。

## 打算长期使用，就准备备份和恢复步骤

“这台电脑坏了，我还能在别处打开笔记吗？”让 AI 指出数据路径，说明如何把备份恢复到新目录并读取笔记。迁移到服务器时，还要确认机器重启后应用如何启动、谁有访问权限。这次只验证了本地请求、保存和重启后读取，没有测试外部访问和备份恢复。 [在专用网络上把 MacBook 用作个人服务器](https://youdozi.github.io/ko/posts/2026-11-23-macbook-personal-server/)
