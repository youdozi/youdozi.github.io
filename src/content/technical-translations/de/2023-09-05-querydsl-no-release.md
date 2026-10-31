---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2023-09-05-querydsl-no-release",
  "routeSlug": "2023-09-05-querydsl-no-release",
  "kind": "post",
  "title": "Querydsl ersetzen: Abfrageverträge vor dem Werkzeugwechsel prüfen",
  "description": "Querydsl und JPA Specifications mit denselben Testdaten vergleichen und Nullwerte, Duplikate und generierte Typen vor einer Migration prüfen.",
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
  "draftSha256": "a7da6e03595de11e8feed315708ee1ac432e6c21b01a10cf1acf0b0a8aba7813",
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
Wählen Sie ein Abfragewerkzeug danach aus, welche Aufgaben Sie ausdrücken und prüfen müssen. Eine Veröffentlichungspause kann Anlass zur Untersuchung geben, belegt aber nicht, dass ein Ersatz das Abfrageverhalten einer Anwendung bewahrt.

Die ursprüngliche Sorge aus 2023 lag vor der späteren [Veröffentlichung von Querydsl 5.1.0](https://github.com/querydsl/querydsl/releases/tag/QUERYDSL_5_1_0). Ein Release-Tag belegt die Existenz dieser Veröffentlichung; bewerten Sie Repository, Artefaktkoordinaten und Kompatibilität der gewünschten Linie separat. Das folgende Beispiel fixiert eine Reproduktionsumgebung, statt eine aktuelle Produktionsversion zu empfehlen.

## Ein repräsentatives Prädikat vergleichen

![Abfrageergebnisse vor dem Werkzeugwechsel vergleichen](/assets/diagrams/technical/de-2023-09-05-querydsl-no-release.svg)

Legen Sie dieselben fünf Zeilen an, erstellen Sie beide Prädikate und prüfen Sie ausdrückliche erwartete Ergebnisse. Die Tests decken diese Entität auf H2 ab. Eine Migrationsentscheidung erfordert auch die Joins, Projektionen, Paginierung und das Datenbankverhalten Ihrer tatsächlichen Anwendung.

[Spring Data JPA Specifications](https://docs.spring.io/spring-data/jpa/reference/3.5/jpa/specifications.html) kombinieren Criteria-Prädikate und führen sie über `JpaSpecificationExecutor` aus. Für einfache Repository-Filter kann das ausreichen, ohne das JPA-Persistenzmodell zu ersetzen.

## Drei Dateien zum Querydsl-Beispiel hinzufügen

Beginnen Sie mit allen fünf Dateien aus dem [vollständigen Jakarta-Querydsl-Projekt](/en/posts/2023-09-09-springboot3-querydsl/), einschließlich `Employee.getName()`. Seine Reproduktion verwendet Java17, Gradle8.4, Boot3.5.7, Querydsl5.1.0 Jakarta und H2. Fügen Sie die folgenden drei vollständigen Dateien hinzu; vermischen Sie diese Konfiguration nicht mit den separaten Boot4-Beispielen im Leitfaden.

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

Führen Sie dies im Projektstamm mit ausgewähltem JDK17 aus:

```sh
gradle --version
gradle --no-daemon clean test
```

Das Projekt hat nun zehn Tests: die ursprünglichen zwei Querydsl-Prüfungen und acht Vergleichs-/Vertragsprüfungen. Bei den sechs Ergebnisvergleichen müssen beide Implementierungen einer unabhängig vorgegebenen Liste entsprechen; bloße Übereinstimmung miteinander reicht nicht. Wiederholen Sie `clean test`, um auch die Neuerzeugung der Q-Typen zu prüfen.

| Fall | Erwartetes Ergebnis |
| --- | --- |
| Name ist gleich Alice | Alice zweimal; Duplikate bleiben erhalten |
| Nicht vorhandener Name | Keine Zeilen |
| Name ist gleich `A_%` | Dieser wörtliche Wert, kein LIKE-Muster |
| Alice AND Bob | Keine Zeilen |
| Alice OR Bob | Alice, Alice, Bob nach Namen sortiert |
| Explizites Null-Prädikat | Ein Null-Name |

## Unterschiedliche Verträge bewahren

Das generierte `employee.name` von Querydsl ist ein Java-Member. In diesem Specification-Beispiel verwendet `root.get("name")` ein String-Attribut; daher kompiliert der absichtliche Tippfehler `missingName` und scheitert erst bei der Ausführung durch das Repository. Specifications müssen deshalb nicht zwangsläufig Strings verwenden: Das [statische JPA-Metamodell](https://docs.spring.io/spring-data/jpa/reference/3.5/jpa/specifications.html) ist eine weitere Möglichkeit.

Der Hilfsbaustein `named` dieses Beispiels lehnt null ausdrücklich ab; Querydsls Gleichheitsaufruf ebenfalls. Verwenden Sie für Nullwerte die separaten Prädikate `withoutName()`/`isNull()`. Dies ist die Eingaberichtlinie des Beispiels; ändern Sie null bei einer realen Migration nicht stillschweigend in einen fehlenden Filter.

| Werkzeug | Was zu bewerten ist |
| --- | --- |
| Querydsl JPA | Generierte Q-Typen, JPA-Abfrageformen und Prozessorkompatibilität |
| JPA Specification | Wiederverwendbare Criteria-Filter und Repository-Integration |
| [jOOQ](https://www.jooq.org/doc/latest/manual/getting-started/use-cases/jooq-as-a-sql-builder-without-codegeneration/) | SQL-orientierte DSL und Schemamodellierung; Generierung ist optional |
| [Jdbi](https://jdbi.org/) | JDBC-Abfragen und Ergebniszuordnung |
| [Doma](https://docs.domaframework.org/en/latest/) | Verarbeitung zur Kompilierzeit, SQL-Vorlagen und Criteria-APIs |

Diese Werkzeuge liegen auf unterschiedlichen Ebenen. Der Test vergleicht weder jOOQ, Jdbi oder Doma noch misst er Leistung oder belegt Gleichwertigkeit auf der Produktionsdatenbank. Ergänzen Sie vor einem Wechsel Ihre tatsächlichen Joins, Sortierungen, Paginierung, Null-Richtlinien und Transaktionsfälle; prüfen Sie die ausgewählte Datenbank und die Lizenzbedingungen der gewählten Artefakte.

Der [Spring-Boot-Lernleitfaden](/en/categories/springboot/) verbindet Projekteinrichtung, Persistenzprüfungen, HTTP-Tests und Paketierung. Jeder Artikel dokumentiert seine eigenen Reproduktionsversionen.
