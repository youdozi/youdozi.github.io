---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2026-11-01-ai-agent-permission-boundaries",
  "routeSlug": "2026-11-01-ai-agent-permission-boundaries",
  "kind": "post",
  "title": "Permisos de agentes de IA: limitar el impacto de acciones inesperadas",
  "description": "Separe los permisos de archivos, comandos, red y cuentas del agente de IA. Alcance de las aprobaciones y control de la elusión administrativa con un ejemplo ejecutable.",
  "categories": [
    "security"
  ],
  "tags": [
    "ai-agent",
    "permissions",
    "least-privilege",
    "sandbox",
    "approval",
    "security"
  ],
  "sourcePath": "src/content/posts/en/2026-11-01-ai-agent-permission-boundaries.md",
  "sourceSha256": "9610960800eb800a78e728fcc84d5cf2a790de1f6b051fe4a8ebb3dfdaec554b",
  "draftSha256": "78da5e752841263efbfe44d6b7fd4b7e51cb7e033e0c102db023daf32fa6c52b",
  "manifestPath": ".pipeline/technical-translations/batch-132/manifest.json",
  "manifestSha256": "9061c67686c9ea3bd8d21799f4c265ee716fee50940f1b6fc38c28a67de01dee",
  "publishedAt": "2026-11-02T03:04:44.245Z",
  "updatedAt": "2026-11-02T03:04:44.245Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 132,
    "approvedAt": "2026-11-02T03:04:44.245Z",
    "basis": "User requested completing missing multilingual technical posts, review, verification and deployment, then instructed continuing the next task on 2026-11-02, with standing blog PR merge/publication authorization. Human approval denotes user publication authorization; linguistic review is AI, not human/native review."
  }
}
---

**Para reducir incidentes por comportamientos inesperados de un agente de IA, limite las acciones ejecutables y los recursos accesibles y defina límites concretos de aprobación para operaciones de gran impacto.** Una edición equivocada o una interpretación demasiado amplia de una solicitud no deberían provocar de inmediato la eliminación de datos de producción, transferencias externas o la elusión de reglas de protección. El diseño de permisos no elimina todos los errores, pero puede reducir su alcance.

Aquí los permisos incluyen el entorno de ejecución y las cuentas de servicios externos, además de la lista de herramientas visibles para el agente. [La descripción de Excessive Agency de OWASP](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/) identifica el exceso de funciones, permisos y autonomía como riesgos principales y recomienda privilegios mínimos y aprobación para acciones de gran impacto.

## Cuando «completar la tarea» se convierte en una autoridad mayor

Considere este escenario hipotético de diseño. Un usuario solicita una publicación y CI pasa, pero el repositorio exige una aprobación de PR aparte. Si el agente interpreta ese requisito como un obstáculo corriente y fusiona con privilegios de administrador, se confunden la publicación y una excepción a las reglas de protección.

Hay dos preguntas: **¿Está autorizado el agente a publicar este artefacto y también a hacer una excepción a las reglas de protección?** Ampliar automáticamente una solicitud normal de publicación hasta permitir la elusión administrativa puede provocar cambios inesperados. Según la configuración, la protección de ramas de GitHub puede eximir a administradores o actores con permisos de elusión; revise tanto las reglas como la capacidad de la cuenta ejecutora para eludirlas. [Ramas protegidas y configuración de elusión de GitHub](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)

Tras una denegación de permisos, use la política para determinar si otro comando, API o identidad puede intentar el mismo efecto. Las acciones bloqueadas por falta de aprobación o permisos insuficientes deben seguir el proceso de espera o excepción de la política. Distinga los reintentos por fallos transitorios del servicio de las respuestas a denegaciones de permisos.

## Las instrucciones y los controles obligatorios tienen funciones distintas

Una instrucción como «no modificar la base de datos de producción» en `AGENTS.md` o un prompt comunica el alcance. Dar a la identidad de base de datos solo privilegios de lectura también permite que la base rechace una escritura generada. Las instrucciones orientan el comportamiento del modelo; los controles del entorno y la autorización del servicio limitan sus posibles efectos.

| Capa | Qué limitar | Ejemplo de diseño |
| --- | --- | --- |
| Instrucciones de tarea | Alcance y condiciones de parada | Permitir borradores; definir la publicación y la elusión administrativa como acciones separadas |
| Entorno de ejecución | Archivos, procesos y acceso a red | Permitir escrituras solo en la carpeta de trabajo, omitir secretos de producción y conectar solo con destinos necesarios |
| Pasarela de herramientas | Combinaciones de acción y argumentos | Comprobar sitio y hash del artefacto para `publish`; no exponer ejecución arbitraria de comandos |
| Servicio externo | Privilegios reales de las credenciales | Usar identidades de servicio con alcance limitado y reglas de protección para repositorios, bases de datos y clústeres |

