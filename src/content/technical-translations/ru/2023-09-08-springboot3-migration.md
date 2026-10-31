---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ru",
  "translationKey": "2023-09-08-springboot3-migration",
  "routeSlug": "2023-09-08-springboot3-migration",
  "kind": "post",
  "title": "Миграция на Spring Boot 3: Java 17, Jakarta и этапы проверки",
  "description": "Начните миграцию Spring Boot 2.7 → 3.0 с Java 17, зависимостей Jakarta и runtime-тестов. Разделяйте исторические границы версий и актуальный выбор для производства.",
  "categories": [
    "springboot"
  ],
  "tags": [
    "springboot",
    "springboot3",
    "springboot3 migration"
  ],
  "sourcePath": "src/content/posts/en/2023-09-08-springboot3-migration.md",
  "sourceSha256": "4939fec22f416da9344b529b0e428c91a700920a27c10fdba00bdfd32e8a53a7",
  "draftSha256": "6e3ef9d78edc84ec301911208b5d218a7fc73139c54fde9590b0ebdbe36793b9",
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

Начните миграцию Spring Boot 2.7 → 3.0 с работающего состояния 2.7, затем проверьте требование Java 17, переход пространств имён Java EE на Jakarta и совместимость библиотек и среды выполнения. [Официальное руководство по миграции 3.0](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.0-Migration-Guide) описывает эту последовательность. Успешная компиляция сама по себе не подтверждает правильность отображений БД, авторизации или конфигурации.

Это **руководство по миграции 2.7 → 3.0**, сохраняющее исходную тему 2023 года. Оно не рекомендует развёртывать Boot 3.0 сегодня. Для реального обновления выберите поддерживаемый целевой выпуск и пройдите промежуточные руководства по миграции.

## Порядок обработки

![Порядок проверок миграции Boot 3](/assets/diagrams/technical/ru-2023-09-08-springboot3-migration.svg)

Это предлагаемый в статье порядок проверок миграции. Команды исследуют среду; они не переносят приложение или базу данных автоматически.

## 1. Зафиксируйте работающую основу 2.7

Обновите старое приложение 2.x до последнего выпуска 2.7.x перед сменой основной версии. Сохраните успешный результат тестов и зафиксируйте wrapper, JVM сборки и зависимости. Для проекта Gradle с существующим wrapper начните с:

```sh
java -version
./gradlew --version
./gradlew clean test
./gradlew dependencies --configuration runtimeClasspath
```

Повторите те же проверки после обновления. В многопроектной сборке запускайте отчёты зависимостей для модуля приложения, например `./gradlew :app:dependencies --configuration runtimeClasspath`. Имя модуля должно соответствовать проекту.

Полезная исходная проверка охватывает хранение данных, аутентификацию, сериализацию, задания по расписанию и исходящие HTTP-вызовы. Для последней границы [тесты WebClient с локальным MockWebServer](/en/posts/2023-09-19-springboot-test-webclient/) дают воспроизводимую отправную точку.

## 2. Меняйте импорты и зависимости Java EE вместе

Boot 3.0 требует Java 17 и Spring Framework 6. Пакеты Java EE, такие как `javax.persistence` и `javax.servlet`, переходят в `jakarta.persistence` и `jakarta.servlet`. Пакеты Java SE, например `javax.sql` и `javax.crypto`, сохраняют имена.

| Текущее использование | Действие при миграции |
| --- | --- |
| `javax.persistence.Entity` | Используйте `jakarta.persistence.Entity` и совместимые зависимости JPA. |
| `javax.servlet.Filter` | Используйте `jakarta.servlet.Filter` и совместимые зависимости servlet. |
| `javax.sql.DataSource` | Сохраните имя пакета Java SE. |
| `javax.crypto.Cipher` | Сохраните имя пакета Java SE. |

Проверяйте разрешённый граф зависимостей вместе с импортами. Например, `./gradlew dependencyInsight --dependency javax.servlet-api --configuration runtimeClasspath` помогает найти устаревший артефакт servlet. Пустой отчёт не доказывает миграцию всего приложения: изучите остальные реально используемые библиотеки и конфигурации. См. [отчёты зависимостей Gradle](https://docs.gradle.org/current/userguide/viewing_debugging_dependencies.html).

Для Querydsl JPA [согласуйте артефакты JPA и процессора аннотаций](/en/posts/2023-09-09-springboot3-querydsl/) и выберите вариант Jakarta, если он требуется этой линейкой артефактов. Убедитесь, что обработка аннотаций создаёт ожидаемые Q-типы и характерные запросы выполняются. Параметр Gradle `configureEach` управляет настройкой задач; он не превращает несовместимую зависимость Java EE в Jakarta.

## 3. Проверьте переименованные свойства и авторизацию

Для Gradle-проекта под управлением Boot официальное руководство предлагает временный помощник свойств:

```groovy
dependencies {
    runtimeOnly 'org.springframework.boot:spring-boot-properties-migrator'
}
```

Запустите приложение в тестовой среде, прочитайте диагностику запуска и обновите затронутые свойства. После миграции удалите помощник. Он не заменяет изучение изменений конфигурации целевого выпуска.

Boot 3.0 также использует Spring Security 6. Руководство предлагает сначала перейти на Spring Security 5.8 в Boot 2.7, затем на 6.0. Проверьте разрешённые, запрещённые и неаутентифицированные запросы, а также диспетчеризацию error/forward, если servlet-приложение её использует; успешный запуск не является тестом авторизации.

## 4. Рассматривайте виртуальные потоки отдельно

Настройка виртуальных потоков появилась в **Boot 3.2 с JDK 21**, а не в Boot 3.0:

```properties
spring.threads.virtual.enabled=true
```

Это историческая граница версий, а не рекомендация выбирать Boot 3.2 сегодня. Сначала подтвердите работоспособность миграции пространств имён и зависимостей. Затем оцените виртуальные потоки с учётом выбранного выпуска, пулов соединений и предположений о thread-local. Одна настройка не доказывает улучшения производительности. [Объяснение Spring о Boot 3.2](https://spring.io/blog/2023/09/09/all-together-now-spring-boot-3-2-graalvm-native-images-java-21-and-virtual).

Предварительные возможности языка JDK также имеют отдельные ограничения версий. [Пример совместимости String Templates](/en/posts/2023-09-23-jdk-21-string-templates/) показывает, почему флаги preview не являются универсальным исправлением обновления.

<span id="decide-whether-the-application-is-ready"></span>

## Как понять, что миграция готова?

| Проверка | Какие свидетельства собрать |
| --- | --- |
| Сборка и сгенерированный код | Успешная сборка wrapper, ожидаемые Q-типы и разрешённые версии зависимостей. |
| Поведение при выполнении | Успешные проверки хранения данных, аутентификации и характерных HTTP-запросов. |
| Конфигурация | Обновлённые свойства и отсутствие необходимости в помощнике миграции. |
| Развёртывание | Проверки развёртываемого артефакта проходят в представительной среде. |

Команды — это последовательность диагностики вашего проекта, а не результат миграции, выполненной в вашем приложении. Сохраните артефакт и конфигурацию до обновления для отката. Переход на основную версию помогает сопровождению, но безопасность по-прежнему зависит от конкретных развёрнутых версий и конфигурации.
