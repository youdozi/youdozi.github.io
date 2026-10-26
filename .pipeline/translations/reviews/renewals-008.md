# 다국어 번역 검토 초안

의미·용어·조건 대조와 대상 언어 교정은 AI로 검토합니다. 수치·제품명 검사는 의미 검토를 대체하지 않습니다. 사이트 게시는 사용자의 명시적 승인 후에 진행합니다.

## Copilot cloud agent model options and usage multipliers

원문: https://github.blog/changelog/2026-05-18-copilot-cloud-agent-fast-cost-efficient-models-for-simple-tasks

검토 기준: 영어 보강본 973739bcb859e5ab, 2026-10-25T06:31:18+00:00

### 영어 기준본

1. GitHub added Claude Haiku 4.5 and GPT-5.4-mini as Copilot cloud agent model options. The notice frames them as options for simpler changes, not universal replacements for complex work.

> Claude Haiku 4.5 (0.33x multiplier) GPT-5.4-mini

근거: https://github.blog/changelog/2026-05-18-copilot-cloud-agent-fast-cost-efficient-models-for-simple-tasks

2. The notice lists a 0.33x multiplier for each added model. A usage multiplier is not a measured guarantee of runtime, code quality or total project cost.

> GPT-5.4-mini (0.33x multiplier)

근거: https://github.blog/changelog/2026-05-18-copilot-cloud-agent-fast-cost-efficient-models-for-simple-tasks

검토 초점: Evaluate representative tasks for correctness, retries and review effort alongside usage charges. Verify the current product model list and policies instead of treating this historical multiplier as a current price quotation.

### 简体中文 (zh-CN)

Copilot 云端代理的模型选项与用量倍率

1. GitHub 将 Claude Haiku 4.5 和 GPT-5.4-mini 加入 Copilot 云端代理的模型选项。公告将它们定位为处理较简单变更的选项，并非复杂工作的通用替代方案。

2. 公告为每个新增模型列出的用量倍率都是 0.33x。用量倍率并不是通过测量得出的运行时间、代码质量或项目总成本保证。

검토 초점: 评估代表性任务时，应同时考察正确性、重试次数、审核工作量和用量费用。应核实产品当前的模型列表与政策，不要将这一历史倍率当作现行报价。

### 日本語 (ja)

Copilot クラウドエージェントのモデル選択肢と使用量の倍率

1. GitHub は Copilot クラウドエージェントのモデル選択肢に Claude Haiku 4.5 と GPT-5.4-mini を追加した。告知では、比較的単純な変更向けの選択肢と位置付けており、複雑な作業を広く代替するものとはしていない。

2. 告知では、追加した各モデルの使用量の倍率を 0.33x と記載している。使用量の倍率は、実行時間、コード品質、プロジェクト全体のコストを測定して保証した値ではない。

검토 초점: 代表的なタスクで、利用料金と併せて正確性、再試行、レビューの負担を評価する。この過去の倍率を現在の見積価格と捉えず、製品の現在のモデル一覧とポリシーを確認する。

### Deutsch (de)

Copilot-Cloud-Agent: Modelloptionen und Nutzungsmultiplikatoren

1. GitHub hat Claude Haiku 4.5 und GPT-5.4-mini als Modelloptionen für den Copilot-Cloud-Agent hinzugefügt. Die Mitteilung stellt sie als Optionen für einfachere Änderungen vor, nicht als universellen Ersatz für komplexe Aufgaben.

2. Die Mitteilung nennt für jedes hinzugefügte Modell einen Nutzungsmultiplikator von 0.33x. Ein Nutzungsmultiplikator ist keine auf Messungen beruhende Garantie für Laufzeit, Codequalität oder Gesamtkosten eines Projekts.

검토 초점: Repräsentative Aufgaben auf Korrektheit, Wiederholungsversuche und Prüfaufwand bewerten und dabei auch die Nutzungsgebühren berücksichtigen. Die aktuelle Modellliste und die Richtlinien des Produkts prüfen, statt diesen historischen Multiplikator als aktuelles Preisangebot zu verstehen.

