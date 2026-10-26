# 다국어 번역 검토 초안

의미·용어·조건 대조와 대상 언어 교정은 AI로 검토합니다. 수치·제품명 검사는 의미 검토를 대체하지 않습니다. 사이트 게시는 사용자의 명시적 승인 후에 진행합니다.

## GitHub organization assessments summarize code-security risks

원문: https://github.blog/changelog/2026-04-08-code-security-risk-assessment-available-for-organizations

검토 기준: 영어 보강본 b4cc1e300a7d9c1b, 2026-10-25T05:38:18+00:00

### 영어 기준본

1. GitHub announced a free Code Security risk assessment that organization admins and security managers can run for their organization.

> run a free Code Security risk assessment

근거: https://github.blog/changelog/2026-04-08-code-security-risk-assessment-available-for-organizations

2. The assessment summarizes vulnerabilities by severity, rule type and programming language, helping readers prioritize the reported findings.

> summarizes vulnerabilities by severity, rule type, and programming language.

근거: https://github.blog/changelog/2026-04-08-code-security-risk-assessment-available-for-organizations

검토 초점: Check assessment scope and repository coverage before interpreting the report as a complete security audit. Suggested fixes still require code review and appropriate tests.

### 简体中文 (zh-CN)

GitHub 组织评估汇总代码安全风险

1. GitHub 宣布推出免费的 Code Security 风险评估，组织管理员和安全经理可以为其组织运行该评估。

2. 该评估按严重程度、规则类型和编程语言汇总漏洞，帮助读者为报告中的发现确定处理优先级。

검토 초점: 在将报告解读为全面的安全审计之前，应检查评估范围及其覆盖的仓库。建议的修复仍需经过代码审查和适当测试。

### 日本語 (ja)

GitHub の組織向け評価でコードセキュリティのリスクを把握

1. GitHub は、組織の管理者とセキュリティマネージャーが自組織向けに実行できる、無料の Code Security リスク評価を発表した。

2. この評価は脆弱性を重大度、ルールの種類、プログラミング言語別にまとめ、報告された検出事項への対応の優先順位付けを支援する。

검토 초점: 報告書を包括的なセキュリティ監査と捉える前に、評価範囲と対象リポジトリの網羅性を確認する。提案された修正にも、コードレビューと適切なテストが必要である。

### Deutsch (de)

GitHub: Organisationsbewertungen fassen Risiken der Codesicherheit zusammen

1. GitHub hat eine kostenlose Code Security-Risikobewertung angekündigt, die Organisationsadministratoren und Sicherheitsmanager für ihre Organisation durchführen können.

2. Die Bewertung fasst Schwachstellen nach Schweregrad, Regeltyp und Programmiersprache zusammen und hilft dabei, die gemeldeten Befunde zu priorisieren.

검토 초점: Umfang der Bewertung und Abdeckung der Repositorys prüfen, bevor der Bericht als vollständiges Sicherheitsaudit interpretiert wird. Vorgeschlagene Korrekturen erfordern weiterhin ein Code-Review und geeignete Tests.

### Français (fr)

GitHub : les évaluations d’organisation résument les risques de sécurité du code

1. GitHub a annoncé une évaluation gratuite des risques Code Security que les administrateurs d’organisation et les responsables de la sécurité peuvent exécuter pour leur organisation.

2. L’évaluation récapitule les vulnérabilités par gravité, type de règle et langage de programmation, afin d’aider les lecteurs à hiérarchiser les problèmes signalés.

검토 초점: Vérifier le périmètre de l’évaluation et les dépôts couverts avant d’interpréter le rapport comme un audit de sécurité complet. Les correctifs proposés nécessitent toujours une revue de code et des tests appropriés.

### Русский (ru)

GitHub: оценки для организаций обобщают риски безопасности кода

1. GitHub объявила о бесплатной оценке рисков Code Security, которую администраторы организаций и менеджеры по безопасности могут запускать для своей организации.

2. Оценка обобщает уязвимости по серьёзности, типу правила и языку программирования, помогая читателям определять приоритеты по обнаруженным проблемам.

검토 초점: Прежде чем считать отчёт полным аудитом безопасности, проверьте границы оценки и охват репозиториев. Предложенные исправления по-прежнему требуют ревью кода и подходящих тестов.

