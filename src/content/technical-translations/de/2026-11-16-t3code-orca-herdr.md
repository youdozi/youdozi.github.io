---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2026-11-16-t3code-orca-herdr",
  "routeSlug": "2026-11-16-t3code-orca-herdr",
  "kind": "post",
  "title": "T3 Code, Orca und Herdr im Vergleich: Das passende Werkzeug für KI-Coding-Aufgaben wählen",
  "description": "Vergleich von Aufgabenverwaltung, Worktrees, Code-Review, Berechtigungen und Sitzungserhalt bei T3 Code, Orca und Herdr mit Vorzügen und Auswahlkriterien.",
  "categories": [
    "ai"
  ],
  "tags": [
    "t3-code",
    "orca",
    "herdr",
    "ai-agent",
    "git-worktree"
  ],
  "sourcePath": "src/content/posts/en/2026-11-16-t3code-orca-herdr.md",
  "sourceSha256": "94725dbdc4ab213e11a438cbe4dbe69f888ffe3750e5d7c351e92178279c388e",
  "draftSha256": "0a1cffa8763d4b2ecc65342da2db917f71193720ce31c52a7070705188202bd6",
  "manifestPath": ".pipeline/technical-translations/batch-165/manifest.json",
  "manifestSha256": "8b72a2b5aba51a050b30cc0ef5f871d2ef550798d50d91ef082c49bbf6448835",
  "publishedAt": "2026-11-17T06:12:46.742Z",
  "updatedAt": "2026-11-17T06:12:46.742Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 165,
    "approvedAt": "2026-11-17T06:12:46.742Z",
    "basis": "User requested multilingual application of the five recent articles and standing publication/merge authorization; AI translation and independent AI comparison completed. This records publication authorization, not human or native-speaker textual review."
  }
}
---

**T3 Code eignet sich, um Aufgaben, Freigaben und Änderungen in einem Gesprächs-Thread zu verfolgen. Orca betont den gemeinsamen Umgang mit Terminal, Editor, Browser und Diff pro Worktree. Herdr ist einen Blick wert, wenn Sie Terminals weiterlaufen lassen und Arbeitsoberflächen sowie Automatisierung selbst gestalten möchten.** Die Funktionen der drei Werkzeuge überschneiden sich. Vergleichen Sie daher eher den Ablauf vom Start über die Prüfung bis zur Rückkehr nach einer Unterbrechung, statt anhand einer einzelnen Funktion eine Rangfolge festzulegen.

