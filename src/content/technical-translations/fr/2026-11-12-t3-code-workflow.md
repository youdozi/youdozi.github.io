---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2026-11-12-t3-code-workflow",
  "routeSlug": "2026-11-12-t3-code-workflow",
  "kind": "post",
  "title": "T3 Code : d’une petite modification à la vérification du diff et des tests",
  "description": "Démarrer une tâche de code IA avec T3 Code v0.1.9, permissions bornées, diff et tests, en distinguant solution de référence et sortie IA.",
  "categories": [
    "util"
  ],
  "tags": [
    "t3-code",
    "ai-agent",
    "coding-agent",
    "testing",
    "javascript"
  ],
  "sourcePath": "src/content/posts/en/2026-11-12-t3-code-workflow.md",
  "sourceSha256": "da83ebd4864d4a4b015af522789e363b4a8695b6424368db9bfd1652f7761089",
  "draftSha256": "7929cab47ad9f67742d4212d76c317892eafcf8b0b26b80d965917c219fd00aa",
  "manifestPath": ".pipeline/technical-translations/batch-156/manifest.json",
  "manifestSha256": "ed48dc20825daff8725d8eba3418b1ad885276b52c9752ba958f7a1705b24430",
  "publishedAt": "2026-11-14T15:16:43.783Z",
  "updatedAt": "2026-11-14T15:16:43.783Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 158,
    "approvedAt": "2026-11-14T15:16:43.783Z",
    "basis": "User requested all 63 language editions and instructed completed PRs to be merged; AI translation and independent AI review were performed, with no claim of human text review."
  }
}
---

**T3 Code relie les agents de codage installés sur l’ordinateur aux vues de projet, de conversation, d’autorisations et de fichiers modifiés.** Pour confier du code à un agent, un périmètre réduit et des critères de fin vérifiables comptent davantage qu’une longue demande. Cet exemple corrige un analyseur numérique de `Retry-After`, de la demande jusqu’à la vérification du diff et des tests.

