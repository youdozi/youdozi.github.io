---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2026-11-15-orca-herdr-comparison",
  "routeSlug": "2026-11-15-orca-herdr-comparison",
  "kind": "post",
  "title": "Orca frente a Herdr: ¿dónde y cómo gestionar agentes de programación con IA?",
  "description": "Comparamos worktrees, persistencia de sesiones, revisión de código, trabajo remoto y extensibilidad de Orca y Herdr, con sus ventajas y limitaciones.",
  "categories": [
    "ai"
  ],
  "tags": [
    "orca",
    "herdr",
    "ai-agent",
    "git-worktree",
    "developer-tools"
  ],
  "sourcePath": "src/content/posts/en/2026-11-15-orca-herdr-comparison.md",
  "sourceSha256": "2a0f1ca513f60e49bad64d71689d7e59effe22e995582b05d6e1688572f172e4",
  "draftSha256": "8b23aa44a043f8ea2099960ea059b6dd07ac4ebbff124656bbe382d0e11f7eab",
  "manifestPath": ".pipeline/technical-translations/batch-165/manifest.json",
  "manifestSha256": "8b72a2b5aba51a050b30cc0ef5f871d2ef550798d50d91ef082c49bbf6448835",
  "publishedAt": "2026-11-17T06:12:46.742Z",
  "updatedAt": "2026-11-17T06:12:46.742Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 165,
    "approvedAt": "2026-11-17T06:12:46.742Z",
    "basis": "User requested multilingual application of the five recent articles and standing publication/merge authorization; AI translation and independent AI comparison completed. This records publication authorization, not human or native-speaker textual review."
  }
}
---

**Orca resulta cómoda para ver los cambios por worktree y manejar navegador, diff y PR en una misma interfaz. Herdr merece atención si quieres una organización centrada en el terminal y ampliar tú mismo la interfaz de la aplicación.** Ambas herramientas permiten ejecutar varios agentes de programación y usar Git worktree. El criterio de elección es cómo gestionan el entorno y los resultados, más que si permiten ejecución paralela.

