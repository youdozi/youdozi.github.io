---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2026-11-18-claude-code-codex-skills-top-10",
  "routeSlug": "2026-11-18-claude-code-codex-skills-top-10",
  "kind": "post",
  "title": "Zehn Skills für Claude Code und Codex und ihr Einsatz im Alltag",
  "description": "Vergleichen Sie zehn Skills für Claude Code und Codex CLI, erfahren Sie mehr über Installation und Aufruf und probieren Sie denselben Release-Notes-Skill in beiden Tools aus.",
  "categories": [
    "ai"
  ],
  "tags": [
    "claude-code",
    "codex",
    "agent-skills",
    "ai-agent",
    "developer-tools"
  ],
  "sourcePath": "src/content/posts/en/2026-11-18-claude-code-codex-skills-top-10.md",
  "sourceSha256": "6e3aca2da19c8f558c9fdaaa5afcc7403a9fedfb528d5e3a58eb0ee33c0fd993",
  "draftSha256": "2d533060742e684f4474bde2e5b1c343214be01bd594914169c865e039479115",
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

Wenn sich ein Auftrag wiederholt, machen Sie daraus einen Skill. Hinterlegen Sie Eingabeumfang und Ausgabeformat im Skill, statt Zusammenfassungsvorgaben und Prüfkriterien jedes Mal erneut zu schreiben. Pro Aufgabe ändern Sie dann nur die betreffenden Dateien. Entwicklungsteams können mit `skill-creator` und `webapp-testing` beginnen. Für Teams mit vielen Dokumenten ist der Skill für das tatsächlich verwendete Dateiformat ein guter Einstieg.

