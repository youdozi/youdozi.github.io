---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "hi",
  "translationKey": "2026-11-13-rust-log-cli",
  "routeSlug": "2026-11-13-rust-log-cli",
  "kind": "post",
  "title": "Rust में एक्सेस लॉग को पंक्ति दर पंक्ति पढ़कर गिनती करने वाला CLI बनाएँ",
  "description": "सरल एक्सेस लॉग पढ़ने के लिए Rust में BufReader, BufRead और BTreeMap इस्तेमाल करें। बाइट की सीमा, त्रुटि, एग्ज़िट कोड और उनके टेस्ट उदाहरण से समझें।",
  "categories": [
    "rust"
  ],
  "tags": [
    "rust",
    "cli",
    "file-processing",
    "streaming",
    "testing"
  ],
  "sourcePath": "src/content/posts/en/2026-11-13-rust-log-cli.md",
  "sourceSha256": "4d2fd4771a2fa07143e52582adf4beccc6662d6b6cbba32538ca807a509c86f0",
  "draftSha256": "5d811ea1672f614dda352960e51121f828921d7939c74bddcaeacc6ee9ff1830",
  "manifestPath": ".pipeline/technical-translations/batch-1341/manifest.json",
  "manifestSha256": "c799b6f94efb991d515ad7d285b737aad0702b220d0e539fdf6b3bc60d7efb56",
  "publishedAt": "2026-11-27T08:44:35.252Z",
  "updatedAt": "2026-11-27T08:44:35.252Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 210,
    "approvedAt": "2026-11-27T08:44:35.252Z",
    "basis": "User authorized publication of the five named Hindi technical editions in item 134."
  }
}
---

**Rust को किसी वास्तविक काम में आज़माने के लिए ऐसी फ़ाइल प्रोसेसिंग CLI से शुरुआत कर सकते हैं जिसका इनपुट और परिणाम स्पष्ट हो।** यहाँ लॉग को एक-एक पंक्ति पढ़कर हर HTTP स्टेटस कोड के अनुरोध गिनेंगे। पूरी फ़ाइल को स्ट्रिंग में रखने से बचेंगे और गलत रिकॉर्ड को फ़ाइल पढ़ने की विफलता से अलग पहचानेंगे।

