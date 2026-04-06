---
layout: posts
title: "[blog] Jekyll 빌드가 깨졌을 때: Ruby/rbenv 복구 기록"
date: 2026-04-07 22:10:00 +0900
categories:
  - blog
  - troubleshooting
tags:
  - ruby
  - rbenv
  - jekyll
  - github-pages
  - macos
excerpt: "rbenv 경로 꼬임, native gem 빌드 실패, macOS CLT 문제를 정리하고 Jekyll 로컬 빌드를 복구한 기록입니다."
header:
  teaser: "/assets/img/blog/troubleshooting/ruby-rbenv-thumb.svg"
  og_image: "/assets/img/blog/troubleshooting/ruby-rbenv-thumb.svg"
---

## 문제 상황

## 시리즈 글 안내

- 1편. [Jekyll 블로그 자동 발행 파이프라인 구축기](/blog/automation/jekyll-github-actions-content-pipeline/)
- 2편. **Jekyll 빌드가 깨졌을 때: Ruby/rbenv 복구 기록**
- 3편. [Jekyll 블로그에 품질 게이트 붙이기](/blog/automation/jekyll-quality-gates-proof-html-bundler-audit/)

Jekyll 블로그 자동 발행 파이프라인을 만들고 나서 가장 먼저 막힌 부분은 의외로 콘텐츠 생성이 아니라 로컬 빌드 환경이었습니다.

겉으로 보기에는 단순히 `bundle exec jekyll build`가 실패하는 문제였지만, 실제로는 여러 문제가 한 번에 겹쳐 있었습니다.

- rbenv Ruby가 다른 사용자 경로를 참조하고 있었고
- native gem 빌드가 깨졌고
- macOS Command Line Tools의 C++ 헤더 경로도 정상적이지 않았습니다.

결과적으로 자동화 스크립트가 아무리 잘 만들어져 있어도, 로컬에서 재현 가능한 빌드 환경이 없으면 운영 신뢰성이 떨어질 수밖에 없었습니다.

## 처음 확인한 증상

가장 먼저 확인된 오류는 Ruby 실행 파일과 연결된 런타임 경로가 잘못된 위치를 바라보는 문제였습니다.

```bash
which ruby
rbenv which ruby
otool -L "$(rbenv which ruby)"
```

확인 결과에서는 현재 사용자 홈 디렉터리가 아니라, 다른 사용자의 rbenv 경로에 있는 `libruby`를 참조하려고 했습니다.

이 상태에서는 Jekyll 문제를 보기 전에 Ruby 런타임 자체가 이미 깨져 있는 상태였습니다.

## 1단계: rbenv Ruby 재설치

우선 이 저장소에서 사용 중이던 Ruby 3.2.2를 다시 설치해서 잘못 연결된 바이너리 문제를 먼저 정리했습니다. 여기서는 저장소의 기존 실행 흐름과 맞추는 것이 우선이었기 때문에, 다른 버전으로 올리기보다 현재 기준 버전을 복구하는 쪽을 택했습니다.

```bash
rbenv uninstall -f 3.2.2
rbenv install 3.2.2
rbenv rehash
```

이후 `ruby -v`는 정상적으로 동작했지만, 문제는 여기서 끝나지 않았습니다.

## 2단계: bundle install 중 native gem 빌드 실패

다음 단계에서 `bundle install`을 실행하자 `eventmachine`, `ffi` 같은 native gem에서 빌드가 실패했습니다.

대표적으로 아래와 같은 문제가 있었습니다.

- `binder.cpp` 컴파일 실패
- `iostream` 헤더를 찾지 못하는 문제
- `ffi` 빌드 중 assembler/CFI 관련 오류

처음에는 단순히 gem 버전 문제라고 생각했지만, 로그를 자세히 보니 C++ 빌드 환경과 SDK 경로가 더 근본적인 원인이었습니다.

## 3단계: Command Line Tools 상태 점검

macOS에서는 Ruby native gem 빌드가 Command Line Tools 상태에 직접 영향을 받습니다.

그래서 아래를 확인했습니다.

```bash
xcode-select -p
softwareupdate --list
```

확인 결과 최신 Command Line Tools 업데이트가 남아 있었고, 실제로 이를 설치한 뒤 SDK 디렉터리 구성이 달라졌습니다. 다만 아래 패키지명은 제가 작업한 당시 이 Mac 환경에서 보였던 값이므로, 다른 시점이나 다른 장비에서는 이름이 달라질 수 있습니다.

```bash
softwareupdate --install "Command Line Tools for Xcode 26.4-26.4"
```

업데이트 후에는 SDK 안쪽에 C++ 헤더 경로가 정상적으로 보이기 시작했습니다.

> 스크린샷 포인트 1: `softwareupdate --list` 결과

## 4단계: Ruby가 C++ 헤더를 찾지 못하는 문제 우회

