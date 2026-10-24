---
title: "[유틸리티] GitHub Source Search"
language: "ko"
translationKey: "2021-08-06-search-github"
routeSlug: "2021-08-06-search-github"
kind: "post"
publishedAt: "2021-08-05T01:00:00.000Z"
categories:
  - "util"
tags:
  - "util"
  - "github"
  - "search"
  - "sourcegraph"
legacyUrl: "/util/search-github/"
legacySource: "_posts/util/2021-08-06-search-github.markdown"
updatedAt: "2026-10-24T09:00:00+09:00"
reviewedAt: "2026-10-24"
reviewStatus: "revised"
reviewScope: "공식 문서 대조 및 예제 코드 검토"
archiveBodySha256: "c8a545f5b1c093bd1721d0966f5dad9412768cdba23f7c1ffa75c17829c7c8e6"
reviewSources:
  - "https://sourcegraph.com/docs/getting-started"
  - "https://sourcegraph.com/docs/code-search/queries"
---
개발자에게 있어 탁월한 검색은 능력은 필수라고 생각됩니다.

특히 키워드를 적절하게 조합하여 원하는 내용을 검색하는 능력.. 이것 또한 개발자에게 필요한 부분이라고 생각되는데요.

최근 sourcegraph 라고 github repository를 검색해주는 아주 훌륭한 사이트가 나왔습니다.

google도 github repository를 검색해주긴 하나... 부족한 점이 많죠.

sourcegraph의 대표적인 기능을 한번 알아볼까요?

---
우선 sourcegraph를 방문해봅시다.

[https://sourcegraph.com/search](https://sourcegraph.com/search)

<img src="/assets/img/util/search_git_hub/sourcegraph.png" alt="sourcegraph">

가운데 검색창에 키워드를 입력하면 `github public repository`를 검색 후 결과를 보여줍니다.

검색 창 우측 물음표를 클릭해보면 검색할 수 있는 조건들을 보여줍니다.

<img src="/assets/img/util/search_git_hub/help.png" width="300px" alt="help">

보자면 아래와 같은 상세 검색 조건을 지정할 수 있습니다.

```
- if, 정규식 등의 메서드 호출
- repository 지정, file 검색, language 지정
- diff, commit
- 기간 검색, author, branch
```
이 중 language 를 설정해서 검색하는 예제를 하나 보여드리겠습니다~!

---
<img src="/assets/img/util/search_git_hub/lang_auto_complete_1.png" alt="language_auto_complete_1">

검색창에 입력할려고 하면 입력바 하단에 자동완성으로 어떤 값을 넣어야할지 `힌트`를 주고 있습니다.

그리고 원하는 키워드를 선택 후 `tab` 버튼을 누르면 바로 자동 완성이 완료되는걸 볼 수 있어요!

<img src="/assets/img/util/search_git_hub/lang_auto_complete_2.png" alt="language_auto_complete_2">

`lang:Java Stream.of` 키워드로 검색해보겠습니다.

그 결과는...두둥!!

---
<img src="/assets/img/util/search_git_hub/search_result.png" alt="search_result">

어마 무시하네요... 제가 검색한 키워드를 `하이라이트`로 표시해주며

스크롤을 하단으로 내리면 내릴수록 더 많은 검색 결과를 조회해서 보여줍니다.

게다가 `intellij`를 사용하시는 분에게 좋은 소식 하나 더!

sourcegraph의 기능이 플러그인 형태로 제공되고 있다는 것!

<img src="/assets/img/util/search_git_hub/intellij_usage.png" alt="intellij_usage">

정말 다양하게 sourcegraph를 활용 할 수 있어서 개발하는데 나름 도움이 될 듯 합니다.

그 외에 repository 코드를 모니터링하여 코드 변경점이 있을때마다 `noti`가 오도록 한다던가..

<img src="/assets/img/util/search_git_hub/code_monitoring.png" alt="code_monitor">

`extensions` 기능으로 더욱 더 확장하여 사용 할 수 있습니다.

<img src="/assets/img/util/search_git_hub/extension.png" alt="extension">

끝.

---

## 검증 및 보강 — 2026-10-24

이 글의 확장 프로그램 화면은 2021년 기록으로 현재 UI나 제공 기능을 보장하지 않습니다. Sourcegraph 검색식의 `repo:`, `lang:`, `file:`를 함께 사용해 범위를 좁히고, 검색 결과의 저장소·브랜치·라이선스와 마지막 변경 시점을 확인하세요. 공개 Sourcegraph 인스턴스와 사내 인스턴스는 검색 대상과 접근 권한이 다릅니다. 비공개 코드를 공개 검색 서비스에 입력하는 절차로 해석하면 안 됩니다.

### 확인한 자료

- [공식 자료 1](https://sourcegraph.com/docs/getting-started)
- [공식 자료 2](https://sourcegraph.com/docs/code-search/queries)
