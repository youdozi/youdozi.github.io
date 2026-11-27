---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2026-10-31-failure-fallback",
  "routeSlug": "2026-10-31-failure-fallback",
  "kind": "post",
  "title": "विफलता पर क्या लौटाएँ? पुराना डेटा, सीमित सुविधा या अनुरोध की अस्वीकृति",
  "description": "बाहरी API, कैश और भुगतान में विफलता पर तय करें कि कौन सा विकल्प स्वीकार्य है। Java में डेटा की उम्र और समवर्ती अनुरोधों की सीमा जाँचें, फिर पुनः प्रयास, बहाली और निगरानी की योजना बनाएँ।",
  "categories": [
    "architecture"
  ],
  "tags": [
    "fallback",
    "resilience",
    "java",
    "timeout",
    "circuit-breaker",
    "load-shedding"
  ],
  "sourcePath": "src/content/posts/en/2026-10-31-failure-fallback.md",
  "sourceSha256": "93196b5c0ce64194996df961642c87053d74ea5be5c63b2b776cdd598dc7effd",
  "draftSha256": "a99e16d340c7a709b778480af8454c963b1edbfe4fee6be599c349a06afb05ff",
  "manifestPath": ".pipeline/technical-translations/batch-1371/manifest.json",
  "manifestSha256": "d570f04b54d96c1161dbd7074fa5bbda3ac5c65e9814d6303b13febc95054f68",
  "publishedAt": "2026-11-27T09:48:30.014Z",
  "updatedAt": "2026-11-27T09:48:30.014Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 213,
    "approvedAt": "2026-11-27T09:48:30.014Z",
    "basis": "User authorized publication of these five existing articles in Hindi in item 137."
  }
}
---

सेवा में बाधा आने पर **फ़ॉलबैक की प्रतिक्रिया पहले से तय न्यूनतम गुणवत्ता पूरी करे और उसे देने की लागत सिस्टम उठा सके**। मसलन, सुझावों का खंड हटा सकते हैं या तय उम्र के भीतर का सार्वजनिक डेटा लौटा सकते हैं। भुगतान का नतीजा अज्ञात होते हुए सफलता दिखाना या कैश विफल होते ही हर अनुरोध डेटाबेस को भेजना नई समस्याएँ पैदा करता है।

यह मार्गदर्शिका HTTP API संचालित करने वाले डेवलपरों के लिए है। [10k RPS आर्किटेक्चर](/ko/posts/2026-10-31-jdk-10k-rps-architecture/) में ओवरलोड नियंत्रण देखने के बाद यहाँ हम तय करते हैं कि विफलता के दौरान कौन सी प्रतिक्रिया लौटाई जाए। Java उदाहरण बिना बाहरी सर्वर के फ़ॉलबैक नीति चलाता है। इसमें थ्रूपुट या प्रोडक्शन में सेवा बहाल होने की प्रक्रिया नहीं मापी गई है।

## अलग विफलताओं में अलग परिणाम स्वीकार्य होते हैं

पहले तय करें कि सामान्य परिणाम से क्या हट सकता है। नीचे डिज़ाइन के उदाहरण हैं। असल में डेटा कितनी देर तक स्वीकार्य है और कौन सी सुविधा घट सकती है, यह सेवा अनुबंध से तय करें।

| विफलता | स्वीकार्य विकल्प | कब रोकें या सीमा लगाएँ |
| --- | --- | --- |
| सुझाव देने वाला API धीमा है या विफल हुआ | वैकल्पिक सुझाव हटाएँ या पहले से तैयार सामान्य सुझाव दें | उत्पाद की मुख्य जानकारी पढ़ने के अनुरोध उसी कतार में न डालें |
| उत्पाद का सार्वजनिक विवरण पढ़ना विफल हुआ | उसी उत्पाद और भाषा का पिछली बार सफलतापूर्वक पढ़ा डेटा और उसके अपडेट का समय लौटाएँ | अधिकतम उम्र पार हो, डेटा न मिले या कुंजी गलत हो |
| पूरा कैश अनुपलब्ध है | मूल स्रोत से सीमित मात्रा में पढ़ें, स्वीकृत स्थानीय प्रति दें या अतिरिक्त अनुरोध अस्वीकार करें | डेटाबेस कनेक्शन और समवर्ती काम की सीमा लाँघकर हर अनुरोध सीधे न भेजें |
| पहचान या अनुमति की जाँच विफल हुई | संरक्षित काम किए बिना अस्थायी त्रुटि लौटाएँ | जाँच की विफलता को अनुमति का अभाव न समझें और न ही अपने आप पहुँच दे दें |
| भुगतान या ऑर्डर भेजने के बाद प्रतिक्रिया खो गई | उसी ऑपरेशन पहचानकर्ता से स्थिति पूछें और रिकॉर्ड का मिलान करें | विफलता मानकर नया भुगतान न करें और मनगढ़ंत सफलता न दिखाएँ |
| वैकल्पिक सर्वर भी वही डेटाबेस इस्तेमाल करता है | केवल अलग से जाँची गई क्षमता तक ट्रैफ़िक बदलें | सर्वर बदलने से साझा डेटाबेस की बाधा दूर नहीं होती |

