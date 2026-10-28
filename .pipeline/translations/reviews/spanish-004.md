# 다국어 번역 검토 초안

의미·용어·조건 대조와 대상 언어 교정은 AI로 검토합니다. 수치·제품명 검사는 의미 검토를 대체하지 않습니다. 사이트 게시는 사용자의 명시적 승인 후에 진행합니다.

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

### Español (es)

Análisis de código con IA: condiciones de la versión preliminar y posterior disponibilidad general

1. Al lanzar la versión preliminar, GitHub describió las detecciones de IA en solicitudes de incorporación de cambios como una ampliación de la cobertura de lenguajes y frameworks más allá de CodeQL. Se requerían permiso empresarial, activación en la organización y el análisis predeterminado de CodeQL en el repositorio, aunque el análisis lo realizaba un motor de IA independiente.

2. Los hallazgos de la versión preliminar eran informativos y no bloqueaban las fusiones. El anuncio exigía una licencia de Copilot y consumía créditos de IA de la organización durante la versión preliminar pública, por lo que la función original no era un control de aprobación automático ni un servicio gratuito sin condiciones.

후속 확인:

- El aviso de GitHub del 2026-10-15 anuncia la disponibilidad general de AI Scan. Indica que no se requiere una licencia de Copilot; los repositorios privados e internos de organizaciones siguen requiriendo GitHub Code Security o Advanced Security. Estas condiciones difieren de las del anuncio de la versión preliminar.
- El aviso posterior mantiene el carácter meramente orientativo de los hallazgos e indica que AI Scan no puede bloquear fusiones mediante conjuntos de reglas. No se ejecuta en solicitudes de incorporación de cambios procedentes de bifurcaciones ni en las creadas por Dependabot.
- El modelo de facturación posterior consume Code Security AI Credits, que aparecen bajo Advanced Security en el uso empresarial de IA. La ausencia del requisito de una licencia de Copilot no significa que el análisis no tenga cargos por uso.

검토 초점: Utilice el aviso posterior para interpretar los requisitos de acceso y la facturación actuales, y conserve las condiciones de la versión preliminar como información histórica. Los hallazgos orientativos requieren una respuesta humana y no sustituyen las comprobaciones obligatorias ni una validación de seguridad completa.

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

### Español (es)

Retirada de modelos de Copilot: alcance, alternativas y excepción para la revisión de código

1. GitHub anunció la retirada de GPT-5.2 y GPT-5.2-Codex el 2026-06-05 en la mayoría de las experiencias de Copilot, pero mantuvo expresamente GPT-5.2 para la revisión de código de Copilot en aquel anuncio. Esto no demuestra su retirada en otros proveedores o API.

2. El anuncio propone GPT-5.5 como alternativa a GPT-5.2 y GPT-5.3-Codex como alternativa a GPT-5.2-Codex. Los administradores empresariales pueden tener que habilitar las alternativas mediante políticas de modelos antes de que los usuarios puedan seleccionarlas.

검토 초점: Antes de migrar, compruebe el producto concreto de Copilot y la política de la organización. Estas son las excepciones y alternativas del aviso histórico, no una afirmación de que la disponibilidad de sus modelos siga igual hoy.

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

### Español (es)

Workers y Durable Objects incorporan perfiles de recursos bajo demanda

1. Cloudflare anunció la creación de perfiles de CPU y memoria para Workers y Durable Objects, con recopilación bajo demanda y perfiles descargables descritos en el artículo.

2. Para los perfiles de CPU, la implementación inicia un perfilador de V8 con un intervalo de muestreo de 1 milisegundo. Ese detalle del muestreo no demuestra que la sobrecarga en producción sea nula.

검토 초점: Compruebe que la versión y el isolate solicitados estén activos en la ubicación seleccionada y compare el comportamiento con y sin perfiles bajo tráfico representativo. Las muestras de asignación de recursos y la memoria retenida son cuestiones diferentes.

## GitHub Copilot: GPT-5.2 and GPT-5.2-Codex retirement corrections

원문: https://github.blog/changelog/2026-05-01-upcoming-deprecation-of-gpt-5-2-and-gpt-5-2-codex

검토 기준: 영어 보강본 3e483be55bb45ecb, 2026-10-25T06:06:33+00:00

### 영어 기준본

1. GitHub published a Copilot retirement notice covering GPT-5.2 and GPT-5.2-Codex. This is a Copilot product notice, not a statement about every provider API.

> GPT-5.2 6-05-2026 GPT-5.5 GPT-5.2-Codex

근거: https://github.blog/changelog/2026-05-01-upcoming-deprecation-of-gpt-5-2-and-gpt-5-2-codex

2. The notice says Copilot Enterprise administrators may need to enable alternative models through their model policies.

