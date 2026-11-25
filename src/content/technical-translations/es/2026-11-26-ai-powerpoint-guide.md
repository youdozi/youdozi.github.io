---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2026-11-26-ai-powerpoint-guide",
  "routeSlug": "2026-11-26-ai-powerpoint-guide",
  "kind": "post",
  "title": "Cómo crear un PowerPoint con IA, del esquema a las diapositivas editables",
  "description": "Tres instrucciones para preparar el esquema, crear un PowerPoint editable y revisar cada diapositiva con el ejemplo de una prueba piloto de comprobaciones previas al despliegue.",
  "categories": [
    "ai"
  ],
  "tags": [
    "powerpoint",
    "pptx",
    "pptxgenjs",
    "ai-agent",
    "presentation"
  ],
  "sourcePath": "src/content/posts/en/2026-11-26-ai-powerpoint-guide.md",
  "sourceSha256": "859efd0ceeccfc1b46a9a9b1f8bbfb0235b50e0f4eee44c55f224a6a936c87cd",
  "draftSha256": "272441b4883380d853cf518868f1ebc79f7800d65c891a2925d9cc5ed82879ef",
  "manifestPath": ".pipeline/technical-translations/batch-193/manifest.json",
  "manifestSha256": "1602f24b3cdc88190ac8cbb05f9fa21d99c0a3957b2dc44d9e939c78944c8c28",
  "publishedAt": "2026-11-25T22:36:09.895Z",
  "updatedAt": "2026-11-25T22:36:09.895Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 197,
    "approvedAt": "2026-11-25T22:36:09.895Z",
    "basis": "The site owner explicitly requested publication of item 74 in Korean, English, Simplified Chinese, Japanese, German, French, Russian and Spanish."
  }
}
---

Cuando le encargues una presentación a una IA, empieza por explicar **quién va a escucharla y qué decisión debe tomar al final**. Con «hazme un PowerPoint bonito» tendrás enseguida una portada y un índice, pero puede que el asunto que motiva la reunión no aparezca hasta la última diapositiva. Define el título de cada diapositiva y en qué se apoya, convierte el esquema en un .pptx y ábrelo en la aplicación que usarás para presentar. Así será más fácil ver qué hay que corregir.

![Define el público y la decisión, revisa el esquema, crea diapositivas editables y compruébalas con las fuentes y en modo presentación.](/assets/diagrams/technical/es-2026-11-26-ai-powerpoint-guide.svg)

## Habilidades y herramientas para crear un PowerPoint

