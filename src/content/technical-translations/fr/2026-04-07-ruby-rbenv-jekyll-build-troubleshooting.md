---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2026-04-07-ruby-rbenv-jekyll-build-troubleshooting",
  "routeSlug": "2026-04-07-ruby-rbenv-jekyll-build-troubleshooting",
  "kind": "post",
  "title": "Ruby, rbenv et Jekyll : isoler les erreurs C++ natives",
  "description": "Vérifier séparément le démarrage Ruby, la configuration du compilateur et un test C++ isolé avant de modifier l’environnement.",
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
  "draftSha256": "47c88389dcd0875ef140d29cbd0d547316c3f3eddfcb5a49d9eba1b3e8f90bef",
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
Séparez le démarrage de Ruby de la compilation des extensions natives. Un `ruby --version` fonctionnel ne prouve pas qu’un compilateur C++ trouve ses en-têtes, et un programme C++ autonome réussi ne prouve pas que l’extension d’une gem compilera.

Le compte rendu d’origine concernait le chemin de bibliothèque Ruby d’une autre personne et un problème de SDK/en-têtes macOS. Ce sont des modes d’échec distincts. Le diagnostic ci-dessous conserve cette distinction sans désinstaller Ruby, changer les Command Line Tools ni remplacer RbConfig globalement. Le site actuel utilise Astro ; ces contrôles concernent les outils Ruby conservés.

## Commencer à la couche en échec

![Vérifier le démarrage Ruby, inspecter le compilateur et lancer un test C++ isolé](/assets/diagrams/technical/fr-2026-04-07-ruby-rbenv-jekyll-build-troubleshooting.svg)

Comparez d’abord le Ruby sélectionné à sa configuration de construction enregistrée :

```sh
command -v ruby
ruby --version
rbenv which ruby
ruby -rrbconfig -e 'puts RbConfig.ruby; puts RbConfig::CONFIG.values_at("CXX", "CPPFLAGS", "CXXFLAGS")'
```

Si Ruby lui-même ne démarre pas à cause d’une bibliothèque manquante, examinez cet interpréteur et ses liens de bibliothèques avant d’installer une gem. Sur macOS, `otool -L` peut inspecter l’exécutable sélectionné par `rbenv which ruby`. Ne réinstallez pas toutes les versions Ruby au seul motif qu’une gem native a échoué.

[RbConfig](https://docs.ruby-lang.org/en/3.2/RbConfig.html) expose la configuration de construction de l’interpréteur. Dans l’environnement Ruby3.2.2 testé, `CXX` valait `false`, tandis qu’un `c++` sélectionné explicitement pouvait fonctionner avec les options d’en-têtes adaptées. Cette observation concerne cet interpréteur et cet hôte, pas toutes les installations rbenv. Ruby3.2 est désormais [en fin de vie](https://www.ruby-lang.org/en/downloads/branches/) ; c’est le diagnostic d’un ancien environnement, pas une base prise en charge.

## Compiler sans modifier la configuration Ruby

Enregistrez ce script complet utilisant la bibliothèque standard Ruby sous `native_probe.rb` :

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

Exécutez-le avec le compilateur sélectionné pour le test :

```sh
ruby native_probe.rb
```

Le script compile un programme C++17 temporaire et exige une sortie exactement égale à `42`. `CXX` choisit la commande du test ; `PROBE_CXXFLAGS` fournit uniquement les options de ce test. Il rapporte le CXX configuré dans Ruby pour comparaison et ne le remplace pas. Un `CXX` vide, une compilation échouée ou une sortie inattendue provoque un code de sortie non nul.

Sur le Mac testé, l’appel par défaut échouait car `iostream` était introuvable. Après inspection du SDK sélectionné et confirmation de l’existence de son répertoire d’en-têtes, les options suivantes, limitées à la commande, ont fait réussir le test :

```sh
probe_sdk="$(xcrun --show-sdk-path)"
test -d "$probe_sdk/usr/include/c++/v1"
PROBE_CXXFLAGS="-isysroot $probe_sdk -isystem $probe_sdk/usr/include/c++/v1" ruby native_probe.rb
```

Ce chemin a été testé sur ce Mac. Ce n’est pas une réparation universelle du SDK, et les chemins contenant des espaces exigent des tokens correctement cités dans la valeur des options. Commencez par `xcode-select -p` et `xcrun --show-sdk-path` ; n’installez pas le paquet CLT nommé dans un vieil exemple. Le [guide Apple des outils en ligne de commande](https://developer.apple.com/library/archive/technotes/tn2339/_index.html) explique le répertoire développeur sélectionné et les outils du SDK.

## Revenir au véritable échec de gem

Un test réussi restreint l’enquête ; l’extension peut encore utiliser des options, en-têtes, bibliothèques ou exigences ABI différents. Conservez le journal de construction de la gem en échec et comparez la commande réellement invoquée. Le `scripts/ruby_cxx_fix.rb` du dépôt change les valeurs RbConfig à l’intérieur du processus Ruby lorsqu’il est explicitement chargé, et son repli Homebrew dépend de l’hôte. N’appliquez ce contournement qu’après correspondance avec l’échec ; préservez les options RUBYOPT existantes au lieu de les écraser aveuglément.

La réussite locale du test n’a ni réinstallé Ruby ni reconstruit les gems natives de l’ancien site. Pour la couche suivante, utilisez le [bundle Jekyll isolé à deux pages](/en/posts/2023-09-04-jekyll-install/). Pour les contrôles du site actif, consultez le [guide des contrôles qualité Astro](/en/posts/2026-04-07-jekyll-quality-gates-proof-html-bundler-audit/).
