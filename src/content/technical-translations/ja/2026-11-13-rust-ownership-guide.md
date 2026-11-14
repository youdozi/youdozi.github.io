---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2026-11-13-rust-ownership-guide",
  "routeSlug": "2026-11-13-rust-ownership-guide",
  "kind": "post",
  "title": "Rust の概要: 所有権、借用、結果と実行可能なサンプル",
  "description": "Java リファレンスとともに Rust の所有権と借用について理解します。 Cargo を使用して金額合計 CLI を構築し、結果エラー、整数オーバーフロー、およびコンパイラ診断をチェックします。",
  "categories": [
    "rust"
  ],
  "tags": [
    "rust",
    "ownership",
    "borrowing",
    "cargo",
    "error-handling"
  ],
  "sourcePath": "src/content/posts/en/2026-11-13-rust-ownership-guide.md",
  "sourceSha256": "b6f336e010d9bfad88b7108ccfb60a6c7f30048a3bb7e54fa94483e719e26d40",
  "draftSha256": "2d5c7a4fe11b4af820d63dcac7b2cb5e473b007364863009967dd2a8119a1005",
  "manifestPath": ".pipeline/technical-translations/batch-156/manifest.json",
  "manifestSha256": "ed48dc20825daff8725d8eba3418b1ad885276b52c9752ba958f7a1705b24430",
  "publishedAt": "2026-11-14T15:16:43.783Z",
  "updatedAt": "2026-11-14T15:16:43.783Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 158,
    "approvedAt": "2026-11-14T15:16:43.783Z",
    "basis": "User requested all 63 language editions and instructed completed PRs to be merged; AI translation and independent AI review were performed, with no claim of human text review."
  }
}
---

**Rust は、コンパイル時に所有権と型のチェックを通じてメモリ使用規則をチェックします。** Java や Kotlin のようにオブジェクトの到達可能性を追跡するガベージ コレクターの代わりに、コードは、値の所有者とその値がどのくらいの期間借用されているかを表現します。これにより、コンパイラ エラーを単なる構文制限ではなく、データ使用規約として読み取ることができます。

この入門記事は、他の言語で関数を書いたことがある開発者向けです。例は **Rust 1.100.0、edition 2024、macOS arm64** で実行しました。edition はコンパイラのバージョンとは独立して構文と互換性のルールを選びます。例は標準ライブラリのみを使い、外部ネットワークにアクセスしません。

## Rust はどのような問題に役立つでしょうか?

