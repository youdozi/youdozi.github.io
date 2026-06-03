---
layout: posts
title: "[dev] 주간 기술 아티클 다이제스트"
date: 2026-06-04 08:28:42 +0900
categories:
  - dev
  - digest
tags:
  - ai
  - cloud
  - data
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

### 1. Article: Two Misconfigurations That Caused Spark OOM Failures on Kubernetes

- 출처: InfoQ
- 발행일: 2026-06-03 18:00 (KST)
- 링크: [https://www.infoq.com/articles/spark-oom-kubernetes-misconfigurations/](https://www.infoq.com/articles/spark-oom-kubernetes-misconfigurations/)
- 한줄 요약: After migrating Spark pipelines to Azure Kubernetes Service, two infrastructure settings interacted destructively: spark.kubernetes.local.dirs.tmpfs=true backed shuffle spill with RAM instead of disk, and a hard podAffinity rule forced all executors onto one node. Together, they caused repeated OOM kills invisible to standard diagnostics. By Pranav Bhasker
- 왜 중요한가: 개발 생산성 자동화나 서비스 기능 고도화에 적용 가능한 흐름입니다.

### 2. Inside Google’s System for Coordinated A/B Testing Across Its Global Service Fleet

- 출처: InfoQ
- 발행일: 2026-06-03 23:54 (KST)
- 링크: [https://www.infoq.com/news/2026/06/google-fleet-ab-experimentation/](https://www.infoq.com/news/2026/06/google-fleet-ab-experimentation/)
- 한줄 요약: Google has shared details of its fleet wide large scale A/B experimentation system designed to standardize experiment assignment, exposure logging, and configuration propagation across distributed services. The approach enables consistent measurement across products, reduces experiment conflicts, and improves reliability of data driven decision making at scale. By Leela Kumili
- 왜 중요한가: 개발 생산성 자동화나 서비스 기능 고도화에 적용 가능한 흐름입니다.

### 3. IntelliJ IDEA 2025.3.6 Is Out!

- 출처: JetBrains Blog
- 발행일: 2026-06-03 22:12 (KST)
- 링크: [https://blog.jetbrains.com/idea/2026/06/intellij-idea-2025-3-6/](https://blog.jetbrains.com/idea/2026/06/intellij-idea-2025-3-6/)
- 한줄 요약: IntelliJ IDEA 2025.3.6 is now available with the latest Oracle critical patch update for Java 21. The update includes the corresponding JetBrains Runtime changes and fixes the issue [IDEA-389015], providing improved reliability and security. You can update to this version from inside the IDE, using the Toolbox App, or using snaps if you are a [&#8230;]
- 왜 중요한가: 개발 생산성 자동화나 서비스 기능 고도화에 적용 가능한 흐름입니다.

### 4. Node.js Moves to One Major Release Per Year, Starting with Node 27

- 출처: InfoQ
- 발행일: 2026-06-03 15:40 (KST)
- 링크: [https://www.infoq.com/news/2026/06/nodejs-release-changes/](https://www.infoq.com/news/2026/06/nodejs-release-changes/)
- 한줄 요약: Node.js will change its release schedule starting with version 27 in October 2026, moving from two major releases per year to one. All releases will become Long-Term Support (LTS), removing the distinction between odd and even versions. An Alpha channel for early testing will also be introduced. This decision addresses maintenance challenges and aims to align with user needs. By Daniel Curtis
- 왜 중요한가: 개발 생산성 자동화나 서비스 기능 고도화에 적용 가능한 흐름입니다.

### 5. Async VFS Content Writes – What Plugin Authors Need to Know

- 출처: JetBrains Blog
- 발행일: 2026-06-04 05:20 (KST)
- 링크: [https://blog.jetbrains.com/platform/2026/06/async-vfs-content-writes-what-plugin-authors-need-to-know/](https://blog.jetbrains.com/platform/2026/06/async-vfs-content-writes-what-plugin-authors-need-to-know/)
- 한줄 요약: Some plugin code follows this pattern: Historically, it was reasonable to assume that once the save finishes, the file on disk already contains the latest editor text. That is no longer guaranteed. The IntelliJ Platform can now update the VFS first and finish the disk write in the background a bit later. Code that reads [&#8230;]
- 왜 중요한가: 개발 생산성 자동화나 서비스 기능 고도화에 적용 가능한 흐름입니다.

### 6. GitHub Copilot in Visual Studio Code, May releases

- 출처: GitHub Changelog
- 발행일: 2026-06-03 22:30 (KST)
- 링크: [https://github.blog/changelog/2026-06-03-github-copilot-in-visual-studio-code-may-releases](https://github.blog/changelog/2026-06-03-github-copilot-in-visual-studio-code-may-releases)
- 한줄 요약: VS Code continues with weekly stable releases. This changelog covers releases v1.120 through v1.123, the releases we shipped throughout May and early June 2026. In May, we made the Agents&#8230; The post GitHub Copilot in Visual Studio Code, May releases appeared first on The GitHub Blog .
- 왜 중요한가: 개발 생산성 자동화나 서비스 기능 고도화에 적용 가능한 흐름입니다.

## 활용 가이드

1. 업무와 직접 연결되는 항목 2개만 먼저 읽고 팀 위키에 메모를 남깁니다.
2. 다음 스프린트에서 적용 가능한 변경점(버전, 아키텍처, 운영지표)을 추려 액션 아이템으로 분리합니다.

---
이 글은 자동 파이프라인으로 생성되며, 품질 기준을 통과한 항목만 게시됩니다.
