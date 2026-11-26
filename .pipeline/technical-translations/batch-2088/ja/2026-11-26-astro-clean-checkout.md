---
{
  "state": "draft",
  "language": "ja",
  "translationKey": "2026-11-26-astro-clean-checkout",
  "title": "クリーンなチェックアウトでだけ Astro のチェックが失敗した理由",
  "description": "ニュースの下書き作成が SVG の欠落で止まりました。アセットを準備する前後で同じチェックを実行し、原因を切り分けました。",
  "sourcePath": "src/content/posts/en/2026-11-26-astro-clean-checkout.md",
  "sourceSha256": "7dba5eae5f82355acd4550b2c1c0881e24e8e8c82d7597021db67ee13393285f"
}
---

ニュースの下書き作成ワークフローが `ENOENT` で止まりました。調べた失敗 4 件のうち 3 件は、Astro が既存の記事の画像サイズを読み取る段階で発生しました。チェックアウト直後は、記事が参照する SVG がまだ生成されていません。前回のビルドで生成したファイルが手元に残っていると、同じチェックでも通ることがあります。[下書き候補のチェックが失敗した実行](https://github.com/youdozi/youdozi.github.io/actions/runs/45548722494)

## SVG の生成前後で同じチェックを実行する

失敗時のコミットを別のディレクトリにチェックアウトして `npm run check` を実行すると、終了コードは 1 でした。同じディレクトリで `node scripts/prepare-public.mjs` を実行して公開用アセットを準備すると、再チェックの終了コードは 0 になりました。ビルド時にもアセットを準備しますが、CI ではその前にチェックが走ります。

![クリーンなチェックアウトから SVG を生成し、Astro が画像サイズを読み取った後でサイトをビルドする。](2026-11-26-astro-clean-checkout.svg)

CI の手順を再現するには、リポジトリのルートで Node.js 24 と Python 3.11 を使い、`npm ci` で依存関係をインストールしてから以下を実行します。各コマンドが成功すると次に進みます。[修正 PR](https://github.com/youdozi/youdozi.github.io/pull/198) · [PR のビルド結果](https://github.com/youdozi/youdozi.github.io/actions/runs/45734945701)

```sh
node scripts/prepare-public.mjs &&
  npm run check &&
  npm run build
```

## 生成段階で起きた別の失敗

別の実行では、生成段階で Gemini が HTTP 503 を返しました。修正後は同じモデルを使い、初回の再試行まで 1 秒、次の再試行まで 2 秒待ちます。この再試行枠は実行全体で共有し、リクエストのたびにリセットされることはありません。[生成段階で失敗した実行](https://github.com/youdozi/youdozi.github.io/actions/runs/45098322259)

Spring の公式記事を使った韓国語・英語のドライランでは、生成とレビューのモデル応答だけを模擬しました。実際の原文と引用を照合し、リンクを確認して、Python と Astro 双方のコンテンツスキーマで検証しました。下書きやキューへの書き込みはなく、実際に Gemini が応答できるかどうかは未検証です。

手元でだけチェックが通る場合は、クリーンなチェックアウトで欠けているファイルを最初に読むコマンドを探してみてください。ファイルを生成する処理との前後関係を調べると、ビルドが成功するのに先行するチェックが失敗する理由を絞り込めます。
