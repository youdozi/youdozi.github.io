---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2026-11-20-ponytail-skill-guide",
  "routeSlug": "2026-11-20-ponytail-skill-guide",
  "kind": "post",
  "title": "Ponytail 技能使用指南：用 Codex 完成小改动和回归测试",
  "description": "了解如何在 Codex 和 Claude Code 中调用 Ponytail，比较 Lite、Full 和 Ultra，并在 Codex CLI 中练习复用已有函数和运行 Node.js 回归测试。",
  "categories": [
    "ai"
  ],
  "tags": [
    "ponytail",
    "codex",
    "claude-code",
    "agent-skills",
    "refactoring",
    "nodejs"
  ],
  "sourcePath": "src/content/posts/en/2026-11-20-ponytail-skill-guide.md",
  "sourceSha256": "7b1777565ade628aa9381193123b7b19f84ba4c91e57779cba53f40b8b19b6de",
  "draftSha256": "a37d69a77386047d6270aad620e0fe26fb0c0e3c81c01ddae34dfbaa6cb5fe1d",
  "manifestPath": ".pipeline/technical-translations/batch-172/manifest.json",
  "manifestSha256": "9fbed8219e1f64a1b7901da9450c566e1c2c7b0ed64840e56f60a1b726fd39df",
  "publishedAt": "2026-11-20T14:40:06.354Z",
  "updatedAt": "2026-11-20T14:40:06.354Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 172,
    "approvedAt": "2026-11-20T14:40:06.354Z",
    "basis": "User requested seven new language editions for each of four already published guides and approved parallel AI translation and verification. This records publication authorization."
  }
}
---

**Ponytail 是一项技能，帮助 AI 编程代理复用现有代码，完成所要求的行为变更。** 例如，库存只有一件时如果显示为 `1 items`，先检查项目里是否已有处理单复数的函数。复用这个函数修正显示，再测试库存数量为 0 和 2 时的行为是否与之前一致。

## 在 Codex 和 Claude Code 中开始使用

