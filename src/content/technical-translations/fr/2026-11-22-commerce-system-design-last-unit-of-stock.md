---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2026-11-22-commerce-system-design-last-unit-of-stock",
  "routeSlug": "2026-11-22-commerce-system-design-last-unit-of-stock",
  "kind": "post",
  "title": "Conception d’un système e-commerce : qui obtient le dernier article en stock ?",
  "description": "Prenez le dernier article en stock comme exemple pour examiner les réservations par SKU, le rapprochement des paiements et les remboursements après libération d’une réservation.",
  "categories": [
    "architecture"
  ],
  "tags": [
    "ecommerce",
    "inventory",
    "payments",
    "transactional-outbox"
  ],
  "sourcePath": "src/content/posts/en/2026-11-22-commerce-system-design-last-unit-of-stock.md",
  "sourceSha256": "63b33b1222e2cc6c885b4f2d63fb1a3f2727041b8710e7bf8ed7b335b6f8b9d6",
  "draftSha256": "b6bc68c6574a31be4abf6eeed8f0934e866b3c5fd1aba4681517c55cc601d54e",
  "manifestPath": ".pipeline/technical-translations/batch-185/manifest.json",
  "manifestSha256": "3281e1d3e7c9b3abbb6c101d911dd0fcdee7dd54f7034838135f391123b6fb44",
  "publishedAt": "2026-11-23T00:19:14.218Z",
  "updatedAt": "2026-11-23T00:19:14.218Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 185,
    "approvedAt": "2026-11-23T00:19:14.218Z",
    "basis": "The site owner explicitly requested missing supported locales for the eight articles published in PRs #177–#184. This authorizes publication of the 48 editions enumerated in this batch."
  }
}
---

**Lorsque deux clients essaient d’acheter le dernier exemplaire d’un produit, une seule de leurs commandes doit pouvoir le réserver.** Si la boutique réserve l’article puis perd la réponse du prestataire de paiement, la commande reste en attente pendant la vérification. Si le paiement est confirmé après la libération de la réservation, la boutique laisse la commande annulée et demande un remboursement. Suivre un achat permet de voir quelles données relèvent du catalogue, du stock, des commandes et des paiements.

L’exemple suppose un marchand de biens physiques qui reçoit un paiement en wons sud-coréens (KRW) par commande et expédie depuis un entrepôt. Il traite les annulations et remboursements liés aux paiements indéterminés ou confirmés tardivement. Les règlements des places de marché, les expéditions partielles et les retours sont hors de son périmètre.

## Stock affiché sur la fiche produit et stock réservé à la commande

Un **produit** est la fiche du catalogue que voit le client. Un **SKU** (unité de gestion des stocks) est l’unité suivie par la boutique dans les commandes et dans le stock. Les variantes blanche et noire d’un même clavier ont des SKU distincts. La fiche produit affiche la disponibilité au moment de la consultation. Si le module de stock ne répond pas, la fiche continue d’afficher le produit avec le message « Vérification du stock ». Ajouter un article au panier ne modifie pas le stock.

| Responsabilité | Données que le module peut modifier | Exemple |
| --- | --- | --- |
| Catalogue et prix | Produits, SKU, disponibilité à la vente et prix unitaires actuels | Modifier le prix unitaire du clavier noir `KB-BLK` |
| Stock | Stock physique par entrepôt, réservations, affectations à l’expédition | Réserver un `KB-BLK` pour une commande donnée |
| Commandes | Acheteur, lignes et montants lors de l’achat, état de la commande | Enregistrer les quantités, prix unitaires, répartition des remises et frais de livraison de `O-42` |
| Paiements | Tentatives de paiement, ID de transaction du prestataire, états du paiement et du remboursement | Rapprocher le résultat du prestataire pour la tentative `P-1` |
| Expédition | Demandes de préparation et progression | Prélever les articles après le paiement et l’affectation du stock |

