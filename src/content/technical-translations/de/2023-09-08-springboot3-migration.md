---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2023-09-08-springboot3-migration",
  "routeSlug": "2023-09-08-springboot3-migration",
  "kind": "post",
  "title": "Spring Boot 2.7 auf 3.0 migrieren: Java, Jakarta und Verhalten prüfen",
  "description": "Eine Boot-Migration mit Java 17, Jakarta-Abhängigkeiten, Konfiguration und Laufzeittests schrittweise prüfen.",
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
  "draftSha256": "66176526db73c5a492900e264a8faa3da56e13725be4cdb27b967b8249ca918e",
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
Beginnen Sie eine Migration von Spring Boot 2.7 auf 3.0 mit einer funktionierenden 2.7-Ausgangsbasis. Prüfen Sie dann die Java-17-Anforderung, die Namespace-Änderungen von Java EE zu Jakarta und die Kompatibilität von Bibliotheken und Laufzeit. Der [offizielle Migrationsleitfaden für 3.0](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.0-Migration-Guide) beschreibt diese Reihenfolge. Erfolgreiches Kompilieren allein belegt weder korrekte Datenbankzuordnungen noch Autorisierung oder Konfiguration.

Dies ist ein **Migrationsleitfaden von 2.7 auf 3.0**, der das ursprüngliche Thema aus 2023 bewahrt. Er empfiehlt nicht, Boot 3.0 heute bereitzustellen. Wählen Sie für ein reales Upgrade eine unterstützte Zielversion und folgen Sie den dazwischenliegenden Migrationsleitfäden.

## Verarbeitungsablauf

![Prüfablauf für die Boot-3-Migration](/assets/diagrams/technical/de-2023-09-08-springboot3-migration.svg)

Dies ist die im Artikel vorgeschlagene Reihenfolge der Migrationsprüfungen. Die Befehle untersuchen die Umgebung; sie migrieren weder eine Anwendung noch eine Datenbank automatisch.

## 1. Eine funktionierende 2.7-Ausgangsbasis herstellen

Aktualisieren Sie eine ältere 2.x-Anwendung zunächst auf die neueste 2.7.x-Version, bevor Sie den Hauptversionswechsel versuchen. Bewahren Sie ein erfolgreiches Testergebnis auf und erfassen Sie Wrapper, Build-JVM und Abhängigkeiten. Beginnen Sie bei einem Gradle-Projekt mit vorhandenem Wrapper mit:

```sh
java -version
./gradlew --version
./gradlew clean test
./gradlew dependencies --configuration runtimeClasspath
```

Führen Sie dieselben Prüfungen nach dem Upgrade aus. Erstellen Sie bei einem Mehrprojekt-Build die Abhängigkeitsberichte für das Anwendungsmodul, etwa mit `./gradlew :app:dependencies --configuration runtimeClasspath`. Der Modulname muss Ihrem Projekt entsprechen.

Eine nützliche Ausgangsbasis prüft Persistenz, Authentifizierung, Serialisierung, geplante Jobs und ausgehende HTTP-Aufrufe. Für die letzte Grenze bieten die [WebClient-Tests mit lokalem MockWebServer](/en/posts/2023-09-19-springboot-test-webclient/) einen reproduzierbaren Ausgangspunkt.

## 2. Java-EE-Imports und Abhängigkeiten gemeinsam ändern

Boot 3.0 benötigt Java 17 und Spring Framework 6. Java-EE-Pakete wie `javax.persistence` und `javax.servlet` wechseln zu `jakarta.persistence` und `jakarta.servlet`. Java-SE-Pakete wie `javax.sql` und `javax.crypto` behalten ihre Namen.

| Bisherige Verwendung | Migrationsmaßnahme |
| --- | --- |
| `javax.persistence.Entity` | `jakarta.persistence.Entity` und kompatible JPA-Abhängigkeiten verwenden. |
| `javax.servlet.Filter` | `jakarta.servlet.Filter` und kompatible Servlet-Abhängigkeiten verwenden. |
| `javax.sql.DataSource` | Den Java-SE-Paketnamen beibehalten. |
| `javax.crypto.Cipher` | Den Java-SE-Paketnamen beibehalten. |

