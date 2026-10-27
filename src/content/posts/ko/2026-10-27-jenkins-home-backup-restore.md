---
language: ko
translationKey: 2026-10-27-jenkins-home-backup-restore
routeSlug: 2026-10-27-jenkins-home-backup-restore
kind: post
publishedAt: 2026-10-27T08:56:40.345Z
categories:
  - jenkins
title: "Jenkins 홈 백업: 정지한 컨트롤러를 새 볼륨에 복구하기"
description: 실습 컨트롤러를 정지하고 master.key를 압축 파일과 분리합니다. 새 볼륨에 복구한 뒤 HTTP 응답·표식·초기 비밀번호의 보존을 확인합니다.
tags:
  - jenkins
  - docker
  - containers
  - backup
  - testing
updatedAt: 2026-10-27T08:56:40.345Z
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Primary documentation and disposable-container contracts reviewed; exact image/version and hosted execution evidence recorded separately.
reviewSources:
  - https://www.jenkins.io/doc/book/installing/docker/
  - https://github.com/jenkinsci/docker/blob/master/README.md
  - https://www.jenkins.io/doc/book/system-administration/backing-up/
  - https://docs.docker.com/engine/storage/volumes/
  - https://docs.docker.com/engine/network/port-publishing/
---
백업은 새 볼륨에 복원하고 Jenkins를 다시 시작해 확인합니다. 압축 파일이 존재한다는 사실만으로 컨트롤러가 그 파일을 사용할 수 있다고 판단하지 않습니다.

이 실습은 새로 만든 미사용 컨트롤러를 정지한 뒤 홈을 복사합니다. master.key를 압축 파일과 분리해 보관한 뒤, 비공개 압축 파일을 또 다른 새 볼륨에 풀고 같은 이미지 digest로 시작해 표식과 원래 초기 비밀번호를 비교합니다. 비밀번호 값은 출력하지 않습니다. 운영 컨트롤러, 실행 중인 작업, 플러그인 이관을 검증하는 예제는 아닙니다.

## 정지·복사·복구·시작하기

![실습 컨트롤러를 정지하고 볼륨을 복사해 별도 복구를 검증하는 흐름](/assets/diagrams/2026-10-27-jenkins-home-backup-restore-ko.svg)

