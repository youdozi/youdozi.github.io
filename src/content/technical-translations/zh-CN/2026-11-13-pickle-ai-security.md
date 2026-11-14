---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2026-11-13-pickle-ai-security",
  "routeSlug": "2026-11-13-pickle-ai-security",
  "kind": "post",
  "title": "Pickle AI 的工作原理：iPhone 应用程序控制和密码保护边界",
  "description": "检查 Pickle AI 是否直接利用其他 iPhone 应用程序，并将单独的浏览器和 API 路径与 Credential Enclave、OAuth 令牌和 Vault 密码保护进行比较。",
  "categories": [
    "security"
  ],
  "tags": [
    "pickle-ai",
    "ai-agent",
    "ios",
    "credentials",
    "nitro-enclaves"
  ],
  "sourcePath": "src/content/posts/en/2026-11-13-pickle-ai-security.md",
  "sourceSha256": "4973bca9ea9b81ec4e068b4f530a2b82742c427074c36836639b0c2db1a811e2",
  "draftSha256": "df4da1581a9d32edc87349d60e7ebdbc257b26c667ebab066d1b9f14f7748b52",
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

**Pickle AI 的官方解释指向单独的浏览器和连接的帐户进行工作，而不是直接操作 iPhone 上的其他应用程序屏幕。** 密码与模型分开加密，但实际用于登录的值的保护边界在 OAuth 和网站密码之间有所不同。

