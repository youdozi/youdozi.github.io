---
language: "de"
translationKey: "2021-07-22-dot-product"
title: "Skalarprodukt von Java-Arrays: IntStream und Ganzzahlgrenzen"
description: "Mit IntStream entsprechende Arrayelemente multiplizieren und addieren. Vorzeichen, int-Grenzen und die Typumwandlung vor einem Überlauf bei der Multiplikation verstehen."
state: "draft"
sourcePath: "src/content/posts/en/2021-07-22-dot-product.md"
sourceSha256: "aa027f07c568f5c9d25dc08d3ee21ea8c23917f73f1409b25b221ad21be86463"
---
Das Skalarprodukt zweier Arrays ist die Summe der Produkte an übereinstimmenden Indizes. Wer zuerst die Elemente addiert oder die beiden Arraysummen multipliziert, berechnet etwas anderes.

Die [Aufgabe](https://school.programmers.co.kr/learn/courses/30/lessons/70128) liefert gleich lange Ganzzahlarrays mit einer Länge von 1–1.000 und Elementen von -1.000 bis 1.000. Innerhalb dieser Grenzen reicht `int` für das Ergebnis aus.

## Ablauf

![Jeden gemeinsamen Index auf ein Produkt abbilden und diese Produkte addieren. Die Grenzen der Aufgabe passen in int.](2021-07-22-dot-product.svg)

Jeden gemeinsamen Index auf ein Produkt abbilden und diese Produkte addieren. Die Grenzen der Aufgabe passen in int.

## Produkte nach Index berechnen und addieren

Diese vollständige Klasse als `Solution.java` speichern. Sie wurde für Java 11 kompiliert und setzt den Vertrag gleich langer Eingabearrays voraus.

```java
import java.util.stream.IntStream;

public class Solution {
    public int solution(int[] a, int[] b) {
        return IntStream.range(0, a.length)
                .map(i -> a[i] * b[i])
                .sum();
    }
}
```

[`IntStream.range(0, a.length)`](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/stream/IntStream.html) schließt den Endindex aus. Jeden Index auf `a[i] * b[i]` abbilden und die Produkte mit `sum()` zusammenfassen. Der Indexstream mit primitivem Datentyp erfordert keine Liste aus geboxten Integer-Objekten.

Für `[1, 2, 3, 4]` und `[-3, -1, 0, 2]` sind die Produkte `-3, -2, 0, 8`; das Ergebnis ist 3. Negative Vorzeichen müssen erhalten bleiben: Die Verwendung von Absolutwerten verändert das Skalarprodukt.

## Wann int ausreicht

Jedes Produkt hat einen Absolutwert von höchstens 1.000.000, bei höchstens 1.000 Summanden. Der Absolutwert der Summe ist somit durch 1.000.000.000 begrenzt und liegt im int-Bereich von Java. Die Grenzprüfungen decken auch die betragsmäßig größten positiven und negativen Summen über 1.000 Summanden ab.

Bei größeren Eingaben reicht es möglicherweise nicht, nur den Akkumulator auf long umzustellen. `(long) (a[i] * b[i])` konvertiert erst, nachdem die int-Multiplikation bereits übergelaufen ist. Mit `(long) a[i] * b[i]` muss die Typerweiterung **vor** der Multiplikation erfolgen; auch Summe und Rückgabetyp sind als long auszulegen. Die hier eingereichte Methode behält den int-Vertrag der Aufgabe bei.

Die Laufzeit beträgt O(n), der zusätzliche Speicherbedarf O(1). Dies ist keine allgemeine Vektorbibliothek mit Prüfungen auf ungleiche Längen, null-Arrays oder Elemente außerhalb des Wertebereichs.

Zur Umwandlung festgelegter englischer Ziffernwörter in eine Ganzzahl siehe [Ziffernwörter und numerische Zeichenfolgen](/en/posts/2021-07-23-number-word/).
