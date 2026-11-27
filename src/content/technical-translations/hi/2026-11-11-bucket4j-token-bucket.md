---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2026-11-11-bucket4j-token-bucket",
  "routeSlug": "2026-11-11-bucket4j-token-bucket",
  "kind": "post",
  "title": "Bucket4j से अनुरोध सीमित करें: स्थानीय टोकन बकेट और वितरित सीमा",
  "description": "Spring MVC और Bucket4j में शुरुआती बर्स्ट और टोकन भरने की दर अलग-अलग तय करें। Retry-After, साझा बकेट और Redis के साथ वितरित सीमा का व्यवहार समझें।",
  "categories": [
    "springboot"
  ],
  "tags": [
    "bucket4j",
    "rate-limit",
    "token-bucket",
    "spring-mvc",
    "redis"
  ],
  "sourcePath": "src/content/posts/en/2026-11-11-bucket4j-token-bucket.md",
  "sourceSha256": "3026360c1ee1f4cc06667cd53ebded53b1bfebf3c0c29658e6eb58affffbdf8f",
  "draftSha256": "39c57944654791e706f8addd4144b68ab3f5a00acfad76e2c85ec66b8cfac63e",
  "manifestPath": ".pipeline/technical-translations/batch-1351/manifest.json",
  "manifestSha256": "210cb3d20786b5609c404e4cfce31f0c675a6803f9e59c9b0ac9360cda251731",
  "publishedAt": "2026-11-27T09:08:25.573Z",
  "updatedAt": "2026-11-27T09:08:25.573Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 211,
    "approvedAt": "2026-11-27T09:08:25.573Z",
    "basis": "User authorized publication of the five named Hindi technical editions in item 135."
  }
}
---

**Bucket4j जावा की एक लाइब्रेरी है जो टोकन बकेट में टोकन भरने और खर्च होने का हिसाब रखती है और एक साथ आए अनुरोधों को सँभालती है।** Spring में एक बकेट साझा करके हर अनुरोध पर एक टोकन लेने की कोशिश करें। इससे आप शुरुआती बर्स्ट और उसके बाद टोकन भरने की दर अलग-अलग तय कर सकते हैं। हर JVM का स्थानीय बकेट स्वतंत्र होता है। सिर्फ़ लाइब्रेरी जोड़ने से सभी सर्वरों के लिए साझा सीमा लागू नहीं होती।

[Redis Lua से अनुरोध सीमित करने पर पिछले लेख](/ko/posts/2026-11-10-redis-lua-rate-limit/) में पहली अनुमति से शुरू होने वाली निश्चित अवधि के अनुरोध गिने गए थे। यहाँ हम **एक JVM में 5 टोकन की क्षमता वाला बकेट बनाएँगे जिसमें 5 टोकन भरने में 10 सेकंड लगते हैं**। फिर देखेंगे कि Redis के साथ वितरित व्यवस्था अपनाने पर क्या बदलता है।

