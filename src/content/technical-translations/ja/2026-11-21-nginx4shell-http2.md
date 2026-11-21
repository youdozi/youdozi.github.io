---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2026-11-21-nginx4shell-http2",
  "routeSlug": "2026-11-21-nginx4shell-http2",
  "kind": "post",
  "title": "Nginx4Shell 対応ガイド — NGINX HTTP/2 の影響範囲と修正バージョンを確認する",
  "description": "NGINX HTTP/2 の脆弱性 CVE-2026-123007 と CVE-2026-123633 の影響条件、修正バージョン、一時的な緩和策を整理し、Python の例でパッチの優先順位を判定する方法を紹介します。",
  "categories": [
    "security"
  ],
  "tags": [
    "nginx",
    "http2",
    "patch-management",
    "cve-2026-123007",
    "cve-2026-123633"
  ],
  "sourcePath": "src/content/posts/en/2026-11-21-nginx4shell-http2.md",
  "sourceSha256": "51daac7a022b582074f762f0ce0c07d617f4af8535152688b060235117af16c2",
  "draftSha256": "6b03bdcda53842c049092eca7194e36d5744b6b9497bfe795c08a9867ac8ac30",
  "manifestPath": ".pipeline/technical-translations/batch-175/manifest.json",
  "manifestSha256": "de1d6420b28e3a41bd670b52f3db93c0a08645e7821632b38b9c35d9f9d8517f",
  "publishedAt": "2026-11-21T00:38:31.366Z",
  "updatedAt": "2026-11-21T00:38:31.366Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 175,
    "approvedAt": "2026-11-21T00:38:31.366Z",
    "basis": "The site owner explicitly asked to publish the Nginx4Shell guide in the supported languages. This records authorization to publish these editions."
  }
}
---

