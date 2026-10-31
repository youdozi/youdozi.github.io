---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ru",
  "translationKey": "2023-09-05-querydsl-no-release",
  "routeSlug": "2023-09-05-querydsl-no-release",
  "kind": "post",
  "title": "Querydsl и JPA Specifications: проверьте запрос до смены инструмента",
  "description": "Сравните предикаты Querydsl и JPA Specification на одних данных H2. Проверьте дубликаты, литералы, AND/OR, null и ошибки строковых атрибутов до смены инструмента.",
  "categories": [
    "springboot"
  ],
  "tags": [
    "querydsl",
    "jpa",
    "specification",
    "spring-data-jpa"
  ],
  "sourcePath": "src/content/posts/en/2023-09-05-querydsl-no-release.md",
  "sourceSha256": "23fe3b60bb4735a72a59a7bcc0dfabd76d68df0af84bdd636d79f15699cfc798",
  "draftSha256": "d8a7f41338ae0e8e63209381aefe395f14806b983c97cc0fdd58b488a410cafe",
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

Выбирайте инструмент запросов по тому, что нужно выразить и проверить. Пауза между выпусками может стать поводом для исследования, но не доказывает, что замена сохранит поведение запросов приложения.

Исходная проблема 2023 года возникла до последующего [выпуска Querydsl 5.1.0](https://github.com/querydsl/querydsl/releases/tag/QUERYDSL_5_1_0). Тег подтверждает существование выпуска; отдельно оцените репозиторий, координаты артефактов и совместимость ветки, которую собираетесь использовать. Пример ниже закрепляет среду воспроизведения, а не рекомендует актуальную производственную версию.

## Сравните характерный предикат

![Сравнение результатов запросов до смены инструмента](/assets/diagrams/technical/ru-2023-09-05-querydsl-no-release.svg)

Загрузите одни и те же пять строк, создайте оба предиката и проверьте явно заданные ожидаемые результаты. Тесты охватывают эту сущность в H2. Решение о миграции также требует проверки соединений, проекций, пагинации и поведения БД, реально используемых приложением.

[Spring Data JPA Specifications](https://docs.spring.io/spring-data/jpa/reference/3.5/jpa/specifications.html) объединяют предикаты Criteria и выполняют их через `JpaSpecificationExecutor`. Для простых фильтров репозитория этого может хватить без замены модели хранения JPA.

## Добавьте три файла в пример Querydsl

Начните со всех пяти файлов [полного проекта Jakarta Querydsl](/en/posts/2023-09-09-springboot3-querydsl/), включая `Employee.getName()`. Его среда воспроизведения использует Java17, Gradle8.4, Boot3.5.7, Querydsl5.1.0 Jakarta и H2. Добавьте следующие три полных файла; не смешивайте эту конфигурацию с отдельными примерами Boot4 из руководства.

### `src/main/java/example/EmployeeRepository.java`

```java
package example;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;

public interface EmployeeRepository extends JpaRepository<Employee, Long>,
        JpaSpecificationExecutor<Employee> {}
```

### `src/main/java/example/EmployeeSpecs.java`

```java
package example;

import org.springframework.data.jpa.domain.Specification;

public final class EmployeeSpecs {
    private EmployeeSpecs() {}

    public static Specification<Employee> named(String name) {
        if (name == null) throw new IllegalArgumentException("Use withoutName for null");
        return (root, query, builder) -> builder.equal(root.get("name"), name);
    }

    public static Specification<Employee> withoutName() {
        return (root, query, builder) -> builder.isNull(root.get("name"));
    }
}
```

### `src/test/java/example/QueryStrategyTest.java`

```java
package example;

import java.util.Arrays;
import java.util.List;
import com.querydsl.core.types.Predicate;
import com.querydsl.jpa.impl.JPAQueryFactory;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.boot.test.autoconfigure.orm.jpa.TestEntityManager;
import org.springframework.dao.InvalidDataAccessApiUsageException;
import org.springframework.data.domain.Sort;
import org.springframework.data.jpa.domain.Specification;

import static org.assertj.core.api.Assertions.*;

@DataJpaTest
class QueryStrategyTest {
    @Autowired TestEntityManager entityManager;
    @Autowired EmployeeRepository employees;
    final QEmployee employee = QEmployee.employee;

    @BeforeEach
    void seed() {
        for (String name : Arrays.asList("Alice", "Bob", "Alice", "A_%", null)) {
            entityManager.persist(new Employee(name));
        }
        entityManager.flush();
    }

    void equivalent(Predicate predicate, Specification<Employee> specification,
                    List<String> expected) {
        var querydsl = new JPAQueryFactory(entityManager.getEntityManager())
                .select(employee.name).from(employee).where(predicate)
                .orderBy(employee.name.asc()).fetch();
        var criteria = employees.findAll(specification, Sort.by("name"))
                .stream().map(Employee::getName).toList();
        assertThat(querydsl).containsExactlyElementsOf(expected);
        assertThat(criteria).containsExactlyElementsOf(expected);
    }

    @Test
    void exactEqualityPreservesDuplicates() {
        equivalent(employee.name.eq("Alice"), EmployeeSpecs.named("Alice"),
                List.of("Alice", "Alice"));
    }

    @Test
    void missingValueReturnsNoRows() {
        equivalent(employee.name.eq("Missing"), EmployeeSpecs.named("Missing"), List.of());
    }

    @Test
    void wildcardCharactersAreLiteralForEquality() {
        equivalent(employee.name.eq("A_%"), EmployeeSpecs.named("A_%"), List.of("A_%"));
    }

    @Test
    void andCanEliminateAllRows() {
        equivalent(employee.name.eq("Alice").and(employee.name.eq("Bob")),
                EmployeeSpecs.named("Alice").and(EmployeeSpecs.named("Bob")), List.of());
    }

    @Test
    void orKeepsMatchesAndDuplicatesInOrder() {
        equivalent(employee.name.eq("Alice").or(employee.name.eq("Bob")),
                EmployeeSpecs.named("Alice").or(EmployeeSpecs.named("Bob")),
                List.of("Alice", "Alice", "Bob"));
    }

    @Test
    void nullRequiresAnExplicitPredicate() {
        equivalent(employee.name.isNull(), EmployeeSpecs.withoutName(),
                Arrays.asList((String) null));
    }

    @Test
    void stringAttributeTypoFailsAtRuntime() {
        Specification<Employee> typo = (root, query, builder) ->
                builder.equal(root.get("missingName"), "Alice");
        assertThatThrownBy(() -> employees.findAll(typo))
                .isInstanceOf(InvalidDataAccessApiUsageException.class);
    }

    @Test
    void equalityHelpersRejectNull() {
        assertThatThrownBy(() -> employee.name.eq((String) null))
                .isInstanceOf(IllegalArgumentException.class);
        assertThatThrownBy(() -> EmployeeSpecs.named(null))
                .isInstanceOf(IllegalArgumentException.class);
    }
}
```

Выполните из корня проекта с выбранным JDK17:

```sh
gradle --version
gradle --no-daemon clean test
```

Теперь проект содержит десять тестов: два исходных теста Querydsl и восемь проверок сравнения и контрактов. В шести сравнениях результатов обе реализации должны совпасть с независимо заданным списком; одного совпадения друг с другом недостаточно. Повторите `clean test`, чтобы также проверить повторную генерацию Q-типов.

| Случай | Ожидаемый результат |
| --- | --- |
| Имя равно Alice | Alice дважды; дубликаты сохраняются |
| Отсутствующее имя | Нет строк |
| Имя равно `A_%` | Это буквальное значение, а не шаблон LIKE |
| Alice AND Bob | Нет строк |
| Alice OR Bob | Alice, Alice, Bob в порядке имён |
| Явный предикат null | Одно имя null |

## Сохраните различающиеся контракты

Сгенерированный Querydsl `employee.name` — член Java. В этом примере Specification выражение `root.get("name")` использует строковый атрибут, поэтому намеренная опечатка `missingName` компилируется, но вызывает ошибку при выполнении репозиторием. Это не означает, что Specifications обязаны использовать строки: другой вариант — [статическая метамодель JPA](https://docs.spring.io/spring-data/jpa/reference/3.5/jpa/specifications.html).

Вспомогательный метод `named` в примере явно отклоняет null; вызов равенства Querydsl тоже его отклоняет. Для null используйте отдельные предикаты `withoutName()`/`isNull()`. Это политика входных данных примера; при реальной миграции не превращайте null в отсутствующий фильтр незаметно.

| Инструмент | Что оценивать |
| --- | --- |
| Querydsl JPA | Сгенерированные Q-типы, формы запросов JPA и совместимость процессора |
| JPA Specification | Повторно используемые фильтры Criteria и интеграция репозитория |
| [jOOQ](https://www.jooq.org/doc/latest/manual/getting-started/use-cases/jooq-as-a-sql-builder-without-codegeneration/) | SQL-ориентированный DSL и моделирование схемы; генерация необязательна |
| [Jdbi](https://jdbi.org/) | Запросы JDBC и отображение результатов |
| [Doma](https://docs.domaframework.org/en/latest/) | Обработка при компиляции, шаблоны SQL и Criteria API |

Эти инструменты работают на разных уровнях. Тест не сравнивает jOOQ, Jdbi и Doma, не измеряет производительность и не устанавливает эквивалентность производственной БД. До смены инструмента добавьте реальные соединения, сортировку, пагинацию, политику null и транзакционные случаи; проверьте выбранную БД и условия лицензий нужных артефактов.

[Руководство по изучению Spring Boot](/en/categories/springboot/) связывает настройку проекта, проверки хранения, HTTP-тестирование и упаковку. Каждая статья фиксирует собственные версии воспроизведения.
