---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2023-09-13-springboot-history",
  "routeSlug": "2023-09-13-springboot-history",
  "kind": "post",
  "title": "Spring Boot का रिलीज़ इतिहास और Spring Framework का सही संस्करण कैसे पहचानें",
  "description": "Spring Boot 1.2 से 4.0 तक के प्रमुख बदलाव देखें। स्टार्टर और BOM की भूमिकाएँ समझें और पता लगाएँ कि आपका प्रोजेक्ट वास्तव में किन डिपेंडेंसी संस्करणों का इस्तेमाल करता है।",
  "categories": [
    "springboot"
  ],
  "tags": [
    "springboot",
    "history"
  ],
  "sourcePath": "src/content/posts/en/2023-09-13-springboot-history.md",
  "sourceSha256": "8f97cfe96eb4ed1a36dae63a187c6f28960c327ff6cba276c45537a1e7745da2",
  "draftSha256": "a32c046f23033280d3b3ae748f66b9dec5f190e4faa9804351f4c97313f99dd8",
  "manifestPath": ".pipeline/technical-translations/batch-143/manifest.json",
  "manifestSha256": "507f1028e4316fae6163aabff3c22cf50eccdee5516bab5c7e7653c530e37280",
  "publishedAt": "2026-11-27T12:21:24.636Z",
  "updatedAt": "2026-11-27T12:21:24.636Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 219,
    "approvedAt": "2026-11-27T12:21:24.636Z",
    "basis": "The owner authorized publication of the five Hindi editions in item 143. The translator reviewed the translations and diagrams."
  }
}
---

Spring Boot और Spring Framework अलग प्रोजेक्ट हैं और इनके संस्करण क्रमांक भी अलग हैं। Boot, Framework के ऊपर ऑटो-कॉन्फ़िगरेशन, डिपेंडेंसी प्रबंधन और चलाने योग्य पैकेज बनाने की सुविधा देता है। इसलिए Boot 3.1 देखकर Framework 6.1 मान लेना सही नहीं है। चुनी गई Boot रिलीज़ का BOM और बिल्ड में हल हुई डिपेंडेंसी का ग्राफ़ देखें।

## प्रोजेक्ट में चुने गए संस्करण कैसे जाँचें

![Boot की सेटिंग से शुरू करके spring-core और Lombok के वास्तविक संस्करण पता करने के चरण](/assets/diagrams/technical/hi-2023-09-13-springboot-history.svg)

चित्र में डिपेंडेंसी की जाँच का क्रम दिखाया गया है। Boot, Framework और Lombok के अपने संस्करण क्रमांक हैं। डिपेंडेंसी की जाँच करते समय उसका कॉन्फ़िगरेशन भी देखना होता है।

## चुनिंदा स्थिर रिलीज़ में क्या बदला

नीचे उन रिलीज़ को चुना गया है जिनमें प्रमुख सुविधाएँ बदलीं। किसी श्रृंखला की पहली स्थिर रिलीज़ और बाद के पैच में बढ़े JDK समर्थन को अलग समझें।

