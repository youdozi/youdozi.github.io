---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2026-11-03-jdk-gc-evolution",
  "routeSlug": "2026-11-03-jdk-gc-evolution",
  "kind": "post",
  "title": "Recolección de basura en JDK: de JDK 27 a 1.4, con G1, ZGC, Shenandoah y CMS",
  "description": "Repase las incorporaciones, valores predeterminados y eliminaciones de GC de HotSpot desde JDK 27 y 28 EA hasta versiones anteriores. Compare recolectores y ejecute un ejemplo reproducible de registros de GC.",
  "categories": [
    "java"
  ],
  "tags": [
    "jdk",
    "gc",
    "g1",
    "zgc",
    "shenandoah",
    "jvm",
    "performance"
  ],
  "sourcePath": "src/content/posts/en/2026-11-03-jdk-gc-evolution.md",
  "sourceSha256": "01667d7b4b2824ee749cd29f79a08f74627c3725ff551aa08ed090d48f9fd693",
  "draftSha256": "7a941ce0397bf778b7a3ddbe2014ade3f548eff18ce54d0e43b0731b251c8415",
  "manifestPath": ".pipeline/technical-translations/batch-137/manifest.json",
  "manifestSha256": "a47db22796f8ae3ce1acbdd6162e7da37c5147ddcf9399188f2018d3829bfcf4",
  "publishedAt": "2026-11-03T01:49:36.356Z",
  "updatedAt": "2026-11-03T01:49:36.356Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 137,
    "approvedAt": "2026-11-03T01:49:36.356Z",
    "basis": "사용자가 JDK GC 한영 글 게시 완료 후 다국어 지원도 진행해줘라고 요청하여 기존 지원 언어 여섯 개의 전체 번역과 현지화 그림 게시를 승인함. 별도 AI 검토는 사용자 게시 승인과 구분함."
  }
}
---

**Para HotSpot moderno, establezca una referencia medida con G1, compare ZGC o Shenandoah si hay objetivos estrictos de latencia y considere Parallel GC cuando prime el rendimiento.** Antes de copiar opciones antiguas de la JVM, compruebe qué recolector se selecciona de forma predeterminada y qué implementaciones existen en la distribución concreta del JDK.

