# 다국어 번역 검토 초안

의미·용어·조건 대조와 대상 언어 교정은 AI로 검토합니다. 수치·제품명 검사는 의미 검토를 대체하지 않습니다. 사이트 게시는 사용자의 명시적 승인 후에 진행합니다.

## Cloudflare reports lower inference costs for its internal reviewer

원문: https://blog.cloudflare.com/obsessive-inference-optimization/

검토 기준: 영어 보강본 68e2ee5d21f7dc1b, 2026-10-25T05:21:13+00:00

### 영어 기준본

1. Cloudflare reports its internal code reviewer averaged $0.77 per review, down 68% against a $2.43 baseline from its most expensive weeks. These are its workload results, not guaranteed savings for other teams.

> $0.77, down 68% from the $2.43

근거: https://blog.cloudflare.com/obsessive-inference-optimization/

2. The company attributes about 40% of the savings to reviewer-code changes and optimizations, with the remainder coming from model and effort choices.

> About 40% of the savings came from changes and optimizations to the reviewer's code

근거: https://blog.cloudflare.com/obsessive-inference-optimization/

검토 초점: Compare cost only alongside review quality, workload mix and the evaluation period. Reproduce measurements on representative changes before selecting models or reducing effort; this draft contains no local benchmark.

### 简体中文 (zh-CN)

Cloudflare 报告内部代码审查工具的推理成本下降

1. Cloudflare 报告，其内部代码审查工具每次审查平均花费 $0.77，相比开销最高的几周所形成的 $2.43 基线下降了 68%。这些是该公司工作负载的结果，并不保证其他团队也能获得同样的节省。

2. 该公司将约 40% 的节省归因于审查工具自身代码的修改与优化，其余来自模型和推理投入程度的选择。

검토 초점: 比较成本时，应同时考察审查质量、工作负载构成和评估周期。选择模型或降低推理投入前，应在有代表性的变更上复现测量；本草稿不包含本地基准测试。

### 日本語 (ja)

Cloudflare が社内コードレビューツールの推論コスト低下を報告

1. Cloudflare は、社内コードレビューツールの平均費用がレビュー当たり $0.77 となり、最も費用が高かった数週間の $2.43 を基準に 68% 減ったと報告している。これは同社のワークロードでの結果であり、他のチームの削減効果を保証するものではない。

2. 同社は、削減分の約 40% をレビューツール自体のコード変更と最適化に、残りをモデルと推論強度の選択に帰している。

검토 초점: コストはレビュー品質、ワークロードの構成、評価期間と併せて比較する。モデルの選択や推論強度の引き下げの前に、代表的な変更で測定を再現する。この草稿にはローカルのベンチマークは含まれない。

### Deutsch (de)

Cloudflare meldet geringere Inferenzkosten seines internen Code-Reviewers

1. Cloudflare berichtet, dass sein interner Code-Reviewer im Mittel $0.77 pro Review kostete, 68% weniger als die Vergleichsbasis von $2.43 aus seinen teuersten Wochen. Dies sind Ergebnisse für die eigene Arbeitslast, keine garantierten Einsparungen für andere Teams.

2. Das Unternehmen führt etwa 40% der Einsparungen auf Änderungen und Optimierungen am Code des Reviewers zurück. Der Rest entfällt demnach auf die Wahl der Modelle und des Inferenzaufwands.

검토 초점: Kosten nur zusammen mit Review-Qualität, Zusammensetzung der Arbeitslast und Auswertungszeitraum vergleichen. Vor der Modellwahl oder einer Verringerung des Inferenzaufwands Messungen an repräsentativen Änderungen reproduzieren; dieser Entwurf enthält keinen lokalen Benchmark.

### Français (fr)

Cloudflare rapporte une baisse des coûts d’inférence de son outil de revue interne

1. Cloudflare indique que son outil interne de revue de code coûtait en moyenne $0.77 par revue, soit une baisse de 68% par rapport à une référence de $2.43 issue de ses semaines les plus coûteuses. Ces résultats concernent sa charge de travail et ne garantissent pas les mêmes économies pour d’autres équipes.

