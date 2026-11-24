---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2026-11-24-github-pages-ads-guide",
  "routeSlug": "2026-11-24-github-pages-ads-guide",
  "kind": "post",
  "title": "Werbung im GitHub-Pages-Blog: von der Dienstwahl bis zur AdSense-Installation",
  "description": "Werbedienst auswählen, AdSense und ads.txt im GitHub-Pages-Stammverzeichnis einrichten und Prüfung sowie Auslieferung kontrollieren.",
  "categories": [
    "tips"
  ],
  "tags": [
    "github-pages",
    "adsense",
    "ads-txt"
  ],
  "sourcePath": "src/content/posts/en/2026-11-24-github-pages-ads-guide.md",
  "sourceSha256": "884b5c639b2345ac6daac6b307db2cd0ec22e80801c8d5d2d5860b4ba12356d8",
  "draftSha256": "bff409130917cb714a0f387f189b1f6243a0a8b91382bfada597ead37ed3e912",
  "manifestPath": ".pipeline/technical-translations/batch-190/manifest.json",
  "manifestSha256": "6b40a455d4e018ed7edaefaa33a3094c5c1475c70d97ffdc7106618f6fa84d3f",
  "publishedAt": "2026-11-24T08:55:29.701Z",
  "updatedAt": "2026-11-24T08:55:29.701Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 193,
    "approvedAt": "2026-11-24T08:55:29.701Z",
    "basis": "Owner requested publication in eight languages; translations self-reviewed without independent or native-speaker review."
  }
}
---

Wer einen technischen Blog unter `username.github.io` betreibt, kann zunächst Google AdSense prüfen. Bei einer beständigen Leserschaft aus der Entwicklung kommen auch Carbon Ads und EthicalAds infrage. Vor der Anmeldung sollte geprüft werden, ob sich `https://username.github.io/ads.txt` veröffentlichen lässt. Das ist besonders bei Projektadressen wie `username.github.io/blog/` wichtig.

