# 다국어 번역 검토 초안

의미·용어·조건 대조와 대상 언어 교정은 AI로 검토합니다. 수치·제품명 검사는 의미 검토를 대체하지 않습니다. 사이트 게시는 사용자의 명시적 승인 후에 진행합니다.

## Cloud-security podcast: attributed isolation and learning advice

원문: https://www.infoq.com/podcasts/new-blueprint-cloud-security/

검토 기준: 영어 보강본 d17b2ae1f047cf94, 2026-10-26T01:34:51+00:00

### 영어 기준본

1. In the transcript, Edera co-founder Alex Zenla describes a zone abstraction for isolating workloads inside virtual machines. This is the vendor speaker’s account of the design, not an independently tested security boundary.

> we have this concept called a zone that allows you to run isolated workloads inside of a safe virtual machine.

근거: https://www.infoq.com/podcasts/new-blueprint-cloud-security/

2. Zenla describes using language models to explain specifications and emphasizes understanding the resulting implementation. The interview’s criticism of existing infrastructure is an attributed engineering viewpoint, not proof that every container or GPU deployment is insecure.

> have Claude explain to me all the information that I need to know

근거: https://www.infoq.com/podcasts/new-blueprint-cloud-security/

> at the end of it, you have to understand what you did.

근거: https://www.infoq.com/podcasts/new-blueprint-cloud-security/

검토 초점: Use the transcript to assess the speaker’s argument, then validate isolation requirements and failure modes against your own threat model. No sandbox-escape, performance or AI-hardware experiment was performed for this summary.

### 简体中文 (zh-CN)

云安全播客：受访者的隔离设计与学习建议

1. 在文字稿中，Edera 联合创始人 Alex Zenla 描述了一种 zone 抽象，用于在虚拟机内隔离工作负载。这是供应商受访者对设计的叙述，并非经过独立测试的安全边界。

2. Zenla 描述了使用语言模型解释规范的做法，并强调必须理解最终得到的实现。访谈对现有基础设施的批评是受访者的工程观点，不能证明所有容器或 GPU 部署都不安全。

검토 초점: 通过文字稿评估受访者的论点，再根据自己的威胁模型验证隔离要求和失效模式。本摘要未进行沙箱逃逸、性能或 AI 硬件实验。

### 日本語 (ja)

クラウドセキュリティのポッドキャスト：話者による隔離設計と学習の助言

1. 書き起こしの中で、Edera の共同創業者 Alex Zenla は、仮想マシン内でワークロードを隔離する zone という抽象化を説明している。これはベンダー側の話者による設計の説明であり、独立したテストで確認されたセキュリティ境界ではない。

2. Zenla は、言語モデルに仕様を説明させる使い方を紹介し、得られた実装を理解することを重視している。インタビューでの既存インフラへの批判は話者のエンジニアリング上の見解であり、すべてのコンテナや GPU のデプロイが安全でないという証拠ではない。

검토 초점: 書き起こしを使って話者の主張を評価し、その上で自分の脅威モデルに照らして隔離要件と障害モードを検証する。この要約では、サンドボックス脱出、性能、AI ハードウェアの実験は行っていない。

### Deutsch (de)

Cloud-Security-Podcast: Aussagen des Sprechers zu Isolation und Lernen

1. Im Transkript beschreibt Edera-Mitgründer Alex Zenla eine Zone-Abstraktion zur Isolation von Workloads innerhalb virtueller Maschinen. Dies ist die Designbeschreibung eines Sprechers des Anbieters, keine unabhängig getestete Sicherheitsgrenze.

2. Zenla beschreibt den Einsatz von Sprachmodellen zur Erklärung von Spezifikationen und betont, dass man die daraus entstandene Implementierung verstehen muss. Die Kritik an bestehender Infrastruktur im Interview ist eine dem Sprecher zuzuordnende technische Sichtweise, kein Beweis dafür, dass jede Container- oder GPU-Bereitstellung unsicher ist.

검토 초점: Anhand des Transkripts die Argumentation des Sprechers bewerten und anschließend Isolationsanforderungen und Fehlermodi am eigenen Bedrohungsmodell prüfen. Für diese Zusammenfassung wurden keine Experimente zu Sandbox-Ausbrüchen, Leistung oder KI-Hardware durchgeführt.

### Français (fr)

Podcast sur la sécurité cloud : propos de l’intervenant sur l’isolation et l’apprentissage

