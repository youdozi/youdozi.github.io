---
layout: posts 
title:  "[springboot] springboot work internally"
date:   2023-09-11 00:00:00 +0900 
categories: 
  - springboot
tags:
  - springboot
  - history
---
### springboot 탄생 배경
springboot란 spring framework를 좀 더 쉽게 개발/배포할려는 목적으로 만들어 졌습니다.  
2012년 Mike Youngstrom은 spring 프레임워크에서 컨테이너 없는 웹 애플리케이션 아키텍처에 대한 지원을 요청하는 spring jira 기능 요청을 작성했습니다.  
해당 지라를 정리해보면 아래와 같습니다.
* Servlet 구성 요소 모델의 지식이 필요하지 않는 통합 컴포넌트 모델을 제공합니다.
* 컴포넌트 및 애플리케이션 구성을 위해 개발자가 학습해야 하는 것은 하나의 스프링 구성 모델뿐입니다.
* `void main`으로 애플리케이션 시작 및 종료를 간소화합니다.
* 더 간단한 순수 자바 클래스 로딩 계층을 갖고 있습니다.
* 개발 도구가 더 간단해야 합니다. 복잡한 IDE를 사용하여 WAR 파일을 생성하고 개발 컨테이너에 배포하는 대신 애플리케이션의 Main 클래스를 실행하면 됩니다.

[참고 - quickprogrammingtips](https://www.quickprogrammingtips.com/spring-boot/history-of-spring-framework-and-spring-boot.html)

위 요청 지라는 아직도 존재하고 있으니 한번 확인해 보면 좋을 것 같습니다.  

[https://jira.spring.io/browse/SPR-9888](https://jira.spring.io/browse/SPR-9888)

이후 2014년 4월에 최초의 springboot 1.0이 release 되었습니다.  
그 후 아래와 같이 마이너 버전이 계속 해서 release 되었지요.  
* Spring boot 1.1 (2014년 6월) - 향상된 템플릿 지원, gemfire 지원, elasticsearch 및 apache solr에 대한 자동 구성.
* Spring boot 1.2 (2015년 3월) - servlet 3.1/tomcat 8/jetty 9로 업그레이드, spring 4.1 업그레이드, 배너/jms/SpringBootApplication 주석 지원.
* Spring boot 1.3 (2016년 12월) - spring 4.2 업그레이드, 새로운 spring-boot-devtools, 캐싱 기술(ehcache, hazelcast, redis, guava 및 infinispan)을 위한 자동 구성 및 완전히 실행 가능한 jar 지원.
* Spring 부트 1.4 (2017년 1월) - Spring 4.3 업그레이드, Couchbase/neo4j 지원, 시작 실패 분석 및 RestTemplateBuilder.
* Spring boot 1.5 (2017년 2월) - kafka/ldap 지원, 타사 라이브러리 업그레이드, CRaSH 지원 중단 및 Actuator 로거 엔드포인트를 통해 즉시 애플리케이션 로그 수준을 수정합니다.
