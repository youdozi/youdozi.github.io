---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2021-07-22-plus-minus",
  "routeSlug": "2021-07-22-plus-minus",
  "kind": "post",
  "title": "Additionner des valeurs signées en Java avec IntStream",
  "description": "Combinez les valeurs absolues et les signes booléens correspondants avec IntStream. Vérifiez l’annulation, les entrées toutes négatives, les limites de int et le contrat de longueurs égales.",
  "categories": [
    "coding-test"
  ],
  "tags": [
    "java",
    "algorithms"
  ],
  "sourcePath": "src/content/posts/en/2021-07-22-plus-minus.md",
  "sourceSha256": "63f6b289759a3487a5cb548baedd43054c6fa803aa1dbd58a39dd4d088a413bc",
  "draftSha256": "ee6acde715691bd560feafa61b2b23a93814ce78f198087efe7ffc45c93f52db",
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
Lorsque les valeurs absolues et les signes sont fournis séparément, appliquez le signe à chaque indice correspondant avant d’additionner. `signs[i]` signifie positif si true et négatif si false ; une seule expression conditionnelle reconstitue donc chaque valeur.

L’[exercice](https://school.programmers.co.kr/learn/courses/30/lessons/76501) garantit des tableaux de même longueur, de 1 à 1 000, et des valeurs absolues de 1 à 1 000. Trier les signes séparément romprait leur association avec les valeurs d’origine ; traitez les tableaux dans l’ordre fourni.

## Déroulement du traitement

![Lisez le même indice dans les deux tableaux, appliquez le signe, puis additionnez les valeurs signées.](/assets/diagrams/technical/fr-2021-07-22-plus-minus.svg)

Lisez le même indice dans les deux tableaux, appliquez le signe, puis additionnez les valeurs signées.

## Lire ensemble les indices correspondants

Enregistrez cette classe complète dans `Solution.java`. Elle a été compilée pour Java 11 et exécutée sur JDK 17.

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

[`IntStream.range`](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/stream/IntStream.html) inclut l’indice 0 et exclut `absolutes.length`. `map` applique le signe à chaque valeur absolue, puis `sum` additionne les valeurs obtenues. La méthode ne modifie pas l’entrée et ne crée pas de tableau séparé de valeurs signées.

| Valeur absolue | Signe | Valeur réelle |
| --- | --- | --- |
| 4 | true | 4 |
| 7 | false | -7 |
| 12 | true | 12 |

La somme de ces valeurs est 9. L’entrée `[1,2,3]` avec `[false,false,true]` s’annule pour donner 0. Compter uniquement les indicateurs positifs et négatifs ne suffit pas : la **valeur absolue** de chaque terme compte aussi.

## Limites des entiers et contrat

Il y a au plus 1 000 termes, chacun de valeur absolue au plus 1 000 ; la valeur absolue de la somme est donc bornée par 1 000 000. Même les cas limites où toutes les valeurs sont positives ou toutes négatives tiennent dans int. Le temps de calcul est O(n), avec O(1) d’espace supplémentaire.

La méthode suppose les valeurs absolues valides et les longueurs égales définies par l’exercice. Elle ne remplace pas les vérifications de null, de longueur et de valeur pour des entrées applicatives quelconques. Des limites plus grandes imposent de réexaminer les types des termes comme de l’accumulateur.

Comparez avec les [produits scalaires de tableaux](/en/posts/2021-07-22-dot-product/) pour un autre calcul à deux tableaux et avec [une suite espacée de x utilisant long](/en/posts/2021-07-29-interval-num/) pour des résultats dépassant int. Le [guide des exercices Java](/en/categories/coding-test/) propose un parcours d’apprentissage.