La fecha de referencia es el **2026-11-03**. [JDK 27](https://jdk.java.net/27/) es la versión de funcionalidades más reciente con disponibilidad general; [JDK 28 está en Early Access](https://jdk.java.net/28/). Este artículo trata de **OpenJDK HotSpot**, no de todas las implementaciones de la JVM. Las líneas LTS de Oracle —8, 11, 17, 21 y 25— son opciones habituales de despliegue, pero los plazos de soporte y las condiciones de actualización dependen del distribuidor. [Hoja de ruta de soporte de Oracle](https://www.oracle.com/java/technologies/java-se-support-roadmap.html)

## Del JDK más reciente a las versiones anteriores

| JDK | Principal cambio en GC | Qué comprobar en los despliegues existentes |
| --- | --- | --- |
| **28 EA** | [JEP 535](https://openjdk.org/jeps/535), que establece el modo generacional de Shenandoah como predeterminado, tiene el estado Targeted | No lo considere entregado en una versión GA. No convierte a Shenandoah en el recolector predeterminado de toda la JVM |
| **27** | [JEP 523](https://openjdk.org/jeps/523) selecciona G1 de forma predeterminada independientemente del número de CPU y del tamaño de la memoria | Revise la selección predeterminada de los servicios que antes seleccionaban Serial en entornos pequeños |
| **26** | [JEP 522](https://openjdk.org/jeps/522) reduce la sobrecarga de sincronización en G1 para mejorar el rendimiento | Una mejora en el proyecto original no demuestra que su servicio obtenga el mismo porcentaje de mejora |
| **25** | [JEP 521](https://openjdk.org/jeps/521) convierte Generational Shenandoah de experimental en una funcionalidad estable | La disponibilidad de un modo y su selección predeterminada son cambios diferentes |
| **24 / 23** | 24 elimina ZGC no generacional ([JEP 490](https://openjdk.org/jeps/490)); 23 establece el modo generacional como predeterminado al seleccionar ZGC ([JEP 474](https://openjdk.org/jeps/474)). 24 también introduce Generational Shenandoah experimental ([JEP 404](https://openjdk.org/jeps/404)) | Un valor predeterminado dentro de ZGC no cambia el recolector predeterminado de la JVM |
| **21 / 17 / 15** | 21 introduce Generational ZGC ([JEP 439](https://openjdk.org/jeps/439)). ZGC y Shenandoah se convierten en funcionalidades estables en 15 ([JEP 377](https://openjdk.org/jeps/377), [379](https://openjdk.org/jeps/379)), por lo que también lo son en 17 | Seleccione ZGC generacional explícitamente en 21. Compruebe por separado la disponibilidad según la plataforma y la distribución |
| **14 / 12 / 11** | 14 elimina CMS ([JEP 363](https://openjdk.org/jeps/363)). 12 añade Shenandoah experimental ([JEP 189](https://openjdk.org/jeps/189)); 11 introduce ZGC y Epsilon experimentales ([JEP 333](https://openjdk.org/jeps/333), [318](https://openjdk.org/jeps/318)) | Distinga el estado experimental histórico del estado estable actual; el soporte inicial no abarcaba todas las plataformas |
| **9** | G1 pasa a ser el predeterminado para la configuración de servidor ([JEP 248](https://openjdk.org/jeps/248)); CMS queda obsoleto ([JEP 291](https://openjdk.org/jeps/291)); llega el registro unificado de GC ([JEP 271](https://openjdk.org/jeps/271)) | No migre sin cambios los analizadores de registros ni las opciones de JDK 8 |
| **8** | Parallel es el predeterminado para rendimiento en máquinas de clase servidor; G1 y CMS son alternativas. Se elimina PermGen ([JEP 122](https://openjdk.org/jeps/122)) | Parallel no era el predeterminado en todos los entornos. No traslade las opciones de PermGen a nuevos despliegues |
| **7u4 / 6 / 5 / 1.4.1** | Oracle JDK admite G1 desde 7u4. La recolección completa paralela llega en 5u6 y mejora en 6. La documentación de 1.4.1 presenta la recolección paralela de la generación joven y la recolección concurrente de la generación antigua | Distinga la primera recolección paralela de la generación joven de la posterior recolección paralela de la generación antigua |

Interprete los valores predeterminados de JDK 8 en el contexto de su [guía de ergonomía](https://docs.oracle.com/javase/8/docs/technotes/guides/vm/gctuning/ergonomics.html). Los hitos anteriores están documentados en el [historial de soporte de G1](https://docs.oracle.com/javase/8/docs/technotes/guides/vm/G1.html), la [descripción de Parallel Compaction](https://docs.oracle.com/javase/8/docs/technotes/guides/vm/par-compaction-6.html) y el [artículo sobre GC de JDK 1.4.1](https://www.oracle.com/technical-resources/articles/java/garbagecollection-in-java-applications-using-jdk141.html). Las recomendaciones históricas de tamaño del heap y los objetivos de pausa describen su época; no son los valores predeterminados de despliegue actuales.

La tabla selecciona hitos importantes. No enumera todas las correcciones de cada actualización ni afirma que se haya ejecutado cada versión histórica para este artículo.

## Tres distinciones antes de elegir un recolector

GC recupera la memoria de objetos **inalcanzables desde las raíces de GC**, como las referencias conservadas por los hilos en ejecución. Una caché o una colección global pueden mantener objetos alcanzables incluso cuando la aplicación ya no los necesita. La recolección generacional aprovecha la observación de que muchos objetos mueren pronto y algunos sobreviven, recolectando de forma diferente los objetos jóvenes y antiguos. [Implementación de GC de HotSpot](https://docs.oracle.com/en/java/javase/27/gctuning/garbage-collector-implementation.html)

**Paralelo** significa que varios hilos de GC trabajan juntos; **concurrente** significa que parte del trabajo de GC se solapa con la ejecución de la aplicación. Son dimensiones diferentes. Una fase **stop-the-world (STW)** pausa la ejecución de la aplicación. Los recolectores concurrentes también pueden tener pausas breves o bloqueos de asignación; la concurrencia no elimina la latencia de las solicitudes.

El marcado identifica los objetos vivos; el barrido deja el espacio recuperable disponible para reutilizarlo. La compactación mueve objetos vivos para consolidar el espacio libre, mientras que la evacuación copia los supervivientes de regiones seleccionadas a otros lugares. Los recolectores combinan estas tareas de distintas formas entre generaciones, regiones, trabajo paralelo y trabajo concurrente.

| Recolector | Enfoque principal | Condiciones que comparar |
| --- | --- | --- |
| Serial | Un hilo de GC; la baja sobrecarga de coordinación puede ser adecuada para tareas pequeñas | Mida el rendimiento y las pausas incluso con un heap pequeño o CPU restringida |
| Parallel | Varios hilos de recolección, con prioridad al rendimiento | Compare el tiempo de finalización de los lotes y las pausas toleradas |
| G1 | Regiones, marcado concurrente y evacuación durante las pausas | Referencia general para servidores; su objetivo de pausa no es una garantía de tiempo real |
| ZGC | Realiza gran parte de la reubicación y del trabajo con referencias de forma concurrente para lograr pausas breves | Observe conjuntamente el margen de CPU y heap, la tasa de asignación y la latencia de la aplicación |
| Shenandoah | Recolector de pausas bajas con reubicación concurrente; el estado del modo generacional varía según la versión | Compruebe primero la disponibilidad en la distribución y el modo seleccionado |
| CMS / Epsilon | CMS es el recolector histórico de marcado y barrido concurrente; Epsilon experimental no recupera memoria | CMS no está disponible en el JDK más reciente. Epsilon no sustituye al GC general de un servicio |

Para Serial y Parallel, empiece por la [guía actual de selección del recolector](https://docs.oracle.com/en/java/javase/27/gctuning/available-collectors.html). La [guía de ajuste de G1](https://docs.oracle.com/en/java/javase/27/gctuning/garbage-first-garbage-collector-tuning.html) explica el comportamiento de G1 y sus objetivos de pausa. La [documentación histórica de CMS](https://docs.oracle.com/en/java/javase/13/gctuning/concurrent-mark-sweep-cms-collector.html) describe las fases concurrentes y las restricciones de fragmentación; [JEP 318](https://openjdk.org/jeps/318) especifica que Epsilon no recupera memoria.

## Compruebe el modo generacional además del recolector

Para ZGC en JDK 21, `-XX:+UseZGC -XX:+ZGenerational` selecciona el modo generacional. En 23, `-XX:+UseZGC` selecciona el modo generacional de forma predeterminada; 24 elimina la implementación no generacional. Declarar obsoleta una opción y eliminarla son pasos distintos de eliminar una implementación. JDK 27 rechazó `-XX:+ZGenerational` en este laboratorio, por lo que no debe añadirla a la configuración actual. [Guía actual de ZGC](https://docs.oracle.com/en/java/javase/27/gctuning/z-garbage-collector.html)

Compruebe Shenandoah por separado. El modo generacional estable introducido en 25 se selecciona con `-XX:+UseShenandoahGC -XX:ShenandoahGCMode=generational`. **Seleccionar únicamente Shenandoah en 27 no demuestra que se haya seleccionado el modo generacional.** JEP 535 apunta a 28 y sigue en estado Targeted en la fecha de referencia. Las opciones de compilación y las adaptaciones a versiones anteriores pueden afectar a los recolectores que ofrece una distribución; compruebe el ejecutable concreto.

## Lea los registros del mismo programa de asignación

Este **laboratorio de un solo hilo** ilustra la vida de los objetos y los registros de GC. Asigna 8192 arrays de 128 KiB, un total de 1 GiB de datos útiles de arrays, mientras sustituye referencias en 64 posiciones rotativas. Los datos útiles retenidos al final ocupan 8 MiB; las cabeceras de los arrays, las referencias y la memoria de la JVM son adicionales. No implementa una carga de producción ni una prueba comparativa de GC.

![Crear 64 posiciones de referencias, asignar repetidamente un array de 128 KiB, sustituir la referencia de una posición y acumular una suma de comprobación durante 8192 iteraciones, y después imprimir el resultado](/assets/diagrams/technical/es-2026-11-03-jdk-gc-evolution.svg)

El diagrama sigue la asignación y la sustitución de referencias del código. La JVM decide cuándo recuperar los objetos inalcanzables; el código no llama a `System.gc()`. No suponga que cada objeto sustituido se recupera de inmediato.

### `GcProbe.java`

```java
import java.lang.management.GarbageCollectorMXBean;
import java.lang.management.ManagementFactory;

public final class GcProbe {
    private static volatile byte[][] retained;
    private static volatile long checksum;

    public static void main(String[] args) {
        System.out.println("runtime=" + System.getProperty("java.runtime.version"));
        for (GarbageCollectorMXBean gc : ManagementFactory.getGarbageCollectorMXBeans()) {
            System.out.println("collector=" + gc.getName());
        }
        retained = new byte[64][];
        for (int i = 0; i < 8192; i++) {
            byte[] block = new byte[128 * 1024];
            block[0] = (byte) i;
            retained[i % retained.length] = block;
            checksum += block[0] & 0xff;
        }
        System.out.println("iterations=8192 retainedSlots=" + retained.length
                + " checksum=" + checksum);
    }
}
```

Los arrays siguen siendo alcanzables desde el exterior a través de `retained`. Aun así, este pequeño programa no determina la distribución de vida de los objetos ni el cuello de botella de un servicio de producción.

### Seleccione cuatro recolectores e inspeccione los registros en JDK 27

Estos comandos usan una shell de estilo Unix. Sustituya `GC_JDK` por el **directorio de instalación del JDK**, guarde el archivo Java en un nuevo directorio de trabajo y ejecute allí los comandos. No se necesitan bibliotecas externas ni solicitudes de red. Cada ejecución usa un heap máximo de 128 MiB y registros rotativos de tamaño limitado.

```sh
GC_JDK="/path/to/jdk-27"
"$GC_JDK/bin/java" -version
mkdir -p out logs
"$GC_JDK/bin/javac" -d out GcProbe.java
for gc in G1 Parallel Serial Z; do
  "$GC_JDK/bin/java" "-XX:+Use${gc}GC" -Xms128m -Xmx128m \
    '-Xlog:gc*,safepoint:file=logs/gc-%p.log:time,uptime,level,tags:filecount=3,filesize=5M' \
    -cp out GcProbe
done
```

`%p` se expande al PID de la JVM, lo que distingue los registros de ejecuciones separadas. Compruebe que las cuatro ejecuciones terminan con la siguiente línea. Las líneas anteriores del entorno de ejecución y del recolector dependen del JDK y del recolector.

```text
iterations=8192 retainedSlots=64 checksum=1044480
```

El entorno de ejecución utilizado fue **macOS arm64, Zulu 8u392-b08 y Temurin 21.0.13+9, 25.0.5+8 y 27.0.1.0.2+1**. Las versiones archivadas ilustran el comportamiento histórico; esto no es una recomendación de combinaciones actuales de actualizaciones de seguridad. El alcance ejecutado fue:

| JDK | Ejecuciones comprobadas |
| --- | --- |
| 8 | Parallel predeterminado, G1 y CMS explícitos, incluida la finalización y los registros de GC antiguos |
| 21 | ZGC no generacional y explícitamente generacional, incluida la finalización y los registros |
| 25 | ZGC generacional seleccionado con la opción de ZGC, incluida la finalización y los registros |
| 27 | Serial, Parallel, G1, ZGC, Shenandoah no generacional y Shenandoah explícitamente generacional, incluida la finalización y los registros |

Las **12 configuraciones de ejecución** produjeron la misma suma de comprobación y registros de GC. No controlan las diferencias de implementación, optimización y seguridad entre JDK, por lo que el tiempo transcurrido o el número de recolecciones no clasifican los recolectores. Los hitos de 28 EA y 1.4.1–7, 9–20, 22–24 y 26 se comprobaron con las fuentes oficiales anteriores.

### Qué indica una línea de registro

Este es un evento real de G1 en JDK 27 al que solo se han quitado los adornos de marca de tiempo y etiquetas.

```text
GC(0) Pause Young (Normal) (G1 Evacuation Pause) 47M->10M(128M) 1.468ms
```

`47M->10M` es el uso del heap antes y después de este GC; `(128M)` es la capacidad del heap en ese momento. El valor entre paréntesis no es siempre el heap máximo. Este laboratorio establece valores iguales para `-Xms` y `-Xmx`. `1.468ms` es la pausa de este evento, no el p99 del servicio ni el coste total de CPU del GC. La línea por sí sola no descarta una fuga de memoria ni establece una garantía de duración de las pausas.

### JDK 8 también necesita otras opciones de registro

No aplique el registro unificado de JDK 9 a 8 sin cambios. Recompile el mismo código fuente con el compilador de ese JDK para evitar incompatibilidades de versión de los archivos de clase.

```sh
GC_JDK="/path/to/jdk-8"
mkdir -p out8 logs
"$GC_JDK/bin/javac" -d out8 GcProbe.java
"$GC_JDK/bin/java" -Xms128m -Xmx128m -XX:+UseConcMarkSweepGC \
  -XX:+PrintGCDetails -XX:+PrintGCDateStamps -Xloggc:logs/jdk8-cms.log \
  -cp out8 GcProbe
```

JDK 27 también rechazó `-XX:+UseConcMarkSweepGC`. Las etapas de soporte, obsolescencia y eliminación varían según la versión; inspeccione los mensajes reales de inicio y el estado de salida durante las actualizaciones.

Compruebe la selección predeterminada del recolector de la siguiente forma. Esto comunica una CPU a una **nueva JVM**; no cambia la asignación de CPU de un servicio en ejecución.

```sh
GC_JDK="/path/to/jdk-27"
"$GC_JDK/bin/java" -XX:ActiveProcessorCount=1 -Xms128m -Xmx128m \
  -XX:+PrintCommandLineFlags -version
```

En las mismas condiciones, Temurin 21 imprimió `UseSerialGC` y Temurin 27 imprimió `UseG1GC`. Una selección explícita del recolector prevalece sobre la predeterminada. Importan la CPU y la memoria visibles para la JVM; las especificaciones del host por sí solas no determinan la selección de un contenedor.

## ¿Qué debe medir una comparación en producción?

Para un servicio existente, registre primero el JDK actual, la distribución, las opciones y la carga de trabajo. Con el mismo patrón de solicitudes y presupuesto de CPU/memoria, observe conjuntamente **el rendimiento de la aplicación, p95/p99, errores, RSS, uso del heap, tasa de asignación, pausas de GC y CPU del GC concurrente**. Unas pausas más cortas pueden aun así ir acompañadas de una peor latencia de la aplicación si los hilos de GC y de la aplicación compiten más por la CPU.

Para G1, establezca una referencia con los valores predeterminados en vez de fijar un tamaño de generación joven heredado de otro recolector; después ajuste el heap global y los objetivos de pausa si es necesario. ZGC necesita margen para el conjunto de objetos vivos y las nuevas asignaciones durante la recolección concurrente. `-Xmx` no es el RSS del proceso ni el límite de memoria de todo el contenedor; reserve también memoria para metaspace, las pilas de los hilos y los búferes directos.

Si los objetos alcanzables siguen creciendo, inspeccione primero las referencias retenidas, los límites de la caché y la vida de las solicitudes. Cambiar de recolector no elimina automáticamente los objetos alcanzables. Combine las pruebas del servicio con el [flujo de trabajo de registros y trazas LGTM](/en/posts/2026-11-02-grafana-lgtm-log-trace/), evitando suponer que la coincidencia entre latencia de solicitudes y eventos de GC demuestra causalidad.
