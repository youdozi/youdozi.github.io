---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2026-11-20-ui-ux-design-agent-skills",
  "routeSlug": "2026-11-20-ui-ux-design-agent-skills",
  "kind": "post",
  "title": "Diseñar UI y UX con Claude Code y Codex — flujos, Figma y accesibilidad",
  "description": "Diseña flujos de usuario, sistemas de diseño en Figma, textos de interfaz y accesibilidad con Claude Code y Codex. Comprueba el teclado y el foco de un diálogo de cancelación con Playwright.",
  "categories": [
    "ai"
  ],
  "tags": [
    "claude-code",
    "codex",
    "agent-skills",
    "figma",
    "ui-ux",
    "accessibility",
    "playwright"
  ],
  "sourcePath": "src/content/posts/en/2026-11-20-ui-ux-design-agent-skills.md",
  "sourceSha256": "2fa2cdf9d087643f65deb61063a994cdd75549bf0b412379d831fa97c01906e2",
  "draftSha256": "fe6fa76ee4916ee3a7f17bbebfb44bf3a8424901e818c68a9281de9e52b254d6",
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

**Antes de dibujar la pantalla, define qué debe completar el usuario y en qué punto puede volver atrás.** En una pantalla de cancelación, la persona debe conocer de antemano las consecuencias y poder conservar o cancelar la reserva. Si defines el texto del diálogo, el foco inicial y adónde vuelve el foco al cerrarlo, tendrás los mismos criterios para implementar y verificar.

Este artículo profundiza en la etapa de UI y UX del [artículo anterior](/ko/posts/2026-11-19-website-building-agent-skills/) sobre el proceso completo de creación de sitios web. El 20 de noviembre de 2026 consulté las habilidades públicas de Claude Code y Codex y los recursos de Figma, Vercel y el W3C. A partir de ese material, seguiremos un flujo de cancelación desde la planificación hasta la prueba en el navegador.

## Elige la habilidad según el resultado que necesitas

