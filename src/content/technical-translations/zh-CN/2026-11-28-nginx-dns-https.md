---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2026-11-28-nginx-dns-https",
  "routeSlug": "2026-11-28-nginx-dns-https",
  "kind": "post",
  "title": "让 AI 帮你把 Duck DNS 接到 Nginx：从 DNS 查到 HTTPS",
  "description": "沿着外部请求到应用的路径逐段检查，区分超时与代理错误，再验证证书和续期流程。",
  "categories": [
    "tips"
  ],
  "tags": [
    "self-hosting",
    "nginx",
    "dns",
    "https"
  ],
  "sourcePath": "src/content/posts/en/2026-11-28-nginx-dns-https.md",
  "sourceSha256": "1afd017a347d250d7ed293c1a456355c47fa605f6f677aa12adda112db84165a",
  "draftSha256": "fae147e05cdba269e0377e45f6332d1635d123ec68c1fb6d8caa350e34e7a5cc",
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

假设 Linux 服务器有公网 IPv4 和一个 Duck DNS 域名。面向公众的应用已在 Nginx 所在主机的 `127.0.0.1:8080` 上监听。上一篇的笔记应用用于本地练习，这里使用单独准备的公开应用。

## 向 AI 索取可以逐项核对的方案

**提示词** 我要在具有公网 IPv4 的 Linux 上把 Duck DNS 域名接到 Nginx。同一主机上的应用监听 `127.0.0.1:8080`。用 `example.com` 代替真实域名。请按 DNS A 记录、外部端口访问、反向代理和 HTTPS 的顺序，给出检查命令和预期结果。如果 DNS 正常，怎样区分超时和 `502`？请说明最小配置改动及回退顺序。遇到未知值先提问，不要执行任何操作。

不要把令牌或 SSH 密钥发给 AI。按连接经过的各个环节核对回答。

![解析域名 → 访问 HTTP 端口 → 匹配 Nginx 主机 → 检查应用响应 → 验证 HTTPS 和续期](/assets/diagrams/technical/zh-CN-2026-11-28-nginx-dns-https.svg)

## 检查 DNS 和本地应用

将下文的 `example.com` 换成自己的域名。在 Duck DNS 更新 A，使它指向公网 IPv4。只有确认外网 IPv6 全程可达时才发布 AAAA。本例的 Nginx 监听 IPv4。先用 dig 查询 DNS，再在服务器上运行 curl，检查是否收到应用平常的响应。 [Duck DNS](https://www.duckdns.org/spec.jsp) · [Let’s Encrypt · IPv6](https://letsencrypt.org/docs/ipv6-support/)

```sh
dig +short example.com A
dig +short example.com AAAA
curl --fail --show-error http://127.0.0.1:8080/
```

## 把 HTTP 请求转给应用

备份当前配置。在站点的 http 上下文中加入以下 server 块，并换成实际主机名。用 `nginx -t` 检查，通过后再用系统的服务管理工具重载配置。 [NGINX · proxy_pass](https://nginx.org/en/docs/beginners_guide.html#proxy) · [nginx -t](https://nginx.org/en/docs/switches.html)

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

从另一网络通过 HTTP 访问，应看到相同的应用内容。若 DNS 正确但连接超时，先查线路、路由器端口转发和防火墙。若 Nginx 返回 `502`，先查本地应用响应和上游端口。需要回退时，恢复备份的配置，检查通过后重载。

```sh
curl --fail --show-error http://example.com/
```

## 检查 HTTPS 并测试续期

安装 Certbot 的 Nginx 插件且外网可访问 TCP `80` 端口时，可以用 HTTP-01 验证域名。插件可能安装证书并修改 Nginx，先保存已能工作的 HTTP 配置。在服务器上运行 Certbot，从外网检查 HTTPS，再回到服务器测试续期。 [Let’s Encrypt · HTTP-01 / DNS-01](https://letsencrypt.org/docs/challenge-types/) · [Certbot](https://eff-certbot.readthedocs.io/en/stable/using.html)

```sh
sudo certbot --nginx -d example.com
```

```sh
curl --fail --show-error https://example.com/
```

```sh
sudo certbot renew --dry-run
```

记录外网的 HTTPS 响应、证书中的域名和续期模拟结果。如果 TCP `80` 端口被阻断，可在自己能管理的 DNS 区域使用 DNS-01 验证域名控制权。访客仍需可用的 HTTPS 路径，通常经过 TCP `443` 端口。

流程已与官方文档核对。未更改实际 DNS、防火墙或服务器配置，未运行 Certbot、签发证书或验证线上部署。

[本地笔记应用练习](https://youdozi.github.io/en/posts/2026-11-28-self-hosting-ai-notes/) · [在家自建 Nginx，可以选哪四种免费子域名？](https://youdozi.github.io/en/posts/2026-11-28-nginx-free-subdomains/)
