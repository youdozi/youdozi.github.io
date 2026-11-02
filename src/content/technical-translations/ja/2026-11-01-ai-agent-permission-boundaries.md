---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2026-11-01-ai-agent-permission-boundaries",
  "routeSlug": "2026-11-01-ai-agent-permission-boundaries",
  "kind": "post",
  "title": "AI エージェントの権限：予期しない操作の影響を抑える",
  "description": "AI エージェントのファイル・コマンド・ネットワーク・アカウント権限を分け、承認範囲と管理者バイパスの制御でリスクを抑える方法を、実行可能な認可例で説明します。",
  "categories": [
    "security"
  ],
  "tags": [
    "ai-agent",
    "permissions",
    "least-privilege",
    "sandbox",
    "approval",
    "security"
  ],
  "sourcePath": "src/content/posts/en/2026-11-01-ai-agent-permission-boundaries.md",
  "sourceSha256": "9610960800eb800a78e728fcc84d5cf2a790de1f6b051fe4a8ebb3dfdaec554b",
  "draftSha256": "808f3d73805a328856881fa809d55b5493c4cf4686d3eef67a7541ca82e26283",
  "manifestPath": ".pipeline/technical-translations/batch-132/manifest.json",
  "manifestSha256": "9061c67686c9ea3bd8d21799f4c265ee716fee50940f1b6fc38c28a67de01dee",
  "publishedAt": "2026-11-02T03:04:44.245Z",
  "updatedAt": "2026-11-02T03:04:44.245Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 132,
    "approvedAt": "2026-11-02T03:04:44.245Z",
    "basis": "User requested completing missing multilingual technical posts, review, verification and deployment, then instructed continuing the next task on 2026-11-02, with standing blog PR merge/publication authorization. Human approval denotes user publication authorization; linguistic review is AI, not human/native review."
  }
}
---

**AI エージェントの予期しない動作による事故を減らすには、実行可能な操作とアクセスできるリソースを制限し、影響の大きい操作に明確な承認境界を設けます。** ファイルの誤編集や依頼の過大な解釈が、即座に本番データの削除、外部送信、保護ルールの回避につながっては困ります。権限設計ですべての誤りはなくせませんが、影響が及ぶ範囲は狭められます。

ここでいう権限には、エージェントに見えるツールの一覧だけでなく、実行環境と外部サービスのアカウントも含みます。[OWASP の Excessive Agency の説明](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/)は、過剰な機能、権限、自律性を主要なリスクに挙げ、最小権限と、影響の大きい操作に対する承認を推奨しています。

## 「タスクを完了する」が広い権限に変わるとき

次の仮想的な設計場面を考えます。ユーザーが公開を依頼し、CI は通過しましたが、リポジトリでは別途 PR 承認が必要です。エージェントがこの要件を単なる障害と解釈して管理者権限でマージすると、公開と保護ルールの例外扱いが混同されます。

問いは二つあります。**この成果物を公開する権限がエージェントにあるか、そして保護ルールを例外扱いする権限もあるかです。** 通常の公開依頼を管理者バイパスの許可へ自動的に拡大すると、予期しない変更を招くことがあります。GitHub のブランチ保護は設定によって管理者やバイパス権限を持つ主体を対象外にできるため、保護ルールと、実行アカウントがそれを回避できるかの両方を確認します。[GitHub の保護ブランチとバイパス設定](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)

権限が拒否された後、別のコマンド、API、主体で同じ効果を試みてよいかは、ポリシーに従って判断します。承認不足や権限不足で止められた操作は、ポリシーの待機手順や例外手順に従います。一時的なサービス障害への再試行と、権限拒否への対応は区別してください。

## 指示と強制される制御は役割が異なる

`AGENTS.md` やプロンプトにある「本番データベースを変更しない」といった指示は、範囲を伝えます。データベース接続に使う主体に読み取り権限しか与えなければ、生成された書き込み要求をデータベース側でも拒否できます。指示はモデルの行動を導き、実行環境の制御とサービス側の認可は、起こせる影響を制限します。

| 層 | 制限する対象 | 設計例 |
| --- | --- | --- |
| タスクの指示 | 範囲と停止条件 | 下書きを許可し、公開と管理者バイパスを別の操作にする |
| 実行環境 | ファイル、プロセス、ネットワークアクセス | 作業フォルダーのみ書き込み可にし、本番の秘密情報を置かず、必要な宛先だけに接続する |
| ツールゲートウェイ | 操作と引数の組み合わせ | `publish` でサイトと成果物ハッシュを確認し、任意のコマンド実行を公開しない |
| 外部サービス | 認証情報が実際に持つ権限 | リポジトリ、データベース、クラスターに範囲を絞ったサービスの実行主体と保護ルールを使う |

