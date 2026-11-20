---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2026-11-20-ui-ux-design-agent-skills",
  "routeSlug": "2026-11-20-ui-ux-design-agent-skills",
  "kind": "post",
  "title": "用 Claude Code 和 Codex 设计 UI/UX：用户流程、Figma 与无障碍技能",
  "description": "用 Claude Code 和 Codex 设计用户流程、Figma 设计系统、界面文案和无障碍交互，并用 Playwright 验证取消预订确认对话框的键盘操作和焦点行为。",
  "categories": [
    "ai"
  ],
  "tags": [
    "claude-code",
    "codex",
    "agent-skills",
    "figma",
    "ui-ux",
    "accessibility",
    "playwright"
  ],
  "sourcePath": "src/content/posts/en/2026-11-20-ui-ux-design-agent-skills.md",
  "sourceSha256": "b548a40ceebcfb72b0b19df913a07279080b56efc21e2264764c3cddd259e65a",
  "draftSha256": "3cad1708850dc7029c2d7d0920796c75d4adda2ddc03f1d16f0ce4656164a653",
  "manifestPath": ".pipeline/technical-translations/batch-172/manifest.json",
  "manifestSha256": "91fb61de3a3d1c432b5f074da43348e5ad1ab92b61742481f1cd4ac05bc2994e",
  "publishedAt": "2026-11-20T14:37:06.595Z",
  "updatedAt": "2026-11-20T14:37:06.595Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 172,
    "approvedAt": "2026-11-20T14:37:06.595Z",
    "basis": "User requested seven new language editions for each of four already published guides and approved parallel AI translation and verification. This records publication authorization."
  }
}
---

**画界面之前，先确定用户需要完成什么，以及在哪些步骤还能返回。** 以取消预订为例，用户需要先了解取消的后果，再决定保留还是取消预订。写清对话框文案、初始焦点及关闭后的焦点位置，实施和验证时才能采用同一套标准。

[上一篇文章](/ko/posts/2026-11-19-website-building-agent-skills/)介绍了网站制作的全过程，这篇专门讨论 UI/UX 阶段。本文以 2026年11月20日查阅的 Claude Code、Codex 公开技能和 Figma、Vercel、W3C 资料为依据，从规划到浏览器验证，走完一条取消预订流程。

## 按交付物选择技能

