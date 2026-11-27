---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2021-08-06-search-github",
  "routeSlug": "2021-08-06-search-github",
  "kind": "post",
  "title": "GitHub, Sourcegraph और स्थानीय Git में कोड कैसे खोजें",
  "description": "रिपॉज़िटरी, भाषा और पथ से कोड खोज का दायरा सीमित करें। GitHub और Sourcegraph के फ़िल्टर की तुलना करें और स्थानीय Git में किसी वाक्यांश को हूबहू खोजें।",
  "categories": [
    "util"
  ],
  "tags": [
    "git",
    "github",
    "sourcegraph",
    "search"
  ],
  "sourcePath": "src/content/posts/en/2021-08-06-search-github.md",
  "sourceSha256": "22da61f44f3002516631540293a6b08b9b0de12d2c7963e6c52ae57b297efddf",
  "draftSha256": "ce1daa242571c2af0b47b759e1195c76f5b1ab2917c7b11b78198aecbd27da49",
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

कोड खोजने से पहले तय करें कि किन रिपॉज़िटरी और फ़ाइलों में देखना है। फिर जहाँ मेल मिला है, वहाँ आसपास का कोड पढ़ें। किसी सिंबल का नाम मिलना एक सुराग है। इससे यह तय नहीं होता कि कोड आपकी डिपेंडेंसी के संस्करण से मेल खाता है या आपकी अपेक्षा के अनुसार काम करेगा।

GitHub कोड सर्च, Sourcegraph और स्थानीय चेकआउट में खोज के लिए अलग-अलग सामग्री उपलब्ध होती है। ऐसा टूल चुनें जिसे आपकी रिपॉज़िटरी तक पहुँच हो। यह मानकर न चलें कि किसी सार्वजनिक इंस्टेंस के इंडेक्स में हर रिपॉज़िटरी या उसका हर रिविज़न मौजूद है।

## खोज का दायरा और परिणाम की जाँच

![रिपॉज़िटरी और पथ चुनने के बाद मिली फ़ाइल का कोड और उसके परीक्षण पढ़ें](/assets/diagrams/technical/hi-2021-08-06-search-github.svg)

परिणामों की लंबी सूची देखने से पहले क्वेरी का दायरा सीमित करें। अगर किसी खास संस्करण का व्यवहार देखना है तो डिफ़ॉल्ट ब्रांच पर निर्भर रहने के बजाय वांछित रिविज़न खोलें या उसका स्थानीय चेकआउट खोजें।

## हर सेवा के लिए उसकी क्वेरी भाषा इस्तेमाल करें

[GitHub की कोड खोज क्वेरी](https://docs.github.com/en/search-github/github-code-search/understanding-github-code-search-syntax) में रिपॉज़िटरी, भाषा और पथ के फ़िल्टर के साथ उद्धरण चिह्नों में वाक्यांश लिख सकते हैं।

```text
repo:spring-projects/spring-framework language:java path:WebClient.java "interface WebClient"
```

इसी खोज के लिए [Sourcegraph के फ़िल्टर](https://sourcegraph.com/docs/code-search/queries) में रिपॉज़िटरी और फ़ाइल के नाम रेगुलर एक्सप्रेशन से तय होते हैं।

```text
repo:^github\.com/spring-projects/spring-framework$ lang:java file:WebClient\.java$ "interface WebClient"
```

| खोज का उद्देश्य | GitHub कोड सर्च | Sourcegraph |
| --- | --- | --- |
| रिपॉज़िटरी | `repo:owner/name` | `repo:` के साथ रेगुलर एक्सप्रेशन। पूरा नाम मिलाना हो तो शुरुआत और अंत के एंकर लगाएँ। |
| Java | `language:java` | `lang:java` या `language:java` |
| फ़ाइल का पथ | `path:` पथ फ़िल्टर | `file:` रेगुलर एक्सप्रेशन |
| हूबहू वाक्यांश | उद्धरण चिह्नों में वाक्यांश | कीवर्ड मोड में उद्धरण चिह्नों में वाक्यांश |

ये क्वेरी लिखने के उदाहरण हैं। लाइव खोज में कितने परिणाम मिलते हैं, इसकी गिनती नहीं की गई है। दोनों पथ फ़िल्टर के परिणाम अलग हो सकते हैं क्योंकि Sourcegraph वाला उदाहरण फ़ाइल नाम के अंत में मेल माँगता है। आपको क्या मिल सकता है, यह पहुँच, इंडेक्स की गई सामग्री और चुने हुए रिविज़न पर भी निर्भर करता है।

## खाली डायरेक्टरी में स्थानीय खोज दोहराएँ

इस छोटे उदाहरण के लिए Git और POSIX शेल चाहिए। `mkdir` जानबूझकर तब विफल होता है जब `demo-search` पहले से मौजूद हो, इसलिए नई कार्यशील डायरेक्टरी चुनें।

```sh
set -eu
mkdir demo-search
cd demo-search
git init -q
mkdir src docs
printf '%s\n' 'interface WebClient {}' > src/WebClient.java
printf '%s\n' 'interface WebClient is discussed here' > docs/notes.txt
git add src docs
git grep -n -F 'interface WebClient' -- src
```

आउटपुट

```text
src/WebClient.java:1:interface WebClient {}
```

यही वाक्यांश `docs/notes.txt` में भी है, लेकिन `-- src` खोज को src तक सीमित करता है। [`git grep -F`](https://git-scm.com/docs/git-grep) पैटर्न को अक्षरशः खोजता है और `-n` पंक्ति संख्या दिखाता है। वर्किंग ट्री में डिफ़ॉल्ट खोज केवल ट्रैक की गई फ़ाइलों को पढ़ती है, इसलिए फ़ाइलों को इंडेक्स में जोड़ा गया है। उदाहरण कोई कमिट नहीं बनाता। वास्तविक चेकआउट में खोजते समय नमूने का पथ और पैटर्न अपनी ज़रूरत के अनुसार बदलें और खोज की सीमा तय रखें।

मिले हुए कोड को अपनाने से पहले उसे कॉल करने वाला कोड, परीक्षण, लाइसेंस और रिविज़न देखें। वही घोषणा दूसरी रिलीज़ में अलग व्यवहार कर सकती है। क्लाइंट के अपेक्षित व्यवहार की पुष्टि के लिए [WebClient के जवाबों का परीक्षण](/hi/posts/2023-09-19-springboot-test-webclient/) देखें।
