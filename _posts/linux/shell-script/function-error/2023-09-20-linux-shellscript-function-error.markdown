---
layout: posts
title:  "[linux] shell script function non-standard"
date:   2023-09-20 00:00:00 +0900
categories: 
    - linux 
tags: 
    - linux
    - bash
    - shell script
    - function
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
error 메시지는 아니기 때문에 지키지 않아도 무방합니다.  
다만 `ShellCheck`도 정적 분석 도구에 일부분 이기 때문에 하나의 룰로 정한다면  
더 좋은 코드가 완성 되지 않을까 합니다.