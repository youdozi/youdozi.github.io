---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2026-04-07-jekyll-quality-gates-proof-html-bundler-audit",
  "routeSlug": "2026-04-07-jekyll-quality-gates-proof-html-bundler-audit",
  "kind": "post",
  "title": "Contrôles qualité Astro : ce que prouvent les PR verts et les déploiements",
  "description": "Séparer validation et déploiement Pages, puis contrôler le commit, les vérifications, l’artefact et les URL publiées.",
  "categories": [
    "blog",
    "automation"
  ],
  "tags": [
    "astro",
    "github-actions",
    "github-pages",
    "quality-gates",
    "testing"
  ],
  "sourcePath": "src/content/posts/en/2026-04-07-jekyll-quality-gates-proof-html-bundler-audit.md",
  "sourceSha256": "f5c09678ab191654be64bc9fd457df828066c7f199625a6b32c5d94a02200363",
  "draftSha256": "02ef1819b96938d047581d487b889bb078b6f0cc9c58b537f5be6be0b58ddf4b",
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
Une construction PR réussie établit que ses contrôles configurés ont réussi. Sur ce site, ce résultat ne publie pas le candidat : le déploiement en production exige en plus la ref `main`, un événement autorisé et une dépendance de construction réussie.

L’ancienne configuration Jekyll utilisait `proof-html` et `bundler-audit`. Le parcours Astro actuel utilise `site-checks.yml` pour la validation et `site-quality-gates.yml` pour le déploiement Pages. Les contrôles Ruby concernent toujours l’ancienne chaîne d’outils ; ils n’auditent pas les dépendances npm utilisées pour construire ce site.

## Séparer validation et déploiement

![Vérifier le candidat, appliquer la condition main/événement et déployer l’artefact vérifié](/assets/diagrams/technical/fr-2026-04-07-jekyll-quality-gates-proof-html-bundler-audit.svg)

