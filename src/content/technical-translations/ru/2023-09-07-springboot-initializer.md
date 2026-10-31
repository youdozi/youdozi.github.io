---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ru",
  "translationKey": "2023-09-07-springboot-initializer",
  "routeSlug": "2023-09-07-springboot-initializer",
  "kind": "post",
  "title": "Создание и проверка проекта Gradle через Spring Initializr",
  "description": "Создайте проект Spring Boot, проверьте настройки Java и Gradle и выполните тесты через Wrapper. Основные файлы рабочего проекта Boot 4.1.2 и границы проверок запуска.",
  "categories": [
    "springboot"
  ],
  "tags": [
    "springboot",
    "springboot initializer"
  ],
  "sourcePath": "src/content/posts/en/2023-09-07-springboot-initializer.md",
  "sourceSha256": "97a876012a6c3d2dbf40856ed6360dc850f12741aecbd5ee7bd96023fb05275f",
  "draftSha256": "9217d7fb797eab36d25b574de62b4eb7cee467b58958075fff5e39ad3bfb447f",
  "manifestPath": ".pipeline/technical-translations/batch-125/manifest.json",
  "manifestSha256": "1934910c02dbe893b786124f1d296d7adf9efbe921d40b3d2cfbceb8f70b4b33",
  "publishedAt": "2026-10-31T15:35:43.034Z",
  "updatedAt": "2026-10-31T15:35:43.034Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 125,
    "approvedAt": "2026-10-31T15:35:43.034Z",
    "basis": "User explicitly requested applying all missing technical-post languages, review, verification and deployment on 2026-11-01, with standing PR merge authorization. Human approval denotes publication authorization; linguistic review is performed by AI, not human/native review."
  }
}
---

Создав проект через Spring Initializr, проверьте его сгенерированным Gradle Wrapper, прежде чем полагаться на IDE. Разделяйте генерацию, разрешение зависимостей, совместимость JDK и запуск приложения, чтобы проще находить причины ошибок.

Пример использует проект Boot 4.1.2, Java 17, Gradle Groovy, действительно сгенерированный [start.spring.io](https://start.spring.io/) 27 октября 2026 года. Его Wrapper выбрал Gradle 9.8.2. Настройки сервиса по умолчанию и доступные версии меняются; не считайте, что эта комбинация будет доступна всегда.

## Порядок обработки

![Процесс генерации, проверки файлов и тестирования](/assets/diagrams/technical/ru-2023-09-07-springboot-initializer.svg)

Сгенерируйте полный архив до запуска Wrapper. Контекстный тест и отдельно запущенное HTTP-приложение подтверждают разные вещи.

## Выберите параметры проекта

| Параметр | Пример | Значение |
| --- | --- | --- |
| Project / Language | Gradle - Groovy / Java | Инструмент сборки и язык исходного кода |
| Spring Boot | 4.1.2 | Финальный выпуск, доступный при создании примера |
| Java / Packaging | 17 / Jar | Инструментарий исходного кода и упаковка |
| Group / Artifact | example / demo | Идентификаторы проекта |
| Package name | example.demo | Пакет приложения |
| Dependencies | Spring Web | Зависимости HTTP-эндпоинта |

Нажмите Generate в интерфейсе или скачайте архив по этому URL. **Убедитесь в успехе каждой команды до запуска следующей.** Используйте пустой рабочий каталог, чтобы не перезаписать существующий проект.

```sh
curl --fail --show-error --location 'https://start.spring.io/starter.zip?type=gradle-project&language=java&bootVersion=4.1.2&baseDir=demo&groupId=example&artifactId=demo&name=Demo&packageName=example.demo&packaging=jar&javaVersion=17&dependencies=web' --output demo.zip
unzip demo.zip
cd demo
./gradlew --version
./gradlew test
```

API генерации может отклонить версию, когда сервис перестанет её предлагать. Проверьте [актуальные метаданные сервиса](https://start.spring.io/metadata/client) и [справочник Initializr](https://docs.spring.io/initializr/docs/current/reference/html/), затем вместе выберите совместимые Boot, JDK и Gradle. Незаметная подмена примера последними настройками по умолчанию меняет условия воспроизведения.

## Проверьте четыре основных сгенерированных файла

Это четыре основных файла с упрощённым форматированием. Полный архив также содержит скрипты Wrapper, JAR и настройки Wrapper и файлы ресурсов. Копирование только этих четырёх файлов в пустой каталог не создаёт `./gradlew`.

### `settings.gradle`

```groovy
rootProject.name = 'demo'
```

### `build.gradle`

```groovy
plugins {
    id 'java'
    id 'org.springframework.boot' version '4.1.2'
    id 'io.spring.dependency-management' version '1.1.7'
}
group = 'example'
version = '0.0.1-SNAPSHOT'
java {
    toolchain { languageVersion = JavaLanguageVersion.of(17) }
}
repositories { mavenCentral() }
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-webmvc'
    testImplementation 'org.springframework.boot:spring-boot-starter-webmvc-test'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
tasks.named('test') { useJUnitPlatform() }
```

### `src/main/java/example/demo/DemoApplication.java`

```java
package example.demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}
```

### `src/test/java/example/demo/DemoApplicationTests.java`

```java
package example.demo;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
class DemoApplicationTests {
    @Test
    void contextLoads() {}
}
```

Сгенерированный проект Boot 4.1.2 использует `spring-boot-starter-webmvc` и `spring-boot-starter-webmvc-test`. Начинайте с конфигурации, созданной для выбранного выпуска, а не смешивайте фрагменты разных поколений Boot. [Требования Boot 4.1.2](https://docs.spring.io/spring-boot/4.1/system-requirements.html) указывают Java 17 или новее и Gradle 8.x начиная с 8.14 либо 9.x.

## Отличайте тесты от запуска приложения

Успешный `contextLoads()` означает, что тестовый контекст запускается. Пока контроллера нет, ответ 404 от `/` не свидетельствует об ошибке запуска. Запустите приложение отдельно и остановите его через Ctrl+C в том терминале.

```sh
./gradlew bootRun
```

Сохраните сгенерированный `build.gradle` и [файлы Gradle Wrapper](https://docs.gradle.org/current/userguide/gradle_wrapper.html) в одном коммите. Версия Gradle не совпадает по смыслу с версией Java в `java.toolchain`. Командой `./gradlew --version` проверьте JVM, выполняющую Gradle, и отличайте её от JDK компиляции и запуска приложения.

Продолжите [открытием проекта в IntelliJ и обслуживанием HTTP](/en/posts/2023-09-10-springboot-intellij-import/). О причинах разных номеров версий Boot и Framework см. [историю выпусков Spring Boot и связи версий](/en/posts/2023-09-13-springboot-history/).
