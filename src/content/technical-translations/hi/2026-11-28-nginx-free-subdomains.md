---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2026-11-28-nginx-free-subdomains",
  "routeSlug": "2026-11-28-nginx-free-subdomains",
  "kind": "post",
  "title": "घर पर Nginx चलाने के लिए चार मुफ़्त सबडोमेन सेवाएँ",
  "description": "घर का IP बदलता हो, डेवलपर पोर्टफ़ोलियो बनाना हो या अपना DNS ज़ोन सँभालना हो, तो नाम चुनने का आधार अलग होगा।",
  "categories": [
    "tips"
  ],
  "tags": [
    "self-hosting",
    "nginx",
    "dns"
  ],
  "sourcePath": "src/content/posts/en/2026-11-28-nginx-free-subdomains.md",
  "sourceSha256": "d11db302c4d9595bd30ea32d7d5c2c2ec680a9c318001ba16e333085dbec5f2e",
  "draftSha256": "53bd4b6b9983a422b13237a392b1ba8fa74c998c72cec551e7bbdfd1c40756f2",
  "manifestPath": ".pipeline/technical-translations/batch-1572/manifest.json",
  "manifestSha256": "075a6cd47b18e2ad7dfdf66b1c1d4074b358747fa12daa35f11394ad860e6063",
  "publishedAt": "2026-11-28T04:45:09.805Z",
  "updatedAt": "2026-11-28T04:45:09.805Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 229,
    "approvedAt": "2026-11-28T04:45:09.805Z",
    "basis": "Explicit item 157 publication approval for both item 155 and 156 follow-up guides in all nine site languages."
  }
}
---

घर पर Nginx चल रहा है। अब आप आगंतुकों को कौन-सा नाम देंगे? ये चारों सेवाएँ अपने डोमेन के तहत मुफ़्त सबडोमेन देती हैं। सर्वर चलाने और बाहर से उस तक पहुँच की व्यवस्था आपको करनी होगी।

## क्या सर्वर तक दूसरे नेटवर्क से पहुँचा जा सकता है?

DDNS उस IP पते को अपडेट करता है जो DNS लौटाता है। अनुरोध Nginx तक पहुँचेगा या नहीं, यह इंटरनेट कनेक्शन, राउटर और फ़ायरवॉल पर निर्भर है। अगर सेवा प्रदाता CGNAT इस्तेमाल करता है, तो सिर्फ़ घरेलू राउटर पर पोर्ट फ़ॉरवर्ड करना काफ़ी नहीं भी हो सकता है। WAN पता `100.64.0.0/10` की सीमा में हो तो प्रदाता से पूछें कि क्या वह सार्वजनिक IPv4 देता है। [RFC 6598](https://www.rfc-editor.org/info/rfc6598/)

## नाम सँभालने के तरीके के आधार पर चुनें

| सेवा | नाम कैसे सँभालें | कहाँ उपयोगी है |
| --- | --- | --- |
| [Duck DNS](https://www.duckdns.org/spec.jsp) | अपडेट क्लाइंट `name.duckdns.org` का पता अद्यतन रखता है। API अपने आप IPv4 पहचान सकता है। IPv6 अपडेट करते समय पता स्पष्ट रूप से दें। | बदलते सार्वजनिक IPv4 पर पहला अभ्यास। |
| [dynv6](https://dynv6.com/) · [API](https://dynv6.com/docs/apis) | होस्टनाम मिलता है और API से A व AAAA रिकॉर्ड तथा IPv6 प्रीफ़िक्स अपडेट कर सकते हैं। | IPv6 या ड्युअल स्टैक। एंटरप्राइज़ SLA उपलब्ध नहीं है। |
| [is-a.dev](https://github.com/is-a-dev/register#-register) | समीक्षा के लिए GitHub पर पुल रिक्वेस्ट भेजें। रखरखाव करने वाली टीम आवेदक से अनुरोध स्वयं लिखने को कहती है। | डेवलपर पोर्टफ़ोलियो। IP बार-बार बदलता हो तो DDNS ज़्यादा सुविधाजनक है। |
| [EU.org](https://nic.eu.org/register.html) · [EU.org NS](https://nic.eu.org/top-policy.html) | आवेदन से पहले आधिकारिक उत्तर देने वाले नेमसर्वर तैयार रखें। मंज़ूरी और NS डेलिगेशन के बाद अपने ज़ोन में A व AAAA आप सँभालते हैं। | अपने DNS रिकॉर्ड खुद सँभालने के लिए। डायनेमिक अपडेट अलग से व्यवस्थित करें। |

## चुना हुआ नाम जाँचें

![WAN पता जाँचें → अपडेट का तरीका चुनें → DNS रिकॉर्ड देखें → दूसरे नेटवर्क से जाँचें](/assets/diagrams/technical/hi-2026-11-28-nginx-free-subdomains.svg)

पहले अभ्यास में पुष्टि करें कि आपके पास सार्वजनिक IPv4 है और एक Duck DNS नाम उस पते से जोड़ें। dig इंस्टॉल होने पर नीचे उदाहरण का नाम बदलकर दोनों प्रकार के पते पूछें। A का परिणाम सार्वजनिक पते से मिलना चाहिए। AAAA प्रकाशित करें तो दूसरे नेटवर्क से IPv6 कनेक्शन भी जाँचें।

```sh
dig +short name.duckdns.org A
dig +short name.duckdns.org AAAA
```

यह तुलना सेवाओं के आधिकारिक दस्तावेज़ों पर आधारित है। हमने खाता नहीं बनाया और नाम के लिए आवेदन नहीं किया।

[स्थानीय नोट्स ऐप का अभ्यास](https://youdozi.github.io/en/posts/2026-11-28-self-hosting-ai-notes/) · [AI की मदद से Duck DNS को Nginx से जोड़ें और DNS से HTTPS तक जाँचें](https://youdozi.github.io/en/posts/2026-11-28-nginx-dns-https/)
