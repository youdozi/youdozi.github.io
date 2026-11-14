---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2026-11-13-pickle-ai-security",
  "routeSlug": "2026-11-13-pickle-ai-security",
  "kind": "post",
  "title": "Pickle AI の仕組み: iPhone アプリの制御とパスワード保護の境界",
  "description": "Pickle AI が他の iPhone アプリを直接タップするかどうかを調べ、個別のブラウザーと API パスを Credential Enclave、OAuth トークン、および Vault パスワード保護と比較します。",
  "categories": [
    "security"
  ],
  "tags": [
    "pickle-ai",
    "ai-agent",
    "ios",
    "credentials",
    "nitro-enclaves"
  ],
  "sourcePath": "src/content/posts/en/2026-11-13-pickle-ai-security.md",
  "sourceSha256": "4973bca9ea9b81ec4e068b4f530a2b82742c427074c36836639b0c2db1a811e2",
  "draftSha256": "ca16b1fafb696a6a545c0016c816b1536fdc6231f1998457953f0f6aac5bdca7",
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

**Pickle AI の公式説明では、iPhone 上で他のアプリ画面を直接操作するのではなく、別のブラウザと接続されたアカウントが作業を実行すると指摘しています。** パスワードはモデルとは別に暗号化されますが、実際にログインに使用される値の保護境界は OAuth と Web サイトのパスワードで異なります。

