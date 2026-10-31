---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2021-07-20-http-status-test",
  "routeSlug": "2021-07-20-http-status-test",
  "kind": "post",
  "title": "HTTP-Statuscodes lokal mit einem kleinen Python-Server testen",
  "description": "Lokale HTTP-Testantworten mit JSON, HTML trotz Status 200 und 204 ohne Antwortinhalt. Header und Inhalt unabhängig vom Statuscode prüfen.",
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
  "draftSha256": "70cc329dd99caa0b9ea3d0cf2cf75eddd05aef803c21d5fad9cfb75f62edb8ce",
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
Ein Statuscode allein belegt nicht, dass eine Antwort nutzbar ist. Ein Client kann HTML mit 200 erhalten oder einen erfolgreichen 204 ohne dekodierbaren Inhalt. Ein lokaler Testserver reproduziert diese Fälle ohne externen Antwortdienst.

Dieses Beispiel nutzt Python 3.11 oder neuer und nur die Standardbibliothek. Es bindet an 127.0.0.1 und implementiert GET für wenige feste Routen. Es ist eine Entwicklungstestumgebung, kein Anwendungsserver.

## Ablauf

![Der Handler wählt Status und Darstellung vor den Headern. Der 204-Zweig endet ohne Inhalt oder Content-Length; andere Routen schreiben die deklarierte Byteanzahl.](/assets/diagrams/technical/de-2021-07-20-http-status-test.svg)

Der Handler wählt Status und Darstellung vor den Headern. Der 204-Zweig endet ohne Inhalt oder Content-Length; andere Routen schreiben die deklarierte Byteanzahl.

## Vollständigen Server als status_server.py speichern

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

Die [Python-HTTP-Server-API](https://docs.python.org/3/library/http.server.html) liefert Anfrageverarbeitung und den Listener mit Threads. Nicht unterstützte Pfade oder Statusnummern ergeben die JSON-404-Antwort des Testservers. `/html/200` liefert absichtlich HTML mit einem Erfolgsstatus.

Starten Sie den Server in einem Terminal und senden Sie Anfragen aus einem anderen:

```sh
python3 status_server.py --port 8089
```

```sh
curl -i http://127.0.0.1:8089/status/500
curl -i http://127.0.0.1:8089/html/200
curl -i http://127.0.0.1:8089/status/204
```

Mit Port 0 wählt das Betriebssystem einen freien Port; der Server gibt die tatsächliche URL aus. Beenden Sie ihn mit Ctrl+C. Die curl-Befehle lassen `--fail` absichtlich weg, damit auch Fehlerantworten untersucht werden können.

| Anfrage | Status | Darstellung |
| --- | --- | --- |
| `/status/200` | 200 | JSON mit Status 200 |
| `/html/200` | 200 | HTML, kein JSON |
| `/status/500` | 500 | JSON mit Status 500 |
| `/status/204` | 204 | Kein Inhalt und kein Content-Length |

[RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html#section-8.6) verbietet Content-Length bei 204-Antworten. Prüfen Sie die Verfügbarkeit von Inhalt getrennt vom 2xx-Status. Dieser Testserver prüft Status, Medientyp und Nachrichtenbegrenzung, modelliert aber keine langsamen Antworten, TLS, Authentifizierung oder Wiederholungszeitpunkte. Für clientseitiges Dekodieren und Fehlersignale siehe [WebClient-Antworttests](/en/posts/2023-09-19-springboot-test-webclient/).
