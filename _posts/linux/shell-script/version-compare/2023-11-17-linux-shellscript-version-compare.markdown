---
layout: posts
title:  "[linux] shell script version compare"
date:   2023-11-17 00:00:00 +0900
categories: 
    - linux 
tags: 
    - linux
    - bash
    - shell script
    - function
---
## 개요
linux를 사용하다 보면 version 비교하는 기능이 필요합니다.  
특히 기존 설치된 패키지의 version을 확인하여 업데이트할 경우가 있겠죠.  
아래와 같이 간단한 shell script로 구현할 수 있습니다.


```shell
#!/bin/bash

function VERSION {
  echo "$@" | awk -F. '{ printf("%d%03d%03d%03d\n", $1,$2,$3,$4); }'
}

CURRENT_VERSION=$1
LATEST_VERSION=$2

if [ $(VERSION $CURRENT_VERSION) -lt $(VERSION $LATEST_VERSION) ]; then
  echo "$CURRENT_VERSION < $LATEST_VERSION"
else
  echo "$CURRENT_VERSION >= $LATEST_VERSION"
fi

```
이제 테스트를 해볼까요?

```shell
➜  shellscript sh test.sh 8 17
8 < 17
➜  shellscript sh test.sh 11 11
11 >= 11
➜  shellscript sh test.sh 17 11
17 >= 11
➜  shellscript sh test.sh 1.1.5 1.3.1
1.1.5 < 1.3.1
➜  shellscript sh test.sh 1.10.5 1.3.1
1.10.5 >= 1.3.1
```
2개의 arg를 비교하여 결과 값을 보여줍니다.