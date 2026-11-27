---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2023-11-17-linux-shellscript-version-compare",
  "routeSlug": "2023-11-17-linux-shellscript-version-compare",
  "kind": "post",
  "title": "शेल में बिंदुओं से अलग किए गए संख्यात्मक संस्करणों की तुलना कैसे करें",
  "description": "Python 3 से संस्करण के हर हिस्से की पूर्णांक के रूप में तुलना करें। अंत के शून्य, अलग-अलग लंबाई और अमान्य इनपुट के लिए निकास कोड को उदाहरणों से समझें।",
  "categories": [
    "linux"
  ],
  "tags": [
    "linux",
    "bash",
    "shell script",
    "function"
  ],
  "sourcePath": "src/content/posts/en/2023-11-17-linux-shellscript-version-compare.md",
  "sourceSha256": "f3a895ba23f21ab99f5083879149d5f7f1ab3ed0c7c9a89c1557b9bf7d6b1ddc",
  "draftSha256": "df36e1aeedc57ea05144a5bb9e482a7476472c0f16a787b8f409c9f5b346a92a",
  "manifestPath": ".pipeline/technical-translations/batch-144/manifest.json",
  "manifestSha256": "f2cdc48717558ad001e3a065a1fcd8bf668c42c267757c24843b091e441bad71",
  "publishedAt": "2026-11-27T12:46:07.279Z",
  "updatedAt": "2026-11-27T12:46:07.279Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 220,
    "approvedAt": "2026-11-27T12:46:07.279Z",
    "basis": "The owner authorized publication of the five Hindi editions in item 144. The translator reviewed the translations and diagrams."
  }
}
---

`1.10` और `1.2` की तुलना स्ट्रिंग या दशमलव संख्या के रूप में न करें। बाएँ से दाएँ हर हिस्से की पूर्णांक के रूप में तुलना करें और अंत में जो हिस्से नहीं दिए गए हैं उन्हें शून्य मानें। इस तरह `1.2` और `1.2.0` बराबर होते हैं। यह उदाहरण केवल बिंदुओं से अलग किए गए संख्यात्मक संस्करणों पर यह नियम लागू करता है।

स्क्रिप्ट `v1.2`, `1.2-rc1` और `1.2+build` अस्वीकार करती है। [SemVer](https://semver.org/) के अनुसार प्री-रिलीज़ की प्राथमिकता तय करने के लिए उसी विनिर्देश का पार्सर इस्तेमाल करें। प्रत्यय को बिना जाँचे हटाने से अर्थ बदल सकता है।

## तुलना का क्रम

![बिंदुओं से अलग किए गए हिस्सों को जाँचें, छूटे हिस्सों को शून्य मानें और पहली असमान जोड़ी से परिणाम निकालें](/assets/diagrams/technical/hi-2023-11-17-linux-shellscript-version-compare.svg)

पहले जाँचें कि संस्करण में बिंदुओं के बीच केवल अंक हैं। छूटे हुए हिस्सों की जगह शून्य रखें और पहली असमान जोड़ी मिलने पर रुकें। एक संस्करण का दूसरे से छोटा होना भी सफल तुलना का परिणाम है।

## तुलना की स्क्रिप्ट चलाएँ

इसके लिए Python 3 चाहिए। इसे `version-compare.sh` के नाम से सहेजें और `sh` से चलाएँ।

### `version-compare.sh`

```sh
#!/bin/sh
set -eu
python3 - "$@" <<'PYTHON'
import re
import sys
from itertools import zip_longest

if len(sys.argv) != 3 or any(not re.fullmatch(r"[0-9]+(?:\.[0-9]+)*", value) for value in sys.argv[1:]):
    print("usage: version-compare.sh CURRENT LATEST (numeric dotted versions)", file=sys.stderr)
    raise SystemExit(2)
current, latest = sys.argv[1:]
try:
    left = [int(part) for part in current.split('.')]
    right = [int(part) for part in latest.split('.')]
except ValueError:
    print("numeric component exceeds this Python runtime's conversion limit", file=sys.stderr)
    raise SystemExit(2)
comparison = 0
for a, b in zip_longest(left, right, fillvalue=0):
    if a != b:
        comparison = -1 if a < b else 1
        break
operator = '<' if comparison < 0 else '>' if comparison > 0 else '='
print(f"{current} {operator} {latest}")
PYTHON
```

```sh
sh version-compare.sh 1.10.5 1.3.1
sh version-compare.sh 1.2 1.2.0
sh version-compare.sh 1.1000 2.0
```

आउटपुट क्रमशः `1.10.5 > 1.3.1`, `1.2 = 1.2.0` और `1.1000 < 2.0` हैं। वैध तुलना का स्टेटस 0 होता है, चाहे परिणाम कुछ भी हो। आर्ग्युमेंट की संख्या गलत हो, प्रारूप असमर्थित हो या संख्यात्मक रूपांतरण की सीमा आ जाए तो stderr पर कारण और स्टेटस 2 मिलता है।

| इनपुट | परिणाम |
| --- | --- |
| `1.2.0.0.1` और `1.2` | `1.2.0.0.1 > 1.2` |
| `01.002` और `1.2` | `01.002 = 1.2` |
| `1.2-rc1` और `1.2` | असमर्थित प्रारूप, स्टेटस 2 |
| `1..2` और `1.2` | असमर्थित प्रारूप, स्टेटस 2 |

## तय चौड़ाई के अंकों को जोड़ने में क्या दिक्कत है?

awk का `%03d` जैसी चौड़ाई देना केवल प्रदर्शन की न्यूनतम चौड़ाई तय करता है। इससे किसी हिस्से की अधिकतम लंबाई तय नहीं होती। ऐसे हिस्सों को जोड़कर शेल का एक पूर्णांक बना देने पर बड़े मानों या अतिरिक्त हिस्सों वाले संस्करणों का क्रम बदल सकता है।

यह उदाहरण हर हिस्से को Python पूर्णांक में बदलता है और [`zip_longest(..., fillvalue=0)`](https://docs.python.org/3/library/itertools.html#itertools.zip_longest) से दोनों की लंबाई बराबर करता है। यदि रनटाइम संख्यात्मक रूपांतरण अस्वीकार कर दे, तो स्क्रिप्ट तुलना को सफल नहीं मानती।

स्वचालित परिनियोजन में तुलना का परिणाम और कमांड की सफलता अलग-अलग निर्णय हैं। मौजूदा संस्करण छोटा हो तो भी यह स्क्रिप्ट विफल नहीं होती। अपनी नीति लागू करने से पहले stdout पर दिया गया संबंध पढ़ें। [GitHub रिलीज़ टैग](/en/posts/2023-09-23-linux-shellscript-github-latest/) दूसरे प्रारूप में भी हो सकते हैं, इसलिए जाँचे बिना उन्हें इनपुट न दें। इंटरप्रेटर के चयन के लिए [POSIX sh फ़ंक्शन का उदाहरण](/hi/posts/2023-09-20-linux-shellscript-function-error/) देखें।