## CNCF and Kusari offer supply-chain tooling to project maintainers

원문: https://www.infoq.com/news/2026/04/cncf-kusari-security/

검토 기준: 영어 보강본 bb5be26c24786b21, 2026-10-25T05:38:18+00:00

### 영어 기준본

1. The CNCF-hosted announcement says CNCF projects receive free access to Kusari Inspector, described as an AI code-review and dependency-management tool.

> provide CNCF projects with free access to Kusari Inspector

근거: https://www.cncf.io/blog/2026/03/23/kusari-and-cncf-advancing-software-supply-chain-security-for-cloud-native-projects/

2. The announcement lists GUAC, in-toto/Witness and OpenVEX among projects adopting the tool. This is a reported adoption list, not independent evidence that all vulnerabilities were removed.

> GUAC, in-toto/Witness, OpenVEX

근거: https://www.cncf.io/blog/2026/03/23/kusari-and-cncf-advancing-software-supply-chain-security-for-cloud-native-projects/

검토 초점: Review eligibility, data handling and dependency coverage before connecting a repository. Measure actionable findings and false positives in the project rather than assuming benefit from tool adoption alone.

### 简体中文 (zh-CN)

CNCF 与 Kusari 向项目维护者提供供应链工具

1. CNCF 网站发布的公告称，CNCF 项目可以免费使用 Kusari Inspector；公告将其描述为 AI 代码审查和依赖管理工具。

2. 公告将 GUAC、in-toto/Witness 和 OpenVEX 列为采用该工具的部分项目。这是一份公告报告的采用名单，并非所有漏洞均已消除的独立证据。

검토 초점: 连接仓库之前，应审查使用资格、数据处理方式和依赖覆盖范围。在项目中衡量可采取行动的发现和误报，不要仅凭采用工具就假定它能带来收益。

### 日本語 (ja)

CNCF と Kusari がプロジェクトメンテナーにサプライチェーンツールを提供

1. CNCF のサイトに掲載された発表によると、CNCF プロジェクトは Kusari Inspector を無料で利用できる。同ツールは AI によるコードレビューと依存関係管理のツールと説明されている。

2. 発表では、このツールを採用するプロジェクトの例として GUAC、in-toto/Witness、OpenVEX を挙げている。これは発表に記載された採用リストであり、すべての脆弱性が解消されたことを示す独立した証拠ではない。

검토 초점: リポジトリを接続する前に、利用資格、データの取り扱い、依存関係のカバー範囲を確認する。ツールを採用しただけで効果を想定せず、プロジェクト内で対応可能な検出事項と誤検知を測定する。

### Deutsch (de)

CNCF und Kusari bieten Projektmaintainern Werkzeuge für die Lieferkette

1. Laut der auf der CNCF-Website veröffentlichten Ankündigung erhalten CNCF-Projekte kostenlosen Zugang zu Kusari Inspector. Das Werkzeug wird als KI-Tool für Code-Reviews und das Abhängigkeitsmanagement beschrieben.

2. Die Ankündigung nennt GUAC, in-toto/Witness und OpenVEX unter den Projekten, die das Werkzeug einsetzen. Dies ist eine gemeldete Liste von Nutzern, kein unabhängiger Nachweis dafür, dass alle Schwachstellen beseitigt wurden.

검토 초점: Vor der Anbindung eines Repositorys die Teilnahmeberechtigung, den Umgang mit Daten und die Abdeckung der Abhängigkeiten prüfen. Im Projekt verwertbare Befunde und Fehlalarme messen, statt allein aus dem Werkzeugeinsatz einen Nutzen abzuleiten.

### Français (fr)

CNCF et Kusari proposent des outils de chaîne d’approvisionnement aux mainteneurs

1. L’annonce publiée sur le site de la CNCF indique que les projets CNCF bénéficient d’un accès gratuit à Kusari Inspector, présenté comme un outil de revue de code par IA et de gestion des dépendances.

2. L’annonce cite GUAC, in-toto/Witness et OpenVEX parmi les projets qui adoptent l’outil. Il s’agit d’une liste d’adoptions rapportée par l’annonce, et non d’une preuve indépendante que toutes les vulnérabilités ont été éliminées.

