---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ru",
  "translationKey": "2026-04-07-jekyll-quality-gates-proof-html-bundler-audit",
  "routeSlug": "2026-04-07-jekyll-quality-gates-proof-html-bundler-audit",
  "kind": "post",
  "title": "Контроли качества Astro: почему успешный PR не развёртывает сайт",
  "description": "Разделяйте проверку Astro и публикацию Pages. Проверьте ref коммита, успешные зависимости и условия развёртывания на 24 случаях и шести ошибочных мутациях.",
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
  "draftSha256": "1a8a299c3cd203f37886a116abd881920230728a0e7add4c0f802923fbe6ecb3",
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

Успешная сборка PR подтверждает прохождение настроенных проверок. На этом сайте она не публикует кандидата: производственное развёртывание дополнительно требует ref `main`, разрешённого события и успешной зависимой сборки.

Прежняя настройка Jekyll использовала `proof-html` и `bundler-audit`. Текущий процесс Astro использует `site-checks.yml` для проверки и `site-quality-gates.yml` для Pages. Проверки Ruby относятся к прежним инструментам; они не проверяют npm-зависимости сборки этого сайта.

## Разделяйте проверку и развёртывание

![Проверка кандидата, условия main и события, развёртывание проверенного артефакта](/assets/diagrams/technical/ru-2026-04-07-jekyll-quality-gates-proof-html-bundler-audit.svg)

[Workflow сайта](https://github.com/youdozi/youdozi.github.io/blob/main/.github/workflows/site-quality-gates.yml) передаёт `${{ github.sha }}` общему проверяющему workflow. [Повторно используемый workflow](https://github.com/youdozi/youdozi.github.io/blob/main/.github/workflows/site-checks.yml) извлекает этот входной ref, содержит задачу сборки и права contents только для чтения, оставляя опцию Pages-артефакта false, если вызывающий её не включает. [Документация GitHub по `workflow_call`](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows) описывает интерфейс.

Настроенные проверки охватывают разные ошибки:

| Проверка | Что подтверждает |
| --- | --- |
| Тесты Python и Node | Проверенные контракты сбора, языков, публикации и рендеринга |
| Извлечённые примеры статей | Выбранные случаи выполнения на записанных инструментах |
| `npm run check` | Правила контента и проверки типов/схемы Astro |
| `npm run build` | Статический результат, внутренние ссылки, изображения, якоря и охват миграции |

Проверка внутренних ссылок не подтверждает доступность внешних URL. Успешный пример не доказывает всё производственное поведение; корректно оформленная статья всё ещё может содержать необоснованное утверждение. Действующий workflow также не выполняет общий аудит уязвимостей npm.

## Воспроизведите выбранные контракты развёртывания

С Node 24 выполните `npm ci` в checkout этого репозитория. Сохраните полный файл как `deploy-contract.mjs` в корне и запустите:

```sh
node deploy-contract.mjs
```

Скрипт проверяет реальные значения YAML, затем моделирует фиксированное условие развёртывания для 24 сочетаний входов. Шесть намеренно изменённых объектов workflow должны провалить контракт. Скрипт не имеет операций deploy или сети.

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

Проверенный вывод:

```text
24 policy-model combinations and 6 rejected workflow mutations passed.
```

Модель разрешает только успешные сборки на `main` с `push` или `workflow_dispatch`. Остальные сочетания отклоняются, включая ручной запуск feature-ветки. Запуск `pull_request` обычно использует ref слияния PR, поэтому его успех не проходит условие сайта. GitHub описывает [условия задач](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-jobs-with-conditions) и [требования успешных зависимостей](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-jobs).

Это модель выбранного ref/события с успешной зависимой сборкой, не интерпретатор выражений Actions. Она проверяет успех и ошибку, не имитируя отмену, пропущенных предков, планирование runner, авторизацию токена, происхождение артефактов или Pages deploy. Утверждения YAML заставляют изменённую политику падать для явной проверки, а не незаметно сравнивать старую модель с новой конфигурацией.

## Подтвердите опубликованный результат

После одобрения и слияния кандидата проверьте коммит запуска main, результат сборки и задачу deploy. Успешный PR с `deploy: skipped` ожидаем; одна успешная сборка не доказывает публикацию. Задача Pages использует проверенный артефакт по [схеме развёртывания Astro Pages](https://docs.astro.build/en/guides/deploy/github/).

Откройте публичную статью и языковые ссылки, проверьте canonical URL, даты источников и sitemap. IndexNow запускается после развёртывания с допускающими ошибку шагами, поэтому может падать при успехе Pages. Принятие уведомления и запись sitemap также не доказывают индексацию или показы в поиске.

[Статья о кандидатах](/en/posts/2026-04-07-jekyll-github-actions-content-pipeline/) объясняет предшествующий Draft PR review. Разделяйте технические проверки и решение публиковать; ни одно не заменяет проверки утверждений статьи.
