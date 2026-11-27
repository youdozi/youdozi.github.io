---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2026-10-30-jdk-emudhra-truststore",
  "routeSlug": "2026-10-30-jdk-emudhra-truststore",
  "kind": "post",
  "title": "JDK में eMudhra प्रमाणपत्रों की जाँच कैसे करें? चलती JVM और उसका ट्रस्ट स्टोर",
  "description": "Oracle, Temurin और Ubuntu की eMudhra संबंधी सलाह में अंतर समझें। JSSE का ट्रस्ट स्टोर और प्रमाणपत्रों के फ़िंगरप्रिंट जाँचें। अकेले संस्करण या उपनाम से सुरक्षा का निर्णय न लें।",
  "categories": [
    "security",
    "jdk"
  ],
  "tags": [
    "java",
    "jdk",
    "emudhra",
    "tls",
    "security"
  ],
  "sourcePath": "src/content/posts/en/2026-10-30-jdk-emudhra-truststore.md",
  "sourceSha256": "abdc8cf489bcb34919f036e665475c6dd2f939c07f1a4c42ffe10c86e32761e3",
  "draftSha256": "ddc4fd8197666b3ee25b212fcb4fe60a5a1aedf892681a5bbceadd65c39b6ecb",
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
JDK में eMudhra की समस्या दूर करने के लिए **एप्लिकेशन चलाने वाले JDK और उसके वास्तविक ट्रस्ट स्टोर दोनों की जाँच करें**। [Oracle की सूचना](https://ops.java/emudhra/) और [Temurin की सूचना](https://adoptium.net/news/2026/10/temurin-october-2026-emudhra/) अपडेट किए गए वितरणों और संबंधित प्रमाणन प्राधिकरणों (CA) पर भरोसा हटाने का विवरण देती हैं। दोनों में इसे लागू करने का तरीका अलग है। ब्राउज़र में सुरक्षा लागू होने या होस्ट JDK अपडेट होने से यह सिद्ध नहीं होता कि बदलाव कंटेनरों या दूसरी JVM तक भी पहुँचा है।

## क्या समयसीमा पार कर चुका सर्वर प्रमाणपत्र आयात करने से समस्या हल होगी?

यह सामान्य सर्वर प्रमाणपत्र की अवधि समाप्त होने से अलग घटना है। eMudhra के मध्यवर्ती CA की कुंजियों से समझौता होने के कारण ऐसी प्रमाणपत्र शृंखलाएँ संभव हुईं जिनसे जाली प्रमाणपत्र भी विश्वसनीय ठहर सकते थे। संबंधित भरोसा हटाना या वितरक का सुझाया बचाव लागू करना ज़रूरी है। [Oracle की CVE-2026-91403 सुरक्षा सूचना](https://www.oracle.com/security-alerts/alert-cve-2026-91403.html) में प्रभावित उत्पाद और पैच की जानकारी है। Oracle के उत्पादों और संस्करणों की तालिका सीधे दूसरे वितरण पर लागू न करें।

`PKIX path building failed` अकेले इस घटना की पहचान नहीं करता। अधूरी सर्वर शृंखला, गलत ट्रस्ट स्टोर, निजी CA और वितरक के भरोसे में बदलाव को अलग-अलग जाँचें। त्रुटि दबाने के लिए सत्यापन बंद करना या बिना जाँचा CA आयात करना सुरक्षा कमज़ोर कर सकता है।

## हर वितरक की सूचना अलग पढ़ें

यह जानकारी 2026-10-30 को जाँची गई सूचनाओं पर आधारित है। डिप्लॉय करते समय उत्पाद, OS, पूरा बिल्ड और बाद की सूचनाएँ फिर जाँचें।

| वितरक | क्या जाँचें |
| --- | --- |
| [Oracle JDK](https://ops.java/emudhra/) | संबंधित रूट हटाने वाले अपडेट। अपडेट में देरी हो तो अलग अंतरिम बचाव। |
| [Eclipse Temurin](https://adoptium.net/news/2026/10/temurin-october-2026-emudhra/) | Mozilla का CA डेटा इस्तेमाल करता है। `emSign ECC Root CA - G3` और `AAA Certificate Services` पर भरोसा हटाया गया। सुधार वाले बिल्डों में 21.0.13+9 और 17.0.21+9 शामिल हैं। |
| [Ubuntu OpenJDK](https://ubuntu.com/blog/emudhra-ca-compromise-fixes-available) | सिस्टम CA स्टोर से जुड़ा है। सूचना के समय मौजूद सिंक्रोनाइज़ेशन दोष के कारण `ca-certificates` अपडेट करने के बाद Java स्टोर में अलग से मैनुअल कदम ज़रूरी है। |

Temurin की सूचना के अनुसार अकेले `emSign Root CA - G1` का मौजूद होना सुधार की विफलता साबित नहीं करता। सामान्य `CheckCerts` रूट सूची को हर वितरण में पास होने की शर्त मानने से गलत निष्कर्ष निकल सकता है। रूट उपनाम, नाम और गिनती अकेले सुरक्षा का प्रमाण नहीं हैं।

## मौजूदा JVM में JSSE के डिफ़ॉल्ट भरोसे की जानकारी पढ़ें

![JVM की पहचान पढ़ें, JSSE का डिफ़ॉल्ट TrustManager आरंभ करें और नाम से मिले संभावित प्रमाणपत्रों के SHA-256 फ़िंगरप्रिंट इकट्ठे करें](/assets/diagrams/technical/hi-2026-10-30-jdk-emudhra-truststore.svg)

चित्र नीचे के केवल पढ़ने वाले प्रोग्राम का क्रम दिखाता है। यह डिफ़ॉल्ट `TrustManagerFactory` आरंभ करता है और CA के नाम खोजता है। नाम मिलने पर फ़िंगरप्रिंट का वितरक की सूचना से मिलान शुरू कर सकते हैं। इससे अकेले असुरक्षित या सुरक्षित होने का फ़ैसला नहीं होता। डिफ़ॉल्ट ट्रस्ट मैनेजर आरंभ न हो सके तो प्रोग्राम अपवाद के साथ रुकता है।

JDK 17 या बाद का संस्करण लेकर यह फ़ाइल नई डायरेक्टरी में सेव करें। इसमें केवल सार्वजनिक [TrustManagerFactory](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/javax/net/ssl/TrustManagerFactory.html) और [X509TrustManager](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/javax/net/ssl/X509TrustManager.html) API हैं। यह फ़ाइलें नहीं बदलता, नेटवर्क अनुरोध नहीं भेजता, प्रमाणपत्र जोड़ता या हटाता नहीं और TLS सत्यापन को बायपास नहीं करता।

### `TrustInventory.java`

```java
import java.security.KeyStore;
import java.security.MessageDigest;
import java.security.cert.X509Certificate;
import java.util.HexFormat;
import java.util.Locale;
import javax.net.ssl.TrustManager;
import javax.net.ssl.TrustManagerFactory;
import javax.net.ssl.X509TrustManager;

public class TrustInventory {
    public static void main(String[] args) throws Exception {
        System.out.println("java.version=" + System.getProperty("java.version"));
        System.out.println("java.vendor=" + System.getProperty("java.vendor"));
        System.out.println("java.home=" + System.getProperty("java.home"));
        System.out.println("configuredTrustStore=" +
            System.getProperty("javax.net.ssl.trustStore", "<default JSSE lookup>"));
        TrustManagerFactory factory = TrustManagerFactory.getInstance(
            TrustManagerFactory.getDefaultAlgorithm());
        factory.init((KeyStore) null);
        System.out.println("trustManagerProvider=" + factory.getProvider().getName());
        MessageDigest sha256 = MessageDigest.getInstance("SHA-256");
        int issuers = 0;
        int matches = 0;
        for (TrustManager manager : factory.getTrustManagers()) {
            if (!(manager instanceof X509TrustManager x509)) continue;
            for (X509Certificate cert : x509.getAcceptedIssuers()) {
                issuers++;
                String subject = cert.getSubjectX500Principal().getName();
                String lower = subject.toLowerCase(Locale.ROOT);
                if (lower.contains("emsign") || lower.contains("aaa certificate services")) {
                    String fingerprint = HexFormat.of().withUpperCase()
                        .formatHex(sha256.digest(cert.getEncoded()));
                    System.out.println("candidate=" + subject + "\tSHA256=" + fingerprint);
                    matches++;
                }
            }
        }
        System.out.println("acceptedIssuers=" + issuers);
        System.out.println("nameMatches=" + matches);
        System.out.println("assessment=inventory-only; no validation verdict");
    }
}
```

```sh
javac --release 17 TrustInventory.java
java TrustInventory
```

स्थानीय JDK पर प्रोग्राम कम्पाइल करके डिफ़ॉल्ट सूची का आउटपुट जाँचा गया। अलग बनाए गए परीक्षण CA स्टोर से नाम के मिलान और SHA-256 फ़िंगरप्रिंट, असंबंधित नामों वाले स्टोर तथा खाली स्टोर भी जाँचे गए। ये परीक्षण CA वास्तविक eMudhra प्रमाणपत्र नहीं हैं। प्रोग्राम चल जाने से प्रोडक्शन JVM की सुरक्षा प्रमाणित नहीं होती।

आउटपुट में `java.home` **अभी शुरू की गई JVM** का है। `configuredTrustStore` में `<default JSSE lookup>` का अर्थ है कि सिस्टम प्रॉपर्टी नहीं दी गई थी। इसका अर्थ यह नहीं है कि कोई स्टोर नहीं मिला। आउटपुट में ट्रस्ट स्टोर के पासवर्ड शामिल नहीं हैं।

## डिफ़ॉल्ट खोज और एप्लिकेशन की सेटिंग अलग हो सकती हैं

[SunJSSE संदर्भ](https://docs.oracle.com/en/java/javase/25/security/java-secure-socket-extension-jsse-reference-guide.html) स्पष्ट रूप से दिए गए `javax.net.ssl.trustStore` और डिफ़ॉल्ट `jssecacerts`/`cacerts` खोज में अंतर बताता है। यह प्रोग्राम नई JVM में डिफ़ॉल्ट आरंभीकरण का रास्ता पढ़ता है। यह एप्लिकेशन के बनाए `SSLContext`/`TrustManager`, फ़्रेमवर्क सेटिंग या नेटिव TLS लाइब्रेरी अपने आप नहीं खोजता।

एक भी संभावित प्रमाणपत्र न मिलना सुरक्षा का प्रमाण नहीं है। प्रदाता और बिल्ड के अनुसार स्टोर का पथ मौजूद न हो तो दूसरा स्टोर इस्तेमाल हो सकता है, खाली सूची मिल सकती है या आरंभीकरण विफल हो सकता है। स्थानीय JDK की जाँच में डिफ़ॉल्ट स्टोर का इस्तेमाल और पासवर्ड न मिलने पर विफलता देखी गई। दूसरे नाम या सत्यापन पथ भी छूट सकते हैं। इसी तरह सूची में नाम होने से यह तय नहीं होता कि TLS सत्यापन उसकी शृंखला स्वीकार करेगा। कोड अवरोध सूची, निरस्तीकरण या प्रमाणपत्र पथ की जाँच नहीं चलाता।

## अपडेट के बाद सामान्य कनेक्शन और प्रभावित शृंखला की अस्वीकृति दोनों जाँचें

1. वास्तविक सेवा का JDK वितरक, पूरा बिल्ड, निष्पादन योग्य फ़ाइल, JVM स्टार्टअप विकल्प और इमेज डाइजेस्ट पहचानें। कस्टम ट्रस्ट स्टोर और एप्लिकेशन की TLS सेटिंग भी शामिल करें।
2. वितरक का सुधार वाला बिल्ड डिप्लॉय करें। अलग स्टोर रखते हैं तो उसकी सामग्री का वितरक की सलाह से मिलान करें। कुछ भी हाथ से हटाने से पहले बैकअप, फ़िंगरप्रिंट और कनेक्शन पर असर जाँचें। Ubuntu की सूचना में बताए सिंक्रोनाइज़ेशन दोष के कारण `ca-certificates` अपडेट करने के बाद [Java रूट CA स्टोर अपडेट करने की प्रक्रिया](https://ubuntu.com/blog/emudhra-ca-compromise-fixes-available#updating-the-java-root-ca-store) भी पूरी करें। दोबारा स्टोर बनाने से पहले स्थानीय रूप से जोड़े गए CA सँभालकर रखें और उन्हें फिर जोड़ने की तैयारी करें।
3. हर JVM और प्रतिकृति को बदलें या रीस्टार्ट करें। एक इंस्टॉलेशन का `cacerts` बदलने से दूसरा JDK या पहले से चल रही प्रक्रिया अपने आप अपडेट नहीं होती।
4. सामान्य HTTPS कनेक्शन की सफलता और वितरक द्वारा बताई प्रभावित शृंखलाओं की अस्वीकृति दोनों जाँचें। हस्ताक्षरित JAR का सत्यापन अलग करें। TLS का नतीजा उसकी जगह नहीं लेता।

इस लेख में बाहरी परीक्षण होस्ट से कनेक्शन या वास्तव में प्रभावित शृंखलाओं की अस्वीकृति नहीं जाँची गई। केवल सूची के आउटपुट के आधार पर इन्हें पूरा दर्ज न करें। प्रोडक्शन में प्रमाणपत्र बदलने की योजना के साथ [वितरक की सत्यापन संबंधी सलाह](https://adoptium.net/news/2026/10/temurin-october-2026-emudhra/) का पालन करें।

GitLab के रेगुलर एक्सप्रेशन से जुड़ी RCE समस्या इस प्रमाणपत्र घटना से अलग है। GitLab अपग्रेड के लिए [CVE-2026-110264 संबंधी मार्गदर्शिका](/en/posts/2026-10-30-gitlab2shell-cve-2026-110264/) देखें।
