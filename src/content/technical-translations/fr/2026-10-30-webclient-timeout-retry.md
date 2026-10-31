---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2026-10-30-webclient-timeout-retry",
  "routeSlug": "2026-10-30-webclient-timeout-retry",
  "kind": "post",
  "title": "Tester les délais d’expiration et les réessais bornés de WebClient avec Reactor",
  "description": "Distinguez les délais de connexion, de réponse, par tentative et total. Testez une politique GET qui réessaie seulement HTTP 503, deux fois, avec un serveur HTTP local et le temps virtuel Reactor.",
  "categories": [
    "springboot"
  ],
  "tags": [
    "springboot",
    "webclient",
    "test",
    "reactor"
  ],
  "sourcePath": "src/content/posts/en/2026-10-30-webclient-timeout-retry.md",
  "sourceSha256": "757c2335d2f6b40391fa299791d6c6e6bade0e499c599b451be06be4eee77e3b",
  "draftSha256": "109938c7c742a93479fc217aa568dd0b7270901fb545b0090963a891cb7294c6",
  "manifestPath": ".pipeline/technical-translations/batch-078/manifest.json",
  "manifestSha256": "e685b2de5dafd8cfff8e8e996fa2b09613becb072bdd575b58b9eca9651474a3",
  "publishedAt": "2026-10-31T02:49:44.828Z",
  "updatedAt": "2026-10-31T02:49:44.828Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 118,
    "approvedAt": "2026-10-31T02:49:44.828Z",
    "basis": "2026-10-31 user instruction “진행해줘” immediately following delivery of the reviewed 72 complete translations in PR #118; interpreted as authorization to publish exactly batch-078 in all six languages. Separate AI language review is recorded in the manifest; this does not claim a human line-by-line review. Excludes the older 120 technical drafts and 318 pending news translations."
  }
}
---
Placez un `timeout` par tentative avant `retryWhen`, et un `timeout` total après celui-ci pour inclure les attentes entre réessais dans le budget global. Ne réessayez que les échecs autorisés par le contrat de l’API : cet exemple GET réessaie HTTP 503 au plus deux fois et s’arrête sur expiration ou autre erreur. Spring documente les [délais du transport](https://docs.spring.io/spring-framework/reference/6.2/web/webflux-webclient/client-builder.html) séparément du [délai du publisher](https://projectreactor.io/docs/core/3.7.12/api/reactor/core/publisher/Mono.html) de Reactor.

## Quelle limite chaque paramètre contrôle-t-il ?

| Paramètre | Périmètre dans cet exemple |
| --- | --- |
| `CONNECT_TIMEOUT_MILLIS` | Établissement d’une connexion TCP ; pas un budget complet pour DNS, acquisition dans le pool ou TLS |
| `responseTimeout` | Intervalle maximal entre lectures réseau pendant la réception d’une réponse ; pas une échéance pour le corps complet |
| Premier `timeout(attemptLimit)` | Un abonnement jusqu’au décodage du corps ; redémarre à chaque réessai |
| Dernier `timeout(totalLimit)` | L’abonnement complet, y compris toutes les tentatives et les attentes entre réessais |
| `StepVerifier.verify(GUARD)` | Attente maximale du lanceur de tests ; ne configure pas le client |

La [documentation de responseTimeout](https://projectreactor.io/docs/netty/1.2.11/api/reactor/netty/http/client/HttpClient.html) de Reactor Netty décrit un intervalle de lecture : une réponse qui continue à fournir des données peut donc dépasser cette durée au total. Le délai du publisher externe fournit une échéance globale distincte. L’annulation arrête cet abonnement ; elle n’annule pas le travail déjà effectué par le service distant.

## Borner les réessais avant d’ajouter d’autres cas d’échec

![Appliquer un délai par tentative, réessayer uniquement les erreurs 503 admissibles et borner toute l’opération](/assets/diagrams/technical/fr-2026-10-30-webclient-timeout-retry.svg)

Le schéma résume l’imbrication des opérateurs, plutôt que chaque événement HTTP. Chaque tentative réussit ou émet une erreur. Seule une erreur 503 avec des réessais restants déclenche un réabonnement différé ; les autres erreurs arrêtent immédiatement le traitement. Le délai externe peut annuler une tentative active comme une attente entre réessais.

[`Retry.fixedDelay(2, delay)`](https://projectreactor.io/docs/core/release/api/reactor/util/retry/Retry.html) autorise deux réessais après la tentative initiale : au plus trois tentatives applicatives par abonnement. `.onRetryExhaustedThrow` propage la dernière exception 503 plutôt qu’une exception enveloppe d’épuisement des réessais. `.disableRetry(true)` désactive le réessai automatique distinct de Reactor Netty lors d’un abandon TCP, afin qu’il n’ajoute pas de réessai de transport caché à ces décomptes.

L’exemple effectue un GET et réessaie délibérément uniquement 503. Une expiration ne prouve pas que le serveur n’a rien fait. N’appliquez pas cette politique aux paiements ou à d’autres écritures sans contrat d’idempotence explicite. Elle ne traite pas `Retry-After`, ne réessaie pas 429, n’applique ni attente exponentielle ni gigue, et ne coordonne pas les réessais entre appelants. La courte attente fixe accélère les tests ; choisissez les limites et les attentes de production selon le contrat de votre API et votre budget de charge.

## Créer un projet autonome

Utilisez un nouveau répertoire vide, JDK 17 et Gradle 8.4. L’exemple fixe Boot BOM 3.5.7 et MockWebServer 4.12.0 pour correspondre aux [tests du contrat de réponse](/en/posts/2023-09-19-springboot-test-webclient/). Ce sont des paramètres de reproduction, pas des recommandations de versions actuelles pour la production. La résolution initiale des dépendances utilise Maven Central ; les tests HTTP utilisent uniquement l’interface de bouclage. Aucune application Boot en cours d’exécution ni aucun wrapper Gradle ne sont fournis.

### `settings.gradle`

```groovy
rootProject.name = 'webclient-timeout-retry'
```

### `build.gradle`

```groovy
plugins { id 'java' }
repositories { mavenCentral() }
dependencies {
    implementation platform('org.springframework.boot:spring-boot-dependencies:3.5.7')
    implementation 'org.springframework.boot:spring-boot-starter-webflux'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testImplementation 'io.projectreactor:reactor-test'
    testImplementation 'com.squareup.okhttp3:mockwebserver:4.12.0'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
test { useJUnitPlatform() }
```

## Placer les deux échéances à des positions différentes

Enregistrez l’implémentation suivante. Le constructeur reçoit des durées positives choisies par l’appelant ; le test fournit des valeurs explicites. Le délai de réponse et le délai de connexion TCP de 1 000 ms relèvent de la fabrique de transport.

### `src/main/java/RetryClient.java`

```java
import java.time.Duration;
import io.netty.channel.ChannelOption;
import org.springframework.http.client.reactive.ReactorClientHttpConnector;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;
import reactor.core.publisher.Mono;
import reactor.netty.http.client.HttpClient;
import reactor.util.retry.Retry;

public class RetryClient {
    private final WebClient client;
    private final Duration attemptLimit;
    private final Duration totalLimit;
    private final Duration retryDelay;

    public RetryClient(WebClient client, Duration attemptLimit,
                       Duration totalLimit, Duration retryDelay) {
        this.client = client;
        this.attemptLimit = attemptLimit;
        this.totalLimit = totalLimit;
        this.retryDelay = retryDelay;
    }

    public static WebClient transport(String baseUrl, Duration responseLimit) {
        HttpClient http = HttpClient.create()
            .disableRetry(true)
            .option(ChannelOption.CONNECT_TIMEOUT_MILLIS, 1000)
            .responseTimeout(responseLimit);
        return WebClient.builder().baseUrl(baseUrl)
            .clientConnector(new ReactorClientHttpConnector(http)).build();
    }

    public Mono<String> get() {
        return Mono.defer(() -> client.get().uri("/value")
                .retrieve().bodyToMono(String.class))
            .timeout(attemptLimit)
            .retryWhen(Retry.fixedDelay(2, retryDelay)
                .filter(error -> error instanceof WebClientResponseException response
                    && response.getStatusCode().value() == 503)
                .onRetryExhaustedThrow((spec, signal) -> signal.failure()))
            .timeout(totalLimit);
    }
}
```

## Reproduire neuf contrats de politique

Sept tests utilisent un vrai WebClient et un MockWebServer local. Deux utilisent un échange synthétique et le temps virtuel de Reactor pour vérifier la chronologie des opérateurs sans dépendre de l’ordonnancement réseau. Le temps virtuel ne teste pas les délais réels des sockets de Reactor Netty. Le test du transport vérifie la cause enveloppée d’expiration de lecture, tandis que le délai du publisher produit `TimeoutException`.

### `src/test/java/RetryClientTest.java`

```java
import java.io.IOException;
import java.time.Duration;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.atomic.AtomicInteger;
import io.netty.handler.timeout.ReadTimeoutException;
import okhttp3.mockwebserver.MockResponse;
import okhttp3.mockwebserver.MockWebServer;
import okhttp3.mockwebserver.SocketPolicy;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpStatus;
import org.springframework.web.reactive.function.client.ClientResponse;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientRequestException;
import org.springframework.web.reactive.function.client.WebClientResponseException;
import reactor.core.publisher.Mono;
import reactor.netty.http.client.HttpClient;
import reactor.test.StepVerifier;
import static org.junit.jupiter.api.Assertions.*;

class RetryClientTest {
    private MockWebServer server;
    private WebClient client;
    private static final Duration GUARD = Duration.ofSeconds(10);

    @BeforeAll
    static void warmUp() {
        HttpClient.create().warmup().block(GUARD);
    }

    @BeforeEach
    void start() throws IOException {
        server = new MockWebServer();
        server.start();
        client = RetryClient.transport(server.url("/").toString(), Duration.ofSeconds(5));
    }

    @AfterEach
    void stop() throws IOException {
        server.shutdown();
    }

    RetryClient policy() {
        return new RetryClient(client, Duration.ofSeconds(3),
            Duration.ofSeconds(8), Duration.ofMillis(10));
    }

    void expectStatus(int status) {
        StepVerifier.create(policy().get())
            .expectErrorSatisfies(error -> assertEquals(status,
                assertInstanceOf(WebClientResponseException.class, error).getStatusCode().value()))
            .verify(GUARD);
    }

    @Test
    void successUsesOneRequest() {
        server.enqueue(new MockResponse().setBody("ok"));
        StepVerifier.create(policy().get()).expectNext("ok").expectComplete().verify(GUARD);
        assertEquals(1, server.getRequestCount());
    }

    @Test
    void two503ResponsesThenSuccessUseThreeRequests() {
        server.enqueue(new MockResponse().setResponseCode(503));
        server.enqueue(new MockResponse().setResponseCode(503));
        server.enqueue(new MockResponse().setBody("ok"));
        StepVerifier.create(policy().get()).expectNext("ok").expectComplete().verify(GUARD);
        assertEquals(3, server.getRequestCount());
    }

    @Test
    void exhausted503PreservesLastStatusAfterThreeRequests() {
        for (int i = 0; i < 3; i++) server.enqueue(new MockResponse().setResponseCode(503));
        expectStatus(503);
        assertEquals(3, server.getRequestCount());
    }

    @Test
    void notFoundIsNotRetried() {
        server.enqueue(new MockResponse().setResponseCode(404));
        expectStatus(404);
        assertEquals(1, server.getRequestCount());
    }

    @Test
    void otherServerErrorsAreNotRetried() {
        server.enqueue(new MockResponse().setResponseCode(500));
        expectStatus(500);
        assertEquals(1, server.getRequestCount());
    }

    @Test
    void attemptTimeoutIsNotRetried() {
        server.enqueue(new MockResponse().setSocketPolicy(SocketPolicy.NO_RESPONSE));
        RetryClient limited = new RetryClient(client, Duration.ofSeconds(1),
            Duration.ofSeconds(8), Duration.ofMillis(10));
        StepVerifier.create(limited.get()).expectError(TimeoutException.class).verify(GUARD);
        assertEquals(1, server.getRequestCount());
    }

    @Test
    void responseReadTimeoutIsNotRetried() {
        server.enqueue(new MockResponse().setSocketPolicy(SocketPolicy.NO_RESPONSE));
        WebClient shortRead = RetryClient.transport(server.url("/").toString(), Duration.ofMillis(250));
        RetryClient limited = new RetryClient(shortRead, Duration.ofSeconds(3),
            Duration.ofSeconds(8), Duration.ofMillis(10));
        StepVerifier.create(limited.get()).expectErrorSatisfies(error -> {
            assertInstanceOf(WebClientRequestException.class, error);
            assertInstanceOf(ReadTimeoutException.class, error.getCause());
        }).verify(GUARD);
        assertEquals(1, server.getRequestCount());
    }

    @Test
    void totalBudgetIncludesRetryDelay() {
        AtomicInteger attempts = new AtomicInteger();
        StepVerifier.withVirtualTime(() -> {
            WebClient synthetic = WebClient.builder().exchangeFunction(request -> Mono.defer(() -> {
                attempts.incrementAndGet();
                return Mono.just(ClientResponse.create(HttpStatus.SERVICE_UNAVAILABLE).build());
            })).build();
            return new RetryClient(synthetic, Duration.ofSeconds(1),
                Duration.ofMillis(1500), Duration.ofSeconds(1)).get();
        }).thenAwait(Duration.ofMillis(1500)).expectError(TimeoutException.class).verify(GUARD);
        assertEquals(2, attempts.get());
    }

    @Test
    void attemptBudgetRestartsAfterRetry() {
        AtomicInteger attempts = new AtomicInteger();
        StepVerifier.withVirtualTime(() -> {
            WebClient synthetic = WebClient.builder().exchangeFunction(request -> Mono.defer(() -> {
                int attempt = attempts.incrementAndGet();
                return Mono.delay(Duration.ofMillis(400)).map(tick -> attempt == 1
                    ? ClientResponse.create(HttpStatus.SERVICE_UNAVAILABLE).build()
                    : ClientResponse.create(HttpStatus.OK).body("ok").build());
            })).build();
            return new RetryClient(synthetic, Duration.ofMillis(500),
                Duration.ofSeconds(2), Duration.ofMillis(200)).get();
        }).thenAwait(Duration.ofSeconds(1)).expectNext("ok").expectComplete().verify(GUARD);
        assertEquals(2, attempts.get());
    }
}
```

## Exécuter le projet et lire le résultat

```sh
gradle --no-daemon clean test
```

La reproduction locale utilisait JDK 17.0.8.1 et Gradle 8.4. Les neuf tests ont réussi. Consultez `build/reports/tests/test/index.html` ou `build/test-results/test/TEST-RetryClientTest.xml` pour les assertions ; `BUILD SUCCESSFUL` seul n’indique pas combien de tests ont été exécutés.

| Scénario | Résultat vérifié |
| --- | --- |
| Succès immédiat | Une requête HTTP, `ok`, puis terminaison |
| 503 → 503 → succès | Trois requêtes HTTP, `ok`, puis terminaison |
| 503 à chaque tentative | Trois requêtes HTTP, dernier 503 préservé |
| 404 / 500 | Une requête HTTP pour chaque cas, statut préservé |
| Aucune réponse, limite d’une seconde par tentative | `TimeoutException`, une requête HTTP |
| Aucune réponse, limite de lecture de réponse de 250 ms | `WebClientRequestException` avec `ReadTimeoutException`, une requête |
| Budget total de 1.5 s, attente d’une seconde entre réessais | Deux tentatives synthétiques ; l’expiration annule l’attente avant une troisième |
| Tentative de 400 ms, attente de 200 ms, tentative de 400 ms | Chaque tentative reste sous 500 ms ; succès et terminaison vérifiés après une avance de 1 s du temps virtuel |

Ces vérifications ne reproduisent pas l’expiration lors de l’établissement d’une connexion TCP, une panne DNS, la négociation TLS, l’épuisement du pool, les redirections ni les effets de bord distribués. La limite de connexion est configurée, mais n’est pas validée expérimentalement ici. L’ordonnancement du système peut affecter la durée réelle ; les tests vérifient les types d’erreur et les nombres de requêtes, pas une durée exacte en millisecondes. Pour le statut, le type de média et le traitement JSON, poursuivez avec l’[exemple de contrat de réponse WebClient](/en/posts/2023-09-19-springboot-test-webclient/).
