---
title: "[springboot] springboot intellij-community lombok"
language: "ko"
translationKey: "2023-09-15-springboot-intellij-lombok"
routeSlug: "2023-09-15-springboot-intellij-lombok"
kind: "post"
publishedAt: "2023-09-15T15:00:00.000Z"
categories:
  - "springboot"
tags:
  - "springboot"
  - "intellij community"
  - "lombok"
legacyUrl: "/springboot/springboot-intellij-lombok/"
legacySource: "_posts/spring/intellij-ce/2023-09-15-springboot-intellij-lombok.markdown"
updatedAt: "2026-10-24T09:00:00+09:00"
reviewedAt: "2026-10-24"
reviewStatus: "revised"
reviewScope: "공식 문서 대조 및 예제 코드 검토"
archiveBodySha256: "8a4674360edd715adc120d7ac95fbd3c194aa0b71e6d8ea194349e304c922930"
reviewSources:
  - "https://projectlombok.org/setup/gradle"
  - "https://www.jetbrains.com/help/idea/annotation-processors-support.html"
---
### 개요

intellij-community 버전으로 springboot 프로젝트를 import하여 가동하는것 까지 성공했습니다.

[참고 - intellij-ce-springboot-import](/ko/posts/2023-09-10-springboot-intellij-import/)

이제 기쁜 마음으로 코드를 하나 하나 짜보고 있는데..  
이 무슨.. lombok이 정상 작동하고 있지 않습니다.  
최근 사용한 ultimate 버전에서는 자동으로 lombok plugin이 설치되어 있었는데..  
역시 community 입니다. 제가 해줘야 하네요.  
이번 시간엔 intellij-community 버전으로 lombok을 사용해보도록 하겠습니다.

### lombok plugin 설치

먼저 plugin 설치를 위해 setting 화면으로 이동해 보도록 하겠습니다.

![intellij_setting.png](/assets%2Fimg%2Fspringboot%2Fintellij-ce%2Flombok%2Fintellij_setting.png)

setting -> plugins로 이동합니다.

![intellij_setting_plugin.png](/assets%2Fimg%2Fspringboot%2Fintellij-ce%2Flombok%2Fintellij_setting_plugin.png)

intellij plugin 관리 화면이 나옵니다.  
여기서 marketplace 탭 -> 텍스트박스에 `lombok`을 입력합니다.

![intellij_setting_plugin_select.png](/assets%2Fimg%2Fspringboot%2Fintellij-ce%2Flombok%2Fintellij_setting_plugin_select.png)

`lombok` plugin이 보입니다. `lombok`을 선택하고 `install` 버튼을 클릭합니다.  
정상적으로 설치 되었다면 installed 탭에서 확인 가능합니다.

![lombok_plugin_install_after.png](/assets%2Fimg%2Fspringboot%2Fintellij-ce%2Flombok%2Flombok_plugin_install_after.png)

설치가 마무리 되었습니다.  
이제 gradle 종속성 주입을 진행 해보겠습니다.  

### lombok 종속성 주입

build.gradle에 아래와 같이 `lombok` 종속성을 주입니다.

```groovy
dependencies {
    compileOnly 'org.projectlombok:lombok'
    annotationProcessor 'org.projectlombok:lombok'    

    testCompileOnly 'org.projectlombok:lombok'
    testAnnotationProcessor 'org.projectlombok:lombok'    
}
```
testCompileOnly, testAnnotationProcessor는 테스트 환경에서 `lombok`을 사용할 수 있도록 해줍니다.  
필요 없다면 compileOnly, annotationProcessor만 종속성 주입 해주면 됩니다.

하지만 여기가 끝이 아닙니다. `lombok` 어노테이션이 정상 작동하도록 추가적인 설정이 필요합니다.
아래 부분까지 진행 해 주세요!

### lombok annotation 셋팅

다시 한번 더 setting 화면으로 이동해 봅니다.  
build, execution, deployment -> compiler -> annotation processors로 이동합니다.

![lombok_setting_annotation.png](/assets%2Fimg%2Fspringboot%2Fintellij-ce%2Flombok%2Flombok_setting_annotation.png)

위 화면처럼 `Enable annotation processing`을 체크하면 됩니다.

그럼 이제 정상적으로 `lombok`이 작동 될겁니다!

## 검증 및 보강 — 2026-10-24

Lombok은 보통 런타임 의존성이 아닌 컴파일 시점의 도구이므로 공식 Gradle 구성에 맞춰 `compileOnly`와 `annotationProcessor`로 수정했습니다. 버전을 생략한 예제는 Spring Boot 의존성 관리가 적용되어 있다는 전제입니다. 일반 Gradle 프로젝트는 두 선언에 동일한 Lombok 버전을 명시해야 합니다. IDE가 인식하는 문제와 Gradle 빌드 문제를 분리하려면 먼저 `./gradlew clean compileJava`를 실행하세요. IDE 화면과 플러그인 기본 제공 여부는 버전에 따라 달라집니다.

### 확인한 자료

- [공식 자료 1](https://projectlombok.org/setup/gradle)
- [공식 자료 2](https://www.jetbrains.com/help/idea/annotation-processors-support.html)
