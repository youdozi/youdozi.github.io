---
state: "draft"
language: "de"
translationKey: "2026-11-10-redis-lua-rate-limit"
title: "Rate-Limits mit Redis und Lua: Entscheidung und Zähler atomar verarbeiten"
description: "Ein festes Anfragefenster mit Spring MVC und Redis Lua implementieren; atomare Zulassung, TTL, 429, 503 und Betriebsgrenzen verstehen."
sourcePath: "src/content/posts/en/2026-11-10-redis-lua-rate-limit.md"
sourceSha256: "bffe243d3ec0d2693086eb4d708c74490b34a27af7c1735cf6a41c81eea561d5"
---

**Um Anfragen desselben Nutzers über mehrere Anwendungsserver hinweg zu begrenzen, treffen Sie die Zulassungsentscheidung und aktualisieren den Zähler gemeinsam in Redis.** Dieser Artikel implementiert ein festes Zeitfenster in Lua und gibt `429` bei Überschreitung und `503` zurück, wenn Redis kein Ergebnis bestimmen kann.

Die Beispielregel erlaubt **höchstens drei Anfragen pro Konto innerhalb der 10 Sekunden ab der ersten erlaubten Anfrage**. Ein festes Fenster ist hier der einfachste Ausgangspunkt; es entspricht weder einem Token-Bucket noch einem gleitenden Fenster. Die Umgebung besteht aus Spring Boot 3.5.16, JDK 21, Gradle 8.14.3 und Redis 8.2.1. Diese Versionen sind zur Reproduktion fixiert und keine Empfehlung der neuesten Produktions-Patches.

## Warum nicht GET gefolgt von INCR in der Anwendung verwenden?

Lesen Server A und B beide einen Zählerstand von `2`, können beide Anfragen erlauben, obwohl das Limit `3` ist. JVM-`synchronized` sperrt keine anderen Prozesse. `INCR` ist atomar, schließt aber die vorherige Zulassungsentscheidung nicht automatisch ein.

