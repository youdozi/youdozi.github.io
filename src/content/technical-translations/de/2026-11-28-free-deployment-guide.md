---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2026-11-28-free-deployment-guide",
  "routeSlug": "2026-11-28-free-deployment-guide",
  "kind": "post",
  "title": "Kostenloses Hosting für statische Websites, Backend-APIs und PostgreSQL",
  "description": "Build-Limits, der erste Aufruf nach einer Pause und die Lebensdauer von Datenbanken helfen bei der Wahl des Hostings für Blogs, Notiz-Apps und Demos.",
  "categories": [
    "tips"
  ],
  "tags": [
    "deployment",
    "hosting",
    "postgresql"
  ],
  "sourcePath": "src/content/posts/en/2026-11-28-free-deployment-guide.md",
  "sourceSha256": "0557a16ab0634eaf65f92ae9f1818ab52b9bcad87cf30fa8bfe95490ac381740",
  "draftSha256": "587c724eaf5ca1a50ae10e261f63e69e011084b0e6f2daffe9dfcafb5c6b94de",
  "manifestPath": ".pipeline/technical-translations/batch-160/manifest.json",
  "manifestSha256": "16c6a6c4c3926f9d0ba97bc36143abd1dc3c54cc5ebeb38641906ae5536beaa6",
  "publishedAt": "2026-11-28T07:59:07.913Z",
  "updatedAt": "2026-11-28T07:59:07.913Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 230,
    "approvedAt": "2026-11-28T07:59:07.913Z",
    "basis": "Explicit item 160 approval to publish the free deployment comparison in all nine site languages."
  }
}
---

Ein Blog oder Portfolio lässt sich auf **GitHub Pages oder Cloudflare Pages** veröffentlichen. Soll die Anwendung auch Notizen speichern, kann die API auf **Cloudflare Workers oder Render** laufen und PostgreSQL auf **Neon oder Supabase** die Daten speichern. Für eine Aufgabe oder Demo mit festem Enddatum kommt auch Render Postgres mit einer Laufzeit von 30 Tagen infrage.

Bei kostenlosen Tarifen lohnt sich der Blick auf das Verhalten bei Inaktivität und beim Erreichen eines Limits. Ein statischer Hoster kann neue Builds blockieren. Eine API kann nach einer Pause länger für die erste Antwort brauchen. Manche Datenbanken wachen bei der nächsten Abfrage auf, andere muss man im Dashboard wieder aktivieren.

*Grundlage sind die offiziellen Dokumentationen und Preislisten vom 28. November 2026. Die Konfigurationen sind Beispiele. Wir haben keine Konten angelegt, Beispiele bereitgestellt oder Antwortzeiten gemessen.*

## Bei statischen Websites zählt das Build-Ergebnis

Entstehen die Seiten schon beim Build, wie bei einem Astro-Blog oder HTML-Portfolio, genügt statisches Hosting. Für die Wahl sind Dateigröße, Build-Häufigkeit und Verwendungszweck entscheidend.

