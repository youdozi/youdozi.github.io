---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2026-10-30-php2shell-runtime-patching",
  "routeSlug": "2026-10-30-php2shell-runtime-patching",
  "kind": "post",
  "title": "PHP2Shellへの対応：修正済みPHPビルドとWebワーカーを検証する",
  "description": "PHP2Shellの上流修正とベンダーのバックポートを区別し、リクエストを処理するPHPワーカーを検証します。セッションの追加問題とWindowsのBrotli再ビルドは個別に追跡します。",
  "categories": [
    "security"
  ],
  "tags": [
    "php2shell",
    "php",
    "security"
  ],
  "sourcePath": "src/content/posts/en/2026-10-30-php2shell-runtime-patching.md",
  "sourceSha256": "f4aa334e127facad6b41b0eb19920466d78f78d25c9065c6faf85c584c63115c",
  "draftSha256": "15b639e41a346b17c4614f8ae76bb0346da4f58b874581e2fd9edaf4fc27b3a0",
  "manifestPath": ".pipeline/technical-translations/batch-078/manifest.json",
  "manifestSha256": "e685b2de5dafd8cfff8e8e996fa2b09613becb072bdd575b58b9eca9651474a3",
  "publishedAt": "2026-10-31T02:49:44.828Z",
  "updatedAt": "2026-10-31T02:49:44.828Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 118,
    "approvedAt": "2026-10-31T02:49:44.828Z",
    "basis": "2026-10-31 user instruction “진행해줘” immediately following delivery of the reviewed 72 complete translations in PR #118; interpreted as authorization to publish exactly batch-078 in all six languages. Separate AI language review is recorded in the manifest; this does not claim a human line-by-line review. Excludes the older 120 technical drafts and 318 pending news translations."
  }
}
---
PHP2Shellへの対処は、CMSやプラグインの更新だけでは完了しません。[CVE-2026-109618](https://github.com/php/php-src/security/advisories/GHSA-w8hw-w9fx-j79w)と[CVE-2026-109619](https://github.com/php/php-src/security/advisories/GHSA-6wmf-4rv5-p3rp)を修正したPHPビルドを入手し、Webリクエストを処理するすべてのワーカーがそれを使用していることを検証します。端末の`php -v`が示すのは、その端末で選択されたCLIだけです。

## PHP2Shellは何に影響しますか？

この二つのCVEは、PHPエンジンのリクエスト状態とメモリの生存期間に関わります。一つ目は、メモリ不足の処理によって初期化が中断された後、クリーンアップ中に不正な状態が使用される問題です。二つ目は、リクエストのメモリ解放後も内部状態が残り、同じワーカーの後続リクエストで使用される問題です。該当する条件下では、認証なしのリモートコード実行が可能です。

[PHPチームのアドバイザリ](https://www.php.net/archive/2026.php)では、調査対象となるWeb提供環境として、mod_phpに加えてPHP-FPM、php-cgi、FrankenPHP、LiteSpeedを挙げています。特定のSAPIであることは、サービスを対象外にする理由にはなりません。一方、脆弱なバージョンの文字列だけでは、そのサービスに到達可能な悪用経路があるとは示せません。

## どのバージョンと比較しますか？

以下は、2026年10月30日に確認した、**当初の二つのCVEを修正した最初の上流ソースリリース**です。インストール前に、同じ供給元の現在サポートされているリリースと追加アドバイザリを確認してください。

| PHPブランチ | 両方のCVEを修正した最初のソースリリース |
| --- | --- |
| 8.2 | 8.2.35 |
| 8.3 | 8.3.36 |
| 8.4 | 8.4.27 |
| 8.5 | 8.5.12 |

ディストリビューションのパッケージは、短いPHPバージョンではなく、完全なパッケージリビジョンをベンダーのアドバイザリと比較します。たとえば、[Ubuntu USN-8948-1](https://ubuntu.com/security/notices/USN-8948-1)は、`8.3.6-0ubuntu0.24.04.13`を、`php8.3-fpm`のUbuntu 24.04向け修正済みパッケージとしています。この番号を上流の`8.3.36`と比較すると、バックポートを誤判定します。この通知は、同じバージョン文字列を表示する任意の独自ビルドの真正性を保証するものではありません。

PHP 8.1以前は、PHPプロジェクトのサポートが終了しています。ベンダーのサポートとバックポートの根拠を確認するか、サポート対象のブランチに移行します。ソースのパッチが公開されていることと、サーバーがそのパッチを実行している証拠は別のものです。

## CLIの証拠を集め、Webの証拠と混同しない

![選択されたCLIの実行ファイル、バージョン、設定をJSONとして記録し、Webワーカーの評価は分離します](/assets/diagrams/technical/ja-2026-10-30-php2shell-runtime-patching.svg)

図は以下の収集コードに対応しています。Web SAPIでは情報を出力せずに終了します。CLIでは、修正状況を判定せずに実行ファイル、バージョン、設定を記録します。サービスの特定、パッチ適用、再起動は別の運用手順であり、このコードは実行しません。

PHP 8.2以降で、ドキュメントルート外の新しいディレクトリにファイルを保存します。[PHP定数](https://www.php.net/manual/en/reserved.constants.php)と[ini_get](https://www.php.net/manual/en/function.ini-get.php)を使い、現在のプロセスだけを読み取ります。リクエストの送信、設定の変更、セッションの開始は行いません。`phpinfo()`ページを公開する必要はありません。

### `runtime-evidence.php`

```php
<?php
if (PHP_SAPI !== 'cli') {
    http_response_code(404);
    exit;
}

$evidence = [
    'scope' => 'this-cli-process-only',
    'pid' => getmypid(),
    'version' => PHP_VERSION,
    'sapi' => PHP_SAPI,
    'binary' => PHP_BINARY,
    'loadedIni' => php_ini_loaded_file() ?: null,
    'uploadProgress' => ini_get('session.upload_progress.enabled'),
    'serializeHandler' => ini_get('session.serialize_handler'),
];
echo json_encode($evidence, JSON_PRETTY_PRINT | JSON_THROW_ON_ERROR), PHP_EOL;
```

```sh
php runtime-evidence.php
php -n -d session.upload_progress.enabled=0 runtime-evidence.php
```

最初のコマンドは、選択されたCLIの設定を読み取ります。二つ目はiniファイルを読み込まず、そのCLI呼び出しだけでアップロード進捗を無効にします。**Webサーバーの設定は変更せず、Webワーカーの有効な設定も確認しません。**

ローカルでの確認は分離したPHP CLIコンテナで実施され、`sapi`が`cli`のJSON出力を確認しました。二つ目のコマンドでは、`null`が`loadedIni`に、文字列`"0"`が`uploadProgress`に返りました。パス、PID、バージョン、既定値は環境によって異なります。この結果は、本番サービスの修正状況を確定するものでも、悪用を再現するものでもありません。

## インストールと稼働中のワーカーを個別に検証する

1. Webサーバーのupstream、FastCGI、モジュールの設定をたどり、実際のPHP実行ファイル、プール、コンテナ、レプリカを特定します。ホストのCLIとWebランタイムが同じインストール先を共有すると仮定しないでください。
2. そのランタイムの供給元と完全なパッケージリビジョン、またはイメージダイジェストをアドバイザリと比較します。独自ビルドでは、修正コミットとデプロイ済み成果物の対応関係を確認します。
3. 互換性のある修正済みビルドをデプロイし、影響を受けるプールやサービスのワーカー、またはコンテナを置き換えます。他のサービスがランタイムを共有している場合は、先に変更範囲を確認します。
4. すべての対象で、新しいプロセスと修正済みビルドの対応関係を検証します。通常のページ、ログインとセッションの動作、アップロード、エラー率を確認します。一部だけの展開や稼働プロセスの証拠不足を、完了とみなさないでください。

内部の資産記録で「修正済み成果物を特定済み」と「稼働中の適用を検証済み」を分けると、漏れたワーカーを見つけやすくなります。クラッシュだけでは侵害を証明できず、エラーログがないことも侵害を否定する根拠にはなりません。侵害が疑われる場合は、証拠を保全し、パッチ適用とは別に調査します。

## セッションの追加問題とWindows再ビルドを分ける

[10月23日のPHP追加通知](https://www.php.net/archive/2026.php)は、**CVE-2026-115560**を別に追跡しています。対象は、`session.serialize_handler`が`php_binary`または`php_serialize`に設定され、アプリケーションコードがそれを`php`へ変更してから`session_start()`を呼び、アップロード進捗が有効なままという組み合わせです。通知では、次の定期修正まで`session.upload_progress.enabled=0`を設定するよう提案しています。この設定は、当初の両CVEが完全に解決した証拠にはなりません。Web SAPIの有効な設定と機能への影響を確認してください。

[10月26日のWindows通知](https://www.php.net/archive/2026.php)では、パッケージ`8.5.12-1`、`8.4.27-1`、`8.3.36-1`、`8.2.35-1`を公開しています。これらには、**CVE-2026-111497**のBrotli修正が組み込まれています。これらはPHPソースのバージョンを変えずに依存関係を再ビルドしているため、`PHP_VERSION`だけでは区別できません。cURLの応答自動展開を使用するWindows環境では、このパッケージ修正も確認する必要があります。Node.jsの同じBrotli CVEについては、[Node2Shell対応ガイド](/en/posts/2026-10-30-node2shell-brotli-runtime-patching/)を参照してください。
