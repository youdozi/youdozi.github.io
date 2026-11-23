---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2026-11-23-orca-bot-guide",
  "routeSlug": "2026-11-23-orca-bot-guide",
  "kind": "post",
  "title": "Orca Botの使い方：ブログ用Botの作成から作業・自動化の確認まで",
  "description": "Orca Botに最初の仕事を依頼し、メモリと作業を確認して定期実行を設定します。",
  "categories": [
    "util"
  ],
  "tags": [
    "orca",
    "ai-agent",
    "automation",
    "developer-tools"
  ],
  "sourcePath": "src/content/posts/en/2026-11-23-orca-bot-guide.md",
  "sourceSha256": "00b9ff415bf1d0fddd82a856377211655f16ca6c010e833f68ed5639ee6d5108",
  "draftSha256": "48d563ea2b5eb2b23f0dd49599026c7aac4f08347a8452ff4357175894e84432",
  "manifestPath": ".pipeline/technical-translations/batch-186/manifest.json",
  "manifestSha256": "afce5bc713412c02f130b1062bfe7d5b9872d9d301b703639a476301c673d0af",
  "publishedAt": "2026-11-23T05:18:32.011Z",
  "updatedAt": "2026-11-23T05:18:32.011Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 186,
    "approvedAt": "2026-11-23T05:18:32.011Z",
    "basis": "Owner explicitly requested publication of the Orca Bot guide in all eight supported languages; translations were self-reviewed, not independently or natively reviewed."
  }
}
---

**Orca Botを初めて作るときは、繰り返し作業を予約する前に、結果を確認できる仕事を一つ依頼しましょう。** 例えば短い技術メモを渡し、ブログのタイトルと構成を求めます。結果が希望する形式なら、Botの役割を調整して繰り返し作業を追加します。この記事ではブログの下書きを準備するBotで手順を紹介します。

Orca Botは名前、目的、メモリを持つ作業単位です。実行するコンピューターとClaude CodeやCodexなどのエージェントを選びます。エージェントはそのコンピューターにインストールしてログインしておきます。最初の練習はOrca内で完結します。Slack・GitHub・LinearからBotを呼び出す場合や、それらのサービスのイベントで実行する場合は必要な接続を追加します。[Orca Botsクイックスタート](https://orca.dev/docs/bots) · [Botコネクター](https://orca.dev/docs/bots/connectors)

![Botを作成して最初の仕事を依頼し、結果を確認します。必要ならNeeds youで判断します。繰り返し作業には時刻またはイベントを設定し、実行履歴を確認します。](/assets/diagrams/technical/ja-2026-11-23-orca-bot-guide.svg)

## Botを作成して最初の依頼を送る

Orcaのサイドバーの **Bots** で **+ → New bot → Start from scratch** を選びます。名前を決め、**Who it is and what it does** に役割を一文で書きます。例の名前は `Blog Draft`、目的は「開発メモを技術ブログの下書きにまとめる」です。名前の下で実行コンピューターとエージェントを確認し、**Create** を選びます。サイドバーにBotsがない場合は **Settings → Bots → Enable bots** を確認します。[Botの作成](https://orca.dev/docs/bots)

Botのチャットに、次のように入力資料と希望する形式を一緒に渡します。このメモは練習用の架空の資料です。

```text
Prepare a technical blog draft from the following practice note.

Note
- A Java service calls an external API.
- Tests checked a successful response and a 404 response.
- Production latency was not measured.

Suggest one title, one introductory paragraph, and three headings.
Do not add versions or performance figures absent from the note.
At the end, list anything that needs checking before writing the body.
Show the result in this chat.
```

結果を受け取ったら、「404応答を確認した」という範囲が残っているか確認します。バージョンやスループットを新たに主張していれば、その部分を削除するか根拠を求めます。最初の依頼の成功条件は、メモに基づいたタイトル・導入・見出しが得られることであり、すぐに公開できる原稿ができることではありません。

## 今後のチャットで使うルールと現在の作業を分ける

| 確認する場所 | 適した内容 | ブログBotの例 |
| --- | --- | --- |
| `SOUL.md` | 継続して適用する役割と作業方法 | 公式文書で根拠を確認し、公開には別の依頼を待つ |
| `MEMORY.md` | 今後のチャットでも参照する事実と好み | 読者はJava開発者で、実行できる例を好む |
| **Home** の作業項目 | 現在の進捗、添付結果、承認待ちの判断 | 新しい原稿がレビューを待っている |

二つのMarkdownファイルはBotフォルダーにあります。「今後の例では実際に実行した結果と期待結果を区別して」のような継続ルールを伝え、次の仕事でも守られるか確認できます。現在の仕事の完了を確認するにはBotの作業項目を開きます。判断が必要なら **Needs you** で質問の対象と結果を確認して回答します。[Orca Botの使い方](https://orca.dev/docs/bots) · [Botのメモリとアクセス](https://orca.dev/docs/bots/security)

リポジトリのコード変更を依頼すると、Botは別のGit worktreeの作業者に引き継ぐことができます。サイドバーで作業者のworkspaceを開いてファイルとテストを確認し、PRが作られたら実際の変更内容を確認します。[Botの作業者](https://orca.dev/docs/bots) · [Orca worktreeガイド](../2026-11-12-orca-worktree-guide/)

## 繰り返し作業の実行条件と結果の保存先を決める

最初の仕事が期待どおりなら、Botのチャットで次のように依頼します。この例では公開文書を読み、記事の題材だけを集めます。

```text
Every Monday at 9:00 a.m. Korea time, select up to three technical
article ideas from official Spring Boot releases announced in the
previous seven days. For each candidate, include the announcement date,
official link, and a question to explore in an exercise.
If there were no announcements, say so.
Make the result available to me in Orca; do not publish it to the blog.
Also tell me which conversation the automation will leave its result in.
```

自動化が作成されたら、Botパネルで **タイムゾーン・実行条件・結果の受け取り先** を確認します。時刻ではなく新しいGitHub PRなどのイベントに反応させる場合は、コネクターが接続済みでそのイベントをサポートしているか先に確認します。Botを実行するコンピューターがスリープ中またはオフラインなら予定どおりすぐには作業できないため、最初の結果を自動化の実行履歴で確認します。[Orca自動化](https://orca.dev/docs/bots) · [Orcaコネクター](https://orca.dev/docs/bots/connectors)

CLIをインストールしたmacOSでは、次のコマンドでBot名と利用可能なイベントを確認できます。二行目の名前は自分のBot名に置き換えてください。

```sh
orca bot list
orca automations trigger-options --bot 'Blog Draft'
```

執筆環境の **Orca CLI 1.4.271** で既存のBotを使い、二つの読み取り専用コマンドを確認しました。GitHub接続のないBotの結果には、GitHubイベントではそのBotを起動できないと表示されました。例の名前とメモは架空で、この記事のために新しいBotや自動化を作成・実行していません。使用バージョンに合ったCLIガイドは `orca skills get orca-cli --reference bots` で読めます。