Le sujet est le [projet officiel T3 Code](https://github.com/pingdotgg/t3code/tree/v0.1.9), distinct de la T3 Stack permettant de créer une app web avec `create-t3-app`. Le README officiel décrit la connexion de fournisseurs existants comme Codex, Claude Code et Cursor. L’installation de T3 Code et la préparation de la connexion et des conditions d’abonnement ou d’API du fournisseur sont distinctes.

La référence est la [version v0.1.9](https://github.com/pingdotgg/t3code/releases/tag/v0.1.9), consultée le 12 novembre 2026. L’exemple a été vérifié sur macOS avec Node.js 24.13.0 et Git ; l’aide CLI de T3 Code et le démarrage du serveur local ont aussi été vérifiés. **Aucune tâche IA n’a été envoyée à un fournisseur.** La solution de référence ci-dessous est une implémentation testée directement, pas une sortie réelle de T3 Code ni une mesure de performance du modèle.

## Comment T3 Code et le fournisseur se répartissent-ils les rôles ?

T3 Code affiche le projet et le fil, le choix du fournisseur, les demandes d’autorisation et les changements. L’agent connecté lit ou modifie les fichiers et exécute des commandes. Voir un appel d’outil ne signifie pas que les tests ont été exécutés et réussis automatiquement : examinez la commande et le résultat.

En suivant le [guide d’installation](https://github.com/pingdotgg/t3code/blob/v0.1.9/docs/user/install.md), installez le fournisseur choisi et authentifiez-vous sur **l’ordinateur exécutant le serveur T3 Code**. L’exercice commence au choix d’un fournisseur déjà prêt. Il n’est pas nécessaire de coller des identifiants ou clés API dans le prompt.

## Préparer un petit projet Git et des tests en échec

![Enregistrer le code initial et les tests fixes dans Git et constater les échecs. Dans T3 Code, choisir projet, fournisseur et permissions Supervised, puis envoyer une demande bornée. Approuver les changements et commandes, comparer diff, tests d’origine et résultats, puis committer soi-même si le contrat est respecté ou demander une correction sinon.](/assets/diagrams/technical/fr-2026-11-12-t3-code-workflow.svg)

Enregistrez ces trois fichiers dans un nouveau dossier `t3-code-example`. Ces tests Node ne nécessitent ni paquet externe ni appel API. Parmi les deux formes de `Retry-After`, cet exercice ne prend en charge **que `delay-seconds`, des secondes entières**. HTTP-date est hors périmètre et doit renvoyer `null`. Pour la grammaire complète, voir la [définition Retry-After de RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html#name-retry-after).

### `package.json`

```json
{
  "name": "t3-code-retry-after-example",
  "private": true,
  "type": "module",
  "engines": { "node": ">=24" },
  "scripts": { "test": "node --test retry-after.test.mjs" }
}
```

### `retry-after.mjs`

```javascript
export function retryAfterMs(header) {
  const seconds = Number.parseInt(header, 10);
  return Number.isFinite(seconds) ? seconds * 1000 : null;
}
```

### `retry-after.test.mjs`

```javascript
import test from 'node:test';
import assert from 'node:assert/strict';
import { retryAfterMs } from './retry-after.mjs';

const cases = [
  ['2', 2000],
  ['0', 0],
  [' 2 ', 2000],
  ['0002', 2000],
  ['', null],
  ['   ', null],
  [undefined, null],
  [null, null],
  [2, null],
  ['0x10', null],
  ['2x', null],
  ['-1', null],
  ['1.5', null],
  ['1e3', null],
  ['Infinity', null],
  ['Wed, 21 Oct 2015 07:28:00 GMT', null],
  ['9007199254740', 9007199254740000],
  ['9007199254741', null],
  ['9007199254740991', null],
];
for (const [input, expected] of cases) {
  test(`retryAfterMs(${JSON.stringify(input)})`, () => {
    assert.equal(retryAfterMs(input), expected);
  });
}
```

Exécutez ces commandes dans le dossier du projet après avoir configuré l’auteur Git.

```sh
git init -b main
git add package.json retry-after.mjs retry-after.test.mjs
git commit -m "Add Retry-After exercise"
npm test
```

Le code initial a été vérifié avec **11 tests réussis et 8 échoués** sur 19. Il accepte certaines chaînes commençant par des chiffres comme `parseInt('2x', 10)` et ne traite pas correctement les valeurs négatives, décimales ou hors plage sûre. Ce test rouge est le point de départ.

## Ouvrir le projet et préciser le périmètre

Depuis le dossier du projet, la commande suivante fixe la version. `--host` limite l’accès aux connexions locales et `--auto-bootstrap-project-from-cwd` ajoute le dossier courant comme projet. Le paquet npm et l’exécutable peuvent être téléchargés au premier usage.

```sh
npm exec --yes --package=t3@0.1.9 -- t3 \
  --host 127.0.0.1 --auto-bootstrap-project-from-cwd .
```

La CLI lance un serveur local et une app web. Si vous utilisez déjà un serveur T3 Code, ouvrez-y le projet. L’installation de bureau et l’accès distant suivent des voies distinctes dans le [guide d’installation de cette version](https://github.com/pingdotgg/t3code/blob/v0.1.9/docs/user/install.md). Cet article ne configure ni service en arrière-plan ni exposition au réseau externe.

Choisissez le dossier et le fil, puis un fournisseur installé et authentifié. Selon le [guide des fils](https://github.com/pingdotgg/t3code/blob/v0.1.9/docs/user/thread-sidebar.md), **New worktree** crée une branche et un dossier de travail séparés. L’exercice de base utilise le dossier de travail existant. Si vous choisissez un nouveau worktree, exécutez aussi les commandes Git et npm suivantes dans ce dossier. Vérifiez d’abord le chemin et la branche du fil. Dans la zone de saisie, vérifiez le mode **Supervised**. Le [guide des permissions v0.1.9](https://github.com/pingdotgg/t3code/blob/v0.1.9/docs/user/permission-modes.md) indique Full access comme valeur initiale et Supervised comme mode demandant une approbation pour les commandes et modifications. Les détails, notamment les lectures autorisées, dépendent du fournisseur.

Envoyez ce prompt :

```text
Lisez d’abord retry-after.mjs et retry-after.test.mjs.
Corrigez retryAfterMs(header) selon ce contrat :

- Retirez les espaces en début et fin et n’acceptez que des secondes entières non négatives composées de chiffres ASCII.
- Renvoyez des millisecondes ; secondes et millisecondes doivent satisfaire Number.isSafeInteger.
- Renvoyez null pour les valeurs vides ou non textuelles, négatives, décimales, en notation exponentielle, avec caractères supplémentaires ou hors plage sûre.
- HTTP-date est hors périmètre et doit renvoyer null.
- Modifiez uniquement retry-after.mjs. Ne changez ni les tests ni package.json.
- N’installez pas de dépendances, n’effectuez pas de requêtes réseau et ne créez ni commit Git, ni push, ni PR.

Vérifiez avec npm test et indiquez la raison de la modification ainsi que les commandes réellement exécutées et leurs résultats.
Précisez explicitement si une commande n’a pas pu être exécutée.
```

Lorsqu’une approbation est demandée pour une modification ou commande, vérifiez qu’elle est nécessaire à l’exercice, par exemple le fichier visé ou `npm test`. Une consigne de périmètre ne remplace pas les permissions des outils. Ici l’agent ne doit pas committer ; vous décidez après réception des changements et résultats.

## Comment vérifier que « la correction est terminée » ?

Le [guide T3 Code de revue des changements](https://github.com/pingdotgg/t3code/blob/v0.1.9/docs/user/source-control.md) distingue les fichiers et diffs par tour des comparaisons de branches. Le diff d’un tour ne montre que ce tour ; comparez aussi à la branche de base avant fusion. Développez les appels de test dans la conversation pour vérifier commande, sortie et statut réels ; vous pouvez aussi les relancer dans un terminal.

```sh
git rev-parse --show-toplevel
git diff --name-only
git diff -- retry-after.mjs
git diff --exit-code -- retry-after.test.mjs package.json
npm test
```

Seul `retry-after.mjs` doit être modifié. Si la troisième commande affiche des changements ou échoue, vérifiez d’abord pourquoi tests ou configuration ont changé. Une réussite obtenue en réduisant les attentes des tests ne satisfait pas ce contrat. Vérifiez aussi `git status --short` pour les nouveaux fichiers.

Si l’agent indique ne pas avoir pu exécuter les tests, ne considérez pas cela comme une réussite : lancez vous-même `npm test`. Si des échecs restent, précisez entrée, attendu et résultat réel dans une nouvelle demande. Par exemple : « `0` doit valoir 0ms et `'2x'` doit valoir null. Conservez les tests et revérifiez ces deux cas. »

Voici l’**implémentation de référence vérifiée directement**. Comparez-la aux changements proposés après l’exercice. Pour l’exécuter, placez ce code dans `retry-after.mjs` à la racine du projet.

### `reference/retry-after.mjs`

```javascript
export function retryAfterMs(header) {
  if (typeof header !== 'string') return null;
  const value = header.trim();
  if (!/^[0-9]+$/.test(value)) return null;
  const seconds = Number(value);
  const milliseconds = seconds * 1000;
  return Number.isSafeInteger(seconds) && Number.isSafeInteger(milliseconds)
    ? milliseconds
    : null;
}
```

Après remplacement du code initial par la référence, les mêmes 19 tests ont tous réussi et le fichier de test initial est resté inchangé. Vérifier la plage sûre des entiers est distinct de fixer un plafond réel d’attente. Cette fonction n’exécute pas l’attente et n’est pas un analyseur HTTP-date complet ; définissez séparément le nombre de reprises et le budget total du client réel.

Pour enregistrer le travail vous-même après examen du diff et des tests, ne committez que le fichier modifié :

```sh
git add retry-after.mjs
git commit -m "Validate numeric Retry-After values"
```

À la fin, arrêtez le serveur au premier plan avec `Ctrl+C` dans le terminal où s’exécute T3 Code.

## Que vérifier si le démarrage échoue ?

| Symptôme | Première vérification |
| --- | --- |
| Fournisseur absent ou impossible à lancer | Installation et PATH sur le serveur, puis fournisseur dans Settings |
| Erreur d’authentification | Compte du fournisseur choisi et connexion sur l’ordinateur serveur |
| Changements absents du dossier initial | Fil utilisant un worktree séparé et chemin consulté |
| Diff ou fonctions de branche indisponibles | Dossier ouvert bien un dépôt Git et chemin du projet correct |
| Tests réussis mais changements hors périmètre | Diff et statut Git, y compris tests, configuration et nouveaux fichiers |

Le README officiel décrit un projet encore jeune pouvant contenir des erreurs. Après mise à jour de l’app ou de la CLI du fournisseur, conserver un petit contrat et une procédure de vérification facilite la comparaison plutôt que d’attendre une réponse fixe d’un même prompt.
