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

### Español (es)

El aviso de retirada de Grok Code Fast 1 delimita su alcance en Copilot

1. GitHub anunció la retirada prevista de Grok Code Fast 1 de Copilot para el 2026-05-15. Aquí se recoge el calendario anunciado, sin verificar de forma independiente que la retirada se haya completado.

2. El aviso indica que la fecha se adelantó debido a la retirada del modelo por parte de su proveedor.

검토 초점: Antes de cambiar los flujos de trabajo, haga un inventario de los nombres de modelos específicos de cada producto y de las dependencias de las políticas de administración. Compruebe la disponibilidad actual y evalúe una alternativa con tareas representativas, en lugar de adoptar automáticamente los modelos recomendados en anuncios históricos.

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

### Español (es)

CodeQL incorpora sanitizadores y validadores personalizados a los modelos como datos

1. GitHub describe sanitizadores y validadores declarativos en las extensiones de datos YAML de CodeQL mediante barrierModel y barrierGuardModel.

2. El anuncio señala que están disponibles a partir de CodeQL 2.25.2. Esta es la versión mínima indicada en aquel anuncio histórico, no una recomendación de actualización actual.

검토 초점: Modele únicamente los tipos de vulnerabilidades y las rutas que el sanitizador protege realmente. Pruebe ejemplos positivos y negativos para evitar que una barrera demasiado amplia oculte flujos reales de datos contaminados; este borrador no afirma haber medido una reducción de los falsos positivos.

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

### Español (es)

GitHub comunica la retirada de Grok Code Fast 1 de Copilot

1. GitHub comunicó que Grok Code Fast 1 se había retirado de sus distintas experiencias de Copilot el 2026-05-15. Se trata del aviso del proveedor del producto que confirma la retirada, distinto del anuncio anterior de la fecha prevista.

2. El aviso indica que los administradores de Copilot Enterprise podrían tener que habilitar modelos alternativos mediante sus políticas de modelos.

검토 초점: Al revisar el archivo, relacione este aviso de retirada completada con el artículo anterior sobre la retirada prevista. Confirme la disponibilidad real del producto y las políticas de administración antes de cambiar un flujo de trabajo; el anuncio no describe todas las API de los proveedores.

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

### Español (es)

Fondos de créditos de Copilot: uso incluido y gasto adicional

1. GitHub anunció fondos de créditos de AI por centro de costes para Copilot Business y Enterprise en Enterprise Cloud. En el momento del anuncio, la configuración estaba disponible mediante la REST API, mientras que la gestión desde la interfaz de ajustes aún estaba prevista.

2. El límite del fondo restringe los créditos incluidos del conjunto de la empresa que puede utilizar un centro de costes; el presupuesto del centro de costes regula los cargos por consumo una vez agotado el fondo incluido. Estos controles cubren distintas fases del gasto y pueden combinarse.

3. GitHub calcula el límite del fondo a partir de las licencias asignadas. Al alcanzar el límite, las empresas pueden bloquear el uso adicional de créditos incluidos o permitir gasto adicional si se autorizan los excesos de consumo, por lo que el fondo no constituye automáticamente un límite estricto para todos los cargos.

검토 초점: Revise conjuntamente la asignación de créditos incluidos, la política de exceso de consumo y los presupuestos de pago por uso. Confirme la disponibilidad actual de la API y de la interfaz antes de cambiar los controles; esta revisión de la fuente no mide el ahorro real.

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

### Español (es)

Los avisos de seguridad de los repositorios de GitHub incorporan búsqueda y filtros

1. GitHub añadió búsqueda y filtrado de avisos de seguridad directamente en la pestaña Security de un repositorio.

2. El aviso enumera sort, package, ecosystems y severity entre las palabras clave de búsqueda o filtrado admitidas.

검토 초점: Compruebe si la vista contiene los avisos en borrador, recibidos y publicados que necesita para la revisión. Un conjunto de resultados filtrados más pequeño no debe interpretarse como un menor número de vulnerabilidades subyacentes.

## Multi-region design: replication, writes and failover trade-offs

원문: https://www.infoq.com/articles/multi-region-latency-cost-tradeoffs/

검토 기준: 영어 보강본 7c3a8ce4dcd53d2b, 2026-10-26T01:34:51+00:00

### 영어 기준본

1. The article author contrasts independently serving active-active regions with a design that serves reads locally but proxies remote writes to a global write region. The trade-off includes replication, conflict handling and cross-region write latency.

> Users are routed to their nearest region; each region handles both reads and writes.

근거: https://www.infoq.com/articles/multi-region-latency-cost-tradeoffs/

> Write requests from non-primary regions are proxied to the global write region before acknowledgment.

근거: https://www.infoq.com/articles/multi-region-latency-cost-tradeoffs/

2. For active-passive operation, the author describes a primary serving traffic and a continuously replicated secondary. The article warns that unexercised failover paths can fail and recommends using measured failover behavior in planning. Its percentage savings and latency-recovery estimates are excluded here.

> a secondary region receives continuous replication but serves no traffic under normal conditions.

근거: https://www.infoq.com/articles/multi-region-latency-cost-tradeoffs/

> Failover paths that are never exercised tend to fail when invoked.

근거: https://www.infoq.com/articles/multi-region-latency-cost-tradeoffs/

검토 초점: This is a scoped review of the author’s design discussion, not a universal cost model. Measure workload locality, consistency requirements, recovery behavior and operating effort before choosing a regional architecture.

### Español (es)

Diseño multirregión: compromisos entre replicación, escrituras y conmutación por error

1. El autor del artículo contrapone las regiones active-active que atienden solicitudes de forma independiente a un diseño que sirve las lecturas localmente, pero reenvía las escrituras remotas a una región de escritura global. Los compromisos incluyen la replicación, la gestión de conflictos y la latencia de escritura entre regiones.

2. Para el funcionamiento active-passive, el autor describe una región principal que atiende el tráfico y una secundaria que recibe replicación continua. El artículo advierte de que las rutas de conmutación por error que no se han probado pueden fallar y recomienda incorporar el comportamiento medido de la conmutación a la planificación. Aquí se excluyen los porcentajes de ahorro y las estimaciones de recuperación de la latencia que presenta.

검토 초점: Esta revisión se limita al análisis del diseño que hace el autor y no constituye un modelo de costes universal. Mida la distribución geográfica de la carga, los requisitos de consistencia, el comportamiento de recuperación y el esfuerzo operativo antes de elegir una arquitectura regional.
