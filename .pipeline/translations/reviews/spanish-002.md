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

### Español (es)

Copilot añade ayuda contextual a los resultados de evaluación de riesgos de GitHub

1. GitHub permite que los administradores de organizaciones y los responsables de seguridad abran Copilot directamente desde los resultados de las evaluaciones de riesgos de secretos o de Code Security.

2. El aviso describe explicaciones contextuales y orientación sobre los siguientes pasos. No demuestra que Copilot haya corregido automáticamente los problemas subyacentes.

검토 초점: Revise las acciones sugeridas y los permisos necesarios para ejecutarlas. Al registrar los resultados de una evaluación, distinga las explicaciones, las correcciones propuestas y las correcciones verificadas.

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

### Español (es)

Proyectos de Spring: clasificación de informes de seguridad y aplicación de parches

1. Spring advirtió que la mayoría de los proyectos de su cartera necesitarían actualizaciones para recibir los parches de seguridad programados y recomendó aplicar los parches más recientes. Se trataba de un aviso sobre una serie de lanzamientos, no de una matriz de versiones afectadas para cada aplicación.

2. El equipo distingue expresamente los informes de seguridad recibidos de los CVE emitidos: los informes pueden contener duplicados o hallazgos no válidos y requieren una clasificación por parte de los mantenedores. El volumen de informes por sí solo no determina la gravedad de las vulnerabilidades.

검토 초점: Relacione las dependencias reales de la aplicación con cada aviso de seguridad y con las ramas de versiones con soporte. Este resumen no reproduce de forma independiente las estadísticas de informes del proveedor ni demuestra que todas las aplicaciones sean explotables.

## Third-party coding-agent security validation on GitHub

원문: https://github.blog/changelog/2026-06-09-security-validation-for-third-party-coding-agents

검토 기준: 영어 보강본 3f90329447f77e33, 2026-10-25T12:23:59+00:00

### 영어 기준본

1. GitHub announced generally available security validation for supported third-party coding agents working in repositories. It describes CodeQL analysis, checks of newly introduced dependencies against the GitHub Advisory Database, and secret scanning.

> GitHub now automatically analyzes it for potential security vulnerabilities using CodeQL

근거: https://github.blog/changelog/2026-06-09-security-validation-for-third-party-coding-agents

> checks newly introduced dependencies against the GitHub Advisory Database, and uses GitHub secret scanning

근거: https://github.blog/changelog/2026-06-09-security-validation-for-third-party-coding-agents

2. The validations are enabled by default, follow repository Copilot validation-tool settings, and do not require a GitHub Advanced Security license. If issues are found, the agent attempts remediation before finalizing the pull request; success is not guaranteed.

> Security validation doesn’t require a GitHub Advanced Security license.

근거: https://github.blog/changelog/2026-06-09-security-validation-for-third-party-coding-agents

> These security validations are on by default and follow your repository’s Copilot settings for which validation tools to use.

근거: https://github.blog/changelog/2026-06-09-security-validation-for-third-party-coding-agents

> the agent attempts to resolve them before finalizing the pull request.

근거: https://github.blog/changelog/2026-06-09-security-validation-for-third-party-coding-agents

검토 초점: Confirm supported agent integration and effective repository settings; keep human review and independent checks for security-sensitive changes. No detection-rate or remediation-success benchmark was reproduced.

### Español (es)

Validación de seguridad para agentes de programación de terceros en GitHub

1. GitHub anunció la disponibilidad general de la validación de seguridad para los agentes de programación de terceros compatibles que trabajan en repositorios. Describe análisis con CodeQL, comprobaciones de las dependencias recién incorporadas frente a GitHub Advisory Database y análisis de secretos.

2. Las validaciones están activadas de forma predeterminada, siguen la configuración de herramientas de validación de Copilot del repositorio y no requieren una licencia de GitHub Advanced Security. Si se detectan problemas, el agente intenta corregirlos antes de finalizar la solicitud de incorporación de cambios; el éxito no está garantizado.

검토 초점: Confirme que la integración del agente sea compatible y compruebe la configuración efectiva del repositorio; mantenga la revisión humana y las comprobaciones independientes para los cambios sensibles desde el punto de vista de la seguridad. No se reprodujo ninguna prueba comparativa de la tasa de detección ni del éxito de las correcciones.

## GitLab 19.0: secret beta, dependency scanning and upgrade prerequisites

원문: https://www.infoq.com/news/2026/06/gitlab-19-agentic-ai/

검토 기준: 영어 보강본 4380abffaf1a31e0, 2026-10-25T12:40:05+00:00

### 영어 기준본

1. In GitLab 19.0, Secrets Manager is an open beta for Premium and Ultimate customers on GitLab.com and Self-Managed. The release notes warn that the beta might not be ready for production use.

