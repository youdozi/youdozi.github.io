---
layout: posts
title: "[dev] 주간 기술 아티클 다이제스트"
date: 2026-09-15 09:08:52 +0900
categories:
  - dev
  - digest
tags:
  - ai
  - data
  - java
  - web
generated_by: content-pipeline
disclaimer: "원문을 재배포하지 않고 핵심 포인트와 링크만 제공합니다."
---

## 이번 다이제스트 기준

- 공식 기술 블로그/검증된 매체 RSS 중심으로 수집
- 최신성(최근 7일), 기술 밀도, 중복 여부 기준으로 선별
- 원문 전체 복제 없이 핵심 포인트 + 출처 링크만 정리

## 핵심 아티클

### 1. Java News Roundup: New OpenJDK JEPs, CDI 5.0, Spring, Open Liberty, RefactorFirst, ADK for Kotlin

- 출처: InfoQ
- 발행일: 2026-09-15 05:15 (KST)
- 링크: [https://www.infoq.com/news/2026/09/java-news-roundup-sep07-2026/](https://www.infoq.com/news/2026/09/java-news-roundup-sep07-2026/)
- 한줄 요약: This week's Java roundup for September 7th, 2026, features news highlighting: new JEPs for ahead-of-time compilation and structured concurrency; GA releases of Jakarta CDI 5.0 and ADK for Kotlin 1.0; the September 2026 edition of Open Liberty; point releases of TornadoVM and RefactorFirst; a maintenance release of Micronaut; and first releases candidates of Groovy 6.0 and Gradle 9.8. By Michael Redlich
- 왜 중요한가: 개발 생산성 자동화나 서비스 기능 고도화에 적용 가능한 흐름입니다.

### 2. Jotai 3.0 Ships as a Modernized, ESM-Only Package That Drops Legacy Builds and Deprecated APIs

- 출처: InfoQ
- 발행일: 2026-09-14 15:46 (KST)
- 링크: [https://www.infoq.com/news/2026/09/jotai-3-released/](https://www.infoq.com/news/2026/09/jotai-3-released/)
- 한줄 요약: Jotai, an atomic state management library for React, has released version 3.0.0, now exclusively using ES modules. It maintains backward compatibility but removes some deprecated APIs. Migration is straightforward for most users. This version emphasizes a leaner core with improvements while deferring significant feature changes for future updates. By Daniel Curtis
- 왜 중요한가: 개발 생산성 자동화나 서비스 기능 고도화에 적용 가능한 흐름입니다.

### 3. Agoda Replaces 72-Shard SQL Server Price Cache with DragonflyDB

- 출처: InfoQ
- 발행일: 2026-09-14 22:48 (KST)
- 링크: [https://www.infoq.com/news/2026/09/agoda-price-cache-dragonflydb/](https://www.infoq.com/news/2026/09/agoda-price-cache-dragonflydb/)
- 한줄 요약: Agoda migrated its 1.5 TB hotel Price Cache from 72 SQL Server shards to DragonflyDB to handle growing read and write volumes. The migration used staged dual reads, parity validation, gradual traffic shifting, and decentralized failover detection. Agoda reports an approximately eightfold reduction in P99 read latency, with two DragonflyDB clusters providing high availability. By Leela Kumili
- 왜 중요한가: 개발 생산성 자동화나 서비스 기능 고도화에 적용 가능한 흐름입니다.

### 4. Article: Implementing Durable Workflows on Postgres Without an External Orchestrator

- 출처: InfoQ
- 발행일: 2026-09-14 20:00 (KST)
- 링크: [https://www.infoq.com/articles/durable-workflows-postgres/](https://www.infoq.com/articles/durable-workflows-postgres/)
- 한줄 요약: Postgres can serve as the durable state store and coordination layer for workflows, eliminating the need for an external orchestrator. SKIP LOCKED enables concurrent work processing, primary-key checkpoints enforce idempotency, and leases support crash recovery. Workflow sleeps and human approvals can also be persisted as database state and survive restarts. By Raman Varma
- 왜 중요한가: 데이터 처리량, 조회 성능, 운영 관측성 개선에 참고할 만한 주제입니다.

### 5. Podcast: How Will We Train Developers If AI Does the Routine Work: A Conversation with Scott Hanselman

- 출처: InfoQ
- 발행일: 2026-09-14 20:00 (KST)
- 링크: [https://www.infoq.com/podcasts/train-developers-ai-routine-work/](https://www.infoq.com/podcasts/train-developers-ai-routine-work/)
- 한줄 요약: In this podcast, Michael Stiefel spoke to Scott Hanselman about developing new software engineers when artificial intelligence agents are doing most of the work on which junior developers were trained. Hanselman suggests the software industry should adopt a preceptorship model similar to the nursing profession. By Scott Hanselman
- 왜 중요한가: 개발 생산성 자동화나 서비스 기능 고도화에 적용 가능한 흐름입니다.

### 6. Presentation: Decision Models in Agentic Architectures: From Production to Agent Skills

- 출처: InfoQ
- 발행일: 2026-09-14 20:00 (KST)
- 링크: [https://www.infoq.com/presentations/decision-models-agentic-ai/](https://www.infoq.com/presentations/decision-models-agentic-ai/)
- 한줄 요약: Alex Porcelli discusses the critical gap in enterprise AI: non-deterministic output and lack of accountability in high-stakes decisions. He shares how integrating DMN decision models with LLMs, agent skills, and NeMo guardrails creates auditable, deterministic agentic architectures - allowing business leaders to own decision logic while engineers maintain robust architectural governance. By Alex Porcelli
- 왜 중요한가: 개발 생산성 자동화나 서비스 기능 고도화에 적용 가능한 흐름입니다.

## 활용 가이드

1. 업무와 직접 연결되는 항목 2개만 먼저 읽고 팀 위키에 메모를 남깁니다.
2. 다음 스프린트에서 적용 가능한 변경점(버전, 아키텍처, 운영지표)을 추려 액션 아이템으로 분리합니다.

---
이 글은 자동 파이프라인으로 생성되며, 품질 기준을 통과한 항목만 게시됩니다.