Mit Claude ist **Claude Code** im Terminal gemeint, mit Codex **Codex CLI**. Ich habe die Kandidaten anhand der offiziellen Quellen vom 18. November 2026 geprüft und nach **Häufigkeit der Wiederverwendung, einfacher Überprüfbarkeit sowie Aufwand für Installation und externe Verbindungen** geordnet. Diese Kriterien bilden die Grundlage der Empfehlung. Installationszahlen und Leistungswerte fließen nicht ein. OpenAI empfiehlt, den früheren Skill-Katalog nicht mehr zu verwenden. Für Codex sind deshalb die aktuelle Dokumentation und die Plugins als Installationsquellen angegeben. [Dokumentation zu Claude-Code-Skills](https://code.claude.com/docs/en/skills) · [Dokumentation zu Codex-Skills](https://learn.chatgpt.com/docs/build-skills) · [Hinweis zum früheren Katalog](https://github.com/openai/skills) · [OpenAI-Plugin-Repository](https://github.com/openai/plugins)

## 10 Empfehlungen für die Praxis

Die Spalte „Quelle und Umgebung“ nennt das offizielle Angebot oder den offiziellen Vertriebsweg. Das gemeinsame Format von `SKILL.md` lässt sich auch nutzen, wenn Sie ein Beispiel von Claude Code zu Codex übertragen. Prüfen Sie mitgelieferte Skripte, Werkzeugnamen und Einstellungen für die jeweilige Umgebung separat.

| Rang | Skill | Quelle und Umgebung | Beispielauftrag und Prüfung |
| --- | --- | --- | --- |
| 1 | `skill-creator` | In Codex integriert / [Claude-Code-Beispiel](https://github.com/anthropics/skills/tree/main/skills/skill-creator) | „Erstelle einen Skill für PR-Beschreibungen mit je einer Beispieleingabe für einen Korrektur-PR und einen Dokumentations-PR.“ Prüfen Sie den Umfang mit je einem passenden und unpassenden Auftrag. |
| 2 | `webapp-testing` | [Claude-Code-Beispiel](https://github.com/anthropics/skills/tree/main/skills/webapp-testing) | „Prüfe mit Playwright, ob das lokale Bestellformular erfolgreich abgesendet wird und wie es bei einem fehlenden Pflichtwert reagiert.“ Halten Sie den tatsächlichen Seitenzustand und das Ausführungsprotokoll fest. Browser und Anwendung müssen laufen können. |
| 3 | `frontend-design` | [Claude-Code-Beispiel](https://github.com/anthropics/skills/tree/main/skills/frontend-design) | „Gestalte die Mobilansicht eines Dashboards für Störfälle. Zeige Status und nächsten Schritt zuerst.“ Prüfen Sie auch leere Zustände, lange Texte und Tastaturnavigation. |
| 4 | `openai-docs` | In Codex integriert / [OpenAI-Developers-Leitfaden](https://developers.openai.com/learn/developers-codex-plugin) | „Ermittle aus der offiziellen Dokumentation, wo Codex CLI Projekt-Skills lädt und wie ich sie aufrufe.“ Prüfen Sie, ob die Quelle die CLI-Anzeige und die beschriebene Funktion direkt belegt. |
| 5 | `xlsx` | [Claude-Code-Skill für Dokumente](https://github.com/anthropics/skills/tree/main/skills/xlsx) | „Erstelle aus der Bestell-CSV eine Arbeitsmappe mit Monatsübersichten. Führe stornierte Bestellungen getrennt und berechne Summen per Formel.“ Vergleichen Sie Zeilenzahl, Auswertungsbereich und Summen mit der Quelle und prüfen Sie Formelfehler. |
| 6 | `pdf` | [Claude-Code-Skill für Dokumente](https://github.com/anthropics/skills/tree/main/skills/pdf) | „Extrahiere aus dem Anforderungs-PDF Lieferbedingungen und Ausnahmen mit Seitenzahlen.“ Prüfen Sie Zeilen- und Spaltenreihenfolge sowie mögliche Auslassungen anhand der Originalseiten. Bei Scans prüfen Sie die OCR-Qualität separat. |
| 7 | `docx` | [Claude-Code-Skill für Dokumente](https://github.com/anthropics/skills/tree/main/skills/docx) | „Erstelle eine Projektübergabe in der beigefügten Word-Vorlage und behalte Überschriftenstile und Tabellenstruktur bei.“ Öffnen Sie das Ergebnis in Word oder einem kompatiblen Editor und achten Sie auf Seitenumbrüche und abgeschnittene Tabellen. |
| 8 | `pptx` | [Claude-Code-Skill für Dokumente](https://github.com/anthropics/skills/tree/main/skills/pptx) | „Erstelle eine Retrospektive zum Betrieb auf 6 Folien. Nenne neben den Werten Messzeitraum und Einheit.“ Rendern Sie die Folien und prüfen Sie Werte, Achsen und abgeschnittenen Text. |
| 9 | `openai-api-troubleshooting` | [OpenAI-Developers-Plugin für Codex](https://github.com/openai/plugins/tree/main/plugins/openai-developers/skills/openai-api-troubleshooting) | „Grenze anhand dieser API-Fehlermeldung ohne Schlüssel die Ursache ein. SDK-Version und Anfrage-ID liegen bei.“ Trennen Sie Hypothesen und Prüfbefehle und lassen Sie echte Schlüssel und Tokens weg. |
| 10 | `imagegen` | In Codex integriert / [Skill-Quelle](https://github.com/openai/codex/tree/main/codex-rs/skills/src/assets/samples/imagegen) | „Erstelle einen Entwurf für ein Titelbild im Querformat. Der Beitragstitel soll nicht ins Bild.“ Prüfen Sie, ob die Generierung verfügbar ist, und kontrollieren Sie Bildgröße, Bearbeitungsumfang und verzerrten Text. |

`skill-creator` steht an erster Stelle, weil Teams damit wiederkehrende Abläufe im Projekt festhalten können. Für `webapp-testing` brauchen Sie Anwendung und Browser. Ausführungsprotokoll und sichtbarer Zustand helfen bei der Bewertung. Wählen Sie aus den vier Dokumentskills den zum Dateiformat passenden. API-Diagnose und Bildgenerierung helfen, wenn ein konkreter Fehler oder Bedarf an Bildmaterial vorliegt.

In der Entwicklung können Sie mit `frontend-design` die Anforderungen an die Oberfläche konkretisieren und nach der Umsetzung mit `webapp-testing` das Nutzerverhalten prüfen. Testen Sie auch bei vorhandenem Entwurf separat, ob Eingaben nach einem fehlgeschlagenen Absenden erhalten bleiben. Bei Dokumenten können Sie eine Tabelle mit `pdf` auslesen und mit `xlsx` auswerten. Vergleichen Sie das Ergebnis der Extraktion mit dem Original, bevor Sie es weitergeben.

## Skills installieren und aufrufen

Fügen Sie in Claude Code den offiziellen Marketplace von Anthropic hinzu und wählen Sie das passende Paket. Für PDF, Word, Excel und PowerPoint verwenden Sie `document-skills`, für Beispiele zum Erstellen von Skills oder für Webtests `example-skills`. Einen installierten Plugin-Skill können Sie in einer natürlich formulierten Anfrage beim Namen nennen. [Anthropics Installationsanleitung](https://github.com/anthropics/skills#claude-code)

```text
/plugin marketplace add anthropics/skills
/plugin install document-skills@anthropic-agent-skills
/plugin install example-skills@anthropic-agent-skills
```

In Codex CLI finden und wählen Sie Skills ausdrücklich über `/skills` oder die Auswahl mit `$`. Den integrierten `skill-creator` rufen Sie mit `$skill-creator` auf. Für die OpenAI-API-Diagnose suchen Sie in `/plugins` nach **OpenAI Developers** und wählen `Install plugin`. Starten Sie eine neue Sitzung und prüfen Sie unter `/skills`, ob der Diagnose-Skill angezeigt wird. [Codex-Skills aufrufen](https://learn.chatgpt.com/docs/build-skills) · [OpenAI-Developers-Plugin](https://developers.openai.com/learn/developers-codex-plugin)

Projektintern verwaltete Skills liegen für Claude Code unter `.claude/skills/<name>/SKILL.md`, für Codex unter `.agents/skills/<name>/SKILL.md`. Ersetzen Sie in beiden Pfaden den Platzhalter durch den Skill-Namen. Prüfen Sie beim Kopieren offizieller Beispiele auch die in `SKILL.md` referenzierten Dateien und Werkzeuge. Falls ein Skill eine Verbindung benötigt, prüfen Sie vor der Ausführung das Konto und den Zugriffsumfang. [Speicherorte für Claude-Code-Skills](https://code.claude.com/docs/en/skills#choose-where-skills-load) · [Speicherorte für Codex-Skills](https://learn.chatgpt.com/docs/build-skills#where-to-save-skills)

## Übung — denselben Release-Notes-Skill in beiden Tools nutzen

Führen Sie die folgenden Befehle in einem frischen Übungsverzeichnis aus. Sie schreiben eine `SKILL.md`, kopieren sie an beide Projektpfade und prüfen mit `cmp`, ob die Dateien identisch sind. Sie brauchen eine POSIX-Shell sowie `mkdir`, `cp` und `cmp`.

![Übungsverzeichnis erstellen und die ursprüngliche SKILL.md schreiben. In die Projektpfade von Claude Code und Codex kopieren, die Kopien vergleichen und beiden Tools dieselben Daten geben, um die Ergebnisse zu prüfen.](/assets/diagrams/technical/de-2026-11-18-claude-code-codex-skills-top-10.svg)

```sh
set -eu
mkdir skills-demo
cd skills-demo

mkdir -p .claude/skills/release-note-draft .agents/skills/release-note-draft

cat > release-note-source.md <<'SKILL'
---
name: release-note-draft
description: Draft a release note from a provided change list and test evidence.
---
Write three sections in Korean: 사용자 변경, 검증, 미확인.
Describe user-facing changes using only the supplied change list.
Put a test in 검증 only when the input explicitly says it ran and gives the result.
If a test is mentioned without a result, put it in 미확인.
Return the draft in the chat.
SKILL

cp release-note-source.md .claude/skills/release-note-draft/SKILL.md
cp release-note-source.md .agents/skills/release-note-draft/SKILL.md
cmp .claude/skills/release-note-draft/SKILL.md .agents/skills/release-note-draft/SKILL.md
printf '%s\n' 'Skill copies match.'
```

In einem temporären Verzeichnis unter macOS ergaben sich die folgende Ausgabe und Exitcode `0`. Beim erneuten Aufruf im selben übergeordneten Verzeichnis bricht das Skript beim ersten `mkdir` ab, weil `skills-demo` bereits existiert.

```text
Skill copies match.
```

Starten Sie von `skills-demo` aus `claude` und `codex` jeweils in einem eigenen Terminal. Wählen Sie `/release-note-draft` in Claude Code und `$release-note-draft` in Codex CLI. Senden Sie den Skill-Namen zusammen mit den folgenden Angaben zu Änderung und Tests in einer Nachricht.

> Änderung: Wenn das E-Mail-Feld auf der Einstellungsseite geleert wird, ist Speichern deaktiviert.\
> Geprüft: 3 Unit-Tests für die Einstellungsseite ausgeführt. Alle bestanden.\
> Geplant: Das Verhalten in einem mobilen Browser prüfen.\
> Erstelle aus diesen Angaben einen Entwurf für die Release Notes.

Das erwartete Ergebnis nennt das Verhalten der Schaltfläche als Änderung für Nutzer, die 3 bestandenen Unit-Tests unter den geprüften Punkten und den mobilen Browsertest unter den offenen Prüfungen.

## Antworten bei derselben Eingabe vergleichen

Beide CLIs wurden mit derselben Skill-Datei und denselben fiktiven Änderungs- und Testdaten gestartet. Die Aufgabe prüft anhand der bereitgestellten Angaben, ob sie **abgeschlossene von geplanten Tests trennen**. Dabei werden keine neuen Anwendungstests angefordert.

Im Protokoll von Codex CLI 0.169.0 mit GPT-6.2 Sol war zu sehen, dass das Tool die Skill-Datei des Projekts gelesen hatte. Die folgenden Aussagen geben die wesentlichen Punkte der Antwort wieder.

| Abschnitt | Antwort von Codex |
| --- | --- |
| Änderung für Nutzer | Wenn die eingegebene E-Mail-Adresse auf der Einstellungsseite gelöscht wird, ist Speichern deaktiviert. |
| Geprüft | Alle 3 Unit-Tests der Einstellungsseite wurden ausgeführt und bestanden. |
| Offen | Eine Prüfung im mobilen Browser ist geplant. |

Auch in Claude Code 2.0.76 und 2.1.327 erschien der Skill des Projekts in der Liste. Ein Anmeldefehler stoppte den Modellaufruf. Der Durchlauf belegt, dass Claude Code den Skill gefunden hat und Codex eine Antwort geliefert hat.
