---
{
  "state": "draft",
  "language": "fr",
  "translationKey": "2026-11-23-commerce-admin-screen",
  "title": "Concevoir une interface d’administration e-commerce pour les commandes, paiements et expéditions",
  "description": "Organisez l’administration par tâche et utilisez les files de commandes et les fiches de détail pour traiter les paiements indéterminés, les réservations libérées et les demandes de remboursement.",
  "sourcePath": "src/content/posts/en/2026-11-23-commerce-admin-screen.md",
  "sourceSha256": "00692a737eb62a4f313f4adb76e503c7796c83e7a788f20151b7f09669719558"
}
---

**L’interface d’administration d’une boutique doit aider le personnel à repérer les commandes à traiter et à trouver les éléments nécessaires pour agir.** Commencez par des files pour la vérification des paiements, la préparation des expéditions et le suivi des remboursements. Dans le détail d’une commande, affichez le résultat du paiement avec le stock réservé. Si le paiement se confirme après la libération de la réservation, l’opérateur doit pouvoir garder l’expédition bloquée et suivre la demande de remboursement.

Supposons un marchand qui vend des biens physiques en wons sud-coréens (KRW) et expédie depuis un entrepôt. Ce guide applique à l’interface d’administration l’exemple du dernier article présenté dans la conception du système, ainsi que le modèle de lignes de commande, de réservations et de tentatives de paiement présenté dans l’article sur la base de données. Il suit un opérateur qui consulte une transaction existante chez le prestataire de paiement. [Conception du système e-commerce](/en/posts/2026-11-22-commerce-system-design-last-unit-of-stock/) · [Conception de la base de données e-commerce](/en/posts/2026-11-22-commerce-database-design/)

## Donner à chaque menu un point de départ opérationnel

« Commandes » est le point de départ du travail quotidien. « Paiements et remboursements » et « Expéditions » mènent directement aux tâches en attente. Quel que soit le point de départ, un même numéro de commande doit mener aux mêmes détails et au même historique pour que le personnel puisse transmettre les dossiers entre équipes et horaires.

| Menu | Travail à commencer ici | Informations nécessaires |
| --- | --- | --- |
| Commandes | Ouvrir les commandes dont le paiement est indéterminé, celles qui attendent l’expédition ou celles dont le remboursement est en cours. | Numéro de commande, articles et montants à l’achat, les quatre états |
| Catalogue | Modifier la disponibilité à la vente d’un SKU, ses options ou son prix actuel. | Conditions actuelles par SKU, valeurs avant et après |
| Stock | Trouver les commandes avec une réservation ou corriger les écarts constatés lors d’un inventaire physique. | Stock physique, réservé et affecté par SKU, commandes liées, historique des ajustements |
| Paiements et remboursements | Rapprocher les transactions existantes du prestataire et suivre les demandes de remboursement. | Tentatives de paiement, ID de transaction du prestataire, montant initial, historique des consultations et remboursements |
| Expéditions | Prélever et expédier les articles affectés aux commandes. | SKU, quantité, possibilité d’expédier, enregistrements des expéditions |
| Rôles et autorisations | Autoriser le personnel à consulter ou à effectuer des tâches, et examiner les changements. | Autorisations par tâche, périmètre, historique des attributions et révocations |

Un changement de prix catalogue s’applique aux ventes à venir. Le détail de la commande lit le montant enregistré dans la ligne de commande. Par exemple, la commande `O-42` d’un clavier noir totalise 43 000 KRW après déduction d’une remise de 2 000 KRW sur un prix unitaire de 42 000 KRW et ajout de 3 000 KRW de frais de livraison. Le détail de la commande et l’écran de vérification du remboursement continuent d’afficher le montant de l’achat quand le prix catalogue change.

## Choisir une tâche dans la file et vérifier les éléments dans le détail

**Vérification des paiements** rassemble les commandes dont le paiement est indéterminé. **En attente d’expédition** rassemble celles dont le stock est affecté et qui attendent la préparation de l’envoi. **Suivi des remboursements** rassemble les commandes avec une demande de remboursement enregistrée mais sans résultat définitif. Choisissez un ordre de tri par file. La vérification des paiements peut commencer par les problèmes détectés le plus tôt, tandis que les expéditions peuvent être triées par heure limite de l’entrepôt.

