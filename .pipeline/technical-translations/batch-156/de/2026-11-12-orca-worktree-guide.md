---
state: "draft"
language: "de"
translationKey: "2026-11-12-orca-worktree-guide"
title: "Orca nutzen: Worktree-Ablauf für Agenten, Tests und Review"
description: "Mit Orca-Projekten und Worktrees eine Coding-Aufgabe trennen, Tests und Browserergebnis prüfen und vor dem Commit das Diff begutachten."
sourcePath: "src/content/posts/en/2026-11-12-orca-worktree-guide.md"
sourceSha256: "4214532491f859b28104e614442c9bc3c33ecc9a00a62567a96d927bc90cffb6"
---

**Orca ist eine Entwicklungsumgebung, die Git-Arbeitsbereiche, Coding-Agenten, Terminals, einen Browser und die Änderungsprüfung zusammenführt.** Eine Aufgabe je Worktree ermöglicht getrennte Branches und Ordner für unterschiedliche Änderungen. Prüfen Sie den Abschluss anhand von tatsächlichem Arbeitspfad, Testausgabe und Diff zum Basis-Branch statt allein anhand der Antwort des Agenten.

Gegenstand ist die [offizielle Orca-App](https://www.onorca.dev/) von Stably AI. Diese Anleitung basiert auf **Orca 1.4.256** unter macOS, dem mitgelieferten CLI-Leitfaden, Node.js 24.13.0, Python 3 und Git. Die Abfrage des aktuellen Arbeitsbereichs, Beispieltests im Orca-Terminal, Porterkennung und Darstellung im eingebetteten Browser wurden geprüft. Das Erstellen oder Zusammenführen eines Worktrees und eine neue KI-Agentenaufgabe wurden nicht ausgeführt; die folgenden Prompts und Erstellungsbefehle sind Übungen für Lesende.

## Worin unterscheiden sich Projekt und Worktree?

Öffnen Sie ein lokales Git-Repository mit **Add Repo** aus der [offiziellen Anleitung zur ersten Sitzung](https://www.onorca.dev/docs/first-session). Auch wenn Orca ein Projekt verwaltet, bleiben Quelldateien und Commits im Git-Repository. Nutzungsbedingungen und Authentifizierung für Modell und Anbieter sind separat vorzubereiten.

| Element | Rolle in dieser Übung |
| --- | --- |
| Projekt | Fasst Beispiel-Repository und Arbeitsbereiche zusammen |
| Worktree | Arbeitsordner mit ausgechecktem Branch und zugehörige Arbeitsansicht |
| Agent | Schlägt im angefragten Umfang Lesen und Ändern von Dateien sowie Befehle vor |
| Terminal | Führt Tests und Entwicklungsserver im Aufgabenordner aus |
| Eingebetteter Browser | Prüft die echte Entwicklungsserver-Seite und Grenzwerte |

Die [Orca-Worktree-Dokumentation](https://www.onorca.dev/docs/model/worktrees) und der [CLI-Leitfaden](https://www.onorca.dev/docs/cli/overview) erklären das Verhältnis von Dateien, Branches und Arbeitsansichten. Nehmen Sie nicht an, dass die Auswahl eines anderen Worktrees in der Oberfläche das aktuelle Verzeichnis einer bereits offenen Shell automatisch ändert. **Pfad und Branch im ausführenden Terminal prüfen** ist der erste Schritt.

## Kleines Beispiel erstellen und Ausgangszustand prüfen

![Beispielrepository öffnen, Worktree erstellen und Pfad und Branch prüfen. Einen Agenten um Änderung einer Datei bitten, dann Tests, Entwicklungsserver und Browser im selben Worktree prüfen. Diff und ursprüngliche Tests mit main vergleichen; bei erfüllten Bedingungen selbst committen, sonst Korrektur verlangen.](2026-11-12-orca-worktree-guide.svg)

Die illustrative Versandregel lautet: **Bestellungen ab 50.000 Won sind versandkostenfrei, darunter fallen 3.000 Won an**; akzeptiert werden nur nichtnegative sichere Ganzzahlen. Es ist keine tatsächliche Richtlinie eines Dienstes. Speichern Sie die vier Dateien in einem neuen Ordner `orca-shipping-example`. Externe npm-Pakete sind nicht nötig.

### `package.json`

```json
{
  "name": "orca-shipping-example",
  "private": true,
  "type": "module",
  "engines": { "node": ">=24" },
  "scripts": { "test": "node --test shipping.test.mjs" }
}
```

### `shipping.mjs`

```javascript
export function shippingFee(orderTotal) {
  return orderTotal > 50_000 ? 0 : 3000;
}
```

### `shipping.test.mjs`

```javascript
import test from 'node:test';
import assert from 'node:assert/strict';
import { shippingFee } from './shipping.mjs';

for (const [total, expected] of [[0, 3000], [49_999, 3000], [50_000, 0], [50_001, 0]]) {
  test(`shippingFee(${total}) = ${expected}`, () => {
    assert.equal(shippingFee(total), expected);
  });
}
for (const [label, total] of [
  ['negative', -1],
  ['fraction', 50_000.5],
  ['string', '50000'],
  ['NaN', Number.NaN],
  ['Infinity', Number.POSITIVE_INFINITY],
  ['unsafe integer', Number.MAX_SAFE_INTEGER + 1],
]) {
  test(`rejects ${label}`, () => {
    assert.throws(() => shippingFee(total), RangeError);
  });
}
```

### `index.html`

```html
<!doctype html>
<html lang="ko">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Orca 배송비 예제</title>
<h1>배송비 경계값 확인</h1>
<pre id="result"></pre>
<script type="module">
  import { shippingFee } from './shipping.mjs';
  const totals = [49_999, 50_000, 50_001];
  document.querySelector('#result').textContent = totals
    .map(total => `${total}원 → 배송비 ${shippingFee(total)}원`)
    .join('\n');
</script>
</html>
```

Führen Sie dies im Beispielordner mit bereits konfiguriertem Git-Autor aus.

```sh
git init -b main
git add package.json shipping.mjs shipping.test.mjs index.html
git commit -m "Add shipping exercise"
npm test
```

Der Startcode behandelt den Grenzwert `50,000` (fünfzigtausend Won) falsch und weist ungültige Eingaben nicht zurück. Ein echter Lauf bestätigte **3 bestandene und 7 fehlgeschlagene Tests von 10**. Durch einen Basis-Commit dieses Zustands lässt sich später vergleichen, ob auch Tests oder Konfiguration geändert wurden.

## Änderung von einem Agenten im Worktree anfordern

Öffnen Sie das Beispielrepository mit **Add Repo** in Orca und prüfen Sie die CLI in einem damit verbundenen Terminal. Fehlt die CLI, installieren Sie sie über Settings → General → Orca CLI gemäß dem [offiziellen CLI-Leitfaden](https://www.onorca.dev/docs/cli/overview). Diese Befehle setzen die ausführbare macOS-Datei `orca` voraus.

```sh
orca skills get orca-cli
orca worktree current --json
```

Um die Arbeit zu trennen, erstellen Sie einen neuen Worktree vom `main` des aktuellen Projekts.

```sh
orca worktree create --name shipping-fee-fix \
  --parent-worktree active --base-branch main \
  --setup skip --activate --json
```

`--parent-worktree active` hält die Orca-Arbeitsbeziehung fest; `--base-branch main` setzt den Git-Ausgangspunkt. Das sind unterschiedliche Einstellungen. Das Beispiel überspringt Setup, da keine externen Abhängigkeiten zu installieren sind. Befolgen Sie für ein echtes Projekt die passende Setup-Richtlinie. Da dieser Befehl kein `--agent` enthält, startet er keine Agentenaufgabe.

Öffnen Sie ein Terminal im neuen Arbeitsbereich und prüfen Sie ihn. Unterscheiden Sie die Shell des ursprünglichen Befehls von der Shell im neuen Worktree.

```sh
git rev-parse --show-toplevel
git branch --show-current
orca worktree current --json
```

Branch-Namen können sich je nach Orca-Präfix und Konfiguration unterscheiden. Prüfen Sie Worktree im JSON sowie Git-Pfad und Branch auf den beabsichtigten Arbeitsbereich, öffnen Sie einen vorbereiteten Agenten-Tab und senden Sie folgenden Prompt. Verfügbare Agenten und Chat-/CLI-Ausführung hängen von der Umgebungskonfiguration ab.

```text
Prüfen Sie zuerst das aktuelle Arbeitsverzeichnis und den Branch und lesen Sie shipping.mjs und shipping.test.mjs.
Ändern Sie die illustrative Versandregel gemäß diesem Vertrag:

- Bestellungen ab 50.000 Won haben 0 Versandkosten; darunter betragen sie 3.000 Won.
- Bestellbeträge dürfen nur nichtnegative sichere Ganzzahlen sein; alle anderen Eingaben ergeben RangeError.
- Ändern Sie nur shipping.mjs; Tests, package.json und index.html bleiben unverändert.
- Installieren Sie keine Abhängigkeiten, rufen Sie keine externen Netzwerke auf und erstellen Sie weder Commit, Push noch PR.

Berichten Sie das tatsächliche Ergebnis von npm test und den Änderungsgrund.
Nennen Sie ausdrücklich, falls Sie eine Prüfung nicht ausführen konnten.
```

Auch wenn Orca Arbeit gruppiert darstellt, hängen tatsächliche Werkzeugrechte vom Agenten und der Ausführungsumgebung ab. Prompt-Einschränkungen allein erzwingen die Zugriffsgrenze nicht. Diese Anleitung setzt weder bestimmte Namen von Berechtigungsschaltflächen noch identisches Verhalten aller Anbieter voraus.

## Tests und Browser im selben Arbeitsbereich prüfen

Führen Sie `npm test` im [eingebetteten Terminal](https://www.onorca.dev/docs/terminal) aus. Für Automatisierung können Sie im aktuellen Worktree ein Testterminal erstellen:

```sh
orca terminal create --title "tests" --command "npm test" --json
```

Verwenden Sie bei Automatisierung das zurückgegebene Terminal-Handle als Ziel späterer Befehle. `terminal read --screen` liest den aktuellen Bildschirm; einfaches `terminal read` liest die angesammelte Ausgabe. Die Annahme einer Eingabe und der tatsächliche Start eines Befehls oder einer Agentenaufgabe sind unterschiedliche Ereignisse. Diese Anleitung prüfte **alle 10 Tests erfolgreich** und nur `shipping.mjs` als Änderung in der Ausgabe eines eigens erstellten Testterminals. Die Referenzlösung wurde direkt eingefügt; dies ist kein Nachweis einer KI-Aufgabenausführung.

Starten Sie für die Browserprüfung den Server in einem Terminal desselben Worktrees. Voraussetzung ist, dass Port 4877 frei ist.

```sh
python3 -m http.server 4877 --bind 127.0.0.1
```

Prüfen Sie den Port in einem anderen Terminal.

```sh
orca ports --json
orca tab create --url http://127.0.0.1:4877/ --json
```

Nutzt der Server einen anderen Port, verwenden Sie den angezeigten Port und die zugehörige URL. Nicht alles, was `orca ports` anzeigt, ist eine HTTP-Webseite. Verbinden Sie sich gemäß der [Anleitung zum eingebetteten Browser](https://www.onorca.dev/docs/browser/overview) und prüfen Sie auf der Beispielseite folgende Werte:

```text
49999원 → 배송비 3000원
50000원 → 배송비 0원
50001원 → 배송비 0원
```

Die drei Zeilen oben wurden im tatsächlichen Orca-Browser mit der Referenzlösung geprüft. Stoppen Sie den Server anschließend mit `Ctrl+C` in seinem Terminal. Schließen Sie nicht alle fremden Terminals, nur weil die Aufgabe beendet ist; unterscheiden Sie die Prozesse und Tabs dieser Aufgabe.

## Diff prüfen und nur die geänderte Datei speichern

Prüfen Sie Basis-Ref und geänderte Dateien im [Orca-Diff-Viewer](https://www.onorca.dev/docs/review/diff-viewer). Mit [Kommentaren an geänderten Zeilen](https://www.onorca.dev/docs/review/annotate-ai-diff) lässt sich eine Stelle für den Agenten markieren. Beispiel: „50.000 Won müssen ebenfalls kostenlos sein. Testerwartungen beibehalten und den Vergleichsoperator prüfen.“

Vergleichen Sie auch im Terminal mit dem Basis-`main`.

```sh
git status --short
git diff main --name-only
git diff main -- shipping.mjs
git diff --exit-code main -- shipping.test.mjs package.json index.html
npm test
```

Nur `shipping.mjs` sollte in dieser Aufgabe geändert sein. Falls Tests, Konfiguration oder Seite geändert wurden, prüfen Sie zuerst warum. Neue Dateien können in einem gewöhnlichen Diff fehlen; prüfen Sie daher auch den Git-Status. Führen Sie vom Agenten nicht ausführbare Prüfungen selbst aus und behandeln Sie „fertig“ nicht als bestandenes Ergebnis.

Es folgt die direkt verifizierte Referenzlösung. Vergleichen Sie sie nach der Übung mit dem vorgeschlagenen Code des Agenten. Zur Ausführung gehört dieser Code in `shipping.mjs` im Projektstamm.

### `reference/shipping.mjs`

```javascript
export function shippingFee(orderTotal) {
  if (!Number.isSafeInteger(orderTotal) || orderTotal < 0) {
    throw new RangeError('orderTotal must be a nonnegative safe integer');
  }
  return orderTotal >= 50_000 ? 0 : 3000;
}
```

Mit der Referenzlösung bestanden alle 10 gleichen Tests und ursprüngliche Tests, Konfiguration und HTML blieben erhalten. Prüfen Sie die Bedingungen und committen Sie nur die nötigen Dateien im Aufgaben-Branch.

```sh
git add shipping.mjs
git commit -m "Fix free-shipping boundary and input validation"
```

Ein Commit und das Zusammenführen in den Basis-Branch sind getrennte Schritte. Hat eine andere Aufgabe `main` geändert, prüfen Sie Diff und Tests vor dem Zusammenführen erneut. Ein Worktree trennt Quell-Arbeitsbereiche, ist aber keine Sicherheits-Sandbox. Verschiedene Worktrees können Ausführungsressourcen wie Datenbanken, Ports, Konten und Geheimnisse weiterhin teilen.

Anfangs lassen sich Probleme leichter lokalisieren, wenn dieser Ablauf an einer Aufgabe geübt wird, bevor mehrere Agenten hinzukommen. Erweitern Sie parallele Arbeit, wenn Datei- oder Funktionsgrenzen und Abschlussbedingungen klar getrennt sind.
