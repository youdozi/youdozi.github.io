---
{
  "schemaVersion": 1,
  "state": "draft",
  "language": "es",
  "translationKey": "2026-11-21-nginx4shell-http2",
  "sourcePath": "src/content/posts/en/2026-11-21-nginx4shell-http2.md",
  "sourceSha256": "51daac7a022b582074f762f0ce0c07d617f4af8535152688b060235117af16c2",
  "title": "Guía de respuesta a Nginx4Shell — versiones de NGINX afectadas en HTTP/2 y parches",
  "description": "Condiciones de exposición, versiones corregidas y mitigación temporal para las vulnerabilidades HTTP/2 de NGINX CVE-2026-123007 y CVE-2026-123633. El ejemplo en Python ayuda a priorizar los parches."
}
---

**Empieza por comprobar qué puntos de escucha de NGINX aceptan HTTP/2.** Divulgadas el 18 de noviembre de 2026, las vulnerabilidades CVE-2026-123007 y CVE-2026-123633 pueden provocar corrupción de memoria durante el procesamiento de HTTP/2. Según las condiciones, un proceso trabajador puede fallar o puede ejecutarse código de forma remota con sus privilegios. Las versiones corregidas de NGINX Open Source son stable **1.30.7** y mainline **1.31.9**. Para los paquetes de una distribución, NGINX Plus y los productos Ingress, consulta la versión corregida del proveedor correspondiente. [Avisos de seguridad de NGINX](https://nginx.org/en/security_advisories.html) · [Actualización de seguridad de F5 del 18 de noviembre](https://my.f5.com/s/article/K000164058)

## ¿Qué entornos están afectados?

**Nginx4Shell** se usa aquí como alias de búsqueda. Registra ambos identificadores CVE por separado en las solicitudes de cambio y en el inventario para cotejar el aviso y el estado del parche de cada producto.

| CVE | Condiciones y consecuencias | Versiones afectadas de NGINX Open Source |
| --- | --- | --- |
| CVE-2026-123007 | Puede producirse corrupción de memoria cuando NGINX procesa tráfico HTTP/2 de clientes. Comprueba también los servidores que solo ofrecen contenido estático si tienen HTTP/2 habilitado. | 1.9.5–1.30.6 y 1.31.0–1.31.8 |
| CVE-2026-123633 | Al reenviar peticiones HTTP/2 de clientes a un servidor upstream, NGINX puede acceder a memoria ya liberada en determinadas condiciones. Revisa primero los proxies inversos con HTTP/2. | 1.19.7–1.30.6 y 1.31.0–1.31.8 |

La versión estable 1.30.7 corrige ambas vulnerabilidades. Aunque su numeración sea superior a la de 1.30.7, **la versión 1.31.8 sigue afectada**. La actualización también incluye correcciones para HTTP/3, el resolvedor DNS y el proxy de correo. Sigue preparando el parche del producto si cambias la configuración de HTTP/2 como medida temporal. [Anuncios de versiones de NGINX](https://nginx.org/news.html) · [F5 CVE-2026-123007](https://my.f5.com/s/article/K000163926) · [F5 CVE-2026-123633](https://my.f5.com/s/article/K000163928) · [Aviso de CERT-EU](https://cert.europa.eu/publications/security-advisories/2026-022)

## Comprueba el producto en ejecución y la ruta HTTP/2

1. **Identifica el origen del binario en ejecución.** En una máquina virtual, comprueba el ejecutable y el paquete que usa el servicio. En un contenedor, comprueba la imagen en ejecución y su digest. Ejecuta `nginx -V` en ese entorno para ver la versión y las opciones de compilación. Algunas distribuciones, como Ubuntu 24.04 LTS, trasladan correcciones a versiones existentes. El aviso de Ubuntu indica que el paquete corregido para esa versión es `1.24.0-2ubuntu7.20`. [Opciones de línea de comandos de NGINX](https://nginx.org/en/docs/switches.html) · [Ubuntu USN-9159-1](https://ubuntu.com/security/notices/USN-9159-1)
2. **Comprueba el tramo del cliente o del proxy frontal a NGINX.** El navegador puede usar HTTP/2 con la CDN mientras la CDN llega al origen NGINX mediante otro protocolo. Consulta la configuración que utiliza el servicio con `nginx -T`. Revisa los bloques `http` y `server`, los archivos incluidos y la sintaxis utilizada. La configuración completa puede contener direcciones internas y secretos, así que revísala en un entorno autorizado. [Documentación del módulo HTTP/2 de NGINX](https://nginx.org/en/docs/http/ngx_http_v2_module.html)
3. **Aplica el parche primero a las instancias afectadas que aceptan peticiones externas.** Tras el despliegue, verifica que los procesos usan el nuevo binario o la nueva imagen. Ejecuta `nginx -t` para verificar la configuración. Comprueba también las peticiones HTTP normales, el estado de los servidores upstream, las tasas de error y los reinicios de procesos trabajadores. En un clúster, comprueba si quedan réplicas que usan la imagen anterior. [Aviso de CERT-EU](https://cert.europa.eu/publications/security-advisories/2026-022)

Si no puedes actualizar de inmediato, desactivar HTTP/2 en los puntos de escucha afectados puede reducir la exposición a ambas CVE. Con la sintaxis actual, usa `http2 off;`. Con la anterior, elimina la opción `http2` de `listen`. Antes del cambio, revisa las rutas que dependen de HTTP/2, como gRPC. Después, comprueba las conexiones reales a esos puntos de escucha y las peticiones normales del servicio. [Documentación de configuración de HTTP/2 en NGINX](https://nginx.org/en/docs/http/ngx_http_v2_module.html) · [Guía de mitigación de Red Hat](https://access.redhat.com/security/vulnerabilities/RHSB-2026-019)

## Ejercicio — fija la prioridad del parche con tus comprobaciones

El ejemplo acepta **el origen del producto, su versión y el estado de HTTP/2** que haya verificado el equipo de operaciones. Funciona con Python 3.10 o posterior y solo usa la biblioteca estándar. Con los datos de los pasos anteriores puedes decidir qué parches aplicar primero.

![Introduce el origen y la versión del producto. Para los paquetes de distribución y los productos de un proveedor, consulta el aviso correspondiente. Si la versión original de NGINX está en el intervalo afectado, usa el estado de HTTP/2 para priorizar el parche o revisar la configuración.](2026-11-21-nginx4shell-http2.svg)

Guarda el script como `nginx_http2_triage.py`. Usa `upstream` únicamente para las versiones originales Open Source publicadas por el proyecto NGINX. Usa `vendor` para paquetes con correcciones trasladadas a versiones anteriores o imágenes de proveedores. Si aún no has comprobado el origen del producto o la configuración del punto de escucha, indica `unknown` en el campo correspondiente.

```python
import argparse
import re


def upstream_version(value: str) -> tuple[int, int, int]:
    if not re.fullmatch(r"[0-9]{1,4}\.[0-9]{1,4}\.[0-9]{1,4}", value):
        raise argparse.ArgumentTypeError("use an upstream version such as 1.30.7")
    major, minor, patch = map(int, value.split("."))
    return major, minor, patch


def triage(origin: str, value: str, http2: str) -> str:
    if origin != "upstream":
        return "CHECK_VENDOR_ADVISORY"

    version = upstream_version(value)
    if version[0] != 1 or version > (1, 31, 9):
        return "CHECK_CURRENT_ADVISORY"
    if (1, 30, 7) <= version < (1, 31, 0) or version == (1, 31, 9):
        return "UPSTREAM_FIX_VERSION"

    affected = [
        cve
        for cve, first_version in (
            ("CVE-2026-123007", (1, 9, 5)),
            ("CVE-2026-123633", (1, 19, 7)),
        )
        if version >= first_version
    ]
    if not affected:
        return "OUTSIDE_LISTED_RANGES"

    action = {
        "on": "PRIORITIZE_PATCH",
        "off": "PATCH_STILL_REQUIRED",
        "unknown": "VERIFY_HTTP2_AND_PATCH",
    }[http2]
    return f"{action} {' '.join(affected)}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("origin", choices=("upstream", "vendor", "unknown"))
    parser.add_argument("version")
    parser.add_argument("http2", choices=("on", "off", "unknown"))
    args = parser.parse_args()
    try:
        print(triage(args.origin, args.version, args.http2))
    except argparse.ArgumentTypeError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
```

```bash
python3 nginx_http2_triage.py upstream 1.31.8 on
python3 nginx_http2_triage.py upstream 1.30.7 on
python3 nginx_http2_triage.py upstream 1.19.6 unknown
python3 nginx_http2_triage.py vendor 1.24.0-2ubuntu7.20 on
```

Al ejecutar los comandos anteriores con Python 3.13.0 se obtuvo esta salida.

```text
PRIORITIZE_PATCH CVE-2026-123007 CVE-2026-123633
UPSTREAM_FIX_VERSION
VERIFY_HTTP2_AND_PATCH CVE-2026-123007
CHECK_VENDOR_ADVISORY
```

La lista de CVE indica **qué vulnerabilidades podrían afectar a la versión**. Para saber si se cumple la condición relativa al servidor upstream de CVE-2026-123633, comprueba la configuración real del punto de escucha. El ejemplo clasifica los datos introducidos según los intervalos publicados. La configuración de producción y el estado de los parches se verifican por separado.