1. Dans la transcription, Alex Zenla, cofondateur d’Edera, décrit une abstraction appelée zone pour isoler les charges de travail à l’intérieur de machines virtuelles. Il s’agit du récit de la conception par un intervenant du fournisseur, et non d’une frontière de sécurité testée indépendamment.

2. Zenla décrit l’utilisation de modèles de langage pour expliquer des spécifications et souligne la nécessité de comprendre l’implémentation obtenue. Les critiques de l’infrastructure existante formulées dans l’entretien constituent un point de vue d’ingénierie attribué à l’intervenant, sans prouver que tout déploiement de conteneurs ou de GPU est peu sûr.

검토 초점: Utiliser la transcription pour évaluer l’argumentation de l’intervenant, puis valider les exigences d’isolation et les modes de défaillance au regard de son propre modèle de menace. Aucune expérience d’évasion de sandbox, de performance ou de matériel d’IA n’a été réalisée pour ce résumé.

### Русский (ru)

Подкаст об облачной безопасности: взгляды собеседника на изоляцию и обучение

1. В расшифровке сооснователь Edera Alex Zenla описывает абстракцию zone для изоляции нагрузок внутри виртуальных машин. Это рассказ представителя поставщика об устройстве системы, а не независимо проверенная граница безопасности.

2. Zenla рассказывает об использовании языковых моделей для объяснения спецификаций и подчёркивает необходимость понимать полученную реализацию. Критика существующей инфраструктуры в интервью — инженерная точка зрения собеседника, а не доказательство небезопасности любого развёртывания контейнеров или GPU.

검토 초점: Используйте расшифровку для оценки аргументов собеседника, затем проверьте требования к изоляции и режимы отказа с учётом собственной модели угроз. Для этого обзора не проводились эксперименты по выходу из песочницы, производительности или оборудованию для ИИ.

## Copilot Gemini retirement: planned and completed notices

원문: https://github.blog/changelog/2026-07-02-upcoming-deprecation-of-gemini-2-5-pro-and-gemini-3-flash

검토 기준: 영어 보강본 d92a8a6927fa76ff, 2026-10-25T17:03:04+00:00

### 영어 기준본

1. The original GitHub notice scheduled Gemini 2.5 Pro and Gemini 3 Flash retirement across Copilot experiences for 2026-07-31. This is a Copilot-product notice and does not establish retirement of the same models from other providers or APIs.

> We will deprecate Gemini 2.5 Pro and Gemini 3 Flash across all GitHub Copilot experiences

근거: https://github.blog/changelog/2026-07-02-upcoming-deprecation-of-gemini-2-5-pro-and-gemini-3-flash

> code completions) on July 31st, 2026:

근거: https://github.blog/changelog/2026-07-02-upcoming-deprecation-of-gemini-2-5-pro-and-gemini-3-flash

2. The planned alternatives were Gemini 3.1 Pro and Gemini 3.5 Flash. The notice also warned that enterprise model policies might need to permit the alternatives before users could select them.

> Gemini 2.5 Pro 7-31-2026 Gemini 3.1 Pro Gemini 3 Flash 7-31-2026 Gemini 3.5 Flash

근거: https://github.blog/changelog/2026-07-02-upcoming-deprecation-of-gemini-2-5-pro-and-gemini-3-flash

> Copilot Enterprise administrators may need to enable access to the alternative models through their model policies

근거: https://github.blog/changelog/2026-07-02-upcoming-deprecation-of-gemini-2-5-pro-and-gemini-3-flash

후속 확인:

- GitHub’s 2026-07-31 follow-up reports the Copilot deprecation as completed. Its alternative table lists Gemini 3.1 Pro (Preview) and Gemini 3.6 Flash, replacing the earlier Gemini 3.5 Flash suggestion. These are that notice’s alternatives, not a claim of unchanged availability today.

검토 초점: Confirm the specific Copilot experience, organization policy and currently supported models. The later completion notice changes a suggested alternative; do not keep presenting the initial suggestion as the final migration guidance.

### 简体中文 (zh-CN)

Copilot 中 Gemini 的停用：计划公告与完成公告

1. GitHub 的最初公告计划于 2026-07-31 在各项 Copilot 使用环境中停用 Gemini 2.5 Pro 和 Gemini 3 Flash。这是针对 Copilot 产品的公告，不能据此认定其他提供商或 API 也停用了相同模型。

