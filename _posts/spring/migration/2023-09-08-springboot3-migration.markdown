---
layout: posts 
title:  "[springboot] springboot3 migration"
date:   2023-09-08 00:00:00 +0900 
categories: 
  - springboot
tags:
  - springboot
  - springboot3
  - springboot3 migration
---
### 개요
2022년 하반기에 springboot3가 공식 release 되었습니다.  
springboot2가 2018년 상반기에 release되고 나서 새롭게 판올림 버전으로  
가장 큰 변화로는 아래와 같습니다.  
* spring framework 6 적용
* 최소 사양 JDK 17
* javax -> jakarta 패키지 변경
* GraalVM 네이티브 이미지 지원

### 굳이 springboot3로 업그레이드 해야할까?
새로운 프로젝트는 springboot3로 시작해도 문제가 없겠지만  
기존 springboot2.x 프로젝트를 마이그레이션해야할 필요성은 분명 있습니다.  
2021년 11월에 발생한 log4shell 취약점과 같은 이슈를 피하기 위해서는  
레거시화된 프로젝트에 대한 버전업 관리도 필요하다고 생각됩니다.  
그리고 개인적으로는 JDK 21의 가상스레드를 spring framework 6.1부터 지원하기 때문에 미리 판올림을 하는 것도 나쁘지 않다 생각됩니다.

### 마이그레이션에 어려움은 없을까?
마이그레이션 작업시 제일 염려되는 것은 무엇일까요?  
당연히 기존에 잘 동작하던 비지니스가 마이그레이션 이후 제대로 작동 되지 않는 부분 아니겠습니까?  
또한 레퍼런스가 많이 없다는 것도 충분히 생각해볼 수 있죠.  
하지만 spring에서는 친절하게 springboot3 migration 문서를 제공해줬죠.

[springboot3 migration 문서](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.0-Migration-Guide)

그런데.. 이것으로 끝은 아닙니다.  
migration문서에는 나와 있지 않는 서드파티 라이브러리 문제가 있죠.  
이 부분을 공유할까 합니다.

### QueryDSL
JPA와 영혼의 찰떡 궁합이었던 querydsl은 2021년 릴리즈를 마지막으로  
javax -> jakarta 패키징 변경, hibernate 6 지원에 대한 어마어마한 이슈를  
우리에게 선물하였습니다.  
querydsl github 이슈 등록 건수도 어마어마하고 관리는 계속 할 수 있나 싶었습니다.  
서론이 길었네요. 우선 springboot3에서 가동할 수 있도록 수정해 보겠습니다.
