# 다국어 번역 검토 초안

의미·용어·조건 대조와 대상 언어 교정은 AI로 검토합니다. 수치·제품명 검사는 의미 검토를 대체하지 않습니다. 사이트 게시는 사용자의 명시적 승인 후에 진행합니다.

## Copilot CLI security review remains an experimental preview

원문: https://github.blog/changelog/2026-06-10-dedicated-security-review-command-now-available-in-copilot-cli

검토 기준: 영어 보강본 c4a7f428da738696, 2026-10-25T12:23:59+00:00

### 영어 기준본

1. GitHub introduced the /security-review command for local code changes as an experimental public-preview feature. Users must enable experimental mode to try the command.

> The new /security-review slash command is shipping as an experimental feature in public preview

근거: https://github.blog/changelog/2026-06-10-dedicated-security-review-command-now-available-in-copilot-cli

> turn on experimental mode in Copilot CLI

근거: https://github.blog/changelog/2026-06-10-dedicated-security-review-command-now-available-in-copilot-cli

2. The announcement describes a Copilot-driven scan that does not rely on GitHub code scanning, Dependabot or secret scanning. It complements those tools with on-demand review before committing; it is not evidence that all vulnerabilities will be detected.

> This is a Copilot-driven scan that doesn’t rely on GitHub code scanning, Dependabot, or GitHub secret scanning.

근거: https://github.blog/changelog/2026-06-10-dedicated-security-review-command-now-available-in-copilot-cli

검토 초점: Check feature availability in the installed CLI and inspect findings manually. Preserve deterministic security checks and avoid treating a clean preview scan as a security certification.

### 简体中文 (zh-CN)

Copilot CLI 安全审查仍处于实验性预览阶段

1. GitHub 推出了用于本地代码变更的 /security-review 命令，作为处于公开预览阶段的实验性功能。用户必须启用实验模式才能试用该命令。

2. 公告将其描述为由 Copilot 驱动的扫描，不依赖 GitHub 代码扫描、Dependabot 或机密扫描。它通过提交前的按需审查补充这些工具，但这并不能证明所有漏洞都会被检测到。

검토 초점: 检查所安装 CLI 中该功能的可用性，并手动核查发现。保留确定性的安全检查，不要将未发现问题的预览扫描当作安全认证。

### 日本語 (ja)

Copilot CLI のセキュリティレビューは実験的プレビューの段階

1. GitHub は、ローカルのコード変更を対象とする /security-review コマンドを、パブリックプレビューの実験的機能として導入した。試用には実験モードを有効にする必要がある。

2. 告知では、GitHub のコードスキャン、Dependabot、シークレットスキャンに依存しない、Copilot 主導のスキャンと説明している。コミット前のオンデマンドレビューによって既存ツールを補完するが、すべての脆弱性を検出するという証拠ではない。

검토 초점: インストール済みの CLI で機能の利用可否を確認し、検出事項を手動で精査する。決定論的なセキュリティチェックを維持し、プレビューのスキャンで問題が見つからなくても安全性の認証とは捉えない。

### Deutsch (de)

Copilot CLI: Sicherheitsreview bleibt eine experimentelle Vorschau

1. GitHub hat den Befehl /security-review für lokale Codeänderungen als experimentelle Funktion in öffentlicher Vorschau eingeführt. Zum Ausprobieren müssen Nutzer den experimentellen Modus aktivieren.

2. Die Ankündigung beschreibt einen Copilot-gesteuerten Scan, der nicht auf GitHub-Code-Scanning, Dependabot oder Secret-Scanning angewiesen ist. Er ergänzt diese Werkzeuge durch Reviews auf Abruf vor dem Commit; dies ist kein Nachweis dafür, dass sämtliche Schwachstellen erkannt werden.

검토 초점: Die Verfügbarkeit der Funktion in der installierten CLI prüfen und Befunde manuell untersuchen. Deterministische Sicherheitsprüfungen beibehalten und einen Preview-Scan ohne Befunde nicht als Sicherheitszertifizierung behandeln.

### Français (fr)

Copilot CLI : la revue de sécurité reste une préversion expérimentale

1. GitHub a introduit la commande /security-review pour les modifications de code locales sous la forme d’une fonctionnalité expérimentale en préversion publique. Les utilisateurs doivent activer le mode expérimental pour l’essayer.

