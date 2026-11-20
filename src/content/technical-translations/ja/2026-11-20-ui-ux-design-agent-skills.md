---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2026-11-20-ui-ux-design-agent-skills",
  "routeSlug": "2026-11-20-ui-ux-design-agent-skills",
  "kind": "post",
  "title": "Claude Code・Codex で UI/UX を設計する — ユーザーフロー、Figma、アクセシビリティのスキル",
  "description": "Claude Code と Codex でユーザーフロー、Figma のデザインシステム、UI 文言、アクセシビリティを設計し、予約キャンセルの確認ダイアログを Playwright でキーボード操作とフォーカスの面から検証する。",
  "categories": [
    "ai"
  ],
  "tags": [
    "claude-code",
    "codex",
    "agent-skills",
    "figma",
    "ui-ux",
    "accessibility",
    "playwright"
  ],
  "sourcePath": "src/content/posts/en/2026-11-20-ui-ux-design-agent-skills.md",
  "sourceSha256": "2fa2cdf9d087643f65deb61063a994cdd75549bf0b412379d831fa97c01906e2",
  "draftSha256": "af371a400b46952a2999a7e2aa2795205b8aa9271e062bb39cde99cd829778f8",
  "manifestPath": ".pipeline/technical-translations/batch-172/manifest.json",
  "manifestSha256": "9fbed8219e1f64a1b7901da9450c566e1c2c7b0ed64840e56f60a1b726fd39df",
  "publishedAt": "2026-11-20T14:40:06.354Z",
  "updatedAt": "2026-11-20T14:40:06.354Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 172,
    "approvedAt": "2026-11-20T14:40:06.354Z",
    "basis": "User requested seven new language editions for each of four already published guides and approved parallel AI translation and verification. This records publication authorization."
  }
}
---

**画面を描く前に、ユーザーが何を終える必要があり、どこで引き返せるかを決める。** 予約キャンセル画面なら、キャンセルの結果を事前に把握したうえで、予約を維持するかキャンセルするかを選べるようにする。ダイアログの文言、初期フォーカス、閉じた後にフォーカスを戻す先まで決めれば、実装と検証に同じ基準を使える。

[前回の記事](/ko/posts/2026-11-19-website-building-agent-skills/)はウェブサイト制作全体を扱った。ここでは UI/UX の工程を掘り下げる。2026年11月20日に確認した Claude Code と Codex の公開スキル、Figma・Vercel・W3C の資料をもとに、予約キャンセルの流れを企画からブラウザーでの確認まで追う。

## 成果物に合わせてスキルを選ぶ

