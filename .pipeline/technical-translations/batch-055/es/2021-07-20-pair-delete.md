---
language: "es"
translationKey: "2021-07-20-pair-delete"
title: "Eliminar pares iguales adyacentes en Java con una pila ArrayDeque"
description: "Reduce pares de caracteres iguales adyacentes con una pila. Invariante del prefijo, eliminación en cascada, límites de un millón de caracteres y costes de tiempo y espacio."
state: "draft"
sourcePath: "src/content/posts/en/2021-07-20-pair-delete.md"
sourceSha256: "a1962a62aeb00132eea16a0b3b607dfb9e256902ddc165613dbe7c044f14966e"
---
Una pila elimina pares de caracteres iguales adyacentes en un solo recorrido al conservar el resultado reducido del prefijo ya leído. Si el siguiente carácter coincide con la cima, elimina el par; en caso contrario, apílalo.

El [ejercicio](https://school.programmers.co.kr/learn/courses/30/lessons/12973) acepta 1–1 000 000 letras inglesas minúsculas y devuelve 1 si todo puede eliminarse, o 0 en caso contrario. Que el total de cada carácter sea par no basta, porque la eliminación depende de la adyacencia.

## Flujo de procesamiento

![La pila guarda el prefijo reducido. Cada carácter nuevo elimina la cima igual o se convierte en la nueva cima.](2021-07-20-pair-delete.svg)

La pila guarda el prefijo reducido. Cada carácter nuevo elimina la cima igual o se convierte en la nueva cima.

## Conservar el prefijo reducido

Guarda la clase completa como `Solution.java`. El código del artículo original se compiló para Java 11 y se ejecutó en JDK 17.

```java
import java.util.ArrayDeque;
import java.util.Deque;

public class Solution {
    public int solution(String s) {
        Deque<Character> stack = new ArrayDeque<>();
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (!stack.isEmpty() && stack.peek() == c) stack.pop();
            else stack.push(c);
        }
        return stack.isEmpty() ? 1 : 0;
    }
}
```

La pila contiene el prefijo procesado sin pares iguales adyacentes restantes. Un siguiente carácter igual crea un par eliminable en el límite, así que se desapila. Un carácter diferente no crea ese par, así que se apila. El mismo invariante se mantiene para el paso siguiente.

| Carácter leído | Pila: fondo → cima |
| --- | --- |
| b | b |
| a | ba |
| a | b |
| b | vacía |
| a | a |
| a | vacía |

Así, `baabaa` devuelve 1. En cambio, `abab` devuelve 0 pese a que ambos caracteres aparecen un número par de veces: no hay caracteres iguales adyacentes. La pila gestiona los límites expuestos por la eliminación sin sustituir repetidamente el texto de toda la cadena.

## ArrayDeque y complejidad

Usa [`ArrayDeque`](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/ArrayDeque.html) mediante las operaciones `push`, `peek` y `pop` de Deque. Como `c` es un char primitivo, `stack.peek() == c` desempaqueta Character para comparar; no compara la identidad de los objetos.

Cada carácter se apila como máximo una vez y se desapila como máximo una vez. Con las operaciones amortizadas de la deque, el tiempo es O(n) y el espacio adicional en el peor caso es O(n) cuando quedan caracteres. Las comprobaciones de ejecución del artículo original incluyen un millón de caracteres repetidos y un millón de caracteres alternos sin pares eliminables. Son comprobaciones de límites, no un benchmark de velocidad ni una garantía de memoria para cualquier entorno.

La información que conservas depende del problema: [el ejercicio del corredor que no termina](/en/posts/2021-07-23-unsuccessful-runner/) necesita frecuencias de nombres en lugar del orden adyacente.
