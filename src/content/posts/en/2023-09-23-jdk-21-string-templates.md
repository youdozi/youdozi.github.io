---
title: "Java String Templates: JDK 21 Preview and JDK 23 Removal"
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
updatedAt: "2026-10-24T06:00:52.186Z"
reviewedAt: "2026-10-24"
reviewStatus: "revised"
reviewScope: "English edition based on the reviewed Korean article; technical
  references and reproduction conditions retained."
reviewSources:
  - "https://inside.java/2024/06/20/newscast-71/"
  - "https://openjdk.org/jeps/430"
  - "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/text/Mes\
    sageFormat.html"
description: "Understand Java String Templates in JDK 21 and 22, their removal
  in JDK 23, matching preview flags, and standard String and MessageFormat
  alternatives."
---
## The compatibility point to check first

String Templates were a preview feature in JDK 21 and were previewed again in JDK 22. They were removed in JDK 23. Code using the `STR` processor from these previews cannot be enabled in JDK 23 simply by adding `--enable-preview`.

This article preserves the context of the original JDK 21 example and explains the constraints that matter when revisiting it. Preview syntax is tied to a particular JDK release and should not be assumed to become a permanent language feature.

## Reproduce a JDK 21 preview example

Use a JDK 21 compiler and runtime for this historical example:

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

Compile and run with the matching release and preview flags:

```sh
javac --enable-preview --release 21 Example.java
java --enable-preview Example
```

The expected output is `2 plus 3 equals 5`. Running a preview class on a different Java release is not a portable deployment strategy.

## Standard formatting alternatives

For ordinary formatting, standard APIs remain useful. In the following examples, `x` is 2 and `y` is 3:

```java
String result = "%1$d plus %2$d equals %3$d".formatted(x, y, x + y);
```

`String.formatted` is available from Java 15. For older Java environments, use `String.format` with the same format string.

`MessageFormat` uses numbered placeholders and accepts the values as an object array:

```java
java.text.MessageFormat format =
    new java.text.MessageFormat("{0} plus {1} equals {2}");
String result = format.format(new Object[] {x, y, x + y});
```

The array is significant: the original article’s `format(x, y, x + y)` call did not match that API. MessageFormat also has its own quoting and locale rules, so Java format strings and MessageFormat patterns are not interchangeable.

## Formatting is not escaping

Interpolating a value into text does not automatically produce valid JSON or a safe SQL statement. A quote or a backslash inside a value can require encoding in the destination format.

Use a JSON serializer to produce JSON and parameter binding to construct SQL queries. Treat HTML output with the escaping rules of the rendering system. The convenience of a formatting expression does not replace those contracts.

## Migration notes

- Identify whether existing code depends on a preview feature or a standard API.
- Record the compiler and runtime versions used by the example.
- Keep preview flags scoped to the matching build and test configuration.
- Replace preview syntax before moving to a release that no longer includes it.
- Keep shell or JShell output separate from compilable Java source.

The Korean article retains more of the original comparison examples; both editions include the removal and compatibility correction.

## Sources

- [Inside Java: what happened to String Templates](https://inside.java/2024/06/20/newscast-71/)
- [JEP 430: String Templates, preview in JDK 21](https://openjdk.org/jeps/430)
- [JDK 21 MessageFormat API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/text/MessageFormat.html)
- [JDK 21 String API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/String.html#formatted(java.lang.Object...))
