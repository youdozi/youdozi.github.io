---
title: "[springboot] springboot3 migration"
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
updatedAt: "2026-10-24T09:00:00+09:00"
reviewedAt: "2026-10-24"
reviewStatus: "revised"
reviewScope: "공식 문서 대조 및 예제 코드 검토"
archiveBodySha256: "1d7de750bbc8801a9fd3e50b28b53820a6e8beede1dde34cc4ee282f000414b5"
reviewSources:
  - "https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.0-Migration-Guide"
  - "https://spring.io/blog/2023/09/09/all-together-now-spring-boot-3-2-graalvm-native-images-java-21-and-virtual"
---
### 개요
2022년 하반기에 springboot3가 공식 release 되었습니다.  
springboot2가 2018년 상반기에 release되고 나서 새롭게 판올림 버전으로  
가장 큰 변화로는 아래와 같습니다.  
* spring framework 6 적용
* 최소 사양 JDK 17
* Java EE API의 javax -> jakarta 패키지 변경
* GraalVM 네이티브 이미지 지원

### 굳이 springboot3로 업그레이드 해야할까?
새로운 프로젝트는 springboot3로 시작해도 문제가 없겠지만  
기존 springboot2.x 프로젝트를 마이그레이션해야할 필요성은 분명 있습니다.  
2021년 11월에 발생한 log4shell 취약점과 같은 이슈를 피하기 위해서는  
레거시화된 프로젝트에 대한 버전업 관리도 필요하다고 생각됩니다.  
그리고 개인적으로는 JDK 21의 가상스레드를 spring framework 6.1부터 지원하기 때문에 미리 판올림을 하는 것도 나쁘지 않다 생각됩니다.

### 마이그레이션에 어려움은 없을까?
마이그레이션 작업시 제일 염려되는 것은 무엇일까요?  
당연히 기존에 잘 동작하던 비지니스가 마이그레이션 이후 제대로 작동 되지 않는 부분 아니겠습니까?  
또한 레퍼런스가 많이 없다는 것도 충분히 생각해볼 수 있죠.  
하지만 spring에서는 친절하게 springboot3 migration 문서를 제공해줬죠.

[springboot3 migration 문서](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.0-Migration-Guide)

그런데.. 이것으로 끝은 아닙니다.  
migration문서에는 나와 있지 않는 서드파티 라이브러리 문제가 있죠.  
이 부분을 공유할까 합니다.

### QueryDSL
이 글을 작성하던 2023년 9월에는 Querydsl의 릴리스 간격이 길었고  
Jakarta API와 Hibernate 버전의 호환성을 별도로 확인해야 했습니다.  
querydsl github 이슈 등록 건수도 어마어마하고 관리는 계속 할 수 있나 싶었습니다.  
해당 적용 부분은 아래 링크를 통해 확인할 수 있습니다.  
[springboot3 querydsl 적용](https://youdozi.github.io/springboot/springboot3-querydsl/)

## 검증 및 보강 — 2026-10-24

Spring Boot 3.0은 Java 17과 Spring Framework 6.0을 기준으로 합니다. 이전 프로젝트는 우선 2.7로 정리한 뒤 3.0 마이그레이션 가이드에 따라 변경점을 분리하는 방식이 권장됩니다. 모든 `javax.*`를 바꾸는 것은 잘못입니다. `javax.persistence`, `javax.servlet` 같은 Java EE API가 대상이고 `javax.sql`, `javax.crypto` 같은 Java SE API는 그대로 사용합니다. 가상 스레드 설정은 JDK 21과 Boot 3.2/Framework 6.1 조합에서 확인할 수 있습니다. 보안 업데이트와 라이브러리 지원 기간은 별도로 확인해야 하며 메이저 버전 변경만으로 취약점이 자동 해결되는 것은 아닙니다.

### 확인한 자료

- [공식 자료 1](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.0-Migration-Guide)
- [공식 자료 2](https://spring.io/blog/2023/09/09/all-together-now-spring-boot-3-2-graalvm-native-images-java-21-and-virtual)
