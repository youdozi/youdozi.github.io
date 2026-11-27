---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2026-10-30-webclient-timeout-retry",
  "routeSlug": "2026-10-30-webclient-timeout-retry",
  "kind": "post",
  "title": "Reactor से WebClient के टाइमआउट और सीमित पुनः प्रयासों की जाँच",
  "description": "कनेक्शन, प्रतिक्रिया, हर प्रयास और पूरे अनुरोध की समय-सीमाएँ अलग रखें। स्थानीय HTTP और Reactor की आभासी घड़ी से जाँचें कि GET में केवल HTTP 503 पर दो बार पुनः प्रयास होता है।",
  "categories": [
    "springboot"
  ],
  "tags": [
    "springboot",
    "webclient",
    "test",
    "reactor"
  ],
  "sourcePath": "src/content/posts/en/2026-10-30-webclient-timeout-retry.md",
  "sourceSha256": "757c2335d2f6b40391fa299791d6c6e6bade0e499c599b451be06be4eee77e3b",
  "draftSha256": "58f67a418c35aaa8192b906ad7276b07ea45b47a237f20377798ce8db2e0c5d7",
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
हर प्रयास का `timeout`, `retryWhen` से पहले रखें और कुल `timeout` उसके बाद, ताकि दो प्रयासों के बीच का इंतज़ार भी कुल समय में गिना जाए। API का अनुबंध जिन विफलताओं पर दोबारा अनुरोध की अनुमति देता है, सिर्फ़ उन्हीं पर पुनः प्रयास करें। इस GET उदाहरण में HTTP 503 पर अधिकतम दो पुनः प्रयास होते हैं। टाइमआउट या दूसरी त्रुटि पर अनुरोध वहीं रुक जाता है। Spring के दस्तावेज़ में [ट्रांसपोर्ट के टाइमआउट](https://docs.spring.io/spring-framework/reference/6.2/web/webflux-webclient/client-builder.html) और Reactor के [पब्लिशर के टाइमआउट](https://projectreactor.io/docs/core/3.7.12/api/reactor/core/publisher/Mono.html) अलग समझाए गए हैं।

## कौन सी सेटिंग किस समय को सीमित करती है?

| सेटिंग | इस उदाहरण में दायरा |
| --- | --- |
| `CONNECT_TIMEOUT_MILLIS` | TCP कनेक्शन स्थापित करने का समय। DNS, पूल से कनेक्शन मिलने या TLS का पूरा समय इसमें शामिल नहीं है। |
| `responseTimeout` | प्रतिक्रिया प्राप्त करते समय नेटवर्क से लगातार दो बार पढ़ने के बीच अधिकतम अंतराल। पूरे बॉडी के लिए समय-सीमा नहीं है। |
| पहला `timeout(attemptLimit)` | एक सब्सक्रिप्शन से बॉडी डिकोड होने तक। हर पुनः प्रयास पर घड़ी फिर शुरू होती है। |
| अंतिम `timeout(totalLimit)` | पूरा सब्सक्रिप्शन, जिसमें सभी प्रयास और उनके बीच का इंतज़ार शामिल है। |
| `StepVerifier.verify(GUARD)` | टेस्ट रनर अधिकतम कितनी देर इंतज़ार करेगा। इससे क्लाइंट की सेटिंग नहीं बदलती। |

Reactor Netty के [responseTimeout संदर्भ](https://projectreactor.io/docs/netty/1.2.11/api/reactor/netty/http/client/HttpClient.html) में पढ़ने के बीच का अंतराल बताया गया है। यदि लगातार डेटा मिलता रहे, तो पूरी प्रतिक्रिया में इससे अधिक समय लग सकता है। बाहरी पब्लिशर का टाइमआउट पूरे काम की अलग समय-सीमा तय करता है। रद्द करने से यह सब्सक्रिप्शन रुकता है। दूर की सेवा जो काम पहले ही कर चुकी है, वह वापस नहीं होता।

## दूसरी विफलताएँ जोड़ने से पहले पुनः प्रयासों की सीमा तय करें

![हर प्रयास की समय-सीमा लगाएँ, केवल पात्र 503 पर दोबारा प्रयास करें और पूरी प्रक्रिया का समय सीमित रखें](/assets/diagrams/technical/hi-2026-10-30-webclient-timeout-retry.svg)

चित्र ऑपरेटरों का क्रम दिखाता है। इसमें हर HTTP घटना नहीं दिखाई गई है। हर प्रयास सफल होता है या त्रुटि देता है। केवल 503 मिलने और पुनः प्रयास शेष होने पर कुछ देर बाद नया सब्सक्रिप्शन शुरू होता है। दूसरी त्रुटियों पर प्रक्रिया तुरंत रुकती है। बाहरी टाइमआउट जारी प्रयास और अगले प्रयास की प्रतीक्षा दोनों को रद्द कर सकता है।

[`Retry.fixedDelay(2, delay)`](https://projectreactor.io/docs/core/release/api/reactor/util/retry/Retry.html) शुरुआती प्रयास के बाद दो पुनः प्रयास की अनुमति देता है। यानी एक सब्सक्रिप्शन में एप्लिकेशन अधिकतम तीन प्रयास करता है। `.onRetryExhaustedThrow` सीमा पूरी होने पर अंतिम 503 अपवाद आगे भेजता है, इसलिए कॉलर को उसकी जगह पुनः प्रयास समाप्त होने वाला रैपर नहीं मिलता। `.disableRetry(true)` TCP कनेक्शन अचानक टूटने पर Reactor Netty का अलग स्वचालित पुनः प्रयास बंद करता है। इस तरह गिनती में ट्रांसपोर्ट का कोई छिपा प्रयास नहीं जुड़ता।

उदाहरण GET करता है और जानबूझकर केवल 503 पर दोबारा प्रयास करता है। टाइमआउट से यह साबित नहीं होता कि सर्वर ने कुछ नहीं किया। स्पष्ट इडेम्पोटेंसी अनुबंध के बिना इस नीति को भुगतान या दूसरी लिखने वाली क्रियाओं पर लागू न करें। यह `Retry-After` नहीं पढ़ती, 429 पर पुनः प्रयास नहीं करती, एक्सपोनेंशियल बैकऑफ़ या जिटर नहीं लगाती और अलग-अलग कॉलरों के प्रयासों में तालमेल नहीं बिठाती। छोटी निश्चित देरी से परीक्षण जल्दी पूरा होता है। प्रोडक्शन की सीमाएँ और बैकऑफ़ अपने API अनुबंध और उपलब्ध क्षमता के अनुसार चुनें।

## अलग प्रोजेक्ट बनाएँ

नई खाली डायरेक्टरी, JDK 17 और Gradle 8.4 लें। [प्रतिक्रिया अनुबंध के परीक्षणों](/en/posts/2023-09-19-springboot-test-webclient/) से मिलान के लिए उदाहरण Boot BOM 3.5.7 और MockWebServer 4.12.0 इस्तेमाल करता है। ये संस्करण परिणाम दोहराने के लिए हैं। प्रोडक्शन के लिए मौजूदा संस्करण की सिफ़ारिश इनसे न निकालें। पहली बार निर्भरताएँ Maven Central से आती हैं। HTTP परीक्षण सिर्फ़ लूपबैक पर चलते हैं। साथ में चलता हुआ Boot एप्लिकेशन या Gradle रैपर नहीं दिया गया है।

### `settings.gradle`

```groovy
rootProject.name = 'webclient-timeout-retry'
```

### `build.gradle`

```groovy
plugins { id 'java' }
repositories { mavenCentral() }
dependencies {
    implementation platform('org.springframework.boot:spring-boot-dependencies:3.5.7')
    implementation 'org.springframework.boot:spring-boot-starter-webflux'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testImplementation 'io.projectreactor:reactor-test'
    testImplementation 'com.squareup.okhttp3:mockwebserver:4.12.0'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
test { useJUnitPlatform() }
```

## दोनों समय-सीमाएँ अलग जगह लगाएँ

नीचे का कोड सेव करें। कॉलर कंस्ट्रक्टर को धनात्मक अवधियाँ देता है। परीक्षण में इनके मान स्पष्ट हैं। प्रतिक्रिया का टाइमआउट और TCP कनेक्शन का 1,000 ms का टाइमआउट ट्रांसपोर्ट फ़ैक्टरी में लगते हैं।

### `src/main/java/RetryClient.java`

```java
import java.time.Duration;
import io.netty.channel.ChannelOption;
import org.springframework.http.client.reactive.ReactorClientHttpConnector;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;
import reactor.core.publisher.Mono;
import reactor.netty.http.client.HttpClient;
import reactor.util.retry.Retry;

public class RetryClient {
    private final WebClient client;
    private final Duration attemptLimit;
    private final Duration totalLimit;
    private final Duration retryDelay;

    public RetryClient(WebClient client, Duration attemptLimit,
                       Duration totalLimit, Duration retryDelay) {
        this.client = client;
        this.attemptLimit = attemptLimit;
        this.totalLimit = totalLimit;
        this.retryDelay = retryDelay;
    }

    public static WebClient transport(String baseUrl, Duration responseLimit) {
        HttpClient http = HttpClient.create()
            .disableRetry(true)
            .option(ChannelOption.CONNECT_TIMEOUT_MILLIS, 1000)
            .responseTimeout(responseLimit);
        return WebClient.builder().baseUrl(baseUrl)
            .clientConnector(new ReactorClientHttpConnector(http)).build();
    }

    public Mono<String> get() {
        return Mono.defer(() -> client.get().uri("/value")
                .retrieve().bodyToMono(String.class))
            .timeout(attemptLimit)
            .retryWhen(Retry.fixedDelay(2, retryDelay)
                .filter(error -> error instanceof WebClientResponseException response
                    && response.getStatusCode().value() == 503)
                .onRetryExhaustedThrow((spec, signal) -> signal.failure()))
            .timeout(totalLimit);
    }
}
```

## नीति की नौ शर्तें जाँचें

सात परीक्षण असली WebClient और स्थानीय MockWebServer का उपयोग करते हैं। दो परीक्षण कृत्रिम एक्सचेंज और Reactor की आभासी घड़ी से ऑपरेटरों का समय जाँचते हैं ताकि नतीजा नेटवर्क शेड्यूलिंग पर निर्भर न हो। आभासी समय Reactor Netty के वास्तविक सॉकेट टाइमआउट नहीं जाँचता। ट्रांसपोर्ट वाला परीक्षण अपवाद में लिपटे रीड टाइमआउट को जाँचता है। पब्लिशर टाइमआउट से `TimeoutException` मिलता है।

### `src/test/java/RetryClientTest.java`

```java
import java.io.IOException;
import java.time.Duration;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.atomic.AtomicInteger;
import io.netty.handler.timeout.ReadTimeoutException;
import okhttp3.mockwebserver.MockResponse;
import okhttp3.mockwebserver.MockWebServer;
import okhttp3.mockwebserver.SocketPolicy;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpStatus;
import org.springframework.web.reactive.function.client.ClientResponse;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientRequestException;
import org.springframework.web.reactive.function.client.WebClientResponseException;
import reactor.core.publisher.Mono;
import reactor.netty.http.client.HttpClient;
import reactor.test.StepVerifier;
import static org.junit.jupiter.api.Assertions.*;

class RetryClientTest {
    private MockWebServer server;
    private WebClient client;
    private static final Duration GUARD = Duration.ofSeconds(10);

    @BeforeAll
    static void warmUp() {
        HttpClient.create().warmup().block(GUARD);
    }

    @BeforeEach
    void start() throws IOException {
        server = new MockWebServer();
        server.start();
        client = RetryClient.transport(server.url("/").toString(), Duration.ofSeconds(5));
    }

    @AfterEach
    void stop() throws IOException {
        server.shutdown();
    }

    RetryClient policy() {
        return new RetryClient(client, Duration.ofSeconds(3),
            Duration.ofSeconds(8), Duration.ofMillis(10));
    }

    void expectStatus(int status) {
        StepVerifier.create(policy().get())
            .expectErrorSatisfies(error -> assertEquals(status,
                assertInstanceOf(WebClientResponseException.class, error).getStatusCode().value()))
            .verify(GUARD);
    }

    @Test
    void successUsesOneRequest() {
        server.enqueue(new MockResponse().setBody("ok"));
        StepVerifier.create(policy().get()).expectNext("ok").expectComplete().verify(GUARD);
        assertEquals(1, server.getRequestCount());
    }

    @Test
    void two503ResponsesThenSuccessUseThreeRequests() {
        server.enqueue(new MockResponse().setResponseCode(503));
        server.enqueue(new MockResponse().setResponseCode(503));
        server.enqueue(new MockResponse().setBody("ok"));
        StepVerifier.create(policy().get()).expectNext("ok").expectComplete().verify(GUARD);
        assertEquals(3, server.getRequestCount());
    }

    @Test
    void exhausted503PreservesLastStatusAfterThreeRequests() {
        for (int i = 0; i < 3; i++) server.enqueue(new MockResponse().setResponseCode(503));
        expectStatus(503);
        assertEquals(3, server.getRequestCount());
    }

    @Test
    void notFoundIsNotRetried() {
        server.enqueue(new MockResponse().setResponseCode(404));
        expectStatus(404);
        assertEquals(1, server.getRequestCount());
    }

    @Test
    void otherServerErrorsAreNotRetried() {
        server.enqueue(new MockResponse().setResponseCode(500));
        expectStatus(500);
        assertEquals(1, server.getRequestCount());
    }

    @Test
    void attemptTimeoutIsNotRetried() {
        server.enqueue(new MockResponse().setSocketPolicy(SocketPolicy.NO_RESPONSE));
        RetryClient limited = new RetryClient(client, Duration.ofSeconds(1),
            Duration.ofSeconds(8), Duration.ofMillis(10));
        StepVerifier.create(limited.get()).expectError(TimeoutException.class).verify(GUARD);
        assertEquals(1, server.getRequestCount());
    }

    @Test
    void responseReadTimeoutIsNotRetried() {
        server.enqueue(new MockResponse().setSocketPolicy(SocketPolicy.NO_RESPONSE));
        WebClient shortRead = RetryClient.transport(server.url("/").toString(), Duration.ofMillis(250));
        RetryClient limited = new RetryClient(shortRead, Duration.ofSeconds(3),
            Duration.ofSeconds(8), Duration.ofMillis(10));
        StepVerifier.create(limited.get()).expectErrorSatisfies(error -> {
            assertInstanceOf(WebClientRequestException.class, error);
            assertInstanceOf(ReadTimeoutException.class, error.getCause());
        }).verify(GUARD);
        assertEquals(1, server.getRequestCount());
    }

    @Test
    void totalBudgetIncludesRetryDelay() {
        AtomicInteger attempts = new AtomicInteger();
        StepVerifier.withVirtualTime(() -> {
            WebClient synthetic = WebClient.builder().exchangeFunction(request -> Mono.defer(() -> {
                attempts.incrementAndGet();
                return Mono.just(ClientResponse.create(HttpStatus.SERVICE_UNAVAILABLE).build());
            })).build();
            return new RetryClient(synthetic, Duration.ofSeconds(1),
                Duration.ofMillis(1500), Duration.ofSeconds(1)).get();
        }).thenAwait(Duration.ofMillis(1500)).expectError(TimeoutException.class).verify(GUARD);
        assertEquals(2, attempts.get());
    }

    @Test
    void attemptBudgetRestartsAfterRetry() {
        AtomicInteger attempts = new AtomicInteger();
        StepVerifier.withVirtualTime(() -> {
            WebClient synthetic = WebClient.builder().exchangeFunction(request -> Mono.defer(() -> {
                int attempt = attempts.incrementAndGet();
                return Mono.delay(Duration.ofMillis(400)).map(tick -> attempt == 1
                    ? ClientResponse.create(HttpStatus.SERVICE_UNAVAILABLE).build()
                    : ClientResponse.create(HttpStatus.OK).body("ok").build());
            })).build();
            return new RetryClient(synthetic, Duration.ofMillis(500),
                Duration.ofSeconds(2), Duration.ofMillis(200)).get();
        }).thenAwait(Duration.ofSeconds(1)).expectNext("ok").expectComplete().verify(GUARD);
        assertEquals(2, attempts.get());
    }
}
```

## प्रोजेक्ट चलाएँ और परिणाम पढ़ें

```sh
gradle --no-daemon clean test
```

स्थानीय परीक्षण JDK 17.0.8.1 और Gradle 8.4 पर चला। सभी नौ परीक्षण पास हुए। जाँची गई शर्तों के लिए `build/reports/tests/test/index.html` या `build/test-results/test/TEST-RetryClientTest.xml` देखें। सिर्फ़ `BUILD SUCCESSFUL` से परीक्षणों की संख्या नहीं पता चलती।

| स्थिति | जाँचा गया परिणाम |
| --- | --- |
| तुरंत सफलता | एक HTTP अनुरोध, `ok` और फिर समापन |
| 503 → 503 → सफलता | तीन HTTP अनुरोध, `ok` और फिर समापन |
| हर प्रयास पर 503 | तीन HTTP अनुरोध, अंतिम 503 बरकरार |
| 404 / 500 | दोनों में एक-एक HTTP अनुरोध, मूल स्टेटस बरकरार |
| कोई प्रतिक्रिया नहीं, प्रयास की सीमा एक सेकंड | `TimeoutException`, एक HTTP अनुरोध |
| कोई प्रतिक्रिया नहीं, पढ़ने की सीमा 250 ms | `WebClientRequestException` के भीतर `ReadTimeoutException`, एक अनुरोध |
| कुल 1.5 s, पुनः प्रयास की देरी एक सेकंड | दो कृत्रिम प्रयास। तीसरे से पहले ही टाइमआउट प्रतीक्षा रद्द करता है। |
| 400 ms का प्रयास, 200 ms की देरी, 400 ms का प्रयास | हर प्रयास 500 ms में पूरा होता है। आभासी समय 1 s आगे बढ़ाकर सफलता और समापन जाँचे गए। |

इन जाँचों में TCP कनेक्शन स्थापित करने का टाइमआउट, DNS विफलता, TLS नेगोशिएशन, पूल का भरना, रीडायरेक्ट या अलग-अलग सेवाओं में होने वाले प्रभाव नहीं दोहराए गए। कनेक्शन की सीमा सेट की गई है पर उसका प्रयोग नहीं किया गया। OS की शेड्यूलिंग से वास्तविक अवधि बदल सकती है। परीक्षण त्रुटि के प्रकार और अनुरोधों की गिनती जाँचते हैं, घड़ी पर सटीक मिलीसेकंड नहीं। स्टेटस, मीडिया टाइप और JSON संभालने के लिए [WebClient प्रतिक्रिया अनुबंध का उदाहरण](/en/posts/2023-09-19-springboot-test-webclient/) देखें।
