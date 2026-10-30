---
language: "en"
translationKey: "2026-10-30-jdk-emudhra-truststore"
routeSlug: "2026-10-30-jdk-emudhra-truststore"
kind: "post"
categories: ["security", "jdk"]
tags: ["java", "jdk", "emudhra", "tls", "security"]
publishedAt: "2026-10-30T14:44:57.917449+00:00"
updatedAt: "2026-10-30T14:44:57.917449+00:00"
title: "JDK eMudhra Certificates: Inspect the Running JVM and Its Trust Store"
description: "Distinguish Oracle, Temurin and Ubuntu eMudhra distrust guidance. Inspect JSSE trust-store selection and certificate fingerprints without treating version labels or aliases as a verdict."
reviewedAt: "2026-10-30"
reviewStatus: "revised"
reviewScope: "Primary vendor advisories and API documentation; offline version comparison and read-only JSSE inventory with synthetic stores. No exploit, production upgrade or external TLS rejection validation."
reviewSources: ["https://ops.java/emudhra/", "https://www.oracle.com/security-alerts/alert-cve-2026-91403.html", "https://adoptium.net/news/2026/10/temurin-october-2026-emudhra/", "https://ubuntu.com/blog/emudhra-ca-compromise-fixes-available", "https://docs.oracle.com/en/java/javase/25/security/java-secure-socket-extension-jsse-reference-guide.html", "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/javax/net/ssl/TrustManagerFactory.html", "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/javax/net/ssl/X509TrustManager.html"]
---
JDK eMudhra remediation requires **checking both the JDK running the application and the trust store it actually uses**. The [Oracle notice](https://ops.java/emudhra/) and [Temurin notice](https://adoptium.net/news/2026/10/temurin-october-2026-emudhra/) describe updated distributions and distrust of relevant CAs, but their implementations differ. Browser protection or a host JDK update does not establish adoption in containers or separate JVMs.

## Will importing an expired server certificate solve it?

This incident differs from ordinary server-certificate expiry. Compromised eMudhra intermediate CA keys created paths that could trust fraudulent certificates, requiring removal of relevant trust or supplier-recommended protection. [Oracle’s CVE-2026-91403 security alert](https://www.oracle.com/security-alerts/alert-cve-2026-91403.html) provides affected products and patch guidance. Do not apply Oracle’s product/version table indiscriminately to another distribution.

`PKIX path building failed` is not a unique diagnosis of this incident. Distinguish an incomplete server chain, the wrong trust store, private CAs and supplier trust changes. Disabling validation or importing an unverified CA merely to silence an error can undermine the protection.

## Read each supplier’s advisory separately

The following reflects notices checked on October 30, 2026. Recheck the product, OS, full build and current follow-ups when deploying.

| Supplier | Distinction to check |
| --- | --- |
| [Oracle JDK](https://ops.java/emudhra/) | Updates removing relevant roots and separate interim mitigation when updates are delayed |
| [Eclipse Temurin](https://adoptium.net/news/2026/10/temurin-october-2026-emudhra/) | Uses Mozilla CA data; distrusts `emSign ECC Root CA - G3` and `AAA Certificate Services`. Fixed builds include 21.0.13+9 and 17.0.21+9 |
| [Ubuntu OpenJDK](https://ubuntu.com/blog/emudhra-ca-compromise-fixes-available) | System CA-store integration; a current synchronization defect requires additional manual action on the Java store after updating `ca-certificates` |

Temurin’s notice explains that the presence of `emSign Root CA - G1` alone does not establish failed remediation. Treating the generic `CheckCerts` root list as a universal pass criterion can misclassify distributions. Root aliases, names and counts alone do not certify protection.

## Read the current JVM’s default JSSE trust information

![Read JVM identity, initialize the default JSSE TrustManager and collect name candidates with SHA-256 fingerprints](/assets/diagrams/2026-10-30-jdk-emudhra-truststore-en.svg)

The diagram follows the read-only collector below. It initializes the default `TrustManagerFactory` and searches CA names. A name match is a starting point for comparing fingerprints with supplier guidance, not a vulnerable/safe verdict. Failure to initialize the default trust manager terminates with an exception.

Save this file in a new directory with JDK 17 or later. It uses only public [TrustManagerFactory](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/javax/net/ssl/TrustManagerFactory.html) and [X509TrustManager](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/javax/net/ssl/X509TrustManager.html) APIs. It does not modify files, send network requests, add/delete certificates or bypass TLS validation.

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

Local JDK checks compiled the program and confirmed default inventory output. Separately generated test-CA stores also checked name candidates and SHA-256 fingerprints, stores with unrelated names and an empty store. These test CAs are not actual eMudhra certificates; execution success does not certify protection of a production JVM.

The reported `java.home` belongs to **the JVM just started**. A `configuredTrustStore` value of `<default JSSE lookup>` means the system property was not specified, not that no store was found. The output does not include trust-store passwords.

## Default lookup can differ from application configuration

The [SunJSSE reference](https://docs.oracle.com/en/java/javase/25/security/java-secure-socket-extension-jsse-reference-guide.html) distinguishes an explicit `javax.net.ssl.trustStore` from default `jssecacerts`/`cacerts` lookup. This program reads that default initialization path in a new JVM. It does not discover application-created `SSLContext`/`TrustManager` instances, framework settings or native TLS libraries automatically.

Zero candidates is not a safety verdict. Depending on the provider and build, a nonexistent store path may fall back to another store, produce an empty inventory or fail initialization. Local JDK checks observed default-store fallback and password-mismatch failure. Other names or validation paths can also be missed. Conversely, a listed name does not establish that TLS validation necessarily accepts its chain. This code does not execute blocklist, revocation or certificate-path checks.

## Check normal connections and rejection after updating

1. Identify the real service’s JDK supplier, full build, executable, JVM startup options and image digest, including custom trust stores and application-specific TLS settings.
2. Deploy the supplier’s fixed build. If maintaining a separate store, compare its contents with supplier guidance. Before any manual deletion, establish backups, fingerprints and connection impact. Ubuntu’s current synchronization defect requires the additional [Java root CA-store update procedure](https://ubuntu.com/blog/emudhra-ca-compromise-fixes-available#updating-the-java-root-ca-store) after updating `ca-certificates`. Preserve locally provisioned CAs and prepare to re-add them before regeneration.
3. Replace or restart every JVM and replica. Changing one installation’s `cacerts` does not automatically update another JDK or a process already running.
4. Verify both ordinary HTTPS success and rejection of supplier-specified affected chains. A TLS result does not replace validation of signed JARs.

This article did not connect to external test hosts or verify rejection of actual affected chains. Do not record those checks as completed on the strength of collector output. Follow [supplier-specific verification guidance](https://adoptium.net/news/2026/10/temurin-october-2026-emudhra/) together with a certificate-replacement plan in production.

The GitLab regular-expression RCE is separate from this certificate issue. See the [CVE-2026-110264 response guide](/en/posts/2026-10-30-gitlab2shell-cve-2026-110264/) for GitLab upgrade guidance.
