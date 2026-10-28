# 다국어 번역 검토 초안

의미·용어·조건 대조와 대상 언어 교정은 AI로 검토합니다. 수치·제품명 검사는 의미 검토를 대체하지 않습니다. 사이트 게시는 사용자의 명시적 승인 후에 진행합니다.

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

### Español (es)

Spring Boot en fase milestone: cambios en LDAP y telemetría

1. El milestone Spring Boot 4.2.0-M2 añade soporte de paquetes SSL para LDAP, incluido LDAPS para el servidor integrado. Este resumen verifica la parte relativa a Boot de la recopilación anterior.

2. El mismo milestone añade soporte para las convenciones semánticas de OpenTelemetry, junto con una configuración común del endpoint OTLP, las cabeceras y la compresión.

검토 초점: Conserve la fecha original de la recopilación y describa estas funciones como propias de un milestone. Antes de aprobar el artículo original completo, verifique por separado las versiones de Framework, Data, Security e Integration; este borrador de alcance más limitado no verifica esas secciones.

## Spring Boot release candidate adds client-network and telemetry controls

원문: https://www.infoq.com/news/2026/04/spring-news-roundup-apr20-2026/

검토 기준: 영어 보강본 f05ff63990b375e2, 2026-10-25T05:38:18+00:00

### 영어 기준본

1. The Spring Boot 4.1.0-RC1 announcement lists HTTP client SSRF mitigation with InetAddressFilter. This draft covers only the Boot portion of the older roundup.

> Spring Boot 4.1.0-RC1 has been released

근거: https://spring.io/blog/2026/04/23/spring-boot-4-1-0-RC1-available-now

> HTTP Client SSRF Mitigation with InetAddressFilter

근거: https://spring.io/blog/2026/04/23/spring-boot-4-1-0-RC1-available-now

2. The same release candidate lists support for OpenTelemetry SDK environment variables.

> Support for OpenTelemetry SDK environment variables

근거: https://spring.io/blog/2026/04/23/spring-boot-4-1-0-RC1-available-now

검토 초점: Verify the other projects in the roundup separately before marking the entire original item complete. Review release-candidate status, address-filter configuration and observability settings against the versions actually deployed.

### Español (es)

Spring Boot incorpora controles de red del cliente y telemetría en una versión candidata

1. El anuncio de Spring Boot 4.1.0-RC1 incluye medidas de mitigación de SSRF en el cliente HTTP mediante InetAddressFilter. Este resumen abarca únicamente la parte relativa a Boot de la recopilación anterior.

2. La misma versión candidata incluye soporte para las variables de entorno del SDK de OpenTelemetry.

검토 초점: Verifique por separado los demás proyectos de la recopilación antes de dar por completado el artículo original. Revise el estado de versión candidata, la configuración del filtro de direcciones y los ajustes de observabilidad frente a las versiones realmente desplegadas.

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

### Español (es)

Recopilación de versiones de Spring: bases seleccionadas de plataforma e IA

1. El equipo de Spring Boot anunció la disponibilidad de 4.1.0 en Maven Central e indica que incluye las correcciones de Spring Boot 4.0.7. Este resumen abarca esa versión de la plataforma, no todos los proyectos de la recopilación original.

2. El equipo de Spring AI anunció la disponibilidad de 2.0.0 en Maven Central. Su base documentada es Spring Boot 4.0 / 4.1 con Spring Framework 7.0, por lo que se debe revisar la compatibilidad de las aplicaciones antes de actualizarlas.

검토 초점: Compruebe las notas de migración, la coherencia de las versiones de las dependencias y el comportamiento en las pruebas de regresión. Los demás proyectos y los CVE individuales mencionados en la recopilación original no se han validado en este resumen de alcance limitado.

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

### Español (es)

Versiones de Spring Security y límites de soporte en el aviso de abril

1. El aviso de abril anuncia Spring Security 6.5.10, 7.0.5 y 7.1.0-RC1 y enlaza los avisos de seguridad abordados por esas versiones. Se trata de versiones históricas.

2. Indica que el soporte de código abierto para las generaciones Spring Security 5.7.x, 5.8.x, 6.3.x y 6.4.x había finalizado. El soporte comercial tiene un alcance distinto.

검토 초점: Relacione las dependencias desplegadas con cada aviso oficial y con la rama de versiones con soporte que corresponda. No elija una versión histórica solo porque aparezca en este archivo y distinga una versión candidata de una versión estable.

## Argo CD release candidate: internal mTLS and source-integrity configuration

원문: https://www.infoq.com/news/2026/06/argocd-supply-chain-security/

검토 기준: 영어 보강본 7067e48d153e8525, 2026-10-25T12:40:05+00:00

### 영어 기준본

1. The official Argo CD v3.5.0-rc1 page labels this artifact a pre-release and lists mTLS support in the repo-server. That supports describing a release-candidate capability, not claiming that every installation has mTLS enforced.

