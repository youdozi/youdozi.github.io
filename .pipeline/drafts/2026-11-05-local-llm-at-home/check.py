"""Exercise the HTTP client against a temporary loopback fixture, without model inference."""
import importlib.util
import json
from pathlib import Path
import re
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("local_summary", ROOT / "summarize.py")
client = importlib.util.module_from_spec(spec)
spec.loader.exec_module(client)


class Handler(BaseHTTPRequestHandler):
    status = 200
    body = {"message": {"content": "고정 테스트 응답"}, "done": True, "done_reason": "stop"}
    requests = []

    def do_POST(self):
        length = int(self.headers["Content-Length"])
        Handler.requests.append((self.path, self.headers["Content-Type"], json.loads(self.rfile.read(length))))
        self.send_response(Handler.status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(Handler.body if isinstance(Handler.body, bytes) else json.dumps(Handler.body).encode())

    def log_message(self, *_):
        pass


def expect(error_type, path):
    try:
        client.summarize(path)
    except error_type:
        return
    raise AssertionError(f"Expected {error_type}")


def main():
    checks = 0
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    client.ENDPOINT = f"http://127.0.0.1:{server.server_port}/api/chat"
    try:
        with tempfile.TemporaryDirectory(prefix="local-llm-client-") as directory:
            note = Path(directory) / "notes.txt"
            note.write_text((ROOT / "notes.txt").read_text(), encoding="utf-8")
            assert client.summarize(note) == "고정 테스트 응답"; checks += 1
            path, content_type, payload = Handler.requests[-1]
            assert path == "/api/chat" and content_type == "application/json"; checks += 1
            assert payload["model"] == "home-assistant" and payload["stream"] is False; checks += 1
            assert payload["options"] == {"num_ctx": 4096, "num_predict": 512} and payload["keep_alive"] == 0; checks += 1
            assert note.read_text() in payload["messages"][0]["content"] and "tools" not in payload; checks += 1
            before = len(Handler.requests)
            for value in ["", " ", "가" * 2001]:
                note.write_text(value, encoding="utf-8"); expect(ValueError, note); checks += 1
            assert len(Handler.requests) == before; checks += 1
            note.write_text("검사할 메모", encoding="utf-8")
            Handler.status = 404; expect(HTTPError, note); checks += 1
            Handler.status = 200
            for body in [b"not json", [], {"done": True}, {"done": True, "message": {"content": ""}},
                         {"done": False, "message": {"content": "진행 중"}},
                         {"done": True, "done_reason": "length", "message": {"content": "잘린 답"}}]:
                Handler.body = body; expect((ValueError, RuntimeError), note); checks += 1
    finally:
        server.shutdown(); server.server_close(); worker.join(timeout=5)
    article = ROOT / "article.ko.md"
    if article.exists():
        raw = article.read_text()
        for filename, language in [("summarize.py", "python"), ("Modelfile", "text"), ("notes.txt", "text")]:
            match = re.search(r"### `" + re.escape(filename) + r"`\n\n```" + language + r"\n(.*?)\n```", raw, re.S)
            assert match and match[1] + "\n" == (ROOT / filename).read_text(); checks += 1
    if article.exists():
        for code in re.findall(r'^```sh\n(.*?)\n```', raw, re.M | re.S):
            __import__('subprocess').run(['bash', '-n'], input=code, text=True, check=True, capture_output=True)
        site = ROOT.parents[2]
        published = site / 'src/content/posts/ko/2026-11-05-local-llm-at-home.md'
        if published.exists():
            def body(value):
                return re.sub(r'^---\n[\s\S]*?\n---\n', '', value, count=1)
            assert body(published.read_text()) == body(raw).replace(
                '(./local-llm-flow-ko.svg)', '(/assets/img/architecture/local-llm-flow-ko.svg)')
            assert (site / 'assets/img/architecture/local-llm-flow-ko.svg').read_bytes() == (ROOT / 'local-llm-flow-ko.svg').read_bytes()
    print(json.dumps({"checks": checks, "python": __import__('platform').python_version(),
                      "transport": "Actual HTTP on a temporary loopback server", "actualModelInference": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
