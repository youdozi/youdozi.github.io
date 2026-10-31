---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2026-04-07-jekyll-quality-gates-proof-html-bundler-audit",
  "routeSlug": "2026-04-07-jekyll-quality-gates-proof-html-bundler-audit",
  "kind": "post",
  "title": "Astro 品質ゲート：PR が成功しても配備されない理由",
  "description": "Astro の検証と GitHub Pages 公開を分ける。24 のモデルケースと6つの失敗変異でコミット参照、成功した依存ジョブ、配備条件を確認する。",
  "categories": [
    "blog",
    "automation"
  ],
  "tags": [
    "astro",
    "github-actions",
    "github-pages",
    "quality-gates",
    "testing"
  ],
  "sourcePath": "src/content/posts/en/2026-04-07-jekyll-quality-gates-proof-html-bundler-audit.md",
  "sourceSha256": "f5c09678ab191654be64bc9fd457df828066c7f199625a6b32c5d94a02200363",
  "draftSha256": "3278ec8bd6293a8379e19d215a9c501aaca1a1051e1e7f0bb5987046cce7760b",
  "manifestPath": ".pipeline/technical-translations/batch-125/manifest.json",
  "manifestSha256": "1934910c02dbe893b786124f1d296d7adf9efbe921d40b3d2cfbceb8f70b4b33",
  "publishedAt": "2026-10-31T15:35:43.034Z",
  "updatedAt": "2026-10-31T15:35:43.034Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 125,
    "approvedAt": "2026-10-31T15:35:43.034Z",
    "basis": "User explicitly requested applying all missing technical-post languages, review, verification and deployment on 2026-11-01, with standing PR merge authorization. Human approval denotes publication authorization; linguistic review is performed by AI, not human/native review."
  }
}
---

PR ビルドの成功は、設定された検査が通った意味です。このサイトはそれだけで候補を公開しません。本番配備には `main` 参照、許可したイベント、依存ビルドの成功も必要です。

以前の Jekyll は `proof-html` と `bundler-audit` を使っていました。現行 Astro は `site-checks.yml` で検証し、`site-quality-gates.yml` で Pages を配備します。Ruby の検査は旧ツール向けで、サイト構築用の npm 依存は監査しません。

## 検証と配備を分ける

![候補を確認し main のイベント条件を適用して検査済み成果物を配備する](/assets/diagrams/technical/ja-2026-04-07-jekyll-quality-gates-proof-html-bundler-audit.svg)