### Français (fr)

Agent cloud Copilot : modèles disponibles et multiplicateurs d’utilisation

1. GitHub a ajouté Claude Haiku 4.5 et GPT-5.4-mini aux modèles proposés pour l’agent cloud Copilot. L’annonce les présente comme des options pour des modifications plus simples, sans en faire des substituts universels pour les tâches complexes.

2. L’annonce indique un multiplicateur d’utilisation de 0.33x pour chacun des modèles ajoutés. Un multiplicateur d’utilisation ne constitue pas une garantie fondée sur des mesures du temps d’exécution, de la qualité du code ou du coût total du projet.

검토 초점: Évaluer, sur des tâches représentatives, la justesse des résultats, les nouvelles tentatives et l’effort de revue, en parallèle des frais d’utilisation. Vérifier la liste actuelle des modèles et les politiques du produit, sans considérer ce multiplicateur historique comme un tarif en vigueur.

### Русский (ru)

Облачный агент Copilot: выбор моделей и коэффициенты использования

1. GitHub добавила Claude Haiku 4.5 и GPT-5.4-mini в список моделей облачного агента Copilot. В объявлении они представлены как варианты для более простых изменений, а не как универсальная замена для сложной работы.

2. В объявлении для каждой добавленной модели указан коэффициент использования 0.33x. Такой коэффициент не является основанной на измерениях гарантией времени выполнения, качества кода или общей стоимости проекта.

검토 초점: На репрезентативных задачах оцените корректность, повторные попытки и трудозатраты на ревью вместе с платой за использование. Проверьте актуальный список моделей и правила продукта, не принимая этот исторический коэффициент за действующее ценовое предложение.

## BadHost: Starlette path-based authorization and proxy conditions

원문: https://www.infoq.com/news/2026/06/badhost-ai-systems-vulnerability/

검토 기준: 영어 보강본 9aee971925826c50, 2026-10-25T12:23:59+00:00

### 영어 기준본

1. The researchers explain that Starlette reconstructed a URL from an unvalidated Host header while routing used the actual request path. Authorization based on the reconstructed path could therefore disagree with the routed endpoint.

> routing in Starlette is based on the actual request path.

근거: https://www.x41-dsec.de/lab/advisories/x41-2026-002-starlette/

> does not perform any validation of the Host header value.

근거: https://www.x41-dsec.de/lab/advisories/x41-2026-002-starlette/

2. The researcher advisory lists affected Starlette versions as >= 0.8.3 and < 1.0.1, and identifies 1.0.1 as patched. Applicability still depends on the application’s path-based security decisions.

> Confirmed Affected Versions: starlette >= 0.8.3, < 1.0.1 Confirmed Patched Versions: starlette 1.0.1

근거: https://www.x41-dsec.de/lab/advisories/x41-2026-002-starlette/

후속 확인:

- At review time, the maintainer advisory says a proxy or load balancer mitigates this only if it rejects or normalizes malformed Host headers before forwarding and the application does not trust attacker-controlled host headers elsewhere.

검토 초점: Inspect authorization middleware, resolved dependencies and forwarded-header trust. Merely having a proxy is insufficient; test the real ingress configuration. No exploit experiment was performed for this draft.

### 简体中文 (zh-CN)

BadHost：Starlette 基于路径的授权与代理缓解条件

1. 研究人员解释，Starlette 使用未经验证的 Host 标头重建 URL，而路由使用实际的请求路径。因此，基于重建路径的授权判断可能与路由指向的端点不一致。

2. 研究人员的安全公告将受影响的 Starlette 版本列为 >= 0.8.3 且 < 1.0.1，并将 1.0.1 列为已修复版本。是否适用仍取决于应用是否根据路径作出安全判断。

후속 확인:

- 在本次审阅时，维护者的安全公告说明：只有代理或负载均衡器在转发前拒绝格式错误的 Host 标头或将其规范化，并且应用在其他地方也不信任攻击者控制的主机标头，才能缓解此问题。

검토 초점: 检查授权中间件、解析后的实际依赖版本，以及对转发标头的信任设置。仅有代理还不够，应测试真实的入口配置。本草稿未进行漏洞利用实验。

