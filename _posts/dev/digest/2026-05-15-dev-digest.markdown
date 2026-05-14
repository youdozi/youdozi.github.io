---
layout: posts
title: "[dev] 주간 기술 아티클 다이제스트"
date: 2026-05-15 07:52:30 +0900
categories:
  - dev
  - digest
tags:
  - ai
  - cloud
  - security
generated_by: content-pipeline
disclaimer: "원문을 재배포하지 않고 핵심 포인트와 링크만 제공합니다."
---

## 이번 다이제스트 기준

- 공식 기술 블로그/검증된 매체 RSS 중심으로 수집
- 최신성(최근 7일), 기술 밀도, 중복 여부 기준으로 선별
- 원문 전체 복제 없이 핵심 포인트 + 출처 링크만 정리

## 핵심 아티클

### 1. Kubernetes v1.36: Security Defaults Tighten as AI Workload Support Matures

- 출처: InfoQ
- 발행일: 2026-05-14 17:00 (KST)
- 링크: [https://www.infoq.com/news/2026/05/kubernetes-1-36-released/](https://www.infoq.com/news/2026/05/kubernetes-1-36-released/)
- 한줄 요약: Kubernetes v1.36, released in 2026, includes 70 enhancements focused on security, AI workloads, and API scalability. Key features graduating to General Availability are User Namespaces, Mutating Admission Policies, and Fine-Grained Kubelet API Authorization. The release also addresses workload management and introduces new features for AI resource allocations. By Matt Saunders
- 왜 중요한가: 개발 생산성 자동화나 서비스 기능 고도화에 적용 가능한 흐름입니다.

### 2. Copilot cloud agent supports auto model selection

- 출처: GitHub Changelog
- 발행일: 2026-05-14 21:59 (KST)
- 링크: [https://github.blog/changelog/2026-05-14-copilot-cloud-agent-supports-auto-model-selection](https://github.blog/changelog/2026-05-14-copilot-cloud-agent-supports-auto-model-selection)
- 한줄 요약: Copilot cloud agent now supports Copilot auto model selection. When you select Auto in the model picker, Copilot intelligently selects the best available model based on system health and model&#8230; The post Copilot cloud agent supports auto model selection appeared first on The GitHub Blog .
- 왜 중요한가: 개발 생산성 자동화나 서비스 기능 고도화에 적용 가능한 흐름입니다.

### 3. Moonrepo Releases Moon v2.0 with WASM Plugin Toolchains and Overhauled CLI

- 출처: InfoQ
- 발행일: 2026-05-14 21:47 (KST)
- 링크: [https://www.infoq.com/news/2026/05/moonrepo-2-release/](https://www.infoq.com/news/2026/05/moonrepo-2-release/)
- 한줄 요약: Moonrepo has released moon v2.0, its first major update since v1, featuring a plugin-based toolchain system and support for multiple configuration formats including JSON and TOML. The CLI has been restructured, enhancing task inheritance and Docker integration. Notable changes include a shift in architecture and improvements to VCS support. By Daniel Curtis
- 왜 중요한가: 개발 생산성 자동화나 서비스 기능 고도화에 적용 가능한 흐름입니다.

### 4. Pinterest Engineers Eliminate CPU Zombies to Resolve Production Bottlenecks

- 출처: InfoQ
- 발행일: 2026-05-14 19:00 (KST)
- 링크: [https://www.infoq.com/news/2026/05/pinterest-cpu-zombies-bottleneck/](https://www.infoq.com/news/2026/05/pinterest-cpu-zombies-bottleneck/)
- 한줄 요약: Pinterest identified and resolved CPU starvation issues that affected machine learning training jobs on its Kubernetes-based platform, PinCompute. The engineers traced the problem to an unused Amazon ECS agent, which caused memory cgroup leaks. By disabling the agent, they stabilised performance. This case illustrates the importance of understanding system defaults for effective troubleshooting. By Mark Silvester
- 왜 중요한가: 개발 생산성 자동화나 서비스 기능 고도화에 적용 가능한 흐름입니다.

### 5. GitHub Actions: Upcoming image migrations

- 출처: GitHub Changelog
- 발행일: 2026-05-15 03:31 (KST)
- 링크: [https://github.blog/changelog/2026-05-14-github-actions-upcoming-image-migrations](https://github.blog/changelog/2026-05-14-github-actions-upcoming-image-migrations)
- 한줄 요약: There are two upcoming image migrations customers should be aware of, and GitHub is transitioning to owning the Arm64 images for hosted runners. Arm64 runner images now maintained by GitHub&#8230; The post GitHub Actions: Upcoming image migrations appeared first on The GitHub Blog .
- 왜 중요한가: 개발 생산성 자동화나 서비스 기능 고도화에 적용 가능한 흐름입니다.

### 6. GitHub Copilot app is now available in technical preview

- 출처: GitHub Changelog
- 발행일: 2026-05-15 01:10 (KST)
- 링크: [https://github.blog/changelog/2026-05-14-github-copilot-app-is-now-available-in-technical-preview](https://github.blog/changelog/2026-05-14-github-copilot-app-is-now-available-in-technical-preview)
- 한줄 요약: The GitHub Copilot app is now in technical preview. It&#8217;s a GitHub-native desktop experience to start agentic development from the work in front of you, keep it isolated, steer it&#8230; The post GitHub Copilot app is now available in technical preview appeared first on The GitHub Blog .
- 왜 중요한가: 개발 생산성 자동화나 서비스 기능 고도화에 적용 가능한 흐름입니다.

## 활용 가이드

1. 업무와 직접 연결되는 항목 2개만 먼저 읽고 팀 위키에 메모를 남깁니다.
2. 다음 스프린트에서 적용 가능한 변경점(버전, 아키텍처, 운영지표)을 추려 액션 아이템으로 분리합니다.

---
이 글은 자동 파이프라인으로 생성되며, 품질 기준을 통과한 항목만 게시됩니다.
