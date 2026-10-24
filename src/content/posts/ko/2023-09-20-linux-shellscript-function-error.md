---
title: "[linux] shell script function non-standard"
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
updatedAt: "2026-10-24T09:00:00+09:00"
reviewedAt: "2026-10-24"
reviewStatus: "revised"
reviewScope: "공식 문서 대조 및 예제 코드 검토"
archiveBodySha256: "e578326b731309c674cf215918a0e02baa58dd49df7f97f0d555ba35700c805b"
reviewSources:
  - "https://www.shellcheck.net/wiki/SC2112"
---
## 개요
intellij에서 shell script 코드를 작성할 때 이런 warning 메시지를 보여주더군요.  

```shell
function keyword is non-standard. Delete it.
```

문제가 되는 shell script 코드는 아래와 같습니다.

```shell
#!/bin/sh
function hello() {
  echo "Hello World"
}
```

위 코드에서 function 키워드를 삭제하라고 안내해주고 있습니다.  
올바른 코드는 무엇일까요?

```shell
#!/bin/sh
hello() {
  echo "Hello World"
}
```

아주 심플하죠? function 키워드만 삭제하면 됩니다.  
왜 이런 warning 메시지가 표시될까요?

아래 `ShellCheck` 링크에 그 해답이 있습니다.

[https://www.shellcheck.net/wiki/SC2112](https://www.shellcheck.net/wiki/SC2112)

```text
function is a non-standard keyword that can be used to declare functions in Bash and Ksh.

In POSIX sh and dash, a function is instead declared without the function keyword as in the correct example.
```
간단하게 해석하자면 아래와 같습니다.

```text
"function"은 Bash와 Ksh에서 함수를 선언하는 데 사용할 수 있는 비표준 키워드입니다.

반면에 POSIX sh와 dash에서는 함수를 선언할 때 "function" 키워드 없이 아래와 같이 선언됩니다.
```
`#!/bin/sh`로 선언한 스크립트에서는 무시하면 안 됩니다. 실행 환경의 sh 구현에 따라 문법 오류로 종료될 수 있습니다.  
다만 `ShellCheck`도 정적 분석 도구에 일부분 이기 때문에 하나의 룰로 정한다면  
더 좋은 코드가 완성 되지 않을까 합니다.

## 검증 및 보강 — 2026-10-24

Bash 문법이 필요하면 shebang을 `#!/usr/bin/env bash`로 지정하고 `bash script.sh` 또는 실행 권한을 준 뒤 `./script.sh`로 실행하세요. `sh script.sh`는 shebang을 따르는 실행 방식이 아닙니다. POSIX 호환 스크립트라면 `hello() { ...; }` 형태를 사용합니다. 정적 분석은 실제 실행할 셸 설정과 함께 수행해야 합니다.

### 확인한 자료

- [공식 자료 1](https://www.shellcheck.net/wiki/SC2112)
