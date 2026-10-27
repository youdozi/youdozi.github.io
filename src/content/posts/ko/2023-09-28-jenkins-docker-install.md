---
title: "Docker Jenkins: 부팅과 컨테이너 재생성 검증하기"
language: ko
translationKey: 2023-09-28-jenkins-docker-install
routeSlug: 2023-09-28-jenkins-docker-install
kind: post
publishedAt: 2023-09-27T15:00:00.000Z
categories:
  - jenkins
tags:
  - jenkins
  - docker
  - containers
  - backup
  - testing
legacyUrl: /jenkins/jenkins-docker-install/
legacySource: _posts/jenkins/docker-install/2023-09-28-jenkins-docker-install.markdown
updatedAt: 2026-10-27T07:50:31.083Z
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Primary documentation and disposable-container contracts reviewed; exact image/version and hosted execution evidence recorded separately.
archiveBodySha256: 15cb216cb3c50496f3c50b550fc831b31c44ebcb0830d8be8ef009d8ac7d5bbd
reviewSources:
  - https://www.jenkins.io/doc/book/installing/docker/
  - https://github.com/jenkinsci/docker/blob/master/README.md
  - https://www.jenkins.io/doc/book/system-administration/backing-up/
  - https://docs.docker.com/engine/storage/volumes/
  - https://docs.docker.com/engine/network/port-publishing/
description: 이미지 digest로 일회용 Jenkins를 실행하고 로컬 HTTP 준비 상태와 같은 볼륨의 컨테이너 재생성을 확인합니다. 초기 비밀번호는 출력하지 않습니다.
---
Jenkins를 이름 있는 홈 볼륨으로 시작하고 HTTP 응답을 확인한 뒤, 같은 볼륨으로 컨테이너를 다시 생성합니다. 설정 화면에 접근할 수 있다는 사실은 컨트롤러가 시작됐음을 보여줍니다. 홈 데이터가 컨테이너 교체 뒤에도 남는지는 두 번째 실행으로 확인합니다.

변경되는 이미지 태그는 나중에 다른 이미지를 가리킬 수 있습니다. 실험을 시작할 때 이미지를 고정하고 생성된 초기 비밀번호는 비공개로 다룹니다. 일회용 예제는 비교 결과만 출력하며 비밀번호 자체는 출력하지 않습니다.

## 한 번의 실험에서 이미지를 고정하기

![로컬 Jenkins 컨트롤러를 시작하고 재생성 뒤 데이터를 확인하는 흐름](/assets/diagrams/2023-09-28-jenkins-docker-install-ko.svg)

