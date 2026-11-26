---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2026-11-26-news-dry-run-guide",
  "routeSlug": "2026-11-26-news-dry-run-guide",
  "kind": "post",
  "title": "Cómo validar borradores de noticias en GitHub Actions sin publicarlos",
  "description": "Comprueba que el borrador supera la validación y compara los manuscritos, la cola de publicación y los archivos de estado antes y después de la ejecución.",
  "categories": [
    "blog"
  ],
  "tags": [
    "github-actions",
    "ci",
    "dry-run"
  ],
  "sourcePath": "src/content/posts/en/2026-11-26-news-dry-run-guide.md",
  "sourceSha256": "bbd2b23eadacc9df77585d34bf7ba6243a6a849fbbfcba51c6f2272b35553659",
  "draftSha256": "9c93480cf20f5be56dd70590959ec79bdf7d1b8e5020932398dd12e93c62b2ff",
  "manifestPath": ".pipeline/technical-translations/batch-2092/manifest.json",
  "manifestSha256": "9a982e5784cecb3a4cc8afc502eaa7a3dabfd32dbeb039f0577cad485ee5cb2d",
  "publishedAt": "2026-11-26T07:02:16.794Z",
  "updatedAt": "2026-11-26T07:02:16.794Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 201,
    "approvedAt": "2026-11-26T07:02:16.794Z",
    "basis": "The owner authorized publication of the news draft dry-run guide in all eight blog languages in item 92."
  }
}
---

Un borrador puede cumplir el esquema y aun así dejar una entrada en la cola de publicación. La prueba debe responder a dos preguntas. ¿Devuelve el programa el código de salida previsto para esa entrada? ¿Coinciden los archivos de manuscritos, cola y estado con los que había antes de la ejecución?

## Probar una vista previa válida y los casos de error

Ejecuta este comando desde la raíz del repositorio con Python 3. Las dos pruebas usan directorios temporales y datos preparados para la fuente de noticias, la generación del borrador y la comprobación de enlaces. Pueden ejecutarse sin red ni clave de API del modelo.

```sh
PYTHONPATH=scripts python3 -B -m unittest \
  test_bilingual_digest.PublicationTests.test_preview_validates_without_writing_content_or_state \
  test_bilingual_digest.PublicationTests.test_ai_or_link_failures_do_not_write
```

![La vista previa válida termina correctamente y un error de la IA o de un enlace provoca un fallo. En ambos casos se comprueba si se crearon los directorios de manuscritos y de estado.](/assets/diagrams/technical/es-2026-11-26-news-dry-run-guide.svg)

La primera prueba pasa `--dry-run --force` y comprueba el código de salida 0 y el valor `generated=false`. La segunda pasa `--check-links`, simula por separado un error de la IA y un error de enlace, y comprueba el código de salida 1 en cada caso. Ambas pruebas fallan si aparece `src` o `.pipeline` bajo la raíz temporal. El comando anterior devolvió `Ran 2 tests` y `OK`.

## Qué se contrastó con el artículo de Spring en local

En una ejecución local independiente se usó un [artículo del equipo de Spring AI](https://spring.io/blog/2026/11/24/spring-ai-tool-call-confirmation-park-resume). El entorno de prueba aislado pasó `--dry-run --force --max-items 1 --check-links` e inyectó respuestas preparadas únicamente para la generación y la revisión con Gemini. Ejecutar la CLI con esos argumentos por sí solos no inyecta las respuestas.

La solicitud al original devolvió HTTP 200. Se comprobaron los enlaces, se cotejaron con el texto publicado las 4 citas de los borradores en coreano e inglés y se validó el contenido con los esquemas de Python y Astro. La salida fue `generated=false`. Otra comparación confirmó que los 3.333 archivos de manuscritos, cola y estado conservaban tanto sus rutas como su contenido. La disponibilidad real de Gemini y la calidad de sus respuestas quedaron sin evaluar. [Registro de la ejecución local](https://github.com/youdozi/youdozi.github.io/pull/198)

## Limitar los permisos de la tarea de validación de una PR

En la ejecución habitual de CI de esa PR se superó la comprobación obligatoria `build / build` y se omitió la tarea `deploy`. El registro de la ejecución local recoge el cotejo con el artículo de Spring. [Resultados de la PR](https://github.com/youdozi/youdozi.github.io/actions/runs/45734945701) · [Por qué fallaba la comprobación de Astro con una copia de trabajo limpia (en coreano)](https://youdozi.github.io/ko/posts/2026-11-26-astro-clean-checkout/)

Si añades una tarea de validación independiente, concede solo `contents: read` para obtener el código y excluye las credenciales de publicación. Incluso con un token de solo lectura para el repositorio, el proceso puede modificar archivos locales. Por eso conviene comparar los manuscritos, la cola y los archivos de estado antes y después de la ejecución. [Documentación de GitHub sobre el token de la tarea](https://docs.github.com/en/actions/concepts/security/github_token)
