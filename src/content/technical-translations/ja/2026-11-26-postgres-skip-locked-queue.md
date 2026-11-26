---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2026-11-26-postgres-skip-locked-queue",
  "routeSlug": "2026-11-26-postgres-skip-locked-queue",
  "kind": "post",
  "title": "PostgreSQL の SKIP LOCKED で作るジョブキュー：ワーカーが途中で停止したら？",
  "description": "二つのセッションでジョブを取得し、ロールバックした場合とコミット後に接続を閉じた場合に、どちらのジョブが再取得できるかを確かめます。",
  "categories": [
    "architecture"
  ],
  "tags": [
    "postgresql",
    "sql",
    "job-queue"
  ],
  "sourcePath": "src/content/posts/en/2026-11-26-postgres-skip-locked-queue.md",
  "sourceSha256": "47e798b84fdcc29b4f58d8c6e35bed1ea56c2145f4c9767e14b18888eee939d8",
  "draftSha256": "929544ccdf90a41e1aaba9a32f26d59995985a4a4b3775a62e577499a2c24714",
  "manifestPath": ".pipeline/technical-translations/batch-2099/manifest.json",
  "manifestSha256": "80bcd0f1141bc18b7aae220d9c061126e4788f8b902834069f1f0dd0eeb7984d",
  "publishedAt": "2026-11-26T08:25:16.518Z",
  "updatedAt": "2026-11-26T08:25:16.518Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 202,
    "approvedAt": "2026-11-26T08:25:16.518Z",
    "basis": "In item 99 the owner authorized publication of the PostgreSQL SKIP LOCKED job queue article in the eight existing blog languages."
  }
}
---

A が先頭のジョブをロックしている間も、B は `SKIP LOCKED` で次のジョブを取得できます。ただし、B が取得をコミットした直後に停止すると、そのジョブは `running` のままです。行ロックで仕事を分担できても、いつ別のワーカーに引き継げるかはキュー側で記録する必要があります。

## 各セッションでジョブを一件ずつ取得する

空の実習用データベースにセッション A を接続し、自動コミットで次の準備を行います。B も同じデータベースに接続します。両方とも既定の分離レベル `READ COMMITTED` を使います。

```sql
CREATE TABLE queue_demo (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  status text NOT NULL DEFAULT 'pending'
);
INSERT INTO queue_demo (status) VALUES ('pending'), ('pending');
```

まず A で次のブロックを実行し、トランザクションを開いたままにします。続いて B でも同じブロックを実行します。両方の戻り値を確認するまでコミットしないでください。

```sql
BEGIN;
WITH next_job AS (
  SELECT id FROM queue_demo
  WHERE status = 'pending'
  ORDER BY id
  LIMIT 1
  FOR UPDATE SKIP LOCKED
)
UPDATE queue_demo AS job
SET status = 'running'
FROM next_job
WHERE job.id = next_job.id
RETURNING job.id, job.status;
```

![A がジョブ 1 をロックすると、B はそれを飛ばしてジョブ 2 を取得します。B がコミットし、A がロールバックすると、前者のジョブは待機に戻り、後者は実行中のままです。](/assets/diagrams/technical/ja-2026-11-26-postgres-skip-locked-queue.svg)

`ORDER BY id` が決めるのは候補を調べる順序です。B は先にコミットできるので、完了順は前後します。PostgreSQL のマニュアルでも、複数のコンシューマーがキューテーブルの行ロックを取り合う場面での利用を挙げています。 [PostgreSQL の SELECT のロック句](https://www.postgresql.org/docs/current/sql-select.html#SQL-FOR-UPDATE-SHARE)

## 取得をコミットしてから接続を閉じる

B で `COMMIT;`、次に A で `ROLLBACK;` を実行します。B の接続を閉じ、A から状態を確認します。

```sql
SELECT id, status FROM queue_demo ORDER BY id;
```

ローカルに隔離した PostgreSQL 17.12 に二つの接続を開いて実行しました。取得時に A は `(1, running)`、B は `(2, running)` を返しました。最後の問い合わせの結果は次のとおりです。

```text
id | status
1  | pending
2  | running
```

A のロールバックは状態変更も取り消します。B のコミットはロックを解放し、変更を確定します。次のワーカーの検索条件は `pending` なので、ジョブ 2 は引き続き対象外です。

## 期限を過ぎたジョブを引き継ぐ

運用時は、取得用の短いトランザクションで期限と新しい試行 ID を記録し、試行回数を増やします。実作業はコミット後に行います。復旧用ワーカーは期限切れの実行中ジョブをロックして状態を再確認し、試行回数に余裕があれば、新しい試行 ID と期限で引き継ぎます。上限に達したら失敗として記録し、調査対象にします。

遅れて戻ったワーカーが完了を記録する条件は、ジョブ ID、実行中の状態、自分の試行 ID がすべて一致することです。引き継ぎ後に更新される行はありません。ただし、メール送信後、完了を記録する前に停止することもあります。同じメールの再試行には共通の冪等性キーを使い、メールサービス側で重複送信を防ぎます。引き継ぎで試行 ID が変わっても、送信キーは維持します。
