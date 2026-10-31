---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2023-09-20-linux-shellscript-function-error",
  "routeSlug": "2023-09-20-linux-shellscript-function-error",
  "kind": "post",
  "title": "Corriger l’avertissement Shell sur function : POSIX sh et Bash",
  "description": "Corrigez l’avertissement lié au mot-clé non standard function, choisissez explicitement POSIX sh ou Bash et vérifiez les arguments entre guillemets et les codes de retour.",
  "categories": [
    "linux"
  ],
  "tags": [
    "linux",
    "bash",
    "shell script",
    "function"
  ],
  "sourcePath": "src/content/posts/en/2023-09-20-linux-shellscript-function-error.md",
  "sourceSha256": "06ada98f4723e3b70cb188c01cc5efe1f31f9a724392b8e273b665663b5a73f8",
  "draftSha256": "10f059fc79458632ad74b6a53a333464036878b1ffb2d0d139b9dd3829310a86",
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
Dans un script `#!/bin/sh`, déclarez une fonction avec `hello() { ...; }`, sans le mot-clé `function`. Si le script nécessite la syntaxe Bash, choisissez Bash et invoquez-le en conséquence. L’appel `sh script.sh` ne suit pas le shebang Bash contenu dans le fichier.

[ShellCheck SC2112](https://www.shellcheck.net/wiki/SC2112) explique que `function` n’appartient pas à la syntaxe POSIX sh. Le fait qu’une implémentation particulière de `/bin/sh` l’accepte ne démontre pas la portabilité.

## Déroulement du traitement

![L’interpréteur invoqué analyse la fonction. L’exemple vérifie qu’un seul argument est fourni et préserve les espaces et les caractères génériques grâce aux guillemets.](/assets/diagrams/technical/fr-2023-09-20-linux-shellscript-function-error.svg)

L’interpréteur invoqué analyse la fonction. L’exemple vérifie qu’un seul argument est fourni et préserve les espaces et les caractères génériques grâce aux guillemets.

## Écrire une fonction pour le Shell choisi

Enregistrez le fichier sous `greet.sh`. Les guillemets dans `"$1"` et `"$@"` préservent les espaces et les caractères génériques dans les arguments.

### `greet.sh`

```sh
#!/bin/sh
set -eu

greet() {
    if [ "$#" -ne 1 ]; then
        printf '%s\n' 'usage: greet.sh NAME' >&2
        return 2
    fi
    printf 'Hello, %s\n' "$1"
}

greet "$@"
```

```sh
sh -n greet.sh
sh greet.sh 'Ada Lovelace'
sh greet.sh 'Ada *'
```

Les sorties sont `Hello, Ada Lovelace` et `Hello, Ada *`. `sh -n` vérifie uniquement la syntaxe : exécutez donc aussi le script. Des arguments manquants ou supplémentaires produisent un message d’utilisation sur stderr et un code de sortie 2. Un argument valide donne le code 0.

## Distinguer le shebang de l’interpréteur explicite

| Invocation | Choix de l’interpréteur |
| --- | --- |
| `sh greet.sh NAME` | Le `sh` invoqué lit le fichier. |
| `bash greet.sh NAME` | Bash le lit. |
| `chmod +x greet.sh`, puis `./greet.sh NAME` | Cette exécution utilise le shebang du fichier. |

Pour les tableaux Bash ou `[[ ... ]]`, utilisez `#!/usr/bin/env bash` et lancez `bash script.sh` ou le fichier exécutable `./script.sh`. Ne présumez pas que la syntaxe Bash fonctionnera avec `sh script.sh`. Consultez [l’explication de ShellCheck sur le choix du Shell](https://www.shellcheck.net/wiki/SC2112).

Le `return` d’une fonction rend le contrôle et un code à l’appelant. `exit` termine le Shell en cours. Ici, l’appel à la fonction est la dernière commande ; son code devient donc le code de sortie du script.

L’exemple a été vérifié avec des arguments contenant des espaces et des caractères génériques, ainsi qu’avec des nombres d’arguments invalides. Les implémentations de `/bin/sh` diffèrent : testez aussi avec le Shell de déploiement. Pour poursuivre l’automatisation, consultez la [comparaison de versions numériques](/en/posts/2023-11-17-linux-shellscript-version-compare/) ou la [recherche de releases GitHub](/en/posts/2023-09-23-linux-shellscript-github-latest/), où les entrées et les codes d’échec comptent également.
