# 다국어 번역 검토 초안

의미·용어·조건 대조와 대상 언어 교정은 AI로 검토합니다. 수치·제품명 검사는 의미 검토를 대체하지 않습니다. 사이트 게시는 사용자의 명시적 승인 후에 진행합니다.

## Cloudflare roadmap includes post-quantum authentication

원문: https://blog.cloudflare.com/post-quantum-roadmap/

검토 기준: 영어 보강본 fb47d93f2cc47316, 2026-10-25T05:38:18+00:00

### 영어 기준본

1. Cloudflare announced a target of 2029 for full post-quantum security, explicitly including authentication. This is a roadmap target rather than a completed migration.

> target 2029 to be fully post-quantum

근거: https://blog.cloudflare.com/post-quantum-roadmap/

2. The announcement distinguishes post-quantum encryption from authentication and says the work is incomplete until authentication is upgraded.

> work is not done until authentication is also upgraded.

근거: https://blog.cloudflare.com/post-quantum-roadmap/

검토 초점: Inventory key exchange, certificates and signing dependencies separately. Confirm the current product-specific roadmap before scheduling changes; the historical date is not a migration guarantee for every deployment.

### 简体中文 (zh-CN)

Cloudflare 路线图涵盖后量子身份认证

1. Cloudflare 宣布以 2029 年为实现全面后量子安全的目标，明确包括身份认证。这是路线图目标，并非已经完成迁移。

2. 公告区分了后量子加密与身份认证，并表示在身份认证也完成升级之前，这项工作仍未完成。

검토 초점: 分别盘点密钥交换、证书和签名方面的依赖。在安排变更之前，核实各产品当前的路线图；这一历史目标日期并不保证所有部署都能完成迁移。

### 日本語 (ja)

Cloudflare のロードマップに含まれる耐量子認証

1. Cloudflare は、認証を明示的に含む全面的な耐量子セキュリティの実現目標を 2029 年と発表した。これはロードマップ上の目標であり、移行が完了したという意味ではない。

2. 発表では耐量子暗号化と認証を区別し、認証もアップグレードするまでは取り組みは完了しないと述べている。

검토 초점: 鍵交換、証明書、署名の依存関係を別々に把握する。変更を予定する前に、現在の製品別ロードマップを確認する。過去に示された日付は、すべての環境での移行を保証するものではない。

### Deutsch (de)

Cloudflares Roadmap umfasst Post-Quanten-Authentifizierung

1. Cloudflare kündigte 2029 als Ziel für vollständige Post-Quanten-Sicherheit an, ausdrücklich einschließlich der Authentifizierung. Dies ist ein Roadmap-Ziel und keine abgeschlossene Migration.

2. Die Ankündigung unterscheidet Post-Quanten-Verschlüsselung von Authentifizierung und erklärt, dass die Arbeit erst abgeschlossen ist, wenn auch die Authentifizierung aktualisiert wurde.

검토 초점: Abhängigkeiten bei Schlüsselaustausch, Zertifikaten und Signaturen getrennt erfassen. Vor der Planung von Änderungen die aktuelle produktspezifische Roadmap prüfen; das historisch genannte Datum garantiert keine Migration für jede Bereitstellung.

### Français (fr)

La feuille de route de Cloudflare inclut l’authentification post-quantique

1. Cloudflare a annoncé viser 2029 pour une sécurité entièrement post-quantique, en incluant explicitement l’authentification. C’est un objectif de feuille de route, sans indiquer une migration achevée.

2. L’annonce distingue le chiffrement post-quantique de l’authentification et précise que le travail reste incomplet tant que l’authentification n’est pas elle aussi mise à niveau.

검토 초점: Inventorier séparément les dépendances liées à l’échange de clés, aux certificats et aux signatures. Confirmer la feuille de route actuelle de chaque produit avant de planifier des changements ; la date historique ne garantit pas la migration de tous les déploiements.

