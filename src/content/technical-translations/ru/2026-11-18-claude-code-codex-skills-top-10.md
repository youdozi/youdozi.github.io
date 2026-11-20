---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ru",
  "translationKey": "2026-11-18-claude-code-codex-skills-top-10",
  "routeSlug": "2026-11-18-claude-code-codex-skills-top-10",
  "kind": "post",
  "title": "Десять полезных навыков Claude Code и Codex и как их применять",
  "description": "Сравнение десяти практических навыков для Claude Code и Codex CLI, инструкции по установке и вызову и упражнение с одним навыком для заметок о релизе в обоих инструментах.",
  "categories": [
    "ai"
  ],
  "tags": [
    "claude-code",
    "codex",
    "agent-skills",
    "ai-agent",
    "developer-tools"
  ],
  "sourcePath": "src/content/posts/en/2026-11-18-claude-code-codex-skills-top-10.md",
  "sourceSha256": "6e3aca2da19c8f558c9fdaaa5afcc7403a9fedfb528d5e3a58eb0ee33c0fd993",
  "draftSha256": "b8731d51a15e2d58444f666648930717d82d313b70912d74621365616811f82c",
  "manifestPath": ".pipeline/technical-translations/batch-172/manifest.json",
  "manifestSha256": "91fb61de3a3d1c432b5f074da43348e5ad1ab92b61742481f1cd4ac05bc2994e",
  "publishedAt": "2026-11-20T14:37:06.595Z",
  "updatedAt": "2026-11-20T14:37:06.595Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 172,
    "approvedAt": "2026-11-20T14:37:06.595Z",
    "basis": "User requested seven new language editions for each of four already published guides and approved parallel AI translation and verification. This records publication authorization."
  }
}
---

Если вы повторяете один и тот же запрос, оформите его как навык. Сохраните в нём допустимые входные данные для сводки изменений, формат результата и критерии проверки. Тогда для каждой задачи будет достаточно менять целевые файлы. Команды разработки могут начать с `skill-creator` и `webapp-testing`, а команды, которые часто работают с документами, — с навыка для нужного формата.

