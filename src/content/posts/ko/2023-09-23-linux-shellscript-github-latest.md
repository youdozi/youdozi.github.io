---
title: "curl·jq로 GitHub 최신 릴리스 조회와 다운로드 자산 선택하기"
language: "ko"
translationKey: "2023-09-23-linux-shellscript-github-latest"
routeSlug: "2023-09-23-linux-shellscript-github-latest"
kind: "post"
publishedAt: "2023-09-26T15:00:00.000Z"
categories:
  - "linux"
tags:
  - "linux"
  - "bash"
  - "shell script"
  - "jq"
  - "github latest release"
legacyUrl: "/linux/linux-shellscript-github-latest/"
legacySource: "_posts/linux/shell-script/github-latest/2023-09-23-linux-shellsc\
  ript-github-latest.markdown"
updatedAt: 2026-10-30T05:15:39.658659+00:00
reviewedAt: "2026-10-30"
reviewStatus: "revised"
reviewScope: "공식 문서 대조 및 원고 실행 예제 검증"
archiveBodySha256: "877051a28045533ef144cb07484e1a225f8961202dd0b24dd398d49603b3a275"
reviewSources:
  - "https://docs.github.com/en/rest/releases/releases#get-the-latest-release"
  - "https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api"
  - "https://curl.se/docs/manpage.html"
  - "https://jqlang.org/manual/"
description: "curl과 jq로 GitHub 최신 릴리스에서 OS·CPU·형식에 맞는 자산 하나를 선택합니다. HTTP 오류·잘못된 JSON·누락·중복을 처리하며 파일은 다운로드하지 않습니다."
---
`curl`로 GitHub 최신 릴리스를 조회하고 `jq`로 OS·CPU·파일 형식에 맞는 다운로드 자산을 정확히 하나 선택합니다. 아래 스크립트는 HTTP 오류·잘못된 JSON·자산 누락·중복에서 실패하며, 파일을 다운로드하지 않고 메타데이터를 반환합니다.

