---
layout: posts 
title:  "[springboot] springboot3 querydsl 적용"
date:   2023-09-08 00:00:00 +0900 
categories: 
  - springboot
tags:
  - springboot
  - springboot3
  - querydsl
---
### 개요
springboot3로 메이저 업그레이드 되면서 JPA + querydsl 셋팅 환경에 변화가 생겼습니다.  
기존 의존성으로는 작동하지 않고 jakarta classification을 추가해야 작동하는 이슈가 발생합니다.  
springboot3부터 javax -> jakarta 패키징으로 넘어갔기 때문에 queryDSL도 맞춰서 변경해줘야하는데요..  
안타깝게도 queryDSL은 2021년 공식 release 이후로 업데이트가 없는 상황입니다.  
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

intellij의 가이드대로 `Add 'configureEash'`를 추가해서 아래 코드처럼 변경합니다.

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
