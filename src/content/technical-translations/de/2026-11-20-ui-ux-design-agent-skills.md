---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2026-11-20-ui-ux-design-agent-skills",
  "routeSlug": "2026-11-20-ui-ux-design-agent-skills",
  "kind": "post",
  "title": "UI und UX mit Claude Code und Codex entwerfen — Nutzerführung, Figma und Barrierefreiheit",
  "description": "Entwerfen Sie mit Claude Code und Codex Nutzerabläufe, Figma-Designsysteme und Oberflächentexte. Prüfen Sie mit Playwright Tastatur und Fokus im Dialog zur Stornierung einer Buchung.",
  "categories": [
    "ai"
  ],
  "tags": [
    "claude-code",
    "codex",
    "agent-skills",
    "figma",
    "ui-ux",
    "accessibility",
    "playwright"
  ],
  "sourcePath": "src/content/posts/en/2026-11-20-ui-ux-design-agent-skills.md",
  "sourceSha256": "b548a40ceebcfb72b0b19df913a07279080b56efc21e2264764c3cddd259e65a",
  "draftSha256": "5dc93adfed0ad78aa9a355771dead91357d4ba3b3fa677e4cef5a2545cd9f82b",
  "manifestPath": ".pipeline/technical-translations/batch-172/manifest.json",
  "manifestSha256": "91fb61de3a3d1c432b5f074da43348e5ad1ab92b61742481f1cd4ac05bc2994e",
  "publishedAt": "2026-11-20T14:37:06.595Z",
  "updatedAt": "2026-11-20T14:37:06.595Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 172,
    "approvedAt": "2026-11-20T14:37:06.595Z",
    "basis": "User requested seven new language editions for each of four already published guides and approved parallel AI translation and verification. This records publication authorization."
  }
}
---

**Klären Sie vor dem Entwurf, was Nutzer abschließen müssen und bis zu welchem Punkt sie ihre Entscheidung rückgängig machen können.** Beim Stornieren einer Buchung sollen sie die Folgen im Voraus kennen und die Buchung behalten oder stornieren können. Legen Sie den Text des Dialogs, den Anfangsfokus und das Ziel nach dem Schließen fest. Das gibt Umsetzung und Prüfung dieselben Kriterien.

Der [vorherige Beitrag](/ko/posts/2026-11-19-website-building-agent-skills/) behandelt die gesamte Website-Erstellung. Hier geht es im Detail um UI und UX. Auf Grundlage der am 20. November 2026 geprüften öffentlichen Skills für Claude Code und Codex sowie der Unterlagen von Figma, Vercel und W3C verfolgen wir die Stornierung einer Buchung vom Entwurf bis zur Prüfung im Browser.

## Skills passend zum Ergebnis auswählen