2. L’annonce décrit une analyse pilotée par Copilot qui ne repose ni sur l’analyse de code GitHub, ni sur Dependabot, ni sur la détection de secrets. Elle complète ces outils par une revue à la demande avant le commit ; cela ne prouve pas que toutes les vulnérabilités seront détectées.

검토 초점: Vérifier la disponibilité de la fonctionnalité dans la CLI installée et examiner les résultats manuellement. Conserver les contrôles de sécurité déterministes et ne pas considérer une analyse de préversion sans anomalie comme une certification de sécurité.

### Русский (ru)

Copilot CLI: проверка безопасности остаётся экспериментальной предварительной функцией

1. GitHub представила команду /security-review для локальных изменений кода как экспериментальную функцию в публичной предварительной версии. Чтобы опробовать команду, пользователи должны включить экспериментальный режим.

2. В объявлении описано сканирование под управлением Copilot, которое не опирается на сканирование кода GitHub, Dependabot или сканирование секретов. Оно дополняет эти инструменты проверкой по запросу перед коммитом; это не доказывает, что будут обнаружены все уязвимости.

검토 초점: Проверьте доступность функции в установленной CLI и изучите находки вручную. Сохраните детерминированные проверки безопасности и не считайте отсутствие находок при предварительном сканировании сертификатом безопасности.

## Tracking-service case study: event schemas and non-blocking delivery

원문: https://www.infoq.com/presentations/mobile-user-tracking-service/

검토 기준: 영어 보강본 c505a5c997b12684, 2026-10-25T12:40:05+00:00

### 영어 기준본

1. In the published transcript, Alina Krasavina describes Delivery Hero’s internal tracking service using mobile and frontend SDKs, an ingestion API, real-time consumers and BigQuery storage. This is the speaker’s implementation account.

> we have a mobile SDK, and a frontend SDK, in TypeScript, to collect the data and to send to our API.

근거: https://www.infoq.com/presentations/mobile-user-tracking-service/

> our data storage, which is BigQuery

근거: https://www.infoq.com/presentations/mobile-user-tracking-service/

2. The speaker says code-generated event models exposed schema problems during application compilation, while a device queue and background batched sending supported non-blocking delivery. The reported cost and capture-rate figures are excluded from this scoped summary.

> we introduced code generated event models

근거: https://www.infoq.com/presentations/mobile-user-tracking-service/

> you have an error on compilation time

근거: https://www.infoq.com/presentations/mobile-user-tracking-service/

> it reads from the queue, takes a batch of some events, and is sending to our API.

근거: https://www.infoq.com/presentations/mobile-user-tracking-service/

검토 초점: Treat the transcript as primary evidence of what the speaker reported, not independent replication. Evaluate schema ownership, buffering limits, delivery failures, privacy requirements and migration parity for your own workload.

### 简体中文 (zh-CN)

追踪服务案例：事件模式与非阻塞传送

1. 在已发布的演讲文字稿中，Alina Krasavina 描述了 Delivery Hero 的内部追踪服务，涉及移动端和前端 SDK、数据接入 API、实时消费者及 BigQuery 存储。这是演讲者对其实现的叙述。

2. 演讲者表示，自动生成的事件模型使模式问题在应用编译时暴露出来，而设备端队列和后台批量发送支持非阻塞传送。本篇限定范围的摘要不包含所报告的成本和采集率数据。

검토 초점: 将文字稿视为演讲者所报告内容的一手证据，而非独立复现。针对自己的工作负载，评估模式归属责任、缓冲限制、传送失败、隐私要求和迁移前后的一致性。

### 日本語 (ja)

トラッキングサービスの事例：イベントスキーマとノンブロッキング配信

1. 公開された講演の書き起こしで、Alina Krasavina は Delivery Hero の社内トラッキングサービスについて、モバイルおよびフロントエンドの SDK、取り込み API、リアルタイムのコンシューマー、BigQuery ストレージを使う構成を説明している。これは登壇者による実装の報告である。

2. 登壇者によると、コード生成したイベントモデルによりアプリケーションのコンパイル時にスキーマの問題が表面化し、端末のキューとバックグラウンドのバッチ送信によりノンブロッキング配信を支えたという。報告されたコストや取得率の数値は、対象を限定したこの要約には含めていない。

검토 초점: 書き起こしは登壇者の報告内容に関する一次資料として扱い、独立した再現とは捉えない。自分のワークロードで、スキーマの管理責任、バッファの上限、配信失敗、プライバシー要件、移行前後の同等性を評価する。

### Deutsch (de)

