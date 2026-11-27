---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2021-07-23-app-diagrams.net",
  "routeSlug": "2021-07-23-app-diagrams.net",
  "kind": "post",
  "title": "draw.io का संपादन योग्य स्रोत साझा किए गए आरेख के साथ कैसे रखें",
  "description": "बिना संपीड़न वाले XML में छोटा draw.io आरेख बनाएँ। संपादन के लिए .drawio स्रोत सँभालकर रखें और साझा करने के लिए SVG या PNG निर्यात करें।",
  "categories": [
    "util"
  ],
  "tags": [
    "diagrams",
    "xml",
    "drawio"
  ],
  "sourcePath": "src/content/posts/en/2021-07-23-app-diagrams.net.md",
  "sourceSha256": "994c0cd18640921c0e130d9310adace919b39b5be0e5a2b54b5cee9772bdd8c0",
  "draftSha256": "14d89786125220fefda43fdb3bbd3395f5417a4d55af92274a1670eb1418c902",
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

प्रकाशित चित्र के साथ आरेख का संपादन योग्य स्रोत भी रखें। चित्र में मौजूदा परिणाम दिखता है। स्रोत में वे आकृतियाँ, कनेक्टर और लेबल रहते हैं जिनकी अगले बदलाव में ज़रूरत पड़ेगी।

[draw.io की फ़ाइल फ़ॉर्मैट गाइड](https://www.drawio.com/docs/manual/editor/save-file-formats/) बिना संपीड़न वाले XML फ़ॉर्मैट `.drawio` की सलाह देती है। SVG और PNG में भी आरेख का डेटा शामिल हो सकता है। इसलिए सिर्फ़ एक्सटेंशन देखकर तय नहीं कर सकते कि फ़ाइल का संपादन हो सकेगा या नहीं। निर्यात की गई फ़ाइल में डेटा शामिल होने पर भी मूल स्रोत अलग रखें।

## उदाहरण में अनुरोध का क्रम

![Request से Validate होते हुए Response तक दो तीर](/assets/diagrams/technical/hi-2021-07-23-app-diagrams.net.svg)

चित्र में वही तीन नोड और दो दिशात्मक कनेक्शन हैं जो नीचे XML में दिए गए हैं। यह चित्र लेख के लिए बनाया गया है। यह संपादक का स्क्रीनशॉट या उससे निर्यात की गई फ़ाइल नहीं है।

## XML को request-flow.drawio में सहेजें

```xml
<mxfile host="app.diagrams.net">
  <diagram id="request-flow" name="Request flow">
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="request" value="Request" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="40" y="40" width="160" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="validate" value="Validate" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="40" y="160" width="160" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="response" value="Response" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="40" y="280" width="160" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="first" edge="1" parent="1" source="request" target="validate" style="endArrow=block;">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="second" edge="1" parent="1" source="validate" target="response" style="endArrow=block;">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

जिन `mxCell` तत्वों में `vertex="1"` है, वे तीन नोड परिभाषित करते हैं। दोनों कनेक्शन अपने शुरुआती और अंतिम नोड की ID इस्तेमाल करते हैं। `mxGeometry` से स्थिति और आकार तय होते हैं। दिखाई देने वाला लेबल बदलने और कनेक्शन में इस्तेमाल होने वाली ID बदलने का असर अलग होता है।

फ़ाइल को संपादक में खोलें। पूरी फ़ाइल में बाहरी `mxfile` और `diagram` तत्व भी होते हैं। अगर आप **Extras → Edit Diagram** खोलते हैं, तो वहाँ केवल मौजूदा पृष्ठ का `mxGraphModel` मिलता है। [स्रोत संपादक के दस्तावेज़](https://www.drawio.com/docs/manual/advanced/diagram-source-edit/) में इसी अंश का वर्णन है। पूरी फ़ाइल में इसे घेरने वाले तत्व भी चाहिए।

| फ़ाइल | उपयोग |
| --- | --- |
| `request-flow.drawio` | संस्करण नियंत्रण में रखा संपादन योग्य स्रोत |
| `request-flow.svg` या `.png` | साझा करने या दिखाने के लिए चित्र। जाँचें कि इसमें आरेख का डेटा भी है या नहीं। |

बदलाव के बाद स्रोत दोबारा खोलें, हर तीर की दिशा जाँचें और साझा करने के लिए नया चित्र निर्यात करें। स्रोत में हुए बदलाव और उनसे बना चित्र दोनों देखें। फ़ॉर्मैटिंग के कई बदलावों के बीच किसी कनेक्शन में छोटा बदलाव छूट सकता है।

मूल उदाहरण में XML की संरचना, ID की विशिष्टता और कनेक्टर के संदर्भ स्थानीय रूप से जाँचे गए थे। उन जाँचों में क्लाउड स्टोरेज, संपादक के इंटरफ़ेस का उपयोग या निर्यात की गई फ़ाइल को दोबारा खोलना शामिल नहीं था। अपने खाते और संपादक के अनुसार स्टोरेज का विकल्प अलग से चुनें। किसी रिपॉज़िटरी में जाँच को चुनिंदा फ़ाइलों तक सीमित रखने के लिए [कोड खोजने की गाइड](/hi/posts/2021-08-06-search-github/) देखें।
