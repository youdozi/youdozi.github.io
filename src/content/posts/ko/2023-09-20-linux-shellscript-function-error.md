---
title: "셸 함수의 function 경고 해결: POSIX sh와 Bash 실행 구분"
language: "ko"
translationKey: "2023-09-20-linux-shellscript-function-error"
routeSlug: "2023-09-20-linux-shellscript-function-error"
kind: "post"
publishedAt: "2023-09-19T15:00:00.000Z"
categories:
  - "linux"
tags:
  - "linux"
  - "bash"
  - "shell script"
  - "function"
legacyUrl: "/linux/linux-shellscript-function-error/"
legacySource: "_posts/linux/shell-script/function-error/2023-09-20-linux-shells\
  cript-function-error.markdown"
updatedAt: "2026-10-27T02:12:24+00:00"
reviewedAt: "2026-10-27"
reviewStatus: "revised"
reviewScope: "공식 문서 대조 및 원고 실행 예제 검증"
archiveBodySha256: "e578326b731309c674cf215918a0e02baa58dd49df7f97f0d555ba35700c805b"
reviewSources:
  - "https://www.shellcheck.net/wiki/SC2112"
description: "function 키워드 경고를 POSIX sh 함수 문법으로 해결하고, shebang과 sh·bash 호출의 차이, 인자 인용과 반환 코드를 실행 예제로 확인합니다."
---
`#!/bin/sh` 스크립트에서는 `function hello()` 대신 `hello() { ...; }` 형태를 사용합니다. Bash 문법이 필요하다면 Bash를 선택하고 그 인터프리터로 실행해야 합니다. `sh script.sh`는 파일의 Bash shebang을 따르는 호출이 아닙니다.

[ShellCheck SC2112](https://www.shellcheck.net/wiki/SC2112)는 `function`이 POSIX sh 문법이 아니라는 점을 지적합니다. `/bin/sh`가 어떤 구현인지에 따라 우연히 동작할 수 있어도 이식성을 보장하지는 않습니다.

## 실행할 셸에 맞는 함수 작성하기

다음을 `greet.sh`로 저장합니다. 함수 인자는 `"$1"`, 호출 인자는 `"$@"`로 인용해 공백과 와일드카드를 그대로 전달합니다.

### `greet.sh`

```sh
#!/bin/sh
set -eu

greet() {
    if [ "$#" -ne 1 ]; then
        printf '%s\n' 'usage: greet.sh NAME' >&2
        return 2
    fi
    printf 'Hello, %s\n' "$1"
}

greet "$@"
```

```sh
sh -n greet.sh
sh greet.sh 'Ada Lovelace'
sh greet.sh 'Ada *'
```

출력은 각각 `Hello, Ada Lovelace`, `Hello, Ada *`입니다. `sh -n`은 구문만 검사하므로 실제 호출도 확인해야 합니다. 인자가 없거나 둘 이상이면 사용법을 stderr에 쓰고 종료 코드 2를 반환합니다. 유효한 인자는 종료 코드 0입니다.

## shebang과 명시적 호출 구분하기

| 실행 방법 | 인터프리터 선택 |
| --- | --- |
| `sh greet.sh NAME` | 호출한 `sh`가 파일을 읽습니다. |
| `bash greet.sh NAME` | Bash가 읽습니다. |
| `chmod +x greet.sh` 후 `./greet.sh NAME` | 이 실행에서는 파일의 shebang을 사용합니다. |

Bash 배열이나 `[[ ... ]]`가 필요하면 `#!/usr/bin/env bash`를 사용하고 `bash script.sh` 또는 실행 권한을 준 `./script.sh`로 실행하세요. `sh script.sh`로 호출하면서 Bash 문법을 기대해서는 안 됩니다. [`function`과 셸 선택에 관한 ShellCheck 설명](https://www.shellcheck.net/wiki/SC2112).

함수의 `return`은 호출자에게 제어를 돌려주고 상태를 전달합니다. 함수 안의 `exit`는 실행 중인 셸을 끝냅니다. 위 스크립트는 함수를 마지막에 호출하므로 그 상태가 스크립트의 종료 상태가 됩니다.

예제는 공백·와일드카드가 있는 인자와 인자 개수 오류를 검사했습니다. `/bin/sh`의 실제 구현은 환경마다 다르므로 배포할 셸에서도 실행하세요. 다음 단계는 [숫자 버전 비교](/ko/posts/2023-11-17-linux-shellscript-version-compare/)나 [GitHub 릴리스 조회](/ko/posts/2023-09-23-linux-shellscript-github-latest/)처럼 입력과 실패 상태를 명확히 하는 자동화입니다.
