---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2026-11-01-ai-agent-permission-boundaries",
  "routeSlug": "2026-11-01-ai-agent-permission-boundaries",
  "kind": "post",
  "title": "Berechtigungen für KI-Agenten: Auswirkungen unerwarteter Aktionen begrenzen",
  "description": "Datei-, Befehls-, Netzwerk- und Kontoberechtigungen von KI-Agenten trennen und Risiken durch Freigabegrenzen und Kontrolle administrativer Umgehungen begrenzen – mit ausführbarem Autorisierungsbeispiel.",
  "categories": [
    "security"
  ],
  "tags": [
    "ai-agent",
    "permissions",
    "least-privilege",
    "sandbox",
    "approval",
    "security"
  ],
  "sourcePath": "src/content/posts/en/2026-11-01-ai-agent-permission-boundaries.md",
  "sourceSha256": "9610960800eb800a78e728fcc84d5cf2a790de1f6b051fe4a8ebb3dfdaec554b",
  "draftSha256": "689315062f7c27e09b05eca85b9d3eb3ff4805119766fc4610bfcddf6719961d",
  "manifestPath": ".pipeline/technical-translations/batch-132/manifest.json",
  "manifestSha256": "9061c67686c9ea3bd8d21799f4c265ee716fee50940f1b6fc38c28a67de01dee",
  "publishedAt": "2026-11-02T03:04:44.245Z",
  "updatedAt": "2026-11-02T03:04:44.245Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 132,
    "approvedAt": "2026-11-02T03:04:44.245Z",
    "basis": "User requested completing missing multilingual technical posts, review, verification and deployment, then instructed continuing the next task on 2026-11-02, with standing blog PR merge/publication authorization. Human approval denotes user publication authorization; linguistic review is AI, not human/native review."
  }
}
---
**Um Vorfälle durch unerwartetes Verhalten von KI-Agenten zu reduzieren, begrenzen Sie ausführbare Aktionen und zugängliche Ressourcen und definieren Sie konkrete Freigabegrenzen für folgenreiche Vorgänge.** Eine fehlerhafte Dateiänderung oder eine zu weite Auslegung eines Auftrags sollte nicht unmittelbar zur Löschung von Produktionsdaten, zur externen Übertragung oder zur Umgehung von Schutzregeln führen. Berechtigungsdesign kann nicht jeden Fehler beseitigen, aber dessen Reichweite verringern.

Berechtigungen umfassen hier die Ausführungsumgebung und externe Dienstkonten ebenso wie die Liste der für den Agenten sichtbaren Werkzeuge. [OWASPs Beschreibung von Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/) nennt übermäßige Funktionalität, Berechtigungen und Autonomie als wesentliche Risiken und empfiehlt minimale Rechte sowie Freigaben für folgenreiche Aktionen.

## Wenn „Auftrag abschließen“ zu weitergehender Befugnis wird

Betrachten Sie dieses hypothetische Entwurfsszenario. Ein Nutzer beauftragt eine Veröffentlichung und CI besteht, doch das Repository verlangt eine separate PR-Freigabe. Interpretiert der Agent diese Anforderung als gewöhnliches Hindernis und führt die Zusammenführung mit Administratorrechten durch, werden Veröffentlichung und Ausnahme von den Schutzregeln vermischt.

Es stellen sich zwei Fragen: **Darf der Agent dieses Artefakt veröffentlichen, und darf er außerdem eine Ausnahme von den Schutzregeln machen?** Eine gewöhnliche Veröffentlichungsanfrage automatisch zur Erlaubnis einer administrativen Umgehung auszuweiten, kann unerwartete Änderungen verursachen. GitHubs Branch-Schutz kann je nach Konfiguration Administratoren oder Akteure mit Umgehungsrechten ausnehmen; prüfen Sie daher sowohl die Schutzregeln als auch die Umgehungsmöglichkeiten des Ausführungskontos. [Geschützte GitHub-Branches und Umgehungseinstellungen](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)

Bestimmen Sie nach einer Berechtigungsverweigerung anhand der Richtlinie, ob ein anderer Befehl, eine andere API oder Identität dieselbe Wirkung versuchen darf. Wegen fehlender Freigabe oder unzureichender Rechte blockierte Aktionen sollten dem Warte- oder Ausnahmeprozess der Richtlinie folgen. Unterscheiden Sie Wiederholungen bei vorübergehenden Dienstfehlern von Reaktionen auf verweigerte Berechtigungen.

