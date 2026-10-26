# 다국어 번역 검토 초안

의미·용어·조건 대조와 대상 언어 교정은 AI로 검토합니다. 수치·제품명 검사는 의미 검토를 대체하지 않습니다. 사이트 게시는 사용자의 명시적 승인 후에 진행합니다.

## Cloudflare Security Overview separates risk priority from visibility

원문: https://www.infoq.com/news/2026/05/cloudflare-security-dashboard/

검토 기준: 영어 보강본 7ec61f556fb8d2c3, 2026-10-25T06:06:33+00:00

### 영어 기준본

1. Cloudflare describes a Security Overview dashboard that ranks items by criticality and filters insights such as suspicious activity or insecure configuration.

> items are ranked by criticality

근거: https://blog.cloudflare.com/security-overview-dashboard/

2. At launch, the article describes a domain-level experience and places account-level aggregation on the roadmap. This does not establish that the account-wide view was already released.

> launching at the domain level today

근거: https://blog.cloudflare.com/security-overview-dashboard/

검토 초점: Review what is actually observed and which controls are enabled before treating a dashboard as proof of protection. Distinguish a live product feature from a roadmap statement and confirm present account-level availability separately.

### 简体中文 (zh-CN)

Cloudflare Security Overview：区分风险优先级与可见性

1. Cloudflare 介绍了 Security Overview 仪表板，可按严重程度排列条目，并筛选可疑活动或不安全配置等洞察信息。

2. 发布时，文章描述的是域名级体验，并将账户级汇总列入路线图。这并不能证明覆盖整个账户的视图当时已经发布。

검토 초점: 将仪表板视为防护证据前，应检查实际观测到了什么，以及启用了哪些控制措施。区分已经可用的产品功能和路线图声明，并单独确认当前账户级功能的可用性。

### 日本語 (ja)

Cloudflare Security Overview：リスクの優先順位と可視性を区別

1. Cloudflare は、項目を重大度で並べ、疑わしいアクティビティや安全でない設定などのインサイトを絞り込める Security Overview ダッシュボードを紹介している。

2. 公開時の記事が説明するのはドメイン単位の機能であり、アカウント単位の集約はロードマップに位置付けている。これにより、アカウント全体の表示が当時すでに提供されていたと確認できるわけではない。

검토 초점: ダッシュボードを保護の証拠と捉える前に、実際の観測対象と有効な制御を確認する。提供中の製品機能とロードマップ上の計画を区別し、現在のアカウント単位の利用可否は別途確認する。

### Deutsch (de)

Cloudflare Security Overview: Risikopriorität und Sichtbarkeit unterscheiden

1. Cloudflare beschreibt ein Security Overview-Dashboard, das Einträge nach Kritikalität ordnet und Erkenntnisse wie verdächtige Aktivitäten oder unsichere Konfigurationen filtert.

2. Zum Start beschreibt der Artikel eine Ansicht auf Domainebene und ordnet die kontoweite Zusammenfassung der Roadmap zu. Daraus folgt nicht, dass eine kontoweite Ansicht damals bereits veröffentlicht war.

검토 초점: Vor der Bewertung eines Dashboards als Schutzbeleg prüfen, was tatsächlich beobachtet wird und welche Kontrollen aktiviert sind. Eine verfügbare Produktfunktion von einer Roadmap-Aussage unterscheiden und die heutige Verfügbarkeit auf Kontoebene gesondert bestätigen.

### Français (fr)

Cloudflare Security Overview : distinguer priorité des risques et visibilité

1. Cloudflare décrit un tableau de bord Security Overview qui classe les éléments par criticité et filtre des informations telles que les activités suspectes ou les configurations non sécurisées.

2. Lors du lancement, l’article décrit une expérience au niveau du domaine et place l’agrégation au niveau du compte dans la feuille de route. Cela ne démontre pas que la vue couvrant tout le compte était déjà disponible.

