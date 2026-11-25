---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2026-11-26-ai-powerpoint-guide",
  "routeSlug": "2026-11-26-ai-powerpoint-guide",
  "kind": "post",
  "title": "Mit KI eine PowerPoint-Präsentation erstellen – von der Gliederung zu bearbeitbaren Folien",
  "description": "Drei Prompts für Gliederung, Erstellung und Prüfung einer bearbeitbaren PowerPoint-Datei, am Beispiel eines Pilotversuchs für automatisierte Prüfungen vor dem Deployment.",
  "categories": [
    "ai"
  ],
  "tags": [
    "powerpoint",
    "pptx",
    "pptxgenjs",
    "ai-agent",
    "presentation"
  ],
  "sourcePath": "src/content/posts/en/2026-11-26-ai-powerpoint-guide.md",
  "sourceSha256": "859efd0ceeccfc1b46a9a9b1f8bbfb0235b50e0f4eee44c55f224a6a936c87cd",
  "draftSha256": "c12791a58e28e33b54b90a54bb1e1987fc6c8534901995a863ba40a968874881",
  "manifestPath": ".pipeline/technical-translations/batch-193/manifest.json",
  "manifestSha256": "a54ee41212e4537256255e8c5a3c92386aff1f0228b7c74e991073c7b90d9b49",
  "publishedAt": "2026-11-25T22:36:09.895Z",
  "updatedAt": "2026-11-25T22:36:09.895Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 197,
    "approvedAt": "2026-11-25T22:36:09.895Z",
    "basis": "The site owner explicitly requested publication of item 74 in Korean, English, Simplified Chinese, Japanese, German, French, Russian and Spanish."
  }
}
---

Wenn Sie eine KI mit einer Präsentation beauftragen, erklären Sie zuerst, **wer zuhört und welche Entscheidung am Ende ansteht**. Auf „Erstelle mir eine ansprechende Präsentation“ bekommen Sie schnell eine Titelfolie und eine Agenda. Worum es in der Besprechung gehen soll, erfahren die Zuhörenden womöglich erst auf der letzten Folie. Legen Sie für jede Folie Titel und Beleg fest, lassen Sie aus der Gliederung eine .pptx erstellen und öffnen Sie sie in der Anwendung, mit der Sie vortragen. So sehen Sie, wo Sie nacharbeiten müssen.

![Zielgruppe und Entscheidung festlegen, Gliederung prüfen, bearbeitbare Folien erstellen und sie mit den Quellen sowie im Präsentationsmodus kontrollieren.](/assets/diagrams/technical/de-2026-11-26-ai-powerpoint-guide.svg)

## Skills und Werkzeuge für die Erstellung

