# 다국어 번역 검토 초안

의미·용어·조건 대조와 대상 언어 교정은 AI로 검토합니다. 수치·제품명 검사는 의미 검토를 대체하지 않습니다. 사이트 게시는 사용자의 명시적 승인 후에 진행합니다.

## Grok Code Fast 1 retirement notice specifies Copilot scope

원문: https://github.blog/changelog/2026-05-08-upcoming-deprecation-of-grok-code-fast-1

검토 기준: 영어 보강본 0915f64eb6629c85, 2026-10-25T06:06:33+00:00

### 영어 기준본

1. GitHub announced the planned retirement of Grok Code Fast 1 from Copilot on 2026-05-15. This records the announced schedule rather than independently verifying the completed shutdown.

> Grok Code Fast 1 2026-05-15

근거: https://github.blog/changelog/2026-05-08-upcoming-deprecation-of-grok-code-fast-1

2. The notice says the date was accelerated because of the model provider deprecation.

> accelerated due to the model provider deprecation

근거: https://github.blog/changelog/2026-05-08-upcoming-deprecation-of-grok-code-fast-1

검토 초점: Inventory product-specific model names and admin policy dependencies before changing workflows. Verify present availability and evaluate an alternative on representative tasks rather than adopting historical suggested models automatically.

### 简体中文 (zh-CN)

Grok Code Fast 1 停用公告明确了 Copilot 范围

1. GitHub 宣布计划于 2026-05-15 从 Copilot 中停用 Grok Code Fast 1。此处记录的是公告中的时间安排，并未独立核实停用是否已经完成。

2. 公告称，由于模型提供商弃用该模型，停用日期被提前。

검토 초점: 调整工作流程前，应清点各产品使用的模型名称及其对管理员策略的依赖。核实当前可用性，并用有代表性的任务评估替代方案，不应直接采用历史公告中建议的模型。

### 日本語 (ja)

Grok Code Fast 1 の提供終了予告：Copilot での対象範囲

1. GitHub は、Copilot での Grok Code Fast 1 の提供を 2026-05-15 に終了する予定を発表した。これは発表された予定の記録であり、実際の提供終了を独立に確認したものではない。

2. 告知によると、モデル提供元による廃止に伴い、終了日が前倒しされた。

검토 초점: ワークフローを変更する前に、製品ごとのモデル名と管理者ポリシーへの依存関係を洗い出す。現在の利用可否を確認し、代表的なタスクで代替モデルを評価する。過去に推奨されたモデルをそのまま採用しない。

### Deutsch (de)

Ankündigung zur Einstellung von Grok Code Fast 1 grenzt den Copilot-Bereich ab

1. GitHub kündigte die geplante Einstellung von Grok Code Fast 1 in Copilot zum 2026-05-15 an. Hier wird der angekündigte Zeitplan festgehalten; die tatsächlich abgeschlossene Abschaltung wurde nicht unabhängig überprüft.

2. Laut Mitteilung wurde der Termin vorgezogen, weil der Modellanbieter das Modell abkündigte.

검토 초점: Vor Änderungen an Arbeitsabläufen sollten produktspezifische Modellnamen und Abhängigkeiten von Administratorrichtlinien erfasst werden. Aktuelle Verfügbarkeit prüfen und Alternativen anhand repräsentativer Aufgaben bewerten, statt historisch empfohlene Modelle ungeprüft zu übernehmen.

### Français (fr)

L’annonce du retrait de Grok Code Fast 1 précise le périmètre de Copilot

1. GitHub a annoncé le retrait prévu de Grok Code Fast 1 de Copilot le 2026-05-15. Il s’agit du calendrier annoncé, sans vérification indépendante de l’arrêt effectif.

2. L’avis indique que la date a été avancée en raison de l’abandon du modèle par son fournisseur.

검토 초점: Avant de modifier les processus de travail, recenser les noms de modèles propres à chaque produit et les dépendances aux règles d’administration. Vérifier la disponibilité actuelle et évaluer une solution de remplacement sur des tâches représentatives, plutôt que d’adopter automatiquement les modèles recommandés à l’époque.

### Русский (ru)

Объявление о прекращении поддержки Grok Code Fast 1 уточняет охват Copilot

1. GitHub объявила о планируемом прекращении использования Grok Code Fast 1 в Copilot с 2026-05-15. Здесь зафиксирован объявленный график, а не независимое подтверждение фактического отключения.

