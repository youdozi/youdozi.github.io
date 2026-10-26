# 다국어 번역 검토 초안

의미·용어·조건 대조와 대상 언어 교정은 AI로 검토합니다. 수치·제품명 검사는 의미 검토를 대체하지 않습니다. 사이트 게시는 사용자의 명시적 승인 후에 진행합니다.

## Copilot adds contextual help to GitHub risk-assessment results

원문: https://github.blog/changelog/2026-04-09-ask-copilot-in-security-assessments-now-available

검토 기준: 영어 보강본 1e8ba1d86d179142, 2026-10-25T05:38:18+00:00

### 영어 기준본

1. GitHub lets organization admins and security managers open Copilot directly from secret or Code Security risk-assessment results.

> Organization admins and security managers

근거: https://github.blog/changelog/2026-04-09-ask-copilot-in-security-assessments-now-available

2. The notice describes contextual explanations and guided next steps. It does not establish that Copilot has automatically remediated the underlying issues.

> get contextual explanations and guided next steps.

근거: https://github.blog/changelog/2026-04-09-ask-copilot-in-security-assessments-now-available

검토 초점: Review the suggested actions and the permissions needed to perform them. Keep explanation, suggested remediation and verified fixes distinct when recording assessment outcomes.

### 简体中文 (zh-CN)

Copilot 为 GitHub 风险评估结果提供上下文帮助

1. GitHub 允许组织管理员和安全管理员直接从机密信息或 Code Security 风险评估结果中打开 Copilot。

2. 公告介绍了结合上下文的解释和后续操作指引，但并未证明 Copilot 已自动修复相关问题。

검토 초점: 检查建议的操作及执行这些操作所需的权限。记录评估结果时，应区分解释、修复建议与已经验证的修复。

### 日本語 (ja)

Copilot が GitHub のリスク評価結果に応じた説明を提供

1. GitHub は、組織管理者とセキュリティマネージャーが、シークレットまたは Code Security のリスク評価結果から直接 Copilot を開けるようにした。

2. 告知では、結果の文脈に応じた説明と次の操作の案内を紹介している。Copilot が実際の問題を自動修復したことを示すものではない。

검토 초점: 提案された操作と、その実行に必要な権限を確認する。評価結果を記録する際は、説明、修復の提案、検証済みの修復を区別する。

### Deutsch (de)

Copilot ergänzt kontextbezogene Hilfe zu GitHub-Risikobewertungen

1. GitHub ermöglicht Organisationsadministratoren und Sicherheitsmanagern, Copilot direkt aus den Ergebnissen einer Risikobewertung für Secrets oder Code Security zu öffnen.

2. Die Mitteilung beschreibt kontextbezogene Erläuterungen und angeleitete nächste Schritte. Sie belegt nicht, dass Copilot die zugrunde liegenden Probleme automatisch behoben hat.

검토 초점: Die vorgeschlagenen Maßnahmen und die dafür erforderlichen Berechtigungen prüfen. Bei der Dokumentation von Bewertungsergebnissen zwischen Erläuterungen, vorgeschlagenen Behebungen und nachweislich behobenen Problemen unterscheiden.

### Français (fr)

Copilot apporte une aide contextuelle aux résultats d’évaluation des risques de GitHub

1. GitHub permet aux administrateurs d’organisation et aux responsables de la sécurité d’ouvrir Copilot directement depuis les résultats d’évaluation des risques liés aux secrets ou à Code Security.

2. L’avis décrit des explications contextuelles et un accompagnement pour les étapes suivantes. Il ne démontre pas que Copilot a automatiquement corrigé les problèmes sous-jacents.

검토 초점: Examiner les actions proposées et les autorisations nécessaires pour les exécuter. Lors de la consignation des résultats, distinguer les explications, les corrections suggérées et les corrections vérifiées.

### Русский (ru)

Copilot дополняет результаты оценки рисков GitHub контекстными пояснениями

1. GitHub позволяет администраторам организаций и руководителям по безопасности открывать Copilot прямо из результатов оценки рисков для секретов или Code Security.

