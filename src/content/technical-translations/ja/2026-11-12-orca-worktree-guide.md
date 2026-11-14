---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2026-11-12-orca-worktree-guide",
  "routeSlug": "2026-11-12-orca-worktree-guide",
  "kind": "post",
  "title": "Orca の使用: エージェント、テスト、レビューのためのワークツリー ワークフロー",
  "description": "Orca プロジェクトとワークツリーを使用して、コーディング タスクを分離し、テストとブラウザ出力を検証し、コミットする前に差分を確認します。",
  "categories": [
    "util"
  ],
  "tags": [
    "orca",
    "ai-agent",
    "git-worktree",
    "testing",
    "developer-tools"
  ],
  "sourcePath": "src/content/posts/en/2026-11-12-orca-worktree-guide.md",
  "sourceSha256": "4214532491f859b28104e614442c9bc3c33ecc9a00a62567a96d927bc90cffb6",
  "draftSha256": "70e7fffbd568b0ce768e59e53cadbb08f70dc31718334cb60e7fb79d3dcfd459",
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

**Orca は、Git ワークスペース、コーディング エージェント、ターミナル、ブラウザー、および変更レビューを一緒に操作するための開発環境です。** 一 つのタスクを 一 つのワークツリーに配置すると、別々のブランチやフォルダーでさまざまな変更に取り組むことができます。エージェントの回答だけではなく、実際の作業パス、テスト出力、およびベース ブランチとの差分を使用して完了を確認します。