Fallstudie zum Trackingdienst: Ereignisschemata und nicht blockierende Übermittlung

1. Im veröffentlichten Transkript beschreibt Alina Krasavina den internen Trackingdienst von Delivery Hero mit Mobil- und Frontend-SDKs, einer Ingestion-API, Echtzeit-Consumern und BigQuery als Speicher. Dies ist der Implementierungsbericht der Vortragenden.

2. Die Vortragende berichtet, dass per Codegenerierung erzeugte Ereignismodelle Schemaprobleme beim Kompilieren der Anwendung sichtbar machten. Eine Gerätewarteschlange und gebündeltes Senden im Hintergrund unterstützten die nicht blockierende Übermittlung. Die berichteten Kostenzahlen und Erfassungsraten sind aus dieser inhaltlich begrenzten Zusammenfassung ausgenommen.

검토 초점: Das Transkript als Primärbeleg für den Bericht der Vortragenden behandeln, nicht als unabhängige Replikation. Für die eigene Arbeitslast die Verantwortung für Schemata, Puffergrenzen, Übermittlungsfehler, Datenschutzanforderungen und Gleichwertigkeit bei der Migration bewerten.

### Français (fr)

Étude d’un service de suivi : schémas d’événements et transmission non bloquante

1. Dans la transcription publiée, Alina Krasavina décrit le service de suivi interne de Delivery Hero, qui utilise des SDK mobiles et frontend, une API d’ingestion, des consommateurs en temps réel et un stockage BigQuery. Il s’agit du récit de l’implémentation par l’intervenante.

2. Selon l’intervenante, les modèles d’événements générés par code faisaient apparaître les problèmes de schéma à la compilation de l’application, tandis qu’une file d’attente sur l’appareil et des envois groupés en arrière-plan permettaient une transmission non bloquante. Les chiffres de coût et de taux de collecte rapportés sont exclus de ce résumé au périmètre limité.

검토 초점: Considérer la transcription comme une source primaire de ce que l’intervenante a rapporté, et non comme une reproduction indépendante. Évaluer, pour sa propre charge de travail, la responsabilité des schémas, les limites de mise en tampon, les échecs de transmission, les exigences de confidentialité et la parité lors de la migration.

### Русский (ru)

Кейс сервиса отслеживания: схемы событий и неблокирующая доставка

1. В опубликованной расшифровке Alina Krasavina описывает внутренний сервис отслеживания Delivery Hero с мобильными и фронтенд-SDK, API приёма данных, потребителями в реальном времени и хранилищем BigQuery. Это рассказ докладчицы о реализации.

2. По словам докладчицы, сгенерированные модели событий выявляли проблемы схемы при компиляции приложения, а очередь на устройстве и фоновая пакетная отправка обеспечивали неблокирующую доставку. Приведённые в докладе показатели стоимости и доли собранных событий исключены из этого обзора с ограниченным охватом.

검토 초점: Рассматривайте расшифровку как первичное свидетельство того, что сообщила докладчица, а не как независимое воспроизведение. Для своей нагрузки оцените ответственность за схемы, ограничения буферизации, сбои доставки, требования к конфиденциальности и эквивалентность при миграции.

## eMudhra incident: audit application trust as well as client updates

원문: https://blog.cloudflare.com/emudhra-certificate-compromise/

검토 기준: 영어 보강본 c78cf468160e1a45, 2026-10-25T05:21:13+00:00

### 영어 기준본

1. Cloudflare instructed Tunnel customers to upgrade cloudflared to 2026.10.2 and redeploy fixed container images where applicable. This is the version in the incident notice, not a claim about the latest version.

> Upgrade to 2026.10.2 .

근거: https://blog.cloudflare.com/emudhra-certificate-compromise/

2. The notice warns that updating an SDK alone may leave the underlying certificate-verification policy unchanged.

> Updating the SDK alone may not change the underlying policy.

근거: https://blog.cloudflare.com/emudhra-certificate-compromise/

3. Cloudflare warns against resolving certificate errors by disabling verification.

> not resolve these errors by disabling verification

근거: https://blog.cloudflare.com/emudhra-certificate-compromise/

검토 초점: Trace which HTTP library, runtime and trust store each application actually uses. A successful browser request is not sufficient evidence that every application path is protected; validate the relevant clients without disabling verification.

### 简体中文 (zh-CN)

eMudhra 事件：更新客户端之外，还需审查应用的信任配置

