---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2026-11-10-redis-lua-rate-limit",
  "routeSlug": "2026-11-10-redis-lua-rate-limit",
  "kind": "post",
  "title": "Limiter les requêtes avec Redis et Lua : décision et compteur atomiques",
  "description": "Implémenter une fenêtre fixe avec Spring MVC et Redis Lua ; comprendre admission atomique, TTL, 429, 503 et limites en production.",
  "categories": [
    "springboot"
  ],
  "tags": [
    "redis",
    "rate-limit",
    "lua",
    "spring-mvc",
    "distributed-systems"
  ],
  "sourcePath": "src/content/posts/en/2026-11-10-redis-lua-rate-limit.md",
  "sourceSha256": "bffe243d3ec0d2693086eb4d708c74490b34a27af7c1735cf6a41c81eea561d5",
  "draftSha256": "010eec190ab9d7ffd04d7c5f984f81bd75bc75b02b681aa5f2d91cbb37fd4221",
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

**Pour limiter les requêtes d’un même utilisateur sur plusieurs serveurs applicatifs, prenez la décision d’admission et mettez à jour le compteur ensemble dans Redis.** Cet article implémente une fenêtre fixe en Lua, avec `429` lorsque la limite est dépassée et `503` lorsque Redis ne peut déterminer le résultat.

La règle d’exemple autorise **au plus trois requêtes par compte pendant les 10 secondes suivant la première requête autorisée**. Une fenêtre fixe est ici le point de départ le plus simple ; elle n’équivaut ni à un seau à jetons ni à une fenêtre glissante. L’environnement utilise Spring Boot 3.5.16, JDK 21, Gradle 8.14.3 et Redis 8.2.1. Ces versions sont fixées pour la reproduction, pas recommandées comme correctifs de production les plus récents.

## Pourquoi ne pas utiliser GET puis INCR dans l’application ?

Si les serveurs A et B lisent tous deux un compteur à `2`, ils peuvent autoriser les deux requêtes alors que la limite est `3`. Le `synchronized` de la JVM ne verrouille pas les autres processus. `INCR` est atomique, mais n’inclut pas automatiquement la décision d’admission précédente.

