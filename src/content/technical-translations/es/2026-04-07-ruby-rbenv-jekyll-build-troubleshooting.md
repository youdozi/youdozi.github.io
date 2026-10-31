---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2026-04-07-ruby-rbenv-jekyll-build-troubleshooting",
  "routeSlug": "2026-04-07-ruby-rbenv-jekyll-build-troubleshooting",
  "kind": "post",
  "title": "Fallos de gemas nativas Ruby: separar ejecución y cabeceras C++",
  "description": "Diagnostica el arranque Ruby aparte de compilar C++ con una prueba temporal. Compara RbConfig y opciones SDK por comando sin reinstalar el entorno.",
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
  "draftSha256": "e618e330395c881c1ecfc5b30ccf42d29291f82c2071ec168cb2c933e4144578",
  "manifestPath": ".pipeline/technical-translations/batch-125/manifest.json",
  "manifestSha256": "1934910c02dbe893b786124f1d296d7adf9efbe921d40b3d2cfbceb8f70b4b33",
  "publishedAt": "2026-10-31T15:35:43.034Z",
  "updatedAt": "2026-10-31T15:35:43.034Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 125,
    "approvedAt": "2026-10-31T15:35:43.034Z",
    "basis": "User explicitly requested applying all missing technical-post languages, review, verification and deployment on 2026-11-01, with standing PR merge authorization. Human approval denotes publication authorization; linguistic review is performed by AI, not human/native review."
  }
}
---

Separa arranque Ruby y compilación nativa. Un `ruby --version` funcional no demuestra que C++ encuentre sus cabeceras, ni un programa C++ correcto que compile una extensión gema.

El registro original trataba una ruta de biblioteca Ruby de otro usuario y un problema SDK/cabeceras macOS. Son fallos distintos. El diagnóstico los separa sin desinstalar Ruby, cambiar Command Line Tools ni sobrescribir RbConfig globalmente. El sitio usa ahora Astro; las comprobaciones son para las herramientas Ruby conservadas.

## Empezar por la capa que falla

![Comprobar arranque Ruby, inspeccionar compilador y probar C++ aisladamente](/assets/diagrams/technical/es-2026-04-07-ruby-rbenv-jekyll-build-troubleshooting.svg)

Compara primero Ruby elegido con su configuración de compilación registrada:

```sh
command -v ruby
ruby --version
rbenv which ruby
ruby -rrbconfig -e 'puts RbConfig.ruby; puts RbConfig::CONFIG.values_at("CXX", "CPPFLAGS", "CXXFLAGS")'
```

Si Ruby no arranca por una biblioteca ausente, investiga intérprete y enlace antes de instalar gemas. En macOS, `otool -L` inspecciona el ejecutable seleccionado por `rbenv which ruby`. No reinstales todos los Ruby solo por fallar una gema nativa.

[RbConfig](https://docs.ruby-lang.org/en/3.2/RbConfig.html) expone la configuración del intérprete. En Ruby3.2.2 probado, `CXX` era `false`, mientras `c++` explícito funcionaba con opciones de cabeceras adecuadas. Afecta a ese intérprete y host, no a toda instalación rbenv. Ruby3.2 está [fuera de soporte](https://www.ruby-lang.org/en/downloads/branches/); se diagnostica un entorno antiguo.

## Compilar sin cambiar la configuración Ruby

Guarda este script completo de biblioteca estándar Ruby como `native_probe.rb`:

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

Ejecútalo con el compilador elegido para la prueba:

```sh
ruby native_probe.rb
```

Compila un programa C++17 temporal y exige salida exacta `42`. `CXX` elige el comando de prueba y `PROBE_CXXFLAGS` solo sus opciones. Informa del CXX configurado de Ruby sin reemplazarlo. `CXX` vacío, compilación fallida o salida inesperada causan código distinto de cero.

En el Mac probado, la invocación predeterminada falló por no encontrar `iostream`. Tras revisar SDK y confirmar el directorio de cabeceras, estas opciones limitadas al comando hicieron pasar la prueba:

```sh
probe_sdk="$(xcrun --show-sdk-path)"
test -d "$probe_sdk/usr/include/c++/v1"
PROBE_CXXFLAGS="-isysroot $probe_sdk -isystem $probe_sdk/usr/include/c++/v1" ruby native_probe.rb
```

La ruta se probó en ese Mac. No es una reparación SDK universal; las rutas con espacios requieren tokens bien entrecomillados dentro de las opciones. Empieza con `xcode-select -p` y `xcrun --show-sdk-path`; no instales el paquete CLT nombrado en un ejemplo antiguo. La [guía Apple](https://developer.apple.com/library/archive/technotes/tn2339/_index.html) explica directorio y herramientas SDK.

## Volver al fallo real de la gema

Pasar reduce la investigación; la extensión puede usar otras opciones, cabeceras, bibliotecas o ABI. Conserva el log y compara el comando real. `scripts/ruby_cxx_fix.rb` cambia RbConfig dentro de Ruby al cargarse explícitamente; su alternativa Homebrew depende del host. Aplica la solución tras confirmar el fallo y conserva opciones RUBYOPT existentes.

El éxito local no reinstaló Ruby ni reconstruyó gemas nativas antiguas. Para la siguiente capa usa el [bundle Jekyll aislado de dos páginas](/en/posts/2023-09-04-jekyll-install/). Para el sitio activo, la [guía de controles Astro](/en/posts/2026-04-07-jekyll-quality-gates-proof-html-bundler-audit/).
