---
{
  "state": "draft",
  "language": "de",
  "translationKey": "2026-11-23-commerce-admin-screen",
  "title": "E-Commerce-Verwaltung für Bestellwarteschlangen, Zahlungen und Versand",
  "description": "Die Shopverwaltung nach Aufgaben gliedern und mit Bestellwarteschlangen und Detailansichten ungeklärte Zahlungen, freigegebene Bestandsreservierungen und Rückerstattungen bearbeiten.",
  "sourcePath": "src/content/posts/en/2026-11-23-commerce-admin-screen.md",
  "sourceSha256": "00692a737eb62a4f313f4adb76e503c7796c83e7a788f20151b7f09669719558"
}
---

**Eine Shopverwaltung soll Mitarbeitenden helfen, Bestellungen mit Handlungsbedarf und die nötigen Nachweise zu finden.** Beginnen Sie mit Warteschlangen für Zahlungsprüfung, Versandabwicklung und Erstattungsverfolgung. Zeigen Sie in den Bestelldetails das Zahlungsergebnis neben der zugehörigen Bestandsreservierung. Wird eine Zahlung nach Freigabe der Reservierung bestätigt, soll der Versand gesperrt bleiben und der Erstattungsauftrag nachvollziehbar sein.

Das Beispiel setzt einen Händler voraus, der physische Waren in südkoreanischen Won (KRW) verkauft und aus einem Lager versendet. Der Leitfaden überträgt das Beispiel zum letzten Exemplar aus dem Systemdesign und das Modell für Positionen, Reservierungen und Zahlungsversuche aus dem Datenbankartikel auf die Verwaltung. Er folgt einem Mitarbeiter, der eine bestehende Transaktion beim Zahlungsdienstleister abfragt. [E-Commerce-Systemdesign](/en/posts/2026-11-22-commerce-system-design-last-unit-of-stock/) · [E-Commerce-Datenbankdesign](/en/posts/2026-11-22-commerce-database-design/)

## Einen Einstieg pro Menü anbieten

„Bestellungen“ ist der Ausgangspunkt für den Alltag. „Zahlungen und Erstattungen“ und „Versandabwicklung“ führen direkt zu offenen Aufgaben. Egal, wo Mitarbeitende beginnen: Dieselbe Bestellnummer führt zu denselben Details und derselben Historie, damit sie Aufgaben über Schichten und Teams hinweg übergeben können.

| Menü | Aufgaben, die hier beginnen | Was Mitarbeitende sehen müssen |
| --- | --- | --- |
| Bestellungen | Bestellungen mit ungeklärter Zahlung, ausstehendem Versand oder ausstehender Erstattung öffnen. | Bestellnummer, Artikel und Beträge zum Kaufzeitpunkt, die vier Statusfelder |
| Katalog | Verkaufsfreigabe einer SKU, Varianten oder aktuellen Preis ändern. | Aktuelle Konditionen je SKU, Werte vor und nach der Änderung |
| Bestand | Bestellungen mit Reservierungen finden oder Abweichungen aus der Inventur korrigieren. | Physischer, reservierter und zugewiesener Bestand je SKU, verknüpfte Bestellungen, Änderungshistorie |
| Zahlungen und Erstattungen | Bestehende Transaktionen beim Dienstleister abgleichen und Erstattungsaufträge verfolgen. | Zahlungsversuche, Transaktions-ID des Dienstleisters, ursprünglicher Betrag, Abfrage- und Erstattungshistorie |
| Versandabwicklung | Zugewiesene Artikel kommissionieren und versenden. | SKU, Menge, Versandfreigabe, Versandnachweise |
| Rollen und Berechtigungen | Mitarbeitenden Lese- oder Ausführungsrechte erteilen und Änderungen prüfen. | Rechte je Aufgabe, Geltungsbereich, Vergabe und Entzug |

Eine Katalogpreisänderung gilt für zukünftige Verkäufe. Die Bestelldetails lesen den Betrag von der Bestellposition. Beispielsweise summiert sich Bestellung `O-42` für eine schwarze Tastatur auf 43.000 KRW: 2.000 KRW Rabatt vom Stückpreis von 42.000 KRW abziehen und 3.000 KRW Versandkosten addieren. Auch nach Änderungen im Katalog zeigen Bestelldetails und Erstattungsprüfung weiterhin den Betrag zum Kaufzeitpunkt.

## In der Warteschlange Aufgaben wählen und im Detail Nachweise prüfen

**Zahlungsprüfung** enthält Bestellungen mit ungeklärten Zahlungen. **Versand ausstehend** enthält Bestellungen mit zugewiesenem Bestand, deren Versand noch nicht bearbeitet wurde. **Erstattungsverfolgung** enthält Bestellungen mit einem dokumentierten Erstattungsauftrag ohne Endergebnis. Legen Sie pro Warteschlange eine Sortierung fest. Die Zahlungsprüfung kann etwa die ältesten erkannten Fälle zuerst zeigen, die Versandabwicklung nach Annahmeschluss des Lagers sortieren.

