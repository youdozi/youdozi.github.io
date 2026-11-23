---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2026-11-22-spring-boot-4-2-restclient-traceparent",
  "routeSlug": "2026-11-22-spring-boot-4-2-restclient-traceparent",
  "kind": "post",
  "title": "Vérifier la propagation de traceparent avec RestClient dans Spring Boot 4.2",
  "description": "Comparez la propagation de traceparent et les relations entre spans dans Tempo pour deux modes de création de RestClient dans Spring Boot 4.2.0.",
  "categories": [
    "springboot"
  ],
  "tags": [
    "spring-boot",
    "restclient",
    "opentelemetry",
    "micrometer",
    "tempo",
    "distributed-tracing"
  ],
  "sourcePath": "src/content/posts/en/2026-11-22-spring-boot-4-2-restclient-traceparent.md",
  "sourceSha256": "79632a97012abbc73db2e3e1a0bbe924c261ceb52f4603146310d3e2c4f897f5",
  "draftSha256": "b7d7b6d9d4a6c98db8bc42b87e2fed5839a3148d6c6d0b6bab898546d616a0a1",
  "manifestPath": ".pipeline/technical-translations/batch-185/manifest.json",
  "manifestSha256": "3281e1d3e7c9b3abbb6c101d911dd0fcdee7dd54f7034838135f391123b6fb44",
  "publishedAt": "2026-11-23T00:19:14.218Z",
  "updatedAt": "2026-11-23T00:19:14.218Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 185,
    "approvedAt": "2026-11-23T00:19:14.218Z",
    "basis": "The site owner explicitly requested missing supported locales for the eight articles published in PRs #177–#184. This authorizes publication of the 48 editions enumerated in this batch."
  }
}
---