お題はStably AIの[Orca公式アプリ](https://www.onorca.dev/)です。このガイドでは、macOS にインストールされた **Orca 1.4.256**、バンドルされた CLI ガイド、Node.js 24.13.0、Python 3、および Git を使用します。現在のワークスペースの検査、Orca ターミナルでのサンプル テストの実行、ポートの検出と組み込みブラウザでの表示がチェックされました。ワークツリーの作成またはマージ、または新しい AI エージェント タスクの開始は実行されませんでした。以下のプロンプトと作成コマンドは読者のための演習です。

## プロジェクトとワークツリーはどう違うのでしょうか?

[公式初回セッション ガイド](https://www.onorca.dev/docs/first-session) の **リポジトリの追加** を使用して、ローカル Git リポジトリを開きます。 Orca がプロジェクトを管理している場合でも、ソース ファイルとコミットは Git リポジトリに残ります。モデル・プロバイダーの利用規約と認証を別途準備します。

| 要素 | この演習での役割 |
| --- | --- |
| プロジェクト | サンプルの Git リポジトリとワークスペースをグループ化します。 |
| ワークツリー | 特定のブランチにチェックアウトされた作業フォルダーとその作業ビュー |
| エージェント | ファイルの読み取りと変更、および要求されたスコープ内でのコマンドの実行を提案します。 |
| ターミナル | タスクフォルダー内のテストと開発サーバーを実行します |
| 組み込みブラウザ | 実際の開発サーバーのページと境界値を確認します |

[Orca ワークツリー ドキュメント](https://www.onorca.dev/docs/model/worktrees) および [CLI ガイド](https://www.onorca.dev/docs/cli/overview) では、ファイル、ブランチ、作業ビューの関係について説明しています。 UI で別のワークツリーを選択すると、すでに開いているシェルの現在のディレクトリが自動的に変更されるとは想定しないでください。 **コマンドを実行するターミナルでパスとブランチを確認する**ことが最初のステップです。

## 小さなサンプルを作成して開始状態を確認する

![サンプルの Git リポジトリを開き、ワークツリーを作成し、そのパスとブランチを確認します。エージェントに 一 つのファイルを変更してから、そのワークツリー内のテスト、開発サーバー、およびブラウザをチェックするように依頼します。 差分と元のテストを main と比較します。要件が満たされている場合はコミットするか、要件が満たされていない場合は修正をリクエストしてください。](/assets/diagrams/technical/ja-2026-11-12-orca-worktree-guide.svg)

例示的な配送料金ポリシーを使用します。 **注文金額が 50,000 ウォン以上なら送料無料、未満なら送料 3,000 ウォン**で、非負の安全な整数のみを受け入れます。これは実際のサービスのポリシーではありません。次の 四 つのファイルを新しい `orca-shipping-example` フォルダーに保存します。外部の npm パッケージは必要ありません。

### `package.json`

```json
{
  "name": "orca-shipping-example",
  "private": true,
  "type": "module",
  "engines": { "node": ">=24" },
  "scripts": { "test": "node --test shipping.test.mjs" }
}
```

### `shipping.mjs`

```javascript
export function shippingFee(orderTotal) {
  return orderTotal > 50_000 ? 0 : 3000;
}
```

### `shipping.test.mjs`

```javascript
import test from 'node:test';
import assert from 'node:assert/strict';
import { shippingFee } from './shipping.mjs';

for (const [total, expected] of [[0, 3000], [49_999, 3000], [50_000, 0], [50_001, 0]]) {
  test(`shippingFee(${total}) = ${expected}`, () => {
    assert.equal(shippingFee(total), expected);
  });
}
for (const [label, total] of [
  ['negative', -1],
  ['fraction', 50_000.5],
  ['string', '50000'],
  ['NaN', Number.NaN],
  ['Infinity', Number.POSITIVE_INFINITY],
  ['unsafe integer', Number.MAX_SAFE_INTEGER + 1],
]) {
  test(`rejects ${label}`, () => {
    assert.throws(() => shippingFee(total), RangeError);
  });
}
```

### `index.html`

```html
<!doctype html>
<html lang="ko">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Orca 배송비 예제</title>
<h1>배송비 경계값 확인</h1>
<pre id="result"></pre>
<script type="module">
  import { shippingFee } from './shipping.mjs';
  const totals = [49_999, 50_000, 50_001];
  document.querySelector('#result').textContent = totals
    .map(total => `${total}원 → 배송비 ${shippingFee(total)}원`)
    .join('\n');
</script>
</html>
```

Git 作成者設定がすでに準備されているサンプル フォルダーで次のコマンドを実行します。

```sh
git init -b main
git add package.json shipping.mjs shipping.test.mjs index.html
git commit -m "Add shipping exercise"
npm test
```

初期コードは `50,000` の境界を誤って処理し、無効な入力も拒否しません。実行により、3 件が成功し 7 件が失敗（合計 10 件）したことを確認しました。この状態を基準コミットとして記録すると、後でテストや設定の変更も比較できます。

## ワークツリー内のエージェントに変更をリクエストする

Orca の **Add Repo** を使用してサンプル リポジトリを開き、そのリポジトリに接続されているターミナルで CLI を確認します。 CLI が利用できない場合は、[公式 CLI ガイド](https://www.onorca.dev/docs/cli/overview) の説明に従って、[設定] → [一般] → [Orca CLI] を介してインストールします。これらのコマンドは、macOS `orca` 実行可能ファイルを前提としています。

```sh
orca skills get orca-cli
orca worktree current --json
```

作業を分割する場合は、現在のプロジェクトの `main` から新しいワークツリーを作成します。

```sh
orca worktree create --name shipping-fee-fix \
  --parent-worktree active --base-branch main \
  --setup skip --activate --json
```

`--parent-worktree active` は Orca の仕事関係を記録します。 `--base-branch main` は Git の開始点を設定します。これらは異なる設定です。この例では、インストールする外部依存関係がないため、セットアップをスキップします。実際のプロジェクトでは、適切なセットアップ ポリシーに従ってください。このコマンドには `--agent` がないため、エージェント タスクは要求されません。

新しいワークスペースでターミナルを開いて確認します。元のコマンドを実行したシェルと、新しいワークツリー内のシェルを区別します。

```sh
git rev-parse --show-toplevel
git branch --show-current
orca worktree current --json
```

ブランチ名は、Orca プレフィックス設定やその他の構成によって異なる場合があります。 JSON 内のワークツリー、Git パスおよびブランチが目的のワークスペースであることを確認した後、準備されたエージェント タブを開き、次のプロンプトを送信します。利用可能なエージェントとチャット/CLI の実行は環境の構成によって異なります。

```text
まず現在の作業ディレクトリとブランチを確認し、shipping.mjs と shipping.test.mjs を読んでください。
次の契約を満たすように、例の送料ポリシーを修正してください。

- 注文金額が 50,000 ウォン以上なら送料は 0、未満なら 3,000 ウォンです。
- 注文合計には非負の安全な整数のみを受け入れ、それ以外は RangeError を送出します。
- 変更するのは shipping.mjs のみです。テスト、package.json、index.html は変更しないでください。
- 依存関係のインストール、外部ネットワークへの接続、コミット、プッシュ、PR 作成はしないでください。

npm test の実際の結果と変更理由を報告してください。
実行できなかった検査があれば明記してください。
```

Orca グループが連携して動作する場合でも、実際のツールの権限はエージェントと実行環境によって異なります。プロンプトの制約だけではアクセス境界を強制できません。このガイドでは、特定の許可ボタンの名前や、すべてのプロバイダーでの同一の動作は想定していません。

## 同じワークスペースでテストとブラウザを確認する

[組み込み端末](https://www.onorca.dev/docs/terminal)で `npm test` を実行します。自動化のために、現在のワークツリーにテスト端末を作成できます。

```sh
orca terminal create --title "tests" --command "npm test" --json
```

オートメーションでは、返された端末ハンドルを後のコマンドのターゲットとして使用します。 `terminal read --screen` は現在の画面を読み取ります。プレーン `terminal read` は蓄積された出力を読み取ります。受け入れられた入力と、コマンドまたはエージェント タスクの実際の開始は別のイベントです。このガイドでは、**すべての 10 テストが合格**し、この目的のために作成されたテスト端末の出力で `shipping.mjs` のみが変更されたことを検証しました。これは、リファレンス実装を直接挿入することによって確認されました。 AI タスクの実行の記録ではありません。

ブラウザを確認するには、同じワークツリー内のターミナルでサーバーを起動します。これは、ポート 4877 が使用可能であることを前提としています。

```sh
python3 -m http.server 4877 --bind 127.0.0.1
```

別の端末でポートを確認してください。

```sh
orca ports --json
orca tab create --url http://127.0.0.1:4877/ --json
```

サーバーが別のポートを使用する場合は、リストのポートとそれに対応する URL を使用します。 `orca ports` によって表示されるすべてが HTTP Web ページであるわけではありません。 [埋め込みブラウザ ガイド](https://www.onorca.dev/docs/browser/overview) に従って接続し、サンプル ページで次の値を確認します。

```text
49999원 → 배송비 3000원
50000원 → 배송비 0원
50001원 → 배송비 0원
```

上の 三 行は、リファレンス ソリューションの例を使用して、実際の Orca ブラウザーで確認されました。確認後、ターミナルで `Ctrl+C` を使用してサーバーを停止します。タスクが終了したからといって、無関係な端末を一括で閉じないでください。タスクのプロセスとタブを区別します。

## 差分を確認し、変更されたファイルのみを記録します

[Orca diff viewer](https://www.onorca.dev/docs/review/diff-viewer)でベース参照と変更されたファイルを確認してください。 [変更されたコメント](https://www.onorca.dev/docs/review/annotate-ai-diff) により、エージェントに場所を示すことができます。例: 「50,000 ウォンも無料であるはずです。テストの期待値を維持し、比較演算子を確認してください。」

ターミナル内のベース `main` とも比較してください。

```sh
git status --short
git diff main --name-only
git diff main -- shipping.mjs
git diff --exit-code main -- shipping.test.mjs package.json index.html
npm test
```

このタスクでは、`shipping.mjs` のみを変更する必要があります。テスト、構成、またはページが変更された場合は、まずその理由を特定します。通常の差分では新規ファイルを省略できるので、Git のステータスも確認してください。エージェントが自分で実行できなかったチェックを実行します。 「完了」という回答を合格結果として扱わないでください。

以下は、直接検証された参照ソリューションです。演習後にエージェントが提案したコードと比較します。実行するには、このコードをプロジェクト ルートの `shipping.mjs` に置きます。

### `reference/shipping.mjs`

```javascript
export function shippingFee(orderTotal) {
  if (!Number.isSafeInteger(orderTotal) || orderTotal < 0) {
    throw new RangeError('orderTotal must be a nonnegative safe integer');
  }
  return orderTotal >= 50_000 ? 0 : 3000;
}
```

リファレンス ソリューションでは、同じテストのすべての 10 が合格し、元のテスト、構成、および HTML が保存されました。条件を確認したら、必要なファイルのみをタスクブランチにコミットします。

```sh
git add shipping.mjs
git commit -m "Fix free-shipping boundary and input validation"
```

コミットとベース ブランチへのマージは別のステップです。別のタスクが `main` を変更する場合は、マージする前に差分を確認して再度テストします。ワークツリーはソース ワークスペースを分離しますが、セキュリティ サンドボックスではありません。異なるワークツリーでも、データベース、ポート、アカウント、シークレットなどの実行リソースを共有できます。

最初は、このフローを 一 つのタスクで実践すると、すぐに複数のエージェントを追加するよりも問題を見つけやすくなります。ファイルまたは機能の境界と完了条件が明確な場合は、並列作業に拡張します。
