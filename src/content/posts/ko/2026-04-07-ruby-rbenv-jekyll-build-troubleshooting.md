---
title: "Ruby 네이티브 gem 실패: 실행기와 C++ 헤더 검사 나누기"
language: ko
translationKey: 2026-04-07-ruby-rbenv-jekyll-build-troubleshooting
routeSlug: 2026-04-07-ruby-rbenv-jekyll-build-troubleshooting
kind: post
publishedAt: 2026-04-07T13:10:00.000Z
categories:
  - blog
  - troubleshooting
tags:
  - ruby
  - rbenv
  - bundler
  - jekyll
  - macos
legacyUrl: /blog/troubleshooting/ruby-rbenv-jekyll-build-troubleshooting/
description: 임시 컴파일 예제로 Ruby 실행 실패와 C++ 헤더 문제를 나눠 진단합니다. 재설치 없이 RbConfig와 명령 단위 SDK 플래그를 비교합니다.
legacySource: _posts/blog/troubleshooting/2026-04-07-ruby-rbenv-jekyll-build-troubleshooting.markdown
updatedAt: 2026-10-27T08:56:40.345Z
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Primary documentation checked; isolated legacy bundle render and temporary C++ probe executed. Historical versions and host-specific limits stated.
archiveBodySha256: cf68d54330429be1028aaea682918197bb90ef686f5461683976bb8276b6012e
reviewSources:
  - https://github.com/rbenv/rbenv#readme
  - https://jekyllrb.com/docs/installation/macos/
  - https://guides.rubygems.org/using_bundler_in_applications/
  - https://docs.ruby-lang.org/en/3.2/RbConfig.html
  - https://www.ruby-lang.org/en/downloads/branches/
  - https://developer.apple.com/library/archive/technotes/tn2339/_index.html
---
Ruby 실행과 네이티브 확장 컴파일을 나눠 확인합니다. `ruby --version`이 동작해도 C++ 컴파일러가 헤더를 찾는다는 뜻은 아닙니다. 독립 C++ 프로그램이 성공해도 gem의 네이티브 확장 빌드가 성공한다고 보장할 수 없습니다.

원래 기록은 다른 사용자의 Ruby 라이브러리 경로와 macOS SDK·헤더 문제를 다뤘습니다. 두 문제의 실패 계층은 다릅니다. 아래 예제는 Ruby 삭제·Command Line Tools 변경·RbConfig 전역 덮어쓰기 없이 계층을 나눠 진단합니다. 현재 사이트는 Astro를 사용하며, 이 검사는 남아 있는 Ruby 도구를 위한 것입니다.

## 실패한 계층에서 시작하기

![Ruby 실행과 컴파일러 설정을 확인하고 격리된 C++ 예제를 실행하는 흐름](/assets/diagrams/2026-04-07-ruby-rbenv-jekyll-build-troubleshooting-ko.svg)

먼저 선택된 Ruby와 빌드 설정을 비교합니다.

```sh
command -v ruby
ruby --version
rbenv which ruby
ruby -rrbconfig -e 'puts RbConfig.ruby; puts RbConfig::CONFIG.values_at("CXX", "CPPFLAGS", "CXXFLAGS")'
```

Ruby 자체가 라이브러리 누락으로 시작하지 못하면 gem 설치 전에 해당 실행기와 라이브러리 연결을 조사합니다. macOS에서는 `rbenv which ruby`가 선택한 실행 파일을 `otool -L`로 확인할 수 있습니다. 네이티브 gem 하나가 실패했다는 이유만으로 Ruby 버전을 모두 재설치하지 않습니다.

