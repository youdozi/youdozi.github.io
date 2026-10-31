---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2026-04-07-jekyll-github-actions-content-pipeline",
  "routeSlug": "2026-04-07-jekyll-github-actions-content-pipeline",
  "kind": "post",
  "title": "De la chaîne Jekyll au Draft PR Astro : séparer candidat et publication",
  "description": "Préparer les contenus générés comme candidats, valider leur commit et ouvrir un Draft PR avant la publication.",
  "categories": [
    "blog",
    "automation"
  ],
  "tags": [
    "astro",
    "github-actions",
    "github-pages",
    "content-review",
    "automation"
  ],
  "sourcePath": "src/content/posts/en/2026-04-07-jekyll-github-actions-content-pipeline.md",
  "sourceSha256": "12226531a63ffece862798351d0562f1f29cc2b14f9731dad4dd5fece0e77637",
  "draftSha256": "95a12dcbb13e99e9a11421ccbb31b36ce220cc240f5032b9199859196e3c5418",
  "manifestPath": ".pipeline/technical-translations/batch-125/manifest.json",
  "manifestSha256": "1934910c02dbe893b786124f1d296d7adf9efbe921d40b3d2cfbceb8f70b4b33",
  "publishedAt": "2026-10-31T15:35:43.034Z",
  "updatedAt": "2026-10-31T15:35:43.034Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 125,
    "approvedAt": "2026-10-31T15:35:43.034Z",
    "basis": "User explicitly requested applying all missing technical-post languages, review, verification and deployment on 2026-11-01, with standing PR merge authorization. Human approval denotes publication authorization; linguistic review is performed by AI, not human/native review."
  }
}
---
Un générateur de contenu doit produire un candidat à examiner. Dans ce dépôt, une génération et une CI réussies conduisent à un Draft PR ; la publication suit une fusion distincte et le workflow Pages de la branche principale.

La chaîne Jekyll d’avril écrivait du Markdown et poussait le contenu généré. Le site utilise maintenant Astro, stocke les nouveaux digests bilingues en JSON et garde le candidat hors de `main` jusqu’à sa revue. Les fichiers `_posts` et les outils Ruby existants décrivent l’ancien site, et non la commande de publication actuelle.

## Suivre le commit du candidat

![Générer un candidat, valider son commit et ouvrir un Draft PR](/assets/diagrams/technical/fr-2026-04-07-jekyll-github-actions-content-pipeline.svg)