Python3와 Linux 컨테이너를 실행하는 Docker 엔진이 필요합니다. [Jenkins 이미지 안내](https://github.com/jenkinsci/docker/blob/master/README.md)는 `jenkins/jenkins`와 홈 디렉터리를 설명합니다. 이 실습은 `jenkins/jenkins:lts-jdk21`을 내려받고 저장소 digest를 확인합니다. 이후 해당 실행의 컨트롤러는 변경되는 태그를 다시 조회하지 않고 digest를 사용합니다. 재현할 때는 digest와 응답의 Jenkins 버전을 기록하세요. 태그만으로 영구적인 릴리스를 지정할 수는 없습니다.

매핑한 포트에 누가 접근할 수 있는지는 Docker의 [포트 공개 방식](https://docs.docker.com/engine/network/port-publishing/)을 따릅니다. 스크립트는 `127.0.0.1::8080`을 요청해 Docker가 루프백의 호스트 포트를 선택하게 하고 실제 바인딩을 확인합니다. 에이전트 포트를 공개하거나 Docker 소켓을 마운트하지 않습니다. 로컬 컨트롤러 실습이며 Docker 빌드 에이전트나 원격 HTTPS 서비스 설치가 아닙니다.

## 전체 실습 실행하기

다음 전체 파일을 `jenkins_lab.py`로 저장합니다. 고유한 이름의 볼륨과 컨테이너를 새로 생성합니다. 준비 상태나 데이터 검사가 실패해도 context manager가 생성한 실습 자원을 정리합니다. 일회용 예제에 운영 볼륨을 넣지 마세요.

### `jenkins_lab.py`

```python
import json
import os
import subprocess
import time
import urllib.error
import urllib.request
import uuid


class DockerLab:
    def __init__(self):
        self.prefix = 'jenkins-proof-' + uuid.uuid4().hex[:12]
        self.containers, self.volumes = [], []

    def cli(self, *args):
        return subprocess.check_output(['docker', *args], text=True, stderr=subprocess.PIPE).strip()

    def volume(self):
        name = f'{self.prefix}-home-{len(self.volumes)}'
        existing = subprocess.run(['docker', 'volume', 'inspect', name], capture_output=True)
        if existing.returncode == 0:
            raise RuntimeError('Refusing an existing volume')
        self.cli('volume', 'create', name)
        self.volumes.append(name)
        return name

    def __enter__(self):
        self.cli('info')
        requested = os.environ.get('JENKINS_IMAGE', 'jenkins/jenkins:lts-jdk21')
        self.cli('pull', requested)
        self.image = self.cli('image', 'inspect', requested, '--format', '{{index .RepoDigests 0}}')
        if '@sha256:' not in self.image:
            raise RuntimeError('Expected a pulled repository digest')
        self.home = self.volume()
        return self

    def start(self, volume=None):
        name = f'{self.prefix}-controller-{len(self.containers)}'
        self.cli('run', '-d', '--name', name, '-p', '127.0.0.1::8080',
                 '--mount', f'type=volume,source={volume or self.home},target=/var/jenkins_home', self.image)
        self.containers.append(name)
        port = self.cli('port', name, '8080/tcp')
        if not port.startswith('127.0.0.1:'):
            raise RuntimeError('Expected a loopback binding')
        deadline = time.monotonic() + 180
        while time.monotonic() < deadline:
            try:
                with urllib.request.urlopen(f'http://{port}/login', timeout=5) as response:
                    self.version = response.headers.get('X-Jenkins')
                    if response.status == 200 and self.version and b'Jenkins' in response.read():
                        return name
            except (urllib.error.URLError, TimeoutError):
                pass
            time.sleep(2)
        raise RuntimeError('Jenkins login was not ready within 180 seconds')

    def password(self, name):
        return self.cli('exec', name, 'cat', '/var/jenkins_home/secrets/initialAdminPassword')

    def marker(self, name):
        return self.cli('exec', name, 'cat', '/var/jenkins_home/lab-marker')

    def __exit__(self, *_):
        for name in reversed(self.containers):
            subprocess.run(['docker', 'rm', '-f', name], capture_output=True)
        for name in reversed(self.volumes):
            subprocess.run(['docker', 'volume', 'rm', name], capture_output=True)


if __name__ == '__main__':
    with DockerLab() as lab:
        first = lab.start()
        password = lab.password(first)
        assert password, 'Missing initial password'
        lab.cli('exec', first, 'sh', '-c', 'printf kept > /var/jenkins_home/lab-marker')
        lab.cli('rm', '-f', first)
        second = lab.start()
        assert lab.marker(second) == 'kept'
        assert lab.password(second) == password
        print(json.dumps({'image': lab.image, 'jenkins': lab.version, 'recreated': True,
                          'markerPersisted': True, 'passwordPersisted': True, 'result': 'passed'}))
```

Docker 데몬을 사용할 수 있는 상태에서 실행합니다.

```sh
python3 jenkins_lab.py
```

컨트롤러를 두 번 시작할 때 각각 최대 180초 동안 `/login`의 HTTP200, `X-Jenkins` 헤더, `Jenkins`가 포함된 본문을 기다립니다. 표식 파일을 쓰고 초기 비밀번호를 출력 없이 읽은 뒤 첫 컨테이너를 교체하고 두 값을 다시 비교합니다. `recreated`·`markerPersisted`·`passwordPersisted`가 true이고 `result: passed`라면 선택한 검사를 통과한 것입니다. JSON에는 digest와 실제 Jenkins 버전도 기록하므로 임의의 pull 로그를 붙이지 않아도 됩니다.

이 실습은 Jenkins 잠금 해제, 플러그인 설치, 관리자 계정 설정 완료나 작업 실행을 하지 않습니다. 준비 상태 검사는 로그인 HTTP 응답을 확인하며 초기 설정 완료를 뜻하지 않습니다. Mac에서 Docker 엔진이 꺼져 있다면 선택한 엔진을 먼저 시작해야 합니다. Docker CLI만으로는 실습을 실행할 수 없습니다.

## 설치와 데이터 보존 구분하기

계속 사용할 설치는 [공식 설정 마법사](https://www.jenkins.io/doc/book/installing/docker/)를 따라 관리자 계정을 생성합니다. 초기 비밀번호는 직접 만든 컨트롤러의 `/var/jenkins_home/secrets/initialAdminPassword`에서 읽으세요. 예제 값을 재사용하거나 해당 값이 포함된 로그를 공개하지 않습니다. 이 스크립트는 실습 자원을 삭제하므로 대화형 설치를 보존할 명령은 아닙니다.

[이름 있는 Docker 볼륨](https://docs.docker.com/engine/storage/volumes/)은 컨테이너를 삭제해도 남길 수 있지만 백업은 아닙니다. 볼륨을 잃으면 데이터도 잃습니다. [정지한 볼륨의 백업·복구 실습](/ko/posts/2026-10-27-jenkins-home-backup-restore/)에서 같은 이미지와 별도 대상 볼륨으로 이어 확인합니다. 이 블로그 자체의 게시는 [Astro Draft PR 워크플로](/ko/posts/2026-04-07-jekyll-github-actions-content-pipeline/)를 따릅니다. Jenkins 예제가 해당 파이프라인을 대체하지 않습니다.
