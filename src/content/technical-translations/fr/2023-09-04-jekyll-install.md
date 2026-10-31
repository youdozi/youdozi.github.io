---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2023-09-04-jekyll-install",
  "routeSlug": "2023-09-04-jekyll-install",
  "kind": "post",
  "title": "Installer Jekyll : vérifier Ruby et le contexte Bundler",
  "description": "Vérifier la sélection de Ruby et le contexte Bundler, puis exécuter un test de compatibilité Jekyll avec deux pages rendues.",
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
  "draftSha256": "ec63b6bc850aa24737b3a7aba8dc4fe9431a0bbbd80dfe708fe35b2edb30ca53",
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
Avant de modifier les permissions, vérifiez quel Ruby s’exécute, quel Bundler gère le contexte des dépendances et si un petit site se rend correctement. La construction actuelle de ce site utilise Astro ; l’exemple Jekyll ci-dessous sert à diagnostiquer l’archive Ruby conservée.

L’installation d’origine utilisait Ruby 3.2.2. Cette branche est désormais [en fin de vie](https://www.ruby-lang.org/en/downloads/branches/) : l’ancienne version sert donc à reproduire la compatibilité, et ne constitue pas une recommandation pour une nouvelle installation. Choisissez un Ruby maintenu compatible avec les gems du projet avant de l’adopter.

## Choisir l’interpréteur avant d’installer les gems

![Vérifier Ruby, les dépendances du bundle et le rendu d’un petit site](/assets/diagrams/technical/fr-2023-09-04-jekyll-install.svg)

[Les instructions macOS de Jekyll](https://jekyllrb.com/docs/installation/macos/) conseillent un environnement Ruby distinct plutôt que le Ruby système. La configuration précédente de ce dépôt utilisait rbenv. Ses [règles de sélection de version](https://github.com/rbenv/rbenv#readme) distinguent le fichier `.ruby-version` du projet, `RBENV_VERSION` et la valeur globale par défaut.

Exécutez ces commandes dans le répertoire du projet :

```sh
command -v ruby
ruby --version
rbenv version
rbenv which ruby
gem env home
bundle --version
```

Si `ruby` n’est pas sélectionné par le gestionnaire attendu, corrigez l’initialisation du shell avant toute installation. Utilisez `rbenv init` selon les instructions de la version rbenv installée ; ne collez pas le chemin personnel d’une autre personne dans votre profil shell. Une sélection propre au projet est préférable à une modification de tous les projets Ruby avec `rbenv global`.

## Tester un bundle avec deux pages rendues

Ce test de compatibilité a été exécuté avec Ruby3.2.2, Bundler2.4.19, Jekyll3.9.3 et kramdown-parser-gfm1.1.0. Ce sont des versions anciennes consignées, et non une base de versions prises en charge. Le Gemfile fige les deux gems directes ; le Gemfile.lock résultant enregistre les versions transitives pour votre plateforme.

Créez un répertoire d’essai distinct et enregistrez-y ces fichiers complets. Ne remplacez pas le Gemfile existant du dépôt.

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

Avec Ruby et Bundler sélectionnés disponibles, exécutez depuis ce répertoire :

```sh
bundle install
bundle exec ruby jekyll_probe.rb
```

Si les gems exactes sont déjà installées, `bundle lock --local` peut résoudre les dépendances à partir de cet inventaire local avant la même commande d’exécution. Il ne peut pas obtenir une gem manquante. Conservez le fichier de verrouillage pour reproduire un échec et examinez les modifications avant de le mettre à jour. Le [guide d’application de Bundler](https://guides.rubygems.org/using_bundler_in_applications/) explique le rôle du Gemfile et du fichier de verrouillage.

Le résultat observé était :

```json
{"ruby":"3.2.2","jekyll":"3.9.3","pages":2,"result":"passed"}
```

Le test construit dans un répertoire temporaire, utilise son chemin réel pour éviter une divergence de lien symbolique macOS sur `/var`, désactive la découverte des fichiers de configuration par défaut et se place dans sa propre source pendant le rendu. Il vérifie un titre, un lien et la page cible. Les fichiers temporaires sont ensuite supprimés ; l’archive complète, son thème, ses plugins, son CSS et son déploiement sortent du périmètre de ce contrôle.

## Distinguer disponibilité et appartenance au bundle

Pendant cette reproduction, Jekyll pouvait se charger, mais la conversion Markdown échouait car le bundle ne déclarait pas `kramdown-parser-gfm`. Installer une gem quelque part sur la machine et la rendre disponible dans `bundle exec` sont deux conditions distinctes. L’ajout du parseur au Gemfile de ce test a permis la conversion.

Un test réussi sur deux pages concentre la suite de l’enquête sur la configuration, le thème, les plugins et les entrées du vrai site. Un échec au chargement d’une extension native relève d’une autre couche : utilisez le [test de diagnostic Ruby et C++](/en/posts/2026-04-07-ruby-rbenv-jekyll-build-troubleshooting/). Pour le processus de publication actif de ce site, consultez le [workflow Astro de revue des candidats](/en/posts/2026-04-07-jekyll-github-actions-content-pipeline/).