[RbConfig](https://docs.ruby-lang.org/en/3.2/RbConfig.html)는 실행기의 빌드 설정을 제공합니다. 검사한 Ruby3.2.2 환경에서는 `CXX`가 `false`였지만 명시적으로 선택한 `c++`에 적절한 헤더 플래그를 주면 실행할 수 있었습니다. 이는 해당 실행기와 호스트의 관찰이며 모든 rbenv 설치에 해당하는 현상이 아닙니다. Ruby3.2는 현재 [지원 종료](https://www.ruby-lang.org/en/downloads/branches/) 상태이므로 오래된 환경의 진단 사례로 다룹니다.

## Ruby 설정을 바꾸지 않고 컴파일하기

다음 Ruby 표준 라이브러리 전체 코드를 `native_probe.rb`로 저장합니다.

```ruby
require 'rbconfig'
require 'open3'
require 'shellwords'
require 'tmpdir'
require 'json'

compiler = Shellwords.split(ENV.fetch('CXX', 'c++'))
abort 'CXX must name a compiler' if compiler.empty?
flags = Shellwords.split(ENV.fetch('PROBE_CXXFLAGS', ''))
Dir.mktmpdir('ruby-cxx-probe-') do |root|
  source = File.join(root, 'probe.cpp')
  binary = File.join(root, 'probe')
  File.write(source, "#include <iostream>\nint main() { std::cout << 42 << '\\n'; }\n")
  _out, error, status = Open3.capture3(*compiler, '-std=c++17', *flags, source, '-o', binary)
  abort "C++ compilation failed:\n#{error}" unless status.success?
  output, error, status = Open3.capture3(binary)
  abort "Probe failed: #{error}" unless status.success? && output == "42\n"
  puts JSON.generate('ruby' => RUBY_VERSION, 'configured_cxx' => RbConfig::CONFIG['CXX'],
                     'probe_compiler' => compiler, 'output' => output.strip, 'result' => 'passed')
end
```

진단에 사용할 컴파일러로 실행합니다.

```sh
ruby native_probe.rb
```

스크립트는 임시 C++17 프로그램을 컴파일하고 출력이 정확히 `42`인지 확인합니다. `CXX`는 진단용 명령을 선택하고 `PROBE_CXXFLAGS`는 해당 진단의 플래그만 전달합니다. Ruby의 CXX 설정은 비교를 위해 출력할 뿐 바꾸지 않습니다. 빈 `CXX`, 컴파일 실패, 예상과 다른 출력은 0이 아닌 종료 코드를 반환합니다.

검사한 Mac에서는 기본 호출이 `iostream`을 찾지 못해 실패했습니다. 선택된 SDK와 헤더 디렉터리의 존재를 확인한 뒤, 해당 명령에만 다음 플래그를 전달하면 통과했습니다.

```sh
probe_sdk="$(xcrun --show-sdk-path)"
test -d "$probe_sdk/usr/include/c++/v1"
PROBE_CXXFLAGS="-isysroot $probe_sdk -isystem $probe_sdk/usr/include/c++/v1" ruby native_probe.rb
```

해당 Mac에서 확인한 경로이며 모든 SDK 문제의 해결책은 아닙니다. 경로에 공백이 있다면 플래그 값 내부의 각 토큰도 올바르게 인용해야 합니다. `xcode-select -p`와 `xcrun --show-sdk-path`부터 확인하고 과거 예제에 적힌 CLT 패키지명을 그대로 설치하지 않습니다. Apple의 [명령행 도구 안내](https://developer.apple.com/library/archive/technotes/tn2339/_index.html)에서 개발자 디렉터리 선택과 SDK 도구를 설명합니다.

## 실제 gem 실패로 돌아가기

진단이 성공하면 조사 범위를 좁힐 수 있지만 확장은 다른 플래그·헤더·라이브러리·ABI 조건을 사용할 수 있습니다. 실패한 gem의 빌드 로그를 보존하고 실제 호출한 명령을 비교하세요. 저장소의 `scripts/ruby_cxx_fix.rb`는 명시적으로 불러온 Ruby 프로세스 안에서 RbConfig 값을 변경하며, Homebrew 대체 경로도 호스트에 따라 다릅니다. 실패 원인이 맞는지 확인한 뒤 제한적으로 적용하고 기존 RUBYOPT 옵션을 무작정 덮어쓰지 않습니다.

이번 로컬 진단 성공은 Ruby 재설치나 이전 사이트의 네이티브 gem 재빌드를 뜻하지 않습니다. 다음 계층은 [두 페이지 Jekyll 번들 예제](/ko/posts/2023-09-04-jekyll-install/)로 확인합니다. 현재 사이트의 검사는 [Astro 품질 게이트 안내](/ko/posts/2026-04-07-jekyll-quality-gates-proof-html-bundler-audit/)를 따릅니다.
