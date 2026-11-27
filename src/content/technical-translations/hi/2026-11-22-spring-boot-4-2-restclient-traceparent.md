---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2026-11-22-spring-boot-4-2-restclient-traceparent",
  "routeSlug": "2026-11-22-spring-boot-4-2-restclient-traceparent",
  "kind": "post",
  "title": "Spring Boot 4.2 में जाँचें कि RestClient से traceparent आगे जाता है या नहीं",
  "description": "Spring Boot 4.2.0 में RestClient बनाने के दो तरीकों की तुलना करें। देखें कि इनसे traceparent हेडर और Tempo में स्पैन का संबंध कैसे बदलता है।",
  "categories": [
    "springboot"
  ],
  "tags": [
    "spring-boot",
    "restclient",
    "opentelemetry",
    "micrometer",
    "tempo",
    "distributed-tracing"
  ],
  "sourcePath": "src/content/posts/en/2026-11-22-spring-boot-4-2-restclient-traceparent.md",
  "sourceSha256": "79632a97012abbc73db2e3e1a0bbe924c261ceb52f4603146310d3e2c4f897f5",
  "draftSha256": "b9477ddd10009f195d90d0aa94c2f378d94bd9fdc1f9260faaf6516cc9f9f908",
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

**उत्पाद की खोज और उससे जुड़ी इन्वेंटरी कॉल को एक ही ट्रेस में देखने के लिए Spring Boot से इंजेक्ट किया गया `RestClient.Builder` इस्तेमाल करें।** इस उदाहरण में `RestClient.create()` से बना क्लाइंट भी वही उत्पाद खोजकर HTTP 200 लौटाता है। लेकिन इन्वेंटरी API को `traceparent` हेडर नहीं मिलता और वह अलग ट्रेस शुरू करता है। HTTP जवाब और Tempo में सहेजे गए स्पैन की तुलना करके पता लगाएँ कि ट्रेस का संदर्भ कहाँ आगे जाना बंद हुआ। [Spring Boot में ट्रेस का प्रसार](https://docs.spring.io/spring-boot/4.2/reference/actuator/tracing.html#actuator.micrometer-tracing.propagating-traces)

यह अभ्यास [RestClient माइग्रेशन वाले लेख](/en/posts/2026-11-22-spring-boot-4-2-restclient-migration/) की उत्पाद खोज पर आधारित है। [HTTP मेट्रिक वाला लेख](/en/posts/2026-11-22-spring-boot-4-2-otel-http-metrics/) अनुरोधों की गिनती करता है। यहाँ हम एक अनुरोध का रास्ता देखेंगे।

## उत्पाद और स्टॉक की खोज को जोड़ने वाला हेडर

`traceparent` ट्रेस का संदर्भ आगे भेजने के लिए W3C का मानक HTTP हेडर है। इस अभ्यास में इसका प्रारूप `00-<trace-id>-<parent-id>-<trace-flags>` है। `trace-id` पूरे ट्रेस की पहचान है। `parent-id` भेजने वाले के HTTP क्लाइंट स्पैन की पहचान है। इससे प्राप्तकर्ता सेवा उस स्पैन को अपने सर्वर स्पैन का पैरेंट बना सकती है। [W3C Trace Context विनिर्देश](https://www.w3.org/TR/trace-context/#traceparent-header)

![उत्पाद ऐप इन्वेंटरी API को कॉल करता है। Boot बिल्डर traceparent भेजकर दोनों ऐप को एक ट्रेस में जोड़ता है। सीधे बना क्लाइंट हेडर नहीं भेजता और इन्वेंटरी API अलग ट्रेस शुरू करता है।](/assets/diagrams/technical/hi-2026-11-22-spring-boot-4-2-restclient-traceparent.svg)

चित्र उत्पाद 42 के लिए दोनों क्लाइंट के रास्ते दिखाता है। दोनों में स्टॉक का एक ही मान मिलता है। इस उदाहरण में `traceparent` हेडर तय करता है कि इन्वेंटरी सर्वर का स्पैन उत्पाद के ट्रेस में जुड़ेगा या नहीं।

## एक ही JAR से दो ऐप चलाएँ

JDK 21, Maven, Docker, `curl` और `jq` चाहिए। अभ्यास स्थानीय पोर्ट `13200`, `14318`, `18180` और `18181` इस्तेमाल करता है। खाली डायरेक्टरी में नीचे की फ़ाइलें बनाएँ। वही JAR दो बार चलाएँ, एक बार सेवा का नाम `product` और दूसरी बार `inventory` रखकर। जाँच के लिए उदाहरण जवाब में मौजूदा ट्रेस ID और प्राप्त हेडर देता है।

### `pom.xml`

```xml
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>4.2.0</version>
    </parent>
    <groupId>example</groupId>
    <artifactId>trace-propagation</artifactId>
    <version>1.0.0</version>
    <properties>
        <java.version>21</java.version>
    </properties>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-webmvc</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-restclient</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-opentelemetry</artifactId>
        </dependency>
    </dependencies>
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
```

### `src/main/java/example/TraceApplication.java`

```java
package example;

import io.micrometer.tracing.Tracer;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestClient;

@SpringBootApplication
public class TraceApplication {
    public static void main(String[] args) {
        SpringApplication.run(TraceApplication.class, args);
    }
}

@RestController
class ProductController {
    private final RestClient bootClient;
    private final RestClient directClient;
    private final Tracer tracer;

    ProductController(RestClient.Builder builder, Tracer tracer,
            @Value("${inventory.base-url}") String inventoryUrl) {
        this.bootClient = builder.baseUrl(inventoryUrl).build();
        this.directClient = RestClient.create(inventoryUrl);
        this.tracer = tracer;
    }

    @GetMapping("/products/{id}")
    ProductReply product(@PathVariable("id") long id,
            @RequestParam("instrumented") boolean instrumented) {
        RestClient client = instrumented ? bootClient : directClient;
        InventoryReply inventory = client.get().uri("/items/{id}", id)
            .retrieve().body(InventoryReply.class);
        return new ProductReply(tracer.currentSpan().context().traceId(), inventory);
    }
}

@RestController
class InventoryController {
    private final Tracer tracer;

    InventoryController(Tracer tracer) {
        this.tracer = tracer;
    }

    @GetMapping("/items/{id}")
    InventoryReply item(@PathVariable("id") long id,
            @RequestHeader(name = "traceparent", required = false) String traceparent) {
        return new InventoryReply(id, 7, traceparent, tracer.currentSpan().context().traceId());
    }
}

record ProductReply(String productTraceId, InventoryReply inventory) {}
record InventoryReply(long id, int stock, String traceparent, String inventoryTraceId) {}
```

### `src/main/resources/application.properties`

```properties
server.address=127.0.0.1
inventory.base-url=http://127.0.0.1:18181
management.tracing.sampling.probability=1.0
management.opentelemetry.tracing.export.otlp.endpoint=http://127.0.0.1:14318/v1/traces
management.otlp.metrics.export.enabled=false
```

सैंपलिंग की प्रायिकता `1.0` रखने से अभ्यास के सभी अनुरोध दर्ज होते हैं। ऐप OTLP पर सिर्फ़ ट्रेस एक्सपोर्ट करते हैं। पहले HTTP जवाब में हेडर देखें। इससे हेडर आगे पहुँचने की समस्या और Tempo में स्पैन गायब होने की समस्या को अलग जाँच सकते हैं। [Spring Boot सैंपलिंग गाइड](https://docs.spring.io/spring-boot/4.2/reference/actuator/tracing.html#actuator.micrometer-tracing.sampling)

### `tempo.yaml`

इस कॉन्फ़िगरेशन में Tempo, OTLP HTTP पर स्पैन लेकर स्थानीय स्टोरेज में लिखता है। क्वेरी API और रिसीवर के पोर्ट सिर्फ़ होस्ट के लूपबैक पते पर उपलब्ध हैं।

```yaml
server:
  http_listen_port: 3200

distributor:
  receivers:
    otlp:
      protocols:
        http:
          endpoint: 0.0.0.0:4318

storage:
  trace:
    backend: local
    wal:
      path: /tmp/tempo/wal
    local:
      path: /tmp/tempo/blocks
```

प्रोजेक्ट की मूल डायरेक्टरी से Tempo और ऐप चलाएँ। पहले टर्मिनल में Tempo शुरू करें।

```sh
docker run --rm --name traceparent-tempo \
  -p 127.0.0.1:13200:3200 -p 127.0.0.1:14318:4318 \
  --mount "type=bind,source=$PWD/tempo.yaml,target=/etc/tempo.yaml,readonly" \
  grafana/tempo:2.9.0 -config.file=/etc/tempo.yaml
```

एक अलग टर्मिनल में देखें कि `curl -fsS http://127.0.0.1:13200/ready` सफल होता है। फिर Maven से बिल्ड करें। दोनों `java` कमांड अलग-अलग टर्मिनल में चलाएँ।

```sh
mvn package

java -jar target/trace-propagation-1.0.0.jar \
  --spring.application.name=inventory --server.port=18181

java -jar target/trace-propagation-1.0.0.jar \
  --spring.application.name=product --server.port=18180
```

## जवाबों के हेडर और ट्रेस ID की तुलना करें

दोनों ऐप चलने लगें तो वही उत्पाद दो बार खोजें। क्लाइंट चुनने के लिए सिर्फ़ `instrumented` बदलें।

```sh
curl -fsS 'http://127.0.0.1:18180/products/42?instrumented=true' -o boot.json
curl -fsS 'http://127.0.0.1:18180/products/42?instrumented=false' -o direct.json

jq '{id: .inventory.id, stock: .inventory.stock,
     headerReceived: (.inventory.traceparent != null),
     sameTrace: (.productTraceId == .inventory.inventoryTraceId)}' boot.json direct.json
jq -r .inventory.traceparent boot.json
```

दोनों अनुरोधों ने HTTP 200 लौटाया। Boot बिल्डर के साथ दोनों ऐप का ट्रेस ID एक था और इन्वेंटरी API को मिले `traceparent` हेडर में भी वही ID था। सीधे बनाए गए क्लाइंट के साथ इन्वेंटरी API ने `traceparent` का मान `null` बताया और दोनों ऐप के ट्रेस ID अलग थे।

| क्लाइंट कैसे बना | उत्पाद ID और स्टॉक | हेडर मिला? | दोनों ऐप के ट्रेस ID |
| --- | --- | --- | --- |
| Boot से इंजेक्ट किया गया `RestClient.Builder` | 42 और 7 | हाँ | एक जैसे |
| `RestClient.create()` | 42 और 7 | नहीं | अलग |

## Tempo में स्पैन जाँचें

जवाबों से मिले ट्रेस ID लेकर Tempo में क्वेरी करें। स्पैन एक्सपोर्ट होने में कुछ सेकंड लग सकते हैं। ट्रेस न मिले तो थोड़ी देर बाद फिर क्वेरी करें। [ID से ट्रेस खोजने के लिए Grafana Tempo API](https://grafana.com/docs/tempo/latest/api_docs/#query)

```sh
show_spans() {
  curl -fsS "http://127.0.0.1:13200/api/traces/$1" | jq -r '
    (.batches // .resourceSpans)[] as $batch
    | ($batch.resource.attributes[]
       | select(.key == "service.name").value.stringValue) as $service
    | $batch.scopeSpans[].spans[]
    | [$service, .kind, .name, .spanId, (.parentSpanId // "-")] | @tsv'
}

show_spans "$(jq -r .productTraceId boot.json)"
show_spans "$(jq -r .productTraceId direct.json)"
show_spans "$(jq -r .inventory.inventoryTraceId direct.json)"
```

उदाहरण Spring Boot 4.2.0, JDK 21.0.1, Maven 3.9.11 और Tempo 2.9.0 पर चला। दो अनुरोधों से मिले तीन ट्रेस ID के लिए Tempo API ने ये स्पैन लौटाए।

| किस ट्रेस ID की क्वेरी की | Tempo में मिले स्पैन |
| --- | --- |
| Boot बिल्डर वाला अनुरोध | उत्पाद सर्वर → उत्पाद HTTP क्लाइंट → इन्वेंटरी सर्वर |
| सीधे बने क्लाइंट वाला अनुरोध, उत्पाद ऐप | उत्पाद सर्वर का एक रूट स्पैन |
| सीधे बने क्लाइंट वाला अनुरोध, इन्वेंटरी ऐप | इन्वेंटरी सर्वर का एक रूट स्पैन |

Boot बिल्डर वाले रास्ते में Tempo में इन्वेंटरी सर्वर का `parentSpanId` उत्पाद HTTP क्लाइंट के `spanId` से मिला। इस रन में Tempo API ने स्पैन ID को Base64 में लौटाया, जबकि `traceparent` हेक्साडेसिमल इस्तेमाल करता है। क्लाइंट स्पैन ID को Base64 से डीकोड करके बाइट को हेक्साडेसिमल में लिखने पर हेडर के `parent-id` के बराबर मान मिला।

अगर अनुरोध सफल होते हैं लेकिन सेवा की सीमा पर ट्रेस रुक जाता है, तो देखें कि प्राप्तकर्ता को `traceparent` मिलता है या नहीं। हेडर गायब हो तो जाँचें कि कॉल करने वाला Boot का कॉन्फ़िगर किया हुआ बिल्डर इस्तेमाल कर रहा है। ट्रेस ID पहुँचता है लेकिन Tempo में स्पैन गायब हैं तो सैंपलिंग और OTLP एक्सपोर्ट सेटिंग जाँचें। फिर उसी ट्रेस ID से लॉग खोजने के लिए [Grafana LGTM में लॉग और ट्रेस जोड़ना](/en/posts/2026-11-02-grafana-lgtm-log-trace/) देखें।
