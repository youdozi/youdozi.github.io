---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2021-07-29-interval-num",
  "routeSlug": "2021-07-29-interval-num",
  "kind": "post",
  "title": "Secuencia de paso x en Java: ampliar el tipo antes de multiplicar",
  "description": "Genera n valores de x a x*n con IntStream. Por qué mapToLong por sí solo no evita el desbordamiento de int; pasos positivos, negativos y nulos.",
  "categories": [
    "coding-test"
  ],
  "tags": [
    "java",
    "algorithms"
  ],
  "sourcePath": "src/content/posts/en/2021-07-29-interval-num.md",
  "sourceSha256": "4674cdefcccdc5107e92b9fe49ee186426b25a096d2687d60d42724c51d29cf4",
  "draftSha256": "18f937dcf80c742e027c470a64892babd822f568a1b1657ccbaf5900f51b40c6",
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
Los n valores que empiezan en x van de `x × 1` a `x × n`. Como los resultados pueden superar el rango de int, tanto el array de salida como **la propia multiplicación** deben usar long.

El [ejercicio](https://school.programmers.co.kr/learn/courses/30/lessons/12954) limita x entre -10 000 000 y 10 000 000, y n entre 1 y 1 000. El último valor puede tener una magnitud de 10 000 000 000, por lo que requiere un array de long.

## Flujo de procesamiento

![Convierte los índices desde cero en números de término, amplía x a long antes de multiplicar y recoge los valores en orden.](/assets/diagrams/technical/es-2021-07-29-interval-num.svg)

Convierte los índices desde cero en números de término, amplía x a long antes de multiplicar y recoge los valores en orden.

## Convertir un índice en un número de término

Guarda esta clase completa como `Solution.java`. El código del artículo original se compiló para Java 11 y se ejecutó en JDK 17.

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

[`IntStream.range(0, n)`](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/stream/IntStream.html) genera índices de 0 a n-1. Al multiplicar por `i + 1`, el primer valor es x y el último x×n. Empezar en x×0 cambiaría la secuencia solicitada.

| x | n | Resultado |
| --- | --- | --- |
| 2 | 5 | `[2,4,6,8,10]` |
| -4 | 2 | `[-4,-8]` |
| 0 | 3 | `[0,0,0]` |

Un x negativo produce valores decrecientes, mientras que x=0 solo produce ceros. Conserva el orden de los términos: no es un problema de ordenación.

## mapToLong por sí solo no protege el producto

Incluso dentro de `mapToLong`, evaluar primero `x * (i + 1)` usa multiplicación de int porque ambos operandos son int. `(long) (x * (i + 1))` también convierte después de que se haya producido el desbordamiento.

El ejemplo amplía primero un operando con `(long) x * (i + 1)`. Las comprobaciones del artículo original comparan los arrays de referencia completos que terminan en 10 000 000 000 y -10 000 000 000 para los límites positivo y negativo. También comparan entradas positivas, negativas y nulas más pequeñas con arrays construidos mediante sumas repetidas.

El tiempo es O(n) y el espacio, incluido el array devuelto, es O(n). La implementación sigue las condiciones del ejercicio, sin validar de forma general el tamaño de una secuencia ni entradas arbitrarias de una API.

Compara las [sumas con signo](/en/posts/2021-07-22-plus-minus/) y los [productos escalares de arrays](/en/posts/2021-07-22-dot-product/) para cálculos que caben en int dentro de sus límites. La [guía de ejercicios Java](/en/categories/coding-test/) conecta los cálculos de arrays con cadenas y colecciones.
