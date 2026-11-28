---
{
  "state": "draft",
  "language": "ru",
  "translationKey": "2026-11-28-cloudflare-workers-neon-notes",
  "title": "Развёртывание приложения для заметок на Cloudflare Workers и Neon",
  "description": "Разместим страницу и API на одном домене Cloudflare Pages и проверим, может ли API после повторного развёртывания прочитать сохранённую в Neon заметку.",
  "sourcePath": "src/content/posts/en/2026-11-28-cloudflare-workers-neon-notes.md",
  "sourceSha256": "71e5ccc2d896aa47ab412ccae04a8ee5e45ca38371038625108fb6befd488a52"
}
---

Cloudflare Pages отдаёт статическую страницу, а запросы к `/api/notes` обрабатывает функция Pages в среде Workers. У страницы и API один источник, поэтому браузер может загрузить список без дополнительной настройки CORS. Заметки хранятся в Neon PostgreSQL. [Pages Functions](https://developers.cloudflare.com/pages/functions/get-started/)

Список открыт для всех, а для записи нужен токен. Сохраняйте только учебные заметки. Ниже приведены ожидаемые ответы после развёртывания.

## Создание таблицы заметок и API

Создайте таблицу в SQL Editor учебной базы Neon.

```sql
CREATE TABLE notes (
  id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  body text NOT NULL CHECK (char_length(body) BETWEEN 1 AND 200)
);
```

Установите Node.js и npm и выполните команды в корне проекта.

```bash
npm init -y
npm install @neondatabase/serverless
npm install --save-dev wrangler
mkdir -p functions/api public
```

Сохраните обработчик в файле `functions/api/notes.js` относительно корня проекта. Тегированный шаблон драйвера Neon передаёт текст заметки как параметр SQL. [Pages Functions](https://developers.cloudflare.com/pages/functions/routing/) · [Neon](https://neon.com/docs/serverless/serverless-driver)

```js
import { neon } from "@neondatabase/serverless";

export async function onRequest({ request, env }) {
  const reply = (data, status = 200) =>
    Response.json(data, {
      status,
      headers: { "Cache-Control": "no-store" },
    });

  if (request.method === "POST") {
    if (
      !env.DEMO_WRITE_TOKEN ||
      request.headers.get("Authorization") !== `Bearer ${env.DEMO_WRITE_TOKEN}`
    ) {
      return reply({ error: "Unauthorized" }, 401);
    }

    const input = await request.json().catch(() => null);
    const body = typeof input?.body === "string" ? input.body.trim() : "";

    if (!body || Array.from(body).length > 200) {
      return reply({ error: "Enter a note of 1 to 200 characters" }, 400);
    }

    const sql = neon(env.DATABASE_URL);
    const [note] = await sql`
      INSERT INTO notes (body) VALUES (${body}) RETURNING id, body
    `;
    return reply(note, 201);
  }

  if (request.method === "GET") {
    const sql = neon(env.DATABASE_URL);
    const notes = await sql`
      SELECT id, body FROM notes ORDER BY id DESC LIMIT 20
    `;
    return reply(notes);
  }

  return new Response(null, {
    status: 405,
    headers: { Allow: "GET, POST" },
  });
}
```

В `public/index.html` загрузите список и выведите текст каждой заметки через `textContent`.

```html
<!doctype html>
<html lang="en">
<meta charset="utf-8">
<title>Notes</title>
<h1>Notes</h1>
<pre id="notes">Loading…</pre>
<script type="module">
  const output = document.querySelector("#notes");
  try {
    const response = await fetch("/api/notes");
    if (!response.ok) throw new Error();
    const notes = await response.json();
    output.textContent = notes.map((note) => note.body).join("\n") || "No notes";
  } catch {
    output.textContent = "Could not load notes.";
  }
</script>
</html>
```

## Чтение той же заметки после повторного развёртывания

![Проверка токена и текста → Сохранение заметки → Развёртывание с той же БД → Чтение последних заметок](2026-11-28-cloudflare-workers-neon-notes.svg)

Войдите в учётную запись через Wrangler и создайте проект Pages в режиме Direct Upload. Замените имя проекта в примере своим. В качестве рабочей ветки для среды Production здесь указана `main`.

```bash
PROJECT_NAME="my-neon-notes"
npx wrangler login
npx wrangler pages project create "$PROJECT_NAME" --production-branch main
```

В среде Production проекта Pages сохраните строку подключения к Neon в секрете `DATABASE_URL`, а длинный случайно сгенерированный токен — в `DEMO_WRITE_TOKEN`. Запустите развёртывание из корня проекта, чтобы Wrangler собрал функции вместе со статической страницей. Для других веток используются секреты среды Preview. [Direct Upload](https://developers.cloudflare.com/pages/get-started/direct-upload/) · [Pages Secrets](https://developers.cloudflare.com/pages/functions/bindings/#secrets)

```bash
npx wrangler pages deploy public --project-name "$PROJECT_NAME" --branch main
```

В оболочке задайте для `BASE_URL` рабочий URL проекта, а для `DEMO_WRITE_TOKEN` — тот же токен записи. Отправьте запросы ниже.

```bash
curl -i "$BASE_URL/api/notes" \
  -H "Authorization: Bearer $DEMO_WRITE_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"body":"Keep this note after redeployment"}'

curl -i "$BASE_URL/api/notes"
```

При записи проверьте код 201 и идентификатор заметки. Повторно разверните тот же проект в рабочей ветке с той же базой и ещё раз отправьте запрос на чтение. Ответ 200 с прежними идентификатором и текстом означает, что новая версия API читает сохранённую заметку. Проверьте, что она отображается в браузере, а запрос на запись без токена возвращает 401.

[Сравнение бесплатных вариантов размещения](../2026-11-28-free-deployment-guide/) · [Приложение для заметок на своём сервере](../2026-11-28-self-hosting-ai-notes/)
