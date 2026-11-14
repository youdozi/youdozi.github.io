---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2026-11-12-t3-code-workflow",
  "routeSlug": "2026-11-12-t3-code-workflow",
  "kind": "post",
  "title": "T3 Code ガイド: 小さなコード変更から差分とテスト検証まで",
  "description": "AI コーディング タスクを開始するには、T3 Code v0.1.9 を使用します。実行可能ノードの例、制限されたアクセス許可、差分、テストを使用し、参照ソリューションと AI 出力を区別します。",
  "categories": [
    "util"
  ],
  "tags": [
    "t3-code",
    "ai-agent",
    "coding-agent",
    "testing",
    "javascript"
  ],
  "sourcePath": "src/content/posts/en/2026-11-12-t3-code-workflow.md",
  "sourceSha256": "da83ebd4864d4a4b015af522789e363b4a8695b6424368db9bfd1652f7761089",
  "draftSha256": "32cf0518100f0b1673de5a15d243ed6fa5571481906304932dbc1d9c2c624698",
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

**T3 Codeは、コンピュータにインストールされているコーディング エージェントをプロジェクト、会話、アクセス許可、および変更されたファイルのインターフェイスに接続します。** コードをエージェントに委任する場合は、長いリクエストよりも小さな範囲と検証可能な完了基準が重要です。このガイドでは、リクエストから diff およびテスト検証を通じて数値 `Retry-After` パーサーの修正に従います。

