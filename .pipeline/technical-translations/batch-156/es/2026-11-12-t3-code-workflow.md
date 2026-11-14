---
{
  "state": "draft",
  "language": "es",
  "translationKey": "2026-11-12-t3-code-workflow",
  "title": "Guía de T3 Code: de un cambio pequeño a la revisión de diff y pruebas",
  "description": "Inicia una tarea de código con T3 Code v0.1.9, limita permisos y comprueba el diff y las pruebas sin confundir la solución de referencia con una salida de IA.",
  "sourcePath": "src/content/posts/en/2026-11-12-t3-code-workflow.md",
  "sourceSha256": "da83ebd4864d4a4b015af522789e363b4a8695b6424368db9bfd1652f7761089"
}
---

**T3 Code conecta agentes de programación instalados en tu equipo con una interfaz de proyectos, conversaciones, permisos y archivos modificados.** Al delegar código, importan más un alcance pequeño y criterios de finalización verificables que una petición larga. Esta guía sigue la corrección de un analizador numérico de `Retry-After` desde la petición hasta la comprobación del diff y las pruebas.

El tema es el [proyecto oficial T3 Code](https://github.com/pingdotgg/t3code/tree/v0.1.9). Es distinto de T3 Stack, que crea aplicaciones web con `create-t3-app`. El README oficial describe la conexión de proveedores existentes como Codex, Claude Code y Cursor. Instalar T3 Code y preparar la autenticación y las condiciones de suscripción/API del proveedor son pasos separados.

La referencia es la [versión v0.1.9](https://github.com/pingdotgg/t3code/releases/tag/v0.1.9), consultada el 12 de noviembre de 2026. El ejemplo se comprobó en macOS con Node.js 24.13.0 y Git; también se comprobaron la ayuda de la CLI de T3 Code y el arranque del servidor local. **No se envió ninguna tarea de IA a un proveedor.** La solución de referencia se probó directamente; no es una salida real generada por T3 Code ni una medición del rendimiento de un modelo.

## ¿Cómo se reparten las responsabilidades T3 Code y el proveedor?

T3 Code muestra el proyecto y el hilo de trabajo, la selección del proveedor, las solicitudes de permiso y los cambios. El agente conectado lee y modifica archivos o ejecuta comandos. Ver una llamada a una herramienta no significa que las pruebas se hayan ejecutado y superado automáticamente: comprueba el comando y el resultado.

Según la [guía de instalación](https://github.com/pingdotgg/t3code/blob/v0.1.9/docs/user/install.md), instala el proveedor y completa la autenticación en **el equipo donde se ejecuta el servidor T3 Code**. El ejercicio empieza seleccionando un proveedor ya preparado. No es necesario pegar credenciales ni claves API en el prompt.

## Preparar un proyecto Git pequeño y pruebas que fallan

![Guarda el código inicial y las pruebas fijas en Git y comprueba el fallo. En T3 Code elige proyecto, proveedor y permisos Supervised, y envía una petición acotada. Aprueba cambios y comandos del agente; compara diff, pruebas originales y resultados. Si se cumple el contrato, haz el commit; si no, pide una corrección.](2026-11-12-t3-code-workflow.svg)

Guarda estos tres archivos en una carpeta nueva `t3-code-example`. Las pruebas Node no usan paquetes externos ni llamadas API. De las dos formas de `Retry-After`, el ejercicio admite **solo `delay-seconds`, segundos enteros**. HTTP-date está fuera de alcance y debe devolver `null`. Consulta la [definición de Retry-After en RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html#name-retry-after) para la gramática completa.

### `package.json`

```json
{
  "name": "t3-code-retry-after-example",
  "private": true,
  "type": "module",
  "engines": { "node": ">=24" },
  "scripts": { "test": "node --test retry-after.test.mjs" }
}
```

### `retry-after.mjs`

```javascript
export function retryAfterMs(header) {
  const seconds = Number.parseInt(header, 10);
  return Number.isFinite(seconds) ? seconds * 1000 : null;
}
```

### `retry-after.test.mjs`

```javascript
import test from 'node:test';
import assert from 'node:assert/strict';
import { retryAfterMs } from './retry-after.mjs';

const cases = [
  ['2', 2000],
  ['0', 0],
  [' 2 ', 2000],
  ['0002', 2000],
  ['', null],
  ['   ', null],
  [undefined, null],
  [null, null],
  [2, null],
  ['0x10', null],
  ['2x', null],
  ['-1', null],
  ['1.5', null],
  ['1e3', null],
  ['Infinity', null],
  ['Wed, 21 Oct 2015 07:28:00 GMT', null],
  ['9007199254740', 9007199254740000],
  ['9007199254741', null],
  ['9007199254740991', null],
];
for (const [input, expected] of cases) {
  test(`retryAfterMs(${JSON.stringify(input)})`, () => {
    assert.equal(retryAfterMs(input), expected);
  });
}
```

Ejecuta estos comandos en la carpeta del proyecto con el autor de Git ya configurado.

```sh
git init -b main
git add package.json retry-after.mjs retry-after.test.mjs
git commit -m "Add Retry-After exercise"
npm test
```

Se comprobó que el código inicial tiene **11 pruebas correctas y 8 fallidas** de 19. Acepta algunas cadenas que empiezan por dígitos, como `parseInt('2x', 10)`, y no trata correctamente negativos, decimales ni valores fuera del rango seguro. Las pruebas en rojo son el punto de partida.

## Abrir el proyecto y definir el alcance del cambio

Ejecuta lo siguiente desde la carpeta del proyecto para fijar la versión. `--host` limita el acceso a conexiones locales y `--auto-bootstrap-project-from-cwd` añade la carpeta actual como proyecto. La primera vez pueden descargarse el paquete npm y el ejecutable.

```sh
npm exec --yes --package=t3@0.1.9 -- t3 \
  --host 127.0.0.1 --auto-bootstrap-project-from-cwd .
```

La CLI inicia un servidor local y una aplicación web. Si ya usas un servidor T3 Code, abre el proyecto en ese entorno. La instalación de escritorio y el acceso remoto siguen rutas distintas en la [guía de instalación de esta versión](https://github.com/pingdotgg/t3code/blob/v0.1.9/docs/user/install.md). Aquí no se configura un servicio en segundo plano ni la exposición a una red externa.

Selecciona carpeta e hilo y elige un proveedor instalado y autenticado. Según la [guía de hilos](https://github.com/pingdotgg/t3code/blob/v0.1.9/docs/user/thread-sidebar.md), **New worktree** crea una rama y un directorio de trabajo separados. El ejercicio básico usa el directorio existente de la carpeta preparada. Si eliges otro worktree, ejecuta allí también los comandos Git y npm posteriores. Comprueba primero la ruta y rama del hilo. En el área de entrada verifica el modo **Supervised**. La [guía de permisos v0.1.9](https://github.com/pingdotgg/t3code/blob/v0.1.9/docs/user/permission-modes.md) indica que Full access es el valor inicial y que Supervised solicita aprobación para comandos y cambios de archivos. Los detalles, como las lecturas permitidas, varían según el proveedor.

Envía este prompt:

```text
Primero lee retry-after.mjs y retry-after.test.mjs.
Corrige retryAfterMs(header) según este contrato:

- Elimina espacios alrededor y acepta solo segundos enteros no negativos compuestos por dígitos ASCII.
- Devuelve milisegundos; tanto segundos como milisegundos deben cumplir Number.isSafeInteger.
- Devuelve null para valores vacíos o que no sean cadenas, negativos, decimales, notación exponencial, caracteres finales y valores fuera del rango seguro.
- HTTP-date queda fuera del alcance y debe devolver null.
- Modifica solo retry-after.mjs. No cambies las pruebas ni package.json.
- No instales dependencias, hagas solicitudes de red, commits, push ni crees un PR.

Verifica con npm test y comunica por qué cambiaste el código, los comandos ejecutados y sus resultados.
Indica explícitamente cualquier comando que no hayas podido ejecutar.
```

Cuando se solicite aprobación para un archivo o comando, comprueba que sea necesario para el ejercicio, como el archivo previsto o `npm test`. Una instrucción de alcance en el prompt no sustituye los permisos de herramientas. Aquí no se pide al agente que haga el commit: tú decides después de recibir los cambios y la verificación.

## ¿Cómo comprobar que «la corrección está completa»?

La [guía de revisión de cambios de T3 Code](https://github.com/pingdotgg/t3code/blob/v0.1.9/docs/user/source-control.md) distingue archivos y diffs por turno de la comparación entre ramas. El diff de turno muestra solo ese turno; antes de integrar compara también con la rama base. Despliega las llamadas de prueba en la conversación para revisar comando, salida y estado reales; también puedes repetirlas en una terminal.

```sh
git rev-parse --show-toplevel
git diff --name-only
git diff -- retry-after.mjs
git diff --exit-code -- retry-after.test.mjs package.json
npm test
```

Solo debe cambiar `retry-after.mjs`. Si el tercer comando muestra cambios o falla, determina primero por qué cambiaron pruebas o configuración. Pasar reduciendo las expectativas de las pruebas no satisface este contrato. Comprueba también `git status --short` para detectar archivos nuevos.

Si el agente dice que no pudo ejecutar las pruebas, no lo trates como éxito: ejecuta `npm test` tú mismo. Si quedan fallos, concreta entrada, valor esperado y resultado en una petición adicional. Por ejemplo: «`0` debe ser 0ms y `'2x'` debe ser null. Mantén las pruebas y revisa ambos casos».

Esta es la **implementación de referencia verificada directamente**. Compárala con el cambio del agente tras el ejercicio. Para ejecutarla, coloca este código en `retry-after.mjs` en la raíz del proyecto.

### `reference/retry-after.mjs`

```javascript
export function retryAfterMs(header) {
  if (typeof header !== 'string') return null;
  const value = header.trim();
  if (!/^[0-9]+$/.test(value)) return null;
  const seconds = Number(value);
  const milliseconds = seconds * 1000;
  return Number.isSafeInteger(seconds) && Number.isSafeInteger(milliseconds)
    ? milliseconds
    : null;
}
```

Al sustituir el código inicial por la referencia pasaron las mismas 19 pruebas y el archivo original de pruebas permaneció intacto. Comprobar el rango seguro de enteros es distinto de fijar un máximo real de espera entre reintentos. Esta función no ejecuta esperas ni analiza por completo HTTP-date; fija aparte el número de reintentos y el presupuesto total del cliente real.

Para registrar el trabajo después de revisar diff y pruebas, haz commit solo del archivo cambiado:

```sh
git add retry-after.mjs
git commit -m "Validate numeric Retry-After values"
```

Al terminar, detén el servidor en primer plano con `Ctrl+C` en la terminal que ejecuta T3 Code.

## ¿Qué revisar si no puedes empezar?

| Síntoma | Primera comprobación |
| --- | --- |
| Falta el proveedor o no se ejecuta | Instalación y PATH en el equipo servidor y configuración del proveedor en Settings |
| Error de autenticación | Cuenta del proveedor elegido e inicio de sesión en el equipo servidor |
| Los cambios no aparecen en la carpeta original | Si el hilo usa otro worktree y si consultas la misma ruta |
| No aparecen diff o funciones de ramas | Si la carpeta abierta es un repositorio Git y la ruta del proyecto es correcta |
| Las pruebas pasan, pero los cambios exceden el alcance | Diff y estado Git, incluidas pruebas, configuración y archivos adicionales |

El README oficial indica que es un proyecto temprano que puede contener errores. Después de actualizar la aplicación o la CLI del proveedor, mantener un contrato pequeño y este procedimiento de verificación facilita comparar resultados, en vez de esperar una respuesta fija del mismo prompt.
