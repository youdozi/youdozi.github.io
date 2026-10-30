---
language: "fr"
translationKey: "2021-07-20-http-status-test"
title: "Tester les statuts HTTP localement avec un petit serveur Python"
description: "Un serveur local reproduit les réponses JSON, le HTML avec statut 200 et le 204 sans corps. Vérifier en-têtes et corps indépendamment du statut."
state: "draft"
sourcePath: "src/content/posts/en/2021-07-20-http-status-test.md"
sourceSha256: "6a0015675b8a80249e52069a1e2ba364408570bbf983db78a56b13b3ebf0b721"
---
Un code de statut seul ne prouve pas qu’une réponse est exploitable. Un client peut recevoir du HTML avec 200, ou un succès 204 sans corps à décoder. Un simulateur local reproduit ces cas sans service de réponse externe.

Cet exemple utilise Python 3.11 ou ultérieur et uniquement la bibliothèque standard. Il écoute sur 127.0.0.1 et implémente GET pour quelques routes fixes. C’est un simulateur de développement, pas un serveur d’application.

## Déroulement

![Le gestionnaire choisit statut et représentation avant les en-têtes. La branche 204 finit sans corps ni Content-Length ; les autres écrivent le nombre d’octets déclaré.](2021-07-20-http-status-test.svg)

Le gestionnaire choisit statut et représentation avant les en-têtes. La branche 204 finit sans corps ni Content-Length ; les autres écrivent le nombre d’octets déclaré.

## Enregistrer le serveur complet dans status_server.py

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

L’[API du serveur HTTP Python](https://docs.python.org/3/library/http.server.html) fournit le traitement des requêtes et l’écoute avec des threads. Les chemins ou numéros de statut non pris en charge renvoient le JSON 404 du simulateur. `/html/200` renvoie volontairement du HTML avec un statut de succès.

Lancez le serveur dans un terminal, puis envoyez des requêtes dans un autre :

```sh
python3 status_server.py --port 8089
```

```sh
curl -i http://127.0.0.1:8089/status/500
curl -i http://127.0.0.1:8089/html/200
curl -i http://127.0.0.1:8089/status/204
```

Utilisez le port 0 pour laisser le système choisir un port libre ; le serveur affiche l’URL réelle. Arrêtez-le avec Ctrl+C. Ces commandes curl omettent volontairement `--fail` pour permettre d’examiner aussi la réponse d’erreur.

| Requête | Statut | Représentation |
| --- | --- | --- |
| `/status/200` | 200 | JSON contenant le statut 200 |
| `/html/200` | 200 | HTML, pas JSON |
| `/status/500` | 500 | JSON contenant le statut 500 |
| `/status/204` | 204 | Ni corps ni Content-Length |

La [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html#section-8.6) interdit Content-Length sur les réponses 204. Traitez la présence d’un corps séparément d’une vérification 2xx. Ce simulateur vérifie le statut, le type de média et la délimitation ; il ne modélise pas les réponses lentes, TLS, l’authentification ou le calendrier des nouvelles tentatives. Pour le décodage et les signaux d’erreur côté client, poursuivez avec les [tests de réponses WebClient](/en/posts/2023-09-19-springboot-test-webclient/).
