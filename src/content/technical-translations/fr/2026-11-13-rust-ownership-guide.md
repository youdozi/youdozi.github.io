---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2026-11-13-rust-ownership-guide",
  "routeSlug": "2026-11-13-rust-ownership-guide",
  "kind": "post",
  "title": "Débuter avec Rust : propriété, emprunt et Result par des exemples exécutables",
  "description": "Comprendre la propriété et les emprunts Rust face aux références Java. Créer une CLI avec Cargo et vérifier Result, débordement entier et erreurs de compilation.",
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
  "draftSha256": "5559f7084e1a741b0f081e53eae2f5823e4fd9e808d2c34ccda673a6b988f154",
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

**Rust vérifie dès la compilation les règles d’utilisation de la mémoire grâce à la propriété et au contrôle des types.** Contrairement à Java et Kotlin, où un ramasse-miettes suit l’accessibilité des objets, le code exprime qui possède une valeur et combien de temps elle est empruntée. Les erreurs du compilateur peuvent ainsi se lire comme des contrats d’utilisation des données, et non comme de simples contraintes syntaxiques.

Cette introduction s’adresse aux personnes ayant déjà écrit des fonctions dans un autre langage. Les exemples ont été exécutés avec **Rust 1.100.0, édition 2024, sur macOS arm64**. Une édition choisit des règles de syntaxe et de compatibilité indépendamment de la version du compilateur. Les exemples utilisent uniquement la bibliothèque standard et n’effectuent aucune communication réseau externe.

## À quels problèmes Rust peut-il répondre ?

