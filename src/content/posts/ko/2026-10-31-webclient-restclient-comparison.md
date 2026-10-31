---
language: "ko"
translationKey: "2026-10-31-webclient-restclient-comparison"
routeSlug: "2026-10-31-webclient-restclient-comparison"
kind: "post"
categories: ["springboot"]
tags: ["spring", "webclient", "restclient", "http-client", "reactive", "virtual-threads"]
publishedAt: "2026-10-30T23:49:15.271160+00:00"
updatedAt: "2026-10-30T23:49:15.271160+00:00"
title: "WebClient와 RestClient 비교: 동기 호출·반응형·스트리밍 선택 기준"
description: "Spring WebClient와 RestClient의 실행 시점, block, 오류 처리와 가상 스레드 적용 기준을 비교합니다. 로컬 HTTP 예제로 구독별 요청과 404·503 처리를 확인합니다."
reviewedAt: "2026-10-31"
reviewStatus: "revised"
reviewScope: "Spring Framework 7.0.10/JDK 17 console HTTP contracts; not a throughput benchmark, server-stack test or production policy."
reviewSources: ["https://docs.spring.io/spring-framework/reference/integration/rest-clients.html", "https://spring.io/blog/2025/09/30/the-state-of-http-clients-in-spring/", "https://docs.spring.io/spring-framework/reference/web/webflux-webclient/client-synchronous.html", "https://docs.spring.io/spring-framework/reference/web/webflux-webclient/client-retrieve.html", "https://docs.spring.io/spring-framework/reference/web/webflux/new-framework.html", "https://docs.spring.io/spring-framework/docs/7.0.10/javadoc-api/org/springframework/http/client/JdkClientHttpRequestFactory.html", "https://docs.spring.io/spring-framework/docs/7.0.10/javadoc-api/org/springframework/http/client/reactive/JdkClientHttpConnector.html"]
---
**동기식 서비스에서 HTTP 응답 하나를 받아 다음 작업을 진행한다면 RestClient부터 검토하고, 반응형 호출 조합이나 스트리밍이 필요하다면 WebClient를 검토합니다.** 둘 다 체이닝 API를 제공하지만, [RestClient는 동기식이고 WebClient는 비차단·반응형 클라이언트](https://docs.spring.io/spring-framework/reference/integration/rest-clients.html)입니다. 선택은 요청 수보다 애플리케이션의 실행 모델에 맞춥니다.


RestClient는 Spring Framework 6.1에서 도입됐고 WebClient는 5.0부터 제공됩니다. 현재 Framework가 선택한 클라이언트를 지원하는지 먼저 확인하세요. Boot 프로젝트를 업그레이드할 때는 Boot가 관리하는 호환 조합을 따릅니다. 아래 실행 예제는 7.0.10으로 고정합니다.

## 어떤 상황에서 무엇을 선택하나요?

| 기준 | RestClient | WebClient |
| --- | --- | --- |
| 호출 결과 | 본문 추출 같은 종료 연산에서 응답을 기다려 값 반환 | Mono·Flux로 결과를 표현하고 구독 시 요청 수행 |
| 자연스러운 사용처 | Spring MVC·배치 등 순차적인 동기 코드 | WebFlux·반응형 호출 조합·SSE 등 스트리밍 |
| 오류 전달 | 기본 retrieve 경로의 4xx·5xx는 RestClientResponseException | 기본 retrieve 경로의 4xx·5xx는 WebClientResponseException 오류 신호 |
| 추가 비용 | 일반 호출 스택에서 추적하기 쉬움 | 연산자·구독·취소·컨텍스트 전파를 이해해야 함 |
| 동시성 관리 | 실행기·가상 스레드 등을 별도 설계 | flatMap 등 조합의 동시성과 연결·대기 예산을 별도 설계 |

이 표는 응답을 메모리에 모으는 일반 API 호출을 출발점으로 삼습니다. RestClient도 저수준 응답 처리로 바이트 스트림을 직접 읽을 수 있지만, 반응형 요소 스트림·수요 제어가 필요하면 WebClient가 자연스럽습니다. WebClient를 쓴다고 서버를 반드시 WebFlux로 바꿔야 하지는 않습니다. Spring MVC에서도 반응형 반환 타입을 사용할 수 있습니다. [Spring의 HTTP 클라이언트 선택 안내](https://spring.io/blog/2025/09/30/the-state-of-http-clients-in-spring/)도 일반적인 동기 호출과 반응형·스트리밍 요구를 구분합니다.

가상 스레드를 쓰는 동기식 서비스에서도 RestClient의 순차적인 코드를 유지할 수 있습니다. 다만 가상 스레드는 호출 API를 비차단으로 바꾸거나 외부 서비스·연결 용량을 늘리지 않습니다. [가상 스레드의 적용 범위](/ko/posts/2026-10-31-virtual-threads-jdk21-jdk25/)와 [의존성 용량 제한](/ko/posts/2026-10-31-jdk-10k-rps-architecture/)을 함께 설계합니다.

## 같은 HTTP 응답으로 실행 시점 비교하기

![RestClient 종료 연산으로 첫 응답을 받은 뒤 WebClient의 Mono를 만들고 두 차례 구독해 별도 요청을 수행하며 두 클라이언트의 404·503 오류를 확인하는 흐름](/assets/diagrams/2026-10-31-webclient-restclient-comparison-ko.svg)

그림은 아래 main의 핵심 검증 순서입니다. 로컬 서버 준비·클라이언트 설정·종료 정리는 생략했습니다. **RestClient도 retrieve()만으로 요청을 전송하지 않으며**, 이 예제에서는 body(String.class)가 요청을 수행하고 결과를 기다립니다. WebClient는 bodyToMono로 만든 기본 요청 Mono를 구독할 때 실행합니다. 캐시·공유 연산자가 없는 이 Mono를 두 번 구독하면 요청도 두 번 발생합니다.

Spring Framework 7.0.10·Reactor Core 3.8.8, JDK 17·Gradle 8.4에서 실행한 독립 콘솔 예제입니다. Spring Boot 애플리케이션이 아니며 양쪽 모두 JDK HttpClient를 명시해 기본 커넥터 선택 차이를 제외했습니다. Boot 프로젝트에는 해당 Boot 버전이 관리하는 의존성을 우선 사용하고 이 BOM을 그대로 덮어씌우지 마세요.

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

### 실행과 확인

```sh
gradle --no-daemon --console=plain -q clean run
```

최초 의존성 다운로드에는 네트워크가 필요합니다. 실행 중 HTTP 요청은 임시 포트의 127.0.0.1 서버로만 전송합니다. 다음은 위 환경에서 확인한 애플리케이션 표준 출력입니다. Gradle·로깅 구현의 진단 메시지는 별도로 나올 수 있습니다.

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

0→1은 RestClient의 종료 연산에서 첫 요청이 완료됐다는 뜻입니다. Mono를 구성한 직후에도 요청 수는 1이고, 두 번의 block은 각각 구독하여 2·3으로 늘립니다. 뒤의 네 요청은 404·503 처리 확인이며 최종 합계는 7입니다. 이 횟수는 실행·오류 계약을 확인한 결과이며 처리량·지연·이벤트 루프 성능 비교가 아닙니다.

## block을 쓰면 같은 방식인가요?

WebClient에 block을 붙이면 **호출자는 결과를 기다립니다.** 내부 전송 구현까지 RestClient와 같아지는 것은 아닙니다. [동기 사용 문서](https://docs.spring.io/spring-framework/reference/web/webflux-webclient/client-synchronous.html)처럼 반응형 컨트롤러에서는 Mono·Flux를 반환하고 프레임워크가 구독하게 합니다. 위 block은 동작을 관찰하는 콘솔 main에서만 사용합니다. 이벤트 루프에서 RestClient를 호출하거나 block으로 기다리면 처리 스레드를 붙잡거나 비차단 스레드에서 차단이 금지됐다는 예외를 만날 수 있습니다.

이미 WebClient 기반 필터·인증·관측 설정을 운영하고 있다면 동기 호출이라는 이유만으로 즉시 교체할 필요는 없습니다. 새 동기식 호출을 위해 반응형 의존성과 구독 처리를 도입하는 비용, 기존 설정을 유지하는 비용을 비교합니다. 여러 외부 요청을 동시에 조합할 때도 무제한 구독은 피합니다. [WebFlux의 반응형 수요 제어](https://docs.spring.io/spring-framework/reference/web/webflux/new-framework.html)는 생산·소비 속도를 조율하지만 외부 서비스의 RPS·연결 상한을 자동 보장하지 않습니다.

## 운영 전에는 무엇을 확인하나요?

양쪽 모두 연결·응답 읽기·전체 호출 시간 예산과 오류 상태 정책을 정해야 합니다. 예제의 연결 2초, 읽기 2초, block 대기 5초는 재현용 제한이며 동일한 의미의 시간 제한이나 운영 권장값이 아닙니다. 두 읽기 제한의 적용 범위는 [요청 팩터리](https://docs.spring.io/spring-framework/docs/7.0.10/javadoc-api/org/springframework/http/client/JdkClientHttpRequestFactory.html)·[반응형 커넥터](https://docs.spring.io/spring-framework/docs/7.0.10/javadoc-api/org/springframework/http/client/reactive/JdkClientHttpConnector.html) 문서에서 확인합니다. 이 빠른 로컬 응답 예제로 시간 초과·TLS·취소 전파를 검증한 것은 아닙니다.

기본 retrieve의 4xx·5xx 오류 처리는 양쪽에서 확인했습니다. 상태별 분기가 필요하면 onStatus로 정책을 명시하고, 저수준 exchange 계열은 retrieve의 기본 상태 처리가 그대로 적용된다고 가정하지 않습니다. [WebClient 상태 처리](/ko/posts/2023-09-19-springboot-test-webclient/)와 [시간 제한·제한된 재시도](/ko/posts/2026-10-30-webclient-timeout-retry/) 예제에서 후속 계약을 확인할 수 있습니다. 재시도에는 멱등성·횟수·전체 시간 예산을 두고, 빈 본문·큰 응답·연결 실패도 별도로 시험합니다.

RestTemplate을 사용하는 기존 코드는 별도 이관 대상입니다. Spring Framework 7.0에서는 RestClient를 권장하며 RestTemplate이 deprecated로 표시됩니다. 이는 WebClient가 deprecated라는 뜻이 아닙니다. 선택을 마친 뒤 인증·관측·연결 설정과 실제 요청 분포를 맞춰 검증하세요.
