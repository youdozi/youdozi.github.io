---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2026-04-07-jekyll-quality-gates-proof-html-bundler-audit",
  "routeSlug": "2026-04-07-jekyll-quality-gates-proof-html-bundler-audit",
  "kind": "post",
  "title": "Astro-Qualitätsprüfungen: Was grüne PRs und Deployments belegen",
  "description": "Validierung und Pages-Deployment trennen und Commit, Prüfungen, Artefakt und veröffentlichte URLs kontrollieren.",
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
  "draftSha256": "3bb8d96491ac756684299a40381aed31c2d495e18c714828859d7845a05f1847",
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
Ein bestandener PR-Build belegt, dass seine konfigurierten Prüfungen bestanden wurden. Auf dieser Website veröffentlicht dieses Ergebnis den Kandidaten nicht: Das Produktionsdeployment erfordert zusätzlich die Ref `main`, ein zulässiges Ereignis und eine erfolgreiche Build-Abhängigkeit.

Die frühere Jekyll-Einrichtung verwendete `proof-html` und `bundler-audit`. Der aktuelle Astro-Ablauf verwendet `site-checks.yml` zur Validierung und `site-quality-gates.yml` zum Pages-Deployment. Ruby-Prüfungen betreffen weiterhin die alte Toolchain; sie auditieren nicht die npm-Abhängigkeiten, mit denen diese Website gebaut wird.

## Validierung und Deployment trennen

![Kandidaten prüfen, Main-Ereignisbedingung anwenden und geprüftes Artefakt deployen](/assets/diagrams/technical/de-2026-04-07-jekyll-quality-gates-proof-html-bundler-audit.svg)

Der [Website-Workflow](https://github.com/youdozi/youdozi.github.io/blob/main/.github/workflows/site-quality-gates.yml) übergibt `${{ github.sha }}` an die gemeinsame Prüfung. Der [wiederverwendbare Workflow](https://github.com/youdozi/youdozi.github.io/blob/main/.github/workflows/site-checks.yml) checkt diese Eingabe-Ref aus, besitzt einen Build-Job und nur lesende Contents-Berechtigungen und lässt seine Pages-Artefaktoption auf false, sofern ein Aufrufer sie nicht aktiviert. GitHubs [`workflow_call`-Dokumentation](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows) beschreibt diese Schnittstelle.

Die konfigurierten Prüfungen decken unterschiedliche Fehler ab:

| Prüfung | Was sie belegen kann |
| --- | --- |
| Python- und Node-Tests | Geprüfte Verträge zu Sammlung, Sprache, Veröffentlichung und Rendering |
| Extrahierte Artikelbeispiele | Die ausgewählten Ausführungsfälle der Beispiele auf ihren dokumentierten Toolchains |
| `npm run check` | Inhaltsregeln und Astro-Typ-/Schemaprüfungen |
| `npm run build` | Statische Ausgabe sowie interne Links, Bilder, Anker und Migrationsabdeckung |

Eine Prüfung interner Links belegt keine Erreichbarkeit externer URLs. Ein bestandenes Beispiel belegt nicht jedes Produktionsverhalten, und ein formal korrekter Artikel kann weiterhin unbelegte Aussagen enthalten. Der aktive Workflow führt auch kein allgemeines npm-Schwachstellenaudit aus.

## Die ausgewählten Deployment-Verträge reproduzieren

Führen Sie mit Node 24 `npm ci` in einem Checkout dieses Repositorys aus. Speichern Sie diese vollständige Datei als `deploy-contract.mjs` im Repository-Stamm und führen Sie Folgendes aus:

```sh
node deploy-contract.mjs
```

Das Skript prüft die tatsächlichen YAML-Werte und modelliert anschließend die feste Deployment-Bedingung für 24 Eingabekombinationen. Sechs absichtlich veränderte Workflow-Objekte müssen die Vertragsprüfung nicht bestehen. Das Skript besitzt keine Deployment- oder Netzwerkoperation.

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

Die geprüfte Ausgabe lautet:

```text
24 policy-model combinations and 6 rejected workflow mutations passed.
```

In diesem Modell sind nur erfolgreiche Builds auf `main` mit `push` oder `workflow_dispatch` zulässig. Alle anderen Kombinationen werden abgelehnt, auch ein manuell gestarteter Feature-Branch. Ein `pull_request`-Lauf verwendet gewöhnlich eine Pull-Request-Merge-Ref; sein Erfolg erfüllt daher nicht die Deployment-Bedingung dieser Website. GitHub dokumentiert sowohl [Job-Bedingungen](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-jobs-with-conditions) als auch [Anforderungen an erfolgreiche Abhängigkeiten](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-jobs).

Dies ist ein Modell der ausgewählten Ref-/Ereignisbedingung samt erfolgreicher Build-Abhängigkeit, kein Interpreter für Actions-Ausdrücke. Es testet Erfolgs- und Fehlerzustände; es simuliert weder Abbruch, übersprungene Vorgänger, Runner-Planung, Token-Autorisierung, Artefaktherkunft noch ein Pages-Deployment. Die YAML-Assertions lassen eine geänderte Richtlinie zur ausdrücklichen Prüfung scheitern, statt stillschweigend das alte Modell gegen eine neue Konfiguration zu testen.

## Das veröffentlichte Ergebnis bestätigen

Prüfen Sie nach Freigabe und Zusammenführung eines Kandidaten Commit, Build-Ergebnis und Deploy-Job des Main-Laufs. Ein grüner PR-Lauf mit `deploy: skipped` ist erwartbar; ein erfolgreicher Build allein belegt keine Veröffentlichung. Der Pages-Job verwendet das geprüfte Artefakt gemäß dem [Astro-Pages-Deployment-Muster](https://docs.astro.build/en/guides/deploy/github/).

Öffnen Sie den öffentlichen Artikel und seine Sprachlinks und prüfen Sie anschließend kanonische URL, Quelldaten und Sitemap-Eintrag. IndexNow läuft nach dem Deployment mit fehlertoleranten Schritten und kann daher scheitern, während Pages erfolgreich ist. Auch die Annahme einer Benachrichtigung und das Vorhandensein in der Sitemap belegen weder Suchmaschinenindexierung noch Impressionen.

Der [Artikel zum Kandidatenworkflow](/en/posts/2026-04-07-jekyll-github-actions-content-pipeline/) erläutert die vorgelagerte Draft-PR-Prüfung. Halten Sie technische Prüfungen und Veröffentlichungsentscheidung als getrennte Verantwortlichkeiten fest; keines ersetzt die Prüfung der Artikelaussagen.
