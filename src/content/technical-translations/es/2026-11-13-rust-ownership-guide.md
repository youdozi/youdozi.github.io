---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2026-11-13-rust-ownership-guide",
  "routeSlug": "2026-11-13-rust-ownership-guide",
  "kind": "post",
  "title": "Rust: propiedad, préstamos y un primer programa CLI",
  "description": "Aprende cómo Rust aplica las reglas de propiedad y préstamos con un ejemplo de línea de comandos que valida importes, detecta errores y suma valores.",
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
  "draftSha256": "0c4676d51956de7d7b07c5f67c0064881ef1050da81dc8c1eec191e9410c96ba",
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

**Rust comprueba en tiempo de compilación las reglas de uso de memoria mediante la propiedad y la comprobación de tipos.** En lugar de que un recolector de basura siga la alcanzabilidad de los objetos como en Java y Kotlin, el código expresa quién posee un valor y durante cuánto tiempo se presta. Así, los errores del compilador pueden leerse como contratos de uso de datos y no como simples restricciones sintácticas.

Esta introducción está dirigida a desarrolladores que ya han escrito funciones en otro lenguaje. Los ejemplos se ejecutaron con **Rust 1.100.0, edición 2024, en macOS arm64**. La edición selecciona las reglas de sintaxis y compatibilidad independientemente de la versión del compilador. Los ejemplos solo usan la biblioteca estándar y no realizan comunicaciones externas.

## ¿Para qué problemas puede servir Rust?

