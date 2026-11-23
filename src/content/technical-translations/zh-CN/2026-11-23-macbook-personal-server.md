---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2026-11-23-macbook-personal-server",
  "routeSlug": "2026-11-23-macbook-personal-server",
  "kind": "post",
  "title": "在私人网络上将 MacBook 用作个人服务器",
  "description": "通过 SSH 隧道测试回环 HTTP 服务，并了解 Mac 的可用性限制。",
  "categories": [
    "tips"
  ],
  "tags": [
    "macos",
    "ssh",
    "home-server"
  ],
  "sourcePath": "src/content/posts/en/2026-11-23-macbook-personal-server.md",
  "sourceSha256": "9d4d027b764ef8bf01ccd259c0d9a651cbb6306532afced8de3af23db443416c",
  "draftSha256": "cdc6da779b23c1462e199b0ed5062ba00a1c8263e25a4581b0e7fa30d87225f4",
  "manifestPath": ".pipeline/technical-translations/batch-188/manifest.json",
  "manifestSha256": "0299e8051adcb92b1b0d8f83c7f973d232b9676d01fd9a79b6552df09c1e8612",
  "publishedAt": "2026-11-23T10:04:19.784Z",
  "updatedAt": "2026-11-23T10:04:19.784Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 188,
    "approvedAt": "2026-11-23T10:04:19.784Z",
    "basis": "Owner explicitly requested publication in eight languages; translations were self-reviewed without independent or native-speaker review."
  }
}
---

MacBook 可以在可信的私人网络上向另一台电脑提供短暂的开发演示，而无需在网络上开放 HTTP 端口。在 Mac 的回环接口上启动临时 HTTP 服务器，再通过 SSH 本地转发访问它。这是测试，并非始终可用的公共服务配置。

![客户端请求经过 SSH 本地转发到达 Mac 回环 HTTP，后者返回测试文件。](/assets/diagrams/technical/zh-CN-2026-11-23-macbook-personal-server.svg)

图中概括了请求和响应；身份验证与清理步骤见下文。

## 准备访问

在自己控制的私人网络上使用两台电脑。共享或公共网络可能包含不可信设备；私有地址本身不能限制访问。不要在路由器上转发端口。为此任务使用单独的 macOS 标准账户，仅授予所需文件的访问权限。在 Mac 上打开“系统设置”→“通用”→“共享”→“远程登录”，启用该功能并选择“仅这些用户”以允许该账户。除非另有需要，不要允许远程用户完全访问磁盘。远程登录面板会显示 Mac 的 SSH 地址。设置可能因 macOS 版本或设备管理而异。[Apple：远程登录](https://support.apple.com/guide/mac-help/allow-a-remote-computer-to-access-your-mac-mchlp1066/mac)

在客户端创建专用密钥，出现提示时选择密码短语。如果文件已存在，请勿覆盖；请选择另一个未使用的路径，并在后续命令中使用该路径：

```sh
ssh-keygen -t ed25519 -f ~/.ssh/macbook_demo
```

通过可信渠道将 `~/.ssh/macbook_demo.pub` 中的单行公钥复制到 Mac。在 Mac 上以允许的账户本地登录，运行以下命令，粘贴公钥行，然后在新的一行按 Ctrl-D。这会将公钥追加到 `~/.ssh/authorized_keys` 并保留现有条目。绝不要复制私钥。

```sh
umask 077
mkdir -p ~/.ssh
chmod 700 ~/.ssh
cat >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

参见 [OpenSSH 授权密钥](https://man.openbsd.org/sshd#AUTHORIZED_KEYS_FILE_FORMAT)和 [ssh-keygen](https://man.openbsd.org/ssh-keygen)。

在 Mac 的本地终端中查看主机密钥指纹：

```sh
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
```

在客户端使用允许的账户和远程登录面板显示的地址连接；下面的 `demo` 和 `192.168.1.20` 是示例，请替换为实际值。首次接受连接前，将显示的 ED25519 指纹与在 Mac 上读取的指纹比较。如果不同，请停止并调查原因。主机密钥变更警告也需要调查，不能自动接受。[OpenSSH 主机验证](https://man.openbsd.org/ssh#VERIFYING_HOST_KEYS)

```sh
ssh -i ~/.ssh/macbook_demo -o HostKeyAlgorithms=ssh-ed25519 demo@192.168.1.20
```

确认登录成功后输入 `exit`。账户密码仍可能有效：添加密钥本身不会关闭密码认证。

## 启动测试并转发

在 Mac 上以允许的账户打开终端，创建空的临时目录，添加一个无害文件，然后启动 Python 3.7+。服务器仅绑定到 Mac 的 IPv4 回环地址。保持该终端打开。

```sh
sample_dir=$(mktemp -d)
printf 'home server test\n' > "$sample_dir/index.html"
python3 -m http.server 8000 --bind 127.0.0.1 --directory "$sample_dir"
```

如果端口 8000 已被占用，请停止操作，在服务器和转发命令中都改用未占用的端口。Python 的简单 HTTP 服务器用于测试，不适合生产；它会跟随符号链接，因此仅使用空的测试目录和无害文件。[Python http.server](https://docs.python.org/3/library/http.server.html)

在客户端的第二个终端中建立隧道并保持打开：

```sh
ssh -N -o ExitOnForwardFailure=yes -i ~/.ssh/macbook_demo -L 127.0.0.1:18000:127.0.0.1:8000 demo@192.168.1.20
```

在客户端的另一个终端中运行：

```sh
curl http://127.0.0.1:18000/
```

预期输出为 `home server test`。客户端连接自己的 18000 端口；SSH 将请求传到 Mac，再连接 Mac 的回环端口 8000。如果隧道失败，请在重试前检查地址、允许名单、指纹和密钥。如果隧道启动但 curl 失败，请检查 Python 进程是否仍在运行以及两端端口是否匹配。`ExitOnForwardFailure` 确认本地监听器已创建，并不确认目标 HTTP 服务器可达。[OpenSSH 转发](https://man.openbsd.org/ssh#L)

在 SSH 隧道终端中按 Ctrl-C 停止隧道。在 Mac 终端中按 Ctrl-C 停止 Python，然后仅删除上面创建的测试目录：

```sh
rm "$sample_dir/index.html"
rmdir "$sample_dir"
```

如果示例公钥和远程登录仅为本次练习添加，请删除该公钥行并关闭远程登录。保留原有密钥和访问设置。

## 可用性与后续选择

显示器关闭和 Mac 睡眠是不同状态。合上笔记本电脑的显示屏通常会使其睡眠；不要假设合盖、网络唤醒或电源设置变更会让测试持续运行。启用 FileVault 的 Mac 重新启动后，应准备在必要时由人手动解锁。Apple 说明了搭载 Apple Silicon 且运行 macOS 26 或更高版本的 Mac 在特定条件下可通过 SSH 解锁 FileVault；不要假设这些条件一定满足。[Apple：睡眠](https://support.apple.com/guide/mac-help/put-your-mac-to-sleep-or-wake-it-mh10330/mac) · [Apple：FileVault](https://support.apple.com/guide/security/managing-filevault-sec8447f5049/web)

一次性演示结束后停止进程。文件访问可以考虑 macOS 文件共享及其访问控制。长期运行的服务需要单独的 launchd 配置、更新、备份和恢复计划；专用硬件可能更合适。在外访问时可以单独评估私人 VPN，但仍需保护 Mac 和服务。

回环 HTTP 响应已使用临时文件和进程在本地检查；SSH 连接和隧道是供读者操作的文档步骤，并未测试到这台 Mac 的连接。
