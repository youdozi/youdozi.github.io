---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ru",
  "translationKey": "2021-07-22-plus-minus",
  "routeSlug": "2021-07-22-plus-minus",
  "kind": "post",
  "title": "Суммирование значений со знаками в Java с IntStream",
  "description": "Объединяем абсолютные значения с соответствующими булевыми знаками с помощью IntStream. Проверяем взаимное сокращение, все отрицательные значения, диапазон int и равную длину массивов.",
  "categories": [
    "coding-test"
  ],
  "tags": [
    "java",
    "algorithms"
  ],
  "sourcePath": "src/content/posts/en/2021-07-22-plus-minus.md",
  "sourceSha256": "63f6b289759a3487a5cb548baedd43054c6fa803aa1dbd58a39dd4d088a413bc",
  "draftSha256": "dfd0fbac3fb05aad6cd8b5a288febe9e82b97e71cf74d05c022ff7e5999c229d",
  "manifestPath": ".pipeline/technical-translations/batch-050/manifest.json",
  "manifestSha256": "e57f8d6a3aeeb6da0cb9abf684356147993428fb695af669351ebfcfd6c865aa",
  "publishedAt": "2026-10-31T15:21:35.938Z",
  "updatedAt": "2026-10-31T15:21:35.938Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 125,
    "approvedAt": "2026-10-31T15:21:35.938Z",
    "basis": "User explicitly requested applying all missing technical-post languages, review, verification and deployment on 2026-11-01, with standing PR merge authorization. Human approval denotes publication authorization; linguistic review is performed by AI, not human/native review."
  }
}
---
Если абсолютные значения и знаки поступают отдельно, перед суммированием примените знак по каждому соответствующему индексу. `signs[i]` означает положительный знак при true и отрицательный при false, поэтому каждое значение можно восстановить одним условным выражением.

[Задача](https://school.programmers.co.kr/learn/courses/30/lessons/76501) гарантирует одинаковую длину массивов от 1 до 1 000 и абсолютные значения от 1 до 1 000. Отдельная сортировка знаков нарушит их соответствие исходным значениям; обрабатывайте массивы в заданном порядке.

## Порядок обработки

![Прочитайте элементы обоих массивов с одним индексом, примените знак, затем сложите полученные значения со знаками.](/assets/diagrams/technical/ru-2021-07-22-plus-minus.svg)

Прочитайте элементы обоих массивов с одним индексом, примените знак, затем сложите полученные значения со знаками.

## Читаем соответствующие индексы вместе

Сохраните этот полный класс в `Solution.java`. Он был скомпилирован для Java 11 и выполнен на JDK 17.

```java
import java.util.stream.IntStream;

public class Solution {
    public int solution(int[] absolutes, boolean[] signs) {
        return IntStream.range(0, absolutes.length)
                .map(i -> signs[i] ? absolutes[i] : -absolutes[i])
                .sum();
    }
}
```

[`IntStream.range`](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/stream/IntStream.html) включает индекс 0 и исключает `absolutes.length`. `map` применяет знак к каждому абсолютному значению, а `sum` складывает результаты. Метод не меняет входные данные и не создаёт отдельный массив значений со знаками.

| Абсолютное значение | Знак | Фактическое значение |
| --- | --- | --- |
| 4 | true | 4 |
| 7 | false | -7 |
| 12 | true | 12 |

Сумма этих значений равна 9. Для входных данных `[1,2,3]` и `[false,false,true]` слагаемые взаимно сокращаются до 0. Недостаточно подсчитать только положительные и отрицательные флаги: важна и **абсолютная величина** каждого слагаемого.

## Границы целых чисел и контракт

Всего не более 1 000 слагаемых с абсолютным значением не более 1 000, поэтому абсолютное значение суммы ограничено 1 000 000. Даже граничные случаи со всеми положительными или всеми отрицательными значениями укладываются в int. Время работы — O(n), дополнительная память — O(1).

Метод предполагает допустимые абсолютные значения и одинаковую длину массивов по условиям задачи. Он не заменяет проверку null, длины и значений для произвольных входных данных приложения. При расширении границ нужно пересмотреть типы и слагаемых, и накопителя.

Для другого вычисления с двумя массивами см. [скалярное произведение массивов](/en/posts/2021-07-22-dot-product/), а для результатов за пределами int — [последовательность с шагом x и типом long](/en/posts/2021-07-29-interval-num/). Порядок изучения представлен в [руководстве по задачам на Java](/en/categories/coding-test/).
