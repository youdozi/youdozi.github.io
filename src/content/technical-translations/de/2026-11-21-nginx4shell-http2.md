---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2026-11-21-nginx4shell-http2",
  "routeSlug": "2026-11-21-nginx4shell-http2",
  "kind": "post",
  "title": "Nginx4Shell-Leitfaden — betroffene NGINX-Versionen und Patches für HTTP/2",
  "description": "Betroffene Konfigurationen, korrigierte Versionen und vorläufige Maßnahmen für die NGINX-HTTP/2-Schwachstellen CVE-2026-123007 und CVE-2026-123633. Ein Python-Beispiel hilft beim Priorisieren der Patches.",
  "categories": [
    "security"
  ],
  "tags": [
    "nginx",
    "http2",
    "patch-management",
    "cve-2026-123007",
    "cve-2026-123633"
  ],
  "sourcePath": "src/content/posts/en/2026-11-21-nginx4shell-http2.md",
  "sourceSha256": "51daac7a022b582074f762f0ce0c07d617f4af8535152688b060235117af16c2",
  "draftSha256": "d365220cd7f6d4657af832527322662639fe542b32958ac809c94cea6d24411f",
  "manifestPath": ".pipeline/technical-translations/batch-175/manifest.json",
  "manifestSha256": "de1d6420b28e3a41bd670b52f3db93c0a08645e7821632b38b9c35d9f9d8517f",
  "publishedAt": "2026-11-21T00:38:31.366Z",
  "updatedAt": "2026-11-21T00:38:31.366Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 175,
    "approvedAt": "2026-11-21T00:38:31.366Z",
    "basis": "The site owner explicitly asked to publish the Nginx4Shell guide in the supported languages. This records authorization to publish these editions."
  }
}
---

