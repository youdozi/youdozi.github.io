---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2026-11-27-postgres-queue-partial-index",
  "routeSlug": "2026-11-27-postgres-queue-partial-index",
  "kind": "post",
  "title": "¿Cuánto ayuda un índice parcial cuando se acumulan trabajos terminados en PostgreSQL?",
  "description": "Comparamos los planes y los accesos a búferes al buscar los trabajos pendientes más antiguos antes y después de indexar solo los pendientes.",
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
  "draftSha256": "b547b7a5461a71a5506c8d17eb9da731ab571a75f266f88b732a6a025eee50eb",
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

De 300.000 trabajos, 297.000 habían terminado y solo 3.000 seguían pendientes. Al buscar los 20 trabajos pendientes más antiguos, el plan dejó de necesitar una ordenación cuando un índice parcial permitió leer solo los pendientes por fecha de creación e identificador.

## Ejecutar dos veces la misma consulta

Ejecuta el siguiente SQL en orden en una base de datos vacía. `ANALYZE` actualiza las estadísticas de la tabla. El índice creado entre las dos consultas solo contiene las filas que cumplen `status = 'pending'`. [Índices parciales](https://www.postgresql.org/docs/19/indexes-partial.html)

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

## ¿Qué cambió en el plan?

![Antes de crear el índice: Seq Scan → Sort → Limit. Con el índice parcial: Index Only Scan → Limit.](/assets/diagrams/technical/es-2026-11-27-postgres-queue-partial-index.svg)

El primer plan recorre la tabla, descarta los trabajos terminados y ordena los candidatos restantes. El índice entrega los pendientes en el orden de `(created_at, id)`, de modo que el segundo plan puede detenerse en cuanto alcanza `LIMIT 20`.

| Plan de ejecución | Antes de crear el índice | Con el índice parcial |
| --- | --- | --- |
| Búferes compartidos en el nodo raíz | `shared hit=1911` | `shared hit=1 read=2` |
| Detalle del nodo de exploración | `Rows Removed by Filter=297000` | `Heap Fetches=0` |
| Filas devueltas | 20 | 20 |

Cada consulta se ejecutó una vez en una instancia aislada de PGlite en memoria con `@electric-sql/pglite 0.6.0`. `SHOW server_version` devolvió `19.0`. El contador `read` indica cuántos bloques se leyeron en los búferes compartidos de PostgreSQL. Esta medición en memoria no permite deducir la E/S física de disco. [EXPLAIN](https://www.postgresql.org/docs/19/sql-explain.html) · [PGlite](https://pglite.dev/docs/about)

El experimento midió una consulta de lectura. La reserva de trabajos mediante `FOR UPDATE SKIP LOCKED`, la actualización de su estado y la ejecución concurrente de varios trabajadores requieren mediciones aparte. [Reservar trabajos con SKIP LOCKED en dos sesiones](/en/posts/2026-11-26-postgres-skip-locked-queue/)