2. 最初计划的替代模型是 Gemini 3.1 Pro 和 Gemini 3.5 Flash。公告还提醒，在用户可以选择替代模型之前，企业模型政策可能需要允许使用它们。

후속 확인:

- GitHub 于 2026-07-31 发布的后续公告称，Copilot 中的停用已完成。其替代模型表列出 Gemini 3.1 Pro (Preview) 和 Gemini 3.6 Flash，取代了先前对 Gemini 3.5 Flash 的建议。这些是该公告列出的替代选项，并非声称它们如今仍以相同状态提供。

검토 초점: 确认具体的 Copilot 使用环境、组织政策和当前受支持的模型。较晚的完成公告变更了建议的替代模型，不应继续将最初建议作为最终迁移指引。

### 日本語 (ja)

Copilot の Gemini 提供終了：予定の告知と完了の告知

1. GitHub の最初の告知では、Copilot の各利用環境で Gemini 2.5 Pro と Gemini 3 Flash の提供を 2026-07-31 に終了する予定だとされていた。これは Copilot 製品に関する告知であり、他のプロバイダーや API からも同じモデルが廃止されたと確認するものではない。

2. 当初予定された代替モデルは Gemini 3.1 Pro と Gemini 3.5 Flash だった。告知では、ユーザーが選択できるようにする前に、企業のモデルポリシーで代替モデルを許可する必要がある場合もあると注意していた。

후속 확인:

- GitHub の 2026-07-31 の続報は、Copilot での廃止が完了したと報告している。代替モデルの表には Gemini 3.1 Pro (Preview) と Gemini 3.6 Flash が載り、以前推奨された Gemini 3.5 Flash に代わっている。これらは当該告知の代替案であり、現在も利用状況が変わっていないという主張ではない。

검토 초점: 具体的な Copilot の利用環境、組織のポリシー、現在サポートされるモデルを確認する。後の完了告知では代替モデルの推奨が変わっているため、最初の推奨を最終的な移行指針として示し続けない。

### Deutsch (de)

Gemini-Einstellung in Copilot: Planung und Vollzugsmeldung

1. Die ursprüngliche GitHub-Mitteilung sah die Einstellung von Gemini 2.5 Pro und Gemini 3 Flash in allen Copilot-Nutzungsumgebungen für den 2026-07-31 vor. Dies ist eine Mitteilung zum Produkt Copilot und belegt nicht die Einstellung derselben Modelle bei anderen Anbietern oder APIs.

2. Als Alternativen waren Gemini 3.1 Pro und Gemini 3.5 Flash vorgesehen. Die Mitteilung warnte zudem, dass Unternehmensrichtlinien für Modelle die Alternativen möglicherweise erst erlauben müssen, bevor Nutzer sie auswählen können.

후속 확인:

- GitHubs Folgemitteilung vom 2026-07-31 meldet die Abkündigung in Copilot als abgeschlossen. Die Tabelle der Alternativen nennt Gemini 3.1 Pro (Preview) und Gemini 3.6 Flash und ersetzt damit die frühere Empfehlung für Gemini 3.5 Flash. Dies sind die Alternativen aus dieser Mitteilung, keine Aussage über eine heute unveränderte Verfügbarkeit.

검토 초점: Die konkrete Copilot-Umgebung, Organisationsrichtlinien und aktuell unterstützte Modelle prüfen. Die spätere Vollzugsmeldung ändert eine empfohlene Alternative; die ursprüngliche Empfehlung daher nicht weiter als endgültige Migrationsanleitung darstellen.

### Français (fr)

Retrait de Gemini dans Copilot : annonce initiale et confirmation de l’achèvement

1. L’annonce initiale de GitHub prévoyait le retrait de Gemini 2.5 Pro et Gemini 3 Flash dans tous les environnements Copilot pour le 2026-07-31. Elle concerne le produit Copilot et n’établit pas le retrait de ces mêmes modèles chez d’autres fournisseurs ou dans d’autres API.

2. Les alternatives prévues étaient Gemini 3.1 Pro et Gemini 3.5 Flash. L’annonce avertissait aussi que les politiques de modèles d’entreprise pourraient devoir autoriser les alternatives avant que les utilisateurs puissent les sélectionner.

후속 확인:

