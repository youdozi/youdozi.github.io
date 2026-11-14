---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2026-11-12-orca-worktree-guide",
  "routeSlug": "2026-11-12-orca-worktree-guide",
  "kind": "post",
  "title": "使用 Orca：用于代理、测试和审核的工作树工作流程",
  "description": "使用 Orca 项目和工作树来隔离编码任务，验证其测试和浏览器输出，并在提交之前检查其差异。",
  "categories": [
    "util"
  ],
  "tags": [
    "orca",
    "ai-agent",
    "git-worktree",
    "testing",
    "developer-tools"
  ],
  "sourcePath": "src/content/posts/en/2026-11-12-orca-worktree-guide.md",
  "sourceSha256": "4214532491f859b28104e614442c9bc3c33ecc9a00a62567a96d927bc90cffb6",
  "draftSha256": "fbb1f93ed275cdf03e4dc092822f73b3f8dadc2a749c123b1450168b6b0343b7",
  "manifestPath": ".pipeline/technical-translations/batch-156/manifest.json",
  "manifestSha256": "ed48dc20825daff8725d8eba3418b1ad885276b52c9752ba958f7a1705b24430",
  "publishedAt": "2026-11-14T15:16:43.783Z",
  "updatedAt": "2026-11-14T15:16:43.783Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 158,
    "approvedAt": "2026-11-14T15:16:43.783Z",
    "basis": "User requested all 63 language editions and instructed completed PRs to be merged; AI translation and independent AI review were performed, with no claim of human text review."
  }
}
---

**Orca 是一种开发环境，用于同时使用 Git 工作区、编码代理、终端、浏览器和变更审核。** 将一项任务放入一个工作树中，您可以在单独的分支和文件夹中处理不同的变更。使用实际工作路径、测试输出和与基本分支的差异来验证完成情况，而不是单独使用代理的答案。