| <span style="display:inline-block;min-width:13ch">Dienst</span> | <span style="display:inline-block;min-width:18ch">Geeignete Projekte</span> | <span style="display:inline-block;min-width:28ch">Bedingungen im kostenlosen Tarif</span> |
| --- | --- | --- |
| GitHub Pages | Blogs, Projektdokumentation und Portfolios in öffentlichen Repositorys | Die veröffentlichte Website darf bis zu 1 GB groß sein. Für die Bandbreite gilt ein weiches Limit von 100 GB pro Monat. Für Websites, die vorrangig dem Betrieb eines Onlinehandels oder der Bereitstellung kommerzieller SaaS dienen, gelten Nutzungsbeschränkungen. [Limits von GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits) |
| Cloudflare Pages | Statische Astro- oder Vite-Sites, Projekte mit Vorschau pro Branch | 500 Builds pro Monat, 1 Build gleichzeitig, höchstens 25 MiB pro Datei. Für Zugriffe auf statische Dateien ohne Aufruf von Functions gibt es kein Anfragelimit. [Pages-Limits](https://developers.cloudflare.com/pages/platform/limits/) · [Abrechnung für statische Dateien und Functions](https://developers.cloudflare.com/pages/functions/pricing/) |
| Vercel Hobby | Private, nichtkommerzielle Next.js-Projekte | Statische Seiten und Functions lassen sich im selben Projekt bereitstellen. Zu prüfen sind die zulässige Nutzung von Hobby und der Verbrauch der Functions. [Hobby-Tarif](https://vercel.com/docs/plans/hobby) · [Fair-Use-Richtlinien](https://vercel.com/docs/limits/fair-use-guidelines) · [Preise von Vercel](https://vercel.com/pricing) |

Wer Beiträge wie in diesem Blog vorab baut, kann mit GitHub Pages einsteigen. Wie wir den Build von der Veröffentlichung getrennt haben, beschreibt ein früherer Beitrag. [Von der automatischen Veröffentlichung mit Jekyll zur Prüfung von Entwurfs-PRs mit Astro](../2026-04-07-jekyll-github-actions-content-pipeline/)

## Wie soll die Backend-API laufen?

| <span style="display:inline-block;min-width:13ch">Dienst</span> | <span style="display:inline-block;min-width:18ch">Geeignete APIs</span> | <span style="display:inline-block;min-width:28ch">Bedingungen im kostenlosen Tarif</span> |
| --- | --- | --- |
| Cloudflare Workers | Schlanke HTTP-APIs, die Eingaben prüfen, Daten abfragen und JSON zurückgeben | 100.000 Anfragen pro Tag und 10 ms CPU-Zeit pro Anfrage. Gezählt wird die Zeit der Codeausführung ohne Wartezeiten auf Netzwerkantworten. Pages Functions nutzen dasselbe kostenlose Anfragekontingent. [Workers-Limits](https://developers.cloudflare.com/workers/platform/limits/) · [Preise für Pages Functions](https://developers.cloudflare.com/pages/functions/pricing/) |
| Render Free Web Service | Demos mit einem HTTP-Serverprozess, etwa mit FastAPI oder Express | Nach 15 Minuten ohne eingehenden Verkehr stoppt der Dienst. Die nächste Anfrage startet ihn erneut. Laut Render dauert das etwa eine Minute. Jeder Workspace erhält monatlich 750 kostenlose Instanzstunden. Lokale Dateiänderungen gehen bei Neustart, erneutem Deployment oder Wechsel in den Ruhezustand verloren. [Kostenloses Hosting bei Render](https://render.com/docs/free) |

Was passiert mit der Python-Notiz-App aus dem früheren Beitrag auf Render? Selbst wenn `GET /health` erfolgreich antwortet, können Notizen in einer lokalen SQLite-Datei nach einer Ruhephase mit anschließendem Neustart verschwunden sein. Für die dauerhafte Speicherung empfiehlt sich eine externe PostgreSQL-Datenbank. Nach dem Neustart sollte dieselbe Notiz wieder abrufbar sein. [Die Notiz-App selbst hosten](../2026-11-28-self-hosting-ai-notes/) · [Dateisystem bei Render](https://render.com/docs/free#local-files-lost-on-redeploy)

## Bei PostgreSQL auf Speicherplatz und Ruhephasen achten

| <span style="display:inline-block;min-width:13ch">Dienst</span> | <span style="display:inline-block;min-width:18ch">Kostenlos enthalten</span> | <span style="display:inline-block;min-width:28ch">Folgen einer Nutzungspause</span> |
| --- | --- | --- |
| Neon Free | 1 GB PostgreSQL-Speicher und monatlich 100 CU-Stunden Rechenleistung pro Projekt | Nach 5 Minuten ohne Aktivität stoppt die Recheninstanz und startet bei der nächsten Abfrage automatisch. Ist das monatliche Rechenkontingent erschöpft, bleibt sie bis zum nächsten Abrechnungszeitraum oder einem Upgrade angehalten. [Preise von Neon](https://neon.com/pricing) |
| Supabase Free | 500 MB Datenbankspeicher pro Projekt sowie verwaltetes PostgreSQL, Auth und die Data API | Bei geringer Datenbankaktivität über 7 Tage kann das Projekt pausiert werden. Im Dashboard lässt es sich wieder aktivieren. [Preise von Supabase](https://supabase.com/pricing) · [Projektpausen](https://supabase.com/docs/guides/platform/free-project-pausing) |
| Render Free Postgres | 1 kostenlose Datenbank pro Workspace mit 1 GB Speicher | Die Datenbank läuft unabhängig von ihrer Nutzung 30 Tage nach der Erstellung ab. Ohne Upgrade innerhalb von 14 Tagen nach Ablauf löscht Render die Daten. [Kostenloses PostgreSQL bei Render](https://render.com/docs/free#free-postgres) |

Wer einen eigenen API-Server betreiben und direkt SQL schreiben will, kann zuerst Neon prüfen. Für Projekte, die zusätzlich eine Anmeldung und eine API für Datenabfragen benötigen, bietet sich Supabase an. Bei Aufrufen der Supabase Data API aus dem Browser kommt ein öffentlicher Schlüssel zum Einsatz. Richtlinien für Row-Level Security (RLS) legen fest, welche Zeilen die jeweiligen Nutzer lesen und schreiben dürfen. Die Datenbank-Verbindungszeichenfolge und geheime Administratorschlüssel gehören auf den Server. [API-Schlüssel von Supabase](https://supabase.com/docs/guides/getting-started/api-keys) · [Row-Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security)

## Passende Kombinationen je nach Projekt

![Oberfläche im Browser · Cloudflare Pages → API für Notizen · Workers → Gespeicherte Notizen · Neon PostgreSQL](/assets/diagrams/technical/de-2026-11-28-free-deployment-guide.svg)

- **Technisches Blog oder Dokumentationsseite.** Nur das Build-Ergebnis auf GitHub Pages oder Cloudflare Pages veröffentlichen.
- **Schlanke Notiz-App.** Die Oberfläche auf Cloudflare Pages, die API auf Workers und die Daten auf Neon unterbringen. Nach einer längeren Pause einen Ladehinweis anzeigen, bis die erste Abfrage abgeschlossen ist.
- **Demo einer vorhandenen Python-API.** Den Server auf Render betreiben und die Daten auf Neon speichern. Vor der Vorführung die Antwortzeit des ersten Aufrufs nach einer Pause prüfen und kontrollieren, ob die Daten ein erneutes Deployment überstehen.
- **Privates Projekt mit Anmeldung.** Die Oberfläche auf Cloudflare Pages bereitstellen und mit Supabase Auth und der Data API verbinden. Mit zwei Konten prüfen, dass keines die Notizen des anderen lesen oder bearbeiten kann.

Sobald die Startseite lädt, **einen neuen Datensatz speichern, die API erneut bereitstellen und denselben Datensatz wieder abrufen**. Werden die Daten nach der Demo noch gebraucht, auch das Ablaufdatum des kostenlosen Tarifs und die Exportmöglichkeiten prüfen.
