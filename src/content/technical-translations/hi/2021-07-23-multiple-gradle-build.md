---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2021-07-23-multiple-gradle-build",
  "routeSlug": "2021-07-23-multiple-gradle-build",
  "kind": "post",
  "title": "Gradle से कई Vue ऐप एक Spring Boot JAR में कैसे पैक करें",
  "description": "हर Vue ऐप के लिए अलग npm ci और बिल्ड टास्क चलाएँ। Gradle Sync से मौजूदा फ़ाइलें इकट्ठी करें और bootJar में सही पथ पर रखें ताकि पुरानी फ़ाइलें पैकेज में न रहें।",
  "categories": [
    "springboot"
  ],
  "tags": [
    "gradle",
    "vue",
    "build",
    "SpringBoot"
  ],
  "sourcePath": "src/content/posts/en/2021-07-23-multiple-gradle-build.md",
  "sourceSha256": "2af4402a72130c6c53faa9d34008be0c7bc63b78b82a680f5675bdd70532ec4d",
  "draftSha256": "ed27de246c322d9d13a94f6e75dcfb4be28b1070e06266b9b21959e233e97b69",
  "manifestPath": ".pipeline/technical-translations/batch-144/manifest.json",
  "manifestSha256": "f2cdc48717558ad001e3a065a1fcd8bf668c42c267757c24843b091e441bad71",
  "publishedAt": "2026-11-27T12:46:07.279Z",
  "updatedAt": "2026-11-27T12:46:07.279Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 220,
    "approvedAt": "2026-11-27T12:46:07.279Z",
    "basis": "The owner authorized publication of the five Hindi editions in item 144. The translator reviewed the translations and diagrams."
  }
}
---

एक Spring Boot JAR में कई Vue ऐप पैक करने के लिए हर ऐप का अपना `npm ci` और बिल्ड टास्क रखें। बनी हुई फ़ाइलें पहले `build/` के नीचे इकट्ठी करें, फिर उन्हें `bootJar` में जोड़ें। एक ऐप का इंस्टॉल टास्क दूसरे ऐप के लिए इस्तेमाल न करें और बने हुए बंडल सीधे `src/main/resources` में न लिखें।

