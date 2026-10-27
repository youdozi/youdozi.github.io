---
language: en
translationKey: 2026-04-07-ruby-rbenv-jekyll-build-troubleshooting
routeSlug: 2026-04-07-ruby-rbenv-jekyll-build-troubleshooting
kind: post
publishedAt: 2026-10-27T08:56:40.345Z
categories:
  - blog
  - troubleshooting
title: "Ruby Native Gem Failures: Separate Runtime and C++ Header Checks"
description: Diagnose Ruby startup separately from C++ compilation with a temporary probe. Compare RbConfig and command-scoped SDK flags without reinstalling the runtime.
tags:
  - ruby
  - rbenv
  - bundler
  - jekyll
  - macos
updatedAt: 2026-10-27T08:56:40.345Z
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Primary documentation checked; isolated legacy bundle render and temporary C++ probe executed. Historical versions and host-specific limits stated.
reviewSources:
  - https://github.com/rbenv/rbenv#readme
  - https://jekyllrb.com/docs/installation/macos/
  - https://guides.rubygems.org/using_bundler_in_applications/
  - https://docs.ruby-lang.org/en/3.2/RbConfig.html
  - https://www.ruby-lang.org/en/downloads/branches/
  - https://developer.apple.com/library/archive/technotes/tn2339/_index.html
---
Separate Ruby startup from native-extension compilation. A working `ruby --version` does not prove that a C++ compiler can find its headers, and a successful standalone C++ program does not prove a gem's extension will compile.

The original record concerned another user's Ruby library path and a macOS SDK/header problem. Those are distinct failure modes. The diagnostic below preserves that distinction without uninstalling Ruby, changing Command Line Tools or overriding RbConfig globally. The current site uses Astro; these checks apply to the retained Ruby tooling.

## Start at the failing layer

![Check Ruby startup, inspect the compiler, then run an isolated C++ probe](/assets/diagrams/2026-04-07-ruby-rbenv-jekyll-build-troubleshooting-en.svg)

First compare the selected Ruby with its recorded build configuration:

```sh
command -v ruby
ruby --version
rbenv which ruby
ruby -rrbconfig -e 'puts RbConfig.ruby; puts RbConfig::CONFIG.values_at("CXX", "CPPFLAGS", "CXXFLAGS")'
```

If Ruby itself fails to start with a missing library error, investigate that interpreter and its library linkage before a gem install. On macOS, `otool -L` can inspect the executable selected by `rbenv which ruby`. Do not reinstall every Ruby version solely because a native gem failed.

[RbConfig](https://docs.ruby-lang.org/en/3.2/RbConfig.html) exposes the interpreter's build configuration. In the tested Ruby3.2.2 environment, `CXX` was `false`, while an explicitly selected `c++` could run with suitable header flags. That observation concerns this interpreter and host, not every rbenv installation. Ruby3.2 is now [end of life](https://www.ruby-lang.org/en/downloads/branches/); this is diagnosis of an old environment, not a supported baseline.

## Compile without changing Ruby's configuration

Save this complete Ruby standard-library script as `native_probe.rb`:

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

Run it with the compiler selected for the probe:

```sh
ruby native_probe.rb
```

The script compiles a temporary C++17 program and requires its output to be exactly `42`. `CXX` chooses the probe command; `PROBE_CXXFLAGS` supplies only that probe's flags. It reports Ruby's configured CXX for comparison and does not replace it. Empty `CXX`, compilation failure or unexpected output causes a nonzero exit.

On the tested Mac, the default invocation failed with `iostream` not found. After inspecting the selected SDK and confirming its header directory existed, the following command-scoped flags made the probe pass:

```sh
probe_sdk="$(xcrun --show-sdk-path)"
test -d "$probe_sdk/usr/include/c++/v1"
PROBE_CXXFLAGS="-isysroot $probe_sdk -isystem $probe_sdk/usr/include/c++/v1" ruby native_probe.rb
```

This path was tested on that Mac. It is not a universal SDK repair, and paths containing whitespace require correctly quoted tokens inside the flag value. Start with `xcode-select -p` and `xcrun --show-sdk-path`; do not install an old example's named CLT package. Apple's [command-line tools guidance](https://developer.apple.com/library/archive/technotes/tn2339/_index.html) explains the selected developer directory and SDK tools.

## Return to the actual gem failure

A passing probe narrows the investigation; the extension may still use different flags, headers, libraries or ABI requirements. Keep the failing gem's build log and compare the command it actually invoked. The repository's `scripts/ruby_cxx_fix.rb` changes RbConfig values inside the Ruby process when explicitly loaded, and its Homebrew fallback is host-specific. Apply such a workaround only after matching the failure; preserve any existing RUBYOPT options rather than overwriting them blindly.

The probe's local success did not reinstall Ruby or rebuild the legacy site's native gems. For the next layer, use the [isolated two-page Jekyll bundle](/en/posts/2023-09-04-jekyll-install/). For the active site's checks, use the [Astro quality-gate guide](/en/posts/2026-04-07-jekyll-quality-gates-proof-html-bundler-audit/).
