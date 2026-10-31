---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ru",
  "translationKey": "2023-11-17-linux-shellscript-version-compare",
  "routeSlug": "2023-11-17-linux-shellscript-version-compare",
  "kind": "post",
  "title": "Сравнение числовых версий с точками в Shell с помощью Python",
  "description": "Сравниваем версии без упаковки полей фиксированной ширины. Обрабатываем завершающие нули, длинные компоненты, недопустимые данные и явные коды завершения.",
  "categories": [
    "linux"
  ],
  "tags": [
    "linux",
    "bash",
    "shell script",
    "function"
  ],
  "sourcePath": "src/content/posts/en/2023-11-17-linux-shellscript-version-compare.md",
  "sourceSha256": "f3a895ba23f21ab99f5083879149d5f7f1ab3ed0c7c9a89c1557b9bf7d6b1ddc",
  "draftSha256": "2a6ca2d8c1cca75ffe1568dd309ddaa9f5bda91c0a204404a77230d321af7453",
  "manifestPath": ".pipeline/technical-translations/batch-052/manifest.json",
  "manifestSha256": "3d0fe88e42da93129f62cd5dba401357ffe96d3d01f3038c35211f5afff754c7",
  "publishedAt": "2026-10-31T15:21:36.227Z",
  "updatedAt": "2026-10-31T15:21:36.227Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 125,
    "approvedAt": "2026-10-31T15:21:36.227Z",
    "basis": "User explicitly requested applying all missing technical-post languages, review, verification and deployment on 2026-11-01, with standing PR merge authorization. Human approval denotes publication authorization; linguistic review is performed by AI, not human/native review."
  }
}
---
Не сравнивайте `1.10` и `1.2` как строки или десятичные числа. Сравнивайте целочисленные компоненты слева направо, дополняя отсутствующие конечные компоненты нулями; тогда `1.2` равно `1.2.0`. Пример реализует это правило только для числовых версий с точками.

Он отклоняет `v1.2`, `1.2-rc1` и `1.2+build`. Для приоритета предварительных версий по [SemVer](https://semver.org/) используйте парсер этой спецификации. Безусловное удаление суффиксов может изменить смысл.

## Порядок обработки

![Проверьте контракт, допускающий только числовые компоненты, дополните отсутствующие компоненты нулями и остановитесь на первой различающейся паре. Результат «меньше» тоже означает успешно выполненное сравнение.](/assets/diagrams/technical/ru-2023-11-17-linux-shellscript-version-compare.svg)

Проверьте контракт, допускающий только числовые компоненты, дополните отсутствующие компоненты нулями и остановитесь на первой различающейся паре. Результат «меньше» тоже означает успешно выполненное сравнение.

## Исполняемый скрипт сравнения

Требуется Python 3. Сохраните код в `version-compare.sh` и вызывайте через `sh`.

### `version-compare.sh`

```sh
#!/bin/sh
set -eu
python3 - "$@" <<'PYTHON'
import re
import sys
from itertools import zip_longest

if len(sys.argv) != 3 or any(not re.fullmatch(r"[0-9]+(?:\.[0-9]+)*", value) for value in sys.argv[1:]):
    print("usage: version-compare.sh CURRENT LATEST (numeric dotted versions)", file=sys.stderr)
    raise SystemExit(2)
current, latest = sys.argv[1:]
try:
    left = [int(part) for part in current.split('.')]
    right = [int(part) for part in latest.split('.')]
except ValueError:
    print("numeric component exceeds this Python runtime's conversion limit", file=sys.stderr)
    raise SystemExit(2)
comparison = 0
for a, b in zip_longest(left, right, fillvalue=0):
    if a != b:
        comparison = -1 if a < b else 1
        break
operator = '<' if comparison < 0 else '>' if comparison > 0 else '='
print(f"{current} {operator} {latest}")
PYTHON
```

```sh
sh version-compare.sh 1.10.5 1.3.1
sh version-compare.sh 1.2 1.2.0
sh version-compare.sh 1.1000 2.0
```

Вывод: `1.10.5 > 1.3.1`, `1.2 = 1.2.0` и `1.1000 < 2.0`. Допустимое сравнение возвращает код 0 независимо от отношения версий. Неверное число аргументов, неподдерживаемый синтаксис или ограничение преобразования чисел приводят к пояснению в stderr и коду 2.

| Входные данные | Результат |
| --- | --- |
| `1.2.0.0.1` и `1.2` | `1.2.0.0.1 > 1.2` |
| `01.002` и `1.2` | `01.002 = 1.2` |
| `1.2-rc1` и `1.2` | Неподдерживаемый формат, код 2 |
| `1..2` и `1.2` | Неподдерживаемый формат, код 2 |

## Почему не объединять числа фиксированной ширины?

Ширина вроде `%03d` в awk — это минимальная ширина вывода, а не максимальная длина компонента. Упаковка таких полей в целое число оболочки может нарушить исходный порядок при больших значениях или дополнительных компонентах.

В примере каждый компонент преобразуется в целое число Python, а [`zip_longest(..., fillvalue=0)`](https://docs.python.org/3/library/itertools.html#itertools.zip_longest) выравнивает длины. Отказ среды выполнения преобразовать число не считается успешным сравнением.

В автоматизации развёртывания сравнение и успешность команды — разные решения. Скрипт не завершается с ошибкой лишь потому, что текущая версия ниже: сначала прочитайте отношение из stdout, затем примените свою политику. [Теги релизов GitHub](/en/posts/2023-09-23-linux-shellscript-github-latest/) не обязаны следовать этому числовому синтаксису, поэтому не передавайте их без проверки. Выбор интерпретатора описан в [примере функции POSIX sh](/en/posts/2023-09-20-linux-shellscript-function-error/).