> their model policies

근거: https://github.blog/changelog/2026-05-01-upcoming-deprecation-of-gpt-5-2-and-gpt-5-2-codex

후속 확인:

- A later editor note moved the planned retirement from 2026-06-01 to 2026-06-05.
- Another correction identifies GPT-5.2, rather than GPT-5.2-Codex, as the exception for Copilot Code Review.

검토 초점: Use the corrected dates and product exception when auditing historical model choices. Confirm current availability in the relevant product rather than treating this archive as a current model recommendation.

### Español (es)

GitHub Copilot: correcciones sobre la retirada de GPT-5.2 y GPT-5.2-Codex

1. GitHub publicó un aviso de retirada en Copilot que abarcaba GPT-5.2 y GPT-5.2-Codex. Es un aviso del producto Copilot, no una declaración sobre todas las API de los proveedores.

2. El aviso indica que los administradores de Copilot Enterprise pueden tener que habilitar modelos alternativos mediante sus políticas de modelos.

후속 확인:

- Una nota editorial posterior trasladó la retirada prevista del 2026-06-01 al 2026-06-05.
- Otra corrección identifica GPT-5.2, en lugar de GPT-5.2-Codex, como la excepción para Copilot Code Review.

검토 초점: Utilice las fechas corregidas y la excepción del producto al auditar decisiones históricas sobre modelos. Confirme la disponibilidad actual en el producto pertinente en lugar de tratar este archivo como una recomendación de modelos vigente.

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

### Español (es)

Azure DevOps Autofix: fases preliminares, controles de revisión y facturación

1. La publicación de lanzamiento de Microsoft describe Copilot Autofix para GitHub Advanced Security for Azure DevOps como una versión preliminar privada limitada, con altas procesadas por tandas. No se deben combinar esa publicación y la documentación posterior como si describieran una disponibilidad sin cambios.

2. El flujo de lanzamiento genera un cambio sugerido a partir de alertas de CodeQL compatibles y abre una solicitud de incorporación de cambios. Los controles de revisión y compilación existentes siguen ejecutándose, y la alerta se resuelve después de la fusión y del siguiente análisis de CodeQL.

후속 확인:

- En el momento de la revisión, la guía oficial identifica la función como una versión preliminar pública limitada e indica que Microsoft no acepta más usuarios. Es un estado documentado posteriormente, no una prueba de que la descripción original como versión preliminar privada fuera falsa.
- La guía actual indica que la generación de correcciones consume créditos de IA facturados mediante la suscripción de Azure vinculada y que los presupuestos y límites de usuario de GitHub Copilot no rigen ese medidor de Azure DevOps. La inclusión en la licencia no debe interpretarse como generación gratuita de correcciones.

검토 초점: Antes de activar la generación, compruebe la inscripción, los tipos de alertas compatibles y la suscripción de Azure vinculada. Valide las correcciones manualmente y mediante pruebas; generar una sugerencia no corrige por sí mismo una alerta.

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

### Español (es)

Los límites estrictos de presupuesto de GitHub Advanced Security pueden bloquear nueva cobertura

1. GitHub anunció límites estrictos de presupuesto de licencias para Advanced Security que pueden configurar los administradores empresariales y los responsables de facturación. Es un control de licencias del producto, no un límite para todos los gastos de la empresa.

2. Al alcanzar el umbral, el aviso indica que se bloquea el uso adicional de licencias y no se activa Advanced Security en repositorios nuevos hasta que se libere capacidad o se aumente el presupuesto.

검토 초점: Supervise tanto la capacidad de licencias restante como los repositorios sin cobertura de seguridad. Pruebe los procedimientos de incorporación y escalado para evitar que un límite de presupuesto deje repositorios nuevos fuera de los controles previstos sin que se advierta.

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

### Español (es)

Cloudflare comunica menores costes de inferencia para su revisor interno

1. Cloudflare informa de que su revisor interno de código tuvo un coste medio de $0.77 por revisión, un 68% menos frente a una base de $2.43 de sus semanas más caras. Son resultados de su carga de trabajo, no ahorros garantizados para otros equipos.

2. La empresa atribuye cerca del 40% del ahorro a cambios y optimizaciones en el código del revisor, y el resto a la elección de modelos y niveles de esfuerzo.

검토 초점: Compare los costes junto con la calidad de las revisiones, la combinación de cargas de trabajo y el período de evaluación. Reproduzca las mediciones con cambios representativos antes de seleccionar modelos o reducir el esfuerzo; este borrador no contiene ninguna prueba comparativa local.

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

### Español (es)

Presupuestos por usuario en centros de costes: interfaz de facturación y alcance de la pertenencia

