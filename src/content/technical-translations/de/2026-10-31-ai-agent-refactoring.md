---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2026-10-31-ai-agent-refactoring",
  "routeSlug": "2026-10-31-ai-agent-refactoring",
  "kind": "post",
  "title": "Mit KI-Agenten refaktorieren: Verhalten bewahren und Änderungen prüfen",
  "description": "Refactoring-Aufträge begrenzen, Verhalten mit unabhängigen Erwartungen prüfen und Ergebnisse anhand von Diff und tatsächlicher Ausführung bewerten.",
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
  "draftSha256": "bfd5d4fc61690958f2c42ffe946cf10ef4ab271b8f4e684d0ee567004c46ebc3",
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
**Refactoring mit einem KI-Agenten beginnt mit der Festlegung des zu bewahrenden Verhaltens und des Änderungsumfangs; anschließend wird das Ergebnis anhand von Ausführungsnachweisen und Diff geprüft.** Eine kürzere Funktion oder die Agentenaussage „Tests bestanden“ reicht nicht als Abschluss. Prüfen Sie, ob Rückgabewerte, Ausnahmen und externe Auswirkungen gleich bleiben und ob die Prüfung selbst abgeschwächt wurde.

Dies ist ein werkzeugunabhängiger Leitfaden für Entwickler, die Git und Testausführung kennen. Er setzt weder eine bestimmte Produktoberfläche noch ein Modell voraus. Die folgenden Prompts sind selbst verfasste, kopier- und anpassbare Beispiele, keine Protokolle eines bestimmten Produkts oder Leistungsmessungen. Ausführungsergebnisse des Java-Beispiels sind separat gekennzeichnet.

## Was gehört in die erste Anfrage?

