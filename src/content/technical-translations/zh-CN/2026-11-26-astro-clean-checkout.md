---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2026-11-26-astro-clean-checkout",
  "routeSlug": "2026-11-26-astro-clean-checkout",
  "kind": "post",
  "title": "为什么 Astro 检查只在干净的检出目录中失败",
  "description": "新闻草稿工作流因缺少 SVG 而中断。在准备资源前后运行同一个 Astro 检查，就能定位原因。",
  "categories": [
    "blog"
  ],
  "tags": [
    "astro",
    "github-actions",
    "ci",
    "svg"
  ],
  "sourcePath": "src/content/posts/en/2026-11-26-astro-clean-checkout.md",
  "sourceSha256": "e1cc192ccc59b4557362e39f19838911c05e42d35d855acc766381023844e6e8",
  "draftSha256": "25fe6bd87825bf21a259e84227738121bd6d45f08490d913ee50ea60acc42d63",
  "manifestPath": ".pipeline/technical-translations/batch-2088/manifest.json",
  "manifestSha256": "311a7141caf0352bb2e15fd64983c3b0cb9e64b742168c9bdf7b204d20a13c75",
  "publishedAt": "2026-11-26T04:55:07.155Z",
  "updatedAt": "2026-11-26T04:55:07.155Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 200,
    "approvedAt": "2026-11-26T04:55:07.155Z",
    "basis": "The owner explicitly requested publication of the Astro CI retrospective in all supported blog languages (item 88)."
  }
}
---

新闻草稿工作流报出 `ENOENT` 后中断。我们调查了当时的 4 次失败，其中 3 次发生在 Astro 读取已有文章的图片尺寸时。刚检出代码时，这些文章引用的 SVG 尚未生成。如果本地留有上次构建生成的文件，同一个检查就有可能通过。[候选草稿检查失败的记录](https://github.com/youdozi/youdozi.github.io/actions/runs/45548722494)

## 在生成 SVG 前后运行同一个检查

我们在单独的目录中检出失败时的提交，运行 `npm run check`，退出码为 1。在同一目录运行 `node scripts/prepare-public.mjs` 准备公共资源后，再次检查，退出码为 0。构建也会准备资源，但 CI 先执行检查。

![从干净的检出目录开始，先生成 SVG，再由 Astro 读取图片尺寸，最后构建站点。](/assets/diagrams/technical/zh-CN-2026-11-26-astro-clean-checkout.svg)

要复现 CI 的执行顺序，请在仓库根目录使用 Node.js 24 和 Python 3.11，通过 `npm ci` 安装依赖，然后运行以下命令。每一步成功后才会执行下一步。[修复 PR](https://github.com/youdozi/youdozi.github.io/pull/198) · [PR 构建结果](https://github.com/youdozi/youdozi.github.io/actions/runs/45734945701)

```sh
node scripts/prepare-public.mjs &&
  npm run check &&
  npm run build
```

## 另一次失败发生在生成阶段

另一次运行中，Gemini 在生成阶段返回了 HTTP 503。修复后仍使用同一模型，首次重试前等待 1 秒，再次重试前等待 2 秒。一次运行中的所有请求共用这两次重试机会。[生成失败的记录](https://github.com/youdozi/youdozi.github.io/actions/runs/45098322259)

我们用 Spring 官方文章试跑了韩语和英语草稿的生成流程，只模拟了模型在生成和审阅环节的响应。我们对照真实原文核对了引文，检查了链接，并用 Python 和 Astro 的内容模式验证了草稿。试跑没有写入草稿或队列，也没有验证 Gemini 服务当时是否可用。

如果检查在本地通过，可以在干净的检出目录中找到最先读取缺失文件的命令。将它和生成文件的步骤对照，就能判断为什么完整构建可以成功，而先执行的检查却会失败。