यह उदाहरण दो ऐप को `/project1/index.html` और `/project2/index.html` पर उपलब्ध कराता है। इसे दोहराने का वातावरण JDK 17.0.8.1, Gradle 8.4, Node 24.13.0/npm 11.6.2, Boot 3.5.7, Vue 3.5.44 और Vite 8.3.5 है। ये संस्करण उदाहरण दोहराने के लिए तय किए गए थे। प्रोडक्शन के लिए डिपेंडेंसी चुनते समय [Vite की रनटाइम आवश्यकताएँ](https://vite.dev/guide/) और चुनी हुई Boot रिलीज़ की आवश्यकताएँ अलग से जाँचें।

## ऐप के बिल्ड से JAR तक

![दोनों Vue ऐप अलग-अलग बिल्ड होते हैं, Sync उनके आउटपुट इकट्ठे करता है और bootJar उन्हें JAR में अलग पथ पर रखता है](/assets/diagrams/technical/hi-2021-07-23-multiple-gradle-build.svg)

हर Vue ऐप अपना आउटपुट बनाता है। Gradle का Sync टास्क केवल उन आउटपुट को इकट्ठा करता है। फिर bootJar उन्हें स्टैटिक फ़ाइलों के लिए अलग-अलग पथ पर रखता है।

## हर ऐप के टास्क और पैकेजिंग

इन फ़ाइलों को खाली प्रोजेक्ट में सहेजें। हर ऐप की अपनी `package.json`, लॉकफ़ाइल, `node_modules` और `dist` निर्देशिकाएँ हैं। `prepare.sh` साझा HTML और JS को दूसरे ऐप में कॉपी करती है और दोनों लॉकफ़ाइलें बनाती है।

### `settings.gradle`

```groovy
rootProject.name = 'multi-frontend'
```

### `build.gradle`

```groovy
plugins {
    id 'java'
    id 'org.springframework.boot' version '3.5.7'
}
group = 'example'
version = '1.0.0'
repositories { mavenCentral() }
dependencies {
    implementation platform('org.springframework.boot:spring-boot-dependencies:3.5.7')
    implementation 'org.springframework.boot:spring-boot-starter-web'
}

def apps = ['project1', 'project2']
def npmCommand = System.getProperty('os.name').toLowerCase().contains('windows') ? 'npm.cmd' : 'npm'
def frontendBuilds = apps.collect { app ->
    def frontend = layout.projectDirectory.dir("frontend/${app}")
    def install = tasks.register("${app}NpmCi", Exec) {
        workingDir frontend
        commandLine npmCommand, 'ci', '--no-audit', '--no-fund'
        inputs.files(frontend.file('package.json'), frontend.file('package-lock.json'))
        outputs.dir(frontend.dir('node_modules'))
    }
    tasks.register("${app}Build", Exec) {
        dependsOn install
        workingDir frontend
        commandLine npmCommand, 'run', 'build'
        inputs.files(fileTree(frontend) {
            exclude 'node_modules/**', 'dist/**'
        })
        outputs.dir(frontend.dir('dist'))
    }
}
def collectFrontend = tasks.register('collectFrontend', Sync) {
    dependsOn frontendBuilds
    into layout.buildDirectory.dir('frontend-resources')
    apps.each { app ->
        from("frontend/${app}/dist") { into "static/${app}" }
    }
}
tasks.named('bootJar') {
    dependsOn collectFrontend
    from(collectFrontend) { into 'BOOT-INF/classes' }
}
```

### `src/main/java/example/Application.java`

```java
package example;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

### `frontend/project1/package.json`

```json
{
  "name": "project1",
  "private": true,
  "type": "module",
  "scripts": {
    "build": "vite build --base=/project1/"
  },
  "dependencies": {
    "vue": "3.5.44"
  },
  "devDependencies": {
    "vite": "8.3.5"
  }
}
```

### `frontend/project2/package.json`

```json
{
  "name": "project2",
  "private": true,
  "type": "module",
  "scripts": {
    "build": "vite build --base=/project2/"
  },
  "dependencies": {
    "vue": "3.5.44"
  },
  "devDependencies": {
    "vite": "8.3.5"
  }
}
```

### `frontend/project1/index.html`

```html
<!doctype html>
<html lang="en"><head><meta charset="UTF-8"><title>Vue build example</title></head>
<body><div id="app"></div><script type="module" src="/src/main.js"></script></body></html>
```

### `frontend/project1/src/main.js`

```js
import { createApp, h } from 'vue';
createApp({ render: () => h('h1', `Vue app at ${import.meta.env.BASE_URL}`) }).mount('#app');
```

### `prepare.sh`

```sh
#!/bin/sh
set -eu
mkdir -p frontend/project2/src
cp frontend/project1/index.html frontend/project2/index.html
cp frontend/project1/src/main.js frontend/project2/src/main.js
for app in project1 project2; do
    (cd "frontend/$app" && npm install --package-lock-only --ignore-scripts --no-audit --no-fund)
done
```

उदाहरण पहली बार तैयार करते समय `prepare.sh` चलाएँ और दोनों बनी हुई `package-lock.json` फ़ाइलें कमिट करें। इसके बाद CI बिल्ड सहेजी हुई लॉकफ़ाइलों के साथ `npm ci` इस्तेमाल करते हैं। हर बिल्ड पर लॉकफ़ाइलें दोबारा न बनाएँ।

## बिल्ड करें और चलाएँ

Node और npm को PATH में रखकर प्रोजेक्ट की मूल निर्देशिका से ये कमांड चलाएँ।

```sh
node --version
npm --version
sh prepare.sh
gradle --no-daemon clean bootJar
java -jar build/libs/multi-frontend-1.0.0.jar
```

मौजूदा प्रोजेक्ट में Gradle Wrapper हो तो उसके चुने हुए Gradle संस्करण को `./gradlew` से चलाएँ। एप्लिकेशन शुरू होने पर `http://localhost:8080/project1/index.html` और `http://localhost:8080/project2/index.html` खोलें। पन्नों पर क्रमशः `Vue app at /project1/` और `Vue app at /project2/` दिखते हैं।

[Vite का base विकल्प](https://vite.dev/guide/build.html#public-base-path) हर ऐप की फ़ाइलों के लिए सही URL बनाता है। सर्वर पर SPA रूटिंग अलग से कॉन्फ़िगर करनी होती है। यह उदाहरण सीधे `index.html` के URL खोलता है। हिस्ट्री राउटर के किसी पथ को सीधे खोलने या दूसरा कॉन्टेक्स्ट पथ इस्तेमाल करने के लिए अतिरिक्त कॉन्फ़िगरेशन चाहिए।

## JAR के भीतर वास्तविक पथ जाँचें

```text
BOOT-INF/classes/static/project1/index.html
BOOT-INF/classes/static/project1/assets/...
BOOT-INF/classes/static/project2/index.html
BOOT-INF/classes/static/project2/assets/...
```

हर ऐप का बिल्ड पूरा होने पर `collectFrontend`, `Sync` से सिर्फ मौजूदा आउटपुट इकट्ठा करता है। `bootJar` उन फ़ाइलों को निष्पादन योग्य JAR के क्लासपाथ के नीचे जोड़ता है। [Gradle में फ़ाइलों का प्रबंधन](https://docs.gradle.org/current/userguide/working_with_files.html) और [Boot आर्काइव की पैकेजिंग](https://docs.spring.io/spring-boot/3.5/gradle-plugin/packaging.html) देखें।

इस कॉन्फ़िगरेशन से दोनों ऐप बिल्ड और पैक किए गए थे। चल रहे JAR ने दोनों के HTML और JS को HTTP पर उपलब्ध कराया। फिर एक ऐप की `public` निर्देशिका से एक फ़ाइल हटाई गई और `clean` के बिना JAR दोबारा बनाया गया। इससे जाँचा गया कि पुरानी फ़ाइल नए JAR में नहीं रही। दोनों ऐप की लॉकफ़ाइलें अलग-अलग जाँची गई थीं।

## मौजूदा प्रोजेक्ट में इसे कैसे अपनाएँ

- `apps` सूची में निर्देशिकाओं के अनुरूप नाम रखें और हर ऐप की लॉकफ़ाइल दें।
- बिल्ड से बनने वाले `static/project1` और `static/project2` के पथ हाथ से लिखे संसाधनों से अलग रखें।
- Vue SFC के लिए उस ऐप के अनुरूप प्लगइन और Vite कॉन्फ़िगरेशन जोड़ें। यह छोटा उदाहरण Vue रेंडर फ़ंक्शन इस्तेमाल करता है।
- यह कॉन्फ़िगरेशन निष्पादन योग्य `bootJar` के लिए है। साधारण `jar` अलग होता है। जिस आर्टिफ़ैक्ट को तैनात करेंगे, उसी को जाँचें।

मौजूदा एप्लिकेशन के लिए पैकेजिंग से अलग [Spring Boot में Java और Jakarta माइग्रेशन की आवश्यकताएँ](/hi/posts/2023-09-08-springboot3-migration/) जाँचें। यदि एप्लिकेशन Batch जॉब भी चलाता है, तो [Batch रिपॉज़िटरी के माइग्रेशन और रीस्टार्ट की जाँचें](/hi/posts/2023-10-27-springbatch5-migration/) अपनाएँ। JAR से फ़्रंटएंड फ़ाइलें उपलब्ध होने से सहेजे गए जॉब डेटा की पुष्टि नहीं होती।

रिलीज़ के आधार पर स्वचालन करने के लिए [GitHub रिलीज़ और एसेट का चयन](/en/posts/2023-09-23-linux-shellscript-github-latest/) और [संख्यात्मक संस्करण तुलना के इनपुट नियम](/hi/posts/2023-11-17-linux-shellscript-version-compare/) देखें। तैयारी की स्क्रिप्ट में इंटरप्रेटर चुनने के बारे में [POSIX sh फ़ंक्शन गाइड](/hi/posts/2023-09-20-linux-shellscript-function-error/) बताती है।
