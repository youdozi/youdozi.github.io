---
title: "macOS Jekyll 환경: Ruby·Bundler와 두 페이지 빌드 확인하기"
language: ko
translationKey: 2023-09-04-jekyll-install
routeSlug: 2023-09-04-jekyll-install
kind: post
publishedAt: 2023-09-03T15:00:00.000Z
categories:
  - jekyll
tags:
  - ruby
  - rbenv
  - bundler
  - jekyll
  - macos
legacyUrl: /jekyll/jekyll-install/
legacySource: _posts/jekyll/install/2023-09-04-jekyll-install.markdown
updatedAt: 2026-10-27T08:56:40.345Z
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Primary documentation checked; isolated legacy bundle render and temporary C++ probe executed. Historical versions and host-specific limits stated.
archiveBodySha256: 3e460f436e05c908c3ebf4c4ff74bf0b742768e8499e1989228baa0d89e24812
reviewSources:
  - https://github.com/rbenv/rbenv#readme
  - https://jekyllrb.com/docs/installation/macos/
  - https://guides.rubygems.org/using_bundler_in_applications/
  - https://docs.ruby-lang.org/en/3.2/RbConfig.html
  - https://www.ruby-lang.org/en/downloads/branches/
  - https://developer.apple.com/library/archive/technotes/tn2339/_index.html
description: 권한 변경 전에 Ruby 선택과 번들 환경을 확인합니다. 격리된 Jekyll 예제를 실행하고 gem 설치 여부와 번들 포함 여부를 구분합니다.
---
권한을 바꾸기 전에 실행 중인 Ruby, Bundler가 선택한 의존성, 작은 사이트의 렌더링을 순서대로 확인합니다. 현재 이 사이트는 Astro로 빌드합니다. 아래 Jekyll 예제는 남아 있는 Ruby 아카이브를 진단하기 위한 것입니다.

