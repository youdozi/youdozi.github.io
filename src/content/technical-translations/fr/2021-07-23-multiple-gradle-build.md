---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2021-07-23-multiple-gradle-build",
  "routeSlug": "2021-07-23-multiple-gradle-build",
  "kind": "post",
  "title": "Empaqueter plusieurs applications Vue dans un JAR Spring Boot avec Gradle",
  "description": "Construire chaque application Vue avec npm ci, réunir les assets avec Gradle Sync et les intégrer à bootJar avec les bons chemins, sans fichiers obsolètes.",
  "categories": [
    "springboot"
  ],
  "tags": [
    "gradle",
    "vue",
    "build",
    "SpringBoot"
  ],
  "sourcePath": "src/content/posts/en/2021-07-23-multiple-gradle-build.md",
  "sourceSha256": "2af4402a72130c6c53faa9d34008be0c7bc63b78b82a680f5675bdd70532ec4d",
  "draftSha256": "8a85627d1ba68d656862ba0ca7ed3df0d902d150a9dbf727f2f448ec360e718a",
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
Pour empaqueter plusieurs applications Vue dans un JAR Spring Boot, attribuez à chacune sa propre tâche `npm ci` et de compilation, rassemblez les fichiers générés sous `build/`, puis ajoutez-les à `bootJar`. Ne partagez pas la tâche d’installation d’une application avec les autres et n’écrivez pas les bundles générés directement dans `src/main/resources`.