2. L’entreprise attribue environ 40% des économies aux modifications et optimisations du code de l’outil de revue ; le reste provient, selon elle, du choix des modèles et du niveau d’effort d’inférence.

검토 초점: Comparer les coûts avec la qualité des revues, la composition de la charge de travail et la période d’évaluation. Reproduire les mesures sur des modifications représentatives avant de choisir des modèles ou de réduire l’effort d’inférence ; ce brouillon ne contient aucun benchmark local.

### Русский (ru)

Cloudflare сообщает о снижении затрат на инференс внутреннего инструмента ревью

1. Cloudflare сообщает, что её внутренний инструмент проверки кода обходился в среднем в $0.77 за ревью — на 68% меньше базового уровня $2.43 за ревью в самые затратные недели. Это результаты на нагрузке компании, а не гарантия такой же экономии для других команд.

2. Компания связывает около 40% экономии с изменениями и оптимизациями кода самого инструмента ревью, а остальную часть — с выбором моделей и уровня усилий при рассуждении.

검토 초점: Сравнивайте затраты вместе с качеством ревью, составом нагрузки и периодом оценки. Перед выбором моделей или снижением усилий при рассуждении воспроизведите измерения на типичных изменениях; этот черновик не содержит локального бенчмарка.

## TeamCity advisory separates on-premises and cloud exposure

원문: https://blog.jetbrains.com/teamcity/2026/05/cve-2026-44413/

검토 기준: 영어 보강본 6944923e55b6bbd0, 2026-10-25T06:06:33+00:00

### 영어 기준본

1. JetBrains describes CVE-2026-44413 as a post-authentication TeamCity On-Premises issue affecting versions through 2025.11.4 and fixed in 2026.1. These are the versions in the historical advisory.

> assigned the CVE identifier CVE-2026-44413.

근거: https://blog.jetbrains.com/teamcity/2026/05/cve-2026-44413/

> versions through 2025.11.4.

근거: https://blog.jetbrains.com/teamcity/2026/05/cve-2026-44413/

> fixed in version 2026.1.

근거: https://blog.jetbrains.com/teamcity/2026/05/cve-2026-44413/

2. The vendor states that TeamCity Cloud is not affected and requires no action for this issue.

> TeamCity Cloud is not affected and requires no action.

근거: https://blog.jetbrains.com/teamcity/2026/05/cve-2026-44413/

검토 초점: Match deployment type and installed version to the vendor advisory. Confirm a supported patched release or applicable patch plugin and its activation requirements; the archive is not a recommendation to install an old version.

### 简体中文 (zh-CN)

TeamCity 公告区分本地部署与云服务的受影响范围

1. JetBrains 将 CVE-2026-44413 描述为 TeamCity On-Premises 的身份验证后问题，影响截至 2025.11.4 的版本，并在 2026.1 修复。这些是历史公告中列出的版本。

2. 厂商表示，TeamCity Cloud 不受影响，无需针对该问题采取行动。

검토 초점: 将部署类型和已安装版本与厂商公告对应。确认仍受支持的修复版本，或适用的补丁插件及其启用要求；本归档并非建议安装旧版本。

### 日本語 (ja)

TeamCity のアドバイザリ：オンプレミスとクラウドの影響を区別

1. JetBrains は CVE-2026-44413 を TeamCity On-Premises の認証後に生じる問題と説明している。2025.11.4 までのバージョンに影響し、2026.1 で修正されたとしている。これらは当時のアドバイザリに記載されたバージョンである。

2. ベンダーは TeamCity Cloud には影響がなく、この問題への対応も不要としている。

검토 초점: デプロイ形態とインストール済みバージョンをベンダーのアドバイザリと照合する。サポート対象の修正版、または適用できるパッチプラグインと有効化の条件を確認する。このアーカイブは古いバージョンのインストールを勧めるものではない。

### Deutsch (de)