### 日本語 (ja)

BadHost：Starlette のパスに基づく認可とプロキシの緩和条件

1. 研究者によると、Starlette は未検証の Host ヘッダーから URL を再構成する一方、ルーティングには実際のリクエストパスを使っていた。そのため、再構成したパスに基づく認可の判断が、ルーティング先のエンドポイントと食い違う可能性がある。

2. 研究者のアドバイザリは、影響を受ける Starlette のバージョンを >= 0.8.3 かつ < 1.0.1、修正済みのバージョンを 1.0.1 としている。実際に該当するかは、アプリケーションがパスに基づいて行うセキュリティ判断にも依存する。

후속 확인:

- レビュー時点のメンテナーのアドバイザリによると、プロキシまたはロードバランサーが転送前に不正な Host ヘッダーを拒否するか正規化し、かつアプリケーションが他の箇所でも攻撃者の制御するホストヘッダーを信頼しない場合に限り、この問題を緩和できる。

검토 초점: 認可ミドルウェア、解決済みの依存関係、転送されたヘッダーの信頼設定を確認する。プロキシがあるだけでは不十分であり、実際の入口の設定をテストする。この草稿では脆弱性を悪用する実験は行っていない。

### Deutsch (de)

BadHost: Pfadbasierte Autorisierung in Starlette und Bedingungen für Proxys

1. Die Forschenden erklären, dass Starlette eine URL aus einem ungeprüften Host-Header rekonstruierte, während das Routing den tatsächlichen Anfragepfad verwendete. Die Autorisierung anhand des rekonstruierten Pfads konnte deshalb vom tatsächlich angesteuerten Endpunkt abweichen.

2. Der Sicherheitshinweis der Forschenden nennt Starlette-Versionen >= 0.8.3 und < 1.0.1 als betroffen und 1.0.1 als gepatcht. Ob eine Anwendung betroffen ist, hängt weiterhin von ihren pfadbasierten Sicherheitsentscheidungen ab.

후속 확인:

- Zum Zeitpunkt dieser Prüfung besagt der Sicherheitshinweis der Maintainer, dass ein Proxy oder Load Balancer das Problem nur dann abmildert, wenn er fehlerhafte Host-Header vor der Weiterleitung zurückweist oder normalisiert und die Anwendung auch an anderen Stellen keinen vom Angreifer kontrollierten Host-Headern vertraut.

검토 초점: Autorisierungs-Middleware, aufgelöste Abhängigkeiten und das Vertrauen in weitergeleitete Header prüfen. Ein Proxy allein reicht nicht aus; die tatsächliche Eingangskonfiguration testen. Für diesen Entwurf wurde kein Exploit-Experiment durchgeführt.

### Français (fr)

BadHost : autorisation fondée sur le chemin dans Starlette et conditions côté proxy

1. Les chercheurs expliquent que Starlette reconstruisait une URL à partir d’un en-tête Host non validé, tandis que le routage utilisait le chemin réel de la requête. Une autorisation fondée sur le chemin reconstruit pouvait donc diverger du point de terminaison ciblé par le routage.

2. L’avis des chercheurs indique que les versions de Starlette >= 0.8.3 et < 1.0.1 sont touchées et que la version 1.0.1 est corrigée. L’applicabilité dépend toujours des décisions de sécurité que l’application prend en fonction du chemin.

후속 확인:

- Au moment de cette revue, l’avis des mainteneurs précise qu’un proxy ou un répartiteur de charge n’atténue ce problème que s’il rejette ou normalise les en-têtes Host mal formés avant de les transmettre, et si l’application ne fait pas non plus confiance ailleurs à des en-têtes d’hôte contrôlés par un attaquant.

검토 초점: Examiner le middleware d’autorisation, les dépendances résolues et la confiance accordée aux en-têtes transmis. La seule présence d’un proxy ne suffit pas ; tester la configuration réelle du point d’entrée. Aucun essai d’exploitation n’a été réalisé pour ce brouillon.

### Русский (ru)

