---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2026-10-30-jdk-emudhra-truststore",
  "routeSlug": "2026-10-30-jdk-emudhra-truststore",
  "kind": "post",
  "title": "JDK-eMudhra-Zertifikate: Laufende JVM und ihren Truststore prüfen",
  "description": "Unterscheiden Sie eMudhra-Misstrauenshinweise von Oracle, Temurin und Ubuntu. Prüfen Sie JSSE-Truststore-Auswahl und Zertifikatsfingerabdrücke, ohne Versionsangaben oder Aliasse als Urteil zu behandeln.",
  "categories": [
    "security",
    "jdk"
  ],
  "tags": [
    "java",
    "jdk",
    "emudhra",
    "tls",
    "security"
  ],
  "sourcePath": "src/content/posts/en/2026-10-30-jdk-emudhra-truststore.md",
  "sourceSha256": "abdc8cf489bcb34919f036e665475c6dd2f939c07f1a4c42ffe10c86e32761e3",
  "draftSha256": "3d642ab82b1ff796d04d425fefd4812d352507de41750628cfba74c3a5789b23",
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
Die Behebung des JDK-eMudhra-Problems erfordert, **sowohl das JDK der laufenden Anwendung als auch den tatsächlich verwendeten Truststore zu prüfen**. Der [Oracle-Hinweis](https://ops.java/emudhra/) und der [Temurin-Hinweis](https://adoptium.net/news/2026/10/temurin-october-2026-emudhra/) beschreiben aktualisierte Distributionen und den Vertrauensentzug für relevante CAs, ihre Implementierungen unterscheiden sich jedoch. Browserschutz oder ein JDK-Update auf dem Host belegt keine Übernahme in Containern oder separaten JVMs.

## Hilft der Import eines abgelaufenen Serverzertifikats?

Dieser Vorfall unterscheidet sich vom gewöhnlichen Ablauf eines Serverzertifikats. Kompromittierte Schlüssel von eMudhra-Zwischen-CAs schufen Pfade, die gefälschten Zertifikaten vertrauen konnten. Deshalb muss das entsprechende Vertrauen entfernt oder der vom Anbieter empfohlene Schutz angewandt werden. [Oracles Sicherheitshinweis zu CVE-2026-91403](https://www.oracle.com/security-alerts/alert-cve-2026-91403.html) nennt betroffene Produkte und Patch-Anleitungen. Übertragen Sie Oracles Produkt-/Versionstabelle nicht unterschiedslos auf andere Distributionen.

`PKIX path building failed` ist keine eindeutige Diagnose dieses Vorfalls. Unterscheiden Sie eine unvollständige Serverkette, den falschen Truststore, private CAs und Vertrauensänderungen des Anbieters. Validierung zu deaktivieren oder eine ungeprüfte CA zu importieren, nur um eine Fehlermeldung zu unterdrücken, kann den Schutz untergraben.

## Hinweise jedes Anbieters separat lesen

Das Folgende entspricht den am 30. Oktober 2026 geprüften Hinweisen. Prüfen Sie bei der Bereitstellung Produkt, Betriebssystem, vollständigen Build und aktuelle Nachmeldungen erneut.

| Anbieter | Zu prüfender Unterschied |
| --- | --- |
| [Oracle JDK](https://ops.java/emudhra/) | Updates entfernen relevante Wurzeln; separate Übergangsmaßnahme bei verzögerten Updates |
| [Eclipse Temurin](https://adoptium.net/news/2026/10/temurin-october-2026-emudhra/) | Verwendet Mozilla-CA-Daten; entzieht `emSign ECC Root CA - G3` und `AAA Certificate Services` das Vertrauen. Korrigierte Builds umfassen 21.0.13+9 und 17.0.21+9 |
| [Ubuntu OpenJDK](https://ubuntu.com/blog/emudhra-ca-compromise-fixes-available) | Integration des System-CA-Speichers; ein aktueller Synchronisationsfehler erfordert nach Aktualisierung von `ca-certificates` einen zusätzlichen manuellen Schritt am Java-Speicher |

Temurins Hinweis erklärt, dass das Vorhandensein von `emSign Root CA - G1` allein keine fehlgeschlagene Behebung belegt. Die allgemeine `CheckCerts`-Wurzelliste als universelles Erfolgskriterium zu behandeln, kann Distributionen falsch einstufen. Wurzel-Aliasse, Namen und Anzahlen allein zertifizieren keinen Schutz.

## Standardmäßige JSSE-Vertrauensinformationen der aktuellen JVM lesen

![JVM-Identität lesen, standardmäßigen JSSE-TrustManager initialisieren und Namenskandidaten mit SHA-256-Fingerabdrücken sammeln](/assets/diagrams/technical/de-2026-10-30-jdk-emudhra-truststore.svg)

Das Diagramm folgt dem folgenden rein lesenden Erfassungsprogramm. Es initialisiert die standardmäßige `TrustManagerFactory` und durchsucht CA-Namen. Ein passender Name ist ein Ausgangspunkt zum Vergleich von Fingerabdrücken mit Anbieterhinweisen, kein Urteil „verwundbar/sicher“. Scheitert die Initialisierung des Standard-Trustmanagers, endet das Programm mit einer Ausnahme.

Speichern Sie diese Datei mit JDK 17 oder neuer in einem neuen Verzeichnis. Sie verwendet ausschließlich öffentliche APIs von [TrustManagerFactory](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/javax/net/ssl/TrustManagerFactory.html) und [X509TrustManager](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/javax/net/ssl/X509TrustManager.html). Sie ändert keine Dateien, sendet keine Netzwerkanfragen, fügt keine Zertifikate hinzu oder entfernt sie und umgeht keine TLS-Validierung.

### `TrustInventory.java`

```java
import java.security.KeyStore;
import java.security.MessageDigest;
import java.security.cert.X509Certificate;
import java.util.HexFormat;
import java.util.Locale;
import javax.net.ssl.TrustManager;
import javax.net.ssl.TrustManagerFactory;
import javax.net.ssl.X509TrustManager;

public class TrustInventory {
    public static void main(String[] args) throws Exception {
        System.out.println("java.version=" + System.getProperty("java.version"));
        System.out.println("java.vendor=" + System.getProperty("java.vendor"));
        System.out.println("java.home=" + System.getProperty("java.home"));
        System.out.println("configuredTrustStore=" +
            System.getProperty("javax.net.ssl.trustStore", "<default JSSE lookup>"));
        TrustManagerFactory factory = TrustManagerFactory.getInstance(
            TrustManagerFactory.getDefaultAlgorithm());
        factory.init((KeyStore) null);
        System.out.println("trustManagerProvider=" + factory.getProvider().getName());
        MessageDigest sha256 = MessageDigest.getInstance("SHA-256");
        int issuers = 0;
        int matches = 0;
        for (TrustManager manager : factory.getTrustManagers()) {
            if (!(manager instanceof X509TrustManager x509)) continue;
            for (X509Certificate cert : x509.getAcceptedIssuers()) {
                issuers++;
                String subject = cert.getSubjectX500Principal().getName();
                String lower = subject.toLowerCase(Locale.ROOT);
                if (lower.contains("emsign") || lower.contains("aaa certificate services")) {
                    String fingerprint = HexFormat.of().withUpperCase()
                        .formatHex(sha256.digest(cert.getEncoded()));
                    System.out.println("candidate=" + subject + "\tSHA256=" + fingerprint);
                    matches++;
                }
            }
        }
        System.out.println("acceptedIssuers=" + issuers);
        System.out.println("nameMatches=" + matches);
        System.out.println("assessment=inventory-only; no validation verdict");
    }
}
```

```sh
javac --release 17 TrustInventory.java
java TrustInventory
```

Lokale JDK-Prüfungen kompilierten das Programm und bestätigten die Ausgabe des Standardbestands. Separat erzeugte Test-CA-Speicher prüften zudem Namenskandidaten und SHA-256-Fingerabdrücke, Speicher mit nicht zugehörigen Namen und einen leeren Speicher. Diese Test-CAs sind keine tatsächlichen eMudhra-Zertifikate; erfolgreiche Ausführung zertifiziert keinen Schutz einer Produktiv-JVM.

Das gemeldete `java.home` gehört zur **gerade gestarteten JVM**. Der Wert von `configuredTrustStore`, wenn er `<default JSSE lookup>` lautet, bedeutet, dass die Systemeigenschaft nicht angegeben wurde, nicht dass kein Speicher gefunden wurde. Die Ausgabe enthält keine Truststore-Passwörter.

## Standardsuche kann von der Anwendungskonfiguration abweichen

Die [SunJSSE-Referenz](https://docs.oracle.com/en/java/javase/25/security/java-secure-socket-extension-jsse-reference-guide.html) unterscheidet ein explizites `javax.net.ssl.trustStore` von der Standardsuche nach `jssecacerts`/`cacerts`. Dieses Programm liest diesen Standardinitialisierungspfad in einer neuen JVM. Es erkennt anwendungseigene `SSLContext`-/`TrustManager`-Instanzen, Framework-Einstellungen oder native TLS-Bibliotheken nicht automatisch.

Null Kandidaten ist kein Sicherheitsurteil. Je nach Provider und Build kann ein nicht existierender Speicherpfad auf einen anderen Speicher zurückfallen, einen leeren Bestand liefern oder die Initialisierung scheitern lassen. Lokale JDK-Prüfungen beobachteten den Rückfall auf den Standardspeicher und ein Scheitern bei falschem Passwort. Andere Namen oder Validierungspfade können ebenfalls übersehen werden. Umgekehrt belegt ein aufgeführter Name nicht, dass die TLS-Validierung seine Kette zwangsläufig akzeptiert. Dieser Code führt keine Sperrlisten-, Widerrufs- oder Zertifikatspfadprüfungen aus.

## Nach dem Update normale Verbindungen und Ablehnung prüfen

1. Identifizieren Sie JDK-Anbieter, vollständigen Build, Programmdatei, JVM-Startoptionen und Image-Digest des tatsächlichen Dienstes einschließlich eigener Truststores und anwendungsspezifischer TLS-Einstellungen.
2. Stellen Sie den korrigierten Build des Anbieters bereit. Wenn Sie einen separaten Speicher pflegen, vergleichen Sie seinen Inhalt mit den Anbieterhinweisen. Klären Sie vor manuellen Löschungen Sicherungen, Fingerabdrücke und Verbindungsauswirkungen. Ubuntus aktueller Synchronisationsfehler erfordert nach Aktualisierung von `ca-certificates` das zusätzliche [Verfahren zur Aktualisierung des Java-Wurzel-CA-Speichers](https://ubuntu.com/blog/emudhra-ca-compromise-fixes-available#updating-the-java-root-ca-store). Bewahren Sie lokal bereitgestellte CAs und bereiten Sie deren erneutes Hinzufügen vor der Regeneration vor.
3. Ersetzen oder starten Sie jede JVM und jedes Replikat neu. Die Änderung von `cacerts` einer Installation aktualisiert nicht automatisch ein anderes JDK oder einen bereits laufenden Prozess.
4. Prüfen Sie sowohl den Erfolg gewöhnlicher HTTPS-Verbindungen als auch die Ablehnung der vom Anbieter bezeichneten betroffenen Ketten. Ein TLS-Ergebnis ersetzt nicht die Validierung signierter JARs.

Für diesen Artikel wurden keine externen Testhosts verbunden und keine Ablehnung tatsächlich betroffener Ketten geprüft. Tragen Sie diese Prüfungen nicht allein aufgrund der Erfassungsausgabe als abgeschlossen ein. Befolgen Sie im Produktivbetrieb [anbieterspezifische Prüfanleitungen](https://adoptium.net/news/2026/10/temurin-october-2026-emudhra/) zusammen mit einem Plan zum Zertifikatsaustausch.

Die GitLab-RCE über reguläre Ausdrücke ist von diesem Zertifikatsproblem getrennt. Upgrade-Hinweise zu GitLab stehen im [Leitfaden zu CVE-2026-110264](/en/posts/2026-10-30-gitlab2shell-cve-2026-110264/).
