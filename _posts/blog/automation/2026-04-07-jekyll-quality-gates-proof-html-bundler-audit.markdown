---
layout: posts
title: "[blog] Jekyll 블로그에 품질 게이트 붙이기"
date: 2026-04-07 22:40:00 +0900
categories:
  - blog
  - automation
tags:
  - jekyll
  - github-actions
  - proof-html
  - bundler-audit
  - ci
excerpt: "Jekyll 블로그에 build, 링크 검사, Ruby 의존성 점검을 붙여 발행 전 품질 게이트를 만든 과정입니다."
header:
  teaser: "/assets/img/blog/automation/jekyll-quality-gates-thumb.svg"
  og_image: "/assets/img/blog/automation/jekyll-quality-gates-thumb.svg"
---

## 왜 품질 게이트가 필요했을까

## 시리즈 글 안내

- 1편. [Jekyll 블로그 자동 발행 파이프라인 구축기](/blog/automation/jekyll-github-actions-content-pipeline/)
- 2편. [Jekyll 빌드가 깨졌을 때: Ruby/rbenv 복구 기록](/blog/troubleshooting/ruby-rbenv-jekyll-build-troubleshooting/)
- 3편. **Jekyll 블로그에 품질 게이트 붙이기**

자동 발행 파이프라인을 만들고 나면 보통 "글이 자동으로 올라간다"는 사실에 먼저 만족하게 됩니다.

그런데 실제 운영에서는 그다음 문제가 바로 나타납니다.

- Markdown 파일은 생성됐지만 사이트 빌드는 실패할 수 있고
- 링크는 생성됐지만 이미 깨진 주소일 수 있고
- Ruby 의존성은 조용히 오래된 상태로 남아 있을 수 있습니다.

즉, 발행 자동화만으로는 충분하지 않았고, **발행 전에 무엇을 막아야 하는지**를 정의하는 단계가 추가로 필요했습니다.

그래서 이번에는 Jekyll 블로그에 **품질 게이트(Quality Gates)** 를 붙이기로 했습니다.

## 이번에 만든 품질 게이트

현재 품질 게이트는 `.github/workflows/site-quality-gates.yml`에서 동작합니다.

구성은 크게 두 갈래입니다.

1. 사이트 자체가 정상적으로 빌드되는지 확인
2. 빌드된 결과와 Ruby 의존성이 안전한지 확인

## 1. Jekyll build 검사

가장 기본이면서 가장 중요한 단계입니다.

```yaml
- name: Build site
  env:
    JEKYLL_ENV: production
  run: bundle exec jekyll build
```

이 단계가 필요한 이유는 단순합니다.

자동 생성된 글이 형식상 맞아 보여도, 실제 Jekyll 렌더링 시점에 front matter나 템플릿 처리 문제로 깨질 수 있기 때문입니다.

즉, 글 파일 생성 성공보다 **사이트 전체 빌드 성공**이 더 중요한 기준입니다.

## 2. proof-html로 링크/HTML 검사

사이트가 빌드되었다고 해서 모든 것이 끝난 것은 아닙니다.

정적 블로그는 특히 다음 문제가 자주 남습니다.

- 외부 링크 404
- 잘못된 HTML 구조
- favicon / Open Graph 메타 누락
- HTTPS 강제 정책 누락

이 부분은 `proof-html`로 검사하게 했습니다.

```yaml
- name: Proof HTML
  uses: anishathalye/proof-html@v2
  with:
    directory: ./_site
    check_html: true
    check_favicon: true
    check_opengraph: true
    enforce_https: true
```

이 설정 덕분에 "페이지는 열리지만 어딘가 어색한 상태"를 좀 더 빨리 발견할 수 있습니다.

> 스크린샷 포인트 1: quality gates workflow 실행 결과 화면

## 3. bundler-audit로 Ruby 의존성 점검

Jekyll 블로그는 애플리케이션처럼 복잡하지 않아 보여도, 결국 Ruby gem 위에서 돌아갑니다.

그래서 의존성 보안 점검도 따로 붙였습니다.

