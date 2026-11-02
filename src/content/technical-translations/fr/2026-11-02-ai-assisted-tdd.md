---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2026-11-02-ai-assisted-tdd",
  "routeSlug": "2026-11-02-ai-assisted-tdd",
  "kind": "post",
  "title": "TDD assisté par IA : vérifier Red, Green et Refactor avec Java",
  "description": "Combiner IA et TDD avec des tests fondés sur les exigences, des échecs voulus, des implémentations minimales et la refactorisation. Exécuter des exemples Java et JUnit détectant les tests affaiblis et les régressions aux limites.",
  "categories": [
    "architecture"
  ],
  "tags": [
    "ai-agent",
    "tdd",
    "java",
    "junit",
    "testing",
    "refactoring"
  ],
  "sourcePath": "src/content/posts/en/2026-11-02-ai-assisted-tdd.md",
  "sourceSha256": "bfc69c72419b9b2b5ce2693c4111b12dd8f935ed3d1115dd350b837bed13bf80",
  "draftSha256": "7aa97f1d70c307d211675a30613c7751c4d9072615d3821af2ded4be13114989",
  "manifestPath": ".pipeline/technical-translations/batch-132/manifest.json",
  "manifestSha256": "9061c67686c9ea3bd8d21799f4c265ee716fee50940f1b6fc38c28a67de01dee",
  "publishedAt": "2026-11-02T03:04:44.245Z",
  "updatedAt": "2026-11-02T03:04:44.245Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 132,
    "approvedAt": "2026-11-02T03:04:44.245Z",
    "basis": "User requested completing missing multilingual technical posts, review, verification and deployment, then instructed continuing the next task on 2026-11-02, with standing blog PR merge/publication authorization. Human approval denotes user publication authorization; linguistic review is AI, not human/native review."
  }
}
---
**Pour combiner IA et TDD, déduisez les résultats attendus des exigences, observez l’échec d’un test, puis répétez de petites étapes d’implémentation et de refactorisation.** L’IA peut proposer tests et implémentations, mais les deux peuvent réussir en partageant la même incompréhension. Vérifiez l’origine de chaque attente et ce que rapporte réellement le lanceur de tests.

