---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2026-11-22-spring-boot-4-2-otel-http-metrics",
  "routeSlug": "2026-11-22-spring-boot-4-2-otel-http-metrics",
  "kind": "post",
  "title": "Comment les conventions OpenTelemetry modifient les métriques HTTP dans Spring Boot 4.2",
  "description": "Comparez les métriques Prometheus de Spring MVC et de RestClient dans Spring Boot 4.2.0 et adaptez une requête sur les 404 aux conventions OpenTelemetry.",
  "categories": [
    "springboot"
  ],
  "tags": [
    "spring-boot",
    "opentelemetry",
    "prometheus",
    "micrometer",
    "restclient"
  ],
  "sourcePath": "src/content/posts/en/2026-11-22-spring-boot-4-2-otel-http-metrics.md",
  "sourceSha256": "184d3ca3476cfc05571ad97d60ef35f2d4c93f54cb152df388401376edc0ef57",
  "draftSha256": "2a5505ddf39962d8fe11c720d71403fd4b4743dca070dd4deb2d00eed53d166e",
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

**Lorsque vous activez les conventions d’observation OpenTelemetry dans Spring Boot 4.2.0, la métrique Prometheus du serveur Spring MVC passe de `http_server_requests_seconds_count` à `http_server_request_duration_seconds_count`.** L’étiquette utilisée pour repérer les réponses 404 passe de `status` à `http_response_status_code`. Dans la même application, les appels de `RestClient` à une API en amont ont conservé leur nom de métrique et leurs étiquettes. Vérifiez séparément les métriques entrantes et sortantes lors de la mise à jour des tableaux de bord et des alertes. [Notes de version de Spring Boot 4.2](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.2-Release-Notes#semantic-conventions)

## Envoyer les deux mêmes requêtes avec chaque configuration

Reprenez [l’exemple de recherche de produits du guide précédent](/en/posts/2026-11-22-spring-boot-4-2-restclient-migration/). Quand l’application reçoit `GET /products/{id}`, elle utilise `RestClient` pour appeler `GET /items/{id}` sur l’API en amont. Dans cet exercice, l’identifiant `42` renvoie `200` et le nom `Keyboard`, tandis que l’identifiant `99` renvoie `404` avec un corps vide.

![La même application est lancée avec chaque convention. Chaque exécution demande les produits 42 et 99, puis enregistre la sortie Prometheus pour comparer les métriques du serveur Spring MVC et de RestClient.](/assets/diagrams/technical/fr-2026-11-22-spring-boot-4-2-otel-http-metrics.svg)

Le schéma suit les deux exécutions. Chacune envoie les mêmes requêtes et enregistre séparément la sortie Prometheus pour la comparaison.

Utilisez Spring Boot 4.2.0 et JDK 21. Copiez `pom.xml` et `src/main/java/example/CatalogApplication.java` depuis le guide précédent. Retirez la dépendance `spring-boot-starter-webmvc-test`, inutilisée ici, et ajoutez les deux dépendances ci-dessous à la liste Maven. `CatalogApplication.java` reçoit déjà le `RestClient.Builder` configuré par Boot. [Documentation Spring Boot des métriques du client HTTP](https://docs.spring.io/spring-boot/reference/actuator/metrics.html#actuator.metrics.supported.http-clients)

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>
```

Pour empaqueter l’application en JAR exécutable, ajoutez cette configuration sous `<project>` dans `pom.xml`.

```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-maven-plugin</artifactId>
        </plugin>
    </plugins>
</build>
```

Dans un terminal, démarrez un serveur local pour jouer le rôle de l’API en amont. Il sert le fichier à l’adresse `/items/42` et renvoie 404 pour `/items/99`, dont le fichier est absent. Utilisez un environnement de développement local où les deux ports sont libres.

```sh
upstream_dir=$(mktemp -d)
mkdir -p "$upstream_dir/items"
printf '%s' Keyboard > "$upstream_dir/items/42"
python3 -m http.server 18081 --bind 127.0.0.1 --directory "$upstream_dir"
```

Dans un autre terminal, construisez l’application depuis la racine du projet Maven et démarrez-la avec les conventions par défaut. Exposez le point d’accès Actuator à collecter et liez l’application à l’adresse de bouclage.

```sh
mvn package

java -jar target/restclient-migration-1.0.0.jar \
  --server.address=127.0.0.1 \
  --server.port=18080 \
  --catalog.base-url=http://127.0.0.1:18081 \
  --management.endpoints.web.exposure.include=health,prometheus
```

Après le démarrage de l’application, envoyez ces requêtes depuis un troisième terminal. Vérifiez les deux réponses, puis enregistrez la sortie de Prometheus. Elle contient les séries `_count` pour les nombres cumulés de requêtes.

```sh
curl -sS -i http://127.0.0.1:18080/products/42
curl -sS -i http://127.0.0.1:18080/products/99
curl -fsS http://127.0.0.1:18080/actuator/prometheus > default.prom
```

Arrêtez l’application et redémarrez-la avec la même commande `java -jar`, en ajoutant `--management.observations.conventions=open-telemetry`. Envoyez à nouveau les trois requêtes et enregistrez la dernière réponse dans `open-telemetry.prom`. Démarrer un nouveau processus remet à zéro les compteurs de la première exécution.

```sh
grep -E '^http_(server|client).*_count\{.*(/products/|/items/)' \
  default.prom open-telemetry.prom
```

## Ce qui a changé dans les métriques collectées

J’ai exécuté les deux configurations avec JDK 21.0.1, Maven 3.9.11, Spring Boot 4.2.0 et Tomcat embarqué. Chaque exécution a envoyé une requête qui a renvoyé `200` et une autre qui a renvoyé `404`. Les quatre réponses avaient le statut et le corps attendus.

| Métrique du serveur MVC | Conventions par défaut | Conventions OpenTelemetry |
| --- | --- | --- |
| Compteur de requêtes Prometheus | `http_server_requests_seconds_count` | `http_server_request_duration_seconds_count` |
| Étiquette de méthode HTTP | `method` | `http_request_method` |
| Étiquette de statut de réponse | `status` | `http_response_status_code` |
| Étiquette de route | `uri` | `http_route` |
| Valeur de la route dans cet exemple | `/products/{id}` | `/products/{id}` |

L’étiquette de route contient le modèle de route avec `{id}`. L’extrait montre les séries 404 collectées avec les seules étiquettes utilisées dans les requêtes. Côté serveur, le compteur de 404 valait `1` à chaque exécution.

```text
http_server_requests_seconds_count{status="404",uri="/products/{id}"} 1
http_server_request_duration_seconds_count{http_response_status_code="404",http_route="/products/{id}"} 1
```

Dans les mêmes captures, les deux configurations ont enregistré les requêtes sortantes dans `http_client_requests_seconds_count`, avec `method="GET"`, `uri="/items/{id}"` et soit `status="200"`, soit `status="404"`. Ce résultat s’applique à la combinaison de l’autoconfiguration de Boot et du `RestClient.Builder` de l’exemple. L’exercice lit les métriques dans le registre Prometheus de Micrometer. La convention d’observation et le mode d’exportation des données se configurent séparément. [Documentation Spring Boot sur l’observabilité](https://docs.spring.io/spring-boot/reference/actuator/observability.html#actuator.observability.semantic-conventions)

## Mettre à jour la requête sur les 404

Avec les conventions par défaut, un panneau Grafana peut interroger le nombre cumulé de 404 pour cette route comme suit.

```text
sum(http_server_requests_seconds_count{uri="/products/{id}",status="404"})
```

Avec les conventions OpenTelemetry, modifiez le nom de la métrique et les deux étiquettes.

```text
sum(http_server_request_duration_seconds_count{http_route="/products/{id}",http_response_status_code="404"})
```

J’ai testé les requêtes sur les séries collectées avec `promtool` de Prometheus 3.5.0. Chaque requête a renvoyé `1` avec la convention correspondante et un résultat vide avec l’autre.

Ces requêtes comparent les compteurs cumulés d’une seule application. Si un panneau en production affiche déjà un débit en requêtes par seconde sur une fenêtre récente, conservez son calcul, par exemple `rate(...[5m])`, et mettez à jour le sélecteur de métrique à l’intérieur. Tant que Prometheus collecte les anciennes et les nouvelles versions, interrogez chaque cible de déploiement pour savoir lesquelles publient encore chaque nom. [Principes des requêtes Prometheus](https://prometheus.io/docs/prometheus/latest/querying/basics/) · [Documentation Prometheus de `rate()`](https://prometheus.io/docs/prometheus/latest/querying/functions/#rate)

Si vous définissez le nom de la métrique serveur avec `management.observations.http.server.requests.name`, vérifiez d’abord les panneaux et les alertes qui utilisent le nom personnalisé. Ce paramètre est sans effet avec les conventions OpenTelemetry. Pour suivre une requête des métriques aux journaux et traces, consultez [Corréler les journaux et les traces dans Grafana LGTM](/en/posts/2026-11-02-grafana-lgtm-log-trace/). [Notes de version de Spring Boot 4.2](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.2-Release-Notes#semantic-conventions)