Zeigen Sie Bestellnummer, Zeit, Produkt, Betrag und aktuelle Status in der Liste. Bieten Sie neben einem Zahlungsstatusfilter eine Suche nach Bestellnummer, Produktname oder SKU an. Zeigen Sie die ungefilterte Gesamtzahl neben jeder Aufgabe und die aktuelle Trefferzahl über der Liste. Ergänzen Sie in Produktion bei Bedarf Datums- und Zuständigkeitsfilter. Behalten Sie Filter, Suchbegriffe und Scrollposition beim Schließen der Detailansicht bei. Verschwindet die ursprüngliche Zeile nach einer Änderung, setzen Sie den Fokus auf die ausgewählte Aufgabe zurück, damit die nächste Bestellung erreichbar bleibt.

| Status | Was angezeigt wird | Warum er wichtig ist |
| --- | --- | --- |
| Bestellung | Zahlung ausstehend, bestätigt, storniert | Zeigt den Stand der Bestellung. Eine Zahlung kann nach der Stornierung noch eingehen. |
| Zahlung | Ungeklärt, bezahlt, Erstattung angefordert, erstattet | Zeigt, ob dieselbe Transaktion erneut abgefragt werden soll oder das Erstattungsergebnis abzuwarten ist. |
| Bestand | Reserviert, Reservierung freigegeben, zugewiesen, versendet | Zeigt die für den Auftrag gesicherte Menge und ihren Status. |
| Versand | Versand gesperrt, Versand ausstehend, versendet | Zeigt, ob das Lager tätig werden darf oder bereits versendet hat. |

Platzieren Sie Kaufbetrag, SKU und Menge, Reservierungs-ID und Transaktions-ID des Zahlungsdienstleisters direkt unter den Statusangaben. Bei ungeklärter Zahlung lässt der aktuell verfügbare Bestand nicht erkennen, ob für diese Bestellung Ware gesichert wurde. Zeigen Sie in der Historie Zeitpunkt, ausführende Person, Ursprung und relevante IDs jeder Änderung an. Halten Sie Statusbezeichnungen auf schmalen Bildschirmen lesbar und setzen Sie Farbe zur Hervorhebung ein.

## Bei ungeklärter Zahlung die bestehende Transaktion abfragen

Die Antwort auf die Zahlungsanfrage für `O-42` ging verloren. Der Ausgang blieb lange genug ungeklärt, dass eine autorisierte Person eine Ausnahme genehmigte, Reservierung `R-42` freigab und die Bestellung stornierte. Der Zahlungsmitarbeiter öffnet die Bestellung und fragt die bestehende Transaktion `PG-DEMO-42` ab. Ist die Zahlung bestätigt, erfassen Sie einen **Erstattungsauftrag**. Die Bestellung bleibt storniert, der Versand gesperrt und die Reservierung freigegeben. Erfassen Sie die Erstattung als abgeschlossen, sobald der Dienstleister sie bestätigt.

![Für eine Bestellung mit ungeklärter Zahlung die bestehende Transaktion beim Dienstleister abfragen. Ohne Antwort bleiben die Status für Zahlung, Bestand und Versand unverändert. Bei bestätigter Zahlung eine Erstattung anfordern, wenn die Reservierung freigegeben ist, oder bei aktiver Reservierung Bestand zuweisen und die Bestellung in die Versandwarteschlange verschieben.](2026-11-23-commerce-admin-screen.svg)

Das Diagramm zeigt die Zweige für drei fiktive Bestellungen. Bei `O-43` bleibt die Abfrage ohne Antwort. **Die Zahlung bleibt ungeklärt, die Reservierung aktiv und der Versand gesperrt.** Bei `O-44` wird die Zahlung bestätigt und die Reservierung ist aktiv. **Die Bestellung wird bestätigt, die Zahlung als bezahlt markiert, Bestand zugewiesen und die Bestellung in die Versandwarteschlange verschoben.** Die Grafik behandelt fehlende Antworten und bestätigte Zahlungen. In Produktion kann ein bestätigter Abschluss ohne Abbuchung zur Freigabe der Reservierung und zur Stornierung führen. Bei widersprüchlichen Transaktionsdaten dokumentieren Sie einen Abgleichsfall, bevor Sie Status ändern.

### Ein JavaScript-Beispiel für Statusübergänge

Das Beispiel wendet Abfrageergebnisse auf drei fiktive Bestellungen mit ungeklärter Zahlung und gesperrtem Versand an. Fügen Sie den Code in die Entwicklerkonsole eines Browsers ein, um ihn ohne Installation auszuführen. Die Funktion ändert nur Bestellobjekte im Arbeitsspeicher.

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

Die erwartete Konsolenausgabe zeigt nacheinander die Bestell-ID, das Ergebnis sowie den Status von Bestellung, Zahlung, Bestand und Versand.

```text
O-42 REFUND_REQUESTED CANCELLED REFUND_PENDING RELEASED BLOCKED
O-43 NO_CHANGE PENDING_PAYMENT UNKNOWN HELD BLOCKED
O-44 READY_TO_SHIP CONFIRMED PAID ALLOCATED READY
```