BadHost: авторизация по пути в Starlette и условия для прокси

1. Исследователи объясняют, что Starlette восстанавливала URL из непроверенного заголовка Host, тогда как маршрутизация использовала фактический путь запроса. Поэтому авторизация по восстановленному пути могла не соответствовать конечной точке, выбранной маршрутизацией.

2. В бюллетене исследователей затронутыми названы версии Starlette >= 0.8.3 и < 1.0.1, а исправленной — версия 1.0.1. Применимость проблемы по-прежнему зависит от решений безопасности, которые приложение принимает на основе пути.

후속 확인:

- На момент этой проверки в бюллетене сопровождающих указано, что прокси или балансировщик нагрузки смягчает проблему только в том случае, если он отклоняет или нормализует некорректные заголовки Host до пересылки, а приложение также не доверяет контролируемым злоумышленником заголовкам хоста в других местах.

검토 초점: Проверьте промежуточное ПО авторизации, фактически выбранные версии зависимостей и настройки доверия к пересылаемым заголовкам. Самого наличия прокси недостаточно; протестируйте реальную конфигурацию входящего трафика. Для этого черновика эксперименты по эксплуатации уязвимости не проводились.

## Spring release roundup: selected platform and AI baselines

원문: https://www.infoq.com/news/2026/06/spring-news-roundup-jun08-2026/

검토 기준: 영어 보강본 9d263cda22c982a1, 2026-10-25T12:23:59+00:00

### 영어 기준본

1. The Spring Boot team announced 4.1.0 availability from Maven Central and says it includes fixes from Spring Boot 4.0.7. This summary covers that platform release rather than every project in the original roundup.

> It also includes all of the bug fixes, documentation improvements and security fixes from Spring Boot 4.0.7

근거: https://spring.io/blog/2026/06/10/spring-boot-4

> Spring Boot 4.1.0 has been released and is now available from Maven Central.

근거: https://spring.io/blog/2026/06/10/spring-boot-4

2. The Spring AI team announced 2.0.0 availability from Maven Central. Its documented baseline is Spring Boot 4.0 / 4.1 with Spring Framework 7.0, so applications should review compatibility before upgrading.

> Spring AI 2.0 has been designed to be used with Spring Boot 4.0 / 4.1 and Spring Framework 7.0

근거: https://spring.io/blog/2026/06/12/spring-ai-2-0-0-GA-available-now

> Spring AI 2.0.0 has been released and is now available from Maven Central!

근거: https://spring.io/blog/2026/06/12/spring-ai-2-0-0-GA-available-now

검토 초점: Check migration notes, dependency alignment and regression behavior. Other projects and individual CVEs mentioned in the original roundup have not been validated by this scoped summary.

### 简体中文 (zh-CN)

Spring 发布综述：选定的平台与 AI 基础版本

1. Spring Boot 团队宣布 4.1.0 已在 Maven Central 提供，并表示它包含 Spring Boot 4.0.7 的修复。本摘要仅涵盖该平台版本，而非原始综述中的所有项目。

2. Spring AI 团队宣布 2.0.0 已在 Maven Central 提供。其文档列出的基础版本是 Spring Boot 4.0 / 4.1 和 Spring Framework 7.0，因此应用在升级前应审查兼容性。

검토 초점: 检查迁移说明、依赖版本的协调情况和回归行为。原始综述中提及的其他项目与个别 CVE，未在这篇限定范围的摘要中得到验证。

### 日本語 (ja)

Spring リリース総覧：一部のプラットフォームと AI の基盤バージョン

1. Spring Boot チームは 4.1.0 が Maven Central で利用可能になったと発表し、Spring Boot 4.0.7 の修正も含むと説明している。この要約は当該プラットフォームのリリースを対象とし、元の総覧にあるすべてのプロジェクトを扱うものではない。

2. Spring AI チームは 2.0.0 が Maven Central で利用可能になったと発表した。文書上の基盤バージョンは Spring Boot 4.0 / 4.1 と Spring Framework 7.0 であるため、アプリケーションのアップグレード前に互換性を確認する必要がある。

