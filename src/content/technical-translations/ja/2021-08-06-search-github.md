---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2021-08-06-search-github",
  "routeSlug": "2021-08-06-search-github",
  "kind": "post",
  "title": "GitHub・Sourcegraph・ローカル Git でコードを検索する",
  "description": "リポジトリ・言語・パスで検索を絞り、GitHub と Sourcegraph の構文を区別します。ローカル Git の固定文字列検索も再現します。",
  "categories": [
    "util"
  ],
  "tags": [
    "git",
    "github",
    "sourcegraph",
    "search"
  ],
  "sourcePath": "src/content/posts/en/2021-08-06-search-github.md",
  "sourceSha256": "22da61f44f3002516631540293a6b08b9b0de12d2c7963e6c52ae57b297efddf",
  "draftSha256": "e28045106722baff09ea9f3d974732b4e5b4740305f600ec7e36e6f2c058cd9e",
  "manifestPath": ".pipeline/technical-translations/batch-056/manifest.json",
  "manifestSha256": "5c3bd2ee5ccb0b59bad65322a026d7b2ef52cfac963e0236a497f74510717e42",
  "publishedAt": "2026-10-31T15:21:36.846Z",
  "updatedAt": "2026-10-31T15:21:36.846Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 125,
    "approvedAt": "2026-10-31T15:21:36.846Z",
    "basis": "User explicitly requested applying all missing technical-post languages, review, verification and deployment on 2026-11-01, with standing PR merge authorization. Human approval denotes publication authorization; linguistic review is performed by AI, not human/native review."
  }
}
---
コード検索は、リポジトリとファイルの範囲を固定してから、見つかった実装を文脈の中で読みます。シンボル名の一致は手掛かりであり、依存バージョンや意図する動作に合う証拠ではありません。

GitHub コード検索、Sourcegraph、ローカルのチェックアウトは、検索可能なデータが異なります。必要なリポジトリへアクセスできるツールを選び、公開インスタンスがすべてのリポジトリやリビジョンを索引化しているとは考えないでください。

## 処理の流れ

![結果を増やす前にクエリの範囲を絞ります。版が重要なら、既定ブランチに頼らず、対象リビジョンを開くか、そのチェックアウトを検索します。](/assets/diagrams/technical/ja-2021-08-06-search-github.svg)

結果を増やす前にクエリの範囲を絞ります。版が重要なら、既定ブランチに頼らず、対象リビジョンを開くか、そのチェックアウトを検索します。

## 各サービス固有のクエリ言語を使う

[GitHub コード検索クエリ](https://docs.github.com/en/search-github/github-code-search/understanding-github-code-search-syntax)では、次の修飾子と引用符付きのフレーズを組み合わせられます。

```text
repo:spring-projects/spring-framework language:java path:WebClient.java "interface WebClient"
```

対応する [Sourcegraph フィルター](https://sourcegraph.com/docs/code-search/queries)はリポジトリとファイルの正規表現を使います。

```text
repo:^github\.com/spring-projects/spring-framework$ lang:java file:WebClient\.java$ "interface WebClient"
```

| 目的 | GitHub コード検索 | Sourcegraph |
| --- | --- | --- |
| リポジトリ | `repo:owner/name` | `repo:` の正規表現。厳密な一致にはアンカーを使う |
| Java | `language:java` | `lang:java` または `language:java` |
| ファイル範囲 | `path:` のパスフィルター | `file:` の正規表現 |
| 完全一致フレーズ | 引用符付きフレーズ | キーワードモードの引用符付きフレーズ |

これはクエリの組み立て例であり、実際の検索件数を測定したものではありません。二つのパスフィルターが同じ集合を返すとは限りません。Sourcegraph の例はファイル名の末尾をアンカーで固定しています。アクセス権、索引化された内容、選択したリビジョンも結果を左右します。

## 空のディレクトリでローカル検索を再現する

この小さなモックには Git と POSIX シェルが必要です。`demo-search` が既にあると `mkdir` は意図的に失敗するので、新しい作業ディレクトリを選びます。

```sh
set -eu
mkdir demo-search
cd demo-search
git init -q
mkdir src docs
printf '%s\n' 'interface WebClient {}' > src/WebClient.java
printf '%s\n' 'interface WebClient is discussed here' > docs/notes.txt
git add src docs
git grep -n -F 'interface WebClient' -- src
```

出力：

```text
src/WebClient.java:1:interface WebClient {}
```

同じフレーズは `docs/notes.txt` にもありますが、`-- src` が検索を制限します。[`git grep -F`](https://git-scm.com/docs/git-grep) はパターンを固定文字列として扱い、`-n` は行番号を表示します。既定の作業ツリー検索は追跡ファイルを使うため、先にファイルをインデックスへ追加しています。この例はコミットを作りません。実際のチェックアウトでは、意図する範囲を保ったままパスとパターンを置き換えます。

結果を利用する前に、呼び出し元、テスト、ライセンス、リビジョンを読んでください。同じ宣言でも別の版では動作が異なることがあります。検索の一致から推測せず、[WebClient 応答テスト](/en/posts/2023-09-19-springboot-test-webclient/)でクライアントの契約を確認してください。