검토 초점: Examiner les critères d’éligibilité, le traitement des données et la couverture des dépendances avant de connecter un dépôt. Mesurer, dans le projet, les signalements pouvant donner lieu à des mesures correctives et les faux positifs, sans présumer d’un bénéfice du seul fait de l’adoption de l’outil.

### Русский (ru)

CNCF и Kusari предлагают сопровождающим проектов инструменты для цепочки поставок

1. В объявлении на сайте CNCF говорится, что проекты CNCF получают бесплатный доступ к Kusari Inspector, описанному как инструмент ревью кода с помощью ИИ и управления зависимостями.

2. В объявлении среди проектов, внедряющих инструмент, перечислены GUAC, in-toto/Witness и OpenVEX. Это заявленный список внедрений, а не независимое доказательство устранения всех уязвимостей.

검토 초점: Перед подключением репозитория изучите условия участия, обработку данных и охват зависимостей. Измеряйте в проекте число находок, по которым можно принять меры, и ложных срабатываний, а не предполагайте пользу лишь на основании внедрения инструмента.

## GitHub GPT-4.1 retirement notice applies to Copilot

원문: https://github.blog/changelog/2026-05-07-upcoming-deprecation-of-gpt-4-1

검토 기준: 영어 보강본 be1017688a0667ca, 2026-10-25T06:06:33+00:00

### 영어 기준본

1. GitHub announced the planned retirement of GPT-4.1 from Copilot on 2026-06-01. This does not describe availability through every external API.

> GPT-4.1 2026-06-01 GPT-5.5

근거: https://github.blog/changelog/2026-05-07-upcoming-deprecation-of-gpt-4-1

2. Copilot Enterprise administrators may need to enable access to replacement models through model policies, according to the notice.

> enable access to alternative models through their model policies

근거: https://github.blog/changelog/2026-05-07-upcoming-deprecation-of-gpt-4-1

검토 초점: Confirm which Copilot experience and policy a workflow uses. Treat the scheduled date as historical evidence and check actual current model availability before updating configuration.

### 简体中文 (zh-CN)

GitHub 的 GPT-4.1 停用预告适用于 Copilot

1. GitHub 宣布计划于 2026-06-01 在 Copilot 中停用 GPT-4.1。这并不说明该模型在所有外部 API 中的可用性。

2. 根据公告，Copilot Enterprise 管理员可能需要通过模型政策启用对替代模型的访问。

검토 초점: 确认工作流使用的是哪种 Copilot 使用环境及政策。将计划日期视为历史记录，并在更新配置之前核实模型当前实际的可用性。

### 日本語 (ja)

GitHub の GPT-4.1 提供終了予告は Copilot が対象

1. GitHub は、Copilot での GPT-4.1 の提供を 2026-06-01 に終了する計画を発表した。これは、すべての外部 API を通じた利用可否を説明するものではない。

2. 告知によると、Copilot Enterprise の管理者は、モデルポリシーを通じて代替モデルへのアクセスを有効にする必要がある場合がある。

검토 초점: ワークフローが利用する Copilot の環境とポリシーを確認する。予定日は過去の記録として扱い、設定を更新する前に、現在のモデルの実際の利用可否を確認する。

### Deutsch (de)

GitHubs Ankündigung zur Einstellung von GPT-4.1 betrifft Copilot

1. GitHub hat angekündigt, GPT-4.1 planmäßig am 2026-06-01 aus Copilot zu nehmen. Dies beschreibt nicht die Verfügbarkeit über sämtliche externen APIs.

2. Laut der Mitteilung müssen Administratoren von Copilot Enterprise möglicherweise über Modellrichtlinien den Zugang zu Ersatzmodellen aktivieren.

검토 초점: Prüfen, welche Copilot-Umgebung und welche Richtlinie ein Arbeitsablauf nutzt. Das geplante Datum als historischen Beleg behandeln und vor Konfigurationsänderungen die tatsächliche aktuelle Modellverfügbarkeit prüfen.

### Français (fr)

L’annonce de GitHub sur le retrait de GPT-4.1 concerne Copilot

1. GitHub a annoncé le retrait prévu de GPT-4.1 de Copilot pour le 2026-06-01. Cette annonce ne décrit pas sa disponibilité via toutes les API externes.

