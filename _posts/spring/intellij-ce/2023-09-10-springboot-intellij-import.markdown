---
layout: posts 
title:  "[springboot] springboot intellij-ce import"
date:   2023-09-10 00:00:00 +0900 
categories: 
  - springboot
tags:
  - springboot
  - intellij ce
  - project import
---
### 개요
지난번 spring-initializer를 통해 프로젝트를 생성하여 파일로 다운로드 받았습니다.

[참고 - springboot-initializer](http://localhost:4000/springboot/springboot-initializer/)

이제 intellij-ce에서 spring-initializer를 통해 생성된 프로젝트를 import하고 가동해보도록 하겠습니다.

### project import
먼저 다운로드 받은 프로젝트를 import합니다.

![project_import.png](/assets%2Fimg%2Fspringboot%2Fintellij-ce%2Fproject_import.png)

import를 하게 되면 아래와 같이 프로젝트 타입을 선택합니다.  
이전엔 gradle로 프로젝트를 생성하였으므로 gradle을 선택하고 우측 하단의 `Create` 버튼을 클릭합니다.

![project_import_type.png](/assets%2Fimg%2Fspringboot%2Fintellij-ce%2Fproject_import_type.png)

정상적으로 springboot 프로젝트가 import 되었습니다.

![project_import_complete.png](/assets%2Fimg%2Fspringboot%2Fintellij-ce%2Fproject_import_complete.png)

### run

정상적으로 프로젝트를 import하였으나 제일 중요한 무언가가 없습니다.  
그렇죠. springboot를 가동해야 하는데 ultimate에서 항상 봐왔던 RUN 기능이 없습니다.  
intellij에서 springboot를 가동할 수 있는 방법은 3가지가 있습니다.  
* RUN/DEBUG configurations 설정
* Service 등록
* gradle bootRun task 실행

intellij-ce에서는 사용자가 직접 RUN/DEBUG configurations를 설정해줘야 합니다.