> The GitLab Secrets Manager is now available in open beta for Premium and Ultimate customers on GitLab.com and GitLab Self-Managed.

근거: https://docs.gitlab.com/releases/19/gitlab-19-0-released/

> might not be ready for production use.

근거: https://docs.gitlab.com/releases/19/gitlab-19-0-released/

2. SBOM-based dependency scanning is generally available in the Ultimate tier across GitLab.com, Self-Managed and Dedicated. Its availability and tier differ from the Secrets Manager beta.

> Dependency scanning by using SBOM generally available Tier: Ultimate Offering: GitLab.com, GitLab Self-Managed, GitLab Dedicated

근거: https://docs.gitlab.com/releases/19/gitlab-19-0-released/

3. For Self-Managed upgrades to GitLab 19.0, PostgreSQL 17 is the minimum supported version. The notes instruct users of packaged PostgreSQL 16 to upgrade the database before installing the release.

> The minimum supported version of PostgreSQL is now version 17.

근거: https://docs.gitlab.com/releases/19/gitlab-19-0-released/

> If you use the packaged PostgreSQL 16, upgrade the packaged PostgreSQL server before installing GitLab 19.0.

근거: https://docs.gitlab.com/releases/19/gitlab-19-0-released/

검토 초점: This scoped brief covers selected release conditions, not every agentic workflow, billing change or platform requirement. Check the applicable offering, plan, database migration and beta support policy before deployment.

### Español (es)

GitLab 19.0: beta de secretos, análisis de dependencias y requisitos de actualización

1. En GitLab 19.0, Secrets Manager es una beta abierta para clientes Premium y Ultimate de GitLab.com y Self-Managed. Las notas de la versión advierten que la beta podría no estar lista para su uso en producción.

2. El análisis de dependencias basado en SBOM está disponible de forma general en el nivel Ultimate de GitLab.com, Self-Managed y Dedicated. Su disponibilidad y su nivel de suscripción difieren de los de la beta de Secrets Manager.

3. Para actualizar una instalación Self-Managed a GitLab 19.0, PostgreSQL 17 es la versión mínima compatible. Las notas indican a quienes utilizan PostgreSQL 16 incluido en el paquete que actualicen la base de datos antes de instalar esta versión de GitLab.

검토 초점: Este resumen de alcance limitado abarca determinadas condiciones del lanzamiento, no todos los flujos de trabajo con agentes, los cambios de facturación ni los requisitos de plataforma. Antes del despliegue, compruebe la modalidad del servicio, el plan, la migración de la base de datos y la política de soporte de la beta que correspondan.

## Cloudflare reports its operational response to Copy Fail

원문: https://blog.cloudflare.com/copy-fail-linux-vulnerability-mitigation/

검토 기준: 영어 보강본 46983b9e8a1cf49c, 2026-10-25T06:06:33+00:00

### 영어 기준본

1. For Copy Fail (CVE-2026-31431), Cloudflare describes testing a patched kernel in staging before resuming its fleet reboot process.

> Copy Fail" ( CVE-2026-31431 )

근거: https://blog.cloudflare.com/copy-fail-linux-vulnerability-mitigation/

> test the patched kernel in our staging datacenters

근거: https://blog.cloudflare.com/copy-fail-linux-vulnerability-mitigation/

2. Cloudflare reports no impact to its own environment during the incident. That company-specific statement does not establish the safety of other Linux deployments.

> no impact to the Cloudflare environment

근거: https://blog.cloudflare.com/copy-fail-linux-vulnerability-mitigation/

검토 초점: Compare exposure, telemetry, temporary mitigation and verified patch rollout separately. Use distribution-specific advisories for affected versions and do not treat a vendor case study as proof that another fleet is protected.

### Español (es)

Cloudflare describe su respuesta operativa a Copy Fail

1. En relación con Copy Fail (CVE-2026-31431), Cloudflare describe cómo probó un kernel con el parche aplicado en un entorno de preproducción antes de reanudar el proceso de reinicio de su infraestructura.

2. Cloudflare afirma que su propio entorno no se vio afectado durante el incidente. Esa afirmación específica de la empresa no demuestra la seguridad de otras instalaciones de Linux.

검토 초점: Compare por separado la exposición, la telemetría, las medidas temporales de mitigación y el despliegue verificado de parches. Consulte los avisos de cada distribución para identificar las versiones afectadas y no considere el caso de un proveedor como prueba de que otra infraestructura está protegida.

## PHP patches remain necessary alongside Cloudflare WAF protections

원문: https://blog.cloudflare.com/php-vulnerabilities-waf-protection/

검토 기준: 영어 보강본 4a59615041b968ae, 2026-10-25T05:21:13+00:00

### 영어 기준본

1. The PHP project lists 8.5.12, 8.4.27, 8.3.36 and 8.2.35 as fixes for the critical remote-code-execution vulnerabilities disclosed at the time.

