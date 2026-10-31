---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2021-07-23-unsuccessful-runner",
  "routeSlug": "2021-07-23-unsuccessful-runner",
  "kind": "post",
  "title": "Trouver le coureur manquant en Java avec les fréquences de noms",
  "description": "Soustraire les fréquences des arrivants de celles des participants avec HashMap. Gérer les homonymes sans différence de Set et préciser la garantie d’un seul coureur manquant.",
  "categories": [
    "coding-test"
  ],
  "tags": [
    "java",
    "algorithms"
  ],
  "sourcePath": "src/content/posts/en/2021-07-23-unsuccessful-runner.md",
  "sourceSha256": "a8c9e485842a9d8718e6cec7f5d0bcbda5a716bad751608cc67094ac938487d6",
  "draftSha256": "0b37f7513e70e857ad1f0ae97d542387c053bf371a925f07283973be790786de",
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
Pour trouver le coureur manquant, comptez les personnes par nom au lieu de vérifier uniquement l’existence du nom. Soustrayez les fréquences des arrivants de celles des participants ; l’exercice garantit qu’exactement un nom garde un effectif de 1.

Les [conditions d’entrée](https://school.programmers.co.kr/learn/courses/30/lessons/42576) autorisent jusqu’à 100 000 participants, un arrivant de moins et des homonymes. Les noms contiennent 1–20 lettres anglaises minuscules. La liste des arrivants est supposée être une liste valide de participants dont une personne a été retirée.

## Déroulement

![Compter tous les participants, soustraire chaque arrivant, puis renvoyer le nom dont l’effectif restant est un.](/assets/diagrams/technical/fr-2021-07-23-unsuccessful-runner.svg)

Compter tous les participants, soustraire chaque arrivant, puis renvoyer le nom dont l’effectif restant est un.

## Stocker la différence d’effectifs

Enregistrez cette classe complète dans `Solution.java`. Le code de l’article source a été compilé pour Java 11 et exécuté sur JDK 17.

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

`merge(name, 1, Integer::sum)` commence un nouveau nom à 1 et incrémente les noms existants. Chaque arrivant réduit le compte de son nom d’une unité. Avec les participants `[ana, bob, ana]` et les arrivants `[bob, ana]`, il reste pour ana `2 - 1 = 1`.

Une différence de Set ferait perdre le fait que deux personnes se nommaient ana. Les comptes conservent la multiplicité et représentent ainsi une personne manquante. Réordonner le tableau des arrivants ne change pas le résultat.

## Ne pas dépendre de l’ordre de HashMap

[`HashMap`](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/HashMap.html) ne garantit pas l’ordre d’itération. Renvoyer la première entrée positive fonctionne parce qu’une entrée valide n’en laisse qu’une, et non grâce à un ordre particulier. Le code renvoie le nom dont le compte restant vaut 1.

L’exception finale ne constitue pas une validation complète des entrées. Une API générale de rapprochement aurait besoin de règles et de contrôles supplémentaires pour les arrivants inconnus ou plusieurs personnes manquantes.

Avec des noms limités à 20 caractères et des opérations de hachage en temps constant en moyenne, le temps est O(n), avec O(u) d’espace supplémentaire pour u noms distincts. Aucun benchmark ne prouve que les streams ou les boucles sont universellement plus rapides.

Quand seuls les types distincts comptent, un Set suffit ; comparez [la borne de sélection de l’exercice Ponketmon](/en/posts/2021-07-29-ponkemon/).
