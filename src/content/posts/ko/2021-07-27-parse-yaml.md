---
title: "셸에서 YAML 읽기: eval 없이 포트 검증하고 프로세스 실행하기"
language: ko
translationKey: 2021-07-27-parse-yaml
routeSlug: 2021-07-27-parse-yaml
kind: post
publishedAt: 2021-07-26T15:00:00.000Z
categories:
  - linux
tags:
  - linux
  - bash
  - parse
  - yaml
legacyUrl: /linux/parse-yaml/
legacySource: _posts/linux/shell-script/parse-yaml/2021-07-27-parse-yaml.markdown
updatedAt: 2026-10-27T05:23:47.316+00:00
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Official sources checked; runnable examples checked separately from
  migration and production claims.
archiveBodySha256: c510b6cca7b94d9bd54a7e99e781003c51084f82b38710ebda2bc3869af2b072
reviewSources:
  - https://pyyaml.org/wiki/PyYAMLDocumentation
  - https://pypi.org/project/PyYAML/6.0.3/
  - https://www.gnu.org/software/bash/manual/html_node/Executing-Commands.html
description: Python과 PyYAML로 YAML 정수 포트를 검증하고, eval 없이 자식 프로세스에 SERVER_PORT를
  전달합니다. 문자열·불리언·잘못된 입력을 거부합니다.
---
셸에서 YAML을 읽을 때는 sed/awk로 전체 문법을 흉내 내거나 파싱 결과를 `eval`하지 말고, YAML 파서가 읽은 값의 타입과 범위를 검사한 뒤 필요한 변수만 전달하세요. 이 예제는 Python과 PyYAML로 `server.port` 하나를 읽고, 검증에 성공했을 때만 자식 명령을 실행합니다.

출력 문자열만 검사하면 YAML 정수 `8080`과 문자열 `"8080"`을 구분하기 어렵습니다. 여기서는 **문자열을 숫자로 강제 변환하지 않고**, 파서가 정수로 읽은 1~65535만 허용합니다. Python의 bool은 int의 하위 타입이므로 `isinstance(port, int)` 대신 `type(port) is int`로 불리언을 거부합니다.

## 처리 흐름

![YAML 검증 후 명령 실행 흐름도](/assets/diagrams/2021-07-27-parse-yaml-ko.svg)

정수 포트를 파싱·검증한 뒤 SERVER_PORT를 내보냅니다. 로더 실패 시 대상 명령은 시작하지 않으며 exec는 대상의 종료 상태를 유지합니다.

## 실행 환경과 입력

Python 3과 [PyYAML 6.0.3](https://pypi.org/project/PyYAML/6.0.3/)을 사용합니다. 로컬 실행 환경은 Python 3.13입니다. 다음 세 파일을 같은 디렉터리에 저장하고, 전용 가상 환경에 의존성을 설치합니다.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install PyYAML==6.0.3
```

### `application.yml`

```yaml
server:
  port: 8080
```

### `read-port.py`

```python
import sys
from pathlib import Path
import yaml

if len(sys.argv) != 2:
    sys.exit("usage: read-port.py CONFIG")
try:
    with Path(sys.argv[1]).open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    if not isinstance(config, dict):
        raise ValueError("root must be a mapping")
    server = config.get("server")
    if not isinstance(server, dict):
        raise ValueError("server must be a mapping")
    port = server.get("port")
    if type(port) is not int or not 1 <= port <= 65535:
        raise ValueError("server.port must be an integer from 1 to 65535")
except (OSError, UnicodeError, yaml.YAMLError, ValueError) as error:
    print(f"invalid configuration: {error}", file=sys.stderr)
    sys.exit(2)
print(port)
```

### `run-with-port.sh`

```sh
#!/bin/sh
set -eu
if [ "$#" -lt 2 ]; then
    printf '%s\n' 'usage: run-with-port.sh CONFIG COMMAND [ARG ...]' >&2
    exit 2
fi
config=$1
shift
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
port=$("${PYTHON:-python3}" "$script_dir/read-port.py" "$config")
export SERVER_PORT="$port"
exec "$@"
```

## 검증된 값으로 명령 실행

```sh
PYTHON=.venv/bin/python sh run-with-port.sh application.yml \
  .venv/bin/python -c 'import os; print(os.environ["SERVER_PORT"])'
```

```text
8080
```

`read-port.py`는 정상 값만 stdout에 출력하고 오류는 stderr로 보냅니다. 파일 누락, 잘못된 YAML, 여러 문서, 매핑이 아닌 입력, 필드 누락, 문자열·불리언·실수·범위 초과를 상태 2로 거부합니다. `run-with-port.sh`는 이 실패를 전달하므로 대상 명령을 실행하지 않습니다. 반면 대상 명령이 실행된 뒤의 종료 상태는 `exec`가 그대로 전달합니다.

`"$@"`는 명령과 각 인자를 분리해 보존합니다. 인자 안의 공백이나 `$()`를 셸 소스로 다시 평가하지 않습니다. 상대 경로인 `PYTHON`과 설정 파일 경로는 호출한 작업 디렉터리를 기준으로 해석하고, `read-port.py`는 래퍼 파일의 위치에서 찾습니다.

export는 실행한 자식 프로세스에만 전달되며 호출한 부모 셸의 환경을 바꾸지 않습니다. 이 스크립트를 source하지 말고 `sh run-with-port.sh ...`로 실행하세요. 애플리케이션이 `SERVER_PORT`를 실제로 읽는지도 별도로 확인해야 합니다.

## 이 설정 로더의 범위

[`safe_load`](https://pyyaml.org/wiki/PyYAMLDocumentation)는 임의 Python 객체를 생성하는 태그를 허용하지 않지만, 애플리케이션의 타입·범위 검사는 별도로 필요합니다. 또한 이 예제는 악의적인 크기의 입력에 대한 메모리·시간 제한을 제공하지 않으므로 신뢰하는 로컬 설정을 대상으로 합니다.

PyYAML의 암시적 타입 규칙을 따르므로 `on` 같은 값이 불리언으로 읽힐 수 있습니다. 중복 키는 거부하지 않으며 뒤의 값이 남을 수 있으니 입력에서 금지하고 별도로 검사하세요. YAML 1.2 전체의 타입 정책이나 범용 설정 스키마 검증을 구현한 로더가 아닙니다. 여러 설정을 추가하려면 각 필드의 타입과 누락 정책을 별도로 정의해야 합니다.

명령 실행과 오류 상태 처리는 [GitHub 릴리스 조회 예제](/ko/posts/2023-09-23-linux-shellscript-github-latest/)에서, JVM 작업의 데이터 호환성은 [Spring Batch 5 이관](/ko/posts/2023-10-27-springbatch5-migration/)에서 이어서 볼 수 있습니다.
