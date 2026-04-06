---
layout: posts
title: "[blog] Jekyll 블로그 자동 발행 파이프라인 구축기"
date: 2026-04-07 21:30:00 +0900
categories:
  - blog
  - automation
tags:
  - jekyll
  - github-actions
  - github-pages
  - automation
  - python
excerpt: "Jekyll 블로그에 RSS 수집, Markdown 생성, 검증, 빌드, 자동 push를 연결한 발행 파이프라인 구축기입니다."
header:
  teaser: "/assets/img/blog/automation/jekyll-pipeline-thumb.svg"
  og_image: "/assets/img/blog/automation/jekyll-pipeline-thumb.svg"
---

## 왜 자동화가 필요했을까

## 시리즈 글 안내

- 1편. **Jekyll 블로그 자동 발행 파이프라인 구축기**
- 2편. [Jekyll 빌드가 깨졌을 때: Ruby/rbenv 복구 기록](/blog/troubleshooting/ruby-rbenv-jekyll-build-troubleshooting/)
- 3편. [Jekyll 블로그에 품질 게이트 붙이기](/blog/automation/jekyll-quality-gates-proof-html-bundler-audit/)

지금 운영 중인 블로그는 GitHub 저장소에 Markdown 파일을 올리고, Jekyll이 정적 사이트로 빌드하는 구조입니다.

이 방식은 단순하고 안정적이지만, 글을 하나 올릴 때마다 아래 과정을 반복해야 했습니다.

1. 읽을 만한 개발 글을 찾는다.
2. 핵심 내용을 정리한다.
3. Markdown 포스트 형식으로 변환한다.
4. front matter를 맞춘다.
5. 빌드가 깨지지 않는지 확인한다.
6. git push 한다.

문제는 이 흐름이 한두 번은 괜찮아도, 꾸준히 운영하려면 생각보다 손이 많이 간다는 점입니다.

특히 "좋은 글을 찾는 시간"과 "형식을 맞추는 시간"이 누적되기 시작하면, 정작 중요한 읽기와 정리는 뒤로 밀리기 쉽습니다.

그래서 이번에는 단순히 글을 쓰는 블로그가 아니라, **좋은 개발 콘텐츠를 선별해서 가공하고 자동으로 발행하는 파이프라인**으로 바꿔보기로 했습니다.

한마디로 정리하면, 이번 작업의 목표는 **글쓰기 자동화**가 아니라 **블로그 운영 자동화**였습니다.

## 목표

이번 자동화의 목표는 아래 4가지였습니다.

- 고품질 개발 소스를 자동으로 수집할 것
- 원문을 복제하지 않고 요약/맥락 중심으로 Markdown을 만들 것
- 잘못된 글 형식이나 빌드 오류를 자동으로 잡을 것
- 최종적으로 GitHub Actions가 commit/push까지 처리할 것

즉, 단순 크롤링이 아니라 **수집 -> 가공 -> 검증 -> 발행**이 한 번에 이어지는 구조를 만들고 싶었습니다.

## 전체 구조

현재 파이프라인은 아래 흐름으로 동작합니다.

```text
RSS/공식 블로그 수집
  -> 점수화/중복 제거
  -> Markdown 생성
  -> 형식 검증
  -> Jekyll build
  -> GitHub Actions commit/push
```

이 구조를 만들면서 가장 신경 쓴 부분은 "중간 단계 하나라도 깨지면 다음 단계로 넘어가지 않게 하는 것"이었습니다.

### 1. 콘텐츠 수집

`scripts/generate_dev_digest.py`가 RSS 기반으로 개발 관련 글을 가져옵니다.

현재는 다음과 같은 소스를 기준으로 수집합니다.

- GitHub Blog
- Spring Blog
- JetBrains Blog
- Cloudflare Blog
- InfoQ

아무 글이나 가져오는 것이 아니라, 최신성/중복 여부/기술 키워드 기준으로 점수를 계산해서 상위 항목만 선택합니다.

예를 들어 공식 블로그이거나, 최근 며칠 안에 올라왔거나, 현재 블로그 주제와 맞는 키워드를 포함한 글에 더 높은 점수를 주는 방식입니다.

> 스크린샷 포인트 1: GitHub Actions 실행 화면에서 digest 생성 로그

## 2. Markdown 생성

선택된 결과는 Jekyll 포스트 형식으로 `_posts/dev/digest/` 아래에 생성됩니다.

