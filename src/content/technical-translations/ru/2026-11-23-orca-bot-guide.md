---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ru",
  "translationKey": "2026-11-23-orca-bot-guide",
  "routeSlug": "2026-11-23-orca-bot-guide",
  "kind": "post",
  "title": "Orca Bot: создание бота для блога и проверка задач и автоматизаций",
  "description": "Поручите Orca Bot первую задачу, проверьте память и работу и настройте повторяющиеся задачи.",
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
  "sourceSha256": "00b9ff415bf1d0fddd82a856377211655f16ca6c010e833f68ed5639ee6d5108",
  "draftSha256": "2f60eae21ada61055e3b36da9c426529a1fc5c8b589cbf32e30051d69b5a33c3",
  "manifestPath": ".pipeline/technical-translations/batch-186/manifest.json",
  "manifestSha256": "afce5bc713412c02f130b1062bfe7d5b9872d9d301b703639a476301c673d0af",
  "publishedAt": "2026-11-23T05:18:32.011Z",
  "updatedAt": "2026-11-23T05:18:32.011Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 186,
    "approvedAt": "2026-11-23T05:18:32.011Z",
    "basis": "Owner explicitly requested publication of the Orca Bot guide in all eight supported languages; translations were self-reviewed, not independently or natively reviewed."
  }
}
---

**Создавая первого Orca Bot, до настройки повторяющейся работы поручите ему одну задачу с проверяемым результатом.** Например, передайте короткую техническую заметку и попросите заголовок и план статьи. Если результат имеет нужный формат, уточните роль бота и добавьте повторяющиеся задачи. В этом руководстве показан процесс на примере бота для подготовки черновиков блога.

Orca Bot — единица работы с именем, назначением и памятью. Выберите компьютер для запуска и агента, например Claude Code или Codex. Установите агента на этом компьютере и войдите в него. Первое упражнение выполняется внутри Orca. Чтобы вызывать бота из Slack, GitHub или Linear либо запускать его по событиям этих сервисов, добавьте необходимые подключения. [Быстрый старт Orca Bots](https://orca.dev/docs/bots) · [Коннекторы ботов](https://orca.dev/docs/bots/connectors)

![Создайте бота и поручите ему первую задачу. Проверьте результат и при необходимости примите решение в Needs you. Для повторяющейся работы задайте время или событие и проверьте историю запусков.](/assets/diagrams/technical/ru-2026-11-23-orca-bot-guide.svg)

## Создание бота и первый запрос

В боковой панели Orca в разделе **Bots** выберите **+ → New bot → Start from scratch**. Задайте имя и одним предложением опишите роль в **Who it is and what it does**. Имя в примере — `Blog Draft`, назначение — «превращать заметки о разработке в черновики технического блога». Проверьте компьютер и агента под именем и выберите **Create**. Если Bots нет в боковой панели, проверьте **Settings → Bots → Enable bots**. [Создание бота](https://orca.dev/docs/bots)

В чате бота укажите исходный материал и желаемый формат, как показано ниже. Эта заметка — вымышленный учебный материал.

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

Получив результат, проверьте, сохранилось ли ограничение: ответ 404 был проверен. Если добавлено утверждение о версии или пропускной способности, удалите его или запросите подтверждение. Успех первого запроса — заголовок, введение и подзаголовки на основе заметки, а не готовая к публикации статья.

## Правила для будущих чатов и текущая работа

| Где смотреть | Подходящее содержимое | Пример для бота блога |
| --- | --- | --- |
| `SOUL.md` | Постоянная роль и способы работы | Проверять сведения по официальной документации и ждать отдельного запроса на публикацию |
| `MEMORY.md` | Факты и предпочтения для будущих чатов | Читатели — разработчики Java и предпочитают исполняемые примеры |
| Рабочий элемент в **Home** | Текущий прогресс, приложенные результаты и решения, ожидающие утверждения | Новый черновик ожидает проверки |

Оба файла Markdown находятся в папке бота. Можно сообщить ему постоянное правило, например «В следующих примерах различай результаты собственных запусков и ожидаемые результаты», а затем проверить его соблюдение в дальнейшей работе. Чтобы узнать, завершена ли текущая работа, откройте рабочий элемент бота. Если необходимо решение, проверьте предмет вопроса и последствия в **Needs you** и ответьте. [Работа с Orca Bots](https://orca.dev/docs/bots) · [Память и доступ бота](https://orca.dev/docs/bots/security)

При запросе изменений кода в репозитории бот может передать работу исполнителю в отдельном Git worktree. Откройте workspace исполнителя в боковой панели и проверьте файлы и тесты; если создан PR, проверьте фактические изменения. [Исполнители бота](https://orca.dev/docs/bots) · [Руководство по Orca worktree](../2026-11-12-orca-worktree-guide/)

## Условие запуска и место результата повторяющейся задачи

Если первая задача выполнена удовлетворительно, отправьте в чат бота следующий запрос. В этом примере бот читает общедоступную документацию и только собирает идеи статей.

```text
Every Monday at 9:00 a.m. Korea time, select up to three technical
article ideas from official Spring Boot releases announced in the
previous seven days. For each candidate, include the announcement date,
official link, and a question to explore in an exercise.
If there were no announcements, say so.
Make the result available to me in Orca; do not publish it to the blog.
Also tell me which conversation the automation will leave its result in.
```

После создания автоматизации проверьте в панели бота **часовой пояс, условие запуска и место получения результата**. Если запуск должен происходить по событию, например новому PR в GitHub, а не по времени, сначала убедитесь, что коннектор подключён и поддерживает это событие. Если компьютер бота спит или находится вне сети, он не сможет сразу выполнить работу по расписанию; поэтому проверьте первый результат в истории запусков автоматизации. [Автоматизации Orca](https://orca.dev/docs/bots) · [Коннекторы Orca](https://orca.dev/docs/bots/connectors)

В macOS с установленным CLI следующие команды показывают имена ботов и доступные события. Замените имя во второй строке именем своего бота.

```sh
orca bot list
orca automations trigger-options --bot 'Blog Draft'
```

Обе команды чтения проверены с существующим ботом в **Orca CLI 1.4.271** в среде подготовки статьи. Для бота без подключения к GitHub результат показал, что события GitHub не могут его запускать. Имя и заметка в примере вымышлены; для статьи новый бот или автоматизация не создавались и не запускались. Руководство CLI для своей версии можно прочитать командой `orca skills get orca-cli --reference bots`.
