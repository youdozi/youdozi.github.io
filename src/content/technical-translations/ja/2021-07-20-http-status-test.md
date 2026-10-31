---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2021-07-20-http-status-test",
  "routeSlug": "2021-07-20-http-status-test",
  "kind": "post",
  "title": "小さな Python サーバーで HTTP ステータスをローカルテストする",
  "description": "localhost のモックで JSON の状態応答、200 の HTML、本文のない 204 を再現します。ステータスとは別にヘッダーと本文を確認します。",
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
  "draftSha256": "ab1a0968d1e7f69ebaf52086fa3c16a6a45a8b60d3fe8290d85145c91f57cd84",
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
ステータスコードだけでは応答が利用可能だとは分かりません。200 で HTML が返ったり、成功の 204 でデコードする本文がなかったりします。ローカルのモックなら、外部の応答サービスなしでこれらを再現できます。

この例は Python 3.11 以降と標準ライブラリだけを使います。127.0.0.1 にバインドし、少数の固定ルートに GET を実装します。開発用のモックであり、アプリケーションサーバーではありません。

## 処理の流れ

![ハンドラーはヘッダーの前にステータスと表現を選びます。204 分岐は本文と Content-Length なしで終了し、それ以外は宣言したバイト数を書き込みます。](/assets/diagrams/technical/ja-2021-07-20-http-status-test.svg)

ハンドラーはヘッダーの前にステータスと表現を選びます。204 分岐は本文と Content-Length なしで終了し、それ以外は宣言したバイト数を書き込みます。

## 完全なサーバーを status_server.py に保存する

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

[Python HTTP サーバー API](https://docs.python.org/3/library/http.server.html) がリクエスト処理とスレッド化されたリスナーを提供します。未対応のパスやステータス番号には、モックの JSON 404 を返します。`/html/200` は意図的に成功ステータスで HTML を返します。

一つのターミナルでサーバーを実行し、別のターミナルからリクエストを送ります。

```sh
python3 status_server.py --port 8089
```

```sh
curl -i http://127.0.0.1:8089/status/500
curl -i http://127.0.0.1:8089/html/200
curl -i http://127.0.0.1:8089/status/204
```

ポート 0 なら OS が空きポートを選び、サーバーが実際の URL を表示します。Ctrl+C で停止します。エラー応答も確認できるよう、curl コマンドは意図的に `--fail` を付けていません。

| リクエスト | ステータス | 表現 |
| --- | --- | --- |
| `/status/200` | 200 | ステータス 200 を含む JSON |
| `/html/200` | 200 | JSON ではなく HTML |
| `/status/500` | 500 | ステータス 500 を含む JSON |
| `/status/204` | 204 | 本文も Content-Length もなし |

[RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html#section-8.6) は 204 応答の Content-Length を禁止しています。本文の有無は 2xx の確認とは分けて扱います。このモックはステータス・メディア型・メッセージの区切りを確認しますが、遅い応答、TLS、認証、リトライのタイミングは再現しません。クライアントのデコードとエラーシグナルは [WebClient 応答テスト](/en/posts/2023-09-19-springboot-test-webclient/)へ進んでください。
