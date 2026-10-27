---
title: "GitHub·Sourcegraph 코드 검색: 저장소·경로를 좁히고 로컬에서 확인하기"
language: ko
translationKey: 2021-08-06-search-github
routeSlug: 2021-08-06-search-github
kind: post
publishedAt: 2021-08-05T01:00:00.000Z
categories:
  - util
tags:
  - util
  - github
  - search
  - sourcegraph
legacyUrl: /util/search-github/
legacySource: _posts/util/2021-08-06-search-github.markdown
updatedAt: 2026-10-27T07:19:48.249Z
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Primary documentation checked; paired examples and diagram/code
  structure validated. Execution and UI limits are stated in the article.
archiveBodySha256: c8a545f5b1c093bd1721d0966f5dad9412768cdba23f7c1ffa75c17829c7c8e6
reviewSources:
  - https://docs.github.com/en/search-github/github-code-search/understanding-github-code-search-syntax
  - https://sourcegraph.com/docs/code-search/queries
  - https://git-scm.com/docs/git-grep
description: GitHub와 Sourcegraph의 검색 문법을 구분하고 저장소·언어·경로로 범위를 좁힙니다. 작은 Git 저장소에서
  고정 문자열 검색과 경로 필터를 재현합니다.
---
코드 검색은 저장소와 파일 범위를 먼저 정하고, 일치한 구현의 문맥을 읽는 순서로 진행하세요. 이름이 같은 심볼을 찾았다고 사용 중인 의존성 버전이나 동작까지 일치하는 것은 아닙니다.

GitHub 코드 검색, Sourcegraph, 로컬 체크아웃은 접근·검색 가능한 데이터가 다릅니다. 필요한 저장소를 볼 수 있는 도구를 선택하고, 공개 인스턴스가 모든 저장소와 리비전을 색인한다고 가정하지 않습니다.

## 처리 흐름

![검색 범위를 좁힌 뒤 구현 문맥을 확인하는 흐름도](/assets/diagrams/2021-08-06-search-github-ko.svg)

결과 목록을 늘리기 전에 질의 범위를 좁힙니다. 버전이 중요하면 기본 브랜치 대신 필요한 리비전을 열거나 해당 리비전의 체크아웃에서 검색합니다.

## 서비스별 검색 문법 구분하기

[GitHub 코드 검색](https://docs.github.com/en/search-github/github-code-search/understanding-github-code-search-syntax)에서는 다음 조건과 따옴표로 감싼 구문을 조합할 수 있습니다.

```text
repo:spring-projects/spring-framework language:java path:WebClient.java "interface WebClient"
```

[Sourcegraph 검색 필터](https://sourcegraph.com/docs/code-search/queries)는 저장소·파일 범위에 정규식을 사용합니다.

```text
repo:^github\.com/spring-projects/spring-framework$ lang:java file:WebClient\.java$ "interface WebClient"
```

| 목적 | GitHub 코드 검색 | Sourcegraph |
| --- | --- | --- |
| 저장소 | `repo:owner/name` | `repo:` 정규식. 정확한 범위가 필요하면 앵커 사용 |
| Java | `language:java` | `lang:java`·`language:java` |
| 파일 범위 | `path:` 경로 필터 | `file:` 정규식 |
| 정확한 구문 | 따옴표로 감싼 구문 | keyword 모드의 따옴표 구문 |

질의 구성 예제이며 실시간 검색 결과 수를 측정한 것은 아닙니다. Sourcegraph 예제는 파일명 끝을 고정하므로 두 도구의 경로 조건이 같은 결과 집합을 만든다고 단정할 수도 없습니다. 접근 권한·색인 대상·리비전도 확인하세요.

## 빈 디렉터리에서 로컬 검색 재현하기

Git과 POSIX 셸로 작은 예제를 만듭니다. `demo-search`가 이미 있으면 `mkdir`에서 중단하므로 새로운 작업 디렉터리를 사용하세요.

```sh
set -eu
mkdir demo-search
cd demo-search
git init -q
mkdir src docs
printf '%s\n' 'interface WebClient {}' > src/WebClient.java
printf '%s\n' 'interface WebClient is discussed here' > docs/notes.txt
git add src docs
git grep -n -F 'interface WebClient' -- src
```

출력:

```text
src/WebClient.java:1:interface WebClient {}
```

`docs/notes.txt`에도 같은 구문이 있지만 `-- src`로 범위를 제한했습니다. [`git grep -F`](https://git-scm.com/docs/git-grep)는 정규식이 아닌 고정 문자열로 검색하고 `-n`은 줄 번호를 표시합니다. 기본 작업 트리 검색은 추적 파일을 대상으로 하므로 먼저 인덱스에 추가했으며 커밋은 만들지 않았습니다. 실제 체크아웃에서는 필요한 경로·패턴으로 바꾸되 의도한 범위를 유지합니다.

찾은 코드를 적용하기 전에는 호출부·테스트·라이선스·리비전을 함께 읽으세요. 다른 릴리스에서는 같은 선언의 동작도 달라질 수 있습니다. 검색 결과에서 동작을 추측하는 대신 [WebClient 응답 테스트](/ko/posts/2023-09-19-springboot-test-webclient/)로 필요한 클라이언트 계약을 확인할 수 있습니다.