Prüfen Sie neben den Imports auch den aufgelösten Abhängigkeitsgraphen. Beispielsweise hilft `./gradlew dependencyInsight --dependency javax.servlet-api --configuration runtimeClasspath`, ein altes Servlet-Artefakt zu finden. Ein leerer Bericht belegt nicht die Migration der gesamten Anwendung: Prüfen Sie auch die anderen tatsächlich verwendeten Bibliotheken und Konfigurationen. Siehe [Gradles Abhängigkeitsberichte](https://docs.gradle.org/current/userguide/viewing_debugging_dependencies.html).

Für Querydsl JPA müssen Sie [JPA- und Annotation-Processor-Artefakte aufeinander abstimmen](/en/posts/2023-09-09-springboot3-querydsl/) und, soweit die Artefaktlinie dies erfordert, ihre Jakarta-Variante auswählen. Bestätigen Sie, dass die Annotation-Verarbeitung die erwarteten Q-Typen erzeugt und repräsentative Abfragen ausgeführt werden. Gradles `configureEach` steuert die Aufgabenkonfiguration; es kann keine inkompatible Java-EE-Abhängigkeit in eine Jakarta-Abhängigkeit umwandeln.

## 3. Umbenannte Eigenschaften und Autorisierungsverhalten prüfen

Für ein Gradle-Projekt mit Boot-Abhängigkeitsverwaltung bietet der offizielle Migrationsleitfaden vorübergehend diesen Eigenschaftenhelfer an:

```groovy
dependencies {
    runtimeOnly 'org.springframework.boot:spring-boot-properties-migrator'
}
```

Starten Sie die Anwendung in einer Testumgebung, lesen Sie die Startdiagnosen und aktualisieren Sie betroffene Eigenschaften. Entfernen Sie den Helfer nach Abschluss der Migration. Er ersetzt nicht die Lektüre der Konfigurationsänderungen der Zielversion.

Boot 3.0 verwendet außerdem Spring Security 6. Der Migrationsleitfaden empfiehlt einen Übergang über Spring Security 5.8 unter Boot 2.7, bevor der Wechsel auf 6.0 erfolgt. Testen Sie erlaubte, verweigerte und nicht authentifizierte Anfragen sowie Error-/Forward-Dispatches, sofern die Servlet-Anwendung sie nutzt; ein erfolgreicher Start ersetzt keinen Autorisierungstest.

## 4. Virtuelle Threads als separate Änderung behandeln

Die Einstellung für virtuelle Threads wurde in **Boot 3.2 mit JDK 21** eingeführt und ist kein Boot-3.0-Merkmal:

```properties
spring.threads.virtual.enabled=true
```

Dies ist eine historische Versionsgrenze und keine Empfehlung, Boot 3.2 heute zu wählen. Stellen Sie zuerst sicher, dass die Namespace- und Abhängigkeitsmigration funktioniert. Bewerten Sie virtuelle Threads anschließend anhand der gewählten Version, Verbindungspools und Annahmen zu Thread-Locals. Die Einstellung allein belegt keine Leistungssteigerung. [Springs Erläuterung zu Boot 3.2](https://spring.io/blog/2023/09/09/all-together-now-spring-boot-3-2-graalvm-native-images-java-21-and-virtual).

Auch Sprachvorschauen des JDK haben eigene Versionsbeschränkungen. Das [Kompatibilitätsbeispiel zu String Templates](/en/posts/2023-09-23-jdk-21-string-templates/) zeigt, warum Preview-Flags kein allgemeines Mittel zur Upgrade-Reparatur sind.

<span id="decide-whether-the-application-is-ready"></span>

## Woran erkennt man eine abgeschlossene Migration?

| Prüfung | Zu sammelnde Nachweise |
| --- | --- |
| Build und generierter Code | Erfolgreicher Wrapper-Build, erwartete Q-Typen und aufgelöste Abhängigkeitsversionen. |
| Laufzeitverhalten | Erfolgreiche Persistenz-, Authentifizierungs- und repräsentative HTTP-Tests. |
| Konfiguration | Aktualisierte Eigenschaften und kein weiterer Bedarf am Migrationshelfer. |
| Deployment | Das Deployment-Artefakt besteht die Prüfungen in einer repräsentativen Umgebung. |

Die Befehle sind eine Diagnosereihenfolge für Ihr Projekt, nicht das Ergebnis einer Migration Ihrer Anwendung. Halten Sie Artefakt und Konfiguration vor dem Upgrade für ein Rollback bereit. Ein Hauptversionswechsel unterstützt die Wartung; Sicherheit hängt jedoch weiterhin von den konkret bereitgestellten Versionen und ihrer Konfiguration ab.