```yaml
- name: Install bundler-audit
  run: gem install bundler-audit --no-document

- name: Run bundler audit
  shell: bash
  run: |
    set -o pipefail
    bundle-audit check --update | tee bundler-audit-report.txt
```

이 단계는 취약점 데이터베이스를 갱신한 뒤 현재 `Gemfile.lock` 기준으로 알려진 취약점을 확인합니다.

즉, 블로그가 조용히 돌아가고 있더라도 "안전하게 오래된 상태"인지, 아니면 "위험하게 오래된 상태"인지를 가려내는 역할을 합니다.

## 4. 실패했을 때 디버깅 가능하게 만들기

CI가 실패했을 때 가장 아쉬운 점은 "왜 실패했는지 다시 재현해야 한다"는 것입니다.

그래서 품질 게이트 워크플로에서는 가능한 경우 아래 결과를 artifact로 남기도록 구성했습니다.

- `_site` 빌드 산출물
- `bundler-audit-report.txt`

```yaml
- name: Upload built site artifact
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: site-build-output
    path: _site

- name: Upload bundler audit report
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: bundler-audit-report
    path: bundler-audit-report.txt
```

물론 빌드가 너무 이른 단계에서 실패하면 `_site`가 없을 수도 있습니다. 그래도 가능한 경우 결과를 남겨두면, 문제를 훨씬 빠르게 좁힐 수 있습니다.

> 스크린샷 포인트 2: artifact 다운로드 화면

## 발행 파이프라인과 역할을 분리한 이유

이번에 의도적으로 나눈 것은 "글을 올리는 파이프라인"과 "품질을 막는 파이프라인"의 역할입니다.

- `dev-content-pipeline.yml`: 새 digest 생성, 검증, 빌드, commit/push
- `site-quality-gates.yml`: 사이트 품질과 의존성 상태 검사

이렇게 나누면 자동 발행 흐름은 단순해지고, 품질 검사는 더 명확한 책임을 갖게 됩니다.

운영 경험상 이런 분리는 나중에 유지보수할 때 특히 도움이 됩니다.

## 적용하고 나서 좋아진 점

품질 게이트를 붙인 뒤 가장 좋아진 점은 "문제가 생겨도 나중에 찾는 방식"에서 "올리기 전에 막는 방식"으로 바뀌었다는 것입니다.

특히 아래 변화가 체감됐습니다.

- 발행 신뢰도가 높아졌다.
- 링크 깨짐이나 메타 누락을 빨리 찾게 됐다.
- Ruby 의존성 점검이 습관이 아니라 시스템이 됐다.
- 실패 시 재현 시간이 줄었다.

## 앞으로 더 붙이고 싶은 것

아직도 확장할 여지는 많습니다.

- Actions summary에 실패 원인 요약 남기기
- proof-html 결과를 별도 리포트 파일로 저장하기
- Dependabot으로 gem/npm 업데이트 자동 제안 받기
- 특정 태그/카테고리별 빌드 검사 범위 최적화

## 마무리

블로그 자동화는 글을 더 빨리 올리게 해주지만, 품질 게이트는 그 글이 **문제 없이 오래 남도록** 도와줍니다.

개인 블로그라도 운영 기간이 길어질수록 "한 번쯤 확인해야 할 것들"은 반드시 쌓입니다.

그래서 지금 단계에서 가장 중요했던 것은 더 많은 자동화를 붙이는 것이 아니라, **자동화된 결과를 믿을 수 있게 만드는 것**이었습니다.

결국 자동 발행 다음 단계는 품질 게이트였고, 이 둘이 같이 있어야 비로소 운영 가능한 블로그 시스템이 된다고 느꼈습니다.

## 함께 읽으면 좋은 글

- 이전 글: [Jekyll 블로그 자동 발행 파이프라인 구축기](/blog/automation/jekyll-github-actions-content-pipeline/)
- 이전 글: [Jekyll 빌드가 깨졌을 때: Ruby/rbenv 복구 기록](/blog/troubleshooting/ruby-rbenv-jekyll-build-troubleshooting/)
