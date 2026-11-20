---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2026-11-20-ponytail-skill-guide",
  "routeSlug": "2026-11-20-ponytail-skill-guide",
  "kind": "post",
  "title": "Utiliser le skill Ponytail — corrections ciblées et tests de régression avec Codex",
  "description": "Découvrez comment appeler Ponytail dans Codex et Claude Code, choisir entre Lite, Full et Ultra, puis réutiliser une fonction et lancer un test de régression Node.js avec Codex CLI.",
  "categories": [
    "ai"
  ],
  "tags": [
    "ponytail",
    "codex",
    "claude-code",
    "agent-skills",
    "refactoring",
    "nodejs"
  ],
  "sourcePath": "src/content/posts/en/2026-11-20-ponytail-skill-guide.md",
  "sourceSha256": "51597fdb68c31cae936e748ddf6719dce0d443cd28dabfb4a97b1ff62f991cf5",
  "draftSha256": "ad3bcc717d453804acb190e04b9d44f5982314ae3b8595c558caa582d1b8f983",
  "manifestPath": ".pipeline/technical-translations/batch-172/manifest.json",
  "manifestSha256": "91fb61de3a3d1c432b5f074da43348e5ad1ab92b61742481f1cd4ac05bc2994e",
  "publishedAt": "2026-11-20T14:37:06.595Z",
  "updatedAt": "2026-11-20T14:37:06.595Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 172,
    "approvedAt": "2026-11-20T14:37:06.595Z",
    "basis": "User requested seven new language editions for each of four already published guides and approved parallel AI translation and verification. This records publication authorization."
  }
}
---

**Ponytail aide un agent de programmation IA à réutiliser le code existant pour obtenir le comportement demandé.** Si l’affichage indique `1 items` alors qu’il n’y a qu’un article en stock, commencez par chercher dans le projet une fonction qui gère le singulier et le pluriel. Réutilisez-la pour corriger le libellé, puis vérifiez que les quantités 0 et 2 s’affichent toujours comme avant.

## Prendre en main Ponytail dans Codex et Claude Code

