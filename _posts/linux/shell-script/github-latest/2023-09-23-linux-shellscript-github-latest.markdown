---
layout: posts
title:  "[linux] github latest release"
date:   2023-09-27 00:00:00 +0900
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

request
```shell
curl https://api.github.com/rate_limit
```

### github API 분석
openjdk의 공급사인 adoptium의 최신 release를 가져오도록 하겠습니다.  
github access token을 아래 넣어주고 API 요청을 합니다.  

request
```shell
curl -L -H "Authorization: Bearer ${ACCESS_TOKEN}" \
https://api.github.com/repos/adoptium/temurin17-binaries/releases/latest
```
response
```json
{
  "url": "https://api.github.com/repos/adoptium/temurin17-binaries/releases/119075034",
  "assets_url": "https://api.github.com/repos/adoptium/temurin17-binaries/releases/119075034/assets",
  "upload_url": "https://uploads.github.com/repos/adoptium/temurin17-binaries/releases/119075034/assets{?name,label}",
  "html_url": "https://github.com/adoptium/temurin17-binaries/releases/tag/jdk-17.0.8.1%2B1",
  "id": 119075034,
  "author": {
    "login": "eclipse-temurin-bot",
    "id": 81643974,
    "node_id": "MDQ6VXNlcjgxNjQzOTc0",
    "avatar_url": "https://avatars.githubusercontent.com/u/81643974?v=4",
    "gravatar_id": "",
    "url": "https://api.github.com/users/eclipse-temurin-bot",
    "html_url": "https://github.com/eclipse-temurin-bot",
    "followers_url": "https://api.github.com/users/eclipse-temurin-bot/followers",
    "following_url": "https://api.github.com/users/eclipse-temurin-bot/following{/other_user}",
    "gists_url": "https://api.github.com/users/eclipse-temurin-bot/gists{/gist_id}",
    "starred_url": "https://api.github.com/users/eclipse-temurin-bot/starred{/owner}{/repo}",
    "subscriptions_url": "https://api.github.com/users/eclipse-temurin-bot/subscriptions",
    "organizations_url": "https://api.github.com/users/eclipse-temurin-bot/orgs",
    "repos_url": "https://api.github.com/users/eclipse-temurin-bot/repos",
    "events_url": "https://api.github.com/users/eclipse-temurin-bot/events{/privacy}",
    "received_events_url": "https://api.github.com/users/eclipse-temurin-bot/received_events",
    "type": "User",
    "site_admin": false
  },
  "node_id": "RE_kwDOFjpjCs4HGPDa",
  "tag_name": "jdk-17.0.8.1+1",
  "target_commitish": "main",
  "name": "jdk-17.0.8.1+1",
  "draft": false,
  "prerelease": false,
  "created_at": "2022-08-15T07:03:39Z",
  "published_at": "2023-08-29T13:10:18Z",
  "assets": [
    {
      "url": "https://api.github.com/repos/adoptium/temurin17-binaries/releases/assets/123616608",
      "id": 123616608,
      "node_id": "RA_kwDOFjpjCs4HXj1g",
      "name": "OpenJDK17U-debugimage_aarch64_linux_hotspot_17.0.8.1_1.tar.gz",
      "label": "",
      "uploader": {
        "login": "eclipse-temurin-bot",
        "id": 81643974,
        "node_id": "MDQ6VXNlcjgxNjQzOTc0",
        "avatar_url": "https://avatars.githubusercontent.com/u/81643974?v=4",
        "gravatar_id": "",
        "url": "https://api.github.com/users/eclipse-temurin-bot",
        "html_url": "https://github.com/eclipse-temurin-bot",
        "followers_url": "https://api.github.com/users/eclipse-temurin-bot/followers",
        "following_url": "https://api.github.com/users/eclipse-temurin-bot/following{/other_user}",
        "gists_url": "https://api.github.com/users/eclipse-temurin-bot/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/eclipse-temurin-bot/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/eclipse-temurin-bot/subscriptions",
        "organizations_url": "https://api.github.com/users/eclipse-temurin-bot/orgs",
        "repos_url": "https://api.github.com/users/eclipse-temurin-bot/repos",
        "events_url": "https://api.github.com/users/eclipse-temurin-bot/events{/privacy}",
        "received_events_url": "https://api.github.com/users/eclipse-temurin-bot/received_events",
        "type": "User",
        "site_admin": false
      },
      "content_type": "application/x-compressed-tar",
      "state": "uploaded",
      "size": 162252748,
      "download_count": 493,
      "created_at": "2023-08-29T13:10:53Z",
      "updated_at": "2023-08-29T13:11:00Z",
      "browser_download_url": "https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.8.1%2B1/OpenJDK17U-debugimage_aarch64_linux_hotspot_17.0.8.1_1.tar.gz"
    },
    ...
}
```
방대한 데이터가 오기 때문에 앞 부분만 잘랐습니다.  
크게 부모 release object -> 자식 assets array 구조로 나눠져 있는 것을 볼 수 있습니다.  
여기서 tag_name, assets[].browser_download_url 만 있으면 될 것 같네요.  
하지만 tag_name은 부모, browser_download_url는 자식 array에 있으니 평탄화 해서 이쁘게 처리 해보겠습니다.

```shell
curl -L -H "Authorization: Bearer ${ACCESS_TOKEN}" \
https://api.github.com/repos/adoptium/temurin17-binaries/releases/latest |
jq '{("tag_name"): .tag_name, ("download_url"): .assets[].browser_download_url} |
select( .download_url | contains("jdk_x64_linux_hotspot")) |
select( .tag_name | contains("beta") | not) |
select( .download_url | test("\\.tar.gz$"))'
```
curl 이후 pipe를 통해 jq로 응답값을 전달합니다.  
이제 본격적으로 jq를 이용해서 json을 만져볼텐데..  
단락별로 나눠서 설명 드리도록 하겠습니다.

```shell
jq '{("tag_name"): .tag_name, ("download_url"): .assets[].browser_download_url}'
```
tag_name, assets[].browser_download_url를 파싱하여 한쌍의 json으로 노출될 수 있도록 평탄화해주는 작업을 합니다.  
jq에서도 pipe를 통해 값을 이후로 전달할 수 있습니다!

```shell
select( .download_url | contains("jdk_x64_linux_hotspot")) |
select( .tag_name | contains("beta") | not) |
select( .download_url | test("\\.tar.gz$"))
```
jq select 함수를 이용하여 필터링 합니다.
여기서 필터링할 내용이 몇가지 있는데 
* linux x64 hotspot
* beta 제외
* tar.gz로 끝나는 확장자

이 3가지 유형을 contains, not contains, 정규식등의 예제가 각각 보여줍니다.
이제 결과물을 보자면?
```json
{
  "tag_name": "jdk-17.0.8.1+1",
  "download_url": "https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.8.1%2B1/OpenJDK17U-jdk_x64_linux_hotspot_17.0.8.1_1.tar.gz"
}
```
우리가 원하는 데이터가 나옵니다.
이런 방식으로 github API를 응용하면 재미난 것을 많이 구현할 수 있습니다.

