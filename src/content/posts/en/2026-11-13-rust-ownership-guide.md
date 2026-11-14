---
kind: post
publishedAt: "2026-11-13T06:49:08.685311+00:00"
updatedAt: "2026-11-13T06:49:08.685311+00:00"
reviewedAt: "2026-11-13"
reviewStatus: source-audited
reviewScope: "Independent AI static review of the Korean Rust introduction, followed by author corrections and reviewer recheck. Rust 1.100.0 CLI verified with 12 cases in each of debug and release, 9 cargo run cases and expected E0382/E0502 compiler errors. No comparative performance or concurrent server testing."
reviewSources: ["https://rust-lang.org/", "https://rust-lang.org/tools/install/", "https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html", "https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html", "https://doc.rust-lang.org/book/ch01-03-hello-cargo.html", "https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html", "https://doc.rust-lang.org/book/ch16-04-extensible-concurrency-sync-and-send.html", "https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html"]
language: en
translationKey: 2026-11-13-rust-ownership-guide
routeSlug: 2026-11-13-rust-ownership-guide
title: "Rust introduction: ownership, borrowing, and Result with runnable examples"
description: "Understand Rust ownership and borrowing alongside Java references. Build an amount-summing CLI with Cargo and check Result errors, integer overflow, and compiler diagnostics."
categories: [rust]
tags: [rust, ownership, borrowing, cargo, error-handling]
---

**Rust checks memory-use rules at compile time through ownership and type checking.** Instead of a garbage collector tracking object reachability as in Java and Kotlin, code expresses who owns a value and how long it is borrowed. This lets you read compiler errors as data-use contracts rather than mere syntax restrictions.

This introduction is for developers who have written functions in another language. The examples were run with **Rust 1.100.0, edition 2024, on macOS arm64**. An edition selects syntax and compatibility rules independently of the compiler version. The examples use only the standard library and make no external network requests.

## What problems can Rust help with?

