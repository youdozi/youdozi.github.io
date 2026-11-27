---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2023-10-10-temurin-jdk21-delay",
  "routeSlug": "2023-10-10-temurin-jdk21-delay",
  "kind": "post",
  "title": "Temurin JDK 21 की बाइनरी का मेटाडेटा कैसे जाँचें और 2023 में रिलीज़ क्यों देर से हुई",
  "description": "Adoptium API में OS, आर्किटेक्चर और पैकेज के आधार पर Temurin JDK 21 चुनें। समझें कि मेटाडेटा जाँचना, डाउनलोड की पुष्टि करना और 2023 की देरी का कारण जानना अलग काम हैं।",
  "categories": [
    "jdk"
  ],
  "tags": [
    "jdk21",
    "adoptium",
    "temurin"
  ],
  "sourcePath": "src/content/posts/en/2023-10-10-temurin-jdk21-delay.md",
  "sourceSha256": "4aca27fcb8d1eb088ae7cc816e9cc82c662724ac7ee8a418618759fe8df67eac",
  "draftSha256": "4f25040fc475dfcf344ef69e0cdd1867fdf62b42fe3d9343036989f9192aa14c",
  "manifestPath": ".pipeline/technical-translations/batch-143/manifest.json",
  "manifestSha256": "507f1028e4316fae6163aabff3c22cf50eccdee5516bab5c7e7653c530e37280",
  "publishedAt": "2026-11-27T12:21:24.636Z",
  "updatedAt": "2026-11-27T12:21:24.636Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 219,
    "approvedAt": "2026-11-27T12:21:24.636Z",
    "basis": "The owner authorized publication of the five Hindi editions in item 143. The translator reviewed the translations and diagrams."
  }
}
---

Temurin JDK 21 की बाइनरी खोजने के लिए Adoptium API में अपना OS, CPU, JVM और पैकेज प्रकार दें। नीचे का उदाहरण Linux x64 JDK का मेटाडेटा, चेकसम का प्रारूप और डाउनलोड URL जाँचता है। यह आर्काइव डाउनलोड नहीं करता और उसका हैश नहीं निकालता।

Temurin 21 के शुरुआती वितरण में 2023 में हुई देरी का OpenJDK 21 की रिलीज़ से अलग कारण था। Adoptium के अनुसार TCK समझौते की समीक्षा के कारण देरी हुई थी। बाद की सूचना में उसने TCK मिलने और रिलीज़ की बाइनरी प्रकाशित होने को अलग घटनाएँ बताया। Temurin 21 उसके बाद जारी हो चुका था।

## बाइनरी का मेटाडेटा कैसे जाँचें

![प्लैटफ़ॉर्म, Java संस्करण, डाउनलोड URL और चेकसम का प्रारूप जाँचकर एक बाइनरी का मेटाडेटा चुनने के चरण](/assets/diagrams/technical/hi-2023-10-10-temurin-jdk21-delay.svg)

चित्र में मेटाडेटा चुनने का क्रम है। इसमें इंस्टॉलेशन नहीं होता। प्लैटफ़ॉर्म, Java का मेजर संस्करण, चेकसम का प्रारूप और URL का पता जाँचा जाता है। इसके लिए आर्काइव डाउनलोड करने या उसका हैश निकालने की ज़रूरत नहीं होती।

## देरी की घोषणा और रिलीज़ की तारीखें

