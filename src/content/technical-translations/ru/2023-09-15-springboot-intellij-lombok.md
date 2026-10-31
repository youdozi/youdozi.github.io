---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ru",
  "translationKey": "2023-09-15-springboot-intellij-lombok",
  "routeSlug": "2023-09-15-springboot-intellij-lombok",
  "kind": "post",
  "title": "Lombok в IntelliJ: разделяем компиляцию Gradle и поддержку IDE",
  "description": "Настройте Lombok для обработки аннотаций main и test, проверьте созданные методы и отличайте ошибки сборки от распознавания IDE.",
  "categories": [
    "springboot"
  ],
  "tags": [
    "springboot",
    "intellij community",
    "lombok"
  ],
  "sourcePath": "src/content/posts/en/2023-09-15-springboot-intellij-lombok.md",
  "sourceSha256": "9fe45995bdaea610316410d2b79746c008656c5d20256f9de7d66bc47499dda1",
  "draftSha256": "9c8efbdd2ece010efd2e69ca3035d00ce65ed298f627f004cfabdf26f81f80f6",
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

Если методы Lombok кажутся отсутствующими, сначала выполните `./gradlew clean test`, чтобы понять, падает ли сборка. Поддержка IDE помогает редактору распознавать созданные члены; конфигурация процессора Gradle генерирует их при компиляции. Одно не заменяет другое.

Пример продолжает [проект Initializr](/en/posts/2023-09-07-springboot-initializer/) и [HTTP-пример](/en/posts/2023-09-10-springboot-intellij-import/). Он использует Boot 4.1.2, Gradle 9.8.2 и JDK 17; BOM выбрал Lombok 1.18.48. Это одна рабочая комбинация, а не гарантия совместимости всех сочетаний JDK/Lombok.

## Порядок обработки

![Компиляция Lombok до исправлений IDE](/assets/diagrams/technical/ru-2023-09-15-springboot-intellij-lombok.svg)

Отдельно проверьте созданные конструкторы и getter при компиляции main и test. Исправляйте распознавание IDE после успешных тестов Wrapper.

## Настройте компиляцию Gradle

Добавьте этот блок в существующий `build.gradle`, не дублируя уже имеющиеся объявления.

```groovy
dependencies {
    compileOnly 'org.projectlombok:lombok'
    annotationProcessor 'org.projectlombok:lombok'
    testCompileOnly 'org.projectlombok:lombok'
    testAnnotationProcessor 'org.projectlombok:lombok'
}
```

[Официальная настройка Gradle](https://projectlombok.org/setup/gradle) разделяет зависимости компиляции и процессоры main и test. Два тестовых объявления нужны лишь при использовании аннотаций Lombok в самих тестовых исходниках. Тесты ниже также проверяют этот путь.

Объявления без версий работают, потому что проект применяет Boot plugin и `io.spring.dependency-management`, который [импортирует BOM Boot](https://docs.spring.io/spring-boot/4.1/gradle-plugin/managing-dependencies.html). В обычном Gradle-проекте задайте одну совместимую явную версию во всех нужных объявлениях либо отдельно настройте управление зависимостями этих конфигураций.

## Используйте созданные конструктор и getter

Добавьте `Greeting`, замените существующий контроллер этой версией, сохраните HTTP-тесты и добавьте тестовый класс Lombok.

### `src/main/java/example/demo/Greeting.java`

```java
package example.demo;

import lombok.Getter;
import lombok.RequiredArgsConstructor;

@Getter
@RequiredArgsConstructor
public class Greeting {
    private final String message;
}
```

### `src/main/java/example/demo/GreetingController.java`

```java
package example.demo;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class GreetingController {
    @GetMapping("/greeting")
    public Greeting greeting() {
        return new Greeting("Hello, Gradle");
    }
}
```

### `src/test/java/example/demo/LombokGenerationTest.java`

```java
package example.demo;

import lombok.Getter;
import lombok.RequiredArgsConstructor;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class LombokGenerationTest {
    @Getter
    @RequiredArgsConstructor
    static class Expected {
        private final String message;
    }

    @Test
    void mainSourceConstructorAndGetterAreGenerated() {
        assertEquals("Hello, Gradle", new Greeting("Hello, Gradle").getMessage());
    }

    @Test
    void testSourceConstructorAndGetterAreGenerated() {
        assertEquals("test fixture", new Expected("test fixture").getMessage());
    }
}
```

```sh
./gradlew clean test bootJar
./gradlew dependencyInsight --configuration annotationProcessor --dependency lombok
```

Теперь тестов пять: один контекстный, два HTTP и два генерации Lombok. Они вызывают созданные конструкторы и getter в основных и тестовых исходниках. `/greeting` должен продолжать возвращать тот же JSON, проверяя и сериализацию через созданный getter.

Поскольку Lombok имеет `compileOnly`, исполняемый JAR примера не включает его как runtime-библиотеку. Установка одного плагина IDE не обеспечивает успешную компиляцию Gradle. Для использования уже скомпилированного getter здесь не нужна runtime-зависимость Lombok `implementation`.

## Когда ошибки показывает только IDE

Если тесты Wrapper проходят, перезагрузите Gradle-проект. [Документация JetBrains](https://www.jetbrains.com/help/idea/annotation-processors-support.html) указывает, что импорт процессоров из файлов сборки автоматически включает обработку аннотаций. Ручное переключение флажка не является обязательным универсальным шагом.

Затем проверьте поддержку Lombok и активацию плагина для своей версии IDE по [руководству Lombok для IntelliJ](https://projectlombok.org/setup/intellij). Не обобщайте, что одной редакции всегда нужна ручная установка, а другая всегда включает плагин. Также выясните, использует IDE собственный компилятор или делегирует сборку Gradle.

Если Gradle тоже падает из-за отсутствующих членов, проверьте наличие `compileOnly` без `annotationProcessor`. Если падают только тесты, изучите две тестовые конфигурации. Проверка воспроизведения подтверждает ошибку компиляции при отдельном удалении основного или тестового процессора, затем восстанавливает их и снова проверяет все пять тестов. Работа с интерфейсом IDE этими проверками не охвачена.