- Le suivi de GitHub du 2026-07-31 rapporte que la dépréciation dans Copilot est achevée. Son tableau d’alternatives indique Gemini 3.1 Pro (Preview) et Gemini 3.6 Flash, remplaçant la suggestion antérieure de Gemini 3.5 Flash. Ce sont les alternatives de cette annonce, sans affirmer que leur disponibilité reste identique aujourd’hui.

검토 초점: Confirmer l’environnement Copilot concerné, la politique de l’organisation et les modèles actuellement pris en charge. L’annonce ultérieure d’achèvement change une alternative suggérée ; ne pas continuer à présenter la suggestion initiale comme la recommandation finale de migration.

### Русский (ru)

Вывод Gemini из Copilot: план и сообщение о завершении

1. Первоначальное уведомление GitHub планировало вывод Gemini 2.5 Pro и Gemini 3 Flash из всех вариантов использования Copilot на 2026-07-31. Это уведомление о продукте Copilot; оно не подтверждает вывод тех же моделей у других поставщиков или из других API.

2. Запланированными альтернативами были Gemini 3.1 Pro и Gemini 3.5 Flash. Уведомление также предупреждало, что корпоративные политики моделей могут требовать разрешить альтернативы, прежде чем пользователи смогут их выбрать.

후속 확인:

- В дополнении GitHub от 2026-07-31 сообщается о завершении вывода моделей из Copilot. В таблице альтернатив указаны Gemini 3.1 Pro (Preview) и Gemini 3.6 Flash вместо прежней рекомендации Gemini 3.5 Flash. Это альтернативы из данного уведомления, а не утверждение о неизменности их доступности сегодня.

검토 초점: Уточните конкретный вариант использования Copilot, политику организации и модели, поддерживаемые сейчас. Более позднее сообщение о завершении меняет предложенную альтернативу; не продолжайте представлять первоначальную рекомендацию как окончательное руководство по миграции.

## A coding-language benchmark measures a simplified Git task

원문: https://www.infoq.com/news/2026/04/ai-coding-language-benchmark/

검토 기준: 영어 보강본 d9492522fb4514ef, 2026-10-25T05:38:18+00:00

### 영어 기준본

1. The benchmark author asked Claude Code to implement a simplified Git in 13 languages. The experiment measures this task rather than general language suitability.

> simplified version of Git in 13 languages.

근거: https://dev.to/mame/which-programming-language-is-best-for-claude-code-508a

2. The author reports 20 runs per language using Claude Opus 4.6 with high effort. Reported cost and speed depend on this model and task setup.

> Each language was run 20 times. The model was Claude Opus 4.6 (high effort).

근거: https://dev.to/mame/which-programming-language-is-best-for-claude-code-508a

검토 초점: Compare prompts, test coverage, tool permissions, repetitions and model configuration before using the result to choose a production language. The reported rankings were not independently reproduced here.

### 简体中文 (zh-CN)

编程语言基准测试衡量的是一个简化版 Git 实现任务

1. 基准测试作者要求 Claude Code 用 13 种语言实现简化版 Git。该实验衡量的是这一任务，而非语言的一般适用性。

2. 作者报告，使用 Claude Opus 4.6 并将 effort 设为 high，每种语言运行了 20 次。所报告的成本和速度取决于这一模型与任务设置。

검토 초점: 在根据结果选择生产环境使用的语言之前，应比较提示词、测试覆盖、工具权限、重复次数和模型配置。此处未独立复现所报告的排名。

### 日本語 (ja)

コーディング言語のベンチマークが測るのは簡略版 Git の実装タスク

1. ベンチマークの著者は、Claude Code に 13 言語で簡略版 Git を実装させた。この実験が測定するのはそのタスクであり、言語の一般的な適性ではない。

2. 著者の報告によると、Claude Opus 4.6 を high effort で使い、各言語で 20 回実行したという。報告されたコストと速度は、このモデルとタスクの設定に依存する。

검토 초점: 結果を本番用の言語選択に使う前に、プロンプト、テストカバレッジ、ツールの権限、反復回数、モデル設定を比較する。報告された順位は、ここでは独立して再現していない。

### Deutsch (de)

Programmiersprachen-Benchmark misst eine vereinfachte Git-Aufgabe

1. Der Benchmark-Autor ließ Claude Code ein vereinfachtes Git in 13 Sprachen implementieren. Das Experiment misst diese Aufgabe und nicht die allgemeine Eignung einer Sprache.