**まず、HTTP/2 を受け付ける NGINX のリスナーを確認してください。** 2026年11月18日に公開された CVE-2026-123007 と CVE-2026-123633 は、HTTP/2 の処理中にメモリ破損を引き起こす可能性があります。条件によってはワーカープロセスが異常終了したり、ワーカーの権限でリモートコードが実行されたりします。NGINX Open Source の修正バージョンは stable **1.30.7**、mainline **1.31.9** です。ディストリビューションのパッケージ、NGINX Plus、Ingress 製品は提供元が公開した修正版を基準に確認してください。 [NGINX セキュリティアドバイザリ](https://nginx.org/en/security_advisories.html) · [F5 の11月18日セキュリティ更新](https://my.f5.com/s/article/K000164058)

## どのような環境が影響を受けますか？

この記事では、検索で使われる別名として **Nginx4Shell** を用います。変更チケットや資産台帳には両方の CVE 番号を別々に記録すると、製品ごとのアドバイザリとパッチ状況を正確に照合できます。

| CVE | 影響を受ける条件と結果 | 影響を受ける NGINX Open Source バージョン |
| --- | --- | --- |
| CVE-2026-123007 | NGINX がクライアントの HTTP/2 通信を処理するときに、メモリ破損が発生する可能性があります。静的コンテンツのみを提供するサーバーも、HTTP/2 が有効なら確認対象です。 | 1.9.5～1.30.6 および 1.31.0～1.31.8 |
| CVE-2026-123633 | クライアントの HTTP/2 リクエストをアップストリームへ転送する構成では、条件によって解放済みのメモリを参照することがあります。HTTP/2 のリバースプロキシを優先して確認してください。 | 1.19.7～1.30.6 および 1.31.0～1.31.8 |

stable の 1.30.7 では両方の脆弱性が修正されています。バージョン番号が 1.30.7 より大きい **1.31.8 も、引き続き影響範囲に含まれます**。今回の更新には HTTP/3、DNS リゾルバー、メールプロキシなどの修正も含まれます。HTTP/2 の設定変更で一時的に緩和する場合も、製品のパッチ適用に向けた準備を続けてください。 [NGINX リリース情報](https://nginx.org/news.html) · [F5 CVE-2026-123007](https://my.f5.com/s/article/K000163926) · [F5 CVE-2026-123633](https://my.f5.com/s/article/K000163928) · [CERT-EU アドバイザリ](https://cert.europa.eu/publications/security-advisories/2026-022)

## 稼働中の製品と HTTP/2 の通信経路を確認する

1. **稼働中のバイナリの提供元を確認します。** VM ではサービスが使う実行ファイルとパッケージを、コンテナでは実際のイメージとそのダイジェストを確認します。対象環境で `nginx -V` を実行すると、バージョンとビルドオプションを確認できます。Ubuntu 24.04 LTS のように、既存バージョンに修正をバックポートするディストリビューションもあります。Ubuntu のアドバイザリでは、このリリースの修正済みパッケージは `1.24.0-2ubuntu7.20` です。 [NGINX のコマンドラインオプション](https://nginx.org/en/docs/switches.html) · [Ubuntu USN-9159-1](https://ubuntu.com/security/notices/USN-9159-1)
2. **クライアントまたは前段のプロキシから NGINX への区間を確認します。** ブラウザーと CDN が HTTP/2 で通信していても、CDN からオリジンの NGINX までは別のプロトコルを使う場合があります。`nginx -T` で稼働中のサービスの設定を確認し、`http` と `server` の各ブロック、読み込まれるファイル、使われている構文を照合します。設定全体には内部アドレスや秘密情報が含まれる場合があるため、確認は許可された環境で行います。 [NGINX HTTP/2 モジュールのドキュメント](https://nginx.org/en/docs/http/ngx_http_v2_module.html)
3. **外部リクエストを受け付ける影響対象のインスタンスから修正します。** デプロイ後、プロセスが新しいバイナリまたはイメージで動いていることを確認します。`nginx -t` で設定を検査し、通常の HTTP リクエスト、アップストリームの状態、エラー率、ワーカーの再起動を確認します。クラスターでは古いイメージで動くレプリカが残っていないかも確認します。 [CERT-EU アドバイザリ](https://cert.europa.eu/publications/security-advisories/2026-022)

すぐに更新できない場合、影響を受けるリスナーで HTTP/2 を無効にすると、両方の CVE に対する露出を抑えられます。現在の構文では `http2 off;` を使い、古い構文では `listen` の `http2` オプションを削除します。変更前に gRPC など HTTP/2 に依存する経路を確認し、変更後は対象リスナーへの実際の接続と通常のサービスリクエストを確認します。 [NGINX HTTP/2 の設定ドキュメント](https://nginx.org/en/docs/http/ngx_http_v2_module.html) · [Red Hat の緩和策ガイド](https://access.redhat.com/security/vulnerabilities/RHSB-2026-019)

## 実習 — 確認結果からパッチの優先順位を決める

この例では運用担当者が確認した**製品の提供元、バージョン、HTTP/2 の状態**を入力します。Python 3.10 以降で動作し、標準ライブラリだけを使います。先ほどの手順で確認した情報をもとに、パッチの優先順位を決められます。

![製品の提供元とバージョンを入力する。ディストリビューションやベンダーの製品は提供元のアドバイザリを確認する。NGINX 公式版が影響範囲に入る場合、HTTP/2 の状態に応じてパッチを優先するか、設定を追加で確認する。](/assets/diagrams/technical/ja-2026-11-21-nginx4shell-http2.svg)

`nginx_http2_triage.py` として保存します。`upstream` は NGINX プロジェクトが配布する Open Source 版に限って指定します。修正がバックポートされたパッケージやベンダーのイメージには `vendor` を指定します。提供元やリスナーの実際の設定を確認できていない場合は、該当する入力に `unknown` を指定します。

```python
import argparse
import re


def upstream_version(value: str) -> tuple[int, int, int]:
    if not re.fullmatch(r"[0-9]{1,4}\.[0-9]{1,4}\.[0-9]{1,4}", value):
        raise argparse.ArgumentTypeError("use an upstream version such as 1.30.7")
    major, minor, patch = map(int, value.split("."))
    return major, minor, patch


def triage(origin: str, value: str, http2: str) -> str:
    if origin != "upstream":
        return "CHECK_VENDOR_ADVISORY"

    version = upstream_version(value)
    if version[0] != 1 or version > (1, 31, 9):
        return "CHECK_CURRENT_ADVISORY"
    if (1, 30, 7) <= version < (1, 31, 0) or version == (1, 31, 9):
        return "UPSTREAM_FIX_VERSION"

    affected = [
        cve
        for cve, first_version in (
            ("CVE-2026-123007", (1, 9, 5)),
            ("CVE-2026-123633", (1, 19, 7)),
        )
        if version >= first_version
    ]
    if not affected:
        return "OUTSIDE_LISTED_RANGES"

    action = {
        "on": "PRIORITIZE_PATCH",
        "off": "PATCH_STILL_REQUIRED",
        "unknown": "VERIFY_HTTP2_AND_PATCH",
    }[http2]
    return f"{action} {' '.join(affected)}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("origin", choices=("upstream", "vendor", "unknown"))
    parser.add_argument("version")
    parser.add_argument("http2", choices=("on", "off", "unknown"))
    args = parser.parse_args()
    try:
        print(triage(args.origin, args.version, args.http2))
    except argparse.ArgumentTypeError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
```

```bash
python3 nginx_http2_triage.py upstream 1.31.8 on
python3 nginx_http2_triage.py upstream 1.30.7 on
python3 nginx_http2_triage.py upstream 1.19.6 unknown
python3 nginx_http2_triage.py vendor 1.24.0-2ubuntu7.20 on
```

上記のコマンドを Python 3.13.0 で実行し、次の出力を確認しました。

```text
PRIORITIZE_PATCH CVE-2026-123007 CVE-2026-123633
UPSTREAM_FIX_VERSION
VERIFY_HTTP2_AND_PATCH CVE-2026-123007
CHECK_VENDOR_ADVISORY
```

出力される CVE の一覧は**バージョンから見て影響を受ける可能性がある項目**です。CVE-2026-123633 のアップストリーム構成に該当するかは、実際のリスナーを確認してください。この例は入力値と公開バージョン範囲を照合するもので、運用サーバーの設定とパッチ適用状況は別途確認が必要です。