1. Cloudflare 指示 Tunnel 客户将 cloudflared 升级到 2026.10.2，并在适用时重新部署已修复的容器镜像。这是事件公告中的版本，并非声称它是最新版本。

2. 公告警告，仅更新 SDK 可能不会改变底层的证书验证策略。

3. Cloudflare 警告，不要通过禁用验证来解决证书错误。

검토 초점: 追查每个应用实际使用的 HTTP 库、运行时和信任存储。浏览器请求成功不足以证明应用的每条调用路径都受到保护；应在不禁用验证的情况下验证相关客户端。

### 日本語 (ja)

eMudhra の事案：クライアント更新に加えてアプリの信頼設定を点検

1. Cloudflare は Tunnel の利用者に、cloudflared を 2026.10.2 にアップグレードし、該当する場合は修正済みコンテナイメージを再デプロイするよう指示した。これは事案の告知に記載されたバージョンであり、最新バージョンだという主張ではない。

2. 告知は、SDK の更新だけでは基盤となる証明書検証ポリシーが変わらない可能性があると警告している。

3. Cloudflare は、検証を無効にして証明書エラーを解消しないよう警告している。

검토 초점: 各アプリケーションが実際に使う HTTP ライブラリ、ランタイム、信頼ストアを追跡する。ブラウザーのリクエストが成功しても、アプリケーションのすべての処理経路が保護されている証拠としては不十分である。検証を無効にせず、該当するクライアントを検証する。

### Deutsch (de)

eMudhra-Vorfall: Neben Clientupdates auch die Vertrauenskonfiguration von Anwendungen prüfen

1. Cloudflare wies Tunnel-Kunden an, cloudflared auf 2026.10.2 zu aktualisieren und gegebenenfalls korrigierte Containerimages erneut bereitzustellen. Dies ist die Version aus der Vorfallsmeldung, keine Aussage über die neueste Version.

2. Die Meldung warnt davor, dass ein SDK-Update allein die zugrunde liegende Richtlinie zur Zertifikatsprüfung möglicherweise unverändert lässt.

3. Cloudflare warnt davor, Zertifikatsfehler durch das Abschalten der Prüfung zu beheben.

검토 초점: Nachverfolgen, welche HTTP-Bibliothek, Laufzeitumgebung und welchen Vertrauensspeicher jede Anwendung tatsächlich nutzt. Eine erfolgreiche Browseranfrage reicht nicht als Nachweis dafür, dass sämtliche Anwendungspfade geschützt sind; die betreffenden Clients prüfen, ohne die Zertifikatsprüfung abzuschalten.

### Français (fr)

Incident eMudhra : auditer la confiance des applications en plus de mettre à jour les clients

1. Cloudflare a demandé aux clients Tunnel de mettre à niveau cloudflared vers 2026.10.2 et de redéployer les images de conteneurs corrigées le cas échéant. Il s’agit de la version indiquée dans l’avis d’incident, sans affirmer que c’est la plus récente.

2. L’avis prévient qu’une mise à jour du SDK seule peut laisser inchangée la politique sous-jacente de vérification des certificats.

3. Cloudflare met en garde contre la résolution des erreurs de certificat par la désactivation de la vérification.

검토 초점: Identifier la bibliothèque HTTP, l’environnement d’exécution et le magasin de confiance réellement utilisés par chaque application. Une requête réussie dans le navigateur ne suffit pas à prouver que tous les chemins d’exécution des applications sont protégés ; valider les clients concernés sans désactiver la vérification.

### Русский (ru)

Инцидент eMudhra: кроме обновления клиентов проверьте настройки доверия приложений

1. Cloudflare поручила клиентам Tunnel обновить cloudflared до 2026.10.2 и, где применимо, повторно развернуть исправленные образы контейнеров. Это версия из уведомления об инциденте, а не утверждение о последней версии.

2. В уведомлении предупреждается, что одного обновления SDK может быть недостаточно для изменения базовой политики проверки сертификатов.

3. Cloudflare предостерегает от устранения ошибок сертификатов путём отключения проверки.

검토 초점: Проследите, какую HTTP-библиотеку, среду выполнения и хранилище доверия фактически использует каждое приложение. Успешный запрос из браузера не доказывает, что защищены все пути выполнения приложения; проверьте соответствующие клиенты, не отключая проверку сертификатов.

## Windows agent containment: early preview and audit-mode limits

원문: https://www.infoq.com/news/2026/06/windows-security-agents/

