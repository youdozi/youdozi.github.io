---
title: "셸에서 숫자 버전 비교하기: 1.10·1.2와 긴 구간 처리"
language: "ko"
translationKey: "2023-11-17-linux-shellscript-version-compare"
routeSlug: "2023-11-17-linux-shellscript-version-compare"
kind: "post"
publishedAt: "2023-11-16T15:00:00.000Z"
categories:
  - "linux"
tags:
  - "linux"
  - "bash"
  - "shell script"
  - "function"
legacyUrl: "/linux/linux-shellscript-version-compare/"
legacySource: "_posts/linux/shell-script/version-compare/2023-11-17-linux-shell\
  script-version-compare.markdown"
updatedAt: "2026-10-27T02:12:24+00:00"
reviewedAt: "2026-10-27"
reviewStatus: "revised"
reviewScope: "공식 문서 대조 및 원고 실행 예제 검증"
archiveBodySha256: "f37ceec00fdff01e81f73fcc49dae62b19867ad2b93ab3dfd840987a01b0521f"
reviewSources:
  - "https://docs.python.org/3/library/itertools.html#itertools.zip_longest"
  - "https://semver.org/"
description: "Python 3로 점으로 구분한 숫자 버전을 비교합니다. 자릿수와 구간 개수, 뒤쪽 0, 잘못된 입력의 종료 상태를 처리하며 SemVer와 범위를 구분합니다."
---
`1.10`과 `1.2`는 문자열이나 소수로 비교하면 안 됩니다. 점으로 구분한 정수 구간을 왼쪽부터 비교하고, 빠진 뒤쪽 구간은 0으로 채우면 `1.2`와 `1.2.0`을 같게 취급할 수 있습니다. 아래 예제는 이 규칙을 사용하는 숫자 버전 전용입니다.

`v1.2`, `1.2-rc1`, `1.2+build`는 받지 않습니다. [SemVer](https://semver.org/)의 pre-release 우선순위가 필요하면 해당 규격의 파서를 사용해야 합니다. 접미사를 무조건 잘라내면 의미가 달라질 수 있습니다.

## 실행 가능한 비교 스크립트

Python 3가 필요합니다. `version-compare.sh`로 저장하고 `sh`로 실행합니다.

### `version-compare.sh`

```sh
#!/bin/sh
set -eu
python3 - "$@" <<'PYTHON'
import re
import sys
from itertools import zip_longest

if len(sys.argv) != 3 or any(not re.fullmatch(r"[0-9]+(?:\.[0-9]+)*", value) for value in sys.argv[1:]):
    print("usage: version-compare.sh CURRENT LATEST (numeric dotted versions)", file=sys.stderr)
    raise SystemExit(2)
current, latest = sys.argv[1:]
try:
    left = [int(part) for part in current.split('.')]
    right = [int(part) for part in latest.split('.')]
except ValueError:
    print("numeric component exceeds this Python runtime's conversion limit", file=sys.stderr)
    raise SystemExit(2)
comparison = 0
for a, b in zip_longest(left, right, fillvalue=0):
    if a != b:
        comparison = -1 if a < b else 1
        break
operator = '<' if comparison < 0 else '>' if comparison > 0 else '='
print(f"{current} {operator} {latest}")
PYTHON
```

```sh
sh version-compare.sh 1.10.5 1.3.1
sh version-compare.sh 1.2 1.2.0
sh version-compare.sh 1.1000 2.0
```

출력은 차례로 `1.10.5 > 1.3.1`, `1.2 = 1.2.0`, `1.1000 < 2.0`입니다. 유효한 비교는 대소관계와 상관없이 종료 코드 0입니다. 인자 개수·표기가 잘못됐거나 숫자 변환 한도를 넘으면 stderr에 설명을 쓰고 2로 종료합니다.

| 입력 | 결과 |
| --- | --- |
| `1.2.0.0.1`과 `1.2` | `1.2.0.0.1 > 1.2` |
| `01.002`와 `1.2` | `01.002 = 1.2` |
| `1.2-rc1`과 `1.2` | 허용하지 않는 형식, 종료 코드 2 |
| `1..2`와 `1.2` | 허용하지 않는 형식, 종료 코드 2 |

## 고정 자릿수로 합치지 않는 이유

`awk`의 `%03d` 같은 폭 지정은 최소 표시 폭이며 구간의 최대 길이를 정하는 규칙이 아닙니다. 이어 붙인 값을 셸 정수로 비교하면 큰 값이나 구간 개수 때문에 원래 순서를 잃을 수 있습니다.

이 예제는 구간마다 Python 정수로 변환하고 [`zip_longest(..., fillvalue=0)`](https://docs.python.org/3/library/itertools.html#itertools.zip_longest)로 길이를 맞춥니다. 변환을 실행 환경이 거부하는 경우도 정상 비교로 처리하지 않습니다.

자동 배포에서 비교 결과와 명령 성공 여부는 별개입니다. 버전이 낮다고 실패 코드로 종료하는 스크립트가 아니므로, stdout의 관계를 읽어 후속 정책을 결정해야 합니다. [GitHub 릴리스 태그](/ko/posts/2023-09-23-linux-shellscript-github-latest/)는 이 숫자 형식이라는 보장이 없으므로 그대로 넘기지 마세요. 인터프리터 호출 방식은 [POSIX sh 함수 예제](/ko/posts/2023-09-20-linux-shellscript-function-error/)를 참고할 수 있습니다.
