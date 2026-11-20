---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2026-11-20-ponytail-skill-guide",
  "routeSlug": "2026-11-20-ponytail-skill-guide",
  "kind": "post",
  "title": "Cómo usar Ponytail — cambios pequeños y pruebas de regresión en Codex",
  "description": "Aprende a invocar Ponytail en Codex y Claude Code, distinguir Lite, Full y Ultra y reutilizar una función con una prueba de regresión en Node.js desde Codex CLI.",
  "categories": [
    "ai"
  ],
  "tags": [
    "ponytail",
    "codex",
    "claude-code",
    "agent-skills",
    "refactoring",
    "nodejs"
  ],
  "sourcePath": "src/content/posts/en/2026-11-20-ponytail-skill-guide.md",
  "sourceSha256": "7b1777565ade628aa9381193123b7b19f84ba4c91e57779cba53f40b8b19b6de",
  "draftSha256": "e57493b40a925d253cdf7394bc9b761af74d45c164520cd8ed92f8d4edabd83f",
  "manifestPath": ".pipeline/technical-translations/batch-172/manifest.json",
  "manifestSha256": "9fbed8219e1f64a1b7901da9450c566e1c2c7b0ed64840e56f60a1b726fd39df",
  "publishedAt": "2026-11-20T14:40:06.354Z",
  "updatedAt": "2026-11-20T14:40:06.354Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 172,
    "approvedAt": "2026-11-20T14:40:06.354Z",
    "basis": "User requested seven new language editions for each of four already published guides and approved parallel AI translation and verification. This records publication authorization."
  }
}
---

**Ponytail es una habilidad que ayuda a un agente de programación con IA a completar una tarea reutilizando el código existente.** Si la etiqueta de existencias muestra `1 items` cuando hay un solo artículo, comprueba primero si el proyecto ya tiene una función para el singular y el plural. Reutilízala para corregir la etiqueta y verifica que las cantidades 0 y 2 se sigan mostrando como antes.

## Primeros pasos en Codex y Claude Code

