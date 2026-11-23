---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2026-11-23-commerce-storefront-design",
  "routeSlug": "2026-11-23-commerce-storefront-design",
  "kind": "post",
  "title": "Concevoir une boutique en ligne, de la sélection des produits à la confirmation du paiement",
  "description": "Définissez ce que les acheteurs peuvent voir et faire de la liste des produits au détail de la commande. Guidez-les au retour du paiement en fonction des états de commande et de paiement sur le serveur.",
  "categories": [
    "architecture"
  ],
  "tags": [
    "ecommerce",
    "storefront",
    "checkout",
    "order-management",
    "payments"
  ],
  "sourcePath": "src/content/posts/en/2026-11-23-commerce-storefront-design.md",
  "sourceSha256": "fde9deae56ab163d6fad0ea42a0136927d901a84ecd0111e5006b0eb21aa00ce",
  "draftSha256": "c0005bb36d8567e92c5df5e8fae5c00fdb84944efbc17a83d2e89c8924e63218",
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

**Lorsqu’un acheteur revient du paiement sur une page vide, il veut d’abord savoir si son compte a été débité.** Affichez un écran où il peut vérifier le résultat pour la commande existante. De la fiche produit à l’historique des commandes, associez les faits que chaque écran peut confirmer à une action que l’acheteur peut réaliser.

Le [guide de l’interface d’administration e-commerce](/en/posts/2026-11-23-commerce-admin-screen/) suit un opérateur qui consulte une commande dont le paiement n’est pas confirmé. Ici, nous examinons la même situation du point de vue de l’acheteur. Supposons une boutique gérée par un seul marchand qui vend des biens physiques en wons sud-coréens et les expédie. Les acheteurs passent commande avec un compte. Les règles de remise et de livraison servent d’exemple.

## Que décide l’acheteur sur chaque écran ?

| Écran | À afficher en premier | Ce que l’acheteur peut faire ensuite |
| --- | --- | --- |
| Liste des produits et recherche | Noms et photos des produits, prix comparables et filtres actifs | Affiner les résultats ou ouvrir une fiche produit |
| Fiche produit | Prix et disponibilité de la variante sélectionnée, conditions de livraison | Choisir une variante et une quantité, puis ajouter au panier |
| Panier | Variante, quantité et montant de chaque article, total estimé et articles qui empêchent de passer commande | Modifier les quantités et les articles, puis passer commande |
| Passage de commande | Adresse de livraison, frais de livraison, remises, montant final et accès aux modifications | Vérifier les conditions et demander le paiement |
| Détail de la commande | Numéro de commande, états du paiement, de l’expédition et du remboursement, historique des modifications | Vérifier le résultat ou suivre l’envoi selon l’état actuel |

Si la liste indique « À partir de 39 000 ₩ », affichez le prix réel dès que l’acheteur sélectionne une variante sur la fiche produit. Identifiez les variantes épuisées par du texte. Si une recherche ne donne aucun résultat, affichez les filtres actifs et permettez de les effacer. Si la recherche ne se charge pas, proposez de réessayer.

Appliquez la même règle que dans le [guide e-commerce sur les réservations de stock](/en/posts/2026-11-22-commerce-system-design-last-unit-of-stock/). La fiche produit affiche le stock au moment de la consultation et le panier conserve les choix de l’acheteur. Le serveur réserve le stock en créant la commande. Si une autre personne réserve le dernier article en premier, signalez dans le panier l’article et la variante concernés. Conservez les autres articles et l’adresse de livraison saisie.

## Permettre aux acheteurs de vérifier et de modifier les détails avant de payer