Un `EXPIRE` séparé après `INCR` pose un autre problème : si le client s’arrête entre les commandes, la clé peut rester sans TTL. L’[exemple officiel Redis de limitation avec INCR](https://redis.io/docs/latest/commands/incr/) explique aussi cette concurrence et l’usage de Lua.

À la première requête, le script ci-dessous crée ensemble valeur et TTL avec `SET ... PX`. Pour les suivantes, il vérifie la limite dans Lua et n’incrémente que les requêtes autorisées. Les requêtes refusées ne changent ni compteur ni expiration.

## Dans quel ordre la limite s’applique-t-elle ?

![Le serveur choisit une clé de limitation ; Redis Lua vérifie son compteur et sa TTL. Si la requête est autorisée, SET PX ou INCR l’enregistre et l’application renvoie 200 ; en cas de dépassement elle renvoie 429 et Retry-After sans changer l’état. Une erreur de connexion ou d’état renvoie 503.](/assets/diagrams/technical/fr-2026-11-10-redis-lua-rate-limit.svg)

La zone bleue représente la décision dans Redis ; l’application crée la réponse HTTP. Une clé absente démarre une nouvelle fenêtre. Une clé existante doit contenir un compteur entier positif et une TTL valide. La limite compte les admissions, et un compte n’est pas remboursé si le travail échoue après admission.

## Implémenter la limite avec Spring MVC et Redis Lua

Enregistrez ces six fichiers dans un projet Gradle. L’authentification n’est pas implémentée. `/demo` traite chaque requête comme le même `demo-account` : la clé est donc un exemple fixe reproduisant une politique par utilisateur. Le serveur n’écoute qu’une adresse locale.

Dans un vrai service, dérivez la clé d’une **identité vérifiée par le serveur**, comme un `Principal` authentifié. Faire confiance à un en-tête `userId` arbitraire permet de contourner la limite en le changeant. Par exemple, `rl:orders:v1:<tenant-and-subject-digest>` peut distinguer périmètre d’opération, version de politique et sujet ; envisagez un identifiant comme un HMAC à secret serveur plutôt que des données personnelles brutes. N’interprétez les en-têtes IP transmis qu’à l’intérieur d’une limite de proxy de confiance.

### `settings.gradle`

```groovy
rootProject.name = 'redis-lua-rate-limit'
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
    implementation 'org.springframework.boot:spring-boot-starter-data-redis'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
application { mainClass = 'example.RateLimitApplication' }
test {
    useJUnitPlatform()
    systemProperty 'demo.redis.port', providers.gradleProperty('redisPort').getOrElse('6379')
}
```

### `src/main/resources/application.yml`

```yaml
server:
  address: 127.0.0.1
spring:
  data:
    redis:
      host: 127.0.0.1
      port: ${REDIS_PORT:6379}
      connect-timeout: 200ms
      timeout: 200ms
```

### `src/main/resources/rate-limit.lua`

```lua
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
if not limit or limit < 1 or limit > 1000000 or limit ~= math.floor(limit)
   or not window or window < 1 or window > 3600000 or window ~= math.floor(window) then
    return redis.error_reply('invalid rate limit policy')
end

local raw = redis.call('GET', KEYS[1])
if raw then
    local count = tonumber(raw)
    local ttl = redis.call('PTTL', KEYS[1])
    if not count or count < 1 or count ~= math.floor(count) or ttl < 0 then
        return redis.error_reply('invalid counter state')
    end
    if count >= limit then
        return {0, 0, ttl}
    end
    local updated = redis.call('INCR', KEYS[1])
    return {1, limit - updated, ttl}
end

redis.call('SET', KEYS[1], 1, 'PX', window)
return {1, limit - 1, window}
```

### `src/main/java/example/RedisRateLimiter.java`

```java
package example;

import java.time.Duration;
import java.util.List;
import org.springframework.core.io.ClassPathResource;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.script.DefaultRedisScript;
import org.springframework.stereotype.Component;

@Component
public class RedisRateLimiter {
    private static final DefaultRedisScript<List> SCRIPT = new DefaultRedisScript<>();
    static {
        SCRIPT.setLocation(new ClassPathResource("rate-limit.lua"));
        SCRIPT.setResultType(List.class);
    }
    private final StringRedisTemplate redis;

    public RedisRateLimiter(StringRedisTemplate redis) {
        this.redis = redis;
    }

    public Decision check(String key, int limit, Duration window) {
        long milliseconds = window.toMillis();
        if (key == null || key.isBlank() || key.length() > 160 || limit < 1 || limit > 1_000_000
                || milliseconds < 1 || milliseconds > 3_600_000) {
            throw new IllegalArgumentException("Invalid rate limit policy");
        }
        List<?> result = redis.execute(SCRIPT, List.of(key),
                Integer.toString(limit), Long.toString(milliseconds));
        if (result == null || result.size() != 3) {
            throw new IllegalStateException("Invalid limiter result");
        }
        return new Decision(((Number) result.get(0)).longValue() == 1,
                ((Number) result.get(1)).longValue(), ((Number) result.get(2)).longValue());
    }

    public record Decision(boolean allowed, long remaining, long ttlMillis) {
        public long retryAfterSeconds() {
            return Math.max(1, (ttlMillis + 999) / 1000);
        }
    }
}
```

### `src/main/java/example/RateLimitApplication.java`

```java
package example;

import java.time.Duration;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.dao.DataAccessException;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
@RestController
public class RateLimitApplication {
    private final RedisRateLimiter limiter;

    public RateLimitApplication(RedisRateLimiter limiter) {
        this.limiter = limiter;
    }

    public static void main(String[] args) {
        SpringApplication.run(RateLimitApplication.class, args);
    }

    @GetMapping("/demo")
    public ResponseEntity<String> demo() {
        try {
            var decision = limiter.check("rl:demo:v1:demo-account", 3, Duration.ofSeconds(10));
            if (!decision.allowed()) {
                return ResponseEntity.status(429)
                        .header("Retry-After", Long.toString(decision.retryAfterSeconds()))
                        .body("rate limit exceeded\n");
            }
            return ResponseEntity.ok("ok\n");
        } catch (DataAccessException | IllegalStateException unavailable) {
            return ResponseEntity.status(503).body("limiter unavailable\n");
        }
    }
}
```

Ce script utilise une clé. Dans Redis Cluster, il s’exécute dans le slot de cette clé. Étendre un script à plusieurs clés exige une nouvelle conception tenant compte de la contrainte de même slot.

`StringRedisTemplate` utilise des clés et arguments textuels ; le tableau numérique du script est renvoyé sous forme de `List`. La raison de réutiliser `DefaultRedisScript` et l’exécution par défaut de `EVALSHA`, suivie de `EVAL` en cas d’absence du cache, figurent dans la [documentation des scripts Spring Data Redis](https://docs.spring.io/spring-data/redis/reference/redis/scripting.html).

## Quelles réponses attendre ?

Exécutez l’exemple avec Docker disponible, le port Redis `16379` et le port applicatif `8080` libres. Redis n’est exposé que sur l’adresse loopback de l’hôte ; persistance et volumes persistants sont désactivés. La première exécution télécharge l’image Redis et les dépendances Maven, ce qui nécessite le réseau.

```sh
docker run --rm -d --name redis-rate-limit-demo \
  -p 127.0.0.1:16379:6379 \
  redis:8.2.1-alpine@sha256:987c376c727652f99625c7d205a1cba3cb2c53b92b0b62aade2bd48ee1593232 \
  redis-server --save '' --appendonly no
REDIS_PORT=16379 gradle run
```

Une fois le serveur prêt, effectuez quatre appels en 10 secondes depuis un autre terminal.

```sh
for attempt in 1 2 3 4; do
  curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8080/demo
done
curl -i http://127.0.0.1:8080/demo
```

Ces quatre requêtes envoyées à la suite dans une nouvelle fenêtre devraient produire les codes suivants :

```text
200
200
200
429
```

Le `Retry-After` du refus est la TTL restante arrondie à la seconde entière supérieure, avec un minimum d’une seconde. Sa valeur varie selon l’heure de l’appel. La signification de `429` et de l’éventuel `Retry-After` suit [RFC 6585 section 4](https://www.rfc-editor.org/rfc/rfc6585#section-4). Ce n’est pas une réservation tenant compte des autres requêtes : un nouvel essai peut encore être refusé si une autre requête consomme entre-temps l’autorisation.

Arrêtez `gradle run` et supprimez le conteneur de test.

```sh
docker stop redis-rate-limit-demo
```

## Qu’a-t-on vérifié pour la concurrence et les erreurs ?

Des tests de reproduction séparés ont utilisé un vrai Redis dans Docker local et Tomcat embarqué. Ils vérifient le comportement, pas le débit.

| Condition | Résultat observé |
| --- | --- |
| 40 appels simultanés pour une clé depuis un pool de threads | 3 autorisés ; compteur Redis à 3 |
| Deux objets limiteurs utilisant le même Redis et la même clé | Limite partagée. Les objets partagent un bean client ; deux JVM séparées n’ont pas été lancées. |
| Requête après trois appels autorisés | Refus sans incrément du compteur ni prolongation de TTL |
| Autre clé de compte et clé expirée | Autre clé autorisée indépendamment ; nouvelle fenêtre après expiration |
| Valeur invalide ou clé sans TTL | Erreur sans réparation arbitraire |
| Appels HTTP réels successifs | Trois réponses 200 puis 429 avec `Retry-After` |
| Requête HTTP avec compteur invalide | 503 |
| Point TCP séparé acceptant les connexions mais ne répondant pas en Redis | Erreur du limiteur associée à 503 |

Un compteur validé doit avoir une TTL. La [documentation PTTL](https://redis.io/docs/latest/commands/pttl/) définit `-1` comme absence de TTL et `-2` comme clé absente. Ajouter silencieusement une TTL et autoriser une requête lorsque l’état est invalide pourrait cacher une erreur de politique ; cette implémentation renvoie donc une erreur.

**L’exécution atomique de Lua ne signifie pas que les écritures sont automatiquement annulées en cas d’erreur.** Distinguez isolation d’exécution et traitement des erreurs comme dans la [documentation officielle des scripts](https://redis.io/docs/latest/develop/programmability/eval-intro/). Un test de reproduction a aussi confirmé qu’une valeur restait présente après qu’un script séparé avait exécuté `SET` puis délibérément renvoyé une erreur. Le script de cet article valide entrée et état existant avant écriture ; sa seule écriture est le `SET` ou `INCR` final.

## Quelles limites et politiques d’échec choisir en production ?

**Une fenêtre fixe ne garantit pas au plus trois requêtes dans tout intervalle consécutif de 10 secondes.** Utiliser l’autorisation restante juste avant la fin d’une fenêtre puis demander aussitôt après le début de la suivante peut concentrer les requêtes sur une courte durée. Envisagez des journaux ou fenêtres glissants pour un total mobile précis sur une période, ou un seau à jetons pour régler séparément rythme moyen et rafale autorisée. Cet article n’implémente ni ne mesure ces algorithmes.

L’exemple utilise un comportement **fail-closed** : les erreurs Redis ne laissent pas passer les requêtes. Cela peut convenir lorsque le contournement est coûteux, par exemple pour les paiements, mais un problème Redis réduit aussi la disponibilité de l’API. Si la disponibilité importe davantage, par exemple pour une API de lecture, autoriser temporairement les requêtes avec un seau local limité est une autre option. L’autorisation totale peut croître avec le nombre de serveurs ; ce n’est donc pas la même garantie qu’une limite globale.

Le réglage 200ms est un délai de connexion et de commande, pas une garantie que toute la requête HTTP se termine en 200ms. Prenez séparément en compte la file, la reconnexion et l’ordonnancement. Le code n’ajoute aucune nouvelle tentative au niveau applicatif ; vérifiez aussi les politiques de reconnexion et de retransmission du client. Si Redis enregistre une admission et que la réponse est perdue, le compteur peut être consommé alors que l’appelant voit un échec. Pour ne compter qu’une fois une requête réessayée, il faut un identifiant et une politique d’idempotence distincte.

Si une clé Redis est évincée sous pression mémoire ou si son compteur est perdu au redémarrage ou lors d’une bascule, une requête ultérieure peut démarrer une nouvelle fenêtre et être autorisée. Lua atomique seul ne fournit pas une limite globale couvrant réplication et récupération. Gérez instances dédiées, limites mémoire, politique d’éviction, clés versionnant la politique, nombres de refus et d’erreurs Redis et latence de décision. Placer directement les identifiants de clés dans les étiquettes de métriques augmente aussi leur cardinalité.

Cette reproduction couvre le fonctionnement normal d’une instance Redis unique et certains traitements d’erreurs. Elle ne teste ni bascule Redis Cluster, ni plusieurs régions, ni récupération après panne réelle du processus Redis, ni performance sous charge de production. Limiter les débuts de requête ne limite pas non plus l’occupation DB concurrente ni le nombre de requêtes longues : appliquez des limites de concurrence séparées si nécessaire.
