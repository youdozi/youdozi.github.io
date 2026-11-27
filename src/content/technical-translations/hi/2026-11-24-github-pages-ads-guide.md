---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2026-11-24-github-pages-ads-guide",
  "routeSlug": "2026-11-24-github-pages-ads-guide",
  "kind": "post",
  "title": "GitHub Pages ब्लॉग पर विज्ञापन कैसे लगाएँ — सेवा चुनने से AdSense सेटअप तक",
  "description": "GitHub Pages पर विज्ञापन सेवा चुनें, AdSense और रूट ads.txt सेट करें और साइट समीक्षा तथा विज्ञापन की स्थिति अलग-अलग जाँचें। सेवा शर्तों का संदर्भ 24 नवंबर 2026 का है।",
  "categories": [
    "tips"
  ],
  "tags": [
    "github-pages",
    "adsense",
    "ads-txt"
  ],
  "sourcePath": "src/content/posts/en/2026-11-24-github-pages-ads-guide.md",
  "sourceSha256": "884b5c639b2345ac6daac6b307db2cd0ec22e80801c8d5d2d5860b4ba12356d8",
  "draftSha256": "f4b336df75de24e61302d3002626e5d04362036a6f8fecf5506683a295781e49",
  "manifestPath": ".pipeline/technical-translations/batch-140/manifest.json",
  "manifestSha256": "ee8a891ee0726eb23d009f33d7c051a5323f082fec373455d5e19f789a46b55c",
  "publishedAt": "2026-11-27T10:44:09.638Z",
  "updatedAt": "2026-11-27T10:44:09.638Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 216,
    "approvedAt": "2026-11-27T10:44:09.638Z",
    "basis": "The owner authorized publication of the five Hindi editions in item 140. Translation and diagram review was performed by the translator."
  }
}
---

`username.github.io` पर तकनीकी ब्लॉग चलाते हैं तो Google AdSense से शुरुआत कर सकते हैं। नियमित डेवलपर पाठक हों तो Carbon Ads और EthicalAds भी विकल्प हैं। आवेदन से पहले देखें कि आप `https://username.github.io/ads.txt` प्रकाशित कर सकते हैं या नहीं, ख़ासकर यदि प्रोजेक्ट का पता `username.github.io/blog/` जैसा हो। नीचे की सेवा शर्तें मूल लेख में प्रकाशन के समय की गई जाँच के अनुसार हैं।