### Русский (ru)

Дорожная карта Cloudflare включает постквантовую аутентификацию

1. Cloudflare объявила 2029 год целевым сроком достижения полной постквантовой безопасности, явно включая аутентификацию. Это цель дорожной карты, а не завершённая миграция.

2. Объявление различает постквантовое шифрование и аутентификацию и указывает, что работа не завершена, пока аутентификация также не обновлена.

검토 초점: Отдельно составьте перечень зависимостей обмена ключами, сертификатов и подписей. Перед планированием изменений проверьте актуальную дорожную карту конкретного продукта; исторически указанная дата не гарантирует миграцию каждого развёртывания.

## Copilot app security review: preview scope and review limits

원문: https://github.blog/changelog/2026-07-14-security-reviews-now-available-in-the-github-copilot-app

검토 기준: 영어 보강본 fe469724f5828fb0, 2026-10-25T17:03:04+00:00

### 영어 기준본

1. GitHub introduced the Copilot app /security-review command in public preview for current workstream changes. The announcement described severity- and confidence-scored findings with actionable suggestions, not a proof that every vulnerability would be found.

> The /security-review slash command is shipping in public preview

근거: https://github.blog/changelog/2026-07-14-security-reviews-now-available-in-the-github-copilot-app

> High-confidence security findings, scored by severity and confidence.

근거: https://github.blog/changelog/2026-07-14-security-reviews-now-available-in-the-github-copilot-app

2. The command complements code scanning, Dependabot and secret scanning with an on-demand local-change review. At launch, it was available to Copilot Free, Pro, Business and Enterprise users during public preview; the notice does not establish permanent pricing or continued availability.

> It complements GitHub code scanning, Dependabot, and secret scanning

근거: https://github.blog/changelog/2026-07-14-security-reviews-now-available-in-the-github-copilot-app

> The command is available to Copilot Free, Pro, Business, and Enterprise users during public preview.

근거: https://github.blog/changelog/2026-07-14-security-reviews-now-available-in-the-github-copilot-app

검토 초점: Confirm installed-app support and current plan terms, then validate each suggestion with tests and review. A clean AI review should not be treated as a security certification or a substitute for release controls.

### 简体中文 (zh-CN)

Copilot 应用安全审查：预览范围与审查限制

1. GitHub 在公开预览中推出了 Copilot 应用的 /security-review 命令，用于当前工作流中的变更。公告介绍了按严重程度和置信度评分的发现，并附带可采取行动的建议，但这不能证明所有漏洞都会被发现。

2. 该命令通过按需审查本地变更，补充代码扫描、Dependabot 和机密扫描。在发布时的公开预览期间，Copilot Free、Pro、Business 和 Enterprise 用户都可使用；公告不能据此确定永久定价或持续可用性。

검토 초점: 确认已安装应用的支持情况与当前套餐条款，再通过测试和审查验证每项建议。未发现问题的 AI 审查不应视为安全认证，也不能代替发布控制。

### 日本語 (ja)

Copilot アプリのセキュリティレビュー：プレビューの範囲と限界

1. GitHub は、現在のワークストリームの変更を対象とする Copilot アプリの /security-review コマンドをパブリックプレビューで導入した。告知では、重大度と確信度で評価された検出事項に具体的な対応につながる提案を添えると説明しており、すべての脆弱性が見つかることを証明するものではない。

2. このコマンドは、ローカルの変更をオンデマンドでレビューし、コードスキャン、Dependabot、シークレットスキャンを補完する。公開時はパブリックプレビュー中に Copilot Free、Pro、Business、Enterprise のユーザーが利用できたが、告知は恒久的な料金や継続的な利用可否を確定するものではない。

검토 초점: インストール済みアプリの対応状況と現在のプラン条件を確認し、各提案をテストとレビューで検証する。指摘のない AI レビューを、安全性の認証やリリース管理の代替と捉えるべきではない。