2. Der Autor berichtet von 20 Durchläufen pro Sprache mit Claude Opus 4.6 und der Einstellung high effort. Die berichteten Kosten und Geschwindigkeiten hängen von diesem Modell und diesem Aufgabenaufbau ab.

검토 초점: Prompts, Testabdeckung, Werkzeugberechtigungen, Wiederholungen und Modellkonfiguration vergleichen, bevor das Ergebnis zur Wahl einer Sprache für den Produktivbetrieb genutzt wird. Die berichteten Rangfolgen wurden hier nicht unabhängig reproduziert.

### Français (fr)

Un benchmark de langages mesure une tâche d’implémentation simplifiée de Git

1. L’auteur du benchmark a demandé à Claude Code d’implémenter une version simplifiée de Git dans 13 langages. L’expérience mesure cette tâche, et non l’adéquation générale des langages.

2. L’auteur rapporte 20 exécutions par langage avec Claude Opus 4.6 et le réglage high effort. Les coûts et vitesses rapportés dépendent de ce modèle et de cette configuration de tâche.

검토 초점: Comparer les prompts, la couverture des tests, les autorisations des outils, les répétitions et la configuration du modèle avant d’utiliser le résultat pour choisir un langage en production. Les classements rapportés n’ont pas été reproduits indépendamment ici.

### Русский (ru)

Бенчмарк языков программирования измеряет задачу реализации упрощённого Git

1. Автор бенчмарка поручил Claude Code реализовать упрощённый Git на 13 языках. Эксперимент измеряет выполнение этой задачи, а не общую пригодность языков.

2. Автор сообщает о 20 запусках для каждого языка с Claude Opus 4.6 при настройке high effort. Заявленные стоимость и скорость зависят от этой модели и условий задачи.

검토 초점: Прежде чем использовать результат для выбора языка в продакшене, сравните промпты, покрытие тестами, разрешения инструментов, число повторений и конфигурацию модели. Заявленные рейтинги здесь независимо не воспроизводились.

## Security Insights: batch processing and adaptive scan scheduling

원문: https://blog.cloudflare.com/scaling-security-scans/

검토 기준: 영어 보강본 db11f89181439d98, 2026-10-25T12:23:59+00:00

### 영어 기준본

1. Cloudflare describes changing checkers to consume messages in batches and process each message in a separate goroutine. It explicitly notes the trade-offs of redoing work after a mid-batch crash and slightly higher memory use.

> The trade-offs are that we’d have more work to re-do if our process crashed midway through a batch, and our memory usage would be slightly increased.

근거: https://blog.cloudflare.com/scaling-security-scans/

> We changed our checkers to consume messages in batches , processing each message in a separate goroutine.

근거: https://blog.cloudflare.com/scaling-security-scans/

2. The engineering account also describes an adaptive scheduling limit recalculated from account and zone totals and required scanning frequencies, rather than keeping an unchanged rate as the workload grows.

> based on the total number of accounts and zones we have, and our scanning frequencies.

근거: https://blog.cloudflare.com/scaling-security-scans/

검토 초점: This is a scoped review of the documented architecture, not independent reproduction of the headline’s throughput increase. Compare workload, memory, restart behavior and scheduling latency before adopting these patterns.

### 简体中文 (zh-CN)

Security Insights：批处理与自适应扫描调度

1. Cloudflare 描述了将检查器改为批量消费消息、并在独立 goroutine 中处理每条消息的做法。文章明确指出其代价：进程在批次中途崩溃后需要重做更多工作，内存使用量也会略有增加。

2. 这篇工程实践文章还描述了自适应调度上限，会根据账户和 zone 总数以及所需扫描频率重新计算，而不是在工作负载增长时仍维持不变的速率。

검토 초점: 这是对已记录架构的限定范围审阅，并未独立复现标题所称的吞吐量增长。在采用这些模式前，应比较工作负载、内存、重启行为和调度延迟。

### 日本語 (ja)

Security Insights：バッチ処理と適応的なスキャンスケジューリング

1. Cloudflare は、チェッカーをバッチ単位でメッセージを受け取り、各メッセージを別の goroutine で処理する方式に変えたと説明している。バッチの途中でプロセスがクラッシュした際にやり直す作業が増え、メモリ使用量もわずかに増加するというトレードオフを明記している。

2. この技術記事では、アカウントとゾーンの総数、必要なスキャン頻度から上限を再計算する適応的なスケジューリングも説明している。ワークロードが増えても一定のレートを維持する方式ではない。

