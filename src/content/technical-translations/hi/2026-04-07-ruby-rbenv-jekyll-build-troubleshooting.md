---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2026-04-07-ruby-rbenv-jekyll-build-troubleshooting",
  "routeSlug": "2026-04-07-ruby-rbenv-jekyll-build-troubleshooting",
  "kind": "post",
  "title": "Ruby के नेटिव gem की बिल्ड विफलता: रनटाइम और C++ हेडर अलग-अलग जाँचें",
  "description": "अस्थायी C++ प्रोग्राम से पता लगाएँ कि समस्या Ruby शुरू होने में है या कम्पाइलेशन में। रनटाइम दोबारा इंस्टॉल किए बिना RbConfig की सेटिंग और एक कमांड तक सीमित SDK फ़्लैग की तुलना करें।",
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
  "draftSha256": "3d0792358049e8d7678ea0e248ae7a382eabedc722dceecf4bf8d28cdf060305",
  "manifestPath": ".pipeline/technical-translations/batch-141/manifest.json",
  "manifestSha256": "edfaf1b1fc31bea15d90b136c5f93dbf615cbf995ac63c9126177915c9e13875",
  "publishedAt": "2026-11-27T11:07:35.795Z",
  "updatedAt": "2026-11-27T11:07:35.795Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 217,
    "approvedAt": "2026-11-27T11:07:35.795Z",
    "basis": "The owner authorized publication of the five Hindi editions in item 141. Translation and diagram review was performed by the translator."
  }
}
---

Ruby शुरू होने की जाँच नेटिव एक्सटेंशन के कम्पाइलेशन से अलग करें। `ruby --version` चलने से यह साबित नहीं होता कि C++ कम्पाइलर को उसके हेडर मिलेंगे। इसी तरह एक स्वतंत्र C++ प्रोग्राम चलने से gem के एक्सटेंशन का कम्पाइलेशन सुनिश्चित नहीं होता।

मूल विवरण में दूसरे उपयोगकर्ता की Ruby लाइब्रेरी का पथ और macOS SDK के हेडर की समस्या सामने आई थी। दोनों अलग तरह की विफलताएँ हैं। नीचे की जाँच Ruby हटाए बिना, Command Line Tools बदले बिना और पूरे सिस्टम में RbConfig को ओवरराइड किए बिना इनका अंतर पता करती है। मौजूदा साइट Astro इस्तेमाल करती है। ये जाँच पुराने Ruby टूल के लिए हैं जो अभी भी रिपॉज़िटरी में हैं।

## जिस स्तर पर विफलता हो, वहीं से शुरू करें

![Ruby का स्टार्टअप और कम्पाइलर जाँचें, फिर अलग से छोटा C++ प्रोग्राम चलाएँ](/assets/diagrams/technical/hi-2026-04-07-ruby-rbenv-jekyll-build-troubleshooting.svg)

पहले चुने गए Ruby की तुलना उसकी दर्ज बिल्ड सेटिंग से करें।

```sh
command -v ruby
ruby --version
rbenv which ruby
ruby -rrbconfig -e 'puts RbConfig.ruby; puts RbConfig::CONFIG.values_at("CXX", "CPPFLAGS", "CXXFLAGS")'
```

यदि लाइब्रेरी न मिलने के कारण Ruby शुरू ही नहीं होता, तो gem इंस्टॉल करने से पहले उस इंटरप्रेटर और उससे जुड़ी लाइब्रेरी की जाँच करें। macOS पर `otool -L` से उस एक्ज़ीक्यूटेबल को देख सकते हैं जिसे `rbenv which ruby` चुनता है। एक नेटिव gem की विफलता के कारण Ruby के सभी संस्करण फिर से इंस्टॉल न करें।