2. Уведомление описывает контекстные пояснения и рекомендации по следующим действиям. Оно не подтверждает, что Copilot автоматически устранил сами проблемы.

검토 초점: Проверьте предлагаемые действия и необходимые для их выполнения разрешения. При документировании результатов оценки различайте пояснения, предлагаемые способы устранения и проверенные исправления.

## AI code scanning: preview conditions and later general availability

원문: https://github.blog/changelog/2026-07-14-code-scanning-shows-ai-security-detections-on-pull-requests

검토 기준: 영어 보강본 27d181b6a4903b28, 2026-10-25T17:03:04+00:00

### 영어 기준본

1. At preview launch, GitHub described AI detections on pull requests as extending language and framework coverage beyond CodeQL. Enterprise permission, organization enablement and repository CodeQL default analysis were required even though a separate AI engine performed the analysis.

> AI security detections must be allowed by your Enterprise policy and enabled at the organization level.

근거: https://github.blog/changelog/2026-07-14-code-scanning-shows-ai-security-detections-on-pull-requests

> While CodeQL is not the tool performing the AI analysis, the AI detection engine relies on it to function.

근거: https://github.blog/changelog/2026-07-14-code-scanning-shows-ai-security-detections-on-pull-requests

2. The preview findings were informational and did not block merges. The announcement required a Copilot license and consumed organization AI credits during public preview, so the original feature was neither an automatic approval gate nor an unconditional free service.

> These findings are informational and won’t block pull request merges.

근거: https://github.blog/changelog/2026-07-14-code-scanning-shows-ai-security-detections-on-pull-requests

> During public preview, AI security detections require a GitHub Copilot license and draw down your organization’s AI credits.

근거: https://github.blog/changelog/2026-07-14-code-scanning-shows-ai-security-detections-on-pull-requests

후속 확인:

- GitHub’s 2026-10-15 notice announces AI Scan general availability. It says a Copilot license is not required; private and internal organization repositories still require GitHub Code Security or Advanced Security. These conditions differ from the preview announcement.
- The later notice retains advisory-only findings and says AI Scan cannot block merges through rulesets. It does not run on fork pull requests or pull requests created by Dependabot.
- The later billing model consumes Code Security AI Credits, displayed under Advanced Security in enterprise AI usage. The absence of a Copilot-license requirement does not mean scanning has no usage charge.

검토 초점: Use the later notice for current eligibility and billing interpretation, while retaining the preview conditions as history. Advisory findings need a human response and do not replace required checks or comprehensive security validation.

### 简体中文 (zh-CN)

AI 代码扫描：预览条件与后续正式可用公告

1. 预览版推出时，GitHub 将拉取请求中的 AI 检测描述为对 CodeQL 之外语言和框架覆盖范围的扩展。虽然分析由独立的 AI 引擎执行，仍须获得企业许可、在组织中启用功能，并为仓库启用 CodeQL 默认分析。

2. 预览版的发现仅供参考，不会阻止合并。公告要求在公开预览期间持有 Copilot 许可证，并消耗组织的 AI 额度，因此原始功能既不是自动审批关卡，也不是无条件的免费服务。

후속 확인:

- GitHub 在 2026-10-15 的公告中宣布 AI Scan 正式可用。公告称无需 Copilot 许可证；组织的私有和内部仓库仍须具备 GitHub Code Security 或 Advanced Security。这些条件与预览公告不同。
- 后续公告保留了发现仅供参考的定位，并说明 AI Scan 不能通过规则集阻止合并。它不会对来自 fork 的拉取请求或由 Dependabot 创建的拉取请求运行。
- 后续计费模式消耗 Code Security AI Credits，在企业 AI 用量中显示于 Advanced Security 项下。无需 Copilot 许可证，并不意味着扫描没有使用费用。

검토 초점: 解读当前使用资格和计费条件时，应采用后续公告，同时保留预览条件作为历史记录。建议性的发现需要人员响应，不能替代必需检查或全面的安全验证。

### 日本語 (ja)