문제는 Command Line Tools를 설치해도 Ruby가 native gem을 빌드할 때 적절한 C++ 플래그를 자동으로 잡지 못했다는 점입니다.

그래서 `scripts/ruby_cxx_fix.rb`를 추가해 Ruby의 컴파일 설정에 아래 값을 주입했습니다. 이 방법은 일반적인 정답이라기보다, 이 저장소와 이 로컬 환경에서 재현 가능한 빌드를 만들기 위한 저장소 전용 우회책에 가깝습니다.

- 사용할 C++ 컴파일러
- `isysroot` 경로
- SDK 내부의 `usr/include/c++/v1` 경로
- `-stdlib=libc++`

또한 fallback 경로로 사용한 `/opt/homebrew/...` 값 역시 Apple Silicon Homebrew 기준이어서, 다른 Mac에서는 경로를 다르게 잡아야 할 수 있습니다.

핵심 아이디어는 "매번 쉘 환경을 수동으로 고치는 대신, Ruby가 빌드 시점에 필요한 플래그를 일관되게 적용하게 만들자"는 것이었습니다.

구조는 대략 아래와 같습니다.

```ruby
[RbConfig::CONFIG, RbConfig::MAKEFILE_CONFIG].each do |config|
  config['CXX'] = cxx
  config['CPPFLAGS'] = [config['CPPFLAGS'], extra_cppflags].compact.join(' ').strip
  config['CXXFLAGS'] = [config['CXXFLAGS'], '-stdlib=libc++'].compact.join(' ').strip
end
```

이후 `RUBYOPT`로 이 파일을 로드해서 `bundle install`과 `jekyll build`를 실행하도록 구성했습니다.

## 5단계: 매번 같은 방식으로 빌드하기

환경이 한 번 맞더라도, 실행 방식이 제각각이면 다시 깨질 가능성이 큽니다.

그래서 `scripts/jekyll-build.sh`를 추가해서 로컬 빌드 루틴을 한 줄로 고정했습니다.

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RUBYOPT_FIX="-r${ROOT_DIR}/scripts/ruby_cxx_fix.rb"

cd "$ROOT_DIR"
RUBYOPT="$RUBYOPT_FIX" bundle install
RUBYOPT="$RUBYOPT_FIX" bundle exec jekyll build
```

이제는 아래 명령 하나로 로컬 재현이 가능합니다.

```bash
npm run jekyll:build
```

## 최종 확인

최종적으로는 아래 검증이 모두 성공했습니다.

```bash
npm run jekyll:build
python3 scripts/validate_dev_digest.py _posts/dev/digest/2026-03-16-dev-digest.markdown --min-items 1
```

즉, 단순히 에러 메시지를 없앤 것이 아니라 아래 두 가지를 모두 만족하게 되었습니다.

- 로컬에서 Jekyll 사이트를 다시 빌드할 수 있다.
- 자동 생성 포스트도 같은 환경에서 검증 가능하다.

> 스크린샷 포인트 2: `npm run jekyll:build` 성공 로그

## 이번에 배운 점

이번 문제를 해결하면서 가장 크게 느낀 점은, 블로그 자동화에서 중요한 것은 Python 스크립트나 GitHub Actions 자체보다도 **기반 런타임을 재현 가능하게 유지하는 것**이라는 사실이었습니다.

특히 Jekyll처럼 Ruby 생태계와 로컬 툴체인 영향을 받는 프로젝트는 아래가 중요합니다.

- Ruby 버전 관리가 명확해야 하고
- native gem 빌드 경로가 재현 가능해야 하며
- 로컬과 CI 실행 방식 차이를 줄여야 합니다.

즉, 자동화는 발행 단계만 자동이면 끝나는 게 아니라, **실패했을 때도 같은 방식으로 복구할 수 있어야 진짜 자동화**라고 볼 수 있습니다.

## 마무리

이번 복구 작업 덕분에 이 블로그는 다시 "글을 올릴 수 있는 상태"가 되었고, 그 위에서 자동 digest와 품질 게이트도 안정적으로 운영할 수 있게 되었습니다.

나중에 시간이 더 생기면 다음도 정리해보고 싶습니다.

- `faraday-retry` 경고 정리
- Ruby/Jekyll 의존성 업데이트 전략
- GitHub Pages 호환성을 유지하면서 자동화 범위 넓히기

비슷한 문제를 겪고 있다면, 에러 메시지만 보고 gem 버전을 계속 바꾸기보다 **Ruby 경로 -> SDK 상태 -> C++ 헤더 경로 -> 빌드 루틴 고정** 순서로 보는 것이 훨씬 빠를 수 있습니다.

## 함께 읽으면 좋은 글

- 이전 글: [Jekyll 블로그 자동 발행 파이프라인 구축기](/blog/automation/jekyll-github-actions-content-pipeline/)
- 다음 글: [Jekyll 블로그에 품질 게이트 붙이기](/blog/automation/jekyll-quality-gates-proof-html-bundler-audit/)
