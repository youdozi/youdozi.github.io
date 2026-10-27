# 핵심 글 검색 성과 확인

대표 글은 `content/seo/core-articles.json`의 10개 주제로 관리합니다. 첫 4개는 기존 Search Console 조회에서 노출이 있었던 주제이며, 나머지는 셸 입력 검증과 Spring 생성·영속성·HTTP 테스트·패키징의 연결을 고려해 선정했습니다. 이 목록은 검색량 순위가 아닙니다. 홈의 대표 글 목록과 조회 도구가 같은 키를 사용합니다.

## 조회

기존 Search Console OAuth 인증과 `scripts/requirements-search-console.txt` 환경을 사용합니다. 기본 명령은 URL 목록만 표시하며 외부 API를 호출하지 않습니다.

```sh
.venv-search-console/bin/python scripts/search_growth.py
.venv-search-console/bin/python scripts/search_growth.py --live
.venv-search-console/bin/python scripts/search_growth.py --live --previous ~/.config/youdozi-search-console/이전-스냅샷.json
```

`--live`는 핵심 한영 글 20개와 과거 Jekyll 주소 10개를 조회합니다. 공개 URL의 HTTP 응답·canonical·robots·즉시 meta refresh와 Google에 저장된 색인 상태를 별도로 기록합니다. URL Inspection API는 실시간 색인 가능성 검사가 아니며 색인 생성 요청도 하지 않습니다. [공식 API](https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect)

검색 실적은 최근 3일을 제외한 PT 달력 날짜 기준 28일과 직전 28일을 조회합니다. `dataState: final`을 지정하고 사이트 전체 합계와 대상 URL의 페이지 행을 보관합니다. 현재 구간에서는 페이지·검색어 행도 보관합니다. API의 상위 행 제한과 익명화 등으로 모든 행을 얻는 것은 아니므로, 반환되지 않은 URL을 노출 0으로 바꾸지 않습니다. 페이지 합계를 속성 전체 합계와 같다고 가정하지 않습니다. [Search Analytics API](https://developers.google.com/webmaster-tools/v1/searchanalytics/query)

결과는 저장소 밖 `~/.config/youdozi-search-console/search-growth-시각.json`에 권한 600으로 저장합니다. `--output`으로 저장소 밖 새 파일을 지정할 수 있습니다. 이미 있는 파일은 덮어쓰지 않습니다. 검색어·사용자별 실적과 인증 파일은 Git·공개 사이트·CI 산출물에 올리지 않습니다. Google 권한 오류나 조회 실패를 미색인으로 세지 않습니다.

`--previous`는 같은 속성·URL 집합의 이전 스냅샷과 비교해 PASS 전환·PASS 해제·Google canonical 변경을 기록합니다. 한쪽 API가 실패한 URL은 비교 불가로 분리합니다. 주간 조회의 28일 실적 구간은 서로 겹칠 수 있으므로 독립적인 전후 실험으로 해석하지 않습니다.

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
