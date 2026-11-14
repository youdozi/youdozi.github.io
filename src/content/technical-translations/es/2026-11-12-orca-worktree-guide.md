---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2026-11-12-orca-worktree-guide",
  "routeSlug": "2026-11-12-orca-worktree-guide",
  "kind": "post",
  "title": "Guía de Orca: worktrees, agentes, pruebas y revisión",
  "description": "Usa proyectos y worktrees de Orca para aislar una tarea de código, comprobar pruebas y navegador, y revisar el diff antes del commit.",
  "categories": [
    "util"
  ],
  "tags": [
    "orca",
    "ai-agent",
    "git-worktree",
    "testing",
    "developer-tools"
  ],
  "sourcePath": "src/content/posts/en/2026-11-12-orca-worktree-guide.md",
  "sourceSha256": "4214532491f859b28104e614442c9bc3c33ecc9a00a62567a96d927bc90cffb6",
  "draftSha256": "58b102d4b2241e1e4532bb1aa8cd585be2b0df399c4aaabeca7458bdb4504d8c",
  "manifestPath": ".pipeline/technical-translations/batch-156/manifest.json",
  "manifestSha256": "ed48dc20825daff8725d8eba3418b1ad885276b52c9752ba958f7a1705b24430",
  "publishedAt": "2026-11-14T15:16:43.783Z",
  "updatedAt": "2026-11-14T15:16:43.783Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 158,
    "approvedAt": "2026-11-14T15:16:43.783Z",
    "basis": "User requested all 63 language editions and instructed completed PRs to be merged; AI translation and independent AI review were performed, with no claim of human text review."
  }
}
---

**Orca es un entorno de desarrollo que reúne espacios Git, agentes de código, terminales, navegador y revisión de cambios.** Separar cada tarea en un worktree permite trabajar en distintas ramas y carpetas. Comprueba que terminó con la ruta real, el resultado de las pruebas y el diff frente a la rama base, no solo con la respuesta del agente.