Le [workflow du site](https://github.com/youdozi/youdozi.github.io/blob/main/.github/workflows/site-quality-gates.yml) transmet `${{ github.sha }}` au vérificateur partagé. Le [workflow réutilisable](https://github.com/youdozi/youdozi.github.io/blob/main/.github/workflows/site-checks.yml) extrait cette ref d’entrée, possède un job de construction et des permissions contents en lecture seule, et garde son option d’artefact Pages à false sauf activation par un appelant. La [documentation `workflow_call`](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows) de GitHub décrit cette interface.

Les contrôles configurés couvrent des échecs différents :

| Contrôle | Ce qu’il peut établir |
| --- | --- |
| Tests Python et Node | Contrats testés de collecte, langue, publication et rendu |
| Exemples extraits des articles | Cas d’exécution sélectionnés des exemples sur leurs chaînes d’outils consignées |
| `npm run check` | Règles de contenu et contrôles de types/schéma Astro |
| `npm run build` | Sortie statique, liens internes, images, ancres et couverture de migration |

Un contrôle de lien interne n’établit pas la disponibilité des URL externes. Un exemple réussi n’établit pas tous les comportements de production, et un article bien formé peut toujours contenir une affirmation sans preuve. Le workflow actif n’exécute pas non plus d’audit général des vulnérabilités npm.

## Reproduire les contrats de déploiement sélectionnés

Avec Node 24, exécutez `npm ci` dans une copie de ce dépôt. Enregistrez ce fichier complet sous `deploy-contract.mjs` à la racine du dépôt et exécutez :

```sh
node deploy-contract.mjs
```

Le script vérifie les véritables valeurs YAML, puis modélise la condition de déploiement fixe sur 24 combinaisons d’entrées. Six objets de workflow délibérément altérés doivent échouer au contrôle de contrat. Le script n’a aucune opération de déploiement ou de réseau.

### `deploy-contract.mjs`

```javascript
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import YAML from 'yaml';

const read = file => YAML.parse(readFileSync(`.github/workflows/${file}`, 'utf8'));
const site = read('site-quality-gates.yml');
const checks = read('site-checks.yml');
const condition = "github.ref == 'refs/heads/main' && (github.event_name == 'push' || github.event_name == 'workflow_dispatch')";
function verify(site, checks) {
    assert.equal(site.jobs.deploy.if, condition);
    assert.equal(site.jobs.deploy.needs, 'build');
    assert.equal(site.jobs.build.with.ref, '${{ github.sha }}');
    assert.equal(site.jobs.build.with.pages_artifact, '${{ ' + condition + ' }}');
    assert.deepEqual(Object.keys(checks.jobs), ['build']);
    assert.deepEqual(checks.permissions, { contents: 'read' });
    assert.equal(checks.on.workflow_call.inputs.pages_artifact.default, false);
    assert.equal(checks.jobs.build.steps[0].with.ref, '${{ inputs.ref }}');
    assert.ok(site.jobs.deploy.steps.some(step => step.uses === 'actions/deploy-pages@v4'));
}
verify(site, checks);

// A model of this fixed condition and successful dependency, not the Actions engine.
function allowed(ref, event, build) {
    return build === 'success' && ref === 'refs/heads/main' &&
        (event === 'push' || event === 'workflow_dispatch');
}
const expected = new Set([
    'refs/heads/main|push|success',
    'refs/heads/main|workflow_dispatch|success',
]);
let cases = 0;
for (const ref of ['refs/heads/main', 'refs/heads/develop', 'refs/heads/content/example', 'refs/pull/42/merge']) {
    for (const event of ['push', 'workflow_dispatch', 'pull_request']) {
        for (const build of ['success', 'failure']) {
            assert.equal(allowed(ref, event, build), expected.has(`${ref}|${event}|${build}`));
            cases++;
        }
    }
}

const mutations = [
    (site, checks) => { site.jobs.deploy.if = "github.event_name == 'pull_request'"; },
    (site, checks) => { site.jobs.deploy.needs = []; },
    (site, checks) => { site.jobs.build.with.ref = 'main'; },
    (site, checks) => { checks.permissions.pages = 'write'; },
    (site, checks) => { checks.on.workflow_call.inputs.pages_artifact.default = true; },
    (site, checks) => { checks.jobs.build.steps[0].with.ref = 'main'; },
];
for (const mutate of mutations) {
    const badSite = structuredClone(site), badChecks = structuredClone(checks);
    mutate(badSite, badChecks);
    assert.throws(() => verify(badSite, badChecks), assert.AssertionError);
}
console.log(`${cases} policy-model combinations and ${mutations.length} rejected workflow mutations passed.`);
```

La sortie vérifiée est :

```text
24 policy-model combinations and 6 rejected workflow mutations passed.
```

Seules les constructions réussies sur `main` avec `push` ou `workflow_dispatch` sont autorisées dans ce modèle. Toutes les autres combinaisons sont refusées, y compris une branche de fonctionnalité déclenchée manuellement. Une exécution `pull_request` utilise normalement une ref de fusion de pull request ; sa réussite ne satisfait donc pas la condition de déploiement du site. GitHub documente les [conditions de job](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-jobs-with-conditions) et les [exigences de réussite des dépendances](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-jobs).

C’est un modèle de la condition ref/événement sélectionnée et d’une dépendance de construction réussie, pas un interpréteur d’expressions Actions. Il teste les états de succès et d’échec ; il ne simule ni annulation, ni prédécesseurs ignorés, ni planification des runners, ni autorisation des tokens, ni provenance des artefacts, ni déploiement Pages. Les assertions YAML font échouer une politique modifiée pour examen explicite plutôt que de tester silencieusement l’ancien modèle avec une nouvelle configuration.

## Confirmer le résultat publié

Après approbation et fusion d’un candidat, inspectez le commit, le résultat de construction et le job de déploiement de l’exécution principale. Une exécution PR verte avec `deploy: skipped` est attendue ; une construction réussie seule ne prouve pas la publication. Le job Pages utilise l’artefact vérifié selon le [modèle de déploiement Astro Pages](https://docs.astro.build/en/guides/deploy/github/).

Ouvrez l’article public et ses liens de langue, puis vérifiez l’URL canonique, les dates des sources et l’entrée du sitemap. IndexNow s’exécute après le déploiement avec des étapes tolérant les échecs : il peut donc échouer alors que Pages réussit. L’acceptation d’une notification et la présence dans le sitemap ne prouvent pas non plus l’indexation ou les impressions dans les moteurs de recherche.

L’[article sur le workflow des candidats](/en/posts/2026-04-07-jekyll-github-actions-content-pipeline/) explique la revue Draft PR préalable. Conservez les contrôles techniques et la décision de publication comme responsabilités distinctes ; aucun ne remplace la vérification des affirmations de l’article.