主题是 Stably AI 的[Orca 官方应用](https://www.onorca.dev/)。本指南使用 macOS 上安装的 **Orca 1.4.256**、捆绑的 CLI 指南、Node.js 24.13.0、Python 3 和 Git。检查当前工作区检查、在 Orca 终端中运行示例测试、端口发现以及嵌入式浏览器中的显示。未执行创建或合并工作树或启动新的AI代理任务；下面的提示和创建命令是供读者练习的。

## 项目和工作树有何不同？

使用[官方第一会话指南](https://www.onorca.dev/docs/first-session)中的**添加存储库**打开本地 Git 存储库。即使 Orca 管理项目，源文件和提交仍保留在 Git 存储库中。分别准备模型/提供商的使用条款和身份验证。

| 元素 | 在本次练习中的角色 |
| --- | --- |
| 项目 | 对示例 Git 存储库和工作区进行分组 |
| 工作树 | 签出到特定分支及其工作视图的工作文件夹 |
| 代理人 | 建议在请求的范围内读取和更改文件以及运行命令 |
| 终端 | 在任务文件夹中运行测试和开发服务器 |
| 嵌入式浏览器 | 检查真实的开发服务器页面和边界值 |

[Orca 工作树文档](https://www.onorca.dev/docs/model/worktrees) 和 [CLI 指南](https://www.onorca.dev/docs/cli/overview) 解释了文件、分支和工作视图之间的关系。不要假设在 UI 中选择另一个工作树会自动更改已打开的 shell 的当前目录。 **检查终端中将执行命令的路径和分支**是第一步。

## 创建一个小示例并检查启动状态

![打开示例 Git 存储库，创建一个工作树并检查其路径和分支。要求代理更改一个文件，然后检查该工作树中的测试、开发服务器和浏览器。将 diff 和原始测试与 main 进行比较；如果满足要求，请自行提交，如果不满足，请请求修复。](/assets/diagrams/technical/zh-CN-2026-11-12-orca-worktree-guide.svg)

使用说明性运费政策：**订单金额满 50,000 韩元免运费，低于该金额时运费为 3,000 韩元**，并且仅接受非负安全整数。这不是真正的服务政策。将以下四个文件保存在新的 `orca-shipping-example` 文件夹中。不需要外部 npm 包。

### `package.json`

```json
{
  "name": "orca-shipping-example",
  "private": true,
  "type": "module",
  "engines": { "node": ">=24" },
  "scripts": { "test": "node --test shipping.test.mjs" }
}
```

### `shipping.mjs`

```javascript
export function shippingFee(orderTotal) {
  return orderTotal > 50_000 ? 0 : 3000;
}
```

### `shipping.test.mjs`

```javascript
import test from 'node:test';
import assert from 'node:assert/strict';
import { shippingFee } from './shipping.mjs';

for (const [total, expected] of [[0, 3000], [49_999, 3000], [50_000, 0], [50_001, 0]]) {
  test(`shippingFee(${total}) = ${expected}`, () => {
    assert.equal(shippingFee(total), expected);
  });
}
for (const [label, total] of [
  ['negative', -1],
  ['fraction', 50_000.5],
  ['string', '50000'],
  ['NaN', Number.NaN],
  ['Infinity', Number.POSITIVE_INFINITY],
  ['unsafe integer', Number.MAX_SAFE_INTEGER + 1],
]) {
  test(`rejects ${label}`, () => {
    assert.throws(() => shippingFee(total), RangeError);
  });
}
```

### `index.html`

```html
<!doctype html>
<html lang="ko">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Orca 배송비 예제</title>
<h1>배송비 경계값 확인</h1>
<pre id="result"></pre>
<script type="module">
  import { shippingFee } from './shipping.mjs';
  const totals = [49_999, 50_000, 50_001];
  document.querySelector('#result').textContent = totals
    .map(total => `${total}원 → 배송비 ${shippingFee(total)}원`)
    .join('\n');
</script>
</html>
```

在已准备好 Git 作者配置的示例文件夹中运行以下命令。

```sh
git init -b main
git add package.json shipping.mjs shipping.test.mjs index.html
git commit -m "Add shipping exercise"
npm test
```

起始代码错误处理了 `50,000` 边界，且未拒绝无效输入。实际运行确认 **3 项通过、7 项失败，共 10 项测试**。将此状态记录为基准提交，便于之后比较测试或配置是否也发生了变化。

## 向工作树中的代理请求更改

使用 Orca 的 **Add Repo** 打开示例存储库，然后检查连接到该存储库的终端中的 CLI。如果 CLI 不可用，请按照[官方 CLI 指南](https://www.onorca.dev/docs/cli/overview) 中的说明通过“设置”→“常规”→“Orca CLI”进行安装。这些命令假定 macOS `orca` 可执行文件。

```sh
orca skills get orca-cli
orca worktree current --json
```

分离工作时，从当前项目的 `main` 中创建一个新的工作树。

```sh
orca worktree create --name shipping-fee-fix \
  --parent-worktree active --base-branch main \
  --setup skip --activate --json
```

`--parent-worktree active` 记录Orca工作关系； `--base-branch main` 设置 Git 起点。这些是不同的设置。此示例跳过安装，因为没有要安装的外部依赖项。在实际项目中遵循适当的设置策略。由于此命令没有 `--agent`，因此它不请求代理任务。

在新工作区中打开终端并检查它。区分运行原始命令的 shell 和新工作树中的 shell。

```sh
git rev-parse --show-toplevel
git branch --show-current
orca worktree current --json
```

分支名称可能会因 Orca 前缀设置和其他配置而异。检查 JSON 中的工作树以及 Git 路径和分支是否是预期工作区后，打开准备好的代理选项卡并发送以下提示。可用的代理和聊天/CLI 执行取决于环境的配置。

```text
首先确认当前工作目录和分支，然后读取 shipping.mjs 和 shipping.test.mjs。
修改示例运费规则，使其满足以下约定：

- 订单金额达到或超过 50,000 韩元时运费为 0；低于该金额时为 3,000 韩元。
- 订单总额只接受非负安全整数；所有其他输入均抛出 RangeError。
- 仅修改 shipping.mjs；不要修改测试、package.json 或 index.html。
- 不要安装依赖、访问外部网络、提交、推送或创建 PR。

报告实际运行 npm test 的结果及修改原因。
如果无法执行某项检查，请明确说明。
```

即使 Orca 组一起工作，实际的工具权限也取决于代理和执行环境。仅提示限制并不能强制执行访问边界。本指南既不假设特定的权限按钮名称，也不假设所有提供程序具有相同的行为。

## 在同一工作区中检查测试和浏览器

在[嵌入式终端](https://www.onorca.dev/docs/terminal)中运行`npm test`。为了自动化，您可以在当前工作树中创建一个测试终端：

```sh
orca terminal create --title "tests" --command "npm test" --json
```

在自动化中，使用返回的终端句柄作为后续命令的目标。 `terminal read --screen` 读取当前屏幕；普通 `terminal read` 读取累积输出。接受的输入和命令或代理任务的实际启动是不同的事件。本指南验证了**所有 10 测试都通过**，并且只有 `shipping.mjs` 在为此目的创建的测试终端的输出中进行了更改。这是通过直接插入参考解法来检查的；它不是人工智能任务执行的记录。

要检查浏览器，请在同一工作树的终端中启动服务器。这假设端口 4877 可用。

```sh
python3 -m http.server 4877 --bind 127.0.0.1
```

检查另一个终端中的端口。

```sh
orca ports --json
orca tab create --url http://127.0.0.1:4877/ --json
```

如果服务器使用其他端口，请使用列表中的端口及其相应的 URL。 `orca ports` 显示的所有内容并非都是 HTTP 网页。根据[嵌入式浏览器指南](https://www.onorca.dev/docs/browser/overview)进行连接，并检查示例页面上的以下值：

```text
49999원 → 배송비 3000원
50000원 → 배송비 0원
50001원 → 배송비 0원
```

上面三行是在实际 Orca 浏览器中使用示例和参考解决方案进行检查的。检查后，在终端中停止带有 `Ctrl+C` 的服务器。不要因为任务完成而批量关闭无关终端；区分任务的进程和选项卡。

## 查看差异并仅记录更改的文件

在 [Orca diff 查看器](https://www.onorca.dev/docs/review/diff-viewer) 中检查基本引用和更改的文件。 [更改行注释](https://www.onorca.dev/docs/review/annotate-ai-diff) 让您将代理指向某个位置。例如：“50,000 won也应该是免费的。保留测试期望并检查比较运算符。”

同样与终端中的底座 `main` 进行比较。

```sh
git status --short
git diff main --name-only
git diff main -- shipping.mjs
git diff --exit-code main -- shipping.test.mjs package.json index.html
npm test
```

在此任务中仅应更改 `shipping.mjs`。如果测试、配置或页面发生更改，请首先确定原因。新文件可以从普通 diff 中省略，因此还要检查 Git 状态。运行代理无法自行执行的任何检查；不要将“完成”的答案视为通过结果。

以下是直接验证的参考方案。练习后将其与代理提出的代码进行比较。要运行它，请将此代码放在项目根目录下的 `shipping.mjs` 中。

### `reference/shipping.mjs`

```javascript
export function shippingFee(orderTotal) {
  if (!Number.isSafeInteger(orderTotal) || orderTotal < 0) {
    throw new RangeError('orderTotal must be a nonnegative safe integer');
  }
  return orderTotal >= 50_000 ? 0 : 3000;
}
```

使用参考解决方案，相同测试的所有 10 都通过了，并且保留了原始测试、配置和 HTML。检查条件后，仅提交任务分支上所需的文件。

```sh
git add shipping.mjs
git commit -m "Fix free-shipping boundary and input validation"
```

提交和合并到基础分支是单独的步骤。如果另一个任务更改了 `main`，请在合并之前检查差异并再次测试。工作树分隔源工作区，但它不是安全沙箱。不同的工作树仍然可以共享执行资源，例如数据库、端口、帐户和机密。

最初，在一项任务上练习此流程比立即添加多个代理更容易定位问题。当文件或功能边界和完成条件不同时，可以扩展到并行工作。