1. GitHub anunció que los administradores de Enterprise Cloud podían crear presupuestos por usuario para centros de costes desde la interfaz de facturación, exponiendo controles antes disponibles mediante la API REST. Se trata de una ampliación de la interfaz de gestión.

2. El presupuesto por usuario configurado se aplica a los equipos empresariales o usuarios individuales del centro de costes y se adapta automáticamente a los cambios de pertenencia. Es una configuración de presupuesto compartida que se aplica a cada miembro, no un límite negociado por separado para cada persona.

검토 초점: Examine la pertenencia efectiva, el comportamiento del presupuesto y los ajustes de exceso de consumo junto con la política de facturación empresarial. La disponibilidad de una interfaz no demuestra por sí sola que se bloquee todo el gasto en IA ni que se hayan medido ahorros.

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

### Español (es)

AWS FinOps Agent en versión preliminar: alcance de la investigación y límites regionales

1. AWS anunció una versión preliminar de FinOps Agent que responde a preguntas sobre costes, presenta recomendaciones de optimización, investiga anomalías de costes y programa flujos de trabajo recurrentes. Puede canalizar hallazgos mediante Jira o Slack; esas capacidades no demuestran ahorros medidos.

2. El anuncio sitúa la versión preliminar en US East (N. Virginia), con datos de costes que abarcan las regiones de AWS excepto GovCloud y China. Ofrece el servicio sin cargo adicional durante la versión preliminar; no es un precio permanente ni un compromiso de uso ilimitado.

검토 초점: Confirme la disponibilidad actual, las cuotas, el alcance de los permisos y la facturación antes de activar los flujos de trabajo. La investigación de costes y la creación de incidencias no deben generalizarse como permiso para modificar autónomamente recursos de producción.

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

### Español (es)

Coalición Athena: coordinación de correcciones y condiciones de divulgación

1. Docker anunció su incorporación a Athena como participante fundador y describió la coalición como una defensa coordinada del software de código abierto. Es la descripción de la iniciativa por parte de un participante.

2. Docker describe cómo las organizaciones comparten hallazgos y coordinan respuestas antes de que las vulnerabilidades se hagan públicas. Esto establece el modelo de colaboración declarado, no una cobertura o un éxito de corrección verificados de forma independiente.

후속 확인:

- En el momento de la revisión, la página del programa de Chainguard describe versiones privadas reforzadas disponibles para los miembros mediante Chainguard Libraries durante los 30 días previos a la divulgación. Es la condición de acceso declarada por el programa, no una promesa de disponibilidad pública inmediata de los parches.

검토 초점: Evalúe las reglas de participación, la gestión de los embargos de divulgación y la coordinación con los mantenedores de los proyectos originales. Aquí no se sustentan de forma independiente las métricas de lanzamiento ni las afirmaciones de protección universal; no se deben presentar las condiciones actuales del programa como hechos invariables desde el día del lanzamiento.

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

### Español (es)

Diseño de series temporales: identidad de las series y compromisos de cardinalidad

1. El autor propone almacenar las dimensiones repetidas de las series en una tabla de metadatos separada y referenciarlas mediante un identificador compacto. Describe una propuesta de diseño, no un ahorro de almacenamiento garantizado.

2. El autor advierte que no se utilicen campos de alta cardinalidad, como identificadores de solicitudes y tokens de sesión, como identidad de las series, porque el beneficio depende de que las muestras repetidas compartan una identidad.

검토 초점: Compare la tasa de ingesta, la cardinalidad de las dimensiones, la retención y los patrones de consulta con datos representativos. Este resumen no reproduce los ahorros numéricos comunicados, y la propuesta del autor no debe generalizarse a todos los motores de series temporales.

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

### Español (es)

Opciones de modelos y multiplicadores de uso del agente en la nube de Copilot

1. GitHub añadió Claude Haiku 4.5 y GPT-5.4-mini como opciones de modelos para el agente en la nube de Copilot. El aviso los presenta como opciones para cambios sencillos, no como sustitutos universales para trabajos complejos.

2. El aviso indica un multiplicador de 0.33x para cada modelo añadido. Un multiplicador de uso no es una garantía medida de tiempo de ejecución, calidad del código o coste total del proyecto.

검토 초점: Evalúe tareas representativas atendiendo a la corrección, los reintentos y el esfuerzo de revisión, además de los cargos por uso. Verifique la lista actual de modelos del producto y sus políticas en lugar de tratar este multiplicador histórico como una cotización de precio vigente.

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

### Español (es)

El anuncio de retirada de Claude Sonnet 4 se refiere a Copilot

1. GitHub declaró que Claude Sonnet 4 fue retirado de sus experiencias de Copilot el 2026-05-06. La declaración se refiere a Copilot, no a todos los canales de distribución de Anthropic.

