---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2026-11-22-spring-boot-4-2-restclient-migration",
  "routeSlug": "2026-11-22-spring-boot-4-2-restclient-migration",
  "kind": "post",
  "title": "Spring Boot 4.2 में RestTemplate और TestRestTemplate से माइग्रेशन",
  "description": "Spring Boot 4.2 में RestTemplate की कॉल RestClient पर और TestRestTemplate के टेस्ट RestTestClient पर ले जाएँ। चालू सर्वर पर 200 और 404 दोनों जवाब जाँचें।",
  "categories": [
    "springboot"
  ],
  "tags": [
    "spring-boot",
    "resttemplate",
    "testresttemplate",
    "restclient",
    "resttestclient",
    "http-client"
  ],
  "sourcePath": "src/content/posts/en/2026-11-22-spring-boot-4-2-restclient-migration.md",
  "sourceSha256": "8859ad29e5643a2fc5112004d1582dceddbd10ea1ccfdc3bd1bfb21aacff6b33",
  "draftSha256": "11d17ea0f9cf8de51b2926b902fb85f19d84e35a9cbdd4d1c1843e874d79155b",
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

**बाहरी API को कॉल करने के लिए `RestClient` और अपने ऐप को अनुरोध भेजकर उसके जवाब जाँचने के लिए `RestTestClient` इस्तेमाल करें।** Spring Boot 4.2 में `RestTemplate` के ऑटो-कॉन्फ़िगरेशन और बिल्डर के साथ-साथ `TestRestTemplate` का समर्थन भी डेप्रिकेट किया गया है। माइग्रेशन में सफलता और त्रुटि, दोनों की जाँच बनाए रखें। अगर पुराना टेस्ट HTTP 404 जाँचता था, तो नए टेस्ट में भी वही स्टेटस जाँचें। [Spring Boot 4.2 रिलीज़ नोट्स](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.2-Release-Notes#deprecation-of-testresttemplate-support)

## पुराने API की जगह क्या इस्तेमाल करें?

| मौजूदा कोड | नया API | क्या जाँचें |
| --- | --- | --- |
| `RestTemplateBuilder` और `getForObject()` | `RestClient.Builder` और `get().uri().retrieve().body()` | बेस URL, अनुरोध हेडर और 4xx व 5xx जवाबों का व्यवहार |
| `RestTemplateCustomizer` | `RestClientCustomizer` | इंटरसेप्टर, टाइमआउट और अनुरोध फ़ैक्टरी |
| `@AutoConfigureTestRestTemplate` और `TestRestTemplate` | `@AutoConfigureRestTestClient` और `RestTestClient` | असली सर्वर कैसे शुरू होता है, स्टेटस कोड और जवाब की बॉडी |

डिफ़ॉल्ट `RestTemplate` की तरह `RestClient.retrieve()` भी 4xx और 5xx जवाब मिलने पर अपवाद उठाता है। `TestRestTemplate` जवाब लौटाता है ताकि टेस्ट उसका स्टेटस देख सके। `RestTestClient` में यही जाँच रखने के लिए `exchange()` के बाद `expectStatus()` लगाएँ। अगर पुराने क्लाइंट में अपना एरर हैंडलर था, तो वही स्टेटस नियम `defaultStatusHandler()` या हर अनुरोध के `onStatus()` में लिखें। [Spring Framework के REST क्लाइंट](https://docs.spring.io/spring-framework/reference/integration/rest-clients.html) · [TestRestTemplate API](https://docs.spring.io/spring-boot/api/java/org/springframework/boot/resttestclient/TestRestTemplate.html)

## उत्पाद खोजने वाले API की दोनों HTTP सीमाएँ जाँचें

![RestTestClient उत्पाद ID को Spring MVC ऐप को भेजता है। ऐप RestClient से अपस्ट्रीम API को कॉल करता है। अपस्ट्रीम से 200 मिलने पर ऐप 200 और उत्पाद का नाम लौटाता है। 404 पर क्लाइंट अपवाद उठाता है, जिसे ऐप 404 जवाब में बदलता है।](/assets/diagrams/technical/hi-2026-11-22-spring-boot-4-2-restclient-migration.svg)

उत्पाद ID `42` के लिए अपस्ट्रीम API नाम `Keyboard` लौटाता है। बाकी सभी ID पर 404 मिलता है। चित्र में दो इंटीग्रेशन टेस्ट ऐप के ज़रिए अनुरोध भेजते हैं। टेस्ट अपस्ट्रीम API की जगह एक स्थानीय HTTP सर्वर चलाते हैं।

### `pom.xml`

उदाहरण Spring Boot 4.2.0 और JDK 21 पर चलता है। MVC टेस्ट स्टार्टर में `RestTestClient` का ऑटो-कॉन्फ़िगरेशन मॉड्यूल शामिल है।

```xml
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>4.2.0</version>
    </parent>
    <groupId>example</groupId>
    <artifactId>restclient-migration</artifactId>
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
            <artifactId>spring-boot-starter-webmvc-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>
```

### `src/main/java/example/CatalogApplication.java`

अगर पुरानी कॉल `restTemplate.getForObject("/items/{id}", String.class, id)` थी, तो नई कॉल में वही URI टेम्पलेट और जवाब का टाइप रखें। Boot से कॉन्फ़िगर किया हुआ बिल्डर इंजेक्ट करें और अपस्ट्रीम का बेस URL सेट करें। इस उदाहरण में उत्पाद न मिलने पर अपस्ट्रीम के 404 को कंट्रोलर ऐप के 404 जवाब में बदलता है।

```java
package example;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestClient;

@SpringBootApplication
public class CatalogApplication {
    public static void main(String[] args) {
        SpringApplication.run(CatalogApplication.class, args);
    }
}

@Service
class CatalogClient {
    private final RestClient http;

    CatalogClient(RestClient.Builder builder, @Value("${catalog.base-url}") String baseUrl) {
        this.http = builder.baseUrl(baseUrl).build();
    }

    String findName(long id) {
        return http.get()
            .uri("/items/{id}", id)
            .retrieve()
            .body(String.class);
    }
}

@RestController
class ProductController {
    private final CatalogClient catalog;

    ProductController(CatalogClient catalog) {
        this.catalog = catalog;
    }

    @GetMapping("/products/{id}")
    ResponseEntity<String> product(@PathVariable("id") long id) {
        try {
            return ResponseEntity.ok(catalog.findName(id));
        } catch (HttpClientErrorException.NotFound ex) {
            return ResponseEntity.notFound().build();
        }
    }
}
```

### `src/test/java/example/CatalogApplicationTests.java`

चलते हुए एम्बेडेड सर्वर को HTTP अनुरोध भेजने के लिए `RANDOM_PORT` बनाए रखें। Boot से इंजेक्ट किया गया `RestTestClient` सापेक्ष पथों को उस सर्वर के पते के आधार पर हल करता है। अगर पुराने टेस्ट में `getForEntity("/products/99", String.class).getStatusCode()` से 404 जाँचते थे, तो वही स्टेटस `exchange().expectStatus().isNotFound()` से जाँचें। [चलते सर्वर पर टेस्ट के लिए Spring Boot गाइड](https://docs.spring.io/spring-boot/reference/testing/spring-boot-applications.html#testing.spring-boot-applications.with-running-server)

```java
package example;

import java.io.IOException;
import java.io.UncheckedIOException;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;

import com.sun.net.httpserver.HttpServer;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.resttestclient.autoconfigure.AutoConfigureRestTestClient;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.web.servlet.client.RestTestClient;
import org.springframework.web.client.HttpClientErrorException;

import static org.assertj.core.api.Assertions.assertThatThrownBy;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureRestTestClient
class CatalogApplicationTests {
    private static final HttpServer upstream = startUpstream();

    @Autowired
    private RestTestClient app;

    @Autowired
    private CatalogClient catalog;

    @DynamicPropertySource
    static void configureUpstream(DynamicPropertyRegistry properties) {
        properties.add("catalog.base-url",
            () -> "http://127.0.0.1:" + upstream.getAddress().getPort());
    }

    @AfterAll
    static void stopUpstream() {
        upstream.stop(0);
    }

    @Test
    void returnsProductName() {
        app.get().uri("/products/42").exchange()
            .expectStatus().isOk()
            .expectBody(String.class).isEqualTo("Keyboard");
    }

    @Test
    void returnsNotFoundForMissingProduct() {
        app.get().uri("/products/99").exchange()
            .expectStatus().isNotFound()
            .expectBody().isEmpty();
    }

    @Test
    void turnsUpstream404IntoAnException() {
        assertThatThrownBy(() -> catalog.findName(99))
            .isInstanceOf(HttpClientErrorException.NotFound.class);
    }

    private static HttpServer startUpstream() {
        try {
            HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
            server.createContext("/items/", exchange -> {
                try (exchange) {
                    if (exchange.getRequestURI().getPath().equals("/items/42")) {
                        byte[] body = "Keyboard".getBytes(StandardCharsets.UTF_8);
                        exchange.getResponseHeaders().set("Content-Type", "text/plain; charset=UTF-8");
                        exchange.sendResponseHeaders(200, body.length);
                        exchange.getResponseBody().write(body);
                    } else {
                        exchange.sendResponseHeaders(404, -1);
                    }
                }
            });
            server.start();
            return server;
        } catch (IOException ex) {
            throw new UncheckedIOException(ex);
        }
    }
}
```

## टेस्ट चलाएँ

तीनों फ़ाइलें सहेजें और प्रोजेक्ट की मूल डायरेक्टरी से यह कमांड चलाएँ।

```sh
mvn test
```

यह रन JDK 21.0.1 और Maven 3.9.11 पर हुआ। एम्बेडेड Tomcat और अपस्ट्रीम API की जगह चलने वाले स्थानीय HTTP सर्वर ने अलग-अलग रैंडम पोर्ट लिए। तीनों टेस्ट पास हुए।

| टेस्ट की जाँच | दर्ज नतीजा |
| --- | --- |
| `GET /products/42` | `200 OK` और बॉडी में `Keyboard` |
| `GET /products/99` | `404 Not Found` और खाली बॉडी |
| `catalog.findName(99)` | `HttpClientErrorException.NotFound` अपवाद उठता है |

```text
Tests run: 3, Failures: 0, Errors: 0, Skipped: 0
BUILD SUCCESS
```

माइग्रेशन से पहले उन स्टेटस और बॉडी की सूची बनाएँ जिन्हें मौजूदा टेस्ट जाँचते हैं। उदाहरण के लिए, अपस्ट्रीम के 404 को खाली परिणाम में बदलने वाले क्लाइंट का व्यवहार और खुद 404 भेजने वाले कंट्रोलर का व्यवहार अलग अनुबंध हैं। हर सीमा पर अलग टेस्ट रखें ताकि पता चले कि व्यवहार कहाँ बदला। सिंक्रोनस और रिएक्टिव कॉल की तुलना के लिए [WebClient और RestClient](/en/posts/2026-10-31-webclient-restclient-comparison/) देखें।
