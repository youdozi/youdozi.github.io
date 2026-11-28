---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2026-11-28-nginx-free-subdomains",
  "routeSlug": "2026-11-28-nginx-free-subdomains",
  "kind": "post",
  "title": "Cuatro servicios de subdominios gratuitos para alojar Nginx en casa",
  "description": "Una IP doméstica que cambia, un portafolio de desarrollo y una zona DNS propia requieren distintas formas de gestionar el nombre.",
  "categories": [
    "tips"
  ],
  "tags": [
    "self-hosting",
    "nginx",
    "dns"
  ],
  "sourcePath": "src/content/posts/en/2026-11-28-nginx-free-subdomains.md",
  "sourceSha256": "d11db302c4d9595bd30ea32d7d5c2c2ec680a9c318001ba16e333085dbec5f2e",
  "draftSha256": "77fcca1ab7e7e1e0690c537bf800b07cb593a3726047d7d5d4be2bba264455f1",
  "manifestPath": ".pipeline/technical-translations/batch-1571/manifest.json",
  "manifestSha256": "bf6a83d6c439631d9c3af30e329fc60c4018ee5580ce2cd06ccd9111caf54227",
  "publishedAt": "2026-11-28T04:45:08.727Z",
  "updatedAt": "2026-11-28T04:45:08.727Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 229,
    "approvedAt": "2026-11-28T04:45:08.727Z",
    "basis": "Explicit item 157 publication approval for both item 155 and 156 follow-up guides in all nine site languages."
  }
}
---

Ya tienes Nginx en marcha en casa. ¿Qué nombre podrán escribir los visitantes? Estos servicios ofrecen subdominios gratuitos bajo un dominio del operador. Tú te encargas del servidor y del acceso desde Internet.

## ¿Se puede llegar al servidor desde otra red?

El DNS dinámico (DDNS) actualiza la IP que devuelve el DNS. La conexión depende de la línea, el router y el cortafuegos. Si tu operador usa CGNAT, puede que reenviar un puerto en tu router no baste. Si la dirección WAN está dentro de `100.64.0.0/10`, pregunta al operador si ofrece una IPv4 pública. [RFC 6598](https://www.rfc-editor.org/info/rfc6598/)

## Elige según cómo vayas a mantener el nombre

| Servicio | Gestión del nombre | Cuándo conviene |
| --- | --- | --- |
| [Duck DNS](https://www.duckdns.org/spec.jsp) | Un cliente mantiene actualizado `name.duckdns.org`. La API puede detectar IPv4 automáticamente. Para actualizar IPv6 debes indicar la dirección. | Una primera práctica con una IPv4 pública que cambia. |
| [dynv6](https://dynv6.com/) · [API](https://dynv6.com/docs/apis) | Ofrece un nombre de host y API para actualizar los registros A y AAAA y el prefijo IPv6. | IPv6 o doble pila. No ofrece un acuerdo de nivel de servicio empresarial. |
| [is-a.dev](https://github.com/is-a-dev/register#-register) | Envía una pull request en GitHub para su revisión. El equipo pide que redactes personalmente la solicitud. | Un portafolio de desarrollo. Si la IP cambia a menudo, DDNS resulta más práctico. |
| [EU.org](https://nic.eu.org/register.html) · [EU.org NS](https://nic.eu.org/top-policy.html) | Prepara los servidores de nombres autoritativos antes de solicitarlo. Tras la aprobación y la delegación NS, administras A y AAAA en tu zona. | Si quieres gestionar tus propios registros DNS. La actualización dinámica se configura por separado. |

## Comprueba el nombre elegido

![Comprobar la dirección WAN → Elegir el método de actualización → Consultar los registros DNS → Probar desde otra red](/assets/diagrams/technical/es-2026-11-28-nginx-free-subdomains.svg)

Para empezar, confirma que tienes una IPv4 pública y apunta a ella un nombre de Duck DNS. Con dig instalado, sustituye el nombre de ejemplo y consulta ambos tipos de dirección. A debería coincidir con tu dirección pública. Si publicas AAAA, prueba también la ruta IPv6 desde otra red.

```sh
dig +short name.duckdns.org A
dig +short name.duckdns.org AAAA
```

La comparación se basa en la documentación oficial. No creamos cuentas ni solicitamos subdominios.

[Práctica local con la aplicación de notas](https://youdozi.github.io/en/posts/2026-11-28-self-hosting-ai-notes/) · [Conectar Duck DNS con Nginx con ayuda de la IA: del DNS a HTTPS](https://youdozi.github.io/en/posts/2026-11-28-nginx-dns-https/)