### Deutsch (de)

Sicherheitsreview der Copilot-App: Vorschauumfang und Prüfgrenzen

1. GitHub führte den Befehl /security-review der Copilot-App in öffentlicher Vorschau für Änderungen im aktuellen Workstream ein. Die Ankündigung beschrieb nach Schweregrad und Konfidenz bewertete Befunde mit umsetzbaren Vorschlägen, keinen Nachweis dafür, dass jede Schwachstelle gefunden wird.

2. Der Befehl ergänzt Code-Scanning, Dependabot und Secret-Scanning durch ein Review lokaler Änderungen auf Abruf. Bei der Einführung stand er während der öffentlichen Vorschau Nutzern von Copilot Free, Pro, Business und Enterprise zur Verfügung; die Mitteilung belegt weder dauerhafte Preise noch eine fortgesetzte Verfügbarkeit.

검토 초점: Die Unterstützung in der installierten App und die aktuellen Tarifbedingungen prüfen, anschließend jeden Vorschlag durch Tests und Review validieren. Ein KI-Review ohne Befunde sollte weder als Sicherheitszertifizierung noch als Ersatz für Releasekontrollen gelten.

### Français (fr)

Revue de sécurité de l’application Copilot : périmètre de la préversion et limites

1. GitHub a introduit en préversion publique la commande /security-review de l’application Copilot pour les modifications du flux de travail courant. L’annonce décrivait des signalements évalués selon la gravité et le niveau de confiance, accompagnés de suggestions permettant d’agir, sans prouver que toutes les vulnérabilités seraient détectées.

2. La commande complète l’analyse de code, Dependabot et la détection de secrets par une revue à la demande des modifications locales. Au lancement, elle était accessible aux utilisateurs de Copilot Free, Pro, Business et Enterprise pendant la préversion publique ; l’annonce ne définit ni une tarification permanente ni une disponibilité continue.

검토 초점: Confirmer la prise en charge dans l’application installée et les conditions actuelles du forfait, puis valider chaque suggestion par des tests et une revue. Une revue par IA sans problème détecté ne doit pas être considérée comme une certification de sécurité ni comme un substitut aux contrôles de publication.

### Русский (ru)

Проверка безопасности в приложении Copilot: охват предварительной версии и пределы ревью

1. GitHub представила команду /security-review приложения Copilot в публичной предварительной версии для изменений текущего рабочего потока. В объявлении описаны находки с оценками серьёзности и уверенности и практическими рекомендациями, а не доказательство обнаружения каждой уязвимости.

2. Команда дополняет сканирование кода, Dependabot и сканирование секретов проверкой локальных изменений по запросу. На момент запуска в период публичной предварительной версии она была доступна пользователям Copilot Free, Pro, Business и Enterprise; уведомление не устанавливает постоянную стоимость или неизменную доступность.

검토 초점: Проверьте поддержку в установленном приложении и актуальные условия тарифа, затем подтвердите каждую рекомендацию тестами и ревью. Проверку ИИ без обнаруженных проблем не следует считать сертификатом безопасности или заменой контроля выпуска.

## Kubernetes 1.36: stable admission mutation and pod user namespaces

원문: https://www.infoq.com/news/2026/05/kubernetes-1-36-released/

검토 기준: 영어 보강본 fecc68bc1f0f9da3, 2026-10-25T06:31:18+00:00

### 영어 기준본

1. The Kubernetes 1.36 release team describes MutatingAdmissionPolicies as graduating to Stable. This is a feature maturity statement for that release.

> graduation of MutatingAdmissionPolicies to Stable.

근거: https://kubernetes.io/blog/2026/04/22/kubernetes-v1-36-release/

2. The same release describes user namespace support for pods as graduating to Stable; it does not establish that every existing cluster is configured to use it.

> support for User Namespaces graduates to Stable.

근거: https://kubernetes.io/blog/2026/04/22/kubernetes-v1-36-release/

