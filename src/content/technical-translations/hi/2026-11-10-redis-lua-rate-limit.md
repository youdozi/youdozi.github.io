---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2026-11-10-redis-lua-rate-limit",
  "routeSlug": "2026-11-10-redis-lua-rate-limit",
  "kind": "post",
  "title": "Redis से अनुरोध सीमित करें: Lua की परमाणु क्रिया और 429/503 जवाब",
  "description": "Spring MVC और Redis Lua में कई सर्वरों के लिए साझा अनुरोध सीमा लागू करें। चलाए गए उदाहरण से निश्चित विंडो की TTL, समवर्ती अनुरोध, Retry-After और Redis विफलता की नीति समझें।",
  "categories": [
    "springboot"
  ],
  "tags": [
    "redis",
    "rate-limit",
    "lua",
    "spring-mvc",
    "distributed-systems"
  ],
  "sourcePath": "src/content/posts/en/2026-11-10-redis-lua-rate-limit.md",
  "sourceSha256": "bffe243d3ec0d2693086eb4d708c74490b34a27af7c1735cf6a41c81eea561d5",
  "draftSha256": "12688bded88e5c31edea5e565853d0a198c94c9e7fe37095f054b6c0ba9d8472",
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

**अलग-अलग ऐप सर्वरों पर एक ही उपयोगकर्ता के अनुरोध सीमित करने के लिए अनुमति का फ़ैसला और काउंटर का अपडेट Redis में एक साथ करें।** यहाँ Lua में निश्चित विंडो लागू करेंगे। सीमा पार होने पर `429` और Redis से नतीजा तय न हो पाने पर `503` लौटाएँगे।

उदाहरण की नीति **प्रति खाते अधिकतम तीन अनुरोध स्वीकार करती है। पहली अनुमति से 10 सेकंड की अवधि शुरू होती है।** शुरुआत के लिए निश्चित विंडो सरल है। इसका व्यवहार टोकन बकेट या स्लाइडिंग विंडो से अलग है। परिवेश Spring Boot 3.5.16, JDK 21, Gradle 8.14.3 और Redis 8.2.1 है। ये संस्करण उदाहरण दोहराने के लिए तय किए गए हैं। इन्हें प्रोडक्शन के नवीनतम पैच की सिफ़ारिश न समझें।

## ऐप में GET पढ़कर INCR करना पर्याप्त क्यों नहीं है?

सर्वर A और B दोनों काउंटर का मान `2` पढ़ लें तो सीमा `3` होने पर भी दोनों अपने अनुरोध स्वीकार कर सकते हैं। JVM का `synchronized` दूसरे प्रोसेस को लॉक नहीं करता। `INCR` एक परमाणु क्रिया है लेकिन इससे पहले लिया गया अनुमति का निर्णय उस क्रिया का हिस्सा नहीं बनता।

