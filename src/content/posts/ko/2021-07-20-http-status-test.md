---
title: "[유틸리티] Mock Http Status Test"
language: "ko"
translationKey: "2021-07-20-http-status-test"
routeSlug: "2021-07-20-http-status-test"
kind: "post"
publishedAt: "2021-07-19T22:40:30.000Z"
categories:
  - "util"
tags:
  - "util"
  - "mock"
  - "http-status-code"
legacyUrl: "/util/http-status-test/"
legacySource: "_posts/util/2021-07-20-http-status-test.markdown"
updatedAt: "2026-10-24T09:00:00+09:00"
reviewedAt: "2026-10-24"
reviewStatus: "revised"
reviewScope: "공식 문서 대조 및 예제 코드 검토"
archiveBodySha256: "6a5acf144ac5c86b519c04778300425bd1258f9cf0f65d3a1bf753bd55713d96"
reviewSources:
  - "https://www.rfc-editor.org/rfc/rfc9110.html#name-status-codes"
  - "https://docs.spring.io/spring-framework/reference/web/webflux-webclient/client-testing.html"
---
외부 통신에 대한 Error 처리는 앱을 더욱 더 견고하게 만들 수 있습니다.
Error 처리를 위해 엔드포인트에 대한 Http Status Code를 억지로 생성하는것은 매우 귀찮은 일이라고 할까요?
보다 간편하게 Mock 서버를 두는게 더 효율적이라고 볼 수 있습니다.

---
[https://savanttools.com/test-http-status-codes](https://savanttools.com/test-http-status-codes)

http status code를 return 해주는 고마운 사이트입니다!

<img src="/assets/img/util/http-status-code-1.png" alt="mock server">

위 http status code 링크를 따라가면 아래와 같은 화면이 나옵니다.

<img src="/assets/img/util/http-status-code-2.png" alt="mock server detail">

여기서 url 주소를 복사해서 postman같은 API 테스트툴로 돌려보면 어떻게 될까요?

웹 브라우저 URL을 복사해보도록 하겠습니다!

<img src="/assets/img/util/http-status-code-3.png" alt="browser url copy">

복사한 URL 주소를 그대로 postman에 태워보면...

<img src="/assets/img/util/http-status-code-200.png" alt="postman 200 ok">

빨간 사각 하이라이트를 보면 http status code 200을 return 해주는 걸 볼 수 있습니다!

다른 http status code도 요청해보면..

<img src="/assets/img/util/http-status-code-201.png" alt="postman 201 ok">
<p>
<img src="/assets/img/util/http-status-code-404.png" alt="postman 404 ok">
<p>
<img src="/assets/img/util/http-status-code-500.png" alt="postman 500 ok">

사용자 입장에서 필요한 http status code 모두 손쉽게 받을 수 있습니다!

가끔 http status code mock 서버 구축에 시간이 걸리고 어렵다면 위 사이트를 이용해 보는 것을 추천합니다!

## 검증 및 보강 — 2026-10-24

외부 상태 코드 응답 사이트는 빠른 수동 확인용입니다. CI 테스트가 외부 사이트의 네트워크·인증서·가용성에 종속되면 재현성이 떨어집니다. 상태 코드 외에도 Content-Type, 본문, 지연 시간, 연결 종료를 독립적으로 제어하는 로컬 MockWebServer 같은 도구를 사용하는 편이 테스트 목적에 맞습니다. 200과 JSON 본문, 500과 HTML 본문, 타임아웃을 별도 케이스로 검증하세요. 상태 코드 자체의 의미는 HTTP 표준을 기준으로 확인합니다.

### 확인한 자료

- [공식 자료 1](https://www.rfc-editor.org/rfc/rfc9110.html#name-status-codes)
- [공식 자료 2](https://docs.spring.io/spring-framework/reference/web/webflux-webclient/client-testing.html)
