---
title: "[jenkins] jenkins docker install"
language: "ko"
translationKey: "2023-09-28-jenkins-docker-install"
routeSlug: "2023-09-28-jenkins-docker-install"
kind: "post"
publishedAt: "2023-09-27T15:00:00.000Z"
categories:
  - "jenkins"
tags:
  - "jenkins"
  - "docker install"
legacyUrl: "/jenkins/jenkins-docker-install/"
legacySource: "_posts/jenkins/docker-install/2023-09-28-jenkins-docker-install.markdown"
updatedAt: "2026-10-24T09:00:00+09:00"
reviewedAt: "2026-10-24"
reviewStatus: "revised"
reviewScope: "공식 문서 대조 및 예제 코드 검토"
archiveBodySha256: "15cb216cb3c50496f3c50b550fc831b31c44ebcb0830d8be8ef009d8ac7d5bbd"
reviewSources:
  - "https://www.jenkins.io/doc/book/installing/docker/"
  - "https://github.com/jenkinsci/docker/blob/master/README.md"
---
ci/cd 오픈소스 도구로 가장 많이 사랑 받는 jenkins에 대해 포스팅 해보겠습니다.  
먼저 설치부터 해야겠지요?  
항상 패키지 매니저로 설치했었는데 이번에는 docker로 설치해보도록 하겠습니다.

### jenkins docker 이미지 다운로드
docker hub에서 jenkins를 검색하면 가장 상단에 `jenkins docker official image`가 가장 먼저 보일겁니다.

![jenkins_00.png](/assets%2Fimg%2Fjenkins%2Fdocker-install%2Fjenkins_00.png)

하지만 `DEPRECATED; use "jenkins/jenkins:lts" instead`라고 안내하고 있으니 아래에 있는 `jenkins/jenkins Sponsored OSS`의 이미지를 다운로드 받도록 합니다.
```shell
docker pull jenkins/jenkins:lts-jdk21
```
정상적으로 이미지를 다운로드 받았습니다.
```shell
latest: Pulling from jenkins/jenkins
796cc43785ac: Pull complete
0f7bbb193a37: Pull complete
eb083ec37208: Pull complete
811cee232129: Pull complete
9cb3c9c2fc84: Pull complete
391cfa07b590: Pull complete
2bd9a9e0235f: Pull complete
0c4eaef6fe70: Pull complete
b96098b82b9a: Pull complete
ea3fc5fce43a: Pull complete
ffabf053eb7a: Pull complete
77934a986327: Pull complete
9399b337c044: Pull complete
Digest: sha256:14e3f4912ade77739d675aced9673eeab7ceaa4186dee8365ba61b72828f3b29
Status: Downloaded newer image for jenkins/jenkins:latest
docker.io/jenkins/jenkins:latest
```

### jenkins docker 실행
이제 docker 컨테이너를 가동하도록 하겠습니다.
```shell
docker run -d --restart=on-failure \
  -p 127.0.0.1:8080:8080 \
  -v jenkins_home:/var/jenkins_home \
  --name jenkins jenkins/jenkins:lts-jdk21
```
플러그인과 설정을 유지하기 위해 볼륨 설정을 넣었습니다.
```shell
fadd1ce5b81bf64038f5583e9ff86bdc71b2fa53eb58a488b62201214930813c
```
docker 컨테이너 id를 리턴해주면서 정상적으로 생성됐네요.  
이제 jenkins 설정 화면을 만나보겠습니다!
아 그전에 초기 비번을 확인해야 하는데 아래 명령어를 통해 알아보도록 하겠습니다.

### jenkins 초기 비번 확인
```shell
docker logs fadd1ce5b81bf64038f5583e9ff86bdc71b2fa53eb58a488b62201214930813c
```
위 명령어를 통해 docker 로그를 볼 수 있습니다.  
로그 중에 아래 단락에서 초기 비번을 확인할 수 있습니다.
```shell
Jenkins initial setup is required. An admin user has been created and a password generated.
Please use the following password to proceed to installation:

992e7983ba1748b1852018edff0638bf

This may also be found at: /var/jenkins_home/secrets/initialAdminPassword
```
위 값은 과거 실행 로그의 예시입니다. 실제 초기 비밀번호는 각 설치에서 생성되며 그대로 재사용하지 않습니다.  
초기 비번을 확인됐으니 웹브라우저로 http://localhost:8080에 접속 해보겠습니다.