Rust compiles to native code and does not require a tracing GC for its default memory management. It is worth considering for CLIs, system components, and programs with important memory or latency budgets. Its [official introduction](https://rust-lang.org/) also lists performance and memory safety as goals. The absence of a GC alone does not prove that Rust is faster or has lower latency than Java. This article does not measure comparative performance.

| Criterion | Java/Kotlin on the JVM | Rust |
| --- | --- | --- |
| Typical object memory management | GC tracks objects to reclaim | Resources cleaned up through ownership and `Drop` |
| Passing data | Multiple places can hold object references | Values move or copy depending on type and can be borrowed by reference |
| Communicating failures | Exceptions, result types and other mechanisms | APIs commonly express success or failure with `Result<T, E>` |
| Adoption costs to check | Existing JVM libraries and team experience | Learning ownership and the fit of libraries, build and operational tools |

If an existing service is bottlenecked by database waits or external APIs, measure those paths before changing languages. For a first adoption, start with a small CLI with clear boundaries and examine development and deployment costs.

## How do ownership and borrowing differ?

First install `rustup` and Rust using the [official instructions](https://rust-lang.org/tools/install/) for your operating system, then run the examples below. On macOS, also install the Command Line Tools needed for native linking.

A `String` owns its string data. Save the following as `move_error.rs`; it **intentionally fails to compile**.

```rust
fn main() {
    let name = String::from("Rust");
    let moved = name;
    println!("{name}, {moved}");
}
```

```bash
rustc --edition 2024 move_error.rs
```

Because `let moved = name` transfers ownership, the later attempt to print `name` produces **E0382: borrow of moved value**. Not every assignment moves a value: types that implement `Copy`, such as `u64`, are copied on assignment. `String::clone()` duplicates separate string data, so use it when needed. See the [official ownership explanation](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html) for the rules.

When only reading a value, you can borrow it with `&` instead of transferring ownership. Save the next code in a separate `borrow_ok.rs` file.

```rust
fn main() {
    let mut name = String::from("Rust");
    let borrowed = &name;
    println!("{borrowed}");
    name.push_str(" language");
    println!("{name}");
}
```

```bash
rustc --edition 2024 borrow_ok.rs -o borrow_ok
./borrow_ok
```

The actual output is:

```text
Rust
Rust language
```

After the first `println!`, `borrowed` is not used again, so the shared borrow ends. This allows `name` to be modified later in the same block. If you print `borrowed` again after `push_str`, the reference's required lifetime overlaps the exclusive borrow needed for mutation, and compilation fails.

A useful starting rule is **multiple shared references `&T` or one exclusive reference `&mut T`** to the same data. This does not mean that `&T` forbids all interior mutability. The [official borrowing documentation](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html) gives the detailed conditions. A lifetime expresses relationships between periods during which references must be valid; it does not keep memory alive longer.

## Build an amount-summing CLI with Cargo

The program prints the count and sum of integer amounts. It is an explanatory program, not a payment implementation for a particular service, and assumes all inputs use the same unit. It does not accept decimals or negative values; each amount and the total must fit in `u64`.

These commands use a macOS or Linux shell. Prepare the exercise version in an environment with Rust tools installed.

```bash
rustup toolchain install 1.100.0 --profile minimal --component rustfmt --component clippy
cargo +1.100.0 new expense-summary --bin --edition 2024
cd expense-summary
```

Set up the three files below. `rust-toolchain.toml` pins the tool version for this folder, and `Cargo.toml` contains package configuration. The [official Cargo introduction](https://doc.rust-lang.org/book/ch01-03-hello-cargo.html) also covers Cargo build and check commands.

### `Cargo.toml`

```toml
[package]
name = "expense-summary"
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

![main owns input strings and lends them to summarize. It rejects empty input, parses each value as u64 and accumulates it with checked_add. A failure returns Err immediately; otherwise it returns the count and sum. main sends success and failure to different output streams and exit codes.](/assets/img/architecture/rust-flow-en.svg)

The diagram shows the loop and early returns in `summarize`. The line returning to the next-value check on the left is the loop after a successful accumulation; all error paths on the right meet at the `Err` branch in `main`.

### `src/main.rs`

```rust
use std::{env, process::ExitCode};

struct Summary {
    count: usize,
    total: u64,
}

#[derive(Debug)]
enum InputError {
    EmptyInput,
    InvalidAmount,
    TotalOverflow,
}

fn summarize(inputs: &[String]) -> Result<Summary, InputError> {
    if inputs.is_empty() {
        return Err(InputError::EmptyInput);
    }

    let mut total = 0_u64;
    for input in inputs {
        let amount = input
            .parse::<u64>()
            .map_err(|_| InputError::InvalidAmount)?;
        total = total.checked_add(amount).ok_or(InputError::TotalOverflow)?;
    }

    Ok(Summary {
        count: inputs.len(),
        total,
    })
}

fn main() -> ExitCode {
    let inputs: Vec<String> = env::args().skip(1).collect();
    match summarize(&inputs) {
        Ok(summary) => {
            println!("count={}, total={}", summary.count, summary.total);
            ExitCode::SUCCESS
        }
        Err(error) => {
            eprintln!("error: {error:?}");
            ExitCode::FAILURE
        }
    }
}
```

`inputs` is a `Vec<String>` owned by `main`. `summarize(&inputs)` borrows its strings as a slice `&[String]`, without cloning the whole input or transferring ownership. `for input in inputs` also reads the strings by reference. Borrowing avoids copying input strings here, but it does not eliminate allocations during command-line argument collection.

`Summary` is a struct holding a successful result; `InputError` is an enum of possible failures. `Result<Summary, InputError>` is the contract that one of those results is returned. `?` returns early from the current function on `Err` and unwraps the inner value on success. It does not throw an exception or terminate the program immediately. The [official Result explanation](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html) describes error propagation.

`parse::<u64>()` checks the format and range of each number. If the sum of two values exceeds the range, `checked_add` returns `None`, which `ok_or` converts into a `TotalOverflow` error. Thus individually valid inputs can still overflow the total. `main` uses `match` to handle both outcomes, and `{:?}` prints the error name using its `Debug` format.

## What can you verify by running it?

```bash
rustc --version
cargo check --offline
cargo fmt --check
cargo clippy --offline -- -D warnings
cargo run --offline --quiet -- 12000 8000 0
```

Standard output from that run follows. Values after `--` are passed to the example program rather than Cargo.

```text
count=3, total=20000
```

These are representative results observed in actual CLI runs. On error, no partial sum is printed; errors go to standard error and exit with code 1.

| Arguments after `cargo run --offline --quiet --` | Output | Exit code |
| --- | --- | --- |
| `12000 8000 0` | stdout `count=3, total=20000` | 0 |
| `0` | stdout `count=1, total=0` | 0 |
| No arguments | stderr `error: EmptyInput` | 1 |
| `12000 abc` | stderr `error: InvalidAmount` | 1 |
| `-1` or `1.5` | stderr `error: InvalidAmount` | 1 |
| `18446744073709551616` | stderr `error: InvalidAmount` | 1 |
| `18446744073709551615 0` | stdout `count=2, total=18446744073709551615` | 0 |
| `18446744073709551615 1` | stderr `error: TotalOverflow` | 1 |

`cargo check` checks types and related properties without running the code. `cargo fmt --check` checks formatting, while Clippy provides static diagnostics. Even if they succeed, run the program separately to check the calculation rules. Here, output, errors and exit codes were compared in debug and release runs; throughput and production load were not measured.

## What does Rust guarantee?

Safe Rust's type and ownership checks help prevent invalid reference use and data races. Whether values can move between threads and references can be shared is also tied to type contracts such as [`Send` and `Sync`](https://doc.rust-lang.org/book/ch16-04-extensible-concurrency-sync-and-send.html). That does not eliminate all race conditions, deadlocks, memory leaks or business-logic errors.

[`unsafe`](https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html) makes the author responsible for the safety conditions of certain operations. It is not a switch that turns off the entire borrow checker; incorrect `unsafe` implementations or FFI boundaries can affect safety. Server, asynchronous execution and shared-state designs were not within the validation scope of this CLI.

For a next exercise, extend the program to read input amounts from a file. Decide how file I/O errors differ from the existing `InputError` to see more concretely how ownership and error types express program boundaries.