검토 기준: 영어 보강본 ce26c7555a2bf537, 2026-10-25T12:40:05+00:00

### 영어 기준본

1. Microsoft introduced the MXC SDK as an early preview: a policy-driven execution layer for agents on Windows and WSL. An SDK announcement is not independent evidence that arbitrary agent workloads are safe.

> an early preview of the Microsoft Execution Containers (MXC) SDK

근거: https://blogs.windows.com/windowsdeveloper/2026/06/02/windows-platform-security-for-ai-agents/

> a cross-platform, policy-driven execution layer for agents on Windows and WSL.

근거: https://blogs.windows.com/windowsdeveloper/2026/06/02/windows-platform-security-for-ai-agents/

2. The announcement describes multiple isolation constructs behind a shared policy model. It labels Linux-container support and MXC cloud integration as future work, so those plans should not be presented as delivered features at announcement time.

> Linux containers Will bring the containment model to Linux-first agent toolchains via WSL.

근거: https://blogs.windows.com/windowsdeveloper/2026/06/02/windows-platform-security-for-ai-agents/

> With the future addition of MXC integration

근거: https://blogs.windows.com/windowsdeveloper/2026/06/02/windows-platform-security-for-ai-agents/

후속 확인:

- At review time, the MXC repository warns that --audit disables all sandbox security for the analyzed workload and must never be used to run untrusted code. Policy-authoring audit mode is not a containment guarantee.

검토 초점: Verify the actual backend, operating-system support, filesystem access and network behavior in a representative environment. This is a source-context review without sandbox-escape or containment testing.

### 简体中文 (zh-CN)

Windows 智能体隔离：早期预览与审计模式的限制

1. Microsoft 推出了早期预览版 MXC SDK，作为面向 Windows 和 WSL 智能体的策略驱动执行层。SDK 公告并不能独立证明任意智能体工作负载都是安全的。

2. 公告描述了共享策略模型下的多种隔离机制。它将 Linux 容器支持和 MXC 云集成列为未来工作，因此不应将这些计划表述为公告发布时已经交付的功能。

후속 확인:

- 在本次审阅时，MXC 仓库警告：--audit 会关闭被分析工作负载的所有沙箱安全防护，绝不能用于运行不受信任的代码。用于编写策略的审计模式并不保证隔离。

검토 초점: 在具有代表性的环境中验证实际后端、操作系统支持、文件系统访问和网络行为。这是基于来源上下文的审阅，未进行沙箱逃逸或隔离测试。

### 日本語 (ja)

Windows のエージェント隔離：初期プレビューと監査モードの限界

1. Microsoft は MXC SDK を初期プレビューとして紹介した。これは Windows と WSL 上のエージェント向けに、ポリシーに基づく実行レイヤーを提供するものだ。SDK の発表は、任意のエージェントワークロードの安全性を示す独立した証拠ではない。

2. 発表では、共通のポリシーモデルの下で複数の隔離機構を利用すると説明している。Linux コンテナのサポートと MXC のクラウド統合は今後の作業とされており、発表時に提供済みの機能として扱うべきではない。

후속 확인:

- レビュー時点の MXC リポジトリは、--audit が分析対象のワークロードのサンドボックス保護をすべて無効にし、信頼できないコードの実行に絶対に使ってはならないと警告している。ポリシー作成用の監査モードは隔離を保証しない。

검토 초점: 代表的な環境で、実際のバックエンド、OS のサポート、ファイルシステムへのアクセス、ネットワーク動作を検証する。これは出典の文脈を確認したレビューであり、サンドボックス脱出や隔離のテストは行っていない。

### Deutsch (de)

Windows-Agenten isolieren: Frühe Vorschau und Grenzen des Audit-Modus

1. Microsoft stellte das MXC SDK als frühe Vorschau vor: eine richtliniengesteuerte Ausführungsschicht für Agenten auf Windows und WSL. Die Ankündigung eines SDK ist kein unabhängiger Nachweis dafür, dass beliebige Agenten-Workloads sicher sind.

2. Die Ankündigung beschreibt mehrere Isolationsmechanismen unter einem gemeinsamen Richtlinienmodell. Sie bezeichnet die Unterstützung für Linux-Container und die MXC-Cloudintegration als künftige Arbeiten; diese Pläne sollten daher nicht als zum Ankündigungszeitpunkt bereits gelieferte Funktionen dargestellt werden.

후속 확인:

- Zum Zeitpunkt dieser Prüfung warnt das MXC-Repository, dass --audit sämtliche Sandbox-Sicherheitsmaßnahmen für den analysierten Workload abschaltet und niemals zum Ausführen nicht vertrauenswürdigen Codes verwendet werden darf. Der Audit-Modus zur Richtlinienerstellung garantiert keine Isolation.

검토 초점: Das tatsächliche Backend, die Betriebssystemunterstützung, Dateisystemzugriffe und das Netzwerkverhalten in einer repräsentativen Umgebung überprüfen. Dies ist eine Prüfung des Quellenkontexts ohne Tests auf Sandbox-Ausbrüche oder Isolation.

### Français (fr)

Confinement des agents Windows : préversion initiale et limites du mode audit

1. Microsoft a présenté le SDK MXC en préversion initiale : une couche d’exécution fondée sur des politiques pour les agents sous Windows et WSL. L’annonce d’un SDK ne constitue pas une preuve indépendante de la sûreté de charges de travail d’agents quelconques.

2. L’annonce décrit plusieurs mécanismes d’isolation derrière un modèle de politique commun. Elle présente la prise en charge des conteneurs Linux et l’intégration cloud MXC comme des travaux futurs ; ces projets ne doivent donc pas être décrits comme des fonctionnalités livrées au moment de l’annonce.

후속 확인:

- Au moment de cette revue, le dépôt MXC avertit que --audit désactive toutes les protections de sécurité de la sandbox pour la charge analysée et ne doit jamais servir à exécuter du code non fiable. Le mode audit destiné à la rédaction des politiques ne garantit pas le confinement.

검토 초점: Vérifier le backend réel, la prise en charge des systèmes d’exploitation, les accès au système de fichiers et le comportement réseau dans un environnement représentatif. Il s’agit d’une revue du contexte des sources, sans test d’évasion de sandbox ni de confinement.

### Русский (ru)

Изоляция агентов Windows: ранняя предварительная версия и ограничения режима аудита

1. Microsoft представила SDK MXC в ранней предварительной версии: управляемый политиками слой выполнения для агентов в Windows и WSL. Объявление SDK не является независимым доказательством безопасности произвольных нагрузок агентов.

2. В объявлении описаны несколько механизмов изоляции с общей моделью политик. Поддержка контейнеров Linux и облачная интеграция MXC обозначены как будущие работы, поэтому эти планы нельзя представлять как функции, уже поставленные на момент объявления.

후속 확인:

- На момент этой проверки репозиторий MXC предупреждает, что --audit отключает все средства безопасности песочницы для анализируемой нагрузки и его категорически нельзя использовать для запуска недоверенного кода. Режим аудита для составления политик не гарантирует изоляцию.

검토 초점: Проверьте фактический бэкенд, поддержку операционных систем, доступ к файловой системе и поведение сети в репрезентативной среде. Это проверка контекста источников без тестирования выхода из песочницы или изоляции.

## npm installation defaults and staged token restrictions

원문: https://github.blog/changelog/2026-07-08-npm-install-time-security-and-gat-bypass2fa-deprecation

검토 기준: 영어 보강본 d123262315e62321, 2026-10-25T17:03:04+00:00

### 영어 기준본

1. The npm 12 announcement makes dependency lifecycle scripts and implicit node-gyp builds opt-in, and defaults Git and remote-URL dependency resolution to none unless explicitly allowed. These are installation defaults, not a guarantee that installed code is harmless.

> Dependency lifecycle scripts (i.e., preinstall , install , postinstall ) and implicit node-gyp builds no longer run unless explicitly allowed.

근거: https://github.blog/changelog/2026-07-08-npm-install-time-security-and-gat-bypass2fa-deprecation

> --allow-git defaults to none

근거: https://github.blog/changelog/2026-07-08-npm-install-time-security-and-gat-bypass2fa-deprecation

> --allow-remote defaults to none

근거: https://github.blog/changelog/2026-07-08-npm-install-time-security-and-gat-bypass2fa-deprecation

2. The same notice planned removal of sensitive management actions from npm 2FA-bypass tokens for early 2026-08. It separately targeted direct-publish restrictions for around 2027-01, with trusted publishing or human-approved staged publishing as migration paths.

> We expect this change to take effect in early August 2026.

근거: https://github.blog/changelog/2026-07-08-npm-install-time-security-and-gat-bypass2fa-deprecation

> We expect this change to take effect around January 2027.