Der Code lief unter Node.js 24.13.0 und gab alle drei erwarteten Zeilen aus.

## Berechtigungen und aktuellen Status auf dem Server prüfen

Geben Sie dem Zahlungsteam Zugriff auf die Abfrage bestehender Transaktionen, dem Lagerteam auf Versanddaten und zuständigen Personen das Recht, außerordentliche Freigaben und Erstattungen zu genehmigen. Vergeben Sie das Recht zur Änderung von Katalogpreisen getrennt. Liefert die API Bestelldetails, gibt sie nur die für den aktuellen Nutzer relevanten Felder und verfügbaren Aktionen zurück. Bei jeder Aktionsanfrage prüft sie Authentifizierung, Aktionsberechtigung, Zugriff auf die betroffene Bestellung und deren aktuellen Status. Die API zur Zahlungsprüfung ermittelt auf dem Server die verknüpfte bestehende Transaktion. Gleichen Sie Dienstleisterkonto, Transaktions-ID, Betrag und Währung ab. Lesen Sie beim Anwenden des Ergebnisses den aktuellen Stand der Bestellung und der verknüpften Reservierung. Verhindern Sie doppelte Versand- oder Erstattungsaufträge, wenn eine Wiederholung mit einem Webhook zusammenfällt. Fordert das Lager den Versand an, prüft der Server erneut, ob Bestellung und Zahlung bestätigt sind und Bestand zugewiesen ist.

Zeigen Sie bei Aktionen wie der Abfrage einer bestehenden Transaktion neben der Schaltfläche die Transaktion und den Umfang der Aktion an. Die Abfrage löst keine neue Abbuchung aus. Bestätigt sie die Zahlung, bestimmt der Reservierungsstatus, ob der Server eine Rückerstattung anfordert oder die Bestellung in die Versandwarteschlange verschiebt. Aktionen, die Geld oder Bestand verändern, etwa manuelle Erstattungen oder außerordentliche Freigaben, erfordern eine gesonderte Bestätigung und Berechtigung. Die Bestätigung für eine manuelle Erstattung zeigt zum Beispiel **Bestellung `O-42`, Originaltransaktion `PG-DEMO-42`, beantragte Erstattung von 43.000 KRW und den Grund**. Kennzeichnen Sie den angenommenen Auftrag mit „Erstattung angefordert“. Erfassen Sie im serverseitigen Auditprotokoll Genehmigende, ausführende Person, Anfragezeit, alten und neuen Status, verknüpfte Transaktion und Ergebnis. Geht die Antwort verloren, fragen Sie zuerst den Status desselben Auftrags ab.

## Leere Warteschlangen und ungeklärte Ergebnisse unterschiedlich melden

| Situation | Meldung und nächste Aktion |
| --- | --- |
| Die Warteschlange enthält keine Bestellungen | „Für diese Aufgabe gibt es keine Bestellungen.“ Lassen Sie Mitarbeitende eine andere Warteschlange öffnen. |
| Nichts entspricht Suche oder Filtern | „Keine Bestellungen entsprechen den Such- oder Filterkriterien.“ Lassen Sie sie die Bedingungen in derselben Warteschlange entfernen. |
| Die Bestellliste konnte nicht geladen werden | „Bestellungen konnten nicht geladen werden.“ Behalten Sie die Suchbedingungen bei und bieten Sie erneutes Laden an. Falls ältere Ergebnisse sichtbar bleiben, zeigen Sie ihre Abrufzeit an. |
| Die Bestellung ist geöffnet, das Dienstleisterergebnis ungeklärt | „Die Abfrage blieb ohne Antwort. Die Zahlung bleibt ungeklärt und der Versand gesperrt.“ Lassen Sie dieselbe Transaktion erneut abfragen. |
| Der Nutzer hat keine Berechtigung | „Das Zahlungsteam kann bestehende Transaktionen abfragen.“ Zeigen Sie Status und Historie im erlaubten Umfang weiter an. |

## Die Beispielergebnisse in den Warteschlangen nachvollziehen

Öffnen Sie gedanklich eine Bestellung in **Zahlungsprüfung** und wählen Sie **Bestehende Zahlung abfragen**. Ohne Antwort bleibt `O-43` in „Zahlungsprüfung“. In der Abfragehistorie steht, dass keine Antwort einging und die Reservierung aktiv blieb. Nachdem Sie den Erstattungsauftrag für `O-42` erfasst haben, finden Sie die Bestellung in **Erstattungsverfolgung**. Nach der Bestandszuweisung für `O-44` steht diese in **Versand ausstehend**. Ein Mitarbeiter der Versandabwicklung sieht Status und Historie sowie den Hinweis, dass das Zahlungsteam die Abfrage ausführen kann.

Das Beispiel verwendet vorbereitete Bestellungen und Zahlungsantworten. Die Produktionsimplementierung behandelt Anmeldung, Kundendaten, tatsächliche Abfragen und Rückerstattungen beim Dienstleister und die Lageranbindung separat.