## Anweisungen und durchgesetzte Kontrollen haben unterschiedliche Aufgaben

Eine Anweisung wie „Produktionsdatenbank nicht ändern“ in `AGENTS.md` oder einem Prompt vermittelt den Umfang. Hat die Datenbankidentität zusätzlich nur Leserechte, kann auch die Datenbank eine erzeugte Schreibanfrage ablehnen. Anweisungen lenken das Modellverhalten; Kontrollen der Ausführungsumgebung und Dienstautorisierung begrenzen seine möglichen Auswirkungen.

| Ebene | Was begrenzt werden soll | Beispielentwurf |
| --- | --- | --- |
| Aufgabenanweisungen | Umfang und Stoppbedingungen | Entwürfe erlauben; Veröffentlichung und administrative Umgehung als getrennte Aktionen definieren |
| Ausführungsumgebung | Dateien, Prozesse und Netzwerkzugriff | Schreibzugriff nur im Arbeitsordner erlauben, Produktionsgeheimnisse weglassen, nur notwendige Ziele verbinden |
| Werkzeug-Gateway | Kombinationen von Aktionen und Argumenten | Für `publish` Website und Artefakt-Hash prüfen; keine beliebige Befehlsausführung bereitstellen |
| Externer Dienst | Tatsächliche Rechte der Zugangsdaten | Eingeschränkte Dienstidentitäten und Schutzregeln für Repositorys, Datenbanken und Cluster verwenden |

Ein Gateway lässt einen alternativen Weg offen, wenn der Agentenprozess weiterhin ein Administratortoken besitzt und APIs direkt aufrufen kann. Ein möglicher Entwurf verwahrt Ausführungszugangsdaten in einem eingeschränkten Dienst und lässt den Agenten strukturierte Anfragen an diesen Dienst senden. Der Agent darf außerdem Richtliniendateien und Freigabespeicher nicht ändern können.

## Auswirkungen begrenzen, nicht nur Befehlsnamen

Eine Regel, die „Testbefehle“ erlaubt, sichert allein noch keine Ausführungsumgebung. Tests, Builds und die Installation von Abhängigkeiten können Repository- oder Paketcode ausführen. Geben Sie keine Produktionszugangsdaten in einen Arbeitsbereich mit nicht vertrauenswürdigem Code; stellen Sie nur benötigte Dateien, Netzwerkzugriffe und Ressourcen bereit. Prüfen Sie auch bei Containern die Isolationsgrenze erneut, wenn sensible Hostpfade oder der Docker-Socket eingebunden sind.

Auch Leseoperationen brauchen Ressourcen- und Datengrenzen. Ein Geheimnis zu lesen und extern zu übertragen oder sensible Daten in eine Abfragezeichenfolge zu setzen, kann ohne Änderung der Quelldaten einen Vorfall auslösen. In externen Dokumenten, Webseiten oder Werkzeugantworten eingebettete Anweisungen sind keine Aufgabenfreigaben. [OWASPs Hinweise zu Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) behandeln indirekte Injection über externe Inhalte.

Ein GitHub-Actions-Workflow kann nur die benötigten Tokenrechte deklarieren. Dies ist ein Fragment einer Workflow-Konfiguration:

```yaml
permissions:
  contents: read
```