Una pasarela deja abierta una ruta alternativa si el proceso del agente conserva un token de administrador y puede llamar a las API directamente. Un diseño posible consiste en guardar las credenciales de ejecución en un servicio restringido al que el agente envía solicitudes estructuradas. El agente tampoco debe poder modificar los archivos de política ni el almacén de aprobaciones.

## Limite los efectos, además de los nombres de comandos

Una regla que permite «comandos de prueba» no protege por sí sola el entorno de ejecución. Las pruebas, compilaciones e instalaciones de dependencias pueden ejecutar código del repositorio o de paquetes. No inyecte credenciales de producción en un espacio que ejecuta código no confiable; proporcione solo los archivos, acceso a red y recursos necesarios. Incluso con contenedores, revise el límite de aislamiento si se montan rutas sensibles del host o el socket de Docker.

Las operaciones de lectura también necesitan límites de recursos y datos. Leer un secreto y transmitirlo fuera o incluir datos sensibles en una cadena de consulta puede causar un incidente sin modificar los datos originales. Las instrucciones insertadas en documentos externos, páginas web o respuestas de herramientas no son aprobaciones de tarea. [La guía de inyección de prompts de OWASP](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) aborda la inyección indirecta mediante contenido externo.

Un flujo de GitHub Actions puede declarar solo los privilegios de token que necesita. Este es un fragmento de configuración:

```yaml
permissions:
  contents: read
```

