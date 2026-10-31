---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2023-09-09-springboot3-querydsl",
  "routeSlug": "2023-09-09-springboot3-querydsl",
  "kind": "post",
  "title": "Querydsl-Q-Typen mit Spring Boot 3 und Jakarta erzeugen",
  "description": "Querydsl-JPA- und APT-Artefakte auf Jakarta abstimmen, Q-Typen generieren und mit H2-Abfragetests prüfen.",
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
  "draftSha256": "9ca879b988d4b75e463c71d47a788b7235b6cbe89cf942c42d0446ac9d20b447",
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
Um Querydsl-JPA-Q-Typen unter Spring Boot 3 zu erzeugen, stimmen Sie Versionen und `jakarta`-Classifier von `querydsl-jpa` und `querydsl-apt` aufeinander ab, konfigurieren die Annotation-Verarbeitung und prüfen anschließend einen sauberen Build sowie einen Datenbankabfragetest. Die [Versionshinweise zu 5.0](https://github.com/querydsl/querydsl/releases/tag/QUERYDSL_5_0_0) dokumentieren die Jakarta-Classifier-Unterstützung. Mit Gradles Standardpfaden für generierte Quellen vermeiden Sie, dass Haupt- und Testkompilierung in dasselbe Verzeichnis schreiben.

Dieser Leitfaden erweitert das ursprüngliche koreanische Beispiel aus 2023 zu einer ausführbaren Konfiguration. Die folgenden Versionen fixieren die Reproduktionsumgebung; sie sind keine Empfehlung aktueller Produktionsabhängigkeiten.

## Verarbeitungsablauf

![Q-Typen erzeugen und Abfrage ausführen](/assets/diagrams/technical/de-2023-09-09-springboot3-querydsl.svg)

Der Prozessor erzeugt QEmployee während der Hauptkompilierung. Der H2-Test führt anschließend eine Abfrage mit diesen generierten Typen aus.

## Reproduktionsumgebung und vollständige Gradle-Einrichtung

| Komponente | Reproduktionsversion |
| --- | --- |
| JDK / Gradle | 17.0.8.1 / 8.4 |
| Spring Boot BOM | 3.5.7 |
| Querydsl JPA / APT | 5.1.0, beide mit dem `jakarta`-Classifier |
| Hibernate / H2 | 6.6.33.Final / 2.3.232, durch die BOM verwaltet |

Erstellen Sie diese fünf Dateien in einem neuen Verzeichnis. Dieses Testprojekt verwendet das Java-Plugin und die Boot-BOM; das Boot-Gradle-Plugin benötigt es nicht. Ergänzen Sie in einer bestehenden Boot-Anwendung nur die benötigten Abhängigkeiten neben der gewählten Abhängigkeitsverwaltung.

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

Gradle löst `annotationProcessor` getrennt von den normalen Kompilier- und Laufzeitklassenpfaden auf. Das Beispiel wendet die BOM daher auch auf die Prozessorkonfiguration an und stellt die Jakarta Persistence- und Annotation-APIs ausdrücklich bereit. Eine Abhängigkeit unter `implementation` steht dem Prozessor nicht automatisch zur Verfügung. Siehe die [Dokumentation des Gradle-Java-Plugins](https://docs.gradle.org/current/userguide/java_plugin.html).

## Anwendung und Entität erstellen

Über die Anwendungsklasse findet der JPA-Test seine Boot-Konfiguration. Für den Test muss kein separater Serverprozess gestartet werden.

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

`Employee` verwendet `jakarta.persistence`. Schreiben Sie `QEmployee` nicht selbst: Der Annotation-Prozessor erzeugt den im folgenden Test referenzierten Typ.

## Über den generierten Q-Typ abfragen

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

`@DataJpaTest` verwendet H2 aus dem Klassenpfad dieses Beispiels. Jeder Test läuft in einer Transaktion, die danach zurückgerollt wird. Nach dem Einfügen der Daten mit `persistAndFlush` ermöglicht das generierte `QEmployee` zwei Prüfungen: eine exakte Namensübereinstimmung und eine Abfrage ohne Ergebniszeilen. Siehe [Spring Boots Leitfaden zu JPA-Tests](https://docs.spring.io/spring-boot/3.5/reference/testing/spring-boot-applications.html#testing.spring-boot-applications.autoconfigured-spring-data-jpa-tests).

Diese Tests prüfen diese Entität und Abfrage auf H2. Sie prüfen weder SQL-Dialekt, Sortierregeln, Sperren noch Migrationsverhalten Ihrer Produktionsdatenbank.

## Ausführen und generierte Dateien prüfen

Wählen Sie JDK 17 und verwenden Sie ein installiertes Gradle 8.4. Führen Sie im Projektstamm Folgendes aus:

```sh
java -version
gradle --version
gradle --no-daemon clean test
```

Prüfen Sie diese generierten Artefakte und den Testbericht:

```text
build/generated/sources/annotationProcessor/java/main/example/QEmployee.java
build/classes/java/main/example/QEmployee.class
build/reports/tests/test/index.html
```

Beide Tests bestanden mit dieser Konfiguration. Eine Wiederholung von `clean test` erzeugte den Q-Typ neu und ließ beide Tests erneut bestehen. Verwenden Sie bei einem bestehenden Projekt mit Gradle Wrapper dessen ausgewählte Version über `./gradlew clean test`.

Der generierte Q-Typ dieses Beispiels importiert `javax.annotation.processing.Generated`, eine Java-SE-API aus `java.compiler`. Dieser Import benötigt keinen Jakarta-Ersatz. [Generated-API des JDK 17](https://docs.oracle.com/en/java/javase/17/docs/api/java.compiler/javax/annotation/processing/Generated.html).

<span id="troubleshoot-missing-or-duplicate-q-types"></span>

## Warum fehlen Q-Typen oder werden doppelt erzeugt?

| Symptom | Erste Prüfung |
| --- | --- |
| `QEmployee` wird nicht gefunden | CLI-Ergebnis von `clean compileJava`, Prozessorabhängigkeiten und `jakarta.persistence`-Imports der Entität prüfen. |
| Der Prozessor findet Persistence-APIs nicht | Prüfen, ob die nötigen Jakarta-APIs getrennt vom normalen Klassenpfad auf dem Prozessorpfad liegen. |
| Ein inkompatibler Typ `javax.persistence.EntityManager` erscheint | Übereinstimmende Versionen und Jakarta-Classifier beider Querydsl-Artefakte prüfen. |
| Doppelte Q-Typen oder ein Build, der nur nach clean funktioniert | Manuell geschriebene Q-Quellen und gemeinsame Generierungspfade entfernen; Ausgabekonfiguration für Haupt- und Testquellen prüfen. |
| CLI funktioniert, aber die IDE sieht keine Q-Typen | Gradle-Synchronisierung, delegierte Build-Einstellungen und Annotation-Verarbeitung der IDE prüfen. |

Das Beispiel ergänzt keine benutzerdefinierte Konfiguration von `sourceSets`, `JavaCompile` oder `clean` für generierte Dateien. Falls Sie einen eigenen Pfad benötigen, halten Sie Haupt- und Testausgaben getrennt. `configureEach` steuert die verzögerte Aufgabenkonfiguration; es behebt keine Jakarta-Abhängigkeitsinkompatibilität. [Gradle-Konfigurationsvermeidung](https://docs.gradle.org/current/userguide/lazy_configuration.html).

Für den umgebenden Upgrade-Ablauf siehe den [Spring-Boot-3-Migrationsleitfaden](/en/posts/2023-09-08-springboot3-migration/). Für ausgehende HTTP-Grenzen verwenden Sie die [WebClient- und MockWebServer-Tests](/en/posts/2023-09-19-springboot-test-webclient/).

## Vor einem Wechsel der Abfragewerkzeuge vergleichen

Die vollständige Employee-Klasse enthält einen Getter, damit sich Repository-Ergebnisse anhand der Namen vergleichen lassen. Ergänzen Sie die drei Dateien aus dem [Vergleich von Querydsl und Specification](/en/posts/2023-09-05-querydsl-no-release/), um acht weitere Prüfungen derselben Entität auszuführen. Die beiden ursprünglichen Tests oben bleiben Teil dieses Projekts mit zehn Tests. Verglichen werden ausgewählte H2-Prädikate, nicht das gesamte Datenbankverhalten. Der [Spring-Boot-Leitfaden](/en/categories/springboot/) verbindet die umgebenden Einrichtungs- und Testschritte.
