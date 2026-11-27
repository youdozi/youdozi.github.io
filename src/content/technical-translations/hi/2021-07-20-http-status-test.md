---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2021-07-20-http-status-test",
  "routeSlug": "2021-07-20-http-status-test",
  "kind": "post",
  "title": "स्थानीय Python सर्वर पर HTTP स्टेटस कोड कैसे जाँचें",
  "description": "localhost पर छोटा सर्वर चलाकर JSON जवाब, स्टेटस 200 के साथ HTML और बिना बॉडी वाला 204 जाँचें। स्टेटस के साथ हेडर और बॉडी भी पढ़ें।",
  "categories": [
    "util"
  ],
  "tags": [
    "http",
    "testing",
    "python"
  ],
  "sourcePath": "src/content/posts/en/2021-07-20-http-status-test.md",
  "sourceSha256": "6a0015675b8a80249e52069a1e2ba364408570bbf983db78a56b13b3ebf0b721",
  "draftSha256": "d4d71ba95a9d4daa6ce476346d19a52790e51e968af07f9d8021df89953c5b30",
  "manifestPath": ".pipeline/technical-translations/batch-145/manifest.json",
  "manifestSha256": "83632a9c260a632e1d8e633d7c66621183e6d3f6d7cd0894b37dc210ce6b8c78",
  "publishedAt": "2026-11-27T13:09:20.073Z",
  "updatedAt": "2026-11-27T13:09:20.073Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 221,
    "approvedAt": "2026-11-27T13:09:20.073Z",
    "basis": "The owner authorized publication of the five Hindi editions in item 145. The translator reviewed the translations and diagrams."
  }
}
---

सिर्फ़ स्टेटस कोड से पता नहीं चलता कि क्लाइंट जवाब का उपयोग कर पाएगा या नहीं। उसे 200 के साथ HTML मिल सकता है, या सफल 204 जवाब में डिकोड करने के लिए कोई बॉडी ही नहीं हो सकती। स्थानीय टेस्ट सर्वर से आप किसी बाहरी सेवा के बिना दोनों स्थितियाँ दोहरा सकते हैं।

यह उदाहरण Python 3.11 या उसके बाद के संस्करण और केवल मानक लाइब्रेरी का उपयोग करता है। सर्वर 127.0.0.1 पर सुनता है और कुछ तय रूट के लिए GET संभालता है। इसे विकास के दौरान परीक्षण के लिए बनाया गया है, एप्लिकेशन चलाने के लिए नहीं।

## सर्वर जवाब कैसे चुनता है

![स्थानीय सर्वर रूट के अनुसार स्टेटस और बॉडी चुनता है](/assets/diagrams/technical/hi-2021-07-20-http-status-test.svg)

हैंडलर हेडर लिखने से पहले स्टेटस और जवाब का फ़ॉर्मैट तय करता है। 204 वाले रूट पर वह बिना बॉडी और बिना Content-Length के जवाब पूरा करता है। बाकी रूट पर वह हेडर में घोषित संख्या के बराबर बाइट लिखता है।

## सर्वर का पूरा कोड status_server.py में सहेजें

```python
import argparse
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

SUPPORTED = {200, 201, 204, 400, 404, 429, 500, 503}

class StatusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlsplit(self.path).path
        match = re.fullmatch(r"/status/([0-9]{3})", path)
        requested = int(match.group(1)) if match else None
        status = requested if requested in SUPPORTED else 404
        content_type = "application/json; charset=utf-8"
        body = json.dumps({"status": status}).encode("utf-8")
        if path == "/html/200":
            status = 200
            content_type = "text/html; charset=utf-8"
            body = b"<html><body>not JSON</body></html>"
        self.send_response(status)
        if status == 204:
            self.end_headers()
            return
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass

def make_server(port=8089):
    return ThreadingHTTPServer(("127.0.0.1", port), StatusHandler)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8089)
    args = parser.parse_args()
    if not 0 <= args.port <= 65535:
        parser.error("port must be from 0 through 65535")
    with make_server(args.port) as server:
        print(f"http://127.0.0.1:{server.server_port}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass

```

[Python का HTTP सर्वर API](https://docs.python.org/3/library/http.server.html) अनुरोध संभालने और अलग-अलग थ्रेड पर कनेक्शन स्वीकार करने की सुविधा देता है। जिन पथ या स्टेटस नंबर का समर्थन नहीं है, उनके लिए सर्वर JSON में 404 लौटाता है। रूट `/html/200` जानबूझकर सफल स्टेटस के साथ HTML लौटाता है।

एक टर्मिनल में सर्वर चलाएँ और दूसरे से अनुरोध भेजें।

```sh
python3 status_server.py --port 8089
```

```sh
curl -i http://127.0.0.1:8089/status/500
curl -i http://127.0.0.1:8089/html/200
curl -i http://127.0.0.1:8089/status/204
```

पोर्ट 0 देने पर ऑपरेटिंग सिस्टम खाली पोर्ट चुनता है और सर्वर उसका वास्तविक URL दिखाता है। सर्वर रोकने के लिए Ctrl+C दबाएँ। इन curl कमांड में `--fail` छोड़ दिया गया है ताकि आप त्रुटि वाला जवाब भी देख सकें।

| अनुरोध | स्टेटस | जवाब की बॉडी |
| --- | --- | --- |
| `/status/200` | 200 | JSON में स्टेटस 200 |
| `/html/200` | 200 | HTML, JSON नहीं |
| `/status/500` | 500 | JSON में स्टेटस 500 |
| `/status/204` | 204 | न बॉडी, न Content-Length |

[RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html#section-8.6) के अनुसार 204 जवाब में Content-Length भेजना मना है। 2xx स्टेटस की जाँच से अलग यह भी जाँचें कि बॉडी मौजूद है या नहीं। इस उदाहरण से स्टेटस, मीडिया टाइप और बॉडी की सीमा जाँची जा सकती है। इसमें धीमे जवाब, TLS, प्रमाणीकरण या दोबारा अनुरोध भेजने के समय का अनुकरण नहीं किया गया है। क्लाइंट पर डिकोडिंग और त्रुटि संकेत जाँचने के लिए [WebClient के जवाबों का परीक्षण](/hi/posts/2023-09-19-springboot-test-webclient/) देखें।
