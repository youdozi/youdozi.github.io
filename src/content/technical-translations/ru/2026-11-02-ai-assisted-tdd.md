---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ru",
  "translationKey": "2026-11-02-ai-assisted-tdd",
  "routeSlug": "2026-11-02-ai-assisted-tdd",
  "kind": "post",
  "title": "TDD с помощью AI: проверка Red, Green и Refactor на Java",
  "description": "Объедините AI и TDD: тесты из требований, ожидаемые падения, минимальные реализации и рефакторинг. Примеры Java и JUnit выявляют ослабление тестов и граничные регрессии.",
  "categories": [
    "architecture"
  ],
  "tags": [
    "ai-agent",
    "tdd",
    "java",
    "junit",
    "testing",
    "refactoring"
  ],
  "sourcePath": "src/content/posts/en/2026-11-02-ai-assisted-tdd.md",
  "sourceSha256": "bfc69c72419b9b2b5ce2693c4111b12dd8f935ed3d1115dd350b837bed13bf80",
  "draftSha256": "d71ce33877ee364c023dbd5cb47f1a3b1fad207ab3f11b0060bd603c11f32527",
  "manifestPath": ".pipeline/technical-translations/batch-132/manifest.json",
  "manifestSha256": "9061c67686c9ea3bd8d21799f4c265ee716fee50940f1b6fc38c28a67de01dee",
  "publishedAt": "2026-11-02T03:04:44.245Z",
  "updatedAt": "2026-11-02T03:04:44.245Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 132,
    "approvedAt": "2026-11-02T03:04:44.245Z",
    "basis": "User requested completing missing multilingual technical posts, review, verification and deployment, then instructed continuing the next task on 2026-11-02, with standing blog PR merge/publication authorization. Human approval denotes user publication authorization; linguistic review is AI, not human/native review."
  }
}
---

**Объединяя AI с TDD, выводите ожидаемые результаты из требований, наблюдайте падение теста, затем повторяйте небольшие шаги реализации и рефакторинга.** AI может предлагать тесты и реализацию, но они способны успешно пройти проверку, разделяя одно и то же неверное понимание. Проверяйте происхождение каждого ожидания и фактический отчёт тестового исполнителя.

