---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2026-11-26-news-dry-run-guide",
  "routeSlug": "2026-11-26-news-dry-run-guide",
  "kind": "post",
  "title": "GitHub Actions でニュースの下書きを公開せずに検証する方法",
  "description": "下書きが検証を通ったか、原稿・公開待ちキュー・状態ファイルが実行前と同じかを個別に確かめます。",
  "categories": [
    "blog"
  ],
  "tags": [
    "github-actions",
    "ci",
    "dry-run"
  ],
  "sourcePath": "src/content/posts/en/2026-11-26-news-dry-run-guide.md",
  "sourceSha256": "bbd2b23eadacc9df77585d34bf7ba6243a6a849fbbfcba51c6f2272b35553659",
  "draftSha256": "396d657c5e054d2b881bccc6d382138c2b85a513d9ad01406e1ef35703941993",
  "manifestPath": ".pipeline/technical-translations/batch-2092/manifest.json",
  "manifestSha256": "9a982e5784cecb3a4cc8afc502eaa7a3dabfd32dbeb039f0577cad485ee5cb2d",
  "publishedAt": "2026-11-26T07:02:16.794Z",
  "updatedAt": "2026-11-26T07:02:16.794Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 201,
    "approvedAt": "2026-11-26T07:02:16.794Z",
    "basis": "The owner authorized publication of the news draft dry-run guide in all eight blog languages in item 92."
  }
}
---

下書きがスキーマ検証を通っても、公開待ちキューに項目が追加されていれば、公開を伴わない検証としては失敗です。テストでは、入力に応じた終了コードが返ることと、原稿・キュー・状態ファイルが実行前と一致することを個別に確かめます。

## プレビューの成功と検証の失敗を試す

リポジトリのルートで Python 3 を使い、次のコマンドを実行します。どちらのテストも一時ディレクトリを使い、フィード、下書き生成、リンク検査の結果をテストデータに置き換えます。ネットワーク接続やモデルの API キーは不要です。

```sh
PYTHONPATH=scripts python3 -B -m unittest \
  test_bilingual_digest.PublicationTests.test_preview_validates_without_writing_content_or_state \
  test_bilingual_digest.PublicationTests.test_ai_or_link_failures_do_not_write
```

![テスト入力を正常なプレビューと AI またはリンクのエラーに分け、成功時も失敗時も原稿と状態のディレクトリが作成されていないことを確認します。](/assets/diagrams/technical/ja-2026-11-26-news-dry-run-guide.svg)

最初のテストは `--dry-run --force` で終了コード 0 と `generated=false` を確認します。次のテストは `--check-links` を指定し、AI エラーとリンクエラーを別々に発生させ、それぞれ終了コード 1 を確認します。どちらも一時ディレクトリの直下に `src` または `.pipeline` ができると失敗します。上のコマンドの実行結果は `Ran 2 tests`、`OK` でした。

## ローカルで Spring の記事と照合した範囲

別のローカル検証では、[Spring AI チームの公式記事](https://spring.io/blog/2026/11/24/spring-ai-tool-call-confirmation-park-resume)を一つ選びました。隔離したテスト環境で `--dry-run --force --max-items 1 --check-links` を指定し、Gemini による生成とレビューの応答だけを用意済みのデータに置き換えました。CLI に同じ引数を渡すだけでは、このデータは注入されません。

元記事の取得結果は HTTP 200 でした。リンクを検査し、韓国語と英語の下書きにある計 4 か所の引用を実際の本文と照合しました。Python と Astro のコンテンツスキーマによる検証も通りました。出力は `generated=false` で、別途比較した原稿・キュー・状態ファイル全 3,333 件のパスと内容も実行前後で一致しました。実際の Gemini の可用性と生成品質は未検証です。[ローカル実行の記録](https://github.com/youdozi/youdozi.github.io/pull/198)

## PR の検証ジョブに与える権限

この PR の通常の CI では、必須の `build / build` が成功し、`deploy` はスキップされました。Spring の元記事との照合結果は上記のローカル実行の記録で確認できます。[PR の検査結果](https://github.com/youdozi/youdozi.github.io/actions/runs/45734945701) · [クリーンなチェックアウトで Astro の検査が失敗した理由（韓国語）](https://youdozi.github.io/ko/posts/2026-11-26-astro-clean-checkout/)

独立した検証ジョブを設ける場合は、チェックアウトに `contents: read` だけを許可し、公開用の認証情報は渡さないようにします。リポジトリに対して読み取り専用でも、プロセスはローカルのファイルを書き換えられます。原稿・キュー・状態ファイルは実行前後で比較してください。[GitHub のジョブ用トークンの解説](https://docs.github.com/en/actions/concepts/security/github_token)
