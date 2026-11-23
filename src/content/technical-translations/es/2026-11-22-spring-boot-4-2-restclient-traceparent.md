---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2026-11-22-spring-boot-4-2-restclient-traceparent",
  "routeSlug": "2026-11-22-spring-boot-4-2-restclient-traceparent",
  "kind": "post",
  "title": "Cómo verificar la propagación de traceparent con RestClient en Spring Boot 4.2",
  "description": "Compara la propagación de traceparent y las relaciones entre spans en Tempo con dos formas de crear RestClient en Spring Boot 4.2.0.",
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
  "draftSha256": "88ed0e410004e09f50a0a7aed2dcce180ffc003f798e9e21db408f174ed792fc",
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

**Usa el `RestClient.Builder` que inyecta Spring Boot para seguir la consulta de un producto y su llamada al inventario en una sola traza.** En el ejemplo, el cliente creado con `RestClient.create()` consulta el mismo producto y también devuelve HTTP 200. La API de inventario no recibe el encabezado `traceparent` e inicia una traza independiente. Compara las respuestas HTTP y los spans guardados en Tempo para saber dónde deja de propagarse el contexto de la traza. [Documentación de Spring Boot sobre la propagación de trazas](https://docs.spring.io/spring-boot/4.2/reference/actuator/tracing.html#actuator.micrometer-tracing.propagating-traces)

El ejercicio parte de la consulta de productos de la [guía de migración a RestClient](/en/posts/2026-11-22-spring-boot-4-2-restclient-migration/). La [guía de métricas HTTP](/en/posts/2026-11-22-spring-boot-4-2-otel-http-metrics/) cuenta solicitudes. Aquí sigues el recorrido de una sola solicitud.

## El encabezado que conecta la consulta del producto y del inventario

`traceparent` es el encabezado HTTP estándar de W3C para propagar el contexto de la traza. En este ejercicio tiene el formato `00-<trace-id>-<parent-id>-<trace-flags>`. El `trace-id` identifica toda la traza. El `parent-id` identifica el span del cliente HTTP emisor para que el servicio receptor lo use como padre de su span de servidor. [Especificación W3C Trace Context](https://www.w3.org/TR/trace-context/#traceparent-header)

![La aplicación de productos llama a la API de inventario. El constructor de Boot envía traceparent y conecta ambas aplicaciones en una sola traza. El cliente creado directamente no envía el encabezado y la API de inventario inicia otra traza.](/assets/diagrams/technical/es-2026-11-22-spring-boot-4-2-restclient-traceparent.svg)

El diagrama muestra los dos recorridos del cliente para el producto 42. Ambos devuelven la misma cantidad de existencias. En este ejemplo el encabezado `traceparent` determina si el span del servidor de inventario se integra en la traza del producto.

## Ejecuta el mismo JAR como dos aplicaciones

Necesitas JDK 21, Maven, Docker, `curl` y `jq`. El ejercicio usa los puertos locales `13200`, `14318`, `18180` y `18181`. Crea estos archivos en un directorio vacío. Ejecuta el mismo JAR dos veces, primero con el nombre de servicio `product` y luego con `inventory`. La respuesta incluye los ID de traza actuales y el encabezado recibido para que puedas inspeccionarlos.

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

Una probabilidad de muestreo de `1.0` permite registrar todas las solicitudes del ejercicio. Las aplicaciones exportan solo trazas a través de OTLP. Revisa primero el encabezado en la respuesta HTTP para diagnosticar por separado los spans ausentes en Tempo y los problemas de propagación. [Documentación de Spring Boot sobre el muestreo](https://docs.spring.io/spring-boot/4.2/reference/actuator/tracing.html#actuator.micrometer-tracing.sampling)

### `tempo.yaml`

Esta configuración permite a Tempo recibir spans mediante OTLP HTTP y escribirlos en el almacenamiento local. La API de consulta y los puertos de recepción solo se exponen en la dirección de bucle local del host.

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

Inicia Tempo y las aplicaciones desde la raíz del proyecto. Arranca Tempo en la primera terminal.

```sh
docker run --rm --name traceparent-tempo \
  -p 127.0.0.1:13200:3200 -p 127.0.0.1:14318:4318 \
  --mount "type=bind,source=$PWD/tempo.yaml,target=/etc/tempo.yaml,readonly" \
  grafana/tempo:2.9.0 -config.file=/etc/tempo.yaml
```

En otra terminal, verifica que `curl -fsS http://127.0.0.1:13200/ready` termina correctamente y compila con Maven. Ejecuta los dos comandos `java` en terminales separadas.

```sh
mvn package

java -jar target/trace-propagation-1.0.0.jar \
  --spring.application.name=inventory --server.port=18181

java -jar target/trace-propagation-1.0.0.jar \
  --spring.application.name=product --server.port=18180
```

## Compara los encabezados y los ID de traza en las respuestas

Una vez iniciadas ambas aplicaciones, consulta dos veces el mismo producto. Cambia solo `instrumented` para seleccionar el cliente.

```sh
curl -fsS 'http://127.0.0.1:18180/products/42?instrumented=true' -o boot.json
curl -fsS 'http://127.0.0.1:18180/products/42?instrumented=false' -o direct.json

jq '{id: .inventory.id, stock: .inventory.stock,
     headerReceived: (.inventory.traceparent != null),
     sameTrace: (.productTraceId == .inventory.inventoryTraceId)}' boot.json direct.json
jq -r .inventory.traceparent boot.json
```

Las dos solicitudes devolvieron HTTP 200. Con el constructor de Boot, ambas aplicaciones compartieron el mismo ID de traza y el encabezado `traceparent` recibido por la API de inventario incluía ese ID. Con el cliente creado directamente, la API de inventario informó de `traceparent` con valor `null` y las aplicaciones tuvieron ID de traza distintos.

| Creación del cliente | ID del producto y existencias | Encabezado recibido | ID de traza entre aplicaciones |
| --- | --- | --- | --- |
| `RestClient.Builder` inyectado por Boot | 42 y 7 | Sí | Iguales |
| `RestClient.create()` | 42 y 7 | No | Distintos |

## Comprueba los spans en Tempo

Consulta Tempo con los ID de traza de las respuestas. La exportación de spans puede tardar unos segundos. Si falta una traza, espera un momento y repite la consulta. [API de Grafana Tempo para consultar trazas por ID](https://grafana.com/docs/tempo/latest/api_docs/#query)

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

El ejemplo se ejecutó con Spring Boot 4.2.0, JDK 21.0.1, Maven 3.9.11 y Tempo 2.9.0. La API de Tempo devolvió los siguientes spans para los tres ID de traza de las dos solicitudes.

| ID de traza consultado | Spans observados en Tempo |
| --- | --- |
| Solicitud con el constructor de Boot | Servidor de productos → cliente HTTP de productos → servidor de inventario |
| Aplicación de productos con el cliente creado directamente | Un span raíz del servidor de productos |
| Aplicación de inventario con el cliente creado directamente | Un span raíz del servidor de inventario |

En la ruta con el constructor de Boot, el `parentSpanId` del servidor de inventario en Tempo coincidió con el `spanId` del cliente HTTP de productos. En esta ejecución la API de Tempo codificó los ID de span en Base64 y `traceparent` usa hexadecimal. Al decodificar en Base64 el ID del span cliente y representar los bytes en hexadecimal, se obtuvo el valor `parent-id` del encabezado.

Si las solicitudes se completan pero una traza se corta en el límite entre servicios, comprueba si el servicio receptor recibe `traceparent`. Si falta el encabezado, comprueba que quien hace la llamada usa el constructor configurado por Boot. Si el ID se propaga pero faltan spans en Tempo, revisa el muestreo y la configuración de exportación OTLP. Después puedes buscar los registros con el mismo ID de traza siguiendo [Cómo correlacionar registros y trazas en Grafana LGTM](/en/posts/2026-11-02-grafana-lgtm-log-trace/).