अनुमति, अंतिम कीमत और स्टॉक घटाने जैसे कामों में सही नतीजा ज़रूरी है। इन्हें साधारण पुराने डेटा की रीड से अलग रखें। भुगतान की स्थिति “जाँच जारी है” तभी सार्थक है जब वास्तव में अनुरोध को ट्रैक करके उसकी स्थिति पूछ सकें। संदेश या प्रतिक्रिया का नाम बदलने भर से अनिश्चित नतीजा नहीं सुलझता।

AWS ने [वितरित सिस्टम में फ़ॉलबैक के जोखिमों](https://aws.amazon.com/builders-library/avoiding-fallback-in-distributed-systems/) में बताया है कि कम इस्तेमाल होने वाले रास्तों की जाँच अक्सर अधूरी रहती है और विकल्प नई समस्याएँ ला सकते हैं। सामान्य रास्ते की तरह फ़ॉलबैक भी चलाकर देखें। जाँचें कि दोनों कहीं उन्हीं संसाधनों पर निर्भर तो नहीं हैं।

## टाइमआउट, पुनः प्रयास और सर्किट ब्रेकर क्या करते हैं?

टाइमआउट कॉलर की प्रतीक्षा सीमित करता है। **प्रतीक्षा समाप्त होने का अर्थ यह नहीं है कि दूर की सेवा में ऑपरेशन या भुगतान रद्द हो गया।** पुनः प्रयास वही काम दोबारा करता है। फ़ेलओवर में अनुरोध दूसरी प्रतिकृति पर जाता है। फ़ॉलबैक में कम सुविधा वाली प्रतिक्रिया या दूसरा प्रसंस्करण तरीका अपनाते हैं। बार-बार विफलता के बाद सर्किट ब्रेकर तय शर्तों पर निर्भर सेवा को कॉल रोकता है। सुरक्षित वैकल्पिक प्रतिक्रिया अलग नीति से तय होती है।

पूरे अनुरोध की समय-सीमा में कनेक्शन स्थापित करना, पूल की प्रतीक्षा, प्रतिक्रिया की प्रतीक्षा, पुनः प्रयास और वैकल्पिक काम सभी शामिल करें। कुल 300ms में से पहली कॉल पर 250ms बीत चुके हों तो फिर 250ms इंतज़ार नहीं कर सकते। ये संख्याएँ समझाने के लिए हैं। इन्हें अनुशंसित सेटिंग न मानें। अपने क्लाइंट में यह भी जाँचें कि हर चरण का टाइमआउट क्या-क्या मापता है।

[AWS की पुनः प्रयास संबंधी मार्गदर्शिका](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) बताती है कि पुनः प्रयास लोड बढ़ाते हैं और प्रतिक्रिया विफल होने पर भी ऑपरेशन का प्रभाव हो चुका हो सकता है। पुनः प्रयास की ज़िम्मेदारी एक परत को दें। केवल अस्थायी विफलताओं पर, जब काम दोहराना सुरक्षित हो, बचे समय और प्रयासों की गिनती सीमित रखें। एक्सपोनेंशियल बैकऑफ़ और जिटर एक साथ होने वाले प्रयासों को अलग-अलग समय पर फैलाते हैं। वे पहले से भरे डेटाबेस की क्षमता नहीं बढ़ाते।

## Java उदाहरण में केवल स्वीकृत सार्वजनिक डेटा सीमित समय तक लौटाएँ

उदाहरण **एक तय उत्पाद का सार्वजनिक विवरण** पढ़ता है। सामान्य प्रतिक्रिया को प्राथमिकता मिलती है। केवल `Unavailable` के रूप में पहचानी गई निर्भर सेवा की विफलता पर पिछली सफल प्रति लौट सकती है। प्रति अधिकतम 60 सेकंड पुरानी हो सकती है। भविष्य का टाइमस्टैम्प स्वीकार नहीं होता। 2 की सीमा और 60 सेकंड की अवधि प्रदर्शन के लिए हैं। अलग उत्पादों, भाषाओं या टेनेंटों के लिए अलग कुंजियाँ चाहिए। इस उदाहरण को ज्यों का त्यों प्रमाणित उपयोगकर्ताओं का डेटा कैश करने में न लगाएँ।

![परमिट न मिले तो तुरंत अस्वीकार करें। मिले तो मुख्य स्रोत से पढ़कर परिणाम दें। केवल तय विफलता पर प्रति की उपलब्धता और उम्र जाँचकर फ़ॉलबैक लौटाएँ](/assets/diagrams/technical/hi-2026-10-31-failure-fallback.svg)

चित्र `read()` के निर्णय दिखाता है। परमिट पाने वाला हर रास्ता `finally` में उसे लौटाता है, चाहे मुख्य परिणाम मिले या अपवाद उठे। इसमें टाइमआउट, सर्किट ब्रेकर या कैश रीफ़्रेश लागू नहीं है। वास्तविक HTTP अडैप्टर को केवल स्वीकृत विफलताओं, जैसे कनेक्शन विफलता और टाइमआउट, को `Unavailable` में बदलना चाहिए। 401, 403, 404, स्कीमा की त्रुटियों और प्रोग्रामिंग की गलतियों को भी इसी अपवाद में बदलने से नीति का अर्थ बदल जाता है।

इसे `FallbackDemo.java` में सेव करें। यह JDK 21 या बाद के संस्करण पर बिना बाहरी निर्भरता के चलता है।

```java
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.concurrent.Semaphore;
import java.util.function.Supplier;

public class FallbackDemo {
    record Snapshot(String value, Instant observedAt) {}
    record Reply(String value, String source, long ageSeconds) {}
    static class Unavailable extends RuntimeException {}
    static class Rejected extends RuntimeException {
        Rejected(String reason) { super(reason); }
    }

    static final class Catalog {
        private final Semaphore slots = new Semaphore(2);
        private final Clock clock;
        private final Duration maxAge = Duration.ofSeconds(60);

        Catalog(Clock clock) { this.clock = clock; }

        Reply read(Supplier<String> primary, Snapshot snapshot) {
            if (!slots.tryAcquire()) throw new Rejected("capacity");
            try {
                try {
                    return new Reply(primary.get(), "primary", 0);
                } catch (Unavailable failure) {
                    if (snapshot == null) throw new Rejected("missing");
                    Duration age = Duration.between(
                            snapshot.observedAt(), clock.instant());
                    if (age.isNegative() || age.compareTo(maxAge) > 0) {
                        throw new Rejected("age");
                    }
                    return new Reply(snapshot.value(), "snapshot", age.toSeconds());
                }
            } finally {
                slots.release();
            }
        }
    }

    static void rejected(String reason, Runnable action) {
        try {
            action.run();
        } catch (Rejected e) {
            if (!reason.equals(e.getMessage())) throw new AssertionError(e);
            System.out.println("rejected=" + reason);
            return;
        }
        throw new AssertionError("Expected rejection: " + reason);
    }

    public static void main(String[] args) {
        Instant now = Instant.parse("2026-10-31T00:00:00Z");
        Catalog catalog = new Catalog(Clock.fixed(now, ZoneOffset.UTC));
        Snapshot recent = new Snapshot("saved-description", now.minusSeconds(30));
        Supplier<String> down = () -> { throw new Unavailable(); };

        System.out.println(catalog.read(() -> "live-description", recent));
        System.out.println(catalog.read(down, recent));
        System.out.println(catalog.read(down,
                new Snapshot("boundary", now.minusSeconds(60))));
        rejected("age", () -> catalog.read(down,
                new Snapshot("old", now.minusSeconds(60).minusNanos(1))));
        rejected("age", () -> catalog.read(down,
                new Snapshot("future", now.plusSeconds(1))));
        rejected("missing", () -> catalog.read(down, null));

        try {
            catalog.read(() -> { throw new IllegalStateException("schema"); }, recent);
            throw new AssertionError("Unexpected fallback");
        } catch (IllegalStateException expected) {
            System.out.println("propagated=" + expected.getMessage());
        }

        // Hold both permits through nested calls; the third call must not run.
        catalog.read(() -> catalog.read(() -> {
            rejected("capacity", () -> catalog.read(() -> {
                throw new AssertionError("Primary ran without a permit");
            }, recent));
            return "inner";
        }, recent).value(), recent);
        System.out.println(catalog.read(() -> "recovered", recent));
    }
}
```

```sh
javac --release 21 FallbackDemo.java
java FallbackDemo
```

नीचे का आउटपुट Zulu JDK `21.0.1+12-LTS` पर मिला।

```text
Reply[value=live-description, source=primary, ageSeconds=0]
Reply[value=saved-description, source=snapshot, ageSeconds=30]
Reply[value=boundary, source=snapshot, ageSeconds=60]
rejected=age
rejected=age
rejected=missing
propagated=schema
rejected=capacity
Reply[value=recovered, source=primary, ageSeconds=0]
```

`source=snapshot` और `ageSeconds` एप्लिकेशन के मेटाडेटा हैं जिनसे क्लाइंट को पता चलता है कि प्रतिक्रिया की गुणवत्ता घटी है। ये HTTP का `Age` हेडर लागू नहीं करते। अधिकतम उम्र की तुलना सटीक `Duration` से होती है। केवल दिखाई जाने वाली उम्र पूरे सेकंड में है।

परमिट उपलब्ध न होने पर [Semaphore का `tryAcquire()`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/Semaphore.html) बिना प्रतीक्षा किए विफल होता है। फ़ॉलबैक भी उसी प्रवेश सीमा में आता है, इसलिए क्षमता भर जाने पर प्रति भी नहीं लौटती। प्रोडक्शन में प्रतियों के लिए अलग कम लागत वाला रास्ता दें तो उसकी भी अपनी सीमा रखें। नेस्टेड कॉल से परमिट का ख़त्म होना निश्चित क्रम में दिखता है। यह समवर्ती लोड टेस्ट नहीं है।

उदाहरण में सफल रीड को सहेजना और रीफ़्रेश करना, संग्रहण सीमा, पुरानी प्रविष्टियाँ हटाना, एक जैसे अनुरोध मिलाना या रीस्टार्ट के बाद प्रतियाँ बहाल करना लागू नहीं है। प्रोडक्शन में सफल रीड से ही प्रति अपडेट करें और **प्रति लौटाते समय उसका संग्रहीत टाइमस्टैम्प न बदलें**। हर फ़ॉलबैक पर समय बदलने से पुराना मान हमेशा स्वीकार्य रह सकता है। लंबे समय तक रखी प्रतियों की नीति में सिस्टम घड़ी के समायोजन को भी ध्यान में रखें।

## सेवा बहाल करने की शर्तें भी तय करें

[ओवरलोड पर Google SRE की मार्गदर्शिका](https://sre.google/sre-book/handling-overload/) बताती है कि सीमित प्रतिक्रिया देने की क्षमता भी न बचे तो त्रुटि लौटानी पड़ सकती है। प्रवेश अस्वीकार होने या वैध प्रति न मिलने से सेवा अस्थायी रूप से अनुपलब्ध हो तो HTTP अनुबंध के अनुसार 503 दे सकते हैं। दोबारा प्रयास का भरोसेमंद समय मालूम हो तो `Retry-After` भेज सकते हैं। सिर्फ़ हेडर देने से क्लाइंटों की भीड़ नहीं रुकती। 504 का अर्थ है कि गेटवे या प्रॉक्सी को अपस्ट्रीम सर्वर से समय पर जवाब नहीं मिला। यह हर एप्लिकेशन टाइमआउट का कोड नहीं है। [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html#name-server-error-5xx)

सर्किट ब्रेकर बंद होते ही सारे अनुरोध मुख्य स्रोत को लौटाने से सँभल रहा सर्वर फिर भर सकता है। हाफ़-ओपन स्थिति में थोड़ी जाँच कॉल से शुरुआत करें। फिर ट्रैफ़िक धीरे बढ़ाएँ और स्नैपशॉट रीफ़्रेश तथा कैश भरने के अनुरोध भी सीमित करें। सामान्य प्रतिक्रिया का विलंब, विफलता दर, डेटाबेस कनेक्शन की प्रतीक्षा या कतार में लंबित काम स्वीकार्य सीमा पार करें तो बढ़ोतरी कब रोकनी है या पिछले चरण पर कब लौटना है, पहले तय करें। वास्तविक लोड टेस्ट से अनुपात और निगरानी की अवधि निकालें।

पहली बार लागू करते समय एक वैकल्पिक रीड चुनें और उसकी निर्भर सेवा में विफलता उत्पन्न करें। प्रति गायब होने, अधिकतम उम्र की सीमा, भविष्य के टाइमस्टैम्प, सारे परमिट भरने, अवर्गीकृत अपवाद और निर्भर सेवा की बहाली को जाँचें। वास्तविक सर्वर पर धीमी प्रतिक्रिया, कनेक्शन पूल भरना, पूरा कैश बंद होना, मुख्य और वैकल्पिक रास्तों का एक साथ विफल होना और बहाली के समय एक साथ होने वाले पुनः प्रयास भी परखें।

निगरानी में सामान्य परिणाम, फ़ॉलबैक, अस्वीकृति और विफलता अलग गिनें। केवल HTTP 200 की दर देखने पर वह बाधा छिप सकती है जिसमें अधिकतर प्रतिक्रियाएँ पुराना डेटा दे रही हैं। फ़ॉलबैक का अनुपात, डेटा की उम्र, हर निर्भर सेवा की विफलताएँ, प्रवेश पर अस्वीकृतियाँ और जारी अनुरोध साथ देखें। फ़ॉलबैक से बाधा का असर कितना घटा, यह जानने के लिए **व्यावसायिक काम पूरा करने वाले अनुरोधों और घटी गुणवत्ता पर सँभाले गए अनुरोधों में अंतर रखें**।
