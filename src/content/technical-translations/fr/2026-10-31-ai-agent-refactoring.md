---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2026-10-31-ai-agent-refactoring",
  "routeSlug": "2026-10-31-ai-agent-refactoring",
  "kind": "post",
  "title": "Refactoriser avec un agent IA : préserver le comportement et vérifier les changements",
  "description": "Limiter une demande de refactoring, tester des attentes indépendantes et évaluer le résultat avec le diff et les exécutions réelles.",
  "categories": [
    "architecture"
  ],
  "tags": [
    "ai-agent",
    "refactoring",
    "java",
    "testing",
    "code-review",
    "developer-workflow"
  ],
  "sourcePath": "src/content/posts/en/2026-10-31-ai-agent-refactoring.md",
  "sourceSha256": "efd733fd275675221deef4ebffa545ba2f54a6819e72fed217917d6708e3e4b9",
  "draftSha256": "e275aa15369d81dd215b81a9a01eadcc9db4f530752d5e5bcfe0e504b7a800a5",
  "manifestPath": ".pipeline/technical-translations/batch-125/manifest.json",
  "manifestSha256": "1934910c02dbe893b786124f1d296d7adf9efbe921d40b3d2cfbceb8f70b4b33",
  "publishedAt": "2026-10-31T15:35:43.034Z",
  "updatedAt": "2026-10-31T15:35:43.034Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 125,
    "approvedAt": "2026-10-31T15:35:43.034Z",
    "basis": "User explicitly requested applying all missing technical-post languages, review, verification and deployment on 2026-11-01, with standing PR merge authorization. Human approval denotes publication authorization; linguistic review is performed by AI, not human/native review."
  }
}
---
**Refactoriser avec un agent IA commence par définir le comportement à préserver et le périmètre à modifier, puis vérifier le résultat avec les preuves d’exécution et le diff.** Une fonction plus courte ou l’affirmation de l’agent « les tests ont réussi » ne suffit pas à conclure. Vérifiez que valeurs de retour, exceptions et effets externes restent identiques, et que la vérification elle-même n’a pas été affaiblie.

Ce guide indépendant des outils s’adresse aux développeurs connaissant Git et l’exécution de tests. Il ne suppose aucune interface produit ni aucun modèle particulier. Les prompts ci-dessous sont des exemples rédigés à copier et adapter, pas des transcriptions d’un produit particulier ni des mesures de performance. Les résultats d’exécution de l’exemple Java sont identifiés séparément.

## Que doit inclure la première demande ?