El tema es la [aplicación oficial Orca](https://www.onorca.dev/) de Stably AI. Esta guía usa **Orca 1.4.256** instalado en macOS, la guía CLI incluida, Node.js 24.13.0, Python 3 y Git. Se verificaron la consulta del espacio actual, las pruebas del ejemplo en una terminal Orca, la detección de puertos y la presentación en el navegador integrado. No se creó ni fusionó un worktree ni se inició una tarea nueva de un agente de IA; los prompts y comandos de creación son ejercicios para el lector.

## ¿En qué se diferencian un proyecto y un worktree?

Abre un repositorio Git local con **Add Repo** en la [guía oficial de primera sesión](https://www.onorca.dev/docs/first-session). Aunque Orca gestione el proyecto, el código y los commits permanecen en el repositorio Git. Prepara por separado las condiciones de uso y autenticación del modelo/proveedor.

| Elemento | Función en este ejercicio |
| --- | --- |
| Proyecto | Agrupa el repositorio Git del ejemplo y los espacios de trabajo |
| Worktree | Carpeta con una rama concreta y su vista de trabajo |
| Agente | Propone leer y cambiar archivos y ejecutar comandos dentro del alcance |
| Terminal | Ejecuta pruebas y servidor de desarrollo en la carpeta de la tarea |
| Navegador integrado | Comprueba la página real y los valores límite |

La [documentación de worktrees de Orca](https://www.onorca.dev/docs/model/worktrees) y la [guía CLI](https://www.onorca.dev/docs/cli/overview) explican la relación entre archivos, ramas y vistas de trabajo. No supongas que cambiar de worktree en la interfaz cambia automáticamente el directorio de un shell ya abierto. El primer paso es **comprobar la ruta y rama en la terminal que ejecutará los comandos**.

## Crear un ejemplo pequeño y comprobar el estado inicial

![Abre el repositorio Git del ejemplo, crea un worktree y comprueba su ruta y rama. Pide al agente modificar un archivo y revisa pruebas, servidor y navegador en el mismo worktree. Compara el diff y las pruebas originales con main: haz el commit si cumple los requisitos o pide una corrección.](/assets/diagrams/technical/es-2026-11-12-orca-worktree-guide.svg)

Usa una política de envío ilustrativa: **los pedidos de 50 000 won o más tienen envío gratis; los inferiores cuestan 3 000 won**, y solo se aceptan enteros seguros no negativos. No es la política real de un servicio. Guarda estos cuatro archivos en una nueva carpeta `orca-shipping-example`. No se necesitan paquetes npm externos.

### `package.json`

```json
{
  "name": "orca-shipping-example",
  "private": true,
  "type": "module",
  "engines": { "node": ">=24" },
  "scripts": { "test": "node --test shipping.test.mjs" }
}
```

### `shipping.mjs`

```javascript
export function shippingFee(orderTotal) {
  return orderTotal > 50_000 ? 0 : 3000;
}
```

### `shipping.test.mjs`

```javascript
import test from 'node:test';
import assert from 'node:assert/strict';
import { shippingFee } from './shipping.mjs';

for (const [total, expected] of [[0, 3000], [49_999, 3000], [50_000, 0], [50_001, 0]]) {
  test(`shippingFee(${total}) = ${expected}`, () => {
    assert.equal(shippingFee(total), expected);
  });
}
for (const [label, total] of [
  ['negative', -1],
  ['fraction', 50_000.5],
  ['string', '50000'],
  ['NaN', Number.NaN],
  ['Infinity', Number.POSITIVE_INFINITY],
  ['unsafe integer', Number.MAX_SAFE_INTEGER + 1],
]) {
  test(`rejects ${label}`, () => {
    assert.throws(() => shippingFee(total), RangeError);
  });
}
```

### `index.html`

```html
<!doctype html>
<html lang="ko">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Orca 배송비 예제</title>
<h1>배송비 경계값 확인</h1>
<pre id="result"></pre>
<script type="module">
  import { shippingFee } from './shipping.mjs';
  const totals = [49_999, 50_000, 50_001];
  document.querySelector('#result').textContent = totals
    .map(total => `${total}원 → 배송비 ${shippingFee(total)}원`)
    .join('\n');
</script>
</html>
```

Ejecuta lo siguiente en la carpeta del ejemplo con el autor de Git configurado.

```sh
git init -b main
git add package.json shipping.mjs shipping.test.mjs index.html
git commit -m "Add shipping exercise"
npm test
```

El código inicial gestiona mal el límite `50,000` (cincuenta mil won) y no rechaza entradas inválidas. Una ejecución real confirmó **3 pruebas correctas y 7 fallidas de 10**. Registrar este estado como commit base permite comparar más tarde si también cambiaron las pruebas o la configuración.

## Pedir un cambio a un agente en un worktree

Abre el repositorio de ejemplo con **Add Repo** en Orca y comprueba la CLI en una terminal conectada a él. Si la CLI no está disponible, instálala mediante Settings → General → Orca CLI como indica la [guía oficial CLI](https://www.onorca.dev/docs/cli/overview). Estos comandos suponen el ejecutable `orca` de macOS.

```sh
orca skills get orca-cli
orca worktree current --json
```

Al separar el trabajo, crea un nuevo worktree desde `main` del proyecto actual.

```sh
orca worktree create --name shipping-fee-fix \
  --parent-worktree active --base-branch main \
  --setup skip --activate --json
```

`--parent-worktree active` registra la relación de trabajo en Orca; `--base-branch main` define el punto de partida Git. Son ajustes distintos. El ejemplo omite la preparación porque no necesita dependencias externas. En un proyecto real sigue la política de preparación correspondiente. Como este comando no tiene `--agent`, no solicita una tarea al agente.

Abre una terminal en el nuevo espacio y compruébala. Distingue el shell que ejecutó el comando original del shell del nuevo worktree.

```sh
git rev-parse --show-toplevel
git branch --show-current
orca worktree current --json
```

El nombre de la rama puede variar según los prefijos de Orca y otras opciones. Tras comprobar que el worktree del JSON y la ruta y rama Git son los deseados, abre la pestaña del agente preparado y envía el prompt siguiente. Los agentes disponibles y la ejecución por chat/CLI dependen de la configuración del entorno.

```text
Primero comprueba el directorio y rama actuales y lee shipping.mjs y shipping.test.mjs.
Corrige la política ilustrativa de envío según este contrato:

- Pedidos de 50 000 won o más tienen envío 0; los inferiores cuestan 3 000 won.
- Acepta solo enteros seguros no negativos como total; cualquier otra entrada produce RangeError.
- Modifica solo shipping.mjs; no cambies pruebas, package.json ni index.html.
- No instales dependencias, accedas a redes externas, hagas commits, push ni crees un PR.

Comunica el resultado real de ejecutar npm test y la razón del cambio.
Indica explícitamente las comprobaciones que no hayas podido ejecutar.
```

Aunque Orca agrupe las tareas, los permisos reales de herramientas dependen del agente y del entorno de ejecución. Las restricciones del prompt por sí solas no fuerzan el límite de acceso. La guía no presupone nombres concretos de botones de permisos ni un comportamiento idéntico de todos los proveedores.

## Comprobar pruebas y navegador en el mismo espacio

Ejecuta `npm test` en la [terminal integrada](https://www.onorca.dev/docs/terminal). Para automatización puedes crear una terminal de prueba en el worktree actual:

```sh
orca terminal create --title "tests" --command "npm test" --json
```

En automatización, usa el handle devuelto como destino de comandos posteriores. `terminal read --screen` lee la pantalla actual; `terminal read` sin opciones lee la salida acumulada. Aceptar una entrada y que el comando o la tarea del agente se inicie realmente son eventos distintos. Esta guía confirmó **las 10 pruebas correctas** y solo el archivo `shipping.mjs` modificado en la terminal de prueba creada para ello. Se comprobó insertando directamente la solución de referencia; no es un registro de ejecución de una tarea de IA.

Para comprobar el navegador, inicia el servidor en una terminal del mismo worktree. Se supone que el puerto 4877 está libre.

```sh
python3 -m http.server 4877 --bind 127.0.0.1
```

Comprueba el puerto desde otra terminal.

```sh
orca ports --json
orca tab create --url http://127.0.0.1:4877/ --json
```

Si el servidor utiliza otro puerto, usa el indicado en la consulta y su dirección correspondiente. No todo lo mostrado por `orca ports` es una página HTTP. Conéctate según la [guía del navegador integrado](https://www.onorca.dev/docs/browser/overview) y comprueba estos valores en la página:

```text
49999원 → 배송비 3000원
50000원 → 배송비 0원
50001원 → 배송비 0원
```

Las tres líneas anteriores se comprobaron en el navegador real de Orca con el ejemplo y la solución de referencia. Al terminar, detén el servidor con `Ctrl+C` en su terminal. No cierres en bloque terminales ajenas por haber terminado la tarea; distingue sus procesos y pestañas.

## Revisar el diff y registrar solo el archivo modificado

Comprueba la referencia base y los archivos en el [visor de diff de Orca](https://www.onorca.dev/docs/review/diff-viewer). Los [comentarios en líneas modificadas](https://www.onorca.dev/docs/review/annotate-ai-diff) permiten señalar una ubicación al agente. Por ejemplo: «50 000 won también debe ser gratis. Mantén las expectativas del test y revisa el operador de comparación».

Compara también con `main` en la terminal.

```sh
git status --short
git diff main --name-only
git diff main -- shipping.mjs
git diff --exit-code main -- shipping.test.mjs package.json index.html
npm test
```

En esta tarea solo debe cambiar `shipping.mjs`. Si cambiaron pruebas, configuración o página, determina primero por qué. Un diff ordinario puede omitir archivos nuevos, así que revisa también el estado Git. Ejecuta las comprobaciones que el agente no pudo hacer; no sustituyas un resultado correcto por una respuesta de «terminado».

Esta es la solución de referencia verificada directamente. Compárala con el código del agente después del ejercicio. Para ejecutarla, coloca el código en `shipping.mjs` en la raíz.

### `reference/shipping.mjs`

```javascript
export function shippingFee(orderTotal) {
  if (!Number.isSafeInteger(orderTotal) || orderTotal < 0) {
    throw new RangeError('orderTotal must be a nonnegative safe integer');
  }
  return orderTotal >= 50_000 ? 0 : 3000;
}
```

Con la referencia pasaron las mismas 10 pruebas y se conservaron los archivos originales de pruebas, configuración y HTML. Tras comprobar las condiciones, haz commit solo de los archivos necesarios en la rama.

```sh
git add shipping.mjs
git commit -m "Fix free-shipping boundary and input validation"
```

El commit y la fusión a la rama base son pasos separados. Si otra tarea cambia `main`, vuelve a comprobar diff y pruebas antes de fusionar. Un worktree separa espacios de código, pero no es un sandbox de seguridad. Los worktrees pueden compartir recursos como bases de datos, puertos, cuentas y secretos.

Al principio practicar este flujo con una sola tarea facilita encontrar problemas frente a añadir de inmediato varios agentes. Amplía el trabajo paralelo cuando los límites de archivos o funciones y los criterios de finalización estén definidos.
