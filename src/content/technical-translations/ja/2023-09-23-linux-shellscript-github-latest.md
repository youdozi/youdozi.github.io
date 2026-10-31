---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2023-09-23-linux-shellscript-github-latest",
  "routeSlug": "2023-09-23-linux-shellscript-github-latest",
  "kind": "post",
  "title": "curl と jq で GitHub の最新リリースからダウンロード資産を一つ選ぶ",
  "description": "OS、CPU、形式を指定し、curl と jq で GitHub のリリース資産を一つ選びます。HTTP エラー、不正な JSON、未一致や複数一致を処理します。",
  "categories": [
    "linux"
  ],
  "tags": [
    "linux",
    "bash",
    "shell script",
    "jq",
    "github latest release"
  ],
  "sourcePath": "src/content/posts/en/2023-09-23-linux-shellscript-github-latest.md",
  "sourceSha256": "921c781aad6d00452ee4730c3ae3ccb6d7af94c4ec4e129e5968b7f1ae596e61",
  "draftSha256": "19657776f943b92a661a5d7156b2f234721f385f598e6d50ee3d12b8bc77bef8",
  "manifestPath": ".pipeline/technical-translations/batch-052/manifest.json",
  "manifestSha256": "3d0fe88e42da93129f62cd5dba401357ffe96d3d01f3038c35211f5afff754c7",
  "publishedAt": "2026-10-31T15:21:36.227Z",
  "updatedAt": "2026-10-31T15:21:36.227Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 125,
    "approvedAt": "2026-10-31T15:21:36.227Z",
    "basis": "User explicitly requested applying all missing technical-post languages, review, verification and deployment on 2026-11-01, with standing PR merge authorization. Human approval denotes publication authorization; linguistic review is performed by AI, not human/native review."
  }
}
---
`curl` で GitHub の最新リリースを取得し、`jq` で必要な OS、CPU、形式に合うダウンロード資産をちょうど一つ選びます。次のスクリプトは HTTP エラー、不正な JSON、未一致や複数一致で停止し、ファイルをダウンロードせずメタデータを返します。

