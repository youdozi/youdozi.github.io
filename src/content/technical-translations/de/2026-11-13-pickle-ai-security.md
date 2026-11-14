---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2026-11-13-pickle-ai-security",
  "routeSlug": "2026-11-13-pickle-ai-security",
  "kind": "post",
  "title": "Wie Pickle AI funktioniert: iPhone-App-Steuerung und Grenzen des Passwortschutzes",
  "description": "Offizielle Quellen und Code zu Pickles Browser, API und Credential Enclave: Wie unterscheiden sich die Schutzgrenzen für OAuth-Token und Vault-Passwörter?",
  "categories": [
    "security"
  ],
  "tags": [
    "pickle-ai",
    "ai-agent",
    "ios",
    "credentials",
    "nitro-enclaves"
  ],
  "sourcePath": "src/content/posts/en/2026-11-13-pickle-ai-security.md",
  "sourceSha256": "4973bca9ea9b81ec4e068b4f530a2b82742c427074c36836639b0c2db1a811e2",
  "draftSha256": "ba97279da8e207d708ffd76d573c651fa6f8cedea631197abaff89745c75739e",
  "manifestPath": ".pipeline/technical-translations/batch-156/manifest.json",
  "manifestSha256": "ed48dc20825daff8725d8eba3418b1ad885276b52c9752ba958f7a1705b24430",
  "publishedAt": "2026-11-14T15:16:43.783Z",
  "updatedAt": "2026-11-14T15:16:43.783Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 158,
    "approvedAt": "2026-11-14T15:16:43.783Z",
    "basis": "User requested all 63 language editions and instructed completed PRs to be merged; AI translation and independent AI review were performed, with no claim of human text review."
  }
}
---

**Die offiziellen Erklärungen zu Pickle AI deuten darauf hin, dass ein separater Browser und verbundene Konten Aufgaben ausführen, statt Bildschirme anderer iPhone-Apps direkt zu bedienen.** Passwörter werden getrennt vom Modell verschlüsselt; die Schutzgrenze für tatsächlich zur Anmeldung genutzte Werte unterscheidet sich jedoch zwischen OAuth und Website-Passwörtern.