검토 초점: Avant de considérer un tableau de bord comme une preuve de protection, examiner ce qui est réellement observé et les contrôles activés. Distinguer une fonction disponible d’une intention de la feuille de route, et confirmer séparément la disponibilité actuelle au niveau du compte.

### Русский (ru)

Cloudflare Security Overview: приоритет рисков и видимость — разные вещи

1. Cloudflare описывает панель Security Overview, которая упорядочивает элементы по критичности и фильтрует сведения, например о подозрительной активности или небезопасной конфигурации.

2. На момент запуска статья описывает возможности на уровне домена, а агрегацию на уровне учётной записи относит к планам развития. Это не подтверждает, что представление всей учётной записи уже было выпущено.

검토 초점: Прежде чем считать панель доказательством защиты, проверьте, что именно наблюдается и какие меры контроля включены. Отличайте работающую функцию продукта от планов развития и отдельно подтверждайте текущую доступность на уровне учётной записи.

## AWS FinOps Agent preview: investigation scope and regional limits

원문: https://www.infoq.com/news/2026/06/aws-finops-agent/

검토 기준: 영어 보강본 81aa0c8f7db4aee1, 2026-10-25T12:40:05+00:00

### 영어 기준본

1. AWS announced a FinOps Agent preview that answers cost questions, surfaces optimization recommendations, investigates cost anomalies and schedules recurring workflows. It can route findings through Jira or Slack; those capabilities do not establish measured savings.

> answers cost questions, surfaces optimization opportunities, automatically investigates cost anomalies, and runs recurring FinOps workflows on a schedule you define.

근거: https://aws.amazon.com/about-aws/whats-new/2026/06/aws-finops-agent-preview/

> can open Jira tickets on your behalf.

근거: https://aws.amazon.com/about-aws/whats-new/2026/06/aws-finops-agent-preview/

2. The announcement locates the preview in US East (N. Virginia), with cost data covering AWS Regions except GovCloud and China. It offers the service at no additional charge during preview; that is not a permanent price or an unlimited-use commitment.

> AWS FinOps Agent (preview) is available in the US East (N. Virginia) Region

근거: https://aws.amazon.com/about-aws/whats-new/2026/06/aws-finops-agent-preview/

> except AWS GovCloud (US) Regions and AWS China (Beijing and Ningxia) Regions.

근거: https://aws.amazon.com/about-aws/whats-new/2026/06/aws-finops-agent-preview/

> AWS FinOps Agent is offered at no additional charge during the preview.

근거: https://aws.amazon.com/about-aws/whats-new/2026/06/aws-finops-agent-preview/

검토 초점: Confirm current availability, quotas, permission scope and billing before enabling workflows. Cost investigation and ticket creation should not be generalized into permission to modify production resources autonomously.

### 简体中文 (zh-CN)

AWS FinOps Agent 预览：调查范围与区域限制

1. AWS 宣布推出 FinOps Agent 预览，可回答成本问题、呈现优化建议、调查成本异常并安排定期工作流。它能通过 Jira 或 Slack 传递发现；这些能力并不能证明已测得成本节省。

2. 公告将预览部署位置列为美国东部（弗吉尼亚北部），成本数据覆盖 GovCloud 和中国以外的 AWS 区域。预览期间该服务不额外收费，但这不是永久价格或不限量使用的承诺。

검토 초점: 启用工作流前，确认当前可用性、配额、权限范围和计费。不能将成本调查和创建工单的能力泛化为可自主修改生产资源的权限。

### 日本語 (ja)

AWS FinOps Agent のプレビュー：調査範囲とリージョンの制限

1. AWS は、コストに関する質問への回答、最適化提案の提示、コスト異常の調査、定期ワークフローの設定を行う FinOps Agent のプレビューを発表した。調査結果を Jira や Slack に送れるが、これらの機能がコスト削減の実測を示すわけではない。

2. 告知では、プレビューの提供場所を米国東部（バージニア北部）とし、コストデータは GovCloud と中国を除く AWS リージョンを対象としている。プレビュー中は追加料金なしで提供するが、恒久的な料金や無制限の利用を約束するものではない。