TeamCity-Sicherheitshinweis trennt On-Premises- und Cloud-Betroffenheit

1. JetBrains beschreibt CVE-2026-44413 als Problem nach der Authentifizierung in TeamCity On-Premises. Betroffen sind Versionen bis einschließlich 2025.11.4; behoben wurde es in 2026.1. Dies sind die Versionsangaben des historischen Sicherheitshinweises.

2. Laut Anbieter ist TeamCity Cloud nicht betroffen und erfordert für dieses Problem keine Maßnahmen.

검토 초점: Betriebsform und installierte Version mit dem Anbieterhinweis abgleichen. Ein unterstütztes gepatchtes Release oder ein anwendbares Patch-Plugin samt Aktivierungsanforderungen prüfen. Das Archiv empfiehlt nicht die Installation einer alten Version.

### Français (fr)

L’avis TeamCity distingue l’exposition sur site et dans le cloud

1. JetBrains décrit CVE-2026-44413 comme un problème après authentification dans TeamCity On-Premises, affectant les versions jusqu’à 2025.11.4 incluse et corrigé dans 2026.1. Il s’agit des versions indiquées dans l’avis historique.

2. L’éditeur affirme que TeamCity Cloud n’est pas affecté et ne nécessite aucune action pour ce problème.

검토 초점: Faire correspondre le type de déploiement et la version installée à l’avis de l’éditeur. Confirmer une version corrigée encore prise en charge ou un plugin de correctif applicable et ses conditions d’activation ; ces archives ne recommandent pas d’installer une ancienne version.

### Русский (ru)

Уведомление TeamCity разделяет риски локальной и облачной поставок

1. JetBrains описывает CVE-2026-44413 как проблему TeamCity On-Premises после аутентификации, затрагивающую версии вплоть до 2025.11.4 включительно и исправленную в 2026.1. Это версии, указанные в историческом уведомлении.

2. Поставщик заявляет, что TeamCity Cloud не затронут и по этой проблеме не требуется никаких действий.

검토 초점: Сопоставьте тип развёртывания и установленную версию с уведомлением поставщика. Подтвердите наличие поддерживаемого исправленного выпуска либо применимого плагина исправлений и условий его активации; архив не рекомендует устанавливать старую версию.

## Cost-center user budgets: billing UI and membership scope

원문: https://github.blog/changelog/2026-07-07-per-user-budgets-for-cost-centers-in-the-billing-ui

검토 기준: 영어 보강본 6ad4fb7dea8c6f87, 2026-10-25T17:03:04+00:00

### 영어 기준본

1. GitHub announced that Enterprise Cloud administrators could create cost-center user-level budgets in the billing UI, exposing controls previously available through the REST API. This describes a management interface expansion.

> This feature is available for GitHub Enterprise Cloud.

근거: https://github.blog/changelog/2026-07-07-per-user-budgets-for-cost-centers-in-the-billing-ui

> This gives you the same per-user AI credit budget controls that were previously only available through the REST API.

근거: https://github.blog/changelog/2026-07-07-per-user-budgets-for-cost-centers-in-the-billing-ui

2. The configured per-user budget applies to the cost center’s enterprise teams or individual users and follows membership changes automatically. This is a shared budget setting applied per member, not a separately negotiated limit for every person.

> set one per-user budget for that cost center, and have it automatically apply to everyone in it.

근거: https://github.blog/changelog/2026-07-07-per-user-budgets-for-cost-centers-in-the-billing-ui

> As membership changes, budget coverage stays in sync

근거: https://github.blog/changelog/2026-07-07-per-user-budgets-for-cost-centers-in-the-billing-ui

검토 초점: Inspect effective membership, budget behavior and overage settings together with enterprise billing policy. UI availability does not by itself demonstrate that all AI spending is blocked or that savings have been measured.

### 简体中文 (zh-CN)

成本中心用户预算：计费界面与成员范围

1. GitHub 宣布，Enterprise Cloud 管理员可在计费界面中创建成本中心的用户级预算，将此前通过 REST API 提供的控制功能加入界面。这描述的是管理界面的扩展。

