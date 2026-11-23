---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ru",
  "translationKey": "2026-11-22-claude-mythos-availability",
  "routeSlug": "2026-11-22-claude-mythos-availability",
  "kind": "post",
  "title": "Где доступна Claude Mythos 5.2? Claude Security, Claude Code и API",
  "description": "Сравните условия прямого доступа к Mythos 5.2, проверки кода через Claude Security в Enterprise и использования Fable 5.2 на платных тарифах Claude.",
  "categories": [
    "ai"
  ],
  "tags": [
    "claude",
    "claude-mythos",
    "claude-fable",
    "claude-security",
    "claude-code"
  ],
  "sourcePath": "src/content/posts/en/2026-11-22-claude-mythos-availability.md",
  "sourceSha256": "03f809cd5ff47c9929524f940e1ebf683dc5e75760fb062cfdb425ffbf4ff424",
  "draftSha256": "f19e52e17a8013361fecb06039765b3c1473e3e3e225fd222ab1ce86fd6855fa",
  "manifestPath": ".pipeline/technical-translations/batch-185/manifest.json",
  "manifestSha256": "3281e1d3e7c9b3abbb6c101d911dd0fcdee7dd54f7034838135f391123b6fb44",
  "publishedAt": "2026-11-23T00:19:14.218Z",
  "updatedAt": "2026-11-23T00:19:14.218Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 185,
    "approvedAt": "2026-11-23T00:19:14.218Z",
    "basis": "The site owner explicitly requested missing supported locales for the eight articles published in PRs #177–#184. This authorizes publication of the 48 editions enumerated in this batch."
  }
}
---

