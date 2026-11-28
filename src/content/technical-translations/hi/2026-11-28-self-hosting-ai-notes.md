---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2026-11-28-self-hosting-ai-notes",
  "routeSlug": "2026-11-28-self-hosting-ai-notes",
  "kind": "post",
  "title": "AI का बनाया ऐप अपने सर्वर पर कैसे चलाएँ? शुरुआत एक नोट्स API से करें",
  "description": "AI से नोट्स API बनवाएँ, प्रोसेस बंद करें और जाँचें कि उसी SQLite फ़ाइल से पहला नोट फिर पढ़ा जा सकता है।",
  "categories": [
    "tips"
  ],
  "tags": [
    "self-hosting",
    "python",
    "sqlite"
  ],
  "sourcePath": "src/content/posts/en/2026-11-28-self-hosting-ai-notes.md",
  "sourceSha256": "f31b0a9a46f32859c6cd630d2d77ff943c1ddc47a7f7a4135e924c37fd826809",
  "draftSha256": "5f2bfc5f111505087d149ae622f972b3677755b404d851436886b9c52c451e3d",
  "manifestPath": ".pipeline/technical-translations/batch-1542/manifest.json",
  "manifestSha256": "05eaa6b0c6f7006e6c3a9f9d20c549956c1aa47e51862aadecb9f5d44f5f3862",
  "publishedAt": "2026-11-28T02:44:07.347Z",
  "updatedAt": "2026-11-28T02:44:07.347Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 228,
    "approvedAt": "2026-11-28T02:44:07.347Z",
    "basis": "Explicit item 154 publication instruction for the revised item 153 self-hosted notes article in all nine site languages."
  }
}
---

AI के बनाए नोट्स ऐप ने आपका पहला नोट सहेज लिया। अब ऐप बंद करके फिर चलाएँ। क्या नोट अभी भी दिख रहा है? अपने कंप्यूटर पर ऐप होस्ट करते समय शुरुआत में दो बातें जाँचें। क्या ऐप जवाब देता है और क्या दोबारा शुरू करने पर डेटा मिल जाता है? यहाँ हम AI से एक छोटा नोट्स ऐप और उसे चलाने के निर्देश माँगेंगे, फिर अपने कंप्यूटर पर नतीजा देखेंगे। इस उदाहरण में सिर्फ़ Python और SQLite का इस्तेमाल हुआ है।

## सुविधाओं के साथ यह भी बताएँ कि ऐप कैसे चलेगा

सिर्फ़ “एक नोट्स ऐप बना दो” कहने पर मॉडल खुद तय कर सकता है कि नोट कहाँ रखे जाएँ और कौन कनेक्ट कर सके। पहले ही बता दें कि डेटा कहाँ रखना है, किसे पहुँच चाहिए और किन जाँचों के बाद आप ऐप को तैयार मानेंगे।

**प्रॉम्प्ट**　Python की मानक लाइब्रेरी और SQLite से मेरे लिए एक निजी नोट्स API बनाओ। ऐप सिर्फ़ `127.0.0.1` पर सुने और नोट `data/notes.db` में सहेजे। `GET /healthz` से स्थिति मिले और `GET /notes` से नोटों की सूची। `POST /notes` का इनपुट `{"text":"첫 메모"}` हो और सिर्फ़ खाली जगह वाला टेक्स्ट भेजने पर `400` मिले। `app.py`, ऐप शुरू और बंद करने के कमांड और curl से जाँच के उदाहरण दो। इस क्रम में जाँचो: स्थिति देखना → नोट सहेजना → प्रोसेस बंद करना → उसी डेटाबेस से फिर शुरू करना → नोट पढ़ना। वह पता बताओ जहाँ ऐप सुनता है और उस फ़ाइल का नाम बताओ जो बनती है।

## चलाने से पहले पता और डेटा फ़ाइल का पथ जाँचें