エージェントのプロセスが管理者トークンを持ち、API を直接呼べるままなら、ゲートウェイのほかに経路が残ります。一案は、制限されたサービスに実行用の認証情報を保持し、エージェントからそのサービスへ構造化された要求を送る設計です。エージェントがポリシーファイルや承認ストアを変更できないことも必要です。

## コマンド名だけでなく効果を制限する

「テストコマンド」を許すルールだけでは、実行環境の安全は確保できません。テスト、ビルド、依存関係のインストールは、リポジトリやパッケージのコードを実行できます。信頼できないコードを実行するワークスペースに本番の認証情報を注入せず、必要なファイル、ネットワークアクセス、リソースだけを与えてください。コンテナーを使っていても、機微なホストパスや Docker ソケットをマウントしているなら、隔離境界を見直します。

読み取りにもリソースとデータの境界が必要です。秘密情報を読んで外部へ送信したり、機微なデータをクエリ文字列に含めたりすれば、元のデータを変更せずとも事故になります。外部文書、Web ページ、ツール応答に埋め込まれた指示は、タスクの承認ではありません。[OWASP のプロンプトインジェクションに関する説明](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)は、外部コンテンツ経由の間接インジェクションを扱っています。

GitHub Actions ワークフローでは、必要なトークン権限だけを宣言できます。次はワークフロー設定の一部です。

```yaml
permissions:
  contents: read
```