Le [workflow de contenu](https://github.com/youdozi/youdozi.github.io/blob/main/.github/workflows/dev-content-pipeline.yml) ne génère que sur `main`. Il recherche d’abord un PR ouvert `content/digest-review-` provenant de ce dépôt. S’il en existe un, il suspend un autre candidat, y compris une exécution manuelle de prévisualisation, jusqu’à la fusion ou la fermeture de ce PR.

Sans candidat en attente, `scripts/generate_digest.py` collecte et prépare les éditions anglaise et coréenne. Un fichier généré doit passer `npm run check` et `npm run build` avant qu’un commit soit poussé sur une nouvelle branche de revue. Le validateur partagé vérifie ensuite le SHA de ce commit généré, et le job de revue dépend de la réussite de la génération et de la validation. Cela suit le [comportement des dépendances entre jobs de GitHub](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-jobs).

Le job de revue rend les preuves, crée un Draft PR, ajoute l’URL de prévisualisation et déclenche explicitement le workflow du site sur la branche de revue. Cette branche peut être vérifiée sans satisfaire la condition de déploiement en production. Les [règles d’événements des tokens](https://docs.github.com/en/actions/concepts/security/github_token) comptent aussi lorsqu’une automatisation déclenche un autre workflow ; ne déduisez pas une exécution d’une seule requête API réussie.

## Exercer la logique de revue sans appeler GitHub

Utilisez Node 24 et exécutez `npm ci` dans une copie de ce dépôt. Enregistrez le fichier complet suivant sous `review-contract.mjs` à la racine du dépôt, puis exécutez :

```sh
node review-contract.mjs
```

Ce programme de test lit le véritable YAML du workflow, exécute ses deux extraits JavaScript avec des simulations locales et vérifie cinq cas de PR en attente ainsi que la séquence création/mise à jour/déclenchement. Sa simulation n’expose aucune opération de fusion. Il n’exécute pas le YAML du workflow, ne génère pas de vrai digest et ne fait aucun appel API.

### `review-contract.mjs`

```javascript
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import YAML from 'yaml';

const workflow = YAML.parse(readFileSync('.github/workflows/dev-content-pipeline.yml', 'utf8'));
const { generate, validate, review } = workflow.jobs;
assert.equal(generate.if, "github.ref == 'refs/heads/main'");
assert.deepEqual(review.needs, ['generate', 'validate']);
assert.equal(validate.with.ref, '${{ needs.generate.outputs.commit_sha }}');
assert.equal(validate.uses, './.github/workflows/site-checks.yml');
assert.equal(workflow.jobs.publish, undefined);

const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
const pendingScript = generate.steps.find(step => step.id === 'pending').with.script;
const runPending = new AsyncFunction('github', 'context', 'core', pendingScript);
const context = { repo: { owner: 'example', repo: 'blog' } };
const summary = { addRaw() { return this; }, async write() {} };
const cases = [
    [[], false],
    [[{ head: { repo: { full_name: 'example/blog' }, ref: 'content/digest-review-1' }, html_url: 'mock' }], true],
    [[{ head: { repo: { full_name: 'other/blog' }, ref: 'content/digest-review-1' } }], false],
    [[{ head: { repo: { full_name: 'example/blog' }, ref: 'content/manual-1' } }], false],
    [[{ head: { repo: null, ref: 'content/digest-review-1' } }], false],
];
for (const [pulls, expected] of cases) {
    let exists;
    const github = { rest: { pulls: { list() {} } }, paginate: async () => pulls };
    const core = { summary, setOutput(key, value) { if (key === 'exists') exists = value; } };
    await runPending(github, context, core);
    assert.equal(exists, expected);
}

const calls = [];
const github = { rest: {
    pulls: {
        async create(payload) { calls.push(['create', payload]); return { data: { number: 42, html_url: 'mock-pr' } }; },
        async update(payload) { calls.push(['update', payload]); },
    },
    actions: { async createWorkflowDispatch(payload) { calls.push(['dispatch', payload]); } },
} };
const core = { summary, setOutput() {} };
const requireMock = name => {
    assert.equal(name, 'node:fs');
    return { readFileSync: () => 'Mock review body' };
};
const script = review.steps.find(step => step.id === 'pr').with.script;
const runReview = new AsyncFunction('require', 'github', 'context', 'core', 'process', script);
await runReview(requireMock, github,
    { ...context, serverUrl: 'https://github.com', runId: 7 }, core,
    { env: { REVIEW_BRANCH: 'content/digest-review-7-1' } });
assert.deepEqual(calls.map(call => call[0]), ['create', 'update', 'dispatch']);
assert.equal(calls[0][1].draft, true);
assert.equal(calls[0][1].base, 'main');
assert.equal(calls[0][1].head, 'content/digest-review-7-1');
assert.equal(calls[2][1].workflow_id, 'site-quality-gates.yml');
assert.equal(calls[2][1].ref, calls[0][1].head);
console.log('5 pending-PR cases and the mocked draft/create-update-dispatch sequence passed.');
```

La sortie vérifiée est :

```text
5 pending-PR cases and the mocked draft/create-update-dispatch sequence passed.
```

Les cinq entrées distinguent l’absence de PR en attente, un PR digest local correspondant, un PR d’un autre dépôt, une autre branche locale et un dépôt head manquant. La réussite du programme démontre ces contrats de script sélectionnés, et non les permissions du token GitHub, la protection de branche, l’exactitude des sources ou l’ensemble du workflow hébergé.

## Demander un candidat et décider de sa publication

Dans **Actions → Dev Content Pipeline → Run workflow**, sélectionnez `main`. Laissez `preview` décoché pour préparer un candidat à examiner. Cochez-le pour le parcours à blanc, qui utilise `--dry-run --force --max-items 2` et ne committe pas de candidat. Un digest déjà en attente suspend toujours la génération. GitHub documente les [commandes manuelles de workflow](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow).

Ouvrez le Draft PR et sa prévisualisation bilingue. Vérifiez la date de la source, l’affirmation initiale et ses preuves, le périmètre de traduction, les liens et l’intérêt de publier l’élément. Les contrôles automatiques de code et de schéma ne prennent pas cette décision éditoriale. Modifiez le candidat si nécessaire, confirmez les contrôles du commit résultant, puis marquez-le prêt et fusionnez lorsque la publication est approuvée. Marquer simplement un brouillon prêt ne le déploie pas.

L’[article sur les contrôles qualité](/en/posts/2026-04-07-jekyll-quality-gates-proof-html-bundler-audit/) explique pourquoi une exécution PR verte peut légitimement ignorer le déploiement et quoi vérifier après la fusion. Pour l’ancien environnement Ruby, voir le [compte rendu de dépannage Jekyll](/ko/posts/2026-04-07-ruby-rbenv-jekyll-build-troubleshooting/), actuellement disponible en coréen.
