---
layout: posts
title: "[dev] 주간 기술 아티클 다이제스트"
date: 2026-09-21 08:46:27 +0900
categories:
  - dev
  - digest
tags:
  - ai
  - cloud
  - java
  - security
  - web
generated_by: content-pipeline
disclaimer: "원문을 재배포하지 않고 핵심 포인트와 링크만 제공합니다."
---

## 이번 다이제스트 기준

- 공식 기술 블로그/검증된 매체 RSS 중심으로 수집
- 최신성(최근 7일), 기술 밀도, 중복 여부 기준으로 선별
- 원문 전체 복제 없이 핵심 포인트 + 출처 링크만 정리

## 핵심 아티클

### 1. Bun Rewrites 535K Lines of Zig into Rust in Four Months, Eliminates Numerous Memory Leaks

- 출처: InfoQ
- 발행일: 2026-09-21 04:51 (KST)
- 링크: [https://www.infoq.com/news/2026/09/bun-AI-rewrite-zig-rust-4-months/](https://www.infoq.com/news/2026/09/bun-AI-rewrite-zig-rust-4-months/)
- 한줄 요약: Bun creator Jarred Sumner recently announced that Bun, the JavaScript/TypeScript runtime, bundler and package manager has been rewritten from Zig to Rust. The rewrite seeks to eliminate recurrent memory safety vulnerabilities via Rust’s borrow checker. The AI-assisted rewrite was released after 4 months of work instead of the estimated one year. By Bruno Couriol
- 왜 중요한가: 개발 생산성 자동화나 서비스 기능 고도화에 적용 가능한 흐름입니다.

### 2. Google Agent Development Kit for Kotlin Reaches Feature Parity with Python, Supports On-Device AI

- 출처: InfoQ
- 발행일: 2026-09-20 19:00 (KST)
- 링크: [https://www.infoq.com/news/2026/09/google-adk-1-0-released/](https://www.infoq.com/news/2026/09/google-adk-1-0-released/)
- 한줄 요약: Google has released the Agent Development Kit (ADK) for Kotlin 1.0, a production-ready framework for building AI agents across Kotlin, Android, and JVM/server applications. It brings Kotlin to feature parity with Google's ADK for Python and Java, while adding Android-specific capabilities for on-device and hybrid AI. By Sergio De Simone
- 왜 중요한가: 개발 생산성 자동화나 서비스 기능 고도화에 적용 가능한 흐름입니다.

### 3. Alibaba Open Sources OpenCodeReview for AI-Assisted Code Review

- 출처: InfoQ
- 발행일: 2026-09-20 20:57 (KST)
- 링크: [https://www.infoq.com/news/2026/09/alibaba-opencodereview/](https://www.infoq.com/news/2026/09/alibaba-opencodereview/)
- 한줄 요약: Alibaba recently open-sourced OpenCodeReview, an AI-powered code review CLI that combines deterministic pipelines for file selection, bundling, and rule matching with an LLM agent for dynamic code analysis. It supports built-in checks for issues such as null-pointer exceptions, thread safety, XSS, and SQL injection. By Renato Losio
- 왜 중요한가: 개발 생산성 자동화나 서비스 기능 고도화에 적용 가능한 흐름입니다.

### 4. Cloudflare Measures Origin TLS Preferences, Cutting Handshake Retries from 52% to 3.7%

- 출처: InfoQ
- 발행일: 2026-09-20 17:15 (KST)
- 링크: [https://www.infoq.com/news/2026/09/cloudflare-automatic-key-exchang/](https://www.infoq.com/news/2026/09/cloudflare-automatic-key-exchang/)
- 한줄 요약: Cloudflare has replaced its static X25519 guess for origin TLS handshakes with per-origin measurement. HelloRetryRequests on scanned origins fell from roughly 52% to 3.7%, removing over 150 ms from p90 latency. Post-quantum connections completing in one round trip rose from 0% to 99.2%, though only 12.8% of origins support it. By Steef-Jan Wiggers
- 왜 중요한가: 인프라 운영비나 배포 안정성에 바로 영향을 줄 수 있는 주제입니다.

### 5. Presentation: Complexity and Creativity in Software Engineering

- 출처: InfoQ
- 발행일: 2026-09-18 20:00 (KST)
- 링크: [https://www.infoq.com/presentations/ai-software-engineering-complexity/](https://www.infoq.com/presentations/ai-software-engineering-complexity/)
- 한줄 요약: Phillip Mortimer discusses the shift toward write-only software driven by AI code generation. He explains why traditional pull requests are broken and shares how engineering leaders can manage complexity by decoupling intent from implementation, automating code reviews, and building self-healing architecture to unleash developer creativity across senior engineering and architecture teams. By Phillip Mortimer
- 왜 중요한가: 개발 생산성 자동화나 서비스 기능 고도화에 적용 가능한 흐름입니다.

### 6. Ktor 3.6.0 Is Now Available!

- 출처: JetBrains Blog
- 발행일: 2026-09-18 19:45 (KST)
- 링크: [https://blog.jetbrains.com/ktor/2026/09/18/ktor-3-6-0-is-now-available/](https://blog.jetbrains.com/ktor/2026/09/18/ktor-3-6-0-is-now-available/)
- 한줄 요약: Ktor 3.6.0 is here! This release is full of new experimental features, including typed authentication capabilities with specialized support for OpenID Connect and HTTP/3 support for the Netty engine. There are also a few quality-of-life improvements for routing and request handling, more convenient defaults for Kotlin Multiplatform clients, and more. Check out What&#8217;s new in [&#8230;]
- 왜 중요한가: 개발 생산성 자동화나 서비스 기능 고도화에 적용 가능한 흐름입니다.

## 활용 가이드

1. 업무와 직접 연결되는 항목 2개만 먼저 읽고 팀 위키에 메모를 남깁니다.
2. 다음 스프린트에서 적용 가능한 변경점(버전, 아키텍처, 운영지표)을 추려 액션 아이템으로 분리합니다.

---
이 글은 자동 파이프라인으로 생성되며, 품질 기준을 통과한 항목만 게시됩니다.
