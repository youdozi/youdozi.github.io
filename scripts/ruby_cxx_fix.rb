require "rbconfig"

cxx = ENV.fetch("RUBY_CXX", "clang++")
default_cppflags = ""

begin
  sdk_path = `xcrun --show-sdk-path`.strip
  cxx_headers = "#{sdk_path}/usr/include/c++/v1"
  if !sdk_path.empty? && File.directory?(cxx_headers)
    default_cppflags = "-isysroot #{sdk_path} -isystem #{cxx_headers}"
  else
    default_cppflags = "-nostdinc++ -isystem /opt/homebrew/opt/llvm/include/c++/v1"
  end
rescue StandardError
  default_cppflags = "-nostdinc++ -isystem /opt/homebrew/opt/llvm/include/c++/v1"
end

extra_cppflags = ENV.fetch("RUBY_EXTRA_CPPFLAGS", default_cppflags)

[RbConfig::CONFIG, RbConfig::MAKEFILE_CONFIG].each do |config|
  config["CXX"] = cxx
  config["CPPFLAGS"] = [config["CPPFLAGS"], extra_cppflags].compact.join(" ").strip
  config["CXXFLAGS"] = [config["CXXFLAGS"], "-stdlib=libc++"].compact.join(" ").strip
end
