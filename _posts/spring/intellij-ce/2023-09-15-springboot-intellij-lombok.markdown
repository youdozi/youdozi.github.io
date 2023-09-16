---
layout: posts
title: "[springboot] springboot intellij-community lombok"
date: 2023-09-16 00:00:00 +0900
categories:
  - springboot
tags:
  - springboot
  - intellij community
  - lombok
---

### 개요

intellij-community 버전으로 springboot 프로젝트를 import하여 가동하는것 까지 성공했습니다.

[참고 - intellij-ce-springboot-import](springboot/springboot-intellij-import/)

이제 기쁜 마음으로 코드를 하나 하나 짜보고 있는데..  
이 무슨.. lombok이 정상 작동하고 있지 않습니다.  
최근 사용한 ultimate 버전에서는 자동으로 lombok plugin이 설치되어 있었는데..  
역시 community 입니다. 제가 해줘야 하네요.  
이번 시간엔 intellij-community 버전으로 lombok을 사용해보도록 하겠습니다.

### lombok plugin 설치

먼저 plugin 설치를 위해 setting 화면으로 이동해 보도록 하겠습니다.

![intellij_setting.png](/assets%2Fimg%2Fspringboot%2Fintellij-ce%2Flombok%2Fintellij_setting.png){:width="40%" height="40%"}

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
    implementation 'org.projectlombok:lombok'
    annotationProcessor 'org.projectlombok:lombok'    

    testImplementation 'org.projectlombok:lombok'
    testAnnotationProcessor 'org.projectlombok:lombok'    
}
```
testImplementation, testAnnotationProcessor는 테스트 환경에서 `lombok`을 사용할 수 있도록 해줍니다.  
필요 없다면 implementation, annotationProcessor만 종속성 주입 해주면 됩니다.

하지만 여기가 끝이 아닙니다. `lombok` 어노테이션이 정상 작동하도록 추가적인 설정이 필요합니다.
아래 부분까지 진행 해 주세요!

### lombok annotation 셋팅

다시 한번 더 setting 화면으로 이동해 봅니다.  
build, execution, deployment -> compiler -> annotation processors로 이동합니다.

![lombok_setting_annotation.png](/assets%2Fimg%2Fspringboot%2Fintellij-ce%2Flombok%2Flombok_setting_annotation.png)

위 화면처럼 `Enable annotation processing`을 체크하면 됩니다.

그럼 이제 정상적으로 `lombok`이 작동 될겁니다!