[RbConfig](https://docs.ruby-lang.org/en/3.2/RbConfig.html) इंटरप्रेटर की बिल्ड सेटिंग दिखाता है। जाँचे गए Ruby 3.2.2 वातावरण में `CXX` का मान `false` था, फिर भी स्पष्ट रूप से चुना हुआ `c++` सही हेडर फ़्लैग के साथ चल सका। यह नतीजा उसी इंटरप्रेटर और होस्ट का है। Ruby 3.2 का [समर्थन समाप्त हो चुका है](https://www.ruby-lang.org/en/downloads/branches/)। यहाँ पुराने वातावरण की समस्या जाँची जा रही है।

## Ruby की सेटिंग बदले बिना कम्पाइल करें

Ruby की मानक लाइब्रेरी इस्तेमाल करने वाली यह पूरी स्क्रिप्ट `native_probe.rb` नाम से सहेजें।

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

जाँच के लिए चुने गए कम्पाइलर के साथ इसे चलाएँ।

```sh
ruby native_probe.rb
```

स्क्रिप्ट एक अस्थायी C++17 प्रोग्राम कम्पाइल करती है और उसका आउटपुट ठीक `42` होना चाहिए। `CXX` जाँच का कमांड चुनता है और `PROBE_CXXFLAGS` केवल इसी जाँच के फ़्लैग देता है। तुलना के लिए स्क्रिप्ट Ruby की CXX सेटिंग दिखाती है, उसे बदलती नहीं। `CXX` खाली होने, कम्पाइलेशन विफल होने या अप्रत्याशित आउटपुट मिलने पर प्रक्रिया शून्य से अलग एग्ज़िट कोड देती है।

जिस Mac पर जाँच हुई, वहाँ डिफ़ॉल्ट कमांड को `iostream` नहीं मिला। चुने गए SDK को देखने और उसकी हेडर डायरेक्टरी की मौजूदगी की पुष्टि करने के बाद केवल इस कमांड पर ये फ़्लैग लगाने से जाँच सफल हुई।

```sh
probe_sdk="$(xcrun --show-sdk-path)"
test -d "$probe_sdk/usr/include/c++/v1"
PROBE_CXXFLAGS="-isysroot $probe_sdk -isystem $probe_sdk/usr/include/c++/v1" ruby native_probe.rb
```

यह पथ उसी Mac पर जाँचा गया था। यह हर SDK समस्या का हल नहीं है। पथ में स्पेस हो तो फ़्लैग के मान के अंदर संबंधित टोकन सही ढंग से उद्धृत करें। शुरुआत `xcode-select -p` और `xcrun --show-sdk-path` से करें। किसी पुराने उदाहरण में दिए नाम के आधार पर CLT पैकेज इंस्टॉल न करें। Apple की [कमांड-लाइन टूल गाइड](https://developer.apple.com/library/archive/technotes/tn2339/_index.html) चुनी गई डेवलपर डायरेक्टरी और SDK टूल समझाती है।

## अब विफल gem का बिल्ड लॉग देखें

जाँच सफल होने से संभावित कारण कम हो जाते हैं। एक्सटेंशन के फ़्लैग, हेडर, लाइब्रेरी या ABI की ज़रूरतें फिर भी अलग हो सकती हैं। विफल gem का बिल्ड लॉग रखें और उसमें चले वास्तविक कमांड की तुलना करें। रिपॉज़िटरी की `scripts/ruby_cxx_fix.rb` स्पष्ट रूप से लोड किए जाने पर Ruby प्रक्रिया के अंदर RbConfig के मान बदलती है। उसका वैकल्पिक Homebrew पथ होस्ट पर निर्भर है। विफलता का कारण मेल खाने पर ही ऐसा उपाय करें और RUBYOPT में पहले से मौजूद विकल्प बचाकर रखें।

स्थानीय जाँच सफल हुई थी। इसमें Ruby दोबारा इंस्टॉल नहीं किया गया और पुरानी साइट के नेटिव gem फिर से नहीं बनाए गए। अगला स्तर जाँचने के लिए [दो पेज वाला अलग Jekyll बंडल](/en/posts/2023-09-04-jekyll-install/) देखें। चालू साइट की जाँच के लिए [Astro की गुणवत्ता जाँच गाइड](/hi/posts/2026-04-07-jekyll-quality-gates-proof-html-bundler-audit/) देखें।
