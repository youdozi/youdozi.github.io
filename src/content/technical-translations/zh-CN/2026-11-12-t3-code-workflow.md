---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2026-11-12-t3-code-workflow",
  "routeSlug": "2026-11-12-t3-code-workflow",
  "kind": "post",
  "title": "T3 Code指南：从小的代码更改到差异和测试验证",
  "description": "使用可执行节点示例、有限权限、差异和测试，使用 T3 Code v0.1.9 启动 AI 编码任务，同时区分参考解决方案和 AI 输出。",
  "categories": [
    "util"
  ],
  "tags": [
    "t3-code",
    "ai-agent",
    "coding-agent",
    "testing",
    "javascript"
  ],
  "sourcePath": "src/content/posts/en/2026-11-12-t3-code-workflow.md",
  "sourceSha256": "da83ebd4864d4a4b015af522789e363b4a8695b6424368db9bfd1652f7761089",
  "draftSha256": "4545d56ba297deedc9b00e52eec3d2224f7edfdd6e671367df0dd5e26a7e3dc7",
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

**T3 Code将计算机上安装的编码代理连接到项目、对话、权限和更改文件界面。** 将代码委托给代理时，小范围和可验证的完成标准比长请求更重要。本指南遵循从请求到差异和测试验证的数字 `Retry-After` 解析器修复。