> v3.5.0-rc1 Pre-release

근거: https://github.com/argoproj/argo-cd/releases/tag/v3.5.0-rc1

> feat: adds mTLS support in repo-server

근거: https://github.com/argoproj/argo-cd/releases/tag/v3.5.0-rc1

2. The same changelog lists CLI support for Source Integrity configuration and an exposed ApplicationSet UI. This brief does not assert that signature verification first appeared in this release or that earlier internal traffic was always unencrypted.

> feat(cli): Add support for Source Integrity configuration

근거: https://github.com/argoproj/argo-cd/releases/tag/v3.5.0-rc1

> feat: expose Appset UI and fix pie chart summary

근거: https://github.com/argoproj/argo-cd/releases/tag/v3.5.0-rc1

검토 초점: The linked official blog could not be collected; this narrower draft uses the project’s release artifact. Review upgrade notes, certificates, trust roots and the target version’s integrity settings before rollout. It is not a claim that the candidate remains the newest version.

### Español (es)

Argo CD en versión candidata: mTLS interno y configuración de integridad del código fuente

1. La página oficial de Argo CD v3.5.0-rc1 identifica este artefacto como una versión preliminar e incluye soporte de mTLS en repo-server. Esto permite describir una capacidad de la versión candidata, no afirmar que todas las instalaciones exijan mTLS.

2. El mismo registro de cambios incluye soporte en la CLI para configurar Source Integrity y el acceso a la interfaz de ApplicationSet. Este resumen no afirma que la verificación de firmas apareciera por primera vez en esta versión ni que el tráfico interno anterior siempre circulara sin cifrar.

검토 초점: No se pudo obtener el artículo enlazado del blog oficial; este borrador de alcance más limitado utiliza el artefacto de lanzamiento del proyecto. Antes de la implantación, revise las notas de actualización, los certificados, las raíces de confianza y los ajustes de integridad de la versión de destino. No se afirma que esta versión candidata siga siendo la más reciente.

## Kubernetes 1.36: stable admission mutation and pod user namespaces

원문: https://www.infoq.com/news/2026/05/kubernetes-1-36-released/

검토 기준: 영어 보강본 fecc68bc1f0f9da3, 2026-10-25T06:31:18+00:00

### 영어 기준본

1. The Kubernetes 1.36 release team describes MutatingAdmissionPolicies as graduating to Stable. This is a feature maturity statement for that release.

> graduation of MutatingAdmissionPolicies to Stable.

근거: https://kubernetes.io/blog/2026/04/22/kubernetes-v1-36-release/

2. The same release describes user namespace support for pods as graduating to Stable; it does not establish that every existing cluster is configured to use it.

> support for User Namespaces graduates to Stable.

근거: https://kubernetes.io/blog/2026/04/22/kubernetes-v1-36-release/

검토 초점: Check control-plane version, operating system, container runtime and workload configuration separately. Review migration and compatibility conditions before replacing admission webhooks or enabling user namespaces.

### Español (es)

Kubernetes 1.36: mutación de admisión y espacios de nombres de usuario para pods en estado estable

1. El equipo de lanzamiento de Kubernetes 1.36 describe el paso de MutatingAdmissionPolicies al estado estable. Es una declaración sobre la madurez de esa función en dicha versión.

2. La misma versión describe el paso del soporte de espacios de nombres de usuario para pods al estado estable; esto no demuestra que todos los clústeres existentes estén configurados para utilizarlo.

검토 초점: Compruebe por separado la versión del plano de control, el sistema operativo, el entorno de ejecución de contenedores y la configuración de las cargas de trabajo. Revise las condiciones de migración y compatibilidad antes de sustituir los webhooks de admisión o activar los espacios de nombres de usuario.

## TeamCity advisory separates on-premises and cloud exposure

원문: https://blog.jetbrains.com/teamcity/2026/05/cve-2026-44413/

검토 기준: 영어 보강본 6944923e55b6bbd0, 2026-10-25T06:06:33+00:00

### 영어 기준본

1. JetBrains describes CVE-2026-44413 as a post-authentication TeamCity On-Premises issue affecting versions through 2025.11.4 and fixed in 2026.1. These are the versions in the historical advisory.

> assigned the CVE identifier CVE-2026-44413.

근거: https://blog.jetbrains.com/teamcity/2026/05/cve-2026-44413/

> versions through 2025.11.4.

근거: https://blog.jetbrains.com/teamcity/2026/05/cve-2026-44413/

> fixed in version 2026.1.

근거: https://blog.jetbrains.com/teamcity/2026/05/cve-2026-44413/

2. The vendor states that TeamCity Cloud is not affected and requires no action for this issue.

> TeamCity Cloud is not affected and requires no action.

