---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2026-10-30-verify-sha256-download",
  "routeSlug": "2026-10-30-verify-sha256-download",
  "kind": "post",
  "title": "SHA-256-Prüfsumme einer heruntergeladenen Datei mit Python prüfen",
  "description": "Vergleichen Sie eine heruntergeladene Datei mit einem vertrauenswürdigen SHA-256-Wert per Streaming-Prüfung in Python. Reproduzieren Sie passende, veränderte und unlesbare Dateien mit expliziten Exit-Codes.",
  "categories": [
    "linux"
  ],
  "tags": [
    "python",
    "shellscript",
    "sha256"
  ],
  "sourcePath": "src/content/posts/en/2026-10-30-verify-sha256-download.md",
  "sourceSha256": "9c91eef87fd5390b5be8f867c298bdaaaa20979b4571c13ba7694d62ba172e89",
  "draftSha256": "e8d86546a23eb9cac7db41a745b58c59d985ea815049cbc4cba0e9ea13183623",
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
Um eine heruntergeladene Datei zu prüfen, berechnen Sie ihren SHA-256-Hash und vergleichen ihn mit dem erwarteten Wert eines vertrauenswürdigen Herausgebers. Pythons [hashlib](https://docs.python.org/3.11/library/hashlib.html) kann die Binärbytes blockweise hashen. Eine Übereinstimmung prüft diese Bytes gegen diesen Wert; sie authentifiziert weder den Herausgeber noch belegt sie, dass das Programm sicher ist. Adoptium dokumentiert die [Signaturprüfung](https://adoptium.net/installation/gpg-verification) separat.

## Welche Prüfsumme sollten Sie vergleichen?

Verwenden Sie die Prüfsumme für genau die heruntergeladene Version, das Betriebssystem, die CPU und das Archivformat. Die [GitHub-Release-Auswahl](/en/posts/2023-09-23-linux-shellscript-github-latest/) wählt eine Asset-URL; das [Temurin-Metadatenbeispiel](/en/posts/2023-10-10-temurin-jdk21-delay/) prüft zusätzlich die Syntax der Prüfsumme. Keines der beiden Beispiele hasht die heruntergeladene Datei. Adoptiums [Anleitung zur Archivinstallation](https://adoptium.net/installation/archives) beschreibt, wie Sie die zugehörige Prüfsumme erhalten.

Beziehen Sie den erwarteten Wert über den vertrauenswürdigen Vertriebskanal des Herausgebers. Einen Hash aus der heruntergeladenen Datei zu berechnen und denselben Wert anschließend als Sollwert zu verwenden, kann einen fehlerhaften Download nicht erkennen. Kann ein Angreifer sowohl die Datei als auch ihre veröffentlichte Prüfsumme ersetzen, belegt eine Übereinstimmung keine Authentizität. Die Signaturprüfung mit einem vertrauenswürdigen Herausgeberschlüssel ist ein separater Schritt außerhalb dieses Beispiels.

## Wie funktioniert die Dateiprüfung?

![Prüfsumme validieren, Datei hashen und Ergebnis vergleichen](/assets/diagrams/technical/de-2026-10-30-verify-sha256-download.svg)

Validieren Sie den erwarteten Wert, öffnen Sie eine unveränderte reguläre Datei im Binärmodus, aktualisieren Sie den Hash blockweise bis EOF und vergleichen Sie. Ungültige Eingaben oder Lesefehler liefern 2; eine Abweichung liefert 1; nur eine Übereinstimmung liefert 0. Das Diagramm fasst die Blockschleife in einem Schritt zusammen. Ändern oder ersetzen Sie die Datei weder während der Prüfung noch danach vor ihrer Verwendung. Dies ist kein Werkzeug für atomare Prüfung und Ausführung.

## Prüfprogramm ohne zusätzliche Pakete ausführen

Verwenden Sie Python 3.11 oder neuer und speichern Sie Folgendes als `verify-sha256.py`. Die folgenden Befehle verwenden eine POSIX-Shell. Das Programm liest lokale Dateien; es lädt sie weder herunter noch entpackt oder startet es sie. Es folgt einem symbolischen Link, wenn dieser auf eine reguläre Datei zeigt. Es akzeptiert einen einzelnen hexadezimalen Wert mit 64 Zeichen, einschließlich Großbuchstaben, statt einer Prüfsummenliste, eines Dateinamens oder einer URL.

### `verify-sha256.py`

```python
import hashlib
from pathlib import Path
import re
import sys


def main(argv):
    if len(argv) != 3 or not re.fullmatch(r"[0-9a-fA-F]{64}", argv[1]):
        print("usage: verify-sha256.py EXPECTED_SHA256 FILE", file=sys.stderr)
        return 2
    path = Path(argv[2])
    try:
        if not path.is_file():
            raise OSError("expected an existing regular file")
        digest = hashlib.sha256()
        with path.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as error:
        print(f"READ ERROR: {error}", file=sys.stderr)
        return 2
    if digest.hexdigest() != argv[1].lower():
        print("MISMATCH", file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
```

`rb` erhält die ursprünglichen Bytes einschließlich der Zeilenenden. Jeder Lesevorgang fordert höchstens 1 MiB an; die Datei wird nicht vollständig geladen. Ungültige Prüfsummen werden vor dem Öffnen des Pfads abgewiesen. Fehlende Pfade, Verzeichnisse und Lesefehler haben gemeinsam den Status 2. Benannte Pipes und Gerätedateien gehören nicht zum Vertrag für reguläre Dateien.

## Übereinstimmung und veränderte Datei reproduzieren

Verwenden Sie ein neues leeres Verzeichnis. Diese Testvorbereitung schreibt `sample.bin` mit den drei Bytes `abc` und `changed.bin` mit `abcd`. Der feste Hash im Befehl gehört nur zu `abc`; er ist keine Prüfsumme eines JDK-Archivs.

### `make-samples.py`

```python
from pathlib import Path

Path("sample.bin").write_bytes(b"abc")
Path("changed.bin").write_bytes(b"abcd")
```

```sh
python3 make-samples.py
expected='ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
python3 verify-sha256.py "$expected" sample.bin
python3 verify-sha256.py "$expected" changed.bin
printf 'exit=%s\n' "$?"
```

Die passende Datei gibt `OK` aus. Die veränderte Datei gibt `MISMATCH` auf stderr aus, und der letzte Befehl gibt `exit=1` aus. Bei `set -e` braucht eine erwartete Abweichung ein ausdrückliches `if` oder einen anderen Zweig zur Fehlerbehandlung; sonst kann die Shell vor der Statusausgabe abbrechen.

| Status | Bedeutung | Nächster Schritt |
| --- | --- | --- |
| 0 | Hash stimmt mit dem angegebenen Sollwert überein | Nur fortfahren, wenn dieser Sollwert aus vertrauenswürdiger Quelle stammt |
| 1 | Hashwerte unterscheiden sich | Diese Datei nicht weiter verwenden; ausgewähltes Asset und Download prüfen |
| 2 | Ungültige Argumente, Prüfsummensyntax oder Fehler beim Lesen der Datei | Eingabe oder Dateizugriff korrigieren und erneut versuchen |

Eine Abweichung allein bestimmt nicht, ob eine Beschädigung, ein falsches Asset oder ein böswilliger Austausch die Ursache ist. Die Prüfung bietet weder Signaturprüfung noch Malware-Scan.