근거: https://github.blog/changelog/2026-07-08-npm-install-time-security-and-gat-bypass2fa-deprecation

> move automated publishing to trusted publishing (OIDC) or staged publishing with a human approval step

근거: https://github.blog/changelog/2026-07-08-npm-install-time-security-and-gat-bypass2fa-deprecation

후속 확인:

- The 2026-07-31 follow-up says npm 2FA-bypass granular access tokens can no longer perform sensitive management actions and requires an interactive 2FA challenge. It explicitly excludes GitHub personal access tokens, GitHub App tokens and GITHUB_TOKEN from that change.
- That follow-up still describes removal of direct publishing as a target for 2027-01. It does not report that later publishing restriction as completed.

검토 초점: Test native builds and dependency sources before upgrading, and review script allowlists rather than enabling everything. Verify current publishing support for your CI provider; a schedule announcement is not proof that every registry action has already changed.

### 简体中文 (zh-CN)

npm 安装默认行为与分阶段的令牌限制

1. npm 12 公告将依赖生命周期脚本和隐式 node-gyp 构建改为需明确允许才会执行，并将 Git 和远程 URL 依赖解析的默认值设为 none，除非明确允许。这些是安装默认行为，并不保证安装的代码无害。

2. 同一公告计划在 2026-08 月初移除 npm 2FA 绕过令牌执行敏感管理操作的能力。另外，公告将直接发布限制的目标时间定为 2027-01 左右，并提供可信发布或需人工批准的暂存发布作为迁移路径。

후속 확인:

- 2026-07-31 的后续公告表示，配置为绕过 2FA 的 npm 细粒度访问令牌已无法执行敏感管理操作，相关操作需要交互式 2FA 验证。公告明确说明，此变更不影响 GitHub 个人访问令牌、GitHub App 令牌和 GITHUB_TOKEN。
- 该后续公告仍将移除直接发布能力描述为 2027-01 的目标，并未报告这一较晚的发布限制已经完成。

검토 초점: 升级前应测试原生构建和依赖来源，并审查脚本允许列表，而不是允许所有脚本。核实 CI 提供商当前支持的发布方式；时间表公告不能证明所有注册表操作都已经变更。

### 日本語 (ja)

npm のインストール既定値と段階的なトークン制限

1. npm 12 の発表では、依存パッケージのライフサイクルスクリプトと暗黙的な node-gyp ビルドを明示的な許可が必要な方式にし、Git とリモート URL の依存関係の解決も、明示的に許可しない限り既定値を none としている。これらはインストール時の既定値であり、インストールしたコードが無害だという保証ではない。

2. 同じ告知では、2FA をバイパスする npm トークンから機密性の高い管理操作の権限を外す時期を 2026-08 上旬と予定していた。また、直接公開の制限は 2027-01 頃を目標とし、移行先として信頼された公開方式（trusted publishing）、または人の承認を伴うステージング公開（staged publishing）を示していた。

후속 확인:

- 2026-07-31 の続報によると、2FA のバイパスを設定した npm の細粒度アクセストークンは、機密性の高い管理操作を実行できなくなり、対話的な 2FA 認証が必要となった。この変更から GitHub の個人アクセストークン、GitHub App トークン、GITHUB_TOKEN は明示的に除外されている。
- この続報でも、直接公開の廃止は 2027-01 を目標としている。その後の公開制限が完了したとは報告していない。

검토 초점: アップグレード前にネイティブビルドと依存関係の取得元をテストし、すべてを許可するのではなくスクリプトの許可リストを確認する。利用する CI プロバイダーの現在の公開方式のサポートを確認する。予定の告知は、すべてのレジストリ操作がすでに変わったという証拠ではない。

### Deutsch (de)

npm: Installationsvorgaben und gestaffelte Tokenbeschränkungen

1. Die Ankündigung zu npm 12 macht Lebenszyklusskripte von Abhängigkeiten und implizite node-gyp-Builds zustimmungspflichtig. Die Auflösung von Git- und Remote-URL-Abhängigkeiten steht standardmäßig auf none, sofern sie nicht ausdrücklich erlaubt wird. Dies sind Installationsvorgaben, keine Garantie für die Unschädlichkeit installierten Codes.

2. Dieselbe Mitteilung plante für Anfang 2026-08, npm-Tokens mit 2FA-Umgehung sensible Verwaltungsaktionen zu entziehen. Unabhängig davon waren Beschränkungen für direktes Veröffentlichen für etwa 2027-01 vorgesehen, mit Trusted Publishing oder Staged Publishing mit menschlicher Freigabe als Migrationswegen.