[Rust के पिछले परिचय](/en/posts/2026-11-13-rust-ownership-guide/) में देखे गए स्वामित्व, उधार और `Result` को अब फ़ाइल I/O में लागू करेंगे। उदाहरण **Rust 1.100.0, edition 2024 और macOS arm64** पर चलाया गया। इसे केवल मानक लाइब्रेरी चाहिए। किसी बाहरी पैकेज या नेटवर्क कनेक्शन की ज़रूरत नहीं है। टूल इंस्टॉल करने के लिए [Rust के आधिकारिक निर्देश](https://rust-lang.org/tools/install/) देखें।

## किन कामों में Rust आज़मा सकते हैं?

बार-बार चलने वाले फ़ाइल रूपांतरण, सत्यापन और गणना के टूल लिखते हुए Rust में संसाधन और त्रुटियाँ सँभालना सीख सकते हैं। टीम को बाइनरी देते समय लक्षित ऑपरेटिंग सिस्टम, CPU और ज़रूरी सिस्टम लाइब्रेरी का मिलान करें। एक मशीन पर बना प्रोग्राम हर जगह नहीं चलेगा।

एक बार के विश्लेषण के लिए परिचित शेल या Python में काम जल्दी पूरा हो सकता है। थ्रूपुट का अनुमान लगाने की जगह देखें कि टूल का रखरखाव कितनी बार करना होगा और टीम को सीखने में कितनी मेहनत लगेगी। यहाँ प्रोसेसिंग का क्रम और विफल होने पर व्यवहार जाँचा गया है। दूसरी भाषाओं के साथ गति या मेमोरी की तुलना नहीं की गई।

## लॉग का प्रारूप और त्रुटियों के नियम तय करें

उदाहरण दो फ़ील्ड वाला **सरल एक्सेस लॉग** पढ़ता है जिसका प्रारूप `status-code path` है। Nginx या Apache के डिफ़ॉल्ट लॉग के लिए दूसरा पार्सर चाहिए। इनपुट एक सामान्य फ़ाइल है जिसे लिखना पूरा हो चुका है। लॉग रोटेशन, लिखते समय नई पंक्तियाँ पढ़ना और डीकंप्रेशन इस उदाहरण के दायरे से बाहर हैं।

| शर्त | कार्रवाई |
| --- | --- |
| खाली जगह से अलग दो फ़ील्ड, 100–599 के बीच तीन ASCII अंकों का स्टेटस और `/` से शुरू होने वाला पथ | `valid` और उस स्टेटस की गिनती बढ़ाएँ |
| खाली पंक्ति या फ़ील्ड की संख्या, स्टेटस या पथ नियम से मेल नहीं खाता | `invalid` बढ़ाएँ और अगली पंक्ति पढ़ें |
| फ़ाइल खोलने या पढ़ने में विफलता, अमान्य UTF-8 या 4096 बाइट से लंबी पंक्ति | गणना प्रिंट किए बिना विश्लेषण रोकें और कोड 2 लौटाएँ |
| EOF पर `invalid` का मान 0 है | गणना प्रिंट करें और कोड 0 लौटाएँ |
| EOF पर `invalid` का मान कम से कम 1 है | गणना प्रिंट करें और कोड 1 लौटाएँ |

फ़ील्ड के बीच कई स्पेस या टैब हो सकते हैं। पंक्ति की सीमा में LF या CRLF के बाइट भी गिने जाते हैं। अंतिम पंक्ति का न्यूलाइन पर खत्म होना ज़रूरी नहीं है। खाली फ़ाइल का सफल परिणाम `valid=0 invalid=0` है। पथ से केवल प्रारूप जाँचते हैं, उसे गणना में सहेजते नहीं हैं।

आउटपुट लिखने में विफलता पर भी एग्ज़िट कोड 2 मिलता है। पूरा विश्लेषण होने तक गणना प्रिंट नहीं होती, लेकिन **लिखते समय आउटपुट डिवाइस विफल हो तो कुछ हिस्सा पहले ही लिखा जा चुका हो सकता है**। परिणाम का इस्तेमाल करने से पहले एग्ज़िट कोड देखें।

## प्रोजेक्ट तैयार करें

कमांड और उदाहरण macOS या Linux शेल के लिए हैं। macOS पर नेटिव लिंकिंग के लिए Command Line Tools भी इंस्टॉल करें।

```bash
rustup toolchain install 1.100.0 --profile minimal --component rustfmt --component clippy
cargo +1.100.0 new access-summary --bin --edition 2024
cd access-summary
mkdir -p examples tests
```

नीचे की फ़ाइलें सहेजें। Cargo में `src/lib.rs` लाइब्रेरी है और `src/main.rs` से एक्ज़ीक्यूटेबल बनता है। इस तरह फ़ाइल खोलने और टर्मिनल पर लिखने का व्यवहार गणना के तर्क से अलग जाँच सकते हैं।

### `Cargo.toml`

```toml
[package]
name = "access-summary"
version = "0.1.0"
edition = "2024"

[dependencies]
```

### `rust-toolchain.toml`

```toml
[toolchain]
channel = "1.100.0"
profile = "minimal"
components = ["rustfmt", "clippy"]
```

### `examples/access.log`

```text
200 /api/orders
503 /api/orders
200 /health
404 /missing
broken-line
700 /outside-range
```

## BufReader और BTreeMap से अनुरोध गिनें

![main फ़ाइल का आर्ग्युमेंट जाँचकर BufReader से विश्लेषण शुरू करता है। मौजूदा पंक्ति से अधिकतम 4097 बाइट पढ़ता है और EOF पर गणना लौटाता है। पढ़ने में विफलता, 4096 बाइट से लंबी पंक्ति या अमान्य UTF-8 पर त्रुटि मिलती है। वैध रिकॉर्ड पर स्टेटस की गिनती बढ़ती है, अन्यथा invalid बढ़ता है। अगली पंक्ति के लिए लूप दोहरता है। main क्रमबद्ध परिणाम प्रिंट करके उपयुक्त एग्ज़िट कोड 0, 1 या 2 देता है।](/assets/diagrams/technical/hi-2026-11-13-rust-log-cli.svg)

लूप की रेखा एक पंक्ति का काम पूरा होने के बाद अगली पंक्ति पढ़ने का रास्ता दिखाती है। दाईं रेखा EOF को गणना लौटाने के चरण से जोड़ती है। नीचे के बॉक्स में आर्ग्युमेंट, फ़ाइल, विश्लेषण और आउटपुट की त्रुटियाँ हैं। कोड में ये `?` के ज़रिए `main` तक पहुँचती हैं।

### `src/lib.rs`

```rust
use std::{
    collections::BTreeMap,
    io::{self, BufRead, Read},
    str,
};

pub const MAX_LINE_BYTES: usize = 4096;

#[derive(Default, Debug, PartialEq, Eq)]
pub struct Stats {
    pub valid: u64,
    pub invalid: u64,
    pub by_status: BTreeMap<u16, u64>,
}

fn parse_status(line: &str) -> Option<u16> {
    let mut fields = line.split_whitespace();
    let code = fields.next()?;
    let path = fields.next()?;
    if fields.next().is_some() || !path.starts_with('/') {
        return None;
    }
    if code.len() != 3 || !code.bytes().all(|byte| byte.is_ascii_digit()) {
        return None;
    }
    let status = code.parse::<u16>().ok()?;
    (100..=599).contains(&status).then_some(status)
}

pub fn analyze<R: BufRead>(mut reader: R) -> io::Result<Stats> {
    let mut stats = Stats::default();
    let mut buffer = Vec::new();
    loop {
        buffer.clear();
        let read = reader
            .by_ref()
            .take((MAX_LINE_BYTES + 1) as u64)
            .read_until(b'\n', &mut buffer)?;
        if read == 0 {
            return Ok(stats);
        }
        if buffer.len() > MAX_LINE_BYTES {
            return Err(io::Error::new(
                io::ErrorKind::InvalidData,
                "line exceeds 4096 bytes",
            ));
        }
        let line = str::from_utf8(&buffer)
            .map_err(|_| io::Error::new(io::ErrorKind::InvalidData, "input is not UTF-8"))?;
        match parse_status(line) {
            Some(status) => {
                stats.valid += 1;
                *stats.by_status.entry(status).or_default() += 1;
            }
            None => stats.invalid += 1,
        }
    }
}
```

[`BufReader`](https://doc.rust-lang.org/std/io/struct.BufReader.html) छोटे रीड अनुरोधों के लिए बफ़र रखता है। `analyze<R: BufRead>` को बफ़र से पढ़ने की क्षमता चाहिए। इससे टेस्ट में फ़ाइल की जगह मेमोरी में रखा `Cursor` या पढ़ने पर विफल होने वाला इनपुट दे सकते हैं। यह जेनेरिक टाइप अपने आप असिंक्रोनस या समानांतर प्रोसेसिंग नहीं करता।

एक-एक पंक्ति पढ़ने से उसके आकार पर अपने आप सीमा नहीं लगती। [`read_until`](https://doc.rust-lang.org/std/io/trait.BufRead.html#method.read_until) विभाजक या EOF मिलने तक बफ़र में बाइट जोड़ता है और बहुत लंबी पंक्ति भी पढ़ सकता है। यहाँ [`Read::take`](https://doc.rust-lang.org/std/io/trait.Read.html#method.take) से **हर चक्र में अधिकतम 4097 बाइट पढ़कर** जाँचते हैं कि पंक्ति 4096 बाइट से लंबी है या नहीं। `take` बाइट सीमित करता है, पढ़ने का समय नहीं।

`buffer.clear()` अगली पंक्ति के लिए बफ़र की लंबाई रीसेट करता है और आवंटित मेमोरी फिर इस्तेमाल होती है। वेक्टर में मौजूदा पंक्ति रहती है और `BufReader` कुछ बाइट आगे तक पढ़ चुका हो सकता है। रीड बफ़र, वेक्टर और गणना के मैप, तीनों के लिए मेमोरी चाहिए। अधिकतम 500 अलग स्टेटस कोड हो सकते हैं, इसलिए URL की संख्या बढ़ने से मैप की कुंजियाँ नहीं बढ़तीं। यहाँ प्रक्रिया की वास्तविक मेमोरी नहीं मापी गई।

`parse_status` स्ट्रिंग को `&str` के रूप में उधार लेकर जाँचता है और केवल स्टेटस कोड लौटाता है। [`BTreeMap`](https://doc.rust-lang.org/std/collections/struct.BTreeMap.html) की प्रविष्टियाँ कुंजी के क्रम में मिलती हैं, जिससे स्टेटस को बढ़ते क्रम में प्रिंट करना आसान है। `entry(...).or_default()` नए स्टेटस की गिनती शून्य से शुरू करता है।

## main में आउटपुट और एग्ज़िट कोड तय करें

### `src/main.rs`

```rust
use access_summary::analyze;
use std::{
    env,
    fs::File,
    io::{self, BufReader, Write},
    process::ExitCode,
};

fn run() -> io::Result<u8> {
    let mut args = env::args_os().skip(1);
    let path = args
        .next()
        .filter(|_| args.next().is_none())
        .ok_or_else(|| {
            io::Error::new(io::ErrorKind::InvalidInput, "usage: access-summary <file>")
        })?;
    let stats = analyze(BufReader::new(File::open(path)?))?;
    let mut out = io::BufWriter::new(io::stdout().lock());
    writeln!(out, "valid={} invalid={}", stats.valid, stats.invalid)?;
    for (status, count) in &stats.by_status {
        writeln!(out, "status={status} count={count}")?;
    }
    out.flush()?;
    Ok(if stats.invalid == 0 { 0 } else { 1 })
}

fn main() -> ExitCode {
    match run() {
        Ok(code) => ExitCode::from(code),
        Err(error) => {
            let _ = writeln!(io::stderr().lock(), "error: {error}");
            ExitCode::from(2)
        }
    }
}
```

`args_os` फ़ाइल का पथ ऑपरेटिंग सिस्टम की स्ट्रिंग के रूप में लेता है। विश्लेषक का `io::Result<Stats>`, `run` के `io::Result<u8>` से जुड़ता है, इसलिए फ़ाइल खोलने और विश्लेषण की विफलता `main` की त्रुटि शाखा तक पहुँच सकती है। `BufWriter` आउटपुट भी बफ़र करता है। `flush()?` बचा हुआ आउटपुट लिखने में विफलता जाँचता है। यदि मानक त्रुटि स्ट्रीम पर संदेश लिखना भी विफल हो, तो उस विफलता को अनदेखा करके एग्ज़िट कोड 2 रखा जाता है।

`invalid` उन रिकॉर्ड की संख्या है जो पढ़े जा सके लेकिन नियमों पर खरे नहीं उतरे। आउटपुट मिलना सभी इनपुट के वैध होने का प्रमाण नहीं है। कोड 1 का अर्थ है कि विश्लेषण पूरा हुआ और कम से कम एक रिकॉर्ड अमान्य था। यदि सभी पंक्तियाँ अमान्य थीं, तो `valid` का मान 0 हो सकता है। कोड 2 निष्पादन की विफलता है। नीचे के टेस्ट और अलग CLI रन इस अंतर की जाँच करते हैं।

## नमूना चलाएँ और परिणाम जाँचें

```bash
cargo check --offline
cargo fmt --check
cargo clippy --offline --all-targets -- -D warnings
cargo build --offline --release
./target/release/access-summary examples/access.log
echo $?
```

नमूने में चार वैध और दो अमान्य पंक्तियाँ हैं। नीचे वास्तविक आउटपुट है। अंत में दिख रहा `1` गणना का हिस्सा नहीं है। यह `echo $?` से देखा गया एग्ज़िट कोड है।

```text
valid=4 invalid=2
status=200 count=2
status=404 count=1
status=503 count=1
1
```

| अतिरिक्त इनपुट या रन की स्थिति | मानक आउटपुट | एग्ज़िट कोड |
| --- | --- | --- |
| केवल वैध पंक्तियों वाली फ़ाइल | पूरी गणना | 0 |
| खाली फ़ाइल | `valid=0 invalid=0` | 0 |
| एक खाली पंक्ति | `valid=0 invalid=1` | 1 |
| फ़ाइल का आर्ग्युमेंट गायब, दो आर्ग्युमेंट या फ़ाइल मौजूद नहीं | कोई नहीं, कारण stderr पर | 2 |
| एक वैध पंक्ति के बाद अमान्य UTF-8 | कोई नहीं, कारण stderr पर | 2 |
| 4097 बाइट की पंक्ति | कोई नहीं, कारण stderr पर | 2 |

## बिना फ़ाइल बनाए सीमाएँ और विफलताएँ जाँचें

`Cursor` से मेमोरी में रखे बाइट इनपुट की तरह पढ़ सकते हैं। एक अलग टाइप पढ़ते समय जानबूझकर त्रुटि देता है। असली फ़ाइल में ऐसी त्रुटि पैदा करना मुश्किल है, और यहाँ डिस्क या नेटवर्क की ज़रूरत भी नहीं पड़ती। नीचे दी गई फ़ाइल सहेजकर कमांड चलाएँ।

```bash
cargo test --offline
```

### `tests/stream.rs`

```rust
use access_summary::{MAX_LINE_BYTES, analyze};
use std::io::{self, BufRead, Cursor, Read};

#[test]
fn counts_valid_and_invalid_lines_in_status_order() {
    let stats = analyze(Cursor::new(include_bytes!("../examples/access.log"))).unwrap();
    assert_eq!((stats.valid, stats.invalid), (4, 2));
    assert_eq!(
        stats.by_status.into_iter().collect::<Vec<_>>(),
        vec![(200, 2), (404, 1), (503, 1)]
    );
}

#[test]
fn accepts_crlf_and_a_final_line_without_newline() {
    let stats = analyze(Cursor::new(b"200 /a\r\n503 /b")).unwrap();
    assert_eq!((stats.valid, stats.invalid), (2, 0));
}

#[test]
fn empty_file_and_blank_line_are_different() {
    assert_eq!(analyze(Cursor::new(b"")).unwrap().invalid, 0);
    assert_eq!(analyze(Cursor::new(b"\n")).unwrap().invalid, 1);
}

#[test]
fn rejects_malformed_status_and_fields_as_invalid_records() {
    let data = "099 /a\n600 /a\n+20 /a\n２００ /a\n200 relative\n200 /a extra\n200\n";
    let stats = analyze(Cursor::new(data.as_bytes())).unwrap();
    assert_eq!((stats.valid, stats.invalid), (0, 7));
}

#[test]
fn invalid_utf8_aborts_instead_of_reporting_partial_statistics() {
    let error = analyze(Cursor::new(b"200 /a\n\xff\n")).unwrap_err();
    assert_eq!(error.kind(), io::ErrorKind::InvalidData);
    assert_eq!(error.to_string(), "input is not UTF-8");
}

#[test]
fn accepts_exact_byte_limit_including_newline() {
    let mut data = b"200 /".to_vec();
    data.resize(MAX_LINE_BYTES - 1, b'a');
    data.push(b'\n');
    assert_eq!(analyze(Cursor::new(data)).unwrap().valid, 1);
}

#[test]
fn stops_consuming_an_oversized_line_after_limit_plus_one() {
    let mut reader = Cursor::new(vec![b'x'; 100_000]);
    let error = analyze(&mut reader).unwrap_err();
    assert_eq!(error.to_string(), "line exceeds 4096 bytes");
    assert_eq!(reader.position(), (MAX_LINE_BYTES + 1) as u64);
}

struct FailingReader;
impl Read for FailingReader {
    fn read(&mut self, _: &mut [u8]) -> io::Result<usize> {
        Err(io::Error::other("injected read failure"))
    }
}
impl BufRead for FailingReader {
    fn fill_buf(&mut self) -> io::Result<&[u8]> {
        Err(io::Error::other("injected read failure"))
    }
    fn consume(&mut self, _: usize) {}
}

#[test]
fn propagates_reader_failure() {
    assert_eq!(
        analyze(FailingReader).unwrap_err().to_string(),
        "injected read failure"
    );
}
```

चलाए गए सभी आठ टेस्ट सफल रहे। अलग CLI रन में debug और release दोनों के आउटपुट और एग्ज़िट कोड की तुलना की गई। एक जैसी 100,000 वैध पंक्तियों की गिनती भी जाँची गई। इससे गणना की शुद्धता जाँची गई थी। थ्रूपुट, अधिकतम फ़ाइल आकार या मेमोरी खपत के लिए लोड टेस्ट नहीं किया गया।

इसे संचालन में इस्तेमाल करने के लिए पहले वास्तविक लॉग के प्रारूप से मेल खाता पार्सर चुनें और ऐसी फ़ाइलों से शुरू करें जिन्हें लिखना पूरा हो चुका है। हर URL की अलग गिनती या लाइव संग्रह के लिए कुंजियों की संख्या, डेटा रखने की अवधि, फ़ाइल रोटेशन और रीस्टार्ट के बाद दोहरी गिनती पर अलग से विचार करें। केवल स्टेटस कोड की गणना बढ़ाने से ये समस्याएँ हल नहीं होतीं।