AI コードスキャン：プレビューの条件と後の一般提供

1. プレビュー開始時、GitHub はプルリクエストの AI 検出を、CodeQL の対応範囲を超えて言語・フレームワークのカバレッジを広げるものと説明した。別の AI エンジンが分析するにもかかわらず、エンタープライズ側の許可、組織での有効化、リポジトリの CodeQL デフォルト分析が必要だった。

2. プレビューの検出結果は参考情報であり、マージを阻止しなかった。告知では、パブリックプレビュー中は Copilot ライセンスが必要で、組織の AI クレジットを消費するとしていた。そのため、当初の機能は自動承認ゲートでも、無条件の無料サービスでもなかった。

후속 확인:

- GitHub の 2026-10-15 の告知は、AI Scan の一般提供を発表している。Copilot ライセンスは不要としているが、組織の非公開・内部リポジトリには引き続き GitHub Code Security または Advanced Security が必要である。これらの条件はプレビューの告知とは異なる。
- 後の告知でも検出結果は助言にとどまり、AI Scan はルールセットでマージを阻止できないとしている。フォークからのプルリクエストや、Dependabot が作成したプルリクエストでは実行されない。
- 後の課金方式では Code Security AI Credits を消費し、企業の AI 使用量では Advanced Security の項目に表示される。Copilot ライセンスが不要でも、スキャンの利用料金が発生しないという意味ではない。

검토 초점: 現在の利用条件と課金の解釈には後の告知を使い、プレビュー時の条件は履歴として残す。助言としての検出結果には人による対応が必要であり、必須チェックや包括的なセキュリティ検証の代わりにはならない。

### Deutsch (de)

KI-Codeanalyse: Vorschau-Bedingungen und spätere allgemeine Verfügbarkeit

1. Beim Start der Vorschau beschrieb GitHub die KI-Erkennung in Pull Requests als Erweiterung der Sprach- und Framework-Abdeckung über CodeQL hinaus. Obwohl eine separate KI-Engine analysierte, waren die Erlaubnis auf Unternehmensebene, die Aktivierung in der Organisation und die CodeQL-Standardanalyse im Repository erforderlich.

2. Die Ergebnisse der Vorschau dienten nur zur Information und blockierten keine Merges. Laut Ankündigung war während der öffentlichen Vorschau eine Copilot-Lizenz erforderlich; außerdem wurden KI-Credits der Organisation verbraucht. Die ursprüngliche Funktion war somit weder eine automatische Freigabeschranke noch ein uneingeschränkt kostenloser Dienst.

후속 확인:

- GitHub kündigt in der Mitteilung vom 2026-10-15 die allgemeine Verfügbarkeit von AI Scan an. Eine Copilot-Lizenz sei nicht erforderlich; private und interne Organisations-Repositories benötigen weiterhin GitHub Code Security oder Advanced Security. Diese Bedingungen unterscheiden sich von der Vorschau-Ankündigung.
- In der späteren Mitteilung bleiben die Ergebnisse rein beratend. AI Scan kann demnach Merges nicht über Regelsätze blockieren. Die Analyse läuft weder auf Pull Requests aus Forks noch auf von Dependabot erstellten Pull Requests.
- Das spätere Abrechnungsmodell verbraucht Code Security AI Credits, die in der KI-Nutzungsübersicht des Unternehmens unter Advanced Security erscheinen. Ohne Copilot-Lizenz auszukommen bedeutet nicht, dass für die Analyse keine Nutzungsgebühren anfallen.

검토 초점: Für die Auslegung aktueller Zugangs- und Abrechnungsbedingungen die spätere Mitteilung heranziehen und die Vorschau-Bedingungen als historischen Stand erhalten. Beratende Ergebnisse erfordern eine menschliche Reaktion und ersetzen weder Pflichtprüfungen noch eine umfassende Sicherheitsvalidierung.

### Français (fr)

Analyse de code par IA : conditions de préversion et disponibilité générale ultérieure

