---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2021-07-23-unsuccessful-runner",
  "routeSlug": "2021-07-23-unsuccessful-runner",
  "kind": "post",
  "title": "Fehlenden Läufer in Java über Namenshäufigkeiten finden",
  "description": "Mit HashMap die Häufigkeiten der Finisher von denen der Teilnehmer abziehen. Doppelte Namen ohne Set-Differenz und die Bedingung genau eines fehlenden Läufers.",
  "categories": [
    "coding-test"
  ],
  "tags": [
    "java",
    "algorithms"
  ],
  "sourcePath": "src/content/posts/en/2021-07-23-unsuccessful-runner.md",
  "sourceSha256": "a8c9e485842a9d8718e6cec7f5d0bcbda5a716bad751608cc67094ac938487d6",
  "draftSha256": "1bcb07c627e6e4ed4144ff00c6935ac2a96ec4ab009007fe394bbf0c7feb87d0",
  "manifestPath": ".pipeline/technical-translations/batch-055/manifest.json",
  "manifestSha256": "1fe8bbde2d19f5780ba08f158519bd2d55fdec1dc863ec3bd9126705ddda372f",
  "publishedAt": "2026-10-31T15:21:36.540Z",
  "updatedAt": "2026-10-31T15:21:36.540Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 125,
    "approvedAt": "2026-10-31T15:21:36.540Z",
    "basis": "User explicitly requested applying all missing technical-post languages, review, verification and deployment on 2026-11-01, with standing PR merge authorization. Human approval denotes publication authorization; linguistic review is performed by AI, not human/native review."
  }
}
---
Um den fehlenden Läufer zu finden, zählen Sie Personen je Name, statt nur die Existenz eines Namens zu prüfen. Ziehen Sie die Finisherhäufigkeiten von den Teilnehmerhäufigkeiten ab. Die Aufgabe garantiert, dass genau ein Name mit Anzahl 1 verbleibt.

Die [Eingabebedingungen](https://school.programmers.co.kr/learn/courses/30/lessons/42576) erlauben bis zu 100.000 Teilnehmer, einen Finisher weniger und gleiche Namen. Namen bestehen aus 1–20 englischen Kleinbuchstaben. Die Finisherliste wird als gültige Teilnehmerliste mit einer entfernten Person vorausgesetzt.

## Ablauf

![Alle Teilnehmer zählen, jeden Finisher abziehen und den Namen mit einer verbleibenden Person zurückgeben.](/assets/diagrams/technical/de-2021-07-23-unsuccessful-runner.svg)

Alle Teilnehmer zählen, jeden Finisher abziehen und den Namen mit einer verbleibenden Person zurückgeben.

## Die Anzahldifferenz speichern

Speichern Sie die vollständige Klasse als `Solution.java`. Der Code des Ausgangsartikels wurde für Java 11 kompiliert und auf JDK 17 ausgeführt.

```java
import java.util.HashMap;
import java.util.Map;

public class Solution {
    public String solution(String[] participant, String[] completion) {
        Map<String, Integer> counts = new HashMap<>();
        for (String name : participant) counts.merge(name, 1, Integer::sum);
        for (String name : completion) counts.put(name, counts.get(name) - 1);
        for (Map.Entry<String, Integer> entry : counts.entrySet()) {
            if (entry.getValue() == 1) return entry.getKey();
        }
        throw new IllegalArgumentException("Expected exactly one missing runner");
    }
}
```

`merge(name, 1, Integer::sum)` beginnt einen neuen Namen bei 1 und erhöht vorhandene Anzahlen. Jeder Finisher verringert die Anzahl dieses Namens um eins. Bei Teilnehmern `[ana, bob, ana]` und Finishern `[bob, ana]` verbleibt für ana `2 - 1 = 1`.

Eine Set-Differenz würde verlieren, dass zwei Personen ana hießen. Anzahlen erhalten die Mehrfachvorkommen und bilden so eine fehlende Person ab. Eine andere Reihenfolge des Finisherarrays ändert das Ergebnis nicht.

## Nicht auf die HashMap-Reihenfolge vertrauen

[`HashMap`](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/HashMap.html) garantiert keine Iterationsreihenfolge. Den ersten positiven Eintrag zurückzugeben funktioniert, weil gültige Eingaben genau einen solchen Eintrag übrig lassen, nicht wegen einer bestimmten Reihenfolge. Der Code gibt den Namen mit verbleibender Anzahl 1 zurück.

Die abschließende Ausnahme ist keine vollständige Eingabevalidierung. Eine allgemeine Abgleich-API bräuchte weitere Regeln und Prüfungen für unbekannte Finisher oder mehrere fehlende Personen.

Bei auf 20 begrenzter Namenslänge und durchschnittlich konstanten Hashoperationen beträgt die Laufzeit O(n), mit O(u) zusätzlichem Speicher für u verschiedene Namen. Kein Benchmark belegt, dass Streams oder Schleifen allgemein schneller sind.

Wenn nur verschiedene Arten zählen, reicht ein Set. Vergleichen Sie [die Auswahlgrenze der Ponketmon-Aufgabe](/en/posts/2021-07-29-ponkemon/).
