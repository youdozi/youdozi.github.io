---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2026-11-27-mac-disk-cleanup-du-df",
  "routeSlug": "2026-11-27-mac-disk-cleanup-du-df",
  "kind": "post",
  "title": "Mac पर बिल्ड रुकने के बाद du और df से डिस्क की सफ़ाई का असर कैसे मापा",
  "description": "डायरेक्टरियों का उपयोग और डेटा वॉल्यूम पर उपलब्ध जगह अलग-अलग मापकर देखा कि मैनुअल सफ़ाई के बाद वास्तव में कितनी जगह बढ़ी।",
  "categories": [
    "tips"
  ],
  "tags": [
    "macos",
    "disk-usage",
    "git"
  ],
  "sourcePath": "src/content/posts/en/2026-11-27-mac-disk-cleanup-du-df.md",
  "sourceSha256": "2114224ef5dde962e3cfc28f12de1aa1dbba58c0343db9c3e8e6277ce204cc19",
  "draftSha256": "398bcb91386e362a730f5330317a09fb9bc3ca0f8a9cef71576c2298fc32014b",
  "manifestPath": ".pipeline/technical-translations/batch-1321/manifest.json",
  "manifestSha256": "90bf5396c64a63004b0a27d4cce1402231138b6f09e1e2fbfb748d8d008af607",
  "publishedAt": "2026-11-27T07:59:27.630Z",
  "updatedAt": "2026-11-27T07:59:27.630Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 208,
    "approvedAt": "2026-11-27T07:59:27.630Z",
    "basis": "User authorized publication of the five named Hindi technical editions in item 132 under plan 120."
  }
}
---

Mac पर जगह कम पड़ने से PostgreSQL जॉब कतार वाले लेख का स्थानीय बिल्ड पूरा नहीं हो सका। रिमोट जाँच सफल रही और GitHub Pages पर साइट भी डिप्लॉय हुई। पहले एक अन्य वर्कर ने `hostFault` की सूचना दी थी। वह इसी डिस्क समस्या का हिस्सा था या नहीं, इसकी पुष्टि नहीं हुई। [प्रकाशन का PR #202](https://github.com/youdozi/youdozi.github.io/pull/202)

## सफ़ाई के लिए कौन-सी डायरेक्टरी चुनीं?

बाद में अलग से मैनुअल सफ़ाई करते समय मैंने पूरे हो चुके कामों की 20 ऐसी डायरेक्टरी चुनीं जिन्हें फिर बनाया जा सकता था। इनमें बिल्ड से बनी `dist` और `.astro` तथा एक बार की जाँच में इस्तेमाल हुई निर्भरता और बिल्ड डायरेक्टरियाँ थीं। चल रहे कामों के पथ मैंने छोड़ दिए।

ये केवल पढ़ने वाले कमांड macOS पर ऐसी Git रिपॉज़िटरी की रूट डायरेक्टरी में चलाएँ जिसमें दोनों बिल्ड डायरेक्टरी मौजूद हों। `du` दिए गए हर पथ की खपत दिखाता है। `git ls-files` वहाँ Git द्वारा ट्रैक की जा रही फ़ाइलें दिखाता है और `git check-ignore` वे पथ बताता है जिन पर अनदेखा करने का नियम लागू होता है।

```sh
du -sh ./dist ./.astro
git ls-files -- dist .astro
git check-ignore -- dist .astro
```

Git जिस डायरेक्टरी को अनदेखा करता है उसमें भी अधूरा काम हो सकता है। किसी डायरेक्टरी को हटाने के लिए चुनने से पहले मैंने जाँचा कि उसे फिर बनाया जा सकता है और अभी कोई काम उसका उपयोग नहीं कर रहा है।

## कितनी जगह खाली हुई?

![चुनी गई डायरेक्टरियों की खपत और सफ़ाई के पहले व बाद में डेटा वॉल्यूम पर उपलब्ध जगह को अलग-अलग मापने का क्रम।](/assets/diagrams/technical/hi-2026-11-27-mac-disk-cleanup-du-df.svg)

चुनी गई डायरेक्टरियों की कुल खपत 1.61 GiB थी। उसी डेटा वॉल्यूम पर सफ़ाई से पहले 6.41 GiB और बाद में 7.46 GiB जगह उपलब्ध थी। यानी लगभग 1.05 GiB जगह बढ़ी।

नीचे का कमांड चलाकर सफ़ाई से पहले और बाद का `Avail` कॉलम देखें। `df` उस फ़ाइलसिस्टम पर उपलब्ध जगह बताता है जिसमें दिया गया पथ है। APFS में एक कंटेनर के कई वॉल्यूम उसकी खाली जगह साझा कर सकते हैं। इस मामले में डायरेक्टरियों की कुल खपत और उपलब्ध जगह में हुई वृद्धि अलग क्यों थीं, यह तय नहीं हो सका। [APFS में जगह साझा करने पर Apple की गाइड](https://support.apple.com/ko-kr/guide/security/seca6147599e/web)

```sh
df -h /System/Volumes/Data
```
