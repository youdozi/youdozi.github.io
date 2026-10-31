---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2021-07-27-parse-yaml",
  "routeSlug": "2021-07-27-parse-yaml",
  "kind": "post",
  "title": "Lire du YAML depuis le shell : valider un port et exécuter sans eval",
  "description": "Lire un port YAML typé avec Python et PyYAML, rejeter les entrées invalides et transmettre SERVER_PORT à une commande enfant sans eval ni génération de code shell.",
  "categories": [
    "linux"
  ],
  "tags": [
    "linux",
    "bash",
    "parse",
    "yaml"
  ],
  "sourcePath": "src/content/posts/en/2021-07-27-parse-yaml.md",
  "sourceSha256": "102f35eacb16194761699d994cc9b12de6dbd6cfb89d6e54580f0d74f30ec17f",
  "draftSha256": "6cf1c74a0538288520025708e4a6908a9b96ec041ad1c63f809b49b472b4b889",
  "manifestPath": ".pipeline/technical-translations/batch-058/manifest.json",
  "manifestSha256": "ddb52115d3c0de8ef810b654b7cab3396580933aec400022723b4ba51b5e8d96",
  "publishedAt": "2026-10-31T15:21:37.180Z",
  "updatedAt": "2026-10-31T15:21:37.180Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 125,
    "approvedAt": "2026-10-31T15:21:37.180Z",
    "basis": "User explicitly requested applying all missing technical-post languages, review, verification and deployment on 2026-11-01, with standing PR merge authorization. Human approval denotes publication authorization; linguistic review is performed by AI, not human/native review."
  }
}
---
Pour lire un port YAML depuis le shell sans `eval`, utilisez un [analyseur YAML](https://pyyaml.org/wiki/PyYAMLDocumentation#loading-yaml), validez le type et la plage de la valeur, puis transmettez seulement les variables nécessaires. Cet exemple lit une valeur `server.port` avec Python et PyYAML et ne lance la commande enfant qu’après validation. N’approximez pas toute la grammaire YAML avec sed/awk.

Le texte affiché seul ne distingue pas sûrement l’entier YAML `8080` de la chaîne `"8080"`. Ce chargeur **ne convertit pas les chaînes en nombres** : il accepte uniquement une valeur analysée comme entier entre 1 et 65535. bool étant une sous-classe de int en Python, `type(port) is int` rejette les booléens, contrairement à `isinstance(port, int)`.

## Déroulement

![Analyser et valider le port entier avant d’exporter SERVER_PORT. Un échec du chargeur empêche le démarrage de la commande cible ; exec conserve son statut.](/assets/diagrams/technical/fr-2021-07-27-parse-yaml.svg)

Analyser et valider le port entier avant d’exporter SERVER_PORT. Un échec du chargeur empêche le démarrage de la commande cible ; exec conserve son statut.

## Environnement et entrée

Utilisez Python 3 et [PyYAML 6.0.3](https://pypi.org/project/PyYAML/6.0.3/). L’environnement d’exécution local utilise Python 3.13. Enregistrez les trois fichiers dans le même répertoire et installez la dépendance dans un environnement virtuel dédié.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install PyYAML==6.0.3
```

### `application.yml`

```yaml
server:
  port: 8080
```

### `read-port.py`

```python
import sys
from pathlib import Path
import yaml

if len(sys.argv) != 2:
    sys.exit("usage: read-port.py CONFIG")
try:
    with Path(sys.argv[1]).open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    if not isinstance(config, dict):
        raise ValueError("root must be a mapping")
    server = config.get("server")
    if not isinstance(server, dict):
        raise ValueError("server must be a mapping")
    port = server.get("port")
    if type(port) is not int or not 1 <= port <= 65535:
        raise ValueError("server.port must be an integer from 1 to 65535")
except (OSError, UnicodeError, yaml.YAMLError, ValueError) as error:
    print(f"invalid configuration: {error}", file=sys.stderr)
    sys.exit(2)
print(port)
```

### `run-with-port.sh`

```sh
#!/bin/sh
set -eu
if [ "$#" -lt 2 ]; then
    printf '%s\n' 'usage: run-with-port.sh CONFIG COMMAND [ARG ...]' >&2
    exit 2
fi
config=$1
shift
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
port=$("${PYTHON:-python3}" "$script_dir/read-port.py" "$config")
export SERVER_PORT="$port"
exec "$@"
```

## Lancer une commande avec la valeur validée

```sh
PYTHON=.venv/bin/python sh run-with-port.sh application.yml \
  .venv/bin/python -c 'import os; print(os.environ["SERVER_PORT"])'
```

```text
8080
```

`read-port.py` écrit seulement la valeur valide sur stdout et les erreurs sur stderr. Il rejette avec le statut 2 les fichiers absents, YAML invalide, documents multiples, entrées sans mapping, champs manquants, chaînes, booléens, flottants et valeurs hors plage. `run-with-port.sh` propage l’échec sans lancer la cible. Après le démarrage, `exec` conserve le statut de sortie de celle-ci.

`"$@"` conserve séparément la commande et chaque argument. Les espaces ou `$()` d’un argument ne sont pas réévalués comme du code shell. Les chemins relatifs de `PYTHON` et de configuration sont résolus depuis le répertoire courant de l’appelant ; le wrapper trouve `read-port.py` à côté de lui.

L’export atteint le processus enfant sans changer l’environnement du shell parent appelant. Lancez le wrapper par `sh run-with-port.sh ...` au lieu de le sourcer. Vérifiez séparément que votre application lit réellement `SERVER_PORT`.

## Périmètre du chargeur

[`safe_load`](https://pyyaml.org/wiki/PyYAMLDocumentation) n’autorise pas les balises construisant des objets Python arbitraires, mais les vérifications de type et de plage propres à l’application restent nécessaires. Cet exemple ne limite ni mémoire ni temps pour des entrées malveillantes volumineuses ; il vise donc les configurations locales fiables.

Il suit les règles de typage implicite de PyYAML : des valeurs comme `on` peuvent devenir des booléens. Il ne rejette pas les clés dupliquées, dont la dernière valeur peut subsister ; interdisez-les dans l’entrée et contrôlez-les séparément. Ce n’est ni une politique complète de typage YAML 1.2 ni un validateur général de schéma de configuration. Définissez explicitement le type et la politique de valeur manquante pour chaque champ supplémentaire.

Pour les échecs de commande et statuts de sortie, voir la [recherche des versions GitHub](/en/posts/2023-09-23-linux-shellscript-github-latest/). Pour la compatibilité des données persistées des jobs JVM, voir la [migration Spring Batch 5](/en/posts/2023-10-27-springbatch5-migration/).
