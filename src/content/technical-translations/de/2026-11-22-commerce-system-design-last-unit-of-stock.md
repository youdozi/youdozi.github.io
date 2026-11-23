---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2026-11-22-commerce-system-design-last-unit-of-stock",
  "routeSlug": "2026-11-22-commerce-system-design-last-unit-of-stock",
  "kind": "post",
  "title": "E-Commerce-Systemdesign: Wer bekommt das letzte Exemplar?",
  "description": "Am letzten verfügbaren Exemplar zeigen, wie SKU-Reservierungen, der Abgleich von Zahlungen und Rückerstattungen nach Freigabe einer Reservierung zusammenspielen.",
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
  "draftSha256": "89b2cb9952f58e7c1e077b91513ef6ce8a3aea4218abef60bab5c6fe98cbceee",
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

**Wenn zwei Kunden das letzte Exemplar eines Produkts kaufen wollen, darf nur eine Bestellung es reservieren.** Geht nach der Reservierung die Antwort des Zahlungsdienstleisters verloren, bleibt die Bestellung offen, während der Shop die Zahlung prüft. Bestätigt sich die Zahlung erst nach Freigabe der Reservierung, bleibt die Bestellung storniert und der Shop beantragt eine Rückerstattung. An einem Kauf lässt sich zeigen, für welche Daten Katalog, Bestand, Bestellungen und Zahlungen jeweils zuständig sind.

Im Beispiel verkauft ein Händler physische Waren, nimmt pro Bestellung eine Zahlung in südkoreanischen Won (KRW) an und versendet aus einem Lager. Es umfasst Stornierungen und Erstattungen bei ungeklärten und verspätet bestätigten Zahlungen. Marktplatzabrechnung, Teillieferungen und Retouren liegen außerhalb des Beispiels.

## Angezeigter Bestand und für die Bestellung reservierter Bestand

Ein **Produkt** ist der Katalogeintrag, den Kunden sehen. Eine **SKU** (Stock Keeping Unit) ist die Einheit, die der Shop für Bestellungen und Bestand verwaltet. Die weiße und die schwarze Variante derselben Tastatur haben verschiedene SKUs. Die Produktseite zeigt die Verfügbarkeit zum Zeitpunkt der Abfrage. Antwortet das Bestandsmodul nicht, bleibt das Produkt sichtbar und die Verfügbarkeit lautet „Bestand wird geprüft“. Das Hinzufügen zum Warenkorb ändert den Bestand nicht.

| Zuständigkeit | Daten, die der Bereich ändern darf | Beispiel |
| --- | --- | --- |
| Katalog und Preise | Produkte, SKUs, Verkaufsfreigabe, aktuelle Stückpreise | Den Stückpreis der schwarzen Tastatur `KB-BLK` ändern |
| Bestand | Physischer Bestand je Lager, Reservierungen, Zuteilungen für den Versand | Ein Exemplar von `KB-BLK` für eine bestimmte Bestellung reservieren |
| Bestellungen | Käufer, Bestellpositionen und Beträge zum Kaufzeitpunkt, Bestellstatus | Mengen, Stückpreise, Rabattaufteilung und Versandkosten für Bestellung `O-42` speichern |
| Zahlungen | Zahlungsversuche, Transaktions-IDs des Dienstleisters, Zahlungs- und Erstattungsstatus | Das Ergebnis für Versuch `P-1` mit dem Dienstleister abgleichen |
| Versandabwicklung | Versandaufträge und deren Fortschritt | Ware nach Zahlung und Bestandszuweisung kommissionieren |