예를 들어 아래와 같은 front matter를 포함합니다.

```yaml
---
layout: posts
title: "[dev] 주간 기술 아티클 다이제스트"
date: 2026-03-16 11:46:48 +0900
categories:
  - dev
  - digest
tags:
  - ai
  - java
---
```

실제로는 Python 스크립트가 날짜, 카테고리, 태그, 본문 섹션을 함께 만들어 줍니다.

```python
posts_dir = repo_root / "_posts" / "dev" / "digest"
file_name = f"{today_kst.strftime('%Y-%m-%d')}-dev-digest.markdown"
target_post = posts_dir / file_name

markdown = build_markdown(today_kst, selected, selected_tags)
target_post.write_text(markdown, encoding="utf-8")
```

여기서 중요한 점은 원문 전체를 그대로 재배포하지 않는다는 점입니다.

포스트에는 아래 정보만 넣습니다.

- 출처
- 발행일
- 원문 링크
- 한 줄 요약
- 왜 중요한가

이렇게 하면 블로그 콘텐츠 품질은 유지하면서도, 원문 전체 복제보다 더 제한된 형태로 정보를 다루게 됩니다. 다만 RSS/Atom summary를 활용하는 경우가 있어, 이 부분은 항상 보수적으로 운영하는 것이 좋습니다.

또한 블로그에 올라오는 글의 형식이 일정해져서, 읽는 입장에서도 "어떤 정보를 기대하면 되는지"가 명확해집니다.

> 스크린샷 포인트 2: 실제 생성된 `_posts/dev/digest/*.markdown` 파일 화면

## 3. 검증

자동 생성은 편하지만, 형식이 조금만 틀어져도 Jekyll 빌드가 깨질 수 있습니다.

그래서 `scripts/validate_dev_digest.py`를 추가해서 아래를 검사하게 했습니다.

- front matter 존재 여부
- `layout`, `categories`, `tags` 같은 핵심 필드 존재 여부
- 필수 섹션 존재 여부
- 최소 항목 개수
- 링크 형식

자동 생성이 되었더라도 검증을 통과하지 못하면 publish 단계로 넘어가지 않도록 했습니다.

이 부분은 생각보다 중요합니다. 자동화는 편하지만, 한 번 잘못된 형식이 들어가면 이후 단계가 모두 무의미해질 수 있기 때문입니다.

```bash
python3 scripts/validate_dev_digest.py _posts/dev/digest/YYYY-MM-DD-dev-digest.markdown --min-items 1
```

## 4. GitHub Actions 발행

`.github/workflows/dev-content-pipeline.yml`에서 실제 자동 발행을 처리합니다.

동작 순서는 다음과 같습니다.

1. 저장소 checkout
2. Python 환경 준비
3. digest 생성
4. 생성된 Markdown 검증
5. Jekyll build 수행
6. 변경 사항이 있을 때만 commit/push

여기서 핵심은 **Markdown 생성 성공이 아니라 Jekyll build 성공을 기준으로 발행한다는 점**입니다.

글 파일만 생겼다고 끝나는 것이 아니라, 블로그 전체가 실제로 렌더링 가능한 상태여야 최종 발행됩니다.

워크플로 관점에서는 아래 단계가 핵심입니다.

```yaml
- name: Generate digest post
  run: python3 scripts/generate_dev_digest.py --max-items 6

- name: Resolve latest generated post
  run: latest_post="$(find _posts/dev/digest -name '*-dev-digest.markdown' | sort | tail -n 1)"

- name: Validate generated digest
  run: python3 scripts/validate_dev_digest.py "$latest_post" --min-items 1

- name: Build site
  env:
    JEKYLL_ENV: production
  run: bundle exec jekyll build
```

그리고 자동 commit/push를 넣을 때는 한 가지 더 고려할 점이 있습니다. 워크플로가 같은 브랜치에 다시 push 하기 때문에, 저장소 권한(`contents: write`)과 브랜치 보호 정책, 그리고 후속 워크플로 트리거 방식까지 함께 봐야 운영이 안정적입니다.

> 스크린샷 포인트 3: `dev-content-pipeline.yml` 실행 성공 화면

## 품질 게이트도 따로 추가했다

자동 발행 외에도, 블로그 자체 품질을 지키기 위한 워크플로를 별도로 두었습니다.

`.github/workflows/site-quality-gates.yml`에서는 아래를 검사합니다.

