---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2026-11-22-spring-boot-4-2-otel-http-metrics",
  "routeSlug": "2026-11-22-spring-boot-4-2-otel-http-metrics",
  "kind": "post",
  "title": "Spring Boot 4.2 में OpenTelemetry के नियम अपनाने पर HTTP मेट्रिक कैसे बदलते हैं?",
  "description": "Spring Boot 4.2.0 में ऑब्ज़र्वेशन के नियम बदलकर Spring MVC और RestClient के Prometheus मेट्रिक की तुलना करें और 404 की क्वेरी अपडेट करें।",
  "categories": [
    "springboot"
  ],
  "tags": [
    "spring-boot",
    "opentelemetry",
    "prometheus",
    "micrometer",
    "restclient"
  ],
  "sourcePath": "src/content/posts/en/2026-11-22-spring-boot-4-2-otel-http-metrics.md",
  "sourceSha256": "184d3ca3476cfc05571ad97d60ef35f2d4c93f54cb152df388401376edc0ef57",
  "draftSha256": "f310e96337fc69d464fead3c92f459ec260ccd62058a24c97d77b4fe004cbac9",
  "manifestPath": ".pipeline/technical-translations/batch-1331/manifest.json",
  "manifestSha256": "cbb15c23f9cce0e6fa84da2ba740e6952316329456337b2eb96a443f481847e7",
  "publishedAt": "2026-11-27T08:24:31.688Z",
  "updatedAt": "2026-11-27T08:24:31.688Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 209,
    "approvedAt": "2026-11-27T08:24:31.688Z",
    "basis": "User authorized publication of the five named Hindi technical editions in item 133."
  }
}
---