> PHP 8.5.12, 8.4.27, 8.3.36 and 8.2.35 fix two critical vulnerabilities

근거: https://www.php.net/archive/2026.php

2. Cloudflare says customers should patch PHP even when its WAF provides an additional defensive layer.

> Customers should patch their PHP repos

근거: https://blog.cloudflare.com/php-vulnerabilities-waf-protection/

후속 확인:

- In its later update, Cloudflare limits protection against the related upload-progress issue to the default field name; changing session.upload_progress.name falls outside that WAF rule.

검토 초점: Review the deployed PHP build and distribution backports separately from WAF coverage. Check upload-progress configuration before treating the later mitigation as applicable. These are review suggestions; no application was tested.

### Español (es)

Los parches de PHP siguen siendo necesarios junto con las protecciones WAF de Cloudflare

1. El proyecto PHP identifica las versiones 8.5.12, 8.4.27, 8.3.36 y 8.2.35 como correcciones para las vulnerabilidades críticas de ejecución remota de código divulgadas en aquel momento.

2. Cloudflare indica que sus clientes deben aplicar los parches de PHP incluso cuando su WAF aporte una capa defensiva adicional.

후속 확인:

- En una actualización posterior, Cloudflare limita la protección frente al problema relacionado con el progreso de las cargas al nombre de campo predeterminado; cambiar session.upload_progress.name queda fuera de la cobertura de esa regla WAF.

검토 초점: Revise la compilación de PHP desplegada y los parches adaptados por la distribución por separado de la cobertura WAF. Compruebe la configuración del progreso de las cargas antes de considerar aplicable la mitigación posterior. Estas son sugerencias de revisión; no se probó ninguna aplicación.

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

### Español (es)

Buildkite limita el alcance de los secretos y añade herramientas de validación de pipelines

1. Buildkite describe los secretos de pipeline como secretos del clúster restringidos al pipeline actual, con la posibilidad de establecer condiciones de acceso adicionales.

2. Su servidor MCP incorpora validate_pipeline para comprobar el YAML del pipeline frente al esquema oficial antes de subirlo.

검토 초점: Revise la exposición de los secretos en cada paso y los permisos concedidos a los agentes de CI. La validación del esquema es una comprobación limitada; el comportamiento durante la ejecución, los complementos y los límites de permisos requieren una revisión aparte.

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

### Español (es)

Security Insights: procesamiento por lotes y planificación adaptativa de análisis

1. Cloudflare describe un cambio en sus verificadores para que consuman mensajes por lotes y procesen cada mensaje en una goroutine independiente. Señala expresamente las contrapartidas: repetir más trabajo si el proceso falla a mitad de un lote y un consumo de memoria ligeramente mayor.

2. El relato técnico también describe un límite de planificación adaptativo que se recalcula a partir del número total de cuentas y zonas y de las frecuencias de análisis requeridas, en lugar de mantener una tasa fija a medida que aumenta la carga de trabajo.

검토 초점: Esta revisión se limita a la arquitectura documentada y no reproduce de forma independiente el aumento de la capacidad de procesamiento anunciado en el titular. Antes de adoptar estos patrones, compare la carga de trabajo, la memoria, el comportamiento tras un reinicio y la latencia de planificación.

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

### Español (es)

Avisos innersource: visibilidad empresarial y corrección de dependencias

1. GitHub anunció la disponibilidad general de avisos de seguridad internos para clientes empresariales de Advanced Security. A diferencia de los avisos públicos de código abierto, su visibilidad está restringida a los repositorios propiedad de esa empresa.

2. La API REST permite crear, actualizar y retirar vulnerabilidades innersource. Tras crear un aviso, Dependabot puede notificar a los repositorios internos que utilizan el componente y abrir una solicitud de incorporación de cambios para actualizarlo cuando se necesita una versión corregida.

검토 초점: Antes de la implantación, verifique la propiedad empresarial, la identidad del componente y la correspondencia de las dependencias. Un aviso o una solicitud de incorporación de cambios generada no despliega por sí mismo una corrección; mantenga los controles de revisión, pruebas y publicación.

## Cloudflare describes identity and governance boundaries for MCP

원문: https://www.infoq.com/news/2026/04/cloudflare-mcp/

검토 기준: 영어 보강본 e858b2ec6331d84e, 2026-10-25T05:38:18+00:00

### 영어 기준본

1. Cloudflare describes an MCP server template that uses Cloudflare Access as its OAuth provider. This concerns its reference architecture rather than a universal MCP requirement.

> Cloudflare Access as the OAuth provider.

근거: https://blog.cloudflare.com/enterprise-mcp/

2. The article says MCP server portals centralize logging, policy enforcement and data-loss prevention controls.

> centralized logging, consistent policy enforcement and data loss prevention

