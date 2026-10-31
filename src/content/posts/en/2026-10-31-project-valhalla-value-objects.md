---
language: "en"
translationKey: "2026-10-31-project-valhalla-value-objects"
routeSlug: "2026-10-31-project-valhalla-value-objects"
kind: "post"
categories: ["jdk"]
tags: ["java", "jdk", "valhalla", "value-objects", "jep-401"]
publishedAt: "2026-10-30T15:22:17.028660+00:00"
updatedAt: "2026-10-30T15:22:17.028660+00:00"
title: "Java Project Valhalla: Value Objects, Records and the JDK 28 Preview"
description: "Understand Project Valhalla and JEP 401 through a runnable JDK 28 EA example comparing record identity, value equality and monitor restrictions, with clear optimization limits."
reviewedAt: "2026-10-31"
reviewStatus: "revised"
reviewScope: "Primary OpenJDK project/JEP/specification/API sources; JDK 28 EA Build 21 semantic example. No memory-layout, allocation, GC or throughput measurements; preview is not a finalized feature."
reviewSources: ["https://openjdk.org/projects/valhalla/", "https://openjdk.org/jeps/401", "https://openjdk.org/jeps/539", "https://jdk.java.net/28/", "https://docs.oracle.com/en/java/javase/17/language/records.html", "https://download.java.net/java/early_access/jdk28/docs/api/java.base/java/util/Objects.html", "https://openjdk.org/jeps/401#Comparing-value-objects"]
---
Project Valhalla is **an OpenJDK project that lets data without a need for object identity use value objects, giving the JVM more freedom to store and pass it efficiently**. Checked on October 31, 2026, the [project page](https://openjdk.org/projects/valhalla/) and [JEP 401](https://openjdk.org/jeps/401) show the first value-object preview integrated into JDK 28. This is not a finalized feature. The example below ran on JDK 28 EA Build 21.

## Why value classes when Java already has records?

Ordinary objects have identity even when their fields match. Mutable accounts and lock objects need that distinction, but data such as a coordinate `(3, 4)` may only need its value.

A [`record`](https://docs.oracle.com/en/java/javase/17/language/records.html) declares data components and provides accessors, constructors and methods such as `equals()`. Existing ordinary records still let `==` distinguish two separately constructed objects with matching components. The `value` modifier makes a separate choice: removing object identity. It can be combined with records as `value record`.

| Declaration | Meaning in this example |
| --- | --- |
| `record IdentityPoint(int x, int y)` | Retains distinct object identities even with matching components |
| `value record ValuePoint(int x, int y)` | Instances of the same class with the same field state are not distinguished by identity |
| `value record Label(String text)` | Lacks identity, but `==` and `equals()` still need not agree |

A value class’s instance fields are `final`. This does not automatically make referenced objects deeply immutable: a mutable collection stored in a field can still change its contents. Value objects are still handled through object references; they do not become primitive types.

## Try the JDK 28 preview

![Create ordinary and value records, then check equality, identity, reference fields, a null array slot and the monitor restriction in order](/assets/diagrams/2026-10-31-project-valhalla-value-objects-en.svg)

The diagram follows the code below. `Label` contains distinct `String` objects with matching contents to expose reference-field comparison. Finally, the program checks that moving a value object into an `Object` variable does not make it a valid monitor, and handles the expected exception.

Use a separate experiment directory where `javac` and `java` point to the same [JDK 28 EA](https://jdk.java.net/28/) build. Compare the download against its official SHA-256 and confirm the build with `java --version`. JDK 17 and 21 cannot compile this syntax. Preview flags are required at both compilation and execution.

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

This output was observed on OpenJDK `28-ea+21-1707` for macOS AArch64. The compiler’s preview notice is separate from this standard output.

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

The ordinary records return true from `equals()` but false from `==`. The value records have only integer fields, so their matching field state makes both comparisons true. [`Objects.hasIdentity()`](https://download.java.net/java/early_access/jdk28/docs/api/java.base/java/util/Objects.html#hasIdentity(java.lang.Object)) exposes the distinction too.

## Should value objects be compared with ==?

Continue using `equals()` for domain equality. For value objects, `==` compares field state within the same value class and recursively applies `==` to reference fields. Referents with identity remain distinguishable when they are separate objects, even if their contents match. Primitive fields are compared by bit pattern, which can also differ from semantic floating-point equality. See [value-object comparison rules in JEP 401](https://openjdk.org/jeps/401#Comparing-value-objects) for the precise rules.

The two `Label` objects have strings with matching contents, so their generated record `equals()` returns true. Their strings are distinct identity objects, so `==` returns false. Do not interpret `value` as making every reference field use content-based comparison.

The new value-array slot is `null`, and dynamically using a value object as a monitor throws `IdentityException`. Directly locking an expression whose type is clearly a value class may instead be rejected at compilation. Check identity-sensitive uses such as locking and identity-based caches before migration.

## Does this immediately save memory or enable `List<int>`?

Removing identity gives the JVM room for **flattening**, representing a reference through field state rather than a pointer, and **scalarization**, passing values as separate components in registers and similar locations. The language does not guarantee a particular layout, eliminated allocations or speedup. The output above checks semantics; it does not measure heap usage or throughput.

Valhalla spans multiple JDK releases. The [official roadmap](https://openjdk.org/projects/valhalla/) separates value objects from null-restricted storage, array enhancements, unifying primitives and classes, and the Parametric JVM for generic specialization. JEP 401 alone does not complete `List<int>` or guarantee contiguous storage for every array. The accompanying [JEP 539](https://openjdk.org/jeps/539) supplies JVM support for strict field initialization; it does not add an arbitrary `strict` field modifier to Java source.

Start experiments with small data types such as coordinates or monetary amounts that do not need identity, comparing behavior on the same build. Check framework, serialization and locking dependencies, then measure allocation, GC and throughput on representative workloads before judging the benefit. Do not treat this preview as a finalized, supported feature when choosing a production JDK. Continue with the [JDK feature guide](/en/posts/2023-09-20-jdk-21-release/) for the distinction between final and preview features.