2. El anuncio indica a los administradores de Copilot Enterprise que comprueben las políticas de modelos al habilitar alternativas.

검토 초점: Distinga la retirada de un producto, la retirada por parte del proveedor y el comportamiento local de las alternativas de respaldo. Pruebe los permisos y el comportamiento del flujo de trabajo con opciones compatibles, en lugar de tratar una recomendación antigua de sustitución como orientación vigente.

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

### Español (es)

El aviso de retirada de GPT-4.1 de GitHub se refiere a Copilot

1. GitHub anunció la retirada prevista de GPT-4.1 de Copilot para el 2026-06-01. Esto no describe su disponibilidad a través de todas las API externas.

2. Según el aviso, los administradores de Copilot Enterprise pueden tener que habilitar el acceso a modelos de sustitución mediante políticas de modelos.

검토 초점: Confirme qué experiencia de Copilot y qué política utiliza el flujo de trabajo. Trate la fecha programada como evidencia histórica y compruebe la disponibilidad real y actual de los modelos antes de actualizar la configuración.

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

### Español (es)

Alertas cerradas de Dependabot: retención anunciada y acceso a archivos

1. El aviso de GitHub programó un cambio de retención para el 2026-09-25, empezando por las alertas de seguridad cerradas de Dependabot en github.com y Enterprise Cloud. Excluye expresamente Enterprise Server; el anuncio por sí solo no verifica que el despliegue se haya completado.

2. Según la política anunciada, las alertas abiertas siguen siendo accesibles independientemente de su antigüedad, mientras que las cerradas permanecen en la interfaz y la API durante 2 años después de su cierre. Las alertas cerradas más antiguas pasan a archivos CSV descargables para administradores y responsables de seguridad autorizados, en lugar de seguir apareciendo en los resultados de la API.

검토 초점: Audite las consultas y las exportaciones de cumplimiento que dependen de alertas cerradas antiguas. Verifique el acceso real a los archivos y el estado del despliegue en la cuenta correspondiente; no aplique este aviso a todos los tipos de alertas ni deduzca una retención permanente tras eliminar una cuenta o un repositorio.

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

### Español (es)

Microsoft MDASH: análisis con múltiples modelos y estado preliminar

1. Microsoft describe MDASH como una infraestructura de análisis basada en agentes y múltiples modelos que coordina un conjunto de modelos de frontera y destilados. Es la descripción de su arquitectura por parte del proveedor.

2. El anuncio invita a participar en una versión preliminar privada, que no debe confundirse con disponibilidad pública general.

검토 초점: Distinga los resultados de pruebas comparativas comunicados por el proveedor de los hallazgos reproducidos de forma independiente. Revise las condiciones de acceso, el tratamiento del código fuente y los requisitos de validación antes de utilizar la herramienta en un flujo de seguridad.

## Copilot CLI security review remains an experimental preview

원문: https://github.blog/changelog/2026-06-10-dedicated-security-review-command-now-available-in-copilot-cli

검토 기준: 영어 보강본 c4a7f428da738696, 2026-10-25T12:23:59+00:00

### 영어 기준본

1. GitHub introduced the /security-review command for local code changes as an experimental public-preview feature. Users must enable experimental mode to try the command.

> The new /security-review slash command is shipping as an experimental feature in public preview

근거: https://github.blog/changelog/2026-06-10-dedicated-security-review-command-now-available-in-copilot-cli

> turn on experimental mode in Copilot CLI

근거: https://github.blog/changelog/2026-06-10-dedicated-security-review-command-now-available-in-copilot-cli

2. The announcement describes a Copilot-driven scan that does not rely on GitHub code scanning, Dependabot or secret scanning. It complements those tools with on-demand review before committing; it is not evidence that all vulnerabilities will be detected.

> This is a Copilot-driven scan that doesn’t rely on GitHub code scanning, Dependabot, or GitHub secret scanning.

근거: https://github.blog/changelog/2026-06-10-dedicated-security-review-command-now-available-in-copilot-cli

검토 초점: Check feature availability in the installed CLI and inspect findings manually. Preserve deterministic security checks and avoid treating a clean preview scan as a security certification.

### Español (es)

La revisión de seguridad de Copilot CLI sigue siendo una función preliminar experimental

1. GitHub introdujo el comando /security-review para cambios de código locales como una función experimental en versión preliminar pública. Los usuarios deben activar el modo experimental para probarlo.

2. El anuncio describe un análisis impulsado por Copilot que no depende del análisis de código de GitHub, Dependabot ni del análisis de secretos. Complementa esas herramientas con una revisión bajo demanda antes de confirmar los cambios; no demuestra que se detecten todas las vulnerabilidades.