원래 설치 글은 Ruby3.2.2를 사용했습니다. 해당 계열은 현재 [지원이 종료](https://www.ruby-lang.org/en/downloads/branches/)되어 과거 호환성 재현용이며 신규 설치 권장 버전이 아닙니다. 새 환경에는 프로젝트의 gem과 호환되는 유지보수 중인 Ruby를 선택하세요.

## gem 설치 전에 실행기 선택 확인하기

![Ruby 선택과 번들 의존성을 확인하고 작은 사이트를 렌더링하는 흐름](/assets/diagrams/2023-09-04-jekyll-install-ko.svg)

[Jekyll macOS 설치 문서](https://jekyllrb.com/docs/installation/macos/)는 시스템 Ruby 대신 별도로 관리하는 Ruby 환경을 안내합니다. 이 저장소의 이전 환경은 rbenv를 사용했습니다. [rbenv의 버전 선택 규칙](https://github.com/rbenv/rbenv#readme)은 프로젝트의 `.ruby-version`, `RBENV_VERSION`, 전역 기본값을 구분합니다.

프로젝트 디렉터리에서 다음을 확인합니다.

```sh
command -v ruby
ruby --version
rbenv version
rbenv which ruby
gem env home
bundle --version
```

예상한 관리자가 Ruby를 선택하지 못하면 설치부터 반복하지 말고 셸 초기화를 확인합니다. 설치한 rbenv 버전의 안내에 따라 `rbenv init`을 적용하고, 다른 사용자의 홈 경로를 셸 설정에 복사하지 않습니다. 모든 Ruby 프로젝트에 영향을 주는 `rbenv global`보다 프로젝트 단위 선택을 우선합니다.

## 두 페이지로 번들 렌더링 확인하기

이 호환성 예제는 Ruby3.2.2·Bundler2.4.19·Jekyll3.9.3·kramdown-parser-gfm1.1.0에서 실행했습니다. 기록된 과거 버전 조합이며 지원 버전의 기준이 아닙니다. Gemfile은 직접 사용하는 gem 두 개를 고정하고, 생성된 Gemfile.lock이 해당 플랫폼의 전이 의존성을 기록합니다.

별도 임시 작업 디렉터리를 만들고 다음 전체 파일을 저장합니다. 저장소에 있는 기존 Gemfile을 덮어쓰지 마세요.

### `Gemfile`

```ruby
source 'https://rubygems.org'
gem 'jekyll', '= 3.9.3'
gem 'kramdown-parser-gfm', '= 1.1.0'
```

### `jekyll_probe.rb`

```ruby
require 'jekyll'
require 'tmpdir'
require 'fileutils'
require 'json'

Dir.mktmpdir('jekyll-probe-') do |root|
  root = File.realpath(root)
  source = File.join(root, 'source')
  destination = File.join(root, 'output')
  FileUtils.mkdir_p(File.join(source, '_layouts'))
  File.write(File.join(source, '_layouts', 'default.html'), '<!doctype html><html lang="en"><body>{{ content }}</body></html>')
  File.write(File.join(source, 'index.md'), "---\nlayout: default\ntitle: Probe\n---\n# Bundled build\n\n[Guide](/guide/)\n")
  File.write(File.join(source, 'guide.md'), "---\nlayout: default\npermalink: /guide/\n---\n# Local guide\n")
  config = Jekyll.configuration('config' => [], 'source' => source, 'destination' => destination, 'quiet' => true)
  Dir.chdir(source) { Jekyll::Site.new(config).process }
  home = File.read(File.join(destination, 'index.html'))
  guide = File.read(File.join(destination, 'guide', 'index.html'))
  raise 'Missing rendered heading' unless home.include?('<h1') && home.include?('Bundled build')
  raise 'Missing guide link' unless home.include?('href="/guide/"')
  raise 'Missing guide output' unless guide.include?('Local guide')
  puts JSON.generate('ruby' => RUBY_VERSION, 'jekyll' => Jekyll::VERSION, 'pages' => 2, 'result' => 'passed')
end
```

선택한 Ruby와 Bundler를 사용할 수 있는 상태에서 해당 디렉터리에서 실행합니다.

```sh
bundle install
bundle exec ruby jekyll_probe.rb
```

정확한 gem이 이미 설치되어 있다면 `bundle lock --local`로 로컬 목록에서 의존성을 결정한 뒤 같은 실행 명령을 사용할 수 있습니다. 없는 gem을 내려받지는 않습니다. 실패를 재현할 때는 lockfile을 보존하고 갱신 전 차이를 검토하세요. [Bundler의 애플리케이션 안내](https://guides.rubygems.org/using_bundler_in_applications/)에서 Gemfile과 lockfile의 역할을 설명합니다.

실행해 확인한 결과입니다.

```json
{"ruby":"3.2.2","jekyll":"3.9.3","pages":2,"result":"passed"}
```

예제는 임시 디렉터리에서 빌드합니다. macOS의 `/var` 심볼릭 링크 경로 차이를 피하도록 실제 경로를 사용하고, 기본 설정 파일 탐색을 끈 뒤 자체 소스 디렉터리로 이동해 렌더링합니다. 제목·링크·대상 페이지를 확인하고 임시 파일을 삭제합니다. 전체 아카이브·테마·플러그인·CSS·배포는 이 검사의 범위가 아닙니다.

## 설치 여부와 번들 포함 여부 구분하기

이번 재현에서는 Jekyll을 불러올 수 있어도 번들이 `kramdown-parser-gfm`을 선언하지 않으면 Markdown 변환이 실패했습니다. 시스템 어딘가에 설치된 gem과 `bundle exec` 안에서 사용할 수 있는 gem은 다릅니다. 이 예제의 Gemfile에 파서를 추가한 뒤 변환을 확인했습니다.

두 페이지 예제가 성공하면 실제 사이트의 설정·테마·플러그인·입력으로 조사 범위를 좁힐 수 있습니다. 네이티브 확장을 불러오거나 컴파일하는 단계에서 실패하면 [Ruby·C++ 진단 예제](/ko/posts/2026-04-07-ruby-rbenv-jekyll-build-troubleshooting/)로 계층을 나눠 확인합니다. 현재 사이트의 게시는 [Astro 후보 검토 워크플로](/ko/posts/2026-04-07-jekyll-github-actions-content-pipeline/)를 따릅니다.