후속 확인:

- Laut der Folgemitteilung vom 2026-07-31 können granulare npm-Zugriffstokens, die zur Umgehung von 2FA konfiguriert sind, keine sensiblen Verwaltungsaktionen mehr ausführen; dafür ist eine interaktive 2FA-Prüfung erforderlich. GitHub-Personal-Access-Tokens, GitHub-App-Tokens und GITHUB_TOKEN sind von dieser Änderung ausdrücklich ausgenommen.
- Diese Folgemitteilung nennt für die Abschaffung des direkten Veröffentlichens weiterhin 2027-01 als Ziel. Sie meldet diese spätere Veröffentlichungsbeschränkung nicht als abgeschlossen.

검토 초점: Vor einem Upgrade native Builds und Abhängigkeitsquellen testen und Skript-Positivlisten prüfen, statt alles freizugeben. Die aktuell unterstützten Veröffentlichungswege des eigenen CI-Anbieters überprüfen; ein angekündigter Zeitplan beweist nicht, dass sämtliche Registry-Aktionen bereits geändert wurden.

### Français (fr)

npm : paramètres d’installation par défaut et restrictions progressives des jetons

1. L’annonce de npm 12 soumet les scripts de cycle de vie des dépendances et les compilations implicites node-gyp à une autorisation explicite. La résolution des dépendances Git et par URL distante est réglée par défaut sur none, sauf autorisation explicite. Ce sont des paramètres d’installation, sans garantie que le code installé soit inoffensif.

2. La même annonce prévoyait de retirer aux jetons npm contournant la 2FA la possibilité d’effectuer des opérations de gestion sensibles au début de 2026-08. Elle visait séparément des restrictions sur la publication directe vers 2027-01, avec pour voies de migration la publication de confiance (trusted publishing) ou la publication en attente d’approbation humaine (staged publishing).

후속 확인:

- Le suivi du 2026-07-31 indique que les jetons d’accès granulaires npm configurés pour contourner la 2FA ne peuvent plus effectuer d’opérations de gestion sensibles, lesquelles nécessitent une vérification 2FA interactive. Il exclut explicitement de ce changement les jetons d’accès personnels GitHub, les jetons GitHub App et GITHUB_TOKEN.
- Ce suivi présente toujours la suppression de la publication directe comme un objectif pour 2027-01. Il ne rapporte pas que cette restriction ultérieure de publication a été mise en place.

검토 초점: Tester les compilations natives et les sources des dépendances avant la mise à niveau, et examiner les listes d’autorisation des scripts plutôt que de tout autoriser. Vérifier les modes de publication actuellement pris en charge par le fournisseur CI ; un calendrier annoncé ne prouve pas que toutes les opérations du registre ont déjà changé.

### Русский (ru)

npm: настройки установки по умолчанию и поэтапные ограничения токенов

1. Объявление npm 12 переводит скрипты жизненного цикла зависимостей и неявные сборки node-gyp в режим явного разрешения. Для разрешения зависимостей из Git и по удалённым URL по умолчанию установлено none, если нет явного разрешения. Это настройки установки, а не гарантия безвредности установленного кода.

2. То же уведомление планировало на начало 2026-08 лишить npm-токены с обходом 2FA возможности выполнять чувствительные операции управления. Отдельно ограничения прямой публикации намечались примерно на 2027-01, а путями перехода назывались доверенная публикация (trusted publishing) или публикация с предварительным одобрением человеком (staged publishing).

후속 확인:

- В дополнении от 2026-07-31 сказано, что гранулярные токены доступа npm, настроенные на обход 2FA, больше не могут выполнять чувствительные операции управления: для них требуется интерактивная проверка 2FA. Из этого изменения явно исключены персональные токены доступа GitHub, токены GitHub App и GITHUB_TOKEN.
- Это дополнение по-прежнему указывает 2027-01 как целевой срок отмены прямой публикации. Оно не сообщает, что это более позднее ограничение публикации уже введено.

검토 초점: Перед обновлением протестируйте нативные сборки и источники зависимостей, а также проверьте списки разрешённых скриптов вместо разрешения всего подряд. Уточните, какие способы публикации сейчас поддерживает ваш CI-провайдер; объявленный график не доказывает, что уже изменились все операции реестра.

