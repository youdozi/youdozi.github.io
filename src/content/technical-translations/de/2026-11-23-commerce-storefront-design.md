---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2026-11-23-commerce-storefront-design",
  "routeSlug": "2026-11-23-commerce-storefront-design",
  "kind": "post",
  "title": "Onlineshop gestalten: von der Produktauswahl bis zur Zahlungsbestätigung",
  "description": "Festlegen, was Kunden von der Produktübersicht bis zu den Bestelldetails sehen und tun können, und sie bei der Rückkehr vom Checkout anhand des Bestell- und Zahlungsstatus des Servers weiterführen.",
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
  "draftSha256": "1487cca9ab7e4a173a682d1fd20322d99c1770654a23c65a7b49454e06270e05",
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

**Wenn Käufer nach der Zahlung auf eine leere Seite zurückkehren, möchten sie zuerst wissen, ob ihnen etwas berechnet wurde.** Zeigen Sie ihnen eine Seite, auf der sie den Ausgang für die bestehende Bestellung prüfen können. Zeigen Sie von der Produktseite bis zur Bestellhistorie auf jeder Seite, welche Fakten sie bestätigen kann und was Käufer als Nächstes tun können.

Im [Leitfaden für die Shopverwaltung](/en/posts/2026-11-23-commerce-admin-screen/) prüft ein Mitarbeiter eine Bestellung mit ungeklärter Zahlung. Hier betrachten wir dieselbe Situation aus Kundensicht. Ein Händler verkauft physische Waren in südkoreanischen Won und versendet sie an Käufer, die über ein Konto bestellen. Die Regeln zu Rabatt und Versand dienen als Beispiele.

## Was entscheidet der Käufer auf jeder Seite?

| Seite | Was zuerst angezeigt wird | Was Käufer als Nächstes tun können |
| --- | --- | --- |
| Produktübersicht und Suche | Produktnamen und Fotos, vergleichbare Preise und aktive Filter | Ergebnisse eingrenzen oder eine Produktseite öffnen |
| Produktdetails | Preis und Verfügbarkeit der gewählten Variante sowie Versandbedingungen | Variante und Stückzahl wählen und das Produkt in den Warenkorb legen |
| Warenkorb | Variante, Menge und Betrag pro Artikel, geschätzte Summe und Artikel, die den Checkout blockieren | Mengen und Artikel ändern und zum Checkout gehen |
| Checkout | Lieferadresse, Versandkosten, Rabatte, Endbetrag und Möglichkeiten für Änderungen | Bedingungen prüfen und Zahlung anfordern |
| Bestelldetails | Bestellnummer, Zahlungs-, Versand- und Erstattungsstatus und Änderungshistorie | Je nach Status den Ausgang prüfen oder die Sendung verfolgen |

Steht in der Übersicht „Ab 39.000 ₩“, zeigen Sie den tatsächlichen Preis an, sobald Käufer auf der Produktseite eine Variante wählen. Kennzeichnen Sie ausverkaufte Varianten mit Text. Liefert eine Suche keine Ergebnisse, zeigen Sie die aktiven Filter und lassen Sie Käufer diese entfernen. Kann die Suche nicht geladen werden, bieten Sie einen erneuten Versuch an.

Wenden Sie dieselbe Regel wie im [Leitfaden zur Bestandsreservierung im E-Commerce](/en/posts/2026-11-22-commerce-system-design-last-unit-of-stock/) an. Die Produktseite zeigt den Bestand zum Zeitpunkt der Abfrage. Der Warenkorb hält die Auswahl der Käufer fest. Der Server reserviert den Bestand beim Anlegen der Bestellung. Hat jemand anderes das letzte Exemplar zuerst reserviert, kennzeichnen Sie den betroffenen Artikel und seine Variante im Warenkorb. Behalten Sie die übrigen Artikel und die eingegebene Lieferadresse bei.

## Änderungen und Kontrolle vor der Zahlung ermöglichen

