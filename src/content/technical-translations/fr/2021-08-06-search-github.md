---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2021-08-06-search-github",
  "routeSlug": "2021-08-06-search-github",
  "kind": "post",
  "title": "Rechercher du code avec GitHub, Sourcegraph et Git local",
  "description": "Limiter la recherche par dépôt, langage et chemin, distinguer les syntaxes GitHub et Sourcegraph et reproduire une recherche de chaîne fixe avec Git local.",
  "categories": [
    "util"
  ],
  "tags": [
    "git",
    "github",
    "sourcegraph",
    "search"
  ],
  "sourcePath": "src/content/posts/en/2021-08-06-search-github.md",
  "sourceSha256": "22da61f44f3002516631540293a6b08b9b0de12d2c7963e6c52ae57b297efddf",
  "draftSha256": "4350b4dcd4fc2e13970bcaa84de68ec243a4a69d3f2244052791cb96709a0d95",
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
Commencez la recherche de code en fixant le dépôt et le périmètre des fichiers, puis examinez l’implémentation trouvée dans son contexte. Un nom de symbole correspondant est une piste, pas la preuve que le code convient à votre version de dépendance ou au comportement voulu.

La recherche GitHub, Sourcegraph et un checkout local interrogent des données disponibles différentes. Utilisez l’outil qui peut accéder au dépôt nécessaire ; ne supposez pas qu’une instance publique indexe chaque dépôt ou révision.

## Déroulement

![Limiter la requête avant d’élargir la liste des résultats. Si la version compte, ouvrir la révision voulue ou rechercher dans son checkout plutôt que se fier à la branche par défaut.](/assets/diagrams/technical/fr-2021-08-06-search-github.svg)

Limiter la requête avant d’élargir la liste des résultats. Si la version compte, ouvrir la révision voulue ou rechercher dans son checkout plutôt que se fier à la branche par défaut.

## Utiliser le langage de requête de chaque service

Une [requête de recherche GitHub](https://docs.github.com/en/search-github/github-code-search/understanding-github-code-search-syntax) peut combiner ces qualificatifs avec une expression entre guillemets :

```text
repo:spring-projects/spring-framework language:java path:WebClient.java "interface WebClient"
```

Les [filtres Sourcegraph](https://sourcegraph.com/docs/code-search/queries) correspondants utilisent des expressions régulières pour le dépôt et le fichier :

```text
repo:^github\.com/spring-projects/spring-framework$ lang:java file:WebClient\.java$ "interface WebClient"
```

| Intention | Recherche GitHub | Sourcegraph |
| --- | --- | --- |
| Dépôt | `repo:owner/name` | Expression régulière `repo:` ; ancrer si l’exactitude compte |
| Java | `language:java` | `lang:java` ou `language:java` |
| Périmètre des fichiers | Filtre de chemin `path:` | Expression régulière `file:` |
| Expression exacte | Expression entre guillemets | Expression entre guillemets en mode mots-clés |

Ce sont des exemples de construction de requêtes, pas des mesures du nombre de résultats en direct. Les deux filtres de chemin ne renvoient pas forcément les mêmes ensembles : l’exemple Sourcegraph ancre le suffixe du nom de fichier. L’accès, le contenu indexé et la révision choisie déterminent aussi ce qui est trouvable.

## Reproduire la recherche locale dans un répertoire vide

Ce petit exemple nécessite Git et un shell POSIX. `mkdir` échoue volontairement si `demo-search` existe déjà ; choisissez donc un nouveau répertoire de travail.

```sh
set -eu
mkdir demo-search
cd demo-search
git init -q
mkdir src docs
printf '%s\n' 'interface WebClient {}' > src/WebClient.java
printf '%s\n' 'interface WebClient is discussed here' > docs/notes.txt
git add src docs
git grep -n -F 'interface WebClient' -- src
```

Sortie :

```text
src/WebClient.java:1:interface WebClient {}
```

La même expression existe dans `docs/notes.txt`, mais `-- src` limite la recherche. [`git grep -F`](https://git-scm.com/docs/git-grep) traite le motif comme une chaîne fixe et `-n` affiche les numéros de ligne. Les fichiers ont été ajoutés à l’index parce que la recherche par défaut dans l’arbre de travail utilise les fichiers suivis ; l’exemple ne crée aucun commit. Dans un vrai checkout, remplacez le chemin et le motif en conservant le périmètre voulu.

Avant d’adapter un résultat, lisez les appelants, les tests, la licence et la révision. Une même déclaration peut se comporter différemment dans une autre version. Utilisez les [tests de réponses WebClient](/en/posts/2023-09-19-springboot-test-webclient/) pour vérifier un contrat client plutôt que déduire son comportement d’un résultat de recherche.
