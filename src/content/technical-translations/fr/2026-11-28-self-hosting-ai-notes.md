---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2026-11-28-self-hosting-ai-notes",
  "routeSlug": "2026-11-28-self-hosting-ai-notes",
  "kind": "post",
  "title": "Auto-héberger une application créée par IA : premiers pas avec une API de notes",
  "description": "Demandez une API de notes à une IA, arrêtez le processus et vérifiez que vous retrouvez la première note dans le même fichier SQLite.",
  "categories": [
    "tips"
  ],
  "tags": [
    "self-hosting",
    "python",
    "sqlite"
  ],
  "sourcePath": "src/content/posts/en/2026-11-28-self-hosting-ai-notes.md",
  "sourceSha256": "f31b0a9a46f32859c6cd630d2d77ff943c1ddc47a7f7a4135e924c37fd826809",
  "draftSha256": "33cce5459a3dc93d299e99339fb2b1a17855831cdea22555c526779d8419d13f",
  "manifestPath": ".pipeline/technical-translations/batch-1541/manifest.json",
  "manifestSha256": "3971c1774c424e3b0b6352540dda4d2616bef5ae8e9be66505d93c921c823b31",
  "publishedAt": "2026-11-28T02:44:07.338Z",
  "updatedAt": "2026-11-28T02:44:07.338Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 228,
    "approvedAt": "2026-11-28T02:44:07.338Z",
    "basis": "Explicit item 154 publication instruction for the revised item 153 self-hosted notes article in all nine site languages."
  }
}
---

L’application que l’IA vient de créer a enregistré votre première note. Fermez-la, puis relancez-la. La note est-elle toujours là ? Quand on débute en auto-hébergement, on vérifie que l’application répond et que les données restent lisibles après un redémarrage. Ici, nous demandons à une IA une petite application de notes et son mode d’emploi, puis nous les essayons sur notre ordinateur. L’exemple utilise uniquement Python et SQLite.

## Préciser les conditions de fonctionnement en même temps que les fonctionnalités

Avec « Crée-moi une application de notes », le modèle risque de choisir lui-même le stockage et les conditions d’accès. Précisez où conserver les données, qui peut se connecter et comment vous vérifierez que l’application est prête.

**Consigne**　Crée une API de notes personnelles avec la bibliothèque standard de Python et SQLite. Écoute uniquement sur `127.0.0.1` et stocke les notes dans `data/notes.db`. Fais renvoyer l’état par `GET /healthz` et la liste des notes par `GET /notes`. Fais accepter `{"text":"첫 메모"}` par `POST /notes` et renvoie `400` si le texte ne contient que des espaces. Fournis `app.py`, les commandes de démarrage et d’arrêt et des exemples avec curl. Vérifie dans cet ordre : consulter l’état → enregistrer une note → arrêter le processus → redémarrer avec la même base → lire la note. Indique l’adresse d’écoute et le fichier créé.

## Vérifier l’adresse et le chemin de stockage avant de démarrer

Vérifiez que le serveur écoute sur `127.0.0.1` et que SQLite ouvre `data/notes.db` sur disque. Avec un chemin relatif, changer de répertoire de travail peut faire ouvrir une autre base. L’exemple construit le chemin à partir de l’emplacement du fichier de l’application. Le module Python `http.server` sert ici à un exercice local. [http.server](https://docs.python.org/3/library/http.server.html) · [sqlite3](https://docs.python.org/3/library/sqlite3.html)

Enregistrez le code suivant dans un fichier `app.py`, dans un répertoire de travail vide.

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

## Tester les instructions de l’IA avec de vraies requêtes

![Consulter l’état et la liste vide → rejeter une note blanche → enregistrer la première note → arrêter le processus → redémarrer avec la même base → lire la note enregistrée.](/assets/diagrams/technical/fr-2026-11-28-self-hosting-ai-notes.svg)

Pour vérifier que la note est sur disque, arrêtez le processus qui l’a écrite et lisez-la depuis un nouveau processus.

Exécutez `python3 app.py` depuis le répertoire de l’application. La première ligne indique l’adresse avec son port temporaire et la suivante le chemin de la base. Dans un second terminal, exécutez les commandes ci-dessous. Lorsque `read` attend une saisie, collez l’adresse de la première ligne.

```sh
read -r base
```

```sh
curl -i "$base/healthz"
curl -i "$base/notes"
curl -i -H 'Content-Type: application/json' -d '{"text":"   "}' "$base/notes"
curl -i -H 'Content-Type: application/json' -d '{"text":"첫 메모"}' "$base/notes"
```

Dans le terminal de l’application, appuyez sur `Ctrl+C` et attendez le retour de l’invite de commande. Relancez `python3 app.py`, vérifiez que le chemin de la base est identique et saisissez la nouvelle adresse dans le second terminal.

```sh
read -r base
```

```sh
curl -i "$base/notes"
```

Nous avons testé ces requêtes avec Python `3.13.0` dans un environnement local temporaire, sur l’adresse de bouclage avec un port temporaire. L’état et la liste initialement vide ont renvoyé `200`, le texte composé uniquement d’espaces `400` et l’enregistrement de la première note `201`. Après avoir confirmé l’arrêt du processus et relancé l’application avec la même base, nous avons obtenu `200` et la note enregistrée. Si la liste semble vide, comparez les chemins réels des deux lancements. Transmettez à l’IA les commandes de démarrage, les chemins de la base et les réponses HTTP.

## Préparer la sauvegarde et la restauration pour continuer à utiliser l’application

« Si cet ordinateur tombe en panne, pourrai-je ouvrir mes notes ailleurs ? » Demandez à l’IA où se trouvent les données et comment restaurer une sauvegarde dans un nouveau répertoire pour y relire les notes. Lors du transfert sur un serveur, vérifiez le démarrage de l’application après un redémarrage de la machine ainsi que les droits d’accès. Cet essai a couvert les requêtes locales, l’enregistrement et la lecture après redémarrage. L’accès externe et la restauration d’une sauvegarde n’ont pas été testés. [Utiliser un MacBook comme serveur personnel sur un réseau privé](https://youdozi.github.io/ko/posts/2026-11-23-macbook-personal-server/)