Rust se compila a código nativo y su gestión de memoria predeterminada no requiere un recolector de basura de rastreo. Es una opción que conviene estudiar para herramientas CLI, componentes de sistema y programas con presupuestos exigentes de memoria o latencia. Su [introducción oficial](https://rust-lang.org/) también presenta el rendimiento y la seguridad de memoria como objetivos. La ausencia de GC por sí sola no demuestra que Rust sea más rápido ni tenga menor latencia que Java. Este artículo no mide el rendimiento comparativo.

| Criterio | Java/Kotlin en la JVM | Rust |
| --- | --- | --- |
| Gestión habitual de memoria de objetos | El GC rastrea los objetos que puede recuperar | Los recursos se liberan mediante la propiedad y `Drop` |
| Transferencia de datos | Varias partes pueden conservar referencias a objetos | Los valores se mueven o copian según su tipo y pueden prestarse por referencia |
| Comunicación de errores | Excepciones, tipos de resultado y otros mecanismos | Las API suelen expresar éxito o error con `Result<T, E>` |
| Costes de adopción que revisar | Bibliotecas JVM y experiencia del equipo existentes | Aprendizaje de propiedad y adecuación de bibliotecas y herramientas de compilación y operación |

Si el cuello de botella de un servicio existente es la espera de base de datos o de una API externa, mide primero esas rutas antes de cambiar de lenguaje. Para una primera adopción, empieza por una CLI pequeña con límites claros y evalúa los costes de desarrollo y despliegue.

## ¿En qué se diferencian la propiedad y los préstamos?

Primero instala `rustup` y Rust siguiendo las [instrucciones oficiales](https://rust-lang.org/tools/install/) para tu sistema operativo y luego ejecuta los ejemplos. En macOS instala también las Command Line Tools necesarias para el enlace nativo.

Un `String` posee los datos de su cadena. Guarda el siguiente código como `move_error.rs`: **fallará intencionadamente al compilar**.

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

Como `let moved = name` transfiere la propiedad, el intento posterior de imprimir `name` produce **E0382: borrow of moved value**. No toda asignación mueve un valor: los tipos que implementan `Copy`, como `u64`, se copian al asignarse. `String::clone()` duplica los datos de la cadena, así que úsalo solo cuando sea necesario. Consulta la [explicación oficial de propiedad](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html) para conocer las reglas.

Si solo necesitas leer un valor, puedes tomarlo prestado con `&` en vez de transferir su propiedad. Guarda el siguiente código en un archivo independiente `borrow_ok.rs`.

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

La salida real es:

```text
Rust
Rust language
```

Después del primer `println!`, `borrowed` no vuelve a usarse, por lo que termina el préstamo compartido. Esto permite modificar `name` después dentro del mismo bloque. Si vuelves a imprimir `borrowed` después de `push_str`, el periodo necesario de esa referencia se solapa con el préstamo exclusivo para modificar y la compilación falla.

Una regla útil para empezar es **varias referencias compartidas `&T` o una referencia exclusiva `&mut T`** a los mismos datos. Esto no significa que `&T` prohíba toda mutabilidad interior. La [documentación oficial de préstamos](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html) detalla las condiciones. Un lifetime expresa relaciones entre los periodos durante los que las referencias deben ser válidas; no mantiene viva la memoria durante más tiempo.

## Crear una CLI que suma importes con Cargo

El programa imprime la cantidad y la suma de importes enteros. Es un ejemplo explicativo, no una implementación de pagos de un servicio concreto, y supone que todos los importes usan la misma unidad. No acepta decimales ni negativos; cada importe y el total deben caber en `u64`.

Estos comandos utilizan un shell de macOS o Linux. Prepara la versión del ejercicio en un entorno con las herramientas de Rust instaladas.

```bash
rustup toolchain install 1.100.0 --profile minimal --component rustfmt --component clippy
cargo +1.100.0 new expense-summary --bin --edition 2024
cd expense-summary
```

Prepara los tres archivos siguientes. `rust-toolchain.toml` fija la versión de las herramientas para esta carpeta y `Cargo.toml` contiene la configuración del paquete. La [introducción oficial a Cargo](https://doc.rust-lang.org/book/ch01-03-hello-cargo.html) también explica sus comandos de compilación y comprobación.

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

![main posee las cadenas de entrada y las presta a summarize. Rechaza entradas vacías, analiza cada valor como u64 y lo acumula con checked_add. Si falla, devuelve Err de inmediato; si todos los valores son correctos, devuelve cantidad y suma. main envía éxito y error a distintos flujos de salida y códigos de salida.](/assets/diagrams/technical/es-2026-11-13-rust-ownership-guide.svg)

El diagrama muestra el bucle y las devoluciones anticipadas de `summarize`. La línea que vuelve a comprobar el siguiente valor por la izquierda representa la repetición tras acumular correctamente; todas las rutas de error de la derecha confluyen en la rama `Err` de `main`.

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

`inputs` es un `Vec<String>` del que `main` es propietario. `summarize(&inputs)` toma prestadas sus cadenas como una porción `&[String]`, sin clonar todos los datos ni transferir su propiedad. `for input in inputs` también lee las cadenas por referencia. El préstamo evita copiar las cadenas de entrada en este ejemplo, pero no elimina las asignaciones al recopilar los argumentos de línea de comandos.

`Summary` es una estructura que agrupa el resultado correcto e `InputError` es una enumeración de posibles errores. `Result<Summary, InputError>` es el contrato que devuelve uno de esos dos resultados. `?` devuelve anticipadamente desde la función actual al encontrar `Err` y extrae el valor interno en caso de éxito. No lanza una excepción ni termina el programa de inmediato. La [explicación oficial de Result](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html) describe la propagación de errores.

`parse::<u64>()` comprueba el formato y rango de cada número. Si la suma de dos valores supera el rango, `checked_add` devuelve `None` y `ok_or` lo convierte en el error `TotalOverflow`. Así, aunque cada entrada sea válida, la suma puede fallar. `main` usa `match` para gestionar ambos resultados y `{:?}` imprime el nombre del error con el formato `Debug`.

## ¿Qué puedes comprobar al ejecutarlo?

```bash
rustc --version
cargo check --offline
cargo fmt --check
cargo clippy --offline -- -D warnings
cargo run --offline --quiet -- 12000 8000 0
```

La salida estándar de esa ejecución aparece a continuación. Los valores después de `--` se pasan al programa del ejemplo, no a Cargo.

```text
count=3, total=20000
```

Estos son resultados representativos observados en ejecuciones reales de la CLI. Si hay un error no se imprime una suma parcial; los errores se envían a la salida de error estándar y terminan con el código 1.

| Argumentos después de `cargo run --offline --quiet --` | Salida | Código de salida |
| --- | --- | --- |
| `12000 8000 0` | salida estándar `count=3, total=20000` | 0 |
| `0` | salida estándar `count=1, total=0` | 0 |
| Sin argumentos | error estándar `error: EmptyInput` | 1 |
| `12000 abc` | error estándar `error: InvalidAmount` | 1 |
| `-1` o `1.5` | error estándar `error: InvalidAmount` | 1 |
| `18446744073709551616` | error estándar `error: InvalidAmount` | 1 |
| `18446744073709551615 0` | salida estándar `count=2, total=18446744073709551615` | 0 |
| `18446744073709551615 1` | error estándar `error: TotalOverflow` | 1 |

`cargo check` comprueba los tipos y otras propiedades sin ejecutar el código. `cargo fmt --check` revisa el formato y Clippy ofrece diagnósticos estáticos. Aunque estos comandos tengan éxito, ejecuta el programa por separado para comprobar las reglas de cálculo. Aquí se compararon la salida, los errores y los códigos de salida en ejecuciones debug y release; no se midieron el rendimiento ni la carga de producción.

## ¿Qué garantiza Rust?

Las comprobaciones de tipos y propiedad de Safe Rust ayudan a prevenir el uso incorrecto de referencias y las carreras de datos. La posibilidad de mover valores entre hilos y compartir referencias también depende de contratos de tipo como [`Send` y `Sync`](https://doc.rust-lang.org/book/ch16-04-extensible-concurrency-sync-and-send.html). Esto no elimina todas las condiciones de carrera, bloqueos mutuos, fugas de memoria ni errores de lógica de negocio.

[`unsafe`](https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html) hace que quien escribe el código sea responsable de las condiciones de seguridad de ciertas operaciones. No es un interruptor que desactive todo el comprobador de préstamos; una implementación incorrecta de `unsafe` o los límites de FFI pueden afectar a la seguridad. El diseño de servidores, ejecución asíncrona y estado compartido no se incluyó en la validación de esta CLI.

Como siguiente ejercicio, amplía el programa para leer los importes de un archivo. Decide cómo distinguir los errores de E/S del archivo del `InputError` existente para entender con más detalle cómo la propiedad y los tipos de error expresan los límites del programa.
