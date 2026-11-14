---
kind: post
publishedAt: "2026-11-13T11:57:37.221186+00:00"
updatedAt: "2026-11-13T11:57:37.221186+00:00"
reviewedAt: "2026-11-13"
reviewStatus: source-audited
reviewScope: "Independent AI article/code/diagram review and correction recheck. Rust 1.100.0 tests 8 stream contracts and 13 CLI cases in each of debug and release, broken stdout/stderr and a 100000-record fixture. Simplified two-field log format; no performance or process-memory benchmark."
reviewSources: ["https://rust-lang.org/tools/install/", "https://doc.rust-lang.org/std/io/struct.BufReader.html", "https://doc.rust-lang.org/std/io/trait.BufRead.html#method.read_until", "https://doc.rust-lang.org/std/io/trait.Read.html#method.take", "https://doc.rust-lang.org/std/collections/struct.BTreeMap.html"]
language: en
translationKey: 2026-11-13-rust-log-cli
routeSlug: 2026-11-13-rust-log-cli
title: "Using Rust: build a line-by-line access log aggregation CLI"
description: "Build a Rust CLI to stream a simplified access log. Connect BufReader, BufRead and BTreeMap to byte limits, error handling, exit codes and tests."
categories: [rust]
tags: [rust, cli, file-processing, streaming, testing]
---

**A file-processing CLI with clear inputs and results is a good way to start using Rust for real work.** This article reads a log one line at a time and counts requests by HTTP status code. The key is to avoid holding the entire file as a string and to distinguish invalid records from read failures.

