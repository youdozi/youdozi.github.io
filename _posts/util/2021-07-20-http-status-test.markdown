---
layout: posts
title:  "[유틸리티] Mock Http Status Test"
date:   2021-07-20 07:40:30 +0900
categories: 
    - Util 
    - HttpStatusCodeTest
tags: 
    - util
    - mock
    - http-status-code
---

외부 통신에 대한 Error 처리는 앱을 더욱 더 견고하게 만들 수 있습니다.
Error 처리를 위해 엔드포인트에 대한 Http Status Code를 억지로 생성하는것은 매우 귀찮은 일이라고 할까요?
보다 간편하게 Mock 서버를 두는게 더 효율적이라고 볼 수 있습니다.

---
[https://savanttools.com/test-http-status-codes](https://savanttools.com/test-http-status-codes){:target="_blank"}

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
