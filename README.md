# youdozi's memory

Astro로 생성하고 GitHub Pages에 배포하는 기술 블로그입니다. 영문을 기본 언어로 사용하며 한국어 아카이브를 함께 제공합니다. Python RSS 수집·근거 검증을 유지하고 새 다이제스트는 두 언어의 구조화된 JSON으로 발행합니다.

## 문제별 실행 예제

| 해결할 문제 | 영어 | 한국어 |
| --- | --- | --- |
| curl·jq로 GitHub 릴리스 자산 하나 선택 | [Release asset selection](https://youdozi.github.io/en/posts/2023-09-23-linux-shellscript-github-latest/) | [릴리스 자산 선택](https://youdozi.github.io/ko/posts/2023-09-23-linux-shellscript-github-latest/) |
| Temurin JDK 21의 플랫폼 메타데이터 확인 | [Temurin metadata](https://youdozi.github.io/en/posts/2023-10-10-temurin-jdk21-delay/) | [Temurin 메타데이터](https://youdozi.github.io/ko/posts/2023-10-10-temurin-jdk21-delay/) |
| Batch 5 이관 범위와 새 저장소의 재시작 구분 | [Batch migration and restart](https://youdozi.github.io/en/posts/2023-10-27-springbatch5-migration/) | [Batch 이관과 재시작](https://youdozi.github.io/ko/posts/2023-10-27-springbatch5-migration/) |
| Vue 앱을 실행 JAR에 패키징하고 HTTP 응답 확인 | [Frontend packaging](https://youdozi.github.io/en/posts/2021-07-23-multiple-gradle-build/) | [프런트엔드 패키징](https://youdozi.github.io/ko/posts/2021-07-23-multiple-gradle-build/) |

각 글에 코드·그림·고정 재현 환경과 확인 범위를 함께 제공합니다. 셸 검사는 `scripts/check_shell_automation_examples.py`, YAML·Temurin 입력 검사는 `scripts/check_config_input_examples.py`, Batch 검사는 `scripts/check_jvm_runtime_examples.py --part batch`, 패키징 검사는 `scripts/check_multi_frontend_example.py`를 사용합니다. 실행 환경은 아래 검증 안내와 각 글을 따르세요. 과거 예제의 고정 버전은 현재 운영 환경 추천이 아닙니다.

GitHub 릴리스·숫자 버전 비교·YAML·Temurin 메타데이터·JDK 21·WebClient·Batch의 한영 글 14편은 글 상단에서 예제 ZIP을 받을 수 있습니다. 코드는 해당 언어 원고에서 추출하며 `README.txt`에 실행 환경·명령·네트워크 필요 여부·확인 범위를 제공합니다. WebClient는 본문의 인라인 프로젝트 설정도 파일로 포함합니다. Gradle wrapper나 설치된 의존성은 묶지 않습니다. `PROVENANCE.json`의 원문·파일 해시는 일치를 확인하는 용도이며 정확성이나 운영 적합성 인증이 아닙니다.

`content/examples/downloads.json`이 대상·파일 선택·안내 문구를 관리합니다. `scripts/build_example_archives.py`는 네트워크 요청 없이 한영 코드 일치를 확인하고 고정 순서·시각·권한의 ZIP 14개를 생성합니다. `npm run dev` 전과 일반 빌드의 공통 자산 준비에서 생성하며 결과는 커밋하지 않습니다. 기존 실행 검사는 ZIP에서 푼 코드를 별도로 추출한 원고 코드와 대조한 뒤 실행합니다. 빌드 마지막에는 실제 배포 파일·해시·다운로드 링크·대상 외 페이지의 링크 부재까지 검사합니다. 글의 주소·게시일·본문·수정일과 미게시 번역 고정 목록은 유지합니다.

```sh
python3 -B scripts/build_example_archives.py
python3 -B scripts/build_example_archives.py --check-dist dist
```

## 로컬 실행

Node 24와 Python 3.11 이상을 사용합니다. 게시된 Java 예제 검증에는 JDK 17 이상도 필요합니다.

```sh
nvm use
npm ci
npm run dev
```

- 영문 홈: http://localhost:4321/en/
- 한국어 홈: http://localhost:4321/ko/
- `/`는 `/en/`으로 이동합니다.

기존 글 230개는 한국어로 보존했습니다. 이 중 테스트 데이터로 확인된 1편은 실제 뉴스 목록·검색·RSS에서 제외하고 예제 페이지로 남겼습니다. 핵심 개발 글 36편의 영문판이 준비돼 있으며, 새 원고·영문·한국어 다이제스트는 원고 검토와 게시 승인 후 공개합니다. 번역되지 않은 한국어 글을 영문 페이지로 복제하지 않습니다.

## 콘텐츠 작성

기술 글의 새 작성·본문 보강에는 **흐름 그림과 대응하는 코드 예제를 함께 포함**합니다. 그림·코드·설명의 순서와 분기를 대조하고, 실제 렌더링·모바일 가독성·코드 실행을 확인합니다. 자세한 기준은 [기술 글 작성 기준](docs/technical-writing.md)과 [저장소 작업 규칙](AGENTS.md)을 따릅니다. 현재 한영 기술 글 48개 주제의 흐름도 96개를 준비했으며 공통 자산 준비 단계에서 생성합니다. 알고리즘은 전체 Java 클래스, Spring·빌드·JDK·셸·유틸리티 글은 각 그림에 등록한 코드 언어와 핵심 구문을 검사합니다.

- 기존/수동 작성 글: `src/content/posts/{en,ko}/*.md`
- 새 자동 다이제스트: `src/content/digests/YYYY-MM-DD.json`
- 두 언어의 동일한 글은 `translationKey`를 공유합니다.
- 주소는 `routeSlug`로 결정합니다. Astro의 예약된 `slug` 필드는 사용하지 않습니다.
- 일반 글은 `/{lang}/posts/{routeSlug}/`, 다이제스트는 `/{lang}/digest/YYYY-MM-DD/`입니다.
- `publishedAt`에는 시간대를 포함한 ISO 8601 문자열을 지정합니다. 미래 글은 게시 목록에서 제외됩니다.

```yaml
---
title: "Example article"
language: "en"
translationKey: "example-article"
routeSlug: "example-article"
kind: "post"
publishedAt: "2026-10-24T09:00:00+09:00"
categories: [java]
tags: [java, spring]
---
```

컬렉션 스키마는 `src/content.config.ts`에 있습니다. 같은 언어의 URL과 번역 키 중복은 빌드 오류입니다. 다른 언어의 동일 글이 있을 때 언어 전환과 `hreflang`으로 연결하며, 없으면 해당 언어 홈으로 안내합니다.

## 검증

```sh
npm run test:python
npm run test:articles
npm run check:digests
npm test
npm run check
npm run build
npm run preview
```

`npm test`는 이관 무결성과 실제 Astro의 두 언어 렌더링을 검사합니다. 렌더링 테스트는 임시 fixture를 생성했다가 제거하므로 테스트 후 공개 산출물은 `npm run build`로 다시 생성하세요. `npm run build`는 이미지와 검색엔진 소유권 파일을 `public/`에 준비하고, 전체 페이지·내부 링크·이미지·앵커·기존 글 수를 검사합니다. 외부 사이트 접속 검사는 하지 않습니다. 전체 게시글을 개별 글 하단에 반복하지 않고 관련 글 최대 3개만 표시합니다.

관련 글은 같은 언어의 공개 글에서 공통 태그·카테고리와 제목에 명시된 기술 주제를 기준으로 고릅니다. 구체적인 공통 태그를 우선하고 동점이면 최신 발행일·URL 순으로 정렬합니다. 글과 뉴스 사이의 연결을 허용하되 자기 자신·예제와 관련성이 없는 글은 제외합니다. `dev`, `digest`, `archive-renewal` 같은 공통 분류만으로는 추천하지 않습니다. 번역 뉴스는 승인된 영어 기준 제목도 사용하므로 언어에 따라 기술명이 다르게 표기되어도 같은 신호를 얻습니다. 이는 본문 전체를 이해하는 의미 검색이 아닌 명시적인 규칙이며, 새로운 기술 주제는 `src/lib/related.ts`에서 관리합니다. 관련 글과 주제 탐색 링크를 댓글보다 먼저 보여주며, 내부 작업 태그는 주제 목록에 표시하지 않습니다. 원고·승인 기록과 기존 글·분류 URL은 변경하지 않습니다.

내부 태그를 숨긴 뒤 실제 주제가 없는 언어별 주제 목록은 `noindex,follow`로 유지하고 사이트맵·언어 대체 링크에서 제외합니다. 현재 해당하는 번역 언어 6개의 빈 목록만 제외되며, 모든 글의 사이트맵 항목은 유지됩니다.

기술 글의 실행 예제는 원고의 코드 블록을 직접 추출합니다. `python3 -B scripts/check_developer_tool_examples.py`는 로컬 HTTP 응답 15개·포트 오류 3개, draw.io XML의 노드·연결, Git 검색 5개 사례를 한영 원고에서 추출해 검사합니다. 온라인 검색 결과나 draw.io UI 실행을 검증하는 것은 아닙니다. `python3 -B scripts/check_webclient_example.py`는 JDK 17·Gradle 8.4에서 영문·한국어 Java/Gradle 예제의 일치와 HTTP 응답 계약 8개를 검사합니다. `python3 -B scripts/check_string_formatting_examples.py`는 표준 문자열 예제의 출력과 로케일 독립성을 검사하며, 두 검사는 CI에서도 실행합니다. 역사적인 JDK 21 preview는 해당 JDK를 설치한 뒤 `--preview-jdk /path/to/jdk21`을 추가해 별도로 확인합니다.

알고리즘 예제는 `npm run test:articles`에서 원고의 Java 풀이 11개를 추출해 Java 11 타깃으로 컴파일합니다. LRU·내적·숫자 영단어·아이디 정규화·짝 제거·미완주 선수·실패율·폰켓몬·음양 더하기·x 간격 수열은 한영 전체 코드 일치도 확인합니다. 기존 회귀 사례를 유지하면서 리스트 기반 LRU 기준 구현과 짧은 요청 조합, 아이디 규칙·멱등성, 정수 경계값, 인접 쌍·미완주자·실패율·실제 선택 조합의 작은 입력 열거를 포함한 78,570개 동작 assertion을 검사합니다. 로컬 실행 JDK는 17이며 CI에서도 JDK 17로 검사합니다. 한영 코딩테스트 카테고리는 실제 공개된 풀이를 배열·문자열·컬렉션 학습 순서로 연결하고, 같은 목록을 ItemList 구조화 데이터와 사이트맵에 반영합니다.

Querydsl·Specification 비교는 `python3 -B scripts/check_query_strategies.py`로 설정 글의 파일 5개와 비교 글의 파일 3개를 직접 추출합니다. 한영 코드 일치, 기본 Q 소스·클래스 생성, 기존 H2 조회 2개와 비교·계약 검사 8개를 확인하고 `clean test`를 두 번 실행합니다. 중복·동등 비교의 특수문자·AND/OR·NULL·문자열 속성 오타를 다루며 성능이나 운영 DB 동등성을 입증하지 않습니다. CI에서도 이 확장 검사를 사용하고 기존 5파일 검사는 `scripts/check_querydsl_example.py`로 따로 실행할 수 있습니다.

빌드·쉘 자동화 묶음은 `python3 -B scripts/check_shell_automation_examples.py`로 함수·숫자 버전·릴리스 조회의 경계값과 로컬 HTTP 응답을 검사합니다. `python3 -B scripts/check_multi_frontend_example.py`는 Gradle 8.4/JDK 17/Node 24에서 두 Vue 앱을 빌드하고 실행 JAR의 경로·증분 정리·HTTP 제공을 검사합니다. 실제 세부 도구 버전은 로그에 기록합니다. 설치된 Chrome으로 화면 렌더링까지 확인하려면 `--browser`를 추가합니다. CI는 브라우저 실행 없이 두 검사기를 모두 실행합니다.

JVM·설정 묶음은 `python3 -B scripts/check_jvm_runtime_examples.py`로 Batch 5의 새 H2 스키마에서 파라미터 저장·완료 인스턴스 거부·실패 Step 재시작을 확인하고, JDK 21 정식 기능을 Preview 없이 컴파일·실행합니다. Gradle 8.4/JDK 17과 JDK 21이 필요하며 Linux에서는 `JDK17_HOME`·`JDK21_HOME`으로 경로를 구분할 수 있습니다. `--part batch`·`--part jdk`로 나누어 실행할 수도 있습니다. 기존 v4 데이터 이관 검사는 포함하지 않습니다. `scripts/requirements-config-examples.txt`를 전용 가상 환경에 설치한 뒤 `python3 -B scripts/check_config_input_examples.py`로 YAML 입력·자식 프로세스 실행·Temurin 메타데이터 선택을 검사합니다. 이 검사는 외부 API 호출과 JDK 바이너리 다운로드 없이 실행합니다.

Boot 생성·실행·Lombok 묶음은 `python3 -B scripts/check_boot_workflow_examples.py`로 원고 파일을 추출해 기본 컨텍스트 1개 → HTTP 테스트 포함 3개 → Lombok 테스트 포함 5개를 단계별 실행합니다. main/test 프로세서 누락 시 컴파일 실패, 복원 후 통과, BOM 해석 버전, 실행 JAR의 HTTP 응답과 Lombok 런타임 제외도 검사합니다. JDK 17과 설치된 Gradle로 임시 Wrapper를 생성해 Gradle 9.8.2를 사용하며, 이미 설치한 실행 파일은 `--gradle /path/to/gradle`로 지정할 수 있습니다. 최초 배포판·의존성 다운로드가 필요합니다. Initializr 서버 생성은 별도 확인하며 이 검사기는 Initializr API나 IDE UI를 실행하지 않습니다.

## 배포 전환

1. 이 변경을 검토하고 기본 게시 브랜치 `main`에 반영합니다.
2. GitHub 저장소 **Settings → Pages → Build and deployment → Source → GitHub Actions**를 선택합니다.
3. 기존 `GEMINI_API_KEY` Actions Secret을 유지합니다. 선택적으로 `GEMINI_MODEL` Actions Variable을 지정합니다.
4. `Site Quality Gates and Pages`의 빌드·검증·배포 성공을 확인합니다.
5. 검토 화면 `/review/`의 **GitHub에서 후보 생성 실행**에서 수동 호출할 수 있습니다. `Dev Content Pipeline`의 **Run workflow → main**에서 기본 설정 그대로 실행하면 검토용 Draft PR을 생성합니다. ‘검증만 실행’을 체크하면 PR 없이 AI 연결만 확인합니다. 이 실행만으로 게시되지는 않습니다.

`develop`과 PR에서는 검사만 실행합니다. `main` push와 수동 사이트 워크플로는 검증된 `dist/`를 Pages에 배포합니다. 정기 생성 워크플로는 검증된 JSON과 중복 방지 상태를 `content/digest-review-*` 브랜치에만 커밋하고, 재사용 워크플로로 배포 없이 검사한 뒤 Draft PR을 만듭니다. 사용자가 PR을 검토·수정하고 **Ready for review → Merge pull request**로 `main`에 병합해야 게시됩니다. 자동 병합은 하지 않으며 검토 대기 PR이 있으면 다음 생성은 건너뜁니다.

## 기존 URL과 아카이브

- 기존 일반 글 주소에 정적 이동 페이지를 생성합니다.
- 충돌하던 `/dev/digest/dev-digest/`는 `/ko/digest/`로 연결합니다. 서로 다른 195개 글은 날짜별 새 URL을 갖습니다.
- 기존 `/feed.xml`은 한국어 RSS를 유지합니다. 새 RSS는 `/en/feed.xml`, `/ko/feed.xml`입니다.
- 기존 이미지 주소 `/assets/img/...`와 검색엔진 소유권 파일을 유지합니다.
- 기존 글의 Utterances 댓글은 원래 pathname을 명시해 연결합니다. 새 다이제스트는 공통 번역 키로 두 언어의 댓글을 공유합니다. 실제 이슈 연결은 배포 후 확인해야 합니다.
- 기존 Google Analytics 측정 ID를 유지하며 운영 도메인에서만 로드합니다.
- GitHub Pages의 정적 이동 페이지는 meta refresh이며 HTTP 301은 아닙니다. 기존 taxonomy 앵커의 세부 선택은 새 카테고리/태그 목록에서 다시 해야 합니다.

`_posts/`, `_layouts/`, `_includes/`, `_sass/`, `_config.yml`, `Gemfile` 등은 이관 원본과 이전 구현 확인용으로 남겨두었습니다. 현재 작성 대상은 `src/content/`이며, Astro 배포에는 원본 디렉터리가 포함되지 않습니다. `npm run migrate:jekyll`은 최초 이관용이고 기존 이관 파일을 덮어쓰지 않습니다. 빌드에는 Ruby가 필요하지 않습니다.

자동화의 검증 범위와 호출 예산은 [PIPELINE.md](PIPELINE.md)를 참조하세요.

## 기존 글 내용 검토

2026-10-24에 일반 글 35편을 정정·보강하고 다이제스트 195편의 원문 접근 및 수집 설명을 점검했습니다. 각 글에는 검토 날짜와 범위를 표시하며, 이관 원본의 본문 해시로 변경 전 기록을 추적합니다. 전체 뉴스의 주장 1,125건을 모두 독립적으로 사실 검증했다는 의미는 아닙니다.

- `npm run test:articles`: 게시된 Java 풀이 11개를 직접 컴파일하고 경계값·무작위 입력을 검사합니다.
- `python3 scripts/check_webclient_example.py`: 본문 WebClient 테스트 3개를 추출해 실행합니다. Gradle 8.x와 JDK 17, 최초 의존성 다운로드가 필요합니다.
- `npm run audit:archive`: curl의 기본 TLS 검증으로 원문 응답과 기술 문서 참고 링크를 다시 확인합니다. 네트워크 작업이며 기본 빌드에서는 실행하지 않습니다.
- `.pipeline/archive-editorial-review.json`: 글별 보강 범위와 남아 있는 한계.
- `.pipeline/archive-source-review.json`: 원문 URL 응답·최종 주소·페이지 제목·본문 해시. HTTP 200은 사실 검증 표시가 아닙니다.
- `.pipeline/archive-evidence-review.json`: 기존 AI 감사 로그의 인용문 존재 대조 결과. 인용문 존재와 주장 타당성은 구분합니다.

변경 요약과 미확인 항목은 [CONTENT_REVIEW.md](CONTENT_REVIEW.md)를 참조하세요.

## Search Console 사이트맵 제출

`python3 scripts/search_console.py`는 `https://youdozi.github.io/` 속성의 접근 권한을 확인하고 사이트맵을 API로 제출한 다음 처리 상태를 조회합니다. 일반 API 키나 Gemini API 키는 사용할 수 없습니다. 매 배포마다 재제출하는 자동화는 추가하지 않았습니다.

최초 연결:

1. [Google Cloud Console](https://console.cloud.google.com/)에서 사용할 프로젝트를 선택하고 **Google Search Console API**를 활성화합니다.
2. **Google Auth Platform**에서 앱의 동의 화면을 설정합니다. 외부 앱이 테스트 상태라면 Search Console을 사용하는 본인 Google 계정을 테스트 사용자로 추가합니다.
3. OAuth 클라이언트를 **데스크톱 앱** 유형으로 만들고 JSON을 저장소 밖에 저장합니다. 예: `~/.config/youdozi-search-console/oauth-client.json`.
4. 해당 Google 계정이 Search Console의 정확한 `https://youdozi.github.io/` URL-prefix 속성에 접근할 수 있는지 확인합니다. 아직 소유권을 확인하지 않았다면 기존 HTML 확인 파일을 사용합니다.
5. 아래 명령을 실행하고 열린 브라우저에서 로그인·동의합니다.

```sh
python3 -m venv .venv-search-console
.venv-search-console/bin/pip install -r scripts/requirements-search-console.txt
.venv-search-console/bin/python scripts/search_console.py \
  --client "$HOME/.config/youdozi-search-console/oauth-client.json"
```

인증에는 `https://www.googleapis.com/auth/webmasters` 범위를 사용합니다. 토큰은 기본적으로 저장소 밖 `~/.config/youdozi-search-console/token.json`에 파일 권한 `0600`으로 저장합니다. 이후 같은 명령을 `--client` 없이 실행할 수 있고, `--status`를 붙이면 재제출 없이 상태만 조회합니다. 동의 화면이 테스트 상태인 앱은 재인증이 필요할 수 있습니다. 이미 발급된 접근 토큰을 쓰는 경우 `SEARCH_CONSOLE_ACCESS_TOKEN` 환경 변수도 지원합니다. 비밀키나 토큰을 커밋하거나 채팅에 붙이지 마세요.

제출 성공은 즉시 수집·색인되었다는 뜻이 아닙니다. `isPending`, `lastDownloaded`, `errors`와 Search Console 색인 보고서를 함께 확인하세요.

공식 문서: [사이트맵 제출 API](https://developers.google.com/webmaster-tools/v1/sitemaps/submit), [데스크톱 OAuth 인증](https://developers.google.com/identity/protocols/oauth2/native-app).

게시 JSON의 공통 검증, 당일 추가 후보 선택, RSS 갱신 및 `main` 보호 규칙은 [PIPELINE.md](PIPELINE.md)의 운영 항목을 참조하세요.

새 후보의 검토 카드에는 백엔드 관련성·선정 이유·원문 근거로 구성한 변경/대상/조건·사용자 편집 의견·직접 실험 여부를 표시합니다. 작성 필드와 검증 조건은 [PIPELINE.md](PIPELINE.md)의 후보 선정과 편집 형식 항목을 참조하세요.

핵심 한영 글20개와 과거 URL10개의 색인·검색 실적을 함께 추적하려면 [검색 성과 확인 절차](docs/search-growth.md)를 따릅니다. `python scripts/search_growth.py`는 목록 미리보기이며 `--live`에서만 읽기 전용 API 조회를 수행합니다. 결과는 저장소 밖 비공개 파일에 보관합니다.

## 검색 채널 확장과 IndexNow

검색엔진 등록은 서비스별 계정에서 진행합니다. 현재 사이트 주소는 `https://youdozi.github.io/`이며, Google Search Console의 기존 속성을 유지합니다.

- **Bing Webmaster Tools:** [도구](https://www.bing.com/webmasters/)에 로그인하고 `Google Search Console에서 가져오기`를 선택합니다. 해당 Google 계정에 대한 접근을 허용하고 `https://youdozi.github.io/`를 가져온 다음 사이트맵 등록 상태를 확인합니다. [공식 안내](https://www2.bing.com/webmasters/help/add-and-verify-site-12184f8b)
- **네이버 서치어드바이저:** [웹마스터 도구](https://searchadvisor.naver.com/console/board)에서 사이트를 선택하거나 추가하고 소유권을 확인합니다. 기존 `naver49bf2f26385c94a6a19f523f90c40d00.html`은 Astro에서도 같은 주소로 배포됩니다. 현재 로그인한 계정에 해당하는 확인 파일인지 확인한 뒤 `요청 → 사이트맵 제출`에 `https://youdozi.github.io/sitemap.xml`을 제출합니다. 한국어 RSS 주소는 `https://youdozi.github.io/ko/feed.xml`입니다. [공식 안내](https://searchadvisor.naver.com/guide/request-feed)

### 공개 변경 알림

IndexNow는 Bing·네이버 등 지원 검색엔진에 URL 변경을 알리는 별도 기능입니다. 도구 계정 등록이나 Google Search Console 제출을 대신하지 않습니다. HTTP 200/202 응답은 알림 수신이며 크롤링·색인·검색 순위를 보장하지 않습니다. [프로토콜](https://www.indexnow.org/documentation), [지원 엔드포인트 및 동작](https://www.indexnow.org/faq)

- `main`의 Pages 배포가 성공한 뒤에만 실행합니다. PR·`develop`·비공개 번역 초안은 전송하지 않습니다.
- 배포에 사용한 빌드 산출물의 사이트맵에 포함된 언어별 공개 경로만 읽습니다. 각 HTML의 자기 참조 canonical, `main`, noindex 및 리디렉션 여부를 확인합니다.
- 페이지 제목·설명·`main` 내용을 해시로 비교해 추가·수정된 URL과 이전에 알렸으나 삭제된 URL을 보냅니다. 헤더·푸터만 바뀐 경우는 변경으로 세지 않습니다.
- `public/indexnow-key.txt`는 프로토콜상 공개되는 소유권 확인 파일이며 배포 후 일치 여부를 먼저 확인합니다. Google OAuth JSON·토큰과는 별개이며 Google 인증 정보를 Actions에 올리지 않습니다.
- 알림이 수락된 뒤에만 상태를 갱신하고 Actions 캐시에 보관합니다. 제출 실패 시 기존 상태를 유지하여 다음 배포에서 다시 감지합니다. 캐시가 없거나 만료되면 현재 공개 URL 전체를 초기 목록으로 알립니다.
- 알림 준비·전송·캐시 저장 오류는 이미 성공한 Pages 배포를 취소하지 않습니다. Actions의 IndexNow 단계에서 결과를 확인합니다. 알림 실패 또는 건너뜀을 정상 제출로 해석하지 않습니다.
- 자동 알림을 다시 시도하려면 `Site Quality Gates and Pages` 워크플로의 `Run workflow`에서 **main**을 선택합니다. 품질 검사와 재배포를 거쳐 같은 절차로 재시도합니다.

로컬 미리보기는 네트워크 호출이나 상태 저장을 하지 않습니다.

```sh
npm run build
npm run preview:indexnow

# 배포된 키와 공개 상태가 준비됐을 때 명시적으로 제출
python3 -B scripts/indexnow.py --submit
```

로컬 상태 파일 `.pipeline/indexnow-state.json`은 커밋하지 않습니다. 로컬 제출과 Actions는 각자 마지막 수락 상태를 관리하므로, 새 환경에서 처음 제출하면 공개 목록 전체를 다시 알릴 수 있습니다. 한 번에 최대 10,000 URL을 허용하며 초과하면 제출 전에 실패합니다.

## 공개 본문과 내부 검토 기록

공개 글은 본문·소식 기준일·출처 중심으로 표시합니다. 원문 검토 배너, 비어 있는 후속 확인, 편집 제안, 주장별 감사 기록은 공개 HTML·RSS·검색 인덱스에서 제외합니다. 기존 Markdown의 반복 수집 기준·활용 가이드·검토 기록도 빌드 시 제거합니다. 기술적 정정·실제 후속 사실·코드·출처는 유지하며 원본 콘텐츠와 승인·근거 데이터는 저장소에 보존합니다. 내용 정리는 `src/lib/reader-markdown.ts`와 공통 글 컴포넌트가 담당합니다. 빌드의 [공개 본문 검사](docs/public-reader-content.md)는 글 HTML·검색 인덱스·RSS에 알려진 내부 항목이 남으면 배포 전에 실패합니다.

스페인어 `es`의 UI·스키마·SEO·IndexNow 처리를 지원합니다. 현재 다른 번역 언어로 공개된 6개 글의 스페인어 초안을 [검토 문서](.pipeline/translations/reviews/spanish-001.md)에 준비했습니다. 사용자의 게시 승인에 따라 실제 스페인어 게시 파일 6개를 추가했으며, 배포 시 스페인어 경로·언어 메뉴·검색·RSS·사이트맵이 활성화됩니다. 다른 번역 초안은 승인 후 게시 절차를 유지합니다.

보안·CI 주제의 스페인어 12편은 [두 번째 검토 문서](.pipeline/translations/reviews/spanish-002.md)에 준비했습니다. 해당 12편은 자체 AI 대조·교정과 격리된 렌더링 검사를 거쳤으며 게시 승인은 대기 상태입니다. 당시 Buildkite 원문 재조회 실패는 기록에 보존하며 후속 공식 근거 대조는 아래 통합 목록을 따릅니다. [공개 후보 목록](.pipeline/translations/releases/spanish-002.json)은 당시의 검토 자료이며 공개 번역 파일은 추가하지 않았습니다.

인프라·프레임워크 보안 주제의 스페인어 15편은 [세 번째 검토 문서](.pipeline/translations/reviews/spanish-003.md)에 추가했습니다. 해당 15편은 근거 문서 17개 재조회·자체 AI 번역 검토·격리된 렌더링 검사를 거쳤으며, [게시 후보 목록](.pipeline/translations/releases/spanish-003.json)에 승인을 기다리는 정확한 원고를 기록했습니다.

모델·요금·시험 제공 범위·설계 사례 등 나머지 26편은 [네 번째 검토 문서](.pipeline/translations/reviews/spanish-004.md)에 준비했습니다. 스페인어 59/59편, 전체 6개 번역 언어 354/354건의 준비를 마쳤습니다. 이는 게시 완료나 모든 언어의 현재 외부 사실 재검증을 뜻하지 않습니다. 병합된 PR #78에 스페인어 미게시 후보 53편의 게시 전 검사를 포함했으며, 실제 공개 번역은 기존 36편입니다. [개별 후보 목록](.pipeline/translations/releases/spanish-004.json)은 실행 입력이나 승인 기록이 아닙니다.

[통합 게시 전 목록](.pipeline/translations/reviews/spanish-full-031.md)은 53편의 원고·원문·검토·근거 파일 해시를 고정합니다. Buildkite의 기존 주소는 복구되지 않았지만 별도 공식 변경 기록 2개로 같은 주장을 추가 검증했습니다. `npm run check:translation-release`는 파일 변경·미해결 검토·근거 누락을 검사하며 일반 검사와 빌드에도 포함됩니다. 게시 준비 CLI는 raw `--batch` 대신 검사된 `--release` 목록과 실제 사용자 승인을 기록하는 인자를 요구합니다. 검사 통과를 승인으로 간주하지 않으며 자동 병합·배포를 추가하지 않습니다.

한영 Spring Boot 카테고리는 프로젝트 생성·영속성·테스트·패키징 순서의 학습 안내를 제공합니다. 실제 공개 가능한 글만 연결하고 각 글의 재현 버전을 구분합니다. 안내의 목록·언어 링크·사이트맵·구조화 데이터는 같은 글 집합을 사용합니다.

Ruby 아카이브 예제는 `python3 -B scripts/check_ruby_environment_examples.py`로 한영 전체 파일을 추출해 비교합니다. Ruby3.2.2에서 설치된 gem으로 임시 번들을 해결하고 두 페이지 렌더링·C++17 출력·잘못된 컴파일러의 실패를 확인합니다. CI의 `--install`은 임시 저장소에 과거 번들을 설치합니다. Ruby3.2는 지원 종료된 재현 환경이며 현재 Astro 빌드나 신규 환경 권장 버전이 아닙니다. macOS SDK 플래그 검사는 로컬에서, 기본 C++ 호출은 Linux CI에서 구분해 확인합니다.
Jenkins 예제는 `python3 -B scripts/check_jenkins_examples.py`로 한영 전체 Python 파일을 추출해 실행합니다. 실행 중인 Linux 컨테이너 Docker 엔진이 필요합니다. 이미지를 digest로 고정한 일회용 컨트롤러에서 재생성·정지 백업·master.key 분리·새 볼륨 복구를 검사하고 생성 자원을 삭제합니다. 암호와 백업은 로그나 CI 산출물로 남기지 않습니다. 전체 운영 복구나 작업 실행을 입증하는 검사는 아닙니다. [CI 진단 문서](docs/jenkins-ci-diagnostics.md)는 기동 실패 시 수집하는 제한된 상태 값과 판정 범위를 설명합니다.

한영 `/en/guides/`·`/ko/guides/`에서 Java 문제 풀이·Spring Boot·셸 자동화·JDK·개발 도구·게시 절차·Jenkins 복구·Ruby 환경 진단의 8개 학습 안내를 찾을 수 있습니다. 안내는 실제 공개 가능한 글만 연결하며 본문 카테고리 링크로 돌아올 수 있습니다. 가이드 목록·언어 링크·CollectionPage/ItemList·사이트맵은 같은 등록 정보를 사용합니다. 이 안내는 기존 글을 연결하며 코드의 새 실행 결과나 검색 노출 성과를 주장하지 않습니다. 8개 분야의 안내 문구는 중국어 간체·일본어·독일어·프랑스어·러시아어·스페인어로도 준비했습니다. 해당 언어에 실제 게시된 기술 글이 있는 분야에만 안내와 읽기 경로를 생성하며, 번역 준비 상태와 공개 상태는 구분합니다.

한영 `/en/about/`·`/ko/about/`는 운영 계정·글 작성 원칙·정정 방법을 안내합니다. 글의 작성자 링크와 Person/ProfilePage 식별자를 연결하며, 별도 소개가 없는 언어는 영문 소개로 연결합니다. 소개 문구에는 확인된 정보만 사용하고 소속·경력·자격을 추정해 추가하지 않습니다.

댓글은 독자가 버튼을 누른 뒤 Utterances를 불러옵니다. 기존 `legacyUrl || translationKey` 댓글 식별자와 테마를 유지하고, 로그인 복귀 주소에서는 인증 흐름을 이어서 엽니다. 실패·시간 초과·JavaScript 비활성화 시에는 같은 식별자로 검색하는 GitHub 링크를 제공합니다. 이 변경의 검증 지표는 초기 댓글 스크립트 요청 유무이며 실제 Core Web Vitals 개선 수치를 주장하지 않습니다.

본문에 큰 절이4개 이상인 Markdown 글은 실제 렌더링된 제목으로 접고 펼칠 수 있는 목차를 만듭니다. 발행일과 실제로 더 늦은 수정일을 각 언어로 구분해 표시하며, 표시를 위해 원고 날짜를 새로 만들지 않습니다.

`npm run build`는 `scripts/check_seo.py`로 생성 HTML 전체의 언어 대체 링크와 사이트맵을 대조합니다. `hreflang`의 자기 참조·양방향 연결·대상 언어·중복·절대 URL을 검사하고, 대상이 실제 자기 canonical 페이지이며 `noindex`나 리디렉션이 아닌지 확인합니다. 사이트 정책상 영문 대응 페이지가 있으면 `x-default`도 그 주소여야 합니다. 사이트맵에 언어 대체 링크가 있으면 HTML과 일치해야 하며, 모든 사이트맵 URL이 공개 대상인지 검사합니다. 글이 없는 언어별 목록은 `noindex`를 유지하고 대체 언어 집합에서 제외합니다. 정적 검증은 검색엔진의 실제 색인·노출 여부를 판정하지 않습니다.

사이트 검색은 현재 언어의 정적 색인을 첫 검색 때만 받아 브라우저에서 처리합니다. 제목·주제·요약·본문 순으로 일치를 평가하며 모든 검색어가 포함된 글 중 최대 50개를 표시하고 전체 결과 수도 안내합니다. 같은 점수에서는 기존 색인 순서를 유지합니다. 유니코드 정규화와 라틴 문자 악센트 생략 검색을 지원하되 일본어 탁점과 키릴 문자의 구별은 유지합니다. 한중일 입력기의 조합 완료를 기다리고, 늦은 응답이 새 검색·입력 지우기를 덮어쓰지 않게 합니다. 실패하면 같은 검색어로 재시도할 수 있습니다. 검색어를 URL·서버 검색 API·브라우저 저장소로 보내거나 저장하는 기능은 추가하지 않습니다. 이 변경은 사이트 내부 검색이며 외부 검색엔진 순위 개선을 측정한 결과가 아닙니다.

글의 Open Graph 발행일·수정일·작성자 정보는 JSON-LD와 같은 기록에서 만듭니다. `og:locale:alternate`는 실제 언어 대체 링크에 있는 번역본만 나열합니다. `scripts/check_metadata.py`가 공개 대상 페이지의 JSON-LD·공유 태그·화면 제목·날짜를 대조하며, 원고 날짜를 새로 만들거나 공유 플랫폼의 미리보기·검색 순위를 보장하지 않습니다. JSON-LD의 기존 HTML 안전 직렬화는 보존하고 특수문자·스크립트 종료 문자열의 값 보존을 회귀 검사합니다.

Google·Bing의 공개 글 상태는 `scripts/search_engines.py`로 함께 관측할 수 있습니다. 현재 핵심 글·과거 주소·8개 언어 공개 다이제스트·홈·아카이브 94 URL을 대상으로 저장 색인 상태와 크롤링 기록을 구분합니다. 기본 실행은 미리보기이며, 실제 API 조회는 `--live`, 저장된 비공개 결과 읽기는 `--report`를 사용합니다. [사용 방법과 판정 범위](docs/search-growth.md#googlebing-다국어-공개-글-관측)를 참고하세요. 미게시 번역·자동 게시·검색엔진 제출은 포함하지 않습니다.

[5개 언어 통합 검토 목록](.pipeline/translations/reviews/multilingual-full-032.md)은 중국어 간체·일본어·독일어·프랑스어·러시아어의 미게시 원고 각 53편, 총 265편을 같은 게시 전 검사에 연결합니다. 스페인어 53편과 합한 318편이 승인 대기입니다. [격리 번역 검사](docs/translation-preview.md)는 이 원고를 임시 복사본에서만 빌드해 공개 본문 차단·검색·RSS·언어 연결을 확인합니다. `npm run check:translation-preview`로 수동 실행할 수 있으며 실제 승인·게시 파일과 배포 산출물은 바꾸지 않습니다. [오프라인 번역 검토 파일](docs/translation-review.md)은 영어 기준문·번역문·저장된 근거를 나란히 확인하도록 생성할 수 있습니다. `npm run check:translation-review`는 파일 쓰기 없이 대상만 확인하며, HTML을 생성하려면 저장소 밖 새 `--output` 경로를 지정합니다. 이 가운데 50편은 현재 영어 기준본과 새로 자체 AI 대조·대상 언어 교정을 수행했고, 215편은 현재 파일 해시를 포함하는 기존 AI 검토를 재사용합니다. 동일한 53개 기준 원문에 대한 기존 출처 관측과 Buildkite 보완 근거를 재사용하며 실시간 재조회로 기록하지 않습니다. 기존 공개 번역은 36편입니다.

사이트 탐색은 [전체 글 탐색 문서](docs/site-discovery.md)를 따릅니다. 8개 언어의 연도별 전체 글 목록, 실제 내용에 맞는 공통 메뉴, 번역이 없는 언어 전환과 빈 목록·404의 복구 경로를 함께 관리합니다. 빌드에서 사이트맵 URL의 언어별 도달 가능성과 모든 글의 최대 두 번 링크 이동을 검사하며, 이 수치를 실제 크롤링·색인 결과로 해석하지 않습니다.

기술 글의 코드 블록은 JavaScript가 활성화되면 키보드로 초점을 옮겨 가로 스크롤할 수 있습니다. Clipboard API가 있는 환경에서는 사용자가 버튼을 누를 때만 코드 텍스트를 그대로 복사하고, 성공·실패를 현재 언어로 알립니다. 들여쓰기·빈 줄·명령 프롬프트를 바꾸거나 코드를 실행하지 않으며, API가 없거나 복사가 거부되어도 원래 코드를 직접 선택할 수 있습니다. 안내 문구는 8개 언어를 지원합니다.

한영 기술 글 94편은 기존 학습 안내의 핵심 순서대로 이전·다음 글을 이어 읽을 수 있습니다. 안내로 돌아가는 링크와 현재 위치를 함께 제공하며 뉴스·추가 목록·미게시 원고를 순서에 넣지 않습니다. [기술 글 읽기 경로](docs/site-discovery.md#기술-글의-읽기-경로)는 일반·격리 빌드에서 안내의 실제 목록과 대조합니다.

Markdown 본문의 `/assets/` 이미지는 빌드 시 로컬 파일에서 가로·세로 크기를 읽어 공간을 미리 확보합니다. 첫 이미지는 기본 `eager`, 뒤의 이미지는 `lazy`, 디코딩은 `async`로 지정하며 기존 속성은 유지합니다. 원격 이미지를 조회하거나 파일·대체 텍스트를 변경하지 않습니다. 직접 작성한 HTML 이미지에는 작성자가 크기·로딩 속성을 지정해야 합니다. 일반 빌드와 격리 번역 빌드에서 본문 이미지의 크기·로딩 속성과 SVG 비율을 검사합니다. 이 검사는 실제 Core Web Vitals나 검색 순위 측정이 아닙니다.

검색 실적과 급증한 GA 방문을 구분하려면 [측정 구간·검증 방문 분리 절차](docs/search-growth.md#트래픽-급증-조사와-검증-방문-분리)를 사용합니다. GSC의 PT 날짜를 GA 속성 시간대로 맞춰 읽고, 원본·검토 페이지·명시적 의심 규칙을 별도 조회합니다. 결과와 규칙은 저장소 밖 비공개 파일로 보관하며 원본 데이터나 GA 설정을 변경하지 않습니다. 자동 브라우저 검사는 `scripts/browser/isolated-context.mjs`를 공통 사용하고 `npm run check:browser-isolation`로 GA 전송 차단을 실제 Chrome에서 확인합니다.

홈·글·다이제스트·태그·일반 카테고리의 목록은 현재 페이지에 보이는 글 카드와 같은 배열로 `CollectionPage`·`ItemList`를 생성합니다. 각 페이지의 canonical·언어·제목·설명과 카드의 이름·주소·순서를 연결하며, 목록의 수와 위치는 해당 페이지 기준입니다. 추천 링크와 다른 페이지의 카드를 섞지 않고 빈 목록은 `noindex`와 구조화 데이터 생략을 유지합니다. 일반 빌드와 격리 번역 빌드에서 생성 HTML 전체를 대조합니다. 형식은 [Schema.org ItemList](https://schema.org/ItemList)와 [Google의 공개 내용 일치 원칙](https://developers.google.com/search/docs/appearance/structured-data/sd-policies)을 참고하며 검색 노출이나 리치 결과를 보장하지 않습니다.

공개 게시글의 과거 주소는 `noindex` 없이 즉시 이동과 목적지 canonical을 제공합니다. 루트·목록·예제 이동은 기존 제외 정책을 유지합니다. [게시글 이동 검사](docs/search-growth.md#게시글-이동-신호와-빌드-검사)는 일반·격리 빌드의 전체 이동 경로와 핵심 글 10쌍을 검사하며, 이동 체인·잘못된 목적지·과거 주소로 남은 공개 링크를 차단합니다. 실제 Google 색인 전환은 별도로 관측합니다.

[주제별 주소 전환 보고서](docs/search-growth.md#주제별-주소-전환-보고서)는 저장된 스냅샷에서 핵심 글의 영문·한글·과거 주소를 함께 읽습니다. 실제 배포 완료 시각과 마지막 크롤링을 대조하고, 색인 판정·Google 대표 주소·URL별 검색 실적을 분리합니다. 인증·API 호출 없이 실행하며 판정·canonical 누락을 색인 해제나 대표 주소 변경으로 세지 않습니다.

[공개 크롤링 접근성 관측](docs/search-growth.md#공개-응답의-크롤링-접근성)은 관측 URL 94개의 HTTP 상태·콘텐츠 형식·색인 지시문·사이트맵·다국어 상호 링크를 대조합니다. 기본은 미리보기이며, 일반 HTTP 검사 통과와 실제 Google/Bing 색인·노출을 구분합니다. 조건부 규칙이나 확인하지 못한 항목은 미확인으로 남깁니다.

[기술 글의 6개 언어 번역](docs/technical-translations.md)은 기존 뉴스 번역과 별도로 준비합니다. 총 48개 주제·288편 중 Java 문제 풀이 10개 주제 60편·셸 자동화 3개 주제 18편·개발 도구 3개 주제 18편, JDK 3개 주제 18편·YAML 1개 주제 6편까지 기존 120편에 최근 보안·JDK·HTTP 12개 주제의 72편을 더해 합계 192편의 완전 번역과 현지화한 흐름도를 사이트 미게시 초안으로 준비했습니다. 남은 번역은 96편입니다. `npm run check:technical-translations`로 등록된 묶음의 원문·코드·수치·표·링크·그림을 대조하고, `npm run review:technical-translations -- --output <저장소 밖 새 HTML>`로 원문과 번역문을 함께 볼 수 있습니다. `--manifest`로 특정 묶음을 선택할 수 있으며 승인 해시는 묶음마다 구분합니다. [기술 글 게시 경로·승인 준비](docs/technical-publication.md)는 정확한 묶음과 사용자 승인 정보가 있어야 실행하며 실제 원고의 게시 승인은 남아 있습니다. `npm run check:technical-preview`는 뉴스 318편과 기술 원고 192편을 격리된 임시 빌드에서 함께 검사합니다. 검색 데이터는 비교 연산자와 코드 블록을 HTML 태그로 잘못 제거하지 않도록 보존합니다.


## 질문 중심 기술 글과 AEO 측정

관측 그룹은 기본 한영 10 URL(`technical-answers-059`)과 SHA-256 후속 글 2 URL(`checksum-guide-066`)로 분리합니다. `python3 -B scripts/answer_observation.py --cohort checksum-guide-066 --index-only`로 인증 없이 계획을 확인하며 `--live --output <저장소 밖 새 JSON>`에서만 저장 색인 API를 조회합니다. 색인 전용 모드는 GSC 검색 실적·GA4를 수집하지 않습니다. [그룹 선택·날짜 범위·결과 해석](docs/search-growth.md#aeo-관측-그룹과-색인-전용-조회)을 따릅니다. 실제 API 조회와 저장 응답 재생은 구분하고, 발행일이 관측 구간 안이거나 이후인 경우와 발행일 기록이 없는 과거 보고서에서는 성과 증감을 만들지 않습니다.

[첫 적용 목록](content/seo/answer-pilot.json)은 Spring Boot 이관·Querydsl·WebClient·YAML·JDK 21의 5개 주제, 영어·한국어 10개 URL입니다. 실제 검색량으로 순위를 정한 목록이 아니라 편집 실험입니다. 도입부에서 답과 적용 조건을 밝히고 공식 근거를 가까이 연결합니다. 기존 코드·그림·URL·발행일을 유지하며, 질문형 소제목으로 바꾼 위치에는 이전 문단 ID도 남깁니다. 첫 문단에 실제로 연결된 출처만 기존 `BlogPosting.citation`에 넣습니다. 별도 FAQ나 내부 검토 카드를 본문에 일괄 추가하지 않습니다.

`answer_observation.py`는 현재 OAuth와 GA4 읽기 권한으로 대상 페이지의 GSC Web 검색·현재 URL 검사·GA4 랜딩 페이지별 유입 출처를 수집합니다. 기본 실행은 계획 출력이며 API 호출·파일 쓰기가 없습니다. 실제 수집은 기존 [Google 인증 절차](#search-console-사이트맵-제출)와 Python 의존성 설치 후 실행합니다. 원시 검색어·Analytics 자료는 모든 저장소 worktree 밖의 새 파일에만 저장하며 권한은 600입니다. 기존 파일을 덮어쓰지 않습니다.

```sh
python3 scripts/answer_observation.py
python3 scripts/answer_observation.py --live \
  --output ~/.config/youdozi-search-console/aeo-baseline-new.json
python3 scripts/answer_observation.py --report \
  ~/.config/youdozi-search-console/aeo-baseline-new.json
```

기본 구간은 최근 PT 달력일 3일을 제외한 28일이며 GSC에는 확정 자료를 요청합니다. GA4는 속성 시간대, GSC는 PT를 사용합니다. 같은 날짜 문자열이 같은 UTC 구간을 뜻하지 않으므로 클릭과 세션을 직접 나눠 비율을 만들지 않습니다. URL 검사는 수집 시점의 상태이며 과거 28일의 색인 이력이 아닙니다. 대상 URL이 기준 구간 전체에 존재했는지도 따로 해석해야 합니다.

2026-10-30의 변경 전 실측에서는 대상 10개 모두 URL 검사 HTTP 200·NEUTRAL로 아직 Google에 알려지지 않은 URL이었고, 2026-09-29~2026-10-26의 대상 페이지 Web 검색과 GA4 응답에는 행이 없었습니다. 이는 사이트 전체의 노출·방문 0이나 AI 인용 0을 의미하지 않습니다. 이 기준선으로부터 단기 AEO 효과를 입증하지 않습니다. 실제 원시 보고서는 저장소 밖에 보관합니다.

아래는 후속 실행 형식의 **예시**입니다. 배포 시각은 실제 Pages 배포 시각으로 바꾸고 그 시각의 PT 날짜와 GA4 속성 시간대의 날짜를 모두 지난 날부터 28일을 선택합니다. 서울 시간에 배포했다면 PT의 다음 날도 아직 서울의 배포 당일일 수 있습니다. 구간 종료 후에도 최신 PT 3일 제외 조건을 충족해야 합니다. 두 시간대의 배포 당일·기준선 중복·서로 다른 URL 집합은 거부합니다. GA4 시간대가 미제공이면 전체 게시 경계를 검증했다고 표시하지 않으며 속성 시간대가 바뀌면 비교를 거부합니다. 지금 미래 구간을 조회하면 API 호출 전에 중단됩니다.

```sh
python3 scripts/answer_observation.py --live \
  --compare ~/.config/youdozi-search-console/aeo-baseline-new.json \
  --changed-at 2026-10-30T12:00:00+09:00 \
  --start 2026-10-31 --end 2026-11-27 \
  --output ~/.config/youdozi-search-console/aeo-followup-new.json
```

후속 보고서는 같은 URL의 Web 검색 수치·GA4 유입 집계를 나란히 보존합니다. 미반환·실패·조회 상한 도달을 0으로 채우지 않습니다. 검색어 목록은 완전한 목록이 아니며 GA4 응답의 임계처리·샘플링 관련 메타데이터도 보존합니다. AI 도메인과 일치하는 `sessionSource`는 관측된 기여 출처 이름일 뿐 실제 AI 추천·인용·사람의 방문을 입증하지 않습니다. robots·Analytics 설정을 바꾸거나 색인·사이트맵을 제출하지 않습니다. 비교 결과는 관찰이며 인과 효과가 아닙니다.

Google에는 [Search generative AI 포함 설정](https://support.google.com/webmasters/answer/16908024?hl=en)과 [전용 생성형 AI 성과 보고서](https://support.google.com/webmasters/answer/16984139?hl=en)가 있습니다. 전용 보고서가 보이지 않는 경우 노출 부족이나 제외 설정일 수 있습니다. 현재 계정 설정과 전용 보고서를 이 수집기로 확인했다고 표시하지 않습니다. [공식 Search Analytics API](https://developers.google.com/webmaster-tools/v1/searchanalytics/query)의 Web 자료와 구분해 `not-collected`로 남깁니다. Bing의 [AI Performance](https://www.bing.com/webmasters/help/ai-performance-9f8e7d6c)도 대시보드에서 별도로 확인하며 문서화되지 않은 AI API를 호출하지 않습니다. 엔진의 AI 노출·인용, GSC Web 검색, GA4 방문은 서로 다른 관측값입니다.

다운로드 파일 검증 예제는 `python3 -B scripts/check_checksum_examples.py`로 실행합니다. 실제 예제 ZIP의 한영 코드가 동일한지 대조하고, 정상·변경·빈 파일·읽기 오류·입력 형식·청크 경계를 로컬 바이트로 검사합니다. 파일 다운로드·설치·서명 검증은 수행하지 않습니다.

WebClient 시간 제한·재시도 후속 예제는 `python3 -B scripts/check_webclient_retry_example.py`로 실제 한영 ZIP 코드를 실행합니다. 로컬 HTTP 7개·가상 시간 2개 테스트로 503 재시도 횟수, 다른 상태·타임아웃의 즉시 오류, 시도별·전체 제한의 연산자 순서를 확인합니다. TCP 연결 타임아웃과 운영 정책은 이 검사로 검증하지 않습니다.

PHP2Shell·Node2Shell 글은 런타임 보안 안내에서 연결합니다. `python3 -B scripts/check_runtime_evidence_examples.py`는 원고에서 추출한 ZIP 수집기를 고정된 공식 PHP·Node 컨테이너에서 실행합니다. 현재 프로세스 JSON·CLI 설정 범위·PHP 웹 정보 차단을 확인하며 취약점 악용이나 운영 서버 패치를 수행하지 않습니다.

GitLab 수정 기준 비교와 JDK 기본 JSSE 목록은 `python3 -B scripts/check_gitlab_jdk_examples.py`로 원고의 실제 ZIP 코드를 실행합니다. GitLab 서버·운영 JDK는 변경하지 않으며, 버전 경계와 임시 합성 CA 저장소를 검사합니다. 실행 성공은 실제 배포·외부 TLS 거부·침해 부재의 증거가 아닙니다.

Valhalla 예제는 `python3 -B scripts/check_valhalla_example.py --download-jdk`로 고정된 공식 JDK 28 EA를 임시 디렉터리에 다운로드·SHA-256 검증한 뒤 원고에서 만든 ZIP 코드를 실행합니다. 기존 JDK 설정은 바꾸지 않으며 컴파일·실행 미리보기 플래그와 언어 제약도 확인합니다. 로컬 JDK를 쓰려면 `--jdk <JDK 28 홈>`을 지정합니다.

JDK 25 ScopedValue 예제는 `python3 -B scripts/check_scopedvalue_example.py --jdk <JDK 25 홈>`으로 원고에서 생성한 ZIP을 미리보기 옵션 없이 컴파일·실행합니다. 별도 API 계약 검사는 동시 바인딩 격리·예외 복원·작업 스레드 재사용·null 경계를 대조하며 프레임워크나 구조적 동시성 연동 검증과 구분합니다.

가상 스레드의 JDK 21·25 비교는 각 JDK에서 `python3 -B scripts/check_virtual_thread_example.py --jdk <JDK 홈>`으로 실제 ZIP을 실행합니다. 모니터 안팎 대기의 JFR 파일을 CLI JSON과 대조하고 기존 파일 보호·인수 오류를 확인합니다. 이벤트 관측이며 성능 벤치마크는 아닙니다.

10k RPS 아키텍처 글의 입장 제어 예제는 `python3 -B scripts/check_admission_example.py --jdk <JDK 27 홈>`으로 실제 ZIP과 별도 게이트 계약을 실행합니다. 10,000 RPS 부하 시험이나 인프라 배포를 수행하지 않습니다. 참조 구성의 편집 가능한 SVG 원본은 `assets/img/architecture/`에 있습니다.

WebClient·RestClient 비교는 `python3 -B scripts/check_http_client_comparison.py`로 실제 한영 ZIP의 콘솔 예제를 실행합니다. JDK 17·Gradle 8.4에서 로컬 HTTP 7요청과 종료 연산·구독·404/503 처리를 확인하며, 최초 Maven Central 다운로드가 필요합니다. 성능 비교나 타임아웃·TLS 검증은 아닙니다.

게시글별 공유 카드는 선택적인 `socialImage`(로컬 PNG 경로·현지화한 alt·1200×630 크기)로 지정합니다. Open Graph·Twitter 대형 카드·BlogPosting 이미지가 같은 주소를 사용하며, 지정하지 않은 페이지는 기존 프로필 카드로 표시합니다. WebClient·RestClient 카드의 원본은 `assets/img/social/webclient-restclient-{en,ko}.svg`이며 `node scripts/render_client_social_images.mjs`로 PNG를 다시 만듭니다. Chrome과 설치된 Playwright가 필요하며 외부 이미지 요청은 없습니다. 빌드 검사는 메타데이터 일치·대체 텍스트·로컬 PNG 헤더 크기를 확인하고 실제 플랫폼의 공유 캐시나 카드 표시를 보장하지 않습니다.

Fragnesia 글의 읽기 전용 커널 증거 수집기는 `python3 -B scripts/check_fragnesia_example.py`로 실제 한영 ZIP 코드를 합성 OS·패키지 응답에 연결해 검사합니다. Linux 운영 호스트의 취약성·패치 적용·재부팅·컨테이너 탈출을 검증하지 않습니다.

Fragnesia 공유 카드의 한영 SVG는 `node scripts/render_client_social_images.mjs fragnesia-cve-2026-46300`으로 1200×630 PNG를 다시 생성합니다.