2. В уведомлении говорится, что дату перенесли на более ранний срок из-за отказа поставщика от поддержки модели.

검토 초점: Перед изменением рабочих процессов следует составить перечень названий моделей для каждого продукта и зависимостей от политик администрирования. Проверьте текущую доступность и оцените альтернативу на типичных задачах, а не принимайте автоматически рекомендации моделей из прошлых объявлений.

## CodeQL models-as-data add custom sanitizers and validators

원문: https://www.infoq.com/news/2026/05/github-codeql-security-modeling/

검토 기준: 영어 보강본 097c455a9b953f24, 2026-10-25T06:06:33+00:00

### 영어 기준본

1. GitHub describes declarative sanitizers and validators in CodeQL YAML data extensions, using barrierModel and barrierGuardModel.

> two new extensible predicates: barrierModel

근거: https://github.blog/changelog/2026-04-21-codeql-now-supports-sanitizers-and-validators-in-models-as-data/

2. The announcement lists availability starting with CodeQL 2.25.2. This is the minimum version in that historical announcement, not a current upgrade recommendation.

> available starting with CodeQL 2.25.2

근거: https://github.blog/changelog/2026-04-21-codeql-now-supports-sanitizers-and-validators-in-models-as-data/

검토 초점: Model only the vulnerability kinds and paths the sanitizer actually protects. Test positive and negative examples so an overly broad barrier does not hide real taint flows; this draft does not claim a measured reduction in false positives.

### 简体中文 (zh-CN)

CodeQL 的数据式建模新增自定义净化器与验证器

1. GitHub 介绍了 CodeQL YAML 数据扩展中的声明式净化器与验证器，使用 barrierModel 和 barrierGuardModel。

2. 公告列出的起始可用版本为 CodeQL 2.25.2。这是该历史公告中的最低版本，并非当前的升级建议。

검토 초점: 只应为净化器实际保护的漏洞类型和路径建模。使用正例和反例测试，避免过宽的屏障隐藏真实的污点传播路径；本草稿并不声称已测得误报减少。

### 日本語 (ja)

CodeQL のデータによるモデル定義にカスタムサニタイザーとバリデーターを追加

1. GitHub は、barrierModel と barrierGuardModel を使い、CodeQL の YAML データ拡張でサニタイザーとバリデーターを宣言的に定義する仕組みを紹介している。

2. 告知では CodeQL 2.25.2 以降で利用可能としている。これは当時の告知に記載された最低バージョンであり、現在のアップグレード推奨ではない。

검토 초점: サニタイザーが実際に保護する脆弱性の種類と経路だけをモデル化する。正例と負例をテストし、広すぎるバリアが実際の汚染データの流れを隠さないようにする。この草稿は、誤検知の減少を実測したと主張するものではない。

### Deutsch (de)

CodeQL: Datenbasierte Modelle erhalten eigene Sanitizer und Validatoren

1. GitHub beschreibt deklarative Sanitizer und Validatoren in CodeQL-YAML-Datenerweiterungen mithilfe von barrierModel und barrierGuardModel.

2. Die Ankündigung nennt CodeQL 2.25.2 als erste unterstützte Version. Dies ist die Mindestversion der damaligen Ankündigung und keine aktuelle Upgrade-Empfehlung.

검토 초점: Nur die Schwachstellenarten und Pfade modellieren, die der Sanitizer tatsächlich absichert. Positive und negative Beispiele testen, damit eine zu weit gefasste Barriere keine echten Taint-Flüsse verbirgt. Dieser Entwurf behauptet keine gemessene Verringerung von Fehlalarmen.

### Français (fr)

CodeQL : les modèles déclarés comme données ajoutent des nettoyeurs et validateurs personnalisés

1. GitHub décrit des nettoyeurs et validateurs déclaratifs dans les extensions de données YAML de CodeQL, à l’aide de barrierModel et barrierGuardModel.

2. L’annonce indique une disponibilité à partir de CodeQL 2.25.2. Il s’agit de la version minimale mentionnée dans cette annonce historique, et non d’une recommandation actuelle de mise à niveau.

