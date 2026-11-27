---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2023-09-10-springboot-intellij-import",
  "routeSlug": "2023-09-10-springboot-intellij-import",
  "kind": "post",
  "title": "IntelliJ IDEA में Spring Boot का Gradle प्रोजेक्ट कैसे खोलें और चलाएँ",
  "description": "Gradle Wrapper से बिल्ड चलाएँ, IntelliJ IDEA में SDK और रन सेटिंग जाँचें और HTTP टेस्ट से पता लगाएँ कि समस्या IDE में है या ऐप्लिकेशन में।",
  "categories": [
    "springboot"
  ],
  "tags": [
    "springboot",
    "intellij community",
    "project import",
    "RUN/DEBUG configurations"
  ],
  "sourcePath": "src/content/posts/en/2023-09-10-springboot-intellij-import.md",
  "sourceSha256": "5b3c970364e92d3672967197986ea67769f45094ca27f6c9f8bfbd0779645bc2",
  "draftSha256": "520660e9cd5623d1a5e3fd92595ce11f4713af20230f80efaa251fb65329b4fa",
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

IntelliJ में Spring Boot प्रोजेक्ट खोलने पर पहले देखें कि Gradle सिंक पूरा हुआ है या नहीं। फिर Wrapper से मिले बिल्ड के नतीजे की तुलना IDE से चलाने पर मिले नतीजे से करें। रन बटन न दिखे तो हर बार नया कॉन्फ़िगरेशन बनाने की ज़रूरत नहीं होती। मान्य Java main मेथड को [एडिटर में पंक्ति के बाईं ओर बने रन आइकन](https://www.jetbrains.com/help/idea/running-applications.html) से भी चला सकते हैं।

यह लेख Boot 4.1.2, Gradle 9.8.2 और Java 17 वाले [Initializr उदाहरण](/hi/posts/2023-09-07-springboot-initializer/) को आगे बढ़ाता है। बिल्ड और HTTP अनुरोध स्थानीय रूप से चलाकर देखे गए थे। IDE के चरण JetBrains के दस्तावेज़ों से जाँचे गए थे। किसी खास IDE संस्करण के इंटरफ़ेस में इन चरणों को आज़माने की पुष्टि नहीं हुई है।

## बिल्ड से HTTP अनुरोध तक

![बिल्ड और IDE की गड़बड़ियों को अलग पहचानने के चरण](/assets/diagrams/technical/hi-2023-09-10-springboot-intellij-import.svg)

Wrapper से बिल्ड चलाने पर पता चलता है कि समस्या प्रोजेक्ट में है या IDE की सेटिंग में। HTTP टेस्ट के लिए सर्वर को कोई उपलब्ध पोर्ट मिलता है। हाथ से bootRun चलाने पर वह कॉन्फ़िगरेशन में दिया पोर्ट इस्तेमाल करता है।

## प्रोजेक्ट और JDK की जाँच करें

1. आर्काइव खोलने के बाद File → Open से प्रोजेक्ट का वह मूल फ़ोल्डर चुनें जिसमें `settings.gradle` और `build.gradle` हैं।
2. Gradle सिंक पूरा होने दें। डिपेंडेंसी डाउनलोड करने या सिंक करने में कोई त्रुटि आए तो पहले उसे ठीक करें।
3. प्रोजेक्ट के Wrapper वाला Gradle वितरण चुनें। फिर Gradle JVM और Project SDK जाँचें। इस उदाहरण में दोनों के लिए JDK 17 है।
4. टर्मिनल में `./gradlew --version` और `./gradlew test` चलाएँ ताकि तुलना के लिए IDE के बाहर का नतीजा भी हो।

[Gradle इंटीग्रेशन गाइड](https://www.jetbrains.com/help/idea/gradle.html) और [Gradle JVM चुनने के नियम](https://www.jetbrains.com/help/idea/gradle-jvm-selection.html) देखें। मेन्यू के नाम IDE संस्करण और ऑपरेटिंग सिस्टम के अनुसार बदल सकते हैं। Project SDK, Gradle चलाने वाली JVM, Java टूलचेन और रन कॉन्फ़िगरेशन के JRE की सेटिंग अलग-अलग होती हैं। ज़रूरी नहीं कि वे अपने आप मेल खाएँ।

## एक एंडपॉइंट और वास्तविक HTTP टेस्ट जोड़ें

मौजूदा चार फ़ाइलें रखें और नीचे दी गई दो फ़ाइलें जोड़ें। कंट्रोलर को ऐप्लिकेशन के `example.demo` पैकेज में रखने से वह कंपोनेंट स्कैन के दायरे में आ जाता है।

### `src/main/java/example/demo/GreetingController.java`

```java
package example.demo;

import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class GreetingController {
    @GetMapping("/greeting")
    public Map<String, String> greeting() {
        return Map.of("message", "Hello, Gradle");
    }
}
```

### `src/test/java/example/demo/GreetingHttpTest.java`

```java
package example.demo;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.core.env.Environment;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class GreetingHttpTest {
    @Autowired Environment environment;

    HttpResponse<String> get(String path) throws Exception {
        String port = environment.getRequiredProperty("local.server.port");
        var request = HttpRequest.newBuilder(URI.create("http://127.0.0.1:" + port + path))
                .timeout(Duration.ofSeconds(10)).GET().build();
        return HttpClient.newHttpClient().send(request, HttpResponse.BodyHandlers.ofString());
    }

    @Test
    void greetingReturnsJson() throws Exception {
        var response = get("/greeting");
        assertEquals(200, response.statusCode());
        assertTrue(response.headers().firstValue("content-type").orElse("").contains("application/json"));
        assertEquals("{\"message\":\"Hello, Gradle\"}", response.body());
    }

    @Test
    void missingPathIsNotAnApplicationStartupFailure() throws Exception {
        assertEquals(404, get("/missing").statusCode());
    }
}
```

अब `./gradlew test` मौजूदा कॉन्टेक्स्ट टेस्ट के साथ दो HTTP टेस्ट भी चलाता है। ये टेस्ट किसी उपलब्ध पोर्ट पर वास्तविक सर्वर शुरू करते हैं, JSON आउटपुट की जाँच करते हैं और देखते हैं कि अनुपस्थित पथ पर 404 मिले। स्थानीय पोर्ट 8080 का खाली होना ज़रूरी नहीं है।

## Gradle और IDE के Application कॉन्फ़िगरेशन से चलाकर तुलना करें

पहली कमांड से सर्वर शुरू करें। फिर दूसरे टर्मिनल में दूसरी कमांड चलाएँ।

```sh
./gradlew bootRun --args='--server.port=8081'
```

```sh
curl --fail --show-error http://localhost:8081/greeting
```

```json
{"message":"Hello, Gradle"}
```

IDE में पहले `DemoApplication.main()` के पास वाला रन आइकन आज़माएँ। यदि अलग कॉन्फ़िगरेशन चाहिए तो Run → Edit Configurations में Application कॉन्फ़िगरेशन बनाएँ और ये मान जाँचें।

| सेटिंग | उदाहरण |
| --- | --- |
| Main class | `example.demo.DemoApplication` |
| Classpath module | प्रोजेक्ट के मुख्य सोर्स का मॉड्यूल, जैसे `demo.main` |
| JRE | JDK 17 |
| Program arguments | `--server.port=8081` |

यदि कोई प्रक्रिया पहले से 8081 इस्तेमाल कर रही है तो उसे रोकें या दूसरा पोर्ट चुनें। सामान्य Java Application कॉन्फ़िगरेशन चलाने के लिए Boot की विशेष टूल विंडो या रन कॉन्फ़िगरेशन उपलब्ध होना ज़रूरी नहीं है।

| लक्षण | पहले क्या जाँचें |
| --- | --- |
| Wrapper से भी बिल्ड विफल होता है | JDK और Gradle की संगतता, डिपेंडेंसी और सोर्स कोड की त्रुटियाँ |
| Wrapper सफल होता है लेकिन IDE से रन विफल होता है | Gradle रीलोड, मॉड्यूल का क्लासपाथ, रन के लिए चुना JRE और आर्ग्युमेंट |
| सर्वर शुरू होता है लेकिन `/greeting` पर 404 मिलता है | कंट्रोलर का पैकेज और मैपिंग पथ |
| पोर्ट पहले से इस्तेमाल में होने की त्रुटि आती है | चल रही प्रक्रियाएँ और ऐप्लिकेशन के मौजूदा इंस्टेंस |

यदि कोड कंपाइल हो जाता है लेकिन IDE जनरेट किए गए मेथड में त्रुटि दिखाता है तो [Lombok और एनोटेशन प्रोसेसर की सेटिंग जाँचें](/hi/posts/2023-09-15-springboot-intellij-lombok/)।
