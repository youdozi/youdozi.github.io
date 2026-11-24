---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2026-11-24-github-pages-ads-guide",
  "routeSlug": "2026-11-24-github-pages-ads-guide",
  "kind": "post",
  "title": "GitHub Pages ブログに広告を掲載する：サービス選びから AdSense の設置まで",
  "description": "広告サービスを選び、GitHub Pages に AdSense とルートの ads.txt を設定して、審査と配信の状態を確認します。",
  "categories": [
    "tips"
  ],
  "tags": [
    "github-pages",
    "adsense",
    "ads-txt"
  ],
  "sourcePath": "src/content/posts/en/2026-11-24-github-pages-ads-guide.md",
  "sourceSha256": "884b5c639b2345ac6daac6b307db2cd0ec22e80801c8d5d2d5860b4ba12356d8",
  "draftSha256": "0ae432a716d851e12a18876bf8279b4376ef4319289101eb45ce2e48a9c874f8",
  "manifestPath": ".pipeline/technical-translations/batch-190/manifest.json",
  "manifestSha256": "6b40a455d4e018ed7edaefaa33a3094c5c1475c70d97ffdc7106618f6fa84d3f",
  "publishedAt": "2026-11-24T08:55:29.701Z",
  "updatedAt": "2026-11-24T08:55:29.701Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 193,
    "approvedAt": "2026-11-24T08:55:29.701Z",
    "basis": "Owner requested publication in eight languages; translations self-reviewed without independent or native-speaker review."
  }
}
---

`username.github.io` で技術ブログを運営しているなら、まず Google AdSense を検討できます。開発者が継続的に訪れるサイトなら Carbon Ads や EthicalAds も候補です。申し込む前に `https://username.github.io/ads.txt` を自分で公開できるか確認しましょう。特にプロジェクトのアドレスが `username.github.io/blog/` のような場合に重要です。

