# 핵심 글 검색 성과 확인

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

## 판정과 후속 조치

| 확인 결과 | 다음 행동 |
| --- | --- |
| 새 글 HTTP 200·자기 canonical, Google에는 미발견 | 홈·학습 안내·본문에서 연결되는지 확인하고 다음 관측과 비교 |
| Google 선택 canonical이 다른 주소 | 중복 본문·언어 링크·기존 URL의 이동 대상 대조 |
| 기존 주소 노출이 남고 새 주소는 미발견 | 기존→새 주소 매핑과 Google의 마지막 크롤링 시각을 함께 추적 |
| 노출은 있으나 클릭이 적음 | 검색어와 제목·도입·실제 해결 범위를 대조; 작은 표본의 CTR만으로 교체하지 않음 |
| HTTP·인증·API 오류 | 먼저 조회 실패 해결; 색인 상태와 분리 |

GitHub Pages의 기존 주소는 현재 HTTP 200과 즉시 meta refresh로 이동합니다. 이를 서버 301로 기록하지 않습니다. Google은 즉시 meta refresh를 영구 이동으로 해석하지만 서버 리디렉션을 우선 권장합니다. 추적만으로 순위 하락의 원인이나 호스팅 변경의 필요성을 확정하지 않습니다. [리디렉션 안내](https://developers.google.com/search/docs/crawling-indexing/301-redirects)

## 4주 관측 계획

게시 승인 후의 실제 배포일을 기준일로 삼습니다. 현재 조회는 변경 전 기준선이며 새 제목과 홈 연결의 효과를 측정한 결과가 아닙니다.

1. 기준일: 동일 목록의 색인 상태·canonical·실적 구간과 배포 커밋을 보관합니다.
2. 1주·2주: 같은 명령을 수동 실행해 URL별 마지막 크롤링과 선택 canonical을 비교합니다.
3. 4주: 배포 이후 데이터가 채워진 구간에서 언어별 색인 상태·노출된 URL·클릭을 비교합니다. 브랜드/비브랜드 구분은 반환된 검색어에만 적용하며 익명화된 검색어까지 추정하지 않습니다.

이 문서는 수동 실행 계획입니다. 예약 작업이나 자동 게시를 추가하지 않습니다. 관측 기간의 계절성·검색 수요·동시 배포를 고려하고 변경 전후 차이를 인과효과로 단정하지 않습니다.

## Google·Bing 다국어 공개 글 관측

`scripts/search_engines.py`는 기존 핵심 글 조회에 현재 공개 번역과 각 번역의 한영 대응 글, 언어별 홈을 더합니다. 현재 기준 86 URL(핵심 글·과거 주소 30, 다국어 다이제스트 48, 홈 8)이며 `.pipeline/`의 미게시 번역은 읽지 않습니다. 공개 번역 파일이 바뀌면 대상 수도 바뀝니다. 실제 배포된 `main` 기준으로 실행합니다. PR #77의 탐색 구조나 PR #78의 미게시 번역 효과를 측정한 것으로 해석하지 않습니다.

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

조회 결과는 저장소 밖 새 파일에 권한 600으로 보관하며 기본 경로는 `~/.config/youdozi-search-console/search-engines-시각.json`입니다. `--output`은 기존 파일과 저장소 worktree 내부를 거부합니다. 검색어 실적은 비공개 스냅샷에만 남고 터미널 보고서에는 표시하지 않습니다. `--report`는 API·인증·파일 쓰기 없이 해당 시점의 결과를 읽습니다. `--previous`는 속성과 URL 집합이 같은 스냅샷에만 사용합니다. 공개 글이 늘어나 집합이 바뀌면 새 기준선을 먼저 만듭니다.

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

## 대기 PR의 통합 검증과 적용 순서

PR #77(탐색 구조), #78(번역 준비·게시 전 검사), #79(검색엔진 관측)는 각각 main을 기준으로 준비했으므로 단독 CI 통과만으로 함께 적용되는 결과를 확인할 수는 없습니다. 임시 worktree에서 #77 → #78 → #79 순서로 합쳐 일반 빌드와 미게시 번역 318편을 포함한 테스트 빌드를 검증했습니다. 이 절차는 실제 게시 승인이나 main 병합이 아닙니다.

통합 때 README와 `package.json`의 테스트 명령에 충돌이 생겼습니다. 실제 승인 후 각 브랜치를 main과 맞출 때 다음 내용을 모두 보존해야 합니다.

- README: 전체 글 탐색 안내, 스페인어·5개 언어 게시 전 검사 안내, Google·Bing 관측 안내.
- `test`: 기존 테스트에 `scripts/test-discovery.mjs`와 `scripts/test-translation-release.mjs`를 모두 포함합니다. 한쪽 명령으로 통째로 덮어쓰지 않습니다.
- `build`: `scripts/check_discovery.py`를 유지합니다.
- `check:translations`: 게시 전 검사 호출과 두 개의 고정된 release ledger를 유지합니다.

해당 PR 범위가 각각 승인된 뒤 #77을 먼저 적용하고, #78·#79를 최신 main과 맞춰 충돌 해결과 CI를 다시 확인하는 순서입니다. #78을 병합해도 비공개 초안이 자동 게시되지는 않습니다. 번역 공개는 승인된 원고 집합에 대한 별도 게시 파일 준비와 배포가 필요합니다.

통합 일반 상태에서는 423개 글·479개 사이트맵 URL·공개 번역 36편을 확인했습니다. 318개 테스트 fixture를 더한 상태는 741개 글·797개 사이트맵 URL이며, 8개 언어의 모든 공개 글이 각 언어 홈에서 두 번 이내의 HTML 링크 이동으로 도달했습니다. 두 상태 모두 빈 noindex 목록으로 보내는 공개 링크는 0개입니다. fixture를 제거한 뒤 일반 빌드와 원래 공개 파일을 다시 확인했습니다. 미리보기 수치는 실제 배포 수치가 아닙니다.

Python 209개·Node 74개, Astro 64개 파일 검사, 일반·확장 빌드, 두 상태의 브라우저 검사 총 72개를 수행했습니다. 번역 318편의 주장·후속 사실 738개, 검색·최근 30개 RSS 정책·사이트맵·53개 주제의 8개 언어 상호 링크도 대조했습니다. 새 언어 의미 검토나 외부 출처의 사실 재검증을 추가한 것은 아닙니다. 정확한 PR 커밋과 검사 범위는 [통합 검증 기록](../.pipeline/content-reviews/integration-batch-034.json)을 따릅니다. 이후 PR 원고·코드가 바뀌면 해당 기록을 새 버전의 검증으로 간주하지 않습니다.