검토 초점: これは記載されたアーキテクチャに対象を絞ったレビューであり、元記事の見出しにあるスループット向上を独立して再現したものではない。これらのパターンを採用する前に、ワークロード、メモリ、再起動時の動作、スケジューリング遅延を比較する。

### Deutsch (de)

Security Insights: Stapelverarbeitung und adaptive Scanplanung

1. Cloudflare beschreibt die Umstellung der Prüfer auf den stapelweisen Empfang von Nachrichten, wobei jede Nachricht in einer eigenen goroutine verarbeitet wird. Der Bericht benennt ausdrücklich die Nachteile: Nach einem Absturz mitten im Stapel muss mehr Arbeit wiederholt werden, und der Speicherverbrauch steigt leicht.

2. Der technische Bericht beschreibt außerdem eine adaptive Planungsgrenze, die aus der Gesamtzahl der Konten und Zonen sowie den erforderlichen Scanhäufigkeiten neu berechnet wird, statt bei wachsender Arbeitslast eine unveränderte Rate beizubehalten.

검토 초점: Dies ist eine auf die dokumentierte Architektur begrenzte Prüfung, keine unabhängige Reproduktion des in der Überschrift genannten Durchsatzzuwachses. Vor der Übernahme dieser Muster Arbeitslast, Speicherbedarf, Neustartverhalten und Planungslatenz vergleichen.

### Français (fr)

Security Insights : traitement par lots et planification adaptative des analyses

1. Cloudflare décrit la modification des vérificateurs pour qu’ils consomment les messages par lots et traitent chaque message dans une goroutine distincte. Le récit précise les compromis : davantage de travail à refaire en cas de plantage au milieu d’un lot et une légère hausse de l’utilisation mémoire.

2. Le retour d’ingénierie décrit aussi une limite de planification adaptative, recalculée à partir du nombre total de comptes et de zones et des fréquences d’analyse requises, plutôt qu’un débit inchangé lorsque la charge augmente.

검토 초점: Il s’agit d’une revue limitée à l’architecture documentée, sans reproduction indépendante du gain de débit annoncé dans le titre. Comparer la charge de travail, la mémoire, le comportement au redémarrage et la latence de planification avant d’adopter ces pratiques.

### Русский (ru)

Security Insights: пакетная обработка и адаптивное планирование сканирований

1. Cloudflare описывает переход проверяющих компонентов к получению сообщений пакетами с обработкой каждого сообщения в отдельной goroutine. Явно указаны компромиссы: больше повторной работы после сбоя посреди пакета и немного больший расход памяти.

2. В техническом описании также представлен адаптивный предел планирования, пересчитываемый по общему числу учётных записей и зон и требуемым частотам сканирования, вместо сохранения неизменной интенсивности при росте нагрузки.

검토 초점: Это проверка документированной архитектуры с ограниченным охватом, а не независимое воспроизведение роста пропускной способности из заголовка. Перед применением этих подходов сравните нагрузку, расход памяти, поведение при перезапуске и задержку планирования.

## Innersource advisories: enterprise visibility and dependency remediation

원문: https://github.blog/changelog/2026-07-08-innersource-security-advisories-are-generally-available

검토 기준: 영어 보강본 e458b053b5a9f878, 2026-10-25T17:03:04+00:00

### 영어 기준본

1. GitHub announced generally available internal security advisories for Advanced Security enterprise customers. Unlike public open-source advisories, their visibility is restricted to repositories owned by that enterprise.

> GitHub Advanced Security enterprise customers can now publish internal security advisories.

근거: https://github.blog/changelog/2026-07-08-innersource-security-advisories-are-generally-available

> their visibility is restricted to repositories owned by the enterprise.

근거: https://github.blog/changelog/2026-07-08-innersource-security-advisories-are-generally-available

2. The REST API supports creating, updating and withdrawing innersource vulnerabilities. After an advisory is created, Dependabot can notify internal repositories using the component and open an upgrade pull request when a fixed version is needed.

> including operations to create, update, or withdraw vulnerabilities.

근거: https://github.blog/changelog/2026-07-08-innersource-security-advisories-are-generally-available

> Dependabot will open a pull request to upgrade a vulnerable version of the component to one with a fix.

근거: https://github.blog/changelog/2026-07-08-innersource-security-advisories-are-generally-available

검토 초점: Verify enterprise ownership, component identity and dependency matching before rollout. An advisory or generated pull request does not itself deploy a fix; preserve review, testing and release controls.

