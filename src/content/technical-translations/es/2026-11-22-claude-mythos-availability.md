---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2026-11-22-claude-mythos-availability",
  "routeSlug": "2026-11-22-claude-mythos-availability",
  "kind": "post",
  "title": "¿Dónde puedes usar Claude Mythos 5.2? Claude Security, Claude Code y la API",
  "description": "Compara el acceso directo a Mythos 5.2, el análisis de código para Enterprise en Claude Security y la disponibilidad de Fable 5.2 en los planes de pago de Claude.",
  "categories": [
    "ai"
  ],
  "tags": [
    "claude",
    "claude-mythos",
    "claude-fable",
    "claude-security",
    "claude-code"
  ],
  "sourcePath": "src/content/posts/en/2026-11-22-claude-mythos-availability.md",
  "sourceSha256": "03f809cd5ff47c9929524f940e1ebf683dc5e75760fb062cfdb425ffbf4ff424",
  "draftSha256": "359345a7a8d907d01a27fcd29fb04672543070dbac4d947c2abf3e023b1f3ecc",
  "manifestPath": ".pipeline/technical-translations/batch-185/manifest.json",
  "manifestSha256": "3281e1d3e7c9b3abbb6c101d911dd0fcdee7dd54f7034838135f391123b6fb44",
  "publishedAt": "2026-11-23T00:19:14.218Z",
  "updatedAt": "2026-11-23T00:19:14.218Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 185,
    "approvedAt": "2026-11-23T00:19:14.218Z",
    "basis": "The site owner explicitly requested missing supported locales for the eight articles published in PRs #177–#184. This authorizes publication of the 48 editions enumerated in this batch."
  }
}
---

