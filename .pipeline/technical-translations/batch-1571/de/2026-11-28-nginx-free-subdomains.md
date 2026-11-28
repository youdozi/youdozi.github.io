---
{
  "state": "draft",
  "language": "de",
  "translationKey": "2026-11-28-nginx-free-subdomains",
  "title": "Vier kostenlose Subdomain-Dienste für einen Nginx-Server zu Hause",
  "description": "Bei wechselnder IP-Adresse, für ein Entwicklerportfolio und für eine eigene DNS-Zone bieten sich unterschiedliche Dienste an.",
  "sourcePath": "src/content/posts/en/2026-11-28-nginx-free-subdomains.md",
  "sourceSha256": "d11db302c4d9595bd30ea32d7d5c2c2ec680a9c318001ba16e333085dbec5f2e"
}
---

Nginx läuft zu Hause. Welchen Namen sollen Besucher eingeben? Alle vier Dienste vergeben kostenlose Subdomains unter einer Domain des Betreibers. Für den Server und die Erreichbarkeit von außen bist du selbst zuständig.

## Ist der Server von außen erreichbar?

DDNS aktualisiert die IP-Adresse, die DNS zurückliefert. Ob eine Verbindung Nginx erreicht, hängt von Anschluss, Router und Firewall ab. Bei CGNAT kann die Portweiterleitung am Heimrouter allein unzureichend sein. Liegt seine WAN-Adresse im Bereich `100.64.0.0/10`, frag deinen Anbieter nach einer öffentlichen IPv4-Adresse. [RFC 6598](https://www.rfc-editor.org/info/rfc6598/)

## Nach Art der DNS-Verwaltung auswählen

| Dienst | Verwaltung des Namens | Geeignet für |
| --- | --- | --- |
| [Duck DNS](https://www.duckdns.org/spec.jsp) | Ein Update-Client hält `name.duckdns.org` aktuell. Die API kann IPv4 automatisch erkennen. Für ein IPv6-Update gibst du die Adresse ausdrücklich an. | Erste Versuche mit wechselnder öffentlicher IPv4-Adresse. |
| [dynv6](https://dynv6.com/) · [API](https://dynv6.com/docs/apis) | Hostname mit APIs für A- und AAAA-Einträge und das IPv6-Präfix. | IPv6 oder Dual Stack. Es gibt kein Unternehmens-SLA. |
| [is-a.dev](https://github.com/is-a-dev/register#-register) | Stelle einen Pull Request auf GitHub zur Prüfung. Das Team bittet darum, den Antrag selbst zu verfassen. | Entwicklerportfolios. Bei häufigen IP-Wechseln ist DDNS einfacher. |
| [EU.org](https://nic.eu.org/register.html) · [EU.org NS](https://nic.eu.org/top-policy.html) | Richte vor dem Antrag autoritative Nameserver ein. Nach Genehmigung und NS-Delegation verwaltest du A und AAAA in deiner Zone. | Eigene DNS-Verwaltung. Dynamische Updates richtest du gesondert ein. |

## Den gewählten Namen prüfen

![WAN-Adresse prüfen → Update-Verfahren wählen → DNS-Einträge abfragen → Aus einem anderen Netz testen](2026-11-28-nginx-free-subdomains.svg)

Prüfe beim ersten Versuch, ob du eine öffentliche IPv4-Adresse hast. Lass dann einen Duck-DNS-Namen darauf zeigen. Ersetze im Beispiel den Namen und frage mit installiertem dig beide Adresstypen ab. A sollte deine öffentliche Adresse liefern. Veröffentlichst du AAAA, teste auch die IPv6-Verbindung aus einem anderen Netz.

```sh
dig +short name.duckdns.org A
dig +short name.duckdns.org AAAA
```

Der Vergleich beruht auf der Dokumentation der Anbieter. Wir haben weder Konten angelegt noch Namen beantragt.

[Lokale Notiz-App](https://youdozi.github.io/en/posts/2026-11-28-self-hosting-ai-notes/) · [Duck DNS mit Nginx verbinden: Mit KI von DNS bis HTTPS prüfen](https://youdozi.github.io/en/posts/2026-11-28-nginx-dns-https/)
