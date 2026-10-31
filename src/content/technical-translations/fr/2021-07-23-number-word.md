---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2021-07-23-number-word",
  "routeSlug": "2021-07-23-number-word",
  "kind": "post",
  "title": "Convertir des mots de chiffres anglais avec String.replace en Java",
  "description": "Normaliser par remplacement littéral les mélanges valides de chiffres et de mots de zero à nine. Distinguer replace de replaceAll et préciser les limites des entiers et le périmètre.",
  "categories": [
    "coding-test"
  ],
  "tags": [
    "java",
    "algorithms"
  ],
  "sourcePath": "src/content/posts/en/2021-07-23-number-word.md",
  "sourceSha256": "28614468f78703f7e406439ee8b23b83e06091ae7f42ed9835cd50c6d1bb2e87",
  "draftSha256": "4e6479981f2c493ac21a49c1f58a0172b939372b421a3e50e49de35883b6ac23",
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
Pour une entrée valide mêlant chiffres et mots de chiffres, remplacez les mots fixes de `zero` à `nine` par des chiffres, puis analysez l’entier obtenu. Les termes recherchés sont littéraux : `String.replace` suffit, sans `replaceAll`.

L’[exercice](https://school.programmers.co.kr/learn/courses/30/lessons/81301) garantit des mots de chiffres valides en minuscules et des chiffres, un résultat de 1 à 2 000 000 000 et aucun zéro initial. Ce n’est pas un analyseur d’expressions numériques anglaises générales.

## Déroulement

![Remplacer littéralement les mots fixes de zero à nine par des chiffres, puis analyser la chaîne décimale obtenue.](/assets/diagrams/technical/fr-2021-07-23-number-word.svg)

Remplacer littéralement les mots fixes de zero à nine par des chiffres, puis analyser la chaîne décimale obtenue.

## Remplacer les dix mots fixes

Enregistrez la classe complète dans `Solution.java`. Aucun import supplémentaire n’est nécessaire ; le code de l’article source a été compilé et exécuté avec Java 11 comme cible.

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

[`String.replace(CharSequence, CharSequence)`](https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/lang/String.html) effectue un remplacement littéral. `replaceAll` interprète son premier argument comme une expression régulière. Aucun des dix mots ne nécessite ici de syntaxe regex.

Par exemple, `one4seveneight` devient `1478` et `23four5six7` devient `234567`. Une entrée déjà composée uniquement de chiffres, comme `123`, donne toujours 123. `two` suivi de neuf mots `zero` donne 2 000 000 000, dans la plage de int.

Les chiffres de remplacement ne peuvent pas introduire un autre mot de chiffre, et aucun des dix mots ne contient un autre mot de l’ensemble ; cet ordre fonctionne donc. Les mots invalides, espaces, majuscules et nombres hors plage ne font pas partie des garanties de l’exercice. Un échec d’analyse sur une entrée arbitraire n’est pas réparé en entier valide par cette méthode.

Avec dix mots fixes, le temps est O(n) selon la longueur d’entrée. Les chaînes étant immuables, des chaînes intermédiaires peuvent être allouées ; l’espace supplémentaire est O(n). Aucun benchmark ne montre que cette méthode est plus rapide que d’autres analyseurs pour ces petites entrées.

Comparez la [normalisation d’un nouvel identifiant](/en/posts/2021-07-19-new-id/) pour une transformation où les expressions régulières sont utiles.
