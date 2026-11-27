---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2026-10-31-jdk25-scopedvalue",
  "routeSlug": "2026-10-31-jdk25-scopedvalue",
  "kind": "post",
  "title": "JDK 25 में ScopedValue से अनुरोध का संदर्भ कैसे दें?",
  "description": "वर्चुअल थ्रेड पर स्थायी ScopedValue API चलाएँ। देखें कि नेस्टेड बाइंडिंग और अपवाद के बाद पुराना मान कैसे लौटता है और साधारण चाइल्ड थ्रेड उसे विरासत में क्यों नहीं पाता।",
  "categories": [
    "jdk"
  ],
  "tags": [
    "java",
    "jdk25",
    "scopedvalue",
    "threadlocal",
    "virtual-threads"
  ],
  "sourcePath": "src/content/posts/en/2026-10-31-jdk25-scopedvalue.md",
  "sourceSha256": "b1b2085e75caffb25a2838a9d99da8e4b63dd107657a94ad5e08730bb04fbf66",
  "draftSha256": "e63818cbc74ae18b445e979e6562b84ca06ce1a926133f7ff7fd6f9c011e2b7e",
  "manifestPath": ".pipeline/technical-translations/batch-1362/manifest.json",
  "manifestSha256": "c23292bb868eee9c0eca35de8d905b8be8115647d25cc8fc6b3385913bd5ec68",
  "publishedAt": "2026-11-27T09:29:11.248Z",
  "updatedAt": "2026-11-27T09:29:11.248Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 212,
    "approvedAt": "2026-11-27T09:29:11.248Z",
    "basis": "User authorized publication of these five existing articles in Hindi in item 136."
  }
}
---
JDK 25 में **`ScopedValue` एक स्थायी API है जिससे अनुरोध का संदर्भ जैसा डेटा निष्पादन के सीमित दायरे में बाँधकर कॉलर से उसके बुलाए गए कोड तक पहुँचाया जा सकता है**। [JEP 506](https://openjdk.org/jeps/506) ने इसे स्थायी किया, इसलिए प्रीव्यू फ़्लैग की ज़रूरत नहीं है। बाइंडिंग तब तक लागू रहती है जब तक `run()` या `call()` को दिया ऑपरेशन चलता है। सामान्य वापसी और अपवाद, दोनों में पिछली स्थिति बहाल होती है।

## यह ThreadLocal से कैसे अलग है?

जब सेवा के भीतर गहरे किसी मेथड तक टेनेंट या ट्रेस ID पहुँचाने के लिए बीच के हर मेथड में पैरामीटर जोड़ना पड़े, तब इस विकल्प पर विचार करें। अगर मान सीधे कारोबारी लॉजिक का इनपुट है तो साधारण पैरामीटर अधिक स्पष्ट हो सकता है।

[`ThreadLocal`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/ThreadLocal.html) में `set()` मौजूदा थ्रेड का मान बदलता है और `remove()` उसे हटाता है। अनुरोध तक सीमित उपयोग में सफ़ाई सावधानी से करनी पड़ती है, आम तौर पर `finally` में। `ScopedValue` ज़रूरत वाले ऑपरेशन को बाइंडिंग के भीतर चलाता है, इसलिए मान सेट करके छोड़ना नहीं पड़ता।

| तुलना | ThreadLocal | ScopedValue |
| --- | --- | --- |
| डेटा तक पहुँच | मौजूदा थ्रेड में रखा मान पढ़ें या बदलें | निष्पादन के मौजूदा गतिशील दायरे की बाइंडिंग पढ़ें |
| दायरे का अंत | अनुरोध पूरा होने पर सफ़ाई स्वयं करें | `run()` या `call()` समाप्त होते ही पिछली बाइंडिंग लौटती है |
| बुलाए गए मेथड को दूसरा मान चाहिए | `set()` मौजूदा मान बदल सकता है | अंदर के दायरे में नई बाइंडिंग बनाएँ, वापसी पर बाहरी मान लौटता है |
| उपयोग के उदाहरण | थ्रेड की परिवर्तनशील स्थिति | कॉलर से बुलाए गए मेथड तक अनुरोध का संदर्भ देना |

`ScopedValue` न तो `ThreadLocal` के हर उपयोग की जगह लेता है और न उसे अप्रचलित घोषित करता है। `private static final` फ़ील्ड में **संदर्भ तक पहुँचने की कुंजी** होती है। संदर्भ का मान थ्रेड और दायरे पर निर्भर करता है, इसलिए एक ही कुंजी अलग मान दे सकती है।

## वर्चुअल थ्रेड में बाइंडिंग और उसकी बहाली देखें

![वर्चुअल थ्रेड में बाहरी मान बाँधें। अंदर का काम सामान्य रूप से लौटने या विफल होने पर बाहरी मान जाँचें। देखें कि साधारण चाइल्ड थ्रेड बाइंडिंग नहीं पाता, फिर दायरे से बाहर निकलें।](/assets/diagrams/technical/hi-2026-10-31-jdk25-scopedvalue.svg)

चित्र नीचे के कोड का क्रम दिखाता है। बाहरी टेनेंट `tenant-a` है और अंदर का दायरा `tenant-b` पढ़ता है। अंदर के दायरे में विफलता होने पर अपवाद उसके बाहर पकड़ा जाता है और फिर बहाल मान जाँचा जाता है। उदाहरण HTTP सर्वर या फ़्रेमवर्क के बिना अनुरोध के संदर्भ का व्यवहार दिखाता है।

ऐसी डायरेक्टरी में चलाएँ जहाँ `javac` और `java` एक ही JDK 25 इंस्टॉलेशन के हों। स्थानीय जाँच macOS AArch64 पर Eclipse Temurin `25.0.5+8` में हुई। `ScopedValue` पैकेज `java.lang` का हिस्सा है, इसलिए अलग import नहीं चाहिए।

### `ScopedContextExample.java`

```java
import java.util.NoSuchElementException;
import java.util.concurrent.Executors;

public class ScopedContextExample {
    private static final ScopedValue<RequestContext> CONTEXT = ScopedValue.newInstance();
    record RequestContext(String tenant, String traceId) {}

    public static void main(String[] args) throws Exception {
        try (var tasks = Executors.newVirtualThreadPerTaskExecutor()) {
            tasks.submit(ScopedContextExample::handleRequest).get();
        }
    }

    private static String handleRequest() throws InterruptedException {
        System.out.println("virtual=" + Thread.currentThread().isVirtual());
        System.out.println("before=" + CONTEXT.isBound());
        String result = ScopedValue.where(CONTEXT,
                new RequestContext("tenant-a", "trace-123")).call(() -> {
            System.out.println("outer=" + service());
            ScopedValue.where(CONTEXT,
                    new RequestContext("tenant-b", "trace-123")).run(() ->
                System.out.println("nested=" + service()));
            System.out.println("restored=" + service());

            try {
                ScopedValue.where(CONTEXT,
                        new RequestContext("tenant-fail", "trace-123")).run(() -> {
                    throw new IllegalStateException("demonstration");
                });
            } catch (IllegalStateException expected) {
                System.out.println("after-failure=" + service());
            }

            Thread child = Thread.ofVirtual().start(() ->
                System.out.println("plain-child-bound=" + CONTEXT.isBound()));
            child.join();
            return service();
        });
        System.out.println("result=" + result);
        System.out.println("after=" + CONTEXT.isBound());
        try {
            CONTEXT.get();
        } catch (NoSuchElementException expected) {
            System.out.println("outside=" + expected.getClass().getSimpleName());
        }
        return result;
    }

    private static String service() {
        RequestContext context = CONTEXT.get();
        return context.tenant() + "/" + context.traceId();
    }
}
```

```sh
javac --release 25 ScopedContextExample.java
java ScopedContextExample
```

प्रीव्यू विकल्पों के बिना यह मानक आउटपुट मिला। `Future` पर `get()` बुलाने से काम की विफलता कॉलर तक पहुँचती है। `join()` चाइल्ड थ्रेड के आउटपुट की प्रतीक्षा करता है।

```text
virtual=true
before=false
outer=tenant-a/trace-123
nested=tenant-b/trace-123
restored=tenant-a/trace-123
after-failure=tenant-a/trace-123
plain-child-bound=false
result=tenant-a/trace-123
after=false
outside=NoSuchElementException
```

`service()` बिना संदर्भ पैरामीटर के मौजूदा बाइंडिंग पढ़ता है। बिना परिणाम वाले ऑपरेशन के लिए `run()` और परिणाम लौटाने या अपवाद आगे देने वाले ऑपरेशन के लिए [`Carrier.call()`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/ScopedValue.Carrier.html#call(java.lang.ScopedValue.CallableOp)) इस्तेमाल करें। केवल `where()` से `Carrier` बनाने से बाइंडिंग सक्रिय नहीं होती।

`restored` और `after-failure` दोनों में बाहरी मान दिखता है। बाहरी `call()` लौटने पर `isBound()` false होता है और बिना बाइंडिंग के `get()` बुलाने पर `NoSuchElementException` मिलता है। बाइंडिंग समाप्त होने से संबंधित ऑब्जेक्ट के तत्काल गार्बेज कलेक्शन की गारंटी नहीं मिलती और `AutoCloseable` संसाधन अपने आप बंद नहीं होता।

## क्या नया वर्चुअल थ्रेड मान विरासत में पाता है?

**साधारण `Thread.ofVirtual().start()` अपने पैरेंट की बाइंडिंग अपने आप नहीं पाता।** उदाहरण में इसे `plain-child-bound=false` दिखाता है। `ExecutorService` या `CompletableFuture` को काम देने पर भी संदर्भ अपने आप पहुँचने की धारणा न रखें। उदाहरण का पहला वर्चुअल थ्रेड काम के भीतर अपनी बाइंडिंग बनाता है।

[आधिकारिक विरासत नियमों](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/ScopedValue.html#inheritance) के अनुसार `StructuredTaskScope` बनाते समय बाइंडिंग कैप्चर की जाती हैं। उस दायरे के `fork()` से शुरू हुए चाइल्ड थ्रेड उन्हें पाते हैं। **JDK 25 में स्ट्रक्चर्ड कन्करेंसी अलग प्रीव्यू API है**, जिसका विवरण [JEP 505](https://openjdk.org/jeps/505) में है। यहाँ का कोड उसका उपयोग नहीं करता और विरासत की उस प्रक्रिया को नहीं जाँचता।

## अनुरोध के संदर्भ में अपनाते समय क्या देखें?

बाइंडिंग का बदल न सकना उससे जुड़े ऑब्जेक्ट को पूरी तरह अपरिवर्तनीय नहीं बनाता। उदाहरण में दो स्ट्रिंग वाला रिकॉर्ड है। परिवर्तनशील कलेक्शन साझा करने पर समवर्ती पहुँच का अलग डिज़ाइन चाहिए। कुंजी तक पहुँच भी सीमित रखें।

JDK 25 का API देखकर ही JDK 21 जैसे पुराने संस्करणों के प्रीव्यू उदाहरण अपनाएँ। विशेष रूप से JDK 25 में `orElse(null)` मान्य नहीं है। `null` से बाइंडिंग होने और बाइंडिंग न होने में भी अंतर है।

पहले देखें कि `ThreadLocal` कॉल शृंखला में अनुरोध का डेटा पहुँचाता है या चलते समय परिवर्तनशील स्थिति रखता है। पहले मामले में प्रवेश बिंदु की बाइंडिंग और असिंक्रोनस काम में संदर्भ पहुँचाने की सीमा, दोनों तय करें। फ़्रेमवर्क ट्रांज़ैक्शन, MDC और सुरक्षा संदर्भ अपने आप नहीं जुड़ते। यहाँ उन एकीकरणों या प्रदर्शन की जाँच नहीं हुई। वर्चुअल थ्रेड का व्यवहार समझने के लिए [JDK 21 फ़ीचर लेख](/en/posts/2023-09-20-jdk-21-release/) देखें।
