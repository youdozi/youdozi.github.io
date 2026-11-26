---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2026-11-26-news-dry-run-guide",
  "routeSlug": "2026-11-26-news-dry-run-guide",
  "kind": "post",
  "title": "如何在 GitHub Actions 中验证新闻草稿而不发布",
  "description": "分别检查草稿能否通过验证，以及运行前后稿件、发布队列和状态文件是否一致。",
  "categories": [
    "blog"
  ],
  "tags": [
    "github-actions",
    "ci",
    "dry-run"
  ],
  "sourcePath": "src/content/posts/en/2026-11-26-news-dry-run-guide.md",
  "sourceSha256": "bbd2b23eadacc9df77585d34bf7ba6243a6a849fbbfcba51c6f2272b35553659",
  "draftSha256": "93a02be0783e3e0724e9437d06678795d5b4958549643d07e2f60049e1a074e6",
  "manifestPath": ".pipeline/technical-translations/batch-2092/manifest.json",
  "manifestSha256": "9a982e5784cecb3a4cc8afc502eaa7a3dabfd32dbeb039f0577cad485ee5cb2d",
  "publishedAt": "2026-11-26T07:02:16.794Z",
  "updatedAt": "2026-11-26T07:02:16.794Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 201,
    "approvedAt": "2026-11-26T07:02:16.794Z",
    "basis": "The owner authorized publication of the news draft dry-run guide in all eight blog languages in item 92."
  }
}
---

草稿即使通过了模式验证，也可能在发布队列里留下一个条目。测试需要分别检查两件事：退出码是否符合输入对应的预期，以及运行后的稿件、队列和状态文件是否与运行前一致。

## 分别测试预览成功和验证失败

在仓库根目录使用 Python 3 运行以下命令。这两个测试都使用临时目录，用预设数据替代订阅源、草稿生成结果和链接检查结果，无需联网或提供模型 API 密钥。

```sh
PYTHONPATH=scripts python3 -B -m unittest \
  test_bilingual_digest.PublicationTests.test_preview_validates_without_writing_content_or_state \
  test_bilingual_digest.PublicationTests.test_ai_or_link_failures_do_not_write
```

![测试输入分为两条路径。正常预览成功退出，AI 或链接出错时以失败退出。两条路径都会检查是否创建了稿件和状态目录。](/assets/diagrams/technical/zh-CN-2026-11-26-news-dry-run-guide.svg)

第一个测试传入 `--dry-run --force`，检查退出码是否为 0，以及输出是否为 `generated=false`。第二个测试传入 `--check-links`，分别模拟 AI 错误和链接错误，检查每次的退出码是否为 1。只要临时根目录下出现 `src` 或 `.pipeline`，测试就会失败。运行上述命令得到的结果是 `Ran 2 tests` 和 `OK`。

## 本地验证如何与 Spring 原文核对

另一次独立的本地验证选用了一篇 [Spring AI 官方文章](https://spring.io/blog/2026/11/24/spring-ai-tool-call-confirmation-park-resume)。隔离测试传入 `--dry-run --force --max-items 1 --check-links`，仅将 Gemini 生成和审阅草稿的响应替换为预设数据。单独执行 CLI 并传入这些参数，并不会自动注入预设响应。

获取原文时服务器返回 HTTP 200。测试检查了链接，将韩文和英文草稿中共 4 处引文与实际原文核对，并通过了 Python 和 Astro 两端的内容模式验证。输出为 `generated=false`。另行比对后，稿件、队列和状态文件共 3,333 个，运行前后的路径和内容全部一致。这次运行没有验证 Gemini 在线服务的可用性或生成质量。[本地运行记录](https://github.com/youdozi/youdozi.github.io/pull/198)

## 限制 PR 验证作业的权限

当时 PR 的常规 CI 中，必需的 `build / build` 检查通过，`deploy` 被跳过。与 Spring 在线原文核对的结果记录在上面的本地运行记录中。[PR 检查结果](https://github.com/youdozi/youdozi.github.io/actions/runs/45734945701) · [为什么 Astro 只在全新检出时检查失败（韩文）](https://youdozi.github.io/ko/posts/2026-11-26-astro-clean-checkout/)

如果单独设置验证作业，只为检出代码授予 `contents: read`，并省去发布凭据。即使仓库令牌只有只读权限，进程仍可修改本地文件，因此还需要对比运行前后的稿件、队列和状态文件。[GitHub 作业令牌说明](https://docs.github.com/en/actions/concepts/security/github_token)