Käufer sollen neben dem Endbetrag die Varianten, Mengen und Lieferadresse überprüfen und ändern können. Benennen Sie die Schaltfläche nach der tatsächlichen Aktion, etwa **„43.000 ₩ bezahlen“**. Die WCAG-Hinweise zur Fehlervermeidung bei finanziellen Transaktionen beschreiben, wie Nutzer Angaben vor dem Absenden prüfen und korrigieren können. [W3C-Hinweise zur Fehlervermeidung bei finanziellen Transaktionen](https://www.w3.org/WAI/WCAG22/Understanding/error-prevention-legal-financial-data.html)

Kostete eine Tastatur bei Aufnahme in den Warenkorb 39.000 ₩ und beim Checkout 42.000 ₩, nennen Sie den betroffenen Artikel. Ein Beispiel lautet „Der Preis der schwarzen Tastatur hat sich von 39.000 ₩ auf 42.000 ₩ geändert.“ Zeigen Sie nach erneuter Berechnung von Rabatten und Versandkosten die neue Summe. Lassen Sie die Käufer den Betrag bestätigen, bevor Sie die Zahlung anfordern. Beim Anlegen der Bestellung gleicht der Server das bestätigte Angebot mit dem Betrag ab, den er abbuchen wird, und hält die Konditionen fest. [Wie die E-Commerce-Datenbank Bestellbeträge speichert](/en/posts/2026-11-22-commerce-database-design/)

Platzieren Sie auf Mobilgeräten die Links zur Änderung der Lieferadresse und der Artikel neben den jeweiligen Angaben. Zeigen Sie den Endbetrag in der Nähe der Zahlungsschaltfläche. Ist die Schaltfläche unten fixiert, muss sich die Seite weit genug scrollen lassen, damit das letzte Feld und eventuelle Fehlermeldungen lesbar bleiben. Assistive Technologien können Änderungen melden, bei denen der Fokus an seiner Position bleiben kann, etwa eine neue Warenkorbsumme oder das Ergebnis einer Zahlungsprüfung. Ergänzen Sie zum Beispiel `role="status"` am Bereich, in dem sich der Ergebnistext ändert. [W3C-Hinweise zu Statusmeldungen](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html)

## Den Zahlungsausgang auf dem Server prüfen

![Rufen Sie die bestehende Bestellung ab, sobald der Käufer von der Zahlung zurückkehrt. Unterscheiden Sie Laden und Abruffehler. Bieten Sie anhand des Zahlungs- und Bestellergebnisses eine Statusaktualisierung, die Sendungsverfolgung, die Produktübersicht oder Erstattungsinformationen an.](/assets/diagrams/technical/de-2026-11-23-commerce-storefront-design.svg)

Kehren Käufer von der Zahlungsseite zurück, fragen Sie die bestehende Bestellung auf dem Server ab. Geht nach dem Klick auf „Bezahlen“ die Antwort zum Anlegen der Bestellung verloren, prüfen Sie mit demselben Anfrageschlüssel, ob die Bestellung bereits angenommen wurde. Das kurzzeitige Deaktivieren der Schaltfläche kann Mehrfachklicks reduzieren. Der Anfrageschlüssel und eine Eindeutigkeitsprüfung auf dem Server verhindern doppelte Bestellungen. Die APIs für Bestelldetails und Status prüfen außerdem, ob der aktuelle Käufer auf die Bestellung zugreifen darf.

| Vom Server geprüfter Status | Meldung und Aktion für Käufer |
| --- | --- |
| Abruf des Bestellstatus fehlgeschlagen | „Wir konnten Ihren Bestellstatus nicht laden.“ → **Bestellstatus neu laden** |
| Bestellung vorhanden, Zahlungsausgang ungeklärt | „Wir prüfen den Zahlungsausgang.“ → **Bestellstatus aktualisieren** |
| Zahlung abgeschlossen, Bestellung in Prüfung | „Ihre Zahlung ist eingegangen. Wir prüfen Ihre Bestellung.“ → **Bestellstatus aktualisieren** |
| Zahlung und Bestellung bestätigt | „Wir haben Ihre Bestellung erhalten.“ → **Sendung verfolgen** |
| Stornierung ohne Abbuchung bestätigt | „Ihre Bestellung wurde storniert. Es wurde nichts abgebucht.“ → **Produkte ansehen** |
| Zahlung nach Stornierung bestätigt, Rückerstattung offen | „Wir bearbeiten Ihre Rückerstattung.“ → **Erstattungsstatus aktualisieren** |
| Rückerstattung bestätigt | „Ihre Rückerstattung ist abgeschlossen.“ → **Erstattungsdetails ansehen** |

Zeigen Sie anhand des tatsächlichen Versandstatus, ob die Bestellung vorbereitet wird, unterwegs oder zugestellt ist. Zeigen Sie eine Schaltfläche für Stornierung oder Rückgabe erst, wenn die Aktion im aktuellen Status zulässig ist und die Person die erforderliche Berechtigung hat. Zeigen Sie nach Annahme der Anfrage den Fortschritt an. Melden Sie den Abschluss der Rückerstattung, sobald der Server das Ergebnis bestätigt hat.

## Serverstatus in Meldungen und Aktionen übersetzen

Das Beispiel übernimmt bereits vom Server gelesene Bestell- und Zahlungsstatus und ordnet ihnen eine Überschrift und die nächste Aktion zu. Ein Netzwerkfehler und ein ungeklärter Zahlungsausgang sind getrennte Eingaben. Bei undefinierten Statuskombinationen zeigt die Funktion nie Erfolg an. Der Code verwendet koreanische UI-Texte. Die Tabelle oben enthält die entsprechenden deutschen Texte. Speichern Sie den Code als `order-view.mjs` und führen Sie `node order-view.mjs` aus.

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

Alle neun Eingaben bestanden den Test unter Node.js 22.17.0. Beim Abruffehler, bei ungeklärter Zahlung, bei Stornierung ohne Abbuchung und bei ausstehender Rückerstattung erschienen die erwartete Meldung und Aktion. Der Test deckte die Funktion ab, die Status in UI-Meldungen und Aktionen übersetzt. Die Bedienbarkeit auf Mobilgeräten, das Verhalten assistiver Technologien und die echte Zahlungsintegration sind an den implementierten Seiten zu prüfen.