검토 초점: ワークフローを有効にする前に、現在の利用可否、クォータ、権限の範囲、課金を確認する。コスト調査やチケット作成の機能を、本番リソースを自律的に変更する権限にまで一般化しない。

### Deutsch (de)

Vorschau des AWS FinOps Agent: Untersuchungsumfang und regionale Grenzen

1. AWS kündigte eine Vorschau des FinOps Agent an, der Kostenfragen beantwortet, Optimierungsempfehlungen aufzeigt, Kostenanomalien untersucht und wiederkehrende Arbeitsabläufe plant. Ergebnisse lassen sich über Jira oder Slack weiterleiten; diese Fähigkeiten belegen keine gemessenen Einsparungen.

2. Laut Ankündigung wird die Vorschau in USA Ost (Nord-Virginia) bereitgestellt. Die Kostendaten decken AWS-Regionen außer GovCloud und China ab. Während der Vorschau entstehen keine zusätzlichen Gebühren für den Dienst; dies ist weder ein dauerhafter Preis noch eine Zusage unbegrenzter Nutzung.

검토 초점: Vor dem Aktivieren von Arbeitsabläufen die aktuelle Verfügbarkeit, Kontingente, Berechtigungen und Abrechnung prüfen. Aus Kostenuntersuchungen und Ticketerstellung darf keine Erlaubnis zur autonomen Änderung von Produktivressourcen abgeleitet werden.

### Français (fr)

Préversion d’AWS FinOps Agent : périmètre d’investigation et limites régionales

1. AWS a annoncé une préversion de FinOps Agent qui répond aux questions de coûts, présente des recommandations d’optimisation, examine les anomalies de coûts et planifie des processus récurrents. Il peut transmettre ses résultats via Jira ou Slack ; ces capacités ne démontrent pas des économies mesurées.

2. L’annonce situe la préversion dans la région USA Est (Virginie du Nord), avec des données de coûts couvrant les régions AWS à l’exception de GovCloud et de la Chine. Le service est proposé sans frais supplémentaires pendant la préversion ; ce n’est ni un tarif permanent ni une promesse d’utilisation illimitée.

검토 초점: Confirmer la disponibilité actuelle, les quotas, le périmètre des autorisations et la facturation avant d’activer des processus. L’investigation des coûts et la création de tickets ne doivent pas être assimilées à une permission de modifier les ressources de production de manière autonome.

### Русский (ru)

Предварительная версия AWS FinOps Agent: охват исследований и региональные ограничения

1. AWS объявила о предварительной версии FinOps Agent, который отвечает на вопросы о затратах, предлагает рекомендации по оптимизации, исследует аномалии расходов и планирует регулярные рабочие процессы. Он может передавать результаты через Jira или Slack; эти возможности не подтверждают измеренную экономию.

2. В объявлении местом предоставления предварительной версии указан регион Восток США (Северная Вирджиния), а данные о затратах охватывают регионы AWS, кроме GovCloud и Китая. Во время предварительного доступа сервис предоставляется без дополнительной платы; это не постоянный тариф и не обязательство обеспечить неограниченное использование.

검토 초점: Перед включением рабочих процессов подтвердите текущую доступность, квоты, область разрешений и оплату. Исследование расходов и создание задач нельзя считать разрешением автономно изменять ресурсы в производственной среде.

## Dynatrace runtime context helps prioritize GitHub alerts

원문: https://github.blog/changelog/2026-04-07-prioritize-security-alerts-with-runtime-context-from-dynatrace

검토 기준: 영어 보강본 87db18d4899cc26c, 2026-10-25T05:38:18+00:00

### 영어 기준본

1. The April GitHub notice describes Dynatrace runtime context for prioritizing security alerts by deployed artifacts and runtime risk in Kubernetes.

> deployed artifacts and runtime risk in your Kubernetes environment.

