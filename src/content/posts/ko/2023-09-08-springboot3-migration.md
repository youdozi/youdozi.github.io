---
title: "Spring Boot 3 마이그레이션: Java 17·Jakarta 전환과 검증 순서"
language: "ko"
translationKey: "2023-09-08-springboot3-migration"
routeSlug: "2023-09-08-springboot3-migration"
kind: "post"
publishedAt: "2023-09-07T15:00:00.000Z"
categories:
  - "springboot"
tags:
  - "springboot"
  - "springboot3"
  - "springboot3 migration"
legacyUrl: "/springboot/springboot3-migration/"
legacySource: "_posts/spring/migration/2023-09-08-springboot3-migration.markdown"
updatedAt: 2026-10-27T05:23:47.316+00:00
reviewedAt: "2026-10-27"
reviewStatus: "revised"
reviewScope: "공식 문서 대조, 재현 절차와 버전별 적용 조건 보강"
archiveBodySha256: "1d7de750bbc8801a9fd3e50b28b53820a6e8beede1dde34cc4ee282f000414b5"
reviewSources:
  - "https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.0-Migration-Guide"
  - "https://docs.gradle.org/current/userguide/viewing_debugging_dependencies.html"
  - "https://spring.io/blog/2023/09/09/all-together-now-spring-boot-3-2-graalvm-native-images-java-21-and-virtual"
description: "Spring Boot 2.7에서 3.0으로 옮길 때 Java 17, Jakarta 의존성, Gradle 검사, 설정 변경과 런타임 테스트를 확인하는 순서입니다. 가상 스레드의 버전 조건도 구분합니다."
---
Spring Boot 2.7에서 3.0으로 옮길 때는 Java 17 기준선, Java EE에서 Jakarta로의 패키지 변경, 라이브러리·런타임 호환성을 나눠 확인해야 합니다. 컴파일 성공만으로 DB 매핑·인가·설정이 그대로 동작한다고 판단할 수는 없습니다.

이 글은 2023년에 다룬 **2.7 → 3.0 마이그레이션**의 순서를 정리합니다. 지금 Boot 3.0을 운영에 배포하라는 권장은 아닙니다. 실제 업그레이드에서는 지원 중인 목표 릴리스를 선택하고 중간 버전의 마이그레이션 가이드도 확인하세요. 이 단계의 변경점은 [공식 3.0 가이드](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.0-Migration-Guide)에 나와 있습니다.

## 처리 흐름

![Boot 3 이관 확인 순서 흐름도](/assets/diagrams/2023-09-08-springboot3-migration-ko.svg)

본문에서 제안한 이관 확인 순서입니다. 명령은 환경을 확인하며 애플리케이션이나 데이터베이스를 자동 이관하지 않습니다.

## 1. 정상 동작하는 2.7 기준선 만들기

이전 2.x 프로젝트라면 먼저 최신 2.7.x로 정리합니다. 통과한 테스트 결과와 wrapper·빌드 JVM·의존성 구성을 남깁니다. 기존 Gradle wrapper가 있는 프로젝트에서는 다음 순서로 시작할 수 있습니다.

```sh
java -version
./gradlew --version
./gradlew clean test
./gradlew dependencies --configuration runtimeClasspath
```

업그레이드 후에도 같은 검사를 반복합니다. 멀티 프로젝트라면 의존성 보고서는 애플리케이션 모듈에서 실행합니다. 예를 들어 `./gradlew :app:dependencies --configuration runtimeClasspath`의 `app`은 실제 모듈 이름으로 바꿔야 합니다.

기준선 테스트에는 영속성·인증·직렬화·스케줄 작업·외부 HTTP 호출을 포함하는 것이 좋습니다. 외부 API 경계는 [로컬 MockWebServer를 사용하는 WebClient 테스트](/ko/posts/2023-09-19-springboot-test-webclient/)를 시작점으로 삼을 수 있습니다.

## 2. Java EE import와 의존성을 함께 바꾸기

Boot 3.0의 기준은 Java 17과 Spring Framework 6입니다. `javax.persistence`, `javax.servlet` 같은 Java EE 패키지는 `jakarta.persistence`, `jakarta.servlet`로 옮깁니다. Java SE의 `javax.sql`, `javax.crypto`는 이름을 유지합니다.

