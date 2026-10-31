---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2023-09-10-springboot-intellij-import",
  "routeSlug": "2023-09-10-springboot-intellij-import",
  "kind": "post",
  "title": "Spring-Boot-Projekte in IntelliJ öffnen und Ausführungsfehler eingrenzen",
  "description": "Gradle-Synchronisierung, Wrapper-Build, IDE-Konfiguration und echte HTTP-Tests getrennt prüfen.",
  "categories": [
    "springboot"
  ],
  "tags": [
    "springboot",
    "intellij community",
    "project import",
    "RUN/DEBUG configurations"
  ],
  "sourcePath": "src/content/posts/en/2023-09-10-springboot-intellij-import.md",
  "sourceSha256": "5b3c970364e92d3672967197986ea67769f45094ca27f6c9f8bfbd0779645bc2",
  "draftSha256": "e7a48bd942d6b4c4c74c00c141cc0bf1a515f2df8fd98ea7c287fab01c0d3ee4",
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
Prüfen Sie beim Öffnen eines Spring-Boot-Projekts in IntelliJ zuerst die Gradle-Synchronisierung und vergleichen Sie den Wrapper-Build mit der IDE-Ausführung. Eine fehlende Ausführen-Schaltfläche erfordert nicht immer eine manuelle Konfiguration. Eine gültige Java-main-Methode lässt sich auch über das [Symbol am Editor-Rand](https://www.jetbrains.com/help/idea/running-applications.html) starten.

Dieser Leitfaden setzt das [Initializr-Beispiel](/en/posts/2023-09-07-springboot-initializer/) mit Boot 4.1.2, Gradle 9.8.2 und Java 17 fort. Build und HTTP-Verhalten wurden lokal ausgeführt; die IDE-Schritte wurden anhand der JetBrains-Dokumentation geprüft. Dies behauptet keine praktische Oberflächenprüfung einer bestimmten IDE-Version.

## Verarbeitungsablauf

![Build- und IDE-Fehler getrennt prüfen](/assets/diagrams/technical/de-2023-09-10-springboot-intellij-import.svg)

Unterscheiden Sie mit dem Wrapper-Build Projektfehler von der IDE-Einrichtung. HTTP-Tests verwenden einen zufälligen Port; manuelles bootRun verwendet den konfigurierten Port.

## Projekt und JDK prüfen

1. Öffnen Sie über File → Open den entpackten Projektstamm, der `settings.gradle` und `build.gradle` enthält.
2. Schließen Sie die Gradle-Synchronisierung ab. Beheben Sie zuerst Fehler beim Herunterladen von Abhängigkeiten oder bei der Synchronisierung.
3. Wählen Sie die Wrapper-Distribution des Projekts und prüfen Sie Gradle JVM und Project SDK. Dieses Beispiel verwendet für beide JDK 17.
4. Führen Sie `./gradlew --version` und `./gradlew test` in einem Terminal aus, um ein Ergebnis außerhalb der IDE zu erhalten.

Siehe den [Leitfaden zur Gradle-Integration](https://www.jetbrains.com/help/idea/gradle.html) und die [Auswahlregeln für die Gradle-JVM](https://www.jetbrains.com/help/idea/gradle-jvm-selection.html). Menübezeichnungen variieren nach IDE-Version und Betriebssystem. Project SDK, die JVM von Gradle, die Java-Toolchain und die JRE der Ausführungskonfiguration sind unterschiedliche Einstellungen und stimmen nicht immer automatisch überein.

## Einen Endpunkt und echte HTTP-Tests ergänzen

Behalten Sie die vier vorhandenen Dateien bei und ergänzen Sie diese beiden. Der Controller bleibt durch seine Platzierung im Anwendungspaket `example.demo` innerhalb des Component Scanning.

### `src/main/java/example/demo/GreetingController.java`

```java
package example.demo;

import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class GreetingController {
    @GetMapping("/greeting")
    public Map<String, String> greeting() {
        return Map.of("message", "Hello, Gradle");
    }
}
```

### `src/test/java/example/demo/GreetingHttpTest.java`

```java
package example.demo;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.core.env.Environment;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class GreetingHttpTest {
    @Autowired Environment environment;

    HttpResponse<String> get(String path) throws Exception {
        String port = environment.getRequiredProperty("local.server.port");
        var request = HttpRequest.newBuilder(URI.create("http://127.0.0.1:" + port + path))
                .timeout(Duration.ofSeconds(10)).GET().build();
        return HttpClient.newHttpClient().send(request, HttpResponse.BodyHandlers.ofString());
    }

    @Test
    void greetingReturnsJson() throws Exception {
        var response = get("/greeting");
        assertEquals(200, response.statusCode());
        assertTrue(response.headers().firstValue("content-type").orElse("").contains("application/json"));
        assertEquals("{\"message\":\"Hello, Gradle\"}", response.body());
    }

    @Test
    void missingPathIsNotAnApplicationStartupFailure() throws Exception {
        assertEquals(404, get("/missing").statusCode());
    }
}
```

`./gradlew test` führt nun den vorhandenen Kontexttest und zwei HTTP-Tests aus. Die HTTP-Tests starten einen echten Server auf einem zufälligen Port und prüfen JSON-Ausgabe sowie die 404-Antwort eines fehlenden Pfads. Dafür muss der lokale Port 8080 nicht frei sein.

## Gradle- und Application-Ausführung vergleichen

Starten Sie den Server mit dem ersten Befehl und führen Sie den zweiten in einem anderen Terminal aus.

```sh
./gradlew bootRun --args='--server.port=8081'
```

```sh
curl --fail --show-error http://localhost:8081/greeting
```

```json
{"message":"Hello, Gradle"}
```

Versuchen Sie in der IDE zuerst das Ausführen-Symbol neben `DemoApplication.main()`. Wenn Sie eine ausdrückliche Konfiguration benötigen, erstellen Sie unter Run → Edit Configurations eine Application-Konfiguration und prüfen Sie diese Werte.

| Einstellung | Beispiel |
| --- | --- |
| Hauptklasse | `example.demo.DemoApplication` |
| Klassenpfadmodul | Das Modul der Hauptquellen des Projekts, etwa `demo.main` |
| JRE | JDK 17 |
| Programmargumente | `--server.port=8081` |

Beenden Sie einen bestehenden Prozess auf 8081 oder wählen Sie einen anderen Port. Die Verfügbarkeit Boot-spezifischer Werkzeugfenster oder Konfigurationen ist unabhängig von der Ausführung einer normalen Java-Application-Konfiguration.

| Beobachtung | Zuerst prüfen |
| --- | --- |
| Auch der Wrapper-Build scheitert | JDK-/Gradle-Kompatibilität, Abhängigkeiten und Quellcodefehler |
| Wrapper funktioniert, IDE scheitert | Gradle neu laden, Modulklassenpfad, Ausführungs-JRE und Argumente |
| Server startet, aber `/greeting` liefert 404 | Controller-Paket und Mapping-Pfad |
| Fehler wegen belegtem Port | Bestehende Prozesse und Ausführungsinstanzen |

Wenn die Kompilierung gelingt, aber die IDE generierte Methoden als Fehler markiert, fahren Sie mit den [Lombok- und Annotation-Processor-Prüfungen](/en/posts/2023-09-15-springboot-intellij-lombok/) fort.
