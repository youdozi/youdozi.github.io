---
layout: posts
title: "[springboot] springboot test webclient"
date: 2023-09-19 00:00:00 +0900
categories:
  - springboot
tags:
  - springboot
  - test
  - webclient
---

## 개요

신규 API를 개발하면서 있었던 일입니다.  
외부 API를 호출하고 해당 응답 값을 가져오기만 하는 간단한 작업이었습니다.  
외부 API와의 스펙은 이미 공유되어 있고 그것에 맞춰 개발만 하면 되는 것이었습니다.  
하지만 세상사 모든게 만만한게 아니었죠.  
외부 API는 평시에는 전혀 문제 없었으나 모종의 이유로 content-type이  
`application/json`에서 `text/html`로 변경 되며 html로 구성된 에러 메시지가 노출됩니다.  
만약 내가 `webclient`를 사용 하고 있을때..   
이런 경우가 흔하지는 않지만 손쉽게 테스트하는 방법이 있을까?  
이런 고민을 나눠보도록 하겠습니다.

[참고 - https://www.baeldung.com/spring-mocking-webclient](https://www.baeldung.com/spring-mocking-webclient)

## 기존엔 어떤 테스트를 사용하셨나요?

`@SpringBootTest`기반의 테스트가 많았습니다.  
`@SpringBootTest`는 실제로 springboot를 가동하기 때문에  
spring context를 전부 다 사용할 수 있는 장점이 있습니다. 하지만 그만큼 단점도 많죠.  
간단하게 정리 하자면 아래와 같습니다.
* 무거움 -> springboot 가동
* 외부(DB, API) 연동시 직접 연동 -> DB `CUD` 이벤트일 경우 `@Transactional` 어노테이션을 이용하여 롤백하면 되지만 DB 부담이 큼

물론 `@SpringBootTest` 뿐만 아니라 `mockito`를 이용한 테스트도 사용합니다.  
다만..`webclient`의 메소드 체이닝을 전부 다 `mockito`로 구현 하기엔 많은 번거로움이 있습니다.  
여기서는 `mockito`와 좀 더 개선된 `webclient` 테스트 환경을 제공해 주는 `MockWebServer`에 대해 이야기 해 보도록 하겠습니다.

## mocking 방법
* mockito을 이용한 webclient mocking
* mockWebServer를 이용하여 실제 webclient 작동

## mockito
일반적으로 `mockito`를 많이 사용하죠.  
메소드 호출에 대한 응답 값을 미리 정의할 수 있기 때문에 선호하는 라이브러리입니다.

### EmployeeRepository
```java
public class EmployeeRepository {

    public EmployeeRepository(String baseUrl) {
        this.webClient = WebClient.create(baseUrl);
    }
    public Mono<Employee> getEmployeeById(Integer employeeId) {
        return webClient
                .get()
                .uri("http://localhost:8080/employee/{id}", employeeId)
                .retrieve()
                .bodyToMono(Employee.class);
    }
}
```
* `webclient` repository 코드를 생성합니다.

### EmployeeRepositoryTest
```java
@ExtendWith(MockitoExtension.class)
public class EmployeeRepositoryTest {
  
    private final EmployeeRepository employeeRepository;
   
    @Test
    void givenEmployeeId_whenGetEmployeeById_thenReturnEmployee() {

        Integer employeeId = 100;
        Employee mockEmployee = new Employee(100, "Adam", "Sandler", 
          32, Role.LEAD_ENGINEER);
        when(webClientMock.get())
          .thenReturn(requestHeadersUriSpecMock);
        when(requestHeadersUriMock.uri("/employee/{id}", employeeId))
          .thenReturn(requestHeadersSpecMock);
        when(requestHeadersMock.retrieve())
          .thenReturn(responseSpecMock);
        when(responseMock.bodyToMono(Employee.class))
          .thenReturn(Mono.just(mockEmployee));

        Mono<Employee> employeeMono = employeeRepository.getEmployeeById(employeeId);

        StepVerifier.create(employeeMono)
          .expectNextMatches(employee -> employee.getRole()
            .equals(Role.LEAD_ENGINEER))
          .verifyComplete();
    }

}
```
* `webclient` 메소드 체이닝마다 when/thenReturn mocking 데이터를 적용합니다.

위 테스트 코드를 보면 알겠지만 상당히 복잡합니다.
메소드 체이닝마다 mocking 데이터를 삽입해야 하기 때문에 코드가 늘어나죠.  
그 이유는 `webclient`가 `fluent interface`로 설계되었기 때문입니다.  

[참고 - fluent interface](https://ko.wikipedia.org/wiki/%ED%94%8C%EB%A3%A8%EC%96%B8%ED%8A%B8_%EC%9D%B8%ED%84%B0%ED%8E%98%EC%9D%B4%EC%8A%A4)

자 다음은 `MockWebServer`를 사용 해 보도록 하겠습니다.

## MockWebServer
`MockWebServer`는 `baeldung`에서 말하길 HTTP 요청을 수신하고 응답할 수 있는 작은 웹 서버입니다.  
실제로 응답을 받을 수 있기 때문에 endpoint 응답만 정의해 놓으면 손쉽게 사용할 수 있습니다.  
MSA 환경이라면 더욱 더 필수죠. 단점이라면 아래 종속성 추가되는 부분이라고 생각됩니다.  

### 종속성 추가
```groovy
dependencies {
    testImplementation 'com.squareup.okhttp3:okhttp:4.11.0'
    testImplementation 'com.squareup.okhttp3:mockwebserver:4.11.0'
}
```
build.gradle에 okhttp, mockwebserver 종속성을 추가합니다.

### mockWebServerTest
```java
@ExtendWith(MockitoExtension.class)
class MockWebServerTests {

  public static MockWebServer mockWebServer;

  private final ObjectMapper objectMapper = new ObjectMapper();

  private WebClient webClient;

  @BeforeAll
  static void setUp() throws IOException {
    mockWebServer = new MockWebServer();
    mockWebServer.start();
  }

  @AfterAll
  static void down() throws IOException {
    mockWebServer.shutdown();
  }

  @BeforeEach
  void initialize() {
    String baseUrl = String.format("http://localhost:%s", mockWebServer.getPort());
    this.webClient = WebClient.create(baseUrl);
  }

  @Test
  void getErrorHtmlResponse() throws Exception {
    String response = """
        <html>
            <head>
                <META http-equiv="Content-Type" content="text/html; charset=UTF-8">
            </head>
            <body>
                <div align="center">
                    <div>500 Internal Server Error</div>
                    <div><P>Unknown failure</P></div>
                </div>
            </body>
        </html>
        """;

    mockWebServer.enqueue(new MockResponse()
        .setBody(objectMapper.writeValueAsString(response))
        .addHeader("Content-Type", "text/html"));

    Mono<Response> respone = webClient
        .get()
        .uri("/error")
        .accept(MediaType.APPLICATION_JSON)
        .exchangeToMono(clientResponse -> {
          if (isNotSupportedContentType(clientResponse)) {
            return clientResponse.bodyToMono(String.class)
                .flatMap(errorBody -> Mono.error(new RuntimeException(errorBody)));
          }
          return clientResponse.bodyToMono(Response.class);
        });

    StepVerifier.create(respone)
        .expectErrorMatches(throwable -> throwable instanceof ConnectException &&
            throwable.getMessage().contains("500 Internal Server Error") &&
            throwable.getMessage().contains("Unknown failure"))
        .verify();

    RecordedRequest recordedRequest = mockWebServer.takeRequest();
    assertEquals("GET", recordedRequest.getMethod());
  }

  private boolean isNotSupportedContentType(ClientResponse clientResponse) {
    return clientResponse.headers().contentType()
        .stream()
        .anyMatch(contentType -> contentType.includes(MediaType.TEXT_HTML));
  }
}
```
* BeforeAll, AfterAll 단계에서 mockwebserver 시작/종료를 담당합니다.
* BeforeEach 단계에서 endpoint를 지정합니다.
* getErrorHtmlResponse 메소드에서 실제 webclient를 연동하는 테스트를 진행합니다.

단락별로 나눠서 보도록 하겠습니다.
```java
    String response = """
        <html>
            <head>
                <META http-equiv="Content-Type" content="text/html; charset=UTF-8">
            </head>
            <body>
                <div align="center">
                    <div>500 Internal Server Error</div>
                    <div><P>Unknown failure</P></div>
                </div>
            </body>
        </html>
        """;

    mockWebServer.enqueue(new MockResponse()
        .setBody(objectMapper.writeValueAsString(response))
        .addHeader("Content-Type", "text/html"));
```
먼저 `text/html`로 응답 하는 부분을 mocking할 수 있도록 생성합니다.
또한 content-type은 `text/html`로 정의합니다.
```java
    Mono<Response> respone = webClient
        .get()
        .uri("/error")
        .accept(MediaType.APPLICATION_JSON)
        .exchangeToMono(clientResponse -> {
          if (isNotSupportedContentType(clientResponse)) {
            return clientResponse.bodyToMono(String.class)
                .flatMap(errorBody -> Mono.error(new RuntimeException(errorBody)));
          }
          return clientResponse.bodyToMono(Response.class);
        });

    StepVerifier.create(respone)
        .expectErrorMatches(throwable -> throwable instanceof ConnectException &&
            throwable.getMessage().contains("500 Internal Server Error") &&
            throwable.getMessage().contains("Unknown failure"))
        .verify();
    
    ...

    private boolean isNotSupportedContentType(ClientResponse clientResponse) {
        return clientResponse.headers().contentType()
        .stream()
        .anyMatch(contentType -> contentType.includes(MediaType.TEXT_HTML));
    }
```
`webclient` exchangeToMono 체이닝 단계에서 `content-type`에 따른 분기 처리합니다.
* `isNotSupportedContentType` 메소드를 통해 `content-type`에 `text/html`이 포함 여부를 체크합니다.

`StepVerifier`를 통해 테스트 결과를 검증합니다.

![test_result.png](/assets%2Fimg%2Fspringboot%2Ftest%2Fwebclient%2Ftest_result.png)  

정상적으로 잘 작동된 것을 볼 수 있습니다.