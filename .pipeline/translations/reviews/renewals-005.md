# 다국어 번역 검토 초안

의미·용어·조건 대조와 대상 언어 교정은 AI로 검토합니다. 수치·제품명 검사는 의미 검토를 대체하지 않습니다. 사이트 게시는 사용자의 명시적 승인 후에 진행합니다.

## Buildkite scopes pipeline secrets and adds pipeline validation tools

원문: https://www.infoq.com/news/2026/10/buildkite-ci-secrets-agentic/

검토 기준: 영어 보강본 50b97c32c1d2c027, 2026-10-25T05:21:13+00:00

### 영어 기준본

1. Buildkite describes pipeline secrets as cluster secrets restricted to the current pipeline, with additional access conditions available.

> Pipeline secrets are cluster secrets restricted to the current pipeline

근거: https://buildkite.com/resources/blog/what-shipped-at-buildkite-september-27-october-3-2026/

2. Its MCP server adds validate_pipeline to check pipeline YAML against the official schema before upload.

> validate_pipeline to check pipeline YAML against the official schema before upload

근거: https://buildkite.com/resources/blog/what-shipped-at-buildkite-september-27-october-3-2026/

검토 초점: Review secret exposure at individual steps and permissions granted to CI agents. Schema validation is a narrow check; execution behavior, plugins and permission boundaries still need separate review.

### 简体中文 (zh-CN)

Buildkite 限定流水线机密范围并新增流水线验证工具

1. Buildkite 将流水线机密描述为仅限当前流水线使用的集群机密，并可附加访问条件。

2. 其 MCP 服务器新增 validate_pipeline，可在上传前根据官方模式校验流水线 YAML。

검토 초점: 检查各个步骤中的机密暴露情况及授予 CI 代理的权限。模式校验的范围有限；执行行为、插件和权限边界仍需单独审查。

### 日本語 (ja)

Buildkite がパイプラインのシークレット範囲を限定し、検証ツールを追加

1. Buildkite は、パイプラインシークレットを現在のパイプラインに利用を限定したクラスターシークレットと説明している。追加のアクセス条件も設定できる。

2. MCP サーバーには validate_pipeline が追加され、アップロード前にパイプライン YAML を公式スキーマと照合できる。

검토 초점: 各ステップでのシークレットの露出と、CI エージェントに付与した権限を確認する。スキーマ検証で確認できる範囲は限られる。実行時の動作、プラグイン、権限境界は別途レビューする必要がある。

### Deutsch (de)

Buildkite begrenzt Pipeline-Secrets und ergänzt Werkzeuge zur Pipeline-Prüfung

1. Buildkite beschreibt Pipeline-Secrets als Cluster-Secrets, die auf die aktuelle Pipeline beschränkt sind. Zusätzliche Zugriffsbedingungen lassen sich festlegen.

2. Der MCP-Server bietet jetzt validate_pipeline, um Pipeline-YAML vor dem Hochladen gegen das offizielle Schema zu prüfen.

검토 초점: Die Offenlegung von Secrets in einzelnen Schritten und die Berechtigungen der CI-Agenten prüfen. Die Schemaprüfung deckt nur einen engen Bereich ab; Ausführungsverhalten, Plugins und Berechtigungsgrenzen benötigen weiterhin eine gesonderte Prüfung.

### Français (fr)

Buildkite limite la portée des secrets de pipeline et ajoute des outils de validation

1. Buildkite décrit les secrets de pipeline comme des secrets de cluster limités au pipeline courant, auxquels peuvent s’ajouter des conditions d’accès.

2. Son serveur MCP ajoute validate_pipeline pour vérifier le YAML du pipeline par rapport au schéma officiel avant son envoi.

검토 초점: Examiner l’exposition des secrets dans chaque étape et les autorisations accordées aux agents CI. La validation du schéma est un contrôle limité ; le comportement à l’exécution, les plugins et les frontières d’autorisation nécessitent une revue distincte.

### Русский (ru)

Buildkite ограничивает область действия секретов конвейера и добавляет средства проверки

1. Buildkite описывает секреты конвейера как секреты кластера, доступные только текущему конвейеру, с возможностью задать дополнительные условия доступа.

2. В MCP-сервер добавлен validate_pipeline для проверки YAML конвейера по официальной схеме перед загрузкой.

검토 초점: Проверьте раскрытие секретов на отдельных этапах и разрешения, выданные CI-агентам. Проверка схемы имеет ограниченный охват; поведение при выполнении, плагины и границы полномочий требуют отдельного рассмотрения.

## Azure DevOps Autofix: preview phases, review gates and billing

원문: https://www.infoq.com/news/2026/06/azuredevops-copilot-autofix/

검토 기준: 영어 보강본 52ee7abbb037f678, 2026-10-25T12:40:05+00:00

### 영어 기준본

1. Microsoft’s launch post describes Copilot Autofix for GitHub Advanced Security for Azure DevOps as a limited private preview with enrollment processed in waves. The launch post and later documentation must not be collapsed into an unchanged availability claim.

> Copilot Autofix is available today in limited private preview for GitHub Advanced Security for Azure DevOps.

근거: https://devblogs.microsoft.com/devops/copilot-autofix-for-github-advanced-security-for-azure-devops/

> Enablement is processed in waves

근거: https://devblogs.microsoft.com/devops/copilot-autofix-for-github-advanced-security-for-azure-devops/

2. The launch workflow generates a suggested change from supported CodeQL alerts and opens a pull request. Existing review and build gates still run, and the alert resolves after merge and the next CodeQL scan.

> Your usual review and build gates run on the pull request. Once it merges and the next CodeQL scan completes, the alert resolves on its own.

근거: https://devblogs.microsoft.com/devops/copilot-autofix-for-github-advanced-security-for-azure-devops/

후속 확인:

- At review time, the official guide labels the feature a limited public preview and says Microsoft is not accepting additional users. This is a later documented state, not evidence that the original private-preview wording was false.
- The current guide says fix generation consumes AI credits billed through the linked Azure subscription, and GitHub Copilot budgets and user limits do not govern that Azure DevOps meter. License inclusion should not be read as free fix generation.

검토 초점: Check enrollment, supported alert types and the linked Azure subscription before enabling generation. Validate fixes manually and through tests; generating a suggestion does not itself remediate an alert.

### 简体中文 (zh-CN)

Azure DevOps Autofix：预览阶段、审查关卡与计费

1. Microsoft 的发布文章将用于 GitHub Advanced Security for Azure DevOps 的 Copilot Autofix 描述为有限私有预览，分批处理加入申请。不能将发布文章与后续文档合并为一项可用性始终未变的声明。

2. 发布时介绍的流程会根据受支持的 CodeQL 告警生成修改建议并打开拉取请求。现有审查和构建关卡仍会运行，告警会在合并并完成下一次 CodeQL 扫描后消除。

후속 확인:

- 本次审阅时，官方指南将该功能标为有限公开预览，并称 Microsoft 不接受更多用户加入。这是后续文档记录的状态，并不能证明最初的私有预览表述有误。
- 本次审阅时的指南称，修复生成会消耗 AI 额度，并通过关联的 Azure 订阅计费；GitHub Copilot 的预算和用户限额不控制 Azure DevOps 的这项用量计费。许可证中包含该功能，不应被理解为修复生成免费。

검토 초점: 启用生成前，检查加入条件、受支持的告警类型和关联的 Azure 订阅。应手动验证修复并运行测试；生成建议本身并不会消除告警。

### 日本語 (ja)

Azure DevOps Autofix：プレビュー段階・レビュー条件・課金

1. Microsoft の公開開始時の記事は、GitHub Advanced Security for Azure DevOps 向けの Copilot Autofix を、参加申請を段階的に処理する限定プライベートプレビューと説明している。公開時の記事と後の文書をまとめて、利用条件が変わっていないと扱ってはならない。

