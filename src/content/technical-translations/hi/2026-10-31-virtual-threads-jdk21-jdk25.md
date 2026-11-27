---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2026-10-31-virtual-threads-jdk21-jdk25",
  "routeSlug": "2026-10-31-virtual-threads-jdk21-jdk25",
  "kind": "post",
  "title": "Java के वर्चुअल थ्रेड: JDK 21 और 25 में JFR से पिनिंग की जाँच",
  "description": "कैरियर और I/O प्रतीक्षा का संबंध समझें। एक ही JFR प्रयोग से दो JDK में synchronized के भीतर पिनिंग की तुलना करें और देखें कि कौन से API स्थायी हैं और कौन सी बाधाएँ बनी रहती हैं।",
  "categories": [
    "jdk"
  ],
  "tags": [
    "java",
    "virtual-threads",
    "jdk21",
    "jdk25",
    "jfr",
    "pinning"
  ],
  "sourcePath": "src/content/posts/en/2026-10-31-virtual-threads-jdk21-jdk25.md",
  "sourceSha256": "4b100d81b2721e31e0a765676927aa48165b4b60c224dff2ba5846ba70dec8db",
  "draftSha256": "10bacd963eaa2a563385a293be40476477452a4630b385c813076bebedea9676",
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
वर्चुअल थ्रेड **ऐसे Java थ्रेड हैं जिनकी मदद से I/O की प्रतीक्षा करने वाले अनेक काम कम OS थ्रेड साझा कर सकते हैं**। JDK 21 में [JEP 444](https://openjdk.org/jeps/444) के साथ ये स्थायी फ़ीचर बने। JDK 25 में भी इनके बुनियादी API वही हैं। एक अहम अंतर तब दिखता है जब कोई थ्रेड `synchronized` के भीतर ब्लॉक होता है। [JEP 491](https://openjdk.org/jeps/491) ने JDK 24 में इससे होने वाली पिनिंग कम की और यह सुधार JDK 25 में भी है।

## वर्चुअल थ्रेड से किस काम का खर्च घटता है?

चलने के लिए वर्चुअल थ्रेड को भी OS थ्रेड चाहिए। JVM उस प्लेटफ़ॉर्म थ्रेड को **कैरियर** कहती है जिस पर वर्चुअल थ्रेड चल रहा है। जब किसी समर्थित ब्लॉकिंग ऑपरेशन पर वर्चुअल थ्रेड कैरियर से उतर सकता है, तब कैरियर दूसरा वर्चुअल थ्रेड चला सकता है।

इससे ऐसे अनुरोध सँभालने में मदद मिलती है जिनमें कई काम एक साथ प्रतीक्षा करते हैं। इससे CPU की गणना तेज़ नहीं होती, न ही किसी एक अनुरोध की लेटेंसी अपने आप घटती है। [आधिकारिक मार्गदर्शिका](https://docs.oracle.com/en/java/javase/25/core/virtual-threads.html) हर काम के लिए अलग वर्चुअल थ्रेड बनाने की सलाह देती है और छोटे पूल में उनका पुनः उपयोग करने से मना करती है। थ्रेड बढ़ाने से डेटाबेस कनेक्शन या बाहरी API का कोटा नहीं बढ़ता। उन संसाधनों की सीमा सेमाफ़ोर या कनेक्शन पूल से अलग तय करें।

## JDK 21 और 25 में क्या अंतर है?

| विषय | JDK 21 | JDK 25 |
| --- | --- | --- |
| वर्चुअल थ्रेड API | स्थायी, प्रीव्यू फ़्लैग की ज़रूरत नहीं | स्थायी, थ्रेड बनाने के बुनियादी API कायम |
| `synchronized` में ब्लॉक होना | कैरियर पिन हो सकता है और स्केलिंग सीमित हो सकती है | JDK 24 का JEP 491 सुधार शामिल |
| क्या सारी पिनिंग समाप्त हो गई? | नहीं | नहीं। जैसे, नेटिव कोड से वापस बुलाया गया Java कोड ब्लॉक हो सकता है |
| निदान | JFR और `jdk.tracePinnedThreads` जैसे साधन | JFR में सुधार। `jdk.tracePinnedThreads` का कोई असर नहीं |
| `ScopedValue` | प्रीव्यू | JEP 506 के साथ स्थायी |
| स्ट्रक्चर्ड कन्करेंसी | प्रीव्यू | अलग प्रीव्यू API। पिछले API के साथ संगतता न मानें |

इन बदलावों को समझने के लिए [JDK 21 की मार्गदर्शिका](https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html), JEP 491 और [ScopedValue पर लेख](/en/posts/2026-10-31-jdk25-scopedvalue/) साथ पढ़ें। वर्चुअल थ्रेड, ScopedValue और स्ट्रक्चर्ड कन्करेंसी के स्थायी होने की समयरेखा अलग-अलग है।

पिनिंग होने पर प्रतीक्षा करता वर्चुअल थ्रेड अपना कैरियर छोड़ नहीं पाता। JDK 25 में केवल `synchronized` के सामान्य उपयोग के कारण हर मॉनिटर को `ReentrantLock` से बदलने की ज़रूरत नहीं है। लेकिन **कैरियर छोड़ना और मॉनिटर का लॉक छोड़ना अलग क्रियाएँ हैं**। `synchronized` के भीतर धीमा I/O अब भी दूसरे कामों को वही लॉक लेने से रोकता है। इसलिए लॉक वाले हिस्से की अवधि और लॉक के लिए प्रतिस्पर्धा महत्त्वपूर्ण हैं।

## एक ही कोड को JFR से जाँचें

![मोड की जाँच करके JFR शुरू करें। वर्चुअल थ्रेड में मॉनिटर के भीतर या बाहर समान अवधि की प्रतीक्षा करें और सिर्फ़ उसी वर्कर की पिनिंग घटनाएँ गिनें।](/assets/diagrams/technical/hi-2026-10-31-virtual-threads-jdk21-jdk25.svg)

`monitor` मोड में कोड `synchronized` के भीतर `Thread.sleep(100)` चलाता है। `plain` मोड में वही प्रतीक्षा ब्लॉक के बाहर होती है। कोई वास्तविक नेटवर्क या डेटाबेस अनुरोध नहीं भेजा जाता। [Recording](https://docs.oracle.com/en/java/javase/21/docs/api/jdk.jfr/jdk/jfr/Recording.html) से इवेंट की न्यूनतम अवधि शून्य रखी जाती है। फिर [RecordingFile](https://docs.oracle.com/en/java/javase/21/docs/api/jdk.jfr/jdk/jfr/consumer/RecordingFile.html) से सिर्फ़ वर्कर थ्रेड की घटनाएँ गिनी जाती हैं।

हर JDK के लिए फ़ाइल नई डायरेक्टरी में रखें और उसी इंस्टॉलेशन के `javac` और `java` चलाएँ। JFR सहित HotSpot JDK चाहिए। प्रीव्यू फ़्लैग की ज़रूरत नहीं है। प्रोग्राम `monitor.jfr` और `plain.jfr` बनाता है। लक्षित फ़ाइल पहले से मौजूद हो तो वह चलने से इनकार करता है।

### `VirtualThreadProbe.java`

```java
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.concurrent.Executors;
import jdk.jfr.Recording;
import jdk.jfr.consumer.RecordingFile;

public class VirtualThreadProbe {
    public static void main(String[] args) throws Exception {
        if (args.length != 1 || !(args[0].equals("monitor") || args[0].equals("plain"))) {
            throw new IllegalArgumentException("Usage: VirtualThreadProbe monitor|plain");
        }
        String mode = args[0];
        Path destination = Path.of(mode + ".jfr");
        if (Files.exists(destination)) {
            throw new IllegalStateException("Use a new directory: recording already exists");
        }
        Object monitor = new Object();
        long workerId;
        try (var recording = new Recording()) {
            recording.enable("jdk.VirtualThreadPinned").withThreshold(Duration.ZERO);
            recording.start();
            try (var tasks = Executors.newVirtualThreadPerTaskExecutor()) {
                workerId = tasks.submit(() -> {
                    Thread current = Thread.currentThread();
                    System.out.println("virtual=" + current.isVirtual());
                    if (mode.equals("monitor")) {
                        synchronized (monitor) { Thread.sleep(100); }
                    } else {
                        Thread.sleep(100);
                    }
                    return current.threadId();
                }).get();
            }
            recording.stop();
            recording.dump(destination);
        }
        long pinnedEvents = 0;
        try (var events = new RecordingFile(destination)) {
            while (events.hasMoreEvents()) {
                var event = events.readEvent();
                if (event.getEventType().getName().equals("jdk.VirtualThreadPinned")
                        && event.getThread() != null
                        && event.getThread().getJavaThreadId() == workerId) {
                    pinnedEvents++;
                }
            }
        }
        System.out.println(mode + "-pinned-events=" + pinnedEvents);
    }
}
```

```sh
javac --release 21 VirtualThreadProbe.java
java VirtualThreadProbe monitor
java VirtualThreadProbe plain
```

macOS AArch64 पर Eclipse Temurin `21.0.13+9` में यह आउटपुट मिला।

```text
virtual=true
monitor-pinned-events=1
virtual=true
plain-pinned-events=0
```

उसी प्लेटफ़ॉर्म पर Eclipse Temurin `25.0.5+8` ने यह आउटपुट दिया।

```text
virtual=true
monitor-pinned-events=0
virtual=true
plain-pinned-events=0
```

`Future.get()` काम पूरा होने तक प्रतीक्षा करता है और विफलता कॉलर तक पहुँचाता है। पढ़ने से पहले रिकॉर्डिंग रोककर फ़ाइल में लिखी जाती है, इसलिए गिनती के दौरान नई घटनाएँ दर्ज नहीं होतीं। कैरियर की संख्या पर सीमा नहीं लगाई गई और कुल समय की तुलना नहीं की गई। ये गिनतियाँ इसी एक काम की हैं। दूसरे JVM, पैच या इंस्ट्रूमेंटेशन में जाँच के बिना यही संख्या न मानें।

## अपग्रेड के बाद क्या जाँचना बाकी है?

JDK 25 में शून्य घटनाएँ विशेष रूप से **इस उदाहरण में मॉनिटर के भीतर की प्रतीक्षा** के लिए मिलीं। नेटिव या फ़ॉरेन फ़ंक्शन कॉल और क्लास आरंभीकरण से जुड़े शेष रास्ते यहाँ नहीं जाँचे गए। JDK 21 में उपयोगी `-Djdk.tracePinnedThreads=full` का JDK 25 में असर नहीं होता। उस संस्करण के JFR इवेंट और थ्रेड डंप देखें।

शुरुआत ऐसे कार्यभार से करें जिसमें अधिकतर समय I/O की प्रतीक्षा में बीतता है। डेटाबेस पूल, एक साथ चलने वाली बाहरी कॉल, टाइमआउट और रद्दीकरण साथ जाँचें। CPU-प्रधान काम, लॉक के भीतर लंबे ऑपरेशन और बड़े प्रति-थ्रेड कैश अब भी बाधाएँ हो सकते हैं। प्रतिनिधि प्रोडक्शन लोड पर थ्रूपुट, टेल लेटेंसी, मेमोरी और लॉक की प्रतिस्पर्धा मापें। इस छोटे प्रयोग से गति बढ़ने का अनुपात न निकालें। वर्चुअल थ्रेड के साथ अनुरोध का संदर्भ रखने के लिए ScopedValue वाले लेख में बाइंडिंग और असिंक्रोनस काम की सीमाएँ देखें।
