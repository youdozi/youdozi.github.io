---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2026-04-07-ruby-rbenv-jekyll-build-troubleshooting",
  "routeSlug": "2026-04-07-ruby-rbenv-jekyll-build-troubleshooting",
  "kind": "post",
  "title": "Ruby ネイティブ gem の失敗：実行時と C++ ヘッダーを分けて調べる",
  "description": "一時プローブで Ruby 起動と C++ コンパイルを別々に診断する。実行環境を再導入せず RbConfig とコマンド単位の SDK フラグを比較する。",
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
  "draftSha256": "e471d4b8427a4b866a47d665bebe3052b3d89277f025710fde5615aed52ae61e",
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

Ruby の起動とネイティブ拡張のコンパイルを分けます。`ruby --version` が動いても C++ のヘッダー探索は保証せず、単独 C++ の成功も gem 拡張の成功を保証しません。

元の記録は他ユーザーの Ruby ライブラリパスと macOS SDK/ヘッダーの問題でした。異なる失敗として扱い、以下では Ruby の削除、Command Line Tools の変更、RbConfig の全体上書きをしません。現行サイトは Astro で、対象は残してある Ruby ツールです。

## 失敗する層から始める

![Ruby 起動とコンパイラーを確認して分離した C++ プローブを動かす](/assets/diagrams/technical/ja-2026-04-07-ruby-rbenv-jekyll-build-troubleshooting.svg)

まず選ばれた Ruby と記録されたビルド設定を比較します。

```sh
command -v ruby
ruby --version
rbenv which ruby
ruby -rrbconfig -e 'puts RbConfig.ruby; puts RbConfig::CONFIG.values_at("CXX", "CPPFLAGS", "CXXFLAGS")'
```

Ruby 自体がライブラリ不足で起動しないなら、gem 導入前に実行体とリンクを調べます。macOS では `rbenv which ruby` の実行体を `otool -L` で調べられます。ネイティブ gem の失敗だけを理由に全 Ruby を入れ直さないでください。

[RbConfig](https://docs.ruby-lang.org/en/3.2/RbConfig.html)はビルド設定を公開します。試した Ruby3.2.2 では `CXX` が `false` でしたが、明示した `c++` は適切なヘッダーフラグで動きました。この実行体とホストの観測で、全 rbenv に共通しません。Ruby3.2 は[サポート終了](https://www.ruby-lang.org/en/downloads/branches/)済みで、旧環境の診断です。

## Ruby 設定を変えずにコンパイルする

Ruby 標準ライブラリだけの完全なスクリプトを `native_probe.rb` に保存します。

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

プローブ用のコンパイラーを選んで実行します。

```sh
ruby native_probe.rb
```

一時 C++17 をコンパイルし、出力が厳密に `42` であることを要求します。`CXX` はプローブのコマンド、`PROBE_CXXFLAGS` はプローブだけのフラグです。Ruby の CXX を比較用に報告し、置換しません。空の `CXX`、コンパイル失敗、想定外の出力は非ゼロ終了です。

試した Mac では既定の実行が `iostream` 不在で失敗しました。SDK とヘッダーディレクトリの存在を調べた後、次のコマンド単位のフラグで成功しました。

```sh
probe_sdk="$(xcrun --show-sdk-path)"
test -d "$probe_sdk/usr/include/c++/v1"
PROBE_CXXFLAGS="-isysroot $probe_sdk -isystem $probe_sdk/usr/include/c++/v1" ruby native_probe.rb
```

このパスはその Mac で試したもので万能な SDK 修復ではありません。空白入りパスはフラグ値内のトークンを正しく引用します。`xcode-select -p` と `xcrun --show-sdk-path` から始め、古い例の CLT パッケージを入れないでください。Apple の[コマンドラインツール案内](https://developer.apple.com/library/archive/technotes/tn2339/_index.html)が選択ディレクトリと SDK を説明します。

## 実際の gem の失敗へ戻る

成功は調査を絞りますが、拡張は別のフラグ、ヘッダー、ライブラリ、ABI を使う可能性があります。失敗ログを残し実コマンドを比較します。`scripts/ruby_cxx_fix.rb` は明示読込時に Ruby プロセス内の RbConfig を変え、Homebrew フォールバックもホスト固有です。失敗が一致する場合だけ適用し、既存 RUBYOPT を無条件で上書きしません。

ローカルの成功は Ruby 再導入や旧サイトの gem 再構築をしたわけではありません。次は[分離した二ページ Jekyll bundle](/en/posts/2023-09-04-jekyll-install/)、現行サイトは [Astro 品質ゲート](/en/posts/2026-04-07-jekyll-quality-gates-proof-html-bundler-audit/)を使います。