근거: https://blog.jetbrains.com/teamcity/2026/05/cve-2026-44413/

검토 초점: Match deployment type and installed version to the vendor advisory. Confirm a supported patched release or applicable patch plugin and its activation requirements; the archive is not a recommendation to install an old version.

### Español (es)

El aviso de TeamCity distingue la exposición de On-Premises y Cloud

1. JetBrains describe CVE-2026-44413 como un problema de TeamCity On-Premises que requiere autenticación previa, afecta a versiones hasta la 2025.11.4 y está corregido en la 2026.1. Son las versiones indicadas en el aviso histórico.

2. El proveedor declara que TeamCity Cloud no está afectado y no requiere ninguna acción por este problema.

검토 초점: Compare el tipo de despliegue y la versión instalada con el aviso del proveedor. Confirme una versión corregida con soporte o un complemento de parche aplicable y sus requisitos de activación; este archivo no recomienda instalar una versión antigua.

## NetScaler protection requires patching and origin controls

원문: https://blog.cloudflare.com/protect-your-netscaler-gateway/

검토 기준: 영어 보강본 72477d086944244f, 2026-10-25T05:21:13+00:00

### 영어 기준본

1. Cloudflare starts its NetScaler guidance by telling affected customers to patch their gateway before considering additional protective layers.

> If you’re a NetScaler customer and you haven’t patched your instance

근거: https://blog.cloudflare.com/protect-your-netscaler-gateway/

2. The article warns that direct access to the original address or an alternate hostname can bypass the front-end Access controls.

> they can avoid the controls placed in front of it.

근거: https://blog.cloudflare.com/protect-your-netscaler-gateway/

3. Protection of the web authentication path does not automatically cover DTLS-enabled gateway listeners.

> including DTLS-enabled listeners.

근거: https://blog.cloudflare.com/protect-your-netscaler-gateway/

검토 초점: Inventory every exposed listener and alternate origin route. Review patch status, authentication policy and origin restrictions as separate controls; this draft does not claim that a DNS change or WAF alone closes the exposure.

### Español (es)

La protección de NetScaler requiere parches y controles sobre el origen

1. Cloudflare comienza su guía de NetScaler indicando a los clientes afectados que apliquen el parche a su gateway antes de considerar capas de protección adicionales.

2. El artículo advierte que el acceso directo a la dirección de origen o a un nombre de host alternativo puede eludir los controles de Access situados delante.

3. La protección de la ruta de autenticación web no cubre automáticamente los listeners del gateway que tienen DTLS activado.

검토 초점: Haga un inventario de todos los listeners expuestos y de las rutas alternativas al origen. Revise por separado el estado de los parches, la política de autenticación y las restricciones del origen; este borrador no afirma que un cambio de DNS o un WAF por sí solos eliminen la exposición.

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

### Español (es)

Reglas de respuesta del WAF de Cloudflare: acciones y restricciones sobre el cuerpo

1. El WAF de Cloudflare permite crear hasta 3 reglas de respuesta personalizadas compatibles con las acciones Log y Block.

2. El anuncio indica expresamente que todavía no se pueden crear reglas personalizadas sobre el cuerpo de la respuesta.

검토 초점: Al evaluar la cobertura, distinga las detecciones gestionadas de las reglas de respuesta creadas por el cliente. Este artículo conservado había desaparecido del listado anterior después de que un resumen de noticias más reciente sustituyera la página; su renovación sigue requiriendo una revisión explícita.

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

### Español (es)

Cloudflare Security Overview distingue la prioridad del riesgo de la visibilidad

1. Cloudflare describe un panel Security Overview que ordena los elementos por criticidad y permite filtrar información como la actividad sospechosa o las configuraciones inseguras.

2. En el lanzamiento, el artículo describe una experiencia a nivel de dominio y sitúa la agregación a nivel de cuenta en la hoja de ruta. Esto no demuestra que la vista de toda la cuenta ya estuviera disponible.

검토 초점: Revise qué se observa realmente y qué controles están activados antes de considerar un panel como prueba de protección. Distinga una función disponible de una declaración de hoja de ruta y confirme por separado la disponibilidad actual a nivel de cuenta.

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

### Español (es)

El contexto de ejecución de Dynatrace ayuda a priorizar las alertas de GitHub

1. El aviso de GitHub de abril describe el contexto de ejecución de Dynatrace para priorizar alertas de seguridad según los artefactos desplegados y el riesgo en tiempo de ejecución en Kubernetes.

2. El aviso indica que la función está disponible de forma general para los clientes de GitHub Enterprise Cloud. Esa declaración histórica de disponibilidad no afirma que todos los planes de GitHub la incluyan.

검토 초점: Revise la correspondencia entre repositorios y contenedores y la cobertura en tiempo de ejecución antes de considerar una lista de alertas filtrada como un inventario completo. Confirme por separado los requisitos actuales de integración y del plan.

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

