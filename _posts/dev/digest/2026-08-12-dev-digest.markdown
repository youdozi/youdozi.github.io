---
layout: posts
title: "[dev] 주간 기술 아티클 다이제스트"
date: 2026-08-12 07:34:52 +0900
categories:
  - dev
  - digest
tags:
  - ai
  - data
generated_by: content-pipeline
disclaimer: "원문을 재배포하지 않고 핵심 포인트와 링크만 제공합니다."
---

## 이번 다이제스트 기준

- 공식 기술 블로그/검증된 매체 RSS 중심으로 수집
- 최신성(최근 7일), 기술 밀도, 중복 여부 기준으로 선별
- 원문 전체 복제 없이 핵심 포인트 + 출처 링크만 정리

## 핵심 아티클

### 1. GitHub Enterprise Server 3.22 release candidate

- 출처: GitHub Changelog
- 발행일: 2026-08-12 05:26 (KST)
- 링크: [https://github.blog/changelog/2026-08-11-github-enterprise-server-3-22-release-candidate](https://github.blog/changelog/2026-08-11-github-enterprise-server-3-22-release-candidate)
- 한줄 요약: GitHub Enterprise Server (GHES) 3.22 is now available and introduces new capabilities across the platform. Here are a few highlights in the 3.22 release: Administrators can configure Copilot CLI to&#8230; The post GitHub Enterprise Server 3.22 release candidate appeared first on The GitHub Blog .
- 왜 중요한가: 개발 생산성 자동화나 서비스 기능 고도화에 적용 가능한 흐름입니다.

### 2. Copilot memory and Ollama in GitHub Copilot for JetBrains

- 출처: GitHub Changelog
- 발행일: 2026-08-12 05:15 (KST)
- 링크: [https://github.blog/changelog/2026-08-11-copilot-memory-and-ollama-in-github-copilot-for-jetbrains](https://github.blog/changelog/2026-08-11-copilot-memory-and-ollama-in-github-copilot-for-jetbrains)
- 한줄 요약: This update brings persistent memory, local model access, and more enterprise controls to GitHub Copilot for JetBrains. It also improves everyday chat workflows and resolves reliability issues across MCP servers,&#8230; The post Copilot memory and Ollama in GitHub Copilot for JetBrains appeared first on The GitHub Blog .
- 왜 중요한가: 개발 생산성 자동화나 서비스 기능 고도화에 적용 가능한 흐름입니다.

### 3. Upcoming deprecation of MAI-Code-1-Flash

- 출처: GitHub Changelog
- 발행일: 2026-08-12 03:50 (KST)
- 링크: [https://github.blog/changelog/2026-08-11-upcoming-deprecation-of-mai-code-1-flash](https://github.blog/changelog/2026-08-11-upcoming-deprecation-of-mai-code-1-flash)
- 한줄 요약: With the launch of MAI-Code-1.1-Flash, we will deprecate MAI-Code-1-Flash across all GitHub Copilot experiences on September 10, 2026: Model Deprecation date Suggested alternative MAI-Code-1-Flash 9-10-2026 MAI-Code-1.1-Flash Please update your workflows&#8230; The post Upcoming deprecation of MAI-Code-1-Flash appeared first on The GitHub Blog .
- 왜 중요한가: 개발 생산성 자동화나 서비스 기능 고도화에 적용 가능한 흐름입니다.

### 4. MAI-Code-1.1-Flash available in GitHub Copilot

- 출처: GitHub Changelog
- 발행일: 2026-08-12 03:13 (KST)
- 링크: [https://github.blog/changelog/2026-08-11-mai-code-1-1-flash-available-in-github-copilot](https://github.blog/changelog/2026-08-11-mai-code-1-1-flash-available-in-github-copilot)
- 한줄 요약: MAI-Code-1.1-Flash, Microsoft&#8217;s latest small-tier coding model, is now rolling out in GitHub Copilot. Building on MAI-Code-1-Flash, it adds native vision support for image understanding and delivers improvements across coding quality,&#8230; The post MAI-Code-1.1-Flash available in GitHub Copilot appeared first on The GitHub Blog .
- 왜 중요한가: 개발 생산성 자동화나 서비스 기능 고도화에 적용 가능한 흐름입니다.

### 5. Per-model token breakdown in the usage report

- 출처: GitHub Changelog
- 발행일: 2026-08-11 23:41 (KST)
- 링크: [https://github.blog/changelog/2026-08-11-per-model-token-breakdown-in-the-usage-report](https://github.blog/changelog/2026-08-11-per-model-token-breakdown-in-the-usage-report)
- 한줄 요약: You can now see a per-model breakdown of the tokens behind your AI credits in the usage report. For each model, the AI usage report shows the input, output, cache&#8230; The post Per-model token breakdown in the usage report appeared first on The GitHub Blog .
- 왜 중요한가: 개발 생산성 자동화나 서비스 기능 고도화에 적용 가능한 흐름입니다.

### 6. How Netflix Scaled Its Real-Time Service Map

- 출처: InfoQ
- 발행일: 2026-08-11 21:20 (KST)
- 링크: [https://www.infoq.com/news/2026/08/netflix-service-topology/](https://www.infoq.com/news/2026/08/netflix-service-topology/)
- 한줄 요약: Netflix has described how it redesigned the streaming pipeline behind Service Topology, its real-time service dependencies map, to support production scale. The system uses three stages to separate intermediary resolution from enrichment and persistence, propagates backpressure to Kafka rather than dropping records, and uses server-sent events instead of gRPC for high-volume internal transfers. By Eran Stiller
- 왜 중요한가: 데이터 처리량, 조회 성능, 운영 관측성 개선에 참고할 만한 주제입니다.

## 활용 가이드

1. 업무와 직접 연결되는 항목 2개만 먼저 읽고 팀 위키에 메모를 남깁니다.
2. 다음 스프린트에서 적용 가능한 변경점(버전, 아키텍처, 운영지표)을 추려 액션 아이템으로 분리합니다.

---
이 글은 자동 파이프라인으로 생성되며, 품질 기준을 통과한 항목만 게시됩니다.