1. Au lancement de la préversion, GitHub présentait les détections par IA dans les pull requests comme une extension de la couverture des langages et frameworks au-delà de CodeQL. L’autorisation au niveau de l’entreprise, l’activation dans l’organisation et l’analyse CodeQL par défaut du dépôt étaient nécessaires, même si un moteur d’IA distinct réalisait l’analyse.

2. Les résultats de préversion étaient informatifs et ne bloquaient pas les fusions. L’annonce exigeait une licence Copilot et indiquait une consommation des crédits d’IA de l’organisation pendant la préversion publique. La fonction initiale n’était donc ni un mécanisme d’approbation automatique ni un service gratuit sans condition.

후속 확인:

- L’avis de GitHub du 2026-10-15 annonce la disponibilité générale d’AI Scan. Il indique qu’une licence Copilot n’est pas nécessaire ; les dépôts privés et internes d’une organisation nécessitent toujours GitHub Code Security ou Advanced Security. Ces conditions diffèrent de celles de la préversion.
- L’avis ultérieur maintient le caractère consultatif des résultats et précise qu’AI Scan ne peut pas bloquer les fusions via des ensembles de règles. Il ne s’exécute ni sur les pull requests provenant de forks ni sur celles créées par Dependabot.
- Le modèle de facturation ultérieur consomme des Code Security AI Credits, affichés sous Advanced Security dans l’utilisation de l’IA de l’entreprise. L’absence d’exigence de licence Copilot ne signifie pas que l’analyse est sans frais d’utilisation.

검토 초점: S’appuyer sur l’avis ultérieur pour interpréter les conditions actuelles d’accès et de facturation, tout en conservant celles de la préversion comme historique. Les résultats consultatifs nécessitent une réponse humaine et ne remplacent ni les contrôles obligatoires ni une validation complète de la sécurité.

### Русский (ru)

AI-сканирование кода: условия предварительной версии и последующая общая доступность

1. При запуске предварительной версии GitHub описывала AI-проверки pull request как расширение охвата языков и фреймворков за пределы CodeQL. Хотя анализ выполнял отдельный AI-движок, требовались разрешение на уровне предприятия, включение функции в организации и стандартный анализ CodeQL в репозитории.

2. Результаты предварительной версии носили информационный характер и не блокировали слияние. Объявление требовало лицензию Copilot и предусматривало расход AI-кредитов организации во время публичной предварительной версии. Поэтому исходная функция не была ни автоматическим этапом одобрения, ни безусловно бесплатным сервисом.

후속 확인:

- В уведомлении GitHub от 2026-10-15 объявлена общая доступность AI Scan. В нём сказано, что лицензия Copilot не требуется; для частных и внутренних репозиториев организаций по-прежнему нужны GitHub Code Security или Advanced Security. Эти условия отличаются от объявления предварительной версии.
- В последующем уведомлении результаты остаются рекомендательными: AI Scan не может блокировать слияние через наборы правил. Проверка не выполняется для pull request из форков и для pull request, созданных Dependabot.
- Последующая модель оплаты расходует Code Security AI Credits, которые отображаются в разделе Advanced Security в учёте использования AI предприятия. Отсутствие требования лицензии Copilot не означает отсутствие платы за использование сканирования.

검토 초점: При трактовке текущих условий доступа и оплаты используйте последующее уведомление, сохраняя условия предварительной версии как исторические. Рекомендательные результаты требуют реакции человека и не заменяют обязательные проверки или всестороннюю проверку безопасности.

## Copilot model retirement: scope, alternatives and code-review exception

원문: https://github.blog/changelog/2026-06-05-gpt-5-2-and-gpt-5-2-codex-deprecated

검토 기준: 영어 보강본 28ede0247b95214f, 2026-10-25T12:23:59+00:00

### 영어 기준본

1. GitHub announced GPT-5.2 and GPT-5.2-Codex deprecation on 2026-06-05 across most Copilot experiences, while explicitly retaining GPT-5.2 for Copilot code review in that announcement. This does not establish retirement across other providers or APIs.

> Note that GPT-5.2 is still available as part of Copilot code review.

