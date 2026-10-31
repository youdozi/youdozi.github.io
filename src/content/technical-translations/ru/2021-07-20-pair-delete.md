---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ru",
  "translationKey": "2021-07-20-pair-delete",
  "routeSlug": "2021-07-20-pair-delete",
  "kind": "post",
  "title": "Удаление соседних одинаковых пар в Java со стеком ArrayDeque",
  "description": "Удаление соседних одинаковых символов стеком: инвариант префикса, каскадные удаления, граница в миллион символов и затраты времени и памяти.",
  "categories": [
    "coding-test"
  ],
  "tags": [
    "java",
    "algorithms"
  ],
  "sourcePath": "src/content/posts/en/2021-07-20-pair-delete.md",
  "sourceSha256": "a1962a62aeb00132eea16a0b3b607dfb9e256902ddc165613dbe7c044f14966e",
  "draftSha256": "c767a5494dc8e572c100c1bf1e0f7de3eb8b9161dccdecba04e69947875619b7",
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
Стек удаляет соседние пары одинаковых символов за один обход, храня сокращённый результат уже прочитанного префикса. Если следующий символ совпадает с вершиной, удаляем пару; иначе помещаем его в стек.

[Задача](https://school.programmers.co.kr/learn/courses/30/lessons/12973) принимает 1–1 000 000 строчных английских букв и возвращает 1, если можно удалить всё, иначе 0. Чётного общего количества каждой буквы недостаточно, поскольку удаление зависит от соседства.

## Ход обработки

![Стек хранит сокращённый префикс. Каждый новый символ удаляет совпадающую вершину или становится новой вершиной.](/assets/diagrams/technical/ru-2021-07-20-pair-delete.svg)

Стек хранит сокращённый префикс. Каждый новый символ удаляет совпадающую вершину или становится новой вершиной.

## Хранение сокращённого префикса

Сохраните полный класс в `Solution.java`. Код исходной статьи скомпилирован для Java 11 и выполнен на JDK 17.

```java
import java.util.ArrayDeque;
import java.util.Deque;

public class Solution {
    public int solution(String s) {
        Deque<Character> stack = new ArrayDeque<>();
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (!stack.isEmpty() && stack.peek() == c) stack.pop();
            else stack.push(c);
        }
        return stack.isEmpty() ? 1 : 0;
    }
}
```

Стек содержит обработанный префикс без оставшихся соседних одинаковых пар. Совпадающий следующий символ создаёт на границе удаляемую пару — выполняем pop. Другой символ такой пары не создаёт — выполняем push. Тот же инвариант сохраняется для следующего шага.

| Прочитанный символ | Стек: дно → вершина |
| --- | --- |
| b | b |
| a | ba |
| a | b |
| b | пусто |
| a | a |
| a | пусто |

Поэтому `baabaa` возвращает 1. Напротив, `abab` возвращает 0, хотя количества обеих букв чётные: одинаковых соседних символов нет. Стек обрабатывает границы, открытые удалением, без повторных замен по всей строке.

## ArrayDeque и сложность

Используйте [`ArrayDeque`](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/ArrayDeque.html) через операции Deque `push`, `peek` и `pop`. Поскольку `c` — примитивный char, `stack.peek() == c` распаковывает Character для сравнения, а не сравнивает идентичность объектов.

Каждый символ помещается в стек не более одного раза и извлекается не более одного раза. При амортизированных операциях дека время — O(n), а дополнительная память в худшем случае — O(n), когда символы остаются. Проверки выполнения исходной статьи включают миллион повторяющихся символов и миллион чередующихся символов без удаляемых пар. Это граничные проверки, а не бенчмарк скорости и не гарантия расхода памяти для любой среды.

Сохраняемая информация зависит от задачи: [задаче об участнике, не завершившем забег](/en/posts/2021-07-23-unsuccessful-runner/), нужны частоты имён, а не порядок соседства.