Базовый цикл TDD выбирает следующее поведение из списка тестов и повторяет Red → Green → Refactor. [Объяснение TDD Мартина Фаулера](https://www.martinfowler.com/bliki/TestDrivenDevelopment.html) подчёркивает список тестов, короткие циклы и рефакторинг. Пример Java ниже добавляет AI к процессу без привязки к конкретному инструменту. Промпты — авторские примеры, а не расшифровка работы AI-продукта или измерение продуктивности.

## Определите ожидаемое поведение до показа реализации

Пример — чистая функция, вычисляющая остаток запаса из имеющегося и запрошенного количества. Это иллюстративные требования, а не политика реального сервиса. Функция не обновляет БД, не сохраняет резервирования и не обеспечивает атомарность конкурентных запросов.

| Условие | Ожидаемое поведение |
| --- | --- |
| Запас 10, запрошено 3 | Вернуть 7 |
| Запас 10, запрошено 10 | Вернуть 0 |
| Запрос превышает запас, включая запрос 1 при запасе 0 | `IllegalStateException("insufficient_stock")` |
| Отрицательный запас | `IllegalArgumentException("stock")` |
| Запрошенное количество равно нулю или отрицательно | `IllegalArgumentException("requested")` |
| Оба входных значения недопустимы | Сначала проверить запас |
| Запас `Integer.MAX_VALUE`, запрошено 1 | Вернуть `Integer.MAX_VALUE - 1` |

Эта таблица — оракул тестов. Чтение сгенерированной AI реализации и копирование её результата в утверждение может скопировать и ошибку. Начните с требований и контракта API:

```text
Пока ничего не реализуйте.
Предложите тестовые случаи для StockPolicy.remaining(int stock, int requested).
Свяжите каждый ввод, ожидаемый результат или исключение с правилом таблицы требований.

Не вводите внешнее хранилище или базу данных.
Разделите нормальные, граничные и недопустимые входные данные. В первой итерации
напишите только один тест: запрос 3 при запасе 10 возвращает 7.
Не выдумывайте политики там, где требования неясны.
```

## Свяжите Red, Green и Refactor короткими запусками

![Выбор следующего теста из требований, проверка ожидаемого падения, минимальная реализация для его прохождения, рефакторинг с сохранением тестов и возврат к следующему тесту](/assets/diagrams/technical/ru-2026-11-02-ai-assisted-tdd.svg)

Схема описывает процесс под управлением разработчика, а не внутреннее устройство AI. Наблюдайте сбой нового поведения, затем добавляйте минимальную реализацию. После рефакторинга повторите те же тесты перед выбором следующего случая. Если сбой вызвали загрузка зависимостей или среда исполнения, исправьте эту проблему и повторите тот же этап.

Среда воспроизведения — **JDK 17.0.8.1, Gradle 8.4 и JUnit Jupiter 5.12.2**. Эта фиксированная комбинация документирует использованную среду, а не рекомендует текущие производственные версии. Создайте следующие файлы в пустом каталоге. Первый запуск может загрузить тестовые зависимости из Maven Central; сами тесты не вызывают внешние API или БД. В существующем проекте следуйте его политикам Gradle Wrapper и управления зависимостями.

### `settings.gradle`

```groovy
rootProject.name = 'ai-tdd-stock'
```

### `build.gradle`

```groovy
plugins { id 'java' }
repositories { mavenCentral() }
dependencies {
    testImplementation platform('org.junit:junit-bom:5.12.2')
    testImplementation 'org.junit.jupiter:junit-jupiter'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
java {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
}
test {
    useJUnitPlatform()
    testLogging { events 'passed', 'failed' }
}
```

Аннотация JUnit `@Test`, `assertEquals` и `assertThrows` проверяют возвращаемые значения и исключения. Сохраните объект исключения, чтобы проверить и его сообщение. См. [руководство JUnit 5.12.2](https://docs.junit.org/5.12.2/user-guide/) и [руководство Gradle по JVM-тестам](https://docs.gradle.org/current/userguide/java_testing.html).

### Первый тест: `src/test/java/StockPolicyTest.java`

```java
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class StockPolicyTest {
    @Test
    void reservesPartOfStock() {
        assertEquals(7, StockPolicy.remaining(10, 3));
    }
}
```

### Первый Red: `src/main/java/StockPolicy.java`

Создайте вызываемый API с реализацией, которая пока ничего не вычитает. Запустите тест и убедитесь, что он падает, поскольку ожидал `7`, а получил `10`.

```java
public class StockPolicy {
    public static int remaining(int stock, int requested) {
        return stock;
    }
}
```

Выполните эту команду из корня проекта. На этом этапе ожидаются падение теста и ненулевой код завершения.

```sh
gradle --no-daemon --console=plain clean test
```

Отличайте ошибки загрузки или компиляции от сбоя требуемого поведения. Ожидаемый Red здесь — несовпадение в утверждении `reservesPartOfStock()`. Сломанный исполнитель не доказывает, что поведение проверялось.

### Первый Green: замените тот же `StockPolicy.java`

```java
public class StockPolicy {
    public static int remaining(int stock, int requested) {
        return stock - requested;
    }
}
```

Повторный запуск той же команды успешно проходит первый тест. Реализация ещё не обрабатывает отрицательные входные данные или нехватку запаса. Прохождение первого теста не завершает функцию; добавьте следующее требование.

Можно задать AI следующие границы изменений:

```text
Падающий тест — reservesPartOfStock: expected=7, actual=10.
Измените только StockPolicy.java, чтобы этот тест прошёл.
Не меняйте тесты, ожидаемые значения или настройки сборки.
Не добавляйте незапрошенные БД, интерфейс или слой конфигурации.
Сообщите команду, код завершения и результаты тестов, которые действительно проверили.
```

### Следующий Red: добавьте методы в существующий тестовый класс

Добавьте эти методы **внутри** последней закрывающей фигурной скобки `StockPolicyTest`. В реальном TDD добавляйте по одному случаю и повторяйте цикл. В статье оставшиеся случаи объединены в блок, чтобы файлы для воспроизведения оставались компактными.

```java
    @Test
    void reservesAllStock() {
        assertEquals(0, StockPolicy.remaining(10, 10));
    }

    @Test
    void rejectsInsufficientStock() {
        var error = assertThrows(IllegalStateException.class,
                () -> StockPolicy.remaining(2, 3));
        assertEquals("insufficient_stock", error.getMessage());
    }

    @Test
    void rejectsEmptyStock() {
        var error = assertThrows(IllegalStateException.class,
                () -> StockPolicy.remaining(0, 1));
        assertEquals("insufficient_stock", error.getMessage());
    }

    @Test
    void rejectsNegativeStock() {
        var error = assertThrows(IllegalArgumentException.class,
                () -> StockPolicy.remaining(-1, 1));
        assertEquals("stock", error.getMessage());
    }

    @Test
    void rejectsZeroRequest() {
        var error = assertThrows(IllegalArgumentException.class,
                () -> StockPolicy.remaining(10, 0));
        assertEquals("requested", error.getMessage());
    }

    @Test
    void rejectsNegativeRequest() {
        var error = assertThrows(IllegalArgumentException.class,
                () -> StockPolicy.remaining(10, -1));
        assertEquals("requested", error.getMessage());
    }

    @Test
    void validatesStockBeforeRequest() {
        var error = assertThrows(IllegalArgumentException.class,
                () -> StockPolicy.remaining(-1, 0));
        assertEquals("stock", error.getMessage());
    }

    @Test
    void supportsMaximumStock() {
        assertEquals(Integer.MAX_VALUE - 1,
                StockPolicy.remaining(Integer.MAX_VALUE, 1));
    }
```

Запуск этого дополнительного блока с первой реализацией Green даёт 6 падений из 9 тестов.

### Green для дополнительных случаев: замените `StockPolicy.java`

```java
public class StockPolicy {
    public static int remaining(int stock, int requested) {
        if (stock >= 0) {
            if (requested > 0) {
                if (requested <= stock) {
                    return stock - requested;
                }
                throw new IllegalStateException("insufficient_stock");
            }
            throw new IllegalArgumentException("requested");
        }
        throw new IllegalArgumentException("stock");
    }
}
```

Той же командой убедитесь, что все 9 тестов проходят. Теперь реализация удовлетворяет заданному поведению. Далее упростите вложенные ветви, сохранив тесты.

### Refactor: используйте защитные условия в том же файле

```java
public class StockPolicy {
    public static int remaining(int stock, int requested) {
        if (stock < 0) throw new IllegalArgumentException("stock");
        if (requested <= 0) throw new IllegalArgumentException("requested");
        if (requested > stock) throw new IllegalStateException("insufficient_stock");
        return stock - requested;
    }
}
```

Вложенность уменьшена с сохранением порядка проверок, возвращаемых значений и исключений. На этом этапе не вводите новую политику. Запрашивая рефакторинг у AI, укажите сохраняемое поведение и область исполнения:

```text
Сейчас все 9 тестов проходят.
Замените только вложенные ветви в StockPolicy.java защитными условиями.
Сохраните проверку stock перед проверкой запрошенного количества,
возвращаемые значения, типы исключений, сообщения и существующие тесты.
Запустите тот же полный набор тестов до и после изменения
и сообщите результаты и diff.
```

Каждая версия исходного кода от первого Red до Refactor запускалась отдельно. Следующие результаты прочитаны из XML-отчётов JUnit:

| Этап | Тесты | Падения | Пропущено | Код завершения Gradle |
| --- | ---: | ---: | ---: | ---: |
| Первый Red | 1 | 1 | 0 | 1 |
| Первый Green | 1 | 0 | 0 | 0 |
| Red дополнительных случаев | 9 | 6 | 0 | 1 |
| Green дополнительных случаев | 9 | 0 | 0 | 0 |
| Refactor | 9 | 0 | 0 | 0 |

HTML-отчёт создаётся в `build/reports/tests/test/index.html`; машиночитаемый XML находится в `build/test-results/test/`. Эти результаты проверяют локальную функцию политики. Они не измеряют качество AI-продукта, продуктивность или корректность производственной системы.

## Тесты и реализация могут ошибаться вместе

**Приоритет проверок** при одновременно недопустимых запасе и запросе закреплён тестом `validatesStockBeforeRequest()`. Без этого случая регрессия, меняющая приоритет сообщений исключений, могла бы остаться незамеченной. Вместо простого добавления примеров нормальных данных проверьте, что правила таблицы требований покрыты соответствующими тестами.

Можно также проверить, обнаруживают ли тесты граничные регрессии. Ошибочная замена `requested > stock` на `requested >= stock` в итоговой реализации должна привести к падению `reservesAllStock()`. Замена `requested <= 0` на `requested < 0` должна провалить `rejectsZeroRequest()`. Также была выполнена мутация с обратным порядком проверки входных данных, на которой упал `validatesStockBeforeRequest()`. Все три мутации действительно запускались; это не гарантирует обнаружения любого дефекта.

Для проверки с помощью AI снова предоставьте исходные требования и спросите, какое правило проверяет каждый тест. Другой агент может повторить ту же ошибку, если разделяет те же неверные требования. Разделение ролей и независимое установление ожидаемого поведения — разные вопросы.

```text
Сравните исходную таблицу требований с текущими тестами.
Пока не изменяйте тесты или реализацию.
Определите проверенные и недостающие правила, границы и ненаблюдавшиеся условия.
Проверьте, не скопировал ли какой-либо тест вывод текущей реализации
в качестве ожидаемого результата.
Для предлагаемых изменений сначала свяжите каждое с его правилом и свидетельствами.
```

## Не позволяйте AI ослаблять проверку ради прохождения тестов

Удаление падающего теста, пропуск через `@Disabled`, подгонка ожиданий под ошибочную реализацию или поглощение всех исключений могут дать зелёный результат без выполнения требований. Если требования при рефакторинге не меняются, сохраняйте ожидаемое поведение. Если неверен сам тест, установите политику и свидетельства, затем отделите исправление теста от изменения реализации. [Рекомендации GitHub по проверке кода AI](https://docs.github.com/en/copilot/tutorials/review-ai-generated-code) также советуют искать удалённые или пропущенные тесты и несоответствия целевым требованиям.

Отличайте утверждение AI о прохождении тестов от результатов исполнителя. Проверяйте фактическую команду, код завершения, отчёты JUnit и diff. Ноль выполненных тестов или частичный запуск не означают полного успеха. В CI выполняйте итоговую реализацию и полный набор тестов с обычными критериями успеха. Учебный стенд, проверяющий ожидаемые падения Red, держите отдельно от обычного CI и не добивайтесь успеха CI безусловным игнорированием падающих команд.

Для существующего кода сначала получите тесты, фиксирующие текущее поведение, затем выберите одно поведение для изменения. Эта последовательность и критерии сохранения связаны с [рефакторингом AI-агентом](/en/posts/2026-10-31-ai-agent-refactoring/). Тесты и сборки тоже выполняют код, поэтому ограничивайте рабочие каталоги и учётные данные, как описано в статье [Границы прав AI-агента](/en/posts/2026-11-01-ai-agent-permission-boundaries/).

Для превращения примера в реальное резервирование запасов нужны отдельные интеграционные тесты конкурентных запросов, транзакций, дубликатов запросов и повторов. Прохождение этих 9 тестов отдельной функции не доказывает защиту от продажи сверх запасов.