| Spring Boot | पहली स्थिर रिलीज़ | प्रमुख बदलाव और आधिकारिक घोषणा |
| --- | --- | --- |
| 1.2 | 2014-12-11 | [`@SpringBootApplication` और Servlet 3.1 का समर्थन](https://spring.io/blog/2014/12/11/spring-boot-1-2-0-released/) |
| 1.3 | 2015-11-16 | [DevTools, कैशिंग का ऑटो-कॉन्फ़िगरेशन और सीधे चलने वाली JAR फ़ाइलें](https://spring.io/blog/2015/11/16/spring-boot-1-3-0-released/) |
| 1.4 | 2016-07-28 | [स्टार्टअप विफलता का विश्लेषण और परीक्षण के लिए बेहतर सुविधाएँ](https://spring.io/blog/2016/07/28/spring-boot-1-4-released/) |
| 2.0 | 2018-03-01 | [Framework 5.0, न्यूनतम Java 8 और रिएक्टिव वेब का समर्थन](https://spring.io/blog/2018/03/01/spring-boot-2-0-goes-ga/) |
| 3.0 | 2022-11-24 | [Framework 6.0, न्यूनतम Java 17, Jakarta और नेटिव इमेज](https://spring.io/blog/2022/11/24/spring-boot-3-0-goes-ga/) |
| 3.1 | 2023-05-18 | [विकास के दौरान Testcontainers और Docker Compose का इंटीग्रेशन](https://spring.io/blog/2023/05/18/spring-boot-3-1-0-available-now/) |
| 3.2 | 2023-11-23 | [वर्चुअल थ्रेड, RestClient और JdbcClient का समर्थन](https://spring.io/blog/2023/11/23/spring-boot-3-2-0-available-now/) |
| 4.0 | 2025-11-20 | [Framework 7, मॉड्यूल में विभाजन, JSpecify और API वर्ज़निंग](https://spring.io/blog/2025/11/20/spring-boot-4-0-0-available-now/) |

मिसाल के तौर पर, [Boot 3.1.0 की प्रबंधित डिपेंडेंसी सूची](https://docs.spring.io/spring-boot/docs/3.1.0/reference/html/dependency-versions.html) में `spring-core` का संस्करण 6.0.9 है। Boot और Framework के माइनर संस्करण क्रमांक का मेल खाना ज़रूरी नहीं है। इसी तरह Boot 2.4 को Framework 5.4 से जोड़ना भी ग़लत है क्योंकि Framework की ऐसी कोई रिलीज़ श्रृंखला नहीं है।

## स्टार्टर, BOM और बिल्ड प्लगइन

स्टार्टर किसी सुविधा के लिए ज़रूरी डिपेंडेंसी को एक साथ लाता है। BOM उनके संस्करण तय करता है। सूची में होने भर से कोई लाइब्रेरी अपने आप प्रोजेक्ट में नहीं जुड़ती। Boot का बिल्ड प्लगइन `bootRun` जैसे टास्क देता है और चलाने योग्य JAR बना सकता है।

Gradle के लिए [Boot की डिपेंडेंसी प्रबंधन गाइड](https://docs.spring.io/spring-boot/4.1/gradle-plugin/managing-dependencies.html) में dependency-management प्लगइन और Gradle के अपने BOM समर्थन के बारे में बताया गया है। केवल Boot प्लगइन लगाने से यह तय नहीं होता कि हर Gradle कॉन्फ़िगरेशन में संस्करण लिखे बिना डिपेंडेंसी जोड़ सकते हैं। एनोटेशन प्रोसेसर जैसे अलग कॉन्फ़िगरेशन भी जाँचें।

## अपने प्रोजेक्ट के वास्तविक संस्करण देखें

[Initializr](/hi/posts/2023-09-07-springboot-initializer/) और [Lombok](/hi/posts/2023-09-15-springboot-intellij-lombok/) के उदाहरण पूरे करके तैयार हुए प्रोजेक्ट में ये कमांड चलाएँ।

```sh
./gradlew dependencyInsight --configuration runtimeClasspath --dependency spring-core
./gradlew dependencyInsight --configuration annotationProcessor --dependency lombok
```

स्थानीय उदाहरण में Boot 4.1.2, `spring-core` 7.0.10 और Lombok 1.18.48 चुने गए थे। ये अलग-अलग प्रोजेक्ट के संस्करण हैं। `dependencyInsight` बताता है कि कौन-सा संस्करण चुना गया और किस डिपेंडेंसी पथ या नियम के कारण वह चुना गया। इससे संस्करणों के टकराव की वजह समझ सकते हैं। ये मान इसी उदाहरण के हैं। इन्हें भविष्य की डिफ़ॉल्ट सेटिंग या हर प्रोजेक्ट पर लागू संयोजन न मानें।

ऊपर दी गई तारीखें रिलीज़ का इतिहास बताती हैं। नया प्रोजेक्ट बनाते या अपग्रेड करते समय चुनी गई रिलीज़ की आवश्यकताएँ, डिपेंडेंसी की संगतता और वर्तमान समर्थन नीति अलग से जाँचें। [Java 17 और Jakarta पर माइग्रेशन](/hi/posts/2023-09-08-springboot3-migration/) में Boot 3 पर जाने के चरण दिए हैं। स्थानीय रूप से चलाने के लिए [IntelliJ और Gradle की रन सेटिंग जाँचें](/hi/posts/2023-09-10-springboot-intellij-import/)।