देखें कि सर्वर `127.0.0.1` पर सुनता है और SQLite डिस्क पर `data/notes.db` खोलता है। सापेक्ष पथ देने पर किसी दूसरी डायरेक्टरी से ऐप चलाने पर अलग डेटाबेस खुल सकता है। नीचे का उदाहरण ऐप की फ़ाइल के स्थान से पथ तय करता है। यहाँ Python के `http.server` का उपयोग अपने कंप्यूटर पर सीखने के लिए किया गया है। [http.server](https://docs.python.org/3/library/http.server.html) · [sqlite3](https://docs.python.org/3/library/sqlite3.html)

अभ्यास के लिए एक खाली डायरेक्टरी में नीचे का कोड `app.py` के नाम से सहेजें।

```python
import json
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

db_path = Path(__file__).resolve().parent / "data" / "notes.db"


class Notes(BaseHTTPRequestHandler):
    def reply(self, status, value):
        body = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/healthz":
            self.reply(200, {"status": "ok"})
        elif self.path == "/notes":
            rows = db.execute("SELECT text FROM notes ORDER BY id")
            self.reply(200, [{"text": text} for (text,) in rows])
        else:
            self.reply(404, {"error": "unknown path"})

    def do_POST(self):
        if self.path != "/notes":
            self.reply(404, {"error": "unknown path"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 8192:
                raise ValueError
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict):
                raise ValueError
            text = data.get("text")
            if not isinstance(text, str) or not text.strip():
                raise ValueError
        except ValueError:
            self.reply(400, {"error": "invalid note"})
            return
        with db:
            db.execute("INSERT INTO notes (text) VALUES (?)", (text,))
        self.reply(201, {"text": text})


if __name__ == "__main__":
    db_path.parent.mkdir(exist_ok=True)
    db = sqlite3.connect(db_path)
    try:
        db.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, text TEXT NOT NULL)")
        with HTTPServer(("127.0.0.1", 0), Notes) as server:
            print(f"http://127.0.0.1:{server.server_port}", db_path, sep="\n", flush=True)
            server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        db.close()
```

## वास्तविक अनुरोध भेजकर AI के निर्देश जाँचें

![स्थिति और खाली सूची देखें → सिर्फ़ खाली जगह वाला नोट अस्वीकार करें → पहला नोट सहेजें → प्रोसेस बंद करें → उसी डेटाबेस से फिर शुरू करें → सहेजा हुआ नोट पढ़ें।](/assets/diagrams/technical/hi-2026-11-28-self-hosting-ai-notes.svg)

नोट डिस्क पर पहुँचा या नहीं, यह जाँचने के लिए उसे लिखने वाला प्रोसेस बंद करें और नए प्रोसेस से नोट पढ़ें।

ऐप की डायरेक्टरी में `python3 app.py` चलाएँ। पहली पंक्ति में अस्थायी पोर्ट वाला पता और अगली में डेटाबेस का पथ दिखेगा। दूसरे टर्मिनल में नीचे के कमांड चलाएँ। जब `read` इनपुट की प्रतीक्षा करे तो पहली पंक्ति वाला पता पेस्ट करें।

```sh
read -r base
```

```sh
curl -i "$base/healthz"
curl -i "$base/notes"
curl -i -H 'Content-Type: application/json' -d '{"text":"   "}' "$base/notes"
curl -i -H 'Content-Type: application/json' -d '{"text":"첫 메모"}' "$base/notes"
```

ऐप वाले टर्मिनल में `Ctrl+C` दबाएँ और शेल का प्रॉम्प्ट लौटने दें। फिर `python3 app.py` चलाएँ। देखें कि डेटाबेस का पथ पहले वाला ही है और दूसरे टर्मिनल में नया पता दर्ज करें।

```sh
read -r base
```

```sh
curl -i "$base/notes"
```

हमने Python `3.13.0` के एक अस्थायी स्थानीय परिवेश में लूपबैक पते और अस्थायी पोर्ट पर जाँच की। स्थिति पूछने और शुरू की खाली सूची पढ़ने पर `200` मिला। सिर्फ़ खाली जगह भेजने पर `400` और पहला नोट सहेजने पर `201` मिला। हमने देखा कि प्रोसेस बंद हो चुका है, फिर उसी डेटाबेस से ऐप चलाया। सूची माँगने पर `200` के साथ सहेजा हुआ नोट मिला। सूची खाली दिखे तो दोनों बार दिखे डेटाबेस के वास्तविक पथ मिलाएँ। AI को स्टार्ट कमांड, डेटाबेस के पथ और HTTP के जवाब दें।

## ऐप इस्तेमाल करते रहना है तो बैकअप लेने और उसे बहाल करने की तैयारी करें

“अगर यह कंप्यूटर खराब हो जाए तो क्या मैं नोट कहीं और खोल पाऊँगा?” AI से डेटा का पथ बताने और बैकअप को नई डायरेक्टरी में बहाल करके नोट पढ़ने के चरण माँगें। सर्वर पर ले जाते समय जाँचें कि मशीन रीबूट होने के बाद ऐप कैसे शुरू होगा और किसे पहुँच मिलेगी। इस अभ्यास में स्थानीय अनुरोध, नोट सहेजना और ऐप दोबारा चलाकर नोट पढ़ना जाँचा गया। बाहरी पहुँच और बैकअप बहाल करने की जाँच नहीं की गई। [निजी नेटवर्क पर MacBook को निजी सर्वर की तरह इस्तेमाल करें](https://youdozi.github.io/ko/posts/2026-11-23-macbook-personal-server/)