Controla el `GITHUB_TOKEN` correspondiente. Los permisos no especificados pasan a `none`, pero la declaración no limita un PAT, una clave de nube o una credencial de base de datos suministrados por separado. Inspeccione también las credenciales realmente disponibles para el ejecutor del agente. [Sintaxis de permisos de GitHub Actions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#permissions)

En Kubernetes, revise por separado los privilegios `escalate`, `bind` e `impersonate` de una identidad de tarea normal. Pueden permitir adquirir otros privilegios o actuar como otra identidad. [Guía de RBAC de Kubernetes](https://kubernetes.io/docs/concepts/security/rbac-good-practices/)

## Vincule la aprobación al artefacto y al destino

En vez de mostrar solo «¿Continuar?», permita revisar la acción, el destino y el cambio propuesto. Una aprobación de publicación puede vincular el ID del sitio, el hash del artefacto revisado, la identidad ejecutora, el vencimiento y un ID de aprobación de un solo uso. Si el artículo o la imagen de despliegue cambian después, determine si el nuevo artefacto sigue dentro del alcance aprobado.

No toda lectura o edición de borrador necesita aprobación aparte. Permita continuar dentro del alcance ya autorizado y deténgase al cruzarlo o al llegar a un efecto que requiera aprobación adicional según la política. Esto reduce la fatiga de aprobación y conserva los límites de publicación, eliminación, transferencia externa y excepciones administrativas. Un procedimiento operativo que realmente necesite una excepción administrativa debe usar una identidad, autoridad y ruta de auditoría distintas de las del ejecutor normal.

## Ejemplo ejecutable: una aprobación no autoriza acciones fuera de la política

El siguiente es un **ejemplo de autorización en un único proceso sin efectos externos**. Valores como `repo:demo` son ID lógicos predefinidos de recursos, no rutas ni URL reales. La política permite `read` y `edit` de borrador; `publish` requiere una aprobación válida para la misma identidad y solicitud. La elusión administrativa no figura en la política y se deniega aunque exista un objeto de aprobación.

![Comprobación del alcance de la política y luego de la presencia, identidad, artefacto, vencimiento y reutilización de la aprobación antes de permitir publicar](/assets/diagrams/technical/es-2026-11-01-ai-agent-permission-boundaries.svg)

El diagrama muestra la ruta `publish` que requiere aprobación. Omite la autorización inmediata de `read` y `edit` de borradores del código. Detenerse en cualquier comprobación impide las etapas siguientes y la publicación real.

Guarde el código como `permission_gate.py` y ejecute `python3 permission_gate.py` con Python 3.10 o posterior. No necesita red, credenciales ni paquetes adicionales.

```python
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Request:
    action: str
    target: str
    artifact: str


@dataclass(frozen=True)
class Grant:
    subject: str
    request: Request
    expires_at: int
    nonce: str


class Gate:
    def __init__(self):
        self.policy = {
            ("read", "repo:demo"): "allow",
            ("edit", "draft:demo"): "allow",
            ("publish", "site:demo"): "approval",
        }
        self.used = set()

    def check(self, subject, request, grant, now):
        mode = self.policy.get((request.action, request.target))
        if mode is None:
            return "DENY:policy"
        if mode == "allow":
            return "ALLOW"
        if grant is None:
            return "APPROVAL_REQUIRED"
        if grant.subject != subject or grant.request != request:
            return "DENY:scope"
        if now >= grant.expires_at:
            return "DENY:expired"
        if grant.nonce in self.used:
            return "DENY:replay"
        self.used.add(grant.nonce)
        return "ALLOW"


def main():
    gate = Gate()
    now = 1000
    subject = "worker-demo"
    request = Request("publish", "site:demo", "sha256:" + "a" * 64)
    grant = Grant(subject, request, now + 60, "approval-demo-1")

    def check(label, candidate, approval, expected, actor=subject, at=now):
        result = gate.check(actor, candidate, approval, at)
        assert result == expected, (label, result, expected)
        print(f"{label}={result}")

    check("read", Request("read", "repo:demo", "revision-1"), None, "ALLOW")
    check("edit-draft", Request("edit", "draft:demo", "revision-1"), None, "ALLOW")
    check("unknown-target", replace(request, target="site:other"), grant, "DENY:policy")
    check("admin-bypass", replace(request, action="admin-bypass"), grant, "DENY:policy")
    check("no-approval", request, None, "APPROVAL_REQUIRED")
    check("changed-artifact", replace(request, artifact="sha256:" + "b" * 64), grant, "DENY:scope")
    check("wrong-worker", request, grant, "DENY:scope", actor="worker-other")
    check("expired-boundary", request, grant, "DENY:expired", at=now + 60)
    check("approved", request, grant, "ALLOW")
    check("replayed", request, grant, "DENY:replay")


if __name__ == "__main__":
    main()
```

Esta salida se produjo con Python 3.13.0. Se comprobaron los valores de retorno de estos 10 escenarios sintéticos:

```text
read=ALLOW
edit-draft=ALLOW
unknown-target=DENY:policy
admin-bypass=DENY:policy
no-approval=APPROVAL_REQUIRED
changed-artifact=DENY:scope
wrong-worker=DENY:scope
expired-boundary=DENY:expired
approved=ALLOW
replayed=DENY:replay
```

`Grant` presupone información emitida y autenticada por un servicio de aprobaciones. Este ejemplo no verifica la aprobación ni la identidad ejecutora, la autoridad, las firmas o el esquema de entrada; las anotaciones de tipo de dataclass no sustituyen la validación en ejecución. No convierta JSON generado por el modelo directamente en un `Grant` aceptado. `now=1000`, 60 segundos, los hashes y el ID de aprobación son valores sintéticos de demostración, no recomendaciones de producción.

Un ejecutor real debe cargar las aprobaciones desde su almacén y calcular por sí mismo el hash del artefacto. Comparar solo un hash aportado por el agente le permite proporcionar un valor distinto del contenido real. Verifique política, hora, identidad ejecutora y destino desde un contexto de ejecución confiable y limite rutas y credenciales para que el agente no pueda omitir esta función y llamar directamente a la API externa.

El conjunto `used` reside en memoria del proceso, por lo que no impide reutilizaciones tras reinicios o entre varios ejecutores. Un servicio real necesita consumo atómico de aprobaciones, revocación, revalidación de política y destino justo antes de ejecutar e idempotencia de acciones. Los reintentos tras consumir la aprobación y fallar la ejecución también deben usar el mismo ID de operación y el resultado real. Este código devuelve `ALLOW`; no llama a una API de publicación.

## Qué comprobar primero al adoptar este diseño

Inventaríe archivos, tokens e identidades accesibles y las API que el agente puede llamar realmente. Mire más allá de las herramientas conectadas explícitamente: variables de entorno de shell, credenciales del directorio personal y rutas de red. Empiece con lectura y trabajo aislado en borradores y después añada herramientas de alcance limitado para efectos de mayor impacto.

Pruebe que se rechazan publicaciones sin aprobación, cambios de artefacto posteriores, vencimiento, reutilización, otra identidad ejecutora, recursos desconocidos y solicitudes de elusión administrativa. Verifique que los mismos controles se mantienen cuando un documento externo solicita ampliar privilegios. Cierre cualquier ruta que permita al agente modificar la política o leer directamente el token del servicio ejecutor.

Conecte en los registros de auditoría el ID de solicitud, la identidad, el destino, el hash del artefacto, la política aplicada, el ID de aprobación y el resultado, excluyendo tokens y contenido sensible. Si aparece un comportamiento anómalo, deje de aceptar trabajo nuevo y revoque credenciales para limitar efectos posteriores. La revocación no deshace datos ya transmitidos ni cambios externos completados, así que prepare recuperación junto con los controles de ejecución.

Para un flujo operativo que conecta código, pruebas, despliegue, observabilidad y evidencias de base de datos, consulte [Operaciones con agentes de IA](/en/posts/2026-10-31-ai-agent-operations/).