Rust compile en code natif et n’exige pas de ramasse-miettes par traçage pour sa gestion mémoire par défaut. C’est une option à examiner pour les CLI, les composants système et les programmes soumis à des budgets de mémoire ou de latence. L’[introduction officielle](https://rust-lang.org/) présente aussi la performance et la sûreté mémoire comme objectifs. L’absence de GC ne prouve toutefois pas à elle seule que Rust soit plus rapide ou moins latent que Java. Cet article ne mesure aucune comparaison de performances.

| Critère | Java/Kotlin sur la JVM | Rust |
| --- | --- | --- |
| Gestion habituelle de la mémoire des objets | Le GC suit les objets à libérer | Libération des ressources par propriété et `Drop` |
| Transmission des données | Plusieurs endroits peuvent détenir des références d’objet | Les valeurs sont déplacées ou copiées selon leur type et peuvent être empruntées par référence |
| Transmission des erreurs | Exceptions, types résultat et autres moyens | Les API expriment souvent succès ou erreur avec `Result<T, E>` |
| Coûts d’adoption à examiner | Bibliothèques JVM existantes et expérience de l’équipe | Apprentissage de la propriété et adéquation des bibliothèques, du build et des outils d’exploitation |

Si le goulot d’un service existant est l’attente de la base de données ou d’API externes, il faut mesurer ces chemins avant de changer de langage. Pour commencer, une petite CLI aux limites claires permet d’examiner les coûts de développement et de déploiement.

## Quelle différence entre propriété et emprunt ?

Installez d’abord `rustup` et Rust en suivant les [instructions officielles](https://rust-lang.org/tools/install/) de votre système, puis exécutez les exemples. Sur macOS, installez aussi les Command Line Tools nécessaires à l’édition de liens native.

Un `String` possède ses données textuelles. Enregistrez le code suivant sous `move_error.rs` ; il **échoue volontairement à la compilation**.

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

Comme `let moved = name` transfère la propriété, la tentative ultérieure d’afficher `name` produit **E0382: borrow of moved value**. Toute affectation ne déplace pas la valeur : les types implémentant `Copy`, comme `u64`, sont copiés à l’affectation. `String::clone()` duplique séparément les données de la chaîne ; utilisez-le si nécessaire. Les règles sont détaillées dans la [documentation officielle sur la propriété](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html).

Pour seulement lire une valeur, on peut l’emprunter avec `&` au lieu d’en transférer la propriété. Enregistrez le code suivant dans un fichier séparé `borrow_ok.rs`.

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

La sortie réelle est la suivante :

```text
Rust
Rust language
```

Après le premier `println!`, `borrowed` n’est plus utilisé et l’emprunt partagé prend fin. Il est donc possible de modifier `name` plus loin dans le même bloc. Si l’on affiche à nouveau `borrowed` après `push_str`, la durée nécessaire à cette référence chevauche l’emprunt exclusif requis pour la modification et la compilation échoue.

Une règle de départ utile est **plusieurs références partagées `&T` ou une référence exclusive `&mut T`** aux mêmes données. Cela ne signifie pas que `&T` interdise toute mutabilité intérieure. Les conditions détaillées figurent dans la [documentation officielle sur les emprunts](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html). Une lifetime exprime les relations entre les périodes pendant lesquelles les références doivent être valides ; elle ne prolonge pas la durée de vie de la mémoire.

## Créer avec Cargo une CLI qui additionne des montants

Le programme affiche le nombre et la somme de montants entiers. Il sert d’explication, ne met pas en œuvre le paiement d’un service particulier et suppose que toutes les entrées utilisent la même unité. Les décimaux et les valeurs négatives sont refusés ; chaque montant et le total doivent tenir dans `u64`.

Les commandes ci-dessous utilisent un shell macOS ou Linux. Préparez la version de l’exercice dans un environnement où les outils Rust sont installés.

```bash
rustup toolchain install 1.100.0 --profile minimal --component rustfmt --component clippy
cargo +1.100.0 new expense-summary --bin --edition 2024
cd expense-summary
```

Créez les trois fichiers suivants. `rust-toolchain.toml` fixe la version des outils pour ce dossier ; `Cargo.toml` contient la configuration du paquet. L’[introduction officielle à Cargo](https://doc.rust-lang.org/book/ch01-03-hello-cargo.html) présente aussi les commandes de build et de vérification.

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

![main possède les chaînes d’entrée et les prête à summarize. L’entrée vide est refusée ; chaque valeur est analysée comme u64 puis ajoutée avec checked_add. En cas d’échec, Err est renvoyé immédiatement ; sinon le nombre et la somme sont renvoyés. main transmet succès et erreur à des flux et codes de sortie distincts.](/assets/diagrams/technical/fr-2026-11-13-rust-ownership-guide.svg)

Le schéma montre la boucle et les retours anticipés de `summarize`. À gauche, la ligne revenant à la vérification de la valeur suivante représente la répétition après une addition réussie ; à droite, tous les chemins d’erreur rejoignent la branche `Err` de `main`.

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

`inputs` est un `Vec<String>` possédé par `main`. `summarize(&inputs)` emprunte ses chaînes sous forme de slice `&[String]`, sans cloner toutes les entrées ni transférer leur propriété. `for input in inputs` lit également les chaînes par référence. Ici l’emprunt évite de copier les chaînes d’entrée, mais ne supprime pas les allocations effectuées lors de la collecte des arguments de ligne de commande.

`Summary` est une structure qui regroupe un résultat réussi ; `InputError` est une énumération des erreurs possibles. `Result<Summary, InputError>` est le contrat qui renvoie l’un de ces résultats. `?` retourne immédiatement de la fonction courante en cas d’`Err` et extrait la valeur interne en cas de succès. Il ne lance pas d’exception et ne termine pas immédiatement le programme. La [documentation officielle sur Result](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html) décrit la propagation des erreurs.

`parse::<u64>()` vérifie le format et l’intervalle de chaque nombre. Si la somme de deux valeurs dépasse l’intervalle, `checked_add` renvoie `None`, que `ok_or` transforme en erreur `TotalOverflow`. Le total peut donc échouer même si chaque entrée est valide. `main` traite les deux résultats avec `match` et `{:?}` affiche le nom de l’erreur au format `Debug`.

## Que vérifier à l’exécution ?

```bash
rustc --version
cargo check --offline
cargo fmt --check
cargo clippy --offline -- -D warnings
cargo run --offline --quiet -- 12000 8000 0
```

Voici la sortie standard de cette exécution. Les valeurs après `--` sont transmises au programme d’exemple et non à Cargo.

```text
count=3, total=20000
```

Voici des résultats représentatifs observés lors d’exécutions réelles de la CLI. En cas d’erreur, aucune somme partielle n’est affichée ; les erreurs sont transmises à la sortie d’erreur standard et le code de sortie est 1.

| Arguments après `cargo run --offline --quiet --` | Sortie | Code de sortie |
| --- | --- | --- |
| `12000 8000 0` | stdout `count=3, total=20000` | 0 |
| `0` | stdout `count=1, total=0` | 0 |
| Aucun argument | stderr `error: EmptyInput` | 1 |
| `12000 abc` | stderr `error: InvalidAmount` | 1 |
| `-1` ou `1.5` | stderr `error: InvalidAmount` | 1 |
| `18446744073709551616` | stderr `error: InvalidAmount` | 1 |
| `18446744073709551615 0` | stdout `count=2, total=18446744073709551615` | 0 |
| `18446744073709551615 1` | stderr `error: TotalOverflow` | 1 |

`cargo check` vérifie notamment les types sans exécuter le code. `cargo fmt --check` vérifie le formatage et Clippy fournit des diagnostics statiques. Même si ces vérifications réussissent, il faut exécuter séparément le programme pour vérifier les règles de calcul. Ici, les sorties, erreurs et codes de sortie ont été comparés en modes debug et release ; ni le débit ni la charge de production n’ont été mesurés.

## Que garantit Rust ?

Les contrôles de types et de propriété de Safe Rust contribuent à prévenir les utilisations de références invalides et les data races. La possibilité de déplacer des valeurs entre threads et de partager des références dépend aussi de contrats de types comme [`Send` et `Sync`](https://doc.rust-lang.org/book/ch16-04-extensible-concurrency-sync-and-send.html). Cela ne supprime pas toutes les conditions de concurrence, les interblocages, les fuites mémoire ni les erreurs de logique métier.

Avec [`unsafe`](https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html), la personne qui écrit le code assume les conditions de sûreté de certaines opérations. Ce n’est pas un interrupteur qui désactive tout le borrow checker ; une implémentation `unsafe` incorrecte ou une frontière FFI peut affecter la sûreté. Les serveurs, l’exécution asynchrone et les conceptions à état partagé n’ont pas été vérifiés dans le cadre de cette CLI.

Pour un exercice suivant, étendez le programme afin de lire les montants dans un fichier. Décidez comment distinguer les erreurs d’E/S de fichier de l’`InputError` existant pour mieux voir comment propriété et types d’erreur expriment les frontières du programme.