2. 配置的每用户预算适用于成本中心的企业团队或个人用户，并自动随成员变动调整。这是对每位成员应用的共享预算设置，而非为每个人单独协商的限额。

검토 초점: 结合企业计费策略，一并检查实际成员范围、预算行为和超额使用设置。仅凭界面可用，并不能证明所有 AI 支出都会被阻止，也不能证明已测得节省。

### 日本語 (ja)

コストセンターのユーザー予算：請求画面とメンバーの適用範囲

1. GitHub は、Enterprise Cloud の管理者が請求画面でコストセンターのユーザー単位予算を作成できるようになったと発表した。従来 REST API で利用できた制御を画面にも提供する、管理インターフェースの拡張である。

2. 設定したユーザー単位予算は、コストセンターのエンタープライズチームまたは個別ユーザーに適用され、メンバー変更に自動で追従する。各メンバーに共通の予算設定を適用するもので、個人ごとに別途交渉した上限ではない。

검토 초점: 実際に適用されるメンバー、予算の動作、超過利用設定を、企業の請求ポリシーと併せて確認する。画面が利用できるだけでは、すべての AI 支出が止まることや、削減効果を測定済みであることは示せない。

### Deutsch (de)

Nutzerbudgets je Kostenstelle: Abrechnungsoberfläche und Mitgliedschaft

1. GitHub kündigte an, dass Enterprise Cloud-Administratoren nutzerbezogene Kostenstellenbudgets in der Abrechnungsoberfläche anlegen können. Damit werden zuvor über die REST API verfügbare Steuerungsmöglichkeiten in der Oberfläche zugänglich. Es handelt sich um eine Erweiterung der Verwaltungsschnittstelle.

2. Das konfigurierte Pro-Nutzer-Budget gilt für die Enterprise-Teams oder einzelnen Nutzer der Kostenstelle und folgt Mitgliedschaftsänderungen automatisch. Dies ist eine gemeinsame Budgeteinstellung, die auf jedes Mitglied angewendet wird, kein für jede Person gesondert ausgehandeltes Limit.

검토 초점: Die tatsächliche Mitgliedschaft, das Budgetverhalten und Überschreitungseinstellungen zusammen mit der Abrechnungsrichtlinie des Unternehmens prüfen. Die Verfügbarkeit einer Oberfläche belegt allein weder, dass sämtliche KI-Ausgaben blockiert werden, noch, dass Einsparungen gemessen wurden.

### Français (fr)

Budgets utilisateurs par centre de coûts : interface de facturation et périmètre des membres

1. GitHub a annoncé que les administrateurs Enterprise Cloud pouvaient créer des budgets par utilisateur de centre de coûts dans l’interface de facturation. Celle-ci expose des contrôles auparavant disponibles via la REST API. Il s’agit d’une extension de l’interface de gestion.

2. Le budget par utilisateur configuré s’applique aux équipes d’entreprise ou aux utilisateurs individuels du centre de coûts et suit automatiquement les changements d’appartenance. C’est un paramètre budgétaire commun appliqué à chaque membre, pas une limite négociée séparément pour chaque personne.

검토 초점: Examiner les membres effectivement concernés, le comportement du budget et les paramètres de dépassement avec la politique de facturation de l’entreprise. La disponibilité de l’interface ne démontre pas, à elle seule, que toutes les dépenses d’IA sont bloquées ou que des économies ont été mesurées.

### Русский (ru)

Пользовательские бюджеты центров затрат: интерфейс оплаты и состав участников

1. GitHub объявила, что администраторы Enterprise Cloud могут создавать пользовательские бюджеты центров затрат в интерфейсе оплаты. В нём появились настройки, ранее доступные через REST API. Это расширение интерфейса управления.

2. Настроенный бюджет на пользователя применяется к командам предприятия или отдельным пользователям центра затрат и автоматически учитывает изменения состава участников. Это общая настройка бюджета, применяемая к каждому участнику, а не отдельно согласованный лимит для каждого человека.