We apply ownership, borrowing and `Result` from the [earlier Rust introduction](/en/posts/2026-11-13-rust-ownership-guide/) to file I/O. The example was run with **Rust 1.100.0, edition 2024, on macOS arm64** and uses only the standard library. It requires no external packages or network connection. If you do not have the development tools yet, start with the [official Rust installation instructions](https://rust-lang.org/tools/install/).

## What work is a good fit for Rust?

Repeatedly run file conversion, validation and aggregation tools are useful places to learn Rust's resource management and error handling. When distributing binaries to a team, match the target operating system, CPU and required system libraries. An executable built on one machine will not run in every environment.

A familiar shell or Python may finish a one-off analysis sooner. Instead of guessing throughput, weigh the need to maintain the tool repeatedly against the team's learning costs. This article verifies the processing flow and failure behavior; it does not compare speed or memory usage with other languages.

## Define the log format and failure policy

The example reads a **simplified access log** of two fields, `status-code path`. It is not a parser for the default Nginx or Apache log format. The input is assumed to be a regular file whose writing has finished; rotation, live tailing and decompression are outside scope.

| Condition | Handling |
| --- | --- |
| Two whitespace-separated fields, a three-digit ASCII status in 100–599, and a path beginning with `/` | Increment `valid` and the count for that status |
| Blank line, or field count, status or path fails the rules | Increment `invalid` and continue with the next line |
| Failure to open or read the file, invalid UTF-8, or a line longer than 4096 bytes | Fail analysis and exit with code 2 without printing the totals |
| Processing reaches EOF with `invalid` equal to 0 | Print totals and exit with code 0 |
| Processing reaches EOF with `invalid` of at least 1 | Print totals and exit with code 1 |

Whitespace separation includes consecutive spaces and tabs. The line limit includes line-ending bytes such as LF or CRLF, and the last line need not end with a newline. An empty file is a successful result with `valid=0 invalid=0`. The path is used only to check format, not stored in the totals.

Output failure also produces exit code 2. Totals are not printed before analysis completes, but **if the output device fails while writing, some output may already have been written**. The execution contract is to check the exit code before using the result.

## Prepare the project

These commands and examples use a macOS or Linux shell. On macOS, also install the Command Line Tools needed for native linking.

```bash
rustup toolchain install 1.100.0 --profile minimal --component rustfmt --component clippy
cargo +1.100.0 new access-summary --bin --edition 2024
cd access-summary
mkdir -p examples tests
```

Save the files below. Cargo connects `src/lib.rs` as a library and `src/main.rs` as the executable. This separation lets you check file opening and terminal output separately from aggregation logic.

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

## Aggregate with BufReader and BTreeMap

![main checks its file argument and starts analysis with BufReader. It reads at most 4097 bytes of the current line and returns totals at EOF. A read failure, line longer than 4096 bytes or invalid UTF-8 returns an error. A valid record increments the status count; an invalid one increments invalid. The loop reads the next line. main prints sorted totals and returns exit code 0, 1 or 2 according to the result.](/assets/img/architecture/log-cli-flow-en.svg)

The loop path shows reading the next line after one line is processed. The right-hand line connects EOF to the return of totals. Argument, file, analysis and output errors are summarized in the lower error box; the code propagates them to `main` with `?`.

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

[`BufReader`](https://doc.rust-lang.org/std/io/struct.BufReader.html) buffers small read requests. `analyze<R: BufRead>` requires buffered-read behavior rather than a concrete file type, so tests can substitute an in-memory `Cursor` or an input that fails. The generic does not imply asynchronous or parallel processing.

Reading line by line does not itself impose a size limit. [`read_until`](https://doc.rust-lang.org/std/io/trait.BufRead.html#method.read_until) appends to a buffer until the delimiter or EOF. It can read very long lines, so the example uses [`Read::take`](https://doc.rust-lang.org/std/io/trait.Read.html#method.take) to **consume at most 4097 bytes in one iteration** before checking whether the line exceeds 4096 bytes. `take` is a byte limit, not a read-time limit.

`buffer.clear()` resets the buffer length for the next line and reuses its allocation. The aggregation vector holds the current line, and `BufReader` may have read ahead. The read buffer, vector allocation and aggregation map each need memory. Since status codes are limited to at most 500 types, an increasing number of URLs does not increase the map's key count. This is not a measurement of actual process memory.

`parse_status` borrows the string as `&str`, checks it and returns only the status code. [`BTreeMap`](https://doc.rust-lang.org/std/collections/struct.BTreeMap.html) iterates in key order, making it suitable for printing statuses in ascending order. `entry(...).or_default()` starts a missing status counter at zero.

## Decide output and exit codes in main

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

`args_os` takes the file path as an operating-system string. Since the analyzer's `io::Result<Stats>` connects to `run`'s `io::Result<u8>`, file-open and analysis failures can reach the error branch in `main`. `BufWriter` also buffers output, and `flush()?` checks whether writing remaining output failed. If writing the diagnostic to standard error itself fails, that write error is ignored and exit code 2 is retained.

`invalid` counts records that were readable but failed the rules. Output alone therefore does not mean every input was valid. Exit code 1 means analysis completed with at least one invalid record; if all lines were invalid, `valid` can be 0. Code 2 means execution failed. The tests and separate CLI runs below check that distinction.

## Run the sample and check the result

```bash
cargo check --offline
cargo fmt --check
cargo clippy --offline --all-targets -- -D warnings
cargo build --offline --release
./target/release/access-summary examples/access.log
echo $?
```

The sample has four valid lines and two invalid lines. The actual output follows. The final `1` is the exit code observed with `echo $?`, not part of the totals.

```text
valid=4 invalid=2
status=200 count=2
status=404 count=1
status=503 count=1
1
```

| Additional input or execution condition | Standard output | Exit code |
| --- | --- | --- |
| File containing only valid lines | Full totals | 0 |
| Empty file | `valid=0 invalid=0` | 0 |
| One blank line | `valid=0 invalid=1` | 1 |
| Missing file argument, two arguments, or nonexistent file | None; reason on stderr | 2 |
| Invalid UTF-8 after a valid line | None; reason on stderr | 2 |
| A 4097-byte line | None; reason on stderr | 2 |

## Test boundaries and failures without files

`Cursor` lets in-memory bytes be read like input. Without depending on disk or network, a separate type also injects a read failure that is cumbersome to create with a real file. Save the file below and run the command.

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

All eight executed tests passed. Separate CLI checks compared output and exit codes in both debug and release modes and verified the count for 100,000 identical valid lines. That input checked aggregation accuracy; it was not a load test guaranteeing throughput, maximum file size or memory consumption.

To extend this into an operational tool, first choose a parser matching the real log format and start with files whose writing has finished. URL-level aggregation or live collection needs separate design for key count, retention, file rotation and duplicate counting after restart. Simply expanding this example's status-code totals does not solve those problems.
