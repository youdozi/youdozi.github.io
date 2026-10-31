---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ru",
  "translationKey": "2023-09-09-springboot3-querydsl",
  "routeSlug": "2023-09-09-springboot3-querydsl",
  "kind": "post",
  "title": "Spring Boot 3 и Querydsl: настройка Jakarta и генерация Q-типов",
  "description": "Генерируйте Q-типы Querydsl на Spring Boot 3 с согласованными зависимостями Jakarta и обработкой аннотаций, затем проверьте чистую сборку и запросы H2.",
  "categories": [
    "springboot"
  ],
  "tags": [
    "springboot",
    "springboot3",
    "querydsl"
  ],
  "sourcePath": "src/content/posts/en/2023-09-09-springboot3-querydsl.md",
  "sourceSha256": "17f0353d5a048f80291207543b7abbb29e1d987ab0435009b82a4e1c16a7d953",
  "draftSha256": "ab30c62eeaefd138a082150e95a40e5c020b4c4d3e25f90dcfa47894611c4227",
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

Для генерации Q-типов Querydsl JPA в Spring Boot 3 согласуйте версии и классификаторы `jakarta` у `querydsl-jpa` и `querydsl-apt`, настройте обработку аннотаций, затем проверьте чистую сборку и тест запроса к БД. [Примечания к выпуску 5.0](https://github.com/querydsl/querydsl/releases/tag/QUERYDSL_5_0_0) Querydsl описывают поддержку классификатора Jakarta. Стандартные пути Gradle для сгенерированного кода позволяют избежать записи основной и тестовой компиляции в один каталог.

Руководство развивает исходный корейский пример 2023 года до исполняемой конфигурации. Версии ниже закрепляют среду воспроизведения; это не рекомендации актуальных производственных зависимостей.

## Порядок обработки

![Генерация Q-типов и выполнение запроса](/assets/diagrams/technical/ru-2023-09-09-springboot3-querydsl.svg)

Процессор создаёт QEmployee при основной компиляции. Затем тест H2 выполняет запрос с этими сгенерированными типами.

## Среда воспроизведения и полная настройка Gradle

| Компонент | Версия воспроизведения |
| --- | --- |
| JDK / Gradle | 17.0.8.1 / 8.4 |
| Spring Boot BOM | 3.5.7 |
| Querydsl JPA / APT | 5.1.0, оба с классификатором `jakarta` |
| Hibernate / H2 | 6.6.33.Final / 2.3.232, управляются BOM |

Создайте эти пять файлов в новом каталоге. Тестовый проект использует Java plugin и Boot BOM; Boot Gradle plugin ему не нужен. В существующее приложение Boot добавляйте только необходимые зависимости рядом с выбранным управлением зависимостями.

### `settings.gradle`

```groovy
rootProject.name = 'querydsl-jakarta-example'
```

### `build.gradle`

```groovy
plugins { id 'java' }
repositories { mavenCentral() }
dependencies {
    implementation platform('org.springframework.boot:spring-boot-dependencies:3.5.7')
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    implementation 'com.querydsl:querydsl-jpa:5.1.0:jakarta'

    annotationProcessor platform('org.springframework.boot:spring-boot-dependencies:3.5.7')
    annotationProcessor 'com.querydsl:querydsl-apt:5.1.0:jakarta'
    annotationProcessor 'jakarta.persistence:jakarta.persistence-api'
    annotationProcessor 'jakarta.annotation:jakarta.annotation-api'

    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testRuntimeOnly 'com.h2database:h2'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
test { useJUnitPlatform() }
```

Gradle разрешает `annotationProcessor` отдельно от обычных classpath компиляции и выполнения. Поэтому пример также применяет BOM к конфигурации процессора и явно предоставляет Jakarta Persistence и Annotation API. Зависимость `implementation` не становится доступной процессору автоматически. См. [документацию Java plugin Gradle](https://docs.gradle.org/current/userguide/java_plugin.html).

## Создайте приложение и сущность

Класс приложения позволяет JPA-тесту обнаружить конфигурацию Boot. Для теста не требуется отдельный серверный процесс.

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

### `src/main/java/example/Employee.java`

```java
package example;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;

@Entity
public class Employee {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;

    public String getName() { return name; }

    protected Employee() {}

    public Employee(String name) {
        this.name = name;
    }
}
```

`Employee` использует `jakarta.persistence`. Не пишите `QEmployee` вручную: процессор аннотаций создаёт тип, на который ссылается тест ниже.

## Запрос через сгенерированный Q-тип

### `src/test/java/example/EmployeeQueryTest.java`

```java
package example;

import com.querydsl.jpa.impl.JPAQueryFactory;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.boot.test.autoconfigure.orm.jpa.TestEntityManager;

import static org.assertj.core.api.Assertions.assertThat;

@DataJpaTest
class EmployeeQueryTest {
    @Autowired
    private TestEntityManager entityManager;

    @Test
    void findsEmployeeByName() {
        entityManager.persistAndFlush(new Employee("Alice"));
        entityManager.persistAndFlush(new Employee("Bob"));
        QEmployee employee = QEmployee.employee;
        var names = new JPAQueryFactory(entityManager.getEntityManager())
            .select(employee.name).from(employee)
            .where(employee.name.eq("Alice")).fetch();
        assertThat(names).containsExactly("Alice");
    }

    @Test
    void returnsNoRowsForMissingName() {
        entityManager.persistAndFlush(new Employee("Alice"));
        QEmployee employee = QEmployee.employee;
        var names = new JPAQueryFactory(entityManager.getEntityManager())
            .select(employee.name).from(employee)
            .where(employee.name.eq("Missing")).fetch();
        assertThat(names).isEmpty();
    }
}
```

`@DataJpaTest` использует H2 из classpath примера. Каждый тест выполняется в транзакции с последующим откатом. После вставки через `persistAndFlush` сгенерированный `QEmployee` обеспечивает две проверки: точное совпадение имени и запрос без строк. См. [руководство по JPA-тестированию Spring Boot](https://docs.spring.io/spring-boot/3.5/reference/testing/spring-boot-applications.html#testing.spring-boot-applications.autoconfigured-spring-data-jpa-tests).

Эти тесты проверяют эту сущность и запрос в H2. Они не проверяют SQL-диалект, правила сравнения строк, блокировки или миграции вашей производственной БД.

## Запуск и проверка сгенерированных файлов

Выберите JDK 17 и установленный Gradle 8.4. Выполните из корня проекта:

```sh
java -version
gradle --version
gradle --no-daemon clean test
```

Проверьте эти сгенерированные артефакты и отчёт тестов:

```text
build/generated/sources/annotationProcessor/java/main/example/QEmployee.java
build/classes/java/main/example/QEmployee.class
build/reports/tests/test/index.html
```

Оба теста прошли с этой конфигурацией. Повторный `clean test` заново создал Q-тип и снова прошёл оба теста. В существующем проекте с Gradle wrapper используйте выбранную им версию через `./gradlew clean test`.

Q-тип в этом примере импортирует `javax.annotation.processing.Generated` — API Java SE из `java.compiler`. Этот импорт не требует замены на Jakarta. [API Generated JDK 17](https://docs.oracle.com/en/java/javase/17/docs/api/java.compiler/javax/annotation/processing/Generated.html).

<span id="troubleshoot-missing-or-duplicate-q-types"></span>

## Почему Q-типы отсутствуют или генерируются дважды?

| Симптом | Что проверить сначала |
| --- | --- |
| Не удаётся найти `QEmployee` | Проверьте результат CLI `clean compileJava`, зависимости процессора и импорты `jakarta.persistence` сущности. |
| Процессор не находит Persistence API | Проверьте необходимые Jakarta API в пути процессора, отдельно от обычного classpath. |
| Появляется несовместимый тип `javax.persistence.EntityManager` | Проверьте совпадение версий и классификаторы Jakarta обоих артефактов Querydsl. |
| Дубликаты Q-типов или сборка работает только после clean | Удалите написанные вручную Q-файлы и общие пути генерации; проверьте настройки вывода main/test. |
| CLI проходит, но IDE не видит Q-типы | Проверьте синхронизацию Gradle, делегирование сборки и обработку аннотаций в IDE. |

Пример не добавляет специальные настройки `sourceSets`, `JavaCompile` и `clean` для сгенерированных файлов. Если нужен собственный путь, разделяйте вывод main и test. `configureEach` управляет отложенной настройкой задач; он не исправляет совместимость зависимостей Jakarta. [Избежание лишней конфигурации Gradle](https://docs.gradle.org/current/userguide/lazy_configuration.html).

Общую последовательность обновления см. в [руководстве по миграции Spring Boot 3](/en/posts/2023-09-08-springboot3-migration/). Для границ исходящего HTTP используйте [тесты WebClient и MockWebServer](/en/posts/2023-09-19-springboot-test-webclient/).

## Сравните инструменты до замены

Полный класс Employee включает getter для сравнения результатов репозитория по именам. Добавьте три файла из [сравнения Querydsl и Specification](/en/posts/2023-09-05-querydsl-no-release/), чтобы выполнить восемь дополнительных проверок той же сущности. Два исходных теста выше остаются частью проекта с десятью тестами. Это сравнение выбранных предикатов H2, а не всего поведения БД. [Руководство Spring Boot](/en/categories/springboot/) связывает остальные шаги настройки и тестирования.