검토 초점: Modéliser uniquement les types de vulnérabilités et les chemins réellement protégés par le nettoyeur. Tester des exemples positifs et négatifs pour éviter qu’une barrière trop large masque de véritables flux de données contaminées ; ce brouillon ne prétend pas démontrer une baisse mesurée des faux positifs.

### Русский (ru)

CodeQL: модели в виде данных получают пользовательские санитайзеры и валидаторы

1. GitHub описывает декларативные санитайзеры и валидаторы в расширениях данных CodeQL в формате YAML с использованием barrierModel и barrierGuardModel.

2. В объявлении указана доступность начиная с CodeQL 2.25.2. Это минимальная версия из исторического объявления, а не актуальная рекомендация по обновлению.

검토 초점: Моделируйте только те типы уязвимостей и пути, от которых санитайзер действительно защищает. Проверяйте положительные и отрицательные примеры, чтобы чрезмерно широкий барьер не скрывал реальные потоки загрязнённых данных; этот черновик не заявляет об измеренном сокращении ложных срабатываний.

## GitHub reports Grok Code Fast 1 retirement in Copilot

원문: https://github.blog/changelog/2026-05-15-grok-code-fast-1-deprecated

검토 기준: 영어 보강본 09e0d0ec5ed64f8a, 2026-10-25T06:31:18+00:00

### 영어 기준본

1. GitHub reported that Grok Code Fast 1 was deprecated across its Copilot experiences on 2026-05-15. This is the product vendor’s completion notice, distinct from the earlier planned date.

> Grok Code Fast 1 2026-05-15

근거: https://github.blog/changelog/2026-05-15-grok-code-fast-1-deprecated

2. The notice says Copilot Enterprise administrators may need to enable alternative models through their model policies.

> enable access to alternative models through their model policies

근거: https://github.blog/changelog/2026-05-15-grok-code-fast-1-deprecated

검토 초점: Link this completion notice to the earlier scheduled-retirement item when reviewing the archive. Confirm actual product availability and administrative policies before changing a workflow; the announcement does not describe every provider API.

### 简体中文 (zh-CN)

GitHub 通报 Grok Code Fast 1 在 Copilot 中的停用

1. GitHub 通报，Grok Code Fast 1 已于 2026-05-15 在其各项 Copilot 体验中弃用。这是产品厂商确认完成停用的公告，有别于此前仅公布停用计划日期的公告。

2. 公告称，Copilot Enterprise 管理员可能需要通过模型策略启用替代模型。

검토 초점: 审阅归档时，应将这份完成公告与此前的计划停用条目关联。调整工作流程前，确认产品的实际可用性和管理策略；该公告并未涵盖所有提供商的 API。

### 日本語 (ja)

GitHub が Copilot での Grok Code Fast 1 の提供終了を報告

1. GitHub は、2026-05-15 に各種 Copilot 利用環境で Grok Code Fast 1 を廃止したと報告した。これは製品提供元による完了の告知であり、以前の予定日の告知とは異なる。

2. 告知によると、Copilot Enterprise の管理者は、モデルポリシーで代替モデルを有効にする必要がある場合がある。

검토 초점: アーカイブを検討する際は、この完了の告知を以前の終了予定の記事と関連付ける。ワークフローを変更する前に、製品の実際の利用可否と管理ポリシーを確認する。この告知は、すべての提供元の API を説明するものではない。

### Deutsch (de)

GitHub meldet die Einstellung von Grok Code Fast 1 in Copilot

1. GitHub meldete, dass Grok Code Fast 1 am 2026-05-15 in sämtlichen Copilot-Nutzungsumgebungen eingestellt wurde. Dies ist die Abschlussmeldung des Produktanbieters und von der früheren Terminankündigung zu unterscheiden.

2. Laut Mitteilung müssen Administratoren von Copilot Enterprise gegebenenfalls alternative Modelle über ihre Modellrichtlinien aktivieren.

검토 초점: Bei der Archivprüfung diese Abschlussmeldung mit dem früheren Eintrag zur geplanten Einstellung verknüpfen. Vor Änderungen an Arbeitsabläufen die tatsächliche Produktverfügbarkeit und Verwaltungsrichtlinien prüfen; die Ankündigung beschreibt nicht sämtliche Anbieter-APIs.

### Français (fr)

GitHub annonce le retrait effectif de Grok Code Fast 1 dans Copilot

