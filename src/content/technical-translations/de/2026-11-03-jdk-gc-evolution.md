---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2026-11-03-jdk-gc-evolution",
  "routeSlug": "2026-11-03-jdk-gc-evolution",
  "kind": "post",
  "title": "Garbage Collection im JDK: von JDK 27 zurück zu 1.4, mit G1, ZGC, Shenandoah und CMS",
  "description": "Einführung, Standardauswahl und Entfernung von HotSpot-GCs von JDK 27 und 28 EA bis zu älteren Versionen nachvollziehen, Collectors vergleichen und ein reproduzierbares Beispiel mit GC-Protokollen ausführen.",
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
  "draftSha256": "7b2b805f87507ba8793ced0fb4059e7fcccb92e86cc184ddc0f35b8002d2af8e",
  "manifestPath": ".pipeline/technical-translations/batch-137/manifest.json",
  "manifestSha256": "f244063fe26ffa61c98e9820e607a03a676e98093676337edb7a008b2bca8ff5",
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

**Für modernes HotSpot empfiehlt sich eine gemessene G1-Basis: Bei strengen Latenzanforderungen ZGC oder Shenandoah vergleichen und bei vorrangigem Durchsatz Parallel GC erwägen.** Vor dem Übernehmen alter JVM-Flags prüfen, welcher Collector standardmäßig gewählt wird und welche Implementierungen die tatsächlich eingesetzte JDK-Distribution enthält.

