---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2026-11-27-mac-disk-cleanup-du-df",
  "routeSlug": "2026-11-27-mac-disk-cleanup-du-df",
  "kind": "post",
  "title": "Mac 构建因空间不足而中断：用 du 和 df 衡量清理效果",
  "description": "分别测量目录占用量和数据卷的可用空间，看看手动清理后实际多出了多少空间。",
  "categories": [
    "tips"
  ],
  "tags": [
    "macos",
    "disk-usage",
    "git"
  ],
  "sourcePath": "src/content/posts/en/2026-11-27-mac-disk-cleanup-du-df.md",
  "sourceSha256": "2114224ef5dde962e3cfc28f12de1aa1dbba58c0343db9c3e8e6277ce204cc19",
  "draftSha256": "539d07808cc98062b2073dbe14f935e4a77570eb0d6b1a59544405e4ac3d18fc",
  "manifestPath": ".pipeline/technical-translations/batch-21081/manifest.json",
  "manifestSha256": "bb8e7e6d53b468beba198431945a3813993246d6d1a8883806299692c81bfd7a",
  "publishedAt": "2026-11-26T22:37:28.844Z",
  "updatedAt": "2026-11-26T22:37:28.844Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 203,
    "approvedAt": "2026-11-26T22:37:28.844Z",
    "basis": "In item 107 the site owner approved publication of the Mac disk cleanup article. Item 108 requests publication in the eight existing site languages."
  }
}
---

Mac 磁盘空间不足，PostgreSQL 任务队列文章的本地完整构建中断了。远程检查通过，GitHub Pages 也部署成功。此前另一个工作进程报告过 `hostFault`，目前无法确认是否为同一起故障。[发布 PR #202](https://github.com/youdozi/youdozi.github.io/pull/202)

## 怎样选择清理目录

在另一次手动清理中，我从已结束的任务中选出 20 个目录，包括可重新生成的 `dist` 和 `.astro`，以及一次性验证用的依赖目录和构建目录。仍在使用的路径都已排除。

以下只读命令适用于 macOS，执行位置是包含这两个构建目录的 Git 仓库根目录。`du` 显示各个指定路径占用的空间，`git ls-files` 列出这些路径下受 Git 跟踪的文件，`git check-ignore` 则显示匹配忽略规则的路径。

```sh
du -sh ./dist ./.astro
git ls-files -- dist .astro
git check-ignore -- dist .astro
```

Git 忽略的目录也可能存有正在使用的文件。我逐一确认目录可以重新生成，而且没有运行中的任务使用它，才将其列入清理范围。

## 可用空间增加了多少

![先测量各目录的占用量并筛选，再比较清理前后数据卷的可用空间](/assets/diagrams/technical/zh-CN-2026-11-27-mac-disk-cleanup-du-df.svg)

所选目录合计占用 1.61 GiB。同一数据卷的可用空间从清理前的 6.41 GiB 增至清理后的 7.46 GiB，增加了约 1.05 GiB。

用下面的命令可以比较清理前后的 `Avail` 列。`df` 显示指定路径所在文件系统的可用空间。APFS 允许同一容器中的多个卷共享剩余空间。本次目录占用总量与可用空间增量存在差异，具体原因未能确定。[Apple 关于 APFS 空间共享的说明](https://support.apple.com/ko-kr/guide/security/seca6147599e/web)

```sh
df -h /System/Volumes/Data
```