Unmittelbar vor dem Checkout prüft der Server, ob die Artikel noch im Verkauf sind, und kontrolliert die Preise erneut. Er ermittelt den Käufer aus der authentifizierten Sitzung und berechnet den Gesamtbetrag nach seinen eigenen Preis-, Rabatt- und Versandregeln. Kostete die schwarze Tastatur beim Hinzufügen zum Warenkorb 39.000 KRW und kostet sie jetzt 42.000 KRW, zeigt der Shop den neuen Betrag an und bittet um Bestätigung. Beim Anlegen der Bestellung prüft der Server, ob die akzeptierte Preisversion mit der angewandten Version übereinstimmt. In der Bestellung bleiben SKU, Variantenname, Menge, Stückpreis, Rabatte, Versandkosten und Währung erhalten. Mit dem neuen Stückpreis von 42.000 KRW, einem Rabatt von 2.000 KRW und Versandkosten von 3.000 KRW sendet der Server 43.000 KRW an den Zahlungsdienstleister. Auch wenn das Produkt am nächsten Tag umbenannt oder günstiger wird, muss die gespeicherte Bestellung den bestätigten Betrag anzeigen. Diese Grenze kommt hinzu, wenn Sie das [Spring-Boot-Beispiel zur Produktabfrage](/en/posts/2026-11-22-spring-boot-4-2-restclient-migration/) um Bestellungen erweitern.

## Was gehört in eine gemeinsame Transaktion?

Beginnen Sie mit **getrennten Modulen in einer Anwendung** für Katalog, Bestand, Bestellungen und Zahlungsdaten. Die Module teilen sich eine Datenbank und bestimmen jeweils die Schreibregeln für ihre Tabellen. So können Bestellung und Reservierung in einer lokalen Transaktion gemeinsam festgeschrieben werden. Rufen Sie erst nach dem Commit den externen Zahlungsdienstleister auf.