### Unlock Jenkins
![jenkins_01.png](/assets%2Fimg%2Fjenkins%2Fdocker-install%2Fjenkins_01.png)  

`Unlock Jenkins` 화면이 나온다면 설치는 완료된 것 입니다.  
여기에 초기 비번을 입력하고 continue 버튼을 클릭합니다.  

### Customize Jenkins
![jenkins_02.png](/assets%2Fimg%2Fjenkins%2Fdocker-install%2Fjenkins_02.png)

`Customize Jenkins` 화면이 나올텐데 여기서는 우측   
`Install suggested plugins`를 선택합니다.

![jenkins_03.png](/assets%2Fimg%2Fjenkins%2Fdocker-install%2Fjenkins_03.png)

필요한 플러그인을 다운로드 받고 설치하기 시작합니다.  
조금 시간이 걸릴 수 있으니 차분하게 기다려주세요~!  

### Create First Admin User
![jenkins_04.png](/assets%2Fimg%2Fjenkins%2Fdocker-install%2Fjenkins_04.png)

플러그인 설치까지 완료 되었습니다.  
`Create First Admin User` 화면이 나올 텐데 초기 설정이 끝난 이후에도 admin 계정을 만들 수 있습니다.  
개인 관리자 계정을 생성하고 고유한 비밀번호로 초기 설정을 마칩니다. 초기 admin 계정으로 계속 운영하는 절차는 권장하지 않습니다.
> <i class="fa fa-exclamation-triangle" aria-hidden="true"></i> 실 사용시 반드시 admin 계정을 생성하시길 바랍니다.

### Instance Configuration
![jenkins_05.png](/assets%2Fimg%2Fjenkins%2Fdocker-install%2Fjenkins_05.png)

`Instance Configuration` 화면이 나옵니다.  
기본 default로 적용된 주소 그대로 사용하며 `Save and Finish` 버튼을 클릭합니다.

### Jenkins is Ready
![jenkins_06.png](/assets%2Fimg%2Fjenkins%2Fdocker-install%2Fjenkins_06.png)

마지막 입니다.  
`Create First Admin User` 단계에서 admin 계정을 설정하지 않아 warning 메시지를 노출하네요.  
admin 계정을 만들고 왔다면 warning 메시지는 보이지 않을 겁니다.  
이제 `Start using jenkins` 버튼을 클릭합니다.

### Jenkins home
![jenkins_07.png](/assets%2Fimg%2Fjenkins%2Fdocker-install%2Fjenkins_07.png)

드디어 젠킨스 홈 화면으로 진입했습니다~!!  
여기까지 해서 젠킨스 설치를 마무리 짓도록 하겠습니다.  
다음에는 젠킨스 job을 만들어보도록 하겠습니다.  
수고하셨습니다.

## 검증 및 보강 — 2026-10-24

실행 명령은 LTS 이미지와 로컬 접근용 포트 바인딩으로 보완했습니다. `latest`는 재현 가능한 고정 버전이 아니며 운영에서는 검증한 구체 버전 태그 또는 digest를 기록하세요. 본문의 Pull 로그는 2023년 `latest` 실행 기록이므로 현재 이미지의 출력과 일치할 필요가 없습니다. 초기 암호는 `docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword`로 확인할 수 있습니다. 컨테이너 삭제 전 볼륨 백업·복구를 검증하고, 원격 공개 시에는 HTTPS와 접근 제어를 별도로 구성해야 합니다. Docker 소켓 마운트는 이 설치에 필요하지 않습니다.

### 확인한 자료

- [공식 자료 1](https://www.jenkins.io/doc/book/installing/docker/)
- [공식 자료 2](https://github.com/jenkinsci/docker/blob/master/README.md)
