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
  - RUN/DEBUG configurations
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

intellij에서 springboot를 가동할 수 있는 방법은 3가지가 있습니다.
* RUN/DEBUG configurations
* Service
* gradle bootRun task  

여기서는 `RUN/DEBUG configurations`로 springboot를 가동하는 방법에 대해 나누고자 합니다.  
우선 우측 상단을 보시면 ultimate 버전에서 항상 봐왔던 RUN 기능이 비활성화 된 것을 확인할 수 있습니다.    
intellij-ce에서는 사용자가 직접 RUN/DEBUG configurations를 설정해줘야 합니다.  
그럼 `RUN/DEBUG configurations`를 적용해 보도록 하겠습니다.  

### RUN/DEBUG configurations
화면 우측 상단을 보시면 아래와 같이 `Current File`과 가동/디버깅, 더보기 아이콘이 보입니다.

![project_not_run_config.png](/assets%2Fimg%2Fspringboot%2Fintellij-ce%2Fproject_not_run_config.png)

`Current File`을 선택하면 아래와 같이 메뉴가 펼쳐집니다.

![project_start_run_config.png](/assets%2Fimg%2Fspringboot%2Fintellij-ce%2Fproject_start_run_config.png)  

`Edit Configurations` 버튼을 클릭합니다.  
RUN/DEBUG configurations 설정 팝업 화면이 나오네요.

![empty_run_config.png](/assets%2Fimg%2Fspringboot%2Fintellij-ce%2Fempty_run_config.png)  

좌측 상단 `+`, 좌측 중앙 `Add new`, 우측 `Add new run configuration...` 버튼을 클릭하면 동일하게 아래 화면이 펼쳐집니다.  

![select_run_config_templete.png](/assets%2Fimg%2Fspringboot%2Fintellij-ce%2Fselect_run_config_templete.png)

여기서 `Application`을 선택합니다.

![add_run_config.png](/assets%2Fimg%2Fspringboot%2Fintellij-ce%2Fadd_run_config.png)

springboot를 실행하기 위해 몇가지 정보를 더 입력해야 합니다.  
먼저 `Name`란에 `DemoApplication`이라고 입력합니다.

![add_name.png](/assets%2Fimg%2Fspringboot%2Fintellij-ce%2Fadd_name.png)

`Build and run` 하단에 선택된 모듈이 없어 `module not specified`라고 노출된 셀렉트 박스가 보일겁니다.  
해당 셀렉트 박스를 선택하면 아래와 같이 선택할 수 있는 JDK 버전이 펼쳐집니다.

![add_build_and_run_module.png](/assets%2Fimg%2Fspringboot%2Fintellij-ce%2Fadd_build_and_run_module.png)

여기서는 `corretto-17` 즉 JDK 17버전을 선택합니다.
spring-initializer로 생성한 프로젝트는 JDK 17 이상이기만 하면 되니 그 이상도 상관 없습니다.
그리고 오른쪽 `-cp <no module>` 셀렉트 박스를 클릭, `demo.main`을 선택합니다. 

![add_no_module.png](/assets%2Fimg%2Fspringboot%2Fintellij-ce%2Fadd_no_module.png)

이제 얼마 안 남았습니다!!  
바로 밑에 Main class을 입력하는 텍스트 박스가 있고 우측 햄버거 아이콘이 보일겁니다.  
햄버거 아이콘을 클릭 합니다.

![add_main_class.png](/assets%2Fimg%2Fspringboot%2Fintellij-ce%2Fadd_main_class.png)

아래와 같은 팝업이 노출될겁니다.  
팝업이 노출되면서 자동으로 springboot main class를 읽어 화면에 보여줄 것 입니다.  
해당 클래스를 선택합니다.

![choice_main_class.png](/assets%2Fimg%2Fspringboot%2Fintellij-ce%2Fchoice_main_class.png)

이제 다 끝났습니다.  
우측 하단 `OK` 버튼을 클릭해 주세요.

![complete_run_config.png](/assets%2Fimg%2Fspringboot%2Fintellij-ce%2Fcomplete_run_config.png)

그럼 `RUN/DEBUG configurations` 팝업이 닫혀지면서 우측 상단에 시작/디버깅 부분이 활성화 된 것을 확인할 수 있습니다.

![final_run_config.png](/assets%2Fimg%2Fspringboot%2Fintellij-ce%2Ffinal_run_config.png)

### springboot run

이제 시작 버튼을 클릭해보죠!

![run_console.png](/assets%2Fimg%2Fspringboot%2Fintellij-ce%2Frun_console.png)

정상적으로 springboot가 가동된 것을 확인 할 수 있습니다.

