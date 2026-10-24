---
title: "[linux] shell script version compare"
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
updatedAt: "2026-10-24T09:00:00+09:00"
reviewedAt: "2026-10-24"
reviewStatus: "revised"
reviewScope: "정수 구간 비교의 범위 명시 및 오버플로·구간 길이 오류 수정"
archiveBodySha256: "f37ceec00fdff01e81f73fcc49dae62b19867ad2b93ab3dfd840987a01b0521f"
reviewSources:
  - "https://docs.python.org/3/library/itertools.html#itertools.zip_longest"
  - "https://semver.org/"
---
## 비교할 버전 형식부터 정하기

기존 awk의 `%03d`는 각 구간을 최소 세 자리로 출력할 뿐 길이를 제한하지 않습니다. `1.1000`처럼 세 자리를 넘는 구간이나 셸 정수 범위를 넘는 결과에서는 올바른 대소 비교를 보장하지 못합니다. 또한 네 구간 뒤의 값은 버리고 `-rc`, `+build` 같은 표기를 처리하지 않습니다.

아래 코드는 **점으로 구분된 음수가 아닌 정수 구간**만 비교합니다. `1.2`와 `1.2.0`은 같다고 정의합니다. SemVer의 pre-release 우선순위까지 처리하는 코드는 아닙니다.

## 실행 가능한 비교 예제

Python 3가 설치된 환경에서 Bash로 실행합니다.

```bash
#!/usr/bin/env bash
set -euo pipefail

python3 - "$@" <<'PYTHON'
import re
import sys
from itertools import zip_longest

if len(sys.argv) != 3 or any(not re.fullmatch(r"[0-9]+(?:\.[0-9]+)*", value) for value in sys.argv[1:]):
    print("usage: version-compare.sh CURRENT LATEST (numeric dotted versions)", file=sys.stderr)
    raise SystemExit(2)

current, latest = sys.argv[1:]
left = [int(part) for part in current.split('.')]
right = [int(part) for part in latest.split('.')]
comparison = 0
for a, b in zip_longest(left, right, fillvalue=0):
    if a != b:
        comparison = -1 if a < b else 1
        break
operator = '<' if comparison < 0 else '>' if comparison > 0 else '='
print(f"{current} {operator} {latest}")
PYTHON
```

```text
bash version-compare.sh 1.10.5 1.3.1   → 1.10.5 > 1.3.1
bash version-compare.sh 1.2 1.2.0      → 1.2 = 1.2.0
bash version-compare.sh 1.1000 2.0     → 1.1000 < 2.0
bash version-compare.sh 1.2-rc1 1.2    → 사용법을 출력하고 종료 코드 2
```

버전 비교 결과와 명령 실행의 성공·실패는 구분합니다. 이 예제는 유효한 비교를 하면 종료 코드 0, 잘못된 입력이면 2를 반환합니다. prerelease와 build metadata까지 필요하면 직접 문자열을 잘라 비교하는 대신 해당 버전 규격의 파서를 사용하세요.

## 확인한 자료

- [공식 자료 1](https://docs.python.org/3/library/itertools.html#itertools.zip_longest)
- [공식 자료 2](https://semver.org/)
