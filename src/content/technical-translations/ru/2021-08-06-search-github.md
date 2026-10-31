---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ru",
  "translationKey": "2021-08-06-search-github",
  "routeSlug": "2021-08-06-search-github",
  "kind": "post",
  "title": "Поиск кода через GitHub, Sourcegraph и локальный Git",
  "description": "Сужение поиска по репозиторию, языку и пути, различия синтаксиса GitHub и Sourcegraph и воспроизводимый поиск фиксированной строки локальным Git.",
  "categories": [
    "util"
  ],
  "tags": [
    "git",
    "github",
    "sourcegraph",
    "search"
  ],
  "sourcePath": "src/content/posts/en/2021-08-06-search-github.md",
  "sourceSha256": "22da61f44f3002516631540293a6b08b9b0de12d2c7963e6c52ae57b297efddf",
  "draftSha256": "d46fe5c144b9d38761314e7edde95565e7a1a8961cbe155c58e52f75da6dec2a",
  "manifestPath": ".pipeline/technical-translations/batch-056/manifest.json",
  "manifestSha256": "5c3bd2ee5ccb0b59bad65322a026d7b2ef52cfac963e0236a497f74510717e42",
  "publishedAt": "2026-10-31T15:21:36.846Z",
  "updatedAt": "2026-10-31T15:21:36.846Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 125,
    "approvedAt": "2026-10-31T15:21:36.846Z",
    "basis": "User explicitly requested applying all missing technical-post languages, review, verification and deployment on 2026-11-01, with standing PR merge authorization. Human approval denotes publication authorization; linguistic review is performed by AI, not human/native review."
  }
}
---
Начните поиск кода с выбора репозитория и области файлов, затем изучите найденную реализацию в контексте. Совпавшее имя символа — зацепка, а не доказательство соответствия версии зависимости или нужному поведению.

Поиск GitHub, Sourcegraph и локальная рабочая копия ищут по разным доступным данным. Используйте инструмент с доступом к нужному репозиторию; не предполагайте, что публичный экземпляр индексирует каждый репозиторий и ревизию.

## Ход обработки

![Сначала ограничьте запрос, затем расширяйте список результатов. Если важна версия, откройте нужную ревизию или её checkout вместо опоры на ветку по умолчанию.](/assets/diagrams/technical/ru-2021-08-06-search-github.svg)

Сначала ограничьте запрос, затем расширяйте список результатов. Если важна версия, откройте нужную ревизию или её checkout вместо опоры на ветку по умолчанию.

## Собственный язык запросов каждого сервиса

[Запрос поиска GitHub](https://docs.github.com/en/search-github/github-code-search/understanding-github-code-search-syntax) может сочетать эти квалификаторы с фразой в кавычках:

```text
repo:spring-projects/spring-framework language:java path:WebClient.java "interface WebClient"
```

Соответствующие [фильтры Sourcegraph](https://sourcegraph.com/docs/code-search/queries) используют регулярные выражения для репозитория и файла:

```text
repo:^github\.com/spring-projects/spring-framework$ lang:java file:WebClient\.java$ "interface WebClient"
```

| Цель | Поиск GitHub | Sourcegraph |
| --- | --- | --- |
| Репозиторий | `repo:owner/name` | Регулярное выражение `repo:`; закрепите границы для точного совпадения |
| Java | `language:java` | `lang:java` или `language:java` |
| Область файлов | Фильтр пути `path:` | Регулярное выражение `file:` |
| Точная фраза | Фраза в кавычках | Фраза в кавычках в режиме ключевых слов |

Это примеры построения запросов, а не измеренные количества результатов онлайн. Два фильтра пути не обязаны давать одинаковые множества: пример Sourcegraph закрепляет суффикс имени файла. Доступ, индексированное содержимое и выбранная ревизия также определяют, что можно найти.

## Воспроизведение локального поиска в пустом каталоге

Небольшому примеру нужны Git и POSIX shell. `mkdir` намеренно завершается ошибкой, если `demo-search` уже существует, поэтому выберите новый рабочий каталог.

```sh
set -eu
mkdir demo-search
cd demo-search
git init -q
mkdir src docs
printf '%s\n' 'interface WebClient {}' > src/WebClient.java
printf '%s\n' 'interface WebClient is discussed here' > docs/notes.txt
git add src docs
git grep -n -F 'interface WebClient' -- src
```

Вывод:

```text
src/WebClient.java:1:interface WebClient {}
```

Та же фраза есть в `docs/notes.txt`, но `-- src` ограничивает поиск. [`git grep -F`](https://git-scm.com/docs/git-grep) считает шаблон фиксированной строкой, а `-n` выводит номера строк. Файлы добавлены в индекс, поскольку обычный поиск по рабочему дереву использует отслеживаемые файлы; пример не создаёт коммит. В настоящей рабочей копии замените путь и шаблон, сохранив нужную область.

Перед адаптацией прочитайте вызывающий код, тесты, лицензию и ревизию. Одинаковое объявление может вести себя иначе в другом выпуске. Проверяйте клиентский контракт через [тесты ответов WebClient](/en/posts/2023-09-19-springboot-test-webclient/), а не выводите поведение из совпадения поиска.
