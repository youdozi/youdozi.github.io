---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2026-11-03-virtual-threads-db-semaphore",
  "routeSlug": "2026-11-03-virtual-threads-db-semaphore",
  "kind": "post",
  "title": "वर्चुअल थ्रेड और DB सेमाफ़ोर से कनेक्शन पूल से पहले अनुरोध कैसे सीमित करें?",
  "description": "JDBC पूल के साथ अतिरिक्त सेमाफ़ोर कब चाहिए? प्रवेश और निष्पादन सीमित करें, ट्रांज़ैक्शन की सफ़ाई के बाद परमिट लौटाएँ और PostgreSQL के साथ टाइमआउट व रद्दीकरण का व्यवहार जाँचें।",
  "categories": [
    "jdk"
  ],
  "tags": [
    "java",
    "virtual-threads",
    "jdbc",
    "hikaricp",
    "semaphore",
    "postgresql"
  ],
  "sourcePath": "src/content/posts/en/2026-11-03-virtual-threads-db-semaphore.md",
  "sourceSha256": "103d90ef1cccefaa0b1dd31120b1813c5ded6536bcd76a9ae5a0f75388d3584a",
  "draftSha256": "65602d177defd005d42c5e0f20085f0d28cc0f2470b4ff3a201c21d6b8b49914",
  "manifestPath": ".pipeline/technical-translations/batch-1341/manifest.json",
  "manifestSha256": "c799b6f94efb991d515ad7d285b737aad0702b220d0e539fdf6b3bc60d7efb56",
  "publishedAt": "2026-11-27T08:44:35.252Z",
  "updatedAt": "2026-11-27T08:44:35.252Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 210,
    "approvedAt": "2026-11-27T08:44:35.252Z",
    "basis": "User authorized publication of the five named Hindi technical editions in item 134."
  }
}
---

