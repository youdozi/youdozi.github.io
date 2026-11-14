---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2026-11-09-spring-mvc-webclient-execution",
  "routeSlug": "2026-11-09-spring-mvc-webclient-execution",
  "kind": "post",
  "title": "Cómo funciona WebClient en Spring MVC: block, Mono e hilos virtuales",
  "description": "Comprende la comunicación de WebClient con Reactor Netty en Spring MVC, compara block y Mono y verifica qué cambia con hilos virtuales.",
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
  "draftSha256": "f8662437437bada9658be755fa8d82a49026d97eb50c22d06354baf235c5bb39",
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

**WebClient puede realizar comunicación HTTP no bloqueante en Spring MVC, pero llamar a `.block()` en un controlador hace que el hilo de solicitud MVC espere el resultado.** Al devolver el `Mono`, MVC puede adaptarlo al procesamiento asíncrono de Servlet y liberar el hilo inicial. La comunicación del cliente y la gestión de solicitudes del servidor son responsabilidades distintas.

Este artículo trata **Spring MVC en Tomcat y WebClient con Reactor Netty**. Otro conector HTTP puede usar nombres de hilo y recursos diferentes. El ejemplo se reproduce con Spring Boot 3.5.16, JDK 21 y Gradle 8.14.3; no verifica todas las versiones actuales de Boot.

## ¿Añadir WebClient hace que el servidor use WebFlux?

MVC en el servidor y WebClient para llamadas salientes cumplen funciones distintas. Aquí Tomcat y `DispatcherServlet` gestionan las solicitudes entrantes, mientras que el conector Reactor Netty de WebClient gestiona el HTTP saliente.

