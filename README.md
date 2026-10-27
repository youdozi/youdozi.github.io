# youdozi's memory

Astro로 생성하고 GitHub Pages에 배포하는 기술 블로그입니다. 영문을 기본 언어로 사용하며 한국어 아카이브를 함께 제공합니다. Python RSS 수집·근거 검증을 유지하고 새 다이제스트는 두 언어의 구조화된 JSON으로 발행합니다.

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

기존 글 230개는 한국어로 보존했습니다. 이 중 테스트 데이터로 확인된 1편은 실제 뉴스 목록·검색·RSS에서 제외하고 예제 페이지로 남겼습니다. 핵심 개발 글 32편의 영문판이 준비돼 있으며, 새 원고·영문·한국어 다이제스트는 원고 검토와 게시 승인 후 공개합니다. 번역되지 않은 한국어 글을 영문 페이지로 복제하지 않습니다.

## 콘텐츠 작성

기술 글의 새 작성·본문 보강에는 **흐름 그림과 대응하는 코드 예제를 함께 포함**합니다. 그림·코드·설명의 순서와 분기를 대조하고, 실제 렌더링·모바일 가독성·코드 실행을 확인합니다. 자세한 기준은 [기술 글 작성 기준](docs/technical-writing.md)과 [저장소 작업 규칙](AGENTS.md)을 따릅니다. 현재 한영 기술 글 32개 주제의 흐름도 64개를 준비했으며 공통 자산 준비 단계에서 생성합니다. 알고리즘은 전체 Java 클래스, Spring·빌드·JDK·셸·유틸리티 글은 각 그림에 등록한 코드 언어와 핵심 구문을 검사합니다.

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

공개 글은 본문·소식 기준일·출처 중심으로 표시합니다. 원문 검토 배너, 비어 있는 후속 확인, 편집 제안, 주장별 감사 기록은 공개 HTML·RSS·검색 인덱스에서 제외합니다. 기존 Markdown의 반복 수집 기준·활용 가이드·검토 기록도 빌드 시 제거합니다. 기술적 정정·실제 후속 사실·코드·출처는 유지하며 원본 콘텐츠와 승인·근거 데이터는 저장소에 보존합니다. 내용 정리는 `src/lib/reader-markdown.ts`와 공통 글 컴포넌트가 담당합니다.

스페인어 `es`의 UI·스키마·SEO·IndexNow 처리를 지원합니다. 현재 다른 번역 언어로 공개된 6개 글의 스페인어 초안을 [검토 문서](.pipeline/translations/reviews/spanish-001.md)에 준비했습니다. 사용자의 게시 승인에 따라 실제 스페인어 게시 파일 6개를 추가했으며, 배포 시 스페인어 경로·언어 메뉴·검색·RSS·사이트맵이 활성화됩니다. 다른 번역 초안은 승인 후 게시 절차를 유지합니다.

한영 Spring Boot 카테고리는 프로젝트 생성·영속성·테스트·패키징 순서의 학습 안내를 제공합니다. 실제 공개 가능한 글만 연결하고 각 글의 재현 버전을 구분합니다. 안내의 목록·언어 링크·사이트맵·구조화 데이터는 같은 글 집합을 사용합니다.