वर्चुअल थ्रेड इस्तेमाल करने पर डेटाबेस के सामने सेमाफ़ोर लगाना अनिवार्य नहीं है। कनेक्शन की संख्या पूल पहले ही सीमित करता है। अतिरिक्त सेमाफ़ोर तब काम आता है जब आप **DB का काम पहले ही अस्वीकार करना चाहें, प्रवेश पा चुके ऑपरेशन की संख्या सीमित करना चाहें या अलग वर्कलोड के लिए समवर्ती काम का बजट तय करना चाहें**। Oracle की गाइड भी बताती है कि डेटाबेस कनेक्शन पूल स्वयं सेमाफ़ोर की तरह काम करता है। [Oracle की वर्चुअल थ्रेड गाइड](https://docs.oracle.com/en/java/javase/25/core/virtual-threads.html)

[JDK 21–25 में वर्चुअल थ्रेड की तुलना](/en/posts/2026-10-31-virtual-threads-jdk21-jdk25/) के बाद अब डेटाबेस कनेक्शन देखते हैं। [10k RPS आर्किटेक्चर](/en/posts/2026-10-31-jdk-10k-rps-architecture/) में चर्चा किए गए प्रवेश नियंत्रण को यहाँ खास तौर पर DB के काम पर लागू करेंगे। उदाहरण Java 21 या बाद के संस्करण में एक कनेक्शन पर चलने वाले सिंक्रोनस JDBC ट्रांज़ैक्शन के लिए है। एक ऐप इंस्टेंस के सभी अनुरोध एक ही सेमाफ़ोर साझा करें। हर अनुरोध के लिए नया सेमाफ़ोर न बनाएँ।

## कनेक्शन पूल पहले से हो तो किसे सीमित करें?

वर्चुअल थ्रेड की मदद से थ्रेड पर अपेक्षाकृत कम खर्च करते हुए कई काम प्रतीक्षा में रख सकते हैं। इससे डेटाबेस की क्वेरी क्षमता अपने आप नहीं बढ़ती और लॉक की होड़ भी कम नहीं होती। भरे हुए पूल से कनेक्शन की प्रतीक्षा कर रहे अनुरोध अब भी मेमोरी और अनुरोध का स्टेट रखते हैं।

| स्थिति | पहले क्या करें |
| --- | --- |
| कनेक्शन की संख्या और पूल की प्रतीक्षा सीमा पर्याप्त हैं | कनेक्शन पूल का कॉन्फ़िगरेशन बनाए रखें |
| ओवरलोड होने पर अनुरोध पूल तक पहुँचने से पहले अस्वीकार करने हैं | प्रवेश नियंत्रण लगाएँ |
| बैच या महँगी क्वेरी सारे कनेक्शन घेर लेती हैं | वर्कलोड के लिए अलग बजट रखें, ज़रूरत हो तो पूल अलग करें |
| धीमा SQL या लॉक लंबे समय तक कनेक्शन रोकता है | पहले क्वेरी, इंडेक्स, ट्रांज़ैक्शन और डेटाबेस की सीमाएँ जाँचें |

HikariCP का `maximumPoolSize` पूल में कनेक्शन की संख्या सीमित करता है। कोई कनेक्शन उपलब्ध न हो तो `getConnection()`, `connectionTimeout` तक प्रतीक्षा करके एक्सेप्शन देता है। इस टाइमआउट का न्यूनतम मान 250ms है। सेमाफ़ोर पर 20ms की सीमा लगाने से पूल की प्रतीक्षा भी 20ms में समाप्त नहीं होती। [HikariCP का कॉन्फ़िगरेशन](https://github.com/brettwooldridge/HikariCP#configuration-knobs-baby)

## निष्पादन और कुल प्रवेश, दोनों सीमित करें

उदाहरण में दो सेमाफ़ोर हैं।

- **निष्पादन के B परमिट** कनेक्शन लेने से लेकर ट्रांज़ैक्शन और कनेक्शन की सफ़ाई तक चल रहे ऑपरेशन सीमित करते हैं।
- **प्रवेश के B+Q परमिट** गेट के भीतर सभी ऑपरेशन सीमित करते हैं, जिनमें निष्पादन परमिट की प्रतीक्षा करने वाले भी शामिल हैं। प्रवेश परमिट न बचे तो अनुरोध तुरंत अस्वीकार होता है।

जब सभी B निष्पादन परमिट इस्तेमाल में हों, तो प्रवेश पा चुके अधिकतम Q अतिरिक्त ऑपरेशन रह सकते हैं। हालाँकि किसी काम को निष्पादन परमिट मिलने से पहले भी शेड्यूल किया जा सकता है। इसलिए हर क्षण प्रतीक्षारत काम की संख्या पर ठीक Q की सीमा मानना सही नहीं है। केवल प्रतीक्षा की अवधि सीमित करने वाला एक सेमाफ़ोर प्रवेश पा चुके प्रतीक्षारत ऑपरेशन की संख्या सीमित नहीं करता।

![पहले प्रवेश और फिर निष्पादन का परमिट लें। DB ट्रांज़ैक्शन और कनेक्शन की सफ़ाई पूरी होने के बाद केवल वे परमिट लौटाएँ जो वास्तव में मिले थे।](/assets/diagrams/technical/hi-2026-11-03-virtual-threads-db-semaphore.svg)

DB संसाधनों का बॉक्स भीतर के अपवादों के रास्ते दिखाता है। कनेक्शन न मिले तो काम छोड़कर परमिट लौटाएँ। ट्रांज़ैक्शन सेटअप विफल हो तो मिले हुए कनेक्शन की सफ़ाई की कोशिश करें। काम या कमिट विफल हो तो रोलबैक का प्रयास करें।

प्रवेश अस्वीकार होने पर कोई परमिट लौटाना नहीं पड़ता। निष्पादन परमिट न मिले या प्रतीक्षा कर रहा थ्रेड इंटरप्ट हो जाए, तो केवल प्रवेश परमिट लौटाएँ। दोनों परमिट मिल गए हों तो कनेक्शन लेने, ट्रांज़ैक्शन और सफ़ाई का क्रम पूरा होने के बाद ही उन्हें लौटाएँ, चाहे काम सफल हो या एक्सेप्शन के साथ समाप्त हो। **सिर्फ़ कॉलर का टाइमआउट होने पर किसी दूसरे थ्रेड से परमिट न लौटाएँ।** DB का काम जारी हो तो इससे तय निष्पादन सीमा पार हो सकती है।

## B, Q और पूल का आकार कैसे चुनें?

B एक साथ चल रहे DB ऑपरेशन गिनता है, प्रति सेकंड अनुरोध नहीं। इसमें कनेक्शन की प्रतीक्षा, कमिट और सफ़ाई शामिल हैं, इसलिए एक साथ चल रही SQL क्वेरी की संख्या B से कम हो सकती है। डेटाबेस की संतृप्ति, कनेक्शन अपने पास रखने की अवधि और दूसरे वर्कलोड का बजट मापकर B चुनें। Q बताता है कि ओवरलोड में कितने अतिरिक्त ऑपरेशन को प्रवेश देंगे। इसे चुनते समय प्रतीक्षा का बजट और मेमोरी दोनों देखें।

मिसाल के लिए पूल P=24 और गेट B=16 होने पर इस गेट से एक साथ अधिकतम 16 ऑपरेशन चल सकते हैं। बाकी 8 कनेक्शन दूसरे काम के लिए आरक्षित नहीं हैं। गेट के बाहर के कॉलर यदि यही पूल साझा करते हैं तो सारे कनेक्शन ले सकते हैं। अलगाव के लिए अलग पूल बनाएँ तब भी डेटाबेस के स्तर पर सभी पूल के बजट जोड़ें।

कनेक्शन का बजट तय करते समय `peak simultaneous instances × pool size per instance + batch, operations and other client connections ≤ DB connection budget` जाँचें। एक साथ चालू इंस्टेंस की अधिकतम संख्या में ऑटोस्केलिंग और रोलिंग डिप्लॉयमेंट के दौरान पुराने व नए इंस्टेंस का साथ चलना शामिल है। `instance count × B` की सीमा केवल इस गेट से आने वाले काम पर है। ये संख्याएँ गणना समझाने के लिए हैं। इन्हें अनुशंसित सेटिंग या मापा हुआ प्रदर्शन न समझें।

## चलाकर देखने के लिए JDBC का उदाहरण

गेट अपने ट्रांज़ैक्शन और कनेक्शन का स्वामी है। कॉलबैक सिंक्रोनस चले और ऐसा मान लौटाए जिसका पूरा डेटा तैयार हो चुका हो। कॉलबैक में कमिट, रोलबैक या ऑटो-कमिट सेटिंग में बदलाव न करें। `Connection`, `ResultSet` या बाद में पढ़ी जाने वाली क्वेरी स्ट्रीम लौटाने या कॉलबैक में अलग असिंक्रोनस DB काम शुरू करने से काम इस सीमा की सुरक्षा से बाहर चला जाता है।

### `DbBulkhead.java`

```java
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Duration;
import java.util.Objects;
import java.util.concurrent.RejectedExecutionException;
import java.util.concurrent.Semaphore;
import java.util.concurrent.TimeUnit;
import javax.sql.DataSource;

public final class DbBulkhead {
    @FunctionalInterface
    public interface SqlWork<T> {
        T run(Connection connection) throws SQLException;
    }

    private final DataSource source;
    private final Semaphore slots;
    private final Semaphore running;

    public DbBulkhead(DataSource source, int concurrent, int extraSlots) {
        this.source = Objects.requireNonNull(source);
        if (concurrent < 1 || extraSlots < 0) {
            throw new IllegalArgumentException("invalid capacity");
        }
        slots = new Semaphore(Math.addExact(concurrent, extraSlots));
        running = new Semaphore(concurrent, true);
    }

    public <T> T transaction(Duration queueWait, SqlWork<T> work)
            throws SQLException, InterruptedException {
        Objects.requireNonNull(work);
        long nanos = queueWait.toNanos();
        if (nanos < 0) throw new IllegalArgumentException("negative wait");
        if (!slots.tryAcquire()) {
            throw new RejectedExecutionException("db admission full");
        }
        boolean acquired = false;
        try {
            acquired = running.tryAcquire(nanos, TimeUnit.NANOSECONDS);
            if (!acquired) {
                throw new RejectedExecutionException("db admission timed out");
            }
            try (Connection connection = source.getConnection()) {
                connection.setAutoCommit(false);
                try {
                    T value = work.run(connection);
                    connection.commit();
                    return value;
                } catch (SQLException | RuntimeException | Error failure) {
                    try {
                        connection.rollback();
                    } catch (SQLException rollbackFailure) {
                        failure.addSuppressed(rollbackFailure);
                    }
                    throw failure;
                }
            }
        } finally {
            if (acquired) running.release();
            slots.release();
        }
    }

    int available() { return running.availablePermits(); }
    int availableSlots() { return slots.availablePermits(); }
}
```

कोड `running` को तभी लौटाता है जब परमिट मिला हो। इसलिए प्रतीक्षा विफल होने या इंटरप्ट होने पर परमिट की संख्या नहीं बढ़ती। SQL एक्सेप्शन, रनटाइम एक्सेप्शन या एरर पर रोलबैक का प्रयास होता है। रोलबैक विफल हो तो उसका एक्सेप्शन मूल एक्सेप्शन में suppressed exception के रूप में जुड़ता है। कॉलर को परिणाम कमिट और कनेक्शन का `close()` पूरा होने पर ही मिलता है। कमिट विफल होने पर या कमिट के बाद सफ़ाई विफल होने पर कॉलर को एक्सेप्शन मिल सकता है, भले ही बदलाव लागू हो चुका हो। लिखने का ऑपरेशन बिना जाँच दोबारा न चलाएँ।

निष्पक्ष सेमाफ़ोर भी पूरे अनुरोध क्रम की गारंटी नहीं देता। उदाहरण में निष्पादन के लिए निष्पक्ष सेमाफ़ोर से समय सीमा के साथ परमिट माँगते हैं, जबकि प्रवेश के लिए तुरंत प्रयास करते हैं। समय सीमा के बिना `tryAcquire()` निष्पक्षता की सेटिंग नहीं मानता। `available()` मेथड अभ्यास में निरीक्षण के लिए हैं। इनका मान पढ़कर अलग से प्रवेश का निर्णय लेने पर रेस हो सकती है। [Semaphore API](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/Semaphore.html)

डेमो में पूल का आकार 2, B=1 और Q=0 है। यह जाँचता है कि पहले ट्रांज़ैक्शन के पास परमिट रहते हुए दूसरा ऑपरेशन अस्वीकार होता है। लैच से ट्रांज़ैक्शन थोड़ी देर रोकना इसी स्थिति को दोहराने के लिए है। सेवा में अनुरोध सँभालने के लिए यह अनुशंसित तरीका नहीं है।

### `Demo.java`

```java
import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import java.sql.SQLException;
import java.time.Duration;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.RejectedExecutionException;
import java.util.concurrent.TimeUnit;

public class Demo {
    static HikariDataSource pool() {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl(System.getenv("DB_URL"));
        config.setUsername(System.getenv("DB_USER"));
        config.setPassword(System.getenv("DB_PASSWORD"));
        config.setMaximumPoolSize(2);
        config.setMinimumIdle(0);
        config.setConnectionTimeout(500);
        config.setValidationTimeout(250);
        return new HikariDataSource(config);
    }

    public static void main(String[] args) throws Exception {
        try (var pool = pool(); var tasks = Executors.newVirtualThreadPerTaskExecutor()) {
            var gate = new DbBulkhead(pool, 1, 0);
            var entered = new CountDownLatch(1);
            var release = new CountDownLatch(1);
            var first = tasks.submit(() -> gate.transaction(Duration.ZERO, connection -> {
                if (!Thread.currentThread().isVirtual()) throw new AssertionError();
                try (var statement = connection.createStatement()) {
                    statement.setQueryTimeout(2);
                    try (var rows = statement.executeQuery("SELECT 42")) {
                        rows.next();
                        int value = rows.getInt(1);
                        entered.countDown();
                        try {
                            if (!release.await(5, TimeUnit.SECONDS)) {
                                throw new SQLException("demo coordination timed out");
                            }
                        } catch (InterruptedException interrupted) {
                            Thread.currentThread().interrupt();
                            throw new SQLException("demo interrupted", interrupted);
                        }
                        return value;
                    }
                }
            }));
            try {
                if (!entered.await(5, TimeUnit.SECONDS)) throw new AssertionError("not entered");
                var second = tasks.submit(() -> gate.transaction(Duration.ZERO, c -> 0));
                try {
                    second.get(5, TimeUnit.SECONDS);
                    throw new AssertionError("must reject");
                } catch (ExecutionException failure) {
                    if (!(failure.getCause() instanceof RejectedExecutionException)) throw failure;
                    System.out.println("overload=rejected");
                }
            } finally {
                release.countDown();
            }
            System.out.println("query=" + first.get(5, TimeUnit.SECONDS));
            System.out.println("available=" + gate.available());
        }
    }
}
```

### `build.gradle`

```groovy
plugins { id 'application' }
repositories { mavenCentral() }
dependencies {
    implementation 'com.zaxxer:HikariCP:7.1.0'
    runtimeOnly 'org.postgresql:postgresql:42.7.14'
    runtimeOnly 'org.slf4j:slf4j-simple:2.0.20'
}
sourceSets.main.java {
    srcDirs = ['.']
    include 'DbBulkhead.java', 'Demo.java', 'DbBulkheadChecks.java'
}
tasks.withType(JavaCompile).configureEach { options.release = 21 }
application { mainClass = 'Demo' }
tasks.register('copyDependencies', Copy) {
    from configurations.runtimeClasspath
    into layout.buildDirectory.dir('deps')
}
tasks.register('contracts', JavaExec) {
    classpath = sourceSets.main.runtimeClasspath
    mainClass = 'DbBulkheadChecks'
}
```

### `settings.gradle`

```groovy
rootProject.name = 'virtual-threads-db-semaphore'
```

### स्थानीय मशीन पर चलाएँ

ऊपर की चार फ़ाइलें अलग अभ्यास डायरेक्टरी में सहेजें। Docker, JDK 21 और Gradle 8.14.3 इंस्टॉल करें। निर्भरताएँ डाउनलोड करने के लिए Gradle को JDK 21 पर चलाएँ। इसके बाद कंपाइल करने और चलाने के लिए चुने हुए JDK के `javac` और `java` सीधे इस्तेमाल होते हैं। इस तरह JDK 25 जाँचने के लिए Gradle 8.14.3 को JDK 25 पर नहीं चलाना पड़ता। Gradle को स्वयं JDK 21 पर चलाने के लिए संस्करण 8.5 या बाद का चाहिए। इस अभ्यास में 8.14.3 इस्तेमाल हुआ। [Gradle में Java 21 रनटाइम का समर्थन](https://docs.gradle.org/8.5/release-notes.html)

नीचे के कमांड POSIX शेल में चलाएँ। `JAVA_HOME` उस JDK की ओर इंगित करे जिसे चलाना है। निर्भरताएँ डाउनलोड करते समय JDK 21 चुनें। उदाहरण का पासवर्ड केवल अस्थायी स्थानीय डेटाबेस के लिए है। पोर्ट 55432 व्यस्त हो तो दूसरा पोर्ट चुनें।

```sh
(
  set -eu
  gradle --no-daemon -q copyDependencies
  db_container=$(docker run -d --rm -p 127.0.0.1:55432:5432 \
    -e POSTGRES_USER=demo -e POSTGRES_DB=demo \
    -e POSTGRES_PASSWORD=example-only \
    postgres@sha256:839fbb5a4942a7758dd93e18b42ea5649807491a0545b5eeeb8f0b8bb11857a5)
  trap 'docker stop "$db_container" >/dev/null' EXIT
  ready=false
  for attempt in $(seq 1 30); do
    if docker exec "$db_container" pg_isready -h 127.0.0.1 -U demo -d demo >/dev/null 2>&1; then
      ready=true
      break
    fi
    sleep 1
  done
  if [ "$ready" != true ]; then exit 1; fi
  mkdir -p build/classes
  "$JAVA_HOME/bin/javac" --release 21 -cp 'build/deps/*' \
    -d build/classes DbBulkhead.java Demo.java
  DB_URL='jdbc:postgresql://127.0.0.1:55432/demo?connectTimeout=2&socketTimeout=5' \
    DB_USER=demo DB_PASSWORD=example-only \
    "$JAVA_HOME/bin/java" -cp 'build/classes:build/deps/*' Demo
)
```

स्थानीय रन में नीचे का मानक आउटपुट मिला। HikariCP के शुरू और बंद होने के लॉग अलग से दिख सकते हैं।

```text
overload=rejected
query=42
available=1
```

जाँच के लिए Temurin 21.0.13+9 और 25.0.5+8, PostgreSQL 17.11, HikariCP 7.1.0 और pgJDBC 42.7.14 इस्तेमाल हुए। हर JDK पर 45 अतिरिक्त शर्तें जाँची गईं। इनमें कमिट और रोलबैक, प्रवेश सीमा पार होना, प्रतीक्षा का टाइमआउट और इंटरप्ट, रद्द करने के बाद काम जारी रहना, सर्वर पर स्टेटमेंट टाइमआउट के बाद बहाली, पूल भरना और बार-बार विफलता के बाद परमिट वापस मिलना शामिल थे। HTTP लोड टेस्ट या प्रोडक्शन थ्रूपुट का मापन नहीं किया गया।

## टाइमआउट और Spring ट्रांज़ैक्शन में किन सीमाओं का ध्यान रखें?

**प्रतीक्षा का टाइमआउट और काम का टाइमआउट अलग रखें।** उदाहरण में `queueWait` केवल निष्पादन परमिट पाने की प्रतीक्षा सीमित करता है। पूल से कनेक्शन लेने, SQL, लॉक की प्रतीक्षा, नेटवर्क और सफ़ाई के अलग बजट हैं। पूरे अनुरोध की समय सीमा लागू करने के लिए हर चरण तक बचा हुआ समय पहुँचाने की व्यवस्था चाहिए। इस उदाहरण में वह व्यवस्था लागू नहीं की गई है।

PostgreSQL में `statement_timeout` सर्वर पर स्टेटमेंट की अवधि और `lock_timeout` लॉक मिलने तक की प्रतीक्षा सीमित करता है। अभ्यास में ट्रांज़ैक्शन के भीतर `SET LOCAL statement_timeout = '100ms'` सेट करके जाँचा गया कि `pg_sleep(2)` SQLState `57014` के साथ विफल होता है और उसके बाद दूसरा काम चल सकता है। असली मान अपनी क्वेरी और समय सीमा के अनुसार चुनें। [PostgreSQL 17 की टाइमआउट सेटिंग](https://www.postgresql.org/docs/17/runtime-config-client.html)

`Future.cancel(true)` या HTTP अनुरोध समाप्त होने से यह गारंटी नहीं मिलती कि JDBC क्वेरी तुरंत रुकेगी। pgJDBC में क्वेरी, रद्दीकरण संकेत भेजने और सॉकेट से पढ़ने की अलग सीमाएँ हैं। सॉकेट टाइमआउट के बाद कनेक्शन बंद करना इस बात की पुष्टि नहीं है कि सर्वर का काम रुक गया। रद्दीकरण और सफ़ाई के दौरान परमिट उसी कोड के पास रहे जो काम चला रहा है। लिखने का परिणाम अनिश्चित हो तो दोबारा प्रयास तय करने के लिए idempotency key या परिणाम की क्वेरी इस्तेमाल करें। [pgJDBC कनेक्शन प्रॉपर्टी](https://jdbc.postgresql.org/documentation/use/)

**Spring में ट्रांज़ैक्शन शुरू करने से पहले प्रवेश परमिट लें।** अलग बीन में बिना ट्रांज़ैक्शन वाला प्रवेश मेथड पहले गेट से गुज़रकर ट्रांज़ैक्शनल प्रॉक्सी को कॉल कर सकता है। दूसरा तरीका प्रवेश मिलने के बाद `TransactionTemplate` चलाना है। प्रॉक्सी कॉल या टेम्पलेट के कमिट और सफ़ाई पूरी करके लौटने पर परमिट लौटाएँ। पहले से शुरू ट्रांज़ैक्शन के मेथड के भीतर प्रतीक्षा करने पर बाहरी ट्रांज़ैक्शन के संसाधन घिरे रह सकते हैं। ऊपर के JDBC स्वामित्व वाले कोड को मौजूदा Spring ट्रांज़ैक्शन में सीधे न मिलाएँ।

`REQUIRES_NEW` को बाहरी ट्रांज़ैक्शन का कनेक्शन रखते हुए दूसरा कनेक्शन चाहिए हो सकता है। इससे हर ऑपरेशन के लिए एक कनेक्शन की धारणा टूटती है और पूल भर सकता है या डेडलॉक हो सकता है। गेट भी रीएंट्रेंट नहीं है। उसी गेट को रिकर्सिव कॉल में दोबारा न लें। [Spring ट्रांज़ैक्शन प्रोपेगेशन और पूल की सीमा](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/tx-propagation.html)

प्रोडक्शन में प्रवेश सीमा भरने पर अस्वीकृति और प्रतीक्षा टाइमआउट अलग-अलग गिनें। गेट व पूल में प्रतीक्षा, कनेक्शन अपने पास रखने की अवधि, SQL की अवधि और लॉक की प्रतीक्षा साथ देखें। अस्वीकृति को HTTP 503 या किसी दूसरे रिस्पॉन्स में बदलते समय क्लाइंट के दोबारा प्रयास का बजट तय करें ताकि असीमित प्रयास लोड न बढ़ाएँ। सिर्फ़ अस्वीकृति की संख्या देखकर B न बढ़ाएँ। डेटाबेस की लेटेंसी और संतृप्ति के आधार पर निर्णय लें।
