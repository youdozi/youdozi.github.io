---
layout: posts
title:  "[linux] Parse yaml"
date:   2021-07-27 00:00:00 +0900
categories: 
    - Linux 
    - Bash
tags: 
    - linux
    - bash
    - parse
    - yaml
---
bash를 사용하여 yaml 파일을 파싱 및 환경 변수로 손쉽게 등록할 수 있습니다.

CI/CD 및 다양한 환경에서 사용할 수 있으니 참고하면 좋을듯 합니다.

---

프로젝트 구조 .

* [src](./src)
    * [main](./src/main)
        * [resources](./src/main/resources)
            * [application.yml](./src/main/resources/application.yml)
* [util.sh](.util.sh)
* [usage.sh](.usage.sh)


---

application.yml 파일의 내용은 아래와 같습니다.

```yaml
server:
  port: 8080
```

먼저 util.sh 을 작성해봅시다.

참고 : https://gist.github.com/pkuczynski/8665367#gistcomment-2347639
```shell
#!/bin/bash

# application.yml parse util
# '-' 하이픈은 강제 스테이크 케이스로 변경, 하위 property는 상위 property에 '_'로 연결됩니다.
# 예: server.port -> server_port
function parse_yaml() {

  local prefix=$2
  local s='[[:space:]]*'
  local w='[a-zA-Z0-9_\-]*'
  local fs=$(echo @ | tr @ '\034')

  sed "h;s/^[^:]*//;x;s/:.*$//;y/-/_/;G;s/\n//" $1 |
    sed -ne "s|^\($s\)\($w\)$s:$s\"\(.*\)\"$s\$|\1$fs\2$fs\3|p" \
      -e "s|^\($s\)\($w\)$s:$s\(.*\)$s\$|\1$fs\2$fs\3|p" |
    awk -F$fs '{
    indent = length($1)/2;
    vname[indent] = $2;

    for (i in vname) {if (i > indent) {delete vname[i]}}
    if (length($3) > 0) {
        vn=""; for (i=0; i<indent; i++) {vn=(vn)(vname[i])("_")}
        printf("%s%s%s=\"%s\"\n", "'$prefix'",vn, $2, $3);
    }
  }'
}

```

usage.sh을 작성해봅시다.. 로직은 아래와 같습니다.
- util.sh을 import하고 절대 경로 확인 
- application.yml을 파싱 후 환경 변수 등록
- echo 출력

```shell
#!/bin/bash

source ./util.sh

ROOT_DIR=$(
cd "$(dirname "$0")"
pwd -P
)

eval $(parse_yaml ${ROOT_DIR}/src/main/resources/application.yml)

echo "server_port: ${server_port}"
```

이제 shell에서 직접 실행해보겠습니다.

입력
```shell
~ sh usage.sh
```

출력
```shell
~ server_port: 8080
```

${server_port} 환경 변수에 application.yml의 server.port 값이 적용된 것을 확인할 수 있습니다!!