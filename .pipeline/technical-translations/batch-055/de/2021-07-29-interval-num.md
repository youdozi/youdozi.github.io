---
language: "de"
translationKey: "2021-07-29-interval-num"
title: "Eine Folge mit Abstand x in Java: Vor der Multiplikation erweitern"
description: "Mit IntStream n Werte von x bis x*n erzeugen. Warum mapToLong allein keinen int-Überlauf verhindert, mit Prüfungen für positive, negative und Null-Schrittweiten."
state: "draft"
sourcePath: "src/content/posts/en/2021-07-29-interval-num.md"
sourceSha256: "4674cdefcccdc5107e92b9fe49ee186426b25a096d2687d60d42724c51d29cf4"
---
Die n Werte ab x sind `x × 1` bis `x × n`. Da die Ergebnisse den int-Bereich überschreiten können, müssen sowohl das Ergebnisarray als auch **die Multiplikation selbst** long verwenden.

Die [Aufgabe](https://school.programmers.co.kr/learn/courses/30/lessons/12954) begrenzt x auf -10.000.000 bis 10.000.000 und n auf 1 bis 1.000. Der Betrag des letzten Werts kann daher 10.000.000.000 erreichen und erfordert ein long-Array.

## Ablauf

![Nullbasierte Indizes werden zu Gliednummern. Vor der Multiplikation wird x zu long erweitert; die Ergebnisse bleiben in Reihenfolge.](2021-07-29-interval-num.svg)

Nullbasierte Indizes werden zu Gliednummern. Vor der Multiplikation wird x zu long erweitert; die Ergebnisse bleiben in Reihenfolge.

## Einen Index in eine Gliednummer umwandeln

Speichern Sie die vollständige Klasse als `Solution.java`. Der Code des Ausgangsartikels wurde für Java 11 kompiliert und auf JDK 17 ausgeführt.

```java
import java.util.stream.IntStream;

public class Solution {
    public long[] solution(int x, int n) {
        return IntStream.range(0, n)
                .mapToLong(i -> (long) x * (i + 1))
                .toArray();
    }
}
```

[`IntStream.range(0, n)`](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/stream/IntStream.html) erzeugt Indizes von 0 bis n-1. Durch die Multiplikation mit `i + 1` wird der erste Wert x und der letzte x×n. Ein Beginn bei x×0 würde die geforderte Folge verändern.

| x | n | Ergebnis |
| --- | --- | --- |
| 2 | 5 | `[2,4,6,8,10]` |
| -4 | 2 | `[-4,-8]` |
| 0 | 3 | `[0,0,0]` |

Ein negatives x erzeugt abnehmende Werte; bei x=0 entstehen nur Nullen. Behalten Sie die Reihenfolge der Glieder bei. Dies ist keine Sortieraufgabe.

## mapToLong allein schützt das Produkt nicht

Auch innerhalb von `mapToLong` wird `x * (i + 1)` zunächst als int-Multiplikation ausgewertet, weil beide Operanden ints sind. Auch `(long) (x * (i + 1))` konvertiert erst nach einem bereits aufgetretenen Überlauf.

Das Beispiel erweitert mit `(long) x * (i + 1)` zuerst einen Operanden. Die Prüfungen des Ausgangsartikels vergleichen vollständige Referenzarrays, die an den positiven und negativen Grenzen mit 10.000.000.000 beziehungsweise -10.000.000.000 enden. Kleinere positive, negative und Null-Eingaben werden außerdem mit Arrays aus wiederholter Addition verglichen.

Die Laufzeit beträgt O(n), der Speicherbedarf einschließlich des zurückgegebenen Arrays O(n). Die Implementierung folgt den Aufgabenbedingungen, statt die Folgenlänge oder beliebige API-Eingaben allgemein zu validieren.

Vergleichen Sie [vorzeichenbehaftete Summen](/en/posts/2021-07-22-plus-minus/) und [Skalarprodukte von Arrays](/en/posts/2021-07-22-dot-product/) für Berechnungen, die unter ihren Grenzen in int passen. Der [Leitfaden zu Java-Aufgaben](/en/categories/coding-test/) verbindet Array-Berechnungen mit Zeichenketten und Collections.
