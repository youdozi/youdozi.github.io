---
title: "[jdk] temurin jdk21 release"
language: "ko"
translationKey: "2023-10-10-temurin-jdk21-delay"
routeSlug: "2023-10-10-temurin-jdk21-delay"
kind: "post"
publishedAt: "2023-10-11T15:00:00.000Z"
categories:
  - "jdk"
tags:
  - "jdk21"
  - "adoptium"
  - "temurin"
legacyUrl: "/jdk/temurin-jdk21-delay/"
legacySource: "_posts/jdk/temurin-jdk21-delay/2023-10-10-temurin-jdk21-delay.markdown"
updatedAt: "2026-10-24T09:00:00+09:00"
reviewedAt: "2026-10-24"
reviewStatus: "revised"
reviewScope: "공식 문서 대조 및 예제 코드 검토"
archiveBodySha256: "5519b6e2fa9b53ce085d356b1235f1b40a19952b3d869195f85000d800aa25d3"
reviewSources:
  - "https://adoptium.net/news/2023/09/temurin21-delay"
  - "https://github.com/adoptium/temurin21-binaries/releases"
---
## jdk 21 출시!!

2023년 9월 19일 jdk21이 release 되었으나 adoptium의 release가 계속되어 지연되고 있었습니다.  
jdk21이 release 되기 불과 몇일 전에 TCK(Technology Compatibility Kit) 인증에 새로운 라이선스가 있다는 글을 보았습니다.
이것으로 인한 법적 해석과 절차로 인해 늦어진다고 하더군요.  
공식 발표는 TCK 관련 계약·법률 검토 때문에 검증 진행이 지연됐다고 설명합니다. 다른 공급자의 상황만으로 특정 조직의 과실이라고 단정할 근거는 없습니다.

하지만 오래 걸릴 것으로 예상했으나 2023년 10월 10일 TCK 인증 테스트 절차에 들어간다는 소식이 업데이트 되었습니다. 
TCK 진행과 최종 바이너리 공개는 별도 단계이므로 실제 배포 여부와 날짜는 릴리스 페이지에서 확인해야 합니다.

아래 github release를 확인해주세요!

[https://github.com/adoptium/temurin21-binaries](https://github.com/adoptium/temurin21-binaries)

참고 - [https://adoptium.net/blog/2023/09/temurin21-delay/](https://adoptium.net/blog/2023/09/temurin21-delay/)

## 검증 및 보강 — 2026-10-24

이 글은 2023년 첫 Temurin 21 릴리스 지연에 관한 기록입니다. 현재도 배포가 지연 중이라는 의미가 아닙니다. 공식 지연 공지의 날짜별 업데이트와 `temurin21-binaries`의 개별 릴리스 자산을 함께 확인하세요. 바이너리를 사용할 때는 운영체제·CPU·JDK/JRE·체크섬을 구분해야 합니다.

### 확인한 자료

- [공식 자료 1](https://adoptium.net/news/2023/09/temurin21-delay)
- [공식 자료 2](https://github.com/adoptium/temurin21-binaries/releases)
