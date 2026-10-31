---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2026-04-07-jekyll-quality-gates-proof-html-bundler-audit",
  "routeSlug": "2026-04-07-jekyll-quality-gates-proof-html-bundler-audit",
  "kind": "post",
  "title": "Astro 质量关卡：为何 PR 通过仍未部署",
  "description": "区分 Astro 验证与 GitHub Pages 发布。用 24 种模型情况和六种失败变异检查提交引用、成功依赖与部署条件。",
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
  "draftSha256": "54d727c45d5f6916b14af5ee3248649b22067aa85587a88c33976d664774d799",
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

PR 构建通过说明配置的检查已通过。本网站不会因此发布候选：生产部署还要求 `main` 引用、允许的事件以及成功的构建依赖。

旧 Jekyll 配置使用 `proof-html` 和 `bundler-audit`。当前 Astro 使用 `site-checks.yml` 验证，以 `site-quality-gates.yml` 部署 Pages。Ruby 检查仍针对旧工具链，不审计构建本网站的 npm 依赖。

## 区分验证与部署

![检查候选、应用 main 事件条件并部署已检查产物](/assets/diagrams/technical/zh-CN-2026-04-07-jekyll-quality-gates-proof-html-bundler-audit.svg)

[网站工作流](https://github.com/youdozi/youdozi.github.io/blob/main/.github/workflows/site-quality-gates.yml)将 `${{ github.sha }}` 传给共享检查器。[可复用工作流](https://github.com/youdozi/youdozi.github.io/blob/main/.github/workflows/site-checks.yml)检出该输入引用，包含构建作业并仅有内容只读权限；除非调用方启用，否则 Pages 产物选项保持 false。GitHub 的 [`workflow_call` 文档](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows)介绍此接口。

配置的检查覆盖不同失败类型：

| 检查 | 可证明的范围 |
| --- | --- |
| Python 和 Node 测试 | 已测试的收集、语言、发布和渲染契约 |
| 提取的文章示例 | 记录工具链上所选示例执行情况 |
| `npm run check` | 内容规则与 Astro 类型和模式检查 |
| `npm run build` | 静态输出、内部链接、图片、锚点和迁移覆盖 |

内部链接检查不能证明外部 URL 可用。示例通过不证明所有生产行为，格式正确的文章仍可能包含无依据主张。当前工作流也不执行通用 npm 漏洞审计。

## 复现指定部署契约

使用 Node 24，在仓库检出目录运行 `npm ci`。将以下完整文件保存为根目录的 `deploy-contract.mjs` 并运行：

```sh
node deploy-contract.mjs
```

脚本检查实际 YAML 值，再对 24 种输入组合建模固定部署条件。六个故意改变的工作流对象必须无法通过契约检查。脚本没有部署或网络操作。

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

经检查的输出为：

```text
24 policy-model combinations and 6 rejected workflow mutations passed.
```

模型只允许 `main` 上由 `push` 或 `workflow_dispatch` 触发且构建成功的情况。其他组合全部拒绝，包括手动触发的功能分支。`pull_request` 运行通常使用 PR 合并引用，其成功不满足本网站部署条件。GitHub 分别介绍了[作业条件](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-jobs-with-conditions)与[成功依赖要求](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-jobs)。

这是对所选引用和事件条件及成功构建依赖的模型，不是 Actions 表达式解释器。它测试成功与失败，不模拟取消、跳过的祖先、运行器调度、令牌授权、产物来源或 Pages 部署。YAML 断言会让策略变化显式失败以供审核，而不是默默用旧模型测试新配置。

## 确认已发布结果

批准并合并候选后，检查 main 运行的提交、构建结果与部署作业。PR 成功且 `deploy: skipped` 属于预期情况；仅构建成功不能证明发布。Pages 作业使用已检查产物，遵循 [Astro Pages 部署模式](https://docs.astro.build/en/guides/deploy/github/)。

打开公开文章与语言链接，检查 canonical URL、来源日期和站点地图条目。IndexNow 在部署后以容错步骤运行，因此 Pages 成功时它仍可能失败。通知被接受或存在站点地图条目也不证明搜索引擎已收录或展示。

[候选工作流文章](/en/posts/2026-04-07-jekyll-github-actions-content-pipeline/)介绍之前的 Draft PR 审核。技术检查与发布决策应承担不同责任，两者都不能替代核查文章主张。