2. Selon l’annonce, les administrateurs de Copilot Enterprise peuvent devoir activer l’accès aux modèles de remplacement au moyen des politiques de modèles.

검토 초점: Confirmer l’environnement Copilot et la politique utilisés par le workflow. Traiter la date prévue comme un élément historique et vérifier la disponibilité actuelle réelle des modèles avant de modifier la configuration.

### Русский (ru)

Объявление GitHub о выводе GPT-4.1 из эксплуатации касается Copilot

1. GitHub объявила о запланированном на 2026-06-01 выводе GPT-4.1 из Copilot. Это не описывает доступность модели через все внешние API.

2. Согласно объявлению, администраторам Copilot Enterprise может потребоваться включить доступ к моделям на замену через политики моделей.

검토 초점: Уточните, какое окружение Copilot и какую политику использует рабочий процесс. Рассматривайте запланированную дату как историческое свидетельство и перед изменением конфигурации проверяйте фактическую доступность моделей на текущий момент.

## Closed Dependabot alerts: announced retention and archive access

원문: https://github.blog/changelog/2026-06-30-cloud-data-retention-policy-for-closed-security-alerts

검토 기준: 영어 보강본 c12b394bcd713139, 2026-10-25T12:40:05+00:00

### 영어 기준본

1. GitHub’s notice scheduled a retention change for 2026-09-25, beginning with closed Dependabot security alerts on github.com and Enterprise Cloud. It explicitly excludes Enterprise Server; the announcement alone does not verify completion of the rollout.

> Starting September 25, 2026, GitHub will introduce a data retention policy for closed Dependabot security alerts.

근거: https://github.blog/changelog/2026-06-30-cloud-data-retention-policy-for-closed-security-alerts

> It does not apply to GitHub Enterprise Server (GHES).

근거: https://github.blog/changelog/2026-06-30-cloud-data-retention-policy-for-closed-security-alerts

2. Under the announced policy, open alerts remain accessible regardless of age, while closed alerts remain in the UI and API for 2 years after closure. Older closed alerts move to downloadable CSV archives for authorized administrators and security managers rather than remaining in API results.

> Open alerts stay fully accessible in the UI and API, regardless of age.

근거: https://github.blog/changelog/2026-06-30-cloud-data-retention-policy-for-closed-security-alerts

> Closed alerts stay fully accessible in the UI and API for two years after they are closed.

근거: https://github.blog/changelog/2026-06-30-cloud-data-retention-policy-for-closed-security-alerts

> Enterprise, organization, and repository administrators and security managers can download them as a CSV

근거: https://github.blog/changelog/2026-06-30-cloud-data-retention-policy-for-closed-security-alerts

검토 초점: Audit queries and compliance exports that rely on older closed alerts. Verify actual archive access and rollout status in the relevant account; do not apply this notice to every alert type or infer permanent retention after account or repository deletion.

### 简体中文 (zh-CN)

已关闭的 Dependabot 警报：公告中的保留期限与归档访问

1. GitHub 的公告将保留政策变更计划定于 2026-09-25，首先适用于 github.com 和 Enterprise Cloud 上已关闭的 Dependabot 安全警报。公告明确排除 Enterprise Server；仅凭该公告无法验证推出过程已经完成。

2. 根据公布的政策，未关闭的警报无论存在多久都仍可访问，而已关闭的警报在关闭后 2 年内仍可通过 UI 和 API 访问。更早关闭的警报会移至可下载的 CSV 归档，供获授权的管理员和安全经理访问，而不再出现在 API 结果中。

검토 초점: 审查依赖较早关闭警报的查询和合规导出。在相关账户中核实实际归档访问权限及推出状态；不要将本公告套用于所有警报类型，也不要据此推断账户或仓库删除后仍会永久保留数据。

### 日本語 (ja)

クローズ済み Dependabot アラート：告知された保持期間とアーカイブへのアクセス

1. GitHub の告知では、保持ポリシーの変更を 2026-09-25 に予定し、github.com と Enterprise Cloud のクローズ済み Dependabot セキュリティアラートから開始するとしている。Enterprise Server は明示的に対象外であり、告知だけでは展開の完了を確認できない。

