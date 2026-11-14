---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2026-11-09-spring-mvc-webclient-execution",
  "routeSlug": "2026-11-09-spring-mvc-webclient-execution",
  "kind": "post",
  "title": "WebClient dans Spring MVC : traitements bloquant et asynchrone",
  "description": "Comprendre WebClient et Reactor Netty dans Spring MVC : .block(), retour Mono, Servlet asynchrone et threads virtuels.",
  "categories": [
    "springboot"
  ],
  "tags": [
    "spring-mvc",
    "webclient",
    "reactor-netty",
    "servlet-async",
    "virtual-threads"
  ],
  "sourcePath": "src/content/posts/en/2026-11-09-spring-mvc-webclient-execution.md",
  "sourceSha256": "6f81dd9e98a391f7b05ca1d0fef8c01ca8288550531caf852ae518c60843dba8",
  "draftSha256": "4e564e1dffe80014460d19d681851f083f27df79c3bd5c415a83475cca14b59f",
  "manifestPath": ".pipeline/technical-translations/batch-156/manifest.json",
  "manifestSha256": "ed48dc20825daff8725d8eba3418b1ad885276b52c9752ba958f7a1705b24430",
  "publishedAt": "2026-11-14T15:16:43.783Z",
  "updatedAt": "2026-11-14T15:16:43.783Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 158,
    "approvedAt": "2026-11-14T15:16:43.783Z",
    "basis": "User requested all 63 language editions and instructed completed PRs to be merged; AI translation and independent AI review were performed, with no claim of human text review."
  }
}
---

**WebClient peut utiliser une communication HTTP non bloquante dans Spring MVC, mais appeler `.block()` dans un contrôleur fait attendre le thread de requête MVC.** Renvoyer le `Mono` permet à MVC de l’adapter au traitement asynchrone Servlet et de libérer le thread initial. Communication client et traitement serveur sont deux responsabilités distinctes.

Cet article traite de **Spring MVC sur Tomcat et de WebClient avec Reactor Netty**. Un autre connecteur HTTP peut employer d’autres noms de threads et ressources. L’exemple est reproduit avec Spring Boot 3.5.16, JDK 21 et Gradle 8.14.3 ; il ne vérifie pas chaque version actuelle de Boot.

## Ajouter WebClient fait-il utiliser WebFlux au serveur ?

MVC côté serveur et WebClient pour les appels sortants ont des rôles différents. Ici, Tomcat et `DispatcherServlet` traitent les requêtes entrantes, tandis que le connecteur Reactor Netty de WebClient traite le HTTP sortant.