근거: https://blog.cloudflare.com/enterprise-mcp/

검토 초점: Separate identity verification from tool authorization and data-access policy. Review credential scope, write permissions and audit visibility for each connected server; a shared portal does not itself prove least-privilege operation.

### Español (es)

Cloudflare describe los límites de identidad y gobernanza para MCP

1. Cloudflare describe una plantilla de servidor MCP que utiliza Cloudflare Access como proveedor OAuth. Se trata de su arquitectura de referencia, no de un requisito universal de MCP.

2. El artículo indica que los portales de servidores MCP centralizan los registros, la aplicación de políticas y los controles de prevención de pérdida de datos.

검토 초점: Separe la verificación de identidad de la autorización de herramientas y de la política de acceso a los datos. Revise el alcance de las credenciales, los permisos de escritura y la visibilidad de auditoría de cada servidor conectado; un portal compartido no demuestra por sí solo que se opere con el mínimo privilegio.

## Arm Metis: open-source framework and repository context

원문: https://www.infoq.com/news/2026/05/arm-metis-agentic-security/

검토 기준: 영어 보강본 ecc191be72688d94, 2026-10-25T06:31:18+00:00

### 영어 기준본

1. Arm announced that its product security team developed and open-sourced Metis as an agentic security framework.

> developed and open-sourced Metis

근거: https://newsroom.arm.com/blog/arm-metis-agentic-ai-security

2. The announcement describes a retrieval-augmented generation architecture that combines language models with project-specific knowledge for security analysis.

> combines large language models (LLMs) with project-specific knowledge

근거: https://newsroom.arm.com/blog/arm-metis-agentic-ai-security

검토 초점: Review repository context, model access, data boundaries and finding validation before adoption. The vendor’s internal detection-rate and false-positive benchmarks were not independently reproduced in this renewal.

### Español (es)

Arm Metis: framework de código abierto y contexto del repositorio

1. Arm anunció que su equipo de seguridad de producto desarrolló Metis y lo publicó como un framework de seguridad de código abierto basado en agentes.

2. El anuncio describe una arquitectura de generación aumentada por recuperación que combina modelos de lenguaje con conocimiento específico del proyecto para realizar análisis de seguridad.

검토 초점: Antes de adoptarlo, revise el contexto del repositorio, el acceso al modelo, los límites de los datos y la validación de los hallazgos. En esta revisión no se reprodujeron de forma independiente las pruebas comparativas internas del proveedor sobre tasas de detección y falsos positivos.

## AI-security panel: attributed advice on identity and adversarial testing

원문: https://www.infoq.com/articles/security-ai-threat-evolution/

검토 기준: 영어 보강본 eea31f00e6ce7be1, 2026-10-25T12:40:05+00:00

### 영어 기준본

1. In the panel, Elham Arshad recommends treating agents as identities with their own profiles, permissions, credentials and lifecycles, with narrowly scoped capabilities and policy checks for sensitive actions. These are the participant’s recommendations.

> Each agent needs its own profile, permissions, credentials, and lifecycle

근거: https://www.infoq.com/articles/security-ai-threat-evolution/

> agents only get the narrow capabilities they absolutely need, and every sensitive action is checked against policy.

근거: https://www.infoq.com/articles/security-ai-threat-evolution/

2. Vijay Dilwale argues that defenders should test prompt injection, retrieval abuse and tool access by deliberately manipulating inputs and observing behavior as context or permissions change. This is expert advice, not a benchmark proving a control’s effectiveness.

> It requires breaking the system on purpose, experimenting with prompts, seeding malicious content into retrieval sources, and observing how behavior changes when context or permissions shift.

근거: https://www.infoq.com/articles/security-ai-threat-evolution/

검토 초점: This selected panel summary does not represent every participant’s views or establish universal attack frequency. Define a threat model, approval boundaries, logs and repeatable tests before adopting the recommendations.

### Español (es)

Panel sobre seguridad de IA: recomendaciones atribuidas sobre identidad y pruebas adversarias

1. En el panel, Elham Arshad recomienda tratar a los agentes como identidades con sus propios perfiles, permisos, credenciales y ciclos de vida, con capacidades de alcance limitado y comprobaciones de políticas para las acciones sensibles. Estas son recomendaciones de la participante.

2. Vijay Dilwale sostiene que los defensores deben probar la inyección de instrucciones, el abuso de la recuperación de información y el acceso a herramientas manipulando deliberadamente las entradas y observando el comportamiento cuando cambian el contexto o los permisos. Es asesoramiento experto, no una prueba comparativa que demuestre la eficacia de un control.

검토 초점: Este resumen de una selección del panel no representa las opiniones de todos sus participantes ni establece una frecuencia universal de ataques. Antes de adoptar las recomendaciones, defina un modelo de amenazas, los límites de aprobación, los registros y pruebas repetibles.