Comparamos [Orca](https://orca.dev/) y [Herdr](https://herdr.dev/). Herdr se divide en una aplicación de escritorio, **Herdr TUI** para terminal y un entorno de ejecución de terminales separado, **herdr-core**. La explicación se basa en la documentación oficial consultada el 15 de noviembre de 2026; no es una prueba de rendimiento de ambas aplicaciones con la misma tarea. Distingue las funciones descritas por los proveedores de los criterios de elección derivados de ellas.

## Diferencias de un vistazo

| Criterio | Orca | Herdr |
| --- | --- | --- |
| Interfaz principal | Entorno de desarrollo de escritorio que reúne agentes, editor, diff y navegador | Aplicación de escritorio y TUI separada; herdr-core ejecuta terminales sin interfaz |
| Separación de tareas | Crea un Git worktree por tarea y conecta rama, terminal y navegador | La guía de la aplicación y la configuración de TUI incluyen creación de worktrees. Un panel de terminal normal no implica siempre un worktree independiente |
| Revisión de código | Diff por worktree, comentarios sobre líneas modificadas e interfaces de Git y PR | Centrada en el terminal o en la interfaz configurada por el usuario. Hay que comprobar las funciones equivalentes de diff y su alcance en la configuración instalada |
| Persistencia de sesiones | Los procesos siguen al cerrar la aplicación si el demonio continúa activo; reiniciar el host termina los procesos | herdr-core mantiene los terminales de la aplicación; un servidor separado, los de TUI. Reiniciar servidor o host termina los procesos originales |
| Extensibilidad | CLI, habilidades, programación e interfaz de tareas de la aplicación | Diseños y modos de la aplicación, plugins de TUI, CLI y API de herdr-core |
| Licencia | MIT | Apache 2.0 |

La tabla se basa en la [documentación de worktrees](https://orca.dev/docs/model/worktrees) y la [guía de diff](https://orca.dev/docs/review/diff-viewer) de Orca, y en la [guía de la aplicación](https://herdr.dev/guide/) y la [configuración de TUI](https://herdr.dev/tui/docs/config-reference/) de Herdr. No es una medición de todas las funciones de ambos productos en una versión concreta.

## Cómo cambia el flujo al delegar el mismo trabajo

Supongamos que quieres modificar una API y ampliar sus pruebas en paralelo en un mismo repositorio. Si ambas tareas pueden tocar el mismo archivo, separa primero los worktrees. Define qué puede leer y escribir cada agente y, al terminar, revisa cada cambio antes de integrarlo.

Orca permite abrir un worktree por tarea y asociar el agente y el diff a ese espacio. La [guía de primera sesión](https://orca.dev/docs/first-session) describe cómo ejecutar agentes en varios worktrees independientes y revisar después cada diff.

La guía oficial de la aplicación de escritorio de Herdr muestra solicitudes para crear worktrees por tarea y ejecutar agentes. TUI gestiona workspace, tab y pane, y además ofrece funciones de worktree. Abrir varios paneles normales no garantiza que cada uno tenga un directorio de trabajo diferente: comprueba la ruta y la rama antes de empezar. [Guía de la aplicación](https://herdr.dev/guide/) · [Comandos worktree de TUI](https://herdr.dev/tui/docs/cli-reference/)

![Se crean los worktrees A y B desde el commit base, se escriben valores distintos y se comprueban los archivos y las listas de cambios frente al archivo base](/assets/diagrams/technical/es-2026-11-15-orca-herdr-comparison.svg)

El diagrama muestra el flujo de archivos del siguiente ejemplo de Git. No incluye la ejecución de agentes ni la integración automática de resultados.

## Ejemplo para comprobar la separación de worktrees

El ejemplo se ejecuta en un shell de macOS o Linux con Git instalado. Crea un repositorio temporal y dos worktrees, sin modificar un proyecto existente. No sustituye las instrucciones de instalación y configuración de Orca o Herdr.

```sh
#!/bin/sh
set -eu
case_dir=$(mktemp -d)
git init -q "$case_dir/repo"
git -C "$case_dir/repo" config user.name 'Example Author'
git -C "$case_dir/repo" config user.email 'example@example.invalid'
printf 'base\n' > "$case_dir/repo/app.txt"
git -C "$case_dir/repo" add app.txt
git -C "$case_dir/repo" commit -qm 'Initial commit'
git -C "$case_dir/repo" worktree add -qb task-a "$case_dir/task-a" HEAD
git -C "$case_dir/repo" worktree add -qb task-b "$case_dir/task-b" HEAD
printf 'task A\n' > "$case_dir/task-a/app.txt"
printf 'task B\n' > "$case_dir/task-b/app.txt"
printf 'A: '; cat "$case_dir/task-a/app.txt"
printf 'B: '; cat "$case_dir/task-b/app.txt"
printf 'base: '; cat "$case_dir/repo/app.txt"
printf 'A 변경 파일: '; git -C "$case_dir/task-a" diff --name-only
printf 'B 변경 파일: '; git -C "$case_dir/task-b" diff --name-only
```

Esta fue la salida comprobada en el shell local.

```text
A: task A
B: task B
base: base
A 변경 파일: app.txt
B 변경 파일: app.txt
```

El contenido de cada worktree es independiente, pero ambas tareas han modificado `app.txt`. Al integrar los resultados en un proyecto real pueden aparecer conflictos o contradicciones de significado. Un worktree separa los cambios en archivos: no aísla automáticamente bases de datos, puertos, servicios externos ni credenciales, ni resuelve conflictos de código. El ejemplo no elimina automáticamente el directorio temporal.

Al limpiar worktrees en un entorno real, comprueba también qué elimina cada herramienta. Orca puede eliminar el worktree y la rama tras confirmación; la documentación de Herdr TUI indica que su comando de eliminación quita la copia de trabajo, pero no la rama. Revisa los cambios y los commits sin integrar antes de limpiar. [Orca worktree](https://orca.dev/docs/model/worktrees) · [Herdr TUI CLI](https://herdr.dev/tui/docs/cli-reference/)

## Ventajas y aspectos a considerar de Orca

La fortaleza de Orca es **una interfaz que conecta la tarea con la revisión del resultado**. El [diff viewer](https://orca.dev/docs/review/diff-viewer) muestra archivos y líneas modificadas y ofrece resolución de conflictos y preparación parcial de cambios. Tener navegador y editor separados en el mismo espacio facilita modificar una interfaz web, verla y revisar los cambios.

La [guía de ejecución remota](https://orca.dev/docs/ways-to-run) explica también cómo elegir un host SSH o un servidor administrado por el usuario. Poder trabajar en remoto no implica que todos los entornos estén aislados de forma segura por defecto y con los mismos permisos. Las cuentas, los secretos y el acceso de red de la máquina remota deben gestionarse por separado.

Según la [guía de restauración de sesiones](https://orca.dev/docs/model/session-restore), los agentes siguen ejecutándose al cerrar la aplicación mientras el demonio en segundo plano permanezca activo. Si se reinicia el host o termina el demonio, desaparecen los procesos en ejecución y hay que volver a iniciar los agentes en el espacio restaurado.

Hay que aprender el entorno de escritorio y sus funciones. Si solo necesitas una tarea de terminal, varias pantallas y espacios pueden sobrar. Ejecutar varios agentes a la vez puede aumentar el uso de modelos y cada resultado modificado de forma independiente necesita revisión. Orca no garantiza por sí misma la exactitud de las respuestas del modelo.

## Ventajas y aspectos a considerar de Herdr

La fortaleza de Herdr es **la flexibilidad para configurar el espacio manteniendo terminales y agentes en ejecución**. [herdr-core](https://herdr.dev/core/) describe cómo conserva los terminales gestionados al cerrar una ventana y ofrece una interfaz para que un agente inicie otras tareas y lea sus resultados. La [guía oficial](https://herdr.dev/guide/) también presenta la personalización de diseños y modos de la aplicación.

Al usar Herdr hay que distinguir la aplicación de TUI. Según el sitio oficial, la aplicación de escritorio usa herdr-core, pero **Herdr TUI utiliza un servidor separado y ambos entornos no comparten la lista de agentes.** Cerrar la aplicación también es distinto de reiniciar el equipo o el entorno de ejecución. En escritorio, cerrar ventanas o actualizar la aplicación mantiene los procesos si core sigue activo; reiniciar el dispositivo o detener core los termina. El sitio explica que, en ese caso, se recuperan los paneles de la aplicación, pero los agentes no se reinician automáticamente. [Herdr FAQ](https://herdr.dev/)

TUI tiene sus propias reglas de restauración. Al desconectar y volver a conectar, se mantienen los procesos originales mientras el servidor siga activo. Reiniciar el servidor termina los procesos; restaurar el diseño y reanudar sesiones de agentes compatibles son funciones separadas. [Restauración de sesiones TUI](https://herdr.dev/tui/docs/session-state/)

Cuanta más personalización haya, mayor será la responsabilidad de comprobar qué permisos y conexiones externas usa cada modo. Además, el estado que muestra la aplicación Herdr depende de programas que informan mediante [OSC 7501](https://herdr.dev/core/). Otros programas pueden ejecutarse, pero quizá no muestren estado. No equipares la detección de agentes de TUI con el estado mostrado en la aplicación.

## ¿Cuándo elegir cada una?

- **Si lo principal es revisar cambios y comprobar la web:** empieza por el flujo de diff, navegador y PR por worktree de Orca.
- **Si lo principal es mantener terminales y configurar la interfaz:** examina la aplicación Herdr y core; si quieres gestionar desde el terminal, compara también la TUI separada.
- **Si gestionas varios servidores y agentes:** ambas ofrecen funciones remotas; comprueba tu entorno SSH, la autenticación y las condiciones de recuperación de sesiones.
- **Si solo necesitas una corrección breve:** el terminal y Git que ya usas pueden bastar. Compara la comodidad con la complejidad que añade la herramienta de gestión.

Para elegir, conviene hacer una prueba pequeña con el mismo repositorio, tarea, modelo y permisos. Recorre la creación, el regreso tras una interrupción, la revisión y la integración, y registra el tiempo real y los errores. Así podrás elegir según tu forma de trabajar. Este artículo no incluye esas mediciones comparativas.