`releases/latest` エンドポイントは、数値的に最大の Git タグを計算するものではありません。[リリース API のドキュメント](https://docs.github.com/en/rest/releases/releases#get-the-latest-release)では、通常のタグ、ドラフト、プレリリース、公開済みリリースが区別されています。

この例は公開リポジトリ `adoptium/temurin17-binaries` から Linux x64 HotSpot JDK tar.gz のメタデータを取得します。トークンも実際のファイルダウンロードも不要です。リポジトリ引数を省略するとこの既定値を使い、空の引数を明示すると拒否します。

## 処理の流れ

![HTTP の失敗では JSON の解析前に停止します。有効なリリースオブジェクトには一致する資産がちょうど一つ必要です。その URL を選んでもダウンロードファイルの検証にはなりません。](/assets/diagrams/technical/ja-2023-09-23-linux-shellscript-github-latest.svg)

HTTP の失敗では JSON の解析前に停止します。有効なリリースオブジェクトには一致する資産がちょうど一つ必要です。その URL を選んでもダウンロードファイルの検証にはなりません。

## HTTP の失敗と JSON の選択失敗を分ける

`curl`、`jq`、POSIX sh が必要です。`latest-release.sh` として保存してください。

### `latest-release.sh`

```sh
#!/bin/sh
set -eu
if [ "$#" -gt 1 ]; then
    printf '%s\n' 'usage: latest-release.sh OWNER/REPO' >&2
    exit 2
fi
repo=${1-adoptium/temurin17-binaries}
case "$repo" in
    */*/*|/*|*/|*[!A-Za-z0-9_./-]*) printf '%s\n' 'usage: latest-release.sh OWNER/REPO' >&2; exit 2 ;;
esac
case "$repo" in
    */*) ;;
    *) printf '%s\n' 'usage: latest-release.sh OWNER/REPO' >&2; exit 2 ;;
esac
api=${GITHUB_API_URL:-https://api.github.com}
response=$(curl --fail --silent --show-error --location --max-time 20 \
    --header 'Accept: application/vnd.github+json' \
    --header 'X-GitHub-Api-Version: 2026-03-10' \
    "$api/repos/$repo/releases/latest") || exit 1
printf '%s' "$response" | jq --slurp --exit-status '
    if length != 1 or (.[0] | type) != "object" then
        error("expected one release object")
    else .[0] end
    | . as $release
    | if (.tag_name | type) != "string" or (.tag_name | length) == 0
         or (.assets | type) != "array" then
        error("missing release tag or assets")
      else . end
    | [.assets[] | select(.name | test("^OpenJDK17U-jdk_x64_linux_hotspot_.*\\.tar\\.gz$"))] as $assets
    | if ($assets | length) != 1 then
        error("expected exactly one Linux x64 JDK tar.gz asset")
      elif ($assets[0].browser_download_url | type) != "string"
           or ($assets[0].browser_download_url | length) == 0 then
        error("missing asset download URL")
      else {tag_name: $release.tag_name, download_url: $assets[0].browser_download_url} end
'
```

```sh
sh latest-release.sh adoptium/temurin17-binaries
```

成功時には `tag_name` と `download_url` を持つ JSON オブジェクトを返します。値はリクエスト時点のリリースによって変わります。次の例は形式を示すテストデータであり、現在の最新リリースを示すものではありません。

```json
{"tag_name":"jdk-17.0.8.1+1","download_url":"https://github.com/adoptium/temurin17-binaries/releases/download/example/OpenJDK17U-jdk_x64_linux_hotspot_example.tar.gz"}
```

`curl --fail` は先に HTTP エラーを処理します。解析前にレスポンスを保存することで、パイプラインの最後のコマンドがネットワークの失敗を隠すことを防ぎます。[curl のオプション](https://curl.se/docs/manpage.html)を参照してください。

`jq --slurp` は入力全体を配列へ読み込みます。JSON 値がちょうど一つという条件は空のレスポンスも拒否します。続いてリリースオブジェクト、タグ、資産配列を確認し、ファイル名がちょうど一つ一致するときだけ結果を出力します。[jq マニュアル](https://jqlang.org/manual/)を参照してください。

## 自動化で扱う結果

| 条件 | 結果 |
| --- | --- |
| 有効なレスポンスと一致する資産が一つ | JSON を出力、ステータス 0。 |
| HTTP403/404 または接続の失敗 | ゼロ以外のステータス。 |
| 空の本文または不正な JSON | ゼロ以外のステータス。 |
| 一致する資産がない、または複数ある | 任意に選ばず失敗する。 |
| リポジトリ引数の構文が不正 | 使い方を表示、ステータス 2。 |

HTTP リクエストが成功しても一致するアセットがない場合は、`jq` フィルターを変更する前にリリースのファイル名を確認してください。この例が選ぶのは Java 17 の Linux x64 向けパッケージであり、すべての JDK パッケージではありません。Java 21 が必要な場合は [Temurin のプラットフォームメタデータの例](/en/posts/2023-10-10-temurin-jdk21-delay/)を使ってください。リポジトリやプラットフォームの値を YAML から取得する場合は、コマンドに渡す前に[設定をデータとして解析・検証](/en/posts/2021-07-27-parse-yaml/)してください。

ローカルの HTTP レスポンスで成功、HTTP エラー、不正な JSON、資産の欠落、重複を確認しています。`GITHUB_API_URL` は既定で公開 API を指し、同じレスポンス契約を実装するテストサーバーにも変更できます。

公開リソースの読み取りに認証は不要です。認証付きリクエストへ拡張する場合は、ソースや Shell のトレースログにトークンを残さないでください。レート制限のレスポンスヘッダーと [GitHub のレート制限ドキュメント](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api)を確認してください。

このスクリプトは URL を選ぶもので、インストールファイルの完全性は検証しません。インストールの自動化には、提供元のチェックサムや署名、および対象プラットフォームの確認が別途必要です。タグを[数値バージョン比較器](/en/posts/2023-11-17-linux-shellscript-version-compare/)へ渡す前に、その入力契約を満たしているか確認してください。

選択したアセットをダウンロードしたら、[ファイルの SHA-256 チェックサムを信頼できる期待値と比較します](/en/posts/2026-10-30-verify-sha256-download/)。検証器はローカルのバイト列を読み取ります。リリースのダウンロードや配布元の認証は行いません。
