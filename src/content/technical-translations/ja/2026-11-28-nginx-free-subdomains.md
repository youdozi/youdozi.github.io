---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2026-11-28-nginx-free-subdomains",
  "routeSlug": "2026-11-28-nginx-free-subdomains",
  "kind": "post",
  "title": "自宅の Nginx で使える無料サブドメイン４サービスを比較",
  "description": "自宅の IP が変わる場合、作品を公開する場合、ネームサーバーを自分で管理したい場合で、選ぶサービスは変わります。",
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
  "draftSha256": "a5d3ef5f77ed96efe86cba0b9778f67755b2b6f60a2c693bc2dd09dc0acf21cf",
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

自宅で Nginx が起動したら、訪問者にはどの名前を伝えますか。以下のサービスでは、運営者のドメイン配下に無料のサブドメインを取得できます。サーバーの運用と外部から接続するための設定は利用者が担います。

## 外部からサーバーに接続できるか

DDNS は DNS が返す IP を更新します。通信が Nginx に届くかは回線、ルーター、ファイアウォールによって決まります。通信事業者が CGNAT を使っていると、自宅のルーターでポートを転送するだけでは届かない場合があります。WAN 側のアドレスが `100.64.0.0/10` の範囲なら、グローバル IPv4 アドレスを利用できるか事業者に確認してください。 [RFC 6598](https://www.rfc-editor.org/info/rfc6598/)

## 名前の管理方法で選ぶ

| サービス | アドレスの管理方法 | 向いている用途 |
| --- | --- | --- |
| [Duck DNS](https://www.duckdns.org/spec.jsp) | 更新クライアントで `name.duckdns.org` を管理します。API は IPv4 を自動検出できます。IPv6 の更新にはアドレスを明示します。 | グローバル IPv4 が変わる回線での最初の実習。 |
| [dynv6](https://dynv6.com/) · [API](https://dynv6.com/docs/apis) | ホスト名を取得し、API で A・AAAA レコードと IPv6 プレフィックスを更新できます。 | IPv6 またはデュアルスタック。企業向け SLA はありません。 |
| [is-a.dev](https://github.com/is-a-dev/register#-register) | GitHub でプルリクエストを出し、審査を受けます。運営者は申請文を本人が書くよう求めています。 | 開発者のポートフォリオ。IP が頻繁に変わるなら DDNS が便利です。 |
| [EU.org](https://nic.eu.org/register.html) · [EU.org NS](https://nic.eu.org/top-policy.html) | 申請前に権威ネームサーバーを用意します。承認後に NS の委任を受けると、自分のゾーンで A と AAAA を管理できます。 | DNS レコードを自分で管理したい場合。動的更新の仕組みは別途用意します。 |

## 選んだ名前を確認する

![WAN アドレスを確認 → 更新方式を選択 → DNS レコードを照会 → 外部から接続を確認](/assets/diagrams/technical/ja-2026-11-28-nginx-free-subdomains.svg)

最初の実習ではグローバル IPv4 を使えることを確かめ、そのアドレスを指す Duck DNS 名を一つ設定します。dig を用意し、以下の例の名前を置き換えて両方のレコードを照会してください。A がグローバルアドレスと一致することを確認します。AAAA を公開した場合は別のネットワークから IPv6 でも接続します。

```sh
dig +short name.duckdns.org A
dig +short name.duckdns.org AAAA
```

各社の公式文書に基づく比較です。アカウント登録やアドレスの取得は行っていません。

[ローカルのメモアプリ実習](https://youdozi.github.io/en/posts/2026-11-28-self-hosting-ai-notes/) · [AI と進める Duck DNS と Nginx の接続：DNS から HTTPS まで](https://youdozi.github.io/en/posts/2026-11-28-nginx-dns-https/)
