---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2026-11-27-postgres-queue-partial-index",
  "routeSlug": "2026-11-27-postgres-queue-partial-index",
  "kind": "post",
  "title": "PostgreSQL की कतार में पूरे हो चुके काम जमा हों तो आंशिक इंडेक्स से कितना फ़ायदा होता है?",
  "description": "सिर्फ़ लंबित कामों का इंडेक्स बनाकर देखें कि सबसे पुराने लंबित काम खोजने की योजना और बफ़र के आँकड़े कैसे बदलते हैं।",
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
  "draftSha256": "97f95d0258988978c10306242c46fe55063e4f94b8ba6d5dc7d33581e5179181",
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

कुल 300,000 कामों में से 297,000 पूरे हो चुके थे और सिर्फ़ 3,000 लंबित थे। सबसे पुराने 20 लंबित काम खोजने के लिए एक आंशिक इंडेक्स बनाया गया। इसमें सिर्फ़ लंबित पंक्तियाँ काम बनने के समय और आईडी के क्रम में थीं, इसलिए क्वेरी की योजना से छँटाई का चरण हट गया।

## एक ही क्वेरी दो बार चलाएँ

खाली डेटाबेस में नीचे दिया गया SQL क्रम से चलाएँ। `ANALYZE` टेबल के आँकड़े अपडेट करता है। दोनों क्वेरी के बीच बनाया गया इंडेक्स सिर्फ़ उन पंक्तियों को रखता है जो `status = 'pending'` की शर्त पूरी करती हैं। [आंशिक इंडेक्स](https://www.postgresql.org/docs/19/indexes-partial.html)

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

## क्वेरी की योजना में क्या बदला?

![इंडेक्स बनाने से पहले: Seq Scan → Sort → Limit. आंशिक इंडेक्स के साथ: Index Only Scan → Limit.](/assets/diagrams/technical/hi-2026-11-27-postgres-queue-partial-index.svg)

पहली योजना पूरी टेबल पढ़ती है, पूरे हो चुके काम हटाती है और बचे हुए कामों को क्रम में लगाती है। इंडेक्स लंबित कामों को `(created_at, id)` के क्रम में देता है, इसलिए दूसरी योजना `LIMIT 20` तक पहुँचते ही पढ़ना रोक सकती है।

| निष्पादन योजना | इंडेक्स बनाने से पहले | आंशिक इंडेक्स के साथ |
| --- | --- | --- |
| शीर्ष नोड पर साझा बफ़र | `shared hit=1911` | `shared hit=1 read=2` |
| स्कैन नोड का आँकड़ा | `Rows Removed by Filter=297000` | `Heap Fetches=0` |
| लौटी पंक्तियाँ | 20 | 20 |

अलग रखे गए इन-मेमोरी PGlite डेटाबेस में हर क्वेरी एक बार चलाई गई। पैकेज `@electric-sql/pglite 0.6.0` था और `SHOW server_version` ने `19.0` लौटाया। यहाँ `read` उन ब्लॉक की गिनती है जिन्हें PostgreSQL ने साझा बफ़र में पढ़ा। मेमोरी में मिले इस आँकड़े से भौतिक डिस्क I/O का पता नहीं चलता। [EXPLAIN](https://www.postgresql.org/docs/19/sql-explain.html) · [PGlite](https://pglite.dev/docs/about)

इस प्रयोग में सिर्फ़ पढ़ने वाली क्वेरी मापी गई। `FOR UPDATE SKIP LOCKED` से काम लेने, उनकी स्थिति बदलने और कई वर्कर एक साथ चलाने के लिए अलग माप चाहिए। [दो सत्रों में SKIP LOCKED से काम लें](/en/posts/2026-11-26-postgres-skip-locked-queue/)
