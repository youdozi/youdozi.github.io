---
state: "draft"
language: "de"
translationKey: "2026-11-12-t3-code-workflow"
title: "T3 Code: von einer kleinen Codeänderung zur Diff- und Testprüfung"
description: "Eine KI-Codeaufgabe mit T3 Code v0.1.9, begrenzten Berechtigungen, Diff und Tests durchführen und Referenzlösung von KI-Ausgabe unterscheiden."
sourcePath: "src/content/posts/en/2026-11-12-t3-code-workflow.md"
sourceSha256: "da83ebd4864d4a4b015af522789e363b4a8695b6424368db9bfd1652f7761089"
---

**T3 Code verbindet auf dem Computer installierte Coding-Agenten mit Projekt, Dialog, Berechtigungen und Änderungsansicht.** Für die Übergabe von Codearbeit sind ein enger Arbeitsbereich und überprüfbare Abschlussbedingungen wichtiger als eine lange Anfrage. Das Beispiel repariert einen numerischen `Retry-After`-Parser und führt von der Änderungsanfrage bis zur Prüfung von Diff und Tests.

Gegenstand ist das [offizielle T3-Code-Projekt](https://github.com/pingdotgg/t3code/tree/v0.1.9), getrennt vom T3 Stack zur Erstellung von Web-Apps mit `create-t3-app`. Das offizielle README beschreibt die Anbindung vorhandener Anbieter wie Codex, Claude Code und Cursor. Installation von T3 Code und Anmeldung sowie Abonnement-/API-Bedingungen des Anbieters sind getrennte Schritte.

Grundlage ist das [Release v0.1.9](https://github.com/pingdotgg/t3code/releases/tag/v0.1.9), das am 12. November 2026 geprüft wurde. Das Beispiel wurde unter macOS mit Node.js 24.13.0 und Git geprüft; CLI-Hilfe und lokaler Serverstart von T3 Code ebenfalls. **An einen Anbieter wurde keine KI-Aufgabe gesendet.** Die Referenzlösung unten ist eine direkt getestete Implementierung, keine tatsächliche Ausgabe von T3 Code oder eine Messung der Modellleistung.

## Wie teilen T3 Code und der Anbieter ihre Aufgaben?

T3 Code zeigt das Projekt und den Thread, die Anbieterauswahl, Berechtigungsanfragen und Änderungen. Der verbundene Agent liest und ändert Dateien oder führt Befehle aus. Ein sichtbarer Werkzeugaufruf bedeutet nicht, dass Tests automatisch gelaufen und bestanden sind; prüfen Sie Befehl und Ergebnis.

Installieren Sie nach der [Installationsanleitung](https://github.com/pingdotgg/t3code/blob/v0.1.9/docs/user/install.md) den gewünschten Anbieter und authentifizieren Sie sich auf **dem Computer, auf dem der T3-Code-Server läuft**. Die Übung beginnt bei der Auswahl eines bereits vorbereiteten Anbieters. Anmeldedaten oder API-Schlüssel müssen nicht in den Prompt eingefügt werden.

## Kleines Git-Projekt und fehlschlagende Tests vorbereiten

![Startcode und feste Tests in Git speichern und Fehlschläge prüfen. In T3 Code Projekt, Anbieter und Supervised wählen und eine begrenzte Änderungsanfrage senden. Dateiänderungen und Befehle genehmigen und Diff, ursprüngliche Tests und Ergebnisse vergleichen. Bei erfülltem Vertrag selbst committen, sonst eine Korrektur verlangen.](2026-11-12-t3-code-workflow.svg)

Speichern Sie diese drei Dateien in einem neuen Ordner `t3-code-example`. Die Node-Tests brauchen keine externen Pakete oder API-Aufrufe. Von den zwei `Retry-After`-Formen unterstützt die Übung **nur `delay-seconds`, also ganzzahlige Sekunden**. HTTP-date liegt außerhalb des Umfangs und muss `null` liefern. Die vollständige Header-Grammatik steht in der [Retry-After-Definition von RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html#name-retry-after).

### `package.json`

```json
{
  "name": "t3-code-retry-after-example",
  "private": true,
  "type": "module",
  "engines": { "node": ">=24" },
  "scripts": { "test": "node --test retry-after.test.mjs" }
}
```

### `retry-after.mjs`

```javascript
export function retryAfterMs(header) {
  const seconds = Number.parseInt(header, 10);
  return Number.isFinite(seconds) ? seconds * 1000 : null;
}
```

### `retry-after.test.mjs`

```javascript
import test from 'node:test';
import assert from 'node:assert/strict';
import { retryAfterMs } from './retry-after.mjs';

const cases = [
  ['2', 2000],
  ['0', 0],
  [' 2 ', 2000],
  ['0002', 2000],
  ['', null],
  ['   ', null],
  [undefined, null],
  [null, null],
  [2, null],
  ['0x10', null],
  ['2x', null],
  ['-1', null],
  ['1.5', null],
  ['1e3', null],
  ['Infinity', null],
  ['Wed, 21 Oct 2015 07:28:00 GMT', null],
  ['9007199254740', 9007199254740000],
  ['9007199254741', null],
  ['9007199254740991', null],
];
for (const [input, expected] of cases) {
  test(`retryAfterMs(${JSON.stringify(input)})`, () => {
    assert.equal(retryAfterMs(input), expected);
  });
}
```

Führen Sie die Befehle im Projektordner mit bereits konfiguriertem Git-Autor aus.

```sh
git init -b main
git add package.json retry-after.mjs retry-after.test.mjs
git commit -m "Add Retry-After exercise"
npm test
```

Beim Startcode wurden **11 bestandene und 8 fehlgeschlagene Tests** von 19 bestätigt. Er akzeptiert manche mit Ziffern beginnenden Zeichenketten wie `parseInt('2x', 10)` und behandelt negative Werte, Dezimalzahlen und Werte außerhalb des sicheren Bereichs nicht korrekt. Dieser rote Testlauf ist der Ausgangspunkt.

## Projekt öffnen und Änderungsumfang festlegen

Führen Sie dies im Projektordner aus, um die Version zu fixieren. `--host` beschränkt den Zugriff auf lokale Verbindungen; `--auto-bootstrap-project-from-cwd` fügt den aktuellen Ordner als Projekt hinzu. Beim ersten Einsatz können npm-Paket und ausführbare Datei heruntergeladen werden.

```sh
npm exec --yes --package=t3@0.1.9 -- t3 \
  --host 127.0.0.1 --auto-bootstrap-project-from-cwd .
```

Die CLI startet einen lokalen Server und eine Web-App. Wenn bereits ein T3-Code-Server vorhanden ist, öffnen Sie das Projekt dort. Desktop-Installation und Fernzugriff folgen separaten Wegen in der [Installationsanleitung dieser Version](https://github.com/pingdotgg/t3code/blob/v0.1.9/docs/user/install.md). Diese Anleitung richtet weder einen Hintergrunddienst noch externen Netzwerkzugriff ein.

Wählen Sie Projektordner und Thread sowie einen installierten und authentifizierten Anbieter. Laut [Thread-Anleitung](https://github.com/pingdotgg/t3code/blob/v0.1.9/docs/user/thread-sidebar.md) erstellt **New worktree** einen eigenen Branch und Arbeitsordner. Die Grundübung verwendet das vorhandene Arbeitsverzeichnis des vorbereiteten Ordners. Bei einem neuen Worktree müssen spätere Git- und npm-Befehle ebenfalls dort ausgeführt werden. Prüfen Sie zuerst Arbeitspfad und Branch des Threads. Kontrollieren Sie im Eingabebereich den Berechtigungsmodus **Supervised**. Die [Berechtigungsanleitung für v0.1.9](https://github.com/pingdotgg/t3code/blob/v0.1.9/docs/user/permission-modes.md) nennt Full access als anfänglichen Standard; Supervised fordert Genehmigungen für Befehle und Dateiänderungen an. Einzelheiten wie erlaubte Lesezugriffe hängen vom Anbieter ab.

Senden Sie diesen Prompt:

```text
Lesen Sie zuerst retry-after.mjs und retry-after.test.mjs.
Ändern Sie retryAfterMs(header) gemäß diesem Vertrag:

- Entfernen Sie umgebenden Leerraum und akzeptieren Sie nur nichtnegative ganzzahlige Sekunden aus ASCII-Ziffern.
- Geben Sie Millisekunden zurück; Sekunden und Millisekunden müssen Number.isSafeInteger erfüllen.
- Leere oder nicht aus Strings bestehende Werte, negative Werte, Dezimalzahlen, Exponentialschreibweise, nachfolgende Zeichen und Werte außerhalb des sicheren Bereichs ergeben null.
- HTTP-date liegt außerhalb dieses Umfangs und muss null liefern.
- Ändern Sie nur retry-after.mjs. Ändern Sie weder Tests noch package.json.
- Installieren Sie keine Abhängigkeiten, senden Sie keine Netzwerkanfragen und erstellen Sie keinen Git-Commit, Push oder PR.

Prüfen Sie mit npm test und berichten Sie Änderungsgrund sowie tatsächlich ausgeführte Befehle und Ergebnisse.
Nennen Sie ausdrücklich, falls ein Befehl nicht ausgeführt werden konnte.
```

Prüfen Sie bei einer Genehmigungsanfrage, ob Dateiänderung oder Befehl wie `npm test` für diese Übung nötig ist. Eine Umfangsanweisung im Prompt ersetzt keine Werkzeugberechtigungen. Der Agent soll hier nicht committen; nach Änderungen und Prüfergebnissen entscheiden Sie selbst.

## Wie wird „Korrektur abgeschlossen“ geprüft?

Die [T3-Code-Anleitung zur Änderungsprüfung](https://github.com/pingdotgg/t3code/blob/v0.1.9/docs/user/source-control.md) unterscheidet geänderte Dateien und Diffs je Turn von Branch-Vergleichen. Ein Turn-Diff zeigt die Arbeit dieses Turns; vergleichen Sie vor dem Zusammenführen auch mit dem Basis-Branch. Öffnen Sie Test-Werkzeugaufrufe im Dialog, um tatsächlichen Befehl, Ausgabe und Status zu sehen; alternativ können Sie sie im Terminal erneut ausführen.

```sh
git rev-parse --show-toplevel
git diff --name-only
git diff -- retry-after.mjs
git diff --exit-code -- retry-after.test.mjs package.json
npm test
```

Nur `retry-after.mjs` sollte geändert sein. Wenn der dritte Befehl Änderungen ausgibt oder fehlschlägt, prüfen Sie zuerst, warum Tests oder Konfiguration geändert wurden. Ein durch abgeschwächte Testerwartungen erreichter Erfolg erfüllt diesen Vertrag nicht. Prüfen Sie auch `git status --short` auf neue Dateien.

Meldet der Agent, dass er Tests nicht ausführen konnte, behandeln Sie das nicht als Erfolg; führen Sie `npm test` selbst aus. Bleiben Fehler, benennen Sie Eingabe, Erwartung und tatsächliches Ergebnis in einer weiteren Anfrage. Beispiel: „`0` muss 0ms sein und `'2x'` muss null sein. Tests beibehalten und diese beiden Fälle erneut prüfen.“

Es folgt die **direkt verifizierte Referenzimplementierung**. Vergleichen Sie sie nach der Übung mit der vorgeschlagenen Agentenänderung. Zur Ausführung gehört der Code in `retry-after.mjs` im Projektstamm.

### `reference/retry-after.mjs`

```javascript
export function retryAfterMs(header) {
  if (typeof header !== 'string') return null;
  const value = header.trim();
  if (!/^[0-9]+$/.test(value)) return null;
  const seconds = Number(value);
  const milliseconds = seconds * 1000;
  return Number.isSafeInteger(seconds) && Number.isSafeInteger(milliseconds)
    ? milliseconds
    : null;
}
```

Nach Ersatz des Startcodes durch die Referenzimplementierung bestanden dieselben 19 Tests und die ursprüngliche Testdatei blieb unverändert. Die Prüfung des sicheren Ganzzahlbereichs ist von einer tatsächlichen Obergrenze für Wartezeiten getrennt. Diese Funktion führt weder das Warten aus noch ist sie ein vollständiger HTTP-date-Parser; Anzahl und gesamtes Zeitbudget echter Client-Retrys sind separat festzulegen.

Um die Arbeit nach Prüfung von Diff und Tests selbst aufzuzeichnen, committen Sie nur die geänderte Datei:

```sh
git add retry-after.mjs
git commit -m "Validate numeric Retry-After values"
```

Stoppen Sie danach den Vordergrundserver mit `Ctrl+C` im Terminal, in dem T3 Code läuft.

## Was prüfen, wenn der Start scheitert?

| Symptom | Erste Prüfung |
| --- | --- |
| Anbieter fehlt oder startet nicht | Installation und PATH auf dem Serverrechner sowie Anbieter in Settings prüfen |
| Authentifizierungsfehler | Gewähltes Anbieterkonto und Anmeldung auf dem Serverrechner prüfen |
| Änderungen im ursprünglichen Ordner nicht sichtbar | Prüfen, ob der Thread einen separaten Worktree nutzt und derselbe Pfad betrachtet wird |
| Diff oder Branch-Funktionen fehlen | Prüfen, ob der geöffnete Ordner ein Git-Repository ist und der Projektpfad stimmt |
| Tests bestehen, Änderungen gehen über den Umfang hinaus | Diff und Git-Status einschließlich Tests, Konfiguration und neuer Dateien prüfen |

Das offizielle README beschreibt ein frühes Projekt, das Fehler enthalten kann. Nach Updates der App oder Anbieter-CLI erleichtern ein kleiner Vertrag und ein Prüfverfahren wie dieses den Vergleich, statt beim gleichen Prompt eine feste Antwort zu erwarten.