[Martin Fowler définit le refactoring](https://refactoring.com/) comme un changement de structure interne préservant le comportement observable de l’extérieur. Si une modification de politique ou une correction de bug est nécessaire, distinguez-la du refactoring pour évaluer les différences de résultats avant et après.

Donnez à l’agent non seulement les fichiers cibles, mais aussi les appelants, les tests liés, les conventions du dépôt et les véritables commandes de vérification. Plutôt que d’exiger sans condition la lecture de tout le dépôt, commencez par les chemins utiles à cette décision. Lui faire décrire le comportement actuel et ses preuves avant toute modification peut réduire le risque d’élargir les changements à partir d’un malentendu.

La politique d’expédition de l’exemple ci-dessous comprend les **exigences définies pour l’illustration** suivantes. Ce n’est ni une politique de service réelle ni un compte rendu d’incident.

| Condition | Comportement à préserver |
| --- | --- |
| Sous-total de commande négatif | Lever `IllegalArgumentException("subtotal")` |
| Membre ou sous-total d’au moins 50 000 KRW | Frais d’expédition de base de 0 KRW |
| Sinon | Frais d’expédition de base de 3 000 KRW |
| Livraison sur une île ou dans une zone éloignée | Ajouter 3 000 KRW, même si l’expédition de base est gratuite |

Vous pouvez formuler la première demande à l’agent comme suit. Supposez que le code complet présenté plus loin a été enregistré sous `ShippingRefactorDemo.java`. Pour pratiquer l’édition avec un agent, copiez d’abord le corps de `before()` dans `after()`. Le code complet ci-dessous inclut le refactoring achevé pour comparaison.

```text
Lis before(), after() et main() dans ShippingRefactorDemo.java et analyse seulement.
Ne modifie pas encore les fichiers.

Objectif : réduire les branches imbriquées de after() tout en préservant le comportement des frais d’expédition de before().
Les montants d’entrée sont en KRW et utilisent long.
Vérifie le type et le message d’exception pour les montants négatifs, la limite de 50 000 KRW
et les combinaisons d’expédition de base gratuite et de supplément pour zone éloignée.

Fournis les preuves dans le code du comportement actuel, le périmètre de test déjà couvert,
les cas limites supplémentaires à vérifier et un changement minimal modifiant seulement after().
Ne devine ni ne modifie les politiques ambiguës.
```

Le résultat utile à ce stade est le comportement actuel pour chaque condition et les emplacements à changer, plutôt qu’un abstrait « plan d’amélioration de la qualité du code ». Par exemple, interpréter que « les membres paient toujours 0 KRW d’expédition » contredit le supplément des zones éloignées et doit être corrigé avant l’implémentation.

## Faire un petit changement et comparer le comportement

Cet exemple **sépare les calculs de frais de base et de supplément** des branches dupliquées. Il préserve entrées, sorties et exceptions existantes sans ajouter d’interface de stratégie ou de couche de configuration. Un petit changement permet aux personnes chargées de la revue de se concentrer sur la modification de structure et le maintien de la politique. [Conseils Google sur les petits changements](https://google.github.io/eng-practices/review/developer/small-cls.html)

![Lever la même exception pour un sous-total négatif, calculer les frais de base selon l’adhésion et le seuil gratuit, puis ajouter le supplément de zone éloignée et retourner le total](/assets/diagrams/technical/fr-2026-10-31-ai-agent-refactoring.svg)

Le schéma montre l’ordre de calcul de `after()` ci-dessous. Il ne représente pas le fonctionnement interne d’un outil IA. `before()` et `after()` ont été écrits pour l’illustration ; `main()` vérifie des valeurs attendues explicites et compare leurs résultats. Il s’exécute avec JDK 21 ou ultérieur sans dépendances externes.

```java
public class ShippingRefactorDemo {
    static final long FREE_THRESHOLD = 50_000;
    record Case(long subtotal, boolean member, boolean remote, long expected) {}

    static long before(long subtotal, boolean member, boolean remote) {
        if (subtotal < 0) throw new IllegalArgumentException("subtotal");
        if (member) {
            if (remote) return 3_000;
            return 0;
        }
        if (subtotal >= 50_000) {
            if (remote) return 3_000;
            return 0;
        }
        if (remote) return 6_000;
        return 3_000;
    }

    static long after(long subtotal, boolean member, boolean remote) {
        if (subtotal < 0) throw new IllegalArgumentException("subtotal");
        long base = (member || subtotal >= FREE_THRESHOLD) ? 0 : 3_000;
        long surcharge = remote ? 3_000 : 0;
        return base + surcharge;
    }

    static void equal(long actual, long expected) {
        if (actual != expected) {
            throw new AssertionError("expected=" + expected + ", actual=" + actual);
        }
    }

    public static void main(String[] args) {
        Case[] examples = {
            new Case(0, false, false, 3_000),
            new Case(49_999, false, false, 3_000),
            new Case(50_000, false, false, 0),
            new Case(0, true, false, 0),
            new Case(49_999, false, true, 6_000),
            new Case(50_000, false, true, 3_000),
            new Case(0, true, true, 3_000),
            new Case(Long.MAX_VALUE, false, true, 3_000)
        };
        for (Case c : examples) {
            equal(before(c.subtotal(), c.member(), c.remote()), c.expected());
            equal(after(c.subtotal(), c.member(), c.remote()), c.expected());
        }
        System.out.println("examples=" + examples.length);

        int comparisons = 0;
        long[] amounts = {0, 1, 49_999, 50_000, 50_001, Long.MAX_VALUE};
        for (long subtotal : amounts) {
            for (boolean member : new boolean[] {false, true}) {
                for (boolean remote : new boolean[] {false, true}) {
                    equal(after(subtotal, member, remote), before(subtotal, member, remote));
                    comparisons++;
                }
            }
        }
        System.out.println("comparisons=" + comparisons);

        int rejected = 0;
        for (boolean refactored : new boolean[] {false, true}) {
            try {
                if (refactored) after(-1, false, false);
                else before(-1, false, false);
                throw new AssertionError("Negative amount was accepted");
            } catch (IllegalArgumentException e) {
                if (!"subtotal".equals(e.getMessage())) throw new AssertionError(e);
                rejected++;
            }
        }
        System.out.println("negative-inputs=" + rejected);
    }
}
```

```sh
javac --release 21 ShippingRefactorDemo.java
java ShippingRefactorDemo
```

La sortie suivante a été obtenue avec Zulu JDK `21.0.1+12-LTS`. La version initiale, avec les mêmes corps dans `after()` et `before()`, et le refactoring achevé ci-dessous ont tous deux produit cette sortie.

```text
examples=8
comparisons=24
negative-inputs=2
```

Au lieu de Java `assert`, désactivable selon l’option `-ea`, le code lève directement `AssertionError` s’il trouve une différence. Les nombres rapportés comptent les cas spécifiés et les combinaisons d’entrées ; ils ne représentent pas la couverture d’une base de code de production entière.

Lorsque vous demandez l’implémentation, reliez les conditions vérifiées précédemment au périmètre d’édition et aux commandes d’exécution.

```text
Refactorise seulement after(), en préservant le contrat d’expédition établi ci-dessus.
Ne modifie pas before(), main(), les valeurs attendues ou FREE_THRESHOLD.
Préserve entrées et sorties publiques ainsi que types et messages d’exception ; n’ajoute aucune dépendance ni couche.
Si tu estimes des changements hors de ce fichier nécessaires, explique les raisons sans les appliquer.

Exécute javac --release 21 ShippingRefactorDemo.java et java ShippingRefactorDemo.
Fournis les commandes réellement exécutées, codes de sortie, sortie observée et diff des changements.
Si un contrôle échoue, isole et corrige la condition et la cause ; ne supprime pas les contrôles et n’ajuste pas les attentes pour le faire réussir.
```

Si l’environnement de l’agent ne peut ni modifier les fichiers ni exécuter les commandes, appliquez vous-même le patch proposé et exécutez les mêmes commandes. « Ne pas modifier » dans un prompt communique le périmètre du travail ; cela ne remplace pas les véritables permissions des outils ou restrictions d’accès aux fichiers.

## Tests réussis et comportement préservé sont-ils équivalents ?

Cet exemple vérifie 8 valeurs attendues explicites, compare les résultats avant/après pour 24 combinaisons d’entrées et vérifie les exceptions des deux méthodes pour les entrées négatives. Il ne prouve pas l’équivalence pour chaque entrée `long`. Utiliser seulement le résultat de `before()` comme réponse peut préserver des défauts existants ; utilisez aussi des valeurs attendues indépendantes et les exigences métier. Si vous découvrez un défaut existant, décidez séparément de sa correction et du comportement qui changera.

Vous pouvez aussi introduire un contre-exemple pour voir si la vérification détecte une différence pertinente. Par exemple, remplacer `subtotal >= FREE_THRESHOLD` dans `after()` par `subtotal > FREE_THRESHOLD` exclut de l’expédition de base gratuite les commandes non membres d’exactement 50 000 KRW. Le contrôle des valeurs attendues doit alors échouer.

L’exécution d’une copie temporaire avec uniquement cette condition limite modifiée incorrectement a bien échoué avec `AssertionError: expected=0, actual=3000`. Cela confirme que les contrôles détectent une erreur précise ; cela ne garantit pas la détection de chaque changement incorrect. Cette mutation n’est pas appliquée au code achevé de cet article.

Dans un vrai projet, vérifiez le comportement observable par les appelants au-delà des valeurs de retour : exceptions, requêtes et frontières de transaction en base, nombre et ordre des appels externes, résultats sérialisés et libération des ressources. La réussite de cet exemple de fonction pure ne vérifie pas les parcours de base ou HTTP. Si l’objectif est un gain de performance, des mesures distinctes avec entrées et environnement fixes sont aussi nécessaires.

## Commencer la revue finale par les changements, avant l’explication

Inspectez le diff et les résultats d’exécution avant de lire la description des changements de l’agent. Cherchez les modifications de fichiers inutiles, les tests supprimés ou ignorés, les exceptions absorbées et les dépendances sans rapport avec la fonctionnalité. `git diff --check` vérifie les erreurs d’espacement et problèmes similaires ; ce n’est pas un test du comportement métier.

Si un contexte de revue distinct est disponible, fournissez les exigences d’origine, le code avant/après, le diff et les preuves d’exécution plutôt que l’affirmation initiale de succès. Les revues peuvent aussi produire des constats incorrects : comparez chaque commentaire aux preuves du code et des exigences. La [documentation GitHub sur les limites des agents](https://docs.github.com/en/copilot/responsible-use/agents) explique aussi que code généré et commentaires de revue peuvent être inexacts.

```text
Examine ce changement sans le modifier.
Entrée : exigences des frais d’expédition, code avant/après, diff, commandes de test et résultats réels.

Trouve des contre-exemples changeant valeurs de retour, exceptions, limite de 50 000 KRW ou frais de zone éloignée.
Vérifie aussi les changements hors périmètre et les tests affaiblis.
Pour chaque constat, donne emplacement, entrée d’exemple, différence observable et preuves.
Ne prétends pas avoir exécuté des contrôles non réalisés.
```

Gardez la remise finale brève : décrivez la structure modifiée, le comportement préservé, les contrôles réellement exécutés et le périmètre restant à vérifier. Si un test échoue, précisez l’entrée en échec et le comportement attendu, puis resserrez à nouveau la correction ; si les changements grandissent, séparez-les en travaux distincts. **Un changement assez petit pour qu’une personne puisse expliquer pourquoi le comportement est préservé** reste une unité d’achèvement utile avec les agents IA.