1. GitHub a indiqué que Grok Code Fast 1 avait été abandonné dans tous ses environnements Copilot le 2026-05-15. Il s’agit de l’avis d’achèvement publié par l’éditeur du produit, distinct de l’annonce antérieure d’une date prévue.

2. L’avis précise que les administrateurs de Copilot Enterprise peuvent devoir activer des modèles de remplacement au moyen de leurs règles de gestion des modèles.

검토 초점: Lors de la revue des archives, relier cet avis d’achèvement à l’article antérieur annonçant le retrait programmé. Avant de modifier un processus de travail, vérifier la disponibilité effective du produit et les règles d’administration ; l’annonce ne décrit pas toutes les API des fournisseurs.

### Русский (ru)

GitHub сообщает о прекращении использования Grok Code Fast 1 в Copilot

1. GitHub сообщила, что 2026-05-15 модель Grok Code Fast 1 была выведена из использования во всех вариантах работы с Copilot. Это уведомление поставщика продукта о завершении вывода модели из использования, в отличие от прежнего объявления плановой даты.

2. В уведомлении указано, что администраторам Copilot Enterprise может потребоваться включить альтернативные модели через политики моделей.

검토 초점: При проверке архива свяжите это уведомление о завершении с прежней записью о запланированном прекращении поддержки. Перед изменением рабочего процесса проверьте фактическую доступность продукта и административные политики; объявление не описывает API всех поставщиков.

## Copilot credit pools: included usage and additional spending

원문: https://github.blog/changelog/2026-07-02-cost-centers-now-support-included-usage-caps

검토 기준: 영어 보강본 0a337adda878feca, 2026-10-25T17:03:04+00:00

### 영어 기준본

1. GitHub announced cost-center AI credit pools for Copilot Business and Enterprise on Enterprise Cloud. At announcement time, configuration was available through the REST API, while settings-UI management was still planned.

> This is available through the REST API today. Management in the cost center settings UI is coming soon.

근거: https://github.blog/changelog/2026-07-02-cost-centers-now-support-included-usage-caps

> This is available for Copilot Business and Copilot Enterprise on GitHub Enterprise Cloud

근거: https://github.blog/changelog/2026-07-02-cost-centers-now-support-included-usage-caps

2. The pool cap limits a cost center’s draw from enterprise-wide included credits; a cost-center budget governs metered charges after the included pool is exhausted. These controls cover different spending phases and can be combined.

> An AI credit pool is separate from a cost center budget.

근거: https://github.blog/changelog/2026-07-02-cost-centers-now-support-included-usage-caps

> A cost center budget governs the metered phase, capping charges after the pool is exhausted.

근거: https://github.blog/changelog/2026-07-02-cost-centers-now-support-included-usage-caps

3. GitHub calculates the pool limit from assigned licenses. At the cap, enterprises can block further included usage or allow additional spend when overages are permitted, so the pool is not automatically a hard cap on all charges.

> GitHub calculates the pool limit automatically from the licenses assigned to that cost center

근거: https://github.blog/changelog/2026-07-02-cost-centers-now-support-included-usage-caps

> block further included usage or let it continue as additional spend if your enterprise allows overages.

근거: https://github.blog/changelog/2026-07-02-cost-centers-now-support-included-usage-caps

검토 초점: Review included-credit allocation, overage policy and metered budgets together. Confirm current API and UI availability before changing controls; this source review does not measure actual savings.

### 简体中文 (zh-CN)

Copilot 额度池：内含用量与额外支出

1. GitHub 宣布在 Enterprise Cloud 上为 Copilot Business 和 Enterprise 提供成本中心 AI 额度池。公告发布时可通过 REST API 配置，而设置界面中的管理功能仍在规划中。

2. 额度池上限限制成本中心可从企业共享的内含额度中使用多少；成本中心预算则管理内含额度池耗尽后的按量计费费用。这些控制措施针对不同的支出阶段，可结合使用。

3. GitHub 根据已分配的许可证计算额度池上限。达到上限时，企业可以阻止继续使用内含额度，也可以在允许超额使用的情况下放行额外支出，因此额度池并不自动构成所有费用的硬性上限。

검토 초점: 应一并审查内含额度分配、超额使用策略和按量计费预算。调整控制措施前，确认当前 API 与界面功能的可用性；本次来源审阅未测量实际节省金额。

### 日本語 (ja)

Copilot のクレジットプール：含まれる利用枠と追加支出