Juste avant le passage de commande, le serveur vérifie que les articles sont toujours en vente et vérifie de nouveau leurs prix. Il identifie l’acheteur à partir de la session authentifiée et calcule le total selon ses propres tarifs, remises et règles de livraison. Si le clavier noir coûtait 39 000 KRW lors de l’ajout au panier et coûte maintenant 42 000 KRW, la boutique affiche le nouveau montant et demande une confirmation. À la création de la commande, le serveur vérifie que la version du prix acceptée correspond à celle qu’il applique. La commande conserve le SKU, le nom de l’option, la quantité, le prix unitaire, les remises, les frais de livraison et la devise. Avec un nouveau prix unitaire de 42 000 KRW, une remise de 2 000 KRW et des frais de livraison de 3 000 KRW, le serveur envoie 43 000 KRW au prestataire. La commande enregistrée doit garder le montant accepté même si le produit change de nom ou baisse de prix le lendemain. C’est la séparation à introduire lorsque vous prolongez [l’exemple Spring Boot de recherche de produits](/en/posts/2026-11-22-spring-boot-4-2-restclient-migration/) de l’affichage du produit à la prise de commande.

## Quelles opérations réunir dans une seule transaction ?

Commencez par **des modules distincts dans une même application** pour le catalogue, le stock, les commandes et les paiements. Ils partagent une base de données, mais chaque module maîtrise les règles d’écriture de ses tables. La commande et la réservation peuvent ainsi être validées dans une seule transaction locale. Appelez le prestataire externe après cette validation.