[Jenkins 백업 안내](https://www.jenkins.io/doc/book/system-administration/backing-up/)는 백업 대상과 복구 검증을 구분합니다. 이 예제는 컨트롤러가 쓰는 중에 파일을 복사하지 않도록 정지한 소스를 사용합니다. 외부 DB·에이전트·다른 작성 주체를 함께 조정하는 스냅샷은 아닙니다.

[컨트롤러 재생성 실습](/ko/posts/2023-09-28-jenkins-docker-install/)의 전체 `jenkins_lab.py`를 준비하고 같은 디렉터리에 다음 파일을 저장합니다. Python3와 Linux 컨테이너를 실행하는 Docker 엔진이 필요합니다.

### `jenkins_restore.py`

```python
import json
import tempfile
from jenkins_lab import DockerLab

with DockerLab() as lab, \
        tempfile.TemporaryDirectory(prefix='jenkins-private-backup-') as backup, \
        tempfile.TemporaryDirectory(prefix='jenkins-private-key-') as keys:
    original = lab.start()
    password = lab.password(original)
    assert password, 'Missing initial password'
    lab.cli('exec', original, 'sh', '-c', 'printf restored > /var/jenkins_home/lab-marker')
    lab.cli('stop', '-t', '30', original)
    lab.cli('run', '--rm', '--user', '0:0', '--entrypoint', 'sh',
            '--mount', f'type=volume,source={lab.home},target=/source,readonly',
            '--mount', f'type=bind,source={backup},target=/backup',
            '--mount', f'type=bind,source={keys},target=/keys', lab.image,
            '-c', 'set -e; umask 077; tar -C /source --exclude=./secrets/master.key -czpf /backup/home.tgz .; cp -p /source/secrets/master.key /keys/master.key')
    members = lab.cli('run', '--rm', '--user', '0:0', '--entrypoint', 'tar',
                      '--mount', f'type=bind,source={backup},target=/backup,readonly', lab.image,
                      '-tzf', '/backup/home.tgz')
    assert './secrets/master.key' not in members.splitlines()
    restored_home = lab.volume()
    lab.cli('run', '--rm', '--user', '0:0', '--entrypoint', 'tar',
            '--mount', f'type=bind,source={backup},target=/backup,readonly',
            '--mount', f'type=volume,source={restored_home},target=/restore', lab.image,
            '-xzpf', '/backup/home.tgz', '-C', '/restore')
    lab.cli('run', '--rm', '--user', '0:0', '--entrypoint', 'cp',
            '--mount', f'type=bind,source={keys},target=/keys,readonly',
            '--mount', f'type=volume,source={restored_home},target=/restore', lab.image,
            '-p', '/keys/master.key', '/restore/secrets/master.key')
    restored = lab.start(restored_home)
    assert lab.marker(restored) == 'restored'
    assert lab.password(restored) == password
    print(json.dumps({'image': lab.image, 'jenkins': lab.version, 'sourceStopped': True,
                      'restoredToNewVolume': True, 'masterKeyExcluded': True, 'keyCopiedSeparately': True, 'markerRestored': True,
                      'passwordRestored': True, 'result': 'passed'}))
```

실행합니다.

```sh
python3 jenkins_restore.py
```

보조 컨테이너는 entrypoint를 파일 복사 도구로 바꾸므로 다른 Jenkins 프로세스를 시작하지 않습니다. 복사 중 원래 소유권과 권한을 보존하기 위해 보조 컨테이너만 root로 실행합니다. 압축 파일 목록에 master.key가 없는지 확인하고, Jenkins 시작 전에 별도 보조 컨테이너가 키를 복원합니다. 컨트롤러 정지 뒤 소스 볼륨을 읽기 전용으로 마운트하고, 대상은 이 실습이 별도로 생성한 볼륨을 사용합니다. 이미지는 실습을 시작할 때 선택한 digest를 따릅니다.

성공 결과에는 `sourceStopped`·`restoredToNewVolume`·`markerRestored`·`passwordRestored`·`masterKeyExcluded`·`keyCopiedSeparately`가 true이고 `result: passed`가 표시됩니다. 복구한 컨트롤러도 `DockerLab.start`의 HTTP 준비 상태 검사를 통과해야 합니다. 초기 비밀번호 일치는 해당 비밀 파일의 보존만 확인합니다. 관리자 설정 완료나 모든 자격 증명 플러그인을 시험하지 않습니다.

## 압축 파일도 컨트롤러 데이터로 다루기

이 예제는 일회용 복구 실습입니다. 압축 파일에서 `secrets/master.key`를 제외하고 키를 별도로 복사해 압축 해제 후 복원합니다. 다른 컨트롤러 비밀 값은 압축 파일에 남습니다. 임시 디렉터리 두 개 모두 비공개로 만들고 종료 시 삭제합니다. CI 산출물로 업로드하거나 커밋하지 않으며, 전체 복사를 운영 백업 정책으로 그대로 사용하지 않습니다.

운영 환경에서는 [컨트롤러 키에 대한 Jenkins 안내](https://www.jenkins.io/doc/book/system-administration/backing-up/)에 따라 `master.key`를 일반 백업과 분리해 관리해야 합니다. 백업 절차를 도입하기 전에 키 복구·압축 파일 암호화·보존 기간·접근 권한·외부 저장소·외부 상태의 범위를 정합니다. 같은 장비의 임시 파일에는 이러한 내구성 보장이 없습니다.

복구한 컨트롤러도 실습 종료 시 삭제됩니다. 반복 실행을 위한 정리이지만, 표식·비밀 파일·HTTP 검사 통과만으로 모든 작업·플러그인·자격 증명·외부 연동이 복구된다고 보장할 수는 없습니다. 실제 시스템의 복구 연습에는 대표 작업과 비밀 값 복호화 검사도 추가해야 합니다.