2. 告知されたポリシーでは、オープン状態のアラートは経過期間にかかわらずアクセスでき、クローズ済みのアラートはクローズ後 2 年間、UI と API でアクセスできる。それより前にクローズされたアラートは API の結果には残らず、権限のある管理者とセキュリティマネージャーがダウンロードできる CSV アーカイブに移る。

검토 초점: 古いクローズ済みアラートに依存するクエリとコンプライアンス用エクスポートを点検する。該当アカウントで実際のアーカイブへのアクセスと展開状況を確認する。この告知をすべてのアラート種別に適用したり、アカウントやリポジトリの削除後も永久に保持されると推測したりしない。

### Deutsch (de)

Geschlossene Dependabot-Warnungen: Angekündigte Aufbewahrung und Archivzugriff

1. GitHubs Mitteilung sah eine Änderung der Aufbewahrung für den 2026-09-25 vor, beginnend mit geschlossenen Dependabot-Sicherheitswarnungen auf github.com und Enterprise Cloud. Enterprise Server ist ausdrücklich ausgenommen; die Ankündigung allein bestätigt keinen abgeschlossenen Rollout.

2. Nach der angekündigten Richtlinie bleiben offene Warnungen unabhängig von ihrem Alter zugänglich. Geschlossene Warnungen bleiben nach dem Schließen 2 Jahre lang in UI und API verfügbar. Ältere geschlossene Warnungen werden in herunterladbare CSV-Archive für berechtigte Administratoren und Sicherheitsmanager verschoben und erscheinen nicht weiter in API-Ergebnissen.

검토 초점: Abfragen und Compliance-Exporte prüfen, die auf ältere geschlossene Warnungen angewiesen sind. Den tatsächlichen Archivzugriff und Rollout-Status im jeweiligen Konto überprüfen. Die Mitteilung nicht auf jeden Warnungstyp übertragen oder daraus eine dauerhafte Aufbewahrung nach dem Löschen eines Kontos oder Repositorys ableiten.

### Français (fr)

Alertes Dependabot fermées : conservation annoncée et accès aux archives

1. L’annonce de GitHub prévoyait un changement de conservation pour le 2026-09-25, en commençant par les alertes de sécurité Dependabot fermées sur github.com et Enterprise Cloud. Elle exclut explicitement Enterprise Server ; l’annonce seule ne permet pas de vérifier que le déploiement est terminé.

2. Selon la politique annoncée, les alertes ouvertes restent accessibles quel que soit leur âge, tandis que les alertes fermées restent disponibles dans l’interface et l’API pendant 2 ans après leur fermeture. Les alertes fermées plus anciennes sont transférées vers des archives CSV téléchargeables par les administrateurs et responsables de la sécurité autorisés, au lieu de rester dans les résultats de l’API.

검토 초점: Auditer les requêtes et les exports de conformité qui dépendent d’anciennes alertes fermées. Vérifier l’accès effectif aux archives et l’état du déploiement dans le compte concerné ; ne pas appliquer cette annonce à tous les types d’alertes ni en déduire une conservation permanente après la suppression d’un compte ou d’un dépôt.

### Русский (ru)

Закрытые оповещения Dependabot: объявленные сроки хранения и доступ к архивам

1. В объявлении GitHub изменение правил хранения было запланировано на 2026-09-25, начиная с закрытых оповещений безопасности Dependabot на github.com и в Enterprise Cloud. Enterprise Server явно исключён; само объявление не подтверждает завершение внедрения.

2. Согласно объявленным правилам, открытые оповещения остаются доступными независимо от давности, а закрытые доступны в интерфейсе и API в течение 2 лет после закрытия. Более старые закрытые оповещения перемещаются в скачиваемые CSV-архивы для уполномоченных администраторов и менеджеров по безопасности, а не остаются в результатах API.

검토 초점: Проверьте запросы и выгрузки для соблюдения нормативных требований, которые зависят от старых закрытых оповещений. Уточните фактический доступ к архивам и статус внедрения в соответствующей учётной записи; не распространяйте это объявление на все типы оповещений и не делайте из него вывод о бессрочном хранении после удаления учётной записи или репозитория.

## Microsoft MDASH: multi-model scanning and preview status

원문: https://www.infoq.com/news/2026/05/microsoft-mdash/

검토 기준: 영어 보강본 c2532ba4f69bf1ba, 2026-10-25T06:31:18+00:00