근거: https://github.blog/changelog/2026-06-05-gpt-5-2-and-gpt-5-2-codex-deprecated

> As of today, June 5, 2026, we have deprecated the following models across most GitHub Copilot experiences

근거: https://github.blog/changelog/2026-06-05-gpt-5-2-and-gpt-5-2-codex-deprecated

2. The announcement suggests GPT-5.5 for GPT-5.2 and GPT-5.3-Codex for GPT-5.2-Codex. Enterprise administrators may need to enable alternatives through model policies before users can select them.

> Copilot Enterprise administrators may need to enable access to alternative models through their model policies in Copilot settings.

근거: https://github.blog/changelog/2026-06-05-gpt-5-2-and-gpt-5-2-codex-deprecated

> GPT-5.2 2026-06-05 GPT-5.5 GPT-5.2-Codex 2026-06-05 GPT-5.3-Codex

근거: https://github.blog/changelog/2026-06-05-gpt-5-2-and-gpt-5-2-codex-deprecated

검토 초점: Check the specific Copilot product and organization policy before migrating. These are the historical notice’s exceptions and alternatives, not a claim that its model availability remains unchanged today.

### 简体中文 (zh-CN)

Copilot 模型停用：范围、替代方案与代码审查例外

1. GitHub 宣布于 2026-06-05 在大多数 Copilot 体验中弃用 GPT-5.2 和 GPT-5.2-Codex，同时在该公告中明确保留 GPT-5.2 用于 Copilot 代码审查。这并不能证明其他提供商或 API 也停用了这些模型。

2. 公告建议用 GPT-5.5 替代 GPT-5.2，用 GPT-5.3-Codex 替代 GPT-5.2-Codex。企业管理员可能需要先通过模型策略启用替代模型，用户才能选择它们。

검토 초점: 迁移前，检查具体的 Copilot 产品和组织策略。这里记录的是历史公告中的例外与替代方案，并不声称其中的模型可用性至今没有变化。

### 日本語 (ja)

Copilot のモデル廃止：対象範囲・代替モデル・コードレビューの例外

1. GitHub は、2026-06-05 にほとんどの Copilot 利用環境で GPT-5.2 と GPT-5.2-Codex を廃止したと発表した。一方、同じ告知で Copilot のコードレビューには GPT-5.2 を明示的に残している。これにより、他の提供元や API でも廃止されたと確認できるわけではない。

2. 告知では、GPT-5.2 の代替に GPT-5.5、GPT-5.2-Codex の代替に GPT-5.3-Codex を挙げている。ユーザーが選択する前に、エンタープライズ管理者がモデルポリシーで代替モデルを有効にする必要がある場合がある。

검토 초점: 移行前に、対象となる Copilot 製品と組織ポリシーを確認する。ここで示すのは過去の告知に記載された例外と代替案であり、モデルの利用可否が現在も変わらないと主張するものではない。

### Deutsch (de)

Copilot-Modellabkündigung: Umfang, Alternativen und Ausnahme für Code-Reviews

1. GitHub gab bekannt, dass GPT-5.2 und GPT-5.2-Codex am 2026-06-05 in den meisten Copilot-Nutzungsumgebungen eingestellt wurden. Die Mitteilung hielt ausdrücklich fest, dass GPT-5.2 für Copilot-Code-Reviews weiterhin verfügbar war. Daraus lässt sich keine Einstellung bei anderen Anbietern oder APIs ableiten.

2. Die Ankündigung empfiehlt GPT-5.5 als Ersatz für GPT-5.2 und GPT-5.3-Codex als Ersatz für GPT-5.2-Codex. Unternehmensadministratoren müssen Alternativen gegebenenfalls erst über Modellrichtlinien aktivieren, bevor Nutzer sie auswählen können.

검토 초점: Vor der Migration das konkrete Copilot-Produkt und die Organisationsrichtlinie prüfen. Dies sind Ausnahmen und Alternativen der historischen Mitteilung, keine Aussage darüber, dass die damalige Modellverfügbarkeit bis heute unverändert geblieben ist.