| 必要な成果物 | スキルまたは進め方 | レビューの観点 |
| --- | --- | --- |
| ユーザーフローと画面の状態 | プロジェクト用の `frontend-architecture-design` ガイド | 開始、確認、離脱、処理中、成功、失敗を定義できているかを見る。実際のユーザー調査があれば、観察結果と仮説を分ける。 |
| レビュー用のプロトタイプ | Codex の [Product Design プラグイン](https://github.com/openai/plugins/tree/main/plugins/product-design) | 状態遷移を確かめられる試作を作る。予約を維持する経路と、キャンセルを確定する経路の両方があるかを見る。 |
| 視覚的な方針と UI コード | Claude Code の [`frontend-design`](https://github.com/anthropics/skills/tree/main/skills/frontend-design) | 見出し、説明、操作ボタンの視覚的な優先順位を具体化する。見出しが長くなったり画面が狭くなったりしても、意味と順序が保たれるかを確認する。 |
| Figma 画面の組み立て | Figma プラグインの [`figma-generate-design`](https://github.com/openai/plugins/tree/main/plugins/figma/skills/figma-generate-design) | 既存のライブラリにあるボタンやダイアログのインスタンスを再利用し、状態ごとにフレームを作る。コンポーネントと変数の関連付けが維持されているかを確認する。 |
| デザインシステムのライブラリ | Figma プラグインの [`figma-generate-library`](https://github.com/openai/plugins/tree/main/plugins/figma/skills/figma-generate-library) | コードのデザイントークンとコンポーネントをもとに Figma の変数やライブラリを作成・更新する。バリアントと変数の関連付けを実際のコードの名前と照合する。 |
| 確定した Figma 画面の実装 | Figma プラグインの [`figma-design-to-code`](https://github.com/openai/plugins/tree/main/plugins/figma/skills/figma-design-to-code) | 対象のフレームを読み、既存の UI コードで実装する。見た目を比較したあと、キーボード操作と失敗時の状態を別途確認する。 |
| UI 文言 | プロジェクト用の `cms-ux-writing` などの UX ライティングガイド | ボタンを押した結果を動詞で表す。「予約を維持」「予約のキャンセルを確定」のように、操作の結果が分かる文言にする。 |
| インターフェースのレビュー | Vercel の [`web-design-guidelines`](https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines) とブラウザー検証 | コードからアクセシビリティや UI の問題候補を見つけ、ブラウザーでキーボードの操作順、フォーカスの移動、画面幅ごとの配置を確認する。 |

プロジェクト用の二つのガイドは、チームの画面設計や文言のルールを再利用可能なスキルにする例だ。特定製品の組み込み機能ではない。予約フローのレビュー担当者がいるなら、先に試作を見せ、意見を状態表に反映してから実装へ渡す。合意済みの Figma フレームとコードのコンポーネントがあるなら、実装とアクセシビリティのチェックから始めてもよい。

Claude Code では、Anthropic の `frontend-design` は公式マーケットプレイスの `example-skills` に含まれる。Codex で Figma スキルを使うには、プラグインに接続した Figma ツールと、ファイルへのアクセス権が必要だ。Figma 上で画面やコンポーネントを作るときは、作成用スキルとプラグインの `figma-use` ガイドを併用する。実装対象のデザインを読み取る作業には対象フレームのリンクを、新しいフレームを作る作業には編集可能なファイルと再利用するライブラリを渡す。 [Anthropic の導入手順](https://github.com/anthropics/skills#claude-code) · [Codex 向け Figma プラグイン](https://github.com/openai/plugins/tree/main/plugins/figma)

ブランドガイドがあれば、実際のロゴ、色、フォント、禁止例も渡す。名前だけで Anthropic の `brand-guidelines` をチームのブランドに適用すると、Anthropic の色や書体が入り込む可能性がある。このスキルの標準資料は Anthropic のブランド向けだ。 [`brand-guidelines` のソース](https://github.com/anthropics/skills/tree/main/skills/brand-guidelines)

## 予約キャンセルの流れをデザインと実装へ渡す

画面を描く前に、ユーザーの行動とその結果を表にする。以下は設計例だ。返金規定やキャンセル料の案内は、実際のサービスのルールを確認して書く。

| ユーザーの行動またはサーバーの状態 | 画面の動作 |
| --- | --- |
| 予約詳細で「キャンセルオプションを開く」を選ぶ | 確認ダイアログを開き、「予約を維持」にフォーカスを置く。 |
| 「予約を維持」を選ぶ、または Escape を押す | ダイアログを閉じ、予約を維持する。フォーカスはダイアログを開いたボタンに戻る。 |
| 「予約のキャンセルを確定」を選ぶ | 本番サービスではリクエストを送信し、処理中の状態を表示する。同じリクエストが繰り返されても二重処理は防ぐ。 |
| サーバーで成功を確認 | 予約の状態を「キャンセル済み」に変え、結果を知らせる。 |
| サーバーで失敗を確認 | 予約の状態を維持し、失敗理由と次にできる行動を知らせる。 |

取り消しにくい操作の確認では、影響の最も小さい選択肢に初期フォーカスを置くとよい場合がある。ダイアログを閉じたときは通常、開いた要素にフォーカスを戻す。その要素がなくなった場合は、作業を続けられる別の要素に移す。 [W3C のモーダルダイアログパターン](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/)

実装を担当するエージェントに、操作と判定の基準を次のように渡す。

**プロンプト例** 予約詳細にキャンセル確認ダイアログを設計してください。既存のダイアログとボタンを再利用してください。 初期フォーカスは「予約を維持」に置き、Escape で閉じた場合は予約の状態を保ち、 「キャンセルオプションを開く」にフォーカスを戻してください。 キャンセル要求の送信後は、処理中、成功、失敗の状態をそれぞれ表現してください。 失敗画面には再試行やサポートへの問い合わせなど、次に取れる行動を表示してください。 画面と状態表をレビューしてから実装できるよう、フレームと状態の対応を示してください。

## 実習 — 確認ダイアログのフォーカスと二つの結果を確認する

ブラウザーで、表の最初の二行と、キャンセル確定時の画面変化を検証する。実習のキャンセル確定はページ内の状態だけを変える。サーバーへのリクエスト、失敗時の処理、二重送信の防止は本番プロジェクトで別途検証する。

![予約済みの状態からダイアログを開き、初期フォーカスを確認する。Escape または「予約を維持」で閉じたら予約状態とボタンのフォーカスを確認する。キャンセルを確定したら、キャンセル済みの表示を確認する。](/assets/diagrams/technical/ja-2026-11-20-ui-ux-design-agent-skills.svg)

Node.js 22 と Chrome を用意する。新しい作業フォルダーで `npm init -y` と `npm install --save-dev playwright-core@1.64.1` を実行する。以下のコードを `dialog-check.mjs` として保存し、`node dialog-check.mjs` で実行する。Chrome のパスが標準と異なる場合は `CHROME_PATH` を指定する。 [Playwright の起動オプション](https://playwright.dev/docs/api/class-browsertype#browser-type-launch)

```js
import assert from 'node:assert/strict';
import { chromium } from 'playwright-core';

const browser = await chromium.launch({
  executablePath: process.env.CHROME_PATH
    ?? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
});

try {
  const page = await browser.newPage({ viewport: { width: 360, height: 700 } });
  page.setDefaultTimeout(2000);
  await page.setContent(`
    <button id="open">취소 옵션 열기</button>
    <p role="status">예약 유지 중</p>
    <dialog aria-labelledby="title" aria-describedby="description">
      <h2 id="title">예약을 취소할까요?</h2>
      <p id="description">확정하면 예약 상태가 취소됨으로 바뀝니다.</p>
      <form method="dialog">
        <button value="keep" autofocus>예약 유지</button>
        <button value="cancel">예약 취소 확정</button>
      </form>
    </dialog>
    <script>
      const trigger = document.querySelector('#open');
      const dialog = document.querySelector('dialog');
      const status = document.querySelector('[role="status"]');

      trigger.addEventListener('click', () => {
        dialog.returnValue = '';
        dialog.showModal();
      });
      dialog.addEventListener('close', () => {
        if (dialog.returnValue === 'cancel') {
          status.textContent = '예약 취소됨';
        }
      });
    </script>
  `);

  const trigger = page.getByRole('button', { name: '취소 옵션 열기' });
  const dialog = page.getByRole('dialog', { name: '예약을 취소할까요?' });
  const status = page.getByRole('status');
  const focused = () => page.evaluate(
    () => document.activeElement?.textContent?.trim(),
  );

  for (const close of ['Escape', '예약 유지']) {
    await trigger.focus();
    await page.keyboard.press('Enter');
    await dialog.waitFor({ state: 'visible' });
    assert.equal(await focused(), '예약 유지', '초기 포커스');
    await page.keyboard.press(close === 'Escape' ? 'Escape' : 'Enter');
    await dialog.waitFor({ state: 'hidden' });
    assert.equal(await status.textContent(), '예약 유지 중');
    assert.equal(await focused(), '취소 옵션 열기', '닫은 뒤 포커스');
    console.log(`PASS ${close}: 예약 유지 및 포커스 복귀`);
  }

  await page.keyboard.press('Enter');
  await dialog.waitFor({ state: 'visible' });
  assert.equal(await focused(), '예약 유지', '초기 포커스');
  await page.keyboard.press('Tab');
  assert.equal(await focused(), '예약 취소 확정', '확정 버튼 포커스');
  await page.keyboard.press('Enter');
  await page.waitForFunction(
    () => document.querySelector('[role="status"]').textContent === '예약 취소됨',
  );
  await dialog.waitFor({ state: 'hidden' });
  assert.equal(await focused(), '취소 옵션 열기', '확정 뒤 포커스');
  console.log('PASS 예약 취소 확정: 상태 변경 및 포커스 복귀');
} finally {
  await browser.close();
}
```

以下は macOS の Chrome で実行した出力だ。実習コードの画面文言とログは元の韓国語のまま掲載している。

```text
PASS Escape: 예약 유지 및 포커스 복귀
PASS 예약 유지: 예약 유지 및 포커스 복귀
PASS 예약 취소 확정: 상태 변경 및 포커스 복귀
```

`autofocus` を「予約のキャンセルを確定」に移す対照実験では、初期フォーカスの検証が失敗した。この実習では、ダイアログのアクセシブルな名前、キーボード操作、初期フォーカス、閉じた後のフォーカスとステータス表示を確認した。実際の画面では、キーボードで移動するときにフォーカス表示が見えるか、大きい文字でボタンや説明を読めるか、支援技術でステータスのメッセージを読み取れるかも確認する。 [WCAG 2.2](https://www.w3.org/TR/WCAG22/)