Verglichen werden [T3 Code](https://github.com/pingdotgg/t3code/tree/v0.1.9), [Orca](https://orca.dev/) und [Herdr](https://herdr.dev/). Sie sind von T3 Stack und ähnlich benannten Hydra-Projekten zu unterscheiden. Grundlage sind die am 16. November 2026 geprüften Dokumente; die konkreten Verhaltensweisen von T3 Code sind auf die **Dokumentation von v0.1.9** begrenzt. Für Orca und Herdr wurden die aktuellen offiziellen Dokumente herangezogen. Die folgenden Vorzüge und Abwägungen sind dokumentationsbasierte Auswahlkriterien, keine Leistungsmessungen der drei Apps in derselben Umgebung.

## Was steht bei der Arbeit im Mittelpunkt?

| Kriterium | T3 Code | Orca | Herdr |
| --- | --- | --- | --- |
| Hauptablauf | Anfragen, Freigaben und Änderungen in Projekten und Threads verfolgen | Agenten, Dateien, Browser und Diff pro Worktree verwalten | Terminals und Agenten in App/TUI verwalten, Oberflächengestaltung erweitern |
| Aufgabentrennung | Worktree-Funktion vorhanden; tatsächlichen Arbeitspfad prüfen | Branches und Oberflächen um Worktrees pro Aufgabe organisieren | Worktree-Funktionen in App und TUI; ein Pane selbst ist kein Worktree |
| Änderungsprüfung | Änderungen eines Gesprächszugs vom Vergleich des gesamten Branches unterscheiden | Worktree-Diff, zeilenbezogene Kommentare, teilweises Staging | Review-Ablauf der gewählten App-Konfiguration und Terminal-Werkzeuge prüfen |
| Berechtigungen | Thread-Berechtigungsmodus zusammen mit anbieterspezifischem Verhalten prüfen | Berechtigungseinstellungen des Agenten und tatsächlichen Ausführungsumfang prüfen | Berechtigungen ausgeführter Agenten, Befehle und Erweiterungen prüfen |
| Remote-Nutzung | Andere Geräte mit dem Server verbinden | SSH-Hosts, entfernte Orca-Laufzeit | Separate Remote-Funktionen für App/core und TUI |
| Kostenbewertung | Kosten für App und Modellanbieter sowie Bedingungen verbundener Dienste getrennt prüfen | Kosten für App, Modellanbieter und Remote-Rechenleistung getrennt prüfen | Kosten für App/core/TUI, Modellanbieter und Server getrennt prüfen |

Grundlage für die Abläufe sind T3 Codes [Versionsverwaltungsdokumentation](https://github.com/pingdotgg/t3code/blob/v0.1.9/docs/user/source-control.md), Orcas [Worktree-Dokumentation](https://orca.dev/docs/model/worktrees) und Herdrs [App-Anleitung](https://herdr.dev/guide/). In der Tabelle nicht geprüfte Funktionen wurden nicht als fehlend eingestuft. Insbesondere bietet auch T3 Code Worktrees und eine Review-Oberfläche, und auch Herdr hat eine Desktop-App.

## T3 Code: Gespräch und Ausführungsergebnisse gemeinsam verfolgen

T3 Code verbindet installierte Anbieter mit Projekten und Threads. Die [README von v0.1.9](https://github.com/pingdotgg/t3code/blob/v0.1.9/README.md) beschreibt Clients für Mobilgeräte, Web und Desktop sowie die Anbindung vorhandener Anbieter wie Codex und Claude Code. Wer das Werkzeug als eigenen Modellanbieter versteht, kann bei Installation und Authentifizierung leicht durcheinanderkommen.

Ein Vorzug ist, dass sich Arbeitsauftrag, Ausführung, Freigaben und Änderungen in einem Thread verfolgen lassen. Die Versionsverwaltungsdokumentation unterscheidet Änderungen eines einzelnen Gesprächszugs von sämtlichen Änderungen gegenüber dem Referenzbranch. Hat der Agent beispielsweise zunächst aktuellen Code übernommen und dann Änderungen vorgenommen, darf das Lesen der Änderungsliste dieses Zugs nicht als abgeschlossene Prüfung des gesamten Branches gelten.

Zu beachten ist, dass Berechtigungsmodi je nach Anbieter nicht dieselbe Bedeutung haben. Wählen Sie den Modus anhand der [Berechtigungsdokumentation](https://github.com/pingdotgg/t3code/blob/v0.1.9/docs/user/permission-modes.md) und prüfen Sie tatsächliche Freigabeanfragen. Eine Freigabeoberfläche bedeutet nicht, dass auch Datei- und Netzwerkzugriffe auf Betriebssystemebene isoliert sind.

Auch bei der Remote-Nutzung ist die Lebensdauer des Servers entscheidend. Laut [Dokumentation zum Remote-Zugriff](https://github.com/pingdotgg/t3code/blob/v0.1.9/docs/user/remote-access.md) stoppt der lokale Server, wenn das letzte Fenster der Desktop-App geschlossen wird. Für dauerhaften Betrieb muss in einer unterstützten Umgebung ein separater Hintergrunddienst eingerichtet werden. Dieser Dienst ist in der betrachteten Version nicht für Windows verfügbar; unterscheiden Sie daher die Ausführungsarten. Auf dem Server müssen außerdem Anbieteranmeldung und Repository bereitstehen.

## Orca: Entwicklungsoberfläche und Änderungsprüfung pro Aufgabe verbinden

Orca ist eine Entwicklungsumgebung, die je Aufgabe einen Worktree erstellt und dort Agent, Editor, Browser und Diff bereitstellt. Die [Diff-Dokumentation](https://orca.dev/docs/review/diff-viewer) beschreibt unter anderem geänderte Zeilen, teilweises Staging und die Konfliktlösungsansicht. Das erleichtert einen Ablauf, in dem Sie eine Oberfläche ändern, im Browser prüfen und die Änderungen begutachten.

Ein Vorzug ist, dass Dateien und Review-Oberfläche im selben Worktree-Kontext verwaltet werden. Auch mit mehreren Agenten können Sie die Prüfung, zu welchem Branch Änderungen gehören, mit der Oberfläche verbinden. Arbeitsbereiche und Terminals lassen sich außerdem per CLI und Skills steuern. [CLI-Anleitung](https://orca.dev/docs/cli/overview)

Zu beachten ist, dass Sie Aufbau und Git-Ablauf der Entwicklungsumgebung kennenlernen müssen. Bei einer kurzen Einzeländerung kann der Aufwand für Worktrees und mehrere Ansichten ihren Nutzen übersteigen. Mit mehr Agenten können auch Ressourcenverbrauch und Zahl der zu prüfenden Ergebnisse steigen. Parallele Ausführung garantiert keine proportionale Zeitersparnis.

Laut [Dokumentation zur Sitzungswiederherstellung](https://orca.dev/docs/model/session-restore) laufen Agenten nach dem Schließen der App weiter, sofern der Daemon lebt. Ein Host-Neustart oder Daemon-Ende stoppt die Prozesse. Das Wiederherstellen von Arbeitsbereich und Scrollback ist nicht die Wiederherstellung laufender Prozesse. Auch [Remote-Ausführung](https://orca.dev/docs/ways-to-run) ist möglich, aber Werkzeuge und Authentifizierung auf dem ausführenden Host müssen gesondert vorbereitet werden.

## Herdr: Terminals und Arbeitsoberflächen selbst gestalten

Bei Herdr müssen **Desktop-App, herdr-core und Herdr TUI unterschieden** werden. Die App läuft auf herdr-core, die TUI nutzt einen separaten Server. Die offizielle FAQ stellt ausdrücklich klar, dass App und TUI keine gemeinsame Agentenliste haben. [Offizielle Herdr-Website](https://herdr.dev/)

Ein Vorzug ist, dass sich Terminal-Laufzeit und Oberflächengestaltung getrennt erweitern lassen. Die [core-Anleitung](https://herdr.dev/core/) beschreibt Programmausführung, das Starten weiterer Aufgaben, Ergebnisabfragen und Verbindungen mit entfernten Maschinen. Die [App-Anleitung](https://herdr.dev/guide/) zeigt auch, wie Sie einen Agenten bitten können, Layout oder Funktionen zu ändern. Das ist interessant, wenn Sie Ihre vorhandene terminalorientierte Entwicklungsumgebung behalten und ein eigenes Dashboard gestalten möchten.

Zu beachten ist die zusätzliche Verantwortung, Komponenten und Erweiterungen zu verstehen. Die Statusanzeige der App hängt von OSC-7501-Meldungen der Programme ab. Programme ohne Statusmeldungen können laufen, ohne dass ihr Status angezeigt wird. Verwechseln Sie dies nicht mit den Regeln zur Agentenerkennung der TUI. Prüfen Sie außerdem, welche Befehle und externen Verbindungen benutzerdefinierte Modi oder Plugins verwenden.

Terminals bleiben nach dem Schließen des App-Fensters bestehen, solange core läuft. Laut FAQ beendet ein Geräteneustart oder das Stoppen von core die Prozesse, und die App startet Agenten nicht automatisch neu. Die TUI bietet nach einem Serverneustart die Layout-Wiederherstellung und die Fortsetzung unterstützter Agentensitzungen als separate Funktionen. [TUI-Wiederherstellungsdokumentation](https://herdr.dev/tui/docs/session-state/)

## Gemeinsame Grenzen der Worktrees in allen drei Werkzeugen

Wenn mehrere Agenten gleichzeitig dieselben Dateien ändern, lassen sich Änderungen mit einem Worktree pro Aufgabe leichter verfolgen. Getrennte Dateiverzeichnisse isolieren aber nicht automatisch Datenbanken, Entwicklungsserver-Ports, externe Konten oder Zugangsdaten. Diese Einschränkung gilt für alle drei Werkzeuge.

![Zwei Worktrees aus dem Ausgangsrepository erstellen und unterschiedliche Dateiinhalte schreiben. Dateien und Änderungslisten mit der Ausgangsdatei vergleichen; die tatsächliche Zusammenführung gesondert prüfen](/assets/diagrams/technical/de-2026-11-16-t3code-orca-herdr.svg)

Der folgende Code prüft die in der Abbildung gezeigte Dateitrennung. Er erstellt in einer macOS- oder Linux-Shell mit installiertem Git ein temporäres Repository und ändert keine vorhandenen Projekte. Er umfasst weder Agentenausführung noch einen Leistungsvergleich der Produkte.

```sh
#!/bin/sh
set -eu
case_dir=$(mktemp -d)
git init -q "$case_dir/repo"
git -C "$case_dir/repo" config user.name 'Example Author'
git -C "$case_dir/repo" config user.email 'example@example.invalid'
printf 'base\n' > "$case_dir/repo/app.txt"
git -C "$case_dir/repo" add app.txt
git -C "$case_dir/repo" commit -qm 'Initial commit'
git -C "$case_dir/repo" worktree add -qb task-a "$case_dir/task-a" HEAD
git -C "$case_dir/repo" worktree add -qb task-b "$case_dir/task-b" HEAD
printf 'task A\n' > "$case_dir/task-a/app.txt"
printf 'task B\n' > "$case_dir/task-b/app.txt"
printf 'A: '; cat "$case_dir/task-a/app.txt"
printf 'B: '; cat "$case_dir/task-b/app.txt"
printf 'base: '; cat "$case_dir/repo/app.txt"
printf 'A 변경 파일: '; git -C "$case_dir/task-a" diff --name-only
printf 'B 변경 파일: '; git -C "$case_dir/task-b" diff --name-only
```

Diese Ausgabe wurde bei der Ausführung in einer lokalen Shell überprüft.

```text
A: task A
B: task B
base: base
A 변경 파일: app.txt
B 변경 파일: app.txt
```

A und B behalten unterschiedliche Inhalte, haben aber dieselbe Datei geändert. Bei der Integration muss die Absicht beider Änderungen geprüft werden. Das Beispiel löscht das temporäre Verzeichnis nicht automatisch.

## Welches Werkzeug zuerst ausprobieren?

Wenn Sie Anfragen, Freigaben und Änderungen gern im Gespräch verfolgen, können Sie mit **T3 Code** beginnen. Wenn Sie Browser, Editor und Diff pro Aufgabe getrennt betrachten möchten, bietet sich **Orca** an. Wenn Sie Terminals und Dashboards selbst gestalten möchten, ist **Herdr** ein möglicher Ausgangspunkt. Diese Vorschläge leiten sich aus dem Funktionsaufbau der offiziellen Dokumentation ab.

Prüfen Sie Ihre Wahl mit demselben Repository und derselben Aufgabe sowie identischem Modell, identischen Berechtigungen und Testbedingungen für alle drei Werkzeuge. Legen Sie vor Dateiänderungen einen fehlschlagenden Test fest und kontrollieren Sie nach Abschluss Ausführungsergebnisse, Diff und verbleibende Änderungen. Behandeln Sie das Schließen des App-Fensters, die Client-Trennung, das Stoppen des Servers und den Host-Neustart als verschiedene Tests. Vergleichen Sie neben der Bearbeitungszeit auch den Aufwand für Rückkehr und Review, um die Unterschiede für Ihre Arbeitsweise zu erkennen.

Konkrete Abläufe finden Sie im [T3-Code-Beispiel](/ko/posts/2026-11-12-t3-code-workflow/), in der [Orca-Anleitung](/ko/posts/2026-11-12-orca-worktree-guide/) und im [ausführlichen Vergleich von Orca und Herdr](/ko/posts/2026-11-15-orca-herdr-comparison/).
