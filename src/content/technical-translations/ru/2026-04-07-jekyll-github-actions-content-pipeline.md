---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ru",
  "translationKey": "2026-04-07-jekyll-github-actions-content-pipeline",
  "routeSlug": "2026-04-07-jekyll-github-actions-content-pipeline",
  "kind": "post",
  "title": "От автопубликации Jekyll к проверке Draft PR в Astro",
  "description": "Проследите двуязычный дайджест от генерации до проверки коммита, Draft PR и одобренной публикации. Запустите скрипты проверки локально с имитацией GitHub.",
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
  "draftSha256": "dd836fad047fead6dc3fb16f205f38b50edd68a2a9d3f36d4ef202047b2dff80",
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

Генератор контента должен создавать кандидата для проверки. В этом репозитории успешная генерация и CI приводят к Draft PR; публикация следует за отдельным слиянием и workflow Pages ветки main.

Апрельный pipeline Jekyll записывал Markdown и отправлял сгенерированный контент. Теперь сайт использует Astro, хранит новые двуязычные дайджесты как JSON и держит кандидата вне `main` до проверки. Существующие файлы `_posts` и инструменты Ruby описывают прежний сайт, а не текущую команду публикации.

## Проследите коммит кандидата

![Создание кандидата, проверка его коммита и открытие Draft PR](/assets/diagrams/technical/ru-2026-04-07-jekyll-github-actions-content-pipeline.svg)

[Workflow контента](https://github.com/youdozi/youdozi.github.io/blob/main/.github/workflows/dev-content-pipeline.yml) запускает генерацию только на `main`. Сначала он ищет открытый PR `content/digest-review-` из этого репозитория. При его наличии создание следующего кандидата, включая ручной preview, приостанавливается до слияния или закрытия PR.

Если ожидающего кандидата нет, `scripts/generate_digest.py` собирает и готовит английскую и корейскую версии. Сгенерированный файл должен пройти `npm run check` и `npm run build` до отправки коммита в новую ветку проверки. Общий валидатор затем проверяет SHA этого коммита, а задача review зависит от успеха генерации и валидации. Это соответствует [зависимостям задач GitHub](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-jobs).

Задача review отображает доказательства, создаёт Draft PR, добавляет URL preview и явно запускает site workflow на ветке проверки. Ветку можно проверить без выполнения условия производственного развёртывания. [Правила событий токена](https://docs.github.com/en/actions/concepts/security/github_token) тоже важны при запуске другого workflow автоматизацией; успешный API-запрос сам по себе не доказывает наличие запуска.

## Проверьте логику review без вызовов GitHub

Используйте Node 24 и выполните `npm ci` в checkout этого репозитория. Сохраните полный файл как `review-contract.mjs` в корне, затем выполните:

```sh
node review-contract.mjs
```

Проверка читает настоящий YAML workflow, выполняет два JavaScript-фрагмента с локальными mock и проверяет пять случаев ожидающего PR и последовательность create/update/dispatch. Mock не предоставляет операцию слияния. Она не выполняет YAML workflow, не создаёт настоящий дайджест и не вызывает API.

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

Проверенный вывод:

```text
5 pending-PR cases and the mocked draft/create-update-dispatch sequence passed.
```

Пять входов различают отсутствие ожидающего PR, подходящий локальный PR дайджеста, PR другого репозитория, другую локальную ветку и отсутствие head-репозитория. Успех подтверждает выбранные контракты скрипта, а не разрешения токена GitHub, защиту ветки, достоверность источника или весь размещённый workflow.

## Запросите кандидата и решите, что публиковать

В **Actions → Dev Content Pipeline → Run workflow** выберите `main`. Для подготовки кандидата оставьте `preview` выключенным. Включите его для dry-run с `--dry-run --force --max-items 2`; он не создаёт коммит кандидата. Уже ожидающий дайджест всё равно приостанавливает генерацию. GitHub описывает [ручное управление workflow](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow).

Откройте Draft PR и двуязычный preview. Проверьте дату источника, исходное утверждение и его обоснование, полноту перевода, ссылки и целесообразность публикации. Автоматические проверки кода и схемы не принимают это редакционное решение. При необходимости измените кандидата, подтвердите проверки итогового коммита, затем отметьте готовым и слейте после одобрения публикации. Одна отметка готовности не развёртывает сайт.

[Статья о контролях качества](/en/posts/2026-04-07-jekyll-quality-gates-proof-html-bundler-audit/) объясняет, почему успешный PR может корректно пропустить deploy и что проверять после слияния. О прежней среде Ruby см. [запись диагностики Jekyll](/ko/posts/2026-04-07-ruby-rbenv-jekyll-build-troubleshooting/), сейчас доступную на корейском.
