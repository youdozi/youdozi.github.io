---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2026-11-22-spring-boot-4-2-restclient-traceparent",
  "routeSlug": "2026-11-22-spring-boot-4-2-restclient-traceparent",
  "kind": "post",
  "title": "traceparent-Weitergabe mit RestClient in Spring Boot 4.2 prüfen",
  "description": "Für zwei Möglichkeiten, RestClient in Spring Boot 4.2.0 zu erstellen, die Weitergabe von traceparent und die Span-Beziehungen in Tempo vergleichen.",
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
  "draftSha256": "10d0dd872c49be9b1823e76d83dc59fc4fe6345552f3c7f994c61cf3e3133e65",
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

**Mit dem von Spring Boot injizierten `RestClient.Builder` können Sie eine Produktabfrage und den zugehörigen Bestandsabruf in einem Trace verfolgen.** Der mit `RestClient.create()` erstellte Client fragt im Beispiel dasselbe Produkt ab und liefert ebenfalls HTTP 200. Die Bestands-API empfängt dabei keinen `traceparent`-Header und beginnt einen eigenen Trace. Vergleichen Sie die HTTP-Antworten und die in Tempo gespeicherten Spans, um die Stelle zu finden, an der der Trace-Kontext nicht mehr weitergegeben wird. [Spring-Boot-Dokumentation zur Weitergabe von Trace-Kontext](https://docs.spring.io/spring-boot/4.2/reference/actuator/tracing.html#actuator.micrometer-tracing.propagating-traces)

Diese Übung baut auf der Produktabfrage im [Migrationsleitfaden zu RestClient](/en/posts/2026-11-22-spring-boot-4-2-restclient-migration/) auf. Der [Leitfaden zu HTTP-Metriken](/en/posts/2026-11-22-spring-boot-4-2-otel-http-metrics/) zählt Anfragen. Hier verfolgen Sie den Weg einer einzelnen Anfrage.

## Der Header verbindet Produkt- und Bestandsabfrage

`traceparent` ist der W3C-Standardheader für die Weitergabe des Trace-Kontexts per HTTP. In der Übung hat er die Form `00-<trace-id>-<parent-id>-<trace-flags>`. Die `trace-id` kennzeichnet den gesamten Trace. Die `parent-id` identifiziert den HTTP-Client-Span des Senders, damit der empfangende Dienst ihn als übergeordneten Span seines Server-Spans verwenden kann. [W3C-Spezifikation für Trace Context](https://www.w3.org/TR/trace-context/#traceparent-header)

![Die Produkt-App ruft die Bestands-API auf. Der Boot-Builder sendet traceparent und verbindet beide Anwendungen in einem Trace. Ein direkt erstellter Client sendet keinen Header, sodass die Bestands-API einen separaten Trace startet.](/assets/diagrams/technical/de-2026-11-22-spring-boot-4-2-restclient-traceparent.svg)

Das Diagramm zeigt die beiden Client-Pfade für Produkt 42. Beide liefern denselben Bestandswert. Der `traceparent`-Header bestimmt im Beispiel, ob der Bestandsserver-Span Teil des Produkt-Traces wird.

## Dieselbe JAR-Datei für zwei Apps ausführen

Sie benötigen JDK 21, Maven, Docker, `curl` und `jq`. Die Übung verwendet die lokalen Ports `13200`, `14318`, `18180` und `18181`. Legen Sie die folgenden Dateien in einem leeren Verzeichnis an. Starten Sie dieselbe JAR-Datei zweimal, mit den Dienstnamen `product` und `inventory`. Die Antwort enthält zur Kontrolle die aktuellen Trace-IDs und den empfangenen Header.

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

Die Sampling-Wahrscheinlichkeit `1.0` erfasst in dieser Übung alle Anfragen. Die Apps exportieren nur Traces über OTLP. Prüfen Sie zuerst den Header in der HTTP-Antwort. So können Sie fehlende Spans in Tempo unabhängig von der Weitergabe des Trace-Kontexts untersuchen. [Spring-Boot-Dokumentation zum Sampling](https://docs.spring.io/spring-boot/4.2/reference/actuator/tracing.html#actuator.micrometer-tracing.sampling)

### `tempo.yaml`

Mit dieser Konfiguration empfängt Tempo Spans über OTLP HTTP und schreibt sie in den lokalen Speicher. Abfrage-API und Empfangsports sind nur über die Loopback-Adresse des Hosts erreichbar.

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

Starten Sie Tempo und die Anwendungen im Projektstamm. Starten Sie Tempo im ersten Terminal.

```sh
docker run --rm --name traceparent-tempo \
  -p 127.0.0.1:13200:3200 -p 127.0.0.1:14318:4318 \
  --mount "type=bind,source=$PWD/tempo.yaml,target=/etc/tempo.yaml,readonly" \
  grafana/tempo:2.9.0 -config.file=/etc/tempo.yaml
```

Prüfen Sie in einem anderen Terminal, ob `curl -fsS http://127.0.0.1:13200/ready` erfolgreich ist, und bauen Sie dann mit Maven. Führen Sie die beiden `java`-Befehle in getrennten Terminals aus.

```sh
mvn package

java -jar target/trace-propagation-1.0.0.jar \
  --spring.application.name=inventory --server.port=18181

java -jar target/trace-propagation-1.0.0.jar \
  --spring.application.name=product --server.port=18180
```

## Header und Trace-IDs der Antworten vergleichen

Sobald beide Anwendungen laufen, fragen Sie dasselbe Produkt zweimal ab. Ändern Sie zur Client-Auswahl nur `instrumented`.

```sh
curl -fsS 'http://127.0.0.1:18180/products/42?instrumented=true' -o boot.json
curl -fsS 'http://127.0.0.1:18180/products/42?instrumented=false' -o direct.json

jq '{id: .inventory.id, stock: .inventory.stock,
     headerReceived: (.inventory.traceparent != null),
     sameTrace: (.productTraceId == .inventory.inventoryTraceId)}' boot.json direct.json
jq -r .inventory.traceparent boot.json
```

Beide Anfragen lieferten HTTP 200. Beim Boot-Builder hatten beide Anwendungen dieselbe Trace-ID. Der von der Bestands-API empfangene `traceparent`-Header enthielt diese ID. Beim direkt erstellten Client meldete die Bestands-API `traceparent` als `null` und die Trace-IDs der beiden Apps unterschieden sich.

| Erstellung des Clients | Produkt-ID und Bestand | Header empfangen | Trace-IDs der Apps |
| --- | --- | --- | --- |
| Von Boot injizierter `RestClient.Builder` | 42 und 7 | Ja | Gleich |
| `RestClient.create()` | 42 und 7 | Nein | Unterschiedlich |

## Die Spans in Tempo prüfen

Fragen Sie Tempo mit den Trace-IDs aus den Antworten ab. Der Export von Spans kann ein paar Sekunden dauern. Fehlt ein Trace, warten Sie kurz und wiederholen die Abfrage. [Grafana-Tempo-API für die Abfrage von Traces nach ID](https://grafana.com/docs/tempo/latest/api_docs/#query)

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

Das Beispiel lief mit Spring Boot 4.2.0, JDK 21.0.1, Maven 3.9.11 und Tempo 2.9.0. Die Tempo-API gab zu den drei Trace-IDs aus den beiden Anfragen folgende Spans zurück.

| Abgefragte Trace-ID | In Tempo beobachtete Spans |
| --- | --- |
| Anfrage mit dem Boot-Builder | Produktserver → Produkt-HTTP-Client → Bestandsserver |
| Produkt-App bei der Anfrage mit direkt erstelltem Client | Ein Root-Span des Produktservers |
| Bestands-App bei der Anfrage mit direkt erstelltem Client | Ein Root-Span des Bestandsservers |

Beim Boot-Builder entsprach die `parentSpanId` des Bestandsservers in Tempo der `spanId` des Produkt-HTTP-Clients. Die Tempo-API kodierte in diesem Lauf die Span-IDs in Base64, während `traceparent` Hexadezimalwerte enthält. Nach dem Dekodieren der Client-Span-ID aus Base64 entsprach die Hexadezimaldarstellung der Bytes der `parent-id` des Headers.

Wenn Anfragen gelingen, ein Trace aber an einer Dienstgrenze endet, prüfen Sie, ob der Empfänger `traceparent` erhält. Falls der Header fehlt, prüfen Sie, ob der Aufrufer den von Boot konfigurierten Builder verwendet. Wird die Trace-ID weitergegeben, fehlen aber Spans in Tempo, prüfen Sie die Sampling- und OTLP-Exporteinstellungen. Wie Sie mit derselben Trace-ID Logs finden, zeigt [Logs und Traces in Grafana LGTM verknüpfen](/en/posts/2026-11-02-grafana-lgtm-log-trace/).
