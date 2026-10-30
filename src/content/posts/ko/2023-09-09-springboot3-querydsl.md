---
title: "Spring Boot 3 Querydsl 설정: Jakarta 의존성과 Q 타입 생성"
language: "ko"
translationKey: "2023-09-09-springboot3-querydsl"
routeSlug: "2023-09-09-springboot3-querydsl"
kind: "post"
publishedAt: "2023-09-07T15:00:00.000Z"
categories:
  - "springboot"
tags:
  - "springboot"
  - "springboot3"
  - "querydsl"
legacyUrl: "/springboot/springboot3-querydsl/"
legacySource: "_posts/spring/migration/2023-09-09-springboot3-querydsl.markdown"
updatedAt: 2026-10-30T04:11:22.994096+00:00
reviewedAt: "2026-10-30"
reviewStatus: "revised"
reviewScope: "공식 문서 대조 및 Gradle Q 타입 생성·H2 조회 테스트 재현"
archiveBodySha256: "745e0ab660d077632d64c79624ffcf6a0c2b2b7d551068b6a8d5b098e27c5e73"
reviewSources:
  - "https://github.com/querydsl/querydsl/releases/tag/QUERYDSL_5_0_0"
  - "https://docs.gradle.org/current/userguide/java_plugin.html"
  - "https://docs.gradle.org/current/userguide/lazy_configuration.html"
  - "https://docs.spring.io/spring-boot/3.5/reference/testing/spring-boot-applications.html"
  - "https://docs.oracle.com/en/java/javase/17/docs/api/java.compiler/javax/annotation/processing/Generated.html"
