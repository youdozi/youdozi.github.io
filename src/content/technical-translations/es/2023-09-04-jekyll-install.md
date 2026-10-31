---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2023-09-04-jekyll-install",
  "routeSlug": "2023-09-04-jekyll-install",
  "kind": "post",
  "title": "Jekyll en macOS: comprobar Ruby, Bundler y una compilación de dos páginas",
  "description": "Comprueba el Ruby elegido y el contexto de Bundler antes de cambiar permisos. Ejecuta una compilación aislada de Jekyll antiguo y distingue las gemas instaladas de las dependencias declaradas.",
  "categories": [
    "jekyll"
  ],
  "tags": [
    "ruby",
    "rbenv",
    "bundler",
    "jekyll",
    "macos"
  ],
  "sourcePath": "src/content/posts/en/2023-09-04-jekyll-install.md",
  "sourceSha256": "0dbe6c1bad26411bc78aabc17773da808b4c74fe9cdc098a9bada2cfb2873e08",
  "draftSha256": "de4354fc6c8b4804c67f2ed4dbae57e7be017526030ad65bf5d4ed08a9dbfa86",
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

Antes de cambiar permisos, comprueba qué Ruby se ejecuta, qué Bundler controla el contexto de dependencias y si se renderiza un sitio pequeño. La compilación activa de este sitio usa Astro; el ejemplo de Jekyll siguiente sirve para diagnosticar el archivo Ruby conservado.

La instalación original usaba Ruby 3.2.2. Esa rama ya está [fuera de soporte](https://www.ruby-lang.org/en/downloads/branches/), por lo que la versión antigua reproduce compatibilidad, no se recomienda para una instalación nueva. Antes de adoptarla, elige un Ruby mantenido compatible con las gemas del proyecto.

## Elegir el intérprete antes de instalar gemas

![Comprobar Ruby, las dependencias del bundle y renderizar un sitio pequeño](/assets/diagrams/technical/es-2023-09-04-jekyll-install.svg)

Las [instrucciones de Jekyll para macOS](https://jekyllrb.com/docs/installation/macos/) aconsejan usar un entorno Ruby separado en lugar del Ruby del sistema. La configuración anterior de este repositorio usaba rbenv. Sus [reglas de selección de versión](https://github.com/rbenv/rbenv#readme) distinguen un `.ruby-version` del proyecto, `RBENV_VERSION` y la opción global predeterminada.

Ejecuta estos comandos en el directorio del proyecto:

```sh
command -v ruby
ruby --version
rbenv version
rbenv which ruby
gem env home
bundle --version
```

Si `ruby` no se selecciona mediante el gestor esperado, corrige la inicialización de la shell antes de instalar nada. Usa `rbenv init` según las instrucciones de la versión de rbenv instalada; no pegues la ruta personal de otro usuario en tu perfil. Es preferible una selección local del proyecto a cambiar todos los proyectos Ruby con `rbenv global`.

## Probar un bundle con dos páginas renderizadas

Esta prueba de compatibilidad se ejecutó con Ruby3.2.2, Bundler2.4.19, Jekyll3.9.3 y kramdown-parser-gfm1.1.0. Son versiones antiguas registradas, no una base de versiones soportadas. El Gemfile fija las dos gemas directas; el Gemfile.lock resultante registra las versiones transitivas de tu plataforma.

Crea un directorio de pruebas separado y guarda allí estos archivos completos. No sustituyas el Gemfile existente del repositorio.

### `Gemfile`

```ruby
source 'https://rubygems.org'
gem 'jekyll', '= 3.9.3'
gem 'kramdown-parser-gfm', '= 1.1.0'
```

### `jekyll_probe.rb`

```ruby
require 'jekyll'
require 'tmpdir'
require 'fileutils'
require 'json'

Dir.mktmpdir('jekyll-probe-') do |root|
  root = File.realpath(root)
  source = File.join(root, 'source')
  destination = File.join(root, 'output')
  FileUtils.mkdir_p(File.join(source, '_layouts'))
  File.write(File.join(source, '_layouts', 'default.html'), '<!doctype html><html lang="en"><body>{{ content }}</body></html>')
  File.write(File.join(source, 'index.md'), "---\nlayout: default\ntitle: Probe\n---\n# Bundled build\n\n[Guide](/guide/)\n")
  File.write(File.join(source, 'guide.md'), "---\nlayout: default\npermalink: /guide/\n---\n# Local guide\n")
  config = Jekyll.configuration('config' => [], 'source' => source, 'destination' => destination, 'quiet' => true)
  Dir.chdir(source) { Jekyll::Site.new(config).process }
  home = File.read(File.join(destination, 'index.html'))
  guide = File.read(File.join(destination, 'guide', 'index.html'))
  raise 'Missing rendered heading' unless home.include?('<h1') && home.include?('Bundled build')
  raise 'Missing guide link' unless home.include?('href="/guide/"')
  raise 'Missing guide output' unless guide.include?('Local guide')
  puts JSON.generate('ruby' => RUBY_VERSION, 'jekyll' => Jekyll::VERSION, 'pages' => 2, 'result' => 'passed')
end
```

Con el Ruby y Bundler seleccionados disponibles, ejecuta desde ese directorio:

```sh
bundle install
bundle exec ruby jekyll_probe.rb
```

Si las gemas exactas ya están instaladas, `bundle lock --local` puede resolverlas desde ese inventario local antes del mismo comando de ejecución. No puede obtener una gema ausente. Conserva el archivo de bloqueo al reproducir un fallo y revisa los cambios antes de actualizarlo. La [guía de Bundler para aplicaciones](https://guides.rubygems.org/using_bundler_in_applications/) explica la función del Gemfile y su archivo de bloqueo.

El resultado observado fue:

```json
{"ruby":"3.2.2","jekyll":"3.9.3","pages":2,"result":"passed"}
```

La prueba compila en un directorio temporal, usa su ruta real para evitar una discrepancia con el enlace simbólico `/var` de macOS, desactiva el descubrimiento predeterminado de configuración y cambia a su propio directorio fuente al renderizar. Comprueba un encabezado, un enlace y la página destino. Después elimina los archivos temporales; quedan fuera de esta comprobación el archivo completo, su tema, plugins, CSS y despliegue.

## Distinguir disponibilidad y pertenencia al bundle

Durante esta reproducción, Jekyll cargaba, pero la conversión de Markdown fallaba porque el bundle no declaraba `kramdown-parser-gfm`. Instalar una gema en algún lugar del equipo y tenerla disponible dentro de `bundle exec` son condiciones distintas. Añadir el analizador al Gemfile de esta prueba permitió la conversión.

Una prueba correcta de dos páginas centra la investigación siguiente en la configuración, tema, plugins y entradas del sitio real. Un fallo al cargar una extensión nativa pertenece a otra capa: usa la [prueba de diagnóstico de Ruby y C++](/en/posts/2026-04-07-ruby-rbenv-jekyll-build-troubleshooting/). Para el proceso de publicación activo de este sitio, usa el [flujo de revisión de candidatos de Astro](/en/posts/2026-04-07-jekyll-github-actions-content-pipeline/).