उदाहरण का परिवेश Bucket4j **8.22.0**, Spring Boot 3.5.16, JDK 21 और Gradle 8.14.3 है। Bucket4j का संस्करण [आधिकारिक रिलीज़](https://github.com/bucket4j/bucket4j/releases) और [8.22.0 के संदर्भ दस्तावेज़](https://bucket4j.com/8.22.0/toc.html) से मिलाकर तय किया गया। डिपेंडेंसी के नाम में `jdk17` का अर्थ है कि आर्टिफ़ैक्ट JDK 17 परिवार के लिए बना है। उदाहरण इसे JDK 21 पर चलाता है।

## क्षमता और टोकन भरने की दर में क्या अंतर है?

`capacity(5)` तय करता है कि अधिकतम कितने टोकन जमा हो सकते हैं। डिफ़ॉल्ट रूप से शुरुआत भी पाँच टोकन से होती है, इसलिए पाँच अनुरोध तुरंत स्वीकार हो सकते हैं। `refillGreedy(5, Duration.ofSeconds(10))` दस सेकंड में पाँच टोकन भरने की दर तय करता है। यदि हर अनुरोध एक टोकन लेता है और `t=0` पर सभी टोकन खर्च हो गए हैं, तो `t=2 seconds` पर एक नया टोकन उपलब्ध होगा।

इस नीति को **“किसी भी लगातार दस सेकंड में अधिकतम पाँच अनुरोध”** कहना ग़लत होगा। यह शुरुआती पाँच अनुरोधों के साथ बाद में भरे गए टोकन भी खर्च करने देती है। लंबे समय तक कोई अनुरोध न आए तब भी बकेट में पाँच से अधिक टोकन जमा नहीं होते।

| समान क्षमता और समान मात्रा के साथ भरने का तरीका | `refillGreedy(5, 10 seconds)` | `refillIntervally(5, 10 seconds)` |
| --- | --- | --- |
| `t=0` पर पाँचों टोकन खर्च करें | 0 शेष | 0 शेष |
| और टोकन खर्च किए बिना `t=2 seconds` पर जाँचें | 1 उपलब्ध | 0 |
| और टोकन खर्च किए बिना `t=10 seconds` पर जाँचें | 5 | 5 |

Greedy में समय बीतने के साथ टोकन धीरे-धीरे मिलते हैं। Intervally में पूरी अवधि बीतने पर एक साथ मिलते हैं। तालिका की जाँच शून्य से शुरू होने वाली नियंत्रित घड़ी से हुई। टोकन डालने के लिए अलग शेड्यूलर नहीं चाहिए। बकेट से जानकारी माँगने या टोकन खर्च करने पर गणना में बीता समय शामिल हो जाता है। API के विवरण के लिए [Bucket4j का रीफ़िल संदर्भ](https://bucket4j.com/8.22.0/toc.html) देखें।

## Spring MVC में अनुरोध कैसे सीमित करें?

![ऐप शुरू होने पर बना एक बकेट सभी अनुरोध इस्तेमाल करते हैं। बकेट बीते समय का हिसाब लगाकर एक टोकन लेने की कोशिश एक अविभाज्य क्रिया में करता है। सफलता पर 200 मिलता है। टोकन कम हों तो 429 और पूरे सेकंड तक ऊपर पूर्णांकित Retry-After मिलता है। अलग स्थानीय बकेट अपनी सीमा साझा नहीं करते।](/assets/diagrams/technical/hi-2026-11-11-bucket4j-token-bucket.svg)

कंट्रोलर अलग से टोकन गिनकर अनुमति का अनुमान लगाने के बजाय `tryConsumeAndReturnRemaining(1)` का परिणाम लेता है। `ConsumptionProbe` उसी प्रयास के लिए सफलता, बचे टोकन और टोकन कम होने पर प्रतीक्षा अवधि बताता है।

नीचे दी गई पाँच फ़ाइलें एक प्रोजेक्ट में रखें। सभी `/demo` अनुरोध एक ही बकेट इस्तेमाल करते हैं। उदाहरण में हर उपयोगकर्ता के लिए प्रमाणीकरण या बकेट स्टोर नहीं है। सर्वर केवल स्थानीय पते पर सुनता है।

### `settings.gradle`

```groovy
rootProject.name = 'bucket4j-token-bucket'
```

### `build.gradle`

```groovy
plugins {
    id 'java'
    id 'application'
}
repositories { mavenCentral() }
java { toolchain { languageVersion = JavaLanguageVersion.of(21) } }
dependencies {
    implementation platform('org.springframework.boot:spring-boot-dependencies:3.5.16')
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'com.bucket4j:bucket4j_jdk17-core:8.22.0'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
application { mainClass = 'example.RateLimitApplication' }
test { useJUnitPlatform() }
```

### `src/main/resources/application.yml`

```yaml
server:
  address: 127.0.0.1
```

### `src/main/java/example/BucketPolicy.java`

```java
package example;

import java.time.Duration;
import io.github.bucket4j.Bucket;
import io.github.bucket4j.TimeMeter;

public final class BucketPolicy {
    private BucketPolicy() {}

    public static Bucket local(TimeMeter clock) {
        return Bucket.builder()
                .withCustomTimePrecision(clock)
                .addLimit(limit -> limit.capacity(5).refillGreedy(5, Duration.ofSeconds(10)))
                .build();
    }
}
```

### `src/main/java/example/RateLimitApplication.java`

```java
package example;

import io.github.bucket4j.Bucket;
import io.github.bucket4j.TimeMeter;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
public class RateLimitApplication {
    public static void main(String[] args) {
        SpringApplication.run(RateLimitApplication.class, args);
    }

    @Bean
    Bucket demoBucket() {
        return BucketPolicy.local(TimeMeter.SYSTEM_NANOTIME);
    }

    @RestController
    public static class DemoController {
        private final Bucket bucket;

        public DemoController(Bucket bucket) {
            this.bucket = bucket;
        }

        @GetMapping("/demo")
        public ResponseEntity<String> demo() {
            var probe = bucket.tryConsumeAndReturnRemaining(1);
            if (probe.isConsumed()) {
                return ResponseEntity.ok("ok\n");
            }
            long seconds = Math.max(1, Math.ceilDiv(probe.getNanosToWaitForRefill(), 1_000_000_000L));
            return ResponseEntity.status(429)
                    .header("Retry-After", Long.toString(seconds))
                    .body("rate limit exceeded\n");
        }
    }
}
```

`Bucket` को Spring का डिफ़ॉल्ट सिंगलटन बीन रखने से उसकी स्थिति अगले अनुरोध तक बनी रहती है। कंट्रोलर मेथड के भीतर हर बार `Bucket.builder()` चलाने पर हर अनुरोध को नए शुरुआती टोकन मिलेंगे। कोड में जाँच मौजूद होगी लेकिन सीमा लागू नहीं होगी।

टोकन कम होने पर `tryConsumeAndReturnRemaining` अनुरोध थ्रेड को अगले टोकन के इंतज़ार में रोकने के बजाय अस्वीकृति लौटाता है। इससे पूरा MVC सर्वर नॉन-ब्लॉकिंग नहीं हो जाता। प्रतीक्षा वाला अलग API चुनें तो थ्रेड की प्रतीक्षा और अनुरोध टाइमआउट पर फिर विचार करें।

## कौन से जवाब मिलने चाहिए?

JDK 21 और Gradle 8.14.3 इंस्टॉल होने चाहिए और पोर्ट 8080 उपलब्ध होना चाहिए। Boot के Gradle प्लगइन या अलग Redis सर्वर की ज़रूरत नहीं है। पहली बार चलाने पर Maven Central से डिपेंडेंसी डाउनलोड होती हैं।

```sh
gradle run
```

सर्वर तैयार होने पर दूसरे टर्मिनल से कॉल करें। यहाँ मान लिया गया है कि बकेट नया है, कोई और उसे इस्तेमाल नहीं कर रहा और अगला टोकन भरने से पहले सभी छह कॉल पूरी हो जाती हैं।

```sh
for attempt in 1 2 3 4 5 6; do
  curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8080/demo
done
curl -i http://127.0.0.1:8080/demo
```

नीचे अपेक्षित स्टेटस कोड हैं। कॉल करने में अधिक समय लगे या बीच में और अनुरोध आएँ तो टोकन भरने या खर्च होने से परिणाम बदल सकता है।

```text
200
200
200
200
200
429
```

अस्वीकृत अनुरोध में `Retry-After` का मान `getNanosToWaitForRefill()` को अगले पूरे सेकंड तक ऊपर पूर्णांकित करके मिलता है। न्यूनतम मान एक सेकंड है। नियंत्रित घड़ी के साथ पाँचों टोकन खर्च करने के तुरंत बाद यह `2` था और 1.5 सेकंड बाद `1`। [HTTP 429 में Retry-After के अर्थ](https://www.rfc-editor.org/rfc/rfc6585#section-4) के अनुसार यह क्लाइंट को बताता है कि दोबारा प्रयास करने से पहले कितनी देर रुकें। कोई और अनुरोध अगला टोकन पहले ले सकता है, इसलिए प्रतीक्षा से टोकन आरक्षित नहीं होता।

जिस टर्मिनल में `gradle run` चल रहा है वहाँ `Ctrl+C` दबाकर उदाहरण सर्वर रोकें।

काम शुरू होने से पहले ही टोकन खर्च हो जाता है। बाद में काम विफल होने पर यह कोड उसे वापस नहीं करता। शुरू किए गए अनुरोधों और सफल कार्रवाइयों की सीमाओं में यह अंतर ध्यान में रखें।

## समवर्ती अनुरोधों और समय की जाँच कैसे हुई?

उदाहरण के दस परीक्षण वास्तविक Bucket4j 8.22.0 के साथ `TimeMeter` में नियंत्रित घड़ी देते हैं। समय बीतने के लिए `Thread.sleep` का सहारा नहीं लिया गया। [Intervally रीफ़िल का आधिकारिक परीक्षण](https://github.com/bucket4j/bucket4j/blob/8.22.0/bucket4j-core/src/test/java/io/github/bucket4j/core_algorithms/FixedIntervalRefillTest.java) भी घड़ी देने का तरीका दिखाता है।

| परीक्षण की स्थिति | देखा गया परिणाम |
| --- | --- |
| 40 कॉल, 8 वर्कर थ्रेड, एक बकेट और स्थिर घड़ी | ठीक 5 को अनुमति |
| 2 सेकंड पूरे होने से ठीक पहले और उसी क्षण जाँच, शुरुआत में 5 टोकन खर्च | ठीक पहले अस्वीकृति, फिर 1 को अनुमति जब 2 सेकंड पूरे हुए |
| लंबा समय बीतने पर | क्षमता 5 से अधिक टोकन नहीं |
| Greedy और Intervally में एक ही घड़ी | भरने का अंतर ऊपर की तालिका के अनुसार |
| अस्वीकृति के बाद समय बीता | अस्वीकृति से टोकन भरने की शुरुआत नहीं टली |
| दो स्वतंत्र बकेट | प्रत्येक से 5, कुल 10 टोकन खर्च हो सकते हैं |
| हर अनुरोध पर नया बकेट बनाएँ | 40 अनुरोधों को 40 नए बकेट से अनुमति मिली, सीमा निष्प्रभावी हुई |
| दो बैंडविड्थ सीमाओं वाला अलग बकेट | टोकन लेने के लिए दोनों सीमाएँ पूरी होनी चाहिए |
| Spring MVC की `MockMvc` कॉल | 200, 429 और प्रतीक्षा को अगले पूरे सेकंड तक पूर्णांकित करने की पुष्टि |

`MockMvc` की जाँच वास्तविक नेटवर्क अनुरोध से अलग है। पैकेज किए गए ऐप को एम्बेडेड Tomcat पर अलग से चलाकर असली HTTP `200` जवाब की पुष्टि की गई। समवर्ती कॉल की संख्या व्यवहार जाँचने के लिए चुनी गई थी। थ्रूपुट नहीं मापा गया।

## Redis Lua या Bucket4j कब चुनें?

| आधार | पिछले लेख का Redis Lua उदाहरण | यहाँ का स्थानीय Bucket4j उदाहरण |
| --- | --- | --- |
| नीति | पहले अनुरोध से शुरू अवधि में स्वीकृत अनुरोध | शुरुआती बर्स्ट और उसके बाद टोकन भरने की दर |
| साझा स्थिति | एक ही Redis और कुंजी इस्तेमाल करने वाले अनुरोध | एक JVM में एक ही बकेट ऑब्जेक्ट इस्तेमाल करने वाले अनुरोध |
| हर अनुरोध पर बाहरी स्टोर तक पहुँच | Redis में स्क्रिप्ट चलती है | कोई कॉल नहीं |
| सर्वर जोड़ने का असर | एक कुंजी की स्थिति साझा होने की धारणा | स्वतंत्र बकेट जुड़ने से कुल अनुमति बढ़ती है |

Redis केवल निश्चित विंडो तक और Bucket4j केवल स्थानीय बकेट तक सीमित नहीं हैं। तुलना इन दो लेखों में लागू की गई नीतियों और स्थिति रखने की जगह की है।

सभी सर्वरों पर एक सीमा चाहिए तो Bucket4j का वितरित स्टोर इंटीग्रेशन देखें। [Redis इंटीग्रेशन के 8.22.0 संदर्भ](https://bucket4j.com/8.22.0/toc.html) में Lettuce या दूसरे क्लाइंट के ज़रिए `ProxyManager` और एक साझा कुंजी में बकेट की स्थिति इस्तेमाल होती है। वर्णित CAS पद्धति में क्लाइंट स्थिति पढ़कर गणना करता है, फिर Redis में पुराने मान से तुलना करके उसे बदलता है। प्रतिस्पर्धा के कारण तुलना विफल हो तो प्रयास दोहराया जाता है। पिछले उदाहरण में बकेट की पूरी गणना Redis Lua की एक ही कॉल में होती थी।

वितरित स्थिति की समाप्ति भी नीति का हिस्सा है। छोटी TTL के कारण टोकन कम रहते हुए बकेट हट जाए तो अगली पहुँच पर शुरुआती टोकन वाला नया बकेट बन सकता है और अतिरिक्त अनुरोध स्वीकार हो सकते हैं। [आधिकारिक समाप्ति रणनीति](https://github.com/bucket4j/bucket4j/blob/8.22.0/bucket4j-core/src/main/java/io/github/bucket4j/distributed/ExpirationAfterWriteStrategy.java) के अनुसार बकेट पूरा भरने का समय और कुछ अतिरिक्त गुंजाइश रखें। जबरन निष्कासन या डेटा हानि के विरुद्ध इससे वही गारंटी नहीं मिलती।

यहाँ `SYSTEM_NANOTIME` स्थानीय बकेट के लिए है। अलग-अलग JVM में इसे अपने आप साझा समय का आधार न मानें। वितरित व्यवस्था में इंटीग्रेशन के समय स्रोत, टाइमआउट और CAS पुनःप्रयास की सेटिंग अपनाएँ। अलग से तय करें कि Redis विफल होने पर अनुरोध रोकेंगे या सीमित स्थानीय नीति से अस्थायी अनुमति देंगे। यहाँ का कोड Redis इंटीग्रेशन या फ़ेलओवर नहीं चलाता।

प्रति-उपयोगकर्ता सीमा के लिए बकेट की कुंजी प्रमाणित पहचान और नीति के दायरे से बनाएँ। अनुरोध के हेडर में आए किसी भी पहचानकर्ता पर भरोसा करने से क्लाइंट कुंजी बदलकर सीमा पार कर सकता है। स्थानीय `Map` में लगातार उपयोगकर्ताओं के बकेट जोड़ने से मेमोरी बढ़ती है और लापरवाही से बकेट हटाने या फिर बनाने पर बार-बार शुरुआती टोकन मिल सकते हैं। तय करें कि स्थिति कहाँ और कितनी देर रहेगी।

अनुरोध शुरू होने की दर सीमित करने पर भी लंबे समय तक संसाधन घेरे रखने वाले कामों की समवर्ती संख्या बढ़ सकती है। डेटाबेस कनेक्शन या बाहरी API की समवर्ती कॉल सुरक्षित रखनी हों तो अलग समवर्ती सीमा भी तय करें।
