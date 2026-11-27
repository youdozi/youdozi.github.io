---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2021-07-22-plus-minus",
  "routeSlug": "2021-07-22-plus-minus",
  "kind": "post",
  "title": "Java में IntStream से हर मान पर उसका चिह्न लगाकर योग निकालें",
  "description": "निरपेक्ष मान और बूलियन चिह्न वाले ऐरे को समान इंडेक्स से जोड़ें। देखें कि योग कब शून्य होता है, सभी चिह्न ऋणात्मक हों तो क्या होता है और int क्यों पर्याप्त है।",
  "categories": [
    "coding-test"
  ],
  "tags": [
    "java",
    "algorithms"
  ],
  "sourcePath": "src/content/posts/en/2021-07-22-plus-minus.md",
  "sourceSha256": "63f6b289759a3487a5cb548baedd43054c6fa803aa1dbd58a39dd4d088a413bc",
  "draftSha256": "1051f883bff9c0083ae020319bb60b7b01028adda5df475d2983d80087128a17",
  "manifestPath": ".pipeline/technical-translations/batch-146/manifest.json",
  "manifestSha256": "2bbe3770208f27ecff881899a3ea45294a707ff832e873c6eb76fb6a0733f083",
  "publishedAt": "2026-11-27T13:34:52.523Z",
  "updatedAt": "2026-11-27T13:34:52.523Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 222,
    "approvedAt": "2026-11-27T13:34:52.523Z",
    "basis": "The user authorized publication of these five Hindi articles in batch 146 on 2026-11-27. Publication authorization is distinct from linguistic review, performed by the translator."
  }
}
---

जब संख्याओं के निरपेक्ष मान और चिह्न अलग-अलग मिलें, तो जोड़ने से पहले हर इंडेक्स के मान पर उसी इंडेक्स का चिह्न लगाएँ। `signs[i]` का मान true हो तो संख्या धनात्मक है और false हो तो ऋणात्मक। एक सशर्त व्यंजक से मूल संख्या मिल जाती है।

[अभ्यास](https://school.programmers.co.kr/learn/courses/30/lessons/76501) में दोनों ऐरे की लंबाई समान है और 1 से 1,000 तक हो सकती है। हर निरपेक्ष मान 1 से 1,000 तक है। चिह्नों को अलग से क्रमबद्ध करने पर वे गलत मानों के साथ जुड़ जाएँगे। इसलिए दोनों ऐरे को दिए गए क्रम में पढ़ें।

## चिह्न से योग तक

![दोनों ऐरे में एक ही इंडेक्स पढ़ें, मान पर उसका चिह्न लगाएँ और फिर सभी चिह्नित मान जोड़ें।](/assets/diagrams/technical/hi-2021-07-22-plus-minus.svg)

हर इंडेक्स पर दोनों ऐरे से एक मान और उसका चिह्न मिलता है। चिह्न लगाने के बाद इन संख्याओं का योग निकालें।

## समान इंडेक्स के मान एक साथ पढ़ें

पूरी क्लास `Solution.java` में सहेजें। मूल उदाहरण को Java 11 के लिए संकलित करके JDK 17 पर चलाया गया था।

```java
import java.util.stream.IntStream;

public class Solution {
    public int solution(int[] absolutes, boolean[] signs) {
        return IntStream.range(0, absolutes.length)
                .map(i -> signs[i] ? absolutes[i] : -absolutes[i])
                .sum();
    }
}
```

[`IntStream.range`](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/stream/IntStream.html) इंडेक्स 0 को शामिल करता है और `absolutes.length` को छोड़ता है। `map` हर निरपेक्ष मान पर उसका चिह्न लगाता है और `sum` उन मानों को जोड़ता है। इस विधि में इनपुट जस का तस रहता है और चिह्न लगे मानों के लिए अलग ऐरे भी नहीं बनता।

| निरपेक्ष मान | चिह्न | वास्तविक मान |
| --- | --- | --- |
| 4 | true | 4 |
| 7 | false | -7 |
| 12 | true | 12 |

इन मानों का योग 9 है। `[1,2,3]` और `[false,false,true]` देने पर धनात्मक और ऋणात्मक पद कट जाते हैं और योग 0 होता है। केवल धनात्मक और ऋणात्मक चिह्न गिनना काफ़ी नहीं है। हर पद का **निरपेक्ष मान** भी योगदान देता है।

## पूर्णांकों की सीमा और इनपुट की शर्तें

अधिकतम 1,000 पद हैं और हर पद का निरपेक्ष मान अधिकतम 1,000 है, इसलिए योग का निरपेक्ष मान 1,000,000 से अधिक नहीं होता। सभी पद धनात्मक हों या सभी ऋणात्मक, परिणाम int की सीमा में आता है। समय O(n) और अतिरिक्त स्थान O(1) है।

यह विधि मानती है कि निरपेक्ष मान प्रश्न की सीमा में हैं और दोनों ऐरे की लंबाई समान है। किसी अनुप्रयोग में मनमाना इनपुट मिले तो null, लंबाई और मानों की जाँच अलग से करनी होगी। सीमाएँ बढ़ने पर पदों और योग, दोनों के प्रकार पर फिर से विचार करें।

दो ऐरे के साथ दूसरी गणना के लिए [ऐरे का डॉट प्रोडक्ट](/hi/posts/2021-07-22-dot-product/) देखें। int की सीमा से बड़े परिणामों के लिए [long से x के अंतर वाली श्रेणी बनाना](/en/posts/2021-07-29-interval-num/) देखें। आगे के अभ्यास [Java कोडिंग अभ्यास मार्गदर्शिका](/en/categories/coding-test/) में दिए हैं।
