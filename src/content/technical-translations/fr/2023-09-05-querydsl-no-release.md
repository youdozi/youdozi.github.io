---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2023-09-05-querydsl-no-release",
  "routeSlug": "2023-09-05-querydsl-no-release",
  "kind": "post",
  "title": "Remplacer Querydsl : vérifier les contrats de requête avant de changer d’outil",
  "description": "Comparer Querydsl et JPA Specifications avec les mêmes données et vérifier les valeurs nulles, les doublons et les types générés avant une migration.",
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
  "draftSha256": "38d550949193a991732a5eed911cbc47f763a4ffd4329724efe871ff724ecfff",
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
Choisissez un outil de requête selon le travail à exprimer et à vérifier. Une interruption des releases peut justifier une enquête, mais ne démontre pas qu’un remplacement préserve le comportement des requêtes d’une application.

L’inquiétude initiale de 2023 précède la [release Querydsl 5.1.0](https://github.com/querydsl/querydsl/releases/tag/QUERYDSL_5_1_0) publiée ensuite. Un tag de release prouve son existence ; évaluez séparément le dépôt, les coordonnées des artefacts et la compatibilité de la branche à adopter. L’exemple ci-dessous fige un environnement de reproduction plutôt que de recommander une version actuelle pour la production.

## Comparer un prédicat représentatif

![Comparer les résultats des requêtes avant de changer d’outil](/assets/diagrams/technical/fr-2023-09-05-querydsl-no-release.svg)

Insérez les cinq mêmes lignes, construisez les deux prédicats et vérifiez des résultats attendus explicites. Les tests couvrent cette entité sur H2. Une décision de migration nécessite également les jointures, projections, paginations et comportements de base de données réellement utilisés par votre application.

[Les Specifications Spring Data JPA](https://docs.spring.io/spring-data/jpa/reference/3.5/jpa/specifications.html) combinent des prédicats Criteria et les exécutent via `JpaSpecificationExecutor`. Pour de simples filtres de repository, cela peut suffire sans remplacer le modèle de persistance JPA.

## Ajouter trois fichiers à l’exemple Querydsl

Partez des cinq fichiers du [projet Jakarta Querydsl complet](/en/posts/2023-09-09-springboot3-querydsl/), notamment `Employee.getName()`. Sa reproduction utilise Java17, Gradle8.4, Boot3.5.7, Querydsl5.1.0 Jakarta et H2. Ajoutez les trois fichiers complets suivants ; ne mélangez pas cette configuration avec les exemples Boot4 distincts du guide.

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

Exécutez depuis la racine du projet avec JDK17 sélectionné :

```sh
gradle --version
gradle --no-daemon clean test
```

Le projet compte maintenant dix tests : les deux contrôles Querydsl d’origine et huit contrôles de comparaison/contrat. Pour les six comparaisons de résultats, chaque implémentation doit correspondre à une liste définie indépendamment ; leur seul accord mutuel ne suffit pas. Répétez `clean test` pour vérifier aussi la régénération des types Q.

| Cas | Résultat attendu |
| --- | --- |
| Nom égal à Alice | Alice deux fois ; les doublons sont conservés |
| Nom absent | Aucune ligne |
| Nom égal à `A_%` | Cette valeur littérale, et non un motif LIKE |
| Alice AND Bob | Aucune ligne |
| Alice OR Bob | Alice, Alice, Bob dans l’ordre des noms |
| Prédicat null explicite | Un nom null |

## Préserver les contrats qui diffèrent

Le `employee.name` généré par Querydsl est un membre Java. Dans cet exemple Specification, `root.get("name")` utilise un attribut sous forme de chaîne : la faute volontaire `missingName` compile donc et échoue lorsque le repository l’exécute. Cela ne signifie pas que les Specifications doivent utiliser des chaînes : le [métamodèle statique JPA](https://docs.spring.io/spring-data/jpa/reference/3.5/jpa/specifications.html) est une autre possibilité.

L’utilitaire `named` de l’exemple refuse explicitement null, tout comme l’appel d’égalité de Querydsl. Utilisez les prédicats distincts `withoutName()`/`isNull()` pour les valeurs nulles. C’est la politique d’entrée de l’exemple ; lors d’une véritable migration, ne transformez pas silencieusement null en filtre absent.

| Outil | Éléments à évaluer |
| --- | --- |
| Querydsl JPA | Types Q générés, formes de requêtes JPA et compatibilité du processeur |
| JPA Specification | Filtres Criteria réutilisables et intégration au repository |
| [jOOQ](https://www.jooq.org/doc/latest/manual/getting-started/use-cases/jooq-as-a-sql-builder-without-codegeneration/) | DSL centrée sur SQL et modélisation du schéma ; la génération est facultative |
| [Jdbi](https://jdbi.org/) | Requêtes JDBC et correspondance des résultats |
| [Doma](https://docs.domaframework.org/en/latest/) | Traitement à la compilation, modèles SQL et API Criteria |

Ces outils interviennent à des couches différentes. Le test ne compare pas jOOQ, Jdbi ou Doma, ne mesure pas les performances et n’établit pas l’équivalence sur la base de production. Avant de changer d’outil, ajoutez vos véritables jointures, tris, paginations, politiques null et cas transactionnels ; vérifiez la base choisie et les licences des artefacts retenus.

Le [guide d’apprentissage Spring Boot](/en/categories/springboot/) relie configuration du projet, contrôles de persistance, tests HTTP et empaquetage. Chaque article consigne ses propres versions de reproduction.
