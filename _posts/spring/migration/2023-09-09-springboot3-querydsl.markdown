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
개인적으로 queryDSL보다는 jooq, spring data specification을 이용하는게 좋다고 보지만..
queryDSL에 대한 우리나라 인기는 무시할 수 없는 수준입니다.  
자 그럼..queryDSL에 jakarta 패키징을 입히도록 해볼게요.

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

![springboot_querydsl_build.png](/assets/img/springboot/springboot_querydsl_build.png)

정상적으로 빌드가 완료되었습니다.
이제 즐거운 개발 시간 되시길 바랍니다~!

### 참고
[https://velog.io/@daoh98/Query-DSL-Spring-boot-3.0-%EC%9D%B4%EC%83%81-Query-DSL-%EC%84%A4%EC%A0%95-%EB%B0%A9%EB%B2%95](https://velog.io/@daoh98/Query-DSL-Spring-boot-3.0-%EC%9D%B4%EC%83%81-Query-DSL-%EC%84%A4%EC%A0%95-%EB%B0%A9%EB%B2%95)