검토 초점: 移行に関する注記、依存関係の整合性、リグレッションの有無を確認する。元の総覧で言及された他のプロジェクトや個々の CVE は、対象を限定したこの要約では検証していない。

### Deutsch (de)

Spring-Releaseüberblick: Ausgewählte Plattform- und KI-Basisversionen

1. Das Spring Boot-Team hat die Verfügbarkeit von 4.1.0 über Maven Central angekündigt und erklärt, dass die Version Korrekturen aus Spring Boot 4.0.7 enthält. Diese Zusammenfassung behandelt dieses Plattform-Release und nicht alle Projekte des ursprünglichen Überblicks.

2. Das Spring AI-Team hat die Verfügbarkeit von 2.0.0 über Maven Central angekündigt. Die dokumentierte Basis ist Spring Boot 4.0 / 4.1 mit Spring Framework 7.0; vor einem Upgrade sollten Anwendungen daher auf Kompatibilität geprüft werden.

검토 초점: Migrationshinweise, die Abstimmung der Abhängigkeiten und mögliches Regressionsverhalten prüfen. Andere Projekte und einzelne CVEs aus dem ursprünglichen Überblick wurden in dieser inhaltlich begrenzten Zusammenfassung nicht validiert.

### Français (fr)

Tour d’horizon des versions Spring : socles de plateforme et d’IA sélectionnés

1. L’équipe Spring Boot a annoncé la disponibilité de 4.1.0 sur Maven Central et indique que cette version inclut les correctifs de Spring Boot 4.0.7. Ce résumé couvre cette version de la plateforme, sans traiter tous les projets du tour d’horizon initial.

2. L’équipe Spring AI a annoncé la disponibilité de 2.0.0 sur Maven Central. Le socle documenté associe Spring Boot 4.0 / 4.1 à Spring Framework 7.0 ; la compatibilité des applications doit donc être examinée avant la mise à niveau.

검토 초점: Vérifier les notes de migration, la cohérence des dépendances et le comportement en matière de régressions. Les autres projets et les CVE individuelles mentionnés dans le tour d’horizon initial n’ont pas été validés dans ce résumé au périmètre limité.

### Русский (ru)

Обзор релизов Spring: выбранные базовые версии платформы и ИИ

1. Команда Spring Boot объявила о доступности 4.1.0 в Maven Central и сообщила, что в неё включены исправления из Spring Boot 4.0.7. Этот обзор охватывает указанный релиз платформы, а не все проекты из исходной подборки.

2. Команда Spring AI объявила о доступности 2.0.0 в Maven Central. Документированная основа — Spring Boot 4.0 / 4.1 вместе со Spring Framework 7.0, поэтому перед обновлением следует проверить совместимость приложений.

검토 초점: Проверьте примечания по миграции, согласованность зависимостей и наличие регрессий. Другие проекты и отдельные CVE, упомянутые в исходной подборке, в этом обзоре с ограниченным охватом не проверялись.

## Claude Sonnet 4 retirement announcement applies to Copilot

원문: https://github.blog/changelog/2026-05-07-claude-sonnet-4-deprecated

검토 기준: 영어 보강본 9efda109fcdd4210, 2026-10-25T06:06:33+00:00

### 영어 기준본

1. GitHub stated that Claude Sonnet 4 was deprecated across its Copilot experiences on 2026-05-06. The statement concerns Copilot rather than every Anthropic distribution channel.

> Claude Sonnet 4 2026-05-06

근거: https://github.blog/changelog/2026-05-07-claude-sonnet-4-deprecated

2. The announcement directs Copilot Enterprise administrators to check model policies when enabling alternatives.

> enable access to alternative models through their model policies

근거: https://github.blog/changelog/2026-05-07-claude-sonnet-4-deprecated

검토 초점: Separate product retirement, provider retirement and local fallback behavior. Test permissions and workflow behavior on supported choices instead of treating an old replacement recommendation as current guidance.

### 简体中文 (zh-CN)

Claude Sonnet 4 的停用公告适用于 Copilot