[Martin Fowler definiert Refactoring](https://refactoring.com/) als Änderung der internen Struktur bei Erhalt des extern beobachtbaren Verhaltens. Sind eine Richtlinienänderung oder Fehlerkorrektur nötig, unterscheiden Sie diese vom Refactoring, damit sich Ergebnisunterschiede vor und nach der Änderung beurteilen lassen.

Geben Sie dem Agenten neben Zieldateien auch Aufrufer, zugehörige Tests, Repository-Konventionen und tatsächliche Prüfbefehle. Statt ihn bedingungslos das gesamte Repository lesen zu lassen, beginnen Sie mit den für diese Entscheidung nötigen Pfaden. Eine Beschreibung des aktuellen Verhaltens samt Nachweisen vor jeder Dateibearbeitung kann verhindern, dass sich Änderungen aufgrund eines Missverständnisses ausweiten.

Die Versandrichtlinie des folgenden Beispiels besteht aus diesen **zur Veranschaulichung definierten Anforderungen**. Sie ist keine reale Dienstrichtlinie oder Störungsmeldung.

| Bedingung | Zu bewahrendes Verhalten |
| --- | --- |
| Negative Bestellzwischensumme | `IllegalArgumentException("subtotal")` werfen |
| Mitglied oder Bestellzwischensumme von mindestens 50.000 KRW | Basisversandkosten von 0 KRW |
| Andernfalls | Basisversandkosten von 3.000 KRW |
| Lieferung auf eine Insel oder in ein abgelegenes Gebiet | 3.000 KRW hinzufügen, unabhängig von kostenlosem Basisversand |

Die erste Anfrage an den Agenten lässt sich wie folgt formulieren. Nehmen Sie an, dass der spätere vollständige Code als `ShippingRefactorDemo.java` gespeichert wurde. Um die Bearbeitung mit einem Agenten zu üben, kopieren Sie zuerst den Inhalt von `before()` nach `after()`. Der vollständige Code unten enthält das fertige Refactoring zum Vergleich.

```text
Lies before(), after() und main() in ShippingRefactorDemo.java und analysiere nur.
Ändere noch keine Dateien.

Ziel: verschachtelte Verzweigungen in after() reduzieren und dabei das Versandkostenverhalten von before() bewahren.
Eingabebeträge sind in KRW und verwenden long.
Prüfe Ausnahmetyp und Meldung bei negativen Beträgen, die Grenze von 50.000 KRW
und Kombinationen aus kostenlosem Basisversand und Zuschlag für abgelegene Gebiete.

Liefere Codebelege für das aktuelle Verhalten, den bereits abgedeckten Testumfang,
zusätzliche zu prüfende Grenzfälle und eine minimale Änderung ausschließlich an after().
Errate und ändere keine unklaren Richtlinien.
```

Das nützliche Ergebnis dieser Stufe sind aktuelles Verhalten je Bedingung und die Änderungsstellen statt eines abstrakten „Plans zur Codequalitätsverbesserung“. Die Auslegung „Mitglieder zahlen immer 0 KRW Versand“ widerspricht etwa dem Zuschlag für abgelegene Gebiete und sollte vor der Implementierung korrigiert werden.

## Eine kleine Änderung vornehmen und Verhalten vergleichen

Dieses Beispiel **trennt die Berechnung von Basisversand und Zuschlag** aus duplizierten Verzweigungen heraus. Es bewahrt vorhandene Eingaben, Ausgaben und Ausnahmen, ohne Strategie-Interface oder Konfigurationsebene hinzuzufügen. Eine kleine Änderung lässt Prüfer darauf fokussieren, ob nur die Struktur geändert wurde und die Richtlinie gleich blieb. [Googles Leitfaden zu kleinen Änderungen](https://google.github.io/eng-practices/review/developer/small-cls.html)

![Bei negativer Zwischensumme dieselbe Ausnahme werfen, Basisversand aus Mitgliedschaft und Freigrenze berechnen, Zuschlag für abgelegene Gebiete addieren und Summe zurückgeben](/assets/diagrams/technical/de-2026-10-31-ai-agent-refactoring.svg)

Das Diagramm zeigt die Berechnungsreihenfolge in `after()` unten. Es zeigt nicht die internen Abläufe eines KI-Werkzeugs. `before()` und `after()` wurden zur Veranschaulichung geschrieben; `main()` prüft ausdrückliche erwartete Werte und vergleicht ihre Ergebnisse. Es läuft mit JDK 21 oder neuer ohne externe Abhängigkeiten.

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

Die folgende Ausgabe wurde mit Zulu JDK `21.0.1+12-LTS` erzielt. Sowohl die Anfangsversion mit identischem Inhalt in `after()` und `before()` als auch das fertige Refactoring unten erzeugten diese Ausgabe.

```text
examples=8
comparisons=24
negative-inputs=2
```

Statt Java-`assert`, das abhängig von `-ea` deaktiviert sein kann, wirft der Code bei einer Abweichung direkt `AssertionError`. Die gemeldeten Zahlen bezeichnen vorgegebene Fälle und Eingabekombinationen; sie repräsentieren keine Abdeckung einer gesamten Produktionscodebasis.

Verbinden Sie beim Implementierungsauftrag die zuvor geprüften Bedingungen mit Bearbeitungsumfang und Ausführungsbefehlen.

```text
Refaktoriere nur after() und bewahre den oben festgelegten Versandvertrag.
Ändere weder before(), main(), erwartete Werte noch FREE_THRESHOLD.
Bewahre öffentliche Eingaben und Ausgaben sowie Ausnahmetypen und Meldungen; ergänze weder Abhängigkeiten noch neue Ebenen.
Falls du Änderungen außerhalb dieser Datei für nötig hältst, erkläre die Gründe, ohne sie anzuwenden.

Führe javac --release 21 ShippingRefactorDemo.java und java ShippingRefactorDemo aus.
Liefere tatsächlich ausgeführte Befehle, Exit-Codes, beobachtete Ausgabe und Änderungs-Diff.
Scheitert eine Prüfung, grenze auslösende Bedingung und Ursache ein und behebe sie; lösche keine Prüfungen und ändere keine Erwartungen, um Erfolg zu erzielen.
```

Kann die Agentenumgebung keine Dateien bearbeiten oder Befehle ausführen, wenden Sie den vorgeschlagenen Patch selbst an und führen Sie dieselben Befehle aus. „Nicht ändern“ in einem Prompt vermittelt den Arbeitsumfang; es ersetzt keine tatsächlichen Werkzeugberechtigungen oder Dateizugriffsbeschränkungen.

## Sind bestandene Tests und bewahrtes Verhalten dasselbe?

Dieses Beispiel prüft 8 ausdrückliche erwartete Werte, vergleicht Vorher-/Nachher-Ergebnisse für 24 Eingabekombinationen und prüft die Ausnahmen beider Methoden bei negativen Eingaben. Es beweist keine Äquivalenz für jede `long`-Eingabe. Nur das Ergebnis von `before()` als richtige Antwort zu verwenden kann bestehende Fehler bewahren; nutzen Sie daher auch unabhängige Erwartungen und fachliche Anforderungen. Entdecken Sie einen bestehenden Fehler, entscheiden Sie separat, ob er korrigiert wird und welches Verhalten sich ändert.

Sie können auch ein Gegenbeispiel einführen, um zu prüfen, ob die Verifikation eine relevante Abweichung erkennt. Wird beispielsweise `subtotal >= FREE_THRESHOLD` in `after()` zu `subtotal > FREE_THRESHOLD` geändert, erhalten Nichtmitglieder mit einer Bestellung von exakt 50.000 KRW keinen kostenlosen Basisversand. Die Erwartungswertprüfung sollte dann scheitern.

Die Ausführung einer temporären Kopie mit ausschließlich dieser falsch geänderten Grenzbedingung scheiterte nachweislich mit `AssertionError: expected=0, actual=3000`. Dies bestätigt die Erkennung eines bestimmten Fehlers, garantiert aber nicht die Erkennung jeder falschen Änderung. Diese Mutation ist nicht auf den fertigen Code dieses Artikels angewendet.

Prüfen Sie in einem realen Projekt über Rückgabewerte hinaus das für Aufrufer sichtbare Verhalten: Ausnahmen, DB-Abfragen und Transaktionsgrenzen, Anzahl und Reihenfolge externer Aufrufe, serialisierte Ergebnisse und Ressourcenfreigabe. Das Bestehen dieses Beispiels einer reinen Funktion prüft keine DB- oder HTTP-Pfade. Ist Leistungssteigerung das Ziel, sind außerdem separate Messungen mit festen Eingaben und fester Umgebung nötig.

## Die Abschlussprüfung mit den Änderungen vor der Erklärung beginnen

Prüfen Sie Diff und Ausführungsergebnisse, bevor Sie die Änderungsbeschreibung des Agenten lesen. Achten Sie auf unnötige Dateiänderungen, gelöschte oder übersprungene Tests, verschluckte Ausnahmen und funktionsfremde Abhängigkeiten. `git diff --check` prüft Leerraumfehler und Ähnliches; es ist kein Test des Geschäftsverhaltens.

Falls ein separater Prüfkontext verfügbar ist, geben Sie ursprüngliche Anforderungen, Vorher-/Nachher-Code, Diff und Ausführungsnachweise weiter statt der anfänglichen Erfolgsaussage. Auch Reviews können falsche Befunde erzeugen; gleichen Sie jeden Kommentar mit Code- und Anforderungsnachweisen ab. [GitHubs Dokumentation zu Agentengrenzen](https://docs.github.com/en/copilot/responsible-use/agents) erläutert ebenfalls, dass generierter Code und Review-Kommentare ungenau sein können.

```text
Prüfe diese Änderung, ohne sie zu bearbeiten.
Eingabe: Versandkostenanforderungen, Vorher-/Nachher-Code, Diff, Testbefehle und tatsächliche Ergebnisse.

Finde Gegenbeispiele, die Rückgabewerte, Ausnahmen, die Grenze von 50.000 KRW oder Gebühren abgelegener Gebiete verändern.
Prüfe auch Änderungen außerhalb des Umfangs und abgeschwächte Tests.
Nenne je Befund Stelle, Beispieleingabe, beobachtbaren Unterschied und unterstützende Belege.
Behaupte nicht, Prüfungen ausgeführt zu haben, die du nicht ausgeführt hast.
```

Halten Sie die abschließende Übergabe kurz: Beschreiben Sie geänderte Struktur, bewahrtes Verhalten, tatsächlich ausgeführte Prüfungen und verbleibenden Prüfumfang. Scheitert ein Test, präzisieren Sie fehlerauslösende Eingabe und erwartetes Verhalten und grenzen Sie die Korrektur erneut ein; wachsen Änderungen, teilen Sie sie in separate Aufgaben. **Eine Änderung, die klein genug ist, dass Prüfer den Verhaltenserhalt erklären können**, bleibt bei der Arbeit mit KI-Agenten eine nützliche Abschlusseinheit.
