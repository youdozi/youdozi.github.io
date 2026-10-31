---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2026-10-30-node2shell-brotli-runtime-patching",
  "routeSlug": "2026-10-30-node2shell-brotli-runtime-patching",
  "kind": "post",
  "title": "Node2Shell-Abhilfe: Brotli-Dekompression verfolgen und Node.js-Rollout prüfen",
  "description": "Prüfen Sie Korrekturen für CVE-2026-111497, Brotli-Eingabepfade und irreführende Versionsangaben. Sammeln Sie Laufzeitbelege und unterscheiden Sie Installation von der Übernahme durch jeden Worker und jedes Replikat.",
  "categories": [
    "security"
  ],
  "tags": [
    "node2shell",
    "nodejs",
    "brotli",
    "security"
  ],
  "sourcePath": "src/content/posts/en/2026-10-30-node2shell-brotli-runtime-patching.md",
  "sourceSha256": "9f8abe774ed0a87c0a07284163ad858f1f4ff629708131dff5f1b6088b23b959",
  "draftSha256": "6cc2661a0b326f8ab6438e367166bd7bff1fbee6fd89a494baf68872a4d50be6",
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
Die Behebung von Node2Shell bedeutet, Node.js durch eine korrigierte Laufzeit zu ersetzen und die Übernahme durch jeden Worker zu prüfen, der nicht vertrauenswürdige Brotli-Daten dekomprimiert. Der [Node.js-Sicherheitshinweis](https://nodejs.org/en/blog/vulnerability/october-2026-security-releases) beschreibt **CVE-2026-111497** als Schreibzugriff außerhalb der Speichergrenzen im mitgelieferten Brotli-Decoder. npm-Pakete zu aktualisieren und die Laufzeit zu ersetzen sind separate Vorgänge.

## Ist jede Brotli-Nutzung gleich exponiert?

Der relevante Pfad **dekomprimiert** komprimierte Eingaben. Fehlerhafte, von Angreifern gelieferte Brotli-Daten, die `node:zlib` verarbeitet, können den Prozessspeicher beschädigen und zu Abstürzen, Speicheroffenlegung oder entfernter Codeausführung führen. Ausgehende Antworten mit Brotli zu komprimieren oder allein HTTP/2 zu aktivieren, belegt diesen Pfad nicht. Das Node.js-Projekt stuft das Problem als High ein.

Verfolgen Sie neben Anfrage-Bodies auch die automatische Dekompression externer HTTP-Antworten, Uploads, Dateien und Warteschlangenaufträge. Beispielsweise beschreibt die [body-parser-Dokumentation](https://expressjs.com/en/resources/middleware/body-parser/) automatische Brotli-Dekompression. Prüfen Sie die installierte Middleware-Version und Optionen; kein `brotliDecompress` im Anwendungscode zu finden, belegt keine fehlende Exposition. Ein Hintergrundauftrag kann externe Daten ohne öffentlich erreichbaren lauschenden Port dekomprimieren.

## Welche Node.js-Versionen enthalten die Korrektur?

Die am 30. Oktober 2026 geprüfte Tabelle nennt offizielle Sicherheitsversionen mit der Korrektur für diese CVE. Sie schreibt die zuletzt empfohlene Version nicht dauerhaft fest. Prüfen Sie bei der Bereitstellung die unterstützte Version desselben Anbieters und spätere Hinweise.

| Node.js-Zweig | Offizielle korrigierte Version |
| --- | --- |
| 22.x | [22.23.4](https://nodejs.org/en/blog/release/v22.23.4) |
| 24.x | [24.22.1](https://nodejs.org/en/blog/release/v24.22.1) |
| 26.x | [26.12.1](https://nodejs.org/en/blog/release/v26.12.1) |

Verwenden Sie bei Distributions-, eingebetteten Produkt- oder eigenen Builds die vollständige Paketrevision und Korrekturbelege des Anbieters. Übertragen Sie diese numerischen Schwellen nicht auf einen anderen Hauptversionszweig. Der Node.js-Hinweis behandelt auch Zweige nach ihrem Supportende als betroffen; das Fehlen in der Tabelle belegt keine Sicherheit.

Insbesondere reicht `process.versions.brotli` allein nicht aus. Die [Brotli-Versionsquelle im gepatchten Node.js 24.22.1](https://github.com/nodejs/node/blob/v24.22.1/deps/brotli/c/common/version.h) deklariert weiterhin `1.2.0`. Der [Versionsnachweis](https://nodejs.org/en/blog/release/v24.22.1) führt die übernommene Einzelkorrektur ausdrücklich auf. Ermitteln Sie die Herkunft des korrigierten Laufzeitartefakts, statt sich auf die Bibliotheksangabe zu verlassen.

## Belege aus dem Prozess selbst erfassen

![PID, Programmdatei, Node-Version und Brotli-Angabe des Beispielprozesses lesen und JSON ausgeben](/assets/diagrams/technical/de-2026-10-30-node2shell-brotli-runtime-patching.svg)

Das Diagramm folgt dem Start der folgenden Beispielanwendung. Sie liest Informationen innerhalb desselben Prozesses und gibt JSON aus, ohne Versionen zu vergleichen, Dienste zu erkennen oder den Patchstatus zu bewerten. Die Ausgabe eines neuen CLI-Aufrufs ersetzt keine Belege aus einem bestehenden Dienst.

Speichern Sie diese beiden Dateien mit Node.js 22 oder neuer in einem neuen Verzeichnis. Sie lesen in der [process-Referenz](https://nodejs.org/docs/latest-v24.x/api/process.html) dokumentierte Eigenschaften ohne Netzwerkanfragen, Dekompression oder Ausgabe von Umgebungsvariablen.

### `runtime-evidence.mjs`

```javascript
export function runtimeEvidence() {
  return {
    scope: 'this-process-only',
    pid: process.pid,
    executable: process.execPath,
    node: process.version,
    brotliLabel: process.versions.brotli ?? null,
    platform: process.platform,
    arch: process.arch,
  };
}
```

### `app.mjs`

```javascript
import {runtimeEvidence} from './runtime-evidence.mjs';

console.log(JSON.stringify(runtimeEvidence(), null, 2));
```

```sh
node app.mjs
```

Die lokale Prüfung verwendete einen offiziellen Node.js-24.22.1-Container und lieferte JSON mit `node` gleich `v24.22.1` und `brotliLabel` gleich `1.2.0`. PID, Pfad, Betriebssystem und Architektur variieren je nach Umgebung. Dies zeigt, dass ein korrigierter Build die alte Brotli-Angabe behalten kann; es testet weder eine Ausnutzung noch eine Produktivbereitstellung.

Führen Sie bei einem echten Dienst eine gleichwertige Startprotokollierung über seinen Bereitstellungsprozess ein und beschränken Sie den Zugriff auf diese Betriebslogs. Verknüpfen Sie den Datensatz mit Dienstmanager, Prozess und Image-Digest. Pfade und PIDs gehören nicht in öffentliche HTTP-Antworten. Ein separater Diagnoseprozess prüft nicht den Austausch vorhandener Worker.

## Was bleibt nach der Paketinstallation zu tun?

1. Erfassen Sie für jeden Dienst die Node.js-Programmdatei, den Anbieter, die vollständige Paketversion oder den Image-Digest sowie Prozesse, Worker und Replikate. `node -v` auf dem Host oder ein Dockerfile-Tag allein belegt nicht die Laufzeit in einem laufenden Container.
2. Verfolgen Sie die Bibliotheken, die Eingaben mit dem Brotli-Decoder verbinden. Halten Sie den Korrekturstatus der Laufzeit getrennt von der Eingabeexposition. Innerhalb des Untersuchungsumfangs keinen Dekompressionspfad zu finden, patcht keine unkorrigierte Laufzeit.
3. Beschaffen Sie eine kompatible korrigierte Laufzeit über einen vertrauenswürdigen Kanal. Bauen Sie Container-Images neu und rollen Sie sie aus; ersetzen Sie auch die tatsächliche Programmdatei von Prozessmanagern und verwalteten Plattformen. Gehen Sie nicht davon aus, dass die Aktualisierung einer System-Brotli-Bibliothek eine mitgelieferte Kopie ersetzt.
4. Prüfen Sie neue Laufzeitbelege für jeden Worker und jedes Replikat und anschließend normale API-Aufrufe, die Verarbeitung externer Antworten, Hintergrundaufträge und Fehlerraten. Installationsdateien zu ersetzen oder alte Replikate weiterlaufen zu lassen, ist keine geprüfte Übernahme.

Wenn sich das Patchen verzögert, erwägen Sie, die Dekompression nicht vertrauenswürdiger Brotli-Daten am tatsächlichen Datenpfad abzuweisen oder zu umgehen. Nur `br` aus `Accept-Encoding` zu entfernen blockiert nicht jeden Eingabepfad. Auch ein erfolgreicher Kompressions-/Dekompressionsdurchlauf mit gültigen Daten oder ein unauffälliges `npm audit` belegt nicht, dass diese CVE behoben ist.

## Ist dies dasselbe Problem wie PHP2Shell?

Es sind unterschiedliche Schwachstellen. Die beiden CVEs von PHP2Shell betreffen den Anfragezustand der PHP-Engine; Node2Shell betrifft den Brotli-Decoder. Dieselbe Brotli-CVE kann dennoch in anderen Produkten auftreten; folgen Sie deshalb den jeweiligen Produkthinweisen. Der [PHP2Shell-Leitfaden](/en/posts/2026-10-30-php2shell-runtime-patching/) erläutert den Unterschied zwischen dem PHP-Windows-Brotli-Neubuild und den Korrekturen der PHP-Engine.

Ein Absturz allein belegt keine Kompromittierung, und fehlende Spuren schließen sie nicht aus. Bewahren Sie bei Verdacht Belege an einem zugriffsbeschränkten Ort und untersuchen Sie den Vorfall oder bauen Sie aus einer vertrauenswürdigen Quelle neu, getrennt vom Patchen.