1. **Créer la commande et réserver le stock.** Identifiez les nouvelles tentatives par l’acheteur et la clé de requête de commande. Traitez une même clé avec des données différentes comme un conflit. Le module de stock vérifie les quantités disponibles en verrouillant la ligne du SKU ou par une mise à jour conditionnelle. Pour plusieurs SKU, enregistrez les lignes, les réservations et la tentative de paiement ensemble une fois tous les articles réservés. Si un seul article manque, annulez la transaction entière et signalez le manque de stock. Enregistrez la tâche permettant de reprendre la demande de paiement dans la même transaction locale.
2. **Appeler le prestataire de paiement.** Envoyez la demande avec une clé d’idempotence du prestataire liée à l’ID de la tentative enregistrée. Si le serveur s’arrête juste après l’appel, il doit pouvoir retrouver l’enregistrement et rapprocher la même tentative. Si la réponse est perdue, consultez la transaction existante auprès du prestataire. Renvoyez la demande uniquement dans les limites des garanties du prestataire pour la même clé et les mêmes paramètres. Continuez à utiliser la même tentative tant que le résultat reste indéterminé. [Documentation Stripe sur les requêtes idempotentes](https://docs.stripe.com/api/idempotent_requests)
3. **Appliquer le résultat.** Vérifiez la signature du webhook avant d’enregistrer l’événement, ou consultez la transaction depuis le serveur. Vérifiez la commande, la tentative de paiement, le compte du marchand, le montant et la devise. Verrouillez la commande et la réservation. Lisez leurs états actuels, puis enregistrez l’état du paiement, le changement de stock et les tâches de suivi dans une même transaction. Écrivez la demande d’expédition ou de remboursement dans une outbox au cours de cette même validation. [Règles de livraison des webhooks Stripe](https://docs.stripe.com/webhooks#event-delivery-behaviors) · [Modèle d’outbox transactionnelle d’AWS](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)

Ici, **stock disponible = stock physique − réservations actives − affectations à l’expédition**. Lorsqu’un paiement confirme une réservation, retirez la quantité réservée et ajoutez la même quantité à celle affectée à l’expédition. À l’expédition, réduisez le stock physique et la quantité affectée. Si deux commandes parviennent en même temps alors qu’il ne reste qu’un article, la seconde doit voir un stock disponible nul après la validation de la première réservation. Vérifiez cette règle avec des transactions qui se chevauchent dans la base réelle.

## Traiter les paiements indéterminés et tardifs

![Le système lit le résultat de paiement vérifié et l’état de la commande. Un résultat indéterminé conserve la réservation, et une clôture confirmée sans débit la libère. Un paiement confirmé déclenche une demande d’expédition si le stock est réservé, ou un remboursement si la réservation a été libérée. Appliquer un résultat déjà traité ne crée aucune tâche en double.](/assets/diagrams/technical/fr-2026-11-22-commerce-system-design-last-unit-of-stock.svg)

Le schéma montre comment la boutique applique les résultats du paiement après avoir réservé le stock. Si l’état de paiement enregistré est déjà `PAID` ou `REFUND_PENDING`, le code le conserve et ne crée aucune tâche de suivi.

La commande, le paiement et la réservation de stock ont chacun leur propre état. La boutique les combine dans un message compréhensible. Par exemple, si le prestataire tarde à répondre, la commande reste `PENDING_PAYMENT`, le paiement `UNKNOWN` et la réservation `HELD`. Affichez « Vérification du paiement » et proposez au client de consulter à nouveau la même commande.

| Situation | État enregistré et suivi |
| --- | --- |
| Paiement confirmé, stock réservé | Commande `CONFIRMED`, paiement `PAID`, stock `ALLOCATED`. Enregistrer une demande d’expédition |
| Réponse perdue ou traitement toujours en cours chez le prestataire | Commande `PENDING_PAYMENT`, paiement `UNKNOWN`, stock `HELD`. Vérifier à nouveau le paiement existant |
| Clôture de la transaction confirmée sans débit | Commande `CANCELLED`, paiement `CLOSED_UNPAID`, réservation `RELEASED` |
| Paiement confirmé après une libération exceptionnelle | Commande `CANCELLED`, paiement `REFUND_PENDING`, réservation `RELEASED`. Enregistrer une demande de remboursement |

Si la réservation expire alors que le résultat du paiement est indéterminé, consultez d’abord le prestataire. Si le résultat reste indéterminé, consignez le cas pour qu’un opérateur puisse retrouver et rapprocher la transaction. Si la confirmation du paiement arrive après une libération exceptionnelle, cette conception demande un remboursement et laisse la réservation libérée. Enregistrez le remboursement comme réussi après confirmation du prestataire. Fixez la durée de réservation et les personnes habilitées à autoriser une libération exceptionnelle selon la vitesse d’écoulement du stock et les conditions du contrat du prestataire.

Dédupliquez les livraisons répétées par ID d’événement webhook. Protégez aussi chaque paiement contre les demandes d’expédition en double, même avec des ID d’événement différents. Par exemple, ajoutez une contrainte d’unicité sur `order_id` et le type de tâche dans l’outbox d’expédition, et sur `payment_attempt_id` et le type de tâche dans celle des remboursements. La publication de l’outbox peut être réessayée. Les traitements d’expédition et de remboursement utilisent donc le même ID de tâche pour éviter les doubles exécutions. Pour réessayer un remboursement auprès du prestataire, utilisez une clé d’idempotence propre au remboursement, prise en charge par ce prestataire. Un événement plus ancien indiquant que le paiement est en cours ne modifie pas l’état confirmé. Rapprochez les résultats dont les ID ou les montants diffèrent, ou qui contredisent l’historique confirmé, avant de les appliquer. [Recommandations Stripe sur les webhooks en double](https://docs.stripe.com/webhooks#handle-duplicate-events) · [Modèle d’outbox transactionnelle d’AWS](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)

## Vérifier les transitions de paiement en Java

Enregistrez le code ci-dessous sous `CheckoutPolicy.java` et lancez `java CheckoutPolicy.java`. L’exemple reçoit **le résultat vérifié côté serveur d’une tentative de paiement** liée à une commande. `CLOSED_UNPAID` indique que le prestataire a confirmé la fin de la transaction sans débit. Un simple message de refus ne suffit pas comme preuve. Le code suppose que la commande et sa réservation sont dans des états cohérents. Une commande en attente de paiement a une réservation active, et celle d’une commande annulée a déjà été libérée. L’appelant vérifie les ID et les montants et rapproche les résultats qui se contredisent. Le code renvoie l’état suivant et les tâches de suivi à enregistrer.

```java
public class CheckoutPolicy {
    enum Order { PENDING_PAYMENT, CONFIRMED, CANCELLED }
    enum Payment { PENDING, UNKNOWN, PAID, CLOSED_UNPAID, REFUND_PENDING }
    enum Reservation { HELD, ALLOCATED, RELEASED }
    enum Result { UNRESOLVED, CLOSED_UNPAID, PAID }
    enum Effect { NONE, REQUEST_FULFILLMENT, REQUEST_REFUND }

    record State(Order order, Payment payment, Reservation reservation) {}
    record Decision(State state, Effect effect) {}

    static Decision apply(State current, Result result) {
        if (current.payment() == Payment.PAID
                || current.payment() == Payment.REFUND_PENDING) {
            return new Decision(current, Effect.NONE);
        }

        if (current.order() == Order.CANCELLED) {
            return switch (result) {
                case PAID -> new Decision(
                    new State(Order.CANCELLED, Payment.REFUND_PENDING, Reservation.RELEASED),
                    Effect.REQUEST_REFUND);
                case CLOSED_UNPAID -> new Decision(
                    new State(Order.CANCELLED, Payment.CLOSED_UNPAID, Reservation.RELEASED),
                    Effect.NONE);
                case UNRESOLVED -> new Decision(current, Effect.NONE);
            };
        }

        return switch (result) {
            case PAID -> new Decision(
                new State(Order.CONFIRMED, Payment.PAID, Reservation.ALLOCATED),
                Effect.REQUEST_FULFILLMENT);
            case CLOSED_UNPAID -> new Decision(
                new State(Order.CANCELLED, Payment.CLOSED_UNPAID, Reservation.RELEASED),
                Effect.NONE);
            case UNRESOLVED -> new Decision(
                new State(Order.PENDING_PAYMENT, Payment.UNKNOWN, Reservation.HELD),
                Effect.NONE);
        };
    }

    static void check(String label, Decision expected, Decision actual) {
        if (!expected.equals(actual)) {
            throw new AssertionError(label + ": " + actual);
        }
        System.out.println("PASS " + label);
    }

    public static void main(String[] args) {
        State held = new State(Order.PENDING_PAYMENT, Payment.PENDING, Reservation.HELD);
        State unknown = new State(Order.PENDING_PAYMENT, Payment.UNKNOWN, Reservation.HELD);
        State paid = new State(Order.CONFIRMED, Payment.PAID, Reservation.ALLOCATED);
        State closed = new State(
            Order.CANCELLED, Payment.CLOSED_UNPAID, Reservation.RELEASED);
        State released = new State(Order.CANCELLED, Payment.UNKNOWN, Reservation.RELEASED);
        State refundPending = new State(
            Order.CANCELLED, Payment.REFUND_PENDING, Reservation.RELEASED);

        check("unresolved retains hold", new Decision(unknown, Effect.NONE),
            apply(held, Result.UNRESOLVED));
        check("paid allocates stock", new Decision(paid, Effect.REQUEST_FULFILLMENT),
            apply(unknown, Result.PAID));
        check("duplicate paid has no effect", new Decision(paid, Effect.NONE),
            apply(paid, Result.PAID));
        check("old unresolved does not reopen payment", new Decision(paid, Effect.NONE),
            apply(paid, Result.UNRESOLVED));
        check("closed unpaid releases hold", new Decision(closed, Effect.NONE),
            apply(unknown, Result.CLOSED_UNPAID));
        check("late paid requests refund", new Decision(refundPending, Effect.REQUEST_REFUND),
            apply(released, Result.PAID));
        check("duplicate late paid has no effect", new Decision(refundPending, Effect.NONE),
            apply(refundPending, Result.PAID));
    }
}
```

Les sept vérifications suivantes ont été exécutées avec JDK 21.0.1. Appliquer deux fois la confirmation du paiement n’a créé aucune tâche supplémentaire. Un paiement confirmé après la libération de la réservation a renvoyé une demande de remboursement.

```text
PASS unresolved retains hold
PASS paid allocates stock
PASS duplicate paid has no effect
PASS old unresolved does not reopen payment
PASS closed unpaid releases hold
PASS late paid requests refund
PASS duplicate late paid has no effect
```

Deux situations de concurrence doivent être testées séparément dans l’implémentation. Lorsque deux commandes tentent de réserver le dernier article au même moment, une seule doit réussir. Si le traitement de l’expiration et la confirmation de paiement se présentent ensemble pour une commande, le système ne doit enregistrer qu’une seule issue : l’expédition si le stock est toujours réservé, ou un remboursement après libération. L’exemple Java séquentiel laisse à des tests distincts les accès concurrents à la base, l’intégration au prestataire et les paiements en production.

Envisagez un service de stock distinct si davantage d’entrepôts doivent gérer les stocks, ou si ce service doit être déployé ou dimensionné indépendamment. Les bases des commandes et des stocks perdent alors leur transaction locale commune. Le service de stock doit appliquer chaque ID de réservation une seule fois, et le module de commande doit pouvoir consulter le résultat ou compenser un échec. Les règles métier restent les mêmes de part et d’autre de la frontière : empêcher les ventes au-delà du stock et n’appliquer qu’une fois chaque paiement et chaque expédition.
