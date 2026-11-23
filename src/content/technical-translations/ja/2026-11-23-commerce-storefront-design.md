---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2026-11-23-commerce-storefront-design",
  "routeSlug": "2026-11-23-commerce-storefront-design",
  "kind": "post",
  "title": "EC ストア画面の設計：商品選びから決済確認まで",
  "description": "商品一覧から注文詳細まで購入者が見られる情報とできる操作を決め、決済から戻った購入者をサーバーの注文・決済状態に沿って案内します。",
  "categories": [
    "architecture"
  ],
  "tags": [
    "ecommerce",
    "storefront",
    "checkout",
    "order-management",
    "payments"
  ],
  "sourcePath": "src/content/posts/en/2026-11-23-commerce-storefront-design.md",
  "sourceSha256": "fde9deae56ab163d6fad0ea42a0136927d901a84ecd0111e5006b0eb21aa00ce",
  "draftSha256": "292748103b7287471cf886193ffb298cba02d76dcb105af78b4c85e05d187e32",
  "manifestPath": ".pipeline/technical-translations/batch-185/manifest.json",
  "manifestSha256": "3281e1d3e7c9b3abbb6c101d911dd0fcdee7dd54f7034838135f391123b6fb44",
  "publishedAt": "2026-11-23T00:19:14.218Z",
  "updatedAt": "2026-11-23T00:19:14.218Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 185,
    "approvedAt": "2026-11-23T00:19:14.218Z",
    "basis": "The site owner explicitly requested missing supported locales for the eight articles published in PRs #177–#184. This authorizes publication of the 48 editions enumerated in this batch."
  }
}
---

**決済画面から戻った購入者に空白の画面が表示されたら、最初に気になるのは請求されたかどうかです。** 既存の注文について結果を確認できる画面を用意します。商品詳細から注文履歴まで、各画面で確認できる事実と購入者が取れる操作を組み合わせます。

[EC 管理画面の設計ガイド](/en/posts/2026-11-23-commerce-admin-screen/)では、決済結果が未確定の注文を担当者が照会します。ここでは同じ状況を購入者の側から見ます。単一の販売事業者が物理商品を韓国ウォンで販売し、配送するストアを想定します。購入者はアカウントから注文します。割引と送料の規則は例です。

## 画面ごとに購入者は何を決めるか

| 画面 | 最初に表示する情報 | 購入者が次にできること |
| --- | --- | --- |
| 商品一覧と検索 | 商品名と写真、比較できる価格、適用中の絞り込み条件 | 結果を絞り込むか、商品ページを開く |
| 商品詳細 | 選択したバリエーションの価格と在庫、配送条件 | バリエーションと数量を選び、カートに入れる |
| カート | 商品ごとのバリエーション、数量、金額、概算合計、注文手続きに進めない商品 | 数量や商品を変更し、注文手続きに進む |
| 注文手続き | 配送先住所、送料、割引、最終金額、変更する箇所 | 条件を確認し、支払いをリクエストする |
| 注文詳細 | 注文番号、決済・配送・返金の状態、変更履歴 | 現在の状態に応じて結果を確認するか、配送を追跡する |

一覧に「₩39,000〜」と表示する場合、商品ページでバリエーションを選んだ時点で実価格を表示します。売り切れたバリエーションは文言で示します。検索結果がなければ適用中の絞り込み条件を表示し、解除できるようにします。検索結果の読み込みに失敗したら再試行を案内します。

[EC の在庫予約ガイド](/en/posts/2026-11-22-commerce-system-design-last-unit-of-stock/)と同じ方針を使います。商品ページは照会時点の在庫を表示し、カートは購入者の選択を保持します。注文を作成するときにサーバーが在庫を予約します。他の注文が最後の在庫を先に予約した場合は、対象の商品とバリエーションをカートで示し、ほかの商品と入力済みの配送先住所を残します。

## 購入者が支払い前に確認・変更できるようにする