**El acceso directo a Claude Mythos 5.2 requiere la aprobación de un programa de verificación de Anthropic.** Las personas con un plan elegible pueden obtener Defense Access tras la aprobación de su solicitud en el Cyber Verification Program (CVP). Con Claude Enterprise, una organización puede habilitar Claude Security, que utiliza Mythos 5.2 para analizar el código. Fable 5.2 tiene disponibilidad general en los planes de pago de Claude. Los requisitos de créditos de uso varían según el plan o la licencia. Esta guía refleja la documentación pública disponible al 22 de noviembre de 2026. [Anuncio de la versión 5.2 de Anthropic](https://www.anthropic.com/claude-fable-and-mythos-5-2#availability) · [Ayuda de Claude sobre los modelos incluidos](https://support.claude.com/en/articles/15425695-covered-models) · [Cyber Verification Program](https://support.claude.com/en/articles/14604842-cyber-verification-program)

## ¿Qué opción tienes disponible?

![Para tareas generales de desarrollo, los suscriptores de pago pueden buscar Fable 5.2 en el selector de modelos. La revisión de repositorios de Enterprise se realiza con Claude Security. El acceso directo a Mythos depende de la aprobación de la cuenta y del canal utilizado.](/assets/diagrams/technical/es-2026-11-22-claude-mythos-availability.svg)

| Qué quieres hacer | Dónde buscar | Requisitos de acceso |
| --- | --- | --- |
| Usar un modelo de la versión 5.2 para programar o redactar | El selector de modelos de Claude en la web, en la aplicación de escritorio o móvil, o en Claude Code | Los planes de pago incluyen Fable 5.2. Los créditos de uso dependen del plan y de la licencia. |
| Usar Mythos para buscar problemas de seguridad en un repositorio de la empresa | Claude Security en la versión web de Claude | Beta pública de Enterprise. Tu organización debe habilitar la función y tu licencia debe incluir Claude Code. |
| Usar Mythos directamente como modelo en Claude Code o en la API de Claude | Los permisos de modelos de tu cuenta o el espacio de trabajo que utilizas para la API | Se requiere la aprobación del programa de verificación. Las personas con un plan elegible pueden solicitar Defense Access. |

**Mythos Preview** fue la versión preliminar de investigación que Anthropic ofreció en abril de 2026 a las organizaciones participantes en Project Glasswing. Anthropic presentó **Mythos 5.2** el 9 de noviembre. Si comparas información sobre la disponibilidad de Mythos, comprueba la fecha y la versión del modelo. [Anuncio de Project Glasswing](https://www.anthropic.com/project/glasswing) · [Página del modelo Claude Mythos](https://www.anthropic.com/claude/mythos)

## Dónde se usa Mythos en Enterprise

**Claude Security utiliza Mythos 5.2 para analizar repositorios.** Un equipo puede usarlo para detectar la ausencia de una comprobación de autorización en un servicio web interno y luego revisar las pruebas y la corrección propuesta. Anthropic también ofrece Claude Security a clientes de Enterprise que no forman parte del Cyber Verification Program. Cada persona necesita una licencia que incluya Claude Code. En los planes Enterprise que se facturan por licencia también es necesario habilitar los créditos de uso. Un propietario de la organización con una licencia que incluya Claude Code puede habilitar la función en `Organization settings → Claude Security`. [Anuncio del lanzamiento de Anthropic](https://www.anthropic.com/claude-fable-and-mythos-5-2) · [Requisitos de Claude Security](https://support.claude.com/en/articles/14661296-use-claude-security)

Puedes abrir un hallazgo en Claude Code para trabajar en una corrección. **El análisis y la sesión de Claude Code tienen permisos de modelos independientes.** El análisis utiliza Mythos, mientras que la sesión de Claude Code utiliza los modelos disponibles para tu cuenta. Por eso un usuario de Enterprise puede ver Claude Security aunque Mythos no aparezca en el selector de modelos del chat habitual. [Página de producto de Claude Security](https://claude.com/product/claude-security) · [Configuración de modelos en Claude Code](https://code.claude.com/docs/en/model-config)

## Cómo encontrar Fable 5.2 en un plan individual

Según Anthropic, Fable 5.2 y Mythos 5.2 comparten el mismo modelo base. Fable incorpora medidas de protección adicionales en ciberseguridad y ciencias de la vida. Con un plan individual de pago, puedes usar Fable 5.2 para tareas generales de desarrollo, como entender un repositorio o planificar una refactorización. Pro y algunas licencias estándar requieren créditos de uso desde el principio. [Anuncio de los modelos de Anthropic](https://www.anthropic.com/claude-fable-and-mythos-5-2) · [Disponibilidad de Fable por plan](https://support.claude.com/en/articles/15424964-claude-fable-models-on-your-plan)

En la web y en las aplicaciones de escritorio y móvil, busca `Fable 5.2` en el selector de modelos. Si usas Claude Code en un terminal, comprueba primero que tienes la versión **2.1.321** o posterior. Después abre `/model` en una sesión para ver los modelos que puedes seleccionar. [Ayuda de Claude sobre los planes](https://support.claude.com/en/articles/15424964-claude-fable-models-on-your-plan) · [Configuración de modelos en Claude Code](https://code.claude.com/docs/en/model-config)

```sh
claude --version
```

En la API de Claude, puedes verificar el identificador del modelo Fable con una solicitud de metadatos. El ejemplo utiliza una consola con `curl` y la clave de API del espacio de trabajo correspondiente ya configurada en `ANTHROPIC_API_KEY`. Si la solicitud tiene éxito, la respuesta debería incluir el valor `claude-fable-5-2` para `id`. El formato de la solicitud se cotejó con la referencia oficial y la sintaxis de la consola se comprobó localmente. No se probó el comportamiento de Claude con autenticación, incluidas la respuesta de metadatos y la selección del modelo. [Referencia de la API de Claude para consultar modelos](https://platform.claude.com/docs/en/api/models/retrieve)

```sh
curl --fail-with-body --silent --show-error \
  'https://api.anthropic.com/v1/models/claude-fable-5-2' \
  -H 'anthropic-version: 2026-10-21' \
  -H "Authorization: Bearer ${ANTHROPIC_API_KEY}"
```

## Cómo comprobar el acceso directo a Mythos

Según la ayuda del Cyber Verification Program, los investigadores de seguridad independientes, los responsables de proyectos de código abierto y otras personas pueden solicitar **Defense Access** en planes elegibles como Pro, Max y Ultra. Este nivel incluye Mythos 5.2 para quienes obtengan la aprobación. Una suscripción de pago por sí sola no concede acceso. Anthropic cuenta con un programa de verificación independiente para la investigación en ciencias de la vida. [Ayuda del Cyber Verification Program](https://support.claude.com/en/articles/14604842-cyber-verification-program) · [Anuncio de disponibilidad de Anthropic](https://www.anthropic.com/claude-fable-and-mythos-5-2#availability)

La documentación de la API de Claude indica que el identificador de Mythos 5.2 es `claude-mythos-5-2`. La disponibilidad depende del acceso concedido a tu cuenta u organización y del canal que utilices. El acceso a Claude y el acceso a Claude Console se administran por separado. Los permisos de la consola se aplican al espacio de trabajo asignado. Las organizaciones que utilizan un proveedor de nube también deben comprobar la cuenta vinculada y la compatibilidad del proveedor. [Guía de modelos de la API de Claude](https://platform.claude.com/docs/en/models/fable-5-2/migration-guide) · [Ayuda de Claude sobre planes, espacios de trabajo y cuentas de nube](https://support.claude.com/en/articles/14604842-cyber-verification-program)
