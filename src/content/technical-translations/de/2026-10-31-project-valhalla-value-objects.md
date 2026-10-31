---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2026-10-31-project-valhalla-value-objects",
  "routeSlug": "2026-10-31-project-valhalla-value-objects",
  "kind": "post",
  "title": "Java Project Valhalla: Wertobjekte, Records und die JDK-28-Vorschau",
  "description": "Verstehen Sie Project Valhalla und JEP 401 anhand eines ausführbaren JDK-28-EA-Beispiels zu Record-Identität, Wertgleichheit und Monitorbeschränkungen mit klaren Optimierungsgrenzen.",
  "categories": [
    "jdk"
  ],
  "tags": [
    "java",
    "jdk",
    "valhalla",
    "value-objects",
    "jep-401"
  ],
  "sourcePath": "src/content/posts/en/2026-10-31-project-valhalla-value-objects.md",
  "sourceSha256": "28f39aa8186282dfb536d7054cb1df94683ddf593d1c9adea3387d1cdea9e345",
  "draftSha256": "7648de9311d0de496cd465630daf969a088157d78679a59626bed322c843ae6f",
  "manifestPath": ".pipeline/technical-translations/batch-078/manifest.json",
  "manifestSha256": "e685b2de5dafd8cfff8e8e996fa2b09613becb072bdd575b58b9eca9651474a3",
  "publishedAt": "2026-10-31T02:49:44.828Z",
  "updatedAt": "2026-10-31T02:49:44.828Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 118,
    "approvedAt": "2026-10-31T02:49:44.828Z",
    "basis": "2026-10-31 user instruction “진행해줘” immediately following delivery of the reviewed 72 complete translations in PR #118; interpreted as authorization to publish exactly batch-078 in all six languages. Separate AI language review is recorded in the manifest; this does not claim a human line-by-line review. Excludes the older 120 technical drafts and 318 pending news translations."
  }
}
---
Project Valhalla ist **ein OpenJDK-Projekt, das Daten ohne Bedarf an Objektidentität die Nutzung von Wertobjekten ermöglicht und der JVM damit mehr Freiheit für effiziente Speicherung und Übergabe gibt**. Bei der Prüfung am 31. Oktober 2026 zeigen die [Projektseite](https://openjdk.org/projects/valhalla/) und [JEP 401](https://openjdk.org/jeps/401) die Integration der ersten Wertobjekt-Vorschau in JDK 28. Dies ist keine finalisierte Funktion. Das folgende Beispiel lief auf JDK 28 EA Build 21.

## Warum Wertklassen, wenn Java bereits Records hat?

Gewöhnliche Objekte haben auch dann Identität, wenn ihre Felder übereinstimmen. Veränderliche Konten und Sperrobjekte brauchen diese Unterscheidung; Daten wie eine Koordinate `(3, 4)` benötigen möglicherweise nur ihren Wert.

Ein [`record`](https://docs.oracle.com/en/java/javase/17/language/records.html) deklariert Datenkomponenten und stellt Zugriffsmethoden, Konstruktoren und Methoden wie `equals()` bereit. Bestehende gewöhnliche Records lassen `==` weiterhin zwei separat erzeugte Objekte mit übereinstimmenden Komponenten unterscheiden. Der Modifikator `value` trifft eine separate Entscheidung: Objektidentität entfernen. Er lässt sich als `value record` mit Records kombinieren.

| Deklaration | Bedeutung in diesem Beispiel |
| --- | --- |
| `record IdentityPoint(int x, int y)` | Behält auch bei übereinstimmenden Komponenten unterschiedliche Objektidentitäten |
| `value record ValuePoint(int x, int y)` | Instanzen derselben Klasse mit demselben Feldzustand werden nicht anhand ihrer Identität unterschieden |
| `value record Label(String text)` | Hat keine Identität, doch `==` und `equals()` müssen weiterhin nicht übereinstimmen |

Die Instanzfelder einer Wertklasse sind `final`. Dadurch werden referenzierte Objekte nicht automatisch tief unveränderlich: Eine in einem Feld gespeicherte veränderliche Sammlung kann ihren Inhalt weiterhin ändern. Wertobjekte werden weiterhin über Objektreferenzen behandelt; sie werden nicht zu primitiven Typen.

## JDK-28-Vorschau ausprobieren

![Gewöhnliche und Wert-Records erzeugen, dann Gleichheit, Identität, Referenzfelder, einen null-Arrayplatz und die Monitorbeschränkung nacheinander prüfen](/assets/diagrams/technical/de-2026-10-31-project-valhalla-value-objects.svg)

Das Diagramm folgt dem folgenden Code. `Label` enthält unterschiedliche `String`-Objekte mit gleichem Inhalt, um den Referenzfeldvergleich sichtbar zu machen. Abschließend prüft das Programm, dass die Übergabe eines Wertobjekts an eine `Object`-Variable es nicht zu einem gültigen Monitor macht, und behandelt die erwartete Ausnahme.

Verwenden Sie ein separates Experimentverzeichnis, in dem `javac` und `java` auf denselben [JDK-28-EA](https://jdk.java.net/28/)-Build zeigen. Vergleichen Sie den Download mit seiner offiziellen SHA-256-Prüfsumme und bestätigen Sie den Build mit `java --version`. JDK 17 und 21 können diese Syntax nicht kompilieren. Vorschauoptionen sind beim Kompilieren und Ausführen erforderlich.

### `ValhallaExample.java`

```java
import java.util.Objects;

public class ValhallaExample {
    record IdentityPoint(int x, int y) {}
    value record ValuePoint(int x, int y) {}
    value record Label(String text) {}

    public static void main(String[] args) {
        IdentityPoint a = new IdentityPoint(3, 4);
        IdentityPoint b = new IdentityPoint(3, 4);
        ValuePoint p = new ValuePoint(3, 4);
        ValuePoint q = new ValuePoint(3, 4);
        System.out.println("record == " + (a == b));
        System.out.println("record equals " + a.equals(b));
        System.out.println("value == " + (p == q));
        System.out.println("value equals " + p.equals(q));
        System.out.println("record identity " + Objects.hasIdentity(a));
        System.out.println("value identity " + Objects.hasIdentity(p));

        Label first = new Label(new String(new char[] {'x'}));
        Label second = new Label(new String(new char[] {'x'}));
        System.out.println("label == " + (first == second));
        System.out.println("label equals " + first.equals(second));

        ValuePoint[] points = new ValuePoint[1];
        System.out.println("array slot null " + (points[0] == null));
        Object monitor = p;
        try {
            synchronized (monitor) {
                throw new AssertionError("A value object must not be a monitor");
            }
        } catch (IdentityException expected) {
            System.out.println("monitor " + expected.getClass().getSimpleName());
        }
    }
}
```

```sh
javac --enable-preview --release 28 ValhallaExample.java
java --enable-preview ValhallaExample
```

Diese Ausgabe wurde auf OpenJDK `28-ea+21-1707` für macOS AArch64 beobachtet. Der Vorschauhinweis des Compilers ist von dieser Standardausgabe getrennt.

```text
record == false
record equals true
value == true
value equals true
record identity true
value identity false
label == false
label equals true
array slot null true
monitor IdentityException
```

Die gewöhnlichen Records liefern bei `equals()` true, bei `==` jedoch false. Die Wert-Records haben nur Ganzzahlfelder; ihr übereinstimmender Feldzustand macht deshalb beide Vergleiche wahr. Auch [`Objects.hasIdentity()`](https://download.java.net/java/early_access/jdk28/docs/api/java.base/java/util/Objects.html#hasIdentity(java.lang.Object)) macht den Unterschied sichtbar.

## Sollten Wertobjekte mit == verglichen werden?

Verwenden Sie für fachliche Gleichheit weiterhin `equals()`. Bei Wertobjekten vergleicht `==` den Feldzustand innerhalb derselben Wertklasse und wendet `==` rekursiv auf Referenzfelder an. Referenzierte Objekte mit Identität bleiben unterscheidbar, wenn sie separate Objekte sind, selbst bei gleichem Inhalt. Primitive Felder werden nach Bitmuster verglichen, was ebenfalls von semantischer Gleitkommagleichheit abweichen kann. Die genauen Regeln stehen in den [Wertobjekt-Vergleichsregeln von JEP 401](https://openjdk.org/jeps/401#Comparing-value-objects).

Die beiden `Label`-Objekte besitzen Zeichenfolgen mit gleichem Inhalt; ihr generiertes Record-`equals()` liefert deshalb true. Ihre Zeichenfolgen sind unterschiedliche Identitätsobjekte, weshalb `==` false liefert. Verstehen Sie `value` nicht so, dass jedes Referenzfeld inhaltsbasiert verglichen wird.

Der neue Wert-Arrayplatz ist `null`, und die dynamische Verwendung eines Wertobjekts als Monitor wirft `IdentityException`. Das direkte Sperren eines Ausdrucks, dessen Typ eindeutig eine Wertklasse ist, kann stattdessen schon beim Kompilieren abgewiesen werden. Prüfen Sie vor der Migration identitätssensitive Verwendungen wie Sperren und identitätsbasierte Caches.

## Spart dies sofort Speicher oder ermöglicht `List<int>`?

Das Entfernen der Identität ermöglicht der JVM **Flattening**, also die Darstellung einer Referenz durch Feldzustand statt eines Zeigers, und **Skalarisierung**, also die Übergabe von Werten als separate Komponenten in Registern und ähnlichen Orten. Die Sprache garantiert weder ein bestimmtes Layout noch vermiedene Allokationen oder Beschleunigung. Die obige Ausgabe prüft Semantik; sie misst weder Heap-Nutzung noch Durchsatz.

Valhalla erstreckt sich über mehrere JDK-Versionen. Die [offizielle Roadmap](https://openjdk.org/projects/valhalla/) trennt Wertobjekte von null-beschränkter Speicherung, Array-Erweiterungen, der Vereinheitlichung primitiver Typen und Klassen sowie der Parametric JVM für die Spezialisierung von Generics. JEP 401 allein vervollständigt `List<int>` nicht und garantiert keine zusammenhängende Speicherung für jedes Array. Die begleitende [JEP 539](https://openjdk.org/jeps/539) liefert JVM-Unterstützung für strikte Feldinitialisierung; sie fügt dem Java-Quelltext keinen beliebigen Feldmodifikator `strict` hinzu.

Beginnen Sie Experimente mit kleinen Datentypen wie Koordinaten oder Geldbeträgen, die keine Identität brauchen, und vergleichen Sie das Verhalten auf demselben Build. Prüfen Sie Abhängigkeiten von Frameworks, Serialisierung und Sperren und messen Sie anschließend Allokation, GC und Durchsatz mit repräsentativen Arbeitslasten, bevor Sie den Nutzen beurteilen. Behandeln Sie diese Vorschau bei der Wahl eines Produktiv-JDK nicht als finalisierte, unterstützte Funktion. Der [JDK-Funktionsleitfaden](/en/posts/2023-09-20-jdk-21-release/) erklärt den Unterschied zwischen finalen und Vorschaufunktionen.
