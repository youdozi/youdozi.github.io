---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2026-11-26-astro-clean-checkout",
  "routeSlug": "2026-11-26-astro-clean-checkout",
  "kind": "post",
  "title": "Astro की जाँच सिर्फ़ साफ़ चेकआउट पर क्यों विफल हुई?",
  "description": "पुराने लेखों के चित्रों का आकार पढ़ने और SVG बनने का क्रम जाँचकर समाचार ड्राफ़्ट के CI में ENOENT त्रुटि दोहराई गई।",
  "categories": [
    "blog"
  ],
  "tags": [
    "astro",
    "github-actions",
    "ci",
    "svg"
  ],
  "sourcePath": "src/content/posts/en/2026-11-26-astro-clean-checkout.md",
  "sourceSha256": "e1cc192ccc59b4557362e39f19838911c05e42d35d855acc766381023844e6e8",
  "draftSha256": "2650235fef2b9018f6e624ea5900c67cfd2a15f2d1b340e628db699d8fc06603",
  "manifestPath": ".pipeline/technical-translations/batch-121/manifest.json",
  "manifestSha256": "18418f70555c5976554979bde0a5e1400056aafa333f4babd737559a8d6eaaad",
  "publishedAt": "2026-11-27T02:40:54.030Z",
  "updatedAt": "2026-11-27T02:40:54.030Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 205,
    "approvedAt": "2026-11-27T02:40:54.030Z",
    "basis": "Item 121 explicitly requests publication of these three Hindi editions."
  }
}
---

समाचार का ड्राफ़्ट तैयार करने वाला वर्कफ़्लो `ENOENT` त्रुटि पर रुक गया। जाँची गई 4 विफलताओं में से 3 तब हुईं जब Astro ने मौजूदा लेखों में लगे चित्रों का आकार पढ़ने की कोशिश की। साफ़ चेकआउट में उन लेखों की SVG फ़ाइलें अभी बनी नहीं थीं। पिछले बिल्ड से बची स्थानीय कॉपी होने पर वही जाँच सफल हो सकती थी। [वह रन जिसमें ड्राफ़्ट की जाँच रुकी](https://github.com/youdozi/youdozi.github.io/actions/runs/45548722494)

## SVG बनाने से पहले और बाद में एक ही जाँच चलाएँ

जिस कमिट पर जाँच विफल हुई थी, उसे एक अलग डायरेक्टरी में चेकआउट किया। वहाँ `npm run check` का निकास कोड 1 था। उसी डायरेक्टरी में `node scripts/prepare-public.mjs` से सार्वजनिक फ़ाइलें तैयार करने के बाद वही जाँच निकास कोड 0 के साथ पूरी हुई। बिल्ड भी ये फ़ाइलें तैयार करता है, लेकिन CI में जाँच पहले चलती थी।

![साफ़ चेकआउट से शुरू करें, SVG बनाएँ, Astro को उनके आयाम पढ़ने दें और फिर साइट बिल्ड करें।](/assets/diagrams/technical/hi-2026-11-26-astro-clean-checkout.svg)

CI के चरण दोहराने के लिए रिपॉज़िटरी की रूट डायरेक्टरी में Node.js 24 और Python 3.11 का उपयोग करें। `npm ci` से निर्भरताएँ इंस्टॉल करने के बाद ये कमांड चलाएँ। हर चरण सफल होने पर ही अगला शुरू होता है। [सुधार का पुल अनुरोध](https://github.com/youdozi/youdozi.github.io/pull/198) · [पुल अनुरोध का बिल्ड परिणाम](https://github.com/youdozi/youdozi.github.io/actions/runs/45734945701)

```sh
node scripts/prepare-public.mjs &&
  npm run check &&
  npm run build
```

## सामग्री बनाते समय Gemini की अलग विफलता

एक अन्य रन में सामग्री बनाते समय Gemini ने HTTP 503 लौटाया। सुधार के बाद उसी मॉडल पर पहले पुनःप्रयास से पहले 1 सेकंड और दूसरे से पहले 2 सेकंड का इंतज़ार होता है। पूरे रन के सभी अनुरोधों के लिए कुल दो पुनःप्रयास उपलब्ध हैं। [वह रन जिसमें सामग्री बनाना विफल हुआ](https://github.com/youdozi/youdozi.github.io/actions/runs/45098322259)

Spring के आधिकारिक लेख पर आधारित कोरियाई और अंग्रेज़ी ड्राफ़्ट के परीक्षण में केवल सामग्री बनाने और समीक्षा करने वाले मॉडल के जवाब नकली थे। उद्धरणों का मिलान वास्तविक लेख से किया गया, लिंक जाँचे गए और सामग्री को Python और Astro दोनों के स्कीमा से सत्यापित किया गया। इस परीक्षण ने ड्राफ़्ट या कतार में कुछ नहीं लिखा। उस समय Gemini वास्तविक अनुरोधों का जवाब दे पा रहा था या नहीं, इसकी जाँच नहीं हुई।

यदि जाँच केवल स्थानीय कॉपी में सफल होती है, तो साफ़ चेकआउट में वह पहली कमांड ढूँढ़ें जो गुम फ़ाइल को पढ़ती है। देखें कि फ़ाइल बनाने वाला चरण उसके पहले चलता है या बाद में। इससे पता चल सकता है कि पूरा बिल्ड सफल होने पर भी उससे पहले की CI जाँच क्यों रुकती है।
