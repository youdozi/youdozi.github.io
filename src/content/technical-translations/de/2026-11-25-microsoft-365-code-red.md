---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2026-11-25-microsoft-365-code-red",
  "routeSlug": "2026-11-25-microsoft-365-code-red",
  "kind": "post",
  "title": "Was Microsoft 365 „Code Red“ für die Störungsbewältigung lehrt",
  "description": "Aufnahmekapazität beim Failover, Wiederverbindungsflut und gemeinsames Störungsprotokoll am Beispiel des Microsoft-365-Ausfalls.",
  "categories": [
    "architecture"
  ],
  "tags": [
    "microsoft-365",
    "incident-response",
    "failover",
    "load-shedding"
  ],
  "sourcePath": "src/content/posts/en/2026-11-25-microsoft-365-code-red.md",
  "sourceSha256": "2df9b4039ebb04013f04e21b144e3cb3780236a74b97dd9dcd885df36569a389",
  "draftSha256": "8c385a16656c42c3a03621162a9ae4bd191f1e42034bd58170e78f52c343e8bc",
  "manifestPath": ".pipeline/technical-translations/batch-191/manifest.json",
  "manifestSha256": "6877756f499cf7012e5f91f7e124786194c8c1f60d4c471aac5a2cd4b42eece1",
  "publishedAt": "2026-11-25T04:56:03.451Z",
  "updatedAt": "2026-11-25T04:56:03.451Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 194,
    "approvedAt": "2026-11-25T04:56:03.451Z",
    "basis": "User approved publication of this supplied manuscript in eight languages and authorized the localized diagrams on 2026-11-25; translation review is self-review, not human or native-speaker review."
  }
}
---