Cet exemple exécutable sert deux applications à `/project1/index.html` et `/project2/index.html`. Son environnement de reproduction comprend JDK17.0.8.1, Gradle8.4, Node24.13.0/npm11.6.2, Boot3.5.7, Vue3.5.44 et Vite8.3.5. Ces versions sont figées pour la reproduction et ne constituent pas une recommandation de dépendances actuelles pour la production. Vérifiez séparément les [exigences d’exécution de Vite](https://vite.dev/guide/) et celles de la version Boot choisie.

## Déroulement du traitement

![Construction des assets et intégration dans le JAR](/assets/diagrams/technical/fr-2021-07-23-multiple-gradle-build.svg)

Chaque application Vue construit sa propre sortie. Une tâche Gradle Sync ne rassemble que ces sorties, puis bootJar les place sous des chemins statiques distincts.

## Tâches par application et empaquetage

Enregistrez ces fichiers dans un projet vide. Chaque application possède ses propres `package.json`, fichier de verrouillage, `node_modules` et `dist`. `prepare.sh` copie le HTML/JS commun dans la seconde application et crée les deux fichiers de verrouillage.

### `settings.gradle`

```groovy
rootProject.name = 'multi-frontend'
```

### `build.gradle`

```groovy
plugins {
    id 'java'
    id 'org.springframework.boot' version '3.5.7'
}
group = 'example'
version = '1.0.0'
repositories { mavenCentral() }
dependencies {
    implementation platform('org.springframework.boot:spring-boot-dependencies:3.5.7')
    implementation 'org.springframework.boot:spring-boot-starter-web'
}

def apps = ['project1', 'project2']
def npmCommand = System.getProperty('os.name').toLowerCase().contains('windows') ? 'npm.cmd' : 'npm'
def frontendBuilds = apps.collect { app ->
    def frontend = layout.projectDirectory.dir("frontend/${app}")
    def install = tasks.register("${app}NpmCi", Exec) {
        workingDir frontend
        commandLine npmCommand, 'ci', '--no-audit', '--no-fund'
        inputs.files(frontend.file('package.json'), frontend.file('package-lock.json'))
        outputs.dir(frontend.dir('node_modules'))
    }
    tasks.register("${app}Build", Exec) {
        dependsOn install
        workingDir frontend
        commandLine npmCommand, 'run', 'build'
        inputs.files(fileTree(frontend) {
            exclude 'node_modules/**', 'dist/**'
        })
        outputs.dir(frontend.dir('dist'))
    }
}
def collectFrontend = tasks.register('collectFrontend', Sync) {
    dependsOn frontendBuilds
    into layout.buildDirectory.dir('frontend-resources')
    apps.each { app ->
        from("frontend/${app}/dist") { into "static/${app}" }
    }
}
tasks.named('bootJar') {
    dependsOn collectFrontend
    from(collectFrontend) { into 'BOOT-INF/classes' }
}
```

### `src/main/java/example/Application.java`

```java
package example;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

### `frontend/project1/package.json`

```json
{
  "name": "project1",
  "private": true,
  "type": "module",
  "scripts": {
    "build": "vite build --base=/project1/"
  },
  "dependencies": {
    "vue": "3.5.44"
  },
  "devDependencies": {
    "vite": "8.3.5"
  }
}
```

### `frontend/project2/package.json`

```json
{
  "name": "project2",
  "private": true,
  "type": "module",
  "scripts": {
    "build": "vite build --base=/project2/"
  },
  "dependencies": {
    "vue": "3.5.44"
  },
  "devDependencies": {
    "vite": "8.3.5"
  }
}
```

### `frontend/project1/index.html`

```html
<!doctype html>
<html lang="en"><head><meta charset="UTF-8"><title>Vue build example</title></head>
<body><div id="app"></div><script type="module" src="/src/main.js"></script></body></html>
```

### `frontend/project1/src/main.js`

```js
import { createApp, h } from 'vue';
createApp({ render: () => h('h1', `Vue app at ${import.meta.env.BASE_URL}`) }).mount('#app');
```

### `prepare.sh`

```sh
#!/bin/sh
set -eu
mkdir -p frontend/project2/src
cp frontend/project1/index.html frontend/project2/index.html
cp frontend/project1/src/main.js frontend/project2/src/main.js
for app in project1 project2; do
    (cd "frontend/$app" && npm install --package-lock-only --ignore-scripts --no-audit --no-fund)
done
```

Exécutez `prepare.sh` lors de la préparation initiale de cet exemple et versionnez les deux fichiers `package-lock.json` générés. Les compilations CI suivantes utilisent `npm ci` avec les fichiers de verrouillage enregistrés. Ne les régénérez pas à chaque compilation.

## Construire et exécuter

Depuis la racine du projet, exécutez les commandes suivantes avec Node/npm accessibles dans PATH :

```sh
node --version
npm --version
sh prepare.sh
gradle --no-daemon clean bootJar
java -jar build/libs/multi-frontend-1.0.0.jar
```

Pour un projet existant utilisant le Wrapper, employez la version Gradle sélectionnée via `./gradlew`. Après le démarrage, ouvrez `http://localhost:8080/project1/index.html` et `http://localhost:8080/project2/index.html`. Les pages affichent respectivement `Vue app at /project1/` et `Vue app at /project2/`.

[L’option base de Vite](https://vite.dev/guide/build.html#public-base-path) attribue à chaque application les URL d’assets appropriées. Elle ne configure pas le routage SPA côté serveur. Cet exemple utilise des URL `index.html` explicites ; une navigation directe avec un routeur history ou un autre chemin de contexte nécessite une configuration supplémentaire.

## Inspecter les chemins réels du JAR

```text
BOOT-INF/classes/static/project1/index.html
BOOT-INF/classes/static/project1/assets/...
BOOT-INF/classes/static/project2/index.html
BOOT-INF/classes/static/project2/assets/...
```

Après la compilation de chaque application, `collectFrontend` utilise `Sync` pour ne rassembler que les sorties actuelles. `bootJar` les ajoute sous le classpath du JAR exécutable. Voir la [gestion des fichiers avec Gradle](https://docs.gradle.org/current/userguide/working_with_files.html) et [l’empaquetage des archives Boot](https://docs.spring.io/spring-boot/3.5/gradle-plugin/packaging.html).

Les deux applications ont été construites et empaquetées avec cette configuration, et le JAR en cours d’exécution a servi leurs assets HTML et JS par HTTP. Un fichier du répertoire `public` d’une application a ensuite été supprimé et le JAR reconstruit sans `clean` pour vérifier que le fichier obsolète ne subsistait pas. Les fichiers de verrouillage des deux applications ont été vérifiés séparément.

## Adapter à un projet existant

- Faites correspondre la liste `apps` aux répertoires et fournissez chaque fichier de verrouillage.
- Séparez les espaces de noms générés `static/project1` et `static/project2` des ressources écrites à la main.
- Pour les SFC Vue, ajoutez le plugin et la configuration Vite adaptés à l’application. Ce petit exemple utilise des fonctions de rendu Vue.
- L’intégration cible le `bootJar` exécutable, et non le simple `jar`. Inspectez l’artefact que vous déploierez.

Pour une application existante, vérifiez les [prérequis de migration Java et Jakarta pour Spring Boot](/en/posts/2023-09-08-springboot3-migration/) indépendamment de l’empaquetage. Si elle exécute également des jobs Batch, suivez les [contrôles de migration du repository Batch et de redémarrage](/en/posts/2023-10-27-springbatch5-migration/) ; servir des assets frontend depuis un JAR ne valide pas les données de jobs persistées.

Pour l’automatisation pilotée par les releases, consultez la [sélection des releases et assets GitHub](/en/posts/2023-09-23-linux-shellscript-github-latest/) et le [contrat d’entrée du comparateur numérique](/en/posts/2023-11-17-linux-shellscript-version-compare/). Le [guide des fonctions POSIX sh](/en/posts/2023-09-20-linux-shellscript-function-error/) traite du choix de l’interpréteur pour les scripts de préparation.