**Для прямого доступа к Claude Mythos 5.2 нужно получить одобрение в рамках программы проверки Anthropic.** Пользователи подходящих индивидуальных тарифов могут получить Defense Access, если их заявку одобрят в программе Cyber Verification Program (CVP). Организация с Claude Enterprise может включить Claude Security. Этот сервис использует Mythos 5.2 для проверки кода. Fable 5.2 общедоступна на платных тарифах Claude. Требования к кредитам на использование зависят от тарифа или лицензии. Руководство основано на публичной документации по состоянию на 22 ноября 2026 года. [Анонс версии 5.2 от Anthropic](https://www.anthropic.com/claude-fable-and-mythos-5-2#availability) · [Справка Claude о моделях, на которые распространяются условия](https://support.claude.com/en/articles/15425695-covered-models) · [Cyber Verification Program](https://support.claude.com/en/articles/14604842-cyber-verification-program)

## Какой вариант вам подходит?

![Для обычных задач разработки подписчики платных тарифов могут найти Fable 5.2 в списке моделей. Для проверки репозиториев Enterprise используется Claude Security. Прямой доступ к Mythos зависит от одобрения учётной записи и выбранного канала.](/assets/diagrams/technical/ru-2026-11-22-claude-mythos-availability.svg)

| Задача | Где искать | Условия доступа |
| --- | --- | --- |
| Использовать модель версии 5.2 для написания кода или текста | Список моделей в веб-версии Claude, настольном или мобильном приложении либо в Claude Code | Fable 5.2 доступна на платных тарифах. Кредиты на использование зависят от тарифа и лицензии. |
| Проверить репозиторий компании на проблемы безопасности с помощью Mythos | Claude Security в веб-версии Claude | Публичная бета-версия для Enterprise. Организация должна включить функцию, а у пользователя должна быть лицензия с Claude Code. |
| Использовать модель Mythos напрямую в Claude Code или Claude API | Права на модели в учётной записи или рабочая область, через которую используется API | Требуется одобрение в программе проверки. Пользователи подходящих индивидуальных тарифов могут подать заявку на Defense Access. |

**Mythos Preview** — предварительная исследовательская версия, которую Anthropic предоставила участникам Project Glasswing в апреле 2026 года. Anthropic представила **Mythos 5.2** 9 ноября. Сравнивая сообщения о доступности Mythos, проверяйте дату и версию модели. [Анонс Project Glasswing](https://www.anthropic.com/project/glasswing) · [Страница модели Claude Mythos](https://www.anthropic.com/claude/mythos)

## Где в Enterprise используется Mythos

**Claude Security использует Mythos 5.2 для проверки репозиториев.** Например, команда может обнаружить отсутствие проверки прав доступа во внутреннем веб-сервисе, а затем изучить подтверждающие данные и предложенное исправление. Anthropic предлагает Claude Security и клиентам Enterprise, которые не участвуют в Cyber Verification Program. Каждому пользователю нужна лицензия с Claude Code. На тарифах Enterprise с оплатой за лицензии нужно также включить кредиты на использование. Владелец организации с лицензией, включающей Claude Code, может активировать функцию в разделе `Organization settings → Claude Security`. [Анонс запуска от Anthropic](https://www.anthropic.com/claude-fable-and-mythos-5-2) · [Требования Claude Security](https://support.claude.com/en/articles/14661296-use-claude-security)

Найденную проблему можно открыть в Claude Code и заняться её исправлением. **Проверка и сеанс Claude Code используют разные разрешения на модели.** Для проверки используется Mythos, а в сеансе Claude Code доступны модели, на которые у вашей учётной записи есть права. Поэтому пользователи Enterprise могут видеть Claude Security, даже если Mythos нет в обычном списке моделей чата. [Страница продукта Claude Security](https://claude.com/product/claude-security) · [Настройка моделей Claude Code](https://code.claude.com/docs/en/model-config)

## Как найти Fable 5.2 на индивидуальном тарифе

По данным Anthropic, в основе Fable 5.2 и Mythos 5.2 лежит одна и та же модель. У Fable есть дополнительные меры защиты для задач из области кибербезопасности и наук о жизни. На платном индивидуальном тарифе Fable 5.2 подходит для общих задач разработки, например для знакомства с репозиторием или планирования рефакторинга. На тарифе Pro и для некоторых стандартных лицензий кредиты на использование нужны с самого начала. [Анонс моделей от Anthropic](https://www.anthropic.com/claude-fable-and-mythos-5-2) · [Доступность Fable по тарифам](https://support.claude.com/en/articles/15424964-claude-fable-models-on-your-plan)

В веб-версии, настольном или мобильном приложении найдите `Fable 5.2` в списке моделей. Если вы используете Claude Code в терминале, сначала убедитесь, что установлена версия **2.1.321** или новее. Затем откройте `/model` в сеансе, чтобы увидеть доступные модели. [Справка Claude о тарифах](https://support.claude.com/en/articles/15424964-claude-fable-models-on-your-plan) · [Настройка моделей Claude Code](https://code.claude.com/docs/en/model-config)

```sh
claude --version
```

В Claude API идентификатор Fable можно проверить запросом метаданных. Для примера нужна оболочка с `curl`. Ключ API нужной рабочей области уже должен быть задан в `ANTHROPIC_API_KEY`. При успешном запросе в ответе должно быть поле `id` со значением `claude-fable-5-2`. Формат запроса сверили с официальным справочником, а синтаксис оболочки проверили локально. Поведение Claude после аутентификации, включая ответ с метаданными и выбор модели, не проверялось. [Справочник Claude API по получению сведений о модели](https://platform.claude.com/docs/en/api/models/retrieve)

```sh
curl --fail-with-body --silent --show-error \
  'https://api.anthropic.com/v1/models/claude-fable-5-2' \
  -H 'anthropic-version: 2026-10-21' \
  -H "Authorization: Bearer ${ANTHROPIC_API_KEY}"
```

## Как проверить прямой доступ к Mythos

Согласно справке Cyber Verification Program, независимые исследователи безопасности, разработчики, сопровождающие проекты с открытым исходным кодом, и другие частные лица могут подать заявку на **Defense Access** при наличии подходящего тарифа, например Pro, Max или Ultra. Участники с одобренной заявкой получают доступ к Mythos 5.2 на этом уровне. Одной платной подписки для доступа недостаточно. У Anthropic есть отдельная программа проверки для исследований в области наук о жизни. [Справка Cyber Verification Program](https://support.claude.com/en/articles/14604842-cyber-verification-program) · [Анонс доступности от Anthropic](https://www.anthropic.com/claude-fable-and-mythos-5-2#availability)

В документации Claude API для Mythos 5.2 указан идентификатор модели `claude-mythos-5-2`. Доступность зависит от прав вашей учётной записи или организации и от выбранного канала. Права для Claude и Claude Console управляются отдельно. Разрешения в Console действуют в назначенной рабочей области. Организациям, которые работают через облачного провайдера, следует также проверить связанную облачную учётную запись и поддержку модели у провайдера. [Руководство по моделям Claude API](https://platform.claude.com/docs/en/models/fable-5-2/migration-guide) · [Справка Claude о тарифах, рабочих областях и облачных учётных записях](https://support.claude.com/en/articles/14604842-cyber-verification-program)