검토 초점: Проверяйте фактический состав участников, поведение бюджета и настройки превышения вместе с политикой оплаты предприятия. Само наличие интерфейса не доказывает блокировку всех расходов на AI или наличие измеренной экономии.

## Argo CD release candidate: internal mTLS and source-integrity configuration

원문: https://www.infoq.com/news/2026/06/argocd-supply-chain-security/

검토 기준: 영어 보강본 7067e48d153e8525, 2026-10-25T12:40:05+00:00

### 영어 기준본

1. The official Argo CD v3.5.0-rc1 page labels this artifact a pre-release and lists mTLS support in the repo-server. That supports describing a release-candidate capability, not claiming that every installation has mTLS enforced.

> v3.5.0-rc1 Pre-release

근거: https://github.com/argoproj/argo-cd/releases/tag/v3.5.0-rc1

> feat: adds mTLS support in repo-server

근거: https://github.com/argoproj/argo-cd/releases/tag/v3.5.0-rc1

2. The same changelog lists CLI support for Source Integrity configuration and an exposed ApplicationSet UI. This brief does not assert that signature verification first appeared in this release or that earlier internal traffic was always unencrypted.

> feat(cli): Add support for Source Integrity configuration

근거: https://github.com/argoproj/argo-cd/releases/tag/v3.5.0-rc1

> feat: expose Appset UI and fix pie chart summary

근거: https://github.com/argoproj/argo-cd/releases/tag/v3.5.0-rc1

검토 초점: The linked official blog could not be collected; this narrower draft uses the project’s release artifact. Review upgrade notes, certificates, trust roots and the target version’s integrity settings before rollout. It is not a claim that the candidate remains the newest version.

### 简体中文 (zh-CN)

Argo CD 候选版本：内部 mTLS 与来源完整性配置

1. Argo CD v3.5.0-rc1 官方页面将该构建标为预发布版本，并列出 repo-server 的 mTLS 支持。这能支持对候选版本能力的描述，而不能证明每个安装实例都强制启用了 mTLS。

2. 同一变更日志列出 CLI 对 Source Integrity 配置的支持，以及开放的 ApplicationSet 界面。本简报并未声称签名验证首次出现在该版本，也未声称此前内部流量始终未加密。

검토 초점: 未能采集所链接的官方博客；本草稿因此缩小范围，使用项目的发布产物作为依据。部署前，应检查升级说明、证书、信任根和目标版本的完整性设置。本草稿并不声称该候选版本仍是最新版。

### 日本語 (ja)

Argo CD のリリース候補：内部 mTLS とソース完全性の設定

1. Argo CD v3.5.0-rc1 の公式ページは、この成果物をプレリリースと明示し、repo-server の mTLS 対応を挙げている。これはリリース候補の機能として説明する根拠であり、すべてのインストールで mTLS が強制されることを示すものではない。

2. 同じ変更履歴には、Source Integrity 設定の CLI 対応と、利用できるようになった ApplicationSet UI が記載されている。この短報は、署名検証がこのバージョンで初めて導入されたとも、それ以前の内部トラフィックが常に未暗号化だったとも主張していない。

검토 초점: リンク先の公式ブログは取得できなかったため、この草稿は範囲を絞ってプロジェクトのリリース成果物を根拠にしている。展開前に、アップグレードノート、証明書、信頼のルート、対象バージョンの完全性設定を確認する。この候補が現在も最新版だと主張するものではない。

### Deutsch (de)

Argo-CD-Release-Kandidat: internes mTLS und Source-Integrity-Konfiguration

1. Die offizielle Seite zu Argo CD v3.5.0-rc1 kennzeichnet das Artefakt als Vorabversion und nennt mTLS-Unterstützung im repo-server. Das belegt eine Fähigkeit des Release-Kandidaten, nicht die Durchsetzung von mTLS in jeder Installation.