| 所需交付物 | 技能或工作方式 | 检查标准 |
| --- | --- | --- |
| 用户流程与页面状态 | 项目内的 `frontend-architecture-design` 指南 | 确认进入、确认、退出、处理中、成功和失败状态有定义。如果有实际用户调研资料，要区分观察结果和假设。 |
| 供评审的原型 | Codex 的 [Product Design 插件](https://github.com/openai/plugins/tree/main/plugins/product-design) | 做出可评审状态变化的原型，检查是否既有保留预订的路径，也有确认取消的路径。 |
| 视觉方向与 UI 代码 | Claude Code 的 [`frontend-design`](https://github.com/anthropics/skills/tree/main/skills/frontend-design) | 明确标题、说明和操作按钮的视觉优先级。确认标题变长或屏幕变窄时，信息含义和顺序仍能保留。 |
| 组装 Figma 界面 | Figma 插件的 [`figma-generate-design`](https://github.com/openai/plugins/tree/main/plugins/figma/skills/figma-generate-design) | 复用现有组件库中的按钮和对话框实例，为每种状态制作帧。检查组件与变量的关联是否保留。 |
| 设计系统组件库 | Figma 插件的 [`figma-generate-library`](https://github.com/openai/plugins/tree/main/plugins/figma/skills/figma-generate-library) | 根据代码里的设计令牌和组件创建或更新 Figma 变量和组件库。将变体及变量关联与实际代码中的命名核对。 |
| 实现已确认的 Figma 设计 | Figma 插件的 [`figma-design-to-code`](https://github.com/openai/plugins/tree/main/plugins/figma/skills/figma-design-to-code) | 读取目标帧，用现有 UI 代码实现。完成视觉比对后，再单独检查键盘交互和失败状态。 |
| UI 文案 | 项目内类似 `cms-ux-writing` 的 UX 文案指南 | 用动词说明按下按钮的结果。用“保留预订”“确认取消预订”一类的用词，让每项操作的后果明确。 |
| 界面审查 | Vercel 的 [`web-design-guidelines`](https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines) 与浏览器验证 | 从代码里找出可能的无障碍和 UI 问题，在浏览器中检查键盘顺序、焦点移动和不同屏幕尺寸的布局。 |

两项项目内指南展示了如何将团队已有的页面设计与文案规范做成可复用技能。它们不是特定产品的内置功能。如果有人负责审查预订流程，就先展示原型，将反馈更新到状态表，再交给实现环节。已有获批的 Figma 帧和代码组件时，也可以从实现和无障碍审查开始。

在 Claude Code 中，Anthropic 的 `frontend-design` 位于官方市场的 `example-skills` 套件。要在 Codex 中使用 Figma 技能，需要可用的 Figma 工具连接和文件访问权限。直接在 Figma 中制作页面或组件时，应将相应制作技能与插件的 `figma-use` 指南一起使用。读取待实现的设计时提供目标帧链接，绘制新帧时提供可编辑文件和可复用的组件库。 [Anthropic 安装指南](https://github.com/anthropics/skills#claude-code) · [Codex 的 Figma 插件](https://github.com/openai/plugins/tree/main/plugins/figma)

如果有品牌指南，同时提供实际使用的标志、配色、字体和禁止用法的示例。仅凭名字就把 Anthropic 的 `brand-guidelines` 用到团队品牌上，可能会引入 Anthropic 的配色和排版。这项技能的默认资料适用于 Anthropic 品牌。 [`brand-guidelines` 源文件](https://github.com/anthropics/skills/tree/main/skills/brand-guidelines)

## 将取消预订流程交给设计和开发

画界面之前，用表格定义用户操作及其结果。下表是设计示例。退款规则和取消费用须根据实际服务政策编写。

| 用户操作或服务器状态 | 界面行为 |
| --- | --- |
| 在预订详情中选择“打开取消选项” | 打开确认对话框，将焦点移到“保留预订”。 |
| 选择“保留预订”或按 Escape | 关闭对话框并保留预订。焦点回到打开对话框的按钮。 |
| 选择“确认取消预订” | 正式服务会提交请求并显示处理中状态。即使收到重复请求，也要防止重复处理。 |
| 服务器确认成功 | 将预订状态改为“预订已取消”并告知结果。 |
| 服务器确认失败 | 保留预订状态，说明失败原因以及用户接下来可以采取的操作。 |

对于难以撤销的操作，确认对话框可以把初始焦点放在影响最小的选项上。关闭时通常让焦点回到打开对话框的元素。如果该元素已消失，则选择另一个能让用户继续操作的元素。 [W3C 模态对话框模式](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/)

可以按以下方式把操作及其验收标准交给负责实现的代理。

> 请为预订详情设计取消确认对话框，复用现有的对话框和按钮。\
> 将初始焦点放在“保留预订”。按 Escape 关闭时，保留预订状态，\
> 并将焦点还给“打开取消选项”。\
> 发送取消请求后，分别呈现处理中、成功和失败状态。\
> 失败页面应给出重试或获取帮助的下一步操作。\
> 请说明各帧与状态的对应关系，以便审查界面和状态表后开始实现。

## 练习：检查确认对话框的焦点和两种结果

在浏览器中验证表格前两行和确认取消时的界面变化。练习中的确认取消只改变页面内部状态。服务器请求、失败处理及防止重复提交，需要在正式项目中另行验证。

![从预订状态打开确认对话框，检查初始焦点。用 Escape 或“保留预订”关闭时，检查预订状态和按钮焦点；确认取消时，检查取消状态提示。](/assets/diagrams/technical/zh-CN-2026-11-20-ui-ux-design-agent-skills.svg)

准备 Node.js 22 和 Chrome。在新工作目录运行 `npm init -y` 和 `npm install --save-dev playwright-core@1.64.1`。将下列代码保存为 `dialog-check.mjs`，再运行 `node dialog-check.mjs`。Chrome 的安装位置与默认位置不同时，设置 `CHROME_PATH`。 [Playwright 启动选项](https://playwright.dev/docs/api/class-browsertype#browser-type-launch)

```js
import assert from 'node:assert/strict';
import { chromium } from 'playwright-core';

const browser = await chromium.launch({
  executablePath: process.env.CHROME_PATH
    ?? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
});

try {
  const page = await browser.newPage({ viewport: { width: 360, height: 700 } });
  page.setDefaultTimeout(2000);
  await page.setContent(`
    <button id="open">취소 옵션 열기</button>
    <p role="status">예약 유지 중</p>
    <dialog aria-labelledby="title" aria-describedby="description">
      <h2 id="title">예약을 취소할까요?</h2>
      <p id="description">확정하면 예약 상태가 취소됨으로 바뀝니다.</p>
      <form method="dialog">
        <button value="keep" autofocus>예약 유지</button>
        <button value="cancel">예약 취소 확정</button>
      </form>
    </dialog>
    <script>
      const trigger = document.querySelector('#open');
      const dialog = document.querySelector('dialog');
      const status = document.querySelector('[role="status"]');

      trigger.addEventListener('click', () => {
        dialog.returnValue = '';
        dialog.showModal();
      });
      dialog.addEventListener('close', () => {
        if (dialog.returnValue === 'cancel') {
          status.textContent = '예약 취소됨';
        }
      });
    </script>
  `);

  const trigger = page.getByRole('button', { name: '취소 옵션 열기' });
  const dialog = page.getByRole('dialog', { name: '예약을 취소할까요?' });
  const status = page.getByRole('status');
  const focused = () => page.evaluate(
    () => document.activeElement?.textContent?.trim(),
  );

  for (const close of ['Escape', '예약 유지']) {
    await trigger.focus();
    await page.keyboard.press('Enter');
    await dialog.waitFor({ state: 'visible' });
    assert.equal(await focused(), '예약 유지', '초기 포커스');
    await page.keyboard.press(close === 'Escape' ? 'Escape' : 'Enter');
    await dialog.waitFor({ state: 'hidden' });
    assert.equal(await status.textContent(), '예약 유지 중');
    assert.equal(await focused(), '취소 옵션 열기', '닫은 뒤 포커스');
    console.log(`PASS ${close}: 예약 유지 및 포커스 복귀`);
  }

  await page.keyboard.press('Enter');
  await dialog.waitFor({ state: 'visible' });
  assert.equal(await focused(), '예약 유지', '초기 포커스');
  await page.keyboard.press('Tab');
  assert.equal(await focused(), '예약 취소 확정', '확정 버튼 포커스');
  await page.keyboard.press('Enter');
  await page.waitForFunction(
    () => document.querySelector('[role="status"]').textContent === '예약 취소됨',
  );
  await dialog.waitFor({ state: 'hidden' });
  assert.equal(await focused(), '취소 옵션 열기', '확정 뒤 포커스');
  console.log('PASS 예약 취소 확정: 상태 변경 및 포커스 복귀');
} finally {
  await browser.close();
}
```

下列输出记录了在 macOS 上使用 Chrome 的实际结果。示例保留了原来的韩语界面标签和日志。

```text
PASS Escape: 예약 유지 및 포커스 복귀
PASS 예약 유지: 예약 유지 및 포커스 복귀
PASS 예약 취소 확정: 상태 변경 및 포커스 복귀
```

对照实验将 `autofocus` 移到“确认取消预订”，初始焦点检查随即失败。练习验证了对话框的无障碍名称、键盘操作、初始焦点，以及关闭后的焦点和状态提示。实际页面还应检查用键盘移动时焦点是否可见、字体放大后是否仍能读到按钮和说明，以及辅助技术能否读出状态消息。 [WCAG 2.2](https://www.w3.org/TR/WCAG22/)