| Habilidad o herramienta | Cuándo usarla | Qué encargarle |
|---|---|---|
| **ai-guide-writing** | Para convertir instrucciones o material de formación en una presentación | Organizar los pasos de los ejercicios, las entradas de ejemplo, los resultados esperados y las comprobaciones. |
| **tech-blog-writing** | Para presentar documentación técnica o registros de operaciones | Seleccionar los argumentos y sus fundamentos, y repartir la explicación entre las diapositivas y las notas del orador. |
| **Habilidad pptx de Anthropic** | Para crear un PowerPoint o modificar una plantilla en Claude Code | Crear y editar archivos .pptx, extraer el contenido, revisar las miniaturas y comprobar la estructura del archivo. [Habilidad oficial](https://raw.githubusercontent.com/anthropics/skills/main/skills/pptx/SKILL.md) |
| **PptxGenJS** | Para generar informes semanales parecidos con agentes de programación como Codex | Regenerar un .pptx editable a partir de JavaScript y los datos de entrada. [Guía de inicio](https://github.com/gitbrent/PptxGenJS#-quick-start-guide) |

ai-guide-writing y tech-blog-writing son habilidades de redacción disponibles en el entorno utilizado para esta guía. Para crear el archivo PowerPoint puedes usar la habilidad pptx de Claude Code o PptxGenJS. Si quieres instalar las habilidades oficiales de Anthropic en Claude Code, ejecuta estas dos líneas en orden. Una vez instaladas, puedes pedir en la instrucción que se use la habilidad pptx. [Instrucciones de instalación de Anthropic](https://github.com/anthropics/skills#claude-code)

```text
/plugin marketplace add anthropics/skills
/plugin install document-skills@anthropic-agent-skills
```

Si ya trabajas en PowerPoint, **Copilot** puede preparar un borrador a partir de una instrucción o archivos de referencia. Si tienes una plantilla corporativa, ábrela antes de empezar. Las funciones disponibles dependen de la suscripción y de la configuración de tu organización. Con **Gemini en Presentaciones de Google** puedes generar diapositivas y descargarlas en formato .pptx. Según Google, la generación de una presentación completa requiere un plan compatible y está disponible en ordenadores, en inglés. [Crear una presentación con Copilot](https://support.microsoft.com/en-gb/powerpoint/copilot/create-a-new-presentation-with-copilot-in-powerpoint) · [Generar presentaciones con Gemini](https://support.google.com/docs/answer/17111393) · [Descargar un PPTX](https://support.google.com/a/users/answer/9310270)

## 1. Incluye en la instrucción del esquema la decisión que debe tomarse en la reunión

En este ejemplo ficticio propones a un equipo de desarrollo **una prueba piloto para automatizar las comprobaciones previas al despliegue**. Dispones de 7 minutos y buscas la aprobación de una prueba de 2 semanas en un solo equipo. Con estas condiciones, a la IA le resultará más fácil poner en primer plano la decisión de la reunión en lugar de hablar de las ventajas generales de automatizar procesos.

```text
Prepara el esquema de una charla de 7 minutos para responsables de desarrollo y personal de operaciones.
Propón automatizar las comprobaciones previas al despliegue. Usa 6 diapositivas.
En la reunión se decidirá si se aprueba una prueba piloto de 2 semanas en un equipo.

<Material de referencia>
- Antes del despliegue se comprueban manualmente las variables de entorno y el estado de las migraciones de la base de datos.
- La primera comprobación automática solo verifica si están presentes las variables de entorno
  obligatorias y si falta algún archivo de migración.
- Solo registra resultados de diagnóstico. No modifica la configuración ni la base de datos.
- Durante la prueba se registran el tiempo de comprobación, el número de omisiones detectadas y los falsos positivos.
- Todavía no se han medido el ahorro de tiempo ni la reducción de la tasa de fallos.
</Material de referencia>

Para cada diapositiva, indica un título que exprese su conclusión, hasta 3 puntos para mostrar
en pantalla, notas del orador y el punto del material que la respalda.
Pon la decisión solicitada en la primera y los criterios para evaluar la prueba en la última.
No inventes cifras ni des por designada a ninguna persona responsable.
```

Cuando recibas el esquema, **lee solo los títulos, en orden**. El primero debería expresar la decisión solicitada, los intermedios explicar el problema actual y el alcance de las comprobaciones, y el último indicar cómo se evaluarán los resultados. «Durante la prueba registraremos el tiempo de comprobación y los falsos positivos» orienta mejor al público que «Beneficios esperados de la automatización».

## 2. Pide un archivo .pptx editable

Si vas a modificar texto o gráficos más adelante, **especifica qué elementos necesitas editar**. Si toda la diapositiva es una sola imagen, puede que tengas que rehacerla solo para corregir una frase en PowerPoint.

```text
Crea un archivo PowerPoint en formato 16:9 llamado deployment-check-pilot.pptx
a partir del esquema aprobado que incluyo a continuación.

- Los títulos, el cuerpo del texto, las tablas y los diagramas de flujo deben poder editarse por separado en PowerPoint.
- Dedica cada diapositiva a una idea principal y pon las explicaciones largas en las notas del orador.
- En la diapositiva sobre la comprobación automática, usa tres formas para mostrar
  «Solicitud de despliegue → Comprobación de los dos puntos → Registro del resultado».
- Para los puntos sin cifras, utiliza tablas o diagramas de flujo en vez de gráficos estadísticos.
- Si se adjunta una plantilla corporativa, respeta la posición de los títulos, las fuentes y los colores.
- No presentes como confirmados beneficios o fechas de implantación que no consten en el material.

<Esquema aprobado>
Pega aquí el esquema de diapositivas revisado en el paso 1.
</Esquema aprobado>
```

Si utilizas un agente de programación para preparar el mismo tipo de informe cada semana, añade **«Usa PptxGenJS y entrega también build-deck.js y slides.json para que pueda volver a ejecutarlo».** La semana siguiente podrás cambiar solo los datos de entrada y regenerar la presentación con la misma distribución. Siempre que puedas, conserva las tablas de datos y los gráficos como objetos de PowerPoint y utiliza imágenes independientes solo para las ilustraciones. Así será más fácil editarlos. [Objetos de texto en PptxGenJS](https://gitbrent.github.io/PptxGenJS/docs/api-text.html)

## 3. Pide el número de diapositiva y la justificación de cada corrección

Entrega para la revisión el archivo terminado junto con **el esquema aprobado y el material de referencia original**. Si una diapositiva afirma «hemos reducido la tasa de fallos en los despliegues», la fuente permite distinguir entre un resultado medido y un indicador que aún queda por medir.

```text
Revisa el PPTX terminado y compáralo con el esquema aprobado y el material original.
Para cada problema, indica el número de diapositiva, el fundamento y un texto de reemplazo.

1. Busca cifras sin respaldo, fechas sin confirmar y efectos exagerados.
2. Si puedes renderizar las diapositivas, comprueba la sustitución de fuentes coreanas,
   los saltos de línea, el texto cortado y las formas superpuestas.
3. Señala las notas del orador que repitan el texto en pantalla.
4. Mirando solo la última diapositiva, indica qué decisión debe tomar el público.

Marca como «sin verificar» lo que no hayas podido comprobar directamente.
```

Abre el archivo en la versión de PowerPoint que usarás para exponer y comprueba **el modo de edición y el modo de presentación**. En el primero, intenta cambiar un número de una tabla y el texto de una forma. En el segundo, comprueba que los títulos y las frases principales se lean desde el fondo de la sala. Si exportaste el archivo desde Presentaciones de Google, vuelve a revisar las fuentes coreanas y los saltos de línea. Las instrucciones de este artículo ilustran un caso ficticio. Las capacidades de generación de cada producto se describen a partir de su documentación oficial.

Lectura relacionada · [10 habilidades recomendadas para Claude Code y Codex y cómo usarlas](../2026-11-18-claude-code-codex-skills-top-10/)
