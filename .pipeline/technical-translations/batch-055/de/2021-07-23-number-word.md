---
language: "de"
translationKey: "2021-07-23-number-word"
title: "Englische Ziffernwörter mit Java String.replace umwandeln"
description: "Gültige Mischungen aus Ziffern und zero bis nine durch wörtliche Ersetzung normalisieren. Unterschiede zwischen replace und replaceAll sowie Integer-Grenzen und Geltungsbereich."
state: "draft"
sourcePath: "src/content/posts/en/2021-07-23-number-word.md"
sourceSha256: "28614468f78703f7e406439ee8b23b83e06091ae7f42ed9835cd50c6d1bb2e87"
---
Bei gültigen Eingaben aus Ziffern und Ziffernwörtern werden die festen Wörter `zero` bis `nine` durch Ziffern ersetzt und das Ergebnis als Ganzzahl geparst. Die Suchbegriffe sind Literale; daher reicht `String.replace` ohne `replaceAll` aus.

Die [Aufgabe](https://school.programmers.co.kr/learn/courses/30/lessons/81301) garantiert gültige kleingeschriebene Ziffernwörter und Ziffern, ein Ergebnis von 1 bis 2.000.000.000 und keine führende Null. Dies ist kein Parser für allgemeine englische Zahlausdrücke.

## Ablauf

![Die festen Wörter zero bis nine werden wörtlich durch Ziffern ersetzt; anschließend wird die entstandene Dezimalzeichenkette geparst.](2021-07-23-number-word.svg)

Die festen Wörter zero bis nine werden wörtlich durch Ziffern ersetzt; anschließend wird die entstandene Dezimalzeichenkette geparst.

## Die zehn festen Wörter ersetzen

Speichern Sie die vollständige Klasse als `Solution.java`. Zusätzliche Imports sind unnötig; der Code des Ausgangsartikels wurde mit Java 11 als Ziel kompiliert und ausgeführt.

```java
public class Solution {
    public int solution(String s) {
        String[] words = {"zero", "one", "two", "three", "four",
                "five", "six", "seven", "eight", "nine"};
        for (int digit = 0; digit < words.length; digit++) {
            s = s.replace(words[digit], Integer.toString(digit));
        }
        return Integer.parseInt(s);
    }
}
```

[`String.replace(CharSequence, CharSequence)`](https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/lang/String.html) ersetzt wörtlich. `replaceAll` interpretiert sein erstes Argument als regulären Ausdruck. Keines der zehn Wörter benötigt hier Regex-Syntax.

Zum Beispiel wird `one4seveneight` zu `1478` und `23four5six7` zu `234567`. Eine reine Zifferneingabe wie `123` ergibt weiterhin 123. `two` mit neun folgenden `zero`-Wörtern ergibt 2.000.000.000 und liegt im int-Bereich.

Ersetzte Ziffern können kein neues Ziffernwort erzeugen, und keines der zehn Wörter enthält ein anderes Wort dieser Menge. Deshalb funktioniert diese Reihenfolge. Ungültige Wörter, Leerzeichen, Großbuchstaben und Zahlen außerhalb des Bereichs sind nicht durch die Aufgabe abgedeckt. Ein Parsefehler bei beliebigen Eingaben wird durch diese Methode nicht zu einer gültigen Ganzzahl repariert.

Bei zehn festen Wörtern beträgt die Laufzeit O(n) in der Eingabelänge. Zeichenketten sind unveränderlich; daher können Zwischenzeichenketten entstehen. Der zusätzliche Speicherbedarf ist O(n). Kein Benchmark belegt, dass diese Methode für die kleinen Eingaben schneller als andere Parser ist.

Vergleichen Sie die [Normalisierung neuer IDs](/en/posts/2021-07-19-new-id/) für eine Umformung, bei der reguläre Ausdrücke nützlich sind.
