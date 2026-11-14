---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2026-11-13-rust-ownership-guide",
  "routeSlug": "2026-11-13-rust-ownership-guide",
  "kind": "post",
  "title": "Rust-Einstieg: Ownership, Borrowing und Result an ausführbaren Beispielen",
  "description": "Verstehen Sie Rust-Ownership und Borrowing im Vergleich zu Java-Referenzen. Erstellen Sie eine CLI mit Cargo und prüfen Sie Result, Überlauf und Compilerfehler.",
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
  "draftSha256": "b4b946bc8f056ef46b046af1cd4ab17bfa712690e2b423c1a3ba7cb9ed84adb3",
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

**Rust prüft Regeln zur Speichernutzung bereits beim Kompilieren durch Ownership und Typprüfung.** Anders als bei Java und Kotlin, wo ein Garbage Collector die Erreichbarkeit von Objekten verfolgt, beschreibt der Code, wem ein Wert gehört und wie lange er ausgeliehen wird. So lassen sich Compilerfehler als Verträge über die Datennutzung verstehen und nicht nur als Syntaxvorschriften.

Diese Einführung richtet sich an Entwicklerinnen und Entwickler, die bereits Funktionen in einer anderen Sprache geschrieben haben. Die Beispiele wurden mit **Rust 1.100.0, Edition 2024, unter macOS arm64** ausgeführt. Die Edition legt Syntax- und Kompatibilitätsregeln unabhängig von der Compiler-Version fest. Die Beispiele verwenden nur die Standardbibliothek und bauen keine externen Netzwerkverbindungen auf.

## Bei welchen Problemen hilft Rust?