1. GitHub は、Enterprise Cloud 上の Copilot Business と Enterprise 向けに、コストセンター単位の AI クレジットプールを発表した。発表時点では REST API で設定でき、設定画面での管理は計画段階だった。

2. プールの上限は、企業全体で共有する契約に含まれるクレジットから、コストセンターが使える量を制限する。コストセンターの予算は、そのプールを使い切った後の従量課金を管理する。対象となる支出段階が異なるため、両者を組み合わせられる。

3. GitHub は割り当て済みライセンスからプール上限を算出する。上限に達すると、企業は契約に含まれるクレジットの追加利用を停止するか、超過利用を許可している場合は追加支出を認められる。そのため、プールが自動的に全料金の厳格な上限になるわけではない。

검토 초점: 契約に含まれるクレジットの配分、超過利用ポリシー、従量課金予算をまとめて確認する。設定を変更する前に、現在の API と管理画面の利用可否を確認する。この出典レビューでは実際の削減額を測定していない。

### Deutsch (de)

Copilot-Creditpools: enthaltene Nutzung und zusätzliche Ausgaben

1. GitHub kündigte AI-Creditpools je Kostenstelle für Copilot Business und Enterprise auf Enterprise Cloud an. Zum Zeitpunkt der Ankündigung war die Konfiguration über die REST API möglich; die Verwaltung über die Einstellungsoberfläche war noch geplant.

2. Das Poollimit begrenzt, wie viel eine Kostenstelle aus den unternehmensweit enthaltenen Credits beziehen kann. Ein Kostenstellenbudget steuert die nutzungsabhängigen Gebühren nach Ausschöpfung des enthaltenen Pools. Die Regeln betreffen unterschiedliche Ausgabenphasen und lassen sich kombinieren.

3. GitHub berechnet das Poollimit anhand der zugewiesenen Lizenzen. Am Limit können Unternehmen weitere Nutzung der enthaltenen Credits sperren oder bei erlaubter Überschreitung zusätzliche Ausgaben zulassen. Der Pool begrenzt daher nicht automatisch sämtliche Gebühren verbindlich.

검토 초점: Die Zuteilung enthaltener Credits, Überschreitungsrichtlinien und nutzungsabhängige Budgets gemeinsam prüfen. Vor Änderungen die aktuelle Verfügbarkeit von API und Oberfläche bestätigen; diese Quellenprüfung misst keine tatsächlichen Einsparungen.

### Français (fr)

Pools de crédits Copilot : usage inclus et dépenses supplémentaires

1. GitHub a annoncé des pools de crédits d’IA par centre de coûts pour Copilot Business et Enterprise sur Enterprise Cloud. Lors de l’annonce, la configuration était disponible via la REST API, tandis que la gestion dans l’interface des paramètres restait prévue.

2. Le plafond du pool limite ce qu’un centre de coûts peut prélever sur les crédits inclus partagés à l’échelle de l’entreprise ; son budget régit les frais à l’usage après épuisement du pool inclus. Ces contrôles concernent des phases de dépenses différentes et peuvent être combinés.

3. GitHub calcule la limite du pool à partir des licences attribuées. Une fois le plafond atteint, les entreprises peuvent bloquer tout usage inclus supplémentaire ou autoriser des dépenses additionnelles si les dépassements sont permis. Le pool n’impose donc pas automatiquement un plafond strict à l’ensemble des frais.

검토 초점: Examiner ensemble la répartition des crédits inclus, les règles de dépassement et les budgets de facturation à l’usage. Confirmer la disponibilité actuelle de l’API et de l’interface avant toute modification ; cette revue des sources ne mesure pas les économies réellement réalisées.

### Русский (ru)

Пулы кредитов Copilot: включённое использование и дополнительные расходы

1. GitHub объявила о пулах AI-кредитов по центрам затрат для Copilot Business и Enterprise в Enterprise Cloud. На момент объявления настройка была доступна через REST API, а управление через интерфейс настроек ещё планировалось.

2. Лимит пула ограничивает долю общих включённых кредитов предприятия, которую может использовать центр затрат; бюджет центра затрат регулирует плату по фактическому использованию после исчерпания включённого пула. Эти меры относятся к разным этапам расходов и могут применяться вместе.