1. **Bestellung anlegen und Bestand reservieren.** Erkennen Sie Wiederholungen anhand des Käufers und des Anfrageschlüssels für die Bestellung. Derselbe Schlüssel mit anderen Anfragedaten gilt als Konflikt. Das Bestandsmodul prüft den verfügbaren Bestand mit einer Sperre auf der SKU-Zeile oder einem bedingten Update. Bei mehreren SKUs speichern Sie Bestellpositionen, Reservierungen und Zahlungsversuch zusammen, sobald alle Artikel gesichert sind. Fehlt Bestand für einen Artikel, machen Sie die gesamte Transaktion rückgängig und melden den Mangel. Erfassen Sie im selben lokalen Commit die Arbeit zur Wiederaufnahme der Zahlungsanfrage.
2. **Zahlungsdienstleister aufrufen.** Senden Sie die Zahlungsanfrage mit einem Idempotenzschlüssel des Dienstleisters, der an die ID des gespeicherten Zahlungsversuchs gebunden ist. Fällt der Server direkt nach dem Aufruf aus, muss er den Datensatz wiederfinden und denselben Versuch abgleichen können. Geht die Antwort verloren, fragen Sie beim Dienstleister die bestehende Transaktion ab. Senden Sie die Anfrage nur erneut, soweit der Dienstleister denselben Schlüssel und dieselben Anfrageparameter garantiert. Solange das Ergebnis ungeklärt ist, verwenden Sie den vorhandenen Versuch weiter. [Stripe-Dokumentation zu idempotenten Anfragen](https://docs.stripe.com/api/idempotent_requests)
3. **Ergebnis anwenden.** Prüfen Sie vor dem Speichern des Ereignisses die Webhook-Signatur oder fragen Sie die Transaktion vom Server aus ab. Prüfen Sie, ob Bestellung, Zahlungsversuch, Händlerkonto, Betrag und Währung übereinstimmen. Sperren Sie Bestellung und Reservierung, lesen Sie den aktuellen Status und speichern Sie den Zahlungsstatus, den Bestandsübergang und die Folgeaufgaben in einer Transaktion. Schreiben Sie den Versand- oder Erstattungsauftrag im selben Commit in eine Outbox. [Stripe-Regeln zur Webhook-Zustellung](https://docs.stripe.com/webhooks#event-delivery-behaviors) · [AWS-Muster für eine transaktionale Outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)

Dabei gilt **verfügbarer Bestand = physischer Bestand − aktive Reservierungen − Versandzuteilungen**. Bestätigt eine Zahlung die Reservierung, ziehen Sie die reservierte Menge ab und addieren dieselbe Menge bei der Versandzuteilung. Beim Versand sinken der physische Bestand und die Zuteilung. Treffen zwei Bestellungen für das letzte Exemplar gleichzeitig ein, muss die zweite nach dem Commit der ersten den verfügbaren Bestand null sehen. Prüfen Sie dies mit überlappenden Transaktionen in der tatsächlichen Datenbank.

## Ungeklärte und verspätete Zahlungen behandeln

![Das System liest das verifizierte Zahlungsergebnis und den Bestellstatus. Bleibt das Ergebnis ungeklärt, bleibt der Reservierungsstatus bestehen. Wird die Transaktion nachweislich ohne Abbuchung geschlossen, wird die Reservierung freigegeben. Bei bestätigter Zahlung folgt ein Versandauftrag, solange der Bestand reserviert ist, oder eine Erstattung nach der Freigabe. Bereits bearbeitete Ergebnisse lösen keine doppelten Aufträge aus.](/assets/diagrams/technical/de-2026-11-22-commerce-system-design-last-unit-of-stock.svg)

Das Diagramm zeigt, wie der Shop Zahlungsergebnisse nach der Reservierung anwendet. Ist bereits `PAID` oder `REFUND_PENDING` gespeichert, behält der Code diesen Status bei und legt keine Folgeaufgabe an.

Bestellung, Zahlung und Reservierung haben jeweils einen eigenen Status. Der Shop kombiniert sie zu einer verständlichen Meldung. Antwortet der Dienstleister zum Beispiel langsam, bleibt die Bestellung auf `PENDING_PAYMENT`, die Zahlung auf `UNKNOWN` und die Reservierung auf `HELD`. Zeigen Sie „Zahlung wird geprüft“ an und lassen Sie den Käufer dieselbe Bestellung erneut abfragen.

| Situation | Gespeicherter Status und Folgeschritt |
| --- | --- |
| Zahlung bestätigt, Bestand reserviert | Bestellung `CONFIRMED`, Zahlung `PAID`, Bestand `ALLOCATED`. Versandauftrag erfassen |
| Antwort verloren oder Dienstleister verarbeitet noch | Bestellung `PENDING_PAYMENT`, Zahlung `UNKNOWN`, Bestand `HELD`. Bestehende Zahlung erneut prüfen |
| Transaktion nachweislich ohne Abbuchung geschlossen | Bestellung `CANCELLED`, Zahlung `CLOSED_UNPAID`, Reservierung `RELEASED` |
| Zahlung nach außerordentlicher Freigabe bestätigt | Bestellung `CANCELLED`, Zahlung `REFUND_PENDING`, Reservierung `RELEASED`. Erstattungsauftrag erfassen |

Läuft die Reservierung bei ungeklärter Zahlung ab, fragen Sie zuerst den Dienstleister ab. Bleibt das Ergebnis ungeklärt, erfassen Sie den Fall, damit ein Mitarbeiter die Transaktion finden und abgleichen kann. Trifft die Zahlungsbestätigung nach einer außerordentlichen Freigabe ein, fordert dieses Design eine Rückerstattung an und belässt die Reservierung im freigegebenen Status. Erfassen Sie die Rückerstattung als erfolgreich, wenn der Dienstleister sie bestätigt. Legen Sie Haltedauer und Freigabeberechtigung anhand des Bestandsumschlags und der Vertragsbedingungen des Dienstleisters fest.

Erkennen Sie wiederholte Zustellungen anhand der Webhook-Ereignis-ID. Schützen Sie jede Zahlung auch dann gegen doppelte Versandaufträge, wenn die Ereignis-IDs unterschiedlich sind. Legen Sie beispielsweise in der Versand-Outbox eine Eindeutigkeitsbedingung für `order_id` und Aufgabentyp an. Verwenden Sie in der Erstattungs-Outbox `payment_attempt_id` und Aufgabentyp. Die Veröffentlichung aus der Outbox kann wiederholt werden. Versand- und Erstattungs-Worker verhindern mit derselben Auftrags-ID eine doppelte Ausführung. Verwenden Sie bei einer erneuten Erstattungsanfrage einen vom Dienstleister unterstützten Idempotenzschlüssel für Erstattungen. Ein älteres Ereignis, das eine laufende Verarbeitung meldet, ändert einen bestätigten Zahlungsstatus nicht. Gleichen Sie abweichende IDs oder Beträge und Ergebnisse, die dem bestätigten Verlauf widersprechen, vor der Anwendung ab. [Stripe-Hinweise zu doppelten Webhooks](https://docs.stripe.com/webhooks#handle-duplicate-events) · [AWS-Muster für eine transaktionale Outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)

## Zahlungsübergänge in Java prüfen

Speichern Sie den folgenden Code als `CheckoutPolicy.java` und führen Sie `java CheckoutPolicy.java` aus. Das Beispiel übernimmt **das vom Server verifizierte Ergebnis eines Zahlungsversuchs** für eine Bestellung. `CLOSED_UNPAID` bedeutet, dass der Dienstleister das Ende der Transaktion ohne Abbuchung bestätigt hat. Eine Ablehnungsmeldung allein reicht als Nachweis nicht aus. Der Code setzt voraus, dass Bestell- und Reservierungsstatus zusammenpassen. Eine ausstehende Bestellung hat eine Reservierung, eine stornierte Bestellung hat sie bereits freigegeben. Der Aufrufer prüft IDs und Beträge und gleicht widersprüchliche Ergebnisse ab. Der Code liefert den nächsten Status und die Folgeaufgabe, die zu speichern ist.

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

Die folgenden sieben Prüfungen liefen unter JDK 21.0.1. Die erneute Anwendung derselben Zahlungsbestätigung erzeugte keine zusätzliche Aufgabe. Eine Zahlungsbestätigung nach Freigabe der Reservierung lieferte einen Erstattungsauftrag.

```text
PASS unresolved retains hold
PASS paid allocates stock
PASS duplicate paid has no effect
PASS old unresolved does not reopen payment
PASS closed unpaid releases hold
PASS late paid requests refund
PASS duplicate late paid has no effect
```

Zwei Nebenläufigkeitsfälle brauchen eigene Prüfungen in der Implementierung. Versuchen zwei Bestellungen gleichzeitig, das letzte Exemplar zu reservieren, darf nur eine Erfolg haben. Treffen Ablaufverarbeitung und Zahlungsbestätigung für dieselbe Bestellung zusammen, darf das System nur ein Ergebnis speichern: Versand, solange der Bestand noch reserviert ist, oder Erstattung nach Freigabe. Das sequenzielle Java-Beispiel lässt die Nebenläufigkeit der Datenbank, die Anbindung des Dienstleisters und Zahlungen in der Produktionsumgebung für separate Prüfungen offen.

Wenn mehr Lager den Bestand verwalten müssen oder das Bestandsmodul unabhängig bereitgestellt oder skaliert werden soll, erwägen Sie einen separaten Dienst. Die Bestell- und Bestandsdatenbanken haben dann keinen gemeinsamen lokalen Commit. Der Bestandsdienst muss jede Reservierungs-ID einmalig anwenden. Das Bestellmodul muss das Ergebnis abfragen oder Fehler kompensieren können. Die fachlichen Regeln gelten auch über Dienstgrenzen hinweg: Überverkäufe verhindern und jede Zahlung sowie jeden Versand nur einmal anwenden.