### Español (es)

Las evaluaciones de organizaciones de GitHub resumen los riesgos de seguridad del código

1. GitHub anunció una evaluación gratuita de riesgos de Code Security que los administradores de organizaciones y los responsables de seguridad pueden ejecutar para su organización.

2. La evaluación resume las vulnerabilidades por gravedad, tipo de regla y lenguaje de programación, lo que ayuda a priorizar los hallazgos comunicados.

검토 초점: Compruebe el alcance de la evaluación y la cobertura de los repositorios antes de interpretar el informe como una auditoría de seguridad completa. Las correcciones sugeridas siguen requiriendo revisión del código y las pruebas adecuadas.

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

### Español (es)

BadHost: autorización basada en rutas de Starlette y condiciones del proxy

1. Los investigadores explican que Starlette reconstruía una URL a partir de una cabecera Host sin validar, mientras que el enrutamiento utilizaba la ruta real de la solicitud. Por tanto, la autorización basada en la ruta reconstruida podía no coincidir con el endpoint al que se dirigía la solicitud.

2. El aviso de los investigadores identifica como afectadas las versiones de Starlette >= 0.8.3 y < 1.0.1, y señala la 1.0.1 como corregida. La aplicabilidad sigue dependiendo de las decisiones de seguridad basadas en rutas de la aplicación.

후속 확인:

- En el momento de la revisión, el aviso del mantenedor indica que un proxy o balanceador de carga solo mitiga el problema si rechaza o normaliza las cabeceras Host malformadas antes de reenviarlas y si la aplicación no confía en cabeceras de host controladas por un atacante en otros puntos.

검토 초점: Inspeccione el middleware de autorización, las versiones resueltas de las dependencias y la confianza en las cabeceras reenviadas. La mera presencia de un proxy no basta; pruebe la configuración real de entrada. No se realizó ningún experimento de explotación para este borrador.

## eMudhra incident: audit application trust as well as client updates

원문: https://blog.cloudflare.com/emudhra-certificate-compromise/

검토 기준: 영어 보강본 c78cf468160e1a45, 2026-10-25T05:21:13+00:00

### 영어 기준본

1. Cloudflare instructed Tunnel customers to upgrade cloudflared to 2026.10.2 and redeploy fixed container images where applicable. This is the version in the incident notice, not a claim about the latest version.

> Upgrade to 2026.10.2 .

근거: https://blog.cloudflare.com/emudhra-certificate-compromise/

2. The notice warns that updating an SDK alone may leave the underlying certificate-verification policy unchanged.

> Updating the SDK alone may not change the underlying policy.

근거: https://blog.cloudflare.com/emudhra-certificate-compromise/

3. Cloudflare warns against resolving certificate errors by disabling verification.

> not resolve these errors by disabling verification

근거: https://blog.cloudflare.com/emudhra-certificate-compromise/

검토 초점: Trace which HTTP library, runtime and trust store each application actually uses. A successful browser request is not sufficient evidence that every application path is protected; validate the relevant clients without disabling verification.

### Español (es)

Incidente de eMudhra: revise la confianza de la aplicación además de actualizar los clientes

1. Cloudflare indicó a sus clientes de Tunnel que actualizaran cloudflared a 2026.10.2 y volvieran a desplegar las imágenes de contenedor corregidas cuando correspondiera. Es la versión del aviso del incidente, no una afirmación sobre la versión más reciente.

2. El aviso advierte que actualizar únicamente un SDK puede dejar sin cambios la política subyacente de verificación de certificados.

3. Cloudflare advierte que no se deben resolver los errores de certificados desactivando la verificación.

검토 초점: Identifique qué biblioteca HTTP, entorno de ejecución y almacén de certificados de confianza utiliza realmente cada aplicación. Una solicitud correcta desde el navegador no demuestra por sí sola que todas las rutas de las aplicaciones estén protegidas; valide los clientes pertinentes sin desactivar la verificación.

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

### Español (es)

CNCF y Kusari ofrecen herramientas de cadena de suministro a los mantenedores de proyectos

1. El anuncio alojado por CNCF indica que los proyectos de CNCF reciben acceso gratuito a Kusari Inspector, descrito como una herramienta de revisión de código y gestión de dependencias basada en IA.

2. El anuncio incluye GUAC, in-toto/Witness y OpenVEX entre los proyectos que adoptan la herramienta. Es una lista de adopción comunicada, no una prueba independiente de que se hayan eliminado todas las vulnerabilidades.

검토 초점: Revise los requisitos de acceso, el tratamiento de los datos y la cobertura de las dependencias antes de conectar un repositorio. Mida los hallazgos que permiten actuar y los falsos positivos en el proyecto, en lugar de dar por hecho el beneficio solo por adoptar la herramienta.