### 영어 기준본

1. Microsoft describes MDASH as a multi-model agentic scanning harness that orchestrates an ensemble of frontier and distilled models. This is the vendor’s description of its architecture.

> ensemble of frontier and distilled models

근거: https://www.microsoft.com/en-us/security/blog/2026/05/12/defense-at-ai-speed-microsofts-new-multi-model-agentic-security-system-tops-leading-industry-benchmark/?v=1

2. The announcement invites readers to a private preview, which should not be treated as general public availability.

> sign up to join the private preview

근거: https://www.microsoft.com/en-us/security/blog/2026/05/12/defense-at-ai-speed-microsofts-new-multi-model-agentic-security-system-tops-leading-industry-benchmark/?v=1

검토 초점: Separate vendor-reported benchmark results from independently reproduced findings. Review access conditions, source-code handling and validation requirements before using the tool in a security workflow.

### 简体中文 (zh-CN)

Microsoft MDASH：多模型扫描与预览状态

1. Microsoft 将 MDASH 描述为一种多模型智能体扫描框架，可编排由前沿模型和蒸馏模型组成的集成。这是供应商对其架构的描述。

2. 公告邀请读者申请参加非公开预览，不应将其视为已经面向公众普遍开放。

검토 초점: 区分供应商报告的基准测试结果与独立复现的发现。在将工具用于安全工作流之前，应审查访问条件、源代码处理方式和验证要求。

### 日本語 (ja)

Microsoft MDASH：複数モデルによるスキャンとプレビューの状況

1. Microsoft は MDASH を、最先端モデルと蒸留モデルのアンサンブルを連携させる、複数モデルによるエージェント型スキャン基盤と説明している。これはベンダーによるアーキテクチャの説明である。

2. 発表では非公開プレビューへの参加を案内しており、一般に公開され利用可能になったと捉えるべきではない。

검토 초점: ベンダーが報告したベンチマーク結果と、独立して再現された結果を区別する。セキュリティワークフローに導入する前に、利用条件、ソースコードの取り扱い、検証要件を確認する。

### Deutsch (de)

Microsoft MDASH: Scans mit mehreren Modellen und Preview-Status

1. Microsoft beschreibt MDASH als agentisches Scan-Framework mit mehreren Modellen, das ein Ensemble aus Frontier-Modellen und destillierten Modellen orchestriert. Dies ist die Architekturbeschreibung des Anbieters.

2. Die Ankündigung lädt zur Teilnahme an einer privaten Vorschau ein. Dies sollte nicht als allgemeine öffentliche Verfügbarkeit verstanden werden.

검토 초점: Vom Anbieter gemeldete Benchmark-Ergebnisse von unabhängig reproduzierten Befunden trennen. Vor dem Einsatz in einem Sicherheitsworkflow die Zugangsbedingungen, den Umgang mit Quellcode und die Validierungsanforderungen prüfen.

### Français (fr)

Microsoft MDASH : analyse multimodèle et statut de la préversion

1. Microsoft décrit MDASH comme un cadre d’analyse agentique multimodèle qui orchestre un ensemble de modèles de pointe et de modèles distillés. Il s’agit de la description de l’architecture donnée par le fournisseur.

2. L’annonce invite les lecteurs à participer à une préversion privée, ce qui ne doit pas être interprété comme une disponibilité générale et publique.

검토 초점: Distinguer les résultats de benchmark rapportés par le fournisseur des constats reproduits de manière indépendante. Examiner les conditions d’accès, le traitement du code source et les exigences de validation avant d’utiliser l’outil dans un workflow de sécurité.

### Русский (ru)

Microsoft MDASH: сканирование с несколькими моделями и статус предварительного доступа

1. Microsoft описывает MDASH как агентную среду сканирования с несколькими моделями, которая координирует ансамбль передовых и дистиллированных моделей. Это описание архитектуры со стороны поставщика.

2. Объявление приглашает читателей к участию в закрытой предварительной версии; это не следует считать общедоступностью продукта.

검토 초점: Отделяйте результаты бенчмарков, заявленные поставщиком, от независимо воспроизведённых результатов. Перед использованием инструмента в процессе обеспечения безопасности изучите условия доступа, обработку исходного кода и требования к проверке.

