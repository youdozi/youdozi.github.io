---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2021-07-23-multiple-gradle-build",
  "routeSlug": "2021-07-23-multiple-gradle-build",
  "kind": "post",
  "title": "Empaquetar varias aplicaciones Vue en un JAR de Spring Boot con Gradle",
  "description": "Compila aplicaciones Vue con tareas npm ci independientes, prepara recursos con Gradle Sync y empaquétalos en bootJar con rutas correctas y sin archivos obsoletos.",
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
  "draftSha256": "46f64ecec4e83059c0c1592f79a57aa32643a0ccbae6279d6a06efe943b8f243",
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

Para empaquetar varias aplicaciones Vue en un JAR de Spring Boot, asigna a cada una su propia tarea `npm ci` y de compilación, prepara los archivos generados en `build/` y añádelos a `bootJar`. No compartas la tarea de instalación de una aplicación con las demás ni escribas los paquetes generados directamente en `src/main/resources`.

Este ejemplo ejecutable sirve dos aplicaciones en `/project1/index.html` y `/project2/index.html`. Su entorno de reproducción es JDK17.0.8.1, Gradle8.4, Node24.13.0/npm11.6.2, Boot3.5.7, Vue3.5.44 y Vite8.3.5. Son versiones fijadas para reproducirlo, no recomendaciones de dependencias actuales para producción. Comprueba por separado los [requisitos de ejecución de Vite](https://vite.dev/guide/) y los de la versión de Boot elegida.

## Flujo de procesamiento

![Flujo de compilación de recursos y empaquetado en el JAR](/assets/diagrams/technical/es-2021-07-23-multiple-gradle-build.svg)

Cada aplicación Vue genera su propia salida. Una tarea Gradle Sync reúne únicamente esas salidas y bootJar las coloca en rutas estáticas separadas.

## Tareas por aplicación y empaquetado

Guarda estos archivos en un proyecto vacío. Cada aplicación tiene su propio `package.json`, archivo de bloqueo, `node_modules` y `dist`. `prepare.sh` copia el HTML/JS compartido en la segunda aplicación y crea ambos archivos de bloqueo.

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

Ejecuta `prepare.sh` al preparar inicialmente este ejemplo y registra ambos archivos `package-lock.json` generados. Las siguientes compilaciones de CI usan `npm ci` con los archivos de bloqueo guardados. No los regeneres en cada compilación.

## Compilar y ejecutar

Desde la raíz del proyecto, ejecuta lo siguiente con Node/npm disponibles en PATH:

```sh
node --version
npm --version
sh prepare.sh
gradle --no-daemon clean bootJar
java -jar build/libs/multi-frontend-1.0.0.jar
```

En un proyecto existente con wrapper, usa su versión de Gradle mediante `./gradlew`. Tras el arranque, visita `http://localhost:8080/project1/index.html` y `http://localhost:8080/project2/index.html`. Las páginas muestran `Vue app at /project1/` y `Vue app at /project2/`, respectivamente.

La [opción base de Vite](https://vite.dev/guide/build.html#public-base-path) proporciona las URL de recursos adecuadas a cada aplicación. No configura el enrutamiento SPA del servidor. Este ejemplo usa URL `index.html` explícitas; la navegación directa con history-router u otra ruta de contexto requiere configuración adicional.

## Inspeccionar las rutas reales del JAR

```text
BOOT-INF/classes/static/project1/index.html
BOOT-INF/classes/static/project1/assets/...
BOOT-INF/classes/static/project2/index.html
BOOT-INF/classes/static/project2/assets/...
```

Tras compilar cada aplicación, `collectFrontend` usa `Sync` para preparar solo las salidas actuales. `bootJar` las añade al classpath del JAR ejecutable. Consulta la [gestión de archivos de Gradle](https://docs.gradle.org/current/userguide/working_with_files.html) y el [empaquetado de archivos de Boot](https://docs.spring.io/spring-boot/3.5/gradle-plugin/packaging.html).

Ambas aplicaciones se compilaron y empaquetaron con esta configuración, y el JAR en ejecución sirvió sus recursos HTML y JS por HTTP. Después se eliminó un archivo del directorio `public` de una aplicación y se reconstruyó el JAR sin `clean` para comprobar que el archivo obsoleto no permaneciera. Los archivos de bloqueo de ambas aplicaciones se comprobaron por separado.

## Adaptarlo a un proyecto existente

- Ajusta la lista `apps` a los directorios y proporciona cada archivo de bloqueo.
- Mantén los espacios generados `static/project1` y `static/project2` separados de los recursos escritos manualmente.
- Para componentes Vue SFC, añade el plugin y la configuración Vite adecuados. Este ejemplo pequeño usa funciones de renderizado de Vue.
- La integración se dirige al `bootJar` ejecutable, no al `jar` normal. Inspecciona el artefacto que desplegarás.

En una aplicación existente, comprueba la [base de migración de Java y Jakarta en Spring Boot](/en/posts/2023-09-08-springboot3-migration/) independientemente del empaquetado. Si también ejecuta trabajos Batch, sigue las [comprobaciones de migración del repositorio Batch y reinicio](/en/posts/2023-10-27-springbatch5-migration/); servir recursos de interfaz desde un JAR no valida los datos persistidos de los trabajos.

Para automatización basada en versiones, consulta la [selección de versiones y recursos de GitHub](/en/posts/2023-09-23-linux-shellscript-github-latest/) y el [contrato de entrada del comparador numérico](/en/posts/2023-11-17-linux-shellscript-version-compare/). La [guía de funciones POSIX sh](/en/posts/2023-09-20-linux-shellscript-function-error/) trata la selección del intérprete para scripts de preparación.