### Français (fr)

Retrait de modèles Copilot : périmètre, alternatives et exception pour la revue de code

1. GitHub a annoncé l’abandon de GPT-5.2 et GPT-5.2-Codex le 2026-06-05 dans la plupart des environnements Copilot, tout en conservant explicitement GPT-5.2 pour la revue de code Copilot dans cette annonce. Cela ne démontre pas leur retrait chez d’autres fournisseurs ou dans d’autres API.

2. L’annonce propose GPT-5.5 pour remplacer GPT-5.2 et GPT-5.3-Codex pour remplacer GPT-5.2-Codex. Les administrateurs d’entreprise peuvent devoir activer les alternatives dans les règles de gestion des modèles avant que les utilisateurs puissent les sélectionner.

검토 초점: Avant de migrer, vérifier le produit Copilot concerné et les règles de l’organisation. Il s’agit des exceptions et alternatives de l’avis historique, sans affirmer que la disponibilité de ces modèles est restée inchangée jusqu’à aujourd’hui.

### Русский (ru)

Вывод моделей Copilot: охват, альтернативы и исключение для проверки кода

1. GitHub объявила о прекращении использования GPT-5.2 и GPT-5.2-Codex с 2026-06-05 в большинстве вариантов работы с Copilot, явно сохранив в том же объявлении GPT-5.2 для проверки кода Copilot. Это не подтверждает вывод моделей у других поставщиков или в других API.

2. Объявление предлагает GPT-5.5 вместо GPT-5.2 и GPT-5.3-Codex вместо GPT-5.2-Codex. Администраторам предприятия может потребоваться сначала включить альтернативы через политики моделей, прежде чем пользователи смогут их выбрать.

검토 초점: Перед переходом проверьте конкретный продукт Copilot и политику организации. Здесь приведены исключения и альтернативы исторического уведомления, а не утверждение о неизменной доступности моделей на сегодняшний день.

## Spring portfolio: security-report triage and patching

원문: https://spring.io/blog/2026/06/01/spring_and_security_in_the_times_of_ai

검토 기준: 영어 보강본 2b6f4abe346a373d, 2026-10-25T12:23:59+00:00

### 영어 기준본

1. Spring warned that the majority of portfolio projects would require upgrades for the scheduled security patches and recommended applying the latest patches. This was a release-train notice, not an affected-version matrix for every application.

> The majority of projects within the Spring portfolio will require upgrades for newly released security patches.

근거: https://spring.io/blog/2026/06/01/spring_and_security_in_the_times_of_ai

2. The team explicitly distinguishes incoming security reports from issued CVEs: reports can include duplicates or invalid findings and require maintainer triage. Report volume alone does not establish vulnerability severity.

> not every security report results in a new CVE being issued.

근거: https://spring.io/blog/2026/06/01/spring_and_security_in_the_times_of_ai

> duplicates or invalid findings that get filtered out

근거: https://spring.io/blog/2026/06/01/spring_and_security_in_the_times_of_ai

검토 초점: Map actual application dependencies to individual advisories and supported release lines. This brief does not independently reproduce the vendor’s report statistics or establish that every application is exploitable.

### 简体中文 (zh-CN)

Spring 项目组合：安全报告分诊与补丁

1. Spring 提醒，其项目组合中的大多数项目都需要升级，以应用计划发布的安全补丁，并建议安装最新补丁。这是一份系列发布公告，并非针对每个应用的受影响版本对照表。

2. 团队明确区分了收到的安全报告与已发布的 CVE：报告可能重复或无效，需要维护者分诊。仅凭报告数量无法确定漏洞的严重程度。

검토 초점: 将应用实际使用的依赖映射到各项安全公告及仍受支持的发布分支。本简报未独立复现厂商的报告统计，也未证明每个应用都可被利用。

### 日本語 (ja)

Spring 製品群：セキュリティ報告のトリアージとパッチ適用

1. Spring は、予定されたセキュリティパッチを適用するには製品群の大半のプロジェクトでアップグレードが必要になると警告し、最新パッチの適用を勧めた。これは一連のリリースに関する告知であり、各アプリケーションの影響バージョン一覧ではない。