근거: https://github.blog/changelog/2026-04-07-prioritize-security-alerts-with-runtime-context-from-dynatrace

2. The notice lists the feature as generally available for GitHub Enterprise Cloud customers. That historical availability statement is not a claim that every GitHub plan includes it.

> generally available for GitHub Enterprise Cloud customers.

근거: https://github.blog/changelog/2026-04-07-prioritize-security-alerts-with-runtime-context-from-dynatrace

검토 초점: Review repository-to-container mapping and runtime coverage before treating a filtered alert list as a complete inventory. Confirm current integration and plan requirements separately.

### 简体中文 (zh-CN)

Dynatrace 运行时上下文帮助确定 GitHub 告警优先级

1. GitHub 四月的公告介绍了 Dynatrace 运行时上下文，可根据 Kubernetes 中已部署的产物及运行时风险，确定安全告警的优先级。

2. 公告将该功能列为向 GitHub Enterprise Cloud 客户正式提供。这项历史可用性声明，并不意味着所有 GitHub 套餐都包含它。

검토 초점: 将筛选后的告警列表视为完整清单前，应检查仓库与容器的映射和运行时覆盖范围。当前集成和套餐要求须单独确认。

### 日本語 (ja)

Dynatrace の実行時コンテキストで GitHub アラートの優先順位を判断

1. GitHub の四月の告知は、Kubernetes 内のデプロイ済み成果物と実行時リスクに基づき、セキュリティアラートの優先順位を判断するための Dynatrace 実行時コンテキストを説明している。

2. 告知では、この機能を GitHub Enterprise Cloud 利用者向けの一般提供としている。これは当時の利用条件であり、すべての GitHub プランに含まれるという主張ではない。

검토 초점: 絞り込まれたアラート一覧を完全な台帳と捉える前に、リポジトリとコンテナの対応付け、および実行時のカバー範囲を確認する。現在の連携条件とプラン要件は別途確認する。

### Deutsch (de)

Dynatrace-Laufzeitkontext hilft bei der Priorisierung von GitHub-Warnungen

1. Die GitHub-Mitteilung vom April beschreibt Dynatrace-Laufzeitkontext, mit dem Sicherheitswarnungen anhand bereitgestellter Artefakte und des Laufzeitrisikos in Kubernetes priorisiert werden.

2. Die Mitteilung nennt die Funktion als allgemein verfügbar für Kunden von GitHub Enterprise Cloud. Diese historische Verfügbarkeitsaussage bedeutet nicht, dass jeder GitHub-Tarif sie enthält.

검토 초점: Die Zuordnung zwischen Repository und Container sowie die Laufzeitabdeckung prüfen, bevor eine gefilterte Warnungsliste als vollständiges Inventar behandelt wird. Aktuelle Integrations- und Tarifanforderungen gesondert bestätigen.

### Français (fr)

Le contexte d’exécution Dynatrace aide à prioriser les alertes GitHub

1. L’avis GitHub d’avril décrit le contexte d’exécution Dynatrace pour prioriser les alertes de sécurité selon les artefacts déployés et les risques à l’exécution dans Kubernetes.

2. L’avis indique une disponibilité générale de cette fonction pour les clients GitHub Enterprise Cloud. Cette déclaration historique ne signifie pas que tous les forfaits GitHub l’incluent.

검토 초점: Examiner la correspondance entre dépôts et conteneurs ainsi que la couverture à l’exécution avant de traiter une liste d’alertes filtrée comme un inventaire complet. Confirmer séparément les exigences actuelles d’intégration et de forfait.

### Русский (ru)

Контекст выполнения Dynatrace помогает расставлять приоритеты предупреждений GitHub

1. Апрельское уведомление GitHub описывает контекст выполнения Dynatrace для определения приоритетов предупреждений безопасности по развёрнутым артефактам и рискам выполнения в Kubernetes.

2. Уведомление указывает общую доступность функции для клиентов GitHub Enterprise Cloud. Это историческое заявление о доступности, а не утверждение о включении функции в каждый тариф GitHub.

