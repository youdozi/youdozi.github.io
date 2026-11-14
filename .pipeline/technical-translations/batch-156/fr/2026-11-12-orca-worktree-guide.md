---
state: "draft"
language: "fr"
translationKey: "2026-11-12-orca-worktree-guide"
title: "Utiliser Orca : workflow worktree pour agents, tests et revue"
description: "Utiliser projets et worktrees Orca pour séparer une tâche, vérifier tests et navigateur et examiner le diff avant commit."
sourcePath: "src/content/posts/en/2026-11-12-orca-worktree-guide.md"
sourceSha256: "4214532491f859b28104e614442c9bc3c33ecc9a00a62567a96d927bc90cffb6"
---

**Orca est un environnement de développement qui réunit espaces Git, agents de codage, terminaux, navigateur et revue des changements.** Affecter un worktree à chaque tâche permet de travailler dans des branches et dossiers séparés. Vérifiez l’achèvement à partir du chemin réel, des sorties de test et du diff avec la branche de base, plutôt que de la seule réponse de l’agent.

Le sujet est l’[app officielle Orca](https://www.onorca.dev/) de Stably AI. Ce guide utilise **Orca 1.4.256** sur macOS, le guide CLI fourni, Node.js 24.13.0, Python 3 et Git. La consultation de l’espace courant, les tests dans un terminal Orca, la détection du port et l’affichage dans le navigateur intégré ont été vérifiés. La création ou fusion d’un worktree et le lancement d’une nouvelle tâche d’agent IA n’ont pas été exécutés ; les prompts et commandes ci-dessous sont des exercices.

## Quelle différence entre projet et worktree ?

Ouvrez un dépôt Git local avec **Add Repo** dans le [guide officiel de première session](https://www.onorca.dev/docs/first-session). Même si Orca gère un projet, les sources et commits restent dans le dépôt Git. Préparez séparément les conditions d’utilisation et l’authentification du modèle ou fournisseur.

| Élément | Rôle dans cet exercice |
| --- | --- |
| Projet | Regroupe le dépôt d’exemple et les espaces de travail |
| Worktree | Dossier de travail sur une branche et vue de travail associée |
| Agent | Propose la lecture et la modification de fichiers et l’exécution de commandes dans le périmètre demandé |
| Terminal | Exécute tests et serveur de développement dans le dossier de la tâche |
| Navigateur intégré | Vérifie la vraie page du serveur de développement et les valeurs limites |

La [documentation Orca des worktrees](https://www.onorca.dev/docs/model/worktrees) et le [guide CLI](https://www.onorca.dev/docs/cli/overview) expliquent les relations entre fichiers, branches et vues. Ne supposez pas que sélectionner un autre worktree dans l’interface change automatiquement le dossier courant d’un shell déjà ouvert. La première étape est de **vérifier chemin et branche dans le terminal qui exécutera les commandes**.

## Créer un petit exemple et vérifier son état initial

![Ouvrir le dépôt Git d’exemple, créer un worktree et vérifier chemin et branche. Demander à un agent de modifier un fichier, puis vérifier tests, serveur et navigateur dans ce worktree. Comparer diff et tests d’origine à main ; si les conditions sont remplies, committer soi-même, sinon demander une correction.](2026-11-12-orca-worktree-guide.svg)

Utilisons une politique de frais de port illustrative : **une commande d’au moins 50 000 won est gratuite ; en dessous, les frais sont de 3 000 won**. Seuls des entiers sûrs non négatifs sont acceptés. Ce n’est pas une règle d’un service réel. Enregistrez les quatre fichiers suivants dans un nouveau dossier `orca-shipping-example`. Aucun paquet npm externe n’est nécessaire.

### `package.json`

```json
{
  "name": "orca-shipping-example",
  "private": true,
  "type": "module",
  "engines": { "node": ">=24" },
  "scripts": { "test": "node --test shipping.test.mjs" }
}
```

### `shipping.mjs`

```javascript
export function shippingFee(orderTotal) {
  return orderTotal > 50_000 ? 0 : 3000;
}
```

### `shipping.test.mjs`

```javascript
import test from 'node:test';
import assert from 'node:assert/strict';
import { shippingFee } from './shipping.mjs';

for (const [total, expected] of [[0, 3000], [49_999, 3000], [50_000, 0], [50_001, 0]]) {
  test(`shippingFee(${total}) = ${expected}`, () => {
    assert.equal(shippingFee(total), expected);
  });
}
for (const [label, total] of [
  ['negative', -1],
  ['fraction', 50_000.5],
  ['string', '50000'],
  ['NaN', Number.NaN],
  ['Infinity', Number.POSITIVE_INFINITY],
  ['unsafe integer', Number.MAX_SAFE_INTEGER + 1],
]) {
  test(`rejects ${label}`, () => {
    assert.throws(() => shippingFee(total), RangeError);
  });
}
```

### `index.html`

```html
<!doctype html>
<html lang="ko">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Orca 배송비 예제</title>
<h1>배송비 경계값 확인</h1>
<pre id="result"></pre>
<script type="module">
  import { shippingFee } from './shipping.mjs';
  const totals = [49_999, 50_000, 50_001];
  document.querySelector('#result').textContent = totals
    .map(total => `${total}원 → 배송비 ${shippingFee(total)}원`)
    .join('\n');
</script>
</html>
```

Exécutez ceci dans le dossier d’exemple après configuration de l’auteur Git.

```sh
git init -b main
git add package.json shipping.mjs shipping.test.mjs index.html
git commit -m "Add shipping exercise"
npm test
```

Le code initial traite incorrectement la limite `50,000` (cinquante mille wons) et ne refuse pas les entrées invalides. Une exécution réelle a confirmé **3 tests réussis et 7 échoués sur 10**. Enregistrer cet état comme commit de base permet ensuite de comparer les tests et la configuration.

## Demander un changement à un agent dans un worktree

Ouvrez le dépôt d’exemple avec **Add Repo** dans Orca puis vérifiez la CLI dans un terminal relié au dépôt. Si elle manque, installez-la via Settings → General → Orca CLI selon le [guide CLI officiel](https://www.onorca.dev/docs/cli/overview). Ces commandes supposent l’exécutable `orca` sur macOS.

```sh
orca skills get orca-cli
orca worktree current --json
```

Pour séparer le travail, créez un worktree depuis le `main` du projet courant.

```sh
orca worktree create --name shipping-fee-fix \
  --parent-worktree active --base-branch main \
  --setup skip --activate --json
```

`--parent-worktree active` enregistre la relation de travail Orca ; `--base-branch main` fixe le point de départ Git. Ce sont deux réglages distincts. L’exemple saute la préparation car aucune dépendance externe n’est à installer. Dans un vrai projet, suivez la politique de préparation appropriée. Cette commande ne contient pas `--agent` et ne lance donc pas de tâche d’agent.

Ouvrez un terminal dans le nouvel espace et vérifiez-le. Distinguez le shell de la commande initiale de celui du nouveau worktree.

```sh
git rev-parse --show-toplevel
git branch --show-current
orca worktree current --json
```

Les noms de branches peuvent varier selon le préfixe Orca et la configuration. Après avoir vérifié que le worktree du JSON et le chemin et la branche Git correspondent à l’espace voulu, ouvrez un onglet d’agent préparé et envoyez le prompt suivant. Agents disponibles et exécution par chat ou CLI dépendent de la configuration.

```text
Vérifiez d’abord le dossier de travail et la branche, puis lisez shipping.mjs et shipping.test.mjs.
Corrigez la règle illustrative des frais de port selon ce contrat :

- Une commande d’au moins 50 000 won a des frais de 0 ; en dessous, ils sont de 3 000 won.
- Acceptez uniquement des entiers sûrs non négatifs comme montants ; toute autre entrée produit RangeError.
- Modifiez uniquement shipping.mjs ; ne changez ni les tests, ni package.json, ni index.html.
- N’installez pas de dépendances, n’appelez pas de réseau externe et ne créez ni commit, ni push, ni PR.

Indiquez le résultat réel de npm test et la raison du changement.
Précisez explicitement si une vérification n’a pas pu être exécutée.
```

Même si Orca regroupe le travail, les permissions réelles des outils dépendent de l’agent et de l’environnement d’exécution. Les restrictions du prompt ne les imposent pas. Ce guide ne suppose ni noms particuliers de boutons d’autorisation ni comportement identique chez tous les fournisseurs.

## Vérifier tests et navigateur dans le même espace

Exécutez `npm test` dans le [terminal intégré](https://www.onorca.dev/docs/terminal). Pour automatiser, vous pouvez créer un terminal de test dans le worktree courant :

```sh
orca terminal create --title "tests" --command "npm test" --json
```

En automatisation, utilisez le handle retourné comme cible des commandes suivantes. `terminal read --screen` lit l’écran courant ; `terminal read` sans option lit la sortie accumulée. L’acceptation d’une entrée et le démarrage réel d’une commande ou tâche d’agent sont deux événements distincts. Ce guide a vérifié **les 10 tests réussis** et uniquement `shipping.mjs` modifié dans la sortie d’un terminal de test créé à cet effet. La solution de référence a été insérée directement ; ce n’est pas un historique d’exécution de tâche IA.

Pour vérifier le navigateur, lancez le serveur dans un terminal du même worktree. On suppose que le port 4877 est libre.

```sh
python3 -m http.server 4877 --bind 127.0.0.1
```

Vérifiez le port dans un autre terminal.

```sh
orca ports --json
orca tab create --url http://127.0.0.1:4877/ --json
```

Si le serveur utilise un autre port, utilisez celui affiché et son URL correspondante. Tout ce qu’affiche `orca ports` n’est pas une page web HTTP. Connectez-vous selon le [guide du navigateur intégré](https://www.onorca.dev/docs/browser/overview) et vérifiez les valeurs suivantes sur la page d’exemple :

```text
49999원 → 배송비 3000원
50000원 → 배송비 0원
50001원 → 배송비 0원
```

Ces trois lignes ont été vérifiées dans le vrai navigateur Orca avec la solution de référence. Arrêtez ensuite le serveur avec `Ctrl+C` dans son terminal. Ne fermez pas en bloc des terminaux sans rapport parce que la tâche est terminée ; distinguez les processus et onglets concernés.

## Examiner le diff et enregistrer le seul fichier modifié

Vérifiez la référence de base et les fichiers modifiés dans le [visualiseur de diff Orca](https://www.onorca.dev/docs/review/diff-viewer). Les [commentaires sur les lignes modifiées](https://www.onorca.dev/docs/review/annotate-ai-diff) permettent d’indiquer un emplacement à l’agent. Par exemple : « 50 000 won doit aussi être gratuit. Gardez les attentes des tests et vérifiez l’opérateur de comparaison. »

Comparez également à `main` dans le terminal.

```sh
git status --short
git diff main --name-only
git diff main -- shipping.mjs
git diff --exit-code main -- shipping.test.mjs package.json index.html
npm test
```

Seul `shipping.mjs` doit être modifié pour cette tâche. Si les tests, la configuration ou la page changent, cherchez d’abord pourquoi. Un diff ordinaire peut omettre de nouveaux fichiers ; vérifiez aussi le statut Git. Exécutez vous-même les contrôles que l’agent n’a pas pu lancer ; ne considérez pas « terminé » comme un test réussi.

Voici la solution de référence vérifiée directement. Comparez-la au code proposé par l’agent après l’exercice. Pour l’exécuter, placez ce code dans `shipping.mjs` à la racine du projet.

### `reference/shipping.mjs`

```javascript
export function shippingFee(orderTotal) {
  if (!Number.isSafeInteger(orderTotal) || orderTotal < 0) {
    throw new RangeError('orderTotal must be a nonnegative safe integer');
  }
  return orderTotal >= 50_000 ? 0 : 3000;
}
```

Avec la solution de référence, les mêmes 10 tests ont réussi et les tests, la configuration et le HTML d’origine ont été conservés. Après vérification, committez uniquement les fichiers nécessaires sur la branche de la tâche.

```sh
git add shipping.mjs
git commit -m "Fix free-shipping boundary and input validation"
```

Un commit et sa fusion dans la branche de base sont deux étapes distinctes. Si une autre tâche modifie `main`, revérifiez le diff et les tests avant fusion. Un worktree sépare les espaces de sources mais n’est pas un bac à sable de sécurité. Des worktrees distincts peuvent partager des ressources d’exécution : bases de données, ports, comptes et secrets.

Au départ, pratiquer ce flux sur une tâche facilite la localisation des problèmes par rapport à l’ajout immédiat de plusieurs agents. Étendez ensuite le travail parallèle quand les limites de fichiers ou fonctionnalités et les conditions de fin sont distinctes.
