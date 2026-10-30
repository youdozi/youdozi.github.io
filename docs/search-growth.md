# 핵심 글 검색 성과 확인

## 첫 방문의 언어 선택

첫 주소 `/`에서만 저장된 직접 선택 → 브라우저의 `navigator.languages` 순서 → 영어를 적용합니다. 실제 공개 언어만 선택하며 `ko-KR`, `fr-CA`, `es-419` 등은 대응 언어판으로 연결합니다. `zh`, `zh-CN`, `zh-SG`, `zh-Hans`는 간체로 연결하지만 `zh-Hant`, `zh-TW`, `zh-HK`, `zh-MO`는 다음 선호 언어나 영어로 넘어갑니다. 명시적인 `Hans` 스크립트가 지역보다 우선합니다.

언어 메뉴에서 직접 선택하면 `localStorage`의 `youdozi.language`에 언어 코드만 저장합니다. 현재 언어도 선택할 수 있으며 검색어·URL 조각을 유지합니다. 지역·IP·로그인 정보는 조회하지 않습니다. 저장소 사용이 차단되면 방문 중 전환은 계속 동작하지만 다음 첫 주소 방문은 브라우저 언어를 다시 따릅니다. 브라우저 사이트 데이터를 지우면 저장된 선택도 해제됩니다. 자동으로 감지한 언어는 저장된 직접 선택으로 기록하지 않습니다.

