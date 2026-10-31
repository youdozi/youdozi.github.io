---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2026-10-30-jdk-emudhra-truststore",
  "routeSlug": "2026-10-30-jdk-emudhra-truststore",
  "kind": "post",
  "title": "JDKのeMudhra証明書：稼働JVMとトラストストアを確認する",
  "description": "Oracle、Temurin、UbuntuのeMudhra信頼取り消し方針を区別します。バージョン表示や別名だけで判定せず、JSSEのストア選択と証明書フィンガープリントを調べます。",
  "categories": [
    "security",
    "jdk"
  ],
  "tags": [
    "java",
    "jdk",
    "emudhra",
    "tls",
    "security"
  ],
  "sourcePath": "src/content/posts/en/2026-10-30-jdk-emudhra-truststore.md",
  "sourceSha256": "abdc8cf489bcb34919f036e665475c6dd2f939c07f1a4c42ffe10c86e32761e3",
  "draftSha256": "688f51d8cf3a1f206f312735afd25e3208de4225df44716a19cae6c44d56e6ca",
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
JDKのeMudhra問題への対処には、**アプリケーションを実行するJDKと、実際に使用するトラストストアの両方の確認**が必要です。[Oracleの通知](https://ops.java/emudhra/)と[Temurinの通知](https://adoptium.net/news/2026/10/temurin-october-2026-emudhra/)は、更新された配布物と該当CAの信頼取り消しを説明していますが、実装は異なります。ブラウザーの保護やホストJDKの更新では、コンテナや別JVMへの適用を確定できません。

## 期限切れのサーバー証明書を取り込めば解決しますか？

この事案は、通常のサーバー証明書の期限切れとは異なります。eMudhraの中間CA秘密鍵の侵害により、偽造証明書を信頼し得る経路が生じたため、該当する信頼の削除か、供給元が推奨する保護が必要です。[OracleのCVE-2026-91403セキュリティアラート](https://www.oracle.com/security-alerts/alert-cve-2026-91403.html)は、影響製品とパッチ方針を示しています。Oracleの製品・バージョン表を別のディストリビューションへ無差別に適用しないでください。

`PKIX path building failed`は、この事案に固有の診断ではありません。不完全なサーバーチェーン、誤ったトラストストア、プライベートCA、供給元による信頼変更を区別します。エラーを消すためだけに検証を無効化したり、未検証のCAを取り込んだりすると、保護を損ねる可能性があります。

## 供給元ごとのアドバイザリを個別に読む

以下は、2026年10月30日に確認した通知の内容です。デプロイ時には、製品、OS、完全なビルド、最新の追加情報を再確認します。

| 供給元 | 確認すべき違い |
| --- | --- |
| [Oracle JDK](https://ops.java/emudhra/) | 該当ルートを削除する更新と、更新が遅れる場合の別途の暫定緩和策 |
| [Eclipse Temurin](https://adoptium.net/news/2026/10/temurin-october-2026-emudhra/) | MozillaのCAデータを使用し、`emSign ECC Root CA - G3`と`AAA Certificate Services`の信頼を取り消します。修正済みビルドには21.0.13+9と17.0.21+9が含まれます |
| [Ubuntu OpenJDK](https://ubuntu.com/blog/emudhra-ca-compromise-fixes-available) | システムCAストアとの統合があります。現在の同期不具合により、`ca-certificates`更新後にJavaストアへの追加の手動対応が必要です |

Temurinの通知は、`emSign Root CA - G1`が存在するだけでは対処失敗と判断できないと説明しています。汎用の`CheckCerts`ルート一覧を共通の合格基準として扱うと、ディストリビューションを誤判定する可能性があります。ルートの別名、名前、件数だけでは保護を保証できません。

## 現在のJVMの既定JSSE信頼情報を読む

![JVM識別情報を読み、既定のJSSE TrustManagerを初期化し、名前の候補とSHA-256フィンガープリントを収集します](/assets/diagrams/technical/ja-2026-10-30-jdk-emudhra-truststore.svg)

図は以下の読み取り専用収集コードに対応しています。既定の`TrustManagerFactory`を初期化し、CA名を検索します。名前の一致は、フィンガープリントを供給元の方針と比較する出発点であり、脆弱・安全の判定ではありません。既定トラストマネージャーの初期化に失敗すると、例外で終了します。

JDK 17以降で、新しいディレクトリにファイルを保存します。公開された[TrustManagerFactory](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/javax/net/ssl/TrustManagerFactory.html)と[X509TrustManager](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/javax/net/ssl/X509TrustManager.html)のAPIだけを使用します。ファイル変更、ネットワークリクエスト送信、証明書の追加・削除、TLS検証の迂回は行いません。

### `TrustInventory.java`

```java
import java.security.KeyStore;
import java.security.MessageDigest;
import java.security.cert.X509Certificate;
import java.util.HexFormat;
import java.util.Locale;
import javax.net.ssl.TrustManager;
import javax.net.ssl.TrustManagerFactory;
import javax.net.ssl.X509TrustManager;

public class TrustInventory {
    public static void main(String[] args) throws Exception {
        System.out.println("java.version=" + System.getProperty("java.version"));
        System.out.println("java.vendor=" + System.getProperty("java.vendor"));
        System.out.println("java.home=" + System.getProperty("java.home"));
        System.out.println("configuredTrustStore=" +
            System.getProperty("javax.net.ssl.trustStore", "<default JSSE lookup>"));
        TrustManagerFactory factory = TrustManagerFactory.getInstance(
            TrustManagerFactory.getDefaultAlgorithm());
        factory.init((KeyStore) null);
        System.out.println("trustManagerProvider=" + factory.getProvider().getName());
        MessageDigest sha256 = MessageDigest.getInstance("SHA-256");
        int issuers = 0;
        int matches = 0;
        for (TrustManager manager : factory.getTrustManagers()) {
            if (!(manager instanceof X509TrustManager x509)) continue;
            for (X509Certificate cert : x509.getAcceptedIssuers()) {
                issuers++;
                String subject = cert.getSubjectX500Principal().getName();
                String lower = subject.toLowerCase(Locale.ROOT);
                if (lower.contains("emsign") || lower.contains("aaa certificate services")) {
                    String fingerprint = HexFormat.of().withUpperCase()
                        .formatHex(sha256.digest(cert.getEncoded()));
                    System.out.println("candidate=" + subject + "\tSHA256=" + fingerprint);
                    matches++;
                }
            }
        }
        System.out.println("acceptedIssuers=" + issuers);
        System.out.println("nameMatches=" + matches);
        System.out.println("assessment=inventory-only; no validation verdict");
    }
}
```

```sh
javac --release 17 TrustInventory.java
java TrustInventory
```

ローカルのJDK確認では、プログラムをコンパイルし、既定の一覧出力を確認しました。別途生成したテストCAストアでも、名前の候補とSHA-256フィンガープリント、無関係な名前のストア、空のストアを確認しました。これらのテストCAは実際のeMudhra証明書ではありません。実行の成功は、本番JVMの保護を保証しません。

報告される`java.home`は、**今起動したJVM**のものです。`configuredTrustStore`が`<default JSSE lookup>`なら、システムプロパティが未指定という意味であり、ストアが見つからなかったという意味ではありません。出力にトラストストアのパスワードは含まれません。

## 既定の探索とアプリケーション設定は異なる場合がある

[SunJSSEリファレンス](https://docs.oracle.com/en/java/javase/25/security/java-secure-socket-extension-jsse-reference-guide.html)は、明示的な`javax.net.ssl.trustStore`と、既定の`jssecacerts`/`cacerts`探索を区別しています。このプログラムは、新しいJVMでその既定の初期化経路を読み取ります。アプリケーションが作成した`SSLContext`/`TrustManager`インスタンス、フレームワーク設定、ネイティブTLSライブラリは自動検出しません。

候補がゼロでも安全の判定にはなりません。プロバイダーやビルドによって、存在しないストアパスは別のストアへフォールバックしたり、空の一覧になったり、初期化に失敗したりします。ローカルのJDK確認では、既定ストアへのフォールバックとパスワード不一致による失敗を観測しました。他の名前や検証経路も見逃す可能性があります。一方、名前が一覧にあっても、TLS検証でそのチェーンが必ず受け入れられるとは示せません。このコードは、ブロックリスト、失効、証明書パスの検証を実行しません。

## 更新後に通常の接続と拒否を確認する

1. 実際のサービスのJDK供給元、完全なビルド、実行ファイル、JVM起動オプション、イメージダイジェストを特定し、独自トラストストアやアプリケーション固有のTLS設定も含めます。
2. 供給元の修正済みビルドをデプロイします。別のストアを維持する場合は、その内容を供給元の方針と比較します。手動削除の前に、バックアップ、フィンガープリント、接続への影響を確認します。Ubuntuの現在の同期不具合では、`ca-certificates`更新後に追加の[JavaルートCAストア更新手順](https://ubuntu.com/blog/emudhra-ca-compromise-fixes-available#updating-the-java-root-ca-store)が必要です。ローカルで追加したCAを保全し、再生成前に再追加の準備をしてください。
3. すべてのJVMとレプリカを置き換えるか再起動します。あるインストール先の`cacerts`を変更しても、別のJDKや既に稼働中のプロセスは自動更新されません。
4. 通常のHTTPS接続の成功と、供給元が指定する影響チェーンの拒否の両方を検証します。TLSの結果で署名付きJARの検証を代用することはできません。

この記事では、外部テストホストへの接続や、実際の影響チェーンの拒否を検証していません。収集コードの出力だけを根拠に、これらの確認を完了と記録しないでください。本番では、証明書の置き換え計画とともに[供給元別の検証手順](https://adoptium.net/news/2026/10/temurin-october-2026-emudhra/)に従ってください。

GitLabの正規表現RCEは、この証明書問題とは別です。GitLabのアップグレードについては、[CVE-2026-110264対応ガイド](/en/posts/2026-10-30-gitlab2shell-cve-2026-110264/)を参照してください。
