---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2021-07-23-unsuccessful-runner",
  "routeSlug": "2021-07-23-unsuccessful-runner",
  "kind": "post",
  "title": "Encontrar al corredor que no termina en Java con frecuencias de nombres",
  "description": "Resta las frecuencias de quienes terminan de las de participantes con HashMap. Gestiona nombres repetidos sin diferencias de Set y explica la condición de un único corredor ausente.",
  "categories": [
    "coding-test"
  ],
  "tags": [
    "java",
    "algorithms"
  ],
  "sourcePath": "src/content/posts/en/2021-07-23-unsuccessful-runner.md",
  "sourceSha256": "a8c9e485842a9d8718e6cec7f5d0bcbda5a716bad751608cc67094ac938487d6",
  "draftSha256": "99dbe87938d61abe4913946ddd43f0c63b3d38efbf11cf696c525525969f2c9d",
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
Para encontrar al corredor que no termina, cuenta personas por nombre en lugar de comprobar solo si el nombre existe. Resta las frecuencias de quienes terminan de las de participantes; el ejercicio garantiza que exactamente un nombre conserva un recuento de 1.

Las [condiciones de entrada](https://school.programmers.co.kr/learn/courses/30/lessons/42576) permiten hasta 100 000 participantes, un corredor menos que termina y nombres repetidos. Los nombres contienen 1–20 letras inglesas minúsculas. Se supone que la lista de quienes terminan es una lista válida de participantes de la que se ha quitado a una persona.

## Flujo de procesamiento

![Cuenta a cada participante, resta a cada corredor que termina y devuelve el nombre cuyo recuento restante es uno.](/assets/diagrams/technical/es-2021-07-23-unsuccessful-runner.svg)

Cuenta a cada participante, resta a cada corredor que termina y devuelve el nombre cuyo recuento restante es uno.

## Guardar la diferencia de recuentos

Guarda esta clase completa como `Solution.java`. El código del artículo original se compiló para Java 11 y se ejecutó en JDK 17.

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

`merge(name, 1, Integer::sum)` inicia un nombre nuevo en 1 e incrementa los existentes. Cada corredor que termina reduce en uno el recuento de su nombre. Con participantes `[ana, bob, ana]` y quienes terminan `[bob, ana]`, para ana queda `2 - 1 = 1`.

La diferencia de Set perdería el hecho de que dos personas se llamaban ana. Los recuentos mantienen la multiplicidad y representan así a una persona ausente. Reordenar el array de quienes terminan no cambia el resultado.

## No depender del orden de HashMap

[`HashMap`](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/HashMap.html) no garantiza el orden de iteración. Devolver la primera entrada positiva funciona porque una entrada válida deja exactamente una, no porque exista un orden concreto. El código devuelve el nombre cuyo recuento restante es 1.

La excepción final no es una validación completa de las entradas. Una API general de conciliación necesitaría reglas y comprobaciones adicionales para corredores desconocidos en la lista final o varias personas ausentes.

Con nombres limitados a 20 caracteres y operaciones hash de tiempo constante en promedio, el tiempo es O(n), con O(u) de espacio adicional para u nombres distintos. Ningún benchmark demuestra que los streams o los bucles sean universalmente más rápidos.

Cuando solo importan los tipos distintos, basta con un Set; compara [el límite de selección del ejercicio Ponketmon](/en/posts/2021-07-29-ponkemon/).
