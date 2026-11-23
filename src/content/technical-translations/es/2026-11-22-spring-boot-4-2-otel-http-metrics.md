---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2026-11-22-spring-boot-4-2-otel-http-metrics",
  "routeSlug": "2026-11-22-spring-boot-4-2-otel-http-metrics",
  "kind": "post",
  "title": "Cómo cambian las métricas HTTP de Spring Boot 4.2 con las convenciones de OpenTelemetry",
  "description": "Compara las métricas de Prometheus de Spring MVC y RestClient en Spring Boot 4.2.0 y adapta una consulta de respuestas 404 a las convenciones de OpenTelemetry.",
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
  "draftSha256": "cde6a9eddafbfd579397e5342c816ab480d42a3f5fee9ae4aa8c947251b4e115",
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

**Al habilitar las convenciones de observación de OpenTelemetry en Spring Boot 4.2.0, la métrica de Prometheus del servidor Spring MVC cambia de `http_server_requests_seconds_count` a `http_server_request_duration_seconds_count`.** La etiqueta que filtra las respuestas 404 pasa de `status` a `http_response_status_code`. En la misma aplicación, las llamadas de `RestClient` a una API externa conservaron el nombre y las etiquetas de su métrica. Comprueba por separado las métricas de entrada y salida al actualizar paneles y alertas. [Notas de la versión Spring Boot 4.2](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.2-Release-Notes#semantic-conventions)

## Ejecuta las mismas dos solicitudes con ambas configuraciones

Reutiliza [el ejemplo de consulta de productos de la guía anterior](/en/posts/2026-11-22-spring-boot-4-2-restclient-migration/). Cuando la aplicación recibe `GET /products/{id}`, usa `RestClient` para llamar a `GET /items/{id}` en la API externa. En este ejercicio, el ID `42` devuelve `200` y el nombre `Keyboard`. El ID `99` devuelve `404` con el cuerpo vacío.

![La misma aplicación se ejecuta una vez por convención. En cada ejecución se solicitan los productos 42 y 99 y se guarda la salida de Prometheus para comparar las métricas del servidor Spring MVC y de RestClient.](/assets/diagrams/technical/es-2026-11-22-spring-boot-4-2-otel-http-metrics.svg)

El diagrama muestra ambas ejecuciones. Cada una realiza las mismas solicitudes y guarda por separado la salida de Prometheus para compararlas.

Usa Spring Boot 4.2.0 y JDK 21. Copia `pom.xml` y `src/main/java/example/CatalogApplication.java` de la guía anterior. Elimina la dependencia `spring-boot-starter-webmvc-test`, que este ejercicio no usa, y agrega las dos dependencias indicadas a la lista de Maven. `CatalogApplication.java` ya recibe el `RestClient.Builder` configurado por Boot. [Documentación de Spring Boot sobre métricas del cliente HTTP](https://docs.spring.io/spring-boot/reference/actuator/metrics.html#actuator.metrics.supported.http-clients)

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

Para empaquetar la aplicación como JAR ejecutable, agrega esta configuración en `<project>` dentro de `pom.xml`.

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

En una terminal, inicia un servidor local que actúe como API externa. Sirve el archivo en `/items/42` y devuelve 404 para `/items/99` porque ese archivo no existe. Utiliza un entorno de desarrollo local con ambos puertos libres.

```sh
upstream_dir=$(mktemp -d)
mkdir -p "$upstream_dir/items"
printf '%s' Keyboard > "$upstream_dir/items/42"
python3 -m http.server 18081 --bind 127.0.0.1 --directory "$upstream_dir"
```

En otra terminal, compila la aplicación desde la raíz del proyecto Maven e iníciala con las convenciones predeterminadas. Expón el endpoint de Actuator del que recogerás las métricas y vincula la aplicación a la dirección de bucle local.

```sh
mvn package

java -jar target/restclient-migration-1.0.0.jar \
  --server.address=127.0.0.1 \
  --server.port=18080 \
  --catalog.base-url=http://127.0.0.1:18081 \
  --management.endpoints.web.exposure.include=health,prometheus
```

Una vez iniciada la aplicación, envía estas solicitudes desde una tercera terminal. Verifica ambas respuestas y guarda la salida de Prometheus, que incluye las series `_count` con el número acumulado de solicitudes.

```sh
curl -sS -i http://127.0.0.1:18080/products/42
curl -sS -i http://127.0.0.1:18080/products/99
curl -fsS http://127.0.0.1:18080/actuator/prometheus > default.prom
```

Detén la aplicación y vuelve a iniciarla con el mismo comando `java -jar`, agregando `--management.observations.conventions=open-telemetry`. Repite las tres solicitudes y guarda la última respuesta como `open-telemetry.prom`. Un proceso nuevo reinicia los contadores de la primera ejecución.

```sh
grep -E '^http_(server|client).*_count\{.*(/products/|/items/)' \
  default.prom open-telemetry.prom
```

## Qué cambió en las métricas capturadas

Ejecuté ambas configuraciones con JDK 21.0.1, Maven 3.9.11, Spring Boot 4.2.0 y Tomcat embebido. En cada ejecución, una solicitud devolvió `200` y otra devolvió `404`. El estado y el cuerpo de las cuatro respuestas coincidieron con lo esperado.

| Métrica del servidor MVC | Convenciones predeterminadas | Convenciones de OpenTelemetry |
| --- | --- | --- |
| Contador de solicitudes de Prometheus | `http_server_requests_seconds_count` | `http_server_request_duration_seconds_count` |
| Etiqueta del método HTTP | `method` | `http_request_method` |
| Etiqueta del estado de respuesta | `status` | `http_response_status_code` |
| Etiqueta de la ruta | `uri` | `http_route` |
| Valor de la ruta en este ejemplo | `/products/{id}` | `/products/{id}` |

La etiqueta de la ruta contiene la plantilla con `{id}`. El extracto muestra las series capturadas para 404 con las etiquetas que se usan en las consultas. El contador de respuestas 404 del servidor fue `1` en cada ejecución.

```text
http_server_requests_seconds_count{status="404",uri="/products/{id}"} 1
http_server_request_duration_seconds_count{http_response_status_code="404",http_route="/products/{id}"} 1
```

En las mismas capturas, ambas configuraciones registraron las solicitudes salientes en `http_client_requests_seconds_count`, con `method="GET"`, `uri="/items/{id}"` y `status="200"` o `status="404"`. El resultado corresponde a la combinación de configuración automática de Boot y `RestClient.Builder` del ejemplo. Este ejercicio lee métricas del registro de Prometheus de Micrometer. La convención de observación y el método de exportación son ajustes independientes. [Documentación de Spring Boot sobre observabilidad](https://docs.spring.io/spring-boot/reference/actuator/observability.html#actuator.observability.semantic-conventions)

## Actualiza la consulta de respuestas 404

Con las convenciones predeterminadas, un panel de Grafana puede consultar el recuento acumulado de 404 para esta ruta como sigue.

```text
sum(http_server_requests_seconds_count{uri="/products/{id}",status="404"})
```

Con las convenciones de OpenTelemetry, cambia el nombre de la métrica y ambas etiquetas.

```text
sum(http_server_request_duration_seconds_count{http_route="/products/{id}",http_response_status_code="404"})
```

Probé las consultas con las series capturadas mediante `promtool` de Prometheus 3.5.0. Cada consulta devolvió `1` con la convención correspondiente y un resultado vacío con la otra.

Estas consultas comparan recuentos acumulados de una sola aplicación. Si un panel de producción ya muestra solicitudes por segundo en una ventana reciente, conserva el cálculo, como `rate(...[5m])`, y actualiza el selector de métrica que contiene. Mientras Prometheus recoja métricas de ambas versiones, consulta por destino de despliegue para ver cuáles siguen publicando cada nombre. [Fundamentos de las consultas de Prometheus](https://prometheus.io/docs/prometheus/latest/querying/basics/) · [Documentación de Prometheus sobre `rate()`](https://prometheus.io/docs/prometheus/latest/querying/functions/#rate)

Si configuras el nombre de la métrica del servidor con `management.observations.http.server.requests.name`, revisa primero los paneles y alertas que hacen referencia al nombre personalizado. Este ajuste no tiene efecto con las convenciones de OpenTelemetry. Para seguir una solicitud individual desde las métricas hasta sus registros y trazas, consulta [Cómo correlacionar registros y trazas en Grafana LGTM](/en/posts/2026-11-02-grafana-lgtm-log-trace/). [Notas de la versión Spring Boot 4.2](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.2-Release-Notes#semantic-conventions)
