---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ru",
  "translationKey": "2021-07-23-unsuccessful-runner",
  "routeSlug": "2021-07-23-unsuccessful-runner",
  "kind": "post",
  "title": "Поиск участника, не завершившего забег, по частотам имён в Java",
  "description": "Вычитание частот финишировавших из частот участников через HashMap. Повторяющиеся имена без разности Set и условие ровно одного участника, не завершившего забег.",
  "categories": [
    "coding-test"
  ],
  "tags": [
    "java",
    "algorithms"
  ],
  "sourcePath": "src/content/posts/en/2021-07-23-unsuccessful-runner.md",
  "sourceSha256": "a8c9e485842a9d8718e6cec7f5d0bcbda5a716bad751608cc67094ac938487d6",
  "draftSha256": "e9325059395472105e8e90ba8e48acabbe70f0ee3ed7c97648ccdda4987fd6e7",
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
Чтобы найти участника, не завершившего забег, считайте людей по имени, а не только наличие имени. Вычтите частоты финишировавших из частот участников; задача гарантирует, что ровно у одного имени останется количество 1.

[Условия входа](https://school.programmers.co.kr/learn/courses/30/lessons/42576) допускают до 100 000 участников, на одного меньше финишировавших и повторяющиеся имена. Имена содержат 1–20 строчных английских букв. Предполагается, что список финишировавших — допустимый список участников, из которого удалён один человек.

## Ход обработки

![Считаем всех участников, вычитаем каждого финишировавшего и возвращаем имя с одним оставшимся человеком.](/assets/diagrams/technical/ru-2021-07-23-unsuccessful-runner.svg)

Считаем всех участников, вычитаем каждого финишировавшего и возвращаем имя с одним оставшимся человеком.

## Хранение разности количеств

Сохраните полный класс в `Solution.java`. Код исходной статьи скомпилирован для Java 11 и выполнен на JDK 17.

```java
import java.util.HashMap;
import java.util.Map;

public class Solution {
    public String solution(String[] participant, String[] completion) {
        Map<String, Integer> counts = new HashMap<>();
        for (String name : participant) counts.merge(name, 1, Integer::sum);
        for (String name : completion) counts.put(name, counts.get(name) - 1);
        for (Map.Entry<String, Integer> entry : counts.entrySet()) {
            if (entry.getValue() == 1) return entry.getKey();
        }
        throw new IllegalArgumentException("Expected exactly one missing runner");
    }
}
```

`merge(name, 1, Integer::sum)` начинает новое имя с 1 и увеличивает количество для существующих имён. Каждый финишировавший уменьшает количество для своего имени на одного. При участниках `[ana, bob, ana]` и финишировавших `[bob, ana]` для ana остаётся `2 - 1 = 1`.

Разность Set потеряла бы факт, что ana звали двух человек. Количества сохраняют кратность и тем самым представляют одного отсутствующего человека. Изменение порядка массива финишировавших не меняет результат.

## Не полагайтесь на порядок HashMap

[`HashMap`](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/HashMap.html) не гарантирует порядок обхода. Возврат первой положительной записи работает потому, что допустимый вход оставляет ровно одну такую запись, а не из-за определённого порядка. Код возвращает имя с остатком 1.

Исключение в конце не является полной проверкой входа. Универсальному API сверки потребовались бы дополнительные правила и проверки для неизвестных финишировавших или нескольких отсутствующих людей.

При длине имени не более 20 и среднем постоянном времени хеш-операций время — O(n), дополнительная память для u разных имён — O(u). Нет бенчмарка, доказывающего, что потоки или циклы всегда быстрее.

Когда важны только разные виды, достаточно Set; сравните [границу выбора в задаче Ponketmon](/en/posts/2021-07-29-ponkemon/).
