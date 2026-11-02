---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2026-11-02-open-source-game-engines",
  "routeSlug": "2026-11-02-open-source-game-engines",
  "kind": "post",
  "title": "Open-Source-Spielengines im Vergleich: Godot, Bevy, Stride und O3DE",
  "description": "Godot, Bevy, Stride und O3DE nach Teamworkflow, Lizenzierung und Einschränkungen der Zielplattform vergleichen – mit einem ausführbaren Bewegungstest in Godot.",
  "categories": [
    "game-development"
  ],
  "tags": [
    "game-engine",
    "open-source",
    "godot",
    "bevy",
    "stride",
    "o3de"
  ],
  "sourcePath": "src/content/posts/en/2026-11-02-open-source-game-engines.md",
  "sourceSha256": "a83f90ac45031156dd23d82e78c770e9d3254849fbf67e9594455bc58c54e153",
  "draftSha256": "33b63f852926b16ceafde8e41e6c715f44b52f0411bee16c78d864b0ad4e0425",
  "manifestPath": ".pipeline/technical-translations/batch-133/manifest.json",
  "manifestSha256": "012f8ab540d4cc0a5cef8d221664572be5fe6cfb38caebd3ef7cfc3c84c954a2",
  "publishedAt": "2026-11-02T04:33:37.064Z",
  "updatedAt": "2026-11-02T04:33:37.064Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 133,
    "approvedAt": "2026-11-02T04:33:37.064Z",
    "basis": "User explicitly requested writing and publishing a blog article using the game-engine review writing skill on 2026-11-02, with existing multilingual publication and standing blog PR merge authorization. Human approval denotes user publication authorization, not human/native linguistic review; language reviews are AI."
  }
}
---

**Für ein kleines Team, das ein allgemeines 2D- oder 3D-Spiel beginnt, ist Godot ein sinnvoller erster Kandidat. Bevy passt zu einem Rust-Team, das mehr Verantwortung für seine Werkzeuge übernehmen möchte; Stride verdient bei C#-Workflows einen Blick; O3DE lohnt eine Prüfung, wenn ein Team eine umfangreichere Pipeline für 3D-Inhalte und Builds betreuen kann.** Das sind Ausgangspunkte für die Validierung, keine Leistungsrangliste.

Dies ist ein dokumentenbasierter Vergleich für Entwickler, die eine Spielengine auswählen. Die am 2. November 2026 geprüften Release-Referenzen sind Godot 4.7.2, Bevy 0.20, Stride 4.4 und O3DE 26.05. Das ausführbare Beispiel unten testet nur eine kleine Bewegungsfunktion in Godot; es belegt weder die Bedienung der Editoren noch die Renderinggeschwindigkeit oder die Exportzuverlässigkeit der anderen Engines.

## Was vergleichen wir?

Alle vier Projekte bezeichnen sich als Spielengines. Ihre Arbeitsabläufe unterscheiden sich: Ein integrierter visueller Editor und ein codeorientierter ECS-Workflow lassen dem Team unterschiedlich viel Werkzeugbau übrig. Auch ein Framework oder eine Renderingbibliothek kann passen. Fehlende Werkzeuge für Szenen, Assets und Bearbeitung müssen dann aber als Arbeit berücksichtigt werden, die das Team selbst übernimmt.

