---
{
  "schemaVersion": 1,
  "state": "draft",
  "language": "ru",
  "translationKey": "2026-11-19-website-building-agent-skills",
  "title": "Как создавать сайты с Claude Code и Codex — навыки от планирования до развёртывания",
  "description": "Какие навыки Claude Code и Codex выбрать для сайтов-визиток и веб-приложений, с примерами реализации интерфейса, проверок Playwright и контроля развёртывания.",
  "sourcePath": "src/content/posts/en/2026-11-19-website-building-agent-skills.md",
  "sourceSha256": "f7eb2b67f71eb23934048777fc9d7ffed4a983fc580e1b4d9a7b2cf3c8a3180e"
}
---

Для небольшого корпоративного сайта начните с трёх шагов — **продумать тексты и структуру страницы, собрать интерфейс и проверить в браузере путь к контактам**. Если в приложении есть вход в аккаунт или оплата, сначала спроектируйте права доступа, хранение данных и восстановление после сбоев. От типа сайта зависит, какие навыки выбирать и по каким признакам оценивать их результат.

19 ноября 2026 года я подобрал навыки для разных этапов по официальным материалам Anthropic, OpenAI и Vercel. В примерах работа поручается агенту в Claude Code или Codex CLI. [Навыки Anthropic](https://github.com/anthropics/skills) · [OpenAI Build Web Apps](https://github.com/openai/plugins/tree/main/plugins/build-web-apps) · [Vercel Agent Skills](https://github.com/vercel-labs/agent-skills)

## Как подобрать навыки под тип сайта

| Что создаём | Что определить сначала | Базовая последовательность |
| --- | --- | --- |
| Сайт-визитка, портфолио или блог | Аудитория, основное действие, публичные страницы и способ обновления контента | Тексты → реализация экрана → тест в браузере → проверка развёртывания |
| Приложение для бронирования, оплаты или администрирования | Права пользователей, сохраняемые данные, обработка успеха и ошибок, рабочие журналы | Дизайн экранов и состояний → реализация интерфейса и сервера → тесты нормального хода и сбоев → предпросмотр → проверка в рабочей среде |

Если уже есть репозиторий, сначала выясните, какой фреймворк в нём используется и как проект развёртывается. Например, статью и ссылку для связи в блоге на Astro можно добавить в рамках существующей конфигурации. Навыки оптимизации для React или Next.js и навыки по оплате выбирайте, когда проекту действительно нужны эти технологии и функции.

| Этап | Рекомендуемый навык или критерий | Что поручить и как проверить |
| --- | --- | --- |
| Планирование и тексты | Проектные инструкции `website-copywriting` | Определите аудиторию и основное действие, напишите заголовок, описание и текст для связи. Проверьте, понятно ли с первого экрана, что и кому предлагает сервис. |
| Проектирование интерфейса | Проектные инструкции `frontend-architecture-design` | Определите маршруты, какие компоненты отвечают за состояние, а также экраны успеха и ошибки. Для приложения бронирования продумайте повторное нажатие при отправке и повторную попытку после сбоя сохранения. |
| Реализация интерфейса | [`frontend-design` для Claude Code](https://github.com/anthropics/skills/tree/main/skills/frontend-design) или [`frontend-app-builder` для Codex](https://github.com/openai/plugins/tree/main/plugins/build-web-apps/skills/frontend-app-builder) | Реализуйте утверждённые тексты и структуру на существующих компонентах проекта. Проверьте, что и на узком экране заголовок, кнопка действия и основной текст читаются в нужном порядке. |
| Проверка в браузере | [`webapp-testing` для Claude Code](https://github.com/anthropics/skills/tree/main/skills/webapp-testing), [`frontend-testing-debugging` для Codex](https://github.com/openai/plugins/tree/main/plugins/build-web-apps/skills/frontend-testing-debugging) | На мобильном экране проверьте ссылку для связи, ошибки формы и консоль. Зафиксируйте URL, размеры экрана, точные шаги и результаты. |
| Проверка доступности | [`web-design-guidelines` от Vercel](https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines) | Проверьте подписи, контраст и фокус в коде. В браузере проверьте порядок клавиатурной навигации и видимость индикатора фокуса. Запишите результаты автоматических и ручных проверок. |
| Производительность React | [`react-best-practices` из Build Web Apps](https://github.com/openai/plugins/tree/main/plugins/build-web-apps/skills/react-best-practices) | Для React и Next.js проверьте последовательные запросы данных и начальный бандл. Оценивайте эффект по замерам до и после в одном окружении. |
| Развёртывание | [`deployments-cicd` для Vercel](https://github.com/openai/plugins/tree/main/plugins/vercel/skills/deployments-cicd) или инструкции проекта | Проверьте адрес предварительного или тестового развёртывания на выбранной платформе и опубликуйте согласованную версию. Запишите итоговый URL и версию для отката. |

Первые две строки таблицы показывают, какие инструкции можно написать для своего проекта. Для общедоступных навыков используйте способ установки, который предлагает команда сопровождения. В Claude Code навыки реализации и тестирования интерфейса входят в `example-skills` официального каталога Anthropic. В Codex плагин **Build Web Apps** включает навыки реализации интерфейсов, тестирования и оптимизации React. Навык развёртывания для Vercel подходит для публикации на Vercel. Если проект использует GitHub Pages, следуйте принятым в репозитории процессам Actions и предпросмотра. [Установка для Claude Code](https://github.com/anthropics/skills#claude-code) · [Состав OpenAI Build Web Apps](https://github.com/openai/plugins/blob/main/plugins/build-web-apps/README.md)

## Как выстроить работу навыков на небольшом сайте

Запрос на создание сайта может быть коротким. Если указать сведения об услуге, структуру экрана и проверяемое действие, при планировании, реализации и тестировании будут действовать одни и те же критерии.

**Пример запроса** Создай страницу вымышленной фотостудии. Посетители хотят узнать, где проходит съёмка и как получить консультацию. Размести описание студии и информацию для консультации на одной странице. Свяжи ссылку «Связаться» на первом экране с блоком консультаций на той же странице. Сохрани порядок: описание, ссылка для связи, блок консультаций. Учти узкий экран шириной 360px и управление с клавиатуры. После реализации проверь горизонтальное переполнение при 360px и 1280px. Дойди до ссылки клавишей Tab и открой блок консультаций клавишей Enter. Запиши результат каждого шага и то, что проверить не удалось.

Передайте описание и ссылку для связи на этап реализации, а размеры экрана и требования к клавиатуре используйте как критерии проверки. Если тест не проходит, сообщите агенту-исполнителю ширину и действие, на которых возник сбой. После исправления повторите тест в тех же условиях. Дополнительно при проверке доступности оцените контраст, имена, которые озвучивает программа экранного доступа, и положение фокуса после перехода на другую страницу.

## Упражнение — проверяем путь к контактам с Playwright

В упражнении страница помещается в тестовый файл и открывается в браузере при двух значениях ширины. Подготовьте Node.js 22 и Chrome в новой папке. Выполните `npm init -y`, затем установите зависимость командой `npm install --save-dev playwright-core@1.64.1`. Сохраните код как `website-check.mjs` и на macOS запустите `node website-check.mjs`. Если Chrome установлен в другом месте, укажите путь к исполняемому файлу в `CHROME_PATH`. [Параметры запуска Playwright](https://playwright.dev/docs/api/class-browsertype#browser-type-launch)

![Откройте страницу на двух размерах экрана и проверьте горизонтальное переполнение. Клавишей Tab дойдите до ссылки для связи и нажмите Enter, чтобы проверить переход к блоку консультаций. Если шаг не проходит, исправьте его и повторите проверку в тех же условиях.](2026-11-19-website-building-agent-skills.svg)

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

Ниже вывод запуска. Каждая строка `PASS` означает, что горизонтального переполнения не было, до ссылки удалось дойти с клавиатуры и заголовок блока консультаций попал в область просмотра.

```text
PASS 360px: no overflow, keyboard link reaches contact
PASS 1280px: no overflow, keyboard link reaches contact
```

В реальном проекте вместо HTML-строки запустите локальный сервер и откройте готовую страницу через `page.goto()`. Для формы отдельно проверьте отсутствие обязательного значения, сохранение введённых данных после сбоя отправки и сообщение об успехе. При замене цели ссылки для связи на другой фрагмент URL проверка ссылки при ширине 360px не прошла. Упражнение охватывает одну учебную HTML-страницу и два значения ширины в Chrome.

## Что проверять после развёртывания

Повторно откройте основные страницы и пройдите путь к контактам по ссылкам предпросмотра и рабочей версии. Проверьте ответы сервера и загрузку статических ресурсов. Для страниц, открытых поиску, проверьте заголовки и описания документов, канонические URL, внутренние ссылки и карту сайта. Отдельно от проверки рабочего URL выясните в Search Console, нашла ли поисковая система страницы и добавила ли их в индекс. [Основы SEO от Google](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)