2. チームは、受け付けたセキュリティ報告と発行済み CVE を明確に区別している。報告には重複や無効な指摘が含まれる場合があり、メンテナーによるトリアージが必要である。報告件数だけでは脆弱性の深刻度は判断できない。

검토 초점: 実際のアプリケーション依存関係を、個々のアドバイザリとサポート対象のリリース系列に対応付ける。この短報は、ベンダーの報告統計を独立に再現したものでも、すべてのアプリケーションが攻撃可能と確認したものでもない。

### Deutsch (de)

Spring-Portfolio: Sicherheitsmeldungen bewerten und Patches einspielen

1. Spring warnte, dass die Mehrheit der Portfolio-Projekte für die vorgesehenen Sicherheitspatches aktualisiert werden müsse, und empfahl die neuesten Patches. Dies war eine Mitteilung zu einer Release-Reihe, keine Matrix betroffener Versionen für jede Anwendung.

2. Das Team unterscheidet ausdrücklich zwischen eingehenden Sicherheitsmeldungen und veröffentlichten CVEs: Meldungen können Duplikate oder ungültige Befunde enthalten und müssen von den Maintainerinnen und Maintainern bewertet werden. Die Zahl der Meldungen allein belegt nicht die Schwere von Schwachstellen.

검토 초점: Die tatsächlich verwendeten Anwendungsabhängigkeiten den einzelnen Sicherheitshinweisen und unterstützten Release-Linien zuordnen. Dieser Kurzbericht reproduziert die Meldestatistik des Anbieters nicht unabhängig und belegt nicht, dass jede Anwendung ausnutzbar ist.

### Français (fr)

Portefeuille Spring : triage des signalements de sécurité et correctifs

1. Spring a averti que la majorité des projets de son portefeuille nécessiteraient une mise à niveau pour les correctifs de sécurité prévus et a recommandé d’appliquer les derniers correctifs. Il s’agissait d’un avis relatif à un train de versions, pas d’une matrice des versions affectées pour chaque application.

2. L’équipe distingue explicitement les signalements de sécurité reçus des CVE publiées : les signalements peuvent être des doublons ou des constats invalides et nécessitent un triage par les responsables de maintenance. Leur volume ne suffit pas à établir la gravité des vulnérabilités.

검토 초점: Associer les dépendances réelles de l’application aux avis individuels et aux branches de versions prises en charge. Cette brève ne reproduit pas indépendamment les statistiques de signalement de l’éditeur et ne démontre pas que chaque application est exploitable.

### Русский (ru)

Проекты Spring: разбор сообщений о безопасности и установка исправлений

1. Spring предупредила, что большинству проектов её портфеля потребуются обновления для запланированных исправлений безопасности, и рекомендовала установить последние исправления. Это было уведомление о серии выпусков, а не матрица затронутых версий для каждого приложения.

2. Команда явно различает поступающие сообщения о безопасности и опубликованные CVE: сообщения могут дублироваться или содержать некорректные результаты и требуют разбора сопровождающими. Одно лишь количество сообщений не определяет серьёзность уязвимостей.

검토 초점: Сопоставьте фактические зависимости приложения с отдельными уведомлениями безопасности и поддерживаемыми ветками выпусков. Этот краткий обзор не воспроизводит независимо статистику сообщений поставщика и не подтверждает, что каждое приложение уязвимо для эксплуатации.

## Workers and Durable Objects gain on-demand resource profiles

원문: https://blog.cloudflare.com/workers-on-demand-profiling/

검토 기준: 영어 보강본 38bfcb4310c98b8d, 2026-10-25T05:21:13+00:00

### 영어 기준본

1. Cloudflare announced CPU and memory profiling for Workers and Durable Objects, with on-demand collection and downloadable profiles described in the article.

> support for CPU and memory profiling of Workers and Durable Objects

근거: https://blog.cloudflare.com/workers-on-demand-profiling/

