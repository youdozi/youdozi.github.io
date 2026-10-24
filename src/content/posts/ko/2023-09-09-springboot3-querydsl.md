---
title: "[springboot] springboot3 querydsl 적용"
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
updatedAt: "2026-10-24T09:00:00+09:00"
reviewedAt: "2026-10-24"
reviewStatus: "revised"
reviewScope: "공식 문서 대조 및 예제 코드 검토"
archiveBodySha256: "745e0ab660d077632d64c79624ffcf6a0c2b2b7d551068b6a8d5b098e27c5e73"
reviewSources:
  - "https://github.com/querydsl/querydsl/releases/tag/QUERYDSL_5_1_0"
  - "https://docs.gradle.org/current/userguide/lazy_configuration.html"
---
### 개요
springboot3로 메이저 업그레이드 되면서 JPA + querydsl 셋팅 환경에 변화가 생겼습니다.  
기존 의존성으로는 작동하지 않고 jakarta classification을 추가해야 작동하는 이슈가 발생합니다.  
springboot3부터 javax -> jakarta 패키징으로 넘어갔기 때문에 queryDSL도 맞춰서 변경해줘야하는데요..  
2023년 9월 당시에는 Querydsl 릴리스 간격이 길었습니다. 이후 5.1.0 릴리스가 공개되었으므로 이 문장을 현재의 릴리스 상태로 해석하면 안 됩니다.  
때문에 queryDSL보다는 jooq, spring data specification 이용하는게 좋다고 보지만..  
queryDSL에 대한 우리나라 인기는 무시할 수 없는 수준이기도 해서  
간단하게 의존성 변경하여 마이그레이션 해보도록 하겠습니다.

### build.gradle 수정

```groovy
dependencies {
    // querydsl jakarta 의존성 추가
    implementation 'com.querydsl:querydsl-jpa:5.0.0:jakarta'
    annotationProcessor 'com.querydsl:querydsl-apt:5.0.0:jakarta'
    annotationProcessor 'jakarta.annotation:jakarta.annotation-api'
    annotationProcessor 'jakarta.persistence:jakarta.persistence-api'
}

// Q클래스 location 위치
def generated = "$buildDir/generated"

// java source set에 Q클래스 적용
sourceSets {
    main.java.srcDirs += [generated]
}

// Q클래스 location 위치 적용
tasks.withType(JavaCompile).configureEach {
    options.getGeneratedSourceOutputDirectory().set(file(generated))
}

// gradle clean task 실행시 Q클래스 삭제
clean {
    delete file(generated)
}
```

위 build.gradle 설정까지 마쳤으면 gradle clean -> build task를 실행해봅시다.

![springboot_querydsl_build.png](/assets/img/springboot/querydsl/springboot_querydsl_build.png)

정상적으로 빌드가 완료되었습니다.
이제 즐거운 개발 시간 되시길 바랍니다~!

### 번외 1

springboot3 queryDSL 마이그레이션 관련 블로그를 서치해보면 아래와 같이 task 코드가 적용된 경우가 많습니다.
```groovy
tasks.withType(JavaCompile) {
    options.getGeneratedSourceOutputDirectory().set(file(generated))
}
```

intellij를 사용하시면 위 코드 작성시 노란색 밑줄이 나올겁니다.

![springboot_querydsl_gradle_warning.png](/assets/img/springboot/querydsl/springboot_querydsl_gradle_warning.png)

intellij의 가이드대로 `Add 'configureEach'`를 추가해서 아래 코드처럼 변경합니다.

```groovy
tasks.withType(JavaCompile).configureEach {
    options.getGeneratedSourceOutputDirectory().set(file(generated))
}
```

### 번외 2

아래 코드는 deprecated 메서드 사용된 유형입니다.

```groovy
tasks.withType(JavaCompile) {
    options.annotationProcessorGeneratedSourcesDirectory = file(generated)
}
```

위 코드 중 `annotationProcessorGeneratedSourcesDirectory`가 deprecated 되었다고 표시되며  
gradle 9버전에서 삭제될 메서드입니다. `getGeneratedSourceOutputDirectory().set(file(generated))`  
으로 변경하면 문제 없으니 수정하도록 합니다.

### 참고
[https://velog.io/@daoh98/Query-DSL-Spring-boot-3.0-%EC%9D%B4%EC%83%81-Query-DSL-%EC%84%A4%EC%A0%95-%EB%B0%A9%EB%B2%95](https://velog.io/@daoh98/Query-DSL-Spring-boot-3.0-%EC%9D%B4%EC%83%81-Query-DSL-%EC%84%A4%EC%A0%95-%EB%B0%A9%EB%B2%95)

## 검증 및 보강 — 2026-10-24

본문의 5.0.0은 당시 예제를 재현하기 위한 버전입니다. 새 프로젝트의 최신 권장 버전이라는 뜻은 아닙니다. `querydsl-jpa`와 `querydsl-apt`는 같은 버전 및 `jakarta` classifier로 맞추고, Q 타입 생성이 되는지 `./gradlew clean compileJava`로 확인하세요. 애노테이션 처리 출력 디렉터리는 main/test가 공유하면 충돌할 수 있으므로 보통 Gradle 기본 생성 경로를 유지합니다. `configureEach`는 작업의 지연 구성을 위한 선택이며 Jakarta 호환성 문제를 고치는 기능은 아닙니다.

### 확인한 자료

- [공식 자료 1](https://github.com/querydsl/querydsl/releases/tag/QUERYDSL_5_1_0)
- [공식 자료 2](https://docs.gradle.org/current/userguide/lazy_configuration.html)
