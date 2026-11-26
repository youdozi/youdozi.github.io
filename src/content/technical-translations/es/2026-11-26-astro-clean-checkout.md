---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2026-11-26-astro-clean-checkout",
  "routeSlug": "2026-11-26-astro-clean-checkout",
  "kind": "post",
  "title": "Por qué la comprobación de Astro fallaba solo en una copia de trabajo limpia",
  "description": "Un SVG ausente detuvo la preparación de un borrador de noticias. Repetir la comprobación de Astro después de generar los archivos permitió aislar la causa.",
  "categories": [
    "blog",
    "automation"
  ],
  "tags": [
    "astro",
    "github-actions",
    "ci",
    "svg"
  ],
  "sourcePath": "src/content/posts/en/2026-11-26-astro-clean-checkout.md",
  "sourceSha256": "7dba5eae5f82355acd4550b2c1c0881e24e8e8c82d7597021db67ee13393285f",
  "draftSha256": "206b3757f13352879eaf984fc7f395dbdf7b0720cc378b19bc28389581aad9eb",
  "manifestPath": ".pipeline/technical-translations/batch-2088/manifest.json",
  "manifestSha256": "b7b442fb34494b22edfb8c5f8e0eafaed5565c392112b7fb1119018b9da5f7a9",
  "publishedAt": "2026-11-26T04:45:51.988Z",
  "updatedAt": "2026-11-26T04:45:51.988Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 200,
    "approvedAt": "2026-11-26T04:45:51.988Z",
    "basis": "The owner explicitly requested publication of the Astro CI retrospective in all supported blog languages (item 88)."
  }
}
---

El flujo que prepara los borradores de noticias se detuvo con `ENOENT`. De los 4 fallos que investigamos, 3 se produjeron cuando Astro intentó leer las dimensiones de las imágenes de artículos existentes. Los SVG a los que apuntaban esos artículos todavía no se habían generado en la copia de trabajo limpia. Si quedaban archivos de una compilación anterior, la misma comprobación podía pasar en local. [Fallo al comprobar el borrador](https://github.com/youdozi/youdozi.github.io/actions/runs/45548722494)

## Ejecutar la misma comprobación antes y después de generar los SVG

Recuperamos el commit que fallaba en un directorio aparte. Allí, `npm run check` terminó con el código de salida 1. Tras preparar los recursos públicos con `node scripts/prepare-public.mjs` en ese mismo directorio, la comprobación terminó con el código 0. La compilación también prepara los recursos, pero la CI ejecutaba primero la comprobación.

![Partir de una copia de trabajo limpia, generar los SVG, leer sus dimensiones con Astro y compilar el sitio.](/assets/diagrams/technical/es-2026-11-26-astro-clean-checkout.svg)

Para reproducir la secuencia de la CI, utiliza Node.js 24 y Python 3.11 en la raíz del repositorio. Instala las dependencias con `npm ci` y ejecuta los comandos siguientes. Cada paso debe completarse con éxito para que empiece el siguiente. [Corrección en el PR](https://github.com/youdozi/youdozi.github.io/pull/198) · [Resultado de la compilación del PR](https://github.com/youdozi/youdozi.github.io/actions/runs/45734945701)

```sh
node scripts/prepare-public.mjs &&
  npm run check &&
  npm run build
```

## Otro fallo durante la generación

En otra ejecución, Gemini devolvió HTTP 503 durante la generación. Con la corrección se usa el mismo modelo y se espera 1 segundo antes del primer reintento y 2 segundos antes del segundo. Todas las solicitudes de una ejecución comparten esos dos reintentos. [Fallo en la etapa de generación](https://github.com/youdozi/youdozi.github.io/actions/runs/45098322259)

En una prueba en seco en coreano e inglés con un artículo oficial de Spring, solo simulamos las respuestas del modelo durante la generación y la revisión. Contrastamos las citas con el artículo original, comprobamos los enlaces y validamos el contenido con los esquemas de Python y Astro. La prueba no escribió nada en los borradores ni en la cola. La disponibilidad real de Gemini quedó sin comprobar.

Cuando una comprobación pasa en local, conviene localizar el primer comando que lee el archivo ausente en una copia limpia. Comparar su posición con la del paso que genera el archivo puede explicar por qué se completa toda la compilación aunque falle una comprobación anterior.
