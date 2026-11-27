---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2021-07-24-fail-percentage",
  "routeSlug": "2021-07-24-fail-percentage",
  "kind": "post",
  "title": "Java में विफलता दर के अनुसार चरणों का क्रम कैसे तय करें",
  "description": "हर चरण पर रुके खिलाड़ियों और वहाँ तक पहुँचे खिलाड़ियों को गिनें। long में तिरछा गुणा करके दरों की तुलना करें और बराबरी होने पर छोटे चरण क्रमांक को पहले रखें।",
  "categories": [
    "coding-test"
  ],
  "tags": [
    "java",
    "algorithms"
  ],
  "sourcePath": "src/content/posts/en/2021-07-24-fail-percentage.md",
  "sourceSha256": "c684945a1636e85bfe7ce5165815a7785215f97a78fa784c21dd34e8f275d30b",
  "draftSha256": "20e9a4639c8d57a9565a1209345cadd95c140b0303c5ae1f2b1739e41de28cb4",
  "manifestPath": ".pipeline/technical-translations/batch-147/manifest.json",
  "manifestSha256": "33903ef5add849ed9fe7323deef8444a8e3247ea9dd920f98937dea49d9e3641",
  "publishedAt": "2026-11-27T13:57:44.833Z",
  "updatedAt": "2026-11-27T13:57:44.833Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 223,
    "approvedAt": "2026-11-27T13:57:44.833Z",
    "basis": "The user authorized publication of these five Hindi articles in batch 147 on 2026-11-27. The translator performed the linguistic review."
  }
}
---

किसी चरण की विफलता दर का हर उस चरण तक पहुँचे खिलाड़ियों की संख्या है। पहले गिनें कि हर चरण पर कितने खिलाड़ी रुके। इससे अगले चरण तक पहुँचे खिलाड़ियों की संख्या निकालें। फिर दर के घटते क्रम में चरण रखें और बराबर दर वाले चरणों को उनके क्रमांक के बढ़ते क्रम में रखें।

[अभ्यास](https://school.programmers.co.kr/learn/courses/30/lessons/42889) में चरणों की संख्या N अधिकतम 500 और खिलाड़ियों की संख्या M अधिकतम 200,000 है। इनपुट में N+1 उन खिलाड़ियों को दर्शाता है जिन्होंने सभी चरण पार कर लिए। इसे रैंकिंग में शामिल नहीं करते। जिस चरण तक कोई नहीं पहुँचा, उसकी विफलता दर 0 है।

## गिनती से रैंकिंग तक

![रुके खिलाड़ियों को घटाने से पहले पहुँचने वालों की संख्या सहेजें। long में तिरछा गुणा करके दरों की तुलना करें और बराबरी पर चरण क्रमांक देखें।](/assets/diagrams/technical/hi-2021-07-24-fail-percentage.svg)

हर चरण तक पहुँचे खिलाड़ियों की संख्या सहेजने के बाद ही वहाँ रुके खिलाड़ियों को घटाएँ। दो दरों की तुलना के लिए एक का अंश दूसरे के हर से long में गुणा करें। दरें बराबर हों तो चरण क्रमांक से फ़ैसला करें।

## हर चरण पर रुके और वहाँ तक पहुँचे खिलाड़ियों को गिनें

पूरी क्लास को `Solution.java` में सहेजें। मूल उदाहरण को Java 11 के लिए संकलित करके JDK 17 पर चलाया गया था।

```java
import java.util.Arrays;
import java.util.stream.IntStream;

public class Solution {
    public int[] solution(int N, int[] stages) {
        long[] stopped = new long[N + 2];
        for (int stage : stages) stopped[stage]++;
        long[] reached = new long[N + 1];
        long remaining = stages.length;
        for (int stage = 1; stage <= N; stage++) {
            reached[stage] = remaining;
            remaining -= stopped[stage];
        }
        Integer[] order = IntStream.rangeClosed(1, N).boxed().toArray(Integer[]::new);
        Arrays.sort(order, (a, b) -> {
            long denominatorA = reached[a] == 0 ? 1 : reached[a];
            long denominatorB = reached[b] == 0 ? 1 : reached[b];
            int byRate = Long.compare(stopped[b] * denominatorA, stopped[a] * denominatorB);
            return byRate != 0 ? byRate : Integer.compare(a, b);
        });
        return Arrays.stream(order).mapToInt(Integer::intValue).toArray();
    }
}
```

`remaining` मौजूदा चरण तक पहुँचे खिलाड़ियों की संख्या है। वहाँ रुके खिलाड़ियों को घटाने **से पहले** `reached[stage]` सहेजें। घटाने के बाद जो संख्या बचेगी, वह अगले चरण की दर का हर होगी। N+1 तक पहुँचे खिलाड़ी हर चरण के हर में शामिल रहते हैं।

N=5 और इनपुट `[2,1,2,6,2,4,3,3]` के लिए दरें इस प्रकार हैं।

| चरण | रुके | पहुँचे | विफलता दर |
| --- | --- | --- | --- |
| 1 | 1 | 8 | 1/8 |
| 2 | 3 | 7 | 3/7 |
| 3 | 2 | 4 | 2/4 |
| 4 | 1 | 2 | 1/2 |
| 5 | 0 | 1 | 0/1 |

चरण 3 और 4 की दर बराबर है, इसलिए छोटा क्रमांक पहले आता है। अंतिम क्रम `[3,4,2,1,5]` है।

## पूर्णांकों की सीमा में भिन्नों की तुलना करें

दोनों हर धनात्मक हों तो तिरछे गुणन से दो भिन्नों की तुलना कर सकते हैं। घटता क्रम पाने के लिए `Long.compare` को पहले b के अंश और a के हर का गुणनफल दें। दरें बराबर होने पर `Integer.compare(a, b)` चरण क्रमांक की तुलना करता है। इस तरह [Comparator के अनुबंध](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Comparator.html) के अनुसार क्रम स्पष्ट रूप से तय होता है।

जिस चरण तक कोई खिलाड़ी नहीं पहुँचा, मान्य इनपुट में उस पर रुके खिलाड़ियों की संख्या भी शून्य होगी। तुलना के लिए हर 1 लेकर दर को 0/1 लिखें। दोनों गिनतियाँ 200,000 तक हो सकती हैं, इसलिए गुणनफल की ऊपरी सीमा 40,000,000,000 है। यह int की सीमा से बाहर है, इसलिए ऐरे का प्रकार और गुणा दोनों long रखें। तुलना का परिणाम देने के लिए गुणनफलों के अंतर को int में कास्ट न करें।

रुके खिलाड़ियों की गिनती में O(M), पहुँचने वालों की गिनती में O(N) और छँटाई में O(N log N) समय लगता है। कुल समय O(M + N log N) और अतिरिक्त स्थान O(N) है। इनपुट नहीं बदलता। यदि सभी खिलाड़ी सभी चरण पार कर चुके हैं, तो हर दर शून्य है और परिणाम में चरण क्रमांक बढ़ते क्रम में आते हैं।

इनपुट की सीमा देखकर गुणा का प्रकार चुनने का एक और उदाहरण [ऐरे के अदिश गुणनफल में int और long](/hi/posts/2021-07-22-dot-product/) में देखें।