主題は [公式 T3 Code プロジェクト](https://github.com/pingdotgg/t3code/tree/v0.1.9) です。これは、`create-t3-app` を使用して Web アプリを作成する T3 スタックとは別のものです。公式 README には、Codex、Claude Code、Cursor などの既存のプロバイダーの接続について説明されています。 T3 Codeのインストールと、プロバイダーのログインとサブスクリプション/API 条件の準備は別の手順です。

基準は [v0.1.9 リリース](https://github.com/pingdotgg/t3code/releases/tag/v0.1.9)で、2026 年 11 月 12 日に確認しました。例は macOS 上の Node.js 24.13.0 と Git で確認し、T3 Code CLI のヘルプとローカルサーバーの起動も確認しました。**AI タスクはプロバイダーに送信していません。** 以下の参考解法は直接テストした実装であり、T3 Code の生成出力やモデルの性能測定ではありません。

## T3 Codeとプロバイダーはどのように責任を分担しますか?

T3 Codeには、作業中のプロジェクトとスレッド、プロバイダーの選択、権限の要求と変更が表示されます。接続されたエージェントは、ファイルの読み取りと変更、またはコマンドの実行を行います。ツール呼び出しが表示されても、テストが自動的に実行されて合格したことを意味するわけではありません。コマンドと返された結果を検査してください。

[インストール ガイド](https://github.com/pingdotgg/t3code/blob/v0.1.9/docs/user/install.md) に従って、使用するプロバイダーをインストールし、**T3 Code サーバーを実行しているコンピューター**に認証を完了します。この演習は、すでに準備されているプロバイダーを選択することから始まります。ログインの詳細や API キーをプロンプトに貼り付ける必要はありません。

## 小規模な Git プロジェクトと失敗するテストの準備

![スターター コードと固定されたテストを Git プロジェクトに保存し、失敗を確認します。 T3 Codeで、プロジェクト、プロバイダー、および監視されたアクセス許可を選択し、制限付き変更リクエストを送信します。エージェントのファイル変更とコマンドを承認し、差分、元のテストと結果を比較し、契約が満たされている場合はコミットし、満たされていない場合は修正を要求します。](/assets/diagrams/technical/ja-2026-11-12-t3-code-workflow.svg)

これら 三 つのファイルを新しい `t3-code-example` フォルダーに保存します。これらのノード テストは、外部パッケージや API 呼び出しを使用しません。 二 つの `Retry-After` 形式のうち、この演習では **`delay-seconds`、整数秒** のみをサポートします。 HTTP-date はスコープ外であるため、`null` を返す必要があります。ヘッダーの完全な文法については、[RFC 9110 の Retry-After の定義](https://www.rfc-editor.org/rfc/rfc9110.html#name-retry-after) を参照してください。

### `package.json`

```json
{
  "name": "t3-code-retry-after-example",
  "private": true,
  "type": "module",
  "engines": { "node": ">=24" },
  "scripts": { "test": "node --test retry-after.test.mjs" }
}
```

### `retry-after.mjs`

```javascript
export function retryAfterMs(header) {
  const seconds = Number.parseInt(header, 10);
  return Number.isFinite(seconds) ? seconds * 1000 : null;
}
```

### `retry-after.test.mjs`

```javascript
import test from 'node:test';
import assert from 'node:assert/strict';
import { retryAfterMs } from './retry-after.mjs';

const cases = [
  ['2', 2000],
  ['0', 0],
  [' 2 ', 2000],
  ['0002', 2000],
  ['', null],
  ['   ', null],
  [undefined, null],
  [null, null],
  [2, null],
  ['0x10', null],
  ['2x', null],
  ['-1', null],
  ['1.5', null],
  ['1e3', null],
  ['Infinity', null],
  ['Wed, 21 Oct 2015 07:28:00 GMT', null],
  ['9007199254740', 9007199254740000],
  ['9007199254741', null],
  ['9007199254740991', null],
];
for (const [input, expected] of cases) {
  test(`retryAfterMs(${JSON.stringify(input)})`, () => {
    assert.equal(retryAfterMs(input), expected);
  });
}
```

Git 作成者構成がすでに準備されているプロジェクト フォルダー内でこれらのコマンドを実行します。

```sh
git init -b main
git add package.json retry-after.mjs retry-after.test.mjs
git commit -m "Add Retry-After exercise"
npm test
```

初期コードは **11 件のテストが成功し、8 件が失敗**することを確認しました。合計は 19 件です。`parseInt('2x', 10)` のように数字で始まる一部の文字列を受け入れ、負数、小数、安全範囲外の値を正しく処理しません。失敗するテストが演習の出発点です。

## プロジェクトを開いて変更範囲を指定します

プロジェクト フォルダーから次のコマンドを実行して、バージョンを固定します。 `--host` はローカル接続へのアクセスを制限し、`--auto-bootstrap-project-from-cwd` は現在のフォルダーをプロジェクトとして追加します。 npm パッケージと実行可能ファイルは、最初の使用時にダウンロードできます。

```sh
npm exec --yes --package=t3@0.1.9 -- t3 \
  --host 127.0.0.1 --auto-bootstrap-project-from-cwd .
```

CLI はローカル サーバーと Web アプリを起動します。すでに T3 Code サーバーを使用している場合は、その環境でプロジェクトを開きます。デスクトップのインストールとリモート アクセスは、[このバージョンのインストール ガイド](https://github.com/pingdotgg/t3code/blob/v0.1.9/docs/user/install.md) の別のパスに従います。このガイドでは、バックグラウンド サービスを構成したり、それを外部ネットワークに公開したりすることはありません。

プロジェクト フォルダーとスレッドを選択し、インストールされ認証されているプロバイダーを選択します。 [スレッド ガイド](https://github.com/pingdotgg/t3code/blob/v0.1.9/docs/user/thread-sidebar.md) によると、**New worktree（新しいワークツリー）** は別のブランチと作業ディレクトリを作成します。基本的な演習では、準備されたフォルダーの既存の作業ディレクトリを前提としています。新しいワークツリーを選択した場合は、そのフォルダー内で後続の Git および npm コマンドも実行します。まず、スレッドの作業パスとブランチを確認します。メッセージ入力領域で、権限が **Supervised（監視付き）** であることを確認します。 [v0.1.9 権限ガイド](https://github.com/pingdotgg/t3code/blob/v0.1.9/docs/user/permission-modes.md) によると、初期デフォルトは Full access（フルアクセス）であり、Supervised はコマンドとファイル変更の承認を要求します。どの読み取りが許可されるかなどの詳細はプロバイダーによって異なります。

次のプロンプトを送信します。

```text
まず、retry-after.mjs と retry-after.test.mjs を読み取ります。
この規約を満たすように retryAfterMs(header) を修正します。

- 周囲の空白を削除し、ASCII 数字で構成される負でない整数の秒のみを受け入れます。
- ミリ秒を返します。秒とミリ秒の両方が Number.isSafeInteger を満たす必要があります。
- 空または文字列以外の値、負の値、小数、指数表記、末尾の文字、および安全範囲外の値の場合は、null を返します。
- HTTP-date はこの範囲外であるため、null を返す必要があります。
- retry-after.mjs のみを変更します。テストまたは package.json は変更しないでください。
- 依存関係のインストール、ネットワーク要求の実行、PR のコミット、プッシュ、または作成は行わないでください。

npm test で確認し、変更の理由、実際に実行されたコマンドとその結果を報告します。
コマンドを実行できなかった場合は、明示的に述べてください。
```

ファイルの変更やコマンドの承認を求められたら、目的のファイルや `npm test` など、この演習に必要なものであることを確認してください。プロンプト内のスコープの指示は、ツールの権限設定を置き換えません。この例では、エージェントはコミットを求められません。変更内容と検証結果を受け取ってから決定します。

## 「修正が完了した」ことをどのように確認しますか?

[T3 Code変更レビュー ガイド](https://github.com/pingdotgg/t3code/blob/v0.1.9/docs/user/source-control.md) では、変更ファイルとターンごとの差分を、ブランチ間の比較と区別しています。ターンの差分にはそのターンの作業が表示されるため、マージする前にベース ブランチと比較してください。会話内のテスト ツール呼び出しを展開して、実際のコマンド、出力、ステータスを検査します。ターミナルで再実行することもできます。

```sh
git rev-parse --show-toplevel
git diff --name-only
git diff -- retry-after.mjs
git diff --exit-code -- retry-after.test.mjs package.json
npm test
```

`retry-after.mjs` のみを変更する必要があります。 三 番目のコマンドが変更を出力するか失敗する場合は、まずテストまたは構成が変更された理由を判断します。テストの期待値を下げることによって得られた合格結果は、この契約を満たす修正ではありません。新しいファイルがないか、`git status --short` も確認してください。

エージェントがテストを実行できなかったと報告した場合、それをパスとして扱わないでください。自分で `npm test` を実行します。失敗が残る場合は、フォローアップ要求で入力、期待値、実際の結果を絞り込みます。例: 「`0` は 0ms であり、`'2x'` は null である必要があります。テストを保存して、これら 二 つのケースを再度確認してください。」

以下は、**直接検証されたリファレンス実装**です。演習後にエージェントが提案した変更と比較してください。実行するには、このコードをプロジェクト ルートの `retry-after.mjs` に配置します。

### `reference/retry-after.mjs`

```javascript
export function retryAfterMs(header) {
  if (typeof header !== 'string') return null;
  const value = header.trim();
  if (!/^[0-9]+$/.test(value)) return null;
  const seconds = Number(value);
  const milliseconds = seconds * 1000;
  return Number.isSafeInteger(seconds) && Number.isSafeInteger(milliseconds)
    ? milliseconds
    : null;
}
```

スターターをリファレンス実装に置き換えた後、同じテストのすべての 19 が合格し、元のテスト ファイルは変更されませんでした。安全な整数範囲の確認は、実際の再試行遅延の上限の設定とは別のものです。この関数は待機エグゼキューターでも完全な HTTP-date パーサーでもありません。実際のクライアントの再試行回数と合計時間予算を個別に設定します。

diff とテストを確認した後に自分で作業を記録するには、変更されたファイルのみをコミットします。

```sh
git add retry-after.mjs
git commit -m "Validate numeric Retry-After values"
```

完了したら、T3 Codeを実行している端末で `Ctrl+C` を使用してフォアグラウンド サーバーを停止します。

## 起動できない場合は何を確認すればよいですか?

| 症状 | 最初のチェック |
| --- | --- |
| プロバイダーが見つからないか、実行されません | サーバー コンピューター上のインストールと PATH、および [設定] のプロバイダー設定を確認してください。 |
| 認証エラー | サーバーのコンピューターで選択したプロバイダーのアカウントとログイン状態を確認します |
| 変更は元のフォルダーに反映されません | スレッドが別のワークツリーを使用しているかどうか、および同じパスを表示しているかどうかを確認します。 |
| 差分機能または分岐機能は使用できません | 開いているフォルダーが Git リポジトリであり、プロジェクト パスが正しいことを確認してください |
| テストは合格したが、変更は範囲を超える | テスト、構成、追加ファイルなどの差分と Git ステータスを確認します。 |

公式の README では、これはバグを含む可能性のある初期のプロジェクトであると説明されています。アプリまたはプロバイダーの CLI を更新した後、このように小さな契約と検証手順を保持しておくと、同じプロンプトから固定された答えが得られることを期待するよりも結果を比較しやすくなります。
