---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2026-11-27-droiddesk-android-linux-desktop",
  "routeSlug": "2026-11-27-droiddesk-android-linux-desktop",
  "kind": "post",
  "title": "DroidDesk por dentro · ¿Cómo funciona un escritorio Linux en un teléfono Android?",
  "description": "El APK independiente y el script de Termux usan distintos entornos de ejecución y salidas de pantalla. ¿Qué conviene probar primero en tu teléfono?",
  "categories": [
    "tips"
  ],
  "tags": [
    "android",
    "linux",
    "termux"
  ],
  "sourcePath": "src/content/posts/en/2026-11-27-droiddesk-android-linux-desktop.md",
  "sourceSha256": "656b9e1b21a758a366d894876650b607e9bd2eadcb535e4a0565a68566807a1f",
  "draftSha256": "91a30fec8f1a7e9a94427102ca0bb66169f202dfb7f7cb485bd347709304a432",
  "manifestPath": ".pipeline/technical-translations/batch-130/manifest.json",
  "manifestSha256": "155408f4218bb7fd2e43ec0f8dcb31522024a85ed96fb84e2f9768840357e28c",
  "publishedAt": "2026-11-27T06:13:21.434Z",
  "updatedAt": "2026-11-27T06:13:21.434Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 207,
    "approvedAt": "2026-11-27T06:13:21.434Z",
    "basis": "Explicit user request to publish the approved DroidDesk manuscript from item 129 in all nine languages (item 130)."
  }
}
---

¿Podrías conectar un teclado a un teléfono Android que ya no usas y trabajar con un editor y un navegador de Linux? DroidDesk es un proyecto de código abierto que ejecuta un escritorio Linux sobre Android. Antes de elegir cómo instalarlo, conviene entender que el APK independiente y el script de instalación para Termux siguen caminos distintos.

Este artículo se basa en las notas de la versión y el código fuente de orailnoor/DroidDesk v1.3.1, consultados el 27 de noviembre de 2026. No instalé el APK en un dispositivo físico ni medí el rendimiento de las aplicaciones. [Notas de la versión](https://github.com/orailnoor/DroidDesk/releases/tag/v1.3.1)

## ¿En qué se diferencian el APK y el script de Termux?

| Instalación | Entorno de ejecución | Pantalla |
| --- | --- | --- |
| APK independiente sin acceso root | Escritorio predeterminado en el Termux integrado, con Debian opcional mediante PRoot | Termux:X11 integrado |
| APK independiente con acceso root | Sistema de archivos de Ubuntu para ARM64 en un entorno chroot | Termux:X11 integrado |
| Script de instalación para Termux | Instalación aparte de Termux, con PRoot para los paquetes de la distribución | Aplicación Termux:X11 separada o VNC opcional |

![El APK independiente usa Termux:X11 integrado. El script de Termux muestra el escritorio mediante una aplicación Termux:X11 separada o por VNC.](/assets/diagrams/technical/es-2026-11-27-droiddesk-android-linux-desktop.svg)

El README indica que el APK no usa PRoot en teléfonos sin acceso root. Así funciona el escritorio predeterminado, que se ejecuta directamente en Termux. Sin embargo, en la v1.3.1, LinuxRuntime también permite instalar Debian de forma opcional e incluye un lanzador PRoot. Incluso dentro de la misma aplicación, las condiciones de ejecución pueden variar según abras el programa desde el escritorio predeterminado o dentro de Debian. [README](https://github.com/orailnoor/DroidDesk/blob/v1.3.1/README.md) · [LinuxRuntime](https://github.com/orailnoor/DroidDesk/blob/v1.3.1/app/android/app/src/main/kotlin/com/orailnoor/droiddesk/runtime/LinuxRuntime.kt) · [ChrootRuntime](https://github.com/orailnoor/DroidDesk/blob/v1.3.1/app/android/app/src/main/kotlin/com/orailnoor/droiddesk/runtime/ChrootRuntime.kt)

## ¿Qué puedes usar en tu teléfono?

Empieza por un programa que necesites. El proyecto cita Firefox, LibreOffice y VS Code entre sus ejemplos. Las notas de la v1.3.1 también recogen correcciones de errores de instalación y arranque que afectaban, entre otros, a un paquete necesario para Firefox y a VS Code. Una vez que aparezca el icono del editor, comprueba las extensiones, el método de entrada y las rutas de archivo que usas a diario. [Notas de la versión](https://github.com/orailnoor/DroidDesk/releases/tag/v1.3.1)

Los gráficos también dependen del dispositivo. El código incluye una ruta con Turnip y Zink para Adreno y otra de renderizado por software con llvmpipe. Para una aplicación exigente como Blender, comprueba si la aceleración funciona en tu teléfono y si tu proyecto se maneja con fluidez. Si piensas compilar con PRoot, ten en cuenta que las tareas que acceden con frecuencia a los archivos pueden tener un coste adicional. [Limitaciones de PRoot](https://github.com/termux/proot-distro#limitations)

Si quieres conectar un monitor externo, comprueba primero si el teléfono admite salida de vídeo por USB-C. En el montaje con Raspberry Pi que describe el proyecto, la Pi recibe la sesión VNC que proporciona el script de Termux y la muestra en el monitor. El APK independiente usa su propia pantalla X11 integrada. [Conexión del monitor](https://github.com/orailnoor/DroidDesk/blob/v1.3.1/README.md#for-monitor-output--optional-)

## ¿Qué tarea conviene probar primero?

Si tienes un dispositivo Android ARM64, busca el APK en la página oficial de versiones del proyecto y haz la primera prueba en la pantalla del teléfono. Por ejemplo, escribe un texto en coreano en el editor, guarda el archivo, vuelve a abrir la sesión y carga ese mismo archivo. Si funciona, conecta un teclado y un ratón o un monitor externo y continúa con tu trabajo habitual. El atractivo de DroidDesk es descubrir qué herramientas de Linux puedes aprovechar en un teléfono que ya tienes. Para editar documentos, empieza por la escritura y el guardado. Para desarrollar, comprueba los paquetes y las extensiones que necesitas. Para trabajos gráficos, prueba la aceleración y la respuesta de la pantalla. [Configuración de compilación de Android](https://github.com/orailnoor/DroidDesk/blob/v1.3.1/app/android/app/build.gradle.kts)

[Consultar el espacio que ocupa Docker Desktop en un Mac](../2026-11-27-docker-desktop-mac-disk-space/)
