---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ru",
  "translationKey": "2021-07-29-interval-num",
  "routeSlug": "2021-07-29-interval-num",
  "kind": "post",
  "title": "Последовательность с шагом x в Java: расширение типа до умножения",
  "description": "Создание n значений от x до x*n через IntStream. Почему одного mapToLong недостаточно против переполнения int; положительный, отрицательный и нулевой шаг.",
  "categories": [
    "coding-test"
  ],
  "tags": [
    "java",
    "algorithms"
  ],
  "sourcePath": "src/content/posts/en/2021-07-29-interval-num.md",
  "sourceSha256": "4674cdefcccdc5107e92b9fe49ee186426b25a096d2687d60d42724c51d29cf4",
  "draftSha256": "42ba228063bdd907b508355348c21852616952e2ce9b9c1919097ba94f89a377",
  "manifestPath": ".pipeline/technical-translations/batch-055/manifest.json",
  "manifestSha256": "1fe8bbde2d19f5780ba08f158519bd2d55fdec1dc863ec3bd9126705ddda372f",
  "publishedAt": "2026-10-31T15:21:36.540Z",
  "updatedAt": "2026-10-31T15:21:36.540Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 125,
    "approvedAt": "2026-10-31T15:21:36.540Z",
    "basis": "User explicitly requested applying all missing technical-post languages, review, verification and deployment on 2026-11-01, with standing PR merge authorization. Human approval denotes publication authorization; linguistic review is performed by AI, not human/native review."
  }
}
---
n значений, начиная с x, — это от `x × 1` до `x × n`. Результаты могут выходить за диапазон int, поэтому long нужен и для результирующего массива, и для **самого умножения**.

[Условие задачи](https://school.programmers.co.kr/learn/courses/30/lessons/12954) ограничивает x диапазоном от -10 000 000 до 10 000 000, а n — от 1 до 1 000. Модуль последнего значения может достигать 10 000 000 000, поэтому нужен массив long.

## Ход обработки

![Преобразуем индексы с нуля в номера членов, расширяем x до long перед умножением и собираем результаты по порядку.](/assets/diagrams/technical/ru-2021-07-29-interval-num.svg)

Преобразуем индексы с нуля в номера членов, расширяем x до long перед умножением и собираем результаты по порядку.

## Преобразование индекса в номер члена

Сохраните полный класс в `Solution.java`. Код исходной статьи скомпилирован для Java 11 и выполнен на JDK 17.

```java
import java.util.stream.IntStream;

public class Solution {
    public long[] solution(int x, int n) {
        return IntStream.range(0, n)
                .mapToLong(i -> (long) x * (i + 1))
                .toArray();
    }
}
```

[`IntStream.range(0, n)`](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/stream/IntStream.html) создаёт индексы от 0 до n-1. Умножение на `i + 1` делает первое значение равным x, а последнее — x×n. Начало с x×0 изменило бы требуемую последовательность.

| x | n | Результат |
| --- | --- | --- |
| 2 | 5 | `[2,4,6,8,10]` |
| -4 | 2 | `[-4,-8]` |
| 0 | 3 | `[0,0,0]` |

При отрицательном x значения убывают, а при x=0 получаются только нули. Сохраняйте порядок членов: это не задача сортировки.

## Одного mapToLong недостаточно для защиты произведения

Даже внутри `mapToLong` выражение `x * (i + 1)` сначала выполняет умножение int, поскольку оба операнда имеют тип int. Вариант `(long) (x * (i + 1))` тоже преобразует тип уже после переполнения.

В примере один операнд сначала расширяется: `(long) x * (i + 1)`. Проверки исходной статьи сравнивают полные эталонные массивы, заканчивающиеся на 10 000 000 000 и -10 000 000 000 для положительной и отрицательной границ. Меньшие положительные, отрицательные и нулевые входы также сравниваются с массивами, построенными повторным сложением.

Время — O(n), память с учётом возвращаемого массива — O(n). Реализация следует условиям задачи и не выполняет общую валидацию размера последовательности или произвольных входных данных API.

Для вычислений, помещающихся в int при своих ограничениях, сравните [сумму со знаками](/en/posts/2021-07-22-plus-minus/) и [скалярное произведение массивов](/en/posts/2021-07-22-dot-product/). [Маршрут задач Java](/en/categories/coding-test/) связывает вычисления над массивами со строками и коллекциями.
