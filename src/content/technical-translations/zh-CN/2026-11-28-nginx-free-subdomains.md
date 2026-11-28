---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2026-11-28-nginx-free-subdomains",
  "routeSlug": "2026-11-28-nginx-free-subdomains",
  "kind": "post",
  "title": "在家自建 Nginx，可以选哪四种免费子域名？",
  "description": "家庭 IP 经常变化、展示开发作品、自己管理域名服务器，这三种需求适合不同的地址服务。",
  "categories": [
    "tips"
  ],
  "tags": [
    "self-hosting",
    "nginx",
    "dns"
  ],
  "sourcePath": "src/content/posts/en/2026-11-28-nginx-free-subdomains.md",
  "sourceSha256": "d11db302c4d9595bd30ea32d7d5c2c2ec680a9c318001ba16e333085dbec5f2e",
  "draftSha256": "405a0be4531b9deffd72be57ae9773e2d2a8a0c7a3a7d36cb07950cca7fe96d6",
  "manifestPath": ".pipeline/technical-translations/batch-1571/manifest.json",
  "manifestSha256": "bf6a83d6c439631d9c3af30e329fc60c4018ee5580ce2cd06ccd9111caf54227",
  "publishedAt": "2026-11-28T04:45:08.727Z",
  "updatedAt": "2026-11-28T04:45:08.727Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 229,
    "approvedAt": "2026-11-28T04:45:08.727Z",
    "basis": "Explicit item 157 publication approval for both item 155 and 156 follow-up guides in all nine site languages."
  }
}
---

在家里启动 Nginx 后，该让访客输入什么名字？下面四项服务都在运营方的域名下提供免费子域名。服务器和外部访问仍由你负责。

## 外网能访问服务器吗？

DDNS 更新的是 DNS 返回的 IP。请求能否到达 Nginx，取决于线路、路由器和防火墙。如果运营商使用 CGNAT，仅在家用路由器上转发端口可能还不够。如果 WAN 地址在 `100.64.0.0/10` 范围内，请向运营商确认能否获得公网 IPv4。 [RFC 6598](https://www.rfc-editor.org/info/rfc6598/)

## 按地址的维护方式选择

| 服务 | 如何管理地址 | 适用场景 |
| --- | --- | --- |
| [Duck DNS](https://www.duckdns.org/spec.jsp) | 用更新客户端维护 `name.duckdns.org`。API 可以自动检测 IPv4，更新 IPv6 时需明确提供地址。 | 公网 IPv4 经常变化的入门练习。 |
| [dynv6](https://dynv6.com/) · [API](https://dynv6.com/docs/apis) | 提供主机名，可通过 API 更新 A、AAAA 记录和 IPv6 前缀。 | IPv6 或双栈网络。没有企业级 SLA。 |
| [is-a.dev](https://github.com/is-a-dev/register#-register) | 提交 GitHub 拉取请求，由维护者审核。维护者要求申请人自己撰写申请。 | 开发者作品集。如果 IP 经常变化，DDNS 更方便。 |
| [EU.org](https://nic.eu.org/register.html) · [EU.org NS](https://nic.eu.org/top-policy.html) | 先准备权威域名服务器，再提交申请。获批并完成 NS 委派后，可在自己的区域管理 A 和 AAAA。 | 适合自行管理 DNS 记录。动态更新需另行安排。 |

## 检查选定的域名

![查看 WAN 地址 → 选择更新方式 → 查询 DNS 记录 → 从外网测试](/assets/diagrams/technical/zh-CN-2026-11-28-nginx-free-subdomains.svg)

第一次练习时，先确认有公网 IPv4，再把一个 Duck DNS 域名指向它。安装 dig 后，将以下示例域名替换为自己的域名，查询两种地址。A 应与公网地址一致。如果发布了 AAAA，还应从外网测试 IPv6 连接。

```sh
dig +short name.duckdns.org A
dig +short name.duckdns.org AAAA
```

本文依据服务商的官方文档进行比较。未注册账号，也未申请地址。

[本地笔记应用练习](https://youdozi.github.io/en/posts/2026-11-28-self-hosting-ai-notes/) · [让 AI 帮你把 Duck DNS 接到 Nginx：从 DNS 查到 HTTPS](https://youdozi.github.io/en/posts/2026-11-28-nginx-dns-https/)