`INCR` के बाद अलग से `EXPIRE` भेजने में एक और समस्या है। दोनों कमांड के बीच क्लाइंट रुक जाए तो कुंजी बिना TTL के रह सकती है। [Redis में INCR से अनुरोध सीमित करने का आधिकारिक उदाहरण](https://redis.io/docs/latest/commands/incr/) भी इस रेस और Lua के इस्तेमाल को समझाता है।

नीचे दी गई स्क्रिप्ट पहले अनुरोध पर `SET ... PX` से मान और TTL एक साथ बनाती है। बाद के अनुरोधों के लिए वह Lua के भीतर सीमा जाँचती है और सिर्फ़ स्वीकृत अनुरोधों पर काउंटर बढ़ाती है। अस्वीकृति से काउंटर या उसकी समाप्ति का समय नहीं बदलता।

## सीमा किस क्रम में लागू होती है?

![सर्वर सीमा की कुंजी चुनता है। Redis Lua काउंटर और TTL जाँचता है। अनुमति पर SET PX या INCR अनुरोध दर्ज करता है और ऐप 200 लौटाता है। सीमा पार होने पर स्थिति बदले बिना 429 और Retry-After मिलते हैं। कनेक्शन या स्थिति की त्रुटि पर 503 मिलता है।](/assets/diagrams/technical/hi-2026-11-10-redis-lua-rate-limit.svg)

नीला क्षेत्र Redis के अंदर होने वाला निर्णय दिखाता है। HTTP जवाब ऐप बनाता है। कुंजी न मिले तो नई विंडो शुरू होती है। मौजूदा कुंजी में धनात्मक पूर्णांक काउंटर और वैध TTL होने चाहिए। यहाँ अनुमति गिनी जाती है। अनुमति के बाद काम विफल हो तो गिनती वापस नहीं घटती।

## Spring MVC और Redis Lua में सीमा लागू करें

ये छह फ़ाइलें एक Gradle प्रोजेक्ट में रखें। उदाहरण में प्रमाणीकरण लागू नहीं है। `/demo` सभी अनुरोधों को एक ही `demo-account` का मानता है। यहाँ स्थिर कुंजी से प्रति-उपयोगकर्ता नीति का व्यवहार दोहरा सकते हैं। सर्वर केवल स्थानीय पते पर सुनता है।

वास्तविक सेवा में कुंजी किसी **सर्वर द्वारा सत्यापित पहचान** से बनाएँ, जैसे प्रमाणित `Principal`। हेडर में आए मनमाने `userId` पर भरोसा करने से कॉलर उसे बदलकर सीमा से बच सकता है। उदाहरण के लिए `rl:orders:v1:<tenant-and-subject-digest>` ऑपरेशन का दायरा, नीति का संस्करण और पहचान अलग करता है। सीधे निजी डेटा रखने के बजाय सर्वर के गुप्त मान से बना HMAC इस्तेमाल करने पर विचार करें। फ़ॉरवर्ड किए गए IP हेडर केवल विश्वसनीय प्रॉक्सी की सीमा में स्वीकार करें।

### `settings.gradle`

```groovy
rootProject.name = 'redis-lua-rate-limit'
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
    implementation 'org.springframework.boot:spring-boot-starter-data-redis'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
application { mainClass = 'example.RateLimitApplication' }
test {
    useJUnitPlatform()
    systemProperty 'demo.redis.port', providers.gradleProperty('redisPort').getOrElse('6379')
}
```

### `src/main/resources/application.yml`

```yaml
server:
  address: 127.0.0.1
spring:
  data:
    redis:
      host: 127.0.0.1
      port: ${REDIS_PORT:6379}
      connect-timeout: 200ms
      timeout: 200ms
```

### `src/main/resources/rate-limit.lua`

```lua
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
if not limit or limit < 1 or limit > 1000000 or limit ~= math.floor(limit)
   or not window or window < 1 or window > 3600000 or window ~= math.floor(window) then
    return redis.error_reply('invalid rate limit policy')
end

local raw = redis.call('GET', KEYS[1])
if raw then
    local count = tonumber(raw)
    local ttl = redis.call('PTTL', KEYS[1])
    if not count or count < 1 or count ~= math.floor(count) or ttl < 0 then
        return redis.error_reply('invalid counter state')
    end
    if count >= limit then
        return {0, 0, ttl}
    end
    local updated = redis.call('INCR', KEYS[1])
    return {1, limit - updated, ttl}
end

redis.call('SET', KEYS[1], 1, 'PX', window)
return {1, limit - 1, window}
```

### `src/main/java/example/RedisRateLimiter.java`

```java
package example;

import java.time.Duration;
import java.util.List;
import org.springframework.core.io.ClassPathResource;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.script.DefaultRedisScript;
import org.springframework.stereotype.Component;

@Component
public class RedisRateLimiter {
    private static final DefaultRedisScript<List> SCRIPT = new DefaultRedisScript<>();
    static {
        SCRIPT.setLocation(new ClassPathResource("rate-limit.lua"));
        SCRIPT.setResultType(List.class);
    }
    private final StringRedisTemplate redis;

    public RedisRateLimiter(StringRedisTemplate redis) {
        this.redis = redis;
    }

    public Decision check(String key, int limit, Duration window) {
        long milliseconds = window.toMillis();
        if (key == null || key.isBlank() || key.length() > 160 || limit < 1 || limit > 1_000_000
                || milliseconds < 1 || milliseconds > 3_600_000) {
            throw new IllegalArgumentException("Invalid rate limit policy");
        }
        List<?> result = redis.execute(SCRIPT, List.of(key),
                Integer.toString(limit), Long.toString(milliseconds));
        if (result == null || result.size() != 3) {
            throw new IllegalStateException("Invalid limiter result");
        }
        return new Decision(((Number) result.get(0)).longValue() == 1,
                ((Number) result.get(1)).longValue(), ((Number) result.get(2)).longValue());
    }

    public record Decision(boolean allowed, long remaining, long ttlMillis) {
        public long retryAfterSeconds() {
            return Math.max(1, (ttlMillis + 999) / 1000);
        }
    }
}
```

### `src/main/java/example/RateLimitApplication.java`

```java
package example;

import java.time.Duration;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.dao.DataAccessException;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
@RestController
public class RateLimitApplication {
    private final RedisRateLimiter limiter;

    public RateLimitApplication(RedisRateLimiter limiter) {
        this.limiter = limiter;
    }

    public static void main(String[] args) {
        SpringApplication.run(RateLimitApplication.class, args);
    }

    @GetMapping("/demo")
    public ResponseEntity<String> demo() {
        try {
            var decision = limiter.check("rl:demo:v1:demo-account", 3, Duration.ofSeconds(10));
            if (!decision.allowed()) {
                return ResponseEntity.status(429)
                        .header("Retry-After", Long.toString(decision.retryAfterSeconds()))
                        .body("rate limit exceeded\n");
            }
            return ResponseEntity.ok("ok\n");
        } catch (DataAccessException | IllegalStateException unavailable) {
            return ResponseEntity.status(503).body("limiter unavailable\n");
        }
    }
}
```

यह स्क्रिप्ट एक कुंजी इस्तेमाल करती है। Redis Cluster में यह उसी कुंजी वाले स्लॉट में चलती है। एक स्क्रिप्ट से कई कुंजियों पर सीमा लगाने के लिए उन्हें एक ही स्लॉट में रखने की बाध्यता ध्यान में रखकर डिज़ाइन बदलना होगा।

`StringRedisTemplate` की कुंजियाँ और आर्ग्युमेंट स्ट्रिंग होते हैं। स्क्रिप्ट से मिली संख्याओं की सरणी `List` के रूप में लौटती है। `DefaultRedisScript` को दोबारा इस्तेमाल करने का कारण और डिफ़ॉल्ट एक्ज़ीक्यूटर में `EVALSHA` के बाद कैश मिस पर `EVAL` का व्यवहार [Spring Data Redis के स्क्रिप्टिंग दस्तावेज़](https://docs.spring.io/spring-data/redis/reference/redis/scripting.html) में देखें।

## कौन से जवाब मिलने चाहिए?

चलाने के लिए Docker उपलब्ध हो और Redis का पोर्ट `16379` तथा ऐप का पोर्ट `8080` किसी दूसरे प्रोसेस के इस्तेमाल में न हों। Redis केवल होस्ट के लूपबैक पते पर उपलब्ध है। पर्सिस्टेंस और स्थायी वॉल्यूम बंद हैं। पहली बार Redis इमेज और Maven डिपेंडेंसी डाउनलोड करने के लिए नेटवर्क चाहिए।

```sh
docker run --rm -d --name redis-rate-limit-demo \
  -p 127.0.0.1:16379:6379 \
  redis:8.2.1-alpine@sha256:987c376c727652f99625c7d205a1cba3cb2c53b92b0b62aade2bd48ee1593232 \
  redis-server --save '' --appendonly no
REDIS_PORT=16379 gradle run
```

सर्वर तैयार होने पर दूसरे टर्मिनल से 10 सेकंड के अंदर चार कॉल करें।

```sh
for attempt in 1 2 3 4; do
  curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8080/demo
done
curl -i http://127.0.0.1:8080/demo
```

नई विंडो में लगातार चार अनुरोध भेजने पर ये स्टेटस कोड मिलने चाहिए।

```text
200
200
200
429
```

अस्वीकृति में `Retry-After` बची हुई TTL को अगले पूरे सेकंड तक ऊपर पूर्णांकित करके मिलता है। न्यूनतम मान एक सेकंड है। मान कॉल के समय पर निर्भर है। `429` और वैकल्पिक `Retry-After` का अर्थ [RFC 6585 की धारा 4](https://www.rfc-editor.org/rfc/rfc6585#section-4) के अनुसार है। प्रतीक्षा करने से अनुमति आरक्षित नहीं होती। इस बीच दूसरा अनुरोध कोटा इस्तेमाल कर ले तो पुनःप्रयास भी अस्वीकृत हो सकता है।

`gradle run` रोकें और परीक्षण कंटेनर हटाएँ।

```sh
docker stop redis-rate-limit-demo
```

## समवर्ती अनुरोधों और त्रुटियों के लिए क्या जाँचा गया?

अलग परीक्षणों में स्थानीय Docker में वास्तविक Redis और एम्बेडेड Tomcat इस्तेमाल हुए। इनसे व्यवहार जाँचा गया, थ्रूपुट नहीं मापा गया।

| स्थिति | देखा गया परिणाम |
| --- | --- |
| थ्रेड पूल से एक कुंजी पर 40 समवर्ती कॉल | 3 को अनुमति, Redis काउंटर 3 |
| एक ही Redis और कुंजी इस्तेमाल करने वाले दो लिमिटर ऑब्जेक्ट | सीमा साझा रही। दोनों ऑब्जेक्ट एक क्लाइंट बीन इस्तेमाल करते हैं। परीक्षण में दो अलग JVM नहीं चलाए गए। |
| तीन स्वीकृत कॉल के बाद अनुरोध | अस्वीकृति, काउंटर और TTL नहीं बढ़े |
| दूसरे खाते की कुंजी और समाप्त हो चुकी कुंजी | दूसरी कुंजी पर स्वतंत्र अनुमति। समाप्ति के बाद नई विंडो शुरू हुई |
| अमान्य मान या बिना TTL की कुंजी | मनमाने सुधार के बिना त्रुटि |
| लगातार वास्तविक HTTP कॉल | तीन बार 200, फिर 429 के साथ `Retry-After` |
| अमान्य काउंटर पर HTTP अनुरोध | 503 |
| अलग TCP एंडपॉइंट कनेक्शन लेता है लेकिन Redis जवाब नहीं देता | लिमिटर की त्रुटि पर 503 |

वैध काउंटर के साथ TTL होनी चाहिए। [PTTL दस्तावेज़](https://redis.io/docs/latest/commands/pttl/) के अनुसार `-1` का अर्थ TTL नहीं है और `-2` का अर्थ कुंजी मौजूद नहीं है। अमान्य स्थिति में चुपचाप TTL जोड़कर अनुरोध स्वीकार करने से नीति की त्रुटि छिप सकती है। इसीलिए यहाँ त्रुटि लौटती है।

**Lua की परमाणु क्रिया का अर्थ यह नहीं कि त्रुटि पर लिखे गए मान अपने आप वापस हो जाएँगे।** [आधिकारिक स्क्रिप्टिंग दस्तावेज़](https://redis.io/docs/latest/develop/programmability/eval-intro/) के अनुसार निष्पादन के अलगाव और त्रुटि प्रबंधन में अंतर रखें। जाँच में अलग स्क्रिप्ट ने `SET` चलाकर जानबूझकर त्रुटि लौटाई और लिखा हुआ मान बना रहा। इस लेख की स्क्रिप्ट लिखने से पहले इनपुट और मौजूदा स्थिति जाँचती है। अंत में केवल एक बार `SET` या `INCR` से लिखती है।

## प्रोडक्शन में कौन सी सीमा और विफलता नीति चुनें?

**निश्चित विंडो यह गारंटी नहीं देती कि किसी भी लगातार 10 सेकंड में अधिकतम तीन ही अनुरोध आएँगे।** एक विंडो खत्म होने से ठीक पहले बचा कोटा खर्च करके अगली की शुरुआत में फिर अनुरोध भेजने पर थोड़ी देर में कई अनुरोध आ सकते हैं। चलती अवधि में सटीक कुल संख्या चाहिए तो स्लाइडिंग लॉग या स्लाइडिंग विंडो पर विचार करें। औसत आगमन दर और बर्स्ट अलग तय करने के लिए टोकन बकेट देखें। यहाँ इन एल्गोरिदम को लागू करके प्रदर्शन नहीं मापा गया।

उदाहरण **fail-closed** नीति अपनाता है। Redis की त्रुटि होने पर अनुरोध आगे नहीं जाता। भुगतान जैसे कामों में सीमा टूटना महँगा पड़ सकता है, इसलिए यह उचित हो सकता है। लेकिन Redis की समस्या API की उपलब्धता भी घटाती है। रीड API जैसी जगह उपलब्धता अहम हो तो सीमित स्थानीय बकेट से अस्थायी अनुमति दे सकते हैं। सर्वर बढ़ने पर कुल कोटा बढ़ सकता है, इसलिए साझा सीमा की गारंटी बदल जाती है।

200ms की सेटिंग कनेक्शन और कमांड का टाइमआउट है। पूरे HTTP अनुरोध के 200ms में समाप्त होने की गारंटी नहीं है। कतार, पुनःकनेक्शन और शेड्यूलिंग का समय अलग देखें। कोड ऐप स्तर पर पुनःप्रयास नहीं जोड़ता। क्लाइंट की पुनःकनेक्शन और कमांड दोबारा भेजने की नीतियाँ भी जाँचें। Redis अनुमति दर्ज कर ले और जवाब खो जाए तो कॉलर को विफलता दिखने के बावजूद कोटा खर्च हो सकता है। दोहराया गया अनुरोध एक ही बार गिनना हो तो अनुरोध पहचानकर्ता और अलग इडेम्पोटेंसी नीति चाहिए।

मेमोरी दबाव में कुंजी हट जाए या रीस्टार्ट अथवा फ़ेलओवर में काउंटर खो जाए तो अगला अनुरोध नई विंडो शुरू करके स्वीकार हो सकता है। सिर्फ़ परमाणु Lua से प्रतिकृति और रिकवरी तक साझा सीमा की गारंटी नहीं मिलती। समर्पित इंस्टेंस, मेमोरी सीमा, निष्कासन नीति और नीति के संस्करण वाली कुंजियाँ सँभालें। अस्वीकृतियाँ, Redis त्रुटियाँ और निर्णय में लगा समय मापें। हर कुंजी का पहचानकर्ता सीधे मेट्रिक लेबल में रखने से अलग-अलग लेबल संयोजनों की संख्या भी बढ़ती है।

यह जाँच एक Redis इंस्टेंस के सामान्य व्यवहार और कुछ त्रुटियों तक सीमित है। Redis Cluster फ़ेलओवर, कई क्षेत्र, असली Redis प्रोसेस बंद होने के बाद रिकवरी या प्रोडक्शन लोड पर प्रदर्शन नहीं जाँचे गए। अनुरोध शुरू होने की दर से एक साथ व्यस्त DB कनेक्शन या लंबे अनुरोधों की संख्या सीमित नहीं होती। जहाँ ज़रूरत हो वहाँ अलग समवर्ती सीमा लगाएँ।