| Benötigtes Ergebnis | Skill oder Vorgehen | Prüfkriterien |
| --- | --- | --- |
| Nutzerablauf und Ansichtsstatus | Projektinterne Anleitung `frontend-architecture-design` | Einstieg, Bestätigung, Verlassen, laufende Verarbeitung, Erfolg und Fehler festlegen. Bei vorhandener Nutzerforschung Beobachtungen von Hypothesen trennen. |
| Prototyp zur Prüfung | [Plugin Product Design](https://github.com/openai/plugins/tree/main/plugins/product-design) für Codex | Einen Entwurf erstellen, an dem sich Zustandsübergänge prüfen lassen. Kontrollieren, ob man die Buchung sowohl behalten als auch verbindlich stornieren kann. |
| Visuelle Ausrichtung und UI-Code | [`frontend-design`](https://github.com/anthropics/skills/tree/main/skills/frontend-design) für Claude Code | Die visuelle Reihenfolge von Überschrift, Beschreibung und Aktionsschaltfläche festlegen. Prüfen, ob Bedeutung und Reihenfolge auch bei langem Titel und schmalem Bildschirm erhalten bleiben. |
| Ansichten in Figma erstellen | [`figma-generate-design`](https://github.com/openai/plugins/tree/main/plugins/figma/skills/figma-generate-design) aus dem Figma-Plugin | Schaltflächen und Dialoginstanzen aus der vorhandenen Bibliothek wiederverwenden und pro Zustand einen Frame erstellen. Verknüpfungen von Komponenten und Variablen prüfen. |
| Designsystem-Bibliothek | [`figma-generate-library`](https://github.com/openai/plugins/tree/main/plugins/figma/skills/figma-generate-library) aus dem Figma-Plugin | Figma-Variablen und Bibliotheken anhand der Design-Tokens und Komponenten im Code anlegen oder aktualisieren. Varianten und Variablenverknüpfungen mit den Namen im Code abgleichen. |
| Freigegebene Figma-Ansicht umsetzen | [`figma-design-to-code`](https://github.com/openai/plugins/tree/main/plugins/figma/skills/figma-design-to-code) aus dem Figma-Plugin | Den Ziel-Frame lesen und mit vorhandenem UI-Code umsetzen. Nach dem visuellen Vergleich die Tastaturbedienung und den Fehlerzustand gesondert prüfen. |
| Oberflächentexte | Projektinterne UX-Textvorgaben wie `cms-ux-writing` | Das Ergebnis eines Klicks mit einem Verb ausdrücken. „Buchung behalten“ und „Stornierung bestätigen“ benennen jeweils die Folge der Aktion. |
| Prüfung der Oberfläche | Vercels [`web-design-guidelines`](https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines) und Browserprüfung | Im Code nach möglichen Problemen bei Barrierefreiheit und Oberfläche suchen. Im Browser Tab-Reihenfolge, Fokuswechsel und Layout bei unterschiedlichen Bildschirmgrößen prüfen. |

Die beiden projektinternen Vorgaben zeigen, wie ein Team seine Regeln für Oberflächen und Texte als wiederverwendbare Skills festhält. Gibt es jemanden, der den Buchungsablauf prüft, zeigen Sie zuerst den Prototyp. Arbeiten Sie die Rückmeldungen in die Zustandstabelle ein und übergeben Sie sie dann zur Umsetzung. Sind Figma-Frame und Code-Komponenten bereits abgestimmt, können Sie mit Umsetzung und Barrierefreiheitsprüfung beginnen.

In Claude Code gehört Anthropics `frontend-design` zum Paket `example-skills` im offiziellen Marketplace. Für Figma-Skills in Codex benötigen Sie die mit dem Plugin verbundenen Figma-Werkzeuge und Zugriff auf die Datei. Wenn Sie Ansichten oder Komponenten in Figma erstellen, kombinieren Sie den zuständigen Skill mit der Anleitung `figma-use` des Plugins. Geben Sie zum Lesen eines Entwurfs den Link zum Ziel-Frame an. Für neue Frames stellen Sie eine bearbeitbare Datei und die Bibliotheken zur Wiederverwendung bereit. [Anthropics Installationsanleitung](https://github.com/anthropics/skills#claude-code) · [Figma-Plugin für Codex](https://github.com/openai/plugins/tree/main/plugins/figma)

Wenn es einen Markenleitfaden gibt, geben Sie das tatsächliche Logo, Farben, Schriften und Beispiele unzulässiger Verwendung mit. Wer Anthropics `brand-guidelines` allein nach dem Namen für die eigene Marke einsetzt, kann versehentlich Anthropics Farben und Typografie übernehmen. Die mitgelieferten Materialien gehören zur Marke Anthropic. [Quelltext von `brand-guidelines`](https://github.com/anthropics/skills/tree/main/skills/brand-guidelines)

## Den Stornierungsablauf an Design und Umsetzung übergeben

Halten Sie Nutzeraktionen und deren Ergebnisse vor dem Entwurf in einer Tabelle fest. Die folgende Tabelle ist ein Entwurfsbeispiel. Prüfen Sie die tatsächlichen Regeln des Dienstes, bevor Sie Texte zu Erstattungen oder Stornogebühren schreiben.

| Aktion oder Serverzustand | Ergebnis auf dem Bildschirm |
| --- | --- |
| „Stornooptionen öffnen“ in den Buchungsdetails wählen | Der Bestätigungsdialog öffnet sich, der Fokus liegt auf „Buchung behalten“. |
| „Buchung behalten“ oder Escape | Der Dialog schließt sich und die Buchung bleibt bestehen. Der Fokus kehrt zur Schaltfläche zurück, die den Dialog geöffnet hat. |
| „Stornierung bestätigen“ wählen | Der Produktivdienst sendet die Anfrage und zeigt die laufende Verarbeitung an. Wiederholte Anfragen lösen keine doppelte Verarbeitung aus. |
| Server meldet Erfolg | Der Buchungsstatus wechselt zu „Buchung storniert“, und das Ergebnis wird mitgeteilt. |
| Server meldet einen Fehler | Der Buchungsstatus bleibt bestehen. Die Oberfläche nennt den Fehlergrund und mögliche nächste Schritte. |

Bei einem Dialog für schwer rückgängig zu machende Aktionen kann die Option mit den geringsten Folgen als Anfangsfokus sinnvoll sein. Beim Schließen kehrt der Fokus üblicherweise zu dem Element zurück, das den Dialog geöffnet hat. Wenn es nicht mehr vorhanden ist, wählen Sie ein anderes Element, das die Aufgabe sinnvoll fortsetzt. [W3C-Muster für modale Dialoge](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/)

Geben Sie dem Agenten für die Umsetzung das gewünschte Verhalten und die Prüfkriterien mit.

> Entwirf einen Bestätigungsdialog für die Stornierung in den Buchungsdetails und verwende die vorhandenen Dialoge und Schaltflächen wieder.\
> Setze den Anfangsfokus auf „Buchung behalten“. Beim Schließen mit Escape soll die Buchung bestehen bleiben und der Fokus zu „Stornooptionen öffnen“ zurückkehren.\
> Zeige nach dem Absenden der Stornierungsanfrage die Zustände Verarbeitung, Erfolg und Fehler getrennt an.\
> Biete im Fehlerzustand eine Wiederholung oder einen Weg zur Hilfe an.\
> Ordne Frames und Zustände einander zu, damit wir Entwurf und Zustandstabelle vor der Umsetzung prüfen können.

## Übung — Dialogfokus und beide Ergebnisse prüfen

Die Prüfung im Browser deckt die ersten beiden Tabellenzeilen sowie die sichtbare Änderung nach Bestätigung der Stornierung ab. In der Übung ändert die Bestätigung nur den Zustand der Seite. Serveranfragen, Fehlerbehandlung und Schutz vor mehrfacher Übermittlung werden im Produktivprojekt separat geprüft.

![Dialog bei aktiver Buchung öffnen und Anfangsfokus prüfen. Nach Escape oder „Buchung behalten“ Status und Fokus prüfen. Nach Bestätigung der Stornierung die neue Statusanzeige prüfen.](/assets/diagrams/technical/de-2026-11-20-ui-ux-design-agent-skills.svg)

Installieren Sie Node.js 22 und Chrome. Führen Sie in einem neuen Arbeitsordner `npm init -y` und `npm install --save-dev playwright-core@1.64.1` aus. Speichern Sie den folgenden Code als `dialog-check.mjs` und starten Sie ihn mit `node dialog-check.mjs`. Wenn Chrome an einem anderen Ort installiert ist, setzen Sie `CHROME_PATH`. [Playwright-Optionen zum Browserstart](https://playwright.dev/docs/api/class-browsertype#browser-type-launch)

```js
import assert from 'node:assert/strict';
import { chromium } from 'playwright-core';

const browser = await chromium.launch({
  executablePath: process.env.CHROME_PATH
    ?? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
});

try {
  const page = await browser.newPage({ viewport: { width: 360, height: 700 } });
  page.setDefaultTimeout(2000);
  await page.setContent(`
    <button id="open">취소 옵션 열기</button>
    <p role="status">예약 유지 중</p>
    <dialog aria-labelledby="title" aria-describedby="description">
      <h2 id="title">예약을 취소할까요?</h2>
      <p id="description">확정하면 예약 상태가 취소됨으로 바뀝니다.</p>
      <form method="dialog">
        <button value="keep" autofocus>예약 유지</button>
        <button value="cancel">예약 취소 확정</button>
      </form>
    </dialog>
    <script>
      const trigger = document.querySelector('#open');
      const dialog = document.querySelector('dialog');
      const status = document.querySelector('[role="status"]');

      trigger.addEventListener('click', () => {
        dialog.returnValue = '';
        dialog.showModal();
      });
      dialog.addEventListener('close', () => {
        if (dialog.returnValue === 'cancel') {
          status.textContent = '예약 취소됨';
        }
      });
    </script>
  `);

  const trigger = page.getByRole('button', { name: '취소 옵션 열기' });
  const dialog = page.getByRole('dialog', { name: '예약을 취소할까요?' });
  const status = page.getByRole('status');
  const focused = () => page.evaluate(
    () => document.activeElement?.textContent?.trim(),
  );

  for (const close of ['Escape', '예약 유지']) {
    await trigger.focus();
    await page.keyboard.press('Enter');
    await dialog.waitFor({ state: 'visible' });
    assert.equal(await focused(), '예약 유지', '초기 포커스');
    await page.keyboard.press(close === 'Escape' ? 'Escape' : 'Enter');
    await dialog.waitFor({ state: 'hidden' });
    assert.equal(await status.textContent(), '예약 유지 중');
    assert.equal(await focused(), '취소 옵션 열기', '닫은 뒤 포커스');
    console.log(`PASS ${close}: 예약 유지 및 포커스 복귀`);
  }

  await page.keyboard.press('Enter');
  await dialog.waitFor({ state: 'visible' });
  assert.equal(await focused(), '예약 유지', '초기 포커스');
  await page.keyboard.press('Tab');
  assert.equal(await focused(), '예약 취소 확정', '확정 버튼 포커스');
  await page.keyboard.press('Enter');
  await page.waitForFunction(
    () => document.querySelector('[role="status"]').textContent === '예약 취소됨',
  );
  await dialog.waitFor({ state: 'hidden' });
  assert.equal(await focused(), '취소 옵션 열기', '확정 뒤 포커스');
  console.log('PASS 예약 취소 확정: 상태 변경 및 포커스 복귀');
} finally {
  await browser.close();
}
```

Die folgende Ausgabe stammt aus Chrome unter macOS. Sie gibt die koreanischen Beschriftungen des Beispiels wieder.

```text
PASS Escape: 예약 유지 및 포커스 복귀
PASS 예약 유지: 예약 유지 및 포커스 복귀
PASS 예약 취소 확정: 상태 변경 및 포커스 복귀
```

Im Gegenversuch wurde `autofocus` auf „Stornierung bestätigen“ verschoben. Daraufhin schlug die Prüfung des Anfangsfokus fehl. Die Übung prüfte den zugänglichen Namen des Dialogs, die Tastaturbedienung, den Anfangsfokus sowie Fokus und Statusanzeige nach dem Schließen. Prüfen Sie auf der tatsächlichen Oberfläche auch, ob der Fokus bei Tastaturbedienung sichtbar bleibt, ob Schaltflächen und Erläuterungen bei großer Schrift lesbar sind und ob assistive Technik Statusmeldungen ausgibt. [WCAG 2.2](https://www.w3.org/TR/WCAG22/)
