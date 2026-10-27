---
title: "Java String Templates: JDK 21 Preview, JDK 23 Removal and Alternatives"
language: "en"
translationKey: "2023-09-23-jdk-21-string-templates"
routeSlug: "2023-09-23-jdk-21-string-templates"
kind: "post"
publishedAt: "2023-09-22T15:00:00.000Z"
categories:
  - "jdk"
tags:
  - "jdk21"
  - "openjdk"
  - "string templates"
updatedAt: "2026-10-27T01:24:58+00:00"
reviewedAt: "2026-10-27"
reviewStatus: "revised"
reviewScope: "Official documentation checked; runnable examples and version boundaries clarified."
reviewSources:
  - "https://inside.java/2024/06/20/newscast-71/"
  - "https://docs.oracle.com/en/java/javase/21/language/string-templates.html"
  - "https://docs.oracle.com/en/java/javase/21/language/preview-language-and-vm-features.html"
  - "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/text/MessageFormat.html"
  - "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/String.html"
description: "Run a complete JDK 21 String Templates example, understand its JDK 23 removal, and replace STR with tested Java formatting alternatives."
---
String Templates were preview features in JDK 21 and 22 and were removed in JDK 23. Adding `--enable-preview` to JDK 23 does not restore `STR`. For code that must move beyond those previews, use standard string APIs or a format-specific serializer. [Oracle's removal explanation](https://inside.java/2024/06/20/newscast-71/) describes the change.

## Which JDK can run the old example?

| JDK | String Templates status | What to do |
| --- | --- | --- |
| 21 | Preview | Use JDK 21 for both compilation and execution, with preview enabled. |
| 22 | Second preview | Use the matching JDK 22 compiler, runtime and preview settings. |
| 23 | Removed | Replace the preview syntax; flags cannot restore a removed feature. |

A compiler's `--release` flag is not a way to revive an older preview feature on a newer compiler. [Oracle's preview guide](https://docs.oracle.com/en/java/javase/21/language/preview-language-and-vm-features.html) requires the compiler from the preview's release.

## Run the historical JDK 21 example

Save this complete class as `Example.java`. This section requires JDK 21, even if another JDK is your default.

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

Check the selected tools, then compile and run in the directory containing the file:

```sh
javac -version
java -version
javac --enable-preview --release 21 Example.java
java --enable-preview Example
```

The output is `2 plus 3 equals 5`. Compilation also reports that the class uses preview features. `STR` is implicitly imported in this JDK 21 preview; a missing processor on a later JDK is not fixed by adding an import. See the [JDK 21 String Templates guide](https://docs.oracle.com/en/java/javase/21/language/string-templates.html).

## Replace preview syntax with standard APIs

Save the following as `FormattingExample.java`. It uses standard APIs and needs no preview flags. The complete class works on Java 17. `String.format` and `MessageFormat` use an explicit locale here so the numeric output is reproducible.

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

Output:

```text
2 plus 3 equals 5
2 plus 3 equals 5
2 plus 3 equals 5
It's ready
```

| Need | Suitable API | Detail to preserve |
| --- | --- | --- |
| A short expression | `+` | Parentheses around `x + y` keep the arithmetic explicit. |
| Repeated appends | `StringBuilder` | Useful when constructing text incrementally. |
| A format string | `String.format` or `.formatted` | `%d` and `%s` follow Formatter rules; use `String.format(Locale.ROOT, ...)` when an explicit locale is needed. |
| A localized message pattern | `MessageFormat` | Uses numbered arguments, an object array, and different quoting rules. |

`MessageFormat` treats single quotes as pattern syntax. The doubled quote in `It''s {0}` produces the literal apostrophe shown above. Replacing a `%s` pattern with `{0}` also means switching APIs and checking their locale behavior. [MessageFormat API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/text/MessageFormat.html), [String API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/String.html).

## Keep formatting separate from encoding

Neither `STR` nor ordinary formatting makes arbitrary values safe JSON, SQL or HTML. Use a JSON serializer, SQL parameter binding, or the rendering system's HTML escaping for the destination format. A string that looks correct for simple sample values can fail when a value contains quotes or backslashes.

Both complete classes were compiled and run with the commands above: the preview on JDK 21.0.1, and the standard alternative on JDK 17.0.8.1 and 21.0.1. The JDK 22 and 23 rows describe documented feature history; they were not executed in this environment.

A JDK upgrade also changes framework compatibility. For an older Spring application, see the [Spring Boot 2.7 to 3.0 migration sequence](/en/posts/2023-09-08-springboot3-migration/).