対象は Pickle, Inc. の個人向け AI エージェント [Pickle](https://pickle.com/) です。2026 年 11 月 13 日に確認した公式ヘルプと、公開 `credential-enclave` ソースの **commit `cff16a343bf5bb7953e5b65df6ab3600107e127d`** を分析しました。公開セキュリティプログラムのリリース検証は実行しましたが、インストール済み iOS アプリや運用サーバー全体の監査ではありません。

## 実際に他の iPhone アプリをタップするのでしょうか?

[保存されたログインのヘルプ ページ](https://www.pickle.com/help/connect/save-login) によると、Pickle のブラウザは電話機とは別個のものであり、電話機に保存されているログイン情報を直接使用することはできません。 [タスク委任ガイド](https://www.pickle.com/help/tasks/delegate) では、実際のブラウザーでの Web サイトの操作と、アプリを閉じた後の作業の継続についても説明しています。

したがって、完了した注文または予約だけでは、インストールされているショッピング アプリの画面がタップされたとは証明されません。公開資料でサポートされているパスは次のとおりです。

| パス | 証拠と意味 |
| --- | --- |
| 別のブラウザ | 携帯電話のアプリ画面とは別に、Web サイトにログインし、フォームに記入します |
| 接続されたアカウント API | パブリック `forward` コードは、許可されたプロバイダー API リクエストに資格情報を添付します。 |
| 電話 | 公式タスクガイドには、ウェブで処理できないことについてユーザーに代わって電話することが記載されています |

Apple の [サードパーティアプリのサンドボックス](https://support.apple.com/en-gb/guide/security/sec15bfe098e/web)の説明では、他の情報にアクセスするには iOS が提供するサービスを使うよう制限されています。これだけですべての自動化が排除されるわけではありませんが、Pickle がサンドボックスをバイパスして他のアプリを制御しているという証拠は見つかりませんでした。

入手可能な資料では、Pickle のブラウザがどの DOM ツールや画面認識モデルを使用するか、各タスクにどの実行パスが選択されるかは確立されていません。ここでの動作モデルは、公式案内と公開された認証情報の処理経路を結び付けた分析です。

## AI にパスワードを教えずにログインするにはどうすればよいでしょうか?

モデルがパスワード文字列を直接出力しない場合でも、別の実行プログラムが必要な値を受け取り、それをログイン フォームに入力できます。 Pickle の [プライバシーの説明](https://www.pickle.com/privacy) によると、パスワードとカードの値はデバイス上で暗号化され、モデルが受け取る結果からは隠されています。この説明の技術的限界は、公開コードと比較する必要があります。

![セットアップ中に、iPhone はキーを作成し、暗号化されたユーザー キーを検証済みの Enclave に委​​任します。使用中に、アクティブな委任と暗号化されたレコードをチェックし、ログの永続性を確認してから、二 つのパスに分割します。 OAuth トークンは、ノード内の API 呼び出しに使用されます。 Vault のパスワードとカード値は、Web フォームに使う worker への release 応答として平文でノードの外に出ます。後の結果のマスキングは別の境界です。](/assets/diagrams/technical/ja-2026-11-13-pickle-ai-security.svg)

図の上部は、キーが事前に委任されているセットアップを示しています。下部は、委任が有効なままである間の資格情報の使用を示しています。これは、電話機がログインのたびに新しいキーを送信する必要があるという意味ではありません。また、この図はタスク実行プログラムの実装の詳細をすべて再現しているわけではありません。

### デバイスキーと暗号化されたレコード

[パブリック プロトコル](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/docs/protocol.md#3-keys) は、デバイス上で作成されたマスター キーが、署名、ログの復号化、および資格情報用に個別の派生キーとともに iCloud キーチェーンに保持されることを指定します。保存されたレコードは ChaCha20-Poly1305 で暗号化され、アカウントやレコード タイプなどのコンテキストも認証にバインドされます。

デバイスはノードの構成証明と公開キーを検証し、**派生ユーザー キー**を暗号化してそのノードに委任します。リモート構成証明は、公開キーがどの測定された実行環境に属しているかをチェックします。 [AWS Nitro Enclaves](https://docs.aws.amazon.com/enclaves/latest/user/) は、親サーバーからメモリを分離し、直接の外部ネットワークや永続ストレージを提供しません。 Pickle ノードは、ホストによって中継される通信を使用します。そのため、ホストに復号化の許可が与えられるわけではありません。

委任されたユーザー キーは、ノード メモリ内で限られた期間使用されます。 [パブリック アーキテクチャの説明](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/README.md#structure) では、最大委任が 30 日と指定されています。デバイスのキーチェーンとサーバーの Nitro Enclave は、異なる保護層です。

### OAuth トークンはノード内で使用されます

[API 転送コード](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/enclave/src/api/forward.rs) は、アクティブな委任を確認し、OAuth レコードを開き、許可されたプロバイダー リクエストを準備します。利用記録が保存されたことを確認してリクエストを実行します。このパスは、トークンをモデルに渡す代わりに、認証されたリクエストを作成します。

ただし、**トークンを非表示にすることと、そのトークンで読み取られたデータを非表示にすることは別のことです**。 [egress ポリシー](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/docs/egress-policy.md) では、プロバイダーの応答を運用環境に返すことを個別に扱います。電子メールを読み取る権限が付与されている場合、モデルは電子メールの内容を処理できます。これはトークン保護とは別に評価する必要があります。

### Web サイトのパスワードがリリース後に異なる境界を越える

[Vault code](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/enclave/src/vault.rs) は、出力応答のパスワード、カード値、TOTP コードを選択するタイプを定義します。 [実際のリリース ハンドラー](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/enclave/src/api/release.rs) は、使用状況レコードが保存されたことを確認した後、値をシリアル化して返します。 **その時点で、パスワードとカード値は、処理を実行する worker が利用できる平文としてノードの外に出ます。** TOTP の場合、外に出るのはシードではなく計算済みのワンタイムコードです。

パブリック コードの `origin` チェックは、HTTPS オリジンの形式のみを検証します。コメントには、アドレスが保存されたログイン サイトと一致するかどうかを判断するのは呼び出し側の責任であると記載されています。したがって、Enclave コードだけでは、サイト制限やモデル結果のマスキングを確立できません。

これは実際の漏れの証拠ではありません。ただし、**モデル入力からの値の隠蔽**、**暗号化されたストレージ**、**ワーカー メモリでの平文の使用**は、別個のセキュリティ プロパティです。 「AI はパスワードを受け取らない」という記述を、「復号化されたパスワードは決して保護領域から出ない」に拡張してはなりません。

## 使用記録は何を保証しますか?

[公式使用履歴ガイド](https://pickle.com/help/privacy/activity) には、レコードが最初に保存され、保存に失敗した場合には資格情報は使用されないと記載されています。パブリック API コードでは、ログの永続性が確認された後に使用または解放が発生することも示します。暗号化された記録、署名、およびリンクは、変更または欠落を検出可能にすることを目的としています。

レコードは、ユーザーがタスクを意図したこと、または外部サイトでタスクが成功したことを保証しません。たとえば、レコードの保存後に実際のリクエストが失敗する可能性があります。支払い前の承認と金額の再確認は、[公式サービス説明](https://pickle.com/en) の実行ポリシーであり、資格情報の暗号化から自動的に続くプロパティではありません。

TOTP シードも委任されている場合、エージェントはコードを生成できます。これは、[保存されたログイン ガイド](https://www.pickle.com/help/connect/save-login) の便利な機能ですが、ユーザーがタスクごとに 二 番目の認証要素を個別に承認することとは異なります。委任範囲は、パスワードのみを委任する場合よりも広く判断する必要があります。

## 公開セキュリティプログラムの証明を検証する

[セキュア プログラム ドキュメント](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/secure-program/README.md) もデバイス側のセキュリティ プログラムを公開し、リリース署名と透過性ログの証明を検証するツールを提供します。以下の例では、**パブリック ファイルがそのリリース プルーフと一致するかどうか**をチェックします。実稼働ノードに接続したり、実際のパスワードを使用したりしません。

![公開プログラム JS とリリースプルーフは公式検証者への入力です。ファイルのハッシュ、署名、透明性ログの証明をチェックします。元の v42 は終了コード 0 を返します。 一 バイト追加されたファイルは、source_hash エラーと終了コード 1 を返します。運用サーバーとインストール済みアプリの検証は別途必要です。](/assets/diagrams/technical/ja-2026-11-13-pickle-ai-security-architecture.svg)

Git、curl、Rustup、およびネイティブ ビルド ツールが必要で、ソースと Rust の依存関係のダウンロードにはネットワークが使用されます。ベリファイアは、**macOS arm64 と Rust 1.100.0** 上の以下の固定されたコミットからビルドされました。リポジトリ ピン ツールのバージョン 1.98.1。ここで、`+1.100.0` は実行バージョンを明示的に選択します。

### `verify-example.sh`

```bash
# macOS·Linux 셸, Git·curl·Rustup 및 네이티브 빌드 도구가 필요합니다.
# 새 작업 폴더에서 실행합니다. 아래 검증은 계정 로그인이나 실제 비밀번호를 사용하지 않습니다.
git clone https://github.com/pickle-com/credential-enclave.git
cd credential-enclave
git checkout cff16a343bf5bb7953e5b65df6ab3600107e127d
rustup toolchain install 1.100.0 --profile minimal
cargo +1.100.0 build --locked -p credential-enclave-verify
curl --fail --location \
  https://github.com/pickle-com/credential-enclave/releases/download/secure-program-v42/secure-program.release.json \
  --output secure-program.release.json
./target/debug/credential-enclave-verify program \
  --source secure-program/secure-program.js \
  --release secure-program.release.json
```

元のファイルは終了コード 0 と次の出力を返しました。

```text
program release secure-program-v42: version 42, sha256 31e7fa7fb51f87781313b1f97b60ae3c7b69ff8f2fbcee7de12b7a0ed034d8e8, log index 3761959022: ok
```

また、変更されたファイルが拒否されることも確認してください。同じリポジトリ ディレクトリで以下のコマンドを実行します。

### `tamper-example.sh`

```bash
cp secure-program/secure-program.js changed-program.js
printf '\n' >> changed-program.js
./target/debug/credential-enclave-verify program \
  --source changed-program.js \
  --release secure-program.release.json
echo $?
```

一 つの改行バイトが追加されたファイルは、`source_hash` 不一致のため拒否され、コード 1 で終了しました。この結果は、公開プログラムのリリース証明に関するものです。実際のアプリで表示されるバージョンとハッシュが一致するかどうかの確認や、実稼働環境の Enclave の測定を検証するためのリモート構成証明の使用は行っていません。

## 安全性を判断する際に残される条件

[パブリック リポジトリの制限](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/README.md#what-it-does-not-guarantee) では、アプリの誠実さ、プロバイダー API コントラクト、リリース キーとログなどの信頼に関する前提条件について説明します。公開セキュリティプログラムを使っても、iOS アプリのバイナリ全体がそのプログラムを変更せずに実行するかどうかは別の問題です。ノードが委任を新しいリリースに転送できることは、特定のバージョンの保護が永久に固定されることを意味するものではありません。

デバイス側のセキュリティ プログラムの [更新制限](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/secure-program/README.md#limits) も重要です。ドキュメントには、オペレーターが署名し、公開ログに登録し、ロード要件を満たしている場合、新しいコードは事前の待ち時間なしでロードできると記載されています。 **リリース検証では、公開された署名付きファイルとの一致が確認されます。コードが無害であることを保証するものではありません。** 運用者への信頼は、その後のコードにも引き続き必要です。これは、悪意のあるリリースが実際に発生したという主張や観察ではありません。

| 何を確認するか | 決定に必要な質問 |
| --- | --- |
| 接続されたアカウント | どの読み取り/書き込みスコープが許可されますか?また、それらはプロバイダーで取り消すことができますか? |
| ボールトとTOTP | パスワードだけでなくワンタイムコードの生成も委任する必要がありますか? |
| 支払いと予約 | 実行前に条件や金額を確認し、結果を検証してもらえますか？ |
| セキュリティプログラムとノード | アプリのバージョンとハッシュ、公開リリースと実際のノード認証は一致していますか? |
| 会話と接続されたアカウントのデータ | 資格情報が非表示になっている場合でも、モデルはどのようなコンテンツを処理しますか? |

Pickle のセキュリティ設計の鍵は、**どの鍵が誰に委任され、どの境界で各値が復号化されて使用されるか**です。公的なコードは、これらの境界を検査するための証拠を提供します。ユーザーにとっての出発点は、実際の iPhone アプリ制御と委任されたアカウント アクセスを区別し、必要な権限のみを接続し、使用履歴とタスク結果の両方を確認することです。
