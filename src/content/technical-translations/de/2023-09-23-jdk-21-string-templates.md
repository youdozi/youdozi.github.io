---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2023-09-23-jdk-21-string-templates",
  "routeSlug": "2023-09-23-jdk-21-string-templates",
  "kind": "post",
  "title": "Java String Templates: JDK-21-Preview, Entfernung in JDK 23 und Alternativen",
  "description": "Ein vollständiges JDK-21-String-Templates-Beispiel ausführen, die Entfernung in JDK 23 verstehen und STR durch getestete Java-Formatierungsalternativen ersetzen.",
  "categories": [
    "jdk"
  ],
  "tags": [
    "jdk21",
    "openjdk",
    "string templates"
  ],
  "sourcePath": "src/content/posts/en/2023-09-23-jdk-21-string-templates.md",
  "sourceSha256": "82b3cfe0b6ea0478f27df7cea88e1b5974a7e661e6be9f9baa20c5d663c7a01b",
  "draftSha256": "07e0358a52b35d5922299d853bb485a78677a4e284fcf037610c02785bb85400",
  "manifestPath": ".pipeline/technical-translations/batch-058/manifest.json",
  "manifestSha256": "ddb52115d3c0de8ef810b654b7cab3396580933aec400022723b4ba51b5e8d96",
  "publishedAt": "2026-10-31T15:21:37.180Z",
  "updatedAt": "2026-10-31T15:21:37.180Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 125,
    "approvedAt": "2026-10-31T15:21:37.180Z",
    "basis": "User explicitly requested applying all missing technical-post languages, review, verification and deployment on 2026-11-01, with standing PR merge authorization. Human approval denotes publication authorization; linguistic review is performed by AI, not human/native review."
  }
}
---
String Templates waren Preview-Funktionen in JDK 21 und 22 und wurden in JDK 23 entfernt. `--enable-preview` stellt `STR` in JDK 23 nicht wieder her. Code, der über diese Previews hinaus nutzbar bleiben muss, sollte Standard-String-APIs oder einen formatspezifischen Serialisierer verwenden. [Oracles Erklärung zur Entfernung](https://inside.java/2024/06/20/newscast-71/) beschreibt die Änderung.

## Ablauf

![Gezeigt wird das standardkonforme FormattingExample, nicht das historische Preview-Beispiel. Es vergleicht drei Formatierungsformen und prüft die Apostrophbehandlung von MessageFormat.](/assets/diagrams/technical/de-2023-09-23-jdk-21-string-templates.svg)

Gezeigt wird das standardkonforme FormattingExample, nicht das historische Preview-Beispiel. Es vergleicht drei Formatierungsformen und prüft die Apostrophbehandlung von MessageFormat.

## Welches JDK kann das alte Beispiel ausführen?

| JDK | Status von String Templates | Vorgehen |
| --- | --- | --- |
| 21 | Preview | Zum Kompilieren und Ausführen JDK 21 mit aktivierter Preview verwenden. |
| 22 | Zweite Preview | Passenden JDK-22-Compiler, Laufzeit und Preview-Einstellungen verwenden. |
| 23 | Entfernt | Preview-Syntax ersetzen; Flags stellen entfernte Funktionen nicht wieder her. |

Mit `--release` lässt sich eine ältere Preview-Funktion auf einem neueren Compiler nicht wiederbeleben. [Oracles Preview-Leitfaden](https://docs.oracle.com/en/java/javase/21/language/preview-language-and-vm-features.html) verlangt den Compiler der jeweiligen Preview-Version.

## Das historische JDK-21-Beispiel ausführen

Speichern Sie die vollständige Klasse als `Example.java`. Dieser Abschnitt erfordert JDK 21, auch wenn ein anderes JDK als Standard eingestellt ist.

```java
public class Example {
    public static void main(String[] args) {
        int x = 2;
        int y = 3;
        String result = STR."\{x} plus \{y} equals \{x + y}";
        System.out.println(result);
    }
}
```

Prüfen Sie die gewählten Werkzeuge und kompilieren und starten Sie im Verzeichnis der Datei:

```sh
javac -version
java -version
javac --enable-preview --release 21 Example.java
java --enable-preview Example
```

Die Ausgabe lautet `2 plus 3 equals 5`. Der Compiler meldet außerdem die Verwendung von Preview-Funktionen. `STR` wird in dieser JDK-21-Preview implizit importiert; ein fehlender Prozessor in einem späteren JDK lässt sich nicht durch einen Import ergänzen. Siehe [JDK-21-Leitfaden zu String Templates](https://docs.oracle.com/en/java/javase/21/language/string-templates.html).

## Preview-Syntax durch Standard-APIs ersetzen

Speichern Sie Folgendes als `FormattingExample.java`. Es verwendet Standard-APIs ohne Preview-Flags. Die vollständige Klasse funktioniert auf Java 17. Für `String.format` und `MessageFormat` wird hier eine explizite Locale angegeben, damit die Zahlenausgabe reproduzierbar ist.

```java
import java.text.MessageFormat;
import java.util.Locale;

public class FormattingExample {
    public static void main(String[] args) {
        int x = 2;
        int y = 3;
        System.out.println(x + " plus " + y + " equals " + (x + y));
        System.out.println(String.format(Locale.ROOT, "%1$d plus %2$d equals %3$d", x, y, x + y));
        MessageFormat format = new MessageFormat("{0} plus {1} equals {2}", Locale.ROOT);
        System.out.println(format.format(new Object[] {x, y, x + y}));
        System.out.println(new MessageFormat("It''s {0}", Locale.ROOT)
            .format(new Object[] {"ready"}));
    }
}
```

```sh
javac FormattingExample.java
java FormattingExample
```

Ausgabe:

```text
2 plus 3 equals 5
2 plus 3 equals 5
2 plus 3 equals 5
It's ready
```

| Bedarf | Geeignete API | Zu erhaltendes Detail |
| --- | --- | --- |
| Kurzer Ausdruck | `+` | Klammern um `x + y` machen die Berechnung explizit. |
| Wiederholtes Anhängen | `StringBuilder` | Hilfreich beim schrittweisen Aufbau von Text. |
| Formatstring | `String.format` oder `.formatted` | `%d` und `%s` folgen den Formatter-Regeln; für eine explizite Locale `String.format(Locale.ROOT, ...)` verwenden. |
| Lokalisiertes Nachrichtenmuster | `MessageFormat` | Verwendet nummerierte Argumente, ein Objektarray und andere Quoting-Regeln. |

`MessageFormat` behandelt einfache Anführungszeichen als Mustersyntax. Das doppelte Zeichen in `It''s {0}` erzeugt den oben gezeigten wörtlichen Apostroph. Ein `%s`-Muster durch `{0}` zu ersetzen bedeutet auch, die API zu wechseln und ihr Locale-Verhalten zu prüfen. [MessageFormat-API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/text/MessageFormat.html), [String-API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/String.html).

## Formatierung von Kodierung trennen

Weder `STR` noch gewöhnliche Formatierung macht beliebige Werte zu sicherem JSON, SQL oder HTML. Verwenden Sie für das Zielformat einen JSON-Serialisierer, SQL-Parameterbindung oder HTML-Escaping des Renderers. Ein für einfache Beispielwerte korrekt aussehender String kann bei Anführungszeichen oder Backslashes scheitern.

Beide vollständigen Klassen wurden mit den obigen Befehlen kompiliert und ausgeführt: die Preview auf JDK 21.0.1, die Standardalternative auf JDK 17.0.8.1 und 21.0.1. Die Zeilen zu JDK 22 und 23 beschreiben dokumentierte Funktionshistorie; sie wurden in dieser Umgebung nicht ausgeführt.

Ein JDK-Upgrade verändert auch die Framework-Kompatibilität. Für eine ältere Spring-Anwendung siehe die [Migrationsfolge von Spring Boot 2.7 zu 3.0](/en/posts/2023-09-08-springboot3-migration/).
