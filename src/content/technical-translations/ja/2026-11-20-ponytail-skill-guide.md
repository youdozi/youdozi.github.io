---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2026-11-20-ponytail-skill-guide",
  "routeSlug": "2026-11-20-ponytail-skill-guide",
  "kind": "post",
  "title": "Ponytail スキルの使い方 — Codex で小さな修正と回帰テストを完了する",
  "description": "Codex と Claude Code での Ponytail の呼び出し方と Lite・Full・Ultra の違いを紹介する。Codex CLI で既存の関数を再利用し、Node.js の回帰テストを実行する。",
  "categories": [
    "ai"
  ],
  "tags": [
    "ponytail",
    "codex",
    "claude-code",
    "agent-skills",
    "refactoring",
    "nodejs"
  ],
  "sourcePath": "src/content/posts/en/2026-11-20-ponytail-skill-guide.md",
  "sourceSha256": "51597fdb68c31cae936e748ddf6719dce0d443cd28dabfb4a97b1ff62f991cf5",
  "draftSha256": "a35cb0209c1fe23801bea45b323479479c410dc715a033b6b26edf67bc5b952a",
  "manifestPath": ".pipeline/technical-translations/batch-172/manifest.json",
  "manifestSha256": "91fb61de3a3d1c432b5f074da43348e5ad1ab92b61742481f1cd4ac05bc2994e",
  "publishedAt": "2026-11-20T14:37:06.595Z",
  "updatedAt": "2026-11-20T14:37:06.595Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 172,
    "approvedAt": "2026-11-20T14:37:06.595Z",
    "basis": "User requested seven new language editions for each of four already published guides and approved parallel AI translation and verification. This records publication authorization."
  }
}
---

**Ponytail は、AI コーディングエージェントが既存コードを再利用しながら、依頼された動作を実装するためのスキルだ。** 例えば在庫が一件のとき `1 items` と表示されたら、まずプロジェクトに単数・複数を扱う関数がないかを調べる。その関数を再利用して表示を直し、在庫数が 0 と 2 の場合も従来どおり動くかテストする。

## Codex と Claude Code で使い始める