검토 초점: Compruebe la disponibilidad de la función en la CLI instalada e inspeccione los hallazgos manualmente. Mantenga las comprobaciones de seguridad deterministas y no considere un análisis preliminar sin hallazgos como una certificación de seguridad.

## Tracking-service case study: event schemas and non-blocking delivery

원문: https://www.infoq.com/presentations/mobile-user-tracking-service/

검토 기준: 영어 보강본 c505a5c997b12684, 2026-10-25T12:40:05+00:00

### 영어 기준본

1. In the published transcript, Alina Krasavina describes Delivery Hero’s internal tracking service using mobile and frontend SDKs, an ingestion API, real-time consumers and BigQuery storage. This is the speaker’s implementation account.

> we have a mobile SDK, and a frontend SDK, in TypeScript, to collect the data and to send to our API.

근거: https://www.infoq.com/presentations/mobile-user-tracking-service/

> our data storage, which is BigQuery

근거: https://www.infoq.com/presentations/mobile-user-tracking-service/

2. The speaker says code-generated event models exposed schema problems during application compilation, while a device queue and background batched sending supported non-blocking delivery. The reported cost and capture-rate figures are excluded from this scoped summary.

> we introduced code generated event models

근거: https://www.infoq.com/presentations/mobile-user-tracking-service/

> you have an error on compilation time

근거: https://www.infoq.com/presentations/mobile-user-tracking-service/

> it reads from the queue, takes a batch of some events, and is sending to our API.

근거: https://www.infoq.com/presentations/mobile-user-tracking-service/

검토 초점: Treat the transcript as primary evidence of what the speaker reported, not independent replication. Evaluate schema ownership, buffering limits, delivery failures, privacy requirements and migration parity for your own workload.

### Español (es)

Caso de un servicio de seguimiento: esquemas de eventos y envío no bloqueante

1. En la transcripción publicada, Alina Krasavina describe el servicio interno de seguimiento de Delivery Hero, que utiliza SDK móviles y de frontend, una API de ingesta, consumidores en tiempo real y almacenamiento en BigQuery. Es el relato de la implementación por parte de la ponente.

2. La ponente afirma que los modelos de eventos producidos mediante generación de código revelaban problemas de esquema durante la compilación de las aplicaciones, mientras que una cola en el dispositivo y el envío por lotes en segundo plano permitían un envío no bloqueante. Las cifras comunicadas de costes y tasa de captura se excluyen de este resumen de alcance limitado.

검토 초점: Trate la transcripción como evidencia primaria de lo que comunicó la ponente, no como una reproducción independiente. Evalúe la responsabilidad sobre los esquemas, los límites de almacenamiento temporal, los fallos de entrega, los requisitos de privacidad y la equivalencia durante la migración para su propia carga de trabajo.

## Windows agent containment: early preview and audit-mode limits

원문: https://www.infoq.com/news/2026/06/windows-security-agents/

검토 기준: 영어 보강본 ce26c7555a2bf537, 2026-10-25T12:40:05+00:00

### 영어 기준본

1. Microsoft introduced the MXC SDK as an early preview: a policy-driven execution layer for agents on Windows and WSL. An SDK announcement is not independent evidence that arbitrary agent workloads are safe.

> an early preview of the Microsoft Execution Containers (MXC) SDK

근거: https://blogs.windows.com/windowsdeveloper/2026/06/02/windows-platform-security-for-ai-agents/

> a cross-platform, policy-driven execution layer for agents on Windows and WSL.

근거: https://blogs.windows.com/windowsdeveloper/2026/06/02/windows-platform-security-for-ai-agents/

2. The announcement describes multiple isolation constructs behind a shared policy model. It labels Linux-container support and MXC cloud integration as future work, so those plans should not be presented as delivered features at announcement time.

> Linux containers Will bring the containment model to Linux-first agent toolchains via WSL.

근거: https://blogs.windows.com/windowsdeveloper/2026/06/02/windows-platform-security-for-ai-agents/

> With the future addition of MXC integration

근거: https://blogs.windows.com/windowsdeveloper/2026/06/02/windows-platform-security-for-ai-agents/

후속 확인:

- At review time, the MXC repository warns that --audit disables all sandbox security for the analyzed workload and must never be used to run untrusted code. Policy-authoring audit mode is not a containment guarantee.

검토 초점: Verify the actual backend, operating-system support, filesystem access and network behavior in a representative environment. This is a source-context review without sandbox-escape or containment testing.

### Español (es)

Contención de agentes en Windows: versión preliminar temprana y límites del modo de auditoría

1. Microsoft presentó MXC SDK como una versión preliminar temprana: una capa de ejecución para agentes en Windows y WSL regida por políticas. El anuncio de un SDK no es evidencia independiente de que las cargas arbitrarias de agentes sean seguras.