3. GitHub рассчитывает лимит пула на основе назначенных лицензий. При достижении лимита предприятие может заблокировать дальнейшее использование включённых кредитов или разрешить дополнительные расходы, если допускается превышение. Поэтому пул не становится автоматически жёстким пределом всех начислений.

검토 초점: Проверяйте распределение включённых кредитов, политику превышения и бюджеты оплаты по факту использования совместно. Перед изменением правил подтвердите текущую доступность API и интерфейса; этот разбор источника не измеряет фактическую экономию.

## GitHub repository advisories gain search and filters

원문: https://github.blog/changelog/2026-05-06-search-and-filter-bar-for-repository-security-advisories

검토 기준: 영어 보강본 1c1c9e6c82aad3a4, 2026-10-25T06:06:33+00:00

### 영어 기준본

1. GitHub added search and filtering for security advisories directly in a repository Security tab.

> search and filter security advisories directly

근거: https://github.blog/changelog/2026-05-06-search-and-filter-bar-for-repository-security-advisories

2. The notice lists sort, package, ecosystems and severity among the supported search or filtering keywords.

> sort , package , ecosystems , severity

근거: https://github.blog/changelog/2026-05-06-search-and-filter-bar-for-repository-security-advisories

검토 초점: Check whether the view contains draft, incoming and published advisories needed for the review. A smaller filtered result set should not be interpreted as fewer underlying vulnerabilities.

### 简体中文 (zh-CN)

GitHub 仓库安全公告新增搜索与筛选

1. GitHub 在仓库的 Security 标签页中直接加入了安全公告搜索和筛选功能。

2. 公告列出的受支持搜索或筛选关键字包括 sort（排序）、package（软件包）、ecosystems（生态系统）和 severity（严重程度）。

검토 초점: 检查该视图是否包含审阅所需的草稿、收到的公告及已发布公告。筛选后结果较少，不应被解读为实际存在的漏洞更少。

### 日本語 (ja)

GitHub のリポジトリアドバイザリに検索・絞り込み機能

1. GitHub は、リポジトリの Security タブ内でセキュリティアドバイザリを直接検索・絞り込みできる機能を追加した。

2. 告知では、対応する検索・絞り込みキーワードとして sort（並べ替え）、package（パッケージ）、ecosystems（エコシステム）、severity（深刻度）などを挙げている。

검토 초점: レビューに必要な下書き、受信したアドバイザリ、公開済みアドバイザリが表示対象に含まれるか確認する。絞り込み後の件数が少ないことを、実際の脆弱性が少ないという意味で捉えない。

### Deutsch (de)

GitHub-Sicherheitshinweise in Repositories erhalten Suche und Filter

1. GitHub ergänzte die Suche und Filterung von Sicherheitshinweisen direkt im Security-Tab eines Repositories.

2. Die Mitteilung nennt unter anderem sort, package, ecosystems und severity als unterstützte Such- oder Filterbegriffe.

검토 초점: Prüfen, ob die Ansicht die für die Prüfung benötigten Entwürfe sowie eingegangene und veröffentlichte Sicherheitshinweise enthält. Eine kleinere gefilterte Ergebnismenge bedeutet nicht, dass tatsächlich weniger Schwachstellen bestehen.

### Français (fr)

GitHub ajoute la recherche et les filtres aux avis de sécurité des dépôts

1. GitHub a ajouté la recherche et le filtrage des avis de sécurité directement dans l’onglet Security d’un dépôt.

2. L’avis mentionne notamment sort, package, ecosystems et severity parmi les mots-clés de recherche ou de filtrage pris en charge.

검토 초점: Vérifier que la vue contient les brouillons, les avis reçus et les avis publiés nécessaires à l’examen. Un résultat filtré plus restreint ne signifie pas qu’il existe moins de vulnérabilités sous-jacentes.

### Русский (ru)

В уведомлениях безопасности репозиториев GitHub появились поиск и фильтры

1. GitHub добавила поиск и фильтрацию уведомлений безопасности непосредственно на вкладке Security репозитория.

2. В объявлении среди поддерживаемых ключевых слов поиска и фильтрации перечислены sort, package, ecosystems и severity.

검토 초점: Проверьте, содержит ли представление нужные для проверки черновики, входящие и опубликованные уведомления безопасности. Меньшее число результатов после фильтрации не следует считать признаком меньшего количества самих уязвимостей.