`releases/latest`는 숫자로 가장 큰 Git 태그를 계산하는 API가 아닙니다. [공식 릴리스 API](https://docs.github.com/en/rest/releases/releases#get-the-latest-release)는 일반 태그·draft·prerelease와 게시 릴리스를 구분합니다.

아래 예제는 공개 저장소 `adoptium/temurin17-binaries`의 Linux x64 HotSpot JDK tar.gz 메타데이터를 조회합니다. 토큰이나 실제 파일 다운로드는 필요하지 않습니다. 저장소 인자를 생략하면 이 기본값을 사용하고 명시적인 빈 인자는 거부합니다.

## 처리 흐름

![GitHub 릴리스 자산 1개 선택 흐름도](/assets/diagrams/2023-09-23-linux-shellscript-github-latest-ko.svg)

HTTP 실패는 JSON 파싱 전에 종료합니다. 올바른 릴리스 객체에서 조건에 맞는 자산 1개만 선택하며 URL 선택은 파일 검증이 아닙니다.

## HTTP 실패와 JSON 선택 실패 분리하기

`curl`, `jq`, POSIX sh가 필요합니다. `latest-release.sh`로 저장합니다.

### `latest-release.sh`

```sh
#!/bin/sh
set -eu
if [ "$#" -gt 1 ]; then
    printf '%s\n' 'usage: latest-release.sh OWNER/REPO' >&2
    exit 2
fi
repo=${1-adoptium/temurin17-binaries}
case "$repo" in
    */*/*|/*|*/|*[!A-Za-z0-9_./-]*) printf '%s\n' 'usage: latest-release.sh OWNER/REPO' >&2; exit 2 ;;
esac
case "$repo" in
    */*) ;;
    *) printf '%s\n' 'usage: latest-release.sh OWNER/REPO' >&2; exit 2 ;;
esac
api=${GITHUB_API_URL:-https://api.github.com}
response=$(curl --fail --silent --show-error --location --max-time 20 \
    --header 'Accept: application/vnd.github+json' \
    --header 'X-GitHub-Api-Version: 2026-03-10' \
    "$api/repos/$repo/releases/latest") || exit 1
printf '%s' "$response" | jq --slurp --exit-status '
    if length != 1 or (.[0] | type) != "object" then
        error("expected one release object")
    else .[0] end
    | . as $release
    | if (.tag_name | type) != "string" or (.tag_name | length) == 0
         or (.assets | type) != "array" then
        error("missing release tag or assets")
      else . end
    | [.assets[] | select(.name | test("^OpenJDK17U-jdk_x64_linux_hotspot_.*\\.tar\\.gz$"))] as $assets
    | if ($assets | length) != 1 then
        error("expected exactly one Linux x64 JDK tar.gz asset")
      elif ($assets[0].browser_download_url | type) != "string"
           or ($assets[0].browser_download_url | length) == 0 then
        error("missing asset download URL")
      else {tag_name: $release.tag_name, download_url: $assets[0].browser_download_url} end
'
```

```sh
sh latest-release.sh adoptium/temurin17-binaries
```

정상 결과는 `tag_name`, `download_url`을 가진 JSON 객체입니다. 값은 조회 시점의 릴리스에 따라 달라집니다. 아래는 응답 구조를 보여주는 테스트 데이터이며 현재 최신 버전이라는 뜻은 아닙니다.

```json
{"tag_name":"jdk-17.0.8.1+1","download_url":"https://github.com/adoptium/temurin17-binaries/releases/download/example/OpenJDK17U-jdk_x64_linux_hotspot_example.tar.gz"}
```

`curl --fail`로 HTTP 오류를 먼저 처리합니다. 응답을 변수에 받은 뒤 JSON을 처리하므로 네트워크 실패를 파이프라인의 마지막 명령 성공으로 덮지 않습니다. [`curl` 옵션](https://curl.se/docs/manpage.html).

`jq --slurp`는 입력 전체를 배열로 받습니다. JSON 값이 정확히 하나인지 확인하므로 빈 응답도 거부합니다. 그다음 릴리스 객체·태그·자산 배열을 검사하고, 파일명 패턴과 맞는 자산이 하나일 때만 객체를 출력합니다. [`jq` 매뉴얼](https://jqlang.org/manual/).

## 자동화에서 확인할 결과

| 상황 | 처리 |
| --- | --- |
| 정상 응답, 일치 자산 1개 | JSON 출력, 종료 코드 0 |
| HTTP 403·404 또는 연결 실패 | 0이 아닌 코드로 종료 |
| 빈 응답·잘못된 JSON | 0이 아닌 코드로 종료 |
| 자산 0개·2개 이상 | 임의로 고르지 않고 실패 |
| 잘못된 저장소 인자 형식 | 사용법 출력, 종료 코드 2 |

HTTP 요청은 성공했는데 일치하는 자산이 없다면 `jq` 필터를 바꾸기 전에 릴리스 파일명을 확인하세요. 이 예제는 모든 JDK 패키지가 아니라 Linux x64용 Java 17을 선택합니다. Java 21이 필요하면 [Temurin 플랫폼 메타데이터 예제](/ko/posts/2023-10-10-temurin-jdk21-delay/)를 사용하세요. 저장소나 플랫폼 값을 YAML에서 읽는다면 명령에 넘기기 전에 [설정을 데이터로 읽고 검증](/ko/posts/2021-07-27-parse-yaml/)하세요.

예제는 로컬 HTTP 응답으로 성공·HTTP 오류·JSON 오류·자산 누락과 중복을 확인했습니다. `GITHUB_API_URL`은 기본적으로 공개 API 주소이며 같은 응답 계약을 가진 테스트 서버로 바꿔 검사할 수 있습니다.

공개 리소스 조회에는 인증이 필수가 아닙니다. 인증이 필요해 확장한다면 토큰을 소스에 적거나 셸 추적 로그에 남기지 마세요. 요청 한도는 응답 헤더와 [GitHub rate-limit 안내](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api)로 확인합니다.

이 스크립트는 다운로드 URL을 선택할 뿐 설치 파일의 무결성을 확인하지 않습니다. 설치 자동화에서는 공급자의 체크섬·서명과 대상 플랫폼을 별도로 확인해야 합니다. 태그를 [숫자 버전 비교](/ko/posts/2023-11-17-linux-shellscript-version-compare/)에 넘길 때도 그 문서의 입력 범위와 같은지 먼저 판단하세요.
