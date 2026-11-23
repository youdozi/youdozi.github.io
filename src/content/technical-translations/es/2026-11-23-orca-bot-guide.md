---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2026-11-23-orca-bot-guide",
  "routeSlug": "2026-11-23-orca-bot-guide",
  "kind": "post",
  "title": "Cómo usar Orca Bot: crear un bot para el blog y revisar tareas y automatizaciones",
  "description": "Asigna una primera tarea a Orca Bot, revisa su memoria y trabajo, y configura tareas recurrentes.",
  "categories": [
    "util"
  ],
  "tags": [
    "orca",
    "ai-agent",
    "automation",
    "developer-tools"
  ],
  "sourcePath": "src/content/posts/en/2026-11-23-orca-bot-guide.md",
  "sourceSha256": "96033cbac131a6cad800f9782a2ad820fcfba2e710c8628bb440b0af0c898e02",
  "draftSha256": "8c1cdbaeca60a2ebd607aec3d3f44627f78c5174bf3ffa664214e045e1893255",
  "manifestPath": ".pipeline/technical-translations/batch-186/manifest.json",
  "manifestSha256": "dea1602a6cba39d65e40326263edd4383f93360e1169b9dd1cc36b7bda38be95",
  "publishedAt": "2026-11-23T05:30:14.030Z",
  "updatedAt": "2026-11-23T05:30:14.030Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 186,
    "approvedAt": "2026-11-23T05:30:14.030Z",
    "basis": "Owner explicitly requested publication of the Orca Bot guide in all eight supported languages; translations were self-reviewed, not independently or natively reviewed."
  }
}
---

**Si creas tu primer Orca Bot, antes de programar trabajo recurrente asígnale una tarea cuyo resultado puedas comprobar.** Por ejemplo, dale una nota técnica breve y pídele un título y un esquema para el blog. Si el resultado tiene el formato deseado, ajusta el papel del bot y añade tareas recurrentes. Esta guía sigue ese proceso con un bot que prepara borradores para el blog.

Un Orca Bot es una unidad de trabajo con nombre, propósito y memoria. Elige el equipo donde se ejecutará y un agente como Claude Code o Codex. Instala el agente e inicia sesión en ese equipo. El primer ejercicio se realiza dentro de Orca. Para llamar al bot desde Slack, GitHub o Linear, o ejecutarlo por eventos de esos servicios, añade las conexiones necesarias. [Primeros pasos con Orca Bots](https://orca.dev/docs/bots) · [Conectores de bots](https://orca.dev/docs/bots/connectors)

![Crea un bot y asígnale una primera tarea. Revisa el resultado y decide en Needs you si es necesario. Para el trabajo recurrente, establece una hora o un evento y revisa el historial de ejecución.](/assets/diagrams/technical/es-2026-11-23-orca-bot-guide.svg)

## Crear un bot y enviar la primera solicitud

En la barra lateral de Orca, en **Bots**, selecciona **+ → New bot → Start from scratch**. Elige un nombre y escribe su función en una frase en **Who it is and what it does**. El nombre del ejemplo es `Blog Draft` y su propósito es «convertir notas de desarrollo en borradores para un blog técnico». Comprueba el equipo y el agente bajo el nombre y selecciona **Create**. Si Bots no aparece en la barra lateral, comprueba **Settings → Bots → Enable bots**. [Crear un bot](https://orca.dev/docs/bots)

En el chat del bot, proporciona tanto el material de entrada como el formato deseado, como se muestra abajo. Esta nota es material ficticio para el ejercicio.

```text
Prepare a technical blog draft from the following practice note.

Note
- A Java service calls an external API.
- Tests checked a successful response and a 404 response.
- Production latency was not measured.

Suggest one title, one introductory paragraph, and three headings.
Do not add versions or performance figures absent from the note.
At the end, list anything that needs checking before writing the body.
Show the result in this chat.
```

Cuando recibas el resultado, comprueba que conserve el alcance de la afirmación: se comprobó la respuesta 404. Si añade una afirmación sobre versiones o rendimiento, elimínala o pide pruebas. El éxito de la primera solicitud consiste en obtener un título, una introducción y subtítulos basados en la nota, no un artículo listo para publicar.

## Separar las reglas para futuros chats del trabajo actual

| Dónde revisar | Contenido adecuado | Ejemplo para el bot del blog |
| --- | --- | --- |
| `SOUL.md` | Función y método de trabajo permanentes | Comprobar las fuentes en la documentación oficial y esperar una solicitud aparte para publicar |
| `MEMORY.md` | Datos y preferencias para futuros chats | Los lectores son desarrolladores Java y prefieren ejemplos ejecutables |
| Elemento de trabajo en **Home** | Progreso actual, resultados adjuntos y decisiones pendientes de aprobación | Un nuevo borrador espera revisión |

Los dos archivos Markdown están en la carpeta del bot. Puedes darle una regla permanente como «En futuros ejemplos, distingue los resultados ejecutados por ti de los resultados esperados» y comprobar si la sigue en trabajos posteriores. Para saber si terminó el trabajo actual, abre el elemento de trabajo del bot. Si hace falta una decisión, comprueba el objeto y las consecuencias de la pregunta en **Needs you** y responde. [Uso de Orca Bots](https://orca.dev/docs/bots) · [Memoria y acceso del bot](https://orca.dev/docs/bots/security)

Si le pides modificar código en un repositorio, el bot puede encargar el trabajo a un agente en un worktree Git separado. Abre el workspace del agente en la barra lateral para revisar archivos y pruebas; si se crea una PR, comprueba los cambios reales. [Agentes del bot](https://orca.dev/docs/bots) · [Guía de worktrees de Orca](../2026-11-12-orca-worktree-guide/)

## Definir el disparador y el destino del resultado recurrente

Si la primera tarea es satisfactoria, haz la siguiente solicitud en el chat del bot. Este ejemplo lee documentación pública y solo reúne ideas para artículos.

```text
Every Monday at 9:00 a.m. Korea time, select up to three technical
article ideas from official Spring Boot releases announced in the
previous seven days. For each candidate, include the announcement date,
official link, and a question to explore in an exercise.
If there were no announcements, say so.
Make the result available to me in Orca; do not publish it to the blog.
Also tell me which conversation the automation will leave its result in.
```

Cuando se cree la automatización, comprueba en el panel del bot la **zona horaria, el disparador y el destino del resultado**. Si debe reaccionar a un evento, como una nueva PR de GitHub, en lugar de una hora, comprueba primero que el conector esté conectado y admita ese evento. Si el equipo que ejecuta el bot está en reposo o sin conexión, no podrá trabajar inmediatamente a la hora prevista; por eso revisa el primer resultado en el historial de ejecución de la automatización. [Automatizaciones de Orca](https://orca.dev/docs/bots) · [Conectores de Orca](https://orca.dev/docs/bots/connectors)

En macOS con el CLI instalado, los siguientes comandos muestran los nombres de los bots y los eventos disponibles. Sustituye el nombre de la segunda línea por el de tu bot.

```sh
orca bot list
orca automations trigger-options --bot 'Blog Draft'
```

Los dos comandos de consulta se comprobaron con un bot existente y **Orca CLI 1.4.271** en el entorno de redacción. Para un bot sin conexión a GitHub, el resultado indicó que los eventos de GitHub no podían iniciarlo. El nombre y la nota del ejemplo son ficticios; no se creó ni ejecutó ningún bot nuevo ni automatización para este artículo. Consulta la guía CLI correspondiente a tu versión con `orca skills get orca-cli --reference bots`.
