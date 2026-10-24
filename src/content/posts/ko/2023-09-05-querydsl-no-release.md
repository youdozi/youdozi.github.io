---
title: "[querydsl] querydsl No release for a long time"
language: "ko"
translationKey: "2023-09-05-querydsl-no-release"
routeSlug: "2023-09-05-querydsl-no-release"
kind: "post"
publishedAt: "2023-09-04T15:00:00.000Z"
categories:
  - "springboot"
tags:
  - "querydsl"
  - "springboot3"
  - "jpa"
  - "jooq"
legacyUrl: "/springboot/querydsl-no-release/"
legacySource: "_posts/spring/querydsl/2023-09-05-querydsl-no-release.markdown"
updatedAt: "2026-10-24T09:00:00+09:00"
reviewedAt: "2026-10-24"
reviewStatus: "revised"
reviewScope: "공식 문서 대조 및 예제 코드 검토"
archiveBodySha256: "ed4dd5e11f73c2c88eaf11ddaf2269bceec442dff783e36b7266eb1d5d58764b"
reviewSources:
  - "https://github.com/querydsl/querydsl/releases/tag/QUERYDSL_5_1_0"
  - "https://docs.spring.io/spring-data/jpa/reference/jpa/specifications.html"
  - "https://www.jooq.org/doc/latest/manual/"
  - "https://jdbi.org/"
  - "https://doma.readthedocs.io/"
---
### 개요
JPA를 spring data jpa + querydsl과의 조합으로 접하는 경우가 많습니다.  
spring data jpa에서 제공해주는 specification으로도 충분히 해낼수 있지만  
querydsl에 비할바는 아닙니다.  
entity에 wrapper Q클래스를 생성하여 type-safe하게 사용할 수 있는 장점은 누구나 인정하는 바입니다.  
다만 springboot 3로 메이저 업데이트되면서 querydsl을 계속 유지해야 하는가  
하는 의구심이 들기 시작했습니다.  
2023년 9월 작성 시점에는 2021년 7월 이후 릴리스 공백이 길었고 springboot 3의 javax에서 jakarta 전환, hibernate 6 미지원의 이슈가 발생하고 있습니다.  
공식 github에서도 많은 유저들이 querydsl의 지속성에 대해 의구심을 가지고 있는것 가운데..  
querydsl을 대체할 수 있는 라이브러리는 무엇이 있을까요?  
몇가지 정리해보도록 하겠습니다.

### JOOQ
[https://www.jooq.org/](https://www.jooq.org/)  

### JDBI
[https://jdbi.org/](https://jdbi.org/)

### DOMA
[https://doma.readthedocs.io/](https://doma.readthedocs.io/)

## 검증 및 보강 — 2026-10-24

이 글은 작성 당시의 우려를 기록한 것으로, 현재 릴리스 상태를 단정하는 글이 아닙니다. 공식 저장소에는 이후 5.1.0 릴리스가 있습니다. 대체 도구도 서로 같은 역할은 아닙니다. Spring Data JPA Specification은 JPA Criteria 기반 조건 조합, jOOQ는 SQL 중심의 타입 안전한 DSL, Jdbi는 JDBC 접근과 매핑, Doma는 SQL·애노테이션 처리 중심의 접근입니다. 교체 여부는 기존 JPA 엔티티·동적 쿼리·DB 전용 SQL 활용 범위·라이선스와 마이그레이션 비용을 비교해서 판단해야 합니다.

### 확인한 자료

- [공식 자료 1](https://github.com/querydsl/querydsl/releases/tag/QUERYDSL_5_1_0)
- [공식 자료 2](https://docs.spring.io/spring-data/jpa/reference/jpa/specifications.html)
- [공식 자료 3](https://www.jooq.org/doc/latest/manual/)
- [공식 자료 4](https://jdbi.org/)
- [공식 자료 5](https://doma.readthedocs.io/)
