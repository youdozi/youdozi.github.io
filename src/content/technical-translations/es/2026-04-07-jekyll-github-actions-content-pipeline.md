---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2026-04-07-jekyll-github-actions-content-pipeline",
  "routeSlug": "2026-04-07-jekyll-github-actions-content-pipeline",
  "kind": "post",
  "title": "De publicación automática Jekyll a revisión Draft PR en Astro",
  "description": "Sigue un resumen bilingüe desde generación a validación del commit, Draft PR y publicación aprobada. Ejecuta localmente los scripts de revisión con llamadas GitHub simuladas.",
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
  "draftSha256": "cdd1e3f82e8082af00930f0926799b7c1b777af22feffd060312adfb682787e1",
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

Un generador de contenido debe producir un candidato de revisión. En este repositorio, generación y CI correctos llevan a un Draft PR; la publicación sigue a una fusión separada y al workflow Pages de main.

El pipeline Jekyll de abril escribía Markdown y enviaba contenido generado. Ahora el sitio usa Astro, guarda nuevos resúmenes bilingües como JSON y mantiene al candidato fuera de `main` hasta revisarlo. Los archivos `_posts` y herramientas Ruby describen el sitio anterior, no la orden de publicación actual.

## Seguir el commit candidato

![Generar candidato, validar su commit y abrir un Draft PR](/assets/diagrams/technical/es-2026-04-07-jekyll-github-actions-content-pipeline.svg)

El [workflow de contenido](https://github.com/youdozi/youdozi.github.io/blob/main/.github/workflows/dev-content-pipeline.yml) genera solo en `main`. Primero busca un PR `content/digest-review-` abierto de este repositorio. Si existe, pausa otro candidato, incluida una vista previa manual, hasta fusionarlo o cerrarlo.

Sin candidato pendiente, `scripts/generate_digest.py` recopila y prepara ediciones inglesa y coreana. El archivo debe pasar `npm run check` y `npm run build` antes de enviar el commit a una rama nueva. El validador compartido comprueba ese SHA, y review depende del éxito de generación y validación. Sigue el [comportamiento de dependencias de GitHub](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-jobs).

La tarea review representa evidencias, crea Draft PR, añade la URL previa y despacha explícitamente el workflow del sitio en la rama. Puede comprobarse sin cumplir la condición productiva. También importan las [reglas de eventos del token](https://docs.github.com/en/actions/concepts/security/github_token) al activar otro workflow; una solicitud API correcta no demuestra por sí sola una ejecución.

## Probar la lógica de revisión sin llamar a GitHub

Usa Node 24 y ejecuta `npm ci` en una copia del repositorio. Guarda el archivo completo como `review-contract.mjs` en la raíz y ejecuta:

```sh
node review-contract.mjs
```

Este programa lee el YAML real, ejecuta sus dos fragmentos JavaScript con mocks locales y comprueba cinco casos de PR pendiente más create/update/dispatch. El mock no ofrece fusión. No ejecuta el workflow YAML, genera un resumen real ni llama API.

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

La salida comprobada es:

```text
5 pending-PR cases and the mocked draft/create-update-dispatch sequence passed.
```

Las cinco entradas distinguen ningún PR pendiente, uno local de resumen coincidente, otro repositorio, otra rama local y repositorio head ausente. Pasar demuestra esos contratos, no permisos del token, protección de ramas, precisión de fuentes ni todo el workflow alojado.

## Solicitar un candidato y decidir qué publicar

En **Actions → Dev Content Pipeline → Run workflow**, selecciona `main`. Deja `preview` sin marcar para preparar un candidato. Márcalo para la prueba sin cambios, que usa `--dry-run --force --max-items 2` y no registra candidato. Un resumen pendiente sigue pausando la generación. GitHub documenta los [controles manuales](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow).

Abre Draft PR y su vista previa bilingüe. Comprueba fecha de fuente, afirmación original y respaldo, alcance de traducción, enlaces y mérito de publicación. Los controles de código y esquema no deciden editorialmente. Cambia lo necesario, confirma las comprobaciones del commit final, marca listo y fusiona cuando se apruebe publicar. Marcar listo no despliega.

El [artículo de controles de calidad](/en/posts/2026-04-07-jekyll-quality-gates-proof-html-bundler-audit/) explica por qué un PR correcto puede omitir despliegue y qué verificar al fusionar. Para Ruby anterior, consulta el [registro de diagnóstico Jekyll](/ko/posts/2026-04-07-ruby-rbenv-jekyll-build-troubleshooting/), actualmente en coreano.
