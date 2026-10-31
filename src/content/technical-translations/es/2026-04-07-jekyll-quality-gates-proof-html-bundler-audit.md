---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2026-04-07-jekyll-quality-gates-proof-html-bundler-audit",
  "routeSlug": "2026-04-07-jekyll-quality-gates-proof-html-bundler-audit",
  "kind": "post",
  "title": "Controles Astro: por qué un PR aprobado no despliega",
  "description": "Separa validación Astro y publicación Pages. Comprueba refs, dependencias correctas y condiciones de despliegue con 24 casos y seis mutaciones fallidas.",
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
  "draftSha256": "dfb665d0db7f893f4017d2534c6fd7f88170fccce93e9f76ac60fc940fc344f8",
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

Una compilación PR correcta demuestra que pasaron sus controles configurados. Aquí no publica al candidato: producción requiere además ref `main`, evento permitido y dependencia de compilación correcta.

Jekyll antes usaba `proof-html` y `bundler-audit`. Astro ahora usa `site-checks.yml` para validar y `site-quality-gates.yml` para Pages. Los controles Ruby afectan a las herramientas antiguas; no auditan las dependencias npm del sitio.

## Separar validación y despliegue

![Validar candidato, aplicar condición main y evento, desplegar artefacto comprobado](/assets/diagrams/technical/es-2026-04-07-jekyll-quality-gates-proof-html-bundler-audit.svg)

El [workflow del sitio](https://github.com/youdozi/youdozi.github.io/blob/main/.github/workflows/site-quality-gates.yml) pasa `${{ github.sha }}` al verificador común. El [workflow reutilizable](https://github.com/youdozi/youdozi.github.io/blob/main/.github/workflows/site-checks.yml) descarga ese ref, tiene tarea de compilación y permisos contents de solo lectura, y deja false la opción de artefacto Pages salvo que se active al invocarlo. La [documentación GitHub de `workflow_call`](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows) describe esa interfaz.

Las comprobaciones configuradas cubren fallos distintos:

| Comprobación | Qué puede demostrar |
| --- | --- |
| Pruebas Python y Node | Contratos probados de recopilación, idioma, publicación y renderizado |
| Ejemplos extraídos | Casos seleccionados en sus herramientas registradas |
| `npm run check` | Reglas de contenido y tipos/esquema Astro |
| `npm run build` | Salida estática, enlaces internos, imágenes, anclas y cobertura de migración |

Comprobar enlaces internos no demuestra disponibilidad externa. Un ejemplo aprobado no verifica todo comportamiento productivo y un artículo válido puede tener afirmaciones sin respaldo. El workflow tampoco ejecuta una auditoría general de vulnerabilidades npm.

## Reproducir los contratos de despliegue seleccionados

Con Node 24, ejecuta `npm ci` en una copia del repositorio. Guarda el archivo completo como `deploy-contract.mjs` en la raíz y ejecuta:

```sh
node deploy-contract.mjs
```

El script comprueba valores YAML reales y modela la condición fija sobre 24 combinaciones. Seis objetos workflow alterados deliberadamente deben fallar el contrato. No tiene operaciones de despliegue ni red.

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

La salida comprobada es:

```text
24 policy-model combinations and 6 rejected workflow mutations passed.
```

El modelo solo permite compilaciones correctas en `main` con `push` o `workflow_dispatch`. Rechaza las demás, incluida una rama de función despachada manualmente. `pull_request` suele usar el ref de fusión del PR, por lo que su éxito no cumple la condición. GitHub documenta [condiciones](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-jobs-with-conditions) y [dependencias correctas](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-jobs).

Es un modelo del ref/evento y dependencia correcta, no un intérprete Actions. Prueba éxito y fallo; no simula cancelación, ancestros omitidos, planificación, autorización, procedencia ni Pages. Las aserciones YAML hacen fallar una política modificada para revisión explícita, en vez de probar silenciosamente el modelo antiguo contra la configuración nueva.

## Confirmar el resultado publicado

Tras aprobar y fusionar, inspecciona commit de main, compilación y tarea deploy. Un PR verde con `deploy: skipped` es normal; compilar bien no demuestra publicación. Pages usa el artefacto comprobado según el [patrón Astro Pages](https://docs.astro.build/en/guides/deploy/github/).

Abre el artículo público y sus enlaces de idiomas; comprueba canonical, fechas y sitemap. IndexNow corre después con pasos tolerantes a fallos, así que puede fallar aunque Pages funcione. Aceptación de notificaciones y presencia en sitemap tampoco demuestran indexación ni impresiones.

El [artículo del flujo candidato](/en/posts/2026-04-07-jekyll-github-actions-content-pipeline/) explica la revisión Draft PR previa. Separa controles técnicos y decisión de publicar; ninguno sustituye comprobar las afirmaciones.
