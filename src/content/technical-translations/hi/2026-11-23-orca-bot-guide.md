---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2026-11-23-orca-bot-guide",
  "routeSlug": "2026-11-23-orca-bot-guide",
  "kind": "post",
  "title": "Orca Bot का उपयोग — ब्लॉग बॉट बनाएँ, काम जाँचें और आवर्ती कार्य तय करें",
  "description": "Orca Bot को पहला काम दें, उसकी मेमोरी और काम की स्थिति जाँचें और बार-बार चलने वाले कार्य सेट करें।",
  "categories": [
    "util"
  ],
  "tags": [
    "orca",
    "ai-agent",
    "automation",
    "developer-tools"
  ],
  "sourcePath": "src/content/posts/en/2026-11-23-orca-bot-guide.md",
  "sourceSha256": "96033cbac131a6cad800f9782a2ad820fcfba2e710c8628bb440b0af0c898e02",
  "draftSha256": "3b3c2201ba715c67ae53d50942805e5a45a11a564834f5575305fb60a251fdbb",
  "manifestPath": ".pipeline/technical-translations/batch-139/manifest.json",
  "manifestSha256": "0cc88a23412afe4afe8035992a38c4aa4c53a00a07184c1b7722f6376e8de0a4",
  "publishedAt": "2026-11-27T10:26:18.984Z",
  "updatedAt": "2026-11-27T10:26:18.984Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 215,
    "approvedAt": "2026-11-27T10:26:18.984Z",
    "basis": "The owner requested publication of these five Hindi editions in item 139. The translation and diagrams were self-reviewed against the Korean and English editions."
  }
}
---

**पहला Orca Bot बना रहे हैं तो आवर्ती काम तय करने से पहले उसे कोई ऐसा काम दें जिसका परिणाम आप खुद जाँच सकें।** मसलन, एक छोटा तकनीकी नोट देकर ब्लॉग का शीर्षक और रूपरेखा माँगें। परिणाम मनचाहे प्रारूप में आए तो बॉट की भूमिका और स्पष्ट करें और आवर्ती कार्य जोड़ें। यहाँ यही प्रक्रिया ब्लॉग का मसौदा तैयार करने वाले बॉट के साथ देखेंगे।

