---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2026-10-30-node2shell-brotli-runtime-patching",
  "routeSlug": "2026-10-30-node2shell-brotli-runtime-patching",
  "kind": "post",
  "title": "Node2Shell 响应：追踪 Brotli 解压并验证 Node.js 发布",
  "description": "检查 CVE-2026-111497 修复、Brotli 输入路径和可能误导的版本标签。收集运行时证据，区分安装完成与每个工作进程、副本实际采用。",
  "categories": [
    "security"
  ],
  "tags": [
    "node2shell",
    "nodejs",
    "brotli",
    "security"
  ],
  "sourcePath": "src/content/posts/en/2026-10-30-node2shell-brotli-runtime-patching.md",
  "sourceSha256": "9f8abe774ed0a87c0a07284163ad858f1f4ff629708131dff5f1b6088b23b959",
  "draftSha256": "94a44817fef1d5bad9b07a888751bf39afdb60b34449241da9bbe84d33ed8728",
  "manifestPath": ".pipeline/technical-translations/batch-078/manifest.json",
  "manifestSha256": "e685b2de5dafd8cfff8e8e996fa2b09613becb072bdd575b58b9eca9651474a3",
  "publishedAt": "2026-10-31T02:49:44.828Z",
  "updatedAt": "2026-10-31T02:49:44.828Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 118,
    "approvedAt": "2026-10-31T02:49:44.828Z",
    "basis": "2026-10-31 user instruction “진행해줘” immediately following delivery of the reviewed 72 complete translations in PR #118; interpreted as authorization to publish exactly batch-078 in all six languages. Separate AI language review is recorded in the manifest; this does not claim a human line-by-line review. Excludes the older 120 technical drafts and 318 pending news translations."
  }
}
---
Node2Shell 修复意味着将 Node.js 替换为已修复的运行时，并验证每个解压不可信 Brotli 数据的工作进程均已采用它。[Node.js 安全公告](https://nodejs.org/en/blog/vulnerability/october-2026-security-releases)将 **CVE-2026-111497** 定义为其捆绑 Brotli 解码器中的越界写入。更新 npm 软件包和替换运行时是不同的操作。

## 所有 Brotli 用法的暴露程度都一样吗？

相关路径会**解压**压缩输入。由 `node:zlib` 处理的、攻击者提供的畸形 Brotli 数据可能破坏进程内存，导致崩溃、内存泄露或远程代码执行。仅用 Brotli 压缩发出的响应，或仅启用 HTTP/2，并不能确立这条路径。Node.js 项目将此问题定级为高危。

除了请求体，还应追踪外部 HTTP 响应、上传、文件和队列任务的自动解压。例如，[body-parser 文档](https://expressjs.com/en/resources/middleware/body-parser/)介绍了 Brotli 自动解压。应检查安装的中间件版本与选项；未在应用代码中找到 `brotliDecompress`，不能证明不存在暴露。后台任务即使没有面向互联网的监听端口，也可能解压外部数据。

## 哪些 Node.js 发行版包含修复？

下表列出包含此 CVE 修复的官方安全发行版，核对日期为 2026年10月30日。它不将最新建议版本固定下来。部署时应检查同一供应商受支持的版本及后续公告。

| Node.js 分支 | 官方已修复发行版 |
| --- | --- |
| 22.x | [22.23.4](https://nodejs.org/en/blog/release/v22.23.4) |
| 24.x | [24.22.1](https://nodejs.org/en/blog/release/v24.22.1) |
| 26.x | [26.12.1](https://nodejs.org/en/blog/release/v26.12.1) |

对于发行版、嵌入式产品或自定义构建，使用供应商的完整软件包修订号和修复证据。不要将这些数值门槛应用到不同主版本分支。Node.js 公告也将已终止支持的分支视为受影响；未列入表格不能证明安全。

尤其不能只看 `process.versions.brotli`。[已修复的 Node.js 24.22.1 中的 Brotli 版本源码](https://github.com/nodejs/node/blob/v24.22.1/deps/brotli/c/common/version.h)仍声明 `1.2.0`。[发布记录](https://nodejs.org/en/blog/release/v24.22.1)明确列出了择取合入的修复。应建立已修复运行时产物的来源证据，而不是依赖库的版本标签。

## 从进程自身记录证据

![读取示例进程的 PID、可执行文件、Node 版本及 Brotli 标签，然后输出 JSON](/assets/diagrams/technical/zh-CN-2026-10-30-node2shell-brotli-runtime-patching.svg)

图示对应下面示例应用的启动流程。它在同一进程内读取信息并打印 JSON，不比较版本、不发现服务，也不判断补丁状态。新 CLI 调用的输出不能替代已有服务的进程证据。

使用 Node.js 22 或更高版本，将这两个文件保存在新目录中。它们读取 [process 参考文档](https://nodejs.org/docs/latest-v24.x/api/process.html)所述属性，不发送网络请求、不执行解压，也不输出环境变量。

### `runtime-evidence.mjs`

```javascript
export function runtimeEvidence() {
  return {
    scope: 'this-process-only',
    pid: process.pid,
    executable: process.execPath,
    node: process.version,
    brotliLabel: process.versions.brotli ?? null,
    platform: process.platform,
    arch: process.arch,
  };
}
```

### `app.mjs`

```javascript
import {runtimeEvidence} from './runtime-evidence.mjs';

console.log(JSON.stringify(runtimeEvidence(), null, 2));
```

```sh
node app.mjs
```

本地检查使用官方 Node.js 24.22.1 容器，返回的 JSON 中 `node` 为 `v24.22.1`，`brotliLabel` 为 `1.2.0`。PID、路径、操作系统和架构因环境而异。这表明已修复构建也可能保留旧 Brotli 标签，但并没有测试利用过程或生产部署。

真实服务应通过部署流程引入等效的启动日志，并限制这些运维日志的访问。将记录与服务管理器、进程和镜像摘要关联起来。路径和 PID 不应放入公开 HTTP 响应。启动单独的诊断进程不能验证现有工作进程已被替换。

## 安装软件包之后还剩什么？

1. 记录每项服务的 Node.js 可执行文件、供应商、完整软件包版本或镜像摘要、进程、工作进程及副本。仅有主机上的 `node -v` 或 Dockerfile 标签，不能确立运行中容器所用的运行时。
2. 追踪将输入连接到 Brotli 解码器的库。将运行时修复状态与输入暴露分开。在调查范围内未定位到解压路径，并不等于为未修复运行时打了补丁。
3. 通过可信渠道获取兼容的已修复运行时。重新构建并发布容器镜像；同时替换进程管理器和托管平台实际使用的可执行文件。不要假定更新系统 Brotli 库就会替换捆绑副本。
4. 验证每个工作进程及副本新的运行证据，再检查正常 API 调用、外部响应处理、后台任务和错误率。替换安装文件或让旧副本继续运行，都不算已验证采用。

如果打补丁延迟，可考虑在实际数据路径上拒绝或绕过不可信 Brotli 解压。仅从 `Accept-Encoding` 中移除 `br` 并不能阻断所有输入路径。对有效数据成功完成压缩解压往返，或 `npm audit` 未报告问题，同样不能证明此 CVE 已修复。

## 这与 PHP2Shell 是同一个问题吗？

它们是不同的缺陷。PHP2Shell 的两个 CVE 涉及 PHP 引擎请求状态；Node2Shell 涉及 Brotli 解码器。不过，同一 Brotli CVE 也可能出现在其他产品中，因此应遵循各产品公告。[PHP2Shell 响应指南](/en/posts/2026-10-30-php2shell-runtime-patching/)说明了 PHP Windows Brotli 重新构建与 PHP 引擎修复之间的区别。

仅凭崩溃不能证明入侵，缺少痕迹也不能排除入侵。如果怀疑遭到入侵，请在受限位置保留证据，将调查或从可信来源重新构建与打补丁分开进行。