**Pour suivre dans une même trace la recherche d’un produit et son appel au service de stock, utilisez le `RestClient.Builder` injecté par Spring Boot.** Dans l’exemple, le client construit avec `RestClient.create()` cherche le même produit et renvoie aussi HTTP 200. L’API de stock ne reçoit aucun en-tête `traceparent` et commence une trace distincte. Comparez les réponses HTTP et les spans enregistrés dans Tempo pour repérer où le contexte cesse de se propager. [Documentation Spring Boot sur la propagation des traces](https://docs.spring.io/spring-boot/4.2/reference/actuator/tracing.html#actuator.micrometer-tracing.propagating-traces)

Cet exercice reprend la recherche de produit du [guide de migration vers RestClient](/en/posts/2026-11-22-spring-boot-4-2-restclient-migration/). Le [guide des métriques HTTP](/en/posts/2026-11-22-spring-boot-4-2-otel-http-metrics/) compte les requêtes. Ici, vous suivez le parcours d’une seule requête.

## L’en-tête qui relie la recherche du produit et la consultation du stock

`traceparent` est l’en-tête HTTP normalisé par le W3C pour transmettre le contexte de trace. Dans cet exercice, il prend la forme `00-<trace-id>-<parent-id>-<trace-flags>`. Le `trace-id` identifie la trace entière. Le `parent-id` identifie le span HTTP du client émetteur pour que le service destinataire puisse l’utiliser comme parent de son span serveur. [Spécification W3C Trace Context](https://www.w3.org/TR/trace-context/#traceparent-header)

![L’application de recherche de produit appelle l’API de stock. Le builder de Boot envoie traceparent et relie les applications dans une seule trace. Le client créé directement n’envoie pas l’en-tête. L’API de stock commence alors une trace distincte.](/assets/diagrams/technical/fr-2026-11-22-spring-boot-4-2-restclient-traceparent.svg)

Le schéma montre les deux parcours client pour le produit 42. Les deux renvoient la même quantité en stock. Dans cet exemple, l’en-tête `traceparent` détermine si le span du serveur de stock rejoint la trace de recherche du produit.

## Exécuter le même JAR comme deux applications

Il vous faut JDK 21, Maven, Docker, `curl` et `jq`. L’exercice utilise les ports locaux `13200`, `14318`, `18180` et `18181`. Créez les fichiers suivants dans un répertoire vide. Exécutez le même JAR avec le nom de service `product`, puis avec le nom `inventory`. Les réponses incluent les identifiants de trace courants et l’en-tête reçu pour que vous puissiez les examiner.

### `pom.xml`

```xml
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>4.2.0</version>
    </parent>
    <groupId>example</groupId>
    <artifactId>trace-propagation</artifactId>
    <version>1.0.0</version>
    <properties>
        <java.version>21</java.version>
    </properties>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-webmvc</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-restclient</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-opentelemetry</artifactId>
        </dependency>
    </dependencies>
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
```

### `src/main/java/example/TraceApplication.java`

```java
package example;

import io.micrometer.tracing.Tracer;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestClient;

@SpringBootApplication
public class TraceApplication {
    public static void main(String[] args) {
        SpringApplication.run(TraceApplication.class, args);
    }
}

@RestController
class ProductController {
    private final RestClient bootClient;
    private final RestClient directClient;
    private final Tracer tracer;

    ProductController(RestClient.Builder builder, Tracer tracer,
            @Value("${inventory.base-url}") String inventoryUrl) {
        this.bootClient = builder.baseUrl(inventoryUrl).build();
        this.directClient = RestClient.create(inventoryUrl);
        this.tracer = tracer;
    }

    @GetMapping("/products/{id}")
    ProductReply product(@PathVariable("id") long id,
            @RequestParam("instrumented") boolean instrumented) {
        RestClient client = instrumented ? bootClient : directClient;
        InventoryReply inventory = client.get().uri("/items/{id}", id)
            .retrieve().body(InventoryReply.class);
        return new ProductReply(tracer.currentSpan().context().traceId(), inventory);
    }
}

@RestController
class InventoryController {
    private final Tracer tracer;

    InventoryController(Tracer tracer) {
        this.tracer = tracer;
    }

    @GetMapping("/items/{id}")
    InventoryReply item(@PathVariable("id") long id,
            @RequestHeader(name = "traceparent", required = false) String traceparent) {
        return new InventoryReply(id, 7, traceparent, tracer.currentSpan().context().traceId());
    }
}

record ProductReply(String productTraceId, InventoryReply inventory) {}
record InventoryReply(long id, int stock, String traceparent, String inventoryTraceId) {}
```

### `src/main/resources/application.properties`

```properties
server.address=127.0.0.1
inventory.base-url=http://127.0.0.1:18181
management.tracing.sampling.probability=1.0
management.opentelemetry.tracing.export.otlp.endpoint=http://127.0.0.1:14318/v1/traces
management.otlp.metrics.export.enabled=false
```

Une probabilité d’échantillonnage de `1.0` enregistre toutes les requêtes de cet exercice. Les applications exportent uniquement les traces via OTLP. Commencez par vérifier l’en-tête dans la réponse HTTP pour distinguer les spans manquants dans Tempo d’un problème de propagation. [Documentation Spring Boot sur l’échantillonnage](https://docs.spring.io/spring-boot/4.2/reference/actuator/tracing.html#actuator.micrometer-tracing.sampling)

### `tempo.yaml`

Cette configuration permet à Tempo de recevoir des spans via OTLP HTTP et de les écrire dans le stockage local. L’API de consultation et les ports de réception sont exposés uniquement sur l’adresse de bouclage de l’hôte.

```yaml
server:
  http_listen_port: 3200

distributor:
  receivers:
    otlp:
      protocols:
        http:
          endpoint: 0.0.0.0:4318

storage:
  trace:
    backend: local
    wal:
      path: /tmp/tempo/wal
    local:
      path: /tmp/tempo/blocks
```

Démarrez Tempo et les applications depuis la racine du projet. Démarrez Tempo dans le premier terminal.

```sh
docker run --rm --name traceparent-tempo \
  -p 127.0.0.1:13200:3200 -p 127.0.0.1:14318:4318 \
  --mount "type=bind,source=$PWD/tempo.yaml,target=/etc/tempo.yaml,readonly" \
  grafana/tempo:2.9.0 -config.file=/etc/tempo.yaml
```

Dans un autre terminal, vérifiez que `curl -fsS http://127.0.0.1:13200/ready` réussit, puis construisez avec Maven. Exécutez les deux commandes `java` dans des terminaux distincts.

```sh
mvn package

java -jar target/trace-propagation-1.0.0.jar \
  --spring.application.name=inventory --server.port=18181

java -jar target/trace-propagation-1.0.0.jar \
  --spring.application.name=product --server.port=18180
```

## Comparer les en-têtes et les identifiants de trace des réponses

Une fois les deux applications démarrées, recherchez deux fois le même produit. Modifiez uniquement `instrumented` pour choisir le client.

```sh
curl -fsS 'http://127.0.0.1:18180/products/42?instrumented=true' -o boot.json
curl -fsS 'http://127.0.0.1:18180/products/42?instrumented=false' -o direct.json

jq '{id: .inventory.id, stock: .inventory.stock,
     headerReceived: (.inventory.traceparent != null),
     sameTrace: (.productTraceId == .inventory.inventoryTraceId)}' boot.json direct.json
jq -r .inventory.traceparent boot.json
```

Les deux requêtes ont renvoyé HTTP 200. Avec le builder de Boot, les deux applications avaient le même identifiant de trace et l’en-tête `traceparent` reçu par l’API de stock contenait cet identifiant. Avec le client créé directement, l’API de stock a signalé `traceparent` à `null` et les deux applications avaient des identifiants de trace différents.

| Mode de création du client | ID du produit et stock | En-tête reçu | Identifiants de trace des applications |
| --- | --- | --- | --- |
| `RestClient.Builder` injecté par Boot | 42 et 7 | Oui | Identiques |
| `RestClient.create()` | 42 et 7 | Non | Différents |

## Vérifier les spans dans Tempo

Interrogez Tempo avec les identifiants de trace des réponses. L’exportation de spans peut prendre quelques secondes. Si une trace manque, attendez un instant et relancez la requête. [API Grafana Tempo de recherche des traces par identifiant](https://grafana.com/docs/tempo/latest/api_docs/#query)

```sh
show_spans() {
  curl -fsS "http://127.0.0.1:13200/api/traces/$1" | jq -r '
    (.batches // .resourceSpans)[] as $batch
    | ($batch.resource.attributes[]
       | select(.key == "service.name").value.stringValue) as $service
    | $batch.scopeSpans[].spans[]
    | [$service, .kind, .name, .spanId, (.parentSpanId // "-")] | @tsv'
}

show_spans "$(jq -r .productTraceId boot.json)"
show_spans "$(jq -r .productTraceId direct.json)"
show_spans "$(jq -r .inventory.inventoryTraceId direct.json)"
```

L’exemple a été exécuté avec Spring Boot 4.2.0, JDK 21.0.1, Maven 3.9.11 et Tempo 2.9.0. L’API Tempo a renvoyé les spans suivants pour les trois identifiants issus des deux requêtes.

| Identifiant de trace recherché | Spans observés dans Tempo |
| --- | --- |
| Requête utilisant le builder de Boot | Serveur produit → client HTTP produit → serveur de stock |
| Application produit avec le client créé directement | Un span racine du serveur produit |
| Application de stock avec le client créé directement | Un span racine du serveur de stock |

Avec le builder de Boot, le `parentSpanId` du serveur de stock dans Tempo correspondait au `spanId` du client HTTP produit. Lors de cette exécution, la réponse de l’API Tempo encodait les identifiants des spans en Base64, tandis que `traceparent` utilise l’hexadécimal. Une fois décodés depuis Base64 et représentés en hexadécimal, les octets de l’identifiant du span client donnaient la même valeur que le `parent-id` de l’en-tête.

Si les requêtes aboutissent mais qu’une trace s’arrête à la frontière d’un service, vérifiez que le service destinataire reçoit `traceparent`. Si l’en-tête est absent, vérifiez que l’appelant utilise le builder configuré par Boot. Si l’identifiant de trace se propage mais que des spans manquent dans Tempo, vérifiez les paramètres d’échantillonnage et d’exportation OTLP. Vous pouvez ensuite retrouver les journaux avec le même identifiant en suivant [Corréler les journaux et les traces dans Grafana LGTM](/en/posts/2026-11-02-grafana-lgtm-log-trace/).