Gegenstand ist [Pickle](https://pickle.com/), ein persönlicher KI-Agent von Pickle, Inc. Die Analyse verwendet offizielle Hilfeseiten vom 13. November 2026 und den öffentlichen `credential-enclave`-Quellcode beim **Commit `cff16a343bf5bb7953e5b65df6ab3600107e127d`**. Ich habe die Release-Verifikation des öffentlichen Sicherheitsprogramms selbst ausgeführt; dies ist kein Audit der installierten iOS-App oder des gesamten Produktionsservers.

## Tippt Pickle tatsächlich andere iPhone-Apps an?

Die [Hilfe zu gespeicherten Anmeldungen](https://www.pickle.com/help/connect/save-login) erklärt, dass Pickles Browser vom Telefon getrennt ist und dort gespeicherte Logins nicht direkt nutzen kann. Die [Anleitung zur Aufgabendelegation](https://www.pickle.com/help/tasks/delegate) beschreibt ebenfalls die Arbeit auf Websites in einem echten Browser und deren Fortsetzung nach dem Schließen der App.

Eine ausgeführte Bestellung oder Reservierung allein belegt daher nicht, dass der Bildschirm einer installierten Shopping-App angetippt wurde. Die öffentlichen Unterlagen belegen folgende Wege:

| Weg | Geprüfte Grundlage und Bedeutung |
| --- | --- |
| Separater Browser | Anmeldung auf Websites und Ausfüllen von Formularen, getrennt von App-Bildschirmen auf dem Telefon |
| API verbundener Konten | Der öffentliche `forward`-Code fügt zulässigen Anbieter-API-Anfragen Zugangsdaten hinzu |
| Telefonanruf | Die offizielle Anleitung beschreibt Anrufe für Aufgaben, die nicht im Web erledigt werden können |

Auch Apples Beschreibung der [Sandbox für Drittanbieter-Apps](https://support.apple.com/en-gb/guide/security/sec15bfe098e/web) beschränkt den Zugriff auf andere Informationen auf die von iOS angebotenen Dienste. Das schließt nicht jede Automatisierung aus; ich habe jedoch keinen Beleg gefunden, dass Pickle die Sandbox umgeht, um andere Apps zu steuern.

Die verfügbaren Materialien zeigen weder, welche DOM-Werkzeuge oder Bilderkennungsmodelle Pickles Browser nutzt, noch welcher Ausführungsweg für jede Aufgabe gewählt wird. Das hier beschriebene Funktionsprinzip verbindet offizielle Angaben mit dem öffentlichen Zugangsdatenpfad zu einer Analyse.

## Wie ist eine Anmeldung möglich, ohne der KI das Passwort zu geben?

Auch wenn ein Modell den Passwort-String nie direkt ausgibt, kann eine separate Ausführungskomponente den benötigten Wert erhalten und in ein Login-Formular einsetzen. Pickles [Datenschutzhinweis](https://www.pickle.com/privacy) sagt, dass Passwort- und Kartenwerte auf dem Gerät verschlüsselt und vor den dem Modell übergebenen Ergebnissen verborgen werden. Die technische Grenze dieser Aussage muss mit dem öffentlichen Code verglichen werden.

![Bei der Einrichtung erzeugt das iPhone Schlüssel und delegiert einen verschlüsselten Benutzerschlüssel an eine geprüfte Enclave. Bei der Nutzung werden aktive Delegation und verschlüsselter Datensatz geprüft, die Protokollspeicherung bestätigt und zwei Wege unterschieden. OAuth-Token werden im Knoten für APIs genutzt; Vault-Passwörter und Kartenwerte gelangen in einer release-Antwort im Klartext zum Worker für ein Webformular. Die spätere Maskierung ist eine eigene Grenze.](/assets/diagrams/technical/de-2026-11-13-pickle-ai-security.svg)

Oben zeigt die Grafik die vorherige Schlüsselübergabe bei der Einrichtung, unten die Verwendung von Zugangsdaten während gültiger Delegation. Sie bedeutet nicht, dass das Telefon bei jeder Anmeldung einen neuen Schlüssel senden muss. Die Grafik bildet auch nicht alle Implementierungsdetails der Ausführungskomponente ab.

### Geräteschlüssel und verschlüsselte Datensätze

Das [öffentliche Protokoll](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/docs/protocol.md#3-keys) legt fest, dass ein auf dem Gerät erzeugter Master-Schlüssel im iCloud Keychain liegt und getrennte Schlüssel für Signatur, Protokollentschlüsselung und Zugangsdaten abgeleitet werden. Gespeicherte Datensätze werden mit ChaCha20-Poly1305 verschlüsselt; Kontext wie Konto und Datensatztyp wird in die Authentifizierung eingebunden.

Das Gerät prüft die Attestierung und den öffentlichen Schlüssel des Knotens und delegiert dann den verschlüsselten **abgeleiteten Benutzerschlüssel** an diesen Knoten. Remote Attestation prüft, zu welcher gemessenen Ausführungsumgebung ein öffentlicher Schlüssel gehört. [AWS Nitro Enclaves](https://docs.aws.amazon.com/enclaves/latest/user/) isolieren Speicher vom übergeordneten Server und bieten weder direktes externes Netzwerk noch dauerhaften Speicher. Ein Pickle-Knoten kommuniziert über den Host als Vermittler; dadurch erhält der Host nicht automatisch Entschlüsselungsrechte.

Der delegierte Benutzerschlüssel wird zeitlich begrenzt im Knotenspeicher verwendet. Die [öffentliche Architekturbeschreibung](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/README.md#structure) nennt höchstens 30 Tage Delegationsdauer. Geräte-Keychain und Nitro Enclave auf dem Server sind unterschiedliche Schutzschichten.

### OAuth-Token bleiben bei der Nutzung im Knoten

Der [API-Weiterleitungscode](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/enclave/src/api/forward.rs) prüft eine aktive Delegation, öffnet den OAuth-Datensatz und bereitet eine zulässige Anbieteranfrage vor. Nach bestätigter Speicherung des Nutzungsprotokolls führt er die Anfrage aus. Dieser Pfad erstellt eine authentifizierte Anfrage, statt das Token dem Modell zu übergeben.

**Ein Token zu verbergen und die mit ihm gelesenen Daten zu verbergen, sind unterschiedliche Dinge.** Die [Egress-Richtlinie](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/docs/egress-policy.md) behandelt die Rückgabe von Anbieterantworten in den Betriebsbereich gesondert. Wer Leserechte für E-Mails erteilt, muss unabhängig vom Token-Schutz berücksichtigen, dass das Modell deren Inhalte verarbeiten kann.

### Bei Website-Passwörtern ändert sich nach release die Grenze

Der [Vault-Code](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/enclave/src/vault.rs) definiert Typen, die Passwort-, Karten- und TOTP-Werte für eine Ausfuhrantwort auswählen. Der [release-Handler](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/enclave/src/api/release.rs) serialisiert und sendet Werte nach bestätigter Protokollspeicherung. **Dabei verlassen Passwörter und Kartenwerte den Knoten als Klartext, den der betriebliche Worker verwenden kann.** Bei TOTP wird statt des Seeds der berechnete Einmalcode ausgegeben.

Die `origin`-Prüfung im öffentlichen Code prüft nur das Format eines HTTPS-Origin. Ein Kommentar weist die Entscheidung, ob die Adresse zur gespeicherten Login-Site passt, der aufrufenden Seite zu. Website-Beschränkungen und die Maskierung von Modellergebnissen lassen sich daher nicht allein mit dem Enclave-Code beweisen.

Dies ist kein Beleg für einen tatsächlichen Datenabfluss. **Vor Modelleingaben verbergen**, **verschlüsselt speichern** und **Klartext im Worker-Speicher verwenden** sind jedoch unterschiedliche Sicherheitseigenschaften. Die Aussage „Die KI erhält das Passwort nicht“ darf nicht zu „Ein entschlüsseltes Passwort verlässt den geschützten Bereich nie“ ausgeweitet werden.

## Was garantiert das Nutzungsprotokoll?

Die [offizielle Anleitung zum Aktivitätsverlauf](https://pickle.com/help/privacy/activity) erklärt, dass der Datensatz zuerst gespeichert und bei fehlgeschlagener Speicherung keine Zugangsdaten verwendet werden. Auch der öffentliche API-Code zeigt Nutzung oder Freigabe nach bestätigter Protokollspeicherung. Verschlüsselte Datensätze, Signaturen und Verknüpfungen sollen Änderungen oder Auslassungen erkennbar machen.

Ein Protokoll garantiert weder, dass die Person diese Aufgabe beabsichtigte, noch dass sie auf der externen Website erfolgreich war. Beispielsweise kann die eigentliche Anfrage nach dem Speichern scheitern. Zustimmung vor einer Zahlung und erneute Prüfung des Betrags sind Ausführungsregeln der [offiziellen Dienstbeschreibung](https://pickle.com/en), keine automatischen Folgen der Zugangsdatenverschlüsselung.

Wer auch den TOTP-Seed delegiert, ermöglicht dem Agenten die Erzeugung von Codes. Die [Login-Hilfe](https://www.pickle.com/help/connect/save-login) beschreibt dies als Komfortfunktion; sie unterscheidet sich davon, dass die Person bei jeder Aufgabe einen zweiten Faktor separat bestätigt. Der Delegationsumfang ist daher weiter als bei der alleinigen Übergabe eines Passworts.

## Den Nachweis des öffentlichen Sicherheitsprogramms prüfen

Die [secure-program-Dokumentation](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/secure-program/README.md) veröffentlicht auch das geräteseitige Sicherheitsprogramm und ein Werkzeug zur Prüfung von Release-Signatur und Transparenzlog-Nachweis. Das Beispiel prüft die **Übereinstimmung einer öffentlichen Datei mit ihrem Release-Nachweis**. Es verbindet sich nicht mit einem Produktionsknoten und verwendet keine echten Passwörter.

![Das öffentliche Programm-JS und der Release-Nachweis werden dem offiziellen Prüfwerkzeug übergeben. Es prüft Datei-Hash, Signatur und Transparenzlog-Nachweis. Original v42 liefert Exit-Code 0; eine um ein Byte ergänzte Datei liefert source_hash-Fehler und Code 1. Produktionsserver und installierte App werden separat geprüft.](/assets/diagrams/technical/de-2026-11-13-pickle-ai-security-architecture.svg)

Git, curl, Rustup und native Build-Werkzeuge sind erforderlich; das Herunterladen von Quellcode und Rust-Abhängigkeiten benötigt Netzwerkzugriff. Das Prüfwerkzeug wurde auf **macOS arm64 mit Rust 1.100.0** aus dem unten fixierten Commit gebaut. Das Repository fixiert Werkzeugversion 1.98.1; hier wählt `+1.100.0` die Ausführungsversion ausdrücklich.

### `verify-example.sh`

```bash
# macOS·Linux 셸, Git·curl·Rustup 및 네이티브 빌드 도구가 필요합니다.
# 새 작업 폴더에서 실행합니다. 아래 검증은 계정 로그인이나 실제 비밀번호를 사용하지 않습니다.
git clone https://github.com/pickle-com/credential-enclave.git
cd credential-enclave
git checkout cff16a343bf5bb7953e5b65df6ab3600107e127d
rustup toolchain install 1.100.0 --profile minimal
cargo +1.100.0 build --locked -p credential-enclave-verify
curl --fail --location \
  https://github.com/pickle-com/credential-enclave/releases/download/secure-program-v42/secure-program.release.json \
  --output secure-program.release.json
./target/debug/credential-enclave-verify program \
  --source secure-program/secure-program.js \
  --release secure-program.release.json
```

Die Originaldatei lieferte Exit-Code 0 und folgende Ausgabe:

```text
program release secure-program-v42: version 42, sha256 31e7fa7fb51f87781313b1f97b60ae3c7b69ff8f2fbcee7de12b7a0ed034d8e8, log index 3761959022: ok
```

Prüfen Sie auch, ob eine veränderte Datei abgelehnt wird. Führen Sie die folgenden Befehle im selben Repository-Ordner aus.

### `tamper-example.sh`

```bash
cp secure-program/secure-program.js changed-program.js
printf '\n' >> changed-program.js
./target/debug/credential-enclave-verify program \
  --source changed-program.js \
  --release secure-program.release.json
echo $?
```

Die um ein Zeilenumbruch-Byte ergänzte Datei wurde wegen eines `source_hash`-Unterschieds abgelehnt und endete mit Code 1. Dieses Ergebnis betrifft den Release-Nachweis des öffentlichen Programms. Ich habe weder geprüft, ob die in der tatsächlichen App angezeigte Version und der Hash übereinstimmen, noch die Messung der Produktions-Enclave per Remote Attestation verifiziert.

## Welche Bedingungen bleiben für die Sicherheitsbewertung?

Die [Grenzen des öffentlichen Repositorys](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/README.md#what-it-does-not-guarantee) nennen Vertrauensannahmen wie Ehrlichkeit der App, Anbieter-API-Verträge, Release-Schlüssel und Logs. Auch bei einem öffentlichen Sicherheitsprogramm bleibt separat zu prüfen, ob das gesamte iOS-App-Binärprogramm es unverändert ausführt. Dass ein Knoten Delegationen an eine spätere Version übertragen kann, bedeutet ebenfalls nicht, dass die Schutzwirkung einer Version dauerhaft fixiert ist.

Auch die [Update-Grenzen](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/secure-program/README.md#limits) des geräteseitigen Sicherheitsprogramms sind wichtig. Laut Dokumentation kann neuer Code ohne vorherige Wartezeit geladen werden, wenn der Betreiber ihn signiert, ins öffentliche Log einträgt und die Ladebedingungen erfüllt. **Die Release-Prüfung bestätigt die Übereinstimmung mit der veröffentlichten signierten Datei, garantiert aber nicht die Harmlosigkeit des Codes.** Für spätere Versionen bleibt Vertrauen in den Betreiber nötig. Dies behauptet oder beobachtet keine tatsächlich bösartige Veröffentlichung.

| Prüfgegenstand | Frage für die Entscheidung |
| --- | --- |
| Verbundene Konten | Welche Lese-/Schreibrechte wurden erlaubt und lassen sie sich beim Anbieter widerrufen? |
| Vault und TOTP | Muss neben Passwörtern auch die Erzeugung von Einmalcodes delegiert werden? |
| Zahlungen und Reservierungen | Können Bedingungen und Betrag vor der Ausführung und das Ergebnis danach geprüft werden? |
| Sicherheitsprogramm und Knoten | Stimmen App-Version und Hash, öffentliches Release und tatsächliche Knotenattestierung überein? |
| Gesprächs- und Kontodaten | Welche Inhalte verarbeitet das Modell trotz verborgener Zugangsdaten? |

Der Kern von Pickles Sicherheitsentwurf ist, **welche Schlüssel wem übergeben werden und an welcher Grenze welcher Wert entschlüsselt und verwendet wird**. Öffentlicher Code liefert Hinweise, um diese Grenzen zu prüfen. Für Nutzerinnen und Nutzer ist ein Ausgangspunkt, tatsächliche iPhone-App-Steuerung von delegiertem Kontozugriff zu unterscheiden, nur nötige Berechtigungen zu verbinden und Verlauf sowie Ausführungsergebnisse gemeinsam zu prüfen.