Le cycle TDD de base sélectionne le prochain comportement dans une liste de tests et répète Red → Green → Refactor. [L’explication du TDD par Martin Fowler](https://www.martinfowler.com/bliki/TestDrivenDevelopment.html) souligne la liste de tests, les petits cycles et la refactorisation. L’exemple Java ci-dessous ajoute l’IA à ce processus sans dépendre d’un outil particulier. Les prompts sont des exemples rédigés, pas la transcription d’un produit IA ni une mesure de productivité.

## Définir le comportement attendu avant de montrer une implémentation

L’exemple est une fonction pure qui calcule le stock restant à partir du stock et de la quantité demandée. Ces exigences sont illustratives et ne constituent pas une véritable politique de service. La fonction ne met pas à jour de base de données, ne persiste pas de réservations et n’assure pas l’atomicité entre requêtes concurrentes.

| Condition | Comportement attendu |
| --- | --- |
| Stock 10, quantité demandée 3 | Renvoyer 7 |
| Stock 10, quantité demandée 10 | Renvoyer 0 |
| Demande supérieure au stock, y compris une demande de 1 avec un stock de 0 | `IllegalStateException("insufficient_stock")` |
| Stock négatif | `IllegalArgumentException("stock")` |
| Quantité demandée nulle ou négative | `IllegalArgumentException("requested")` |
| Les deux entrées sont invalides | Valider le stock en premier |
| Stock `Integer.MAX_VALUE`, quantité demandée 1 | Renvoyer `Integer.MAX_VALUE - 1` |

Ce tableau est l’oracle de test. Lire une implémentation générée par IA et copier sa valeur de retour dans une assertion peut aussi copier son défaut. Commencez par les exigences et le contrat d’API :

```text
N’implémente rien pour le moment.
Propose des cas de test pour StockPolicy.remaining(int stock, int requested).
Relie chaque entrée, résultat attendu ou exception à une règle du tableau des exigences.

N’introduis ni stockage externe ni base de données.
Sépare les entrées normales, les limites et les entrées invalides. À la première itération,
écris un seul test : demander 3 sur un stock de 10 renvoie 7.
N’invente pas de politique lorsque les exigences sont ambiguës.
```

## Relier Red, Green et Refactor par de petites exécutions

![Choisir le prochain test dans les exigences, vérifier son échec voulu, le réussir avec une implémentation minimale, refactoriser en préservant les tests, puis revenir au test suivant](/assets/diagrams/technical/fr-2026-11-02-ai-assisted-tdd.svg)

Le schéma décrit un déroulement contrôlé par la personne qui développe, pas le fonctionnement interne de l’IA. Observez l’échec du nouveau comportement, puis ajoutez une implémentation minimale. Après refactorisation, relancez les mêmes tests avant de choisir un autre cas. Si le téléchargement des dépendances ou l’environnement d’exécution a causé l’échec, corrigez ce problème et relancez la même étape.

L’environnement de reproduction est **JDK 17.0.8.1, Gradle 8.4 et JUnit Jupiter 5.12.2**. Cette combinaison fixe consigne l’environnement utilisé ; ce n’est pas une recommandation de versions actuelles pour la production. Créez les fichiers suivants dans un répertoire vide. La première exécution peut télécharger les dépendances de test depuis Maven Central ; les tests eux-mêmes n’appellent aucune API externe ni base de données. Dans un projet existant, suivez ses politiques de Gradle Wrapper et de gestion des dépendances.

### `settings.gradle`

```groovy
rootProject.name = 'ai-tdd-stock'
```

### `build.gradle`

```groovy
plugins { id 'java' }
repositories { mavenCentral() }
dependencies {
    testImplementation platform('org.junit:junit-bom:5.12.2')
    testImplementation 'org.junit.jupiter:junit-jupiter'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
java {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
}
test {
    useJUnitPlatform()
    testLogging { events 'passed', 'failed' }
}
```

Dans JUnit, `@Test`, `assertEquals` et `assertThrows` vérifient les valeurs de retour et les exceptions. Capturez l’objet exception pour vérifier aussi son message. Consultez le [guide utilisateur de JUnit 5.12.2](https://docs.junit.org/5.12.2/user-guide/) et le [guide des tests JVM de Gradle](https://docs.gradle.org/current/userguide/java_testing.html).

### Premier test : `src/test/java/StockPolicyTest.java`

```java
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class StockPolicyTest {
    @Test
    void reservesPartOfStock() {
        assertEquals(7, StockPolicy.remaining(10, 3));
    }
}
```

### Premier Red : `src/main/java/StockPolicy.java`

Créez une API appelable dont l’implémentation ne soustrait encore rien. Exécutez le test et vérifiez qu’il échoue parce qu’il attend `7` mais reçoit `10`.

```java
public class StockPolicy {
    public static int remaining(int stock, int requested) {
        return stock;
    }
}
```

Exécutez cette commande depuis la racine du projet. À cette étape, un échec de test et un code de sortie non nul sont attendus.

```sh
gradle --no-daemon --console=plain clean test
```

Distinguez les erreurs de téléchargement ou de compilation d’un échec du comportement exigé. Le Red voulu ici est la différence d’assertion dans `reservesPartOfStock()`. Un lanceur défectueux ne prouve pas que le comportement a été testé.

### Premier Green : remplacer le même `StockPolicy.java`

```java
public class StockPolicy {
    public static int remaining(int stock, int requested) {
        return stock - requested;
    }
}
```

Relancer la même commande fait réussir le premier test. Cette implémentation ne traite toujours pas les entrées négatives ou le stock insuffisant. Réussir le premier test ne termine pas la fonctionnalité ; ajoutez l’exigence suivante.

Vous pouvez donner à l’IA la limite de modification suivante :

```text
Le test en échec est reservesPartOfStock : expected=7, actual=10.
Modifie uniquement StockPolicy.java pour réussir ce test.
Ne change ni les tests, ni les valeurs attendues, ni les paramètres de compilation.
N’ajoute aucune base de données, interface ou couche de configuration non demandée.
Rapporte la commande, le code de sortie et les résultats de tests réellement vérifiés.
```

### Red suivant : ajouter des méthodes dans la classe de test existante

Ajoutez ces méthodes **à l’intérieur** de l’accolade fermante finale de `StockPolicyTest`. En TDD réel, ajoutez un cas à la fois et répétez le cycle. L’article regroupe les cas restants en un bloc pour garder les fichiers de reproduction concis.

```java
    @Test
    void reservesAllStock() {
        assertEquals(0, StockPolicy.remaining(10, 10));
    }

    @Test
    void rejectsInsufficientStock() {
        var error = assertThrows(IllegalStateException.class,
                () -> StockPolicy.remaining(2, 3));
        assertEquals("insufficient_stock", error.getMessage());
    }

    @Test
    void rejectsEmptyStock() {
        var error = assertThrows(IllegalStateException.class,
                () -> StockPolicy.remaining(0, 1));
        assertEquals("insufficient_stock", error.getMessage());
    }

    @Test
    void rejectsNegativeStock() {
        var error = assertThrows(IllegalArgumentException.class,
                () -> StockPolicy.remaining(-1, 1));
        assertEquals("stock", error.getMessage());
    }

    @Test
    void rejectsZeroRequest() {
        var error = assertThrows(IllegalArgumentException.class,
                () -> StockPolicy.remaining(10, 0));
        assertEquals("requested", error.getMessage());
    }

    @Test
    void rejectsNegativeRequest() {
        var error = assertThrows(IllegalArgumentException.class,
                () -> StockPolicy.remaining(10, -1));
        assertEquals("requested", error.getMessage());
    }

    @Test
    void validatesStockBeforeRequest() {
        var error = assertThrows(IllegalArgumentException.class,
                () -> StockPolicy.remaining(-1, 0));
        assertEquals("stock", error.getMessage());
    }

    @Test
    void supportsMaximumStock() {
        assertEquals(Integer.MAX_VALUE - 1,
                StockPolicy.remaining(Integer.MAX_VALUE, 1));
    }
```

Exécuter ce bloc supplémentaire avec la première implémentation Green produit 6 échecs sur 9 tests.

### Green pour les cas supplémentaires : remplacer `StockPolicy.java`

```java
public class StockPolicy {
    public static int remaining(int stock, int requested) {
        if (stock >= 0) {
            if (requested > 0) {
                if (requested <= stock) {
                    return stock - requested;
                }
                throw new IllegalStateException("insufficient_stock");
            }
            throw new IllegalArgumentException("requested");
        }
        throw new IllegalArgumentException("stock");
    }
}
```

Utilisez la même commande pour vérifier que les 9 tests réussissent. Cette implémentation satisfait désormais les comportements spécifiés. Simplifiez ensuite les branches imbriquées en préservant les tests.

### Refactor : utiliser des clauses de garde dans le même fichier

```java
public class StockPolicy {
    public static int remaining(int stock, int requested) {
        if (stock < 0) throw new IllegalArgumentException("stock");
        if (requested <= 0) throw new IllegalArgumentException("requested");
        if (requested > stock) throw new IllegalStateException("insufficient_stock");
        return stock - requested;
    }
}
```

L’imbrication est réduite en préservant l’ordre de validation, les valeurs de retour et les exceptions. N’introduisez pas de nouvelle politique à cette étape. Pour demander une refactorisation à l’IA, précisez le comportement à préserver et le périmètre d’exécution :

```text
Les 9 tests réussissent actuellement.
Remplace uniquement les branches imbriquées de StockPolicy.java par des clauses de garde.
Préserve la validation du stock avant celle de la quantité demandée,
les valeurs de retour, types d’exception, messages et tests existants.
Exécute la même suite complète de tests avant et après le changement,
et rapporte les résultats et le diff.
```

Chaque version du code, du premier Red à Refactor, a été exécutée séparément. Les résultats suivants ont été lus dans les rapports XML JUnit :

| Étape | Tests | Échecs | Ignorés | Code de sortie Gradle |
| --- | ---: | ---: | ---: | ---: |
| Premier Red | 1 | 1 | 0 | 1 |
| Premier Green | 1 | 0 | 0 | 0 |
| Cas supplémentaires Red | 9 | 6 | 0 | 1 |
| Cas supplémentaires Green | 9 | 0 | 0 | 0 |
| Refactor | 9 | 0 | 0 | 0 |

Le rapport HTML est généré dans `build/reports/tests/test/index.html` ; le XML exploitable par machine se trouve sous `build/test-results/test/`. Ces résultats vérifient une fonction locale de politique. Ils ne mesurent ni la qualité d’un produit IA, ni la productivité, ni la justesse d’un système de production.

## Tests et implémentations peuvent se tromper ensemble

La **priorité de validation** lorsque le stock et la demande sont invalides est fixée par `validatesStockBeforeRequest()`. Sans ce cas, une régression inversant la priorité des messages d’exception pourrait passer inaperçue. Plutôt que d’ajouter seulement des exemples d’entrées normales, vérifiez que les règles du tableau des exigences ont des tests correspondants.

Vous pouvez aussi vérifier que les tests détectent les régressions aux limites. Remplacer à tort `requested > stock` par `requested >= stock` dans l’implémentation finale doit faire échouer `reservesAllStock()`. Remplacer `requested <= 0` par `requested < 0` doit faire échouer `rejectsZeroRequest()`. Une mutation inversant l’ordre de validation des entrées a aussi été exécutée et a fait échouer `validatesStockBeforeRequest()`. Les trois mutations ont réellement été exécutées ; cela ne garantit pas la détection de tous les défauts.

Pour une revue assistée par IA, fournissez à nouveau les exigences originales et demandez quelle règle chaque test vérifie. Un autre agent peut reproduire la même erreur s’il partage les mêmes exigences erronées. Séparer les rôles et établir indépendamment le comportement attendu sont deux préoccupations distinctes.

```text
Compare le tableau original des exigences aux tests actuels.
Ne modifie encore ni les tests ni l’implémentation.
Identifie les règles vérifiées, les règles manquantes, les limites et les conditions non observées.
Vérifie si un test a simplement copié la sortie de l’implémentation actuelle
comme résultat attendu.
Pour les changements proposés, relie d’abord chacun à sa règle et à ses preuves.
```

## Empêcher l’IA d’affaiblir la vérification pour faire réussir les tests

Supprimer un test en échec, l’ignorer avec `@Disabled`, adapter les attentes à une implémentation défectueuse ou absorber toutes les exceptions peut produire du vert sans satisfaire les exigences. Lorsque les exigences restent identiques pendant la refactorisation, préservez le comportement attendu. Si un test est lui-même erroné, établissez la politique et les preuves, puis distinguez cette correction d’un changement d’implémentation. [Les recommandations GitHub pour examiner le code généré par IA](https://docs.github.com/en/copilot/tutorials/review-ai-generated-code) conseillent aussi de rechercher les tests supprimés ou ignorés et les écarts par rapport aux exigences visées.

Distinguez l’affirmation de l’IA selon laquelle les tests réussissent des résultats du lanceur. Examinez la commande réelle, le code de sortie, les rapports JUnit et le diff. Zéro test exécuté ou une exécution partielle ne constitue pas une réussite complète. En CI, exécutez l’implémentation finale et la suite complète avec les conditions ordinaires de succès. Gardez le harnais pédagogique vérifiant les échecs Red attendus séparé de la CI normale, et ne faites pas réussir la CI en ignorant systématiquement les commandes en échec.

Pour le code existant, obtenez d’abord des tests décrivant le comportement actuel, puis choisissez un comportement à changer. Cette séquence et ses critères de préservation rejoignent la [refactorisation par agent IA](/en/posts/2026-10-31-ai-agent-refactoring/). Tests et compilations exécutent aussi du code : limitez donc répertoires de travail et identifiants comme indiqué dans les [limites de permissions des agents IA](/en/posts/2026-11-01-ai-agent-permission-boundaries/).

Étendre cet exemple à de véritables réservations de stock nécessite des tests d’intégration distincts pour les requêtes concurrentes, transactions, demandes dupliquées et nouvelles tentatives. Réussir ces 9 tests unitaires de fonction ne démontre pas une protection contre la survente.
