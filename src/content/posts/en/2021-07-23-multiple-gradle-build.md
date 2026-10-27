---
title: "Package Multiple Vue Apps in a Spring Boot JAR with Gradle"
language: "en"
translationKey: "2021-07-23-multiple-gradle-build"
routeSlug: "2021-07-23-multiple-gradle-build"
kind: "post"
publishedAt: "2026-10-27T02:36:39+00:00"
categories: ["springboot"]
tags: ["gradle", "vue", "build", "SpringBoot"]
updatedAt: 2026-10-27T05:23:47.316+00:00
reviewedAt: "2026-10-27"
reviewStatus: "revised"
reviewScope: "Primary documentation checked; published runnable example verified."
reviewSources: ["https://vite.dev/guide/", "https://vite.dev/guide/build.html", "https://docs.gradle.org/current/userguide/working_with_files.html", "https://docs.spring.io/spring-boot/3.5/gradle-plugin/packaging.html"]
description: "Build Vue apps with separate npm ci tasks, stage assets with Gradle Sync, and package them in bootJar with correct paths and no obsolete files."
---
To package several Vue apps in a Spring Boot JAR, give each app its own `npm ci` and build task, stage generated files under `build/`, then add them to `bootJar`. Do not share one app's install task across the others or write generated bundles directly into `src/main/resources`.

This runnable example serves two apps at `/project1/index.html` and `/project2/index.html`. Its reproduction environment is JDK17.0.8.1, Gradle8.4, Node24.13.0/npm11.6.2, Boot3.5.7, Vue3.5.44 and Vite8.3.5. These are pinned reproduction versions, not a recommendation of current production dependencies. Check [Vite's runtime requirements](https://vite.dev/guide/) and those of the selected Boot release separately.

## Processing flow

![Build assets into the JAR workflow](/assets/diagrams/2021-07-23-multiple-gradle-build-en.svg)

Each Vue app builds its own output. A Gradle Sync task collects only those outputs, then bootJar places them under separate static paths.

## Per-app tasks and packaging

Save these files in an empty project. Each app has its own `package.json`, lockfile, `node_modules` and `dist`. `prepare.sh` copies the shared HTML/JS into the second app and creates both lockfiles.

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

Run `prepare.sh` when initially preparing this example and commit both generated `package-lock.json` files. Subsequent CI builds use `npm ci` against the saved lockfiles. Do not regenerate them on every build.

## Build and run

From the project root, run the following with Node/npm available on PATH:

```sh
node --version
npm --version
sh prepare.sh
gradle --no-daemon clean bootJar
java -jar build/libs/multi-frontend-1.0.0.jar
```

For an existing wrapper-based project, use its selected Gradle version through `./gradlew`. After startup, visit `http://localhost:8080/project1/index.html` and `http://localhost:8080/project2/index.html`. The pages show `Vue app at /project1/` and `Vue app at /project2/` respectively.

[Vite's base option](https://vite.dev/guide/build.html#public-base-path) gives each app the appropriate asset URLs. It does not configure server-side SPA routing. This example uses explicit `index.html` URLs; direct history-router navigation or another context path needs additional configuration.

## Inspect the actual JAR paths

```text
BOOT-INF/classes/static/project1/index.html
BOOT-INF/classes/static/project1/assets/...
BOOT-INF/classes/static/project2/index.html
BOOT-INF/classes/static/project2/assets/...
```

After the per-app builds, `collectFrontend` uses `Sync` to stage only current outputs. `bootJar` adds them beneath the executable JAR's classpath. See [Gradle file handling](https://docs.gradle.org/current/userguide/working_with_files.html) and [Boot archive packaging](https://docs.spring.io/spring-boot/3.5/gradle-plugin/packaging.html).

Both apps were built and packaged with this configuration, and the running JAR served their HTML and JS assets over HTTP. A file in an app's `public` directory was then removed and the JAR rebuilt without `clean` to check that the obsolete file did not survive. Both apps' lockfiles were checked separately.

## Adapt it to an existing project

- Match the `apps` list to the directories and provide each lockfile.
- Keep generated `static/project1` and `static/project2` namespaces separate from hand-written resources.
- For Vue SFCs, add the plugin and Vite configuration appropriate to that app. This small example uses Vue render functions.
- The integration targets executable `bootJar`, not the plain `jar`. Inspect the artifact you will deploy.

For release-driven automation, see [GitHub release/asset selection](/en/posts/2023-09-23-linux-shellscript-github-latest/) and the [numeric comparator's input contract](/en/posts/2023-11-17-linux-shellscript-version-compare/). The [POSIX sh function guide](/en/posts/2023-09-20-linux-shellscript-function-error/) covers interpreter selection for preparation scripts.