В статье рассматриваются **Claude Code** в терминале и **Codex CLI**. 18 ноября 2026 года я сверил варианты с официальными источниками и расположил их по **частоте повторного использования, удобству проверки и затратам на установку и подключение сервисов**. Это практическая подборка по указанным критериям, без учёта числа установок и статистики производительности. OpenAI рекомендует отказаться от старого каталога навыков, поэтому для Codex приведены способы установки из актуальной документации и плагинов. [Документация по навыкам Claude Code](https://code.claude.com/docs/en/skills) · [Документация по навыкам Codex](https://learn.chatgpt.com/docs/build-skills) · [Уведомление в старом каталоге](https://github.com/openai/skills) · [Репозиторий плагинов OpenAI](https://github.com/openai/plugins)

## 10 навыков для повседневной работы

В столбце «Источник и окружение» указано, где навык официально предоставляется или распространяется. Пример из Claude Code можно перенести в Codex с общим форматом `SKILL.md`. Отдельно сверьте прилагаемые скрипты, имена инструментов и настройки конкретного окружения.

| Место | Навык | Источник и окружение | Пример запроса и критерий проверки |
| --- | --- | --- | --- |
| 1 | `skill-creator` | Встроен в Codex / [пример для Claude Code](https://github.com/anthropics/skills/tree/main/skills/skill-creator) | «Создай навык для описаний PR. Подготовь пример входных данных для PR с исправлением и для PR с документацией». Подайте один запрос, который должен вызывать навык, и один, на который он не должен реагировать. |
| 2 | `webapp-testing` | [Пример для Claude Code](https://github.com/anthropics/skills/tree/main/skills/webapp-testing) | «С помощью Playwright проверь на локальной странице заказа успешную отправку и случай с незаполненным обязательным полем». Сохраните фактическое состояние экрана и журнал запуска. Понадобятся браузер и среда выполнения приложения. |
| 3 | `frontend-design` | [Пример для Claude Code](https://github.com/anthropics/skills/tree/main/skills/frontend-design) | «Спроектируй мобильный экран панели реагирования на инциденты. Покажи состояние и следующее действие в первую очередь». Проверьте пустые состояния, длинный текст и навигацию с клавиатуры. |
| 4 | `openai-docs` | Встроен в Codex / [руководство OpenAI Developers](https://developers.openai.com/learn/developers-codex-plugin) | «Проверь по официальной документации, где хранятся проектные навыки в Codex CLI и как их вызывать». Убедитесь, что источники подтверждают описанную возможность и то, что отображается в CLI. |
| 5 | `xlsx` | [Навык работы с документами для Claude Code](https://github.com/anthropics/skills/tree/main/skills/xlsx) | «Собери книгу с итогами по месяцам из CSV заказов. Отдели отменённые заказы и рассчитай суммы формулами». Сверьте число исходных строк, диапазон агрегации и итоги, проверьте формулы на ошибки. |
| 6 | `pdf` | [Навык работы с документами для Claude Code](https://github.com/anthropics/skills/tree/main/skills/pdf) | «Извлеки условия передачи результата и исключения из PDF с требованиями, укажи номера страниц». Сверьте порядок строк и столбцов и проверьте пропуски по оригиналу. Для сканов отдельно оцените качество OCR. |
| 7 | `docx` | [Навык работы с документами для Claude Code](https://github.com/anthropics/skills/tree/main/skills/docx) | «Напиши документ передачи проекта в приложенном шаблоне Word. Сохрани стили заголовков и структуру таблиц». Откройте результат в Word или совместимом редакторе и проверьте разрывы страниц и обрезку таблиц. |
| 8 | `pptx` | [Навык работы с документами для Claude Code](https://github.com/anthropics/skills/tree/main/skills/pptx) | «Подготовь ретроспективу эксплуатации на 6 слайдах. Рядом с цифрами укажи период измерения и единицы». Отобразите слайды и проверьте числа, оси и обрезку текста. |
| 9 | `openai-api-troubleshooting` | [Плагин OpenAI Developers для Codex](https://github.com/openai/plugins/tree/main/plugins/openai-developers/skills/openai-api-troubleshooting) | «Сузь круг причин по сообщению об ошибке API, из которого удалён ключ. Версию SDK и ID запроса я приложил». Разделите гипотезы и команды для их проверки, исключите исходные ключи и токены. |
| 10 | `imagegen` | Встроен в Codex / [исходник навыка](https://github.com/openai/codex/tree/main/codex-rs/skills/src/assets/samples/imagegen) | «Подготовь эскиз горизонтальной обложки для статьи. Не помещай заголовок статьи на изображение». Проверьте доступность генерации, размеры изображения, объём правок и искажения текста. |

`skill-creator` на первом месте, потому что помогает закрепить повторяющиеся процедуры команды в самом проекте. Для `webapp-testing` нужно подготовить приложение и браузер, зато результат можно оценить по журналу и состоянию экрана. Из четырёх документных навыков выбирайте нужный по формату. Диагностика API и генерация изображений полезны, когда есть конкретная ошибка или нужен иллюстративный материал.

В разработке удобно уточнить назначение экрана через `frontend-design`, а после реализации проверить действия пользователя через `webapp-testing`. Даже если есть дизайн-макет, включайте отдельную проверку, например сохраняется ли ввод после неудачной отправки. При работе с документами можно прочитать таблицу через `pdf` и свести данные через `xlsx`. Прежде чем передавать извлечённые данные дальше, сравните их с оригиналом.

## Как установить и вызвать навыки

В Claude Code добавьте официальный каталог Anthropic и выберите нужный набор. Для PDF, Word, Excel и PowerPoint подходит `document-skills`. Примеры создания навыков и веб-тестов входят в `example-skills`. Навык из установленного плагина можно упомянуть по имени в обычном запросе. [Инструкция по установке Anthropic](https://github.com/anthropics/skills#claude-code)

```text
/plugin marketplace add anthropics/skills
/plugin install document-skills@anthropic-agent-skills
/plugin install example-skills@anthropic-agent-skills
```

В Codex CLI найдите и явно выберите навык через `/skills` или меню `$`. Встроенный `skill-creator` вызывается как `$skill-creator`. Чтобы добавить диагностику OpenAI API, найдите **OpenAI Developers** в меню `/plugins` и выберите `Install plugin`. Откройте новый сеанс и убедитесь, что навык диагностики появился в `/skills`. [Вызов навыков в Codex](https://learn.chatgpt.com/docs/build-skills) · [Плагин OpenAI Developers](https://developers.openai.com/learn/developers-codex-plugin)

Навыки, которыми управляете внутри проекта, храните в `.claude/skills/<name>/SKILL.md` для Claude Code и в `.agents/skills/<name>/SKILL.md` для Codex, подставив имя навыка вместо заполнителя. При копировании официального примера проверьте инструменты и файлы, на которые ссылается `SKILL.md`. Если навыку требуется подключение, заранее проверьте аккаунт и область доступа. [Где Claude Code ищет навыки](https://code.claude.com/docs/en/skills#choose-where-skills-load) · [Где хранить навыки Codex](https://learn.chatgpt.com/docs/build-skills#where-to-save-skills)

## Упражнение — используем один навык для заметок о релизе в двух инструментах

Выполните команды ниже из новой учебной папки. Они создают один `SKILL.md`, копируют его в обе проектные папки и сравнивают файлы через `cmp`. Нужны POSIX-совместимая оболочка и `mkdir`, `cp`, `cmp`.

![Создайте учебную папку и исходный SKILL.md. Скопируйте его в проектные папки Claude Code и Codex, сравните файлы, затем передайте обоим инструментам одни и те же данные и проверьте результат.](/assets/diagrams/technical/ru-2026-11-18-claude-code-codex-skills-top-10.svg)

```sh
set -eu
mkdir skills-demo
cd skills-demo

mkdir -p .claude/skills/release-note-draft .agents/skills/release-note-draft

cat > release-note-source.md <<'SKILL'
---
name: release-note-draft
description: Draft a release note from a provided change list and test evidence.
---
Write three sections in Korean: 사용자 변경, 검증, 미확인.
Describe user-facing changes using only the supplied change list.
Put a test in 검증 only when the input explicitly says it ran and gives the result.
If a test is mentioned without a result, put it in 미확인.
Return the draft in the chat.
SKILL

cp release-note-source.md .claude/skills/release-note-draft/SKILL.md
cp release-note-source.md .agents/skills/release-note-draft/SKILL.md
cmp .claude/skills/release-note-draft/SKILL.md .agents/skills/release-note-draft/SKILL.md
printf '%s\n' 'Skill copies match.'
```

Запуск во временной папке macOS дал следующий вывод и код завершения `0`. Повторный запуск из той же родительской папки остановится на первом `mkdir`, поскольку `skills-demo` уже существует.

```text
Skill copies match.
```

Из `skills-demo` запустите `claude` и `codex` в отдельных сеансах терминала. В Claude Code выберите `/release-note-draft`, а в Codex CLI — `$release-note-draft`. Отправьте имя навыка и запись об изменении и проверках одним сообщением.

> Изменение: Если очистить поле электронной почты в настройках, кнопка «Сохранить» станет недоступной.\
> Проверка: Запущены 3 модульных теста экрана настроек. Все прошли.\
> Запланировано: Проверить поведение в мобильном браузере.\
> Составь черновик заметок о релизе по этим данным.

Ожидаемый результат содержит поведение кнопки в изменениях для пользователя, 3 успешных модульных теста в разделе проверки и ещё не проведённую проверку в мобильном браузере.

## Как отличались ответы на одинаковый запрос

Оба CLI получили один файл навыка и одну условную запись об изменении и проверках. Задача — **отделить уже выполненные тесты от запланированных** по предоставленной записи. Запуск новых тестов приложения в упражнение не входит.

При запуске Codex CLI 0.169.0 с GPT-6.2 Sol я подтвердил по журналу, что инструмент прочитал файл навыка в проекте. Ниже основные положения ответа.

| Раздел | Ответ Codex |
| --- | --- |
| Изменение для пользователя | Если удалить адрес из поля электронной почты в настройках, кнопка «Сохранить» станет недоступной. |
| Проверка | Все 3 модульных теста экрана настроек запущены и успешно пройдены. |
| Ещё не проверено | Проверка в мобильном браузере запланирована. |

Проектный навык также отобразился в списке Claude Code 2.0.76 и 2.1.327. Вызов модели остановился из-за ошибки входа. По результатам этого запуска можно подтвердить, что Claude Code обнаружил навык, а Codex выдал один ответ.
