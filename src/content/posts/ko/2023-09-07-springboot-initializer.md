---
title: "[springboot] springboot initializer"
language: "ko"
translationKey: "2023-09-07-springboot-initializer"
routeSlug: "2023-09-07-springboot-initializer"
kind: "post"
publishedAt: "2023-09-06T15:00:00.000Z"
categories:
  - "springboot"
tags:
  - "springboot"
  - "springboot initializer"
legacyUrl: "/springboot/springboot-initializer/"
legacySource: "_posts/spring/initializer/2023-09-07-springboot-initializer.markdown"
updatedAt: "2026-10-24T09:00:00+09:00"
reviewedAt: "2026-10-24"
reviewStatus: "revised"
reviewScope: "공식 문서 대조 및 예제 코드 검토"
archiveBodySha256: "0993c35936346a8878deb7cd9af793ce441c78a471c1561b0d5afbd196424f79"
reviewSources:
  - "https://start.spring.io/"
  - "https://docs.spring.io/initializr/docs/current/reference/html/"
---
### 개요
항상 intellij ultimate 버전만 사용하고 있었는데  
무슨 바람이 난건지.. intellij ce 버전에 도전하였습니다.  
springboot 프로젝트 생성이며.. 그 밖에 기본적으로 될꺼라 싶은것 중에  
안되는 녀석들도 꽤 있더군요.  
이번 시간엔 간단하게 spingboot 프로젝트를 생성해보도록 할게요.

### springboot initalizr
[https://start.spring.io/](https://start.spring.io/)  

위 사이트에 접속하면 아래와 같은 화면이 나옵니다.

![springboot initalizr.png](/assets/img/springboot/initializer/springboot%20initalizr.png)


spring에서 제공해주는 initalizr 사이트입니다.  
여기에서 필요한 springboot 버전..meta 정보, 의존성 라이브러리를 체크하고  
하단 GENERATE 버튼을 클릭하면 springboot 프로젝트 생성되어 다운로드 받을 수 있도록 해줍니다.  
프로젝트를 하나 만들어볼테니 화면 왼쪽을 봐주세요.

### project setting
![springboot_meta.png](/assets/img/springboot/initializer/springboot_meta.png)

project -> gradle - groovy  
language -> java  
springboot -> 3.1.3  
project meta 정보는 그대로 사용합니다.

### dependency
이제 화면 우측을 봅니다.  

![springboot_dependency.png](/assets/img/springboot/initializer/springboot_dependency.png)  

의존성을 추가할 수 있는 `ADD DEPENDENCIES...` 버튼이 보이네요.  
버튼을 클릭하여 새로운 의존성을 추가해봅시다.

![springboot_dependency_popup.png](/assets/img/springboot/initializer/springboot_dependency_popup.png)

레이어 팝업이 뜨면서 의존성 라이브러리를 선택할 수 있습니다.  
검색어를 입력하여 의존성을 추가해보도록 하겠습니다. 

![springboot_dependency_popup_auto.png](/assets/img/springboot/initializer/springboot_dependency_popup_auto.png)

`web` 이라고 검색어를 입력하니 자동완성으로 `Spring Web`등 관련 라이브러리가 노출됩니다.  
저는 여기서 `Spring Web`을 선택하고 레이어 팝업을 닫도록 하겠습니다.

![springboot_dependency_add.png](/assets/img/springboot/initializer/springboot_dependency_add.png)

짜잔!  
우측을 보니 제가 선택한 `Spring Web` 라이브러리가 정상적으로 추가된것을 볼 수 있습니다.  
이제 프로젝트를 다운로드 받아 볼까요? 

### download
화면 하단에 GENERATE 버튼을 클릭해봅시다~!

![springboot_generate.png](/assets/img/springboot/initializer/springboot_generate.png)

아래와 같이 다운로드 창이 나오네요.  

![springboot_download.png](/assets/img/springboot/initializer/springboot_download.png)

맥 파인더를 통해 정상적으로 springboot 어플리케이션이 다운로드 된것을 확인할 수 있습니다.  

![springboot_in_finder.png](/assets/img/springboot/initializer/springboot_in_finder.png)

다음 순서는 intellij-ce버전으로 위 springboot 프로젝트를 import하여 가동해보도록 하겠습니다.

## 검증 및 보강 — 2026-10-24

화면은 2023년 Spring Boot 3.1 시점의 기록입니다. 현재 Initializr의 기본 버전이나 선택 항목과 다를 수 있으므로 Project, Language, Java 버전과 Dependencies를 직접 확인하세요. 압축 해제 후 `./gradlew test`와 `./gradlew bootRun`으로 기본 동작을 확인하면 IDE 문제와 프로젝트 문제를 구분하기 쉽습니다. 생성 시각의 `build.gradle`, Wrapper 버전, Java toolchain 설정도 함께 보관해야 재현할 수 있습니다.

### 확인한 자료

- [공식 자료 1](https://start.spring.io/)
- [공식 자료 2](https://docs.spring.io/initializr/docs/current/reference/html/)