GitHub सामग्री प्रकाशित करने वाली साइटों पर सामान्यतः विज्ञापन प्रतिबंधित नहीं करता। GitHub Pages को ऑनलाइन व्यवसाय, ई-कॉमर्स या व्यावसायिक SaaS की मुफ़्त होस्टिंग की तरह इस्तेमाल करने पर सीमाएँ हैं। तकनीकी ब्लॉग में विज्ञापन जोड़ते समय दोनों नीतियाँ पढ़ें। [GitHub की विज्ञापन नीति](https://docs.github.com/en/site-policy/acceptable-use-policies/github-acceptable-use-policies#10-advertising-on-github) · [GitHub Pages की सीमाएँ](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)

## कौन सी विज्ञापन सेवा चुनें?

| सेवा | किस साइट के लिए | आवेदन |
| --- | --- | --- |
| **Google AdSense** | पहली बार विज्ञापन लगाने वाला निजी ब्लॉग, जहाँ स्थान खुद चुनना हो या अपने आप तय होने देना हो | [AdSense शुरू करें](https://adsense.google.com/start/) |
| **Carbon Ads** | डेवलपर और डिज़ाइनर जिनके लेख, दस्तावेज़ या टूल इस्तेमाल करते हैं। आवेदन के लिए हर महीने कम से कम 10,000 पेजव्यू चाहिए। Carbon के साथ दूसरा विज्ञापन नेटवर्क चलाने की अनुमति नहीं है। | [Carbon Ads का आवेदन](https://www.carbonads.net/join?_hsmi=83378591) |
| **EthicalAds** | डेवलपर-केंद्रित साइट जिसमें कम से कम 50,000 मासिक पेजव्यू हों और पढ़ने के प्रवाह से बाहर एक विज्ञापन के लिए जगह हो | [EthicalAds प्रकाशक गाइड](https://www.ethicalads.io/publisher-guide/) |

पहले स्थान चुनें। बहुत से कोड उदाहरण वाले ब्लॉग में लेख के नीचे एक AdSense विज्ञापन खुद रखकर मोबाइल पर उसका असर देख सकते हैं। AdSense में **ad units** की जगह आप तय करते हैं और **Auto ads** की जगह Google चुनता है। EthicalAds के अपने नियम हैं। डेस्कटॉप और मोबाइल पर उसका विज्ञापन स्क्रॉल किए बिना दिखना चाहिए। मोबाइल पर यह संभव न हो तो वहाँ विज्ञापन बंद करें। [AdSense विज्ञापन सेटिंग्स](https://support.google.com/adsense/answer/7037624)

![AdSense का कोड जोड़ें, होस्ट के रूट पर ads.txt प्रकाशित करें, सार्वजनिक URL जाँचें और फिर साइट की समीक्षा माँगें।](/assets/diagrams/technical/hi-2026-11-24-github-pages-ads-guide.svg)

चित्र सेटअप से समीक्षा के अनुरोध तक का क्रम दिखाता है। वास्तविक विज्ञापन दिख रहा है या नहीं, इसकी जाँच अलग है।

## 1. AdSense खाता बनाएँ और साइट जोड़ें

Google खाते से साइन अप करें और भुगतान का देश व भुगतान संबंधी जानकारी भरें। **Sites → New site** में `https://username.github.io` जोड़ें। Public Suffix List में `github.io` शामिल है। AdSense के अनुसार सूची में शामिल प्लेटफ़ॉर्म का सबडोमेन साइट के रूप में जोड़ा जा सकता है। इसके बाद स्वामित्व की पुष्टि और साइट की समीक्षा होती है। [AdSense खाता बनाएँ](https://support.google.com/adsense/answer/7402253) · [AdSense में साइट जोड़ने के मानदंड](https://support.google.com/adsense/answer/12170421) · [Public Suffix List](https://publicsuffix.org/list/public_suffix_list.dat)

पता जाँचें। GitHub Pages की उपयोगकर्ता साइट `username.github.io/` पर और प्रोजेक्ट साइट आम तौर पर `username.github.io/blog/` पर होती है। प्रोजेक्ट के साथ प्रकाशित की गई `ads.txt` फ़ाइल `/blog/ads.txt` पर पहुँच सकती है। Google होस्ट के रूट `/ads.txt` से तलाश शुरू करता है। फ़ाइल उपयोगकर्ता साइट से प्रकाशित करें या ब्लॉग से जुड़े कस्टम डोमेन के रूट पर रखें। [GitHub Pages साइटों के प्रकार](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages#types-of-github-pages-sites) · [Google ads.txt कैसे खोजता है](https://support.google.com/adsense/answer/7679060)

## 2. साझा `<head>` में एक स्क्रिप्ट और रूट पर एक `ads.txt` रखें

AdSense स्वामित्व की पुष्टि के लिए कोड स्निपेट, `ads.txt` या मेटा टैग का विकल्प देता है। स्निपेट चुनें तो डैशबोर्ड से मिला कोड साझा लेआउट के `<head>` में रखें। नीचे केवल उसका प्रारूप है। वास्तविक परिनियोजन में अपने खाते से कॉपी किया हुआ कोड इस्तेमाल करें। [साइट को AdSense से जोड़ें](https://support.google.com/adsense/answer/7584263)

```html
<script async
  src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-0000000000000000"
  crossorigin="anonymous"></script>
```

डैशबोर्ड पर दी गई पंक्ति `ads.txt` में कॉपी करें। यह फ़ाइल उन खातों की पहचान करती है जिन्हें आपकी साइट का विज्ञापन स्थान बेचने की अनुमति है। मौजूदा विक्रेताओं की पंक्तियाँ बनाए रखते हुए नई पंक्ति जोड़ें।

```text
google.com, pub-0000000000000000, DIRECT, f08c47fec0942fa0
```

Astro की उपयोगकर्ता साइट में फ़ाइल `public/ads.txt` पर रखें। Astro, `public/` की फ़ाइलें बिल्ड आउटपुट में कॉपी करता है। परिनियोजन के बाद रिपॉज़िटरी के साथ सार्वजनिक URL भी जाँचें। [Astro की `public/` डायरेक्टरी](https://docs.astro.build/en/guides/images/#src-vs-public) · [Google की ads.txt गाइड](https://support.google.com/adsense/answer/12171612)

```bash
curl -fsSL https://username.github.io/ads.txt
```

अपेक्षित आउटपुट ऊपर दिखाई गई विक्रेता पंक्ति है। वास्तविक साइट से उसके खाते की प्रकाशक आईडी मिलनी चाहिए। `username` उदाहरण का पता है, इसलिए यह चलाकर देखा गया परिणाम नहीं है।

एक ही होस्ट के बहुभाषी ब्लॉग के लिए रूट पर एक फ़ाइल पर्याप्त है। `/ko/` और `/en/` के लिए अलग फ़ाइलें नहीं चाहिए। हर भाषा का एक प्रतिनिधि लेख चुनकर उसके अंतिम HTML में देखें कि साझा लोडर केवल एक बार आता है।

## 3. परिनियोजन, समीक्षा और विज्ञापन दिखने की अलग-अलग जाँच करें

फ़ाइल और कोड प्रकाशित करने के बाद AdSense में स्वामित्व सत्यापित करें और साइट समीक्षा का अनुरोध करें। साइट की स्थिति **`Ready`** होने का अर्थ है कि वह विज्ञापन दिखाने के लिए तैयार है। ads.txt की स्थिति **`Authorized`** होने का अर्थ है कि Google को फ़ाइल में प्रकाशक आईडी मिली। सार्वजनिक URL खुल रहा हो और डैशबोर्ड फिर भी `Not found` दिखाए तो देखें कि बदलाव पिछली क्रॉल के बाद हुआ था या नहीं। पथ और सामग्री सही हों तो **Check for updates** से फिर जाँच का अनुरोध करें। [साइट की स्थिति](https://support.google.com/adsense/answer/12170222) · [ads.txt की स्थिति](https://support.google.com/adsense/answer/12171612)

विज्ञापन चालू करने से पहले गोपनीयता नीति में बताएँ कि विज्ञापन के लिए कौन सी जानकारी एकत्र या साझा की जाती है और कुकी जैसी कौन सी तकनीक इस्तेमाल होती है। EEA, यूके और स्विट्ज़रलैंड के आगंतुकों को वैयक्तिकृत विज्ञापन दिखाने के लिए Google-प्रमाणित सहमति प्रबंधन प्लेटफ़ॉर्म (CMP) चाहिए जो IAB Transparency and Consent Framework (TCF) से जुड़ा हो। AdSense के **Privacy & messaging** में यूरोपीय नियमों वाला संदेश एक विकल्प है। [प्रकाशकों के लिए Google की गोपनीयता नीति](https://support.google.com/adsense/answer/10502938) · [Google की CMP आवश्यकताएँ](https://support.google.com/adsense/answer/13554116)

समीक्षा के बाद Auto ads के प्रीव्यू या मैन्युअल ad unit से स्थान जाँचें। फ़ोन पर देखें कि विज्ञापन विषय-सूची, कोड कॉपी बटन या भाषा मेन्यू को ढकता तो नहीं। जाँच के लिए अपने विज्ञापन पर क्लिक न करें। प्रीव्यू और डैशबोर्ड रिपोर्ट इस्तेमाल करें। [Auto ads का प्रीव्यू](https://support.google.com/adsense/answer/9261307) · [अमान्य ट्रैफ़िक](https://support.google.com/adsense/answer/16737)

मूल लेख की जाँच में `youdozi.github.io` के सार्वजनिक रूट पर `ads.txt` और कोरियाई होमपेज के HTML में एक AdSense स्क्रिप्ट मिली थी। यह अवलोकन सार्वजनिक फ़ाइल और HTML तक सीमित था। खाते की समीक्षा और वास्तविक विज्ञापन वितरण की स्थिति अलग से सत्यापित करनी होती है। [सार्वजनिक ads.txt](https://youdozi.github.io/ads.txt) · [कोरियाई होमपेज](https://youdozi.github.io/ko/)