| Engine und Release-Referenz | Entwicklungsworkflow | Erste Frage vor der Festlegung |
| --- | --- | --- |
| [Godot 4.7.2](https://godotengine.org/download/archive/) | Szenen-/Knoteneditor mit Skripting | Kann die gewählte Sprache auf das tatsächliche Ziel exportieren? |
| [Bevy 0.20](https://bevy.org/news/bevy-0-20/) | Rust-Systeme und -Komponenten auf ECS-Basis | Kann das Team Werkzeuge und API-Migrationen pflegen? |
| [Stride 4.4](https://www.stride3d.net/blog/announcing-stride-4-4/) | C# und Game Studio | Ist der Editor auf den Entwicklungsrechnern verfügbar? |
| [O3DE 26.05](https://www.docs.o3de.org/docs/release-notes/2605-0-release-notes/) | Erweiterbarer 3D-Editor und Komponentenpipeline | Kann das Team eine kleine Szene bauen, Assets importieren und die Szene paketieren? |

Die folgenden Szenarien sind aus diesen Workflows abgeleitete Empfehlungen. Sie berichten nicht von einem Team, das mit jeder Engine ein Spiel veröffentlicht hat.

## Welche Engine passt zum Workflow des Teams?

### Godot: mit dem vollständigen Erstellungszyklus beginnen

Godot ist ein vernünftiger Ausgangspunkt, wenn das Team Szenen bearbeiten, Verhalten zuordnen und in einer Umgebung iterieren möchte. Die [MIT-Lizenz](https://godotengine.org/license/) erlaubt proprietäre Spiele; bei der Weitergabe der Engine sind weiterhin die entsprechenden Urheberrechts- und Lizenzhinweise erforderlich. Plugins, Schriftarten, Musik und Modelle haben eigene Bedingungen.

Prüfen Sie die Kombination aus Sprache und Plattform frühzeitig. Laut der [Dokumentation zum Godot-Webexport](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_web.html) können Godot 4 C#-Projekte derzeit nicht für das Web exportiert werden. Ein C#-Desktopprototyp belegt daher keine Bereitstellung im Browser. Für Konsolen beschreibt [Godots Portierungsleitfaden](https://godotengine.org/consoles/) die Plattformfreigabe, offizielle SDKs sowie private Exportvorlagen oder Drittanbieter. Eine Open-Source-Engine hebt dieses Verfahren nicht auf.

### Bevy: Rust und Verantwortung für die Werkzeuge gemeinsam wählen

Bevy ist eine Engine, nicht nur ein Renderer. Die [Einführung](https://bevy.org/learn/quick-start/introduction/) beschreibt Rust, ECS und die Wahl zwischen MIT- und Apache 2.0-Lizenzierung. Sie warnt außerdem vor Releases mit inkompatiblen API-Änderungen und möglicherweise schwierigen Migrationen.

Damit ist Bevy für ein Team interessant, das Systeme und Komponenten ins Zentrum seines Entwicklungsmodells stellen möchte. Editorintegration, Asset-Iteration und Versionsmigration sollten mit dem eigenen Projekt nachgewiesen werden. Rust-Kenntnisse allein belegen keinen schnelleren Erstellungszyklus, und ein paralleles ECS beweist keine besseren Framezeiten für ein bestimmtes Spiel.

### Stride: C#-Unterstützung und Editorverfügbarkeit getrennt betrachten

Die [FAQ](https://www.stride3d.net/faq/) von Stride beschreibt die MIT-Lizenzierung und den Verzicht auf Engine-Lizenzgebühren. Der C#-Workflow kann Stride für ein bestehendes .NET-Team zu einem sinnvollen Kandidaten machen.

Die [Plattformmatrix](https://doc.stride3d.net/latest/en/manual/platforms/index.html) unterscheidet Entwicklungsrechner und Spielzielplattformen: Windows bietet vollständige Editorunterstützung; Linux und macOS unterstützen mit Einschränkungen Build- und rein codebasierte Workflows, und außerhalb von Windows ist der Editor nicht nativ verfügbar. Die [Ankündigung von 4.4](https://www.stride3d.net/blog/announcing-stride-4-4/) berichtet von Verbesserungen für Builds außerhalb von Windows. Daraus sollte nicht abgeleitet werden, dass überall derselbe Editorworkflow verfügbar ist.

### O3DE: erst die Pipeline prüfen, dann die Vorzeigefunktionen

O3DE gehört auf die engere Auswahlliste eines Teams, das eine erweiterbare 3D-Pipeline selbst betreuen kann. Die [Lizenzdatei](https://github.com/o3de/o3de/blob/2605.0/LICENSE.txt) nennt standardmäßig Apache 2.0 mit einer MIT-Option und weist gesonderte Drittanbieterkomponenten aus. Die [Downloadseite](https://o3de.org/download/) führt Pakete für Windows/Linux und erhebliche Anforderungen an Entwicklungsrechner auf. Das sind Anforderungen an den Entwicklungsrechner, keine pauschale Liste der Exportziele für Spiele.

Beginnen Sie mit dem Import eines repräsentativen Assets, einem Projektbuild und einer paketierten Szene. Die [Release Notes zu 26.05](https://www.docs.o3de.org/docs/release-notes/2605-0-release-notes/) kennzeichnen das neue Partikelsystem als experimentell und raten vom Produktionseinsatz ab. Eine in den Release Notes genannte Funktion ist nicht automatisch eine produktionsreife Abhängigkeit.

## Bedeutet „kostenlos“ Open Source oder kostenfreie Produktion?

Nein. Quellcodezugriff und ein Kaufpreis von null belegen keine Open-Source-Lizenz. Beispielsweise [beschreibt sich Defold derzeit als „source available“](https://defold.com/open/); prüfen Sie seine konkrete Lizenz, statt es automatisch den vier obigen Engines zuzuordnen.

Die Engine-Lizenzierung bezahlt auch keine Konsolenportierung, Asset-Lizenzen, Hosting, Plugins oder Wartung. Klären Sie vor der Entscheidung, welche Teile die Engine liefert, welche eine weitere Lizenz benötigen und welche das Team selbst baut. Schätzen Sie ohne diese Abgrenzung keine Gesamtkosten.

## Was sollte ein kleiner Prototyp prüfen?

Geben Sie den Engines der engeren Auswahl dieselbe Abnahmeaufgabe: ein repräsentatives Asset laden, eine Interaktion implementieren und einen Build für das vorgesehene Ziel erstellen. Halten Sie Einrichtung, Reibungsverluste beim wiederholten Bearbeiten und Ausführen sowie nicht unterstützte Anforderungen fest. Dies ist ein vorgeschlagenes Bewertungsverfahren, kein für diesen Artikel durchgeführter Benchmark.

Hier ist ein reproduzierbarer Teil: ein **Headless-Bewegungstest in Godot**. Er nimmt Position, synthetische Richtung und verstrichene Sekunden entgegen, begrenzt den Richtungsbetrag auf 1, wendet die Geschwindigkeit an und begrenzt den resultierenden Punkt auf ein Rechteck. Die Eingaben werden als endlich und die verstrichene Zeit als nichtnegativ vorausgesetzt. Diese Begrenzung ist weder Hinderniskollision noch Berücksichtigung der Sprite-Größe oder eine Physiksimulation.

![Position, Richtung und verstrichene Zeit entgegennehmen, Richtungsbetrag begrenzen, Geschwindigkeit und Zeit anwenden, den Punkt auf die Grenzen beschränken und die neue Position zurückgeben](/assets/diagrams/technical/de-2026-11-02-open-source-game-engines.svg)

Das Diagramm zeigt einen Aufruf von `advance`. Der folgende Testrahmen wiederholt Aufrufe und prüft Ergebnisse; er liest keine Tastatur aus und rendert keine Spielfigur. Die [Vector2-Referenz](https://docs.godotengine.org/en/4.7/classes/class_vector2.html) dokumentiert die Vektoroperationen. So bleibt das getestete Verhalten von Aussagen über Editorproduktivität oder Spielleistung getrennt.

Wenn die Standard-Editorbinärdatei von Godot 4.7.2 als `godot` verfügbar ist, speichern Sie `project.godot` und `movement.gd` im selben Verzeichnis. Nach der Engine-Installation sind zum Ausführen des Skripts weder Szene noch externe Assets, Pakete oder Netzwerkzugriff erforderlich.

`project.godot`:

```ini
config_version=5
```

`movement.gd`:

```gdscript
extends SceneTree

const SPEED := 120.0
const LIMIT := Vector2(640.0, 360.0)

func advance(pos: Vector2, direction: Vector2, delta: float) -> Vector2:
    var bounded := direction.limit_length(1.0)
    var next := pos + bounded * SPEED * delta
    return next.clamp(Vector2.ZERO, LIMIT)

func _initialize() -> void:
    var cases := [
        [Vector2(100, 100), Vector2.ZERO, 0.5, Vector2(100, 100)],
        [Vector2(100, 100), Vector2.RIGHT, 0.5, Vector2(160, 100)],
        [Vector2.ZERO, Vector2(1, 1), 1.0, Vector2(84.852814, 84.852814)],
        [Vector2.ZERO, Vector2(0.5, 0), 1.0, Vector2(60, 0)],
        [Vector2(639, 100), Vector2.RIGHT, 1.0, Vector2(640, 100)],
        [Vector2(5, 100), Vector2.LEFT, 1.0, Vector2(0, 100)],
        [Vector2(100, 359), Vector2.DOWN, 1.0, Vector2(100, 360)],
        [Vector2(100, 100), Vector2.RIGHT, 0.0, Vector2(100, 100)],
    ]
    for sample in cases:
        var actual := advance(sample[0], sample[1], sample[2])
        if not actual.is_equal_approx(sample[3]):
            push_error("movement mismatch")
            quit(1)
            return
    var split := advance(advance(Vector2(100, 100), Vector2.RIGHT, 0.25), Vector2.RIGHT, 0.25)
    if not split.is_equal_approx(advance(Vector2(100, 100), Vector2.RIGHT, 0.5)):
        push_error("time-step mismatch")
        quit(1)
        return
    print("movement cases=9")
    quit(0)
```

Führen Sie das Skript aus diesem Verzeichnis über [Godots Kommandozeilenschnittstelle](https://docs.godotengine.org/en/4.7/tutorials/editor/command_line_tutorial.html) aus. Ersetzen Sie unter macOS `godot` durch den Pfad `Godot.app/Contents/MacOS/Godot` im installierten Anwendungspaket, falls die Binärdatei nicht auf `PATH` liegt.

```sh
godot --headless --no-header --path . --script movement.gd --quit-after 1
```

Das Beispiel wurde lokal unter macOS mit Godot 4.7.2 ausgeführt. Die Ausgabe lautete:

```text
movement cases=9
```

Die Prüfungen decken inaktive Eingaben, horizontale und diagonale Bewegung, einen teilweisen Richtungsbetrag, obere/untere Grenzen, keine verstrichene Zeit und einen aufgeteilten Zeitschritt abseits der Grenzen ab. Sie prüfen weder Rendering noch Export auf Zielgeräte, Hindernisse, Netzwerkfunktionen oder vergleichende Leistung.

## Wie sollte die endgültige Wahl getroffen werden?

Wählen Sie den Kandidaten, der den benötigten Workflow und den Zielbuild des Spiels mit einem für das Team tragbaren Wartungsaufwand erfüllt. Hat ein visueller Bearbeitungszyklus Priorität, beginnen Sie den Prototyp mit Godot. Will das Team ausdrücklich Rust/ECS selbst verantworten, prüfen Sie Bevys Werkzeug- und Migrationskosten. Testen Sie für ein C#-Team Stride auf den tatsächlichen Editorrechnern. Validieren Sie bei einer größeren 3D-Pipeline den Asset-/Build-Zyklus von O3DE, bevor Sie sich auf eine Vorzeigefunktion verlassen.

Das nächste nützliche Ergebnis ist ein kleiner Build für das Zielgerät samt Liste unerfüllter Anforderungen, keine universelle Rangliste der Engines. Bewahren Sie diese Entscheidungsgrundlagen beim Projekt auf, damit sich ein Engine-Upgrade anhand desselben Verhaltens bewerten lässt.
