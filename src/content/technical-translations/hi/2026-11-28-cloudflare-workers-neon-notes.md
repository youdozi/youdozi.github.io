---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2026-11-28-cloudflare-workers-neon-notes",
  "routeSlug": "2026-11-28-cloudflare-workers-neon-notes",
  "kind": "post",
  "title": "Cloudflare Workers और Neon के साथ नोट्स ऐप डिप्लॉय करें",
  "description": "Cloudflare Pages पर पेज और API को एक ही ऑरिजिन से उपलब्ध कराएँ और जाँचें कि दोबारा डिप्लॉय करने पर API, Neon में सहेजा हुआ नोट पढ़ पाता है या नहीं।",
  "categories": [
    "tips"
  ],
  "tags": [
    "cloudflare",
    "neon",
    "postgresql"
  ],
  "sourcePath": "src/content/posts/en/2026-11-28-cloudflare-workers-neon-notes.md",
  "sourceSha256": "71e5ccc2d896aa47ab412ccae04a8ee5e45ca38371038625108fb6befd488a52",
  "draftSha256": "9ca975fb84b26243fbe1ce581a261437a975f88f28d34aa08b5214d4b6e43045",
  "manifestPath": ".pipeline/technical-translations/batch-166/manifest.json",
  "manifestSha256": "3b0976e942a459217960a1711811aa1009c06cbf4a3d6f7f61ce5865c5ea7e3b",
  "publishedAt": "2026-11-28T14:03:21.816Z",
  "updatedAt": "2026-11-28T14:03:21.816Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 231,
    "approvedAt": "2026-11-28T14:03:21.816Z",
    "basis": "User directly requested publication of the approved Cloudflare Workers and Neon notes app manuscript in nine languages (item 166)."
  }
}
---

Cloudflare Pages से स्टैटिक पेज मिलता है। Workers पर चलने वाला Pages Function `/api/notes` के अनुरोधों को संभालता है। पेज और API का ऑरिजिन एक होने से ब्राउज़र बिना किसी अतिरिक्त CORS सेटिंग के सूची पढ़ सकता है। नोट्स Neon PostgreSQL में सहेजे जाते हैं। [Pages Functions](https://developers.cloudflare.com/pages/functions/get-started/)

सूची कोई भी पढ़ सकता है। लिखने के लिए टोकन चाहिए। इसमें केवल अभ्यास के लिए नोट्स सहेजें। नीचे बताए गए जवाब डिप्लॉयमेंट के बाद अपेक्षित हैं।

## नोट्स की टेबल और API बनाएँ

अभ्यास के लिए बनाए गए Neon डेटाबेस के SQL Editor में यह टेबल बनाएँ।

```sql
CREATE TABLE notes (
  id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  body text NOT NULL CHECK (char_length(body) BETWEEN 1 AND 200)
);
```

Node.js और npm इंस्टॉल होने के बाद प्रोजेक्ट की रूट डायरेक्टरी से ये कमांड चलाएँ।

```bash
npm init -y
npm install @neondatabase/serverless
npm install --save-dev wrangler
mkdir -p functions/api public
```

प्रोजेक्ट की रूट डायरेक्टरी में `functions/api/notes.js` फ़ाइल बनाकर नीचे दिया कोड रखें। Neon ड्राइवर का टैग्ड टेम्पलेट नोट के टेक्स्ट को SQL पैरामीटर के रूप में भेजता है। [Pages Functions](https://developers.cloudflare.com/pages/functions/routing/) · [Neon](https://neon.com/docs/serverless/serverless-driver)

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

`public/index.html` में सूची लाएँ और हर नोट का टेक्स्ट `textContent` से दिखाएँ।

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

## दोबारा डिप्लॉय करने के बाद वही नोट पढ़ें

![टोकन और टेक्स्ट जाँचें → नोट सहेजें → उसी डेटाबेस के साथ फिर डिप्लॉय करें → हाल के नोट पढ़ें](/assets/diagrams/technical/hi-2026-11-28-cloudflare-workers-neon-notes.svg)

Wrangler से लॉग इन करें और Pages का Direct Upload प्रोजेक्ट बनाएँ। उदाहरण में दिए गए नाम की जगह अपने प्रोजेक्ट का नाम रखें। यहाँ प्रोडक्शन ब्रांच `main` है।

```bash
PROJECT_NAME="my-neon-notes"
npx wrangler login
npx wrangler pages project create "$PROJECT_NAME" --production-branch main
```

Pages प्रोजेक्ट के Production एनवायरनमेंट में Neon की कनेक्शन स्ट्रिंग को `DATABASE_URL` और एक लंबे, रैंडम तरीके से बनाए गए टोकन को `DEMO_WRITE_TOKEN` नाम के सीक्रेट में सहेजें। रूट डायरेक्टरी से डिप्लॉय करें ताकि Wrangler स्टैटिक पेज के साथ Functions भी बिल्ड करे। दूसरी ब्रांच पर डिप्लॉय करने पर Preview एनवायरनमेंट के सीक्रेट इस्तेमाल होते हैं। [Direct Upload](https://developers.cloudflare.com/pages/get-started/direct-upload/) · [Pages Secrets](https://developers.cloudflare.com/pages/functions/bindings/#secrets)

```bash
npx wrangler pages deploy public --project-name "$PROJECT_NAME" --branch main
```

शेल में `BASE_URL` को प्रोजेक्ट के प्रोडक्शन URL पर सेट करें और `DEMO_WRITE_TOKEN` में वही राइट टोकन रखें। फिर ये अनुरोध भेजें।

```bash
curl -i "$BASE_URL/api/notes" \
  -H "Authorization: Bearer $DEMO_WRITE_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"body":"Keep this note after redeployment"}'

curl -i "$BASE_URL/api/notes"
```

लिखने के जवाब में 201 और नोट का ID देखें। उसी डेटाबेस का इस्तेमाल करते हुए उसी प्रोजेक्ट की प्रोडक्शन ब्रांच पर दोबारा डिप्लॉय करें और पढ़ने का अनुरोध फिर से भेजें। 200 के साथ वही ID और टेक्स्ट मिलने पर पता चलता है कि नया API सहेजा हुआ नोट पढ़ सकता है। जाँचें कि नोट ब्राउज़र में भी दिखता है और बिना टोकन के लिखने पर 401 मिलता है।

[मुफ़्त होस्टिंग के विकल्पों की तुलना](../2026-11-28-free-deployment-guide/) · [अपने सर्वर पर नोट्स ऐप चलाएँ](../2026-11-28-self-hosting-ai-notes/)