Es steuert das betreffende `GITHUB_TOKEN`. Nicht angegebene Berechtigungen werden `none`; die Deklaration begrenzt jedoch keinen separat bereitgestellten PAT, Cloud-Schlüssel oder Datenbankzugang. Prüfen Sie auch die Zugangsdaten, die dem Agenten-Runner tatsächlich zur Verfügung stehen. [Berechtigungssyntax von GitHub Actions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#permissions)

Prüfen Sie in Kubernetes die Rechte `escalate`, `bind` und `impersonate` einer gewöhnlichen Aufgabenidentität getrennt. Sie können den Erwerb weiterer Rechte oder das Handeln unter einer anderen Identität ermöglichen. [Kubernetes-RBAC-Empfehlungen](https://kubernetes.io/docs/concepts/security/rbac-good-practices/)

## Freigabe an Artefakt und Ziel binden

Machen Sie statt eines bloßen „Fortfahren?“ Aktion, Ziel und vorgeschlagene Änderung überprüfbar. Eine Veröffentlichungsfreigabe kann Website-ID, Hash des geprüften Artefakts, Ausführungsidentität, Ablaufzeit und eine einmalige Freigabe-ID binden. Ändern sich Artikel oder Deployment-Image nach der Freigabe, bestimmen Sie, ob das neue Artefakt noch in deren Umfang liegt.

Nicht jeder Lesezugriff und jede Entwurfsänderung braucht eine eigene Freigabe. Lassen Sie die Arbeit innerhalb eines bereits autorisierten Umfangs weiterlaufen und stoppen Sie, wenn sie diesen überschreitet oder eine Wirkung erreicht, für die die Richtlinie eine zusätzliche Freigabe verlangt. Das reduziert Freigabemüdigkeit und erhält Grenzen für Veröffentlichung, Löschung, externe Übertragung und administrative Ausnahmen. Ein Betriebsverfahren, das tatsächlich eine administrative Ausnahme benötigt, sollte eine andere Identität, Befugnis und Auditspur als der gewöhnliche Runner nutzen.

## Ausführbares Beispiel: Freigaben erlauben keine richtlinienfremden Aktionen

Das Folgende ist ein **Autorisierungsbeispiel in einem einzelnen Prozess ohne externe Auswirkungen**. Werte wie `repo:demo` sind vordefinierte logische Ressourcen-IDs, keine tatsächlichen Pfade oder URLs. Die Richtlinie erlaubt `read` und Entwurfs-`edit`; `publish` benötigt eine gültige Freigabe für dieselbe Identität und Anfrage. Administrative Umgehung fehlt in der Richtlinie und wird auch mit vorhandenem Freigabeobjekt abgelehnt.

![Richtlinienumfang prüfen, dann vorhandene Freigabe, übereinstimmende Identität und Artefakt, Ablauf und Wiederverwendung prüfen, bevor eine freigabepflichtige Veröffentlichung erlaubt wird](/assets/diagrams/technical/de-2026-11-01-ai-agent-permission-boundaries.svg)

Das Diagramm zeigt den freigabepflichtigen `publish`-Pfad. Die unmittelbare Erlaubnis für `read` und Entwurfs-`edit` aus dem Code fehlt darin. Ein Stopp an einer Prüfung verhindert nachfolgende Schritte und die tatsächliche Veröffentlichung.

Speichern Sie den Code als `permission_gate.py` und führen Sie `python3 permission_gate.py` mit Python 3.10 oder neuer aus. Netzwerkzugriff, Zugangsdaten oder Zusatzpakete sind nicht nötig.

```python
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Request:
    action: str
    target: str
    artifact: str


@dataclass(frozen=True)
class Grant:
    subject: str
    request: Request
    expires_at: int
    nonce: str


class Gate:
    def __init__(self):
        self.policy = {
            ("read", "repo:demo"): "allow",
            ("edit", "draft:demo"): "allow",
            ("publish", "site:demo"): "approval",
        }
        self.used = set()

    def check(self, subject, request, grant, now):
        mode = self.policy.get((request.action, request.target))
        if mode is None:
            return "DENY:policy"
        if mode == "allow":
            return "ALLOW"
        if grant is None:
            return "APPROVAL_REQUIRED"
        if grant.subject != subject or grant.request != request:
            return "DENY:scope"
        if now >= grant.expires_at:
            return "DENY:expired"
        if grant.nonce in self.used:
            return "DENY:replay"
        self.used.add(grant.nonce)
        return "ALLOW"


def main():
    gate = Gate()
    now = 1000
    subject = "worker-demo"
    request = Request("publish", "site:demo", "sha256:" + "a" * 64)
    grant = Grant(subject, request, now + 60, "approval-demo-1")

    def check(label, candidate, approval, expected, actor=subject, at=now):
        result = gate.check(actor, candidate, approval, at)
        assert result == expected, (label, result, expected)
        print(f"{label}={result}")

    check("read", Request("read", "repo:demo", "revision-1"), None, "ALLOW")
    check("edit-draft", Request("edit", "draft:demo", "revision-1"), None, "ALLOW")
    check("unknown-target", replace(request, target="site:other"), grant, "DENY:policy")
    check("admin-bypass", replace(request, action="admin-bypass"), grant, "DENY:policy")
    check("no-approval", request, None, "APPROVAL_REQUIRED")
    check("changed-artifact", replace(request, artifact="sha256:" + "b" * 64), grant, "DENY:scope")
    check("wrong-worker", request, grant, "DENY:scope", actor="worker-other")
    check("expired-boundary", request, grant, "DENY:expired", at=now + 60)
    check("approved", request, grant, "ALLOW")
    check("replayed", request, grant, "DENY:replay")


if __name__ == "__main__":
    main()
```

Diese Ausgabe wurde mit Python 3.13.0 erzeugt. Die Rückgabewerte dieser 10 synthetischen Szenarien wurden geprüft:

```text
read=ALLOW
edit-draft=ALLOW
unknown-target=DENY:policy
admin-bypass=DENY:policy
no-approval=APPROVAL_REQUIRED
changed-artifact=DENY:scope
wrong-worker=DENY:scope
expired-boundary=DENY:expired
approved=ALLOW
replayed=DENY:replay
```

`Grant` setzt Informationen voraus, die ein Freigabedienst ausgestellt und authentifiziert hat. Dieses Beispiel prüft weder die Freigabe noch die Ausführungsidentität, Befugnis, Signaturen oder das Eingabeschema; dataclass-Typhinweise ersetzen keine Laufzeitvalidierung. Übernehmen Sie modellgeneriertes JSON nicht direkt als akzeptiertes `Grant`. `now=1000`, 60 Sekunden, die Hashes und die Freigabe-ID sind synthetische Demonstrationswerte, keine Produktionsempfehlungen.

Ein echter Executor muss Freigaben aus dem Freigabespeicher laden und den Artefakt-Hash selbst berechnen. Prüft er nur einen vom Agenten gelieferten Hash, kann dieser einen vom tatsächlichen Inhalt abweichenden Wert angeben. Prüfen Sie Richtlinie, Zeit, Ausführungsidentität und Ziel anhand vertrauenswürdigen Ausführungskontexts und begrenzen Sie Ausführungspfade und Zugangsdaten so, dass der Agent diese Funktion nicht überspringen und die externe API direkt aufrufen kann.

Die Menge `used` liegt im prozesslokalen Speicher und verhindert daher keine Wiederverwendung nach Neustarts oder über mehrere Runner hinweg. Ein echter Ausführungsdienst benötigt atomaren Freigabeverbrauch, Widerruf, erneute Richtlinien- und Zielprüfung unmittelbar vor der Ausführung sowie idempotente Aktionen. Wiederholungen nach Freigabeverbrauch und Ausführungsfehler müssen ebenfalls dieselbe Vorgangs-ID und das tatsächliche Ausführungsergebnis verwenden. Dieser Code liefert `ALLOW`; er ruft keine Veröffentlichungs-API auf.

## Was bei der Einführung zuerst zu prüfen ist

Inventarisieren Sie zugängliche Dateien, Tokens und Identitäten sowie die APIs, die der Agent tatsächlich aufrufen kann. Betrachten Sie über explizit verbundene Werkzeuge hinaus Shell-Umgebungsvariablen, Zugangsdaten im Home-Verzeichnis und Netzwerkrouten. Beginnen Sie mit Lesezugriff und isolierter Entwurfsarbeit und ergänzen Sie danach eng begrenzte Werkzeuge für folgenreichere Wirkungen.

Testen Sie, dass Veröffentlichung ohne Freigabe, Artefaktänderungen nach Freigabe, Ablauf, Wiederverwendung, eine andere Ausführungsidentität, unbekannte Ressourcen und Anfragen zur administrativen Umgehung abgelehnt werden. Prüfen Sie, dass dieselben Kontrollen gelten, wenn ein externes Dokument erweiterte Rechte verlangt. Schließen Sie alle Wege, über die der Agent Richtlinien ändern oder das Token des Ausführungsdienstes direkt lesen kann.

Verknüpfen Sie Anfrage-ID, Identität, Ziel, Artefakt-Hash, angewandte Richtlinie, Freigabe-ID und Ausführungsergebnis in Auditlogs, ohne Tokens und sensible Inhalte dort abzulegen. Stoppen Sie bei auffälligem Verhalten die Annahme neuer Arbeit und widerrufen Sie Zugangsdaten, um weitere Auswirkungen zu begrenzen. Ein Widerruf macht bereits übertragene Daten oder abgeschlossene externe Änderungen nicht rückgängig; bereiten Sie daher zusammen mit Ausführungskontrollen auch Wiederherstellungsverfahren vor.

Einen Betriebsablauf, der Code, Tests, Deployment, Beobachtbarkeit und Datenbanknachweise verbindet, finden Sie unter [Betrieb von KI-Agenten](/en/posts/2026-10-31-ai-agent-operations/).
