---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2023-09-23-linux-shellscript-github-latest",
  "routeSlug": "2023-09-23-linux-shellscript-github-latest",
  "kind": "post",
  "title": "Dernière release GitHub avec curl et jq : sélectionner un fichier à télécharger",
  "description": "Sélectionnez un seul asset de release GitHub selon le système, le CPU et le format avec curl et jq. Gérez les erreurs HTTP, le JSON invalide et les correspondances absentes ou multiples.",
  "categories": [
    "linux"
  ],
  "tags": [
    "linux",
    "bash",
    "shell script",
    "jq",
    "github latest release"
  ],
  "sourcePath": "src/content/posts/en/2023-09-23-linux-shellscript-github-latest.md",
  "sourceSha256": "921c781aad6d00452ee4730c3ae3ccb6d7af94c4ec4e129e5968b7f1ae596e61",
  "draftSha256": "01e8608b052320bd955e28e7c9f2b64d690b3917d42afaa90284aa734f214c7e",
  "manifestPath": ".pipeline/technical-translations/batch-052/manifest.json",
  "manifestSha256": "3d0fe88e42da93129f62cd5dba401357ffe96d3d01f3038c35211f5afff754c7",
  "publishedAt": "2026-10-31T15:21:36.227Z",
  "updatedAt": "2026-10-31T15:21:36.227Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 125,
    "approvedAt": "2026-10-31T15:21:36.227Z",
    "basis": "User explicitly requested applying all missing technical-post languages, review, verification and deployment on 2026-11-01, with standing PR merge authorization. Human approval denotes publication authorization; linguistic review is performed by AI, not human/native review."
  }
}
---
Utilisez `curl` pour obtenir la dernière release GitHub et `jq` pour sélectionner exactement un asset à télécharger selon le système, le CPU et le format requis. Le script ci-dessous s’arrête en cas d’erreur HTTP, de JSON invalide ou de correspondances absentes ou multiples ; il renvoie des métadonnées sans télécharger le fichier.

