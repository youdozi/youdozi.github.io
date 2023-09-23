---
layout: posts
title:  "[linux] github latest release"
date:   2023-09-24 00:00:00 +0900
categories: 
    - linux 
tags: 
    - linux
    - bash
    - shell script
    - jq
    - github latest release
---
## 개요
github rest API 문서를 보면 재미있는 API들이 있습니다.  
오늘은 그 중 최신 release 가져오는 API를 만져보도록 하겠습니다.

### 준비물
#### jq
* 설치 -> `brew install jq`

#### github access token
* [https://docs.github.com/ko/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens](https://docs.github.com/ko/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
* access token이 없으면 분당 10회만 조회할 수 있습니다.
* 아래 API를 요청하면 core, graphql, integration_manifest, search 별로 limit, reset 시간을 알 수 있습니다.

```shell
curl https://api.github.com/rate_limit
```

### github API 분석