本文分析 Pickle, Inc. 的个人 AI 代理 [Pickle](https://pickle.com/)。依据是 2026 年 11 月 13 日访问的官方帮助页面，以及公开 `credential-enclave` 源码的 **commit `cff16a343bf5bb7953e5b65df6ab3600107e127d`**。我运行了公开安全程序的发布验证；这并非对已安装的 iOS 应用或整个生产服务器的审计。

## 它真的会点击其他iPhone应用程序吗？

[已保存的登录帮助页面](https://www.pickle.com/help/connect/save-login) 表示 Pickle 的浏览器与手机分离，无法直接使用手机上存储的登录信息。 [任务委托指南](https://www.pickle.com/help/tasks/delegate)还描述了在真实浏览器中操作网站以及在应用程序关闭后继续工作。

因此，仅完成订单或预订并不能证明已安装的购物应用程序的屏幕已被点击。公共材料支持的路径是：

| 路径 | 证据和意义 |
| --- | --- |
| 单独的浏览器 | 独立于手机应用程序屏幕登录网站并填写表格 |
| 关联账户 API | 公共 `forward` 代码将凭据附加到允许的提供商 API 请求 |
| 打电话 | 官方任务指南描述了代表用户打电话处理无法通过网页完成的事情 |

苹果对[第三方应用沙箱](https://support.apple.com/en-gb/guide/security/sec15bfe098e/web)的说明还指出，访问其他信息需要通过 iOS 提供的服务。仅此一点并不能排除所有自动化，但我没有发现任何证据表明 Pickle 绕过沙箱来控制其他应用程序。

可用材料并未确定 Pickle 的浏览器使用哪些 DOM 工具或屏幕识别模型，或者为每个任务选择哪个执行路径。本文所述的运行方式，是结合官方说明和公开凭证处理路径作出的分析。

## 不给AI密码怎么能登录呢？

即使模型从不直接输出密码字符串，单独的执行器也可以接收必要的值并将其放入登录表单中。 Pickle 的[隐私解释](https://www.pickle.com/privacy) 表示，密码和卡值在设备上进行了加密，并且从模型接收的结果中隐藏。这种解释的技术边界需要与公共代码进行比较。

![在设置过程中，iPhone 会创建密钥并将加密的用户密钥委托给经过验证的 Enclave。在使用过程中，它会检查活动委托和加密记录，确认日志持久性，然后分成两条路径。 OAuth 令牌用于节点内部的 API 调用；Vault 密码和卡值以明文形式通过 release 响应离开节点，交给 worker 用于网页表单。后面的结果屏蔽是一个单独的边界。](/assets/diagrams/technical/zh-CN-2026-11-13-pickle-ai-security.svg)

该图的顶部显示了设置，其中预先委派了一个密钥；下半部分显示委托仍然有效时的凭证使用情况。这并不意味着手机必须在每次登录时发送新密钥。该图也没有重现任务执行器的每个实现细节。

### 设备密钥和加密记录

[公共协议](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/docs/protocol.md#3-keys) 指定在设备上创建的主密钥保存在 iCloud 钥匙串中，并具有用于签名、日志解密和凭据的单独派生密钥。存储的记录使用 ChaCha20-Poly1305 进行加密，帐户和记录类型等上下文也与身份验证绑定。

设备验证节点的证明和公钥，然后加密并将**派生的用户密钥**委托给该节点。远程认证检查公钥属于哪个测量执行环境。 [AWS Nitro Enclaves](https://docs.aws.amazon.com/enclaves/latest/user/) 将内存与父服务器隔离，并且不提供直接的外部网络或持久存储。 Pickle 节点使用主机中继的通信；该事实并未授予主机解密权限。

委托的用户密钥在节点内存中使用一段有限的时间。 [公共架构描述](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/README.md#structure) 指定最大授权为 30 天。设备钥匙串和服务器的 Nitro Enclave 是不同的保护层。

### OAuth 令牌在节点内部使用

[API 转发代码](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/enclave/src/api/forward.rs) 检查活动委托，打开 OAuth 记录并准备允许的提供者请求。它在确认使用记录已保存后执行请求。此路径发出经过身份验证的请求，而不是将令牌交给模型。

但是，**隐藏令牌和隐藏使用该令牌读取的数据是不同的事情**。 [出口策略](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/docs/egress-policy.md) 单独涵盖返回提供商对操作环境的响应。如果授予阅读电子邮件的权限，则模型可以处理电子邮件内容；必须与令牌保护分开评估。

### 网站密码发布后跨越不同边界

[Vault 代码](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/enclave/src/vault.rs) 定义为出口响应选择密码、卡值和 TOTP 代码的类型。 [实际发布处理程序](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/enclave/src/api/release.rs) 在确认使用记录已保存后序列化并返回值。 **此时密码和卡值以明文形式离开节点，供执行任务的 worker 使用。** 对于 TOTP，离开节点的是计算出的一次性代码，而不是种子。

公共代码的 `origin` 检查仅验证 HTTPS 源的格式。注释指出，调用者负责确定该地址是否与保存的登录站点匹配。因此，仅靠 Enclave 代码无法建立站点限制或模型结果屏蔽。

这并不是实际泄漏的证据。但是，**从模型输入中隐藏值**、**加密存储**和**工作内存中的明文使用**是不同的安全属性。 “人工智能没有收到密码”的说法不得扩大为“解密后的密码永远不会离开保护区”。

## 使用记录能保证什么？

[官方使用历史指南](https://pickle.com/help/privacy/activity) 表示首先保存记录，如果保存失败，则不会使用凭据。公共API代码还显示在确认日志持久性之后发生的使用或释放​​。加密记录、签名和链接旨在使更改或遗漏可被检测到。

记录并不能保证用户确实想要执行该任务或该任务在外部站点上成功。例如，记录保存后，实际请求可能会失败。先审批再确认金额是[官方服务说明](https://pickle.com/en)中的执行策略，不是凭证加密自动遵循的属性。

如果 TOTP 种子也被委托，代理可以生成代码。这是[已保存登录指南](https://www.pickle.com/help/connect/save-login) 中的一项便利功能，但它不同于用户为每个任务单独批准第二个身份验证因素。与仅委托密码时相比，应更广泛地判断委托范围。

## 验证公开安全程序的证明

[安全程序文档](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/secure-program/README.md)还发布了设备端安全程序，并提供了验证发布签名和透明日志证明的工具。下面的示例检查**公共文件是否与其发布证明匹配**。它不连接到生产节点或使用真实密码。

![公开程序JS和发布证明作为官方验证者的输入。它检查文件哈希、签名和透明度日志证明。原来的v42返回退出代码0；添加一个字节的文件返回 source_hash 错误并退出代码 1。生产服务器与已安装应用的验证是另一项工作。](/assets/diagrams/technical/zh-CN-2026-11-13-pickle-ai-security-architecture.svg)

需要 Git、curl、Rustup 和本机构建工具，并且使用网络下载源代码和 Rust 依赖项。验证器是根据下面在 **macOS arm64 上使用 Rust 1.100.0** 的固定提交构建的。存储库引脚工具版本1.98.1；这里 `+1.100.0` 显式选择执行版本。

### `verify-example.sh`

```bash
# macOS·Linux 셸, Git·curl·Rustup 및 네이티브 빌드 도구가 필요합니다.
# 새 작업 폴더에서 실행합니다. 아래 검증은 계정 로그인이나 실제 비밀번호를 사용하지 않습니다.
git clone https://github.com/pickle-com/credential-enclave.git
cd credential-enclave
git checkout cff16a343bf5bb7953e5b65df6ab3600107e127d
rustup toolchain install 1.100.0 --profile minimal
cargo +1.100.0 build --locked -p credential-enclave-verify
curl --fail --location \
  https://github.com/pickle-com/credential-enclave/releases/download/secure-program-v42/secure-program.release.json \
  --output secure-program.release.json
./target/debug/credential-enclave-verify program \
  --source secure-program/secure-program.js \
  --release secure-program.release.json
```

原始文件返回退出代码 0 和以下输出：

```text
program release secure-program-v42: version 42, sha256 31e7fa7fb51f87781313b1f97b60ae3c7b69ff8f2fbcee7de12b7a0ed034d8e8, log index 3761959022: ok
```

还要检查更改的文件是否被拒绝。在同一存储库目录中运行以下命令。

### `tamper-example.sh`

```bash
cp secure-program/secure-program.js changed-program.js
printf '\n' >> changed-program.js
./target/debug/credential-enclave-verify program \
  --source changed-program.js \
  --release secure-program.release.json
echo $?
```

添加了一个换行符字节的文件因 `source_hash` 不匹配而被拒绝，并以代码 1 退出。这个结果涉及到公共程序的发布证明。我没有检查实际应用程序显示的版本和哈希是否匹配，也没有使用远程证明来验证生产 Enclave 的测量。

## 判断安全时仍然存在的条件

[公共存储库的限制](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/README.md#what-it-does-not-guarantee) 描述了信任假设，例如应用程序诚实性、提供商 API 合同、发布密钥和日志。即使使用公共安全程序，整个 iOS 应用程序二进制文件是否在不更改它的情况下执行该程序也是一个单独的问题。节点将委托转移到更高版本的能力也不意味着特定版本的保护是永久固定的。

设备端安全程序的[更新限制](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/secure-program/README.md#limits) 也很重要。该文档称，如果操作员签署新代码、在公共日志中注册并满足加载要求，则无需事先等待即可加载新代码。 **发布验证确认与已发布的签名文件匹配；它不保证代码是无害的。** 对操作员的信任仍然存在于以后的代码中。这并不是对实际发生的恶意发布的声明或观察。

| 要检查什么 | 做出决定所需的问题 |
| --- | --- |
| 关联账户 | 允许哪些读/写范围，以及可以在提供者处撤销它们吗？ |
| Vault 和 TOTP | 是否有必要委托生成一次性代码和密码？ |
| 付款和预订 | 能否在执行前检查一下条件和金额并验证结果？ |
| 安全程序和节点 | 应用程序版本和哈希、公开发布和实际节点证明是否对应？ |
| 对话和关联帐户数据 | 即使凭证被隐藏，模型也会处理哪些内容？ |

Pickle 安全设计的关键是**将哪些密钥委托给谁，以及在哪个边界解密和使用每个值**。公共代码提供了检查这些边界的证据。用户的出发点是区分实际的 iPhone 应用程序控制与委派帐户访问，仅连接必要的权限，并检查使用历史记录和任务结果。