2. 公開時に示されたワークフローは、対応する CodeQL アラートから変更案を生成してプルリクエストを開く。既存のレビューとビルドのゲートは引き続き実行され、アラートはマージとその後の CodeQL スキャンを経て解消される。

후속 확인:

- レビュー時点の公式ガイドは、この機能を限定パブリックプレビューと表記し、Microsoft は追加の利用者を受け付けていないとしている。これは後に文書化された状態であり、当初のプライベートプレビューという表記が誤りだった証拠ではない。
- レビュー時点のガイドによると、修正案の生成は AI クレジットを消費し、関連付けた Azure サブスクリプションに課金される。GitHub Copilot の予算やユーザー上限は、Azure DevOps のこの課金メーターを制御しない。ライセンスに含まれることを、修正案の無料生成と捉えてはならない。

검토 초점: 生成を有効にする前に、参加条件、対応アラートの種類、関連付けた Azure サブスクリプションを確認する。修正は手動確認とテストで検証する。提案を生成しただけでは、アラート自体は解消されない。

### Deutsch (de)

Azure DevOps Autofix: Vorschauphasen, Review-Gates und Abrechnung

1. Microsoft beschreibt Copilot Autofix für GitHub Advanced Security for Azure DevOps im Startbeitrag als begrenzte private Vorschau, deren Anmeldungen schrittweise bearbeitet werden. Der Startbeitrag und die spätere Dokumentation dürfen nicht zu einer Aussage über unveränderte Verfügbarkeit zusammengefasst werden.

2. Der zum Start beschriebene Ablauf erzeugt aus unterstützten CodeQL-Warnungen einen Änderungsvorschlag und öffnet einen Pull Request. Bestehende Review- und Build-Gates laufen weiterhin. Die Warnung wird nach dem Merge und dem nächsten CodeQL-Scan aufgelöst.

후속 확인:

- Zum Prüfzeitpunkt kennzeichnet der offizielle Leitfaden die Funktion als begrenzte öffentliche Vorschau und erklärt, dass Microsoft keine weiteren Nutzer aufnimmt. Dies ist ein später dokumentierter Stand, kein Beleg dafür, dass die ursprüngliche Bezeichnung als private Vorschau falsch war.
- Der zum Prüfzeitpunkt aktuelle Leitfaden erklärt, dass die Generierung von Korrekturen KI-Credits verbraucht, die über das verknüpfte Azure-Abonnement abgerechnet werden. GitHub Copilot-Budgets und Nutzerlimits steuern diesen Azure DevOps-Abrechnungszähler nicht. Die Einbeziehung in eine Lizenz bedeutet keine kostenlose Korrekturgenerierung.

검토 초점: Vor dem Aktivieren der Generierung die Aufnahmebedingungen, unterstützten Warnungstypen und das verknüpfte Azure-Abonnement prüfen. Korrekturen manuell und mit Tests validieren; die Erzeugung eines Vorschlags behebt für sich genommen keine Warnung.

### Français (fr)

Azure DevOps Autofix : phases de préversion, contrôles de revue et facturation

1. L’article de lancement de Microsoft décrit Copilot Autofix pour GitHub Advanced Security for Azure DevOps comme une préversion privée limitée, dont les inscriptions sont traitées par vagues. L’article initial et la documentation ultérieure ne doivent pas être fusionnés en une affirmation de disponibilité inchangée.

2. Le processus présenté au lancement génère une proposition de modification à partir d’alertes CodeQL prises en charge et ouvre une pull request. Les contrôles de revue et de compilation existants continuent de s’exécuter. L’alerte est résolue après la fusion et l’analyse CodeQL suivante.

후속 확인:

- Au moment de cette revue, le guide officiel qualifie la fonction de préversion publique limitée et indique que Microsoft n’accepte pas d’utilisateurs supplémentaires. Cet état documenté ultérieurement ne prouve pas que la formulation initiale de préversion privée était fausse.
- Le guide consulté lors de la revue indique que la génération de correctifs consomme des crédits d’IA facturés via l’abonnement Azure lié. Les budgets et limites par utilisateur de GitHub Copilot ne régissent pas cette mesure de facturation Azure DevOps. L’inclusion dans une licence ne signifie pas que la génération des correctifs est gratuite.

검토 초점: Avant d’activer la génération, vérifier les conditions d’inscription, les types d’alertes pris en charge et l’abonnement Azure lié. Valider les correctifs manuellement et par des tests ; la seule génération d’une suggestion ne corrige pas l’alerte.

### Русский (ru)

Azure DevOps Autofix: этапы предварительного доступа, проверки и оплата

1. В статье о запуске Microsoft описывает Copilot Autofix для GitHub Advanced Security for Azure DevOps как ограниченную закрытую предварительную версию с поэтапной обработкой заявок. Статью о запуске и последующую документацию нельзя объединять в утверждение о неизменных условиях доступности.

2. Описанный при запуске процесс создаёт предложение об изменении на основе поддерживаемых предупреждений CodeQL и открывает pull request. Существующие проверки при ревью и сборке продолжают выполняться; предупреждение устраняется после слияния и следующего сканирования CodeQL.

후속 확인:

- На момент проверки официальный справочник обозначает функцию как ограниченную публичную предварительную версию и сообщает, что Microsoft не принимает новых пользователей. Это более позднее документированное состояние, а не доказательство ошибочности первоначального описания закрытой предварительной версии.
- В руководстве на момент проверки сказано, что создание исправлений расходует AI-кредиты с оплатой через связанную подписку Azure. Бюджеты и пользовательские лимиты GitHub Copilot не управляют этим учётом потребления Azure DevOps. Включение функции в лицензию не означает бесплатного создания исправлений.

검토 초점: Перед включением генерации проверьте условия подключения, поддерживаемые типы предупреждений и связанную подписку Azure. Проверяйте исправления вручную и тестами: само создание предложения не устраняет предупреждение.

## Spring Boot milestone: LDAP and telemetry changes

원문: https://www.infoq.com/news/2026/09/spring-news-roundup-sep21-2026/

검토 기준: 영어 보강본 568305543e6754fa, 2026-10-25T05:21:13+00:00

### 영어 기준본

1. The Spring Boot 4.2.0-M2 milestone adds SSL bundle support for LDAP, including LDAPS for the embedded server. This draft verifies the Boot portion of the older roundup.

> Spring Boot 4.2.0-M2 has been released

근거: https://spring.io/blog/2026/09/25/spring-boot-4-2-0-M2-available-now

> SSL bundle support for LDAP

근거: https://spring.io/blog/2026/09/25/spring-boot-4-2-0-M2-available-now

2. The same milestone adds OpenTelemetry semantic-convention support alongside shared OTLP endpoint, header and compression configuration.

> OpenTelemetry's semantic conventions, alongside common OTLP endpoint, header, and compression configuration.

근거: https://spring.io/blog/2026/09/25/spring-boot-4-2-0-M2-available-now

검토 초점: Keep the original roundup date and describe these as milestone features. Before approving the entire original item, separately verify the Framework, Data, Security and Integration releases; this narrower draft does not verify those sections.

### 简体中文 (zh-CN)

Spring Boot 里程碑版本：LDAP 与遥测变更

1. Spring Boot 4.2.0-M2 里程碑版本新增 LDAP 的 SSL bundle 支持，包括嵌入式服务器的 LDAPS。本草稿核验的是旧版综述中的 Boot 部分。

2. 同一里程碑版本还新增 OpenTelemetry 语义约定支持，以及共享的 OTLP 端点、请求头和压缩配置。

검토 초점: 保留原始综述日期，并将这些能力描述为里程碑版本功能。在批准原条目整体内容前，应单独核验 Framework、Data、Security 和 Integration 的发布；本草稿范围更窄，未核验这些部分。

### 日本語 (ja)

Spring Boot のマイルストーン：LDAP とテレメトリの変更

1. Spring Boot 4.2.0-M2 マイルストーンでは、LDAP の SSL バンドル対応が追加され、組み込みサーバーの LDAPS も含まれる。この草稿で検証するのは、以前のまとめ記事の Boot 部分である。

2. 同じマイルストーンでは、共有の OTLP エンドポイント・ヘッダー・圧縮設定とともに、OpenTelemetry のセマンティック規約への対応が追加されている。

검토 초점: 元のまとめ記事の日付を保ち、これらをマイルストーンの機能として説明する。元の項目全体を承認する前に、Framework、Data、Security、Integration のリリースを別々に確認する。この草稿の範囲は限定されており、それらの部分は検証していない。

### Deutsch (de)

Spring-Boot-Meilenstein: Änderungen bei LDAP und Telemetrie

1. Der Meilenstein Spring Boot 4.2.0-M2 ergänzt SSL-Bundle-Unterstützung für LDAP, einschließlich LDAPS für den eingebetteten Server. Dieser Entwurf prüft den Boot-Teil der älteren Zusammenstellung.

2. Derselbe Meilenstein ergänzt Unterstützung für die semantischen Konventionen von OpenTelemetry sowie gemeinsame Einstellungen für OTLP-Endpunkt, Header und Kompression.

검토 초점: Das ursprüngliche Datum der Zusammenstellung beibehalten und die Änderungen als Meilenstein-Funktionen beschreiben. Vor der Freigabe des gesamten ursprünglichen Eintrags die Releases von Framework, Data, Security und Integration gesondert prüfen; dieser enger gefasste Entwurf bestätigt diese Abschnitte nicht.

### Français (fr)

Version jalon de Spring Boot : évolutions LDAP et télémétrie

1. La version jalon Spring Boot 4.2.0-M2 ajoute la prise en charge des bundles SSL pour LDAP, y compris LDAPS pour le serveur intégré. Ce brouillon vérifie la partie Boot de l’ancienne synthèse.

2. Le même jalon ajoute la prise en charge des conventions sémantiques OpenTelemetry ainsi qu’une configuration commune du point de terminaison, des en-têtes et de la compression OTLP.

검토 초점: Conserver la date de la synthèse initiale et présenter ces éléments comme des fonctionnalités de version jalon. Avant d’approuver l’intégralité de l’article initial, vérifier séparément les versions de Framework, Data, Security et Integration ; ce brouillon plus restreint ne vérifie pas ces sections.

### Русский (ru)

Промежуточный выпуск Spring Boot: изменения LDAP и телеметрии

1. Промежуточный выпуск Spring Boot 4.2.0-M2 добавляет поддержку SSL bundle для LDAP, включая LDAPS для встроенного сервера. Этот черновик проверяет часть Boot из более ранней подборки.

2. Тот же промежуточный выпуск добавляет поддержку семантических соглашений OpenTelemetry, а также общие настройки конечной точки OTLP, заголовков и сжатия.

검토 초점: Сохраняйте дату исходной подборки и описывайте эти возможности как функции промежуточного выпуска. Перед одобрением исходного пункта целиком отдельно проверьте выпуски Framework, Data, Security и Integration: этот более узкий черновик не проверяет соответствующие разделы.

## Cloudflare WAF response rules: actions and body limits

원문: https://blog.cloudflare.com/full-transaction-waf/

검토 기준: 영어 보강본 59c87ea544e0e5db, 2026-10-25T05:21:13+00:00

### 영어 기준본

1. Cloudflare WAF lets customers create up to three custom response rules supporting Log and Block actions.

> up to three custom response rules supporting Log and Block actions

근거: https://blog.cloudflare.com/full-transaction-waf/

2. The announcement explicitly says custom rules on the response body are not yet available.

> Creating rules on the response body is not yet available.

근거: https://blog.cloudflare.com/full-transaction-waf/

검토 초점: Distinguish managed detections from customer-authored response rules when evaluating coverage. This preserved item had disappeared from the legacy listing after a newer digest replaced the page; renewal still requires explicit review.

### 简体中文 (zh-CN)

Cloudflare WAF 响应规则：操作与响应体限制

1. Cloudflare WAF 允许客户创建最多 3 条自定义响应规则，支持 Log 和 Block 操作。

2. 公告明确指出，针对响应体的自定义规则尚不可用。

검토 초점: 评估覆盖范围时，应区分托管检测与客户编写的响应规则。该保留条目曾因较新的简报替换了原页面而从旧版列表中消失；此次更新仍需明确审阅。

### 日本語 (ja)

Cloudflare WAF のレスポンスルール：アクションと本文の制限

1. Cloudflare WAF では、Log と Block アクションに対応するカスタムレスポンスルールを最大 3 件作成できる。

2. 告知では、レスポンス本文に対するカスタムルールはまだ利用できないと明示している。

검토 초점: カバー範囲を評価する際は、マネージド検出と利用者が作成するレスポンスルールを区別する。この保存項目は、新しいダイジェストがページを置き換えた後、旧一覧から消えていた。今回の再整備にも明示的なレビューが必要である。

### Deutsch (de)

Cloudflare-WAF-Antwortregeln: Aktionen und Grenzen beim Antworttext

1. Cloudflare WAF erlaubt Kunden, bis zu 3 benutzerdefinierte Antwortregeln mit den Aktionen Log und Block zu erstellen.

2. Die Ankündigung erklärt ausdrücklich, dass benutzerdefinierte Regeln für den Antwortkörper noch nicht verfügbar sind.

검토 초점: Bei der Bewertung der Abdeckung zwischen verwalteten Erkennungsmechanismen und kundenseitig erstellten Antwortregeln unterscheiden. Dieser erhaltene Eintrag war aus der alten Liste verschwunden, nachdem ein neuerer Digest die Seite ersetzt hatte; die Überarbeitung benötigt weiterhin eine ausdrückliche Prüfung.

### Français (fr)

Règles de réponse Cloudflare WAF : actions et restrictions concernant le corps de la réponse

1. Cloudflare WAF permet aux clients de créer jusqu’à 3 règles de réponse personnalisées prenant en charge les actions Log et Block.

2. L’annonce précise explicitement que les règles personnalisées portant sur le corps de la réponse ne sont pas encore disponibles.

검토 초점: Pour évaluer la couverture, distinguer les détections gérées des règles de réponse rédigées par le client. Cet élément conservé avait disparu de l’ancienne liste après le remplacement de la page par un récapitulatif plus récent ; sa révision nécessite toujours un examen explicite.

### Русский (ru)

Правила ответов Cloudflare WAF: действия и ограничения тела ответа

1. Cloudflare WAF позволяет клиентам создавать до 3 пользовательских правил для ответов с поддержкой действий Log и Block.

2. Объявление прямо указывает, что пользовательские правила для тела ответа пока недоступны.

검토 초점: При оценке охвата различайте управляемые механизмы обнаружения и правила ответов, написанные клиентом. Этот сохранённый пункт исчез из прежнего списка после замены страницы более новым дайджестом; обновление по-прежнему требует явной проверки.

## GitHub Advanced Security hard budgets can block new coverage

원문: https://github.blog/changelog/2026-05-28-hard-budget-limits-now-available-for-github-advanced-security

검토 기준: 영어 보강본 5fe80662057aa753, 2026-10-25T06:31:18+00:00

### 영어 기준본

1. GitHub announced hard license-budget limits for Advanced Security that enterprise administrators and billing managers can configure. This is a product license control, not a cap on every enterprise expense.

> Enterprise administrators and billing managers

근거: https://github.blog/changelog/2026-05-28-hard-budget-limits-now-available-for-github-advanced-security

2. When the threshold is reached, the notice says additional license usage is blocked and Advanced Security is not enabled on new repositories until capacity is freed or the budget is increased.

> additional license usage is blocked

근거: https://github.blog/changelog/2026-05-28-hard-budget-limits-now-available-for-github-advanced-security

검토 초점: Monitor both remaining license capacity and repositories missing security coverage. Test onboarding and escalation procedures so a budget limit does not silently leave new repositories outside the intended controls.

### 简体中文 (zh-CN)

GitHub Advanced Security 硬性预算可能阻止新增安全覆盖

