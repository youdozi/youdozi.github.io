---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2026-11-27-postgres-queue-partial-index",
  "routeSlug": "2026-11-27-postgres-queue-partial-index",
  "kind": "post",
  "title": "PostgreSQL のジョブキューに完了行がたまると、部分インデックスはどれほど効くのか",
  "description": "待機中の行だけにインデックスを作り、古いジョブを取り出す実行計画とバッファの使用状況を比較します。",
  "categories": [
    "architecture"
  ],
  "tags": [
    "postgresql",
    "sql",
    "job-queue"
  ],
  "sourcePath": "src/content/posts/en/2026-11-27-postgres-queue-partial-index.md",
  "sourceSha256": "c12611eba6e452bb96b402836ce6045313c18b44afdbb87a83463f72acf52e81",
  "draftSha256": "06848500e9b4bddd8e20d94a461438e6a08ce0d42803dff4642627c4c58462b1",
  "manifestPath": ".pipeline/technical-translations/batch-2122/manifest.json",
  "manifestSha256": "b6027f307cdb9cd0167371fbdd41e3e32de919d85d4e12d93fff462a3b8c1fc1",
  "publishedAt": "2026-11-27T05:22:32.895Z",
  "updatedAt": "2026-11-27T05:22:32.895Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 206,
    "approvedAt": "2026-11-27T05:22:32.895Z",
    "basis": "Explicit publication request for all nine editions of the PostgreSQL pending queue partial index experiment."
  }
}
---

ジョブ 300,000 件のうち 297,000 件が完了し、待機中は 3,000 件です。古い順に 20 件の待機ジョブを取得するとき、待機行だけを作成時刻と ID の順に格納した部分インデックスを作ると、実行計画からソートが消えました。

## 同じクエリを二度実行する

空のデータベースで以下の SQL を順に実行します。`ANALYZE` でテーブルの統計情報を更新します。二つのクエリの間で作るインデックスには、`status = 'pending'` を満たす行だけが入ります。 [部分インデックス](https://www.postgresql.org/docs/19/indexes-partial.html)

```sql
CREATE TABLE jobs (id bigserial PRIMARY KEY, status text NOT NULL, created_at timestamptz NOT NULL);
INSERT INTO jobs (status, created_at)
SELECT CASE WHEN n % 100 = 0 THEN 'pending' ELSE 'done' END,
       timestamptz '2026-01-01 00:00:00+00' + n * interval '1 second'
FROM generate_series(1, 300000) AS g(n);
ANALYZE jobs;

EXPLAIN (ANALYZE, BUFFERS) SELECT id FROM jobs WHERE status = 'pending' ORDER BY created_at, id LIMIT 20;

CREATE INDEX jobs_pending_created_idx ON jobs (created_at, id) WHERE status = 'pending';

EXPLAIN (ANALYZE, BUFFERS) SELECT id FROM jobs WHERE status = 'pending' ORDER BY created_at, id LIMIT 20;
```

## 実行計画はどう変わったか

![作成前: Seq Scan → Sort → Limit. 部分インデックス作成後: Index Only Scan → Limit.](/assets/diagrams/technical/ja-2026-11-27-postgres-queue-partial-index.svg)

最初の計画はテーブル全体を走査し、完了したジョブを除いてから候補をソートします。インデックスからは待機ジョブを `(created_at, id)` 順に読めるため、次の計画では `LIMIT 20` に達したところで走査を打ち切れます。

| 実行計画 | 作成前 | 部分インデックス作成後 |
| --- | --- | --- |
| 最上位ノードの共有バッファ | `shared hit=1911` | `shared hit=1 read=2` |
| 走査ノードの内訳 | `Rows Removed by Filter=297000` | `Heap Fetches=0` |
| 返却行数 | 20 | 20 |

隔離したインメモリの PGlite で各クエリを一度ずつ実行しました。パッケージは `@electric-sql/pglite 0.6.0` で、`SHOW server_version` の結果は `19.0` でした。ここで `read` は PostgreSQL の共有バッファに読み込んだブロック数です。このメモリ上の測定から物理ディスク I/O は判断できません。 [EXPLAIN](https://www.postgresql.org/docs/19/sql-explain.html) · [PGlite](https://pglite.dev/docs/about)

測定対象は読み取りクエリです。`FOR UPDATE SKIP LOCKED` によるジョブの取得、状態の更新、複数ワーカーの同時実行は個別に測定する必要があります。 [二つのセッションで SKIP LOCKED を使ってジョブを取得する](/en/posts/2026-11-26-postgres-skip-locked-queue/)