**Spring Boot 4.2.0 में OpenTelemetry के ऑब्ज़र्वेशन नियम चालू करने पर Spring MVC सर्वर के Prometheus मेट्रिक का नाम `http_server_requests_seconds_count` से बदलकर `http_server_request_duration_seconds_count` हो जाता है।** 404 खोजने का लेबल भी `status` से बदलकर `http_response_status_code` हो जाता है। इसी ऐप में अपस्ट्रीम API को भेजी गई `RestClient` कॉल के मेट्रिक का नाम और लेबल पहले जैसे रहे। डैशबोर्ड और अलर्ट अपडेट करते समय आने और जाने वाले अनुरोधों के मेट्रिक अलग-अलग जाँचें। [Spring Boot 4.2 रिलीज़ नोट्स](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.2-Release-Notes#semantic-conventions)

## दोनों कॉन्फ़िगरेशन में वही दो अनुरोध चलाएँ

[पिछले लेख का उत्पाद खोजने वाला उदाहरण](/en/posts/2026-11-22-spring-boot-4-2-restclient-migration/) लें। ऐप को `GET /products/{id}` मिलने पर वह `RestClient` से अपस्ट्रीम API पर `GET /items/{id}` कॉल करता है। इस अभ्यास में ID `42` के लिए `200` और उत्पाद का नाम `Keyboard` मिलता है। ID `99` के लिए खाली बॉडी के साथ `404` मिलता है।

![ऐप दोनों नियमों के साथ अलग-अलग चलता है। हर बार उत्पाद 42 और 99 माँगे जाते हैं और Spring MVC सर्वर व RestClient मेट्रिक की तुलना के लिए Prometheus का आउटपुट सहेजा जाता है।](/assets/diagrams/technical/hi-2026-11-22-spring-boot-4-2-otel-http-metrics.svg)

चित्र दोनों रन दिखाता है। हर बार वही अनुरोध भेजें और तुलना के लिए Prometheus का आउटपुट अलग फ़ाइल में रखें।

Spring Boot 4.2.0 और JDK 21 इस्तेमाल करें। पिछले लेख से `pom.xml` और `src/main/java/example/CatalogApplication.java` कॉपी करें। इस अभ्यास में `spring-boot-starter-webmvc-test` की ज़रूरत नहीं है। इसे हटाकर Maven की निर्भरता सूची में नीचे की दो प्रविष्टियाँ जोड़ें। `CatalogApplication.java` में Boot से कॉन्फ़िगर किया गया `RestClient.Builder` पहले से इंजेक्ट होता है। [Spring Boot में HTTP क्लाइंट मेट्रिक](https://docs.spring.io/spring-boot/reference/actuator/metrics.html#actuator.metrics.supported.http-clients)

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>
```

ऐप को चलाने योग्य JAR में पैक करने के लिए `pom.xml` में `<project>` के अंदर यह कॉन्फ़िगरेशन जोड़ें।

```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-maven-plugin</artifactId>
        </plugin>
    </plugins>
</build>
```

एक टर्मिनल में अपस्ट्रीम API की जगह स्थानीय सर्वर चलाएँ। यह `/items/42` की फ़ाइल भेजता है। `/items/99` की फ़ाइल मौजूद न होने पर 404 लौटाता है। स्थानीय डेवलपमेंट परिवेश में दोनों पोर्ट खाली होने चाहिए।

```sh
upstream_dir=$(mktemp -d)
mkdir -p "$upstream_dir/items"
printf '%s' Keyboard > "$upstream_dir/items/42"
python3 -m http.server 18081 --bind 127.0.0.1 --directory "$upstream_dir"
```

दूसरे टर्मिनल में Maven प्रोजेक्ट की मूल डायरेक्टरी से ऐप बिल्ड करें और डिफ़ॉल्ट नियमों के साथ चलाएँ। जिस Actuator एंडपॉइंट से मेट्रिक पढ़ने हैं, उसे उपलब्ध कराएँ और ऐप को लूपबैक पते पर बाँधें।

```sh
mvn package

java -jar target/restclient-migration-1.0.0.jar \
  --server.address=127.0.0.1 \
  --server.port=18080 \
  --catalog.base-url=http://127.0.0.1:18081 \
  --management.endpoints.web.exposure.include=health,prometheus
```

ऐप शुरू होने पर तीसरे टर्मिनल से ये अनुरोध भेजें। दोनों जवाब जाँचें और फिर Prometheus का आउटपुट सहेजें। इसमें अब तक आए अनुरोधों की संख्या वाली `_count` सीरीज़ है।

```sh
curl -sS -i http://127.0.0.1:18080/products/42
curl -sS -i http://127.0.0.1:18080/products/99
curl -fsS http://127.0.0.1:18080/actuator/prometheus > default.prom
```

ऐप रोकें और उसी `java -jar` कमांड में `--management.observations.conventions=open-telemetry` जोड़कर फिर चलाएँ। तीनों अनुरोध दोहराएँ और आखिरी जवाब `open-telemetry.prom` में सहेजें। नई प्रोसेस शुरू करने पर पहले रन के काउंटर रीसेट हो जाते हैं।

```sh
grep -E '^http_(server|client).*_count\{.*(/products/|/items/)' \
  default.prom open-telemetry.prom
```

## दर्ज मेट्रिक में क्या बदला?

मैंने JDK 21.0.1, Maven 3.9.11, Spring Boot 4.2.0 और एम्बेडेड Tomcat पर दोनों कॉन्फ़िगरेशन चलाए। हर बार एक अनुरोध पर `200` और दूसरे पर `404` मिला। चारों जवाबों के स्टेटस और बॉडी अपेक्षा के अनुसार थे।

| MVC सर्वर मेट्रिक | डिफ़ॉल्ट नियम | OpenTelemetry नियम |
| --- | --- | --- |
| Prometheus अनुरोध गणना | `http_server_requests_seconds_count` | `http_server_request_duration_seconds_count` |
| HTTP मेथड का लेबल | `method` | `http_request_method` |
| जवाब के स्टेटस का लेबल | `status` | `http_response_status_code` |
| रूट का लेबल | `uri` | `http_route` |
| इस उदाहरण में रूट का मान | `/products/{id}` | `/products/{id}` |

रूट लेबल में `{id}` वाला रूट टेम्पलेट आता है। नीचे दर्ज की गई 404 सीरीज़ से सिर्फ़ क्वेरी में इस्तेमाल हुए लेबल दिखाए गए हैं। हर रन में सर्वर पर 404 की गिनती `1` थी।

```text
http_server_requests_seconds_count{status="404",uri="/products/{id}"} 1
http_server_request_duration_seconds_count{http_response_status_code="404",http_route="/products/{id}"} 1
```

इन्हीं आउटपुट में दोनों कॉन्फ़िगरेशन ने बाहर जाने वाले अनुरोध `http_client_requests_seconds_count` में दर्ज किए। लेबल `method="GET"`, `uri="/items/{id}"` और `status="200"` या `status="404"` थे। यह नतीजा उदाहरण में इस्तेमाल हुए Boot ऑटो-कॉन्फ़िगरेशन और `RestClient.Builder` के संयोजन के लिए है। अभ्यास में मेट्रिक Micrometer की Prometheus रजिस्ट्री से पढ़े जाते हैं। ऑब्ज़र्वेशन के नियम और डेटा एक्सपोर्ट की विधि अलग-अलग सेटिंग हैं। [Spring Boot ऑब्ज़र्वेबिलिटी गाइड](https://docs.spring.io/spring-boot/reference/actuator/observability.html#actuator.observability.semantic-conventions)

## 404 की क्वेरी बदलें

डिफ़ॉल्ट नियमों वाले Grafana पैनल में इस रूट पर अब तक आए 404 जवाबों की संख्या ऐसे निकाल सकते हैं।

```text
sum(http_server_requests_seconds_count{uri="/products/{id}",status="404"})
```

OpenTelemetry नियमों के साथ मेट्रिक का नाम और दोनों लेबल बदलें।

```text
sum(http_server_request_duration_seconds_count{http_route="/products/{id}",http_response_status_code="404"})
```

मैंने Prometheus 3.5.0 के `promtool` से दर्ज सीरीज़ पर क्वेरी जाँचीं। हर क्वेरी ने अपने नियमों के साथ `1` लौटाया और दूसरे नियमों के साथ परिणाम खाली रहा।

ये क्वेरी एक ऐप के संचयी काउंटर की तुलना करती हैं। अगर प्रोडक्शन पैनल हाल की समयावधि में प्रति सेकंड अनुरोध दिखाता है, तो उसकी मौजूदा गणना, जैसे `rate(...[5m])`, बनाए रखें और उसके अंदर मेट्रिक सिलेक्टर बदलें। जब तक Prometheus पुराने और नए दोनों संस्करणों से डेटा पढ़ रहा है, डिप्लॉयमेंट टारगेट के हिसाब से क्वेरी करके देखें कि कौन-सा टारगेट किस नाम से मेट्रिक भेजता है। [Prometheus क्वेरी की बुनियाद](https://prometheus.io/docs/prometheus/latest/querying/basics/) · [Prometheus में `rate()`](https://prometheus.io/docs/prometheus/latest/querying/functions/#rate)

अगर सर्वर मेट्रिक का नाम `management.observations.http.server.requests.name` से तय किया है, तो पहले उस नाम वाले पैनल और अलर्ट जाँचें। OpenTelemetry नियमों में इस सेटिंग का असर नहीं होता। मेट्रिक से किसी एक अनुरोध के लॉग और ट्रेस तक पहुँचने के लिए [Grafana LGTM में लॉग और ट्रेस जोड़ना](/en/posts/2026-11-02-grafana-lgtm-log-trace/) देखें। [Spring Boot 4.2 रिलीज़ नोट्स](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.2-Release-Notes#semantic-conventions)