1. GitHub 宣布为 Advanced Security 提供硬性许可证预算限制，可由企业管理员和计费管理员配置。这是产品许可证控制，并非对企业所有支出的上限。

2. 公告称，达到阈值后会阻止额外的许可证使用，并且不会为新仓库启用 Advanced Security，直到释放容量或提高预算。

검토 초점: 同时监控剩余许可证容量和缺少安全覆盖的仓库。测试新仓库接入及升级处理流程，避免预算限制悄然使新仓库处于预期控制之外。

### 日本語 (ja)

GitHub Advanced Security の厳格な予算上限は新規リポジトリの保護を妨げ得る

1. GitHub は、エンタープライズ管理者と請求マネージャーが設定できる Advanced Security の厳格なライセンス予算上限を発表した。これは製品ライセンスの制御であり、企業のすべての支出に対する上限ではない。

2. 告知によると、しきい値に達すると追加のライセンス利用がブロックされ、容量が空くか予算が増えるまで、新しいリポジトリでは Advanced Security が有効にならない。

검토 초점: ライセンスの残容量と、セキュリティ保護がないリポジトリの両方を監視する。新規リポジトリの受け入れとエスカレーションの手順をテストし、予算制限によって新しいリポジトリが気付かれないまま意図した制御の対象外に残ることを防ぐ。

### Deutsch (de)

Harte Budgets für GitHub Advanced Security können neue Sicherheitsabdeckung blockieren

1. GitHub kündigte harte Lizenzbudgetgrenzen für Advanced Security an, die Unternehmensadministratoren und Abrechnungsmanager konfigurieren können. Dies ist eine Produktlizenzkontrolle und keine Obergrenze für sämtliche Unternehmensausgaben.

2. Laut Mitteilung wird beim Erreichen des Schwellenwerts zusätzliche Lizenznutzung blockiert. Advanced Security wird auf neuen Repositories nicht aktiviert, bis Kapazität frei wird oder das Budget erhöht wird.

검토 초점: Sowohl die verbleibende Lizenzkapazität als auch Repositories ohne Sicherheitsabdeckung überwachen. Aufnahme- und Eskalationsprozesse testen, damit ein Budgetlimit neue Repositories nicht unbemerkt außerhalb der vorgesehenen Kontrollen lässt.

### Français (fr)

Les budgets stricts de GitHub Advanced Security peuvent bloquer une nouvelle couverture

1. GitHub a annoncé des plafonds stricts de budget de licences Advanced Security, configurables par les administrateurs d’entreprise et les responsables de facturation. Il s’agit d’un contrôle des licences du produit, pas d’un plafond pour toutes les dépenses de l’entreprise.

2. Lorsque le seuil est atteint, l’avis indique que l’utilisation de licences supplémentaires est bloquée et qu’Advanced Security n’est pas activé sur de nouveaux dépôts jusqu’à ce que de la capacité soit libérée ou que le budget soit augmenté.

검토 초점: Surveiller à la fois la capacité de licences restante et les dépôts sans couverture de sécurité. Tester les procédures d’intégration et d’escalade pour éviter qu’un plafond budgétaire laisse silencieusement de nouveaux dépôts hors des contrôles prévus.

### Русский (ru)

Жёсткие бюджеты GitHub Advanced Security могут блокировать новую защиту

1. GitHub объявила о жёстких бюджетных ограничениях на лицензии Advanced Security, которые могут настраивать администраторы предприятия и менеджеры по выставлению счетов. Это управление лицензиями продукта, а не предел всех расходов предприятия.

2. В уведомлении сказано, что при достижении порога использование дополнительных лицензий блокируется, а Advanced Security не включается в новых репозиториях, пока не освободится ёмкость или не будет увеличен бюджет.

검토 초점: Контролируйте как оставшуюся ёмкость лицензий, так и репозитории без защиты. Проверяйте процедуры подключения и эскалации, чтобы бюджетное ограничение незаметно не оставило новые репозитории вне предусмотренных мер контроля.

