---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2026-04-07-ruby-rbenv-jekyll-build-troubleshooting",
  "routeSlug": "2026-04-07-ruby-rbenv-jekyll-build-troubleshooting",
  "kind": "post",
  "title": "Ruby 原生 gem 失败：区分运行时与 C++ 头文件检查",
  "description": "用临时探针分别诊断 Ruby 启动和 C++ 编译。比较 RbConfig 与单命令 SDK 标志，无需重装运行时。",
  "categories": [
    "blog",
    "troubleshooting"
  ],
  "tags": [
    "ruby",
    "rbenv",
    "bundler",
    "jekyll",
    "macos"
  ],
  "sourcePath": "src/content/posts/en/2026-04-07-ruby-rbenv-jekyll-build-troubleshooting.md",
  "sourceSha256": "b186e8b9ffc0b623a12d82e49d3428adc274669397a7a207f235d80673b0759a",
  "draftSha256": "c174a7ca498ec81e6675ae22313bf439e818598d7ff854bb5f7cb416f872e071",
  "manifestPath": ".pipeline/technical-translations/batch-125/manifest.json",
  "manifestSha256": "1934910c02dbe893b786124f1d296d7adf9efbe921d40b3d2cfbceb8f70b4b33",
  "publishedAt": "2026-10-31T15:35:43.034Z",
  "updatedAt": "2026-10-31T15:35:43.034Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 125,
    "approvedAt": "2026-10-31T15:35:43.034Z",
    "basis": "User explicitly requested applying all missing technical-post languages, review, verification and deployment on 2026-11-01, with standing PR merge authorization. Human approval denotes publication authorization; linguistic review is performed by AI, not human/native review."
  }
}
---

区分 Ruby 启动与原生扩展编译。`ruby --version` 正常不证明 C++ 编译器能找到头文件，独立 C++ 程序成功也不证明 gem 扩展能编译。

原始记录涉及其他用户的 Ruby 库路径及 macOS SDK/头文件问题，两者是不同失败模式。下面的诊断保留该区别，不卸载 Ruby、不更改 Command Line Tools，也不全局覆盖 RbConfig。当前网站使用 Astro；这些检查适用于保留的 Ruby 工具。

## 从失败的层开始

![检查 Ruby 启动和编译器，再运行隔离的 C++ 探针](/assets/diagrams/technical/zh-CN-2026-04-07-ruby-rbenv-jekyll-build-troubleshooting.svg)

先比较选中的 Ruby 与记录的构建配置：

```sh
command -v ruby
ruby --version
rbenv which ruby
ruby -rrbconfig -e 'puts RbConfig.ruby; puts RbConfig::CONFIG.values_at("CXX", "CPPFLAGS", "CXXFLAGS")'
```

如果 Ruby 本身因缺少库而启动失败，应在安装 gem 前调查解释器及库链接。macOS 上可用 `otool -L` 检查 `rbenv which ruby` 选中的可执行文件。不要仅因一个原生 gem 失败就重装所有 Ruby 版本。

[RbConfig](https://docs.ruby-lang.org/en/3.2/RbConfig.html)公开解释器构建配置。在测试的 Ruby3.2.2 环境中，`CXX` 为 `false`，但显式选择的 `c++` 配合合适头文件标志能运行。这只针对该解释器与主机，并非所有 rbenv 安装。Ruby3.2 已[终止维护](https://www.ruby-lang.org/en/downloads/branches/)；这是旧环境诊断，不是受支持基线。

## 不更改 Ruby 配置进行编译

将完整的 Ruby 标准库脚本保存为 `native_probe.rb`：

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

使用为探针选定的编译器运行：

```sh
ruby native_probe.rb
```

脚本编译临时 C++17 程序，要求输出恰好为 `42`。`CXX` 选择探针命令；`PROBE_CXXFLAGS` 只提供该探针的标志。它报告 Ruby 配置的 CXX 用于比较，不会替换它。`CXX` 为空、编译失败或输出异常都会以非零状态退出。

测试 Mac 上默认调用因找不到 `iostream` 而失败。检查选中 SDK 并确认头文件目录存在后，以下单命令标志使探针通过：

```sh
probe_sdk="$(xcrun --show-sdk-path)"
test -d "$probe_sdk/usr/include/c++/v1"
PROBE_CXXFLAGS="-isysroot $probe_sdk -isystem $probe_sdk/usr/include/c++/v1" ruby native_probe.rb
```

此路径只在该 Mac 上测试，不是通用 SDK 修复。含空格的路径必须在标志值内正确引用 token。先运行 `xcode-select -p` 和 `xcrun --show-sdk-path`；不要安装旧示例指定的 CLT 包。Apple 的[命令行工具指南](https://developer.apple.com/library/archive/technotes/tn2339/_index.html)说明选中开发目录与 SDK 工具。

## 回到真实 gem 失败

探针通过可缩小范围；扩展仍可能使用其他标志、头文件、库或 ABI 要求。保留失败 gem 的构建日志，比较实际调用命令。仓库的 `scripts/ruby_cxx_fix.rb` 被显式加载后，会在 Ruby 进程内修改 RbConfig，其 Homebrew 回退逻辑依赖主机。只有确认失败匹配时才使用此变通方案；保留现有 RUBYOPT 选项，不要盲目覆盖。

探针本地成功并未重装 Ruby 或重编旧网站原生 gem。下一层请使用[隔离的双页面 Jekyll bundle](/en/posts/2023-09-04-jekyll-install/)。当前网站检查参见 [Astro 质量关卡指南](/en/posts/2026-04-07-jekyll-quality-gates-proof-html-bundler-audit/)。