| Skill oder Werkzeug | Wann es sich anbietet | Aufgabe |
|---|---|---|
| **ai-guide-writing** | Eine Anleitung oder Schulungsunterlagen in einen Vortrag übertragen | Übungsschritte, Beispieleingaben, erwartete Ergebnisse und Kontrollen ordnen. |
| **tech-blog-writing** | Technische Dokumentation oder Betriebsprotokolle präsentieren | Kernaussagen und Belege auswählen und die Erläuterungen auf Folien und Vortragsnotizen verteilen. |
| **pptx-Skill von Anthropic** | In Claude Code eine PowerPoint-Datei erstellen oder eine Vorlage anpassen | .pptx erstellen und bearbeiten, Folieninhalte extrahieren, Vorschaubilder und Dateistruktur überprüfen. [Offizieller Skill](https://raw.githubusercontent.com/anthropics/skills/main/skills/pptx/SKILL.md) |
| **PptxGenJS** | Mit einem Coding-Agenten wie Codex jede Woche ähnliche Berichte erstellen | Aus JavaScript und Eingabedaten erneut eine bearbeitbare .pptx erzeugen. [Offizielle Kurzanleitung](https://github.com/gitbrent/PptxGenJS#-quick-start-guide) |

ai-guide-writing und tech-blog-writing sind Schreib-Skills, die in der hier verwendeten Umgebung verfügbar waren. Für die PowerPoint-Datei selbst können Sie den pptx-Skill in Claude Code oder PptxGenJS nutzen. Führen Sie die folgenden beiden Zeilen nacheinander aus, um die offiziellen Anthropic-Skills in Claude Code zu installieren. Anschließend können Sie im Prompt ausdrücklich den pptx-Skill anfordern. [Installationsanleitung von Anthropic](https://github.com/anthropics/skills#claude-code)

```text
/plugin marketplace add anthropics/skills
/plugin install document-skills@anthropic-agent-skills
```

Wenn Sie bereits in PowerPoint arbeiten, kann **Copilot** anhand eines Prompts oder von Referenzdateien einen Entwurf erstellen. Öffnen Sie zuerst die Firmenvorlage, falls vorhanden. Die verfügbaren Funktionen hängen vom Abonnement und den Einstellungen Ihrer Organisation ab. Mit **Gemini in Google Präsentationen** können Sie Folien generieren und als .pptx herunterladen. Für die Erstellung einer ganzen Präsentation benötigen Sie laut Google einen geeigneten Tarif. Die Funktion ist auf dem Desktop in englischer Sprache verfügbar. [Präsentation mit Copilot erstellen](https://support.microsoft.com/en-gb/powerpoint/copilot/create-a-new-presentation-with-copilot-in-powerpoint) · [Präsentationen mit Gemini generieren](https://support.google.com/docs/answer/17111393) · [Als PPTX herunterladen](https://support.google.com/a/users/answer/9310270)

## 1. Die anstehende Entscheidung in den Gliederungsprompt aufnehmen

In diesem fiktiven Beispiel schlagen Sie einem Entwicklungsteam **einen Pilotversuch für automatisierte Prüfungen vor dem Deployment** vor. Sie haben 7 Minuten Zeit und möchten die Zustimmung zu einem 2-wöchigen Test mit einem Team erhalten. Mit diesen Vorgaben kann die KI die konkrete Entscheidung vor die allgemeinen Vorteile der Automatisierung stellen.

```text
Entwirf einen 7-minütigen Vortrag für die Entwicklungsleitung und den Betrieb über
automatisierte Prüfungen vor dem Deployment. Plane 6 Folien. In der Besprechung soll
über einen 2-wöchigen Pilotversuch mit einem Team entschieden werden.

<Unterlagen>
- Vor dem Deployment prüfen Mitarbeitende die Umgebungsvariablen und den Stand der Datenbankmigrationen.
- Die erste automatisierte Prüfung kontrolliert nur, ob die benötigten Umgebungsvariablen
  vorhanden sind und ob Migrationsdateien fehlen.
- Sie protokolliert nur Diagnoseergebnisse und ändert weder Einstellungen noch die Datenbank.
- Im Pilotversuch werden Prüfdauer, Anzahl entdeckter Auslassungen und Anzahl der Fehlalarme erfasst.
- Zeitersparnis und Rückgang der Fehlerquote wurden noch nicht gemessen.
</Unterlagen>

Gib für jede Folie einen Titel mit der Kernaussage, höchstens 3 sichtbare Textpunkte,
Vortragsnotizen und die zugehörige Stelle in den Unterlagen an.
Nenne auf der ersten Folie die gewünschte Entscheidung und auf der letzten die Kriterien
für die Auswertung. Erfinde keine Zahlen oder bereits benannten Verantwortlichen.
```

**Lesen Sie anschließend nur die Titel, der Reihe nach.** Der erste sollte die anstehende Entscheidung nennen, die mittleren das aktuelle Problem und den Prüfumfang erläutern und der letzte die Auswertung des Pilotversuchs beschreiben. „Im Pilotversuch erfassen wir Prüfdauer und Fehlalarme“ vermittelt die Aussage genauer als „Erwartete Vorteile der Automatisierung“.

## 2. Eine bearbeitbare .pptx anfordern

Wenn Sie Texte oder Diagramme später ändern möchten, nennen Sie im Prompt **die Elemente, die einzeln bearbeitbar sein müssen**. Ist die ganze Folie ein einziges Bild, müssen Sie sie unter Umständen neu erstellen, nur um einen Satz in PowerPoint zu ändern.

```text
Erstelle aus der unten eingefügten freigegebenen Gliederung eine PowerPoint-Datei
im Format 16:9 mit dem Namen deployment-check-pilot.pptx.

- Titel, Fließtext, Tabellen und Ablaufdiagramme sollen in PowerPoint einzeln bearbeitbar sein.
- Verwende pro Folie eine Kernaussage und verschiebe längere Erklärungen in die Vortragsnotizen.
- Stelle die automatisierte Prüfung mit drei Formen dar:
  „Deployment anfordern → Beide Punkte prüfen → Ergebnis protokollieren“.
- Nutze bei Themen ohne Zahlen Tabellen oder Ablaufdiagramme statt statistischer Diagramme.
- Übernimm bei einer beigefügten Firmenvorlage die Titelpositionen, Schriftarten und Farben.
- Stelle Effekte oder Einführungstermine, die in den Unterlagen fehlen, nicht als gesichert dar.

<Freigegebene Gliederung>
Hier die in Schritt 1 geprüfte Gliederung einfügen.
</Freigegebene Gliederung>
```

Für einen wöchentlich wiederkehrenden Bericht können Sie den Coding-Agenten zusätzlich bitten: **„Verwende PptxGenJS und liefere build-deck.js und slides.json mit, damit ich die Erstellung wiederholen kann.“** In der nächsten Woche tauschen Sie nur die Eingabedaten aus und erzeugen das gleiche Layout erneut. Lassen Sie Datentabellen und Diagramme möglichst als PowerPoint-Objekte stehen. Separate Bilder eignen sich für Illustrationen. Das erleichtert spätere Änderungen. [Textobjekte in PptxGenJS](https://gitbrent.github.io/PptxGenJS/docs/api-text.html)

## 3. Bei der Prüfung Foliennummer und Begründung verlangen

Geben Sie neben der fertigen Datei auch **die freigegebene Gliederung und die ursprünglichen Unterlagen** mit. Steht auf einer Folie „Die Fehlerquote bei Deployments ist gesunken“, lässt sich erst anhand der Quelle beurteilen, ob das ein Messergebnis ist oder noch gemessen werden soll.

```text
Vergleiche die fertige PPTX mit der freigegebenen Gliederung und den ursprünglichen Unterlagen.
Nenne für jede betroffene Folie Nummer, Problem, Beleg und Ersatzformulierung.

1. Suche nach unbelegten Zahlen, unbestätigten Terminen und übertriebenen Wirkungsversprechen.
2. Wenn du die Folien rendern kannst, prüfe, ob koreanische Schriftarten ersetzt werden,
   Zeilen ungünstig umbrechen, Text abgeschnitten wird oder sich Formen überlagern.
3. Markiere Vortragsnotizen, die nur den sichtbaren Text wiederholen.
4. Sage allein anhand der letzten Folie, welche Entscheidung das Publikum treffen soll.

Kennzeichne alles, was du nicht selbst prüfen konntest, als „ungeprüft“.
```

Öffnen Sie die Datei in der PowerPoint-Version, mit der Sie vortragen, und prüfen Sie **Bearbeitungsansicht und Bildschirmpräsentation**. Ändern Sie in der Bearbeitungsansicht eine Zahl in einer Tabelle und Text in einer Form. Kontrollieren Sie im Präsentationsmodus, ob Titel und Kernaussagen auch aus der letzten Reihe lesbar sind. Prüfen Sie nach einem Export aus Google Präsentationen die koreanischen Schriftarten und Zeilenumbrüche erneut. Die Prompts beziehen sich auf ein fiktives Beispiel. Die Angaben zur Dateierstellung mit den einzelnen Produkten beruhen auf deren offizieller Dokumentation.

Zum Weiterlesen · [10 Skills für Claude Code und Codex und ihr Einsatz im Alltag](../2026-11-18-claude-code-codex-skills-top-10/)