2. El anuncio describe varias formas de aislamiento bajo un modelo de políticas compartido. Identifica el soporte de contenedores Linux y la integración de MXC con la nube como trabajo futuro, por lo que esos planes no deben presentarse como funciones entregadas en el momento del anuncio.

후속 확인:

- En el momento de la revisión, el repositorio de MXC advierte que --audit desactiva toda la seguridad del entorno aislado para la carga analizada y que nunca debe utilizarse para ejecutar código no confiable. El modo de auditoría para elaborar políticas no es una garantía de contención.

검토 초점: Verifique el backend real, el soporte del sistema operativo, el acceso al sistema de archivos y el comportamiento de la red en un entorno representativo. Esta es una revisión del contexto de las fuentes, sin pruebas de escape del entorno aislado ni de contención.

## npm installation defaults and staged token restrictions

원문: https://github.blog/changelog/2026-07-08-npm-install-time-security-and-gat-bypass2fa-deprecation

검토 기준: 영어 보강본 d123262315e62321, 2026-10-25T17:03:04+00:00

### 영어 기준본

1. The npm 12 announcement makes dependency lifecycle scripts and implicit node-gyp builds opt-in, and defaults Git and remote-URL dependency resolution to none unless explicitly allowed. These are installation defaults, not a guarantee that installed code is harmless.

> Dependency lifecycle scripts (i.e., preinstall , install , postinstall ) and implicit node-gyp builds no longer run unless explicitly allowed.

근거: https://github.blog/changelog/2026-07-08-npm-install-time-security-and-gat-bypass2fa-deprecation

> --allow-git defaults to none

근거: https://github.blog/changelog/2026-07-08-npm-install-time-security-and-gat-bypass2fa-deprecation

> --allow-remote defaults to none

근거: https://github.blog/changelog/2026-07-08-npm-install-time-security-and-gat-bypass2fa-deprecation

2. The same notice planned removal of sensitive management actions from npm 2FA-bypass tokens for early 2026-08. It separately targeted direct-publish restrictions for around 2027-01, with trusted publishing or human-approved staged publishing as migration paths.

> We expect this change to take effect in early August 2026.

근거: https://github.blog/changelog/2026-07-08-npm-install-time-security-and-gat-bypass2fa-deprecation

> We expect this change to take effect around January 2027.

근거: https://github.blog/changelog/2026-07-08-npm-install-time-security-and-gat-bypass2fa-deprecation

> move automated publishing to trusted publishing (OIDC) or staged publishing with a human approval step

근거: https://github.blog/changelog/2026-07-08-npm-install-time-security-and-gat-bypass2fa-deprecation

후속 확인:

- The 2026-07-31 follow-up says npm 2FA-bypass granular access tokens can no longer perform sensitive management actions and requires an interactive 2FA challenge. It explicitly excludes GitHub personal access tokens, GitHub App tokens and GITHUB_TOKEN from that change.
- That follow-up still describes removal of direct publishing as a target for 2027-01. It does not report that later publishing restriction as completed.

검토 초점: Test native builds and dependency sources before upgrading, and review script allowlists rather than enabling everything. Verify current publishing support for your CI provider; a schedule announcement is not proof that every registry action has already changed.

### Español (es)

Valores predeterminados de instalación de npm y restricciones escalonadas de tokens

1. El anuncio de npm 12 exige una autorización explícita para ejecutar scripts del ciclo de vida de las dependencias y compilaciones implícitas de node-gyp, y configura en none la resolución de dependencias de Git y de URL remotas salvo autorización expresa. Son valores predeterminados de instalación, no una garantía de que el código instalado sea inofensivo.

2. El mismo aviso preveía retirar las acciones de gestión sensibles de los tokens de npm que omiten 2FA a principios de 2026-08. Por separado, situaba las restricciones de publicación directa alrededor de 2027-01, con la publicación de confianza o la publicación por etapas aprobada por una persona como vías de migración.

후속 확인:

- La actualización del 2026-07-31 indica que los tokens de acceso granular de npm que omiten 2FA ya no pueden realizar acciones de gestión sensibles y que se requiere una comprobación interactiva de 2FA. Excluye expresamente de ese cambio los tokens de acceso personal de GitHub, los tokens de GitHub App y GITHUB_TOKEN.
- Esa actualización sigue describiendo la retirada de la publicación directa como un objetivo para 2027-01. No comunica que esa restricción posterior de publicación se haya completado.

검토 초점: Pruebe las compilaciones nativas y las fuentes de dependencias antes de actualizar, y revise las listas de scripts permitidos en lugar de activarlo todo. Verifique el soporte actual de publicación de su proveedor de CI; un anuncio de calendario no demuestra que todas las acciones del registro ya hayan cambiado.

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