En Boot 3.5, añadir juntos `spring-boot-starter-web` y `spring-boot-starter-webflux` selecciona MVC por defecto. Esto permite añadir el starter de WebFlux para usar WebClient. Compruébalo por separado si se cambia explícitamente el tipo de aplicación o la configuración del servidor. [Selección de MVC y WebFlux en Boot](https://docs.spring.io/spring-boot/3.5/reference/web/reactive.html#web.reactive.webflux)

## ¿Dónde divergen `.block()` y devolver `Mono`?

![En la ruta block, el hilo de solicitud Servlet espera mientras Netty gestiona HTTP. En la ruta que devuelve Mono, tras la suscripción de MVC, la comunicación de Netty se solapa con el procesamiento asíncrono Servlet y MVC vuelve a despachar el resultado.](/assets/diagrams/technical/es-2026-11-09-spring-mvc-webclient-execution.svg)

El verde muestra las responsabilidades de Servlet y MVC; el azul las de Reactor Netty. Las dos ramas asíncronas pueden solaparse y la respuesta externa no llega necesariamente después de que se libere el hilo inicial. El diagrama se centra en señales de éxito; las señales de error del código se asignan a estados HTTP antes de la gestión de errores MVC.

| Etapa | Devolver valor tras `.block()` | Devolver `Mono` |
| --- | --- | --- |
| Suscripción | La realiza `.block()` | MVC se suscribe al tipo devuelto |
| Espera de HTTP saliente | Espera el hilo de solicitud | El procesamiento asíncrono Servlet puede liberar el hilo inicial |
| Tras recibir el cuerpo | El callback del cliente entrega el resultado y termina la espera | La señal de resultado pasa al procesamiento asíncrono MVC |
| Respuesta HTTP final | MVC serializa y escribe el valor | MVC vuelve a despachar, serializa y escribe |

`retrieve().bodyToMono(...)` ensambla la canalización de la solicitud. Hay que suscribirse a la nueva canalización de WebClient antes de que inicie una solicitud HTTP. Suscribirse dos veces puede producir otra solicitud: cuidado con leer una vez con `.block()` y volver a devolver la canalización.

MVC adapta un `Mono` de un único valor de forma similar a `DeferredResult`. Cuando el resultado está listo, vuelve a despachar al contenedor Servlet para completar la respuesta. El pool puede reutilizar el mismo hilo, por lo que no debe suponerse que el hilo de redespacho sea distinto del inicial. La conexión y los recursos de solicitud asíncrona también permanecen mientras la respuesta está abierta. Devolver `Mono` no hace no bloqueante toda la escritura de la respuesta Servlet. Este ejemplo devuelve JSON de un único valor; streaming y SSE son casos distintos. [Procesamiento asíncrono MVC y tipos reactivos](https://docs.spring.io/spring-framework/reference/6.2/web/webmvc/mvc-ann-async.html)

## Llamar a la misma API externa de dos formas

Guarda los archivos siguientes en un proyecto. Utiliza el plugin `application`, no el plugin Gradle de Boot, y fija el toolchain Java en 21. Las comprobaciones locales usaron Azul JDK 21.0.1; este parche histórico no es una recomendación para nuevos entornos de producción.

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

`WebClient` se reutiliza como bean y utiliza explícitamente el conector Reactor Netty. `HttpClient.create()` en este ejemplo usa el event loop y el pool de conexiones compartidos predeterminados; no crea un hilo Netty dedicado por solicitud saliente. `callbackThread` es el hilo que ejecuta `map` después de producirse el cuerpo, no necesariamente el hilo que escribe la respuesta Servlet final. No se añade ningún cambio de scheduler como `publishOn`. [Conectores y recursos compartidos de WebClient](https://docs.spring.io/spring-framework/reference/6.2/web/webflux-webclient/client-builder.html)

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

`/block` es una ruta de comparación. Un controlador que puede finalizar con una devolución asíncrona puede devolver el `Mono` resultante, como `/async`, para que MVC se suscriba. Llamar directamente a `.subscribe()` y responder primero separa el resultado y error de la llamada saliente de la solicitud HTTP original. [Uso síncrono de WebClient y devolución de controladores](https://docs.spring.io/spring-framework/reference/web/webflux-webclient/client-synchronous.html)

El `timeout` de tres segundos del ejemplo limita el intervalo entre la suscripción y la entrega de un valor. No configura por separado la adquisición de conexión del pool, la conexión ni cada tiempo límite de lectura de respuesta. Los errores HTTP se asignan a 502 y el tiempo agotado de la canalización a 504. Define contratos independientes para errores de conexión, cuerpos vacíos y errores de negocio. `retrieve()` trata por defecto HTTP 4xx y 5xx como errores. [Errores de retrieve](https://docs.spring.io/spring-framework/reference/6.2/web/webflux-webclient/client-retrieve.html)

### Ejecución local

Inicia un servidor HTTP local de Python 3 en lugar de un servicio externo. `/value` devuelve `hello` después de 0.2 segundos. Ese retraso es una entrada para observar el comportamiento, no una medición de rendimiento.

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

Ejecuta el servidor en la primera terminal.

```sh
python3 upstream.py
```

En la segunda terminal selecciona JDK 21 y ejecuta con Gradle 8.14.3.

```sh
gradle run
```

En la tercera terminal llama a ambas rutas:

```sh
curl --fail --show-error --silent http://127.0.0.1:8080/block
curl --fail --show-error --silent http://127.0.0.1:8080/async
```

Ambas devuelven JSON con `hello`. Con hilos ordinarios observamos `requestVirtual=false`; el callback Netty de este ejemplo tuvo `callbackVirtual=false` y `callbackNonBlocking=true`. Los nombres y números exactos de hilos varían entre ejecuciones. El `mode` del JSON por sí solo no demuestra que el hilo se liberara durante la espera.

## ¿Qué cambia al activar hilos virtuales?

Tras detener la aplicación anterior, ejecuta el mismo código con la configuración de hilos virtuales.

```sh
gradle run --args='--spring.threads.virtual.enabled=true'
```

Con esta configuración, `requestVirtual` pasó a `true` en ambas rutas. En `.block()` el hilo virtual que llama sigue esperando el resultado, pero una espera normalmente aparcable no equivale a ocupar continuamente un hilo de plataforma portador. Comprueba por separado el pinning y las diferencias de la versión de JDK utilizada. [Planificación y pinning de hilos virtuales en JDK 21](https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html) **Activar hilos virtuales no convirtió el callback Reactor Netty de este ejemplo en un hilo virtual.** [Configuración de hilos virtuales en Boot](https://docs.spring.io/spring-boot/3.5/reference/features/spring-application.html#features.spring-application.virtual-threads)

Los hilos virtuales no aumentan la capacidad de un servicio externo ni el número de conexiones HTTP o de base de datos. Diseña un límite separado para solicitudes acumuladas, como en [semáforos de DB y control de admisión](/ko/posts/2026-11-03-virtual-threads-db-semaphore/).

## ¿Se puede llamar a JDBC dentro de un callback?

Usar WebClient desde MVC no implica que el `map` posterior se ejecute también en el hilo de solicitud MVC. Una consulta JDBC o lectura larga de archivo dentro del `map` de este ejemplo puede bloquear el event loop de Netty. A la inversa, no todos los `Mono` se ejecutan en un hilo dedicado. La ejecución de un operador depende de la suscripción, las señales y los cambios de scheduler. [Hilos y schedulers de Reactor](https://projectreactor.io/docs/core/release/reference/coreFeatures/schedulers.html)

Si un servicio tiene muchas operaciones síncronas, compara limitar recursos en el flujo síncrono de MVC con aislar el trabajo bloqueante en otro ejecutor mientras se mantiene una cadena asíncrona. Para HTTP síncrono sencillo consulta también [cómo elegir RestClient o WebClient](/ko/posts/2026-10-31-webclient-restclient-comparison/). Cambiar de scheduler por sí solo no resuelve la sobrecarga de DB o servicios dependientes.

## Qué se verificó realmente

Las [pruebas de verificación](https://github.com/youdozi/youdozi.github.io/blob/main/.pipeline/drafts/2026-11-09-spring-mvc-webclient-execution/src/test/java/example/ExecutionTest.java) se ejecutaron con **Tomcat real y un servidor HTTP local** en puertos aleatorios. Pasaron dieciséis comprobaciones: ocho con hilos ordinarios y ocho con hilos virtuales.

- Selección del contexto Servlet, Tomcat y DispatcherServlet con ambos starters
- Ninguna solicitud al ensamblar la canalización; solicitudes al suscribirse y volver a suscribirse
- Espera del hilo para `.block()` y entrada en procesamiento asíncrono Servlet para `Mono` mientras se retiene la respuesta externa
- Si los hilos de solicitud son virtuales y si los callbacks son no bloqueantes o virtuales
- Asignación de errores HTTP a 502 y tiempos agotados de canalización a 504 en ambas rutas

Para ejecutar las pruebas, guarda el código de verificación anterior como `src/test/java/example/ExecutionTest.java` y ejecútalo.

```sh
gradle clean test
gradle test -Pvirtual=true --rerun-tasks
```

Las pruebas observan el estado mediante un latch que retiene la respuesta; no deducen asincronía de un tiempo de ejecución corto. No verifican comparaciones de rendimiento, servicios externos reales, DB o TLS, desconexiones del cliente ni cancelación de efectos remotos. En particular, cancelar la canalización no garantiza cancelar el trabajo ni revertir una transacción en el servidor remoto.
