---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ru",
  "translationKey": "2021-07-23-number-word",
  "routeSlug": "2021-07-23-number-word",
  "kind": "post",
  "title": "Преобразование английских названий цифр через String.replace в Java",
  "description": "Литеральная замена в допустимой смеси цифр и слов от zero до nine. Различия replace и replaceAll, границы целых чисел и область применения.",
  "categories": [
    "coding-test"
  ],
  "tags": [
    "java",
    "algorithms"
  ],
  "sourcePath": "src/content/posts/en/2021-07-23-number-word.md",
  "sourceSha256": "28614468f78703f7e406439ee8b23b83e06091ae7f42ed9835cd50c6d1bb2e87",
  "draftSha256": "c16b77efc6fb392a4cc2c6159b21504909194fa6170c181c4533d85f4f57edd2",
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
Для допустимого входа со смесью цифр и их названий замените фиксированные слова от `zero` до `nine` цифрами и разберите полученное целое число. Искомые слова — литералы, поэтому достаточно `String.replace` без `replaceAll`.

[Задача](https://school.programmers.co.kr/learn/courses/30/lessons/81301) гарантирует допустимые названия цифр в нижнем регистре и цифры, результат от 1 до 2 000 000 000 и отсутствие ведущего нуля. Это не разборщик произвольных английских числовых выражений.

## Ход обработки

![Литерально заменяем фиксированные слова от zero до nine цифрами, затем разбираем полученную десятичную строку.](/assets/diagrams/technical/ru-2021-07-23-number-word.svg)

Литерально заменяем фиксированные слова от zero до nine цифрами, затем разбираем полученную десятичную строку.

## Замена десяти фиксированных слов

Сохраните полный класс в `Solution.java`. Дополнительные импорты не нужны; код исходной статьи скомпилирован и выполнен с целевой версией Java 11.

```java
public class Solution {
    public int solution(String s) {
        String[] words = {"zero", "one", "two", "three", "four",
                "five", "six", "seven", "eight", "nine"};
        for (int digit = 0; digit < words.length; digit++) {
            s = s.replace(words[digit], Integer.toString(digit));
        }
        return Integer.parseInt(s);
    }
}
```

[`String.replace(CharSequence, CharSequence)`](https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/lang/String.html) выполняет литеральную замену. `replaceAll` интерпретирует первый аргумент как регулярное выражение. Здесь ни одному из десяти слов не нужен синтаксис регулярных выражений.

Например, `one4seveneight` превращается в `1478`, а `23four5six7` — в `234567`. Вход только из цифр, например `123`, по-прежнему даёт 123. `two` с девятью следующими словами `zero` даёт 2 000 000 000, что помещается в int.

Цифры после замены не могут породить другое название цифры, а ни одно из десяти слов не содержит другого слова из набора, поэтому этот порядок работает. Некорректные слова, пробелы, верхний регистр и числа вне диапазона не входят в гарантии задачи. Ошибка разбора произвольного входа не исправляется этим методом до допустимого целого числа.

При десяти фиксированных словах время — O(n) по длине входа. Строки неизменяемы, поэтому могут выделяться промежуточные строки; дополнительная память — O(n). Нет бенчмарка, который подтверждал бы, что на этих малых входах метод быстрее других разборщиков.

Для преобразования, где полезны регулярные выражения, сравните [нормализацию нового ID](/en/posts/2021-07-19-new-id/).