1. GitHub 表示，Claude Sonnet 4 已于 2026-05-06 在其各项 Copilot 使用场景中停用。该说明针对 Copilot，并不涵盖 Anthropic 的所有分发渠道。

2. 公告指引 Copilot Enterprise 管理员在启用替代模型时检查模型政策。

검토 초점: 区分产品内停用、提供商停用与本地回退行为。应在受支持的选项上测试权限与工作流行为，不要将旧的替代模型推荐当作当前指引。

### 日本語 (ja)

Claude Sonnet 4 の提供終了の告知は Copilot が対象

1. GitHub は、Copilot の各利用環境で Claude Sonnet 4 を 2026-05-06 に廃止したと述べている。この説明の対象は Copilot であり、Anthropic のすべての提供経路ではない。

2. 告知では、Copilot Enterprise の管理者に対し、代替モデルを有効にする際にモデルポリシーを確認するよう案内している。

검토 초점: 製品内での提供終了、プロバイダーによる提供終了、ローカルのフォールバック動作を区別する。過去の代替モデルの推奨を現在の指針と捉えず、サポート対象の選択肢で権限とワークフローの動作をテストする。

### Deutsch (de)

Die Abkündigung von Claude Sonnet 4 bezieht sich auf Copilot

1. GitHub erklärte, dass Claude Sonnet 4 am 2026-05-06 in sämtlichen Copilot-Nutzungsumgebungen abgekündigt wurde. Diese Aussage betrifft Copilot und nicht alle Vertriebskanäle von Anthropic.

2. Die Ankündigung fordert Administratoren von Copilot Enterprise dazu auf, beim Aktivieren von Alternativen die Modellrichtlinien zu prüfen.

검토 초점: Die Einstellung innerhalb eines Produkts, die Einstellung durch den Anbieter und das lokale Fallback-Verhalten unterscheiden. Berechtigungen und das Verhalten der Arbeitsabläufe mit unterstützten Optionen testen, statt eine frühere Ersatzempfehlung als aktuelle Anleitung zu verstehen.

### Français (fr)

L’annonce du retrait de Claude Sonnet 4 concerne Copilot

1. GitHub a indiqué que Claude Sonnet 4 avait été déprécié dans l’ensemble des environnements Copilot le 2026-05-06. Cette déclaration concerne Copilot, et non tous les canaux de distribution d’Anthropic.

2. L’annonce invite les administrateurs de Copilot Enterprise à vérifier les politiques de modèles lors de l’activation d’alternatives.

검토 초점: Distinguer le retrait au sein d’un produit, le retrait par le fournisseur et le comportement local de repli. Tester les autorisations et le comportement des workflows avec des options prises en charge, sans considérer une ancienne recommandation de remplacement comme un conseil actuel.

### Русский (ru)

Объявление о выводе Claude Sonnet 4 из эксплуатации касается Copilot

1. GitHub сообщила, что 2026-05-06 модель Claude Sonnet 4 была объявлена устаревшей во всех вариантах использования Copilot. Это заявление касается Copilot, а не всех каналов распространения Anthropic.

2. Объявление предписывает администраторам Copilot Enterprise проверять политики моделей при включении альтернатив.

검토 초점: Различайте вывод из эксплуатации внутри продукта, вывод из эксплуатации у поставщика и локальное поведение при переходе на резервный вариант. Проверяйте разрешения и работу процессов с поддерживаемыми вариантами, не принимая старую рекомендацию по замене за актуальное руководство.

## Spring Security releases and support boundaries in the April notice

원문: https://spring.io/blog/2026/04/21/spring-security-releases

검토 기준: 영어 보강본 ad44e1abd30ad1f2, 2026-10-25T05:38:18+00:00

### 영어 기준본

1. The April notice announces Spring Security 6.5.10, 7.0.5 and 7.1.0-RC1 and links the security advisories addressed by the releases. These are historical release versions.

> Spring Security 6.5.10 , 7.0.5 , and 7.1.0-RC1 .

근거: https://spring.io/blog/2026/04/21/spring-security-releases

2. It states that open-source support for the Spring Security 5.7.x, 5.8.x, 6.3.x and 6.4.x generations had ended. Commercial support is a separate scope.

