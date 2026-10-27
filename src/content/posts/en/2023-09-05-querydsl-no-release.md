---
language: en
translationKey: 2023-09-05-querydsl-no-release
routeSlug: 2023-09-05-querydsl-no-release
kind: post
publishedAt: 2026-10-27T06:13:10.631Z
categories:
  - springboot
tags:
  - querydsl
  - jpa
  - specification
  - spring-data-jpa
title: "Querydsl and JPA Specifications: Test a Query Before Switching"
description: Compare Querydsl and JPA Specification predicates on the same H2
  data. Check duplicates, literals, AND/OR, null policy, and string attribute
  failures before changing tools.
updatedAt: 2026-10-27T06:13:10.631Z
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Primary contracts checked; paired Querydsl/Specification project
  compiled and executed on H2. Comparison scope and version constraints stated.
reviewSources:
  - https://github.com/querydsl/querydsl/releases/tag/QUERYDSL_5_1_0
  - https://docs.spring.io/spring-data/jpa/reference/3.5/jpa/specifications.html
  - https://www.jooq.org/doc/latest/manual/getting-started/use-cases/jooq-as-a-sql-builder-without-codegeneration/
  - https://jdbi.org/
  - https://docs.domaframework.org/en/latest/
---
Choose a query tool by the work you need to express and verify. A release gap can prompt investigation, but it does not establish that a replacement preserves an application's query behavior.

The original 2023 concern predates the later [Querydsl 5.1.0 release](https://github.com/querydsl/querydsl/releases/tag/QUERYDSL_5_1_0). A release tag proves that release exists; assess the repository, artifact coordinates and compatibility of the line you intend to adopt separately. The example below pins one reproduction environment rather than recommending a current production version.

## Compare a representative predicate

![Compare query results before changing tools](/assets/diagrams/2023-09-05-querydsl-no-release-en.svg)

Seed the same five rows, build both predicates and check explicit expected results. The tests cover this entity on H2. A migration decision also needs the joins, projections, pagination and database behavior your application actually uses.

[Spring Data JPA Specifications](https://docs.spring.io/spring-data/jpa/reference/3.5/jpa/specifications.html) combine Criteria predicates and run them through `JpaSpecificationExecutor`. For simple repository filters, that can be sufficient without replacing the JPA persistence model.

## Add three files to the Querydsl example

Start with all five files from the [complete Jakarta Querydsl project](/en/posts/2023-09-09-springboot3-querydsl/), including `Employee.getName()`. Its reproduction uses Java17, Gradle8.4, Boot3.5.7, Querydsl5.1.0 Jakarta and H2. Add the following three complete files; do not mix this configuration with the separate Boot4 examples in the guide.

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

Run from the project root with JDK17 selected:

```sh
gradle --version
gradle --no-daemon clean test
```

The project now has ten tests: the original two Querydsl checks and eight comparison/contract checks. For the six result comparisons, both implementations must match an independently specified list; agreeing with each other alone is insufficient. Repeat `clean test` to check that Q types regenerate too.

| Case | Expected result |
| --- | --- |
| Name equals Alice | Alice twice; duplicates remain |
| Missing name | No rows |
| Name equals `A_%` | That literal value, not a LIKE pattern |
| Alice AND Bob | No rows |
| Alice OR Bob | Alice, Alice, Bob in name order |
| Explicit null predicate | One null name |

## Preserve the contracts that differ

Querydsl's generated `employee.name` is a Java member. In this Specification example, `root.get("name")` uses a string attribute, so the deliberate `missingName` typo compiles and fails when the repository executes it. This does not mean Specifications must use strings: the [JPA static metamodel](https://docs.spring.io/spring-data/jpa/reference/3.5/jpa/specifications.html) is another option.

The example's `named` helper rejects null explicitly, and Querydsl's equality call rejects it too. Use the separate `withoutName()`/`isNull()` predicates for null values. That is the example's input policy; do not silently change null into an absent filter during a real migration.

| Tool | What to evaluate |
| --- | --- |
| Querydsl JPA | Generated Q types, JPA query shapes and processor compatibility |
| JPA Specification | Reusable Criteria filters and repository integration |
| [jOOQ](https://www.jooq.org/doc/latest/manual/getting-started/use-cases/jooq-as-a-sql-builder-without-codegeneration/) | SQL-centric DSL and schema modelling; generation is optional |
| [Jdbi](https://jdbi.org/) | JDBC queries and result mapping |
| [Doma](https://docs.domaframework.org/en/latest/) | Compile-time processing, SQL templates and Criteria APIs |

These tools occupy different layers. The test does not compare jOOQ, Jdbi or Doma, benchmark performance, or establish production-database equivalence. Before changing tools, add your actual joins, ordering, pagination, null policy and transaction cases; check the selected database and license terms for the chosen artifacts.

The [Spring Boot learning guide](/en/categories/springboot/) connects project setup, persistence checks, HTTP testing and packaging. Each article records its own reproduction versions.