검토 초점: Прежде чем считать отфильтрованный список предупреждений полным инвентарём, проверьте соответствие репозиториев контейнерам и охват во время выполнения. Отдельно подтвердите текущие требования к интеграции и тарифу.

## Athena coalition: coordinated remediation and disclosure conditions

원문: https://www.infoq.com/news/2026/06/athena-security-coalition/

검토 기준: 영어 보강본 92303a0e5010240e, 2026-10-25T12:23:59+00:00

### 영어 기준본

1. Docker announced that it was joining Athena as a founding participant and described the coalition as coordinated defense of open-source software. This is a participant’s description of the initiative.

> Docker is a founding participant.

근거: https://www.docker.com/blog/docker-joins-the-athena-coalition-a-cross-industry-collaboration-for-supply-chain-security/

2. Docker describes organizations sharing findings and coordinating responses before vulnerabilities become public. This establishes the stated collaboration model, not independently verified coverage or remediation success.

> share findings and coordinate responses before vulnerabilities become public.

근거: https://www.docker.com/blog/docker-joins-the-athena-coalition-a-cross-industry-collaboration-for-supply-chain-security/

후속 확인:

- At review time, Chainguard’s program page describes private hardened versions available to members through Chainguard Libraries before disclosure for 30 days. This is the program’s stated access condition, not a promise of immediate public patch availability.

검토 초점: Assess participation rules, embargo governance and upstream maintainer coordination. Launch metrics and claims of universal protection are not independently substantiated here; current program terms must not be presented as unchanged launch-day facts.

### 简体中文 (zh-CN)

Athena 联盟：协调修复与披露条件

1. Docker 宣布作为创始参与方加入 Athena，并将该联盟描述为对开源软件的协同防御。这是参与方对该倡议的描述。

2. Docker 介绍了各组织在漏洞公开前共享发现、协调响应的方式。这说明的是其宣称的协作模式，并非独立核验的覆盖范围或修复成功情况。

후속 확인:

- 本次审阅时，Chainguard 的项目页面称，成员在披露前的 30 天期间可通过 Chainguard Libraries 访问非公开的加固版本。这是项目声明的访问条件，不是公开补丁会立即可用的承诺。

검토 초점: 评估参与规则、披露禁令治理及与上游维护者的协调。这里未独立证实发布时的指标或普遍保护的说法；不能将当前项目条款描述为发布当天就存在且始终未变的事实。

### 日本語 (ja)

Athena 連合：協調した修復と情報公開の条件

1. Docker は、創設時の参加組織として Athena に加わると発表し、この連合をオープンソースソフトウェアの協調防御と説明した。これは参加組織による取り組みの説明である。

2. Docker は、脆弱性の公開前に組織間で発見事項を共有し、対応を調整すると説明している。これは示された協力モデルの説明であり、カバー範囲や修復の成功を独立に確認したものではない。

후속 확인:

- レビュー時点の Chainguard のプログラムページは、メンバーが公開前の 30 日間、Chainguard Libraries を通じて非公開の強化版を利用できると説明している。これはプログラムが示すアクセス条件であり、公開パッチが直ちに利用可能になるという約束ではない。

검토 초점: 参加規則、公開猶予期間の運営、上流メンテナーとの調整を評価する。開始時の指標や全面的な保護の主張を、ここで独立に裏付けてはいない。現在のプログラム規約を、開始時から変わらない事実として示してはならない。

### Deutsch (de)

Athena-Koalition: koordinierte Behebung und Offenlegungsbedingungen

1. Docker kündigte an, Athena als Gründungsteilnehmer beizutreten, und beschrieb die Koalition als koordinierte Verteidigung von Open-Source-Software. Dies ist die Darstellung der Initiative durch einen Teilnehmer.

2. Docker beschreibt, dass Organisationen Erkenntnisse austauschen und Reaktionen koordinieren, bevor Schwachstellen öffentlich werden. Das belegt das erklärte Kooperationsmodell, nicht unabhängig bestätigte Abdeckung oder erfolgreiche Behebung.