description: "Spring Boot 3의 Jakarta 의존성과 annotation processor를 맞춰 Querydsl Q 타입을 생성하고, clean 빌드와 H2 조회 테스트로 확인합니다."
---
Spring Boot 3에서 Querydsl JPA Q 타입을 생성하려면 `querydsl-jpa`와 `querydsl-apt`의 버전·`jakarta` classifier를 맞추고 annotation processor를 설정한 뒤, clean 빌드와 DB 조회 테스트를 확인하세요. Jakarta classifier 지원은 [Querydsl 5.0 릴리스 설명](https://github.com/querydsl/querydsl/releases/tag/QUERYDSL_5_0_0)에 나와 있습니다. Gradle 기본 생성 경로를 유지하면 main·test 컴파일을 같은 출력 디렉터리에 쓰도록 설정하는 일을 피할 수 있습니다.

기존 2023년 한국어 예제를 실행 가능한 구성으로 정리한 글입니다. 아래에서 고정한 버전은 재현 환경이며 최신 운영 조합의 권장은 아닙니다.

## 처리 흐름

![Q 타입 생성과 쿼리 실행 흐름도](/assets/diagrams/2023-09-09-springboot3-querydsl-ko.svg)

메인 컴파일의 프로세서가 QEmployee를 생성합니다. 이후 H2 테스트가 생성 타입을 사용한 쿼리를 실행합니다.

## 실행 환경과 전체 Gradle 설정

| 구성 요소 | 재현 버전 |
| --- | --- |
| JDK / Gradle | 17.0.8.1 / 8.4 |
| Spring Boot BOM | 3.5.7 |
| Querydsl JPA / APT | 5.1.0, 모두 `jakarta` classifier |
| Hibernate / H2 | 6.6.33.Final / 2.3.232, BOM으로 관리 |

새 디렉터리에 다음 다섯 파일을 만듭니다. Java 플러그인과 Boot BOM을 사용하는 테스트 프로젝트이며, 이 예제에는 Boot Gradle 플러그인이 필요하지 않습니다. 기존 Boot 프로젝트라면 적용 중인 의존성 관리에 맞춰 필요한 항목만 추가하세요.

### `settings.gradle`

```groovy
rootProject.name = 'querydsl-jakarta-example'
```

### `build.gradle`

```groovy
plugins { id 'java' }
repositories { mavenCentral() }
dependencies {
    implementation platform('org.springframework.boot:spring-boot-dependencies:3.5.7')
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    implementation 'com.querydsl:querydsl-jpa:5.1.0:jakarta'

    annotationProcessor platform('org.springframework.boot:spring-boot-dependencies:3.5.7')
    annotationProcessor 'com.querydsl:querydsl-apt:5.1.0:jakarta'
    annotationProcessor 'jakarta.persistence:jakarta.persistence-api'
    annotationProcessor 'jakarta.annotation:jakarta.annotation-api'

    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testRuntimeOnly 'com.h2database:h2'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
test { useJUnitPlatform() }
```

`annotationProcessor`는 일반 컴파일·실행 클래스패스와 별도로 해석됩니다. 그래서 예제는 processor 쪽에도 BOM을 적용하고 Jakarta Persistence·Annotation API를 명시합니다. `implementation`에 의존성이 있다는 이유만으로 processor에서도 사용할 수 있는 것은 아닙니다. [Gradle Java 플러그인 안내](https://docs.gradle.org/current/userguide/java_plugin.html)를 참고하세요.

## 엔티티와 애플리케이션 만들기

애플리케이션 클래스는 JPA 테스트가 사용할 Boot 설정을 찾는 기준입니다. 테스트를 위해 별도의 서버 프로세스를 시작할 필요는 없습니다.

### `src/main/java/example/Application.java`

```java
package example;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

### `src/main/java/example/Employee.java`

```java
package example;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;

@Entity
public class Employee {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;

    public String getName() { return name; }

    protected Employee() {}

    public Employee(String name) {
        this.name = name;
    }
}
```

`Employee`는 `jakarta.persistence`를 사용합니다. 아래 테스트가 참조하는 `QEmployee`는 직접 작성하지 않고 annotation processor가 생성하게 둡니다.

## 생성된 Q 타입으로 조회하기

### `src/test/java/example/EmployeeQueryTest.java`

```java
package example;

import com.querydsl.jpa.impl.JPAQueryFactory;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.boot.test.autoconfigure.orm.jpa.TestEntityManager;

import static org.assertj.core.api.Assertions.assertThat;

@DataJpaTest
class EmployeeQueryTest {
    @Autowired
    private TestEntityManager entityManager;

    @Test
    void findsEmployeeByName() {
        entityManager.persistAndFlush(new Employee("Alice"));
        entityManager.persistAndFlush(new Employee("Bob"));
        QEmployee employee = QEmployee.employee;
        var names = new JPAQueryFactory(entityManager.getEntityManager())
            .select(employee.name).from(employee)
            .where(employee.name.eq("Alice")).fetch();
        assertThat(names).containsExactly("Alice");
    }

    @Test
    void returnsNoRowsForMissingName() {
        entityManager.persistAndFlush(new Employee("Alice"));
        QEmployee employee = QEmployee.employee;
        var names = new JPAQueryFactory(entityManager.getEntityManager())
            .select(employee.name).from(employee)
            .where(employee.name.eq("Missing")).fetch();
        assertThat(names).isEmpty();
    }
}
```

`@DataJpaTest`는 이 예제에서 클래스패스의 H2를 사용합니다. 각 테스트는 트랜잭션 안에서 실행되고 종료 후 롤백됩니다. `persistAndFlush`로 데이터를 넣은 뒤 생성된 `QEmployee`를 이용해 이름 일치와 결과 없음의 두 동작을 확인합니다. [Spring Boot의 JPA 테스트 안내](https://docs.spring.io/spring-boot/3.5/reference/testing/spring-boot-applications.html#testing.spring-boot-applications.autoconfigured-spring-data-jpa-tests).

이 검사는 H2에서 해당 엔티티와 쿼리가 동작함을 확인합니다. 운영 DB의 SQL 방언·문자열 비교 및 정렬 규칙·잠금·마이그레이션까지 검증한 결과는 아닙니다.

## 실행하고 생성 경로 확인하기

JDK 17을 선택하고 Gradle 8.4가 설치된 환경에서 프로젝트 루트에서 실행합니다.

```sh
java -version
gradle --version
gradle --no-daemon clean test
```

다음 두 산출물과 테스트 보고서를 확인하세요.

```text
build/generated/sources/annotationProcessor/java/main/example/QEmployee.java
build/classes/java/main/example/QEmployee.class
build/reports/tests/test/index.html
```

본문 구성으로 두 테스트가 통과했습니다. `clean test`를 다시 실행해도 Q 타입이 재생성되고 두 테스트가 통과하는 것을 확인했습니다. Gradle wrapper가 있는 기존 프로젝트에서는 선택한 버전의 `./gradlew clean test`를 사용하세요.

이 예제의 Q 타입에 있는 `javax.annotation.processing.Generated`는 Java SE의 `java.compiler` API입니다. 이 import를 Jakarta로 바꿀 필요는 없습니다. [JDK 17 Generated API](https://docs.oracle.com/en/java/javase/17/docs/api/java.compiler/javax/annotation/processing/Generated.html).

<span id="q-타입이-없거나-중복-생성될-때"></span>

## Q 타입이 없거나 중복 생성되는 이유는 무엇인가요?

| 증상 | 먼저 확인할 것 |
| --- | --- |
| `QEmployee`를 찾을 수 없음 | CLI의 `clean compileJava` 결과와 `annotationProcessor` 의존성, 엔티티의 `jakarta.persistence` import를 확인합니다. |
| processor에서 Persistence API를 찾지 못함 | 일반 클래스패스와 별개로 processor 경로에 필요한 Jakarta API가 있는지 확인합니다. |
| `javax.persistence.EntityManager`와 타입이 맞지 않음 | `querydsl-jpa`와 `querydsl-apt`가 같은 버전·Jakarta classifier인지 확인합니다. |
| Q 타입이 중복되거나 clean 후에만 동작함 | 수동 Q 소스와 공유 생성 경로를 제거하고 main·test의 출력 설정을 확인합니다. |
| CLI는 통과하지만 IDE에서만 Q 타입이 안 보임 | Gradle 프로젝트 동기화와 IDE의 빌드 위임·annotation processing 설정을 확인합니다. |

본문은 생성 경로를 바꾸는 `sourceSets`, `JavaCompile`, 별도 `clean` 코드를 추가하지 않습니다. 사용자 지정 경로가 꼭 필요하다면 main·test를 분리해야 합니다. `configureEach`는 태스크의 지연 구성을 제어하며 Jakarta 의존성 호환성을 해결하는 기능은 아닙니다. [Gradle 지연 구성 안내](https://docs.gradle.org/current/userguide/lazy_configuration.html).

JPA 설정 전에 전체 업그레이드 순서를 확인하려면 [Spring Boot 3 마이그레이션](/ko/posts/2023-09-08-springboot3-migration/)을, 외부 API 경계 테스트는 [WebClient와 MockWebServer 예제](/ko/posts/2023-09-19-springboot-test-webclient/)를 참고하세요.

## 쿼리 도구를 바꾸기 전에 비교하기

전체 Employee 클래스에는 저장소 결과를 이름으로 비교하도록 getter를 포함했습니다. 같은 엔티티에 [Querydsl·Specification 비교 예제](/ko/posts/2023-09-05-querydsl-no-release/)의 파일 3개를 추가하면 검사 8개를 더 실행합니다. 위의 기존 테스트 2개도 총 10개 프로젝트에 유지됩니다. 선택한 H2 조건을 비교하며 모든 DB 동작을 검증하는 것은 아닙니다. 주변 설정·테스트 순서는 [Spring Boot 안내](/ko/categories/springboot/)에서 이어집니다.
