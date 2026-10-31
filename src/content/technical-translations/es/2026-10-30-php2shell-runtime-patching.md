---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2026-10-30-php2shell-runtime-patching",
  "routeSlug": "2026-10-30-php2shell-runtime-patching",
  "kind": "post",
  "title": "Respuesta a PHP2Shell: verificar la compilación corregida de PHP y los procesos web",
  "description": "Distingue las correcciones originales de PHP2Shell de las adaptaciones del proveedor y verifica los procesos PHP que atienden solicitudes. Controla por separado el aviso posterior sobre sesiones y la recompilación de Brotli para Windows.",
  "categories": [
    "security"
  ],
  "tags": [
    "php2shell",
    "php",
    "security"
  ],
  "sourcePath": "src/content/posts/en/2026-10-30-php2shell-runtime-patching.md",
  "sourceSha256": "f4aa334e127facad6b41b0eb19920466d78f78d25c9065c6faf85c584c63115c",
  "draftSha256": "de46500dd70706bb22ce67289c3af9d28243e062d3aca20fb3328b3b5f51faa9",
  "manifestPath": ".pipeline/technical-translations/batch-078/manifest.json",
  "manifestSha256": "e685b2de5dafd8cfff8e8e996fa2b09613becb072bdd575b58b9eca9651474a3",
  "publishedAt": "2026-10-31T02:49:44.828Z",
  "updatedAt": "2026-10-31T02:49:44.828Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 118,
    "approvedAt": "2026-10-31T02:49:44.828Z",
    "basis": "2026-10-31 user instruction “진행해줘” immediately following delivery of the reviewed 72 complete translations in PR #118; interpreted as authorization to publish exactly batch-078 in all six languages. Separate AI language review is recorded in the manifest; this does not claim a human line-by-line review. Excludes the older 120 technical drafts and 318 pending news translations."
  }
}
---
La corrección de PHP2Shell no termina al actualizar el CMS o un complemento. Obtén una compilación de PHP que corrija [CVE-2026-109618](https://github.com/php/php-src/security/advisories/GHSA-w8hw-w9fx-j79w) y [CVE-2026-109619](https://github.com/php/php-src/security/advisories/GHSA-6wmf-4rv5-p3rp), y verifica después que la utilice cada proceso que atiende solicitudes web. El comando `php -v` de una terminal solo informa sobre el CLI seleccionado en esa terminal.

## ¿A qué afecta PHP2Shell?

Los dos CVE afectan al estado de las solicitudes y al tiempo de vida de la memoria del motor de PHP. El primero implica el uso de un estado no válido durante la limpieza después de que la gestión de un agotamiento de memoria interrumpa la inicialización. El segundo implica un estado interno que persiste tras liberar la memoria de una solicitud y que utiliza una solicitud posterior en el mismo proceso. En las condiciones afectadas, es posible ejecutar código de forma remota sin autenticación.

El [aviso del equipo de PHP](https://www.php.net/archive/2026.php) incluye PHP-FPM, php-cgi, FrankenPHP y LiteSpeed, además de mod_php, entre los despliegues que atienden tráfico web y deben investigarse. Una SAPI concreta no es motivo para excluir un servicio. A la inversa, una cadena de versión vulnerable por sí sola no demuestra que exista una vía de explotación accesible en ese servicio.

## ¿Qué versión debes comparar?

Estas son las **primeras versiones del código fuente original que corrigen los dos CVE iniciales**, comprobadas el 30 de octubre de 2026. Antes de instalar, consulta la versión compatible actual del mismo proveedor y los avisos posteriores.

| Rama de PHP | Primera versión del código fuente que corrige ambos CVE |
| --- | --- |
| 8.2 | 8.2.35 |
| 8.3 | 8.3.36 |
| 8.4 | 8.4.27 |
| 8.5 | 8.5.12 |

En los paquetes de distribuciones, compara la revisión completa del paquete con el aviso de su proveedor, en lugar de la versión abreviada de PHP. Por ejemplo, [Ubuntu USN-8948-1](https://ubuntu.com/security/notices/USN-8948-1) identifica `8.3.6-0ubuntu0.24.04.13` como el paquete `php8.3-fpm` corregido para Ubuntu 24.04. Comparar ese número con la versión original `8.3.36` clasifica erróneamente una corrección adaptada a una versión anterior. El aviso no autentica compilaciones personalizadas arbitrarias que muestren la misma cadena de versión.

El proyecto PHP ya no ofrece soporte para PHP 8.1 ni versiones anteriores. Verifica el soporte del proveedor y las pruebas de la adaptación de las correcciones, o migra a una rama con soporte. Un parche publicado para el código fuente y la prueba de que un servidor ejecuta ese parche son cosas distintas.

## Recopilar pruebas del CLI sin confundirlas con pruebas de la web

![Registrar como JSON el ejecutable CLI seleccionado, su versión y su configuración; evaluar los procesos web por separado](/assets/diagrams/technical/es-2026-10-30-php2shell-runtime-patching.svg)

El diagrama sigue el recopilador que aparece a continuación. Bajo una SAPI web, termina sin imprimir información. Bajo el CLI, registra el ejecutable, la versión y la configuración sin decidir si está corregido. La identificación del servicio, la aplicación del parche y el reinicio son pasos operativos independientes que este código no realiza.

Con PHP 8.2 o posterior, guarda el archivo en un directorio nuevo fuera de la raíz de documentos. Solo lee el proceso actual mediante las [constantes de PHP](https://www.php.net/manual/en/reserved.constants.php) e [ini_get](https://www.php.net/manual/en/function.ini-get.php); no envía solicitudes, no cambia ajustes ni inicia sesiones. No es necesario publicar una página `phpinfo()`.

### `runtime-evidence.php`

```php
<?php
if (PHP_SAPI !== 'cli') {
    http_response_code(404);
    exit;
}

$evidence = [
    'scope' => 'this-cli-process-only',
    'pid' => getmypid(),
    'version' => PHP_VERSION,
    'sapi' => PHP_SAPI,
    'binary' => PHP_BINARY,
    'loadedIni' => php_ini_loaded_file() ?: null,
    'uploadProgress' => ini_get('session.upload_progress.enabled'),
    'serializeHandler' => ini_get('session.serialize_handler'),
];
echo json_encode($evidence, JSON_PRETTY_PRINT | JSON_THROW_ON_ERROR), PHP_EOL;
```

```sh
php runtime-evidence.php
php -n -d session.upload_progress.enabled=0 runtime-evidence.php
```

El primer comando lee la configuración del CLI seleccionado. El segundo omite los archivos ini y desactiva el seguimiento del progreso de las subidas solo para esa invocación del CLI. **No cambia la configuración del servidor web ni comprueba la configuración efectiva de un proceso web.**

La comprobación local se ejecutó en un contenedor aislado de PHP CLI y confirmó una salida JSON con `sapi` igual a `cli`. El segundo comando devolvió `null` para `loadedIni` y la cadena `"0"` para `uploadProgress`. Las rutas, el PID, la versión y los valores predeterminados varían según el entorno. Estos resultados no establecen si un servicio de producción está corregido ni reproducen una explotación.

## Verificar por separado la instalación y los procesos en ejecución

1. Sigue la configuración del servidor web hacia sus servicios de destino, de FastCGI o de los módulos para identificar el ejecutable PHP real, los grupos de procesos, los contenedores y las réplicas. No supongas que el CLI del host y el entorno de ejecución web comparten una ruta de instalación.
2. Compara el proveedor de ese entorno de ejecución y la revisión completa del paquete o el resumen de la imagen con el aviso. En una compilación personalizada, establece la relación entre el commit de corrección y el artefacto desplegado.
3. Despliega una compilación corregida compatible y sustituye los procesos del grupo o servicio afectado, o sus contenedores. Comprueba primero el alcance del cambio si otros servicios comparten el entorno de ejecución.
4. Verifica la relación entre los procesos nuevos y la compilación corregida en todos los objetivos. Comprueba las páginas normales, el comportamiento del inicio de sesión y las sesiones, las subidas y las tasas de error. No consideres terminado un despliegue parcial ni uno sin pruebas de los procesos en ejecución.

Separar «artefacto corregido identificado» de «adopción en ejecución verificada» en los registros internos de activos ayuda a localizar procesos omitidos. Un fallo por sí solo no demuestra una intrusión, y la ausencia de registros de error no la descarta. Si se sospecha una intrusión, conserva las pruebas e investiga por separado de la aplicación del parche.

## Separar el aviso posterior sobre sesiones y la recompilación para Windows

El [aviso posterior de PHP del 23 de octubre](https://www.php.net/archive/2026.php) trata **CVE-2026-115560** por separado. Se refiere a la combinación de `session.serialize_handler` configurado como `php_binary` o `php_serialize`, código de la aplicación que lo cambia a `php` antes de llamar a `session_start()`, y el seguimiento del progreso de las subidas aún habilitado. El aviso sugiere `session.upload_progress.enabled=0` hasta la siguiente corrección ordinaria. Ese ajuste no demuestra que los dos CVE originales estén completamente resueltos. Comprueba la configuración efectiva de la SAPI web y el impacto en las funciones.

El [aviso para Windows del 26 de octubre](https://www.php.net/archive/2026.php) anuncia los paquetes `8.5.12-1`, `8.4.27-1`, `8.3.36-1` y `8.2.35-1`, que incorporan la corrección de Brotli para **CVE-2026-111497**. Estos recompilan dependencias sin cambiar la versión del código fuente de PHP, por lo que `PHP_VERSION` por sí solo no permite distinguirlos. Los despliegues de Windows que usan la descompresión automática de respuestas de cURL también deben comprobar esa corrección del paquete. Consulta la [guía de respuesta a Node2Shell](/en/posts/2026-10-30-node2shell-brotli-runtime-patching/) para el mismo CVE de Brotli en Node.js.