Affichez dans la liste le numéro de commande, l’heure, le produit, le montant et les états actuels. Permettez la recherche par numéro, nom du produit ou SKU et le filtrage par état du paiement. Indiquez le total avant filtrage à côté de chaque tâche et le nombre de résultats au-dessus de la liste. En production, ajoutez si nécessaire des filtres de date et d’affectation. Lorsque le détail se ferme, conservez les filtres, les termes recherchés et la position de défilement. Si une mise à jour retire la ligne de la liste, rendez le focus à la tâche sélectionnée pour que l’opérateur puisse passer à la commande suivante.

| État | Valeurs à afficher | À quoi elles servent |
| --- | --- | --- |
| Commande | En attente de paiement, confirmée, annulée | Indique l’avancement. Un paiement peut encore arriver après l’annulation. |
| Paiement | Indéterminé, payé, remboursement demandé, remboursé | Permet de savoir s’il faut vérifier à nouveau la même transaction ou attendre le résultat du remboursement. |
| Stock | Réservé, réservation libérée, affecté, expédié | Indique la quantité garantie à la commande et son état actuel. |
| Expédition | Expédition bloquée, en attente d’expédition, expédiée | Indique si l’entrepôt peut agir ou s’il a déjà expédié la commande. |

Sous les états, affichez directement le montant à l’achat, le SKU et la quantité, l’ID de la réservation liée et l’ID de transaction du prestataire. Si le résultat du paiement est inconnu, le stock actuellement disponible à la vente ne permet pas de savoir si cette commande a obtenu du stock. Dans l’historique, affichez la date de chaque changement, son auteur, son origine et les identifiants pertinents. Gardez les libellés lisibles sur les écrans étroits et utilisez la couleur pour les mettre en évidence.

## Vérifier la transaction existante si le paiement est indéterminé

La réponse à la demande de paiement de `O-42` a été perdue. Le résultat est resté indéterminé assez longtemps pour qu’une personne autorise une exception, libère la réservation `R-42` et annule la commande. L’opérateur chargé des paiements ouvre la commande et consulte la transaction existante `PG-DEMO-42`. Si le paiement est confirmé, enregistrez une **demande de remboursement**. Laissez la commande annulée, l’expédition bloquée et la réservation libérée. Enregistrez le remboursement comme terminé une fois que le prestataire le confirme.

![Consulter la transaction existante chez le prestataire pour une commande dont le paiement est indéterminé. Sans réponse, conserver les états du paiement, du stock et de l’expédition. Si le paiement est confirmé, demander un remboursement si la réservation est libérée, ou affecter le stock et mettre la commande en attente d’expédition si la réservation est active.](2026-11-23-commerce-admin-screen.svg)

Le schéma présente les branches pour trois commandes fictives. La consultation de `O-43` ne reçoit pas de réponse. **Le paiement reste indéterminé, la réservation active et l’expédition bloquée.** Pour `O-44`, le paiement est confirmé et la réservation est active. **La commande est confirmée, le paiement marqué comme payé, le stock affecté et la commande mise en attente d’expédition.** Le schéma couvre l’absence de réponse et les paiements confirmés. En production, une clôture sans débit confirmée peut conduire à libérer la réservation et annuler la commande. Si les détails de la transaction divergent, consignez une anomalie de rapprochement avant de modifier un état.

### Un exemple JavaScript pour les transitions d’état

L’exemple applique les résultats de consultation à trois commandes fictives dont le paiement est indéterminé et l’expédition bloquée. Collez-le dans la console de développement d’un navigateur pour l’exécuter sans installation. La fonction modifie uniquement les objets de commande en mémoire.

```javascript
function applyDemoPaymentResult(order, result) {
  if (order.payment !== 'UNKNOWN' || result !== 'PAID') return 'NO_CHANGE';

  if (order.stock === 'RELEASED') {
    order.payment = 'REFUND_PENDING';
    return 'REFUND_REQUESTED';
  }

  if (order.stock === 'HELD') {
    order.order = 'CONFIRMED';
    order.payment = 'PAID';
    order.stock = 'ALLOCATED';
    order.shipping = 'READY';
    return 'READY_TO_SHIP';
  }

  return 'NO_CHANGE';
}

const examples = [
  ['O-42', 'CANCELLED', 'RELEASED', 'PAID'],
  ['O-43', 'PENDING_PAYMENT', 'HELD', 'UNAVAILABLE'],
  ['O-44', 'PENDING_PAYMENT', 'HELD', 'PAID'],
];

for (const [id, state, stock, result] of examples) {
  const order = { order: state, payment: 'UNKNOWN', stock, shipping: 'BLOCKED' };
  console.log(id, applyDemoPaymentResult(order, result), ...Object.values(order));
}
```