2. For CPU profiling, the implementation starts a V8 profiler with a one millisecond sampling interval. That sampling detail is not evidence of zero production overhead.

> begin sampling at a one millisecond interval.

근거: https://blog.cloudflare.com/workers-on-demand-profiling/

검토 초점: Check that the requested version and isolate are active at the selected location, and compare behavior with and without profiling under representative traffic. Resource allocation samples and retained memory are different questions.

### 简体中文 (zh-CN)

Workers 和 Durable Objects 新增按需资源性能剖析

1. Cloudflare 宣布为 Workers 和 Durable Objects 提供 CPU 与内存性能剖析；文章介绍了按需采集和可下载的剖析数据。

2. 在 CPU 性能剖析中，该实现以 1 毫秒的采样间隔启动 V8 profiler。这项采样细节并不能证明生产环境中的开销为零。

검토 초점: 检查所请求的版本和 isolate 是否在所选位置处于运行状态，并在有代表性的流量下对比开启与关闭性能剖析时的行为。资源分配采样与保留内存回答的是不同问题。

### 日本語 (ja)

Workers と Durable Objects にオンデマンドのリソースプロファイリング

1. Cloudflare は、Workers と Durable Objects 向けの CPU・メモリプロファイリングを発表した。記事では、必要なときの収集とプロファイルのダウンロードを説明している。

2. CPU プロファイリングの実装では、サンプリング間隔を 1 ミリ秒に設定して V8 プロファイラーを起動する。このサンプリングの仕様だけでは、本番環境でのオーバーヘッドがゼロとはいえない。

검토 초점: 指定したバージョンと isolate が選択した場所で稼働しているか確認し、代表的なトラフィックでプロファイリング有無の動作を比較する。リソース割り当てのサンプルと保持メモリは、それぞれ異なる問いに答えるものとして区別する。

### Deutsch (de)

Workers und Durable Objects erhalten Ressourcenprofile auf Abruf

1. Cloudflare kündigte CPU- und Speicher-Profiling für Workers und Durable Objects an. Der Artikel beschreibt die Erfassung auf Abruf und herunterladbare Profile.

2. Für das CPU-Profiling startet die Implementierung einen V8-Profiler mit einem Abtastintervall von 1 Millisekunde. Dieses Abtastdetail belegt nicht, dass im Produktivbetrieb kein zusätzlicher Aufwand entsteht.

검토 초점: Prüfen, ob die angeforderte Version und das Isolate am ausgewählten Standort aktiv sind. Das Verhalten mit und ohne Profiling unter repräsentativem Datenverkehr vergleichen. Stichproben zur Ressourcenzuweisung und im Speicher gehaltene Daten beantworten unterschiedliche Fragen.

### Français (fr)

Workers et Durable Objects proposent des profils de ressources à la demande

1. Cloudflare a annoncé le profilage du CPU et de la mémoire pour Workers et Durable Objects. L’article décrit une collecte à la demande et des profils téléchargeables.

2. Pour le profilage du CPU, l’implémentation lance un profileur V8 avec un intervalle d’échantillonnage de 1 milliseconde. Ce détail ne prouve pas l’absence de surcoût en production.

검토 초점: Vérifier que la version et l’isolate demandés sont actifs à l’emplacement choisi, puis comparer le comportement avec et sans profilage sous un trafic représentatif. Les échantillons d’allocation de ressources et la mémoire retenue répondent à des questions différentes.

### Русский (ru)

Workers и Durable Objects получили профилирование ресурсов по запросу

1. Cloudflare объявила о профилировании CPU и памяти для Workers и Durable Objects. В статье описаны сбор по запросу и возможность загрузки профилей.

2. Для профилирования CPU реализация запускает профилировщик V8 с интервалом выборки 1 миллисекунда. Эта особенность выборки не доказывает отсутствие накладных расходов в производственной среде.

검토 초점: Проверьте, что нужные версия и isolate активны в выбранном расположении, и сравните поведение с профилированием и без него на типичном трафике. Выборки выделения ресурсов и удерживаемая память отвечают на разные вопросы.

