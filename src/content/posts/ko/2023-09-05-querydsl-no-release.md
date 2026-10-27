---
title: "Querydsl 대안 판단하기: JPA Specification과 같은 조건 실행하기"
language: ko
translationKey: 2023-09-05-querydsl-no-release
routeSlug: 2023-09-05-querydsl-no-release
kind: post
publishedAt: 2023-09-04T15:00:00.000Z
categories:
  - springboot
tags:
  - querydsl
  - springboot3
  - jpa
  - jooq
legacyUrl: /springboot/querydsl-no-release/
legacySource: _posts/spring/querydsl/2023-09-05-querydsl-no-release.markdown
updatedAt: 2026-10-27T06:13:10.631Z
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Primary contracts checked; paired Querydsl/Specification project
  compiled and executed on H2. Comparison scope and version constraints stated.
archiveBodySha256: ed4dd5e11f73c2c88eaf11ddaf2269bceec442dff783e36b7266eb1d5d58764b
reviewSources:
  - https://github.com/querydsl/querydsl/releases/tag/QUERYDSL_5_1_0
  - https://docs.spring.io/spring-data/jpa/reference/3.5/jpa/specifications.html
  - https://www.jooq.org/doc/latest/manual/getting-started/use-cases/jooq-as-a-sql-builder-without-codegeneration/
  - https://jdbi.org/
  - https://docs.domaframework.org/en/latest/
description: 같은 H2 데이터에 Querydsl과 JPA Specification 조건을 실행합니다.
  중복·리터럴·AND/OR·NULL 정책·문자열 속성명 오류를 확인하고 교체 범위를 판단합니다.
---
쿼리 도구는 표현해야 할 요구와 검증할 동작을 기준으로 선택하세요. 릴리스 공백은 확인을 시작할 계기는 되지만, 대체 도구가 애플리케이션의 조회 동작을 보존한다는 근거는 아닙니다.

2023년의 우려 이후 공식 저장소에는 [Querydsl 5.1.0 릴리스](https://github.com/querydsl/querydsl/releases/tag/QUERYDSL_5_1_0)가 있습니다. 릴리스 태그의 존재와 앞으로 선택할 저장소·아티팩트 좌표·호환성은 따로 확인해야 합니다. 아래 버전은 재현 환경이며 현재 운영 버전의 권장값을 뜻하지 않습니다.

## 대표 조건 하나를 같은 데이터로 비교하기

![도구 변경 전에 쿼리 결과를 비교하는 흐름도](/assets/diagrams/2023-09-05-querydsl-no-release-ko.svg)

동일한 행 5개를 넣고 두 조건식을 만든 뒤 명시한 기대 결과를 확인합니다. 테스트 범위는 H2의 이 엔티티입니다. 실제 교체 판단에는 사용하는 조인·프로젝션·페이지네이션·DB 동작도 필요합니다.

[Spring Data JPA Specification](https://docs.spring.io/spring-data/jpa/reference/3.5/jpa/specifications.html)은 Criteria 조건을 조합해 `JpaSpecificationExecutor`로 실행합니다. 단순한 저장소 필터라면 JPA 영속성 모델을 바꾸지 않고 필요한 조회를 표현할 수 있습니다.

## Querydsl 예제에 파일 3개 추가하기

[Jakarta Querydsl 전체 프로젝트](/ko/posts/2023-09-09-springboot3-querydsl/)의 파일 5개와 `Employee.getName()`을 준비합니다. 재현 조합은 Java17·Gradle8.4·Boot3.5.7·Querydsl5.1.0 Jakarta·H2입니다. 아래 전체 파일 3개를 추가하세요. 안내 페이지의 별도 Boot4 예제 설정과 섞지 않습니다.

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

JDK17을 선택하고 프로젝트 루트에서 실행합니다.

```sh
gradle --version
gradle --no-daemon clean test
```

테스트는 기존 Querydsl 2개와 비교·계약 검사 8개로 총 10개입니다. 결과를 비교하는 6개 사례에서는 두 구현이 각자 명시적인 기대 목록과 일치해야 합니다. 두 구현의 결과가 서로 같다는 것만으로 통과하지 않습니다. `clean test`를 반복하면 Q 타입이 다시 생성되는지도 확인할 수 있습니다.

| 조건 | 기대 결과 |
| --- | --- |
| 이름이 Alice | Alice 2개. 중복 유지 |
| 없는 이름 | 결과 없음 |
| 이름이 `A_%` | LIKE 패턴이 아닌 해당 문자열 |
| Alice AND Bob | 결과 없음 |
| Alice OR Bob | 이름 순으로 Alice·Alice·Bob |
| 명시적인 NULL 조건 | 이름이 null인 행 1개 |

## 달라지는 계약도 남기기

Querydsl의 `employee.name`은 생성된 Java 멤버입니다. 이 Specification 예제의 `root.get("name")`은 문자열 속성명이므로 `missingName` 오타도 컴파일되고 저장소 실행 시 실패합니다. Specification이 반드시 문자열을 써야 한다는 뜻은 아닙니다. [JPA 정적 메타모델](https://docs.spring.io/spring-data/jpa/reference/3.5/jpa/specifications.html)도 선택할 수 있습니다.

예제의 `named` 도우미는 null을 명시적으로 거절하며 Querydsl의 동등 비교 호출도 null을 거절합니다. NULL 조회는 별도의 `withoutName()`·`isNull()` 조건을 사용하세요. 이는 예제의 입력 정책입니다. 실제 이관에서 null을 임의로 ‘필터 생략’으로 바꾸지 않습니다.

| 도구 | 확인할 역할 |
| --- | --- |
| Querydsl JPA | 생성 Q 타입·JPA 쿼리 형태·프로세서 호환성 |
| JPA Specification | 재사용할 Criteria 조건·저장소 통합 |
| [jOOQ](https://www.jooq.org/doc/latest/manual/getting-started/use-cases/jooq-as-a-sql-builder-without-codegeneration/) | SQL 중심 DSL·스키마 모델. 코드 생성은 선택 사항 |
| [Jdbi](https://jdbi.org/) | JDBC 쿼리·결과 매핑 |
| [Doma](https://docs.domaframework.org/en/latest/) | 컴파일 시점 처리·SQL 템플릿·Criteria API |

서로 담당하는 계층이 다릅니다. 이 테스트는 jOOQ·Jdbi·Doma 비교나 성능 측정, 운영 DB의 동등성 검증이 아닙니다. 도구를 바꾸기 전 실제 조인·정렬·페이지네이션·NULL 정책·트랜잭션 사례를 추가하고, 선택한 DB와 아티팩트의 라이선스 조건을 확인하세요.

[Spring Boot 학습 안내](/ko/categories/springboot/)에서 프로젝트 생성·영속성 검사·HTTP 테스트·패키징을 이어 읽을 수 있습니다. 각 글의 재현 버전은 해당 글에서 확인합니다.
