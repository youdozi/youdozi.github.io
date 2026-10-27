---
title: "HTTP 상태 코드 로컬 테스트: Python 서버로 응답 계약 확인하기"
language: ko
translationKey: 2021-07-20-http-status-test
routeSlug: 2021-07-20-http-status-test
kind: post
publishedAt: 2021-07-19T22:40:30.000Z
categories:
  - util
tags:
  - util
  - mock
  - http-status-code
legacyUrl: /util/http-status-test/
legacySource: _posts/util/2021-07-20-http-status-test.markdown
updatedAt: 2026-10-27T05:47:47.001Z
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Primary documentation checked; paired examples and diagram/code
  structure validated. Execution and UI limits are stated in the article.
archiveBodySha256: 6a5acf144ac5c86b519c04778300425bd1258f9cf0f65d3a1bf753bd55713d96
reviewSources:
  - https://docs.python.org/3/library/http.server.html
  - https://www.rfc-editor.org/rfc/rfc9110.html#section-8.6
description: 외부 응답 사이트 없이 localhost에서 JSON 상태 응답, 200 HTML, 본문 없는 204를 재현합니다. 상태
  코드와 헤더·본문을 구분해 확인합니다.
---
상태 코드만으로 응답을 사용할 수 있는지 판단할 수는 없습니다. 200인데 HTML이 오거나, 성공한 204인데 디코딩할 본문이 없을 수 있습니다. 로컬 응답 서버를 두면 외부 사이트에 의존하지 않고 이 조건을 반복할 수 있습니다.

예제는 Python 3.11 이상과 표준 라이브러리만 사용합니다. 127.0.0.1에서 고정된 일부 경로의 GET 요청을 처리하는 개발용 테스트 서버입니다.

## 처리 흐름

![로컬 HTTP 응답 선택 흐름도](/assets/diagrams/2021-07-20-http-status-test-ko.svg)

헤더를 쓰기 전에 상태와 표현 형식을 선택합니다. 204 분기는 본문과 Content-Length 없이 종료하고, 나머지 경로는 헤더에 명시한 바이트 수만큼 본문을 씁니다.

## 전체 코드를 status_server.py에 저장하기

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

[Python HTTP 서버 API](https://docs.python.org/3/library/http.server.html)로 요청 처리와 스레드 기반 서버를 구성합니다. 지원하지 않는 경로나 상태 번호는 예제의 JSON 404를 반환합니다. `/html/200`은 성공 상태에 HTML 본문을 붙이는 비교용 경로입니다.

한 터미널에서 서버를 실행한 뒤 다른 터미널에서 요청합니다.

```sh
python3 status_server.py --port 8089
```

```sh
curl -i http://127.0.0.1:8089/status/500
curl -i http://127.0.0.1:8089/html/200
curl -i http://127.0.0.1:8089/status/204
```

포트 0을 지정하면 OS가 빈 포트를 선택하고 실제 URL을 출력합니다. Ctrl+C로 종료합니다. 오류 응답도 확인하도록 위 curl 명령에는 `--fail`을 넣지 않았습니다.

| 요청 | 상태 | 본문·헤더 |
| --- | --- | --- |
| `/status/200` | 200 | 상태 200을 담은 JSON |
| `/html/200` | 200 | JSON이 아닌 HTML |
| `/status/500` | 500 | 상태 500을 담은 JSON |
| `/status/204` | 204 | 본문·Content-Length 없음 |

[RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html#section-8.6)은 204 응답의 Content-Length를 금지합니다. 2xx인지와 본문이 있는지를 따로 다루세요. 이 예제는 상태·미디어 타입·본문 길이를 다루며 지연, TLS, 인증이나 재시도 시간은 재현하지 않습니다. 클라이언트의 디코딩·오류 신호 검증은 [WebClient 응답 테스트](/ko/posts/2023-09-19-springboot-test-webclient/)에서 이어집니다.