2. Derselbe Changelog nennt CLI-Unterstützung für die Source Integrity-Konfiguration und eine zugänglich gemachte ApplicationSet-Oberfläche. Dieser Kurzbericht behauptet weder, dass Signaturprüfung erstmals in diesem Release erschien, noch, dass früherer interner Verkehr stets unverschlüsselt war.

검토 초점: Der verlinkte offizielle Blogbeitrag konnte nicht abgerufen werden; dieser enger gefasste Entwurf stützt sich auf das Release-Artefakt des Projekts. Vor dem Rollout Upgrade-Hinweise, Zertifikate, Vertrauensanker und Integritätseinstellungen der Zielversion prüfen. Es wird nicht behauptet, dass dieser Kandidat weiterhin die neueste Version ist.

### Français (fr)

Version candidate Argo CD : mTLS interne et configuration de l’intégrité des sources

1. La page officielle d’Argo CD v3.5.0-rc1 indique qu’il s’agit d’une préversion et mentionne la prise en charge de mTLS dans le repo-server. Cela permet de décrire une capacité de la version candidate, sans affirmer que mTLS est imposé dans chaque installation.

2. Le même journal des modifications mentionne la prise en charge de la configuration Source Integrity dans la CLI et l’ouverture de l’interface ApplicationSet. Cette brève n’affirme ni que la vérification des signatures est apparue pour la première fois dans cette version ni que le trafic interne antérieur était toujours non chiffré.

검토 초점: L’article de blog officiel lié n’a pas pu être collecté ; ce brouillon plus restreint s’appuie sur l’artefact de version du projet. Avant le déploiement, examiner les notes de mise à niveau, les certificats, les racines de confiance et les paramètres d’intégrité de la version cible. Cela ne signifie pas que cette version candidate reste la plus récente.

### Русский (ru)

Релиз-кандидат Argo CD: внутренний mTLS и настройка целостности источников

1. Официальная страница Argo CD v3.5.0-rc1 помечает этот артефакт как предварительный выпуск и перечисляет поддержку mTLS в repo-server. Это основание говорить о возможности релиз-кандидата, а не об обязательном включении mTLS в каждой установке.

2. Тот же список изменений указывает поддержку настройки Source Integrity в CLI и предоставленный интерфейс ApplicationSet. Обзор не утверждает, что проверка подписей впервые появилась в этом выпуске или что прежний внутренний трафик всегда был незашифрованным.

검토 초점: Указанную официальную запись блога получить не удалось; этот более узкий черновик опирается на артефакт выпуска проекта. Перед развёртыванием проверьте примечания по обновлению, сертификаты, корни доверия и настройки целостности целевой версии. Здесь не утверждается, что этот кандидат по-прежнему является новейшей версией.

## NetScaler protection requires patching and origin controls

원문: https://blog.cloudflare.com/protect-your-netscaler-gateway/

검토 기준: 영어 보강본 72477d086944244f, 2026-10-25T05:21:13+00:00

### 영어 기준본

1. Cloudflare starts its NetScaler guidance by telling affected customers to patch their gateway before considering additional protective layers.

> If you’re a NetScaler customer and you haven’t patched your instance

근거: https://blog.cloudflare.com/protect-your-netscaler-gateway/

2. The article warns that direct access to the original address or an alternate hostname can bypass the front-end Access controls.

> they can avoid the controls placed in front of it.

근거: https://blog.cloudflare.com/protect-your-netscaler-gateway/

3. Protection of the web authentication path does not automatically cover DTLS-enabled gateway listeners.

> including DTLS-enabled listeners.

근거: https://blog.cloudflare.com/protect-your-netscaler-gateway/

검토 초점: Inventory every exposed listener and alternate origin route. Review patch status, authentication policy and origin restrictions as separate controls; this draft does not claim that a DNS change or WAF alone closes the exposure.

### 简体中文 (zh-CN)

NetScaler 防护需要补丁与源站访问控制

1. Cloudflare 在 NetScaler 指南开头要求受影响的客户先为网关安装补丁，再考虑额外防护层。