如果 Codex 已安装独立版 Ponytail 技能，在对话输入框中输入 `$ponytail-help`，即可查看技能名称和模式。在 `$ponytail full` 后写明要改变的行为、需要保留的条件，以及验证命令。下面的练习使用安装在用户路径 `~/.agents/skills/ponytail/SKILL.md` 下的独立技能。在这种配置中，所选模式是当前对话的工作偏好，可用 `$ponytail off` 关闭。 [Codex 技能文档](https://learn.chatgpt.com/docs/build-skills)

Ponytail 项目也提供插件。使用 Codex CLI 时，在 shell 中运行下面两条命令。随后打开 Codex，在 `/hooks` 中查看两个钩子会运行什么。如需使用钩子，请审查后设为可信，再开启新对话。执行钩子的环境需要能从 `PATH` 找到 `node`。 [Ponytail 安装指南](https://github.com/DietrichGebert/ponytail/blob/main/INSTALL.md#codex)

```bash
codex plugin marketplace add DietrichGebert/ponytail
codex plugin add ponytail@ponytail
```

在 Claude Code 中，将下面两条命令逐行输入，再用 `/ponytail full` 选择模式。插件也提供 `/ponytail-review` 审查命令。Codex 插件中的审查技能带有插件名前缀，例如 `$ponytail:ponytail-review`。这里对两款插件的安装与钩子行为的说明来自公开文档。 [Claude Code 安装指南](https://github.com/DietrichGebert/ponytail/blob/main/INSTALL.md#claude-code) · [Ponytail 命令列表](https://github.com/DietrichGebert/ponytail#commands)

```text
/plugin marketplace add DietrichGebert/ponytail
/plugin install ponytail@ponytail
```

## 何时选择 Lite、Full 或 Ultra？

在独立版 Codex 技能中，只输入 `$ponytail` 时会使用默认模式 Full。

| 调用方式 | 工作方式 | 示例 |
| --- | --- | --- |
| `$ponytail lite` | 完成请求；若有实质上更简单的方案，简短说明。 | 修改团队已经敲定的界面文案。 |
| `$ponytail full` | 查看调用方和已有测试，以最小的完整改动实现所需行为，报告验证结果和剩余风险。 | 修复单数显示错误，并检查原有输入。 |
| `$ponytail ultra` | 推进所要求的工作，同时指出不必要的范围扩张。 | 修复某个页面的错误，并另外判断是否需要全面改造公共界面。 |

要控制改动范围，请写清楚**需要改什么、保留什么，以及如何验证**。权限检查、输入校验和数据保护等调用方依赖的行为，也应写进保留条件。技能影响代理的工作方式；文件可写范围和可执行命令由代理的权限设置决定。

## 练习：库存只有一件时显示 `1 item`

练习使用 Node.js 22.17.0 和 Codex CLI 0.169.0，在一个空白练习仓库中运行。要重建初始状态，请在 `stockLabel` 中使用下面的返回语句。`stock.test.mjs` 的第一项测试在初始状态下已有，第二项是这次新增的。

```javascript
return `${count} items`;
```

**提示示例** `$ponytail full` 修复 stockLabel(1) 返回 1 items 的问题。 0 和 2 仍用 items。复用现有的 formatCount， 为 stockLabel 添加回归测试，然后运行 `node --test`。 不要修改练习仓库外的文件，也不要提交。

![收到库存标签修复请求后，检查 stockLabel 和 formatCount。复用 formatCount，用回归测试检查 0、1、2 件时的显示，并记录结果。](/assets/diagrams/technical/zh-CN-2026-11-20-ponytail-skill-guide.svg)

`stock.mjs` 只改动了 `stockLabel` 的一行返回表达式，直接调用已能处理单复数的 `formatCount`。

```javascript
export function formatCount(count, noun) {
  return `${count} ${count === 1 ? noun : noun + 's'}`;
}

export function stockLabel(count) {
  return formatCount(count, 'item');
}
```

在 `stock.test.mjs` 中分别检查数量为 0、1、2 时的显示。将两个文件放入同一目录，再运行 `node --test`。

```javascript
import assert from 'node:assert/strict';
import test from 'node:test';
import { formatCount, stockLabel } from './stock.mjs';

test('formatCount handles singular and plural', () => {
  assert.equal(formatCount(1, 'item'), '1 item');
  assert.equal(formatCount(2, 'item'), '2 items');
});

test('stockLabel handles zero, one, and two items', () => {
  assert.equal(stockLabel(0), '0 items');
  assert.equal(stockLabel(1), '1 item');
  assert.equal(stockLabel(2), '2 items');
});
```

用修改前的代码运行新增测试时，数量为 1 的情况失败。预期是 `1 item`，实际却是 `1 items`。修改后得到以下结果。

```text
ok 1 - formatCount handles singular and plural
ok 2 - stockLabel handles zero, one, and two items
# tests 2
# pass 2
# fail 0
```

这次练习验证的范围是两项测试和两个文件的改动。代理报告完成后，可以对照实际的 `git diff` 和测试结果，核实是否复用了已有函数、是否遵守了要求的范围。

## 改动完成后指定审查范围

如果还安装了配套的独立技能，可以使用下列命令。说明要审查代码的哪一部分，能让结果更容易核实。 [Ponytail 命令列表](https://github.com/DietrichGebert/ponytail#commands)

| 调用方式 | 适用场景 |
| --- | --- |
| `$ponytail-review` | 审查当前 diff 和相关代码。可在创建 PR 前检查调用方和遗漏的回归测试。 |
| `$ponytail-audit` | 以只读方式检查整个仓库，按优先级整理发现的问题。 |
| `$ponytail-debt` | 汇总现有的 `shortcut:` 注释和早期的 `ponytail:` 注释以供检查。 |
| `$ponytail-gain` | 查看项目正式发布的基准报告。要衡量自己仓库里节省的时间或费用，需要另行做对比测试。 |
| `$ponytail-help` | 查看已安装技能的模式与调用方法。 |