Rust はネイティブ コードにコンパイルされ、デフォルトのメモリ管理にトレース GC を必要としません。 CLI、システム コンポーネント、および重要なメモリやレイテンシー バジェットを持つプログラムについては、検討する価値があります。その [公式紹介](https://rust-lang.org/) には、パフォーマンスとメモリの安全性も目標として挙げられています。 GC がないことだけでは、Rust が Java より高速であることや、レイテンシーが低いことを証明するものではありません。この記事は比較パフォーマンスを測定するものではありません。

| 基準 | JVM 上の Java/Kotlin | Rust |
| --- | --- | --- |
| 一般的なオブジェクト メモリ管理 | GC は再利用するオブジェクトを追跡します | 所有権と `Drop` を通じてリソースがクリーンアップされました |
| データの受け渡し | 複数の場所にオブジェクト参照を保持できる | 値は型に応じて移動またはコピーされ、参照によって借用できます。 |
| 失敗の伝達 | 例外、結果の型、およびその他のメカニズム | API は通常、成功または失敗を `Result<T, E>` で表します。 |
| 確認すべき導入コスト | 既存の JVM ライブラリとチームの経験 | 所有権の学習コストと、ライブラリ・ビルド・運用ツールの適合性 |

既存サービスのボトルネックがデータベース待機や外部 API にある場合は、言語を変更する前にそれらのパスを測定してください。最初の導入では、明確な境界を持つ小規模な CLI から始めて、開発と展開のコストを検討します。

## 所有権と借用はどう違うのでしょうか？

まず、オペレーティング システムの [公式手順](https://rust-lang.org/tools/install/) を使用して `rustup` と Rust をインストールし、次に以下の例を実行します。 macOS では、ネイティブ リンクに必要なコマンド ライン ツールもインストールします。

`String` はその文字列データを所有します。以下を `move_error.rs` として保存します。 **意図的にコンパイルに失敗します**。

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

`let moved = name` は所有権を譲渡するため、後で `name` を出力しようとすると、**E0382: 移動された値の借用** が生成されます。すべての代入で値が移動されるわけではありません。`u64` など、`Copy` を実装する型は代入時にコピーされます。 `String::clone()` は個別の文字列データを複製するため、必要に応じて使用します。ルールは[公式所有権解説](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html)をご覧ください。

値を読み取るだけの場合は、所有権を譲渡する代わりに、`&` を使用して値を借用できます。次のコードを別の `borrow_ok.rs` ファイルに保存します。

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

実際の出力は次のとおりです。

```text
Rust
Rust language
```

最初の `println!` の後、`borrowed` は再度使用されないため、共有借用は終了します。これにより、後で同じブロック内で `name` を変更できるようになります。 `push_str` の後に再度 `borrowed` を出力すると、参照に必要な存続期間が変更に必要な排他的借用と重複し、コンパイルは失敗します。

有用な開始ルールは、同じデータに対する **複数の共有参照 `&T` または 一 つの排他的参照 `&mut T`** です。これは、`&T` がすべての内部可変性を禁止するという意味ではありません。詳しい条件は[公式借用書](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html)に記載されています。ライフタイムは、参照が有効でなければならない期間間の関係を表します。メモリそのものの生存期間を延ばすものではありません。

## Cargo を使用して金額合計 CLI を構築する

プログラムは、整数値のカウントと合計を出力します。これは説明的なプログラムであり、特定のサービスの支払い実装ではなく、すべての入力が同じ単位を使用することを前提としています。小数や負の値は受け入れられません。それぞれの金額と合計が `u64` に収まる必要があります。

これらのコマンドは、macOS または Linux シェルを使用します。 Rust ツールがインストールされた環境で演習バージョンを準備します。

```bash
rustup toolchain install 1.100.0 --profile minimal --component rustfmt --component clippy
cargo +1.100.0 new expense-summary --bin --edition 2024
cd expense-summary
```

以下の三つのファイルを設定します。 `rust-toolchain.toml` はこのフォルダーのツールのバージョンを固定し、`Cargo.toml` にはパッケージ構成が含まれます。 [公式 Cargo 入門](https://doc.rust-lang.org/book/ch01-03-hello-cargo.html) では、Cargo のビルド コマンドとチェック コマンドについても説明しています。

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

![main は入力文字列を所有し、それを要約に貸し出します。空の入力を拒否し、各値を u64 として解析し、checked_add で蓄積します。失敗するとすぐに Err が返されます。それ以外の場合は、カウントと合計を返します。 main は成功と失敗を異なる出力ストリームと終了コードに送信します。](/assets/diagrams/technical/ja-2026-11-13-rust-ownership-guide.svg)

この図は、`summarize` のループと早期リターンを示しています。左側の次の値のチェックに戻る行は、累積が成功した後のループです。右側のすべてのエラー パスは、`main` の `Err` ブランチで合流します。

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

`inputs` は、`main` が所有する `Vec<String>` です。 `summarize(&inputs)` は、入力全体を複製したり所有権を譲渡したりせずに、その文字列をスライス `&[String]` として借用します。 `for input in inputs` も参照によって文字列を読み取ります。借用により、ここでの入力文字列のコピーが回避されますが、コマンドライン引数の収集中に割り当てが排除されるわけではありません。

`Summary` は、成功した結果を保持する構造体です。 `InputError` は、起こり得る失敗の列挙です。 `Result<Summary, InputError>` は、それらの結果の 一 つが返されるというコントラクトです。 `?` は `Err` の場合に現在の関数から早期リターンし、成功時には内部値を取り出します。例外をスローしたり、プログラムをすぐに終了したりすることはありません。 [公式の結果の説明](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html) では、エラーの伝播について説明しています。

`parse::<u64>()` は、各数値の形式と範囲をチェックします。 二 つの値の合計が範囲を超える場合、`checked_add` は `None` を返し、`ok_or` は `TotalOverflow` エラーに変換します。したがって、個別に有効な入力が合計をオーバーフローする可能性があります。 `main` は `match` を使用して両方の結果を処理し、`{:?}` は `Debug` 形式を使用してエラー名を出力します。

## 実行すると何が確認できるのでしょうか？

```bash
rustc --version
cargo check --offline
cargo fmt --check
cargo clippy --offline -- -D warnings
cargo run --offline --quiet -- 12000 8000 0
```

その実行からの標準出力は次のとおりです。 `--` 以降の値は、Cargo ではなくサンプル プログラムに渡されます。

```text
count=3, total=20000
```

これらは、実際の CLI 実行で観察された代表的な結果です。エラーの場合、部分合計は出力されません。エラーは標準エラーに送られ、コード 1 で終了します。

| `cargo run --offline --quiet --` の後の引数 | 出力 | 終了コード |
| --- | --- | --- |
| `12000 8000 0` | 標準出力 `count=3, total=20000` | 0 |
| `0` | 標準出力 `count=1, total=0` | 0 |
| 引数なし | 標準エラー `error: EmptyInput` | 1 |
| `12000 abc` | 標準エラー `error: InvalidAmount` | 1 |
| `-1` または `1.5` | 標準エラー `error: InvalidAmount` | 1 |
| `18446744073709551616` | 標準エラー `error: InvalidAmount` | 1 |
| `18446744073709551615 0` | 標準出力 `count=2, total=18446744073709551615` | 0 |
| `18446744073709551615 1` | 標準エラー `error: TotalOverflow` | 1 |

`cargo check` は、コードを実行せずに型と関連プロパティをチェックします。 `cargo fmt --check` はフォーマットをチェックし、Clippy は静的診断を提供します。成功した場合でも、別途プログラムを実行して計算ルールを確認してください。ここでは、出力、エラー、終了コードがデバッグ実行とリリース実行で比較されました。スループットと生産負荷は測定されませんでした。

## Rust は何を保証しますか?

安全な Rust のタイプと所有権のチェックは、無効な参照の使用やデータ競合の防止に役立ちます。スレッド間で値を移動できるかどうか、および参照を共有できるかどうかは、[`Send` および `Sync`](https://doc.rust-lang.org/book/ch16-04-extensible-concurrency-sync-and-send.html) などの型コントラクトにも関係します。これによって、すべての競合状態、デッドロック、メモリ リーク、ビジネス ロジック エラーが排除されるわけではありません。

[`unsafe`](https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html) は、作成者に特定の操作の安全条件に対する責任を課します。これは借用チェッカー全体をオフにするスイッチではありません。間違った `unsafe` 実装または FFI 境界は安全性に影響を与える可能性があります。サーバー、非同期実行、および共有状態の設計は、この CLI の検証範囲内ではありませんでした。

次の演習では、ファイルから入力金額を読み取るようにプログラムを拡張します。ファイル I/O エラーが既存の `InputError` とどのように異なるかを判断して、所有権とエラーの種類がプログラムの境界をどのように表現するかをより具体的に確認します。