2. 文章提醒，直接访问原始地址或备用主机名可能绕过前置 Access 控制。

3. 对 Web 身份验证路径的保护，并不会自动覆盖启用 DTLS 的网关监听端点。

검토 초점: 清点所有暴露的监听端点与备用源站路径。将补丁状态、身份验证策略和源站限制作为独立控制措施审查；本草稿并不声称仅修改 DNS 或只使用 WAF 就能消除暴露风险。

### 日本語 (ja)

NetScaler の保護にはパッチ適用とオリジン制御が必要

1. Cloudflare の NetScaler ガイドは、影響を受ける利用者に対し、追加の防御層を検討する前にゲートウェイへパッチを適用するよう、冒頭で求めている。

2. 記事は、元のアドレスや別のホスト名へ直接アクセスすると、前段の Access 制御を迂回できる可能性があると注意している。

3. Web 認証経路の保護が、DTLS を有効にしたゲートウェイのリスナーまで自動的にカバーするわけではない。

검토 초점: 公開されているすべてのリスナーと、別経路のオリジンへのアクセスを洗い出す。パッチ適用状況、認証ポリシー、オリジンの制限を別々の制御として確認する。この草稿は、DNS の変更や WAF だけで露出を解消できると主張するものではない。

### Deutsch (de)

NetScaler-Schutz erfordert Patches und Kontrollen am Ursprungssystem

1. Cloudflare beginnt seine NetScaler-Anleitung mit der Aufforderung an betroffene Kunden, ihr Gateway zu patchen, bevor sie zusätzliche Schutzschichten erwägen.

2. Der Artikel warnt, dass direkter Zugriff auf die ursprüngliche Adresse oder einen alternativen Hostnamen die vorgeschalteten Access-Kontrollen umgehen kann.

3. Der Schutz des Web-Authentifizierungspfads deckt Gateway-Listener mit aktiviertem DTLS nicht automatisch ab.

검토 초점: Alle exponierten Listener und alternativen Zugangswege zum Ursprungssystem erfassen. Patch-Stand, Authentifizierungsrichtlinie und Ursprungsbeschränkungen als getrennte Kontrollen prüfen. Dieser Entwurf behauptet nicht, dass eine DNS-Änderung oder eine WAF allein die Exposition beseitigt.

### Français (fr)

Protéger NetScaler nécessite des correctifs et des contrôles sur l’origine

1. Cloudflare commence son guide NetScaler en demandant aux clients affectés de corriger leur passerelle avant d’envisager des couches de protection supplémentaires.

2. L’article avertit qu’un accès direct à l’adresse d’origine ou à un autre nom d’hôte peut contourner les contrôles Access placés en amont.

3. La protection du chemin d’authentification Web ne couvre pas automatiquement les points d’écoute de la passerelle où DTLS est activé.

검토 초점: Inventorier chaque point d’écoute exposé et les autres chemins d’accès à l’origine. Examiner l’état des correctifs, la politique d’authentification et les restrictions sur l’origine comme des contrôles distincts ; ce brouillon n’affirme pas qu’un changement DNS ou un WAF suffit à supprimer l’exposition.

### Русский (ru)

Защита NetScaler требует исправлений и контроля доступа к исходному серверу

1. Cloudflare начинает руководство по NetScaler с рекомендации затронутым клиентам установить исправления на шлюз, прежде чем рассматривать дополнительные уровни защиты.

2. Статья предупреждает, что прямое обращение к исходному адресу или альтернативному имени хоста может обойти расположенные перед ним средства контроля Access.

3. Защита пути веб-аутентификации не распространяется автоматически на слушающие интерфейсы шлюза с включённым DTLS.

검토 초점: Составьте перечень всех открытых слушающих интерфейсов и альтернативных маршрутов к исходному серверу. Рассматривайте состояние исправлений, политику аутентификации и ограничения доступа к исходному серверу как отдельные меры. Этот черновик не утверждает, что одно изменение DNS или один WAF устраняет открытый доступ.