Antwortet ein Server nicht, werden Anfragen an funktionierende Server umgeleitet. Üblicherweise bemerken Nutzer dadurch den Ausfall weniger Server nicht. Beim Ausfall im November 2026 von Microsoft 365 trug derselbe Mechanismus die Störung in andere Regionen: Auch die übernehmenden Server hatten denselben Fehler, der bei steigender Last dort ebenfalls auftrat. [Kopie des Microsoft-Nachberichts](https://www.365fanatic.com/wp-content/uploads/2026/11/postincidentreport-mo1550821.pdf)

![Verringerte Gateway-Kapazität, Teams-Verkehr und Spitzenlast treffen zusammen; Umleitung verteilt Last auf Server mit demselben Fehler.](/assets/diagrams/technical/de-2026-11-25-microsoft-365-code-red.svg)

Verringerte Gateway-Kapazität, Teams-Verkehr und Spitzenlast treffen zusammen; Umleitung verteilt Last auf Server mit demselben Fehler.

## Warum trat ein Fehler vom Juli erst im November auf?

Laut Microsofts Nachbericht steckte der Fehler in einem Windows-Update für Microsoft-365-Netzwerk-Gateways. Es wurde ab Juli über mehrere Wochen verteilt; mehr als drei Monate lang wurden keine Kundenauswirkungen beobachtet. Neuere Server mit mehr Kernen konnten jedoch mehr Verbindungsanfragen gleichzeitig verarbeiten, was die Konkurrenz um interne Sperren verstärken konnte. Die damaligen Lasttests verwendeten Server mit weniger Kernen und anderen Datenverkehr als während des Ausfalls. [Kopie des Microsoft-Nachberichts](https://www.365fanatic.com/wp-content/uploads/2026/11/postincidentreport-mo1550821.pdf)

Am 12. November war wegen regulärer Arbeiten ein Teil der Gateway-Kapazität nicht verfügbar, als Teams-Verkehr auf mit Exchange Online geteilte Gateways wechselte. Zunächst funktionierte der Dienst normal. Als die Nutzung in Nordamerika ihren üblichen Höchststand erreichte, antworteten Server nicht mehr; die automatische Umleitung erhöhte die Last pro verbleibendem Server. Auch die Umleitung zwischen Regionen leitete Anfragen an Server mit demselben Fehler. Der Bericht nennt **rund 23 Stunden und 50 Minuten aktiver Kundenauswirkungen**; danach liefen die Verarbeitung verzögerter E-Mails und die Stabilitätsüberwachung weiter. [Kopie des Microsoft-Nachberichts](https://www.365fanatic.com/wp-content/uploads/2026/11/postincidentreport-mo1550821.pdf)

## Auch Failover braucht eine Aufnahmegrenze

Bei der Failover-Planung muss geprüft werden, **wie viel zusätzliche Last die empfangende Seite jetzt verarbeiten kann**. Soll Region A beispielsweise 1.000 Anfragen abgeben und hat B im selben Zeitraum nur für 300 Anfragen freie Kapazität, kann eine vollständige Umleitung beide Regionen ausfallen lassen. Kritische Anfragen können bevorzugt angenommen und verzögerbare Aufgaben mit begrenzter Warteschlange behandelt oder vorübergehend abgewiesen werden. Das gezielte Reduzieren angenommener Anfragen bei Überlast heißt **Load Shedding**. [Microsoft Learn: Überlastungssteuerung](https://learn.microsoft.com/en-us/azure/well-architected/design-guides/throttling)

Dasselbe gilt für die Wiederherstellung. Bei diesem Ausfall erhielten Server beim Wiedereintritt in den Dienst aufgestaute Wiederverbindungsanfragen und antworteten erneut nicht. Betriebsteams können Anfragen schrittweise zurück auf wiederhergestellte Instanzen leiten und dabei Erfolgsrate der Verbindungen, Latenz und Warteschlangen gemeinsam beobachten. Lasttests sollten auf derselben Servergeneration wie im Betrieb **Spitzenlast, durch reguläre Arbeiten verringerte Kapazität, Failover und Wiederverbindung** kombinieren. Einzeltests können Probleme übersehen, die erst beim Zusammentreffen dieser Bedingungen entstehen. [Kopie des Microsoft-Nachberichts](https://www.365fanatic.com/wp-content/uploads/2026/11/postincidentreport-mo1550821.pdf)

## Getrennte Chats, gemeinsames Entscheidungsprotokoll

Laut internen Memos, die Reuters einsah, tauschten die Einsatzkräfte mehr als 11.000 Nachrichten in 11 Teams-Chaträumen aus. Diagnosedaten waren auf mehrere Systeme verteilt; aktive Hypothesen und Verantwortliche für Entscheidungen waren schwer auf einen Blick zu erkennen. Microsoft rief danach „Code Red“ aus und gab der Vermeidung weiterer Ausfälle und der besseren Wiederherstellung Vorrang. Die von Reuters berichtete **weltweite Wiederherstellung innerhalb einer Stunde** ist ein internes Ziel für künftige Störungen. [GeekNews](https://news.hada.io/topic?id=37797) · [Nachdruck des Reuters-Artikels](https://www.investing.com/news/stock-market-news/exclusivemicrosoft-declares-code-red-after-historic-outage-internal-memos-show-5048702)

Auch mit eigenen Untersuchungskanälen können Teams ein gemeinsames Störungsdokument führen. Oben stehen **aktuelle Kundenauswirkungen, bestätigte Fakten, laufende Hypothesen und Verantwortliche, letzte Maßnahme mit Ergebnis und Zeitpunkt der nächsten Mitteilung**. Statt nur „Server neu gestartet“ steht dort etwa: „Verbindungserfolgsrate erholte sich nach dem Neustart kurz, fiel aber beim Ansturm der Wiederverbindungen erneut.“ Die nächste Schicht kann entscheiden, ob sie die Maßnahme sofort wiederholt oder zuerst den Zulauf begrenzt. Prüfen Sie auch, ob der Zugang zum Dokument Abhängigkeiten mit dem wiederherzustellenden Dienst teilt. [Google SRE: Live-Störungsdokument](https://sre.google/sre-book/managing-incidents/#live-incident-state-document)

Beginnen Sie die nächste Übung mit **verminderter Kapazität einer Region zur Spitzenzeit**. Legen Sie fest, wie viele Anfragen die verbleibende Region annimmt, welche Funktionen zuerst eingeschränkt werden und wie schnell Anfragen zu wiederhergestellten Servern zurückkehren. Das Ende sollte nicht schon mit dem Start der Server erreicht sein: Nutzer sollen Kernfunktionen wieder verwenden können und der Rückstau soll abnehmen. So lässt sich das Wiederherstellungsziel messen.

Weiterlesen · [RestClient-traceparent-Weitergabe in Spring Boot 4.2 prüfen (Englisch)](https://youdozi.github.io/en/posts/2026-11-22-spring-boot-4-2-restclient-traceparent/)
