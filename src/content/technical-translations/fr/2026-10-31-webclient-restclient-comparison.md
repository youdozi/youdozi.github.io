---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2026-10-31-webclient-restclient-comparison",
  "routeSlug": "2026-10-31-webclient-restclient-comparison",
  "kind": "post",
  "title": "WebClient ou RestClient : choisir les appels synchrones, réactifs et en streaming",
  "description": "Comparez le déclenchement, le blocage, les erreurs et les threads virtuels avec Spring WebClient et RestClient. Un exemple HTTP local vérifie les requêtes par abonnement et les erreurs 404/503.",
  "categories": [
    "springboot"
  ],
  "tags": [
    "spring",
    "webclient",
    "restclient",
    "http-client",
    "reactive",
    "virtual-threads"
  ],
  "sourcePath": "src/content/posts/en/2026-10-31-webclient-restclient-comparison.md",
  "sourceSha256": "66635549fdfb330bbeabd658046b28dcb1566bef58dbf033b35e22e387806d15",
  "draftSha256": "63dead6a4827f35443ff54cf5cc5d84bd0a214bd542f278aaad32da6876d8a4c",
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
**Commencez par RestClient lorsque du code de service synchrone a besoin d’une réponse HTTP avant de continuer. Envisagez WebClient pour la composition réactive ou le streaming.** Tous deux proposent des API fluides, mais [RestClient est synchrone et WebClient est un client réactif non bloquant](https://docs.spring.io/spring-framework/reference/integration/rest-clients.html). Adaptez le client au modèle d’exécution de l’application plutôt qu’au nombre de requêtes.


RestClient est apparu dans Spring Framework 6.1 ; WebClient est disponible depuis 5.0. Vérifiez d’abord si votre version de Framework prend en charge le client choisi. Lors de la mise à niveau d’un projet Boot, suivez une combinaison compatible gérée par Boot. L’exemple exécutable ci-dessous fixe Framework 7.0.10.

## Quel client répond à quel besoin ?

| Critère | RestClient | WebClient |
| --- | --- | --- |
| Résultat | Une opération terminale comme l’extraction du corps attend la réponse et renvoie une valeur | Mono ou Flux représente le résultat ; l’abonnement déclenche la requête |
| Usage naturel | Code séquentiel et synchrone dans Spring MVC ou les traitements par lots | WebFlux, composition réactive et streaming comme SSE |
| Transmission des erreurs | Le traitement retrieve par défaut lève RestClientResponseException pour 4xx et 5xx | Le traitement retrieve par défaut émet une erreur WebClientResponseException pour 4xx et 5xx |
| Coût supplémentaire | Plus simple à suivre dans une pile d’appels classique | Exige de comprendre opérateurs, abonnement, annulation et propagation du contexte |
| Contrôle de concurrence | Concevoir séparément les exécuteurs ou la concurrence des threads virtuels | Borner séparément la concurrence de composition, comme flatMap, ainsi que les budgets de connexions et d’attente |

Ce tableau part d’appels API ordinaires qui agrègent une réponse en mémoire. RestClient peut aussi lire des flux d’octets par une gestion bas niveau des réponses, mais WebClient convient naturellement aux flux réactifs d’éléments et au contrôle de la demande. Utiliser WebClient n’impose pas de convertir le serveur à WebFlux : Spring MVC peut aussi utiliser des types de retour réactifs. Les [conseils Spring sur les clients HTTP](https://spring.io/blog/2025/09/30/the-state-of-http-clients-in-spring/) font la même distinction entre appels synchrones habituels et besoins réactifs ou de streaming.

Un service synchrone utilisant des threads virtuels peut conserver un code RestClient séquentiel. Les threads virtuels ne rendent pas son API non bloquante et n’augmentent ni la capacité en aval ni les limites de connexion. Considérez le [périmètre des threads virtuels](/en/posts/2026-10-31-virtual-threads-jdk21-jdk25/) avec les [limites de capacité des dépendances](/en/posts/2026-10-31-jdk-10k-rps-architecture/).

## Comparer le déclenchement avec les mêmes réponses HTTP

![Le flux principal termine une opération terminale RestClient, crée un Mono WebClient, s’y abonne deux fois pour des requêtes distinctes et vérifie les erreurs 404 et 503 des deux clients](/assets/diagrams/technical/fr-2026-10-31-webclient-restclient-comparison.svg)

Le schéma présente les vérifications principales de la méthode main ; il omet la préparation du serveur local, la configuration des clients et le nettoyage. **RestClient n’envoie pas de requête au seul appel de retrieve().** Ici, body(String.class) effectue la requête et attend son résultat. WebClient exécute son Mono de requête par défaut à l’abonnement. S’abonner deux fois à ce Mono, sans opérateurs de cache ou de partage, envoie deux requêtes.

Cet exemple console autonome a été exécuté avec Spring Framework 7.0.10, Reactor Core 3.8.8, JDK 17 et Gradle 8.4. Ce n’est pas une application Spring Boot. Les deux clients utilisent explicitement JDK HttpClient pour éliminer les différences de sélection du connecteur par défaut. Dans un projet Boot, préférez les dépendances gérées par cette version de Boot plutôt que de les remplacer avec cette BOM.

### `settings.gradle`

```groovy
rootProject.name = 'http-client-comparison'
```

### `build.gradle`

```groovy
plugins { id 'application' }
repositories { mavenCentral() }
dependencies {
    implementation platform('org.springframework:spring-framework-bom:7.0.10')
    implementation 'org.springframework:spring-webflux'
}
java {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
}
application { mainClass = 'ClientComparison' }
```

### `src/main/java/ClientComparison.java`

```java
import com.sun.net.httpserver.HttpServer;
import java.net.InetSocketAddress;
import java.net.http.HttpClient;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.concurrent.atomic.AtomicInteger;
import org.springframework.http.client.JdkClientHttpRequestFactory;
import org.springframework.http.client.reactive.JdkClientHttpConnector;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientResponseException;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;
import reactor.core.publisher.Mono;

public class ClientComparison {
    static void check(boolean condition) {
        if (!condition) throw new AssertionError("HTTP contract failed");
    }
    public static void main(String[] args) throws Exception {
        var requests = new AtomicInteger();
        var server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        server.createContext("/", exchange -> {
            requests.incrementAndGet();
            String path = exchange.getRequestURI().getPath();
            int status = path.equals("/missing") ? 404 : path.equals("/unavailable") ? 503 : 200;
            byte[] body = (status == 200 ? "hello" : "error").getBytes(StandardCharsets.UTF_8);
            exchange.getResponseHeaders().set("Content-Type", "text/plain;charset=UTF-8");
            exchange.sendResponseHeaders(status, body.length);
            try (var output = exchange.getResponseBody()) { output.write(body); }
        });
        server.start();
        try {
            String base = "http://127.0.0.1:" + server.getAddress().getPort();
            var jdk = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(2)).build();
            var factory = new JdkClientHttpRequestFactory(jdk);
            factory.setReadTimeout(Duration.ofSeconds(2));
            var connector = new JdkClientHttpConnector(jdk);
            connector.setReadTimeout(Duration.ofSeconds(2));
            var rest = RestClient.builder().baseUrl(base).requestFactory(factory).build();
            var web = WebClient.builder().baseUrl(base).clientConnector(connector).build();

            var response = rest.get().uri("/hello").retrieve();
            check(requests.get() == 0);
            System.out.println("before-rest-terminal=" + requests.get());
            String sync = response.body(String.class);
            check("hello".equals(sync) && requests.get() == 1);
            System.out.println("rest=" + sync);

            Mono<String> pending = web.get().uri("/hello").retrieve().bodyToMono(String.class);
            check(requests.get() == 1);
            System.out.println("before-subscribe=" + requests.get());
            String first = pending.block(Duration.ofSeconds(5));
            check("hello".equals(first) && requests.get() == 2);
            System.out.println("web=" + first);
            System.out.println("after-first-subscribe=" + requests.get());
            String second = pending.block(Duration.ofSeconds(5));
            check("hello".equals(second) && requests.get() == 3);
            System.out.println("web-again=" + second);
            System.out.println("after-second-subscribe=" + requests.get());

            for (int status : new int[]{404, 503}) {
                String path = status == 404 ? "/missing" : "/unavailable";
                try {
                    rest.get().uri(path).retrieve().body(String.class);
                    throw new AssertionError("RestClient should fail");
                } catch (RestClientResponseException error) {
                    check(error.getStatusCode().value() == status);
                    System.out.println("rest-" + status + "=" + error.getStatusCode().value());
                }
                try {
                    web.get().uri(path).retrieve().bodyToMono(String.class).block(Duration.ofSeconds(5));
                    throw new AssertionError("WebClient should fail");
                } catch (WebClientResponseException error) {
                    check(error.getStatusCode().value() == status);
                    System.out.println("web-" + status + "=" + error.getStatusCode().value());
                }
            }
            check(requests.get() == 7);
            System.out.println("requests=" + requests.get());
        } finally { server.stop(0); }
    }
}
```

### Exécuter et vérifier

```sh
gradle --no-daemon --console=plain -q clean run
```

Le premier téléchargement des dépendances nécessite un accès réseau. À l’exécution, les requêtes HTTP vont uniquement vers un serveur 127.0.0.1 sur un port temporaire. Voici la sortie standard observée de l’application dans l’environnement indiqué ; Gradle ou les implémentations de journalisation peuvent émettre des diagnostics distincts.

```text
before-rest-terminal=0
rest=hello
before-subscribe=1
web=hello
after-first-subscribe=2
web-again=hello
after-second-subscribe=3
rest-404=404
web-404=404
rest-503=503
web-503=503
requests=7
```

Le passage de 0 à 1 montre que l’opération terminale RestClient a terminé la première requête. Le compteur reste à 1 juste après la construction du Mono. Chaque block s’abonne et l’augmente à 2 puis à 3. Quatre requêtes suivantes vérifient la gestion de 404 et 503, pour un total de 7. Ces décomptes vérifient les contrats d’exécution et d’erreur ; ils ne comparent ni débit, ni latence, ni performances de boucle événementielle.

## block rend-il le comportement des clients identique ?

Ajouter block à WebClient fait **attendre le résultat à l’appelant**. Cela ne rend pas l’implémentation du transport sous-jacent identique à celle de RestClient. Comme l’explique la [documentation d’usage synchrone](https://docs.spring.io/spring-framework/reference/web/webflux-webclient/client-synchronous.html), renvoyez Mono ou Flux depuis un contrôleur réactif et laissez le framework s’abonner. Les appels block ci-dessus se limitent à une méthode main console qui observe le comportement. Appeler RestClient ou attendre avec block sur une boucle événementielle peut occuper son thread de traitement ou lever une exception interdisant le blocage sur un thread non bloquant.

Si une application exploite déjà des filtres, une authentification et une instrumentation WebClient, les appels synchrones seuls n’imposent pas un remplacement immédiat. Comparez le coût de l’ajout de dépendances réactives et de la gestion des abonnements pour un nouvel appel synchrone au coût du maintien de la configuration existante. Évitez les abonnements sans limite lorsque vous combinez plusieurs appels distants. Le [contrôle de demande réactif de WebFlux](https://docs.spring.io/spring-framework/reference/web/webflux/new-framework.html) coordonne les rythmes de production et de consommation ; il n’impose pas automatiquement les limites de RPS ou de connexions d’un service en aval.

## Que vérifier avant la production ?

Les deux clients ont besoin de budgets pour la connexion, la lecture des réponses et l’appel entier, ainsi que d’une politique de statuts d’erreur. La limite de connexion de 2 secondes, les limites de lecture de 2 secondes et l’attente block de 5 secondes sont des paramètres de reproduction, pas des sémantiques de délai équivalentes ni des valeurs recommandées en production. Consultez les documentations de la [fabrique de requêtes](https://docs.spring.io/spring-framework/docs/7.0.10/javadoc-api/org/springframework/http/client/JdkClientHttpRequestFactory.html) et du [connecteur réactif](https://docs.spring.io/spring-framework/docs/7.0.10/javadoc-api/org/springframework/http/client/reactive/JdkClientHttpConnector.html) pour le périmètre de chaque délai de lecture. Ces réponses locales rapides ne valident ni les délais, ni TLS, ni la propagation de l’annulation.

L’exemple vérifie le traitement retrieve par défaut des réponses 4xx et 5xx pour les deux clients. Utilisez onStatus pour des politiques de statut explicites. Ne supposez pas que les API exchange de bas niveau appliquent le traitement de statut par défaut de retrieve. Les exemples de [gestion des réponses WebClient](/en/posts/2023-09-19-springboot-test-webclient/) et de [délais et réessais bornés](/en/posts/2026-10-30-webclient-timeout-retry/) fournissent des contrats complémentaires. Bornez les réessais par l’idempotence, le nombre de tentatives et le budget total ; testez séparément les corps vides, les grandes réponses et les échecs de connexion.

Le code RestTemplate existant est un sujet de migration distinct. Spring Framework 7.0 recommande RestClient et marque RestTemplate comme obsolète ; WebClient n’est pas obsolète. Après le choix d’un client, validez authentification, instrumentation et paramètres de connexion selon la répartition réelle des requêtes.