### Español (es)

Pódcast de seguridad en la nube: consejos atribuidos sobre aislamiento y aprendizaje

1. En la transcripción, Alex Zenla, que cofundó Edera, describe una abstracción denominada zona para aislar cargas dentro de máquinas virtuales. Ese relato del diseño procede del proveedor; no es un límite de seguridad probado de forma independiente.

2. Zenla describe el uso de modelos de lenguaje para explicar especificaciones y subraya la necesidad de comprender la implementación resultante. Las críticas de la entrevista a la infraestructura existente son una opinión técnica atribuida, no una prueba de que todos los despliegues de contenedores o GPU sean inseguros.

검토 초점: Utilice la transcripción para evaluar el argumento de la persona entrevistada y valide después los requisitos de aislamiento y los modos de fallo frente a su propio modelo de amenazas. Para este resumen no se realizó ningún experimento de escape del entorno aislado, rendimiento o hardware de IA.

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

### Español (es)

Retirada de Gemini en Copilot: avisos de planificación y finalización

1. El aviso original de GitHub programó la retirada de Gemini 2.5 Pro y Gemini 3 Flash de las experiencias de Copilot para el 2026-07-31. Es un aviso del producto Copilot y no demuestra la retirada de esos mismos modelos en otros proveedores o API.

2. Las alternativas previstas eran Gemini 3.1 Pro y Gemini 3.5 Flash. El aviso también advertía que las políticas empresariales de modelos podían tener que permitir las alternativas antes de que los usuarios pudieran seleccionarlas.

후속 확인:

- La actualización de GitHub del 2026-07-31 comunica que la retirada en Copilot se ha completado. Su tabla de alternativas incluye Gemini 3.1 Pro (Preview) y Gemini 3.6 Flash, que sustituye la sugerencia anterior de Gemini 3.5 Flash. Son las alternativas de ese aviso, no una afirmación de que su disponibilidad siga igual hoy.

검토 초점: Confirme la experiencia concreta de Copilot, la política de la organización y los modelos actualmente compatibles. El aviso posterior de finalización cambia una alternativa sugerida; no siga presentando la sugerencia inicial como la orientación definitiva de migración.

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

### Español (es)

Una prueba comparativa de lenguajes mide una tarea de Git simplificada

1. El autor de la prueba comparativa pidió a Claude Code que implementara un Git simplificado en 13 lenguajes. El experimento mide esa tarea, no la idoneidad general de los lenguajes.

2. El autor comunica 20 ejecuciones por lenguaje con Claude Opus 4.6 y un nivel de esfuerzo alto. Los costes y la velocidad comunicados dependen de ese modelo y de la configuración de la tarea.

검토 초점: Compare las instrucciones, la cobertura de pruebas, los permisos de las herramientas, las repeticiones y la configuración del modelo antes de utilizar el resultado para elegir un lenguaje de producción. Las clasificaciones comunicadas no se reprodujeron aquí de forma independiente.

## AI-security course announcement: scope and evidence limits

원문: https://www.infoq.com/news/2026/07/online-cohort-ai-security/

검토 기준: 영어 보강본 e467e85426c883ef, 2026-10-26T01:34:51+00:00

### 영어 기준본

1. InfoQ’s own announcement described a 5-week online AI security and privacy cohort for senior engineers and architects in regulated industries, facilitated by Katharine Jarmul. This establishes the provider’s announced format, not an independent endorsement of training quality.

> a five-week online cohort for senior engineers and architects

근거: https://www.infoq.com/news/2026/07/online-cohort-ai-security/

> are facilitated by Katharine Jarmul

근거: https://www.infoq.com/news/2026/07/online-cohort-ai-security/

2. The provider described threat modeling, red teaming, controls, observability and governance, with a documented risk assessment and mitigation report as the capstone. These are advertised learning activities rather than evidence that graduates or products meet regulatory requirements.

> Each working group produces a documented risk assessment and mitigation report for an AI product architecture as its capstone

근거: https://www.infoq.com/news/2026/07/online-cohort-ai-security/

검토 초점: Treat the archived announcement as provider-supplied course information. Verify current schedule, syllabus, price and enrollment directly before purchasing; historical registration dates and prices are deliberately not presented as current offers.

### Español (es)

Anuncio de un curso de seguridad de IA: alcance y límites de la evidencia

1. El propio anuncio de InfoQ describía un curso en línea por cohortes de 5 semanas sobre seguridad y privacidad de IA para ingenieros sénior y arquitectos de sectores regulados, facilitado por Katharine Jarmul. Esto establece el formato anunciado por el proveedor, no un aval independiente de la calidad de la formación.