Orca Bot के पास नाम, उद्देश्य और मेमोरी होती है। वह किस कंप्यूटर पर और किस एजेंट के साथ चलेगा, यह चुनें। Claude Code या Codex जैसे चुने गए एजेंट को उस कंप्यूटर पर स्थापित करके लॉगिन करें। पहला अभ्यास Orca के अंदर ही होता है। Slack, GitHub या Linear से बॉट बुलाने या उन सेवाओं की घटनाओं पर उसे चलाने के लिए संबंधित कनेक्शन जोड़ें। [Orca Bots की शुरुआत](https://orca.dev/docs/bots) · [Orca बॉट कनेक्टर](https://orca.dev/docs/bots/connectors)

![बॉट बनाकर पहला काम दें। परिणाम जाँचें और ज़रूरत हो तो Needs you में निर्णय लें। आवर्ती काम के लिए समय या घटना तय करें और रन का परिणाम देखें।](/assets/diagrams/technical/hi-2026-11-23-orca-bot-guide.svg)

## बॉट बनाएँ और पहला अनुरोध भेजें

Orca के साइडबार में **Bots** के अंदर **+ → New bot → Start from scratch** चुनें। नाम दें और **Who it is and what it does** में उसकी भूमिका एक वाक्य में लिखें। उदाहरण में नाम `Blog Draft` और उद्देश्य है “विकास संबंधी नोट से तकनीकी ब्लॉग का मसौदा बनाना।” नाम के नीचे कंप्यूटर और एजेंट देखकर **Create** चुनें। साइडबार में Bots न दिखे तो **Settings → Bots → Enable bots** देखें। [Orca में बॉट बनाने की गाइड](https://orca.dev/docs/bots)

बॉट की चैट में इनपुट और परिणाम का वांछित प्रारूप साथ दें। मूल कोरियाई अभ्यास में कोरियाई भाषा का तकनीकी मसौदा माँगा गया था। नीचे का नोट लेखन अभ्यास के लिए काल्पनिक सामग्री है।

```text
Prepare a technical blog draft from the following practice note.

Note
- A Java service calls an external API.
- Tests checked a successful response and a 404 response.
- Production latency was not measured.

Suggest one title, one introductory paragraph, and three headings.
Do not add versions or performance figures absent from the note.
At the end, list anything that needs checking before writing the body.
Show the result in this chat.
```

उत्तर में देखें कि दावा 404 प्रतिक्रिया जाँचे जाने तक सीमित है। यदि कोई नया संस्करण या थ्रूपुट का आँकड़ा जोड़ा गया है तो उसे हटाएँ या उसका आधार माँगें। पहले अनुरोध की सफलता का मानदंड नोट पर आधारित शीर्षक, परिचय और उपशीर्षक मिलना है। मसौदा इसी चरण में प्रकाशन के लिए तैयार होना ज़रूरी नहीं है।

## अगली चैट के नियम और मौजूदा काम कहाँ देखें?

| कहाँ देखें | क्या रखें | ब्लॉग बॉट का उदाहरण |
| --- | --- | --- |
| `SOUL.md` | स्थायी भूमिका और काम करने का तरीका | तथ्यों का आधार आधिकारिक दस्तावेज़ों से जाँचें और प्रकाशन के लिए अलग अनुरोध की प्रतीक्षा करें |
| `MEMORY.md` | अगली बातचीत में काम आने वाले तथ्य और प्राथमिकताएँ | पाठक Java डेवलपर हैं और चलने योग्य उदाहरण पसंद करते हैं |
| **Home** में कार्य मद | मौजूदा प्रगति, संलग्न परिणाम और मंज़ूरी के लिए रुके निर्णय | नया मसौदा समीक्षा की प्रतीक्षा में है |

दोनों Markdown फ़ाइलें बॉट के फ़ोल्डर में होती हैं। आप कह सकते हैं, “आगे के उदाहरणों में खुद चलाकर मिले परिणाम और अपेक्षित परिणाम अलग लिखना।” फिर देखें कि अगली बार भी बॉट इसका पालन करता है या नहीं। मौजूदा काम पूरा हुआ या नहीं जानने के लिए उसकी कार्य मद खोलें। निर्णय चाहिए तो **Needs you** में प्रश्न और उसके परिणाम समझकर उत्तर दें। [Orca Bots का उपयोग](https://orca.dev/docs/bots) · [बॉट की मेमोरी और पहुँच](https://orca.dev/docs/bots/security)

रिपॉज़िटरी में कोड बदलने को कहने पर बॉट अलग Git worktree में काम करने वाले वर्कर को कार्य सौंप सकता है। साइडबार से वर्कर का कार्यक्षेत्र खोलकर फ़ाइलें और परीक्षण देखें। PR बने तो वास्तविक बदलाव जाँचें। [बॉट वर्कर की गाइड](https://orca.dev/docs/bots) · [Orca worktree की गाइड](/en/posts/2026-11-12-orca-worktree-guide/)

## आवर्ती काम की शर्त और परिणाम मिलने की जगह तय करें

पहला काम संतोषजनक हो तो बॉट की चैट में नीचे जैसा अनुरोध दें। यह उदाहरण सार्वजनिक दस्तावेज़ पढ़कर केवल लेख के विषय इकट्ठे करता है।

```text
Every Monday at 9:00 a.m. Korea time, select up to three technical
article ideas from official Spring Boot releases announced in the
previous seven days. For each candidate, include the announcement date,
official link, and a question to explore in an exercise.
If there were no announcements, say so.
Make the result available to me in Orca; do not publish it to the blog.
Also tell me which conversation the automation will leave its result in.
```

ऑटोमेशन बनने पर बॉट पैनल में **समय क्षेत्र, शुरू होने की शर्त और परिणाम का गंतव्य** जाँचें। तय समय के बजाय नए GitHub PR जैसी घटना पर चलाना हो तो पहले देखें कि संबंधित कनेक्टर जुड़ा है और घटना का समर्थन करता है। बॉट का कंप्यूटर स्लीप मोड में या ऑफ़लाइन हो तो काम तय समय पर तुरंत नहीं चल सकता। पहले रन का परिणाम ऑटोमेशन के रन इतिहास में देखें। [Orca ऑटोमेशन गाइड](https://orca.dev/docs/bots) · [Orca कनेक्टर गाइड](https://orca.dev/docs/bots/connectors)

macOS में CLI स्थापित हो तो नीचे के कमांड बॉट के नाम और उपलब्ध घटनाएँ दिखाते हैं। दूसरी पंक्ति में उदाहरण की जगह अपने बॉट का नाम दें।

```sh
orca bot list
orca automations trigger-options --bot 'Blog Draft'
```

लेखन के समय **Orca CLI 1.4.271** पर एक मौजूदा बॉट के साथ दोनों केवल-पढ़ने वाले कमांड जाँचे गए। जिस बॉट से GitHub नहीं जुड़ा था उसके परिणाम में दिखा कि GitHub की घटनाएँ उसे शुरू नहीं कर सकतीं। उदाहरण का नाम और नोट काल्पनिक हैं। इस लेख के लिए नया बॉट या ऑटोमेशन बनाकर नहीं चलाया गया। अपने संस्करण की CLI गाइड `orca skills get orca-cli --reference bots` से पढ़ें।
