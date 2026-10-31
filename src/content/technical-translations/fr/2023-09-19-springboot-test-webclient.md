---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2023-09-19-springboot-test-webclient",
  "routeSlug": "2023-09-19-springboot-test-webclient",
  "kind": "post",
  "title": "Tester WebClient avec MockWebServer : statut, type de média et décodage",
  "description": "Vérifier huit contrats HTTP locaux de WebClient : HTML, JSON mal formé, corps vide et statuts d’erreur.",
  "categories": [
    "springboot"
  ],
  "tags": [
    "springboot",
    "test",
    "webclient"
  ],
  "sourcePath": "src/content/posts/en/2023-09-19-springboot-test-webclient.md",
  "sourceSha256": "f0a277b8719dc886c37dd8cbeb15f1e68228dce2f44d7fac53a97fee9cb5f885",
  "draftSha256": "77f939d0d9409c5bbc844164444a179c54eb5be1a862e5bd410c7c46700fc842",
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
Testez WebClient avec un MockWebServer local et vérifiez ensemble le statut HTTP, le Content-Type de la réponse, le décodage du corps et la terminaison ou l’erreur. Une réponse `200 OK` contenant du HTML peut violer le contrat de réponse du client malgré un statut de succès ; envoyer `Accept: application/json` n’impose pas une réponse JSON. Spring documente les [tests avec un serveur Web simulé](https://docs.spring.io/spring-framework/reference/6.2/web/webflux-webclient/client-testing.html) utilisant le véritable client HTTP.

Les tests utilisent un vrai WebClient sur HTTP local plutôt qu’une simulation de sa chaîne de méthodes. Ils couvrent les contrats de réponse ci-dessous ; les politiques de délai et de nouvelle tentative de production nécessitent des tests distincts.

## Déroulement du traitement

![Valider la réponse HTTP](/assets/diagrams/technical/fr-2023-09-19-springboot-test-webclient.svg)

Le client vérifie le statut avant le type de média, libère les corps refusés et décode le JSON pris en charge. StepVerifier vérifie la terminaison ou l’erreur ainsi que les valeurs émises.

## Configurer un projet de test autonome

L’environnement de reproduction comprend JDK 17.0.8.1, Gradle 8.4, la **BOM Spring Boot 3.5.7** et MockWebServer **4.12.0**. Ils figent les dépendances de l’exemple ; ce ne sont pas des recommandations de versions actuelles pour la production. Il s’agit d’un simple projet de test Java, sans besoin d’application Spring Boot en cours d’exécution.

Dans un nouveau répertoire, créez `settings.gradle` contenant `rootProject.name = 'webclient-example'`, et ce `build.gradle` complet :

```groovy
plugins { id 'java' }
repositories { mavenCentral() }
dependencies {
    testImplementation platform('org.springframework.boot:spring-boot-dependencies:3.5.7')
    testImplementation 'org.springframework.boot:spring-boot-starter-webflux'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testImplementation 'io.projectreactor:reactor-test'
    testImplementation 'com.squareup.okhttp3:mockwebserver:4.12.0'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
test { useJUnitPlatform() }
```

La BOM est explicite pour donner des versions aux dépendances Spring et Reactor même sans le plugin Gradle Spring Boot. Pour une application déjà gérée par Boot, adaptez les dépendances de test à sa BOM sélectionnée.

## Tester huit contrats de réponse

Enregistrez cette classe complète dans `src/test/java/ExternalApiTest.java` :

```java
import java.io.IOException;
import java.time.Duration;
import java.util.concurrent.TimeUnit;
import okhttp3.mockwebserver.MockResponse;
import okhttp3.mockwebserver.MockWebServer;
import okhttp3.mockwebserver.RecordedRequest;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.MediaType;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;
import reactor.test.StepVerifier;
import static org.junit.jupiter.api.Assertions.*;

class ExternalApiTest {
    private MockWebServer server;
    private WebClient client;
    record Payload(String message) {}

    @BeforeEach
    void start() throws IOException {
        server = new MockWebServer();
        server.start();
        client = WebClient.builder().baseUrl(server.url("/").toString()).build();
    }

    @AfterEach
    void stop() throws IOException {
        server.shutdown();
    }

    private Mono<Payload> fetch() {
        return client.get().uri("/employee/100")
            .accept(MediaType.APPLICATION_JSON)
            .exchangeToMono(response -> {
                if (response.statusCode().isError()) {
                    return response.createException().flatMap(Mono::error);
                }
                boolean json = response.headers().contentType()
                    .map(type -> "application".equals(type.getType())
                        && ("json".equals(type.getSubtype())
                            || type.getSubtype().endsWith("+json")))
                    .orElse(false);
                if (!json) {
                    return response.releaseBody().then(Mono.<Payload>error(
                        new IllegalStateException("Expected JSON response")));
                }
                return response.bodyToMono(Payload.class);
            });
    }

    @Test
    void rejectsHtmlEvenWhenStatusIs200() throws Exception {
        server.enqueue(new MockResponse().setResponseCode(200)
            .setHeader("Content-Type", "text/html; charset=UTF-8")
            .setBody("<html><body>Unknown failure</body></html>"));
        StepVerifier.create(fetch())
            .expectErrorMatches(error -> error instanceof IllegalStateException
                && error.getMessage().equals("Expected JSON response"))
            .verify(Duration.ofSeconds(5));
        RecordedRequest request = server.takeRequest(1, TimeUnit.SECONDS);
        assertNotNull(request);
        assertEquals("GET", request.getMethod());
        assertEquals("/employee/100", request.getPath());
        assertEquals("application/json", request.getHeader("Accept"));
    }

    @Test
    void preservesHttp500Error() {
        server.enqueue(new MockResponse().setResponseCode(500)
            .setHeader("Content-Type", "text/html")
            .setBody("<html>Unknown failure</html>"));
        StepVerifier.create(fetch())
            .expectError(org.springframework.web.reactive.function.client.WebClientResponseException.InternalServerError.class)
            .verify(Duration.ofSeconds(5));
    }

    @Test
    void decodesJson() {
        server.enqueue(new MockResponse().setResponseCode(200)
            .setHeader("Content-Type", "application/json")
            .setBody("{\"message\":\"ok\"}"));
        StepVerifier.create(fetch())
            .expectNextMatches(payload -> payload.message().equals("ok"))
            .expectComplete().verify(Duration.ofSeconds(5));
    }

    @Test
    void rejectsMissingContentType() {
        server.enqueue(new MockResponse().setResponseCode(200)
            .setBody("{\"message\":\"ok\"}"));
        StepVerifier.create(fetch())
            .expectErrorMatches(error -> error instanceof IllegalStateException
                && error.getMessage().equals("Expected JSON response"))
            .verify(Duration.ofSeconds(5));
    }

    @Test
    void rejectsMalformedJson() {
        server.enqueue(new MockResponse().setResponseCode(200)
            .setHeader("Content-Type", "application/json").setBody("{broken"));
        StepVerifier.create(fetch())
            .expectError(org.springframework.core.codec.DecodingException.class)
            .verify(Duration.ofSeconds(5));
    }

    @Test
    void decodesStructuredJsonSubtype() {
        server.enqueue(new MockResponse().setResponseCode(200)
            .setHeader("Content-Type", "application/vnd.example+json")
            .setBody("{\"message\":\"ok\"}"));
        StepVerifier.create(fetch())
            .expectNextMatches(payload -> payload.message().equals("ok"))
            .expectComplete().verify(Duration.ofSeconds(5));
    }

    @Test
    void completesWithoutPayloadForEmptyJsonBody() {
        server.enqueue(new MockResponse().setResponseCode(200)
            .setHeader("Content-Type", "application/json"));
        StepVerifier.create(fetch())
            .expectComplete().verify(Duration.ofSeconds(5));
    }

    @Test
    void rejectsNonApplicationJsonSubtype() {
        server.enqueue(new MockResponse().setResponseCode(200)
            .setHeader("Content-Type", "text/example+json")
            .setBody("{\"message\":\"ok\"}"));
        StepVerifier.create(fetch())
            .expectErrorMatches(error -> error instanceof IllegalStateException
                && error.getMessage().equals("Expected JSON response"))
            .verify(Duration.ofSeconds(5));
    }
}
```

Exécutez avec JDK 17 sélectionné et Gradle 8.4 installé :

```sh
java -version
gradle --version
gradle --no-daemon test
```

Les huit tests doivent réussir. Ouvrez `build/reports/tests/test/index.html` pour voir le résultat de chaque test ; la sortie de la tâche Gradle ne liste pas nécessairement chaque test réussi.

| Réponse | Résultat exigé par cet exemple |
| --- | --- |
| HTTP 200, corps JSON | Décoder les données. |
| HTTP 200, corps HTML | Refuser le type de contenu inattendu. |
| HTTP 500, corps HTML | Préserver le type d’erreur HTTP. |
| HTTP 200, Content-Type absent | Refuser le format de réponse non précisé. |
| HTTP 200, JSON mal formé | Signaler une erreur de décodage. |
| HTTP 200, `application/vnd.example+json` | Décoder les données JSON compatibles. |
| HTTP 200, corps JSON vide | Terminer sans émettre de données. |
| HTTP 200, `text/example+json` | Refuser le type de média hors application. |

Le comportement en présence d’un corps vide est un contrat délibéré de cet exemple. Si votre point d’accès exige des données, ajoutez `switchIfEmpty(Mono.error(...))` et modifiez ce test pour attendre l’erreur applicative.

<span id="why-status-and-decoding-are-checked-separately"></span>

## Pourquoi HTTP 200 peut-il encore échouer à la validation ?

`fetch()` traite les statuts d’erreur avant d’inspecter le format des réponses réussies. `createException()` préserve HTTP 500 sous forme de `WebClientResponseException.InternalServerError`. Un échec de connexion suit généralement le chemin `WebClientRequestException` ; il ne s’agit pas d’une réponse HTTP du serveur.

Pour un statut sans erreur, le code accepte les types de média `application/json` et `application/*+json`, puis laisse le décodeur valider le corps. Un Content-Type incorrect et un JSON mal formé produisent donc des erreurs différentes. C’est un contrat d’exemple, pas une politique complète pour les redirections ou tous les statuts de succès.

Lorsqu’il refuse une réponse réussie, il libère le corps avant de signaler l’erreur applicative. Avec `exchangeToMono`, consommez ou traitez le corps dans le callback ; la [documentation exchange de Spring](https://docs.spring.io/spring-framework/reference/6.2/web/webflux-webclient/client-exchange.html) explique qu’un corps non consommé est libéré après la terminaison.

`setBody(html)` envoie directement du HTML. Sérialiser d’abord cette chaîne en JSON modifierait la réponse testée. Les assertions sur la requête enregistrée vérifient aussi la méthode, le chemin et l’en-tête `Accept` réellement envoyés.

`verify(Duration.ofSeconds(5))` borne l’attente de chaque test. Il ne configure pas les délais de connexion ou de réponse du client en production. Ajoutez les tests de délai de transport et de nouvelle tentative selon votre contrat d’API ; ces huit cas ne les couvrent pas.

Les huit tests ont réussi dans l’environnement de reproduction ci-dessus. Dans ce dépôt, `python3 scripts/check_webclient_example.py` répète cette vérification. Pour un projet franchissant la frontière Jakarta, établissez la [base de migration Spring Boot](/en/posts/2023-09-08-springboot3-migration/) avant de modifier le comportement du client.

Ces tests client utilisent un serveur simulé local ; ils ne vérifient pas les fichiers statiques d’une application déployée. Si l’application empaquette des applications Vue, l’[exemple d’empaquetage frontend Gradle](/en/posts/2021-07-23-multiple-gradle-build/) vérifie le JAR exécutable et ses réponses HTML/JavaScript. Les deux exemples figent des environnements différents et ne doivent être combinés qu’après alignement de leurs dépendances.

Référence de l’API MockWebServer : [sources et exemples OkHttp 4.12.0](https://github.com/square/okhttp/tree/parent-4.12.0/mockwebserver).

Pour les limites de temps et les nombres de tentatives, poursuivez avec les [tests WebClient de délai et de nouvelles tentatives bornées](/en/posts/2026-10-30-webclient-timeout-retry/). Cet exemple ne réessaie que les réponses GET de statut 503 et sépare les limites par tentative du budget total des nouvelles tentatives.
