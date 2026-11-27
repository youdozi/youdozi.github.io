---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2021-07-23-number-word",
  "routeSlug": "2021-07-23-number-word",
  "kind": "post",
  "title": "Java में String.replace से अंकों के अंग्रेज़ी नाम बदलें",
  "description": "अंक और zero से nine तक के शब्द एक साथ हों तो शब्दों को उनके अंकों से बदलें। replace और replaceAll का अंतर, int की सीमा और इनपुट की शर्तें समझें।",
  "categories": [
    "coding-test"
  ],
  "tags": [
    "java",
    "algorithms"
  ],
  "sourcePath": "src/content/posts/en/2021-07-23-number-word.md",
  "sourceSha256": "28614468f78703f7e406439ee8b23b83e06091ae7f42ed9835cd50c6d1bb2e87",
  "draftSha256": "2e4bf80fe35aeb0bc9becac121f5215ab26cf6502005c8a5455292b727ba82f6",
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

जब मान्य इनपुट में अंक और उनके अंग्रेज़ी नाम मिले-जुले हों, तो `zero` से `nine` तक के तय शब्दों की जगह उनके अंक रखें। फिर बनी हुई स्ट्रिंग को पूर्णांक में बदलें। हर शब्द को ठीक उसी रूप में खोजना है, इसलिए `String.replace` पर्याप्त है। `replaceAll` की ज़रूरत नहीं पड़ती।

[अभ्यास](https://school.programmers.co.kr/learn/courses/30/lessons/81301) में केवल मान्य छोटे अंग्रेज़ी अक्षरों में लिखे अंकों के नाम और अंक मिलते हैं। परिणाम 1 से 2,000,000,000 तक होता है और शुरुआत में शून्य नहीं होता। सामान्य अंग्रेज़ी में लिखी संख्याओं को पढ़ना इस विधि के दायरे से बाहर है।

## शब्दों से पूर्णांक तक

![zero से nine तक के पूरे शब्दों की जगह उनके अंक रखें और फिर बनी हुई दशमलव स्ट्रिंग को पूर्णांक में बदलें।](/assets/diagrams/technical/hi-2021-07-23-number-word.svg)

पहले zero से nine तक के शब्दों की जगह उनके अंक आते हैं। जब केवल दशमलव अंक बचते हैं, तब स्ट्रिंग को पूर्णांक में बदलते हैं।

## दस तय शब्द बदलें

पूरी क्लास `Solution.java` में सहेजें। अतिरिक्त import की ज़रूरत नहीं है। मूल उदाहरण को Java 11 को लक्ष्य बनाकर संकलित किया गया और चलाकर जाँचा गया था।

```java
public class Solution {
    public int solution(String s) {
        String[] words = {"zero", "one", "two", "three", "four",
                "five", "six", "seven", "eight", "nine"};
        for (int digit = 0; digit < words.length; digit++) {
            s = s.replace(words[digit], Integer.toString(digit));
        }
        return Integer.parseInt(s);
    }
}
```

[`String.replace(CharSequence, CharSequence)`](https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/lang/String.html) खोजे जाने वाले पाठ को शाब्दिक रूप में लेता है। `replaceAll` अपने पहले आर्ग्युमेंट को रेगुलर एक्सप्रेशन की तरह पढ़ता है। इन दस शब्दों में से किसी को खोजने के लिए रेगुलर एक्सप्रेशन की ज़रूरत नहीं है।

उदाहरण के लिए, `one4seveneight` से `1478` और `23four5six7` से `234567` मिलता है। `123` जैसे इनपुट में पहले से केवल अंक हैं, इसलिए परिणाम 123 ही है। `two` के बाद नौ बार `zero` लिखने पर 2,000,000,000 मिलता है, जो int की सीमा में है।

प्रतिस्थापन से आने वाला अंक किसी नए अंग्रेज़ी अंक-नाम का हिस्सा नहीं बन सकता। दस शब्दों में से किसी के भीतर सूची का कोई दूसरा पूरा शब्द भी नहीं आता। इसलिए दिया गया क्रम काम करता है। अमान्य शब्द, रिक्त स्थान, बड़े अक्षर और सीमा से बाहर की संख्याएँ प्रश्न की शर्तों में शामिल नहीं हैं। ऐसे इनपुट को पढ़ते समय त्रुटि आए तो यह विधि उसे सुधारकर कोई मान्य पूर्णांक नहीं बनाती।

शब्दों की संख्या दस पर तय है, इसलिए इनपुट की लंबाई n के लिए समय O(n) है। स्ट्रिंग अपरिवर्तनीय हैं। प्रतिस्थापन के बीच नई स्ट्रिंग बन सकती हैं और अतिरिक्त स्थान O(n) है। इन छोटे इनपुट पर इस विधि को दूसरे पार्सरों से तेज़ बताने के लिए कोई बेंचमार्क नहीं है।

जहाँ रेगुलर एक्सप्रेशन काम आता है, ऐसा उदाहरण [नई आईडी को सामान्य रूप देने वाले अभ्यास](/hi/posts/2021-07-19-new-id/) में देखें।