主题是[官方T3代码项目](https://github.com/pingdotgg/t3code/tree/v0.1.9)。它与 T3 堆栈分开，后者使用 `create-t3-app` 创建 Web 应用程序。官方自述文件描述了连接现有提供商，包括 Codex、Claude Code 和 Cursor。安装 T3 Code和准备提供商的登录和订阅/API 条款是单独的步骤。

基准为 [v0.1.9 版本](https://github.com/pingdotgg/t3code/releases/tag/v0.1.9)，于 2026 年 11 月 12 日确认。示例在 macOS 上使用 Node.js 24.13.0 和 Git 检查，也检查了 T3 Code CLI 帮助与本地服务器启动。**没有向提供商发送 AI 任务。** 以下参考解法是直接测试过的实现，不是 T3 Code 的实际输出，也不是模型性能测量。

## T3 Code和提供商如何划分责任？

T3 Code显示工作项目和线程、提供者选择、权限请求和更改。连接的代理读取和修改文件或运行命令。看到工具调用并不意味着测试已自动运行并通过：检查命令并返回结果。

按照[安装指南](https://github.com/pingdotgg/t3code/blob/v0.1.9/docs/user/install.md)，安装您将使用的提供程序并在**运行 T3 Code服务器的计算机**上完成身份验证。此练习首先选择一个已经准备好的提供商。无需将登录详细信息或 API 密钥粘贴到提示中。

## 准备一个小型 Git 项目和失败的测试

![在 Git 项目中保存起始代码和固定测试并确认失败。在 T3 Code中，选择项目、提供商和监督权限，然后发送有界变更请求。批准代理的文件更改和命令，比较差异、原始测试和结果，如果满足约定，则自行提交更改，如果不满足，则请求更正。](/assets/diagrams/technical/zh-CN-2026-11-12-t3-code-workflow.svg)

将这三个文件保存在新的 `t3-code-example` 文件夹中。这些 Node 测试不使用外部包或 API 调用。在两种 `Retry-After` 形式中，本练习仅支持 **`delay-seconds`，即整数秒**。 HTTP-date 超出范围，必须返回 `null`。有关完整的标头语法，请参阅 [RFC 9110 的 Retry-After 定义](https://www.rfc-editor.org/rfc/rfc9110.html#name-retry-after)。

### `package.json`

```json
{
  "name": "t3-code-retry-after-example",
  "private": true,
  "type": "module",
  "engines": { "node": ">=24" },
  "scripts": { "test": "node --test retry-after.test.mjs" }
}
```

### `retry-after.mjs`

```javascript
export function retryAfterMs(header) {
  const seconds = Number.parseInt(header, 10);
  return Number.isFinite(seconds) ? seconds * 1000 : null;
}
```

### `retry-after.test.mjs`

```javascript
import test from 'node:test';
import assert from 'node:assert/strict';
import { retryAfterMs } from './retry-after.mjs';

const cases = [
  ['2', 2000],
  ['0', 0],
  [' 2 ', 2000],
  ['0002', 2000],
  ['', null],
  ['   ', null],
  [undefined, null],
  [null, null],
  [2, null],
  ['0x10', null],
  ['2x', null],
  ['-1', null],
  ['1.5', null],
  ['1e3', null],
  ['Infinity', null],
  ['Wed, 21 Oct 2015 07:28:00 GMT', null],
  ['9007199254740', 9007199254740000],
  ['9007199254741', null],
  ['9007199254740991', null],
];
for (const [input, expected] of cases) {
  test(`retryAfterMs(${JSON.stringify(input)})`, () => {
    assert.equal(retryAfterMs(input), expected);
  });
}
```

在已准备好 Git 作者配置的项目文件夹中运行这些命令。

```sh
git init -b main
git add package.json retry-after.mjs retry-after.test.mjs
git commit -m "Add Retry-After exercise"
npm test
```

已确认起始代码有 **11 项测试通过、8 项失败**，总计 19 项。它接受某些以数字开头的字符串，例如 `parseInt('2x', 10)`，并且不能正确处理负数、小数或超出安全范围的值。失败的测试是练习的起点。

## 打开项目并指定更改范围

从项目文件夹运行以下命令以固定版本。 `--host` 限制对本地连接的访问​​，`--auto-bootstrap-project-from-cwd` 将当前文件夹添加为项目。 npm 包和可执行文件可以在首次使用时下载。

```sh
npm exec --yes --package=t3@0.1.9 -- t3 \
  --host 127.0.0.1 --auto-bootstrap-project-from-cwd .
```

CLI 启动本地服务器和 Web 应用程序。如果您已使用 T3 Code服务器，请在该环境中打开项目。桌面安装和远程访问遵循[此版本的安装指南](https://github.com/pingdotgg/t3code/blob/v0.1.9/docs/user/install.md) 中的单独路径。本指南不会配置后台服务或将其公开给外部网络。

选择项目文件夹和线程，然后选择已安装并经过身份验证的提供程序。根据[线程指南](https://github.com/pingdotgg/t3code/blob/v0.1.9/docs/user/thread-sidebar.md)，New worktree（新工作树）创建一个单独的分支和工作目录。基本练习假设准备好的文件夹的现有工作目录。如果您选择新的工作树，也请在该文件夹中运行后续的 Git 和 npm 命令。首先检查线程的工作路径和分支。在消息输入区域，检查权限是否为 **Supervised（受监督）**。 [v0.1.9 权限指南](https://github.com/pingdotgg/t3code/blob/v0.1.9/docs/user/permission-modes.md) 表示初始默认值为 Full access（完全访问），而 Supervised 会请求批准命令和文件更改。允许哪些读取等详细信息因提供商而异。

发送此提示：

```text
首先读取retry-after.mjs和retry-after.test.mjs。
修复 retryAfterMs(header) 以满足此约定：

- 修剪周围的空白并仅接受由 ASCII 数字组成的非负整数秒。
- 返回毫秒；秒和毫秒都必须满足 Number.isSafeInteger。
- 对于空值或非字符串值、负数、小数、指数表示法、尾随字符和安全范围之外的值，返回 null。
- HTTP-date 在此范围之外，必须返回 null。
- 仅修改retry-after.mjs。不要更改测试或 package.json。
- 请勿安装依赖项、发出网络请求、提交、推送或创建 PR。

使用 npm test 进行验证并报告更改的原因以及实际运行的命令及其结果。
如果您无法运行命令，请明确说明。
```

当要求批准文件更改或命令时，请检查是否有必要进行此练习，例如预期文件或 `npm test`。提示中的范围指令不会取代工具权限设置。在这个例子中，代理没有被要求提交；您在收到变更和验证结果后决定。

## 如何验证“修复已完成”？

[T3 Code更改审阅指南](https://github.com/pingdotgg/t3code/blob/v0.1.9/docs/user/source-control.md) 区分更改的文件和每次分支比较的差异。回合差异显示该回合的工作，因此在合并之前也与基础分支进行比较。在会话中展开测试工具调用以检查实际命令、输出和状态；您还可以在终端中重新运行它们。

```sh
git rev-parse --show-toplevel
git diff --name-only
git diff -- retry-after.mjs
git diff --exit-code -- retry-after.test.mjs package.json
npm test
```

仅应更改 `retry-after.mjs`。如果第三个命令打印更改或失败，请首先确定测试或配置更改的原因。通过降低测试期望而获得的通过结果并不是满足此合同的修复。还要检查 `git status --short` 是否有新文件。

如果代理报告无法运行测试，请勿将其视为通过；自己运行`npm test`。如果仍然存在失败，请缩小后续请求中的输入、期望值和实际结果范围。例如：“`0` 必须是 0ms，`'2x'` 必须是 null。保留测试并再次检查这两种情况。”

下面是**直接验证的参考实现**。将其与代理在练习后建议的更改进行比较。要运行它，请将此代码放置在项目根目录的 `retry-after.mjs` 中。

### `reference/retry-after.mjs`

```javascript
export function retryAfterMs(header) {
  if (typeof header !== 'string') return null;
  const value = header.trim();
  if (!/^[0-9]+$/.test(value)) return null;
  const seconds = Number(value);
  const milliseconds = seconds * 1000;
  return Number.isSafeInteger(seconds) && Number.isSafeInteger(milliseconds)
    ? milliseconds
    : null;
}
```

将启动器替换为参考实现后，相同测试的所有 19 通过，原始测试文件保持不变。检查安全整数范围与设置实际重试延迟上限是分开的。该函数既不是等待执行器，也不是完整的 HTTP-date 解析器；分别设置客户端的实际重试次数和总时间预算。

要在检查差异和测试后自行记录工作，请仅提交更改的文件：

```sh
git add retry-after.mjs
git commit -m "Validate numeric Retry-After values"
```

完成后，在运行 T3 Code的终端中使用 `Ctrl+C` 停止前台服务器。

## 如果无法启动应该检查什么？

| 症状 | 首先检查 |
| --- | --- |
| 提供程序丢失或无法运行 | 检查服务器计算机上的安装和路径以及“设置”中的提供程序设置 |
| 认证错误 | 检查所选提供商帐户并登录服务器计算机 |
| 更改不会出现在原始文件夹中 | 检查线程是否使用单独的工作树以及是否正在查看相同的路径 |
| 差异或分支功能不可用 | 检查打开的文件夹是否为Git仓库且项目路径是否正确 |
| 测试通过，但更改超出范围 | 检查 diff 和 Git 状态，包括测试、配置和其他文件 |

官方自述文件将其描述为可能包含错误的早期项目。更新应用程序或提供商 CLI 后，保留像这样的小型合同和验证程序，比期望相同的提示产生固定答案更容易比较结果。