> Spring Security 5.7.x, 5.8.x, 6.3.x, and 6.4.x generations has ended

근거: https://spring.io/blog/2026/04/21/spring-security-releases

검토 초점: Match deployed dependencies to each official advisory and supported release line. Do not select a historical version merely because it appears in this archive, and distinguish a release candidate from a stable release.

### 简体中文 (zh-CN)

四月公告中的 Spring Security 版本与支持范围

1. 四月公告宣布了 Spring Security 6.5.10、7.0.5 和 7.1.0-RC1，并链接至这些版本所处理的安全公告。这些都是历史发布版本。

2. 公告说明，Spring Security 5.7.x、5.8.x、6.3.x 和 6.4.x 系列的开源支持已经结束。商业支持属于另一个范围。

검토 초점: 将已部署的依赖与各项官方安全公告及受支持的发布分支对照。不要仅因为某个历史版本出现在本归档中就选择它，并应区分候选发布版和稳定版。

### 日本語 (ja)

四月の告知における Spring Security のリリースとサポート範囲

1. 四月の告知では Spring Security 6.5.10、7.0.5、7.1.0-RC1 を発表し、各リリースが対処するセキュリティアドバイザリへのリンクを示している。これらは過去のリリースバージョンである。

2. 告知は Spring Security 5.7.x、5.8.x、6.3.x、6.4.x 系列のオープンソースサポートが終了したと述べている。商用サポートは別の範囲である。

검토 초점: デプロイ済みの依存関係を、各公式アドバイザリとサポート対象のリリース系列に照合する。このアーカイブに載っているという理由だけで過去のバージョンを選ばず、リリース候補版と安定版を区別する。

### Deutsch (de)

Spring Security: Releases und Supportgrenzen in der April-Mitteilung

1. Die April-Mitteilung kündigt Spring Security 6.5.10, 7.0.5 und 7.1.0-RC1 an und verlinkt die Sicherheitshinweise, auf die diese Releases eingehen. Es handelt sich um historische Releaseversionen.

2. Sie erklärt, dass der Open-Source-Support für die Spring Security-Generationen 5.7.x, 5.8.x, 6.3.x und 6.4.x beendet war. Kommerzieller Support ist davon getrennt zu betrachten.

검토 초점: Die eingesetzten Abhängigkeiten mit jedem offiziellen Sicherheitshinweis und den unterstützten Releaselinien abgleichen. Eine historische Version nicht allein deshalb auswählen, weil sie in diesem Archiv vorkommt, und Release Candidates von stabilen Releases unterscheiden.

### Français (fr)

Spring Security : versions et limites du support dans l’annonce d’avril

1. L’annonce d’avril présente Spring Security 6.5.10, 7.0.5 et 7.1.0-RC1 et renvoie aux avis de sécurité traités par ces versions. Il s’agit de versions historiques.

2. Elle indique que le support open source des générations Spring Security 5.7.x, 5.8.x, 6.3.x et 6.4.x avait pris fin. Le support commercial relève d’un périmètre distinct.

검토 초점: Comparer les dépendances déployées à chaque avis officiel et aux branches de versions prises en charge. Ne pas choisir une version historique simplement parce qu’elle figure dans cette archive, et distinguer une version candidate d’une version stable.

### Русский (ru)

Spring Security: релизы и границы поддержки в апрельском объявлении

1. В апрельском объявлении представлены Spring Security 6.5.10, 7.0.5 и 7.1.0-RC1, а также ссылки на бюллетени безопасности, проблемы из которых решаются этими релизами. Это исторические версии релизов.

2. В нём указано, что поддержка в рамках open source для веток Spring Security 5.7.x, 5.8.x, 6.3.x и 6.4.x уже завершилась. Коммерческая поддержка рассматривается отдельно.

검토 초점: Сопоставьте развёрнутые зависимости с каждым официальным бюллетенем и поддерживаемыми ветками релизов. Не выбирайте историческую версию лишь потому, что она встречается в этом архиве, и отличайте релиз-кандидат от стабильного релиза.

