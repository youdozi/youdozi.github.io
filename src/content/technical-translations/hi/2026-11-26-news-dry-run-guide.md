---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2026-11-26-news-dry-run-guide",
  "routeSlug": "2026-11-26-news-dry-run-guide",
  "kind": "post",
  "title": "GitHub Actions में समाचार ड्राफ़्ट प्रकाशित किए बिना उसकी जाँच कैसे करें?",
  "description": "अलग-अलग जाँचें कि ड्राफ़्ट ने सत्यापन पास किया और रन के बाद पांडुलिपि, प्रकाशन कतार और स्थिति फ़ाइलें पहले जैसी हैं।",
  "categories": [
    "blog"
  ],
  "tags": [
    "github-actions",
    "ci",
    "dry-run"
  ],
  "sourcePath": "src/content/posts/en/2026-11-26-news-dry-run-guide.md",
  "sourceSha256": "bbd2b23eadacc9df77585d34bf7ba6243a6a849fbbfcba51c6f2272b35553659",
  "draftSha256": "302cec5128002682f1761ffc37aa8d40936007c1145a097553a7a7369f01d97f",
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

ड्राफ़्ट स्कीमा की जाँच पास कर सकता है, लेकिन अगर रन ने प्रकाशन कतार में प्रविष्टि जोड़ दी तो ड्राई रन विफल रहा। इसलिए परीक्षण में दो सवाल अलग-अलग जाँचते हैं। क्या इस इनपुट का अपेक्षित निकास कोड मिला? क्या रन से पहले और बाद में पांडुलिपि, कतार और स्थिति फ़ाइलें एक जैसी हैं?

## सफल पूर्वावलोकन और विफल जाँच दोनों आज़माएँ

रिपॉज़िटरी की रूट डायरेक्टरी से Python 3 के साथ यह कमांड चलाएँ। दोनों परीक्षण अस्थायी डायरेक्टरी बनाते हैं और फ़ीड, ड्राफ़्ट बनाने और लिंक जाँचने के लिए पहले से तैयार परीक्षण डेटा इस्तेमाल करते हैं। इन्हें नेटवर्क या मॉडल की API कुंजी की ज़रूरत नहीं है।

```sh
PYTHONPATH=scripts python3 -B -m unittest \
  test_bilingual_digest.PublicationTests.test_preview_validates_without_writing_content_or_state \
  test_bilingual_digest.PublicationTests.test_ai_or_link_failures_do_not_write
```

![परीक्षण इनपुट के दो रास्ते हैं। सही पूर्वावलोकन सफल होता है और AI या लिंक की त्रुटि पर जाँच विफल होती है। दोनों रास्तों में जाँचा जाता है कि पांडुलिपि और स्थिति की डायरेक्टरी नहीं बनीं।](/assets/diagrams/technical/hi-2026-11-26-news-dry-run-guide.svg)

पहला परीक्षण `--dry-run --force` देकर निकास कोड 0 और `generated=false` जाँचता है। दूसरा `--check-links` देता है और अलग-अलग मामलों में AI त्रुटि और लिंक त्रुटि पैदा करके दोनों बार निकास कोड 1 जाँचता है। अस्थायी रूट में `src` या `.pipeline` बन जाए तो दोनों परीक्षण विफल होते हैं। ऊपर का कमांड चलाने पर `Ran 2 tests` और `OK` मिले।

## स्थानीय रन में Spring के मूल लेख से क्या जाँचा गया?

एक अलग स्थानीय रन के लिए [Spring AI टीम का एक लेख](https://spring.io/blog/2026/11/24/spring-ai-tool-call-confirmation-park-resume) लिया गया। अलग-थलग परीक्षण में `--dry-run --force --max-items 1 --check-links` दिया गया। केवल ड्राफ़्ट बनाने और उसकी समीक्षा करने वाले Gemini के जवाबों की जगह तैयार डेटा दिया गया था। CLI में केवल ये फ़्लैग देने से परीक्षण डेटा अपने आप नहीं मिलता।

मूल लेख HTTP 200 के साथ मिला। लिंक जाँचने के बाद कोरियाई और अंग्रेज़ी ड्राफ़्ट के कुल 4 उद्धरणों का वास्तविक लेख से मिलान किया गया। सामग्री ने Python और Astro दोनों के स्कीमा की जाँच पास की। आउटपुट `generated=false` था। अलग से की गई तुलना में पांडुलिपि, कतार और स्थिति की सभी 3,333 फ़ाइलों के पथ और सामग्री रन से पहले और बाद में समान थे। इस रन में वास्तविक Gemini सेवा की उपलब्धता या उसके आउटपुट की गुणवत्ता की जाँच नहीं हुई। [स्थानीय रन का रिकॉर्ड](https://github.com/youdozi/youdozi.github.io/pull/198)

## PR की जाँच करने वाले जॉब की अनुमतियाँ सीमित रखें

उस PR के सामान्य CI रन में आवश्यक `build / build` जाँच सफल हुई और `deploy` चरण छोड़ दिया गया। Spring के वास्तविक लेख से किए गए मिलान का परिणाम ऊपर दिए स्थानीय रन के रिकॉर्ड में है। [PR की जाँच के परिणाम](https://github.com/youdozi/youdozi.github.io/actions/runs/45734945701) · [साफ़ चेकआउट पर Astro की जाँच क्यों विफल हुई?](https://youdozi.github.io/hi/posts/2026-11-26-astro-clean-checkout/)

अलग सत्यापन जॉब जोड़ें तो चेकआउट को केवल `contents: read` दें और प्रकाशन के क्रेडेंशियल साझा न करें। केवल पढ़ने की अनुमति वाला रिपॉज़िटरी टोकन भी रनर को अपनी स्थानीय फ़ाइलें बदलने से नहीं रोकता। इसलिए रन से पहले और बाद में पांडुलिपि, कतार और स्थिति फ़ाइलों की तुलना फिर भी करें। [GitHub में जॉब के टोकन](https://docs.github.com/en/actions/concepts/security/github_token)