Ein separates `EXPIRE` nach `INCR` hat ein weiteres Problem: Stoppt der Client zwischen den Befehlen, kann der Schlüssel ohne TTL bleiben. Das [offizielle Redis-Beispiel zur Begrenzung mit INCR](https://redis.io/docs/latest/commands/incr/) erklärt ebenfalls dieses Rennen und den Einsatz von Lua.

Bei der ersten Anfrage erstellt das folgende Skript Wert und TTL zusammen mit `SET ... PX`. Bei späteren Anfragen prüft es das Limit innerhalb von Lua und erhöht den Zähler nur für erlaubte Anfragen. Abgelehnte Anfragen ändern weder Zähler noch Ablaufzeit.

## In welcher Reihenfolge wird das Limit angewendet?

![Der Server wählt einen Rate-Limit-Schlüssel; Redis Lua prüft Zähler und TTL. Bei Erlaubnis erfasst SET PX oder INCR die Anfrage und die Anwendung gibt 200 zurück. Bei Überschreitung folgen 429 und Retry-After ohne Zustandsänderung. Verbindungs- oder Zustandsfehler ergeben 503.](2026-11-10-redis-lua-rate-limit.svg)

Der blaue Bereich zeigt die Entscheidung innerhalb von Redis; die Anwendung erstellt die HTTP-Antwort. Ein fehlender Schlüssel beginnt ein neues Fenster. Ein bestehender Schlüssel muss einen positiven ganzzahligen Zähler und eine gültige TTL enthalten. Das Limit zählt Zulassungen; ein Zähler wird nicht zurückerstattet, wenn Arbeit nach Zulassung fehlschlägt.

## Limit mit Spring MVC und Redis Lua implementieren

Speichern Sie diese sechs Dateien in einem Gradle-Projekt. Authentifizierung ist nicht implementiert. `/demo` behandelt jede Anfrage als dasselbe `demo-account`; der Schlüssel ist damit ein festes Beispiel zur Reproduktion einer benutzerbezogenen Regel. Der Server bindet nur an eine lokale Adresse.

Leiten Sie in einem echten Dienst den Schlüssel von einem **serverseitig geprüften Principal** ab, etwa einem authentifizierten `Principal`. Wer einem beliebigen `userId`-Anfrage-Header vertraut, ermöglicht Anfragenden, das Limit durch Änderung zu umgehen. Zum Beispiel kann `rl:orders:v1:<tenant-and-subject-digest>` Vorgangsumfang, Regelversion und Subjekt unterscheiden; ziehen Sie statt roher personenbezogener Daten einen Kennzeichner wie einen HMAC mit Servergeheimnis vor. Interpretieren Sie weitergeleitete IP-Header nur innerhalb einer vertrauenswürdigen Proxy-Grenze.

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

Dieses Skript verwendet einen Schlüssel. In Redis Cluster läuft es im Slot dieses Schlüssels. Eine Erweiterung auf mehrere Schlüssel erfordert einen Neuentwurf unter Berücksichtigung der Same-Slot-Bedingung.

`StringRedisTemplate` verwendet String-Schlüssel und -Argumente; das numerische Array des Skripts wird als `List` zurückgegeben. Der Grund für die Wiederverwendung von `DefaultRedisScript` und das standardmäßige `EVALSHA` mit anschließendem `EVAL` bei Cache-Miss sind in der [Spring-Data-Redis-Skriptdokumentation](https://docs.spring.io/spring-data/redis/reference/redis/scripting.html) beschrieben.

## Welche Antworten sind zu erwarten?

Führen Sie das Beispiel mit verfügbarem Docker aus, wenn Redis-Port `16379` und Anwendungsport `8080` nicht durch andere Prozesse belegt sind. Redis wird nur auf der Loopback-Adresse des Hosts bereitgestellt; Persistenz und persistente Volumes sind deaktiviert. Beim ersten Lauf werden Redis-Image und Maven-Abhängigkeiten heruntergeladen, wofür Netzwerkzugriff nötig ist.

```sh
docker run --rm -d --name redis-rate-limit-demo \
  -p 127.0.0.1:16379:6379 \
  redis:8.2.1-alpine@sha256:987c376c727652f99625c7d205a1cba3cb2c53b92b0b62aade2bd48ee1593232 \
  redis-server --save '' --appendonly no
REDIS_PORT=16379 gradle run
```

Senden Sie nach Serverstart vier Aufrufe innerhalb von 10 Sekunden aus einem anderen Terminal.

```sh
for attempt in 1 2 3 4; do
  curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8080/demo
done
curl -i http://127.0.0.1:8080/demo
```

Werden diese vier Anfragen in einem neuen Fenster unmittelbar nacheinander gesendet, sollten folgende Statuscodes entstehen:

```text
200
200
200
429
```

`Retry-After` der Ablehnung ist die verbleibende TTL, auf ganze Sekunden aufgerundet, mindestens eine Sekunde. Der Wert hängt vom Aufrufzeitpunkt ab. Die Bedeutung von `429` und dem optionalen `Retry-After` folgt [RFC 6585 Abschnitt 4](https://www.rfc-editor.org/rfc/rfc6585#section-4). Dies ist keine Reservierung unter Berücksichtigung anderer Anfragen: Ein erneuter Versuch kann abgelehnt werden, wenn inzwischen eine andere Anfrage die Zulassung verbraucht.

Beenden Sie `gradle run` und entfernen Sie den Testcontainer.

```sh
docker stop redis-rate-limit-demo
```

## Was wurde bei Nebenläufigkeit und Fehlern geprüft?

Separate Reproduktionstests verwendeten echtes Redis in lokalem Docker und eingebetteten Tomcat. Diese Prüfungen betreffen Verhalten, nicht Durchsatz.

| Bedingung | Beobachtetes Ergebnis |
| --- | --- |
| 40 gleichzeitige Aufrufe für einen Schlüssel aus einem Threadpool | 3 erlaubt; Redis-Zähler 3 |
| Zwei Limiter-Objekte mit demselben Redis und Schlüssel | Teilen das Limit. Beide teilen ein Client-Bean; zwei separate JVMs wurden nicht gestartet. |
| Anfrage nach drei erlaubten Aufrufen | Abgelehnt ohne Zählererhöhung oder TTL-Verlängerung |
| Anderer Kontoschlüssel und abgelaufener Schlüssel | Anderer Schlüssel unabhängig erlaubt; nach Ablauf neues Fenster |
| Ungültiger Wert oder Schlüssel ohne TTL | Fehler ohne willkürliche Reparatur |
| Aufeinanderfolgende echte HTTP-Aufrufe | Drei Antworten 200, dann 429 mit `Retry-After` |
| HTTP-Anfrage mit ungültigem Zähler | 503 |
| Separater TCP-Endpunkt nimmt Verbindungen an, liefert aber keine Redis-Antwort | Limiter-Fehler auf 503 abgebildet |

Ein validierter Zähler muss eine TTL haben. Die [PTTL-Dokumentation](https://redis.io/docs/latest/commands/pttl/) definiert `-1` als keine TTL und `-2` als fehlenden Schlüssel. Eine TTL stillschweigend hinzuzufügen und bei ungültigem Zustand eine Anfrage zu erlauben, könnte einen Regelfehler verbergen; diese Implementierung gibt daher einen Fehler zurück.

**Atomare Lua-Ausführung bedeutet nicht, dass Schreibvorgänge bei Fehlern automatisch zurückgerollt werden.** Unterscheiden Sie Ausführungsisolation und Fehlerbehandlung wie in der [offiziellen Skriptdokumentation](https://redis.io/docs/latest/develop/programmability/eval-intro/). Ein Reproduktionstest bestätigte auch, dass ein Wert bestehen blieb, nachdem ein separates Skript `SET` ausgeführt und absichtlich einen Fehler zurückgegeben hatte. Das Skript dieses Artikels prüft Eingabe und vorhandenen Zustand vor dem Schreiben; der einzige Schreibvorgang ist das abschließende `SET` oder `INCR`.

## Welche Grenzen und Fehlerregeln im Betrieb wählen?

**Ein festes Fenster garantiert nicht höchstens drei Anfragen in jedem beliebigen fortlaufenden 10-Sekunden-Intervall.** Wer die verbleibende Zulassung kurz vor Fensterende nutzt und gleich nach Beginn des nächsten Fensters erneut anfragt, kann Anfragen in kurzer Zeit bündeln. Erwägen Sie Sliding Logs oder gleitende Fenster für eine genaue bewegliche Summe über eine Periode oder einen Token-Bucket, um mittlere Ankunftsrate und zulässigen Burst getrennt festzulegen. Diese Algorithmen werden hier nicht implementiert oder gemessen.

Das Beispiel verwendet **fail-closed**: Redis-Fehler lassen keine Anfragen durch. Das kann angebracht sein, wenn die Umgehung eines Limits teuer ist, etwa bei Zahlungen; ein Redis-Problem verringert aber auch die API-Verfügbarkeit. Wo Verfügbarkeit wichtiger ist, etwa bei einer Lese-API, ist eine zeitweise Erlaubnis unter einem begrenzten lokalen Bucket eine weitere Möglichkeit. Die Gesamtzulassung kann mit der Serverzahl steigen; das ist nicht dieselbe Garantie wie ein globales Limit.

Die Einstellung 200ms ist ein Verbindungs- und Befehls-Timeout und garantiert nicht, dass die gesamte HTTP-Anfrage innerhalb von 200ms endet. Berücksichtigen Sie Warteschlange, Wiederverbindung und Scheduling separat. Der Code ergänzt keinen anwendungsseitigen Retry; prüfen Sie auch die Richtlinien des Clients für Wiederverbindung und erneutes Senden. Wenn Redis eine Zulassung verbucht und die Antwort verloren geht, kann der Zähler verbraucht sein, obwohl der Aufrufer einen Fehler sieht. Soll ein erneuter Versuch nur einmal zählen, sind eine Anfrage-ID und eine eigene Idempotenzregel nötig.

Wenn ein Redis-Schlüssel unter Speicherdruck verdrängt wird oder sein Zähler bei Neustart oder Failover verloren geht, kann eine spätere Anfrage ein neues Fenster beginnen und erlaubt werden. Atomisches Lua allein bietet keine globale Begrenzung einschließlich Replikation und Wiederherstellung. Verwalten Sie dedizierte Instanzen, Speichergrenzen, Verdrängungsregel, Schlüssel mit Regelversion, Zahlen von Ablehnungen und Redis-Fehlern sowie Latenz der Limitentscheidung. Einzelne Schlüsselkennungen direkt in Metriklabels erhöhen zudem die Kardinalität.

Die Reproduktion deckt Normalbetrieb mit einer Redis-Instanz und einige Fehlerbehandlungen ab. Redis-Cluster-Failover, mehrere Regionen, Wiederherstellung nach einem tatsächlichen Redis-Prozessausfall und Leistung unter Produktionslast wurden nicht getestet. Ein Limit gestarteter Anfragen begrenzt auch nicht gleichzeitige DB-Belegung oder die Zahl lang laufender Anfragen; wenden Sie bei Bedarf gesonderte Nebenläufigkeitslimits an.
