---
{
  "schemaVersion": 1,
  "state": "draft",
  "language": "es",
  "translationKey": "2026-11-19-website-building-agent-skills",
  "title": "Crear sitios web con Claude Code y Codex — habilidades desde la planificación hasta el despliegue",
  "description": "Qué habilidades elegir en Claude Code y Codex para crear sitios de presentación o aplicaciones web, con ejemplos de implementación, pruebas con Playwright y verificación del despliegue.",
  "sourcePath": "src/content/posts/en/2026-11-19-website-building-agent-skills.md",
  "sourceSha256": "f7eb2b67f71eb23934048777fc9d7ffed4a983fc580e1b4d9a7b2cf3c8a3180e"
}
---

Para un sitio corporativo pequeño, empieza por **definir los textos y la estructura, montar la interfaz y comprobar en el navegador cómo se llega al contacto**. Si la aplicación incluye inicio de sesión o pagos, diseña antes los permisos, el almacenamiento y la recuperación ante fallos. El tipo de sitio te ayuda a elegir las habilidades y a decidir cómo evaluar el resultado.

El 19 de noviembre de 2026 seleccioné las opciones de cada etapa a partir de las habilidades oficiales de Anthropic, OpenAI y Vercel. Los ejemplos parten de un encargo a un agente de Claude Code o Codex CLI. [Habilidades de Anthropic](https://github.com/anthropics/skills) · [OpenAI Build Web Apps](https://github.com/openai/plugins/tree/main/plugins/build-web-apps) · [Vercel Agent Skills](https://github.com/vercel-labs/agent-skills)

## Cómo elegir habilidades según el tipo de sitio

| Qué vas a crear | Qué definir primero | Combinación básica |
| --- | --- | --- |
| Sitio de presentación, portafolio o blog | Público, acción principal, páginas públicas y forma de editar el contenido | Textos → implementación de la interfaz → prueba de navegador → verificación del despliegue |
| Aplicación de reservas, pagos o administración | Permisos por usuario, datos que se guardan, gestión del éxito y del error, y registros operativos | Diseño de pantallas y estados → implementación de interfaz y servidor → pruebas de éxito y error → vista previa → verificación en producción |

Si ya hay un repositorio, empieza por comprobar el framework y cómo se despliega el proyecto. Por ejemplo, puedes añadir un artículo y un enlace de contacto a un blog Astro con la configuración que ya existe. Elige habilidades de rendimiento para React o Next.js y habilidades de pago cuando realmente hagan falta esas tecnologías y funciones.

| Etapa | Habilidad o criterio recomendado | Qué encargar y cómo verificarlo |
| --- | --- | --- |
| Planificación y textos | Instrucciones de proyecto `website-copywriting` | Define el público y la acción principal, y redacta el título, la descripción y el texto de contacto. En la primera pantalla debe entenderse qué ofrece el servicio y a quién. |
| Diseño de interfaz | Instrucciones de proyecto `frontend-architecture-design` | Define las rutas, qué componentes son responsables del estado y qué muestran las pantallas de éxito y error. Para una aplicación de reservas, diseña cómo tratar un clic repetido durante el envío y cómo reintentar si falla el guardado. |
| Implementación de interfaz | [`frontend-design` de Claude Code](https://github.com/anthropics/skills/tree/main/skills/frontend-design) o [`frontend-app-builder` de Codex](https://github.com/openai/plugins/tree/main/plugins/build-web-apps/skills/frontend-app-builder) | Lleva los textos y la estructura aprobados a los componentes del proyecto. Comprueba que en pantallas estrechas el título, el botón de acción y el cuerpo se lean en ese orden. |
| Pruebas en navegador | [`webapp-testing` de Claude Code](https://github.com/anthropics/skills/tree/main/skills/webapp-testing), [`frontend-testing-debugging` de Codex](https://github.com/openai/plugins/tree/main/plugins/build-web-apps/skills/frontend-testing-debugging) | Revisa el enlace de contacto, los errores del formulario y la consola en móvil. Registra la URL, el tamaño de pantalla, los pasos para reproducir el caso y el resultado. |
| Revisión de accesibilidad | [`web-design-guidelines` de Vercel](https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines) | Revisa etiquetas, contraste y foco en el código. Comprueba en el navegador el orden del teclado y el indicador de foco. Registra los resultados automáticos y los manuales. |
| Rendimiento de React | [`react-best-practices` de Build Web Apps](https://github.com/openai/plugins/tree/main/plugins/build-web-apps/skills/react-best-practices) | Revisa las solicitudes de datos en serie y el paquete inicial en proyectos React y Next.js. Mide antes y después en el mismo entorno para evaluar la mejora. |
| Despliegue | [`deployments-cicd` de Vercel](https://github.com/openai/plugins/tree/main/plugins/vercel/skills/deployments-cicd) o instrucciones de despliegue del proyecto | Comprueba la URL de vista previa o preproducción en el proveedor correspondiente y despliega la versión aprobada. Registra la URL final y a qué versión puedes volver. |

Las dos primeras filas son ejemplos de funciones que se pueden documentar en el propio proyecto. Para las habilidades públicas, sigue la ruta de instalación del equipo que las mantiene. En Claude Code, las de implementación y pruebas de interfaz están en `example-skills` del mercado oficial de Anthropic. En Codex, el complemento **Build Web Apps** reúne implementación, pruebas y optimización de React. Usa la habilidad de despliegue de Vercel si publicas allí. En un proyecto de GitHub Pages, sigue los flujos de Actions y el procedimiento de vista previa del repositorio. [Instalación en Claude Code](https://github.com/anthropics/skills#claude-code) · [Contenido de OpenAI Build Web Apps](https://github.com/openai/plugins/blob/main/plugins/build-web-apps/README.md)

## Cómo encadenar habilidades en un sitio pequeño

El encargo puede ser breve. Si incluyes la información del servicio, la estructura de la página y la acción que se va a comprobar, podrás aplicar los mismos criterios al planificar, implementar y probar.

**Ejemplo de prompt** Crea un sitio de presentación para un estudio fotográfico ficticio. Los visitantes quieren consultar el lugar de la sesión y cómo solicitar asesoramiento. Pon la presentación y la información de contacto en una sola página. Enlaza «Contactar», en la primera pantalla, con la sección de contacto de esa página. Conserva el orden: presentación, enlace de contacto y sección de contacto. Ten en cuenta una pantalla estrecha de 360px y el uso del teclado. Tras implementar, comprueba el desbordamiento horizontal a 360px y 1280px. Llega al enlace de contacto con Tab y usa Enter para abrir la sección. Registra el resultado de cada paso y lo que no hayas podido verificar.

Pasa la presentación y el enlace de contacto a la implementación. Usa los tamaños de pantalla y las condiciones de teclado como criterios de prueba. Si falla una prueba, indica al agente que implementa el ancho y la acción que produjeron el fallo. Repite la prueba en las mismas condiciones cuando se corrija. En la revisión de accesibilidad, añade el contraste, el nombre que anuncia el lector de pantalla y la posición del foco tras navegar a otra página.

## Ejercicio — comprobar el recorrido al contacto con Playwright

El ejercicio incorpora una página al archivo de prueba y la abre en el navegador con dos anchos. Prepara Node.js 22 y Chrome en un directorio nuevo. Ejecuta `npm init -y` y después instala la dependencia con `npm install --save-dev playwright-core@1.64.1`. Guarda el código como `website-check.mjs` y, en macOS, ejecuta `node website-check.mjs`. Si Chrome está instalado en otra ubicación, indica la ruta del ejecutable en `CHROME_PATH`. [Opciones de lanzamiento de Playwright](https://playwright.dev/docs/api/class-browsertype#browser-type-launch)

![Abrir la página con dos tamaños, comprobar si hay desbordamiento horizontal y llegar al enlace de contacto con Tab. Pulsar Enter para comprobar que se llega a la sección de contacto. Si falla un paso, corregirlo y repetir la prueba en las mismas condiciones.](2026-11-19-website-building-agent-skills.svg)

```js
import assert from 'node:assert/strict';
import { chromium } from 'playwright-core';

const html = `<!doctype html>
<html lang="ko">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>봄 사진 스튜디오</title>
<style>
  body { margin: 0; font: 1rem/1.6 system-ui; }
  main { max-width: 42rem; margin: auto; padding: 1rem; }
  section { min-height: 74vh; }
</style>
<main>
  <section>
    <h1>봄 사진 스튜디오</h1>
    <p>프로필 사진과 가족사진을 촬영합니다.</p>
    <a href="#contact">문의하기</a>
  </section>
  <section id="contact">
    <h2>상담 안내</h2>
    <p>촬영 목적과 희망 일정을 준비해 주세요.</p>
  </section>
</main>
</html>`;

const browser = await chromium.launch({
  executablePath: process.env.CHROME_PATH
    ?? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
});

try {
  for (const width of [360, 1280]) {
    const page = await browser.newPage({ viewport: { width, height: 700 } });
    try {
      await page.setContent(html);
      const overflow = await page.evaluate(
        () => document.documentElement.scrollWidth > window.innerWidth,
      );
      assert.equal(overflow, false, `가로 넘침: ${width}px`);

      await page.keyboard.press('Tab');
      const focused = await page.evaluate(
        () => document.activeElement?.getAttribute('href'),
      );
      assert.equal(focused, '#contact', `문의 링크 포커스: ${width}px`);
      await page.keyboard.press('Enter');
      await page.waitForURL(/#contact$/);
      const heading = await page.getByRole('heading', { name: '상담 안내' }).boundingBox();
      assert.ok(heading && heading.y >= 0 && heading.y + heading.height <= 700);
      console.log(`PASS ${width}px: no overflow, keyboard link reaches contact`);
    } finally {
      await page.close();
    }
  }
} finally {
  await browser.close();
}
```

Esta es la salida. Cada `PASS` indica que no hubo desbordamiento horizontal, que se llegó al enlace con el teclado y que el título de la sección de contacto quedó dentro del área visible.

```text
PASS 360px: no overflow, keyboard link reaches contact
PASS 1280px: no overflow, keyboard link reaches contact
```

En un proyecto real, inicia el servidor local y abre la página con `page.goto()` en vez de usar una cadena HTML. Si hay un formulario, añade comprobaciones separadas para campos obligatorios vacíos, conservación de los datos tras un fallo de envío y mensaje de éxito. Al cambiar el destino del enlace de contacto a otro fragmento de URL, falló la prueba del enlace a 360px. El ejercicio cubre una página HTML de prueba y dos anchos en Chrome.

## Qué comprobar después del despliegue

Abre de nuevo las páginas principales y el recorrido de contacto en las URL de vista previa y producción. Comprueba la respuesta del servidor y los recursos estáticos. En las páginas que se publicarán en buscadores, revisa el título y la descripción, la URL canónica, los enlaces internos y el mapa del sitio. Comprueba en Search Console si el buscador ha descubierto e indexado las páginas, por separado de la verificación de que la URL de producción abre. [Guía básica de SEO de Google](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)