Stichtag ist der **2026-11-03**. [JDK 27](https://jdk.java.net/27/) ist die jüngste allgemein verfügbare Feature-Version; [JDK 28 befindet sich im Early Access](https://jdk.java.net/28/). Dieser Artikel behandelt **OpenJDK HotSpot**, nicht sämtliche JVM-Implementierungen. Die LTS-Linien von Oracle — 8, 11, 17, 21 und 25 — werden häufig für den Betrieb gewählt, doch Supportzeiträume und Updatebedingungen hängen vom Distributor ab. [Oracle-Support-Roadmap](https://www.oracle.com/java/technologies/java-se-support-roadmap.html)

## Vom neuesten JDK zurück zu früheren Versionen

| JDK | Wichtigste GC-Änderung | Was in bestehenden Installationen zu prüfen ist |
| --- | --- | --- |
| **28 EA** | [JEP 535](https://openjdk.org/jeps/535), das den generationellen Modus von Shenandoah zum Standard macht, hat den Status Targeted | Dies noch nicht als in einer GA-Version ausgeliefert betrachten. Dadurch wird Shenandoah nicht zum JVM-weiten Standard-Collector |
| **27** | [JEP 523](https://openjdk.org/jeps/523) wählt G1 unabhängig von CPU-Anzahl und Speichergröße standardmäßig aus | Die Standardauswahl für Dienste erneut prüfen, die in kleinen Umgebungen zuvor Serial verwendeten |
| **26** | [JEP 522](https://openjdk.org/jeps/522) senkt den Synchronisierungsaufwand in G1, um den Durchsatz zu verbessern | Eine Verbesserung im Upstream belegt nicht denselben prozentualen Gewinn für den eigenen Dienst |
| **25** | [JEP 521](https://openjdk.org/jeps/521) hebt Generational Shenandoah vom experimentellen Status zum Produktfeature an | Verfügbarkeit eines Modus und dessen standardmäßige Auswahl sind unterschiedliche Änderungen |
| **24 / 23** | 24 entfernt nicht generationelles ZGC ([JEP 490](https://openjdk.org/jeps/490)); 23 macht den generationellen Modus bei Auswahl von ZGC zum Standard ([JEP 474](https://openjdk.org/jeps/474)). 24 führt außerdem experimentelles Generational Shenandoah ein ([JEP 404](https://openjdk.org/jeps/404)) | Ein Standard innerhalb von ZGC ändert nicht den Standard-Collector der JVM |
| **21 / 17 / 15** | 21 führt Generational ZGC ein ([JEP 439](https://openjdk.org/jeps/439)). ZGC und Shenandoah werden in 15 zu Produktfeatures ([JEP 377](https://openjdk.org/jeps/377), [379](https://openjdk.org/jeps/379)) und sind daher auch in 17 Produktfeatures | Generationelles ZGC in 21 explizit auswählen. Plattform- und Distributionsverfügbarkeit separat prüfen |
| **14 / 12 / 11** | 14 entfernt CMS ([JEP 363](https://openjdk.org/jeps/363)). 12 ergänzt experimentelles Shenandoah ([JEP 189](https://openjdk.org/jeps/189)); 11 führt experimentelles ZGC und Epsilon ein ([JEP 333](https://openjdk.org/jeps/333), [318](https://openjdk.org/jeps/318)) | Historischen experimentellen Status vom heutigen Produktstatus unterscheiden; anfangs wurden nicht alle Plattformen unterstützt |
| **9** | G1 wird zum Standard für Serverkonfigurationen ([JEP 248](https://openjdk.org/jeps/248)); CMS wird abgekündigt ([JEP 291](https://openjdk.org/jeps/291)); einheitliches GC-Logging wird eingeführt ([JEP 271](https://openjdk.org/jeps/271)) | Parser und Optionen für JDK-8-Protokolle nicht unverändert übernehmen |
| **8** | Parallel ist der auf Durchsatz ausgelegte Standard für Server-Class-Systeme; G1 und CMS sind Alternativen. PermGen wird entfernt ([JEP 122](https://openjdk.org/jeps/122)) | Parallel war nicht in jeder Umgebung der Standard. PermGen-Flags nicht in neue Installationen übernehmen |
| **7u4 / 6 / 5 / 1.4.1** | Oracle JDK unterstützt G1 ab 7u4. Parallele vollständige Bereinigung kommt in 5u6 hinzu und wird in 6 verbessert. Die Dokumentation zu 1.4.1 stellt parallele Bereinigung der jungen und nebenläufige Bereinigung der alten Generation vor | Frühe parallele Bereinigung der jungen Generation von späterer paralleler Bereinigung der alten Generation unterscheiden |

Die Standardauswahl von JDK 8 ist im Kontext seines [Ergonomie-Leitfadens](https://docs.oracle.com/javase/8/docs/technotes/guides/vm/gctuning/ergonomics.html) zu lesen. Frühere Meilensteine sind in der [G1-Supporthistorie](https://docs.oracle.com/javase/8/docs/technotes/guides/vm/G1.html), der [Beschreibung von Parallel Compaction](https://docs.oracle.com/javase/8/docs/technotes/guides/vm/par-compaction-6.html) und im [GC-Artikel zu JDK 1.4.1](https://www.oracle.com/technical-resources/articles/java/garbagecollection-in-java-applications-using-jdk141.html) dokumentiert. Historische Empfehlungen zur Heap-Größe und zu Pausenzielen beschreiben ihre Zeit; sie sind keine heutigen Standardeinstellungen für den Betrieb.

Die Tabelle enthält ausgewählte wichtige Meilensteine. Sie listet weder sämtliche Korrekturen in Updates auf, noch behauptet sie, dass jede historische Version für diesen Artikel ausgeführt wurde.

## Drei Unterscheidungen vor der Wahl eines Collectors

GC gibt den Speicher von Objekten frei, die **von GC-Roots aus nicht erreichbar** sind, etwa von Referenzen laufender Threads aus. Ein Cache oder eine globale Collection kann Objekte erreichbar halten, obwohl die Anwendung sie nicht mehr benötigt. Generationelle Bereinigung nutzt die Beobachtung, dass viele Objekte rasch sterben, einige aber überleben, und behandelt junge und alte Objekte unterschiedlich. [HotSpot-GC-Implementierung](https://docs.oracle.com/en/java/javase/27/gctuning/garbage-collector-implementation.html)

**Parallel** bedeutet, dass mehrere GC-Threads zusammenarbeiten; **nebenläufig** bedeutet, dass sich ein Teil der GC-Arbeit mit der Anwendungsausführung überschneidet. Das sind unterschiedliche Dimensionen. Eine **Stop-the-world-Phase (STW)** hält die Anwendungsausführung an. Auch nebenläufige Collectors können kurze Pausen oder Wartezeiten bei Allokationen verursachen; Nebenläufigkeit beseitigt die Anfragelatenz nicht.

Markierung identifiziert lebende Objekte; Sweeping stellt freigebbaren Speicher zur Wiederverwendung bereit. Kompaktierung verschiebt lebende Objekte, um freien Speicher zusammenzuführen, während Evakuierung Überlebende aus ausgewählten Regionen an andere Stellen kopiert. Collectors kombinieren diese Aufgaben unterschiedlich über Generationen, Regionen sowie parallele und nebenläufige Arbeit hinweg.

| Collector | Grundprinzip | Zu vergleichende Bedingungen |
| --- | --- | --- |
| Serial | Ein GC-Thread; geringer Koordinationsaufwand kann zu kleinen Aufgaben passen | Durchsatz und Pausen auch bei kleinem Heap oder begrenzter CPU messen |
| Parallel | Mehrere Bereinigungsthreads mit Vorrang für Durchsatz | Batch-Laufzeit und tolerierbare Pausen vergleichen |
| G1 | Regionen, nebenläufige Markierung und Evakuierung während Pausen | Allgemeine Vergleichsbasis für Server; das Pausenziel ist keine Echtzeitgarantie |
| ZGC | Führt einen großen Teil der Verlagerungs- und Referenzarbeit nebenläufig aus, um kurze Pausen anzustreben | CPU- und Heap-Reserven, Allokationsrate und Anwendungslatenz gemeinsam beobachten |
| Shenandoah | Collector für kurze Pausen mit nebenläufiger Verlagerung; der Status des generationellen Modus variiert je nach Version | Zuerst Verfügbarkeit in der Distribution und ausgewählten Modus prüfen |
| CMS / Epsilon | CMS ist der historische nebenläufige Mark-Sweep-Collector; das experimentelle Epsilon gibt keinen Speicher frei | CMS ist im neuesten JDK nicht verfügbar. Epsilon ist kein allgemeiner Ersatz für den GC eines Dienstes |

Für Serial und Parallel ist der [aktuelle Leitfaden zur Collector-Auswahl](https://docs.oracle.com/en/java/javase/27/gctuning/available-collectors.html) ein guter Ausgangspunkt. Der [G1-Tuning-Leitfaden](https://docs.oracle.com/en/java/javase/27/gctuning/garbage-first-garbage-collector-tuning.html) erklärt das Verhalten und die Pausenziele von G1. Die [historische CMS-Dokumentation](https://docs.oracle.com/en/java/javase/13/gctuning/concurrent-mark-sweep-cms-collector.html) beschreibt nebenläufige Phasen und Einschränkungen durch Fragmentierung; [JEP 318](https://openjdk.org/jeps/318) legt fest, dass Epsilon keinen Speicher zurückgewinnt.

## Neben dem Collector auch den generationellen Modus prüfen

Bei ZGC in JDK 21 wählt `-XX:+UseZGC -XX:+ZGenerational` den generationellen Modus aus. In 23 verwendet `-XX:+UseZGC` standardmäßig den generationellen Modus; 24 entfernt die nicht generationelle Implementierung. Das Außerkraftsetzen und Entfernen eines Flags sind von der Entfernung einer Implementierung getrennte Schritte. JDK 27 wies in diesem Versuch `-XX:+ZGenerational` zurück; dieses Flag daher nicht an die aktuelle Konfiguration anhängen. [Aktueller ZGC-Leitfaden](https://docs.oracle.com/en/java/javase/27/gctuning/z-garbage-collector.html)

Shenandoah separat prüfen. Der in 25 eingeführte generationelle Produktmodus wird mit `-XX:+UseShenandoahGC -XX:ShenandoahGCMode=generational` ausgewählt. **Allein die Auswahl von Shenandoah in 27 belegt nicht, dass der generationelle Modus ausgewählt ist.** JEP 535 zielt auf 28 und hat am Stichtag weiterhin den Status Targeted. Build-Optionen und Backports können beeinflussen, welche Collectors eine Distribution bereitstellt; die tatsächlich verwendete Programmdatei prüfen.

## Protokolle desselben Allokationsprogramms lesen

Dieser **Versuch mit einem einzelnen Thread** veranschaulicht Objektlebensdauern und GC-Protokolle. Er allokiert 8192 Arrays mit je 128 KiB, insgesamt 1 GiB an Array-Nutzdaten, und ersetzt dabei Referenzen in 64 zyklisch verwendeten Slots. Die zuletzt gehaltenen Nutzdaten umfassen 8 MiB; Array-Header, Referenzen und JVM-Speicher kommen hinzu. Das Programm bildet weder Produktionslast ab noch implementiert es einen GC-Benchmark.

![64 Referenzslots anlegen, wiederholt ein Array mit 128 KiB allokieren, eine Slotreferenz ersetzen und über 8192 Iterationen eine Prüfsumme aufsummieren, dann das Ergebnis ausgeben](/assets/diagrams/technical/de-2026-11-03-jdk-gc-evolution.svg)

Das Diagramm folgt der Allokation und dem Austausch von Referenzen im Code. Die JVM entscheidet, wann nicht mehr erreichbare Objekte freigegeben werden; der Code ruft `System.gc()` nicht auf. Nicht davon ausgehen, dass jedes ersetzte Objekt sofort freigegeben wird.

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

Die Arrays bleiben über `retained` von außen erreichbar. Dieses kleine Programm belegt dennoch weder die Verteilung der Objektlebensdauern noch den Engpass eines Produktionsdienstes.

### Vier Collectors auswählen und Protokolle in JDK 27 untersuchen

Diese Befehle verwenden eine Unix-artige Shell. `GC_JDK` durch das eigene **JDK-Stammverzeichnis** ersetzen, die Java-Datei in einem neuen Arbeitsverzeichnis speichern und die Befehle dort ausführen. Externe Bibliotheken oder Netzwerkanfragen sind nicht erforderlich. Jeder Lauf verwendet einen maximalen Heap von 128 MiB und begrenzte rotierende Protokolldateien.

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

`%p` wird zur JVM-PID erweitert und unterscheidet so Protokolle verschiedener Läufe. Prüfen, dass alle vier Läufe mit der folgenden Zeile enden. Die davor ausgegebenen Laufzeit- und Collector-Zeilen hängen von JDK und Collector ab.

```text
iterations=8192 retainedSlots=64 checksum=1044480
```

Die ausgeführte Umgebung war **macOS arm64, Zulu 8u392-b08 sowie Temurin 21.0.13+9, 25.0.5+8 und 27.0.1.0.2+1**. Archivierte Versionen veranschaulichen historisches Verhalten; dies ist keine Empfehlung für aktuelle Kombinationen von Sicherheitsupdates. Folgende Ausführungen wurden geprüft:

| JDK | Geprüfte Ausführungen |
| --- | --- |
| 8 | Standardmäßiges Parallel, explizites G1 und CMS, einschließlich Abschluss und älterer GC-Protokolle |
| 21 | Nicht generationelles und explizit generationelles ZGC, einschließlich Abschluss und Protokolle |
| 25 | Mit dem ZGC-Flag ausgewähltes generationelles ZGC, einschließlich Abschluss und Protokolle |
| 27 | Serial, Parallel, G1, ZGC, nicht generationelles Shenandoah und explizit generationelles Shenandoah, einschließlich Abschluss und Protokolle |

Alle **12 Ausführungskonfigurationen** erzeugten dieselbe Prüfsumme und GC-Protokolle. Sie kontrollieren Unterschiede in Implementierung, Optimierung und Sicherheit zwischen JDKs nicht; Laufzeit oder GC-Anzahl ergeben daher keine Rangfolge der Collectors. Die Meilensteine für 28 EA sowie 1.4.1–7, 9–20, 22–24 und 26 wurden anhand der oben genannten offiziellen Quellen geprüft.

### Was eine einzelne Protokollzeile aussagt

Dies ist ein tatsächliches G1-Ereignis aus JDK 27, bei dem lediglich Zeitstempel und Tag-Dekorationen entfernt wurden.

```text
GC(0) Pause Young (Normal) (G1 Evacuation Pause) 47M->10M(128M) 1.468ms
```

`47M->10M` ist die Heap-Belegung vor und nach diesem GC; `(128M)` ist die Heap-Kapazität zu diesem Zeitpunkt. Der Wert in Klammern ist nicht grundsätzlich der maximale Heap. In diesem Versuch sind `-Xms` und `-Xmx` gleich eingestellt. `1.468ms` ist die Pause dieses Ereignisses, weder die p99 des Dienstes noch der gesamte CPU-Aufwand des GC. Die Zeile allein schließt weder ein Speicherleck aus noch belegt sie eine Garantie für die Pausendauer.

### JDK 8 benötigt auch andere Logging-Optionen

Das einheitliche Logging von JDK 9 nicht unverändert auf 8 anwenden. Denselben Quellcode mit dem Compiler dieses JDK neu kompilieren, um inkompatible Klassendateiversionen zu vermeiden.

```sh
GC_JDK="/path/to/jdk-8"
mkdir -p out8 logs
"$GC_JDK/bin/javac" -d out8 GcProbe.java
"$GC_JDK/bin/java" -Xms128m -Xmx128m -XX:+UseConcMarkSweepGC \
  -XX:+PrintGCDetails -XX:+PrintGCDateStamps -Xloggc:logs/jdk8-cms.log \
  -cp out8 GcProbe
```

JDK 27 wies auch `-XX:+UseConcMarkSweepGC` zurück. Die Phasen von Unterstützung, Außerkraftsetzung und Entfernung unterscheiden sich je nach Version; bei Upgrades tatsächliche Startmeldungen und Exitstatus untersuchen.

Die standardmäßige Collector-Auswahl wie folgt prüfen. Damit wird einer **neuen JVM** eine CPU gemeldet; die CPU-Zuteilung eines laufenden Dienstes wird dadurch nicht geändert.

```sh
GC_JDK="/path/to/jdk-27"
"$GC_JDK/bin/java" -XX:ActiveProcessorCount=1 -Xms128m -Xmx128m \
  -XX:+PrintCommandLineFlags -version
```

Unter denselben Bedingungen gab Temurin 21 `UseSerialGC` und Temurin 27 `UseG1GC` aus. Eine explizite Collector-Auswahl hat Vorrang vor dem Standard. Entscheidend sind die für die JVM sichtbare CPU und der sichtbare Speicher; die Host-Spezifikationen allein bestimmen die Auswahl in einem Container nicht.

## Was sollte ein Vergleich im Produktivbetrieb messen?

Bei einem bestehenden Dienst zunächst aktuelles JDK, Distribution, Flags und Workload erfassen. Bei demselben Anfragemuster und CPU-/Speicherbudget **Anwendungsdurchsatz, p95/p99, Fehler, RSS, Heap-Belegung, Allokationsrate, GC-Pausen und CPU-Verbrauch des nebenläufigen GC** gemeinsam beobachten. Kürzere Pausen können dennoch mit schlechterer Anwendungslatenz einhergehen, wenn GC- und Anwendungsthreads stärker um CPU konkurrieren.

Für G1 mit den Standardeinstellungen eine Vergleichsbasis aufbauen, statt die von einem anderen Collector übernommene Größe der jungen Generation festzuschreiben; anschließend bei Bedarf Gesamt-Heap und Pausenziele anpassen. ZGC benötigt Reserven für die lebenden Objekte und neue Allokationen während der nebenläufigen Bereinigung. `-Xmx` ist weder der RSS des Prozesses noch das Speicherlimit des gesamten Containers; Metaspace, Thread-Stacks und direkte Puffer ebenfalls einplanen.

Wenn erreichbare Objekte stetig zunehmen, zuerst gehaltene Referenzen, Cache-Grenzen und Anfragelebensdauern untersuchen. Ein Collector-Wechsel entfernt erreichbare Objekte nicht automatisch. Dienstdaten mit dem [LGTM-Workflow für Logs und Traces](/en/posts/2026-11-02-grafana-lgtm-log-trace/) kombinieren und dabei nicht annehmen, dass zeitlich zusammenfallende Anfragelatenz und GC-Ereignisse einen ursächlichen Zusammenhang belegen.