[Adoptium ने देरी की सूचना](https://adoptium.net/news/2023/09/temurin21-delay) 28 सितंबर 2023 को प्रकाशित की थी। उसमें **9 अक्टूबर के अपडेट** में बताया गया कि TCK मिल गया था और परीक्षण आगे बढ़ रहा था। उस अपडेट की तारीख 10 अक्टूबर नहीं थी। परीक्षण शुरू होने का अर्थ यह भी नहीं था कि हर प्लैटफ़ॉर्म की रिलीज़ तैयार हो गई थी।

अलग से देखें तो [GitHub के मेटाडेटा](https://api.github.com/repos/adoptium/temurin21-binaries/releases/tags/jdk-21%2B35) में [`jdk-21+35` रिलीज़](https://github.com/adoptium/temurin21-binaries/releases/tag/jdk-21%2B35) का `published_at` मान `2023-10-10T13:55:52Z` है। यह रिलीज़ प्रकाशित होने का समय है। हर फ़ाइल का अपलोड तब तक पूरा हो गया था, ऐसा इससे पता नहीं चलता। Early Access बिल्ड और आधिकारिक रिलीज़ का अंतर भी ध्यान में रखें।

## अभी उपलब्ध Java 21 बाइनरी खोजें

[Adoptium API](https://api.adoptium.net/q/swagger-ui/) में Java 21, Linux, x64, HotSpot और JDK चुनें। यदि आपका OS या CPU अलग है तो फ़िल्टर उसी हिसाब से एक साथ बदलें। उदाहरण केवल मेटाडेटा लाता है। JDK बाइनरी डाउनलोड या इंस्टॉल नहीं होती। इसे चलाने के लिए Python 3 और curl चाहिए।

```sh
curl --fail --show-error --silent --location \
  'https://api.adoptium.net/v3/assets/latest/21/hotspot?architecture=x64&image_type=jdk&os=linux&vendor=eclipse' \
  --output assets.json &&
  python3 select-temurin.py assets.json
```

### `select-temurin.py`

```python
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

if len(sys.argv) != 2:
    sys.exit("usage: select-temurin.py ASSETS_JSON")
try:
    assets = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    if not isinstance(assets, list) or len(assets) != 1:
        raise ValueError("expected exactly one asset")
    asset = assets[0]
    binary = asset["binary"]
    if (binary["os"], binary["architecture"], binary["image_type"], binary["jvm_impl"]) != ("linux", "x64", "jdk", "hotspot"):
        raise ValueError("unexpected platform or image type")
    if asset["version"]["major"] != 21:
        raise ValueError("expected Java 21")
    package = binary["package"]
    checksum = package["checksum"]
    if not isinstance(checksum, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", checksum):
        raise ValueError("invalid SHA-256 metadata")
    link = package["link"]
    if not isinstance(link, str):
        raise ValueError("package URL must be a string")
    url = urlparse(link)
    if url.scheme != "https" or url.netloc != "github.com" or not url.path.startswith("/adoptium/temurin21-binaries/releases/download/"):
        raise ValueError("unexpected package URL")
    result = {"version": asset["version"]["semver"], "name": package["name"], "url": link, "sha256": checksum}
except (OSError, UnicodeError, ValueError, KeyError, TypeError) as error:
    print(f"invalid release metadata: {error}", file=sys.stderr)
    sys.exit(2)
print(json.dumps(result, indent=2))
```

स्क्रिप्ट परिणाम तभी लिखती है जब ठीक एक एसेट मिले और Java का मेजर संस्करण, प्लैटफ़ॉर्म, इमेज प्रकार, वितरण URL और चेकसम का प्रारूप अपेक्षा के अनुरूप हों। कोई ज़रूरी फ़ील्ड गायब हो, कई एसेट मिलें या JSON अमान्य हो तो जाँच विफल होती है। `&&` के कारण `curl` विफल होने पर चयन वाली स्क्रिप्ट नहीं चलती।

`latest/21` से क्वेरी के समय उपलब्ध Java 21 अपडेट मिलता है। यह पहली `21+35` रिलीज़ को तय नहीं करता और न ही सभी JDK में सबसे नया मेजर संस्करण चुनता है। वही डिप्लॉयमेंट दोहराने के लिए मिले हुए संस्करण, URL और SHA-256 को दर्ज करें और उन्हीं मानों का इस्तेमाल करें।

यह जाँच चेकसम के **प्रारूप** की है। इससे डाउनलोड की गई फ़ाइल की अखंडता सिद्ध नहीं होती। यदि आर्काइव अलग से डाउनलोड करें तो उसे खोलने या इंस्टॉल करने से पहले उसका SHA-256 निकालकर मेटाडेटा के मान से मिलाएँ। वास्तविक बाइनरी का हैश प्रकाशित चेकसम से मिलाना इस उदाहरण में शामिल नहीं है।

एसेट चुनने का एक और तरीका [GitHub रिलीज़ और एसेट की जानकारी लेने वाले उदाहरण](/en/posts/2023-09-23-linux-shellscript-github-latest/) में देखें। सुविधाओं की स्थिरता के लिए [JDK 21 की स्थिर और प्रीव्यू सुविधाओं](/hi/posts/2023-09-20-jdk-21-release/) वाला लेख पढ़ें।

चुना हुआ एसेट डाउनलोड करने के बाद [उसका SHA-256 चेकसम किसी विश्वसनीय अपेक्षित मान से मिलाएँ](/en/posts/2026-10-30-verify-sha256-download/)। वहाँ दिया जाँच प्रोग्राम स्थानीय फ़ाइल के बाइट पढ़ता है। वह रिलीज़ डाउनलोड नहीं करता और उसके स्रोत की प्रामाणिकता की पुष्टि भी नहीं करता।