후속 확인:

- Zum Prüfzeitpunkt beschreibt die Programmseite von Chainguard, dass Mitglieder über Chainguard Libraries vor der Offenlegung 30 Tage lang Zugang zu nicht öffentlichen gehärteten Versionen erhalten. Dies ist die erklärte Zugangsbedingung des Programms, keine Zusage sofortiger öffentlicher Patch-Verfügbarkeit.

검토 초점: Teilnahmeregeln, die Steuerung von Offenlegungssperrfristen und die Abstimmung mit Upstream-Maintainern bewerten. Startkennzahlen und Aussagen über universellen Schutz werden hier nicht unabhängig belegt. Aktuelle Programmbedingungen dürfen nicht als unveränderte Tatsachen des Starttags dargestellt werden.

### Français (fr)

Coalition Athena : correction coordonnée et conditions de divulgation

1. Docker a annoncé rejoindre Athena en tant que participant fondateur et décrit la coalition comme une défense coordonnée des logiciels open source. Il s’agit de la description de l’initiative par un participant.

2. Docker décrit un partage des constats et une coordination des réponses entre organisations avant que les vulnérabilités deviennent publiques. Cela établit le modèle de collaboration annoncé, pas une couverture ou une réussite des corrections vérifiées indépendamment.

후속 확인:

- Lors de cette revue, la page du programme Chainguard décrit des versions renforcées accessibles en privé aux membres via Chainguard Libraries pendant 30 jours avant divulgation. Il s’agit des conditions d’accès annoncées par le programme, pas d’une promesse de disponibilité immédiate de correctifs publics.

검토 초점: Évaluer les règles de participation, la gouvernance de l’embargo et la coordination avec les responsables de maintenance en amont. Les indicateurs de lancement et les affirmations de protection universelle ne sont pas étayés indépendamment ici. Les conditions actuelles du programme ne doivent pas être présentées comme des faits inchangés depuis son lancement.

### Русский (ru)

Коалиция Athena: совместное устранение проблем и условия раскрытия

1. Docker объявила о присоединении к Athena в качестве участника-основателя и описала коалицию как скоординированную защиту открытого программного обеспечения. Это описание инициативы её участником.

2. Docker описывает обмен результатами и согласование ответных мер между организациями до публикации уязвимостей. Это подтверждает заявленную модель сотрудничества, а не независимо проверенный охват или успешность исправлений.

후속 확인:

- На момент проверки страница программы Chainguard описывает доступ участников через Chainguard Libraries к усиленным версиям в закрытом порядке в течение 30 дней до раскрытия. Это заявленное условие доступа программы, а не обещание немедленной доступности общедоступных исправлений.

검토 초점: Оцените правила участия, управление эмбарго и координацию с сопровождающими исходных проектов. Показатели запуска и утверждения о всеобщей защите здесь независимо не подтверждены. Текущие условия программы нельзя представлять как неизменные факты с момента запуска.

## Time-series design: series identity and cardinality trade-offs

원문: https://www.infoq.com/articles/time-series-storage-design/

검토 기준: 영어 보강본 942a88912e2e412f, 2026-10-25T06:31:18+00:00

### 영어 기준본

1. The article author proposes storing repeated series dimensions in a separate metadata table and referencing them with a compact identifier. This describes a design proposal rather than a guaranteed storage saving.

> referencing it by a compact ID

근거: https://www.infoq.com/articles/time-series-storage-design/

2. The author cautions against using high-cardinality fields such as request IDs and session tokens as series identity, because the benefit depends on repeated samples sharing an identity.

> High-cardinality fields like request IDs and session tokens

근거: https://www.infoq.com/articles/time-series-storage-design/

검토 초점: Compare ingestion rate, dimension cardinality, retention and query patterns on representative data. The reported numerical savings are not reproduced in this brief, and the author’s proposal should not be generalized to every time-series engine.