Rust kompiliert zu nativem Code und benötigt für die standardmäßige Speicherverwaltung keinen nachverfolgenden GC. Die Sprache ist eine prüfenswerte Wahl für CLIs, Systemkomponenten und Programme mit wichtigen Speicher- oder Latenzbudgets. Auch die [offizielle Einführung](https://rust-lang.org/) nennt Leistung und Speichersicherheit als Ziele. Das Fehlen eines GC allein beweist jedoch nicht, dass Rust schneller ist oder geringere Latenz als Java hat. Dieser Artikel misst keine vergleichende Leistung.

| Kriterium | Java/Kotlin auf der JVM | Rust |
| --- | --- | --- |
| Übliche Objekt-Speicherverwaltung | GC verfolgt freizugebende Objekte | Ressourcenbereinigung über Ownership und `Drop` |
| Datenübergabe | Mehrere Stellen können Objektreferenzen halten | Werte werden je nach Typ verschoben oder kopiert und bei Bedarf per Referenz ausgeliehen |
| Fehlerweitergabe | Ausnahmen, Ergebnistypen und andere Mittel | APIs drücken Erfolg oder Fehler häufig mit `Result<T, E>` aus |
| Kosten bei der Einführung | Vorhandene JVM-Bibliotheken und Teamerfahrung | Ownership lernen; Eignung von Bibliotheken, Build- und Betriebswerkzeugen prüfen |

Liegt der Engpass eines bestehenden Dienstes bei Datenbankwartezeiten oder externen APIs, sollten diese Pfade vor einem Sprachwechsel gemessen werden. Für die erste Einführung eignet sich eine kleine CLI mit klaren Grenzen, um Entwicklungs- und Bereitstellungskosten zu prüfen.

## Worin unterscheiden sich Ownership und Borrowing?

Installieren Sie zunächst `rustup` und Rust nach der [offiziellen Anleitung](https://rust-lang.org/tools/install/) für Ihr Betriebssystem und führen Sie dann die Beispiele aus. Installieren Sie unter macOS auch die Command Line Tools für das native Linken.

Ein `String` besitzt seine Zeichenkettendaten. Speichern Sie den folgenden Code als `move_error.rs`; er **lässt sich absichtlich nicht kompilieren**.

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

Da `let moved = name` die Ownership überträgt, führt der spätere Versuch, `name` auszugeben, zu **E0382: borrow of moved value**. Nicht jede Zuweisung verschiebt einen Wert: Typen wie `u64`, die `Copy` implementieren, werden bei der Zuweisung kopiert. `String::clone()` kopiert separate Zeichenkettendaten und sollte bei Bedarf verwendet werden. Die Regeln stehen in der [offiziellen Erklärung zu Ownership](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html).

Wenn ein Wert nur gelesen wird, kann er mit `&` ausgeliehen werden, statt die Ownership zu übertragen. Speichern Sie den nächsten Code in einer separaten Datei `borrow_ok.rs`.

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

Die tatsächliche Ausgabe lautet:

```text
Rust
Rust language
```

Nach dem ersten `println!` wird `borrowed` nicht mehr verwendet; damit endet das gemeinsame Borrowing. Deshalb kann `name` später im selben Block geändert werden. Wird `borrowed` nach `push_str` erneut ausgegeben, überschneidet sich die benötigte Lebensdauer der Referenz mit dem exklusiven Borrowing für die Änderung, und das Kompilieren schlägt fehl.

Eine hilfreiche Ausgangsregel lautet: **mehrere gemeinsame Referenzen `&T` oder eine exklusive Referenz `&mut T`** auf dieselben Daten. Das bedeutet nicht, dass `&T` jede innere Veränderlichkeit verbietet. Die [offizielle Borrowing-Dokumentation](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html) beschreibt die genauen Bedingungen. Eine Lifetime beschreibt Beziehungen zwischen Zeiträumen, in denen Referenzen gültig sein müssen; sie hält Speicher nicht länger am Leben.

## Eine CLI zur Summierung von Beträgen mit Cargo bauen

Das Programm gibt Anzahl und Summe ganzzahliger Beträge aus. Es dient zur Erklärung, implementiert keine Zahlung eines bestimmten Dienstes und setzt voraus, dass alle Eingaben dieselbe Einheit verwenden. Dezimalzahlen und negative Werte werden nicht akzeptiert; jeder Betrag und die Summe müssen in `u64` passen.

Die Befehle verwenden eine macOS- oder Linux-Shell. Bereiten Sie die Übungsversion in einer Umgebung mit installierten Rust-Werkzeugen vor.

```bash
rustup toolchain install 1.100.0 --profile minimal --component rustfmt --component clippy
cargo +1.100.0 new expense-summary --bin --edition 2024
cd expense-summary
```

Legen Sie die folgenden drei Dateien an. `rust-toolchain.toml` fixiert die Werkzeugversion für diesen Ordner; `Cargo.toml` enthält die Paketkonfiguration. Build- und Prüfbefehle stehen auch in der [offiziellen Cargo-Einführung](https://doc.rust-lang.org/book/ch01-03-hello-cargo.html).

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

![main besitzt die Eingabezeichenketten und leiht sie an summarize aus. Leere Eingabe wird abgelehnt; jeder Wert wird als u64 geparst und mit checked_add addiert. Bei einem Fehler wird sofort Err zurückgegeben, sonst Anzahl und Summe. main gibt Erfolg und Fehler über verschiedene Ausgabeströme und Exit-Codes aus.](/assets/diagrams/technical/de-2026-11-13-rust-ownership-guide.svg)

Das Diagramm zeigt die Schleife und die vorzeitigen Rückgaben in `summarize`. Die Linie links zurück zur Prüfung des nächsten Werts stellt die Wiederholung nach erfolgreicher Addition dar; rechts laufen alle Fehlerpfade im `Err`-Zweig von `main` zusammen.

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

`inputs` ist ein `Vec<String>` im Besitz von `main`. `summarize(&inputs)` leiht dessen Zeichenketten als Slice `&[String]` aus, ohne alle Eingaben zu klonen oder die Ownership zu übertragen. Auch `for input in inputs` liest die Zeichenketten per Referenz. Das Borrowing vermeidet hier Kopien der Eingabezeichenketten, beseitigt aber keine Allokationen beim Sammeln der Befehlszeilenargumente.

`Summary` bündelt ein erfolgreiches Ergebnis als Struct; `InputError` ist ein Enum der möglichen Fehler. `Result<Summary, InputError>` ist der Vertrag, eines dieser Ergebnisse zurückzugeben. `?` kehrt bei `Err` frühzeitig aus der aktuellen Funktion zurück und entnimmt bei Erfolg den inneren Wert. Es löst weder eine Ausnahme aus noch beendet es das Programm sofort. Die [offizielle Result-Erklärung](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html) beschreibt die Fehlerweitergabe.

`parse::<u64>()` prüft Format und Wertebereich jeder Zahl. Überschreitet die Summe zweier Werte den Bereich, gibt `checked_add` `None` zurück; `ok_or` wandelt dies in den Fehler `TotalOverflow` um. Somit kann die Summe auch bei einzeln gültigen Eingaben fehlschlagen. `main` behandelt beide Ergebnisse mit `match`; `{:?}` gibt den Fehlernamen im `Debug`-Format aus.

## Was lässt sich bei der Ausführung prüfen?

```bash
rustc --version
cargo check --offline
cargo fmt --check
cargo clippy --offline -- -D warnings
cargo run --offline --quiet -- 12000 8000 0
```

Die Standardausgabe dieses Laufs folgt. Werte nach `--` werden an das Beispielprogramm und nicht an Cargo übergeben.

```text
count=3, total=20000
```

Dies sind repräsentative Ergebnisse tatsächlicher CLI-Läufe. Im Fehlerfall wird keine Teilsumme ausgegeben; Fehler gehen an die Standardfehlerausgabe und enden mit Code 1.

| Argumente nach `cargo run --offline --quiet --` | Ausgabe | Exit-Code |
| --- | --- | --- |
| `12000 8000 0` | stdout `count=3, total=20000` | 0 |
| `0` | stdout `count=1, total=0` | 0 |
| Keine Argumente | stderr `error: EmptyInput` | 1 |
| `12000 abc` | stderr `error: InvalidAmount` | 1 |
| `-1` oder `1.5` | stderr `error: InvalidAmount` | 1 |
| `18446744073709551616` | stderr `error: InvalidAmount` | 1 |
| `18446744073709551615 0` | stdout `count=2, total=18446744073709551615` | 0 |
| `18446744073709551615 1` | stderr `error: TotalOverflow` | 1 |

`cargo check` prüft unter anderem Typen, ohne den Code auszuführen. `cargo fmt --check` prüft das Format; Clippy liefert statische Diagnosen. Auch wenn diese Prüfungen erfolgreich sind, müssen die Berechnungsregeln durch eine separate Ausführung geprüft werden. Hier wurden Ausgabe, Fehler und Exit-Codes in Debug- und Release-Läufen verglichen; Durchsatz und Produktionslast wurden nicht gemessen.

## Was garantiert Rust?

Die Typ- und Ownership-Prüfungen von Safe Rust helfen, ungültige Referenznutzung und Datenrennen zu verhindern. Ob Werte zwischen Threads verschoben und Referenzen geteilt werden können, hängt auch mit Typverträgen wie [`Send` und `Sync`](https://doc.rust-lang.org/book/ch16-04-extensible-concurrency-sync-and-send.html) zusammen. Dadurch verschwinden jedoch nicht alle Race Conditions, Deadlocks, Speicherlecks oder Fehler in der Geschäftslogik.

Bei [`unsafe`](https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html) trägt die Autorin oder der Autor die Verantwortung für Sicherheitsbedingungen bestimmter Operationen. Es schaltet nicht den gesamten Borrow Checker aus; fehlerhaftes `unsafe` oder FFI-Grenzen können die Sicherheit beeinflussen. Server, asynchrone Ausführung und Entwürfe mit gemeinsam genutztem Zustand wurden bei dieser CLI nicht geprüft.

Erweitern Sie als nächste Übung das Programm so, dass Beträge aus einer Datei gelesen werden. Entscheiden Sie, wie sich Datei-I/O-Fehler vom vorhandenen `InputError` unterscheiden; so wird konkreter sichtbar, wie Ownership und Fehlertypen Programmgrenzen ausdrücken.