2. El proveedor describía el modelado de amenazas, las pruebas de red teaming, los controles, la observabilidad y la gobernanza, con una evaluación de riesgos documentada y un informe de mitigación como proyecto final. Son actividades de aprendizaje anunciadas, no evidencia de que los participantes o los productos cumplan los requisitos normativos.

검토 초점: Trate el anuncio archivado como información del curso facilitada por su proveedor. Antes de comprar, verifique directamente el calendario, el temario, el precio y la inscripción actuales; las fechas y los precios históricos de inscripción no se presentan deliberadamente como ofertas vigentes.

## Cloudflare roadmap includes post-quantum authentication

원문: https://blog.cloudflare.com/post-quantum-roadmap/

검토 기준: 영어 보강본 fb47d93f2cc47316, 2026-10-25T05:38:18+00:00

### 영어 기준본

1. Cloudflare announced a target of 2029 for full post-quantum security, explicitly including authentication. This is a roadmap target rather than a completed migration.

> target 2029 to be fully post-quantum

근거: https://blog.cloudflare.com/post-quantum-roadmap/

2. The announcement distinguishes post-quantum encryption from authentication and says the work is incomplete until authentication is upgraded.

> work is not done until authentication is also upgraded.

근거: https://blog.cloudflare.com/post-quantum-roadmap/

검토 초점: Inventory key exchange, certificates and signing dependencies separately. Confirm the current product-specific roadmap before scheduling changes; the historical date is not a migration guarantee for every deployment.

### Español (es)

La hoja de ruta de Cloudflare incluye autenticación poscuántica

1. Cloudflare anunció el objetivo de alcanzar una seguridad plenamente poscuántica en 2029, incluida expresamente la autenticación. Es un objetivo de hoja de ruta, no una migración completada.

2. El anuncio distingue el cifrado poscuántico de la autenticación e indica que el trabajo no está terminado hasta que también se actualice la autenticación.

검토 초점: Haga inventarios separados del intercambio de claves, los certificados y las dependencias de firma. Confirme la hoja de ruta actual de cada producto antes de programar cambios; la fecha histórica no es una garantía de migración para todos los despliegues.

## Copilot app security review: preview scope and review limits

원문: https://github.blog/changelog/2026-07-14-security-reviews-now-available-in-the-github-copilot-app

검토 기준: 영어 보강본 fe469724f5828fb0, 2026-10-25T17:03:04+00:00

### 영어 기준본

1. GitHub introduced the Copilot app /security-review command in public preview for current workstream changes. The announcement described severity- and confidence-scored findings with actionable suggestions, not a proof that every vulnerability would be found.

> The /security-review slash command is shipping in public preview

근거: https://github.blog/changelog/2026-07-14-security-reviews-now-available-in-the-github-copilot-app

> High-confidence security findings, scored by severity and confidence.

근거: https://github.blog/changelog/2026-07-14-security-reviews-now-available-in-the-github-copilot-app

2. The command complements code scanning, Dependabot and secret scanning with an on-demand local-change review. At launch, it was available to Copilot Free, Pro, Business and Enterprise users during public preview; the notice does not establish permanent pricing or continued availability.

> It complements GitHub code scanning, Dependabot, and secret scanning

근거: https://github.blog/changelog/2026-07-14-security-reviews-now-available-in-the-github-copilot-app

> The command is available to Copilot Free, Pro, Business, and Enterprise users during public preview.

근거: https://github.blog/changelog/2026-07-14-security-reviews-now-available-in-the-github-copilot-app

검토 초점: Confirm installed-app support and current plan terms, then validate each suggestion with tests and review. A clean AI review should not be treated as a security certification or a substitute for release controls.

### Español (es)

Revisión de seguridad en la aplicación Copilot: alcance preliminar y límites de la revisión

1. GitHub introdujo el comando /security-review de la aplicación Copilot en versión preliminar pública para los cambios del workstream actual. El anuncio describía hallazgos puntuados por gravedad y confianza, con sugerencias que permiten actuar, no una prueba de que se encontrarían todas las vulnerabilidades.

2. El comando complementa el análisis de código, Dependabot y el análisis de secretos con una revisión bajo demanda de los cambios locales. En el lanzamiento estaba disponible para usuarios de Copilot Free, Pro, Business y Enterprise durante la versión preliminar pública; el aviso no establece precios permanentes ni una disponibilidad continuada.

검토 초점: Confirme la compatibilidad de la aplicación instalada y las condiciones actuales del plan, y valide después cada sugerencia con pruebas y revisión. Una revisión de IA sin hallazgos no debe considerarse una certificación de seguridad ni un sustituto de los controles de publicación.