Si le skill autonome Ponytail est déjà installé dans Codex, saisissez `$ponytail-help` dans la conversation pour voir les noms et les modes disponibles. Après `$ponytail full`, indiquez le comportement à modifier, les conditions à préserver et la commande de vérification. L’exercice ci-dessous utilise le skill autonome installé dans `~/.agents/skills/ponytail/SKILL.md`. Dans cette configuration, le mode définit une préférence de travail pour la conversation en cours. Utilisez `$ponytail off` pour le désactiver. [Documentation Codex sur les skills](https://learn.chatgpt.com/docs/build-skills)

Le projet Ponytail distribue également un plugin. Pour Codex CLI, exécutez les deux commandes ci-dessous dans votre terminal. Ouvrez ensuite Codex et examinez dans `/hooks` ce que les deux hooks exécutent. Pour utiliser ces hooks, approuvez-les après examen et démarrez une nouvelle conversation. Leur environnement d’exécution a besoin de `node` dans son `PATH`. [Guide d’installation de Ponytail](https://github.com/DietrichGebert/ponytail/blob/main/INSTALL.md#codex)

```bash
codex plugin marketplace add DietrichGebert/ponytail
codex plugin add ponytail@ponytail
```

Dans Claude Code, saisissez les deux commandes ci-dessous une par une, puis choisissez le mode avec `/ponytail full`. Le plugin fournit aussi la commande de revue `/ponytail-review`. Dans le plugin Codex, le nom du skill de revue comporte le préfixe du plugin, comme dans `$ponytail:ponytail-review`. Les indications sur l’installation et le fonctionnement des hooks des deux plugins proviennent de la documentation publique. [Installation dans Claude Code](https://github.com/DietrichGebert/ponytail/blob/main/INSTALL.md#claude-code) · [Commandes de Ponytail](https://github.com/DietrichGebert/ponytail#commands)

```text
/plugin marketplace add DietrichGebert/ponytail
/plugin install ponytail@ponytail
```

## Quand utiliser Lite, Full ou Ultra ?

Avec le skill autonome pour Codex, la commande `$ponytail` seule sélectionne Full, le mode par défaut.

| Appel | Fonctionnement | Exemple |
| --- | --- | --- |
| `$ponytail lite` | Traite la demande et signale brièvement une solution plus simple lorsqu’elle présente un avantage concret. | Mettre à jour un texte d’interface déjà validé. |
| `$ponytail full` | Examine le code appelant et les tests existants, puis apporte le plus petit changement qui couvre tout le comportement demandé. Indique les résultats vérifiés et les risques restants. | Corriger le libellé au singulier et vérifier aussi les entrées existantes. |
| `$ponytail ultra` | Traite la demande tout en signalant les élargissements de périmètre superflus. | Corriger une erreur sur un écran et examiner séparément si une refonte de l’interface commune se justifie. |

Pour limiter le changement, précisez **quoi modifier, quoi préserver et comment le vérifier**. Parmi les conditions à préserver, pensez aux comportements dont dépend le code appelant, comme les contrôles d’autorisation, la validation des entrées et la protection des données. Le skill guide la façon de travailler de l’agent. Ses paramètres d’autorisation déterminent où il peut écrire et quelles commandes il peut exécuter.

## Exercice — afficher `1 item` pour un seul article en stock

L’exercice a été exécuté dans un dépôt d’essai vide avec Node.js 22.17.0 et Codex CLI 0.169.0. Pour recréer l’état de départ, remplacez la ligne de retour de `stockLabel` dans le code ci-dessous par ``return `${count} items`;``. Le premier test de
`stock.test.mjs` était déjà présent au départ. Le second a été ajouté pour ce changement.

> $ponytail full\
> Corrige le fait que stockLabel(1) renvoie 1 items.\
> Garde items pour 0 et 2. Réutilise la fonction formatCount existante,\
> ajoute un test de régression pour stockLabel et exécute node --test.\
> Ne modifie rien en dehors de ce dépôt d’essai et ne crée pas de commit.

![Après la demande de correction, examiner stockLabel et formatCount. Réutiliser formatCount, tester les libellés pour 0, 1 et 2 articles, puis noter les résultats.](/assets/diagrams/technical/fr-2026-11-20-ponytail-skill-guide.svg)

Seule l’expression de retour de `stockLabel` a changé dans `stock.mjs`. Elle appelle `formatCount`, qui gère déjà le singulier et le pluriel.

```javascript
export function formatCount(count, noun) {
  return `${count} ${count === 1 ? noun : noun + 's'}`;
}

export function stockLabel(count) {
  return formatCount(count, 'item');
}
```

Dans `stock.test.mjs`, vérifiez les libellés pour les quantités 0, 1 et 2. Placez les deux fichiers dans le même répertoire et exécutez `node --test`.

```javascript
import assert from 'node:assert/strict';
import test from 'node:test';
import { formatCount, stockLabel } from './stock.mjs';

test('formatCount handles singular and plural', () => {
  assert.equal(formatCount(1, 'item'), '1 item');
  assert.equal(formatCount(2, 'item'), '2 items');
});

test('stockLabel handles zero, one, and two items', () => {
  assert.equal(stockLabel(0), '0 items');
  assert.equal(stockLabel(1), '1 item');
  assert.equal(stockLabel(2), '2 items');
});
```

Avec le code d’origine, le test ajouté a échoué pour la quantité 1. Le résultat attendu était `1 item`, et le résultat obtenu était `1 items`. Après correction, l’exécution a produit la sortie suivante.

```text
ok 1 - formatCount handles singular and plural
ok 2 - stockLabel handles zero, one, and two items
# tests 2
# pass 2
# fail 0
```

L’exercice couvre deux tests et des modifications dans deux fichiers. Lorsque l’agent a terminé, comparez le `git diff` réel et les résultats des tests pour vérifier qu’il a réutilisé la fonction existante et respecté le périmètre demandé.

## Définir le périmètre de la revue après la correction

Si les skills autonomes complémentaires sont installés, utilisez les appels ci-dessous. Indiquez la partie du code à examiner pour faciliter la vérification des constats. [Commandes de Ponytail](https://github.com/DietrichGebert/ponytail#commands)

| Appel | Quand l’utiliser |
| --- | --- |
| `$ponytail-review` | Examine le diff actuel et le code associé. À utiliser avant d’ouvrir une PR pour contrôler les appels et repérer les tests de régression manquants. |
| `$ponytail-audit` | Examine le dépôt entier en lecture seule et classe les problèmes détectés par priorité. |
| `$ponytail-debt` | Recense les commentaires `shortcut:` et les anciens commentaires `ponytail:` pour examen. |
| `$ponytail-gain` | Affiche le rapport de benchmark publié par le projet. Pour mesurer les gains de temps ou de coût dans votre dépôt, effectuez une comparaison distincte. |
| `$ponytail-help` | Affiche les modes et les appels des skills installés. |
