---
language: "ru"
translationKey: "2023-09-23-linux-shellscript-github-latest"
title: "Последний релиз GitHub с curl и jq: выбираем один файл для загрузки"
description: "С помощью curl и jq выбираем ровно один ресурс релиза GitHub по ОС, CPU и формату. Обрабатываем ошибки HTTP, неверный JSON и отсутствие или дублирование совпадений."
state: "draft"
sourcePath: "src/content/posts/en/2023-09-23-linux-shellscript-github-latest.md"
sourceSha256: "f16e3b473bf828c56f507244947e3df3c7440005abaf27d54492d6fe5aaa1d23"
---
Используйте `curl`, чтобы получить последний релиз GitHub, и `jq`, чтобы выбрать ровно один файл для нужных ОС, CPU и формата. Скрипт ниже останавливается при ошибках HTTP, неверном JSON, отсутствии или дублировании совпадений; он возвращает метаданные без загрузки файла.

Конечная точка `releases/latest` не вычисляет численно наибольший тег Git. [Документация API релизов](https://docs.github.com/en/rest/releases/releases#get-the-latest-release) различает обычные теги, черновики, предварительные и опубликованные релизы.

Пример запрашивает в публичном репозитории `adoptium/temurin17-binaries` метаданные HotSpot JDK для Linux x64 в формате tar.gz. Не нужны ни токен, ни фактическая загрузка файла. Если аргумент репозитория не указан, используется это значение по умолчанию; явно пустой аргумент отклоняется.

## Порядок обработки

![Ошибка HTTP останавливает скрипт до разбора JSON. Допустимый объект релиза должен содержать ровно один подходящий ресурс; выбор его URL не проверяет загруженный файл.](2023-09-23-linux-shellscript-github-latest.svg)

Ошибка HTTP останавливает скрипт до разбора JSON. Допустимый объект релиза должен содержать ровно один подходящий ресурс; выбор его URL не проверяет загруженный файл.

## Отделяем ошибку HTTP от ошибки выбора из JSON

Нужны `curl`, `jq` и POSIX sh. Сохраните скрипт в `latest-release.sh`.

### `latest-release.sh`

```sh
#!/bin/sh
set -eu
if [ "$#" -gt 1 ]; then
    printf '%s\n' 'usage: latest-release.sh OWNER/REPO' >&2
    exit 2
fi
repo=${1-adoptium/temurin17-binaries}
case "$repo" in
    */*/*|/*|*/|*[!A-Za-z0-9_./-]*) printf '%s\n' 'usage: latest-release.sh OWNER/REPO' >&2; exit 2 ;;
esac
case "$repo" in
    */*) ;;
    *) printf '%s\n' 'usage: latest-release.sh OWNER/REPO' >&2; exit 2 ;;
esac
api=${GITHUB_API_URL:-https://api.github.com}
response=$(curl --fail --silent --show-error --location --max-time 20 \
    --header 'Accept: application/vnd.github+json' \
    --header 'X-GitHub-Api-Version: 2026-03-10' \
    "$api/repos/$repo/releases/latest") || exit 1
printf '%s' "$response" | jq --slurp --exit-status '
    if length != 1 or (.[0] | type) != "object" then
        error("expected one release object")
    else .[0] end
    | . as $release
    | if (.tag_name | type) != "string" or (.tag_name | length) == 0
         or (.assets | type) != "array" then
        error("missing release tag or assets")
      else . end
    | [.assets[] | select(.name | test("^OpenJDK17U-jdk_x64_linux_hotspot_.*\\.tar\\.gz$"))] as $assets
    | if ($assets | length) != 1 then
        error("expected exactly one Linux x64 JDK tar.gz asset")
      elif ($assets[0].browser_download_url | type) != "string"
           or ($assets[0].browser_download_url | length) == 0 then
        error("missing asset download URL")
      else {tag_name: $release.tag_name, download_url: $assets[0].browser_download_url} end
'
```

```sh
sh latest-release.sh adoptium/temurin17-binaries
```

При успехе результат — объект JSON с полями `tag_name` и `download_url`. Значения зависят от релиза на момент запроса. Ниже приведены тестовые данные для демонстрации структуры, а не утверждение о текущем последнем релизе:

```json
{"tag_name":"jdk-17.0.8.1+1","download_url":"https://github.com/adoptium/temurin17-binaries/releases/download/example/OpenJDK17U-jdk_x64_linux_hotspot_example.tar.gz"}
```

`curl --fail` сначала обрабатывает ошибки HTTP. Сохранение ответа до разбора не даёт последней команде конвейера скрыть сетевую ошибку. См. [параметры curl](https://curl.se/docs/manpage.html).

`jq --slurp` читает весь ввод в массив. Требование ровно одного значения JSON также отклоняет пустой ответ. Затем фильтр проверяет объект релиза, тег и массив ресурсов и выдаёт результат, только если совпало ровно одно имя файла. См. [руководство jq](https://jqlang.org/manual/).

## Результаты, которые нужно учитывать в автоматизации

| Условие | Результат |
| --- | --- |
| Допустимый ответ и ровно один подходящий ресурс | Вывод JSON, код 0. |
| HTTP403/404 или ошибка соединения | Ненулевой код. |
| Пустое тело или некорректный JSON | Ненулевой код. |
| Нет подходящих ресурсов или их несколько | Ошибка вместо произвольного выбора. |
| Неверный синтаксис аргумента репозитория | Справка об использовании, код 2. |

Если HTTP-запрос выполнен успешно, но подходящего файла нет, проверьте имена файлов релиза, прежде чем менять фильтр `jq`: этот пример выбирает Java 17 для Linux x64, а не любой пакет JDK. Для Java 21 используйте [пример выбора метаданных платформы Temurin](/en/posts/2023-10-10-temurin-jdk21-delay/). Если значения репозитория или платформы поступают из YAML, [разберите и проверьте конфигурацию как данные](/en/posts/2021-07-27-parse-yaml/), прежде чем передавать значения команде.

Локальные ответы HTTP использовались для проверки успеха, ошибок HTTP, неверного JSON, отсутствующих ресурсов и дублей. `GITHUB_API_URL` по умолчанию указывает на публичный API; его можно направить на тестовый сервер с тем же контрактом ответа.

Для чтения публичных ресурсов аутентификация не требуется. Если добавляете аутентифицированные запросы, не помещайте токены в исходный код и журналы трассировки Shell. Проверяйте заголовки ответа с ограничениями частоты и [документацию GitHub по этим ограничениям](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api).

Скрипт выбирает URL, но не проверяет целостность установочного файла. Автоматизация установки по-прежнему требует учёта контрольных сумм или подписей поставщика и целевой платформы. Прежде чем передавать тег в [компаратор числовых версий](/en/posts/2023-11-17-linux-shellscript-version-compare/), проверьте соответствие его входному контракту.
