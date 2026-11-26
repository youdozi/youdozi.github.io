---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2026-11-26-postgres-skip-locked-queue",
  "routeSlug": "2026-11-26-postgres-skip-locked-queue",
  "kind": "post",
  "title": "Una cola de trabajos con SKIP LOCKED en PostgreSQL: ¿qué pasa si el proceso se detiene?",
  "description": "Dos sesiones toman un trabajo cada una. ¿Cuál vuelve a estar disponible tras una reversión y qué ocurre cuando se cierra la conexión después de confirmar?",
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
  "draftSha256": "98494934f2f3ccf819daf1ece26487bc1ad8a181a19689f7622a971a53190e13",
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

Mientras A mantiene bloqueado el primer trabajo, B puede tomar el siguiente con `SKIP LOCKED`. Si el proceso B se detiene justo después de confirmar que ha tomado el trabajo, este queda en estado `running`. Los bloqueos de fila permiten repartir el trabajo. La cola también debe registrar cuándo puede intervenir otro proceso.

## Tomar un trabajo por sesión

Conecta la sesión A a una base de datos de práctica vacía y ejecuta estas instrucciones con la confirmación automática activada. Conecta B a la misma base. Usa el nivel de aislamiento predeterminado, `READ COMMITTED`, en ambas sesiones.

```sql
CREATE TABLE queue_demo (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  status text NOT NULL DEFAULT 'pending'
);
INSERT INTO queue_demo (status) VALUES ('pending'), ('pending');
```

Ejecuta el siguiente bloque primero en A y deja abierta la transacción. Después ejecútalo en B. Mantén abiertas ambas transacciones hasta que veas las filas devueltas.

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

![A bloquea el trabajo 1. B lo salta y toma el trabajo 2. Cuando B confirma y A revierte su transacción, el primer trabajo vuelve a estar pendiente y el segundo sigue en curso.](/assets/diagrams/technical/es-2026-11-26-postgres-skip-locked-queue.svg)

`ORDER BY id` determina el orden en que se examinan los candidatos. B puede confirmar primero, así que los trabajos pueden terminar en otro orden. PostgreSQL documenta este uso de los bloqueos de fila cuando varios consumidores compiten por las filas de una cola. [Cláusula de bloqueo de SELECT en PostgreSQL](https://www.postgresql.org/docs/current/sql-select.html#SQL-FOR-UPDATE-SHARE)

## Cerrar la conexión después de confirmar

Ejecuta `COMMIT;` en B y después `ROLLBACK;` en A. Cierra la conexión de B y consulta el estado desde A.

```sql
SELECT id, status FROM queue_demo ORDER BY id;
```

Hice la prueba con dos conexiones a una instancia local aislada de PostgreSQL 17.12. Al tomar los trabajos, A devolvió `(1, running)` y B devolvió `(2, running)`. La consulta final devolvió estas filas.

```text
id | status
1  | pending
2  | running
```

La reversión en A deshizo el cambio de estado. La confirmación en B liberó el bloqueo y dejó registrado el cambio. El siguiente proceso buscará filas en estado `pending`, por lo que seguirá pasando por alto el trabajo 2.

## Reasignar un trabajo cuyo plazo ha vencido

En producción, registra un plazo y un identificador de intento nuevo e incrementa el contador de intentos en la breve transacción que asigna el trabajo. Ejecuta la tarea después de confirmar. Un proceso de recuperación bloquea el trabajo en curso cuyo plazo ha vencido y vuelve a comprobar su estado. Si quedan intentos, asigna un nuevo identificador de intento y un nuevo plazo. Si se ha alcanzado el límite, marca el trabajo como fallido para investigarlo.

Un proceso que regresa tarde solo puede registrar la finalización si coinciden el identificador del trabajo, el estado en curso y su propio identificador de intento. Tras una reasignación no actualizará ninguna fila. Sin embargo, el proceso puede enviar un correo y detenerse antes de registrar que ha terminado. Reutiliza la misma clave de idempotencia en cada intento de envío del mismo correo y haz que el servicio de correo descarte duplicados con esa clave. El identificador de intento cambia en cada reasignación, pero la clave de envío se conserva.
