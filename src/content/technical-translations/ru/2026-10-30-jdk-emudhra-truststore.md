---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ru",
  "translationKey": "2026-10-30-jdk-emudhra-truststore",
  "routeSlug": "2026-10-30-jdk-emudhra-truststore",
  "kind": "post",
  "title": "Сертификаты eMudhra в JDK: проверка работающей JVM и её хранилища доверия",
  "description": "Различайте рекомендации Oracle, Temurin и Ubuntu по прекращению доверия eMudhra. Проверяйте выбор хранилища JSSE и отпечатки сертификатов, не принимая версии или псевдонимы за окончательный вывод.",
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
  "draftSha256": "5046cff72a259d0b1cae1b4853b2571dfbcdca6828e8c707a3206049eff4d914",
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
Устранение проблемы eMudhra в JDK требует **проверки как JDK, на которой работает приложение, так и фактически используемого хранилища доверия**. [Уведомление Oracle](https://ops.java/emudhra/) и [уведомление Temurin](https://adoptium.net/news/2026/10/temurin-october-2026-emudhra/) описывают обновлённые дистрибутивы и прекращение доверия соответствующим центрам сертификации, но их реализации различаются. Защита браузера или обновление JDK хоста не подтверждает применение изменений в контейнерах или отдельных JVM.

## Поможет ли импорт просроченного серверного сертификата?

Этот инцидент отличается от обычного истечения срока серверного сертификата. Компрометация ключей промежуточных центров сертификации eMudhra создала пути доверия поддельным сертификатам, что потребовало отозвать соответствующее доверие или применить рекомендованную поставщиком защиту. [Предупреждение Oracle о CVE-2026-91403](https://www.oracle.com/security-alerts/alert-cve-2026-91403.html) содержит затронутые продукты и инструкции по исправлению. Не применяйте таблицу продуктов и версий Oracle без разбора к другому дистрибутиву.

`PKIX path building failed` не является однозначным признаком этого инцидента. Различайте неполную цепочку сервера, неверное хранилище доверия, частные центры сертификации и изменения доверия поставщиком. Отключение проверки или импорт непроверенного центра сертификации только ради устранения ошибки может подорвать защиту.

## Читайте уведомление каждого поставщика отдельно

Следующая информация отражает уведомления, проверенные 30 октября 2026 года. При развёртывании повторно проверьте продукт, ОС, полную сборку и актуальные последующие сообщения.

| Поставщик | Что следует различать |
| --- | --- |
| [Oracle JDK](https://ops.java/emudhra/) | Обновления, удаляющие соответствующие корни, и отдельные временные меры при задержке обновлений |
| [Eclipse Temurin](https://adoptium.net/news/2026/10/temurin-october-2026-emudhra/) | Использует данные центров сертификации Mozilla; прекращает доверие `emSign ECC Root CA - G3` и `AAA Certificate Services`. Исправленные сборки включают 21.0.13+9 и 17.0.21+9 |
| [Ubuntu OpenJDK](https://ubuntu.com/blog/emudhra-ca-compromise-fixes-available) | Интеграция с системным хранилищем центров сертификации; текущий дефект синхронизации требует дополнительного ручного действия с хранилищем Java после обновления `ca-certificates` |

Уведомление Temurin объясняет, что одно лишь присутствие `emSign Root CA - G1` не означает неудачного устранения проблемы. Использование общего списка корней `CheckCerts` как универсального критерия успешности может привести к неверной оценке дистрибутивов. Одни псевдонимы, имена и количество корней не подтверждают защиту.

## Чтение сведений о доверии JSSE по умолчанию текущей JVM

![Чтение идентификаторов JVM, инициализация TrustManager JSSE по умолчанию и сбор кандидатов по имени с отпечатками SHA-256](/assets/diagrams/technical/ru-2026-10-30-jdk-emudhra-truststore.svg)

Схема соответствует приведённому ниже сборщику, работающему только на чтение. Он инициализирует `TrustManagerFactory` по умолчанию и ищет имена центров сертификации. Совпадение имени — отправная точка для сравнения отпечатков с рекомендациями поставщика, а не заключение об уязвимости или безопасности. Невозможность инициализации менеджера доверия по умолчанию завершает выполнение с исключением.

Сохраните этот файл в новом каталоге с JDK 17 или новее. Он использует только публичные API [TrustManagerFactory](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/javax/net/ssl/TrustManagerFactory.html) и [X509TrustManager](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/javax/net/ssl/X509TrustManager.html). Он не изменяет файлы, не отправляет сетевые запросы, не добавляет и не удаляет сертификаты и не обходит проверку TLS.

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

Локальные проверки JDK скомпилировали программу и подтвердили вывод инвентаризации по умолчанию. Отдельно созданные хранилища тестовых центров сертификации также использовались для проверки кандидатов по имени и отпечатков SHA-256, хранилищ с посторонними именами и пустого хранилища. Эти тестовые центры сертификации не являются настоящими сертификатами eMudhra; успешное выполнение не удостоверяет защиту рабочей JVM.

Выведенное `java.home` относится к **только что запущенной JVM**. Значение `configuredTrustStore`, равное `<default JSSE lookup>`, означает, что системное свойство не задано, а не отсутствие найденного хранилища. Вывод не содержит паролей хранилищ доверия.

## Поиск по умолчанию может отличаться от настроек приложения

[Справочник SunJSSE](https://docs.oracle.com/en/java/javase/25/security/java-secure-socket-extension-jsse-reference-guide.html) различает явно заданное `javax.net.ssl.trustStore` и поиск `jssecacerts`/`cacerts` по умолчанию. Эта программа читает результат такого пути инициализации по умолчанию в новой JVM. Она не обнаруживает автоматически созданные приложением экземпляры `SSLContext`/`TrustManager`, настройки фреймворка или нативные библиотеки TLS.

Ноль кандидатов не означает безопасность. В зависимости от провайдера и сборки несуществующий путь хранилища может привести к использованию другого хранилища, пустой инвентаризации или ошибке инициализации. Локальные проверки JDK показали переход к хранилищу по умолчанию и сбой при несовпадении пароля. Другие имена или пути проверки также могут остаться незамеченными. И наоборот, присутствие имени в списке не устанавливает, что проверка TLS обязательно примет его цепочку. Этот код не выполняет проверки списков блокировки, отзыва или путей сертификации.

## После обновления проверяйте обычные подключения и отклонение

1. Определите поставщика JDK настоящего сервиса, полную сборку, исполняемый файл, параметры запуска JVM и хеш образа, включая пользовательские хранилища доверия и специфичные для приложения настройки TLS.
2. Разверните исправленную сборку поставщика. При обслуживании отдельного хранилища сравните его содержимое с рекомендациями поставщика. Перед ручным удалением подготовьте резервные копии, установите отпечатки и оцените влияние на подключения. Текущий дефект синхронизации Ubuntu требует дополнительной [процедуры обновления корневого хранилища центров сертификации Java](https://ubuntu.com/blog/emudhra-ca-compromise-fixes-available#updating-the-java-root-ca-store) после обновления `ca-certificates`. Сохраните локально добавленные центры сертификации и подготовьтесь повторно добавить их перед регенерацией.
3. Замените или перезапустите каждую JVM и реплику. Изменение `cacerts` одной установки не обновляет автоматически другую JDK или уже работающий процесс.
4. Проверьте как успешность обычного HTTPS, так и отклонение затронутых цепочек, указанных поставщиком. Результат TLS не заменяет проверку подписанных JAR.

В этой статье не выполнялись подключения к внешним тестовым узлам и не проверялось отклонение реальных затронутых цепочек. Не отмечайте эти проверки как завершённые на основании вывода сборщика. В рабочей среде следуйте [инструкциям проверки конкретного поставщика](https://adoptium.net/news/2026/10/temurin-october-2026-emudhra/) вместе с планом замены сертификатов.

RCE через регулярные выражения GitLab — отдельная от сертификатов проблема. Рекомендации по обновлению GitLab см. в [руководстве по реагированию на CVE-2026-110264](/en/posts/2026-10-30-gitlab2shell-cve-2026-110264/).
