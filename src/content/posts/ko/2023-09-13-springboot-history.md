---
title: "[springboot] springboot history"
language: "ko"
translationKey: "2023-09-13-springboot-history"
routeSlug: "2023-09-13-springboot-history"
kind: "post"
publishedAt: "2023-09-12T15:00:00.000Z"
categories:
  - "springboot"
tags:
  - "springboot"
  - "history"
legacyUrl: "/springboot/springboot-history/"
legacySource: "_posts/spring/history/2023-09-13-springboot-history.markdown"
updatedAt: "2026-10-24T09:00:00+09:00"
reviewedAt: "2026-10-24"
reviewStatus: "revised"
reviewScope: "공식 릴리스 공지·의존성 목록 대조 및 잘못된 연표 정정"
archiveBodySha256: "4571910a9c9e9947a392264e08fbc211d4f7654bdf22cef5d53a4315871afe53"
reviewSources:
  - "https://spring.io/blog/2014/12/11/spring-boot-1-2-0-released/"
  - "https://spring.io/blog/2015/11/16/spring-boot-1-3-0-released/"
  - "https://spring.io/blog/2016/07/28/spring-boot-1-4-released/"
  - "https://spring.io/blog/2018/03/01/spring-boot-2-0-goes-ga/"
  - "https://spring.io/blog/2022/11/24/spring-boot-3-0-goes-ga/"
  - "https://spring.io/blog/2023/05/18/spring-boot-3-1-0-available-now/"
  - "https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.2-Release-Notes"
  - "https://docs.spring.io/spring-boot/docs/2.3.0.RELEASE/reference/html/dependency-versions.html"
  - "https://docs.spring.io/spring-boot/docs/2.4.0/reference/html/dependency-versions.html"
  - "https://docs.spring.io/spring-boot/docs/3.1.0/reference/html/dependency-versions.html"
---
## Spring Boot와 Spring Framework 구분

Spring Boot는 Spring Framework 위에서 자동 구성, 의존성 관리와 실행 가능한 애플리케이션 패키징을 제공하는 프로젝트입니다. 두 프로젝트의 버전 번호는 별개입니다. Boot 3.1을 Framework 6.1과 연결하거나 Boot 2.4를 존재하지 않는 Framework 5.4 계열과 연결했던 원문을 정정했습니다.

아래 표는 **첫 정식 릴리스의 대표 변화**를 정리한 것입니다. 각 계열의 후속 패치에서 추가된 JDK 지원 범위를 첫 릴리스와 혼동하지 않아야 합니다.

| Spring Boot | 첫 정식 출시 | 대표 변화 |
| --- | --- | --- |
| 1.2 | 2014-12-11 | `@SpringBootApplication`, Tomcat 8/Jetty 9 기본 구성 |
| 1.3 | 2015-11-16 | 개발 도구, 캐시 자동 구성, 실행 가능한 JAR 개선 |
| 1.4 | 2016-07-28 | 시작 실패 분석, 테스트 슬라이스와 테스트 지원 개선 |
| 2.0 | 2018-03-01 | Spring Framework 5 기반, 리액티브 웹 개발 지원 |
| 3.0 | 2022-11-24 | Java 17 최소 기준, Framework 6.0, Jakarta EE 및 GraalVM 네이티브 이미지 지원 |
| 3.1 | 2023-05-18 | Testcontainers·Docker Compose 연동과 개발 서비스 구성 개선 |
| 3.2 | 2023-11-23 | Framework 6.1 기반, JDK 21 가상 스레드 지원 |

## 버전 대응 관계

Boot 2.3은 Framework 5.2 계열, Boot 2.4~2.7은 5.3 계열입니다. Boot 3.0~3.1은 6.0 계열, Boot 3.2는 6.1 계열입니다. 정확한 패치 버전은 해당 Boot 버전의 의존성 관리 목록에서 확인하세요. 초기 Boot 2.0의 JUnit 5 사용 가능 여부와 이후 버전의 기본 테스트 구성도 구분해야 합니다.

Starter는 의존성 집합을 제공하며 BOM은 함께 사용할 의존성 버전을 관리합니다. Spring IO라는 이름의 출시 시점을 starter와 BOM이 처음 도입된 시점이라고 단정할 수는 없습니다.

## 이 글의 적용 범위

2026-10-24에 공식 릴리스 공지를 대조해 과거 연표를 정정했습니다. 이 표는 최신 버전이나 현재 지원 종료 여부를 안내하는 표가 아닙니다. 신규 프로젝트와 업그레이드 대상은 지원 정책, 사용하는 JDK·서드파티 라이브러리와 함께 선택해야 합니다.

## 확인한 자료

- [공식 자료 1](https://spring.io/blog/2014/12/11/spring-boot-1-2-0-released/)
- [공식 자료 2](https://spring.io/blog/2015/11/16/spring-boot-1-3-0-released/)
- [공식 자료 3](https://spring.io/blog/2016/07/28/spring-boot-1-4-released/)
- [공식 자료 4](https://spring.io/blog/2018/03/01/spring-boot-2-0-goes-ga/)
- [공식 자료 5](https://spring.io/blog/2022/11/24/spring-boot-3-0-goes-ga/)
- [공식 자료 6](https://spring.io/blog/2023/05/18/spring-boot-3-1-0-available-now/)
- [공식 자료 7](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.2-Release-Notes)
- [공식 자료 8](https://docs.spring.io/spring-boot/docs/2.3.0.RELEASE/reference/html/dependency-versions.html)
- [공식 자료 9](https://docs.spring.io/spring-boot/docs/2.4.0/reference/html/dependency-versions.html)
- [공식 자료 10](https://docs.spring.io/spring-boot/docs/3.1.0/reference/html/dependency-versions.html)
