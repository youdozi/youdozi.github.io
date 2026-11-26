---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2026-11-26-news-dry-run-guide",
  "routeSlug": "2026-11-26-news-dry-run-guide",
  "kind": "post",
  "title": "Valider des brouillons d’actualité dans GitHub Actions sans les publier",
  "description": "Vérifier la validité du brouillon, puis comparer les manuscrits, la file de publication et les fichiers d’état avant et après l’exécution.",
  "categories": [
    "blog"
  ],
  "tags": [
    "github-actions",
    "ci",
    "dry-run"
  ],
  "sourcePath": "src/content/posts/en/2026-11-26-news-dry-run-guide.md",
  "sourceSha256": "bbd2b23eadacc9df77585d34bf7ba6243a6a849fbbfcba51c6f2272b35553659",
  "draftSha256": "118dbbcf436a02010f088534bc721b585334c52634c8402780aabae21cd5b64e",
  "manifestPath": ".pipeline/technical-translations/batch-2092/manifest.json",
  "manifestSha256": "9a982e5784cecb3a4cc8afc502eaa7a3dabfd32dbeb039f0577cad485ee5cb2d",
  "publishedAt": "2026-11-26T07:02:16.794Z",
  "updatedAt": "2026-11-26T07:02:16.794Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 201,
    "approvedAt": "2026-11-26T07:02:16.794Z",
    "basis": "The owner authorized publication of the news draft dry-run guide in all eight blog languages in item 92."
  }
}
---

Un brouillon peut respecter le schéma tout en laissant une entrée dans la file de publication. Le test doit donc répondre à deux questions. L’entrée produit-elle le code de sortie attendu ? Les manuscrits, la file et les fichiers d’état sont-ils identiques avant et après l’exécution ?

## Tester un aperçu valide et un échec de validation

Exécutez la commande suivante à la racine du dépôt avec Python 3. Les deux tests utilisent des répertoires temporaires et des données prédéfinies pour le flux, la génération du brouillon et la vérification des liens. Ils peuvent s’exécuter sans connexion réseau ni clé d’API pour le modèle.

```sh
PYTHONPATH=scripts python3 -B -m unittest \
  test_bilingual_digest.PublicationTests.test_preview_validates_without_writing_content_or_state \
  test_bilingual_digest.PublicationTests.test_ai_or_link_failures_do_not_write
```

![Un aperçu valide aboutit, tandis qu’une erreur de l’IA ou de lien provoque un échec. Les deux parcours vérifient si les répertoires des manuscrits et de l’état ont été créés.](/assets/diagrams/technical/fr-2026-11-26-news-dry-run-guide.svg)

Le premier test passe `--dry-run --force` et vérifie le code de sortie 0 ainsi que la valeur `generated=false`. Le second passe `--check-links`, simule séparément une erreur de l’IA et une erreur de lien, puis vérifie le code de sortie 1 dans chaque cas. Les deux tests échouent si `src` ou `.pipeline` apparaît à la racine temporaire. La commande ci-dessus a renvoyé `Ran 2 tests` et `OK`.

## Ce que l’essai local a vérifié dans l’article de Spring

Un essai local distinct a pris pour entrée un [article de l’équipe Spring AI](https://spring.io/blog/2026/11/24/spring-ai-tool-call-confirmation-park-resume). Dans un environnement isolé, le test a passé `--dry-run --force --max-items 1 --check-links` et injecté des réponses préparées uniquement pour la génération et la relecture par Gemini. Lancer directement la CLI avec ces options n’injecte pas ces réponses.

La requête vers l’original a renvoyé HTTP 200. Le test a vérifié les liens, comparé au texte en ligne les 4 citations réparties entre les brouillons coréen et anglais et validé le contenu avec les schémas Python et Astro. La sortie indiquait `generated=false`. Une comparaison distincte a retrouvé les mêmes chemins et contenus pour les 3 333 fichiers des manuscrits, de la file et de l’état avant et après l’essai. La disponibilité du service Gemini et la qualité de ses réponses en conditions réelles restent à vérifier. [Compte rendu de l’essai local](https://github.com/youdozi/youdozi.github.io/pull/198)

## Limiter les permissions du job de validation d’une PR

Dans la CI habituelle de la PR, la vérification obligatoire `build / build` a réussi et le job `deploy` a été ignoré. Le compte rendu de l’essai local documente la comparaison avec l’article de Spring. [Résultats des vérifications de la PR](https://github.com/youdozi/youdozi.github.io/actions/runs/45734945701) · [Pourquoi Astro échouait sur une copie de travail neuve (en coréen)](https://youdozi.github.io/ko/posts/2026-11-26-astro-clean-checkout/)

Pour un job de validation indépendant, accordez uniquement `contents: read` pour récupérer le dépôt et ne fournissez aucun identifiant de publication. Même avec un jeton en lecture seule sur le dépôt, le processus peut modifier les fichiers locaux. Comparez donc les manuscrits, la file et les fichiers d’état avant et après le test. [Documentation GitHub sur le jeton du job](https://docs.github.com/en/actions/concepts/security/github_token)