Si ya tienes la habilidad independiente de Ponytail en Codex, escribe `$ponytail-help` en el chat para consultar sus nombres y modos. Después de `$ponytail full`, explica qué comportamiento debe cambiar, qué condiciones hay que conservar y qué comando debe ejecutar para comprobarlo. El ejercicio usa la habilidad independiente instalada en `~/.agents/skills/ponytail/SKILL.md`. En esta configuración el modo se aplica como preferencia de trabajo en la conversación actual. Puedes desactivarlo con `$ponytail off`. [Documentación de habilidades de Codex](https://learn.chatgpt.com/docs/build-skills)

El proyecto Ponytail también distribuye un complemento. Para Codex CLI, ejecuta los dos comandos siguientes en la terminal. Después, abre Codex y revisa qué ejecuta cada uno de los dos hooks en `/hooks`. Si quieres usarlos, márcalos como confiables tras revisarlos e inicia una conversación nueva. El entorno que ejecuta los hooks necesita `node` en `PATH`. [Guía de instalación de Ponytail](https://github.com/DietrichGebert/ponytail/blob/main/INSTALL.md#codex)

```bash
codex plugin marketplace add DietrichGebert/ponytail
codex plugin add ponytail@ponytail
```

En Claude Code, introduce los dos comandos siguientes de uno en uno y luego selecciona el modo con `/ponytail full`. El complemento incluye el comando de revisión `/ponytail-review`. En el complemento de Codex, la habilidad de revisión aparece con el nombre del complemento como prefijo, por ejemplo, `$ponytail:ponytail-review`. La instalación y el comportamiento de los hooks de ambos complementos se describen según la documentación pública. [Guía de instalación para Claude Code](https://github.com/DietrichGebert/ponytail/blob/main/INSTALL.md#claude-code) · [Comandos de Ponytail](https://github.com/DietrichGebert/ponytail#commands)

```text
/plugin marketplace add DietrichGebert/ponytail
/plugin install ponytail@ponytail
```

## Cuándo usar Lite, Full o Ultra

Con la habilidad independiente de Codex, escribir solo `$ponytail` activa Full, el modo predeterminado.

| Invocación | Cómo trabaja | Ejemplo |
| --- | --- | --- |
| `$ponytail lite` | Completa la tarea y señala brevemente un enfoque más pequeño si aporta una ventaja concreta. | Cambiar un texto de interfaz que el equipo ya acordó. |
| `$ponytail full` | Revisa los puntos de llamada y las pruebas existentes. Completa el comportamiento solicitado con el cambio más pequeño posible e informa de las comprobaciones y los riesgos pendientes. | Corregir el singular en una etiqueta y verificar las entradas existentes. |
| `$ponytail ultra` | Señala las ampliaciones innecesarias de alcance mientras realiza el trabajo solicitado. | Corregir un error de una pantalla y valorar por separado si hace falta rehacer toda la interfaz compartida. |

Para mantener acotado el cambio, especifica **qué debe cambiar, qué debe mantenerse y cómo comprobarlo**. Incluye las condiciones de las que dependen los llamadores, como los controles de autorización, la validación de entradas y la protección de datos. La habilidad orienta el trabajo del agente. La configuración de permisos determina dónde puede escribir archivos y qué comandos puede ejecutar.

## Ejercicio — mostrar `1 item` cuando queda un artículo

El ejercicio se ejecutó en un repositorio de práctica vacío con Node.js 22.17.0 y Codex CLI 0.169.0. Para reproducir el estado inicial, usa en `stockLabel` la línea de retorno de abajo. La primera prueba de `stock.test.mjs` ya existía. La segunda se añadió para este cambio.

```javascript
return `${count} items`;
```

**Ejemplo de prompt** `$ponytail full` Corrige el caso stockLabel(1), que devuelve 1 items. Conserva items para 0 y 2. Reutiliza la función formatCount existente, añade una prueba de regresión para stockLabel y ejecuta `node --test`. No hagas cambios fuera de este repositorio de práctica ni crees un commit.

![Tras recibir la solicitud, revisar stockLabel y formatCount. Reutilizar formatCount, comprobar las etiquetas para 0, 1 y 2 artículos y registrar el resultado.](/assets/diagrams/technical/es-2026-11-20-ponytail-skill-guide.svg)

En `stock.mjs` solo cambió la expresión de retorno de `stockLabel`. Ahora llama a `formatCount`, que ya gestiona el singular y el plural.

```javascript
export function formatCount(count, noun) {
  return `${count} ${count === 1 ? noun : noun + 's'}`;
}

export function stockLabel(count) {
  return formatCount(count, 'item');
}
```

En `stock.test.mjs`, comprueba las etiquetas para las cantidades 0, 1 y 2. Pon los dos archivos en el mismo directorio y ejecuta `node --test`.

```javascript
import assert from 'node:assert/strict';
import test from 'node:test';
import { formatCount, stockLabel } from './stock.mjs';

test('formatCount handles singular and plural', () => {
  assert.equal(formatCount(1, 'item'), '1 item');
  assert.equal(formatCount(2, 'item'), '2 items');
});

test('stockLabel handles zero, one, and two items', () => {
  assert.equal(stockLabel(0), '0 items');
  assert.equal(stockLabel(1), '1 item');
  assert.equal(stockLabel(2), '2 items');
});
```

Al ejecutarla con el código original, la nueva prueba falló con la cantidad 1. Esperaba `1 item` y recibió `1 items`. Tras la corrección se obtuvo esta salida.

```text
ok 1 - formatCount handles singular and plural
ok 2 - stockLabel handles zero, one, and two items
# tests 2
# pass 2
# fail 0
```

El ejercicio cubre dos pruebas y cambios en dos archivos. Cuando el agente termine, compara el `git diff` real y los resultados de las pruebas para comprobar que reutilizó la función existente y respetó el alcance de la tarea.

## Define el alcance de la revisión cuando termines el cambio

Si también están instaladas las habilidades independientes complementarias, puedes usar los comandos siguientes. Especifica qué parte del código debe revisarse para facilitar la comprobación de los hallazgos. [Comandos de Ponytail](https://github.com/DietrichGebert/ponytail#commands)

| Invocación | Cuándo usarla |
| --- | --- |
| `$ponytail-review` | Revisa el diff actual y el código relacionado. Úsala antes de abrir un PR para comprobar los puntos de llamada y detectar pruebas de regresión que falten. |
| `$ponytail-audit` | Inspecciona todo el repositorio en modo de solo lectura y prioriza los problemas que encuentra. |
| `$ponytail-debt` | Recopila los comentarios `shortcut:` existentes y los antiguos comentarios `ponytail:` para revisarlos. |
| `$ponytail-gain` | Muestra el informe de rendimiento comparativo publicado por el proyecto. Para medir el ahorro de tiempo o de coste en tu propio repositorio, debes hacer una comparación aparte. |
| `$ponytail-help` | Muestra los modos y las formas de invocar las habilidades instaladas. |