La sortie attendue affiche, dans cet ordre, l’ID de commande, le résultat, puis les états de la commande, du paiement, du stock et de l’expédition.

```text
O-42 REFUND_REQUESTED CANCELLED REFUND_PENDING RELEASED BLOCKED
O-43 NO_CHANGE PENDING_PAYMENT UNKNOWN HELD BLOCKED
O-44 READY_TO_SHIP CONFIRMED PAID ALLOCATED READY
```

Le bloc a été exécuté avec Node.js 24.13.0 et a produit les trois lignes attendues.

## Contrôler les autorisations et les états sur le serveur

Autorisez l’équipe de paiement à consulter les transactions existantes, l’équipe d’entrepôt à accéder aux enregistrements d’expédition et les approbateurs désignés à autoriser les libérations exceptionnelles ou les remboursements. Attribuez séparément le droit de modifier les prix catalogue. Dans le détail, ne renvoyez que les champs et les actions disponibles pour l’utilisateur actuel. À chaque demande d’action, l’API doit vérifier l’authentification, l’autorisation d’agir, l’accès à la commande cible et son état actuel. L’API de consultation retrouve sur le serveur la transaction existante liée à la commande. Vérifiez le compte chez le prestataire, l’ID de transaction, le montant et la devise. Lors de l’application du résultat, lisez les derniers états de la commande et de sa réservation. Évitez les demandes d’expédition ou de remboursement en double lorsqu’une nouvelle tentative arrive en même temps qu’un webhook. Quand l’entrepôt demande l’expédition, le serveur vérifie à nouveau que la commande et le paiement sont confirmés et que le stock est affecté.

Pour une action telle que la consultation d’une transaction, indiquez près du bouton la transaction visée et la portée de l’action. La consultation ne crée aucun débit. Si elle confirme un paiement, l’état de la réservation détermine s’il faut demander un remboursement ou mettre la commande en attente d’expédition. Les actions qui touchent directement à l’argent ou au stock, telles qu’un remboursement manuel ou une libération exceptionnelle, exigent une confirmation et une autorisation distinctes. Par exemple, la confirmation d’un remboursement manuel affiche **la commande `O-42`, la transaction initiale `PG-DEMO-42`, la demande de remboursement de 43 000 KRW et son motif**. Affichez « Remboursement demandé » une fois la demande acceptée. Enregistrez dans l’historique d’audit du serveur l’approbateur, l’opérateur, l’heure de la demande, les anciens et nouveaux états, la transaction liée et le résultat. En cas de perte de la réponse, vérifiez d’abord l’état de la même demande.

## Distinguer les files vides des résultats indéterminés

| Situation | Message et prochaine action |
| --- | --- |
| La file ne contient aucune commande | « Aucune commande pour cette tâche. » Permettre à l’opérateur d’ouvrir une autre file. |
| Aucun résultat ne correspond à la recherche ou aux filtres | « Aucune commande ne correspond à votre recherche ou à vos filtres. » Permettre de supprimer les critères dans la file actuelle. |
| La liste des commandes n’a pas pu être chargée | « Impossible de charger les commandes. » Conserver les critères et proposer de recharger. Si d’anciens résultats restent visibles, indiquer leur heure de récupération. |
| La commande est ouverte mais le résultat du prestataire est indéterminé | « La consultation n’a pas reçu de réponse. Le paiement reste indéterminé et l’expédition bloquée. » Permettre de consulter à nouveau la même transaction. |
| L’utilisateur ne dispose pas de l’autorisation | « L’équipe de paiement peut consulter les transactions existantes. » Laisser visibles les états et l’historique dans la limite du rôle actuel. |

## Répercuter les résultats de l’exemple dans les files

Imaginez que vous ouvrez une commande dans **Vérification des paiements** et choisissez **Consulter le paiement existant**. Sans réponse, `O-43` reste dans « Vérification des paiements ». L’historique indique qu’aucune réponse n’a été reçue et que la réservation est restée active. Après avoir enregistré la demande de remboursement pour `O-42`, vous la retrouvez dans **Suivi des remboursements**. Après avoir affecté le stock pour `O-44`, vous la retrouvez dans **En attente d’expédition**. L’opérateur d’expédition voit les états et l’historique de la commande, ainsi qu’un message expliquant que l’équipe de paiement peut effectuer la consultation.

L’exemple utilise des commandes et des réponses de paiement préparées. L’implémentation de production traite séparément la connexion, les données client, les consultations et remboursements réels auprès du prestataire et l’intégration à l’entrepôt.
