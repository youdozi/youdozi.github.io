---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2021-07-20-http-status-test",
  "routeSlug": "2021-07-20-http-status-test",
  "kind": "post",
  "title": "Probar estados HTTP localmente con un pequeño servidor Python",
  "description": "Un servidor local para respuestas JSON, HTML con estado 200 y 204 sin cuerpo. Comprueba cabeceras y cuerpos independientemente del código de estado.",
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
  "draftSha256": "a7f3a549b10001df9bddff553f7d4751f5372dae46f83b7b3461951814aa958f",
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
Un código de estado por sí solo no demuestra que una respuesta sea utilizable. El cliente puede recibir HTML con 200 o un 204 correcto sin cuerpo que decodificar. Un simulador local reproduce esos casos sin un servicio externo de respuestas.

Este ejemplo usa Python 3.11 o posterior y solo la biblioteca estándar. Se enlaza a 127.0.0.1 e implementa GET para un pequeño conjunto fijo de rutas. Es un simulador de desarrollo, no un servidor de aplicaciones.

## Flujo de procesamiento

![El manejador elige estado y representación antes de escribir cabeceras. La rama 204 termina sin cuerpo ni Content-Length; las otras escriben los bytes declarados.](/assets/diagrams/technical/es-2021-07-20-http-status-test.svg)

El manejador elige estado y representación antes de escribir cabeceras. La rama 204 termina sin cuerpo ni Content-Length; las otras escriben los bytes declarados.

## Guardar el servidor completo como status_server.py

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

La [API de servidor HTTP de Python](https://docs.python.org/3/library/http.server.html) proporciona el manejo de solicitudes y la escucha con hilos. Las rutas o números de estado no admitidos devuelven el JSON 404 del simulador. `/html/200` devuelve HTML con un estado correcto deliberadamente.

Ejecuta el servidor en un terminal y envía solicitudes desde otro:

```sh
python3 status_server.py --port 8089
```

```sh
curl -i http://127.0.0.1:8089/status/500
curl -i http://127.0.0.1:8089/html/200
curl -i http://127.0.0.1:8089/status/204
```

Usa el puerto 0 para que el sistema elija uno libre; el servidor imprime la URL real. Detén el proceso con Ctrl+C. Estos comandos curl omiten `--fail` a propósito para poder inspeccionar también la respuesta de error.

| Solicitud | Estado | Representación |
| --- | --- | --- |
| `/status/200` | 200 | JSON con el estado 200 |
| `/html/200` | 200 | HTML, no JSON |
| `/status/500` | 500 | JSON con el estado 500 |
| `/status/204` | 204 | Sin cuerpo ni Content-Length |

La [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html#section-8.6) prohíbe Content-Length en respuestas 204. Trata la disponibilidad del cuerpo separadamente de la comprobación 2xx. Este simulador comprueba estado, tipo de contenido y delimitación; no modela respuestas lentas, TLS, autenticación ni tiempos de reintento. Para la decodificación y señales de error del cliente, continúa con las [pruebas de respuestas WebClient](/en/posts/2023-09-19-springboot-test-webclient/).