### 简体中文 (zh-CN)

时序设计：序列标识与基数的权衡

1. 文章作者建议将重复的序列维度存入独立的元数据表，并通过紧凑的标识符引用。这是一项设计提议，并非保证节省存储空间。

2. 作者提醒，不应将请求 ID、会话令牌等高基数字段用作序列标识，因为收益取决于重复采样数据能否共享同一标识。

검토 초점: 使用有代表性的数据，对比写入速率、维度基数、留存期限和查询模式。本简报未复现原文给出的数值节省，作者的提议也不应泛化为适合所有时序引擎的方案。

### 日本語 (ja)

時系列設計：系列の識別とカーディナリティのトレードオフ

1. 記事の著者は、繰り返し現れる系列のディメンションを別のメタデータテーブルに保存し、小さな識別子で参照する方法を提案している。これは設計案であり、ストレージ削減を保証するものではない。

2. 著者は、リクエスト ID やセッショントークンなどカーディナリティの高いフィールドを系列の識別に使わないよう注意している。効果は、繰り返し取得するサンプルが同じ識別子を共有できるかに依存する。

검토 초점: 代表的なデータで取り込み速度、ディメンションのカーディナリティ、保持期間、クエリパターンを比較する。この短報は、原文の数値上の削減効果を再現していない。著者の提案をすべての時系列エンジンに一般化しない。

### Deutsch (de)

Zeitreihendesign: Serienidentität und Kardinalität abwägen

1. Der Autor schlägt vor, wiederkehrende Seriendimensionen in einer separaten Metadatentabelle zu speichern und über eine kompakte Kennung zu referenzieren. Dies beschreibt einen Entwurf, keine garantierte Speichereinsparung.

2. Der Autor warnt davor, Felder mit hoher Kardinalität wie Request-IDs und Sitzungstokens als Serienidentität zu verwenden. Der Vorteil hängt davon ab, dass wiederholte Messwerte dieselbe Identität teilen.

검토 초점: An repräsentativen Daten Aufnahmerate, Dimensionskardinalität, Aufbewahrungsdauer und Abfragemuster vergleichen. Die berichteten zahlenmäßigen Einsparungen werden in diesem Kurzbericht nicht reproduziert. Der Vorschlag des Autors sollte nicht auf jede Zeitreihen-Engine verallgemeinert werden.

### Français (fr)

Conception des séries temporelles : identité des séries et compromis de cardinalité

1. L’auteur propose de stocker les dimensions répétées des séries dans une table de métadonnées distincte et de les référencer par un identifiant compact. Il s’agit d’une proposition de conception, pas d’une garantie de réduction du stockage.

2. L’auteur déconseille d’utiliser des champs à forte cardinalité, comme les identifiants de requête et les jetons de session, pour identifier les séries. Le bénéfice dépend du partage d’une même identité par des échantillons répétés.

검토 초점: Comparer le débit d’ingestion, la cardinalité des dimensions, la rétention et les schémas de requêtes sur des données représentatives. Les économies chiffrées rapportées ne sont pas reproduites dans cette brève, et la proposition de l’auteur ne doit pas être généralisée à tous les moteurs de séries temporelles.

### Русский (ru)

Проектирование временных рядов: идентичность ряда и компромиссы кардинальности

1. Автор статьи предлагает хранить повторяющиеся атрибуты рядов в отдельной таблице метаданных и ссылаться на них компактным идентификатором. Это проектное предложение, а не гарантия экономии места.

2. Автор предостерегает от использования полей с высокой кардинальностью, например идентификаторов запросов и токенов сеансов, для идентификации ряда. Выгода зависит от того, имеют ли повторные отсчёты общую идентичность.

검토 초점: На типичных данных сравните скорость поступления, кардинальность атрибутов рядов, срок хранения и шаблоны запросов. Численные оценки экономии из источника здесь не воспроизводятся; предложение автора нельзя обобщать на все движки временных рядов.