最終金額と一緒に、バリエーション、数量、配送先住所を確認・変更できるようにします。ボタンには **「₩43,000 を支払う」** のように実際の操作を表示します。WCAG の金銭取引におけるエラー防止のガイダンスは、送信前に内容を確認し修正する手段を利用者に提供することを説明しています。 [金銭取引でのエラー防止に関する W3C のガイダンス](https://www.w3.org/WAI/WCAG22/Understanding/error-prevention-legal-financial-data.html)

キーボードがカート追加時に ₩39,000、注文手続き時に ₩42,000 なら、対象商品を明示します。たとえば「黒いキーボードの価格が ₩39,000 から ₩42,000 に変わりました」と表示します。割引と送料を再計算した合計を示し、支払いをリクエストする前にその金額を確認できるようにします。注文作成時、サーバーは購入者が確認した見積もりを請求額と照合し、取引条件を記録します。 [EC データベースで注文金額を保存する仕組み](/en/posts/2026-11-22-commerce-database-design/)

モバイルでは配送先や商品を変更するリンクを対応する項目の近くに置き、最終金額を支払いボタンの近くに表示します。ボタンを画面下部に固定する場合は、最後の入力項目やエラーメッセージまでスクロールして読めるようにします。カート合計の変更や決済確認結果など、フォーカスを動かさずに行える更新は、支援技術で通知することもできます。たとえば、結果のテキストが更新される領域に `role="status"` を追加します。 [ステータスメッセージに関する W3C のガイダンス](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html)

## サーバーで決済結果を確認する

![決済画面から戻ったら既存の注文を照会します。読み込み中と照会失敗を区別し、決済と注文の結果に応じて、状態の更新、配送追跡、商品一覧、返金情報の操作を案内します。](/assets/diagrams/technical/ja-2026-11-23-commerce-storefront-design.svg)

購入者が決済ページから戻ったら、サーバーで既存の注文を照会します。支払いボタンを押した後に注文作成のレスポンスが失われた場合は、同じ注文リクエストキーで注文がすでに受け付けられているか確認します。ボタンを短時間無効にすれば連打を減らせます。注文の重複はリクエストキーとサーバー側の一意性チェックで防ぎます。注文詳細と状態の API では、購入者がその注文にアクセスできるかも確認します。

| サーバーが確認した状態 | 購入者向けの文言と操作 |
| --- | --- |
| 注文状態の照会に失敗 | 「注文状態を読み込めませんでした。」 → **注文状態を再読み込み** |
| 注文が存在し、決済結果が未確定 | 「決済結果を確認中です。」 → **注文状態を更新** |
| 支払い完了、注文を確認中 | 「お支払いは完了しました。注文を確認中です。」 → **注文状態を更新** |
| 支払いと注文が確定 | 「ご注文を受け付けました。」 → **配送を追跡** |
| 請求なしで取消を確認 | 「注文を取り消しました。請求はありません。」 → **商品を見る** |
| 取消後に支払いを確認、返金待ち | 「返金を処理中です。」 → **返金状態を更新** |
| 返金を確認 | 「返金が完了しました。」 → **返金の詳細を見る** |

実際の出荷状況に基づいて、出荷準備中、配送中、配達済みを表示します。現在の状態で操作が許可され、利用者に権限があることを確認したうえで、取消や返品のボタンを表示します。受け付けた後は進捗を案内します。返金完了の文言はサーバーが結果を確認した時点で表示します。

## サーバーの状態を文言と操作に対応づける

この例は、サーバーから取得済みの注文と決済の状態を、見出しと次の操作に対応づけます。ネットワークエラーと決済結果未確定は別の入力です。定義されていない状態の組み合わせでは成功を表示しません。例のコードには韓国語の UI 文言を使い、上の表には同じ内容の日本語を載せています。コードを `order-view.mjs` に保存し、`node order-view.mjs` を実行します。

```javascript
const labels = {
  loading: ["주문 상태를 불러오는 중입니다.", null],
  unavailable: ["주문 상태를 불러오지 못했습니다.", "주문 상태 다시 불러오기"],
  pending: ["결제 결과를 확인 중입니다.", "주문 상태 새로고침"],
  paidReview: ["결제는 완료됐고 주문을 확인 중입니다.", "주문 상태 새로고침"],
  confirmed: ["주문이 접수됐습니다.", "배송 상태 보기"],
  closed: ["주문이 취소됐으며 결제된 금액이 없습니다.", "상품 다시 보기"],
  refundPending: ["환불을 처리 중입니다.", "환불 상태 새로고침"],
  refunded: ["환불이 완료됐습니다.", "환불 내역 보기"]
};

function orderView(snapshot) {
  if (snapshot.kind === "loading") return labels.loading;
  if (snapshot.kind === "unavailable") return labels.unavailable;

  const { order, payment } = snapshot;
  if (order === "CANCELLED" && payment === "REFUND_PENDING") {
    return labels.refundPending;
  }
  if (order === "CANCELLED" && payment === "REFUNDED") {
    return labels.refunded;
  }
  if (order === "CANCELLED" && payment === "CLOSED_UNPAID") {
    return labels.closed;
  }
  if (order === "CONFIRMED" && payment === "PAID") {
    return labels.confirmed;
  }
  if (order === "PENDING_PAYMENT" && payment === "PAID") {
    return labels.paidReview;
  }
  if (order === "PENDING_PAYMENT" &&
      (payment === "PENDING" || payment === "UNKNOWN")) {
    return labels.pending;
  }
  return labels.unavailable;
}

const verified = (order, payment) => ({ kind: "loaded", order, payment });
const cases = [
  [{ kind: "loading" }, "loading"],
  [{ kind: "unavailable" }, "unavailable"],
  [verified("PENDING_PAYMENT", "UNKNOWN"), "pending"],
  [verified("PENDING_PAYMENT", "PAID"), "paidReview"],
  [verified("CONFIRMED", "PAID"), "confirmed"],
  [verified("CANCELLED", "CLOSED_UNPAID"), "closed"],
  [verified("CANCELLED", "REFUND_PENDING"), "refundPending"],
  [verified("CANCELLED", "REFUNDED"), "refunded"],
  [verified("CONFIRMED", "UNKNOWN"), "unavailable"]
];

for (const [input, key] of cases) {
  if (orderView(input) !== labels[key]) throw new Error(key);
  console.log("PASS", key);
}
```

Node.js 22.17.0 で九つの入力がすべてテストに合格しました。照会失敗、決済結果未確定、請求なしの取消、返金待ちのそれぞれで期待した文言と操作が返りました。今回のテスト対象は、状態から UI の文言と操作を決める関数です。モバイルでの使いやすさ、支援技術の動作、実際の決済連携は、実装した画面で確認します。