### 简体中文 (zh-CN)

内部开源安全公告：企业内可见性与依赖修复

1. GitHub 宣布，面向 Advanced Security 企业客户的内部安全公告已正式可用。与公开的开源安全公告不同，其可见范围仅限于该企业所拥有的仓库。

2. REST API 支持创建、更新和撤回内部开源漏洞记录。创建安全公告后，Dependabot 可以通知使用该组件的内部仓库，并在需要修复版本时创建升级拉取请求。

검토 초점: 推出前应核实企业所有权、组件身份和依赖匹配情况。安全公告或自动生成的拉取请求本身并不会部署修复；应保留审查、测试和发布控制。

### 日本語 (ja)

インナーソースのアドバイザリ：企業内の可視性と依存関係の修正

1. GitHub は、Advanced Security の企業顧客向けに内部セキュリティアドバイザリの一般提供を発表した。公開オープンソースのアドバイザリとは異なり、可視性はその企業が所有するリポジトリに限定される。

2. REST API は、インナーソースの脆弱性情報の作成、更新、撤回に対応している。アドバイザリ作成後、Dependabot はそのコンポーネントを利用する内部リポジトリに通知し、修正版が必要な場合にアップグレード用のプルリクエストを作成できる。

검토 초점: 展開前に、リポジトリがその企業に属すること、コンポーネントの識別、依存関係の対応付けを確認する。アドバイザリや生成されたプルリクエストだけで修正がデプロイされるわけではない。レビュー、テスト、リリース管理を維持する。

### Deutsch (de)

Innersource-Sicherheitshinweise: Unternehmensinterne Sichtbarkeit und Abhängigkeitskorrekturen

1. GitHub hat die allgemeine Verfügbarkeit interner Sicherheitshinweise für Unternehmenskunden von Advanced Security angekündigt. Anders als bei öffentlichen Open-Source-Sicherheitshinweisen ist ihre Sichtbarkeit auf Repositorys im Besitz dieses Unternehmens beschränkt.

2. Die REST API unterstützt das Erstellen, Aktualisieren und Zurückziehen von Innersource-Schwachstellen. Nach dem Erstellen eines Sicherheitshinweises kann Dependabot interne Repositorys benachrichtigen, die die Komponente verwenden, und einen Upgrade-Pull-Request eröffnen, wenn ein Update auf eine korrigierte Version erforderlich ist.

검토 초점: Vor dem Rollout Unternehmenseigentum, Komponentenidentität und Zuordnung von Abhängigkeiten überprüfen. Ein Sicherheitshinweis oder generierter Pull Request spielt eine Korrektur nicht selbst in die Zielumgebung ein; Review-, Test- und Releasekontrollen beibehalten.

### Français (fr)

Avis innersource : visibilité en entreprise et correction des dépendances

1. GitHub a annoncé la disponibilité générale des avis de sécurité internes pour les clients entreprise d’Advanced Security. Contrairement aux avis publics de l’open source, leur visibilité est limitée aux dépôts appartenant à cette entreprise.

2. L’API REST permet de créer, de mettre à jour et de retirer des vulnérabilités innersource. Une fois un avis créé, Dependabot peut notifier les dépôts internes utilisant le composant et ouvrir une pull request de mise à niveau lorsqu’une version corrigée est nécessaire.

검토 초점: Vérifier l’appartenance des dépôts à l’entreprise, l’identité des composants et la correspondance des dépendances avant le déploiement. Un avis ou une pull request générée ne déploie pas en soi un correctif ; conserver les contrôles de revue, de test et de publication.

### Русский (ru)

Уведомления innersource: видимость внутри предприятия и исправление зависимостей

1. GitHub объявила об общей доступности внутренних уведомлений безопасности для корпоративных клиентов Advanced Security. В отличие от публичных уведомлений open source, их видимость ограничена репозиториями, принадлежащими этому предприятию.

2. REST API поддерживает создание, обновление и отзыв уязвимостей innersource. После создания уведомления Dependabot может оповестить внутренние репозитории, использующие компонент, и открыть пул-реквест на обновление, когда нужна исправленная версия.

검토 초점: Перед внедрением проверьте принадлежность предприятию, идентичность компонентов и сопоставление зависимостей. Само уведомление или созданный пул-реквест не развёртывает исправление; сохраните контроль ревью, тестирования и выпуска.

