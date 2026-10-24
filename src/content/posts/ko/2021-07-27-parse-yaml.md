---
title: "[linux] Parse yaml"
language: "ko"
translationKey: "2021-07-27-parse-yaml"
routeSlug: "2021-07-27-parse-yaml"
kind: "post"
publishedAt: "2021-07-26T15:00:00.000Z"
categories:
  - "linux"
tags:
  - "linux"
  - "bash"
  - "parse"
  - "yaml"
legacyUrl: "/linux/parse-yaml/"
legacySource: "_posts/linux/shell-script/parse-yaml/2021-07-27-parse-yaml.markdown"
updatedAt: "2026-10-24T09:00:00+09:00"
reviewedAt: "2026-10-24"
reviewStatus: "revised"
reviewScope: "YAML 처리 범위 및 eval·부모 셸 환경변수 설명 정정"
archiveBodySha256: "c510b6cca7b94d9bd54a7e99e781003c51084f82b38710ebda2bc3869af2b072"
reviewSources:
  - "https://mikefarah.gitbook.io/yq/"
  - "https://mikefarah.gitbook.io/yq/usage/shellvariables"
  - "https://www.gnu.org/software/bash/manual/html_node/Bourne-Shell-Builtins.html"
---
## 셸에서 YAML 값을 읽을 때의 범위

기존의 sed/awk 예제는 들여쓰기가 단순한 YAML 일부만 처리합니다. 배열, 여러 줄 문자열, 인용과 특수문자, 앵커 등 YAML 문법 전체를 지원하는 파서가 아닙니다. 특히 파싱 결과를 `eval`하면 데이터가 셸 명령으로 해석될 수 있어 원문 방식을 일반적인 설정 로더로 사용하면 안 됩니다.

한두 개의 정해진 값을 읽는다면 YAML 파서로 해당 필드만 추출하고 타입·범위를 검사한 뒤 직접 변수에 넣는 편이 명확합니다. 아래 예제는 **Bash와 Mike Farah의 yq v4**를 전제로 합니다. 같은 이름의 다른 yq 구현과 명령 문법이 다를 수 있습니다.

## 입력 설정

```yaml
server:
  port: 8080
```

## 검증 후 변수에 넣기

```bash
#!/usr/bin/env bash
set -euo pipefail

config_path=${1:-application.yml}
port=$(yq -r '.server.port // ""' "$config_path")

if [[ ! "$port" =~ ^[0-9]{1,5}$ ]]; then
  printf '%s\n' 'server.port must be an integer from 1 to 65535' >&2
  exit 1
fi

# 10#은 앞에 0이 있어도 8진수로 해석하지 않게 합니다.
port_number=$((10#$port))
if (( port_number < 1 || port_number > 65535 )); then
  printf '%s\n' 'server.port is out of range' >&2
  exit 1
fi

export server_port="$port_number"
printf 'server_port: %s\n' "$server_port"
# 이 스크립트에서 시작한 자식 프로세스는 server_port를 상속합니다.
```

파일 경로를 따옴표로 감싸 공백을 보존했고, 누락·문자열·범위 초과를 거부합니다. 설정 파일이 없다면 yq의 실패 상태와 `set -e`로 종료합니다. `bash load-config.sh application.yml`로 실행한 자식 셸의 export는 호출한 부모 셸까지 바꾸지 않습니다. 애플리케이션을 이 스크립트에서 실행하거나 같은 셸에서 함수를 호출하는 방식으로 연결하세요. `set -e`와 `exit`가 있는 파일을 부모 셸에 무심코 source하는 것도 피해야 합니다.

여러 필드를 다룰 때는 필드 이름, 허용 타입과 누락 처리 정책을 명시합니다. YAML 키를 무조건 환경 변수로 평탄화하면 `a.b`와 `a_b`의 충돌이나 배열 처리 기준도 별도로 필요합니다.

## 확인한 자료

- [공식 자료 1](https://mikefarah.gitbook.io/yq/)
- [공식 자료 2](https://mikefarah.gitbook.io/yq/usage/shellvariables)
- [공식 자료 3](https://www.gnu.org/software/bash/manual/html_node/Bourne-Shell-Builtins.html)