| Resultado | Habilidad o método | Qué revisar |
| --- | --- | --- |
| Flujo de usuario y estados de pantalla | Instrucciones de proyecto `frontend-architecture-design` | Comprueba que estén definidos la entrada, la confirmación, la salida, el procesamiento, el éxito y el error. Si hay investigación con usuarios reales, distingue observaciones e hipótesis. |
| Prototipo para revisión | [Complemento Product Design](https://github.com/openai/plugins/tree/main/plugins/product-design) de Codex | Crea un diseño que permita revisar las transiciones entre estados. Comprueba que haya una vía para conservar la reserva y otra para confirmar la cancelación. |
| Dirección visual y código de interfaz | [`frontend-design`](https://github.com/anthropics/skills/tree/main/skills/frontend-design) de Claude Code | Define la jerarquía visual del título, la descripción y los botones de acción. Comprueba que el sentido y el orden se mantengan con títulos largos o pantallas estrechas. |
| Montaje de pantallas en Figma | [`figma-generate-design`](https://github.com/openai/plugins/tree/main/plugins/figma/skills/figma-generate-design) del complemento de Figma | Reutiliza instancias de botones y diálogos de la biblioteca existente y crea marcos para cada estado. Verifica que se conserven los vínculos con componentes y variables. |
| Biblioteca del sistema de diseño | [`figma-generate-library`](https://github.com/openai/plugins/tree/main/plugins/figma/skills/figma-generate-library) del complemento de Figma | Crea o actualiza las variables y la biblioteca de Figma a partir de los tokens de diseño y componentes del código. Contrasta las variantes y los vínculos de variables con los nombres del código. |
| Implementación del diseño aprobado en Figma | [`figma-design-to-code`](https://github.com/openai/plugins/tree/main/plugins/figma/skills/figma-design-to-code) del complemento de Figma | Lee el marco de referencia e impleméntalo con el código de interfaz existente. Tras comparar las pantallas, comprueba por separado el teclado y los estados de error. |
| Textos de interfaz | Instrucciones de UX del proyecto, como `cms-ux-writing` | Expresa con verbos el resultado de pulsar cada botón. Etiquetas como «Conservar reserva» y «Confirmar cancelación» aclaran las consecuencias. |
| Revisión de interfaz | [`web-design-guidelines`](https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines) de Vercel y pruebas de navegador | Busca posibles problemas de accesibilidad e interfaz en el código. Comprueba en el navegador el orden de navegación con el teclado, los cambios de foco y la distribución a distintos tamaños. |

Las dos instrucciones de proyecto son ejemplos de cómo convertir las reglas de diseño de pantallas y de redacción del equipo en habilidades reutilizables. No corresponden a una función integrada en un producto concreto. Si alguien va a revisar el flujo de la reserva, muéstrale primero el prototipo, incorpora sus comentarios a la tabla de estados y pasa esa tabla a implementación. Si el equipo ya aprobó los marcos de Figma y los componentes de código, puedes empezar por implementar y revisar la accesibilidad.

En Claude Code, `frontend-design` de Anthropic forma parte del paquete `example-skills` del mercado oficial. Para usar habilidades de Figma en Codex, necesitas las herramientas de Figma conectadas al complemento y permisos sobre el archivo. Al crear pantallas o componentes en Figma, aplica las instrucciones `figma-use` del complemento junto con la habilidad de creación correspondiente. Para leer un diseño que vas a implementar, proporciona el enlace al marco. Para crear un marco, proporciona un archivo editable y la biblioteca que se va a reutilizar. [Instalación de Anthropic](https://github.com/anthropics/skills#claude-code) · [Complemento de Figma para Codex](https://github.com/openai/plugins/tree/main/plugins/figma)

Si tienes una guía de marca, adjunta los logotipos, colores, tipografías y ejemplos de usos prohibidos. Si aplicas el `brand-guidelines` de Anthropic a tu marca solo por su nombre, podrías acabar usando los colores y la tipografía de Anthropic. Los recursos predeterminados de la habilidad corresponden a la marca Anthropic. [Código fuente de `brand-guidelines`](https://github.com/anthropics/skills/tree/main/skills/brand-guidelines)

## Cómo llevar el flujo de cancelación al diseño y al código

Antes de dibujar, recoge las acciones y sus efectos en una tabla. La siguiente tabla es un ejemplo de diseño. Para redactar las condiciones del reembolso o las comisiones de cancelación, consulta la política real del servicio.

| Acción del usuario o estado del servidor | Qué ocurre en pantalla |
| --- | --- |
| Selecciona «Abrir opciones de cancelación» en el detalle de la reserva | Se abre el diálogo y el foco pasa a «Conservar reserva». |
| «Conservar reserva» o Escape | Se cierra el diálogo y se conserva la reserva. El foco vuelve al botón que abrió el diálogo. |
| Selecciona «Confirmar cancelación» | En producción, se envía la solicitud y se indica que está en curso. Si se repite la misma solicitud, se evita procesarla más de una vez. |
| El servidor confirma el éxito | El estado pasa a «Reserva cancelada» y se anuncia el resultado. |
| El servidor confirma un error | Se conserva el estado de la reserva y se informa del motivo y de las acciones disponibles. |

En un diálogo que confirma una acción difícil de revertir, puede convenir poner el foco inicial en la opción menos destructiva. Al cerrar el diálogo, el foco suele volver al elemento que lo abrió. Si ese elemento desaparece, elige otro que permita continuar la tarea. [Patrón de diálogo modal del W3C](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/)

Pasa las acciones y los criterios de aceptación al agente encargado de implementar el flujo. Por ejemplo:

**Ejemplo de prompt** Diseña un diálogo de cancelación en el detalle de la reserva. Reutiliza el diálogo y los botones existentes. Pon el foco inicial en «Conservar reserva». Al cerrar con Escape, conserva la reserva y devuelve el foco a «Abrir opciones de cancelación». Tras enviar la solicitud, representa por separado los estados en curso, de éxito y de error. En el estado de error, indica cómo reintentar o pedir ayuda. Explica qué marco corresponde a cada estado para revisar las pantallas y la tabla antes de implementar.

## Ejercicio — comprobar el foco del diálogo y los dos resultados posibles

Comprueba en el navegador las dos primeras filas de la tabla y el cambio de pantalla al confirmar la cancelación. En el ejercicio, confirmar solo cambia el estado local de la página. La solicitud al servidor, la gestión de errores y la prevención de envíos duplicados requieren comprobaciones propias en producción.

![Abrir el diálogo desde la reserva y comprobar el foco inicial. Si se cierra con Escape o se conserva la reserva, revisar el estado y el foco del botón. Si se confirma la cancelación, comprobar que se muestre el estado de reserva cancelada.](/assets/diagrams/technical/es-2026-11-20-ui-ux-design-agent-skills.svg)

Prepara Node.js 22 y Chrome. En un directorio nuevo, ejecuta `npm init -y` y `npm install --save-dev playwright-core@1.64.1`. Guarda el código como `dialog-check.mjs` y ejecuta `node dialog-check.mjs`. Si Chrome no está en la ruta predeterminada, especifica `CHROME_PATH`. Las etiquetas del ejemplo ejecutable están en coreano. [Opciones de ejecución de Playwright](https://playwright.dev/docs/api/class-browsertype#browser-type-launch)

```js
import assert from 'node:assert/strict';
import { chromium } from 'playwright-core';

const browser = await chromium.launch({
  executablePath: process.env.CHROME_PATH
    ?? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
});

try {
  const page = await browser.newPage({ viewport: { width: 360, height: 700 } });
  page.setDefaultTimeout(2000);
  await page.setContent(`
    <button id="open">취소 옵션 열기</button>
    <p role="status">예약 유지 중</p>
    <dialog aria-labelledby="title" aria-describedby="description">
      <h2 id="title">예약을 취소할까요?</h2>
      <p id="description">확정하면 예약 상태가 취소됨으로 바뀝니다.</p>
      <form method="dialog">
        <button value="keep" autofocus>예약 유지</button>
        <button value="cancel">예약 취소 확정</button>
      </form>
    </dialog>
    <script>
      const trigger = document.querySelector('#open');
      const dialog = document.querySelector('dialog');
      const status = document.querySelector('[role="status"]');

      trigger.addEventListener('click', () => {
        dialog.returnValue = '';
        dialog.showModal();
      });
      dialog.addEventListener('close', () => {
        if (dialog.returnValue === 'cancel') {
          status.textContent = '예약 취소됨';
        }
      });
    </script>
  `);

  const trigger = page.getByRole('button', { name: '취소 옵션 열기' });
  const dialog = page.getByRole('dialog', { name: '예약을 취소할까요?' });
  const status = page.getByRole('status');
  const focused = () => page.evaluate(
    () => document.activeElement?.textContent?.trim(),
  );

  for (const close of ['Escape', '예약 유지']) {
    await trigger.focus();
    await page.keyboard.press('Enter');
    await dialog.waitFor({ state: 'visible' });
    assert.equal(await focused(), '예약 유지', '초기 포커스');
    await page.keyboard.press(close === 'Escape' ? 'Escape' : 'Enter');
    await dialog.waitFor({ state: 'hidden' });
    assert.equal(await status.textContent(), '예약 유지 중');
    assert.equal(await focused(), '취소 옵션 열기', '닫은 뒤 포커스');
    console.log(`PASS ${close}: 예약 유지 및 포커스 복귀`);
  }

  await page.keyboard.press('Enter');
  await dialog.waitFor({ state: 'visible' });
  assert.equal(await focused(), '예약 유지', '초기 포커스');
  await page.keyboard.press('Tab');
  assert.equal(await focused(), '예약 취소 확정', '확정 버튼 포커스');
  await page.keyboard.press('Enter');
  await page.waitForFunction(
    () => document.querySelector('[role="status"]').textContent === '예약 취소됨',
  );
  await dialog.waitFor({ state: 'hidden' });
  assert.equal(await focused(), '취소 옵션 열기', '확정 뒤 포커스');
  console.log('PASS 예약 취소 확정: 상태 변경 및 포커스 복귀');
} finally {
  await browser.close();
}
```

Esta es la salida de Chrome en macOS.

```text
PASS Escape: 예약 유지 및 포커스 복귀
PASS 예약 유지: 예약 유지 및 포커스 복귀
PASS 예약 취소 확정: 상태 변경 및 포커스 복귀
```

En la prueba de control, al mover `autofocus` a «Confirmar cancelación», falló la comprobación del foco inicial. El ejercicio verifica el nombre accesible del diálogo, la interacción con el teclado, el foco inicial, el foco al cerrar y el estado mostrado. En la interfaz real, comprueba también que el indicador de foco sea visible al navegar con el teclado, que los botones y las descripciones sean legibles con texto ampliado y que las tecnologías de asistencia puedan anunciar los mensajes de estado. [WCAG 2.2](https://www.w3.org/TR/WCAG22/)