Le point d’accès `releases/latest` ne calcule pas le tag Git numériquement le plus grand. La [documentation de l’API des releases](https://docs.github.com/en/rest/releases/releases#get-the-latest-release) distingue les tags ordinaires, les brouillons, les préversions et les releases publiées.

L’exemple interroge le dépôt public `adoptium/temurin17-binaries` pour obtenir les métadonnées d’un JDK HotSpot Linux x64 au format tar.gz. Il ne nécessite ni jeton ni téléchargement effectif du fichier. L’absence d’argument de dépôt utilise cette valeur par défaut ; un argument explicitement vide est rejeté.

## Déroulement du traitement

![Un échec HTTP arrête le script avant l’analyse JSON. Un objet de release valide doit contenir exactement un asset correspondant ; sélectionner son URL ne vérifie pas le fichier téléchargé.](/assets/diagrams/technical/fr-2023-09-23-linux-shellscript-github-latest.svg)

Un échec HTTP arrête le script avant l’analyse JSON. Un objet de release valide doit contenir exactement un asset correspondant ; sélectionner son URL ne vérifie pas le fichier téléchargé.

## Séparer l’échec HTTP de l’échec de sélection JSON

Le script nécessite `curl`, `jq` et POSIX sh. Enregistrez-le dans `latest-release.sh`.

### `latest-release.sh`

```sh
#!/bin/sh
set -eu
if [ "$#" -gt 1 ]; then
    printf '%s\n' 'usage: latest-release.sh OWNER/REPO' >&2
    exit 2
fi
repo=${1-adoptium/temurin17-binaries}
case "$repo" in
    */*/*|/*|*/|*[!A-Za-z0-9_./-]*) printf '%s\n' 'usage: latest-release.sh OWNER/REPO' >&2; exit 2 ;;
esac
case "$repo" in
    */*) ;;
    *) printf '%s\n' 'usage: latest-release.sh OWNER/REPO' >&2; exit 2 ;;
esac
api=${GITHUB_API_URL:-https://api.github.com}
response=$(curl --fail --silent --show-error --location --max-time 20 \
    --header 'Accept: application/vnd.github+json' \
    --header 'X-GitHub-Api-Version: 2026-03-10' \
    "$api/repos/$repo/releases/latest") || exit 1
printf '%s' "$response" | jq --slurp --exit-status '
    if length != 1 or (.[0] | type) != "object" then
        error("expected one release object")
    else .[0] end
    | . as $release
    | if (.tag_name | type) != "string" or (.tag_name | length) == 0
         or (.assets | type) != "array" then
        error("missing release tag or assets")
      else . end
    | [.assets[] | select(.name | test("^OpenJDK17U-jdk_x64_linux_hotspot_.*\\.tar\\.gz$"))] as $assets
    | if ($assets | length) != 1 then
        error("expected exactly one Linux x64 JDK tar.gz asset")
      elif ($assets[0].browser_download_url | type) != "string"
           or ($assets[0].browser_download_url | length) == 0 then
        error("missing asset download URL")
      else {tag_name: $release.tag_name, download_url: $assets[0].browser_download_url} end
'
```

```sh
sh latest-release.sh adoptium/temurin17-binaries
```

Un résultat réussi est un objet JSON avec `tag_name` et `download_url`. Les valeurs dépendent de la release au moment de la requête. L’exemple suivant contient des données de test illustrant la structure, sans affirmer quelle est la dernière release actuelle :

```json
{"tag_name":"jdk-17.0.8.1+1","download_url":"https://github.com/adoptium/temurin17-binaries/releases/download/example/OpenJDK17U-jdk_x64_linux_hotspot_example.tar.gz"}
```

`curl --fail` traite d’abord les erreurs HTTP. Capturer la réponse avant l’analyse évite que la dernière commande d’un pipeline masque un échec réseau. Consultez les [options curl](https://curl.se/docs/manpage.html).

`jq --slurp` lit toute l’entrée dans un tableau. Exiger exactement une valeur JSON rejette aussi une réponse vide. Le filtre vérifie ensuite l’objet de release, le tag et le tableau d’assets ; il n’émet un résultat que si exactement un nom de fichier correspond. Consultez le [manuel jq](https://jqlang.org/manual/).

## Résultats à traiter dans l’automatisation

| Condition | Résultat |
| --- | --- |
| Réponse valide et un seul asset correspondant | Sortie JSON, code 0. |
| HTTP403/404 ou échec de connexion | Code non nul. |
| Corps vide ou JSON mal formé | Code non nul. |
| Aucun asset correspondant ou plusieurs | Échec plutôt qu’un choix arbitraire. |
| Syntaxe invalide de l’argument de dépôt | Message d’utilisation, code 2. |

Si la requête HTTP réussit mais qu’aucun fichier ne correspond, examinez les noms des fichiers de la release avant de modifier le filtre `jq` : cet exemple sélectionne Java 17 pour Linux x64, pas tous les paquets JDK. Pour Java 21, utilisez l’[exemple de métadonnées de plateforme Temurin](/en/posts/2023-10-10-temurin-jdk21-delay/). Si les valeurs du dépôt ou de la plateforme proviennent de YAML, [analysez et validez la configuration comme des données](/en/posts/2021-07-27-parse-yaml/) avant de transmettre les valeurs à une commande.

Des réponses HTTP locales ont servi à vérifier le succès, les erreurs HTTP, le JSON invalide, les assets absents et les doublons. `GITHUB_API_URL` utilise l’API publique par défaut et peut viser un serveur de test implémentant le même contrat de réponse.

La lecture de ressources publiques ne nécessite pas d’authentification. Si vous ajoutez des requêtes authentifiées, ne placez pas les jetons dans le code source ni dans les journaux de traçage du Shell. Vérifiez les en-têtes de réponse relatifs aux limites de débit et la [documentation GitHub sur ces limites](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api).

Le script sélectionne une URL ; il ne vérifie pas l’intégrité du fichier d’installation. L’automatisation de l’installation doit encore prendre en compte les sommes de contrôle ou signatures du fournisseur et la plateforme cible. Avant de transmettre un tag au [comparateur de versions numériques](/en/posts/2023-11-17-linux-shellscript-version-compare/), vérifiez qu’il respecte le contrat d’entrée de ce script.

Après avoir téléchargé la ressource sélectionnée, [comparez sa somme de contrôle SHA-256 à une valeur attendue provenant d’une source fiable](/en/posts/2026-10-30-verify-sha256-download/). Le vérificateur lit les octets locaux ; il ne télécharge pas la version et n’authentifie pas son éditeur.