| 기존 사용 | 변경 방법 |
| --- | --- |
| `javax.persistence.Entity` | `jakarta.persistence.Entity`와 호환 JPA 의존성을 사용합니다. |
| `javax.servlet.Filter` | `jakarta.servlet.Filter`와 호환 Servlet 의존성을 사용합니다. |
| `javax.sql.DataSource` | Java SE 패키지 이름을 유지합니다. |
| `javax.crypto.Cipher` | Java SE 패키지 이름을 유지합니다. |

import뿐 아니라 실제로 해석된 의존성 그래프도 확인해야 합니다. 예를 들어 `./gradlew dependencyInsight --dependency javax.servlet-api --configuration runtimeClasspath`로 예전 Servlet 아티팩트가 들어오는 경로를 찾을 수 있습니다. 결과가 비어 있다고 애플리케이션 전체가 전환된 것은 아닙니다. 실제 사용하는 다른 라이브러리와 configuration도 확인하세요. [Gradle 의존성 보고서 안내](https://docs.gradle.org/current/userguide/viewing_debugging_dependencies.html)를 참고할 수 있습니다.

Querydsl JPA는 JPA 아티팩트와 annotation processor를 맞추고 해당 아티팩트 계열에서 요구하는 Jakarta 변형을 선택합니다. Q 타입 생성과 대표 쿼리 실행까지 확인해야 합니다. Gradle의 `configureEach`는 태스크 설정 방식을 제어하므로 Java EE 의존성의 Jakarta 호환성 문제를 해결해 주지 않습니다. 기존 [Querydsl 적용 글](/ko/posts/2023-09-09-springboot3-querydsl/)도 의존성을 확인할 때 함께 참고하세요.

## 3. 변경된 설정과 인가 동작 확인하기

Boot의 의존성 관리가 적용된 Gradle 프로젝트에서는 공식 가이드의 임시 설정 도우미를 사용할 수 있습니다.

```groovy
dependencies {
    runtimeOnly 'org.springframework.boot:spring-boot-properties-migrator'
}
```

테스트 환경에서 애플리케이션을 시작해 진단 메시지를 읽고 해당 설정을 수정합니다. 전환이 끝나면 도우미를 제거합니다. 이 모듈이 목표 릴리스의 설정 변경점 확인을 대신해 주지는 않습니다.

Boot 3.0은 Spring Security 6도 사용합니다. 공식 가이드는 Boot 2.7에서 Spring Security 5.8을 거치는 전환을 제안합니다. 허용·거부·미인증 요청을 테스트하고 Servlet 애플리케이션에서 사용하는 error/forward dispatch도 확인하세요. 애플리케이션이 시작된 것만으로 인가 검증을 마칠 수는 없습니다.

## 4. 가상 스레드는 별도 변경으로 다루기

Boot의 가상 스레드 설정은 **Boot 3.2와 JDK 21** 조합에 추가됐으며 Boot 3.0의 기능이 아닙니다.

```properties
spring.threads.virtual.enabled=true
```

이는 기능이 도입된 버전의 구분이며 지금 Boot 3.2를 선택하라는 권장은 아닙니다. 먼저 패키지와 의존성 전환이 정상인지 확인한 뒤, 선택한 릴리스·커넥션 풀·ThreadLocal 사용에 맞춰 가상 스레드를 평가하세요. 설정 하나로 성능 향상이 입증되지는 않습니다. [Spring의 Boot 3.2 설명](https://spring.io/blog/2023/09/09/all-together-now-spring-boot-3-2-graalvm-native-images-java-21-and-virtual)을 참고할 수 있습니다.

JDK 언어 미리보기에도 별도의 버전 조건이 있습니다. [String Templates 호환성 예제](/ko/posts/2023-09-23-jdk-21-string-templates/)는 preview 옵션이 일반적인 업그레이드 해결책이 될 수 없는 이유를 보여줍니다.

## 배포 준비 판단하기

| 검사 | 남길 근거 |
| --- | --- |
| 빌드와 생성 코드 | wrapper 빌드 통과, 예상 Q 타입과 실제 의존성 버전 |
| 런타임 동작 | 영속성·인증·대표 HTTP 테스트 통과 |
| 설정 | 변경된 설정 반영과 임시 도우미 제거 |
| 배포 | 대표 환경에서 배포 아티팩트 검사 통과 |

위 명령은 각 프로젝트에서 수행할 진단 순서이며 사용자 애플리케이션의 마이그레이션을 실행한 결과가 아닙니다. 이전 아티팩트와 설정도 롤백할 수 있도록 보관해야 합니다. 메이저 버전 전환은 유지보수의 기반이지만 실제 보안 상태는 배포한 의존성 버전과 설정에 달려 있습니다.