**Prüfen Sie zuerst, welche NGINX-Listener HTTP/2 annehmen.** Die am 18. November 2026 veröffentlichten Schwachstellen CVE-2026-123007 und CVE-2026-123633 können bei der Verarbeitung von HTTP/2 Speicher beschädigen. Unter bestimmten Bedingungen kann ein Worker abstürzen oder fremder Code aus der Ferne mit den Rechten des Workers ausgeführt werden. Die korrigierten Releases von NGINX Open Source sind stable **1.30.7** und mainline **1.31.9**. Für Distributionspakete, NGINX Plus und Ingress-Produkte gelten die korrigierten Versionen des jeweiligen Anbieters. [NGINX-Sicherheitshinweise](https://nginx.org/en/security_advisories.html) · [F5-Sicherheitsupdate vom 18. November](https://my.f5.com/s/article/K000164058)

## Welche Installationen sind betroffen?

**Nginx4Shell** dient hier als Suchbegriff. Erfassen Sie beide CVE-Nummern einzeln in Änderungstickets und im Inventar, damit sich Sicherheitshinweise und Patchstand pro Produkt eindeutig zuordnen lassen.

| CVE | Bedingungen und Auswirkungen | Betroffene Versionen von NGINX Open Source |
| --- | --- | --- |
| CVE-2026-123007 | Bei der Verarbeitung von HTTP/2-Verkehr von Clients kann NGINX Speicher beschädigen. Prüfen Sie auch Server, die nur statische Inhalte ausliefern, sofern dort HTTP/2 aktiviert ist. | 1.9.5–1.30.6 und 1.31.0–1.31.8 |
| CVE-2026-123633 | Wenn NGINX HTTP/2-Anfragen von Clients an einen Upstream weiterleitet, kann es unter bestimmten Bedingungen auf bereits freigegebenen Speicher zugreifen. Prüfen Sie zuerst Reverse-Proxys mit HTTP/2. | 1.19.7–1.30.6 und 1.31.0–1.31.8 |

Die Stable-Version 1.30.7 behebt beide Schwachstellen. Trotz der höheren Versionsnummer gegenüber 1.30.7 ist **1.31.8 weiterhin betroffen**. Dieses Update enthält auch Korrekturen für HTTP/3, den DNS-Resolver und den Mail-Proxy. Bereiten Sie den Patch weiter vor, auch wenn Sie HTTP/2 vorübergehend anders konfigurieren. [NGINX-Veröffentlichungen](https://nginx.org/news.html) · [F5 CVE-2026-123007](https://my.f5.com/s/article/K000163926) · [F5 CVE-2026-123633](https://my.f5.com/s/article/K000163928) · [CERT-EU-Sicherheitshinweis](https://cert.europa.eu/publications/security-advisories/2026-022)

## Das laufende Produkt und den HTTP/2-Pfad prüfen

1. **Ermitteln Sie die Herkunft der laufenden Binärdatei.** Prüfen Sie bei einer VM die ausführbare Datei und das Paket des Dienstes. Prüfen Sie bei einem Container das tatsächlich laufende Image und dessen Digest. Mit `nginx -V` sehen Sie in der betreffenden Umgebung Version und Build-Optionen. Distributionen wie Ubuntu 24.04 LTS übernehmen Korrekturen in bestehende Versionen. Laut Ubuntu ist `1.24.0-2ubuntu7.20` das korrigierte Paket für dieses Release. [NGINX-Kommandozeilenoptionen](https://nginx.org/en/docs/switches.html) · [Ubuntu USN-9159-1](https://ubuntu.com/security/notices/USN-9159-1)
2. **Prüfen Sie die Verbindung vom Client oder vorgeschalteten Proxy zu NGINX.** Der Browser kann HTTP/2 zum CDN verwenden, während das CDN den NGINX-Ursprungsserver über ein anderes Protokoll erreicht. Prüfen Sie die tatsächlich verwendete Konfiguration mit `nginx -T` und achten Sie auf die Blöcke `http` und `server`, eingebundene Dateien und die verwendete Syntax. Die vollständige Konfiguration kann interne Adressen und Geheimnisse enthalten. Prüfen Sie sie in einer dafür freigegebenen Umgebung. [NGINX-Dokumentation zum HTTP/2-Modul](https://nginx.org/en/docs/http/ngx_http_v2_module.html)
3. **Patchen Sie zuerst betroffene Instanzen, die externe Anfragen annehmen.** Prüfen Sie nach dem Deployment, ob die Prozesse mit der neuen Binärdatei oder dem neuen Image laufen. Führen Sie `nginx -t` aus und prüfen Sie normale HTTP-Anfragen, die Verfügbarkeit der Upstreams, Fehlerraten und Worker-Neustarts. Suchen Sie im Cluster nach Replikaten, die noch mit dem alten Image laufen. [CERT-EU-Sicherheitshinweis](https://cert.europa.eu/publications/security-advisories/2026-022)

Wenn Sie nicht sofort aktualisieren können, lässt sich das Risiko für beide CVEs senken, indem Sie HTTP/2 an betroffenen Listenern deaktivieren. In der aktuellen Syntax verwenden Sie `http2 off;`. In der älteren Syntax entfernen Sie die Option `http2` aus `listen`. Prüfen Sie vor der Änderung, welche Pfade von HTTP/2 abhängen, etwa gRPC. Prüfen Sie danach echte Verbindungen zu diesen Listenern und normale Dienstanfragen. [NGINX-Dokumentation zur HTTP/2-Konfiguration](https://nginx.org/en/docs/http/ngx_http_v2_module.html) · [Red-Hat-Leitfaden zur Risikominderung](https://access.redhat.com/security/vulnerabilities/RHSB-2026-019)

## Übung — aus Prüfergebnissen Patch-Prioritäten ableiten

Das Beispiel verarbeitet **Produktherkunft, Version und HTTP/2-Status**, die das Betriebsteam geprüft hat. Es läuft mit Python 3.10 oder neuer und verwendet nur die Standardbibliothek. Anhand der zuvor erhobenen Angaben lassen sich Patches priorisieren.

![Geben Sie Produktherkunft und Version ein. Bei Distributionspaketen und Anbieterprodukten gilt der Hinweis des Anbieters. Liegt die Originalversion von NGINX im betroffenen Bereich, bestimmt der HTTP/2-Status, ob zuerst gepatcht oder die Konfiguration weiter geprüft wird.](/assets/diagrams/technical/de-2026-11-21-nginx4shell-http2.svg)

Speichern Sie das Skript als `nginx_http2_triage.py`. Wählen Sie `upstream` nur für Originalversionen von NGINX Open Source, die das NGINX-Projekt veröffentlicht. Verwenden Sie `vendor` für Pakete mit zurückportierten Korrekturen oder für Anbieter-Images. Setzen Sie die jeweilige Eingabe auf `unknown`, wenn Produktherkunft oder Listener-Konfiguration noch nicht geklärt sind.

```python
import argparse
import re


def upstream_version(value: str) -> tuple[int, int, int]:
    if not re.fullmatch(r"[0-9]{1,4}\.[0-9]{1,4}\.[0-9]{1,4}", value):
        raise argparse.ArgumentTypeError("use an upstream version such as 1.30.7")
    major, minor, patch = map(int, value.split("."))
    return major, minor, patch


def triage(origin: str, value: str, http2: str) -> str:
    if origin != "upstream":
        return "CHECK_VENDOR_ADVISORY"

    version = upstream_version(value)
    if version[0] != 1 or version > (1, 31, 9):
        return "CHECK_CURRENT_ADVISORY"
    if (1, 30, 7) <= version < (1, 31, 0) or version == (1, 31, 9):
        return "UPSTREAM_FIX_VERSION"

    affected = [
        cve
        for cve, first_version in (
            ("CVE-2026-123007", (1, 9, 5)),
            ("CVE-2026-123633", (1, 19, 7)),
        )
        if version >= first_version
    ]
    if not affected:
        return "OUTSIDE_LISTED_RANGES"

    action = {
        "on": "PRIORITIZE_PATCH",
        "off": "PATCH_STILL_REQUIRED",
        "unknown": "VERIFY_HTTP2_AND_PATCH",
    }[http2]
    return f"{action} {' '.join(affected)}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("origin", choices=("upstream", "vendor", "unknown"))
    parser.add_argument("version")
    parser.add_argument("http2", choices=("on", "off", "unknown"))
    args = parser.parse_args()
    try:
        print(triage(args.origin, args.version, args.http2))
    except argparse.ArgumentTypeError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
```

```bash
python3 nginx_http2_triage.py upstream 1.31.8 on
python3 nginx_http2_triage.py upstream 1.30.7 on
python3 nginx_http2_triage.py upstream 1.19.6 unknown
python3 nginx_http2_triage.py vendor 1.24.0-2ubuntu7.20 on
```

Unter Python 3.13.0 ergaben diese Befehle die folgende Ausgabe.

```text
PRIORITIZE_PATCH CVE-2026-123007 CVE-2026-123633
UPSTREAM_FIX_VERSION
VERIFY_HTTP2_AND_PATCH CVE-2026-123007
CHECK_VENDOR_ADVISORY
```

Die CVE-Liste zeigt, **welche Schwachstellen laut Versionsnummer infrage kommen**. Ob die Upstream-Bedingung für CVE-2026-123633 zutrifft, klären Sie anhand der tatsächlichen Listener-Konfiguration. Das Beispiel stuft Eingaben gemäß den veröffentlichten Versionsbereichen ein. Die Produktionskonfiguration und den Patchstand prüfen Sie separat.
