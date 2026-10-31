---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2021-07-29-interval-num",
  "routeSlug": "2021-07-29-interval-num",
  "kind": "post",
  "title": "Suite de pas x en Java : élargir le type avant la multiplication",
  "description": "Construire n valeurs de x à x*n avec IntStream. Pourquoi mapToLong seul ne prévient pas le dépassement de int, avec des pas positifs, négatifs et nuls.",
  "categories": [
    "coding-test"
  ],
  "tags": [
    "java",
    "algorithms"
  ],
  "sourcePath": "src/content/posts/en/2021-07-29-interval-num.md",
  "sourceSha256": "4674cdefcccdc5107e92b9fe49ee186426b25a096d2687d60d42724c51d29cf4",
  "draftSha256": "4c18ee2bc4bf2a4ccb5491c1577d4789a55fb9999e083bc20cda4c747b4686da",
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
Les n valeurs à partir de x vont de `x × 1` à `x × n`. Comme les résultats peuvent dépasser la plage de int, le tableau de résultat et **la multiplication elle-même** doivent utiliser long.

L’[exercice](https://school.programmers.co.kr/learn/courses/30/lessons/12954) borne x entre -10 000 000 et 10 000 000, et n entre 1 et 1 000. La valeur absolue du dernier terme peut donc atteindre 10 000 000 000, ce qui nécessite un tableau de long.

## Déroulement

![Transformer les indices commençant à zéro en numéros de termes, convertir x en long avant la multiplication, puis collecter dans l’ordre.](/assets/diagrams/technical/fr-2021-07-29-interval-num.svg)

Transformer les indices commençant à zéro en numéros de termes, convertir x en long avant la multiplication, puis collecter dans l’ordre.

## Transformer un indice en numéro de terme

Enregistrez cette classe complète dans `Solution.java`. Le code de l’article source a été compilé pour Java 11 et exécuté sur JDK 17.

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

[`IntStream.range(0, n)`](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/stream/IntStream.html) génère les indices de 0 à n-1. Multiplier par `i + 1` donne x comme première valeur et x×n comme dernière. Commencer à x×0 changerait la suite demandée.

| x | n | Résultat |
| --- | --- | --- |
| 2 | 5 | `[2,4,6,8,10]` |
| -4 | 2 | `[-4,-8]` |
| 0 | 3 | `[0,0,0]` |

Un x négatif produit des valeurs décroissantes, tandis que x=0 ne produit que des zéros. Préservez l’ordre des termes : ce n’est pas un problème de tri.

## mapToLong seul ne protège pas le produit

Même dans `mapToLong`, évaluer d’abord `x * (i + 1)` effectue une multiplication de int, car les deux opérandes sont des int. `(long) (x * (i + 1))` convertit également après le dépassement.

L’exemple élargit d’abord un opérande avec `(long) x * (i + 1)`. Les vérifications de l’article source comparent les tableaux de référence complets se terminant par 10 000 000 000 et -10 000 000 000 aux bornes positive et négative. Des entrées positives, négatives et nulles plus petites sont aussi comparées à des tableaux construits par additions répétées.

Le temps est O(n) et l’espace, tableau retourné compris, est O(n). Cette implémentation respecte les conditions de l’exercice ; elle ne valide pas de manière générale la taille de la suite ou des entrées d’API arbitraires.

Comparez les [sommes signées](/en/posts/2021-07-22-plus-minus/) et les [produits scalaires de tableaux](/en/posts/2021-07-22-dot-product/) pour des calculs qui tiennent dans int selon leurs bornes. Le [parcours d’exercices Java](/en/categories/coding-test/) relie les calculs sur les tableaux aux chaînes et collections.
