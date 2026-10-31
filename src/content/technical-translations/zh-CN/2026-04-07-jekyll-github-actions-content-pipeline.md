---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2026-04-07-jekyll-github-actions-content-pipeline",
  "routeSlug": "2026-04-07-jekyll-github-actions-content-pipeline",
  "kind": "post",
  "title": "从 Jekyll 自动发布到 Astro Draft PR 审核",
  "description": "跟踪双语摘要从生成到特定提交验证、Draft PR 和批准发布的流程，并用模拟 GitHub 调用在本地运行审核脚本。",
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
  "draftSha256": "1858d5961f8edd0bbbcdafe81b2d15749175895cfdd46971923c1d2467798e99",
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

内容生成器应产生待审核候选内容。此仓库中，生成与 CI 成功后创建 Draft PR；发布还需单独合并并执行主分支 Pages 工作流。

四月的 Jekyll 流水线写入 Markdown 并推送生成内容。如今网站使用 Astro，以 JSON 保存新的双语摘要，并在审核前将候选内容留在 `main` 之外。现有 `_posts` 文件和 Ruby 工具描述旧网站，不是当前发布命令。

## 跟踪候选提交

![生成候选内容、验证提交并创建 Draft PR](/assets/diagrams/technical/zh-CN-2026-04-07-jekyll-github-actions-content-pipeline.svg)

[内容工作流](https://github.com/youdozi/youdozi.github.io/blob/main/.github/workflows/dev-content-pipeline.yml)只在 `main` 上生成。先检查本仓库是否有未关闭的 `content/digest-review-` PR。如有，则暂停下一候选内容，包括手动预览，直到该 PR 合并或关闭。

没有待处理候选时，`scripts/generate_digest.py` 收集并准备英文和韩文版本。生成文件必须通过 `npm run check` 和 `npm run build`，才能提交并推送至新审核分支。共享验证器随后检查生成提交的 SHA，审核作业依赖生成和验证均成功。这遵循 GitHub 的[作业依赖行为](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-jobs)。

审核作业渲染证据、创建 Draft PR、添加审核预览 URL，并显式在审核分支触发网站工作流。该分支可接受检查而不满足生产部署条件。自动化触发另一个工作流时，还需考虑[令牌事件规则](https://docs.github.com/en/actions/concepts/security/github_token)；不能仅凭 API 请求成功推断运行已发生。

## 不调用 GitHub，验证审核逻辑

使用 Node 24，在此仓库检出目录运行 `npm ci`。将以下完整文件保存为根目录的 `review-contract.mjs`，然后运行：

```sh
node review-contract.mjs
```

测试工具读取真实工作流 YAML，用本地模拟执行两段 JavaScript，并检查五种待处理 PR 情况以及创建、更新、触发顺序。模拟不提供合并操作。它不执行工作流 YAML，不生成真实摘要，也不调用 API。

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

经检查的输出为：

```text
5 pending-PR cases and the mocked draft/create-update-dispatch sequence passed.
```

五种输入分别为无待处理 PR、匹配的本地摘要 PR、其他仓库 PR、不同本地分支，以及缺少 head 仓库。通过测试只证明所选脚本契约，不证明 GitHub 令牌权限、分支保护、来源准确性或完整托管工作流。

## 请求候选内容并决定发布范围

在 **Actions → Dev Content Pipeline → Run workflow** 选择 `main`。不勾选 `preview` 会准备审核候选；勾选则执行使用 `--dry-run --force --max-items 2` 的 dry-run，不提交候选。已有待处理摘要仍会暂停生成。GitHub 文档介绍了[手动工作流控件](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow)。

打开 Draft PR 及双语预览。检查来源日期、原始主张及支持证据、翻译范围、链接，以及是否值得发布。自动代码和模式检查不能作出该编辑决策。必要时修改候选，确认新提交的检查，再在发布获批后标记就绪并合并。仅将草稿标记就绪不会部署。

[质量关卡文章](/en/posts/2026-04-07-jekyll-quality-gates-proof-html-bundler-audit/)解释为何成功的 PR 运行可以正确跳过部署，以及合并后应验证什么。旧 Ruby 环境请参见当前提供韩文版的 [Jekyll 故障排查记录](/ko/posts/2026-04-07-ruby-rbenv-jekyll-build-troubleshooting/)。
