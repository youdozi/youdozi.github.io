---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2026-11-26-astro-clean-checkout",
  "routeSlug": "2026-11-26-astro-clean-checkout",
  "kind": "post",
  "title": "Pourquoi la vérification Astro échouait uniquement après un checkout propre",
  "description": "Un SVG manquant bloquait la préparation des brouillons d’actualité. Relancer la même vérification Astro après avoir généré les fichiers a permis d’isoler la cause.",
  "categories": [
    "blog"
  ],
  "tags": [
    "astro",
    "github-actions",
    "ci",
    "svg"
  ],
  "sourcePath": "src/content/posts/en/2026-11-26-astro-clean-checkout.md",
  "sourceSha256": "e1cc192ccc59b4557362e39f19838911c05e42d35d855acc766381023844e6e8",
  "draftSha256": "09a0b197c03c05841f4c39ddeff72b2e66c36a33e5488b4441750c13adbb107d",
  "manifestPath": ".pipeline/technical-translations/batch-2088/manifest.json",
  "manifestSha256": "311a7141caf0352bb2e15fd64983c3b0cb9e64b742168c9bdf7b204d20a13c75",
  "publishedAt": "2026-11-26T04:55:07.155Z",
  "updatedAt": "2026-11-26T04:55:07.155Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 200,
    "approvedAt": "2026-11-26T04:55:07.155Z",
    "basis": "The owner explicitly requested publication of the Astro CI retrospective in all supported blog languages (item 88)."
  }
}
---

Le workflow de préparation des brouillons d’actualité s’est arrêté avec l’erreur `ENOENT`. Sur les 4 échecs examinés, 3 se sont produits au moment où Astro lisait les dimensions des images d’articles existants. Après un checkout propre, les SVG référencés n’avaient pas encore été générés. En local, un fichier conservé depuis une compilation précédente pouvait suffire à faire passer la vérification. [Échec de la vérification du brouillon](https://github.com/youdozi/youdozi.github.io/actions/runs/45548722494)

## Exécuter la même vérification avant et après la génération des SVG

Dans un répertoire distinct, nous avons récupéré la révision en échec et lancé `npm run check`. Le code de sortie était 1. Après la préparation des ressources publiques avec `node scripts/prepare-public.mjs` dans ce même répertoire, la vérification a renvoyé le code 0. La compilation prépare aussi les ressources, mais la CI lançait la vérification en premier.

![Partir d’un checkout propre, générer les SVG, laisser Astro lire leurs dimensions, puis compiler le site.](/assets/diagrams/technical/fr-2026-11-26-astro-clean-checkout.svg)

Pour reproduire la séquence de la CI, utilisez Node.js 24 et Python 3.11 à la racine du dépôt. Installez les dépendances avec `npm ci`, puis lancez les commandes ci-dessous. Chaque étape doit réussir pour que la suivante démarre. [Correctif proposé et intégré](https://github.com/youdozi/youdozi.github.io/pull/198) · [Résultat de la compilation de la PR](https://github.com/youdozi/youdozi.github.io/actions/runs/45734945701)

```sh
node scripts/prepare-public.mjs &&
  npm run check &&
  npm run build
```

## Un autre échec pendant la génération

Lors d’une autre exécution, Gemini a renvoyé une réponse HTTP 503 pendant la génération. Le correctif conserve le même modèle et attend 1 seconde avant la première relance, puis 2 secondes avant la seconde. Toutes les requêtes d’une même exécution se partagent ces deux relances. [Échec à l’étape de génération](https://github.com/youdozi/youdozi.github.io/actions/runs/45098322259)

Pour un essai à blanc en coréen et en anglais à partir d’un article officiel de Spring, nous avons simulé uniquement les réponses du modèle lors de la génération et de la relecture. Nous avons comparé les citations au texte original, vérifié les liens et validé le contenu avec les schémas Python et Astro. L’essai n’a écrit ni brouillon ni entrée dans la file d’attente. La disponibilité réelle de Gemini reste hors du périmètre de cet essai.

Lorsqu’une vérification passe en local, cherchez la première commande qui lit le fichier manquant après un checkout propre. Sa position par rapport à l’étape qui produit ce fichier peut expliquer pourquoi la compilation complète réussit alors qu’une vérification antérieure échoue.