Codex に単体版の Ponytail スキルをインストール済みなら、チャットの入力欄に `$ponytail-help` と入力してスキル名とモードを確認する。`$ponytail full` に続けて、変える動作、維持する条件、検証コマンドを書く。以下の実習では、ユーザーのパス `~/.agents/skills/ponytail/SKILL.md` に登録した単体版を使った。この構成でモードは現在の会話での作業方針となり、`$ponytail off` で解除できる。 [Codex のスキルドキュメント](https://learn.chatgpt.com/docs/build-skills)

Ponytail プロジェクトはプラグインも配布している。Codex CLI では、シェルで次のコマンドを実行する。その後 Codex を開き、`/hooks` で二つのフックの実行内容を確認する。フックを使用するには、内容を確認して信頼する設定にした後、新しい会話を始める。フックの実行環境では `PATH` に `node` が必要だ。 [Ponytail のインストール手順](https://github.com/DietrichGebert/ponytail/blob/main/INSTALL.md#codex)

```bash
codex plugin marketplace add DietrichGebert/ponytail
codex plugin add ponytail@ponytail
```

Claude Code では、入力欄から次のコマンドを一行ずつ実行し、`/ponytail full` でモードを選ぶ。付属のレビューコマンドは `/ponytail-review` だ。Codex のプラグインでは、レビュー用スキルは `$ponytail:ponytail-review` のようにプラグイン名を含めて表示される。両プラグインの導入手順とフックの動作は公開ドキュメントに基づく。 [Claude Code のインストール手順](https://github.com/DietrichGebert/ponytail/blob/main/INSTALL.md#claude-code) · [Ponytail のコマンド一覧](https://github.com/DietrichGebert/ponytail#commands)

```text
/plugin marketplace add DietrichGebert/ponytail
/plugin install ponytail@ponytail
```

## Lite・Full・Ultra の使い分け

Codex の単体版スキルでは、`$ponytail` だけを入力すると既定の Full が適用される。

| 呼び出し方 | 作業方針 | 例 |
| --- | --- | --- |
| `$ponytail lite` | 依頼を完了し、より小さい変更に実質的な利点があれば短く伝える。 | 合意済みの UI 文言を変更する。 |
| `$ponytail full` | 呼び出し元と既存テストを確認し、必要な動作を最小限の変更で実現する。検証結果と残るリスクを報告する。 | 単数表記の不具合を直して既存の入力も確認する。 |
| `$ponytail ultra` | 依頼された作業を進めながら、不要に広がった変更範囲を指摘する。 | 特定の画面の不具合を修正し、共通 UI 全体の見直しが必要かは別に判断する。 |

変更を小さく保つには、依頼に**変える動作、維持する動作、検証方法**を書く。権限チェック、入力検証、データ保護など、呼び出し元が依存している動作も維持条件に含める。スキルはエージェントの作業方針に影響する。ファイルの書き込み範囲や実行できるコマンドは、エージェントの権限設定で決まる。

## 実習 — 在庫が一件なら `1 item` と表示する

Node.js 22.17.0 と Codex CLI 0.169.0 を使い、空の実習用リポジトリで実行した。以下の完成コードにある `stockLabel` の return 行を ``return `${count} items`;`` に置き換えると初期状態を再現できる。
`stock.test.mjs` の最初のテストは初めからあり、二番目は今回追加した。

> $ponytail full\
> stockLabel(1) が 1 items を返す問題を修正してください。\
> 0 と 2 では items を維持してください。既存の formatCount を再利用し、\
> stockLabel の回帰テストを追加したら node --test を実行してください。\
> この実習用リポジトリの外は変更せず、コミットもしないでください。

![在庫表示の修正依頼を受けて stockLabel と formatCount を確認する。formatCount を再利用し、0、1、2 件の表示を回帰テストで検証して結果を記録する。](/assets/diagrams/technical/ja-2026-11-20-ponytail-skill-guide.svg)

`stock.mjs` の変更は `stockLabel` の return 式一行だけだった。単数・複数をすでに処理している `formatCount` をそのまま呼び出す。

```javascript
export function formatCount(count, noun) {
  return `${count} ${count === 1 ? noun : noun + 's'}`;
}

export function stockLabel(count) {
  return formatCount(count, 'item');
}
```

`stock.test.mjs` で、在庫数が 0、1、2 の表示をそれぞれ確認する。二つのファイルを同じディレクトリに置き、`node --test` を実行する。

```javascript
import assert from 'node:assert/strict';
import test from 'node:test';
import { formatCount, stockLabel } from './stock.mjs';

test('formatCount handles singular and plural', () => {
  assert.equal(formatCount(1, 'item'), '1 item');
  assert.equal(formatCount(2, 'item'), '2 items');
});

test('stockLabel handles zero, one, and two items', () => {
  assert.equal(stockLabel(0), '0 items');
  assert.equal(stockLabel(1), '1 item');
  assert.equal(stockLabel(2), '2 items');
});
```

追加したテストを修正前のコードで実行すると、在庫数が 1 の場合に失敗した。期待値は `1 item`、実際の値は `1 items` だった。修正後は次の結果になった。

```text
ok 1 - formatCount handles singular and plural
ok 2 - stockLabel handles zero, one, and two items
# tests 2
# pass 2
# fail 0
```

この実習で確認した範囲は二つのテストと二つのファイルの変更だ。エージェントから完了報告を受け取ったら、実際の `git diff` とテスト結果を照合する。既存関数が再利用され、依頼の範囲が守られているかを自分で確認できる。

## 修正が終わったらレビュー範囲を指定する

付属の単体版スキルもインストールされていれば、次のコマンドを使える。どのコードをレビューするか明示しておくと、指摘を確認しやすい。 [Ponytail のコマンド一覧](https://github.com/DietrichGebert/ponytail#commands)

| 呼び出し方 | 使う場面 |
| --- | --- |
| `$ponytail-review` | 現在の差分と関連コードをレビューする。PR を開く前に呼び出し元や回帰テストの漏れを確認するときに使う。 |
| `$ponytail-audit` | リポジトリ全体を読み取り専用で調べ、見つけた問題を優先順位順に整理する。 |
| `$ponytail-debt` | 既存の `shortcut:` コメントと、以前の `ponytail:` コメントを集めて確認する。 |
| `$ponytail-gain` | プロジェクトが公開したベンチマークを確認する。自分のリポジトリで節約できた時間や費用の測定には別途比較が必要だ。 |
| `$ponytail-help` | インストールしたスキルのモードと呼び出し方を確認する。 |
