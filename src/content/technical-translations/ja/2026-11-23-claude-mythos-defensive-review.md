---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2026-11-23-claude-mythos-defensive-review",
  "routeSlug": "2026-11-23-claude-mythos-defensive-review",
  "kind": "post",
  "title": "Claude Mythosの使い方：Claude Securityの検出結果を修正とテストにつなぐ",
  "description": "Claude Securityの根拠を確認し、サーバーの認可修正と許可・拒否テストにつなげます。",
  "categories": [
    "util"
  ],
  "tags": [
    "claude",
    "security",
    "ai-agent",
    "testing"
  ],
  "sourcePath": "src/content/posts/en/2026-11-23-claude-mythos-defensive-review.md",
  "sourceSha256": "f2681dfbb0c7b7d09b2e0d0b566305cdaec11b271949b3a7aa2785e56013639e",
  "draftSha256": "0c16a411b497ed624599dd4d6be3847bc1501d75fa6cadc74c88784235ddf898",
  "manifestPath": ".pipeline/technical-translations/batch-187/manifest.json",
  "manifestSha256": "52d3a89003bce4814e49b6ba310085f584df29a5e7c8ae582c4bda8f74269d44",
  "publishedAt": "2026-11-23T09:51:04.563Z",
  "updatedAt": "2026-11-23T09:51:04.563Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 187,
    "approvedAt": "2026-11-23T09:51:04.563Z",
    "basis": "Owner explicitly requested publication of the defensive review guide in all eight supported languages; translations were self-reviewed without independent or native-speaker review."
  }
}
---

**Claude Securityの検出結果を受け取ったら、まず検査対象のコミットと根拠ファイルを確認します。** 次にアプリケーションが守るべき規則を書き出し、許可と拒否の両方をテストします。この記事では「同じ店舗の返金担当者だけが返金を要求できる」という架空のコマース規則を使います。

Anthropicによると、Claude EnterpriseのClaude SecurityはMythos 5.2を含むモデルでリポジトリを検査します。この記事は権限のあるリポジトリで防御的な検出結果を一件確認し、修正する例です。アカウントでの利用条件は[Mythosの利用条件](../2026-11-22-claude-mythos-availability/)を参照してください。[Anthropicのモデル発表](https://www.anthropic.com/claude-fable-and-mythos-5-2) · [Claude Securityヘルプ](https://support.claude.com/en/articles/14661296-use-claude-security)

![検出結果のコミットと根拠を確認します。根拠が足りなければ判断を保留し、規則と欠落を確認できたら修正、許可・拒否のテスト、記録を行います。](/assets/diagrams/technical/ja-2026-11-23-claude-mythos-defensive-review.svg)

## 修正の根拠を選ぶ

Claude Securityの検出結果には深刻度、ファイルと行の位置、根拠のブランチとコミット、修正案が含まれます。まず引用されたファイルを**同じコミット**で開きます。現在のブランチが変わっている場合は、同じ規則が現在の版でも欠けているか別途確認します。[Claude Securityの検出結果](https://support.claude.com/en/articles/14661296-use-claude-security)

| 確認内容 | この例での問い |
| --- | --- |
| 検査した版と位置 | どのコミットの返金要求サービスと権限検査に関する報告か？ |
| 実際の業務規則 | 同じ店舗でも閲覧専用の担当者は返金を要求できないか？ |
| 既存検査の範囲 | ボタンの表示とは別に、サーバーの返金要求経路で役割と店舗を確認するか？ |
| 判断に必要な根拠 | 共通の認可規則を確認できない場合、どのファイルや設定が必要か？ |

例えば報告に「返金要求の権限を確認」とあれば、まずその経路に共通の権限検査が適用済みか確認します。共通規則を読めない場合は必要な資料を検出結果に記録します。欠落を確認できた場合は、サーバーの権限検査と関連テストを修正対象にします。[コマース管理画面の権限設計](../2026-11-23-commerce-admin-screen/)

## 修正ツールに業務規則と完了条件を渡す

Claude Securityの **Fix** からClaude Codeで修正を続けられます。Claude Code in the cloudを利用できない場合は、提示されたプロンプトを自分のClaude Codeにコピーします。セッションではアカウントで利用可能なモデルが使われます。次の架空の依頼は、レビュアーがファイルと規則の根拠を確認した後に使用します。パスとコミットは自分のリポジトリに合わせて変更してください。[検出結果の修正](https://support.claude.com/en/articles/14661296-use-claude-security) · [Claude Security](https://claude.com/product/claude-security)

```text
確認済みのコミットと添付ファイルで、返金要求のサーバー認可を確認してください。

業務規則
- 同じ店舗の返金担当者だけが返金を要求できる。
- 閲覧権限と返金要求権限は別である。
- ユーザーの役割と店舗は認証済みのサーバーコンテキストから読む。

まず共通の認可規則が適用されているか確認し、根拠ファイルを示してください。
欠落を確認した場合は既存の認可検査を最小限修正してください。
同じ店舗の担当者は許可し、閲覧専用ユーザー、別店舗の担当者、
未認証の要求は拒否する回帰テストを追加してください。
確認したファイル、変更、実行したテストと結果、未確認事項を報告してください。
```

完了条件は**許可する範囲が既存の規則に一致すること**です。役割だけを検査すると別店舗の担当者が通過し、店舗だけでは閲覧専用ユーザーを除外できません。変更を読み、サーバーが認証済みユーザーのコンテキストとリポジトリから読み込んだ注文の店舗を比較することを確認します。

## 許可と拒否の両経路を確認する

次のコードは修正後の認可判断だけを独立して確認します。認証と注文の取得が済み、サーバーが `actor` と `order` を渡すと仮定します。実際の返金処理と決済事業者との通信はこの関数の範囲外です。

```javascript
import assert from "node:assert/strict";

function canRequestRefund(actor, order) {
  return actor !== null &&
    actor.role === "REFUND_MANAGER" &&
    actor.storeId === order.storeId;
}

const order = { storeId: "store-a" };
const manager = { role: "REFUND_MANAGER", storeId: "store-a" };

const cases = [
  ["same-store refund manager", manager, true],
  ["read-only operator", { ...manager, role: "VIEWER" }, false],
  ["different-store refund manager", { ...manager, storeId: "store-b" }, false],
  ["unauthenticated request", null, false]
];

for (const [label, actor, expected] of cases) {
  assert.equal(canRequestRefund(actor, order), expected, label);
  console.log(`PASS ${label}`);
}
```

`refund-policy.mjs` として保存して `node refund-policy.mjs` を実行した結果、Node.js 22.17.0で四つの判断が期待どおりになりました。

```text
PASS same-store refund manager
PASS read-only operator
PASS different-store refund manager
PASS unauthenticated request
```

実際のリポジトリでは、返金要求の経路がこの認可判断を通ることも確認します。拒否された要求では返金処理が登録されず、許可された要求では既存の処理が維持されることを結合テストで確認します。検出結果を整理する際は修正コミットまたはPR、実行したテスト、残事項を記録します。報告が誤りと判断した場合も、既存の共通検査などの根拠を記録します。[Claude Securityの検出結果の追跡](https://support.claude.com/en/articles/14661296-use-claude-security)

この記事の検出結果は説明用の架空の例です。Claude Securityで実際のリポジトリを検査したりMythosの応答を収集したりしておらず、上の結果はローカルの認可関数のテストです。認証済みモデルの実行、実際の返金処理、決済連携もテストしていません。
