---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2023-09-10-springboot-intellij-import",
  "routeSlug": "2023-09-10-springboot-intellij-import",
  "kind": "post",
  "title": "Ouvrir un projet Spring Boot dans IntelliJ et isoler les erreurs d’exécution",
  "description": "Vérifier séparément la synchronisation Gradle, la construction Wrapper, la configuration de l’IDE et les tests HTTP réels.",
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
  "draftSha256": "3dc917236302622f65ea4313c2746e92f8b695b3358147409420792043325ca1",
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
Lors de l’ouverture d’un projet Spring Boot dans IntelliJ, vérifiez d’abord la synchronisation Gradle et comparez la construction Wrapper à l’exécution dans l’IDE. L’absence d’un bouton d’exécution n’exige pas toujours une configuration manuelle. Vous pouvez aussi lancer une méthode main Java valide depuis [l’icône de la gouttière de l’éditeur](https://www.jetbrains.com/help/idea/running-applications.html).

Ce guide poursuit l’[exemple Initializr](/en/posts/2023-09-07-springboot-initializer/) avec Boot 4.1.2, Gradle 9.8.2 et Java 17. La construction et le comportement HTTP ont été exécutés localement ; les étapes de l’IDE ont été vérifiées dans la documentation JetBrains. Cela ne revendique pas une vérification pratique de l’interface d’une version précise de l’IDE.

## Déroulement du traitement

![Distinguer les échecs de construction et de l’IDE](/assets/diagrams/technical/fr-2023-09-10-springboot-intellij-import.svg)

Utilisez la construction Wrapper pour distinguer les échecs du projet de la configuration de l’IDE. Les tests HTTP utilisent un port aléatoire ; bootRun lancé manuellement utilise le port configuré.

## Vérifier le projet et le JDK

1. Utilisez File → Open sur la racine extraite du projet contenant `settings.gradle` et `build.gradle`.
2. Terminez la synchronisation Gradle. Résolvez d’abord les échecs de téléchargement des dépendances ou de synchronisation.
3. Sélectionnez la distribution Wrapper du projet, puis vérifiez Gradle JVM et Project SDK. Cet exemple utilise JDK 17 pour les deux.
4. Exécutez `./gradlew --version` et `./gradlew test` dans un terminal pour obtenir un résultat hors de l’IDE.

Voir le [guide d’intégration Gradle](https://www.jetbrains.com/help/idea/gradle.html) et les [règles de sélection de la JVM Gradle](https://www.jetbrains.com/help/idea/gradle-jvm-selection.html). Les libellés des menus varient selon la version de l’IDE et le système. Project SDK, la JVM exécutant Gradle, la toolchain Java et le JRE de la configuration d’exécution sont des paramètres distincts qui ne coïncident pas toujours automatiquement.

## Ajouter un point d’accès et de vrais tests HTTP

Conservez les quatre fichiers existants et ajoutez ces deux fichiers. Placer le contrôleur dans le package applicatif `example.demo` le maintient dans le périmètre de détection des composants.

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

`./gradlew test` exécute maintenant le test de contexte existant et deux tests HTTP. Ces derniers démarrent un véritable serveur sur un port aléatoire et vérifient la sortie JSON et la réponse 404 d’un chemin absent. Ils n’exigent pas que le port local 8080 soit libre.

## Comparer les exécutions Gradle et Application

Démarrez le serveur avec la première commande, puis exécutez la seconde dans un autre terminal.

```sh
./gradlew bootRun --args='--server.port=8081'
```

```sh
curl --fail --show-error http://localhost:8081/greeting
```

```json
{"message":"Hello, Gradle"}
```

Dans l’IDE, essayez d’abord l’icône d’exécution à côté de `DemoApplication.main()`. Si une configuration explicite est nécessaire, créez une configuration Application sous Run → Edit Configurations et vérifiez ces valeurs.

| Paramètre | Exemple |
| --- | --- |
| Classe principale | `example.demo.DemoApplication` |
| Module du classpath | Le module des sources principales du projet, tel que `demo.main` |
| JRE | JDK 17 |
| Arguments du programme | `--server.port=8081` |

Si un processus existant occupe 8081, arrêtez-le ou choisissez un autre port. La disponibilité de fenêtres d’outils ou de configurations propres à Boot est distincte de l’exécution d’une configuration Java Application normale.

| Observation | Premier contrôle |
| --- | --- |
| La construction Wrapper échoue aussi | Compatibilité JDK/Gradle, dépendances et erreurs des sources |
| Le Wrapper réussit mais l’IDE échoue | Rechargement Gradle, classpath du module, JRE d’exécution et arguments |
| Le serveur démarre mais `/greeting` renvoie 404 | Package du contrôleur et chemin de mapping |
| Échec pour port occupé | Processus et instances d’exécution existants |

Si la compilation réussit mais que l’IDE marque les méthodes générées comme erronées, poursuivez avec les [contrôles Lombok et processeur d’annotations](/en/posts/2023-09-15-springboot-intellij-lombok/).