À côté du total définitif, laissez les acheteurs vérifier et modifier leurs variantes, quantités et adresse de livraison. Nommez le bouton d’après l’action réelle, par exemple **« Payer 43 000 ₩ »**. Les recommandations WCAG sur la prévention des erreurs dans les transactions financières décrivent comment permettre aux utilisateurs de vérifier et de corriger leurs informations avant l’envoi. [Recommandations du W3C sur la prévention des erreurs lors des transactions financières](https://www.w3.org/WAI/WCAG22/Understanding/error-prevention-legal-financial-data.html)

Si un clavier coûtait 39 000 ₩ à l’ajout au panier et coûte 42 000 ₩ au passage de commande, nommez l’article concerné. Par exemple, « Le prix du clavier noir est passé de 39 000 ₩ à 42 000 ₩. » Recalculez les remises et les frais de livraison, affichez le nouveau total et laissez l’acheteur le confirmer avant de demander le paiement. Lors de la création de la commande, le serveur compare le montant confirmé par l’acheteur au montant qu’il va débiter et consigne les conditions de la transaction. [Comment la base de données e-commerce conserve les montants des commandes](/en/posts/2026-11-22-commerce-database-design/)

Sur mobile, placez les liens de modification de l’adresse et des articles près des détails correspondants, et le montant final près du bouton de paiement. Si le bouton est fixé en bas, assurez-vous que l’acheteur peut faire défiler la page jusqu’au dernier champ et aux éventuels messages d’erreur. Les technologies d’assistance peuvent aussi annoncer une mise à jour sans déplacer le focus, comme un changement du total du panier ou le résultat d’une vérification du paiement. Vous pouvez, par exemple, ajouter `role="status"` à la zone qui affiche le résultat. [Recommandations du W3C sur les messages d’état](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html)

## Vérifier le résultat du paiement sur le serveur

![Rechercher la commande existante au retour du paiement. Distinguer le chargement d’un échec de consultation. Selon le résultat du paiement et de la commande, proposer une actualisation, le suivi de l’envoi, la liste des produits ou les informations de remboursement.](/assets/diagrams/technical/fr-2026-11-23-commerce-storefront-design.svg)

Au retour de la page de paiement, recherchez la commande existante sur le serveur. Si la réponse à la création de la commande est perdue après le clic sur « Payer », utilisez la même clé de requête de commande pour vérifier si la commande a déjà été acceptée. Désactiver brièvement le bouton peut réduire les clics répétés. La clé de requête et une vérification d’unicité côté serveur préviennent les doublons. Les API de détail et de statut vérifient aussi que l’acheteur courant a le droit d’accéder à la commande.

| État vérifié par le serveur | Message et action pour l’acheteur |
| --- | --- |
| Échec de la consultation de l’état de la commande | « Impossible de charger l’état de votre commande. » → **Recharger l’état de la commande** |
| Commande existante, résultat du paiement indéterminé | « Nous vérifions le résultat du paiement. » → **Actualiser l’état de la commande** |
| Paiement effectué, commande en cours de vérification | « Votre paiement a abouti. Nous vérifions votre commande. » → **Actualiser l’état de la commande** |
| Paiement et commande confirmés | « Nous avons reçu votre commande. » → **Suivre l’envoi** |
| Annulation confirmée sans débit | « Votre commande a été annulée. Vous n’avez pas été débité. » → **Parcourir les produits** |
| Paiement confirmé après annulation, remboursement en cours | « Nous traitons votre remboursement. » → **Actualiser l’état du remboursement** |
| Remboursement confirmé | « Votre remboursement est terminé. » → **Voir les détails du remboursement** |

Selon l’état réel de l’expédition, indiquez si la commande est en préparation, en cours de livraison ou livrée. Affichez un bouton d’annulation ou de retour uniquement si l’action est autorisée à l’état actuel et que l’utilisateur dispose de l’autorisation nécessaire. Suivez la progression une fois la demande acceptée. Affichez le message de fin du remboursement lorsque le serveur en confirme le résultat.

## Associer les états du serveur à des messages et à des actions

L’exemple reçoit des états de commande et de paiement déjà lus sur le serveur et leur associe un titre et la prochaine action. Une erreur réseau et un résultat de paiement indéterminé sont des entrées distinctes. Les combinaisons d’états non définies n’affichent jamais de succès. Le code utilise les textes d’interface coréens, dont le tableau ci-dessus donne les équivalents français. Enregistrez le code sous `order-view.mjs` et exécutez `node order-view.mjs`.

```javascript
const labels = {
  loading: ["주문 상태를 불러오는 중입니다.", null],
  unavailable: ["주문 상태를 불러오지 못했습니다.", "주문 상태 다시 불러오기"],
  pending: ["결제 결과를 확인 중입니다.", "주문 상태 새로고침"],
  paidReview: ["결제는 완료됐고 주문을 확인 중입니다.", "주문 상태 새로고침"],
  confirmed: ["주문이 접수됐습니다.", "배송 상태 보기"],
  closed: ["주문이 취소됐으며 결제된 금액이 없습니다.", "상품 다시 보기"],
  refundPending: ["환불을 처리 중입니다.", "환불 상태 새로고침"],
  refunded: ["환불이 완료됐습니다.", "환불 내역 보기"]
};

function orderView(snapshot) {
  if (snapshot.kind === "loading") return labels.loading;
  if (snapshot.kind === "unavailable") return labels.unavailable;

  const { order, payment } = snapshot;
  if (order === "CANCELLED" && payment === "REFUND_PENDING") {
    return labels.refundPending;
  }
  if (order === "CANCELLED" && payment === "REFUNDED") {
    return labels.refunded;
  }
  if (order === "CANCELLED" && payment === "CLOSED_UNPAID") {
    return labels.closed;
  }
  if (order === "CONFIRMED" && payment === "PAID") {
    return labels.confirmed;
  }
  if (order === "PENDING_PAYMENT" && payment === "PAID") {
    return labels.paidReview;
  }
  if (order === "PENDING_PAYMENT" &&
      (payment === "PENDING" || payment === "UNKNOWN")) {
    return labels.pending;
  }
  return labels.unavailable;
}

const verified = (order, payment) => ({ kind: "loaded", order, payment });
const cases = [
  [{ kind: "loading" }, "loading"],
  [{ kind: "unavailable" }, "unavailable"],
  [verified("PENDING_PAYMENT", "UNKNOWN"), "pending"],
  [verified("PENDING_PAYMENT", "PAID"), "paidReview"],
  [verified("CONFIRMED", "PAID"), "confirmed"],
  [verified("CANCELLED", "CLOSED_UNPAID"), "closed"],
  [verified("CANCELLED", "REFUND_PENDING"), "refundPending"],
  [verified("CANCELLED", "REFUNDED"), "refunded"],
  [verified("CONFIRMED", "UNKNOWN"), "unavailable"]
];

for (const [input, key] of cases) {
  if (orderView(input) !== labels[key]) throw new Error(key);
  console.log("PASS", key);
}
```

Les neuf entrées ont passé les tests avec Node.js 22.17.0. L’échec de consultation, le résultat du paiement indéterminé, l’annulation sans débit et le remboursement en cours ont chacun renvoyé le message et l’action attendus. Le test couvre la fonction qui associe les états aux messages et aux actions de l’interface. L’ergonomie sur mobile, le comportement des technologies d’assistance et l’intégration réelle du paiement sont à vérifier sur les écrans implémentés.