언어가 지정된 홈·검색·글 주소와 과거 글 이동에는 자동 선택을 적용하지 않습니다. 첫 주소는 `location.replace()`로 이동해 뒤로 가기 순환을 피하고 검색 매개변수·조각을 전달합니다. JavaScript가 꺼져 있으면 기존처럼 영어로 이동하며, 스크립트만 로딩 실패한 경우 화면의 8개 언어 링크로 이동할 수 있습니다. 첫 주소의 영어 canonical·`noindex,follow`·사이트맵 제외와 기존 언어판의 canonical·hreflang·영어 x-default를 유지합니다. [Google 다국어 사이트 지침](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites), [브라우저 언어](https://html.spec.whatwg.org/multipage/system-state.html#dom-navigator-languages), [브라우저 저장소](https://html.spec.whatwg.org/multipage/webstorage.html#dom-localstorage-dev)

일반 빌드 후 `node scripts/check_language_preference.mjs`로 자동 선택·수동 선택 저장·명시적 글 주소 유지·번역 글 연결·선호 언어 순서·번체 처리·저장소 차단·JavaScript 비활성화·스크립트 실패·뒤로 가기를 실제 Chrome에서 검사합니다. 운영 검사는 `--url https://youdozi.github.io/`를 추가합니다. 두 모드 모두 GA 전송을 차단하며 필수 CI에도 같은 검사를 적용합니다.

## 사이트 안에서 검색 결과 다시 열기

8개 언어의 검색 페이지는 `/{언어}/search/?q={검색어}` 주소로 결과를 다시 엽니다. 예를 들어 `/en/search/?q=WebClient`를 공유하거나 새로고침해도 검색어와 결과를 복원하며, 결과 글을 읽고 뒤로 돌아온 경우도 처리합니다. 입력은 잠시 모아 현재 기록을 교체하므로 글자마다 뒤로 가기 기록을 추가하지 않습니다. 검색어를 지우면 `q`도 제거합니다. 한글 등 조합 중인 입력은 조합 완료 후 반영합니다.

검색 페이지의 `noindex,follow`와 검색어 없는 canonical, 사이트맵 제외를 유지합니다. 이 변경은 사이트 내부 탐색의 개선이며 Google·Bing 노출 증가를 증명하지 않습니다. URL 처리는 [HTML History API](https://html.spec.whatwg.org/multipage/nav-history-apis.html#dom-history-replacestate-dev)를 사용합니다.

일반 빌드 후 `node scripts/check_search_navigation.mjs`로 8개 언어를 모바일·데스크톱에서 확인합니다. 주소 직접 열기·새로고침·글 방문 후 복귀·검색어 삭제·로딩 실패 후 재시도·늦은 응답 취소를 실제 Chrome에서 검사합니다. 조합 이벤트 검사는 합성 이벤트를 사용하며 운영체제 IME 전체 검증을 뜻하지 않습니다. 운영 배포 확인은 `--url https://youdozi.github.io/`를 추가하며, 두 모드 모두 공통 브라우저 격리로 GA 전송을 차단합니다. 동일 검사는 필수 CI에도 포함됩니다.

## 관측 대상

대표 글은 `content/seo/core-articles.json`의 10개 주제로 관리합니다. 첫 4개는 기존 Search Console 조회에서 노출이 있었던 주제이며, 나머지는 셸 입력 검증과 Spring 생성·영속성·HTTP 테스트·패키징의 연결을 고려해 선정했습니다. 이 목록은 검색량 순위가 아닙니다. 홈의 대표 글 목록과 조회 도구가 같은 키를 사용합니다.

## 조회

기존 Search Console OAuth 인증과 `scripts/requirements-search-console.txt` 환경을 사용합니다. 기본 명령은 URL 목록만 표시하며 외부 API를 호출하지 않습니다.

```sh
.venv-search-console/bin/python scripts/search_growth.py
.venv-search-console/bin/python scripts/search_growth.py --live
.venv-search-console/bin/python scripts/search_growth.py --live --previous ~/.config/youdozi-search-console/이전-스냅샷.json
.venv-search-console/bin/python scripts/search_growth.py --report ~/.config/youdozi-search-console/이전-스냅샷.json
```

`--live`는 핵심 한영 글 20개와 과거 Jekyll 주소 10개를 조회합니다. 공개 URL의 HTTP 응답·canonical·robots·즉시 meta refresh와 Google에 저장된 색인 상태를 별도로 기록합니다. URL Inspection API는 실시간 색인 가능성 검사가 아니며 색인 생성 요청도 하지 않습니다. [공식 API](https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect)

검색 실적은 최근 3일을 제외한 PT 달력 날짜 기준 28일과 직전 28일을 조회합니다. `dataState: final`을 지정하고 사이트 전체 합계와 대상 URL의 페이지 행을 보관합니다. 현재 구간에서는 페이지·검색어 행도 보관합니다. API의 상위 행 제한과 익명화 등으로 모든 행을 얻는 것은 아니므로, 반환되지 않은 URL을 노출 0으로 바꾸지 않습니다. 페이지 합계를 속성 전체 합계와 같다고 가정하지 않습니다. [Search Analytics API](https://developers.google.com/webmaster-tools/v1/searchanalytics/query)

결과는 저장소 밖 `~/.config/youdozi-search-console/search-growth-시각.json`에 권한 600으로 저장합니다. `--output`으로 저장소 밖 새 파일을 지정할 수 있습니다. 이미 있는 파일은 덮어쓰지 않습니다. 검색어·사용자별 실적과 인증 파일은 Git·공개 사이트·CI 산출물에 올리지 않습니다. Google 권한 오류나 조회 실패를 미색인으로 세지 않습니다.

`--previous`는 같은 속성·URL 집합의 이전 스냅샷과 비교해 PASS 전환·PASS 해제·Google canonical 변경을 기록합니다. 한쪽 API가 실패한 URL은 비교 불가로 분리합니다. 주간 조회의 28일 실적 구간은 서로 겹칠 수 있으므로 독립적인 전후 실험으로 해석하지 않습니다.

`--report`는 저장된 결과를 네트워크·인증·파일 쓰기 없이 읽습니다. URL별 색인 상태·Google canonical·마지막 크롤링, 사이트 전체 실적과 저장된 비교 결과를 텍스트로 표시합니다. 검색어 행은 출력하지 않으며 미제공 값을 0으로 바꾸지 않습니다. 조회 시각을 함께 표시하므로 과거 결과를 현재 상태로 해석하지 않습니다. 다른 조회 옵션과 함께 사용할 수 없습니다.

### 주제별 주소 전환 보고서

`scripts/migration_report.py`는 이미 저장한 스냅샷만 읽어 핵심 10개 주제의 영문·한글·과거 주소를 함께 표시합니다. 별도 API 호출이나 OAuth 인증, 색인 요청 없이 사용합니다.

```sh
python3 -B scripts/migration_report.py \
  --snapshot ~/.config/youdozi-search-console/현재-스냅샷.json
python3 -B scripts/migration_report.py \
  --snapshot ~/.config/youdozi-search-console/현재-스냅샷.json \
  --previous ~/.config/youdozi-search-console/이전-스냅샷.json \
  --output ~/.config/youdozi-search-console/새-주소전환-보고서.json
```

기본 출력은 터미널 텍스트뿐입니다. `--output`을 지정한 경우에만 모든 프로젝트 worktree 밖의 새 JSON을 권한 600으로 저장하고 기존 파일은 덮어쓰지 않습니다. 검색어 행과 원본 API 응답은 복사하지 않습니다. 입력 스냅샷의 조회 시점·실적 구간을 유지하고 대상 속성·주소 중복·등록된 핵심 글 매핑을 확인합니다. 이전 스냅샷은 같은 URL 집합과 같거나 앞선 관측 시각이어야 합니다.

`--deployed-at`에는 GitHub Pages의 실제 배포 완료 시각을 시간대가 있는 ISO 8601 값으로 넣을 수 있습니다. 병합 시각을 배포 완료 시각으로 대신하지 않습니다. 스냅샷 자체가 배포 전인지, 각 주소의 마지막 크롤링이 배포 전후인지 별도로 표시합니다. 배포 후 크롤링 날짜가 있더라도 변경 HTML 반영이나 색인 완료·인과효과의 증거는 아닙니다. 인자를 생략하면 배포 전후는 비교하지 않습니다.

새 한글 주소가 PASS여도 과거 주소가 여전히 Google의 대표 주소로 선택되어 있으면 이를 구분합니다. 양쪽이 목적지를 선택한 관측도 전체 이전 완료로 단정하지 않습니다. 영문 상태는 별도로 유지하며 한글 색인을 영문 색인으로 간주하지 않습니다. URL별 페이지 실적을 합산해 속성 전체 클릭·노출로 만들지 않습니다. 미반환 실적·마지막 크롤링·canonical은 비교 불가로 남깁니다.

핵심 글 조회·비교에서도 HTTP 200만으로 색인 판정을 알 수 있다고 가정하지 않습니다. `VERDICT_UNSPECIFIED`·누락된 판정은 PASS 증감에서 제외하고, 양쪽 canonical이 모두 제공된 경우에만 대표 주소 변경으로 셉니다. 판정은 있으나 canonical이 없는 경우에는 색인 비교와 canonical 비교 가능 여부를 따로 기록합니다. [Google 응답 필드와 판정 정의](https://developers.google.com/webmaster-tools/v1/urlInspection.index/UrlInspectionResult)

## 판정과 후속 조치

| 확인 결과 | 다음 행동 |
| --- | --- |
| 새 글 HTTP 200·자기 canonical, Google에는 미발견 | 홈·학습 안내·본문에서 연결되는지 확인하고 다음 관측과 비교 |
| Google 선택 canonical이 다른 주소 | 중복 본문·언어 링크·기존 URL의 이동 대상 대조 |
| 기존 주소 노출이 남고 새 주소는 미발견 | 기존→새 주소 매핑과 Google의 마지막 크롤링 시각을 함께 추적 |
| 노출은 있으나 클릭이 적음 | 검색어와 제목·도입·실제 해결 범위를 대조; 작은 표본의 CTR만으로 교체하지 않음 |
| HTTP·인증·API 오류 | 먼저 조회 실패 해결; 색인 상태와 분리 |

GitHub Pages의 기존 주소는 현재 HTTP 200과 즉시 meta refresh로 이동합니다. 이를 서버 301로 기록하지 않습니다. Google은 즉시 meta refresh를 영구 이동으로 해석하지만 서버 리디렉션을 우선 권장합니다. 추적만으로 순위 하락의 원인이나 호스팅 변경의 필요성을 확정하지 않습니다. [리디렉션 안내](https://developers.google.com/search/docs/crawling-indexing/301-redirects)

### 게시글 이동 신호와 빌드 검사

`search_growth.py --report`는 같은 주제의 과거 주소와 한국어 목적지를 짝지어 보여줍니다. 두 응답이 목적지 canonical을 가리키는 관측, 새 주소가 색인돼도 과거 canonical이 남은 관측, API 오류·canonical 미제공을 구분합니다. 이 판정은 한국어 주소 이전에 한하며 영문 색인이나 전체 이전 완료를 뜻하지 않습니다. 마지막 크롤링 시각과 현재 공개 응답을 함께 확인하고, 과거의 색인 제외 기록을 현재 `noindex`로 단정하지 않습니다.

공개 기술 글의 과거 주소는 즉시 meta refresh·새 주소 canonical·동일한 이동 링크를 함께 제공합니다. 이 이동 페이지에는 `noindex`를 넣지 않습니다. Google은 같은 사이트 안에서 대표 주소를 선택하기 위한 `noindex` 사용을 권장하지 않습니다. 이 정책은 이미 공개된 실제 게시글로 이동하는 경로에만 적용하며, 루트·목록 이동과 예제 글 이동은 기존 `noindex,follow`를 유지합니다. 이동 주소를 사이트맵에 추가하지 않습니다. [대표 주소 지정 안내](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)

`scripts/check_migration.py`는 일반 빌드와 격리 번역 빌드에서 전체 이동 페이지를 검사합니다. 목적지가 실제로 존재하는 최종 자기 canonical 페이지인지, 이동 체인·순환이 없는지, canonical·즉시 refresh·화면 링크가 같은지 확인합니다. 공개 게시글 이동에는 `noindex`가 없고 목적지는 사이트맵에 있어야 하며, 일반 탐색·예제 이동에는 `noindex`가 있어야 합니다. 공개 페이지에서 과거 이동 주소를 계속 링크하면 실패합니다. 핵심 글 10개는 등록된 과거 주소→한글판 매핑과 한영 20개 최종 주소를 별도로 검사합니다.

```sh
python3 -B scripts/check_migration.py --dist dist
```

이 검사는 생성 HTML의 이동 신호 일치만 검증합니다. Google의 재크롤링·대표 주소 선택·색인·순위 개선을 증명하지 않으며, 변경 전후의 실제 결과는 비공개 Search Console 스냅샷으로 비교합니다. 다음 수동 관측일인 2026-11-04에는 과거 주소와 새 주소의 마지막 크롤링·선택 canonical·색인 판정을 함께 비교합니다. 자동 색인 요청이나 예약 실행은 추가하지 않습니다.

## 다운로드 파일 검증 후속 글

2026-10-30에는 메타데이터 선택과 다운로드 파일 검증을 이어 읽도록 SHA-256 가이드의 한영 글을 추가했습니다. GitHub 릴리스·Temurin 한영 4편의 본문과 셸 학습 경로에서 연결하며, 새 글은 코드·현지화한 그림·다운로드 ZIP을 함께 제공합니다. 공식 Python·Adoptium 문서와 로컬 바이트 재현을 근거로 하며 서명 검증·배포자 인증·악성 코드 검사까지 구현했다고 표시하지 않습니다.

새 주소는 `/en/posts/2026-10-30-verify-sha256-download/`와 `/ko/posts/2026-10-30-verify-sha256-download/`입니다. 기존 AEO 첫 적용 10 URL의 고정 목록에 합치지 않고 별도로 추적합니다. 실제 배포 후 두 URL의 첫 색인 관측 시각과 배포 커밋을 보관하고, 이후 Search Console 페이지 필터로 각 URL의 노출·클릭을 확인합니다. 첫 게시 전에 존재하지 않았던 기간의 미반환 행을 노출 0이나 개선 기준선으로 간주하지 않습니다. 28일 사후 실적의 시작일은 실제 배포의 PT·GA4 속성 시간대 날짜를 모두 지난 날로 결정합니다. 이 문서는 수동 관측 계획이며 새 예약 실행이나 색인 요청을 추가하지 않습니다.

## 4주 관측 계획

### AEO 관측 그룹과 색인 전용 조회

`answer_observation.py`의 기본 대상은 기존 `technical-answers-059` 한영 10 URL입니다. `--cohort checksum-guide-066`은 SHA-256 가이드 한영 2 URL만 선택합니다. `content/seo/answer-cohorts.json`에 등록된 ID·파일·주제 수를 확인하고, 조회 전에 원본 글의 공개 시각·언어·종류·검토 상태·경로를 검증합니다. 임의 URL·파일 경로를 인자로 받지 않으며 기존 첫 관측 그룹과 URL 집합 해시는 유지합니다.

```sh
python3 -B scripts/answer_observation.py --cohort checksum-guide-066 --index-only
.venv-search-console/bin/python scripts/answer_observation.py \
  --cohort checksum-guide-066 --index-only --live \
  --output ~/.config/youdozi-search-console/checksum-index-new.json
python3 -B scripts/answer_observation.py \
  --report ~/.config/youdozi-search-console/checksum-index-new.json
```

첫 명령은 계획 출력만 하며 인증·네트워크·파일 쓰기가 없습니다. `--index-only --live`는 Google 저장 색인 상태만 읽고 GSC 검색 실적·GA4를 호출하지 않습니다. 날짜·성과 비교 옵션과 함께 사용할 수 없고 색인 전용 결과를 28일 실적의 기준선으로 사용하지 못합니다. 새 비공개 출력 경로를 필수로 받으며 덮어쓰기·저장소 내부 저장은 기존과 같이 거부합니다. API 오류·판정 미제공·PASS 이외 판정·미조회 URL을 따로 집계하고, URL별 canonical·마지막 크롤링·판정을 표시합니다. HTTP 200과 Google 색인 PASS는 별개입니다. [URL Inspection API](https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect)

성과 모드는 원문 해시와 선언된 `publishedAt`을 기록하고 GSC의 PT·GA4 속성 시간대에서 관측 기간과 비교합니다. `not-yet-published`·`partial-window`·`not-recorded`를 표시하며, GSC 전후 두 구간 모두 `declared-before-window`가 아닐 때 클릭·노출 증감은 계산하지 않습니다. 오래된 보고서에 발행일 정보가 없으면 그 값을 추정하지 않고 원래 수치만 유지합니다. 선언된 발행일은 필요 날짜 조건일 뿐이며, 이전된 URL이 기간 전체에 실제 존재했거나 색인돼 있었다는 증거가 아닙니다. 비교에서도 `routeAvailabilityVerified: false`를 유지합니다. GA4의 같은 날짜 문자열도 PT와 경계가 다를 수 있습니다. [GA4 응답 시간대](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/ResponseMetaData)

보고서의 `dataOrigin`은 실제 API 조회와 저장 응답 재생을 구분하며, 재생은 원래 관측 시각을 유지합니다. `--report`는 조회 시각을 갱신하거나 새 검색 실적을 수집하지 않습니다. 원시 검색어·API 응답은 비공개 파일에만 두고 요약에는 검색어를 출력하지 않습니다. Google·Bing의 전용 AI 보고서는 계속 `not-collected`이며 AI 출처 도메인과 일치한 GA 행을 실제 AI 인용이나 사람 방문으로 확정하지 않습니다.

예제 다운로드 추가는 재현성과 이용 편의를 개선하는 별도 변경입니다. 7개 주제의 한영 14편에 ZIP 링크를 제공하지만 본문·제목·주소·게시일·본문 수정일과 번역 원문 고정 해시는 바꾸지 않습니다. 다운로드 이벤트 수집은 추가하지 않습니다. 이후 검색·참여 실적을 해석할 때 이 화면 변경도 함께 고려하고, 다운로드 파일 제공 자체를 색인·순위·AI 인용 증가로 기록하지 않습니다.

2026-10-30 조회에서 핵심 새 주소 20개 중 한국어 GitHub 릴리스·Vue 패키징 2개가 PASS였고 18개는 미발견 상태였습니다. 과거 주소 10개 중 8개가 PASS였으며, 두 새 주소의 색인이 확인됐어도 Vue 글의 과거 주소에는 다른 Google canonical이 남아 있습니다. 현재 HTTP 응답·canonical·즉시 이동 검사 30개는 일치했습니다. 이는 주소 이전의 원인 확정이나 현재 Googlebot 접근 검사가 아닙니다. 원시 검색어·URL 검사 응답은 저장소 밖 비공개 결과로 보관합니다.

반환된 검색어와 연결 상태를 바탕으로 GitHub 릴리스·Batch·패키징·HTTP 테스트의 한영 본문 8편을 보강했습니다. 표본이 작아 제목은 유지했고, 기존 코드·그림·주소·발행일도 보존했습니다. 홈·학습 안내의 연결을 재확인했으며 GitHub 저장소 README에도 문제별 한영 글을 연결했습니다. 커뮤니티 게시나 타인에게 메시지 전송은 하지 않았습니다.

`check_discovery.py`는 홈에서 두 HTML 링크 이내의 발견 경로 외에, 공개된 핵심 한영 글마다 다른 같은 언어 기술 글의 본문 링크가 하나 이상 들어오는지도 검사합니다. 자기 링크·메뉴·관련 글·다른 언어·중복 링크는 본문 유입 수를 늘리지 않습니다. 이는 링크 존재 검사이며 실제 검색엔진 발견·색인·독자 방문의 증거가 아닙니다.

게시 승인 후의 실제 배포일을 기준일로 삼습니다. 현재 조회는 변경 전 기준선이며 새 제목과 홈 연결의 효과를 측정한 결과가 아닙니다.

1. 기준일: 동일 목록의 색인 상태·canonical·실적 구간과 배포 커밋을 보관합니다.
2. 1주·2주: 같은 명령을 수동 실행해 URL별 마지막 크롤링과 선택 canonical을 비교합니다.
3. 4주: 배포 이후 데이터가 채워진 구간에서 언어별 색인 상태·노출된 URL·클릭을 비교합니다. 브랜드/비브랜드 구분은 반환된 검색어에만 적용하며 익명화된 검색어까지 추정하지 않습니다.

이 문서는 수동 실행 계획입니다. 예약 작업이나 자동 게시를 추가하지 않습니다. 관측 기간의 계절성·검색 수요·동시 배포를 고려하고 변경 전후 차이를 인과효과로 단정하지 않습니다.

## Google·Bing 다국어 공개 글 관측

### 공개 응답의 크롤링 접근성

`scripts/crawl_access.py`는 색인 API와 별개로 같은 공개 관측 목록 94개와 robots.txt·사이트맵을 일반 HTTP로 읽습니다. API 키·OAuth·JavaScript를 사용하지 않으며 실제 Googlebot/Bingbot을 가장하지 않습니다. 기본 실행은 요청 수 미리보기뿐입니다.

```sh
python3 -B scripts/crawl_access.py
.venv-search-console/bin/python scripts/crawl_access.py --live \
  --output ~/.config/youdozi-search-console/새-크롤링-접근성.json
python3 -B scripts/crawl_access.py \
  --report ~/.config/youdozi-search-console/새-크롤링-접근성.json
```

`--live`는 저장소의 공개 파일에서 결정한 주소만 최대 두 개씩 조회하고 서버 리디렉션을 자동 추적하지 않습니다. 대체 링크에 적힌 외부·미관측 주소를 추가로 방문하지 않습니다. 응답의 HTTP 상태·HTML 콘텐츠 형식·canonical·즉시 이동·HTML 언어·색인 제외 지시문을 검사합니다. HTTP `X-Robots-Tag`도 별도로 읽고 Googlebot/Bingbot 범위와 반복 헤더를 구분합니다. HTML 본문의 robots meta도 관측하며 조건부·미지원 지시문은 추가 확인 대상으로 남깁니다. 쿠키·인증 정보·전체 헤더·HTML 본문은 결과에 저장하지 않습니다. [robots meta와 HTTP 지시문](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag)

현재 robots.txt의 `User-agent: *`·`Allow: /`·해당 사이트맵 명시 정책만 인식합니다. 임의의 robots 규칙을 구현한 검색엔진 모방 도구가 아니며 정책이 달라지거나 HTTP 오류가 나면 접근 허용으로 간주하지 않습니다. 이때 `robots-policy-unconfirmed`로 추가 확인을 요구합니다. [Google robots.txt 해석](https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec)

84개 최종 페이지는 사이트맵에 포함되고 과거 이동 주소 10개는 제외되어야 합니다. 현재 공개 언어판의 대체 주소가 빠지지 않았는지, 대체 주소가 조회된 최종 자기 canonical 페이지인지, 언어와 상호 링크가 맞는지 확인합니다. 양쪽 페이지가 서로의 링크를 함께 잃은 경우도 공개 언어판 목록과 비교해 검출합니다. `x-default`는 영문판과 일치해야 합니다. [다국어 대체 페이지 지침](https://developers.google.com/search/docs/specialty/international/localized-versions)

결과는 `checks-passed`·`issue`·`unknown`으로 나누며 하나라도 문제나 미확인이 있으면 종료 코드 2로 반환합니다. 요청 실패와 미확인 상태를 정상으로 바꾸지 않습니다. 비공개 새 파일만 권한 600으로 저장하며 모든 worktree 내부와 기존 파일 덮어쓰기를 거부합니다. 일반 HTTP에서 검사가 통과해도 실제 검색봇의 방문·색인·노출을 증명하지 않으며, 이를 판정하려면 별도의 저장 색인 및 검색 실적 관측과 함께 읽어야 합니다. 예약 조회나 색인·사이트맵 제출은 추가하지 않습니다.

### Google·Bing API 관측

`scripts/search_engines.py`는 기존 핵심 글 조회에 현재 공개 번역과 각 번역의 한영 대응 글, 언어별 홈과 공개 글이 있는 언어의 전체 글 아카이브를 더합니다. 현재 기준 94 URL(핵심 글·과거 주소 30, 다국어 다이제스트 48, 홈 8, 아카이브 8)이며 `.pipeline/`의 미게시 번역은 읽지 않습니다. 공개 번역 파일이 바뀌면 대상 수도 바뀝니다. 실제 배포된 `main` 기준으로 실행합니다. 아카이브는 PR #77에서 배포되었습니다. 관측 목록에 포함한 것만으로 탐색 구조의 검색 성과가 입증되지는 않으며, 미게시 번역은 관측 대상이 아닙니다.

기존 Google OAuth와 `~/.config/youdozi-search-console/bing-api-key.txt`를 사용합니다. 키를 명령행 인자로 전달하지 않습니다.

```sh
.venv-search-console/bin/python scripts/search_engines.py
.venv-search-console/bin/python scripts/search_engines.py --live
.venv-search-console/bin/python scripts/search_engines.py --live \
  --previous ~/.config/youdozi-search-console/이전-다국어-스냅샷.json
.venv-search-console/bin/python scripts/search_engines.py \
  --report ~/.config/youdozi-search-console/다국어-스냅샷.json
```

기본 실행은 URL 목록만 표시합니다. `--live`는 Google 저장 색인 상태와 기존 도구와 같은 실적 구간을 조회하고, Bing의 읽기 전용 `GetUserSites`, `GetFeeds`, `GetRankAndTrafficStats`, `GetUrlInfo`를 호출합니다. Bing REST JSON 경로만 사용하며 URL·사이트맵 제출은 하지 않습니다. 인증 응답의 불필요한 소유권 확인 코드는 저장하지 않습니다. [Bing REST 프로토콜](https://learn.microsoft.com/en-us/bingwebmaster/api-protocols), [공식 시작 안내](https://learn.microsoft.com/en-us/bingwebmaster/getting-started)

조회 결과는 저장소 밖 새 파일에 권한 600으로 보관하며 기본 경로는 `~/.config/youdozi-search-console/search-engines-시각.json`입니다. `--output`은 기존 파일과 저장소 worktree 내부를 거부합니다. 검색어 실적은 비공개 스냅샷에만 남고 터미널 보고서에는 표시하지 않습니다. `--report`는 API·인증·파일 쓰기 없이 해당 시점의 결과를 읽습니다. `--previous`는 기본적으로 속성과 URL 집합이 같은 스냅샷에만 사용합니다. 대상이 달라지면 인증·API 호출 전에 거부합니다. 기존 86개 기록을 새 94개 목록과 비교하려면 `--allow-selection-change`를 명시합니다. 같은 속성의 중복 없는 목록과 공통 URL이 있어야 하며, 공통 URL만 색인 전환·새 크롤링 비교에 사용합니다. 추가·제외 URL은 각각 `addedURLs`·`removedURLs`에 기록하고 증감에 포함하지 않습니다. 새 URL의 첫 관측은 새 기준선입니다. 이후 94개 기록끼리는 이 옵션 없이 비교합니다. 이전 파일과 그 조회 시각은 그대로 보존합니다.

```sh
.venv-search-console/bin/python scripts/search_engines.py --live \
  --previous ~/.config/youdozi-search-console/이전-86개-스냅샷.json \
  --allow-selection-change
```

이 옵션은 조회 대상 수를 줄이지 않습니다. `--live`는 현재 94개 전체를 새로 조회하고 실적 구간도 다시 읽습니다. 2026-10-28의 기존 86개 관측과 배포 후 아카이브 8개 별도 관측은 조회 시점·파일 형식이 다르므로 하나의 동시 조회 결과로 합치지 않습니다. 이 변경 검증에서는 해당 결과를 재조회하지 않았습니다. 다음 수동 확인일은 2026-11-04·11-11·11-25이며, 예약 작업은 등록하지 않았습니다.

Google PASS는 저장된 색인 판정입니다. 성공 응답이라도 판정이 없으면 비교 불가로 처리하며 이전 PASS 해제로 세지 않습니다. API 오류도 미색인으로 바꾸지 않습니다. [Google URL Inspection API](https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect)

Bing `GetUrlInfo`의 유효한 마지막 크롤링 날짜는 크롤링 관측입니다. 이 응답에는 색인 여부를 확정하는 필드가 없으므로 `IsPage`, 문서 크기, HTTP 상태 또는 날짜만으로 색인 완료라고 표시하지 않습니다. 날짜의 기본값이나 `HttpStatus: 0`도 실제 현재 HTTP 오류로 해석하지 않습니다. 크롤링 기록이 없다는 결과와 API 조회 실패를 구분합니다. [공식 UrlInfo 필드](https://learn.microsoft.com/en-us/dotnet/api/microsoft.bing.webmaster.api.interfaces.urlinfo?view=bing-webmaster-dotnet)

공개 응답 검사는 기존 도구와 같은 HTTP·HTML canonical·robots meta·즉시 meta refresh 대조이며, 공개 사이트맵 포함 여부도 따로 기록합니다. 과거 이동 주소가 사이트맵에서 빠지는 것은 정상입니다. robots.txt 해석, 모든 HTTP 헤더 규칙, 검색어별 실제 결과 화면, 네이버·Baidu·Yandex 콘솔을 대신 검사하지 않습니다. Google·Bing의 실적 반환 행이 비어 있어도 노출 0으로 확정하지 않습니다.

다음 관측에서는 같은 목록의 Google PASS 전환·비교 불가, Bing 새 크롤링 기록, 공개 응답과 사이트맵 상태를 비교합니다. 사이트맵 처리 성공·IndexNow 수락·크롤링·색인·검색 노출은 각각 구분합니다. 예약 실행이나 자동 게시를 추가하지 않습니다.

Bing URL 조회는 순차 실행합니다. 일부 요청이 실패했다면 다음 명령으로 실패한 URL만 한 번씩 다시 읽습니다. Google 조회·실적·공개 응답·Bing 사이트맵은 재호출하지 않고 원래 조회 시점을 유지합니다. 기존 파일은 보존하고 새 비공개 스냅샷에 원래 오류와 Bing 재조회 시각을 기록합니다. 재조회 대상도 현재 공개 URL 목록에 속해야 합니다. 재시도 사이에는 0.5초 간격을 두며 실패가 남으면 실패 상태로 끝납니다. HTTP 오류에서 제공하는 숫자형 [Bing 오류 코드](https://learn.microsoft.com/en-us/dotnet/api/microsoft.bing.webmaster.api.interfaces.apierrorcode?view=bing-webmaster-dotnet)만 추가로 보관하고, 키가 포함될 수 있는 요청 URL·예외 메시지·원시 오류 본문은 저장하지 않습니다.

```sh
.venv-search-console/bin/python scripts/search_engines.py \
  --retry-bing ~/.config/youdozi-search-console/이전-다국어-스냅샷.json
```

호스트·사용자 호출 제한(`ThrottleHost: 5`, `ThrottleUser: 4`)을 받으면 해당 실행의 나머지 Bing URL 요청은 중단합니다. 미호출 항목과 실제 실패 응답을 구분하며 자동 반복 재시도는 하지 않습니다. 제한이 풀린 뒤 저장된 결과를 기준으로 실패 항목만 다시 조회할 수 있습니다. 제한이 풀리는 시점은 이 도구가 보장하지 않습니다.

## 통합 검증과 배포 기록

PR #77(탐색 구조), #78(번역 준비·게시 전 검사), #79(검색엔진 관측)는 각각 main을 기준으로 준비했으므로 단독 CI 통과만으로 함께 적용되는 결과를 확인할 수는 없습니다. 임시 worktree에서 #77 → #78 → #79 순서로 합쳐 일반 빌드와 미게시 번역 318편을 포함한 테스트 빌드를 검증했습니다. 이 사전 검증 자체는 게시 승인이나 main 병합을 의미하지 않았습니다. 이후 사용자 승인에 따라 2026-10-28에 #77 → #78 → #79 순서로 main에 병합하고 배포했습니다. 최종 배포 커밋은 `29eef435b11bb7c8d249ddc9e77cef6873991e4e`이며 [배포 작업](https://github.com/youdozi/youdozi.github.io/actions/runs/40645422993)이 성공했습니다.

통합 때 README와 `package.json`의 테스트 명령에 충돌이 생겼습니다. 승인 후 각 브랜치를 main과 맞추면서 다음 내용을 모두 보존했습니다.

- README: 전체 글 탐색 안내, 스페인어·5개 언어 게시 전 검사 안내, Google·Bing 관측 안내.
- `test`: 기존 테스트에 `scripts/test-discovery.mjs`와 `scripts/test-translation-release.mjs`를 모두 포함합니다. 한쪽 명령으로 통째로 덮어쓰지 않습니다.
- `build`: `scripts/check_discovery.py`를 유지합니다.
- `check:translations`: 게시 전 검사 호출과 두 개의 고정된 release ledger를 유지합니다.

#77을 먼저 적용하고, #78·#79를 최신 main과 맞춰 충돌 해결과 CI를 다시 확인했습니다. #78의 병합으로 비공개 초안이 자동 게시되지는 않았습니다. 번역 공개는 승인된 원고 집합에 대한 별도 게시 파일 준비와 배포가 필요합니다.

통합 일반 상태에서는 423개 글·479개 사이트맵 URL·공개 번역 36편을 확인했습니다. 318개 테스트 fixture를 더한 상태는 741개 글·797개 사이트맵 URL이며, 8개 언어의 모든 공개 글이 각 언어 홈에서 두 번 이내의 HTML 링크 이동으로 도달했습니다. 두 상태 모두 빈 noindex 목록으로 보내는 공개 링크는 0개입니다. fixture를 제거한 뒤 일반 빌드와 원래 공개 파일을 다시 확인했습니다. 미리보기 수치는 실제 배포 수치가 아닙니다.

Python 209개·Node 74개, Astro 64개 파일 검사, 일반·확장 빌드, 두 상태의 브라우저 검사 총 72개를 수행했습니다. 번역 318편의 주장·후속 사실 738개, 검색·최근 30개 RSS 정책·사이트맵·53개 주제의 8개 언어 상호 링크도 대조했습니다. 새 언어 의미 검토나 외부 출처의 사실 재검증을 추가한 것은 아닙니다. 정확한 PR 커밋과 검사 범위는 [통합 검증 기록](../.pipeline/content-reviews/integration-batch-034.json)을 따릅니다. 이후 PR 원고·코드가 바뀌면 해당 기록을 새 버전의 검증으로 간주하지 않습니다.

## 트래픽 급증 조사와 검증 방문 분리

`measurement_audit.py`는 Search Console 클릭과 GA4 세션을 같은 실제 시간 구간에서 읽고, 검토 페이지와 의심 규칙에 맞은 `page_view` 이벤트를 별도 보고합니다. 기본 실행은 미리보기이며 인증 정보·네트워크·출력 파일을 사용하지 않습니다.

```sh
.venv-search-console/bin/python scripts/measurement_audit.py \
  --start 2026-10-24 --end 2026-10-26 \
  --segment-start 2026-10-25 --segment-end 2026-10-26

# 검토한 비공개 규칙을 지정해 읽기 전용 조회 결과를 새 파일로 저장
.venv-search-console/bin/python scripts/measurement_audit.py --live \
  --start 2026-10-24 --end 2026-10-26 \
  --segment-start 2026-10-25 --segment-end 2026-10-26 \
  --rules ~/.config/youdozi-blog-review/traffic-review-rules.json \
  --output ~/.config/youdozi-blog-review/measurement-audit-new.json

# 저장된 결과만 읽기: API 조회와 파일 쓰기 없음
.venv-search-console/bin/python scripts/measurement_audit.py \
  --report ~/.config/youdozi-blog-review/measurement-audit-new.json
```

`--start/--end`는 GSC의 PT 달력 날짜이며 최대 7일을 허용합니다. PT 자정 경계를 GA 속성의 한국 시간으로 변환해 `dateHour` 필터를 만듭니다. 예를 들어 PT 10월 24~26일은 한국 시간 10월 24일 16시부터 27일 16시 직전까지입니다. DST 경계는 UTC 시간으로 순회하며 하루를 항상 24시간으로 가정하지 않습니다. `--segment-start/--segment-end`는 별도로 지정하는 GA 속성 시간대의 달력 날짜입니다. [GSC 시간·행 범위](https://developers.google.com/webmaster-tools/v1/searchanalytics/query)와 [GA 세션 집계](https://support.google.com/analytics/answer/9191807)를 참고합니다.

GSC는 `final` 웹 검색 합계·날짜·페이지 행을 요청합니다. 클릭과 GA 세션은 다른 지표이고, GSC는 과거 canonical 주소로 집계할 수 있으며 페이지 행은 일부가 생략될 수 있습니다. API 오류나 반환되지 않은 행을 0으로 만들지 않습니다. Bing은 `GetUserSites`가 돌려준 실제 등록 주소로 `GetRankAndTrafficStats`를 한 번 요청합니다. 빈 배열은 클릭 0이 아니라 실적 비교 불가이며, API 자체의 날짜·검색 범위를 GA 시간 구간과 같다고 가정하지 않습니다. [Bing 공식 실적 API](https://learn.microsoft.com/en-us/dotnet/api/microsoft.bing.webmaster.api.interfaces.iwebmasterapi.getrankandtrafficstats?view=bing-webmaster-dotnet)

분리 보고서는 원본 조회 → `/review`·`/review/` 조회 → 그 외 조회 → 의심 규칙 일치 → 나머지 참고 구간을 표시하고 두 분할 합계를 검산합니다. 단위는 `page_view` 이벤트 수입니다. 페이지별로 겹칠 수 있는 사용자·세션 수를 빼서 순방문자를 계산하지 않습니다. 규칙 파일을 지정하지 않으면 의심 규칙을 자동 생성하지 않습니다. 규칙 파일은 다음 구조를 따르며, 실제 검토한 분·출처·경로를 저장소 밖에 보관합니다.

```json
{
  "schemaVersion": 1,
  "property": "properties/280207087",
  "timeZone": "Asia/Seoul",
  "rules": [{
    "id": "example-reviewed-overlap",
    "classification": "suspected",
    "reason": "검토한 게시 시점·경로 일치. 방문 주체는 미확인",
    "sourceMedium": "bing / organic",
    "minutes": ["202610250000"],
    "paths": ["/en/digest/example/"]
  }]
}
```

이는 파일 형식의 예시입니다. 국가·브라우저·게시 시점이 겹친다는 이유만으로 사람/봇을 확정하지 않으며, 나머지 구간도 검증된 실제 독자로 표시하지 않습니다. 과거 API 결과·규칙·보고서는 덮어쓰지 않고 새 비공개 JSON(600)으로 저장합니다. GA 필터·이벤트·속성 설정을 변경하거나 원본 데이터·기존 파일을 삭제하지 않습니다. 이 절차는 예약 조회·색인 요청·게시 기능을 추가하지 않습니다.

## 운영 Analytics에 더하지 않는 브라우저 검증

간단한 공개 페이지 확인은 다음 명령을 사용합니다. 기본 모드는 페이지를 열기 전에 GA 관련 네트워크 차단을 설치합니다.

```sh
node scripts/check_browser_pages.mjs \
  --url https://youdozi.github.io/en/ \
  --url https://youdozi.github.io/ko/
npm run check:browser-isolation
```

복잡한 검사는 `scripts/browser/isolated-context.mjs`의 `isolatedContext(browser, options)`로 만든 Playwright 컨텍스트를 사용합니다. 모든 페이지·팝업에 같은 경로 차단을 적용하고 서비스 워커를 차단합니다. 기본 모드는 Google 태그·수집 도메인과 알려진 수집 경로·GA 형태의 프록시 요청을 막습니다. 쿠키·원시 요청 URL·본문·개인 식별자를 결과에 보관하지 않고 차단 횟수만 기록합니다. 임의로 이름을 바꾼 모든 외부 수집 서버를 탐지하는 도구는 아닙니다.

실제 Google 태그 생성 여부를 검사해야 할 때만 `isolatedContext(browser, options, 'tag-verification')`을 사용합니다. 이 사이트의 정확한 HTTPS 태그 라이브러리만 허용하며, 생성된 이벤트의 전송은 계속 차단합니다. 페이지별 route로 공통 차단을 덮어쓰지 않습니다. [Playwright 요청 차단과 서비스 워커 제한](https://playwright.dev/docs/api/class-browsercontext#browser-context-route)을 따릅니다.

CI의 로컬 브라우저 검사는 Google 서버에 접속하지 않고 일반 콘텐츠 요청이 통과하는 동안 GET·POST·프록시 본문·비콘·이미지·스크립트·워커·팝업의 수집 요청이 테스트 서버에 도달하지 않는지 확인합니다. 설치된 Chrome/Chromium을 사용하며 `CHROME_PATH`로 실행 파일을 지정할 수 있습니다. `playwright-core`만 설치하며 브라우저를 자동 다운로드하거나 사용자 브라우저 프로필을 재사용하지 않습니다.