これは対象の `GITHUB_TOKEN` を制御します。未指定の権限は `none` になりますが、別途渡された PAT、クラウドキー、データベース認証情報は制限しません。エージェントランナーに実際に渡される認証情報も確認してください。[GitHub Actions の権限構文](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#permissions)

Kubernetes では、通常のタスクの実行主体が持つ `escalate`、`bind`、`impersonate` 権限を個別に確認します。他の権限を取得したり、別の主体として操作したりできる場合があるためです。[Kubernetes RBAC の指針](https://kubernetes.io/docs/concepts/security/rbac-good-practices/)

## 承認を成果物と宛先に結び付ける

「続行しますか？」とだけ示さず、操作、対象、変更案を確認できるようにします。公開承認には、サイト ID、確認済み成果物のハッシュ、実行主体、有効期限、一回限りの承認 ID を結び付けられます。承認後に記事やデプロイイメージが変わったら、新しい成果物が承認範囲内にあるかを判断します。

すべての読み取りや下書き編集に個別承認が必要なわけではありません。承認済みの範囲内では作業を続け、その範囲を越えるか、ポリシー上追加承認が必要な効果に達した時点で止めます。これにより、公開、削除、外部送信、管理者例外の境界を保ちつつ、承認疲れを減らせます。管理者例外が本当に必要な運用手順は、通常のランナーとは別の実行主体、権限、監査経路を使うべきです。

## 実行可能な例：承認はポリシー外の操作を許可できない

以下は、**外部への効果がない単一プロセスの認可例**です。`repo:demo` などは事前定義された論理リソース ID で、実際のパスや URL ではありません。ポリシーは `read` と下書きの `edit` を許可し、`publish` には同じ主体と要求に対する有効な承認を求めます。管理者バイパスはポリシーに存在しないため、承認オブジェクトがあっても拒否されます。

![ポリシー範囲を確認し、承認の有無、実行主体と成果物の一致、有効期限、再利用を検証してから、承認が必要な公開を許可する](/assets/diagrams/technical/ja-2026-11-01-ai-agent-permission-boundaries.svg)

図は、承認が必要な `publish` の経路を示しています。コードが `read` と下書きの `edit` を即座に許可する分岐は省略しています。どの検査でも停止すれば、後続の段階と実際の公開は行われません。

コードを `permission_gate.py` として保存し、Python 3.10 以降で `python3 permission_gate.py` を実行します。ネットワークアクセス、認証情報、追加パッケージは不要です。

```python
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Request:
    action: str
    target: str
    artifact: str


@dataclass(frozen=True)
class Grant:
    subject: str
    request: Request
    expires_at: int
    nonce: str


class Gate:
    def __init__(self):
        self.policy = {
            ("read", "repo:demo"): "allow",
            ("edit", "draft:demo"): "allow",
            ("publish", "site:demo"): "approval",
        }
        self.used = set()

    def check(self, subject, request, grant, now):
        mode = self.policy.get((request.action, request.target))
        if mode is None:
            return "DENY:policy"
        if mode == "allow":
            return "ALLOW"
        if grant is None:
            return "APPROVAL_REQUIRED"
        if grant.subject != subject or grant.request != request:
            return "DENY:scope"
        if now >= grant.expires_at:
            return "DENY:expired"
        if grant.nonce in self.used:
            return "DENY:replay"
        self.used.add(grant.nonce)
        return "ALLOW"


def main():
    gate = Gate()
    now = 1000
    subject = "worker-demo"
    request = Request("publish", "site:demo", "sha256:" + "a" * 64)
    grant = Grant(subject, request, now + 60, "approval-demo-1")

    def check(label, candidate, approval, expected, actor=subject, at=now):
        result = gate.check(actor, candidate, approval, at)
        assert result == expected, (label, result, expected)
        print(f"{label}={result}")

    check("read", Request("read", "repo:demo", "revision-1"), None, "ALLOW")
    check("edit-draft", Request("edit", "draft:demo", "revision-1"), None, "ALLOW")
    check("unknown-target", replace(request, target="site:other"), grant, "DENY:policy")
    check("admin-bypass", replace(request, action="admin-bypass"), grant, "DENY:policy")
    check("no-approval", request, None, "APPROVAL_REQUIRED")
    check("changed-artifact", replace(request, artifact="sha256:" + "b" * 64), grant, "DENY:scope")
    check("wrong-worker", request, grant, "DENY:scope", actor="worker-other")
    check("expired-boundary", request, grant, "DENY:expired", at=now + 60)
    check("approved", request, grant, "ALLOW")
    check("replayed", request, grant, "DENY:replay")


if __name__ == "__main__":
    main()
```

この出力は Python 3.13.0 で生成されました。以下の合成シナリオ 10 件の戻り値を確認しています。

```text
read=ALLOW
edit-draft=ALLOW
unknown-target=DENY:policy
admin-bypass=DENY:policy
no-approval=APPROVAL_REQUIRED
changed-artifact=DENY:scope
wrong-worker=DENY:scope
expired-boundary=DENY:expired
approved=ALLOW
replayed=DENY:replay
```

`Grant` は、承認サービスが発行し認証した情報を前提にしています。この例では、承認や実行主体、権限、署名、入力スキーマを検証していません。dataclass の型ヒントは実行時検証の代わりにはなりません。モデルが生成した JSON を、そのまま受理する `Grant` に変換しないでください。`now=1000`、60 秒、ハッシュ、承認 ID は合成されたデモ用の値で、本番向けの推奨値ではありません。

実際のエグゼキューターは承認ストアから承認を読み込み、成果物ハッシュを自ら計算する必要があります。エージェントが渡したハッシュだけを比較すると、実際の内容と異なる値を渡せてしまいます。信頼できる実行コンテキストからポリシー、時刻、実行主体、対象を検証し、この関数を飛ばして外部 API を直接呼べないよう、実行経路と認証情報を制限します。

`used` 集合はプロセス内のメモリなので、再起動後や複数ランナー間のリプレイを防ぎません。実際の実行サービスには、承認のアトミックな消費、取り消し、実行直前のポリシーと対象の再検証、操作の冪等性が必要です。承認を消費した後に実行が失敗した場合の再試行でも、同じ操作 ID と実際の実行結果を使う必要があります。このコードは `ALLOW` を返すだけで、公開 API は呼びません。

## 導入時に最初に確認すること

アクセスできるファイル、トークン、実行主体と、エージェントが実際に呼べる API を洗い出します。明示的に接続されたツールだけでなく、シェルの環境変数、ホームディレクトリの認証情報、ネットワーク経路も確認します。読み取りアクセスと隔離した下書き作業から始め、影響の大きい効果には範囲を絞ったツールを追加します。

未承認の公開、承認後の成果物変更、有効期限切れ、再利用、異なる実行主体、未知のリソース、管理者バイパス要求が拒否されることをテストします。外部文書が権限拡大を求めても同じ制御が働くことを検証します。エージェントがポリシーを変更したり、実行サービスのトークンを直接読んだりできる経路は閉じてください。

監査ログでは要求 ID、実行主体、対象、成果物ハッシュ、適用ポリシー、承認 ID、実行結果を結び付け、トークンと機微な内容は記録しないようにします。異常な動作が見えたら、新規作業の受け付けを止め、認証情報を失効させて影響の拡大を抑えます。失効しても送信済みデータや完了済みの外部変更は元に戻らないため、実行制御とともに復旧手順も用意してください。

コード、テスト、デプロイ、可観測性、データベースの証拠を結ぶ運用フローは、[AI エージェントの運用](/en/posts/2026-10-31-ai-agent-operations/)を参照してください。