Avec Boot 3.5, ajouter `spring-boot-starter-web` et `spring-boot-starter-webflux` sélectionne MVC par défaut. Cela permet d’ajouter le starter WebFlux pour utiliser WebClient. Vérifiez séparément si le type d’application est changé explicitement ou si une autre configuration serveur est utilisée. [Sélection MVC et WebFlux de Boot](https://docs.spring.io/spring-boot/3.5/reference/web/reactive.html#web.reactive.webflux)

## Où divergent `.block()` et le retour de `Mono` ?

![Dans le chemin block, le thread de requête Servlet attend pendant que Netty gère HTTP. Dans le chemin de retour Mono, après souscription par MVC, la communication Netty peut chevaucher le traitement asynchrone Servlet et MVC redistribue le résultat.](/assets/diagrams/technical/fr-2026-11-09-spring-mvc-webclient-execution.svg)

Le vert indique les responsabilités Servlet et MVC ; le bleu représente Reactor Netty. Les deux branches asynchrones peuvent se chevaucher : la réponse externe n’arrive pas nécessairement après le retour du thread initial. Le schéma se concentre sur les signaux de succès ; dans le code, les signaux d’erreur sont associés à des codes HTTP avant le traitement d’erreur MVC.

| Étape | Renvoyer une valeur après `.block()` | Renvoyer `Mono` |
| --- | --- | --- |
| Souscription | Effectuée par `.block()` | MVC souscrit au type retourné |
| Attente du HTTP sortant | Le thread de requête attend | Le traitement Servlet asynchrone peut libérer le thread initial |
| Après réception du corps | Le callback client fournit le résultat et met fin à l’attente | Le signal de résultat est transmis au traitement MVC asynchrone |
| Réponse HTTP finale | MVC sérialise et écrit la valeur | MVC redistribue puis sérialise et écrit |

`retrieve().bodyToMono(...)` assemble le pipeline de requête. Le pipeline WebClient nouvellement créé ci-dessous doit recevoir une souscription avant de lancer une requête HTTP. Deux souscriptions peuvent provoquer une autre requête ; attention au code qui lit une fois avec `.block()` puis renvoie le pipeline.

MVC adapte un `Mono` à valeur unique de façon similaire à `DeferredResult`. Lorsque le résultat est prêt, il redistribue vers le conteneur Servlet pour terminer la réponse. Le pool peut réutiliser le même thread ; ne supposez donc pas que celui de la redistribution doit être différent de l’original. La connexion et les ressources asynchrones restent également présentes tant que la réponse est ouverte. Renvoyer `Mono` ne rend pas toute l’écriture de la réponse Servlet non bloquante. L’exemple renvoie un JSON à valeur unique ; streaming et SSE sont des cas distincts. [Traitement MVC asynchrone et types réactifs](https://docs.spring.io/spring-framework/reference/6.2/web/webmvc/mvc-ann-async.html)

## Appeler la même API externe de deux façons

Enregistrez les fichiers ci-dessous dans un projet. Il utilise le plugin `application`, pas le plugin Boot Gradle, et fixe la toolchain Java à 21. Les vérifications locales utilisaient Azul JDK 21.0.1 ; cette version corrective historique n’est pas une recommandation pour de nouveaux environnements de production.

### `settings.gradle`

```groovy
rootProject.name = 'mvc-webclient-execution'
```

### `build.gradle`

```groovy
plugins {
    id 'java'
    id 'application'
}
repositories { mavenCentral() }
java { toolchain { languageVersion = JavaLanguageVersion.of(21) } }
dependencies {
    implementation platform('org.springframework.boot:spring-boot-dependencies:3.5.16')
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.boot:spring-boot-starter-webflux'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
application { mainClass = 'example.DemoApplication' }
test {
    useJUnitPlatform()
    systemProperty 'demo.virtual', providers.gradleProperty('virtual').getOrElse('false')
}
```

### `src/main/resources/application.yml`

```yaml
upstream:
  base-url: http://127.0.0.1:9091
  timeout: 3s
spring:
  mvc:
    async:
      request-timeout: 5s
```

`WebClient` est réutilisé comme bean et emploie explicitement le connecteur Reactor Netty. Dans cet exemple, `HttpClient.create()` utilise l’event loop et le pool de connexions partagés par défaut ; il ne crée pas un thread Netty dédié à chaque requête sortante. `callbackThread` exécute `map` après production du corps, sans être nécessairement le thread écrivant la réponse Servlet finale. Aucun changement de scheduler comme `publishOn` n’est ajouté. [Connecteurs WebClient et ressources partagées](https://docs.spring.io/spring-framework/reference/6.2/web/webflux-webclient/client-builder.html)

### `src/main/java/example/DemoApplication.java`

```java
package example;

import java.time.Duration;
import java.util.concurrent.TimeoutException;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.http.HttpStatus;
import org.springframework.http.client.reactive.ReactorClientHttpConnector;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;
import org.springframework.web.server.ResponseStatusException;

import reactor.core.publisher.Mono;
import reactor.core.scheduler.Schedulers;
import reactor.netty.http.client.HttpClient;

@SpringBootApplication
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }

    @Bean
    WebClient upstreamClient(WebClient.Builder builder,
                             @Value("${upstream.base-url}") String baseUrl) {
        return builder.baseUrl(baseUrl)
                .clientConnector(new ReactorClientHttpConnector(HttpClient.create()))
                .build();
    }

    public record Observation(String mode, String requestThread, boolean requestVirtual,
                              String callbackThread, boolean callbackVirtual, boolean callbackNonBlocking,
                              String value) {}

    @RestController
    static class DemoController {
        private final WebClient client;
        private final Duration deadline;

        DemoController(WebClient client, @Value("${upstream.timeout}") Duration deadline) {
            this.client = client;
            this.deadline = deadline;
        }

        private Mono<Observation> fetch(String mode) {
            Thread request = Thread.currentThread();
            String name = request.getName();
            boolean virtual = request.isVirtual();
            return client.get().uri("/value").retrieve().bodyToMono(String.class)
                    .timeout(deadline)
                    .map(value -> new Observation(mode, name, virtual,
                            Thread.currentThread().getName(), Thread.currentThread().isVirtual(),
                            Schedulers.isInNonBlockingThread(), value))
                    .onErrorMap(WebClientResponseException.class, error ->
                            new ResponseStatusException(HttpStatus.BAD_GATEWAY,
                                    "upstream HTTP error", error))
                    .onErrorMap(TimeoutException.class, error ->
                            new ResponseStatusException(HttpStatus.GATEWAY_TIMEOUT,
                                    "upstream deadline", error));
        }

        @GetMapping("/block")
        Observation blocking() {
            return fetch("block").block();
        }

        @GetMapping("/async")
        Mono<Observation> asynchronous() {
            return fetch("async");
        }
    }
}
```

`/block` est un chemin de comparaison. Un contrôleur pouvant terminer avec un retour asynchrone peut renvoyer le `Mono` résultant comme `/async`, pour que MVC y souscrive. Appeler directement `.subscribe()` puis répondre d’abord sépare le résultat sortant et son erreur de la requête HTTP d’origine. [Usage synchrone de WebClient et retours contrôleur](https://docs.spring.io/spring-framework/reference/web/webflux-webclient/client-synchronous.html)

Le `timeout` de trois secondes de l’exemple limite l’intervalle entre souscription et livraison d’une valeur. Il ne configure pas séparément les délais d’acquisition du pool, de connexion ou de chaque lecture de réponse. Les erreurs HTTP deviennent 502 et un délai de pipeline expiré devient 504. Définissez des contrats distincts pour erreurs de connexion, corps vides et erreurs métier. Par défaut, `retrieve()` traite les réponses HTTP 4xx et 5xx comme erreurs. [Erreurs de retrieve](https://docs.spring.io/spring-framework/reference/6.2/web/webflux-webclient/client-retrieve.html)

### Exécution locale

Démarrez un serveur HTTP Python 3 local à la place d’un service externe. `/value` renvoie `hello` après 0,2 seconde. Ce délai est une entrée d’observation, pas une mesure de performance.

### `upstream.py`

```python
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from time import sleep


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != '/value':
            self.send_error(404)
            return
        sleep(0.2)
        body = b'hello'
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


ThreadingHTTPServer(('127.0.0.1', 9091), Handler).serve_forever()
```

Exécutez-le dans le premier terminal.

```sh
python3 upstream.py
```

Dans le deuxième terminal, sélectionnez JDK 21 et lancez avec Gradle 8.14.3.

```sh
gradle run
```

Dans le troisième terminal, appelez les deux chemins :

```sh
curl --fail --show-error --silent http://127.0.0.1:8080/block
curl --fail --show-error --silent http://127.0.0.1:8080/async
```

Les deux renvoient du JSON contenant `hello`. Avec des threads de requête ordinaires, `requestVirtual=false` a été observé ; le callback Netty de cet exemple avait `callbackVirtual=false` et `callbackNonBlocking=true`. Noms et numéros exacts des threads varient selon l’exécution. Le seul champ `mode` du JSON ne prouve pas que le thread de requête a été libéré pendant l’attente.

## Que change l’activation des threads virtuels ?

Après avoir arrêté l’application précédente, relancez le même code avec les réglages de threads virtuels.

```sh
gradle run --args='--spring.threads.virtual.enabled=true'
```

Avec ce réglage, `requestVirtual` est devenu `true` sur les deux chemins. Sur le chemin `.block()`, le thread virtuel appelant attend toujours le résultat, mais une attente normalement suspendable diffère de l’occupation continue d’un thread plateforme porteur. Vérifiez séparément le pinning et les différences du JDK utilisé. [Ordonnancement et pinning dans JDK 21](https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html) **L’activation des threads virtuels n’a pas transformé le callback Reactor Netty de cet exemple en thread virtuel.** [Configuration Boot des threads virtuels](https://docs.spring.io/spring-boot/3.5/reference/features/spring-application.html#features.spring-application.virtual-threads)

Les threads virtuels n’augmentent ni la capacité de traitement d’un service externe, ni le nombre de connexions HTTP ou DB. Concevez séparément une limite des requêtes accumulées, comme dans [les sémaphores DB et l’admission](/ko/posts/2026-11-03-virtual-threads-db-semaphore/).

## Peut-on appeler JDBC dans un callback ?

Appeler WebClient depuis MVC ne signifie pas que le `map` suivant tourne sur le thread de requête MVC. Placer une requête JDBC ou une longue lecture de fichier dans le `map` de cet exemple peut bloquer l’event loop Netty. À l’inverse, chaque `Mono` ne tourne pas sur un thread dédié. L’exécution des opérateurs dépend de la souscription, des signaux et des changements de scheduler. [Threads et schedulers Reactor](https://projectreactor.io/docs/core/release/reference/coreFeatures/schedulers.html)

Pour un service comportant de nombreuses opérations synchrones, comparez la limitation des ressources dans le flux MVC synchrone à l’isolation du travail bloquant sur un executor séparé tout en conservant une chaîne asynchrone. Pour les appels HTTP synchrones simples, voir aussi [choisir RestClient ou WebClient](/ko/posts/2026-10-31-webclient-restclient-comparison/). Un changement de scheduler seul ne résout pas une surcharge DB ou de service aval.

## Ce qui a réellement été vérifié

Les [tests de vérification](https://github.com/youdozi/youdozi.github.io/blob/main/.pipeline/drafts/2026-11-09-spring-mvc-webclient-execution/src/test/java/example/ExecutionTest.java) ont utilisé **un vrai Tomcat et un serveur HTTP local** sur des ports aléatoires. Seize vérifications ont réussi : huit avec des threads de requête ordinaires et huit avec des threads virtuels.

- Sélection du contexte Servlet, de Tomcat et de DispatcherServlet avec les deux starters
- Aucune requête à l’assemblage du pipeline ; requêtes lors de la souscription et de la nouvelle souscription
- Attente du thread de requête pour `.block()` et entrée en traitement Servlet asynchrone pour `Mono` tant que la réponse externe est retenue
- Caractère virtuel des threads de requête et non bloquant ou virtuel des callbacks
- Association des erreurs HTTP à 502 et des délais de pipeline à 504 pour les deux chemins

Pour exécuter les tests vous-même, enregistrez le code de vérification ci-dessus sous `src/test/java/example/ExecutionTest.java` puis lancez-le.

```sh
gradle clean test
gradle test -Pvirtual=true --rerun-tasks
```

Les tests observent l’état à l’aide d’un latch qui retient la réponse ; ils ne déduisent pas l’asynchronie d’une courte durée. Ils ne vérifient ni comparaison de débit, ni vrais services externes, DB ou TLS, ni déconnexion du client ou annulation des effets distants. En particulier, annuler le pipeline ne garantit ni l’arrêt du travail d’un serveur distant ni le rollback d’une transaction.
