---
language: "ko"
translationKey: "2026-10-30-jdk-emudhra-truststore"
routeSlug: "2026-10-30-jdk-emudhra-truststore"
kind: "post"
categories: ["security", "jdk"]
tags: ["java", "jdk", "emudhra", "tls", "security"]
publishedAt: "2026-10-30T14:44:57.917449+00:00"
updatedAt: "2026-10-30T14:44:57.917449+00:00"
title: "JDK eMudhra 인증서 이슈: 실행 JVM과 실제 신뢰 저장소 확인하기"
description: "Oracle·Temurin·Ubuntu의 eMudhra 신뢰 해제 방식을 구분합니다. JSSE의 신뢰 저장소 선택과 인증서 지문을 읽는 Java 예제로 버전·별칭만으로 판정하는 실수를 피합니다."
reviewedAt: "2026-10-30"
reviewStatus: "revised"
reviewScope: "Primary vendor advisories and API documentation; offline version comparison and read-only JSSE inventory with synthetic stores. No exploit, production upgrade or external TLS rejection validation."
reviewSources: ["https://ops.java/emudhra/", "https://www.oracle.com/security-alerts/alert-cve-2026-91403.html", "https://adoptium.net/news/2026/10/temurin-october-2026-emudhra/", "https://ubuntu.com/blog/emudhra-ca-compromise-fixes-available", "https://docs.oracle.com/en/java/javase/25/security/java-secure-socket-extension-jsse-reference-guide.html", "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/javax/net/ssl/TrustManagerFactory.html", "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/javax/net/ssl/X509TrustManager.html"]
---
JDK의 eMudhra 인증서 대응은 **애플리케이션을 실행하는 JDK와 실제 사용하는 신뢰 저장소를 함께 확인하는 작업**입니다. [Oracle 공지](https://ops.java/emudhra/)와 [Temurin 공지](https://adoptium.net/news/2026/10/temurin-october-2026-emudhra/)는 수정 배포판과 영향을 받는 CA의 신뢰 해제를 안내하지만 적용 방식은 같지 않습니다. 브라우저가 차단하거나 호스트 JDK를 업데이트했다는 사실만으로 컨테이너·별도 JVM까지 반영됐다고 볼 수 없습니다.

## 만료된 서버 인증서를 가져오면 해결되나요?

이 문제는 일반적인 서버 인증서 만료와 다릅니다. eMudhra 중간 CA 키 유출로 위조 인증서를 신뢰할 수 있는 경로가 생겼기 때문에, 관련 신뢰를 제거하거나 공급자의 권장 보호를 적용해야 합니다. [Oracle 보안 알림 CVE-2026-91403](https://www.oracle.com/security-alerts/alert-cve-2026-91403.html)은 영향을 받는 제품과 패치 안내를 제공합니다. 다른 배포판에도 Oracle의 제품·버전 표를 그대로 대입하지 마세요.

`PKIX path building failed`는 이 사건만의 고유한 진단 결과가 아닙니다. 서버 체인 누락, 잘못된 신뢰 저장소, 사설 CA와 공급자의 신뢰 변경을 구분해야 합니다. 오류를 없애려고 검증을 끄거나 확인하지 않은 CA를 추가하면 보호 목적을 훼손할 수 있습니다.

## 공급자별 공지를 따로 읽으세요

아래 내용은 2026년 10월 30일에 확인한 공지를 기준으로 합니다. 배포할 때는 제품·OS·전체 빌드와 최신 후속 공지를 다시 대조하세요.

| 공급자 | 공지에서 확인할 차이 |
| --- | --- |
| [Oracle JDK](https://ops.java/emudhra/) | 관련 루트를 제거한 업데이트와, 업데이트 지연 시 적용할 별도 완화 절차 |
| [Eclipse Temurin](https://adoptium.net/news/2026/10/temurin-october-2026-emudhra/) | Mozilla CA 목록을 사용하며 `emSign ECC Root CA - G3`·`AAA Certificate Services` 신뢰 제거. 수정 목록에 21.0.13+9·17.0.21+9 등이 있음 |
| [Ubuntu OpenJDK](https://ubuntu.com/blog/emudhra-ca-compromise-fixes-available) | 시스템 CA 저장소 연동. 현재 동기화 결함으로 `ca-certificates` 업데이트 후 Java 저장소에 추가 수동 조치 필요 |

Temurin 공지는 `emSign Root CA - G1`이 남아 있다는 이유만으로 수정 실패라고 판단하지 말라고 설명합니다. 일반 `CheckCerts` 도구의 루트 목록을 모든 배포판의 합격 기준으로 쓰면 오판할 수 있습니다. 루트 별칭·이름·개수만으로 보호 여부를 인증하지 마세요.

## 현재 JVM의 기본 JSSE 신뢰 정보를 읽기

![현재 JVM 정보를 읽고 기본 JSSE TrustManager의 CA 목록에서 이름 후보와 SHA-256 지문을 수집하는 흐름](/assets/diagrams/2026-10-30-jdk-emudhra-truststore-ko.svg)

그림은 아래 읽기 전용 수집기의 흐름입니다. 기본 `TrustManagerFactory`를 초기화하고 CA 목록에서 이름 후보를 찾습니다. 이름 일치는 공급자 공지와 지문을 대조할 출발점이며, 취약·안전 판정이 아닙니다. 기본 신뢰 관리자 초기화가 실패하면 예외로 종료합니다.

JDK 17 이상에서 새 디렉터리에 저장합니다. [TrustManagerFactory](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/javax/net/ssl/TrustManagerFactory.html)와 [X509TrustManager](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/javax/net/ssl/X509TrustManager.html)의 공개 API만 사용합니다. 파일 수정·네트워크 요청·인증서 추가·삭제·TLS 검증 우회는 하지 않습니다.

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

로컬 JDK에서 컴파일과 기본 목록 출력을 확인했습니다. 별도로 생성한 테스트 CA 저장소에서는 이름 후보와 SHA-256 지문, 관련 이름이 없는 경우와 비어 있는 저장소의 출력도 확인했습니다. 이 테스트 CA는 실제 eMudhra 인증서가 아니며, 실행 성공은 운영 JVM의 보호를 인증하지 않습니다.

출력의 `java.home`은 **지금 실행한 JVM**입니다. `configuredTrustStore`가 `<default JSSE lookup>`이면 저장소를 못 찾았다는 뜻이 아니라 시스템 속성에 명시하지 않았다는 뜻입니다. 출력에는 저장소 비밀번호를 포함하지 않습니다.

## 기본 조회와 실제 애플리케이션 설정은 다를 수 있습니다

[SunJSSE 문서](https://docs.oracle.com/en/java/javase/25/security/java-secure-socket-extension-jsse-reference-guide.html)는 `javax.net.ssl.trustStore`를 지정한 경우와 기본 `jssecacerts`·`cacerts` 조회를 구분합니다. 이 프로그램은 새 JVM에서 그 기본 초기화 경로를 읽습니다. 프로그램에서 별도로 만든 `SSLContext`·`TrustManager`, 프레임워크 설정이나 네이티브 TLS 라이브러리를 자동으로 찾아내지는 않습니다.

후보가 0개여도 안전 판정은 아닙니다. 존재하지 않는 저장소 경로는 제공자·빌드에 따라 다른 저장소로 대체되거나 빈 결과를 내거나 초기화에 실패할 수 있습니다. 로컬 JDK에서는 기본 저장소로 대체되는 경우와 암호 불일치로 실패하는 경우를 확인했습니다. 다른 이름의 인증서·다른 검증 경로도 놓칠 수 있습니다. 반대로 이름이 보인다고 실제 TLS 검증에서 반드시 허용되는 것도 아닙니다. 이 코드는 차단 목록·폐기 확인·인증서 경로 검증을 실행하지 않습니다.

## 업데이트 뒤 정상 연결과 차단을 각각 확인하세요

1. 실제 서비스의 JDK 공급자·전체 빌드, 실행 경로, JVM 시작 옵션과 이미지 digest를 식별합니다. 사용자 신뢰 저장소와 애플리케이션별 TLS 설정도 포함합니다.
2. 해당 공급자의 수정 빌드를 배포하고, 별도 저장소를 유지한다면 공급자 지침에 맞춰 내용을 대조합니다. 수동 삭제가 필요할 때도 원본 백업·지문·연결 영향부터 확인합니다. Ubuntu는 현재 동기화 결함 때문에 `ca-certificates` 업데이트 후 [Java 루트 CA 저장소 갱신 절차](https://ubuntu.com/blog/emudhra-ca-compromise-fixes-available#updating-the-java-root-ca-store)를 추가로 수행해야 합니다. 재생성 전에 로컬에서 추가한 CA를 보존하고 재등록할 준비를 합니다.
3. 모든 JVM·복제본을 교체하거나 재시작해 반영합니다. 한 설치의 `cacerts`를 바꾼 것으로 다른 JDK와 이미 실행 중인 프로세스까지 바뀌지는 않습니다.
4. 일반 HTTPS 연결이 성공하는지와 공급자가 지정한 영향 체인이 거부되는지를 별도로 검증합니다. TLS 검증 통과 여부를 서명된 JAR의 검증 결과로 대신하지 마세요.

이 글에서는 외부 테스트 호스트 연결이나 실제 영향 체인의 거부를 실행하지 않았습니다. 수집기 결과만으로 그런 검증을 완료했다고 기록해서는 안 됩니다. 운영에서는 [공급자별 검증 안내](https://adoptium.net/news/2026/10/temurin-october-2026-emudhra/)와 인증서 교체 계획을 함께 따르세요.

GitLab 서버의 정규식 RCE는 이 인증서 문제와 별개입니다. GitLab 업그레이드는 [CVE-2026-110264 대응 글](/ko/posts/2026-10-30-gitlab2shell-cve-2026-110264/)에서 확인할 수 있습니다.