검토 초점: Check control-plane version, operating system, container runtime and workload configuration separately. Review migration and compatibility conditions before replacing admission webhooks or enabling user namespaces.

### 简体中文 (zh-CN)

Kubernetes 1.36：准入变更策略与 Pod 用户命名空间进入稳定阶段

1. Kubernetes 1.36 发布团队表示，MutatingAdmissionPolicies 已进入 Stable 阶段。这是对该版本中特性成熟度的说明。

2. 同一版本还说明，Pod 的用户命名空间支持已进入 Stable 阶段；这并不能确定所有现有集群都已配置使用该功能。

검토 초점: 分别检查控制平面版本、操作系统、容器运行时和工作负载配置。在替换准入 Webhook 或启用用户命名空间之前，应审查迁移与兼容性条件。

### 日本語 (ja)

Kubernetes 1.36：変更用のアドミッションポリシーと Pod のユーザー名前空間が安定化

1. Kubernetes 1.36 のリリースチームは、MutatingAdmissionPolicies が Stable に昇格したと説明している。これは当該リリースでの機能の成熟度に関する説明である。

2. 同じリリースでは、Pod のユーザー名前空間サポートも Stable に昇格したと説明している。すべての既存クラスターで利用するよう設定済みだと確認するものではない。

검토 초점: コントロールプレーンのバージョン、OS、コンテナランタイム、ワークロード設定を別々に確認する。アドミッション Webhook の置き換えやユーザー名前空間の有効化の前に、移行と互換性の条件を検討する。

### Deutsch (de)

Kubernetes 1.36: Stabile Admission-Mutation und Benutzer-Namespaces für Pods

1. Das Release-Team von Kubernetes 1.36 beschreibt, dass MutatingAdmissionPolicies den Status Stable erreicht haben. Dies ist eine Aussage zur Funktionsreife in diesem Release.

2. Die Beschreibung desselben Releases nennt auch den Übergang der Unterstützung von Benutzer-Namespaces für Pods zum Status Stable; dies belegt nicht, dass jeder bestehende Cluster für deren Nutzung konfiguriert ist.

검토 초점: Control-Plane-Version, Betriebssystem, Containerlaufzeit und Workload-Konfiguration getrennt prüfen. Vor dem Ersetzen von Admission-Webhooks oder dem Aktivieren von Benutzer-Namespaces die Migrations- und Kompatibilitätsbedingungen prüfen.

### Français (fr)

Kubernetes 1.36 : mutation d’admission et espaces de noms utilisateur des pods stabilisés

1. L’équipe de publication de Kubernetes 1.36 indique que MutatingAdmissionPolicies passe au statut Stable. C’est une indication de maturité de cette fonctionnalité pour cette version.

2. La même version indique que la prise en charge des espaces de noms utilisateur pour les pods passe au statut Stable ; cela n’établit pas que tous les clusters existants sont configurés pour l’utiliser.

검토 초점: Vérifier séparément la version du plan de contrôle, le système d’exploitation, le runtime de conteneurs et la configuration des charges de travail. Examiner les conditions de migration et de compatibilité avant de remplacer les webhooks d’admission ou d’activer les espaces de noms utilisateur.

### Русский (ru)

Kubernetes 1.36: стабильные механизмы изменения при допуске и пространства имён пользователей для подов

1. Команда релиза Kubernetes 1.36 описывает переход MutatingAdmissionPolicies в статус Stable. Это заявление о зрелости функции в данном релизе.

2. В том же релизе поддержка пространств имён пользователей для подов также описана как перешедшая в статус Stable; это не подтверждает, что каждый существующий кластер настроен на её использование.

검토 초점: Отдельно проверьте версию управляющего слоя, операционную систему, среду выполнения контейнеров и конфигурацию нагрузок. Перед заменой admission-вебхуков или включением пространств имён пользователей изучите условия миграции и совместимости.