[サイト処理](https://github.com/youdozi/youdozi.github.io/blob/main/.github/workflows/site-quality-gates.yml)は共通検証へ `${{ github.sha }}` を渡します。[再利用ワークフロー](https://github.com/youdozi/youdozi.github.io/blob/main/.github/workflows/site-checks.yml)は入力参照を checkout し、ビルドジョブと contents 読取権限を持ち、呼出側が有効化しない限り Pages 成果物の設定は false です。GitHub の [`workflow_call` 文書](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows)がこのインターフェースを説明します。

設定した検査は異なる失敗を対象とします。

| 検査 | 確認できる内容 |
| --- | --- |
| Python と Node テスト | テスト対象の収集、言語、公開、描画の契約 |
| 記事から抽出した例 | 記録された環境上の選んだ実行ケース |
| `npm run check` | 内容規則と Astro 型、スキーマ検査 |
| `npm run build` | 静的出力、内部リンク、画像、アンカー、移行範囲 |

内部リンク検査は外部 URL の利用可否を証明しません。例が通っても全本番動作を保証せず、形式が正しい記事にも根拠のない主張はあり得ます。現行処理は一般的な npm 脆弱性監査も行いません。

## 選んだ配備契約を再現する

Node 24 で checkout 内から `npm ci` を実行します。完全なファイルをルートの `deploy-contract.mjs` に保存して実行します。

```sh
node deploy-contract.mjs
```

実際の YAML 値を確認してから、固定の配備条件を 24 通りでモデル化します。意図的に変えた六つのワークフローオブジェクトは契約検査に失敗する必要があります。配備や通信の操作はありません。

### `deploy-contract.mjs`

```javascript
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import YAML from 'yaml';

const read = file => YAML.parse(readFileSync(`.github/workflows/${file}`, 'utf8'));
const site = read('site-quality-gates.yml');
const checks = read('site-checks.yml');
const condition = "github.ref == 'refs/heads/main' && (github.event_name == 'push' || github.event_name == 'workflow_dispatch')";
function verify(site, checks) {
    assert.equal(site.jobs.deploy.if, condition);
    assert.equal(site.jobs.deploy.needs, 'build');
    assert.equal(site.jobs.build.with.ref, '${{ github.sha }}');
    assert.equal(site.jobs.build.with.pages_artifact, '${{ ' + condition + ' }}');
    assert.deepEqual(Object.keys(checks.jobs), ['build']);
    assert.deepEqual(checks.permissions, { contents: 'read' });
    assert.equal(checks.on.workflow_call.inputs.pages_artifact.default, false);
    assert.equal(checks.jobs.build.steps[0].with.ref, '${{ inputs.ref }}');
    assert.ok(site.jobs.deploy.steps.some(step => step.uses === 'actions/deploy-pages@v4'));
}
verify(site, checks);

// A model of this fixed condition and successful dependency, not the Actions engine.
function allowed(ref, event, build) {
    return build === 'success' && ref === 'refs/heads/main' &&
        (event === 'push' || event === 'workflow_dispatch');
}
const expected = new Set([
    'refs/heads/main|push|success',
    'refs/heads/main|workflow_dispatch|success',
]);
let cases = 0;
for (const ref of ['refs/heads/main', 'refs/heads/develop', 'refs/heads/content/example', 'refs/pull/42/merge']) {
    for (const event of ['push', 'workflow_dispatch', 'pull_request']) {
        for (const build of ['success', 'failure']) {
            assert.equal(allowed(ref, event, build), expected.has(`${ref}|${event}|${build}`));
            cases++;
        }
    }
}

const mutations = [
    (site, checks) => { site.jobs.deploy.if = "github.event_name == 'pull_request'"; },
    (site, checks) => { site.jobs.deploy.needs = []; },
    (site, checks) => { site.jobs.build.with.ref = 'main'; },
    (site, checks) => { checks.permissions.pages = 'write'; },
    (site, checks) => { checks.on.workflow_call.inputs.pages_artifact.default = true; },
    (site, checks) => { checks.jobs.build.steps[0].with.ref = 'main'; },
];
for (const mutate of mutations) {
    const badSite = structuredClone(site), badChecks = structuredClone(checks);
    mutate(badSite, badChecks);
    assert.throws(() => verify(badSite, badChecks), assert.AssertionError);
}
console.log(`${cases} policy-model combinations and ${mutations.length} rejected workflow mutations passed.`);
```

確認した出力は次のとおりです。

```text
24 policy-model combinations and 6 rejected workflow mutations passed.
```

モデルで許可されるのは `main` 上の `push` または `workflow_dispatch` でのビルド成功だけです。手動実行の機能分岐も含め他は拒否します。`pull_request` は通常 PR のマージ参照を使うため、成功しても配備条件を通りません。[ジョブ条件](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-jobs-with-conditions)と[依存ジョブの成功要件](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-jobs)は GitHub 文書を参照します。

参照とイベント条件、および依存ビルド成功のモデルであり、Actions 式の解釈器ではありません。成功、失敗を試し、取消、スキップされた祖先、runner 割当、権限、成果物の由来、Pages 配備は模擬しません。YAML の断言は方針変更を明示的に失敗させ、古いモデルで新設定を黙って検査せずレビューを求めます。

## 公開結果を確認する

承認してマージしたら main のコミット、ビルド結果、配備ジョブを調べます。成功 PR の `deploy: skipped` は想定どおりで、ビルド成功だけでは公開の証拠になりません。Pages は [Astro Pages 配備パターン](https://docs.astro.build/en/guides/deploy/github/)に沿って検査済み成果物を使います。

公開記事と言語リンクを開き、canonical URL、情報源の日付、サイトマップを確認します。IndexNow は配備後の失敗許容ステップなので Pages 成功でも失敗し得ます。通知受付やサイトマップ掲載は検索の登録、表示の証明ではありません。

[候補ワークフローの記事](/en/posts/2026-04-07-jekyll-github-actions-content-pipeline/)が前段の Draft PR レビューを説明します。技術検査と公開判断は別の責任として保ち、どちらも主張の確認の代わりにはしません。
