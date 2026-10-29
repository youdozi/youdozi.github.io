---
title: Spring Boot 릴리스 역사와 Spring Framework 버전 관계
language: ko
translationKey: 2023-09-13-springboot-history
routeSlug: 2023-09-13-springboot-history
kind: post
publishedAt: 2023-09-12T15:00:00.000Z
categories:
  - springboot
tags:
  - springboot
  - history
legacyUrl: /springboot/springboot-history/
legacySource: _posts/spring/history/2023-09-13-springboot-history.markdown
updatedAt: 2026-10-27T05:23:47.316+00:00
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Official documentation checked; CLI/project execution distinguished
  from IDE UI verification.
archiveBodySha256: 4571910a9c9e9947a392264e08fbc211d4f7654bdf22cef5d53a4315871afe53
reviewSources:
  - https://spring.io/blog/2014/12/11/spring-boot-1-2-0-released/
  - https://spring.io/blog/2015/11/16/spring-boot-1-3-0-released/
  - https://spring.io/blog/2016/07/28/spring-boot-1-4-released/
  - https://spring.io/blog/2018/03/01/spring-boot-2-0-goes-ga/
  - https://spring.io/blog/2022/11/24/spring-boot-3-0-goes-ga/
  - https://spring.io/blog/2023/05/18/spring-boot-3-1-0-available-now/
  - https://spring.io/blog/2023/11/23/spring-boot-3-2-0-available-now/
  - https://spring.io/blog/2025/11/20/spring-boot-4-0-0-available-now/
  - https://docs.spring.io/spring-boot/docs/3.1.0/reference/html/dependency-versions.html
  - https://docs.spring.io/spring-boot/4.1/gradle-plugin/managing-dependencies.html
description: Spring Boot 1.2부터 4.0까지 주요 출시를 공식 공지로 확인하고,
  Boot·Framework·starter·BOM의 차이와 실제 의존성 버전 조회 방법을 정리합니다.
---
Spring Boot와 Spring Framework는 버전 번호가 다른 프로젝트입니다. Boot는 Framework 위에서 자동 구성·의존성 관리·실행 패키징을 제공하므로, Boot 3.1을 Framework 6.1로 읽는 식으로 숫자를 대응시키면 안 됩니다. 실제 조합은 해당 Boot 버전의 BOM과 해석된 의존성 그래프로 확인하세요.

## 처리 흐름

![실제 구성요소 버전 확인 흐름도](/assets/diagrams/2023-09-13-springboot-history-ko.svg)

그림은 릴리스 연표가 아닌 의존성 확인 순서입니다. Boot·Framework·Lombok 버전과 의존성 구성은 서로 구분합니다.

## 주요 정식 릴리스의 변화

다음은 전체 릴리스 목록이 아니라 기능 전환을 보여주는 연표입니다. 첫 정식 릴리스의 변화와 이후 패치의 JDK 지원 확대를 구분해야 합니다.

| Spring Boot | 첫 정식 출시 | 대표 변화와 공식 공지 |
| --- | --- | --- |
| 1.2 | 2014-12-11 | [`@SpringBootApplication`, Servlet 3.1 지원](https://spring.io/blog/2014/12/11/spring-boot-1-2-0-released/) |
| 1.3 | 2015-11-16 | [DevTools·캐시 자동 구성·직접 실행 가능한 JAR](https://spring.io/blog/2015/11/16/spring-boot-1-3-0-released/) |
| 1.4 | 2016-07-28 | [시작 실패 분석과 테스트 지원 개선](https://spring.io/blog/2016/07/28/spring-boot-1-4-released/) |
| 2.0 | 2018-03-01 | [Framework 5.0 기반, Java 8 기준, 리액티브 웹 지원](https://spring.io/blog/2018/03/01/spring-boot-2-0-goes-ga/) |
| 3.0 | 2022-11-24 | [Framework 6.0, Java 17 기준, Jakarta·네이티브 이미지 지원](https://spring.io/blog/2022/11/24/spring-boot-3-0-goes-ga/) |
| 3.1 | 2023-05-18 | [Testcontainers·Docker Compose 개발 서비스 연동](https://spring.io/blog/2023/05/18/spring-boot-3-1-0-available-now/) |
| 3.2 | 2023-11-23 | [가상 스레드·RestClient·JdbcClient 지원](https://spring.io/blog/2023/11/23/spring-boot-3-2-0-available-now/) |
| 4.0 | 2025-11-20 | [Framework 7 기반, 모듈화·JSpecify·API 버저닝](https://spring.io/blog/2025/11/20/spring-boot-4-0-0-available-now/) |

예를 들어 [Boot 3.1.0의 관리 목록](https://docs.spring.io/spring-boot/docs/3.1.0/reference/html/dependency-versions.html)에서 `spring-core`는 6.0.9입니다. Boot의 minor 버전과 Framework의 minor 버전이 같아야 한다는 규칙은 없습니다. 존재하지 않는 Framework 5.4 계열을 Boot 2.4와 연결하는 것도 잘못입니다.

## Starter, BOM, 빌드 플러그인의 역할

Starter는 특정 기능에 필요한 의존성을 묶습니다. BOM은 함께 사용할 의존성의 버전을 관리하며, 선언하지 않은 모든 라이브러리를 자동으로 추가하는 목록이 아닙니다. Boot의 빌드 플러그인은 `bootRun`·실행 JAR 패키징 같은 작업을 제공합니다.

Gradle에서는 [Boot의 의존성 관리 안내](https://docs.spring.io/spring-boot/4.1/gradle-plugin/managing-dependencies.html)에 따라 dependency-management 플러그인 또는 네이티브 BOM 지원을 선택합니다. Boot 플러그인만 적용했다는 사실과 모든 Gradle 구성에서 버전 생략이 가능하다는 주장은 구분해야 합니다. annotation processor처럼 별도의 구성도 확인합니다.

## 내 프로젝트의 실제 버전 확인

[Initializr](/ko/posts/2023-09-07-springboot-initializer/)와 [Lombok 예제](/ko/posts/2023-09-15-springboot-intellij-lombok/)의 최종 프로젝트에서 실행합니다.

```sh
./gradlew dependencyInsight --configuration runtimeClasspath --dependency spring-core
./gradlew dependencyInsight --configuration annotationProcessor --dependency lombok
```

해당 예제의 로컬 해석 결과는 Boot 4.1.2, `spring-core` 7.0.10, Lombok 1.18.48입니다. 숫자가 다른 것은 프로젝트가 서로 다르기 때문입니다. `dependencyInsight`는 최종 선택 버전과 어떤 의존성·규칙으로 선택됐는지 함께 보여주므로 버전 충돌을 조사하는 데 사용할 수 있습니다. 이 숫자는 예제의 실행 기록이며 향후 기본값이나 모든 프로젝트의 조합을 뜻하지 않습니다.

연표는 현재 지원 기간 표가 아닙니다. 신규 생성과 업그레이드에서는 선택한 버전의 요구 사항·의존성 호환성·지원 정책을 따로 확인하세요. Boot 3로의 전환은 [Java 17과 Jakarta 이관](/ko/posts/2023-09-08-springboot3-migration/)을, 실제 로컬 실행은 [IntelliJ·Gradle 실행 점검](/ko/posts/2023-09-10-springboot-intellij-import/)을 참고할 수 있습니다.