- `bundle exec jekyll build`
- `proof-html` 기반 링크/HTML 검사
- `bundler-audit` 기반 Ruby 의존성 보안 검사

실패 시에는 `_site`와 audit 결과를 artifact로 남길 수 있도록 구성해서, 가능하면 나중에 원인을 추적하기 쉽게 만들었습니다. 다만 빌드가 아주 이른 단계에서 실패하면 `_site` 아티팩트는 생성되지 않을 수 있습니다.

즉, 발행 파이프라인은 "새 글을 올리는 일"에 집중하고, 품질 게이트는 "사이트 전체 품질을 지키는 일"에 집중하도록 역할을 분리했습니다.

## 구현하면서 만난 문제

이번 작업에서 가장 까다로웠던 부분은 블로그 글 생성이 아니라 **로컬 Ruby 빌드 환경 복구**였습니다.

특히 다음 문제가 있었습니다.

- rbenv Ruby 바이너리가 다른 사용자 경로를 바라보는 문제
- `eventmachine`, `ffi` 같은 native gem 빌드 문제
- macOS Command Line Tools와 C++ 헤더 경로 문제

결국 `scripts/ruby_cxx_fix.rb`와 `scripts/jekyll-build.sh`를 추가해 로컬에서도 `bundle install`과 `jekyll build`가 다시 가능하도록 정리했습니다.

이 문제는 단순히 "명령어가 실패했다" 수준이 아니라, 블로그 자동화가 장기적으로 유지될 수 있느냐를 결정하는 문제였습니다.

이 과정에서 느낀 점은, 자동화는 스크립트 몇 줄 추가보다 **재현 가능한 개발 환경**을 만드는 일이 훨씬 중요하다는 것입니다.

> 스크린샷 포인트 4: 로컬 `npm run jekyll:build` 성공 로그

## 이번 구조의 장점

현재 구조의 장점은 아래와 같습니다.

- 사람이 매번 수작업으로 정리하지 않아도 된다.
- 글 생성 규칙이 일정해서 품질 편차가 줄어든다.
- 빌드와 링크 검사를 통과한 결과만 발행된다.
- 블로그가 단순 글 저장소가 아니라 운영 가능한 시스템이 된다.

- 사람이 컨텐츠 운영보다 더 중요한 "운영 구조 개선"에 시간을 쓸 수 있다.

결국 블로그 운영의 핵심이 “글을 올리는 행위”에서 “좋은 콘텐츠를 지속적으로 발행하는 시스템”으로 바뀌게 됩니다.

## 앞으로 개선하고 싶은 점

아직 개선할 부분도 남아 있습니다.

- digest 외에 일반 기술 글 초안도 템플릿 기반으로 생성하기
- 소스별 신뢰도 가중치 고도화
- 중복 주제 감지 강화
- 대표 이미지/요약 메타데이터 자동 생성
- 인기 태그 중심의 큐레이션 전략 추가

장기적으로는 이 블로그를 단순한 GitHub Pages 사이트가 아니라, **개발 지식을 축적하고 자동 발행하는 개인 미디어 시스템**으로 발전시키는 것이 목표입니다.

## 마무리

이번 작업을 통해 얻은 가장 큰 변화는 “글을 쓰는 블로그”에서 “발행 프로세스를 설계한 블로그”로 한 단계 넘어갔다는 점입니다.

자동화는 시간을 아끼기 위한 도구이기도 하지만, 더 중요한 것은 **꾸준히 운영할 수 있는 구조를 만든다**는 데 있습니다.

다음 글에서는 이번에 실제로 겪었던 **Ruby/rbenv + Jekyll 빌드 문제를 어떻게 해결했는지**를 좀 더 자세히 정리해보려고 합니다.

운영을 해보니, 개인 블로그를 오래 유지하는 힘은 글쓰기 의지보다도 "반복되는 과정을 얼마나 시스템으로 바꿨는가"에서 나온다는 생각이 들었습니다.

## 함께 읽으면 좋은 글

- 다음 글: [Jekyll 빌드가 깨졌을 때: Ruby/rbenv 복구 기록](/blog/troubleshooting/ruby-rbenv-jekyll-build-troubleshooting/)
- 이어지는 글: [Jekyll 블로그에 품질 게이트 붙이기](/blog/automation/jekyll-quality-gates-proof-html-bundler-audit/)