GitHub は、コンテンツが中心のサイトに広告を載せることを一般に禁止していません。ただし、オンラインビジネス、電子商取引、商用 SaaS を運営するための無料ホスティングとして GitHub Pages を使うことには制限があります。技術ブログに広告を添える場合は両方の方針を確認してください。[GitHub の広告ポリシー](https://docs.github.com/en/site-policy/acceptable-use-policies/github-acceptable-use-policies#10-advertising-on-github) · [GitHub Pages の制限](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)

## どの広告サービスを選ぶか

| サービス | 向いているサイト | 申し込み先 |
| --- | --- | --- |
| **Google AdSense** | 個人ブログに初めて広告を掲載し、自動配置と手動配置を選びたい場合 | [AdSense を始める](https://adsense.google.com/start/) |
| **Carbon Ads** | 開発者やデザイナーが読む記事、ドキュメント、ツール。月間 10,000 ページビューから審査し、他の広告ネットワークとの併用は認められていません。 | [Carbon Ads に申し込む](https://www.carbonads.net/join?_hsmi=83378591) |
| **EthicalAds** | 月間 50,000 ページビュー以上の開発者向けサイトで、読書の流れを妨げない場所に広告を一つ置ける場合 | [EthicalAds パブリッシャーガイド](https://www.ethicalads.io/publisher-guide/) |

まず広告の配置を決めましょう。コード例の多いブログなら、AdSense の手動広告を記事の下に一つ置き、モバイルで確認すると判断しやすくなります。AdSense では自分で位置を決める **広告ユニット** と Google が位置を決める **自動広告** を選べます。EthicalAds は別途、デスクトップとモバイルの最初の画面内に配置し、モバイルで不可能ならモバイル広告を無効にするよう案内しています。[AdSense の広告設定](https://support.google.com/adsense/answer/7037624)

![AdSense の流れ：コードを追加し、ルートに ads.txt を公開して URL を確認し、審査を申請します。](/assets/diagrams/technical/ja-2026-11-24-github-pages-ads-guide.svg)

図は設定から審査申請までをまとめています。実際の広告配信は別途確認します。

## 1. AdSense に登録してサイトを追加する

Google アカウントで AdSense に登録し、支払い国と支払い情報を入力します。**サイト → 新しいサイト** で `https://username.github.io` を追加します。Public Suffix List には `github.io` が含まれ、AdSense はこのリストにあるプラットフォームのサブドメインをサイトとして追加できると案内しています。その後、所有権の確認とサイト審査が続きます。[AdSense アカウントの作成](https://support.google.com/adsense/answer/7402253) · [サイト登録の基準](https://support.google.com/adsense/answer/12170421) · [Public Suffix List](https://publicsuffix.org/list/public_suffix_list.dat)

アドレスを確認してください。GitHub Pages のユーザーサイトは `username.github.io/`、プロジェクトサイトは通常 `username.github.io/blog/` です。プロジェクトの配布物に `ads.txt` を置くと `/blog/ads.txt` に公開される場合があります。Google はホストのルート `/ads.txt` から探すため、ユーザーサイトからルートに公開するか、ブログに接続したカスタムドメインのルートで提供します。[GitHub Pages のサイト種類](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages#types-of-github-pages-sites) · [Google の ads.txt クロール](https://support.google.com/adsense/answer/7679060)

## 2. 共通の `<head>` にコードを一つ、ルートに `ads.txt` を一つ置く

AdSense の所有権確認にはコードスニペット、`ads.txt`、メタタグがあります。スニペットを選んだ場合は、ダッシュボードのコードを共通レイアウトの `<head>` に入れます。以下は形式を示す例です。実際の配布には自分のアカウントからコピーしたコードを使ってください。[サイトを接続する](https://support.google.com/adsense/answer/7584263)

```html
<script async
  src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-0000000000000000"
  crossorigin="anonymous"></script>
```

`ads.txt` にはダッシュボードから提供された行をコピーします。このファイルはサイトの広告枠を販売できるアカウントを公開します。既存の販売者の行は残し、新しい行を追加します。

```text
google.com, pub-0000000000000000, DIRECT, f08c47fec0942fa0
```

Astro のユーザーサイトなら `public/ads.txt` に置きます。Astro は `public/` のファイルをビルド結果にコピーします。配布後はリポジトリだけでなく、公開 URL で開けるか確認します。[Astro の `public/`](https://docs.astro.build/en/guides/images/#src-vs-public) · [Google の ads.txt ガイド](https://support.google.com/adsense/answer/12171612)

```bash
curl -fsSL https://username.github.io/ads.txt
```

期待する出力は上記の販売者行です。実際のサイトではアカウントのパブリッシャー ID が返る必要があります。`username` は例であり、これは実行結果ではありません。

同じホストの多言語ブログならルートのファイル一つで十分で、`/ko/` と `/en/` に別々のファイルは不要です。各言語の代表記事の最終 HTML に共通ローダーが一回ずつ入っているか確認します。

## 3. 配布、審査、広告配信を分けて確認する

ファイルとコードを配布したら、AdSense で所有権を確認し、サイト審査をリクエストします。サイトの **`Ready`** は広告を表示する準備ができた状態、ads.txt の **`Authorized`** は Google がファイル内にパブリッシャー ID を見つけた状態です。公開 URL で開けても `Not found` が残る場合は、最後のクロール以降に変更されたか確認します。パスと内容が正しければ **更新を確認** で再確認をリクエストできます。[サイトの状態](https://support.google.com/adsense/answer/12170222) · [ads.txt の状態](https://support.google.com/adsense/answer/12171612)

広告を有効にする前に、広告のために収集・共有される情報と Cookie などの技術をプライバシーポリシーに記載します。EEA・英国・スイスの訪問者にパーソナライズド広告を配信するには、IAB の Transparency and Consent Framework (TCF) と統合された Google 認定の同意管理プラットフォーム（CMP）が必要です。AdSense の **プライバシーとメッセージ** にある欧州の規制に関するメッセージも選択肢です。[Google パブリッシャーのプライバシーポリシー](https://support.google.com/adsense/answer/10502938) · [Google の CMP 要件](https://support.google.com/adsense/answer/13554116)

審査後、自動広告のプレビューや手動広告ユニットで配置を確認します。スマートフォンで目次、コードのコピーボタン、言語切り替えメニューが広告に隠れないか確認してください。自分の広告をクリックしてテストせず、プレビューとダッシュボードのレポートを使います。[自動広告のプレビュー](https://support.google.com/adsense/answer/9261307) · [無効なトラフィック](https://support.google.com/adsense/answer/16737)

`youdozi.github.io` では、公開ルートの `ads.txt` と韓国語ホームページの HTML にある AdSense スクリプト一つを確認しました。確認範囲は公開ファイルと HTML であり、アカウントの審査状態と実際の広告配信は別途確認が必要です。[公開 ads.txt](https://youdozi.github.io/ads.txt) · [韓国語ホームページ](https://youdozi.github.io/ko/)
