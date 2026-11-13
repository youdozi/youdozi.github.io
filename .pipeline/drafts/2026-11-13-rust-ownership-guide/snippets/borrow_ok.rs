fn main() {
    let mut name = String::from("Rust");
    let borrowed = &name;
    println!("{borrowed}");
    name.push_str(" language");
    println!("{name}");
}
