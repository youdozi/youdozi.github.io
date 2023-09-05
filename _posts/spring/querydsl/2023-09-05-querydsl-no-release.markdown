---
layout: posts 
title:  "[querydsl] querydsl No release for a long time"
date:   2023-09-05 00:00:00 +0900 
categories: 
  - querydsl
  - springboot3
  - jpa
  - jooq
tags:
  - querydsl
  - springboot3
  - jpa
  - jooq
---
### 개요
JPA를 spring data jpa + querydsl과의 조합으로 접하는 경우가 많습니다.  
spring data jpa에서 제공해주는 specification으로도 충분히 해낼수 있지만  
querydsl에 비할바는 아닙니다.  
entity에 wrapper Q클래스를 생성하여 type-safe하게 사용할 수 있는 장점은 누구나 인정하는 바입니다.  
다만 springboot 3로 메이저 업데이트되면서 querydsl을 계속 유지해야 하는가  
하는 의구심이 들기 시작했습니다.  
2021년 7월 이후 새로운 release가 없고 springboot 3의 javax에서 jakarta 전환, hibernate 6 미지원의 이슈가 발생하고 있습니다.  
공식 github에서도 많은 유저들이 querydsl의 지속성에 대해 의구심을 가지고 있는것 가운데..  
querydsl을 대체할 수 있는 라이브러리는 무엇이 있을까요?  
몇가지 정리해보도록 하겠습니다.

### JOOQ
[https://www.jooq.org/](https://www.jooq.org/)  
