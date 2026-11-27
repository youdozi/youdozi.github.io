---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2026-11-27-droiddesk-android-linux-desktop",
  "routeSlug": "2026-11-27-droiddesk-android-linux-desktop",
  "kind": "post",
  "title": "DroidDesk im Detail · Wie läuft ein Linux-Desktop auf einem Android-Smartphone?",
  "description": "Welche Laufzeitumgebung und Anzeige verwenden die eigenständige APK und das Termux-Skript? Davon hängt ab, was sich auf dem eigenen Gerät sinnvoll testen lässt.",
  "categories": [
    "tips"
  ],
  "tags": [
    "android",
    "linux",
    "termux"
  ],
  "sourcePath": "src/content/posts/en/2026-11-27-droiddesk-android-linux-desktop.md",
  "sourceSha256": "656b9e1b21a758a366d894876650b607e9bd2eadcb535e4a0565a68566807a1f",
  "draftSha256": "e24a5cb0b9f7e9a00b8f5bff55cfe20910a8ff4b23da89d9f33c7b409a4ac2bd",
  "manifestPath": ".pipeline/technical-translations/batch-130/manifest.json",
  "manifestSha256": "155408f4218bb7fd2e43ec0f8dcb31522024a85ed96fb84e2f9768840357e28c",
  "publishedAt": "2026-11-27T06:13:21.434Z",
  "updatedAt": "2026-11-27T06:13:21.434Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 207,
    "approvedAt": "2026-11-27T06:13:21.434Z",
    "basis": "Explicit user request to publish the approved DroidDesk manuscript from item 129 in all nine languages (item 130)."
  }
}
---

Lässt sich an ein ausgedientes Android-Smartphone eine Tastatur anschließen, um mit einem Linux-Editor und einem Browser zu arbeiten? Das Open-Source-Projekt DroidDesk bringt einen Linux-Desktop auf Android. Vor der Installation lohnt ein Blick auf die Unterschiede zwischen der eigenständigen APK und dem Installationsskript für Termux.

Grundlage dieses Artikels sind die Versionshinweise und der Quellcode von orailnoor/DroidDesk v1.3.1, eingesehen am 27. November 2026. Ich habe die APK auf keinem physischen Gerät installiert und keine Leistungsmessungen für einzelne Anwendungen durchgeführt. [Versionshinweise](https://github.com/orailnoor/DroidDesk/releases/tag/v1.3.1)

## Worin unterscheiden sich die APK und das Termux-Skript?

| Installation | Laufzeitumgebung | Bildausgabe |
| --- | --- | --- |
| Eigenständige APK ohne Root-Rechte | Standard-Desktop in der integrierten Termux-Umgebung, optional Debian über PRoot | Integriertes Termux:X11 |
| Eigenständige APK mit Root-Rechten | ARM64-Ubuntu-Dateisystem in einer chroot-Umgebung | Integriertes Termux:X11 |
| Termux-Installationsskript | Separate Termux-Installation, PRoot für Distributionspakete | Separate Termux:X11-App oder optional VNC |

![Die eigenständige APK verwendet das integrierte Termux:X11. Beim Termux-Skript übernimmt eine separate Termux:X11-App oder VNC die Anzeige.](/assets/diagrams/technical/de-2026-11-27-droiddesk-android-linux-desktop.svg)

Laut README verwendet die APK ohne Root-Rechte kein PRoot. Für den Standard-Desktop trifft das zu: Er läuft direkt in Termux. LinuxRuntime enthält in v1.3.1 allerdings auch eine optionale Debian-Installation und einen PRoot-Starter. Selbst innerhalb derselben App kann ein Programm unter unterschiedlichen Bedingungen laufen, je nachdem, ob es auf dem Standard-Desktop oder in Debian gestartet wird. [README](https://github.com/orailnoor/DroidDesk/blob/v1.3.1/README.md) · [LinuxRuntime](https://github.com/orailnoor/DroidDesk/blob/v1.3.1/app/android/app/src/main/kotlin/com/orailnoor/droiddesk/runtime/LinuxRuntime.kt) · [ChrootRuntime](https://github.com/orailnoor/DroidDesk/blob/v1.3.1/app/android/app/src/main/kotlin/com/orailnoor/droiddesk/runtime/ChrootRuntime.kt)

## Was lässt sich auf dem eigenen Smartphone nutzen?

Am besten beginnt man mit einem Programm, das man wirklich braucht. Das Projekt nennt unter anderem Firefox, LibreOffice und VS Code als Beispiele. Die Versionshinweise zu v1.3.1 nennen auch behobene Installations- und Startfehler, etwa bei einem für Firefox benötigten Paket und bei VS Code. Sobald das Editor-Symbol zu sehen ist, bleibt zu prüfen, ob die gewohnten Erweiterungen, Eingabemethoden und Dateipfade funktionieren. [Versionshinweise](https://github.com/orailnoor/DroidDesk/releases/tag/v1.3.1)

Auch die Grafik hängt vom Gerät ab. Im Quellcode gibt es einen Pfad mit Turnip und Zink für Adreno sowie Software-Rendering mit llvmpipe. Bei einer grafikintensiven Anwendung wie Blender zählt neben dem Start, ob die Beschleunigung auf dem Gerät greift und wie flüssig sich das eigene Projekt bearbeiten lässt. Wer unter PRoot kompilieren möchte, sollte bei vielen Dateizugriffen mit möglichem Mehraufwand rechnen. [Grenzen von PRoot](https://github.com/termux/proot-distro#limitations)

Für einen externen Monitor sollte man zuerst prüfen, ob das Smartphone die Bildausgabe über USB-C unterstützt. Beim dokumentierten Aufbau mit einem Raspberry Pi empfängt der Pi die vom Termux-Skript bereitgestellte VNC-Sitzung und zeigt sie auf dem Monitor an. Die eigenständige APK nutzt für die Anzeige ihr integriertes X11. [Monitoranschluss](https://github.com/orailnoor/DroidDesk/blob/v1.3.1/README.md#for-monitor-output--optional-)

## Was eignet sich als erster Test?

Wer ein Android-Gerät mit ARM64 hat, findet die APK auf der offiziellen Release-Seite des Projekts. Für den ersten Test reicht das Display des Smartphones: etwa im Editor einen koreanischen Text schreiben, die Datei speichern, die Sitzung erneut öffnen und dieselbe Datei laden. Gelingt das, kann man die gewohnte Arbeit mit Tastatur und Maus oder einem externen Monitor fortsetzen. Der Reiz von DroidDesk liegt darin, Linux-Werkzeuge auf einem Gerät auszuprobieren, das man schon besitzt. Für Dokumente sind Eingabe und Speichern der erste Test, für Entwicklungsarbeit die benötigten Pakete und Erweiterungen, für Grafik die Beschleunigung und die Reaktion auf Eingaben. [Android-Buildkonfiguration](https://github.com/orailnoor/DroidDesk/blob/v1.3.1/app/android/app/build.gradle.kts)

[Speicherplatz von Docker Desktop auf dem Mac prüfen](../2026-11-27-docker-desktop-mac-disk-space/)