GitHub verbietet Werbung auf inhaltsorientierten Websites nicht grundsätzlich. GitHub Pages schränkt aber die Nutzung als kostenloses Hosting für Onlinegeschäfte, E-Commerce oder kommerzielles SaaS ein. Für Werbung in einem technischen Blog sollten beide Richtlinien gelesen werden. [GitHubs Werberichtlinie](https://docs.github.com/en/site-policy/acceptable-use-policies/github-acceptable-use-policies#10-advertising-on-github) · [Grenzen von GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)

## Welcher Werbedienst passt?

| Dienst | Geeignete Websites | Anmeldung |
| --- | --- | --- |
| **Google AdSense** | Ein persönlicher Blog mit ersten Anzeigen und der Wahl zwischen automatischer und manueller Platzierung | [AdSense starten](https://adsense.google.com/start/) |
| **Carbon Ads** | Artikel, Dokumentation und Werkzeuge für Entwickler und Designer. Bewerbungen werden ab 10,000 Seitenaufrufen pro Monat geprüft; andere Werbenetzwerke sind daneben nicht erlaubt. | [Bei Carbon Ads bewerben](https://www.carbonads.net/join?_hsmi=83378591) |
| **EthicalAds** | Entwicklerorientierte Websites mit mindestens 50,000 Seitenaufrufen monatlich und Platz für eine Anzeige außerhalb des Leseflusses | [EthicalAds-Leitfaden für Publisher](https://www.ethicalads.io/publisher-guide/) |

Legen Sie zuerst die Platzierung fest. Bei vielen Codebeispielen ist eine manuell platzierte AdSense-Anzeige unter dem Artikel ein Ausgangspunkt für die Prüfung auf dem Smartphone. AdSense bietet **Anzeigenblöcke**, deren Position Sie wählen, und **automatische Anzeigen**, deren Position Google bestimmt. EthicalAds hat eigene Regeln: Die Anzeige soll auf Desktop und Mobilgerät im ersten sichtbaren Bereich stehen; ist das mobil nicht möglich, kann sie dort deaktiviert werden. [AdSense-Anzeigeneinstellungen](https://support.google.com/adsense/answer/7037624)

![AdSense-Ablauf: Code einfügen, ads.txt im Stammverzeichnis veröffentlichen, URL prüfen und Überprüfung anfordern.](/assets/diagrams/technical/de-2026-11-24-github-pages-ads-guide.svg)

Die Grafik fasst Einrichtung und Prüfungsanfrage zusammen; die tatsächliche Anzeigenauslieferung wird separat geprüft.

## 1. Bei AdSense anmelden und Website hinzufügen

Melden Sie sich mit einem Google-Konto bei AdSense an und geben Sie Zahlungsland und Zahlungsinformationen ein. Fügen Sie unter **Websites → Neue Website** `https://username.github.io` hinzu. Die Public Suffix List enthält `github.io`; AdSense erlaubt laut eigener Anleitung Subdomains von Plattformen auf dieser Liste als Websites. Danach folgen Eigentumsbestätigung und Websiteprüfung. [AdSense-Konto erstellen](https://support.google.com/adsense/answer/7402253) · [AdSense-Websitekriterien](https://support.google.com/adsense/answer/12170421) · [Public Suffix List](https://publicsuffix.org/list/public_suffix_list.dat)

Prüfen Sie die Adresse: Eine GitHub-Pages-Benutzerwebsite liegt unter `username.github.io/`, eine Projektwebsite normalerweise unter `username.github.io/blog/`. Eine `ads.txt` in der Projektveröffentlichung kann unter `/blog/ads.txt` landen. Google beginnt im Stammverzeichnis des Hosts bei `/ads.txt`. Veröffentlichen Sie die Datei daher über die Benutzerwebsite oder im Stammverzeichnis einer mit dem Blog verbundenen eigenen Domain. [GitHub-Pages-Websitetypen](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages#types-of-github-pages-sites) · [Googles ads.txt-Crawling](https://support.google.com/adsense/answer/7679060)

## 2. Ein Code im gemeinsamen `<head>`, eine `ads.txt` im Stammverzeichnis

AdSense bietet ein Code-Snippet, `ads.txt` oder ein Meta-Tag zur Eigentumsbestätigung an. Beim Snippet fügen Sie den Code aus dem Dashboard in den `<head>` des gemeinsamen Layouts ein. Das folgende Beispiel zeigt nur die Form; verwenden Sie für die Veröffentlichung den Code aus Ihrem Konto. [Website verbinden](https://support.google.com/adsense/answer/7584263)

```html
<script async
  src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-0000000000000000"
  crossorigin="anonymous"></script>
```

Kopieren Sie die im Dashboard bereitgestellte Zeile in `ads.txt`. Die Datei nennt Konten, die das Anzeigeninventar Ihrer Website verkaufen dürfen. Bestehende Verkäuferzeilen bleiben erhalten; die neue Zeile wird ergänzt.

```text
google.com, pub-0000000000000000, DIRECT, f08c47fec0942fa0
```

Bei einer Astro-Benutzerwebsite legen Sie die Datei unter `public/ads.txt` ab; Astro kopiert Dateien aus `public/` in das Build-Ergebnis. Prüfen Sie nach der Veröffentlichung die öffentliche URL, nicht nur das Repository. [Astros `public/`-Verzeichnis](https://docs.astro.build/en/guides/images/#src-vs-public) · [Googles ads.txt-Leitfaden](https://support.google.com/adsense/answer/12171612)

```bash
curl -fsSL https://username.github.io/ads.txt
```

Erwartet wird die oben gezeigte Verkäuferzeile. Eine echte Website sollte die Publisher-ID des Kontos zurückgeben. Die Adresse `username` ist ein Beispiel; dies ist keine beobachtete Befehlsausgabe.

Für einen mehrsprachigen Blog auf demselben Host reicht eine Datei im Stammverzeichnis; separate Dateien unter `/ko/` und `/en/` sind nicht nötig. Prüfen Sie im endgültigen HTML je eines repräsentativen Artikels pro Sprache, ob der gemeinsame Loader einmal vorkommt.

## 3. Veröffentlichung, Prüfung und Anzeigenauslieferung getrennt prüfen

Bestätigen Sie nach der Veröffentlichung von Datei und Code das Eigentum in AdSense und fordern Sie die Websiteprüfung an. Der Websitestatus **`Ready`** bedeutet, dass die Website für Anzeigen bereit ist; der ads.txt-Status **`Authorized`** bedeutet, dass Google die Publisher-ID in der Datei gefunden hat. Steht trotz erreichbarer öffentlicher URL noch `Not found` im Dashboard, prüfen Sie, ob die Änderung nach dem letzten Crawling erfolgte. Bei korrektem Pfad und Inhalt können Sie mit **Nach Updates suchen** eine erneute Prüfung anfordern. [Websitestatus](https://support.google.com/adsense/answer/12170222) · [ads.txt-Status](https://support.google.com/adsense/answer/12171612)

Beschreiben Sie vor dem Aktivieren von Anzeigen in der Datenschutzerklärung die für Werbung erhobenen oder weitergegebenen Informationen und verwendete Technologien wie Cookies. Für personalisierte Anzeigen für Besucher im EWR, Vereinigten Königreich und in der Schweiz ist eine von Google zertifizierte Consent-Management-Plattform (CMP) erforderlich, die mit dem IAB Transparency and Consent Framework (TCF) integriert ist. Die Nachricht zu europäischen Vorschriften unter **Datenschutz und Mitteilungen** in AdSense ist eine Möglichkeit. [Google-Datenschutzrichtlinie für Publisher](https://support.google.com/adsense/answer/10502938) · [Googles CMP-Anforderungen](https://support.google.com/adsense/answer/13554116)

Prüfen Sie nach der Freigabe die Platzierung mit der Vorschau automatischer Anzeigen oder einem manuellen Anzeigenblock. Kontrollieren Sie auf dem Smartphone, dass Inhaltsverzeichnis, Code-Kopierschaltflächen und Sprachmenü nicht verdeckt werden. Klicken Sie zum Testen nicht auf eigene Anzeigen; nutzen Sie Vorschau und Dashboardberichte. [Vorschau automatischer Anzeigen](https://support.google.com/adsense/answer/9261307) · [Ungültiger Traffic](https://support.google.com/adsense/answer/16737)

Bei `youdozi.github.io` wurden die öffentliche `ads.txt` im Stammverzeichnis und ein AdSense-Skript im HTML der koreanischen Startseite geprüft. Die Prüfung umfasste die öffentliche Datei und das HTML; Kontoprüfungsstatus und tatsächliche Auslieferung müssen separat geprüft werden. [Öffentliche ads.txt](https://youdozi.github.io/ads.txt) · [Koreanische Startseite](https://youdozi.github.io/ko/)
