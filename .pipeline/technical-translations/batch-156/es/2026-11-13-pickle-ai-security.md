---
{
  "state": "draft",
  "language": "es",
  "translationKey": "2026-11-13-pickle-ai-security",
  "title": "Cómo funciona Pickle AI: control de apps de iPhone y protección de contraseñas",
  "description": "Analiza qué indican las fuentes públicas sobre el navegador de Pickle, sus cuentas conectadas y los límites de protección de tokens, contraseñas y claves.",
  "sourcePath": "src/content/posts/en/2026-11-13-pickle-ai-security.md",
  "sourceSha256": "4973bca9ea9b81ec4e068b4f530a2b82742c427074c36836639b0c2db1a811e2"
}
---

**Las explicaciones oficiales de Pickle AI apuntan a que un navegador separado y cuentas conectadas realizan las tareas, en lugar de manejar directamente las pantallas de otras apps del iPhone.** Las contraseñas se cifran separadamente del modelo, pero el límite de protección de los valores usados para iniciar sesión difiere entre OAuth y las contraseñas de sitios web.

El tema es [Pickle](https://pickle.com/), un agente personal de IA de Pickle, Inc. El análisis utiliza ayuda oficial consultada el 13 de noviembre de 2026 y el código público `credential-enclave` del **commit `cff16a343bf5bb7953e5b65df6ab3600107e127d`**. Ejecuté la verificación de la versión del programa público de seguridad; no es una auditoría de la app iOS instalada ni de todo el servidor de producción.

## ¿Pulsa realmente otras apps del iPhone?

La [ayuda para guardar inicios de sesión](https://www.pickle.com/help/connect/save-login) indica que el navegador de Pickle está separado del teléfono y no puede usar directamente los accesos guardados en él. La [guía de delegación de tareas](https://www.pickle.com/help/tasks/delegate) describe el manejo de sitios web en un navegador real y la continuación del trabajo al cerrar la app.

Por tanto, completar un pedido o reserva no demuestra que se haya pulsado la pantalla de una app de compras instalada. Las rutas respaldadas por el material público son:

| Ruta | Evidencia y significado |
| --- | --- |
| Navegador separado | Inicia sesión y rellena formularios web, separado de las pantallas de apps del teléfono |
| API de cuentas conectadas | El código público `forward` adjunta credenciales a solicitudes API permitidas del proveedor |
| Llamada telefónica | La guía oficial describe llamar por el usuario para lo que no puede hacerse en la web |

La explicación de Apple sobre [aislamiento de apps de terceros](https://support.apple.com/en-gb/guide/security/sec15bfe098e/web) también restringe el acceso a otra información a los servicios que ofrece iOS. Esto por sí solo no descarta toda automatización, pero no encontré pruebas de que Pickle eluda ese aislamiento para controlar otras apps.

El material disponible no establece qué herramientas DOM o modelos de reconocimiento de pantalla usa el navegador de Pickle ni qué ruta se elige para cada tarea. El funcionamiento descrito aquí es un análisis que conecta instrucciones oficiales y la ruta pública de credenciales.

## ¿Cómo inicia sesión sin entregar la contraseña a la IA?

Aunque un modelo nunca emita directamente la contraseña, un ejecutor separado puede recibir el valor necesario e introducirlo en un formulario. La [explicación de privacidad](https://www.pickle.com/privacy) de Pickle afirma que contraseñas y datos de tarjeta se cifran en el dispositivo y se ocultan de los resultados recibidos por el modelo. Hay que contrastar los límites técnicos de esa explicación con el código público.

![Durante la configuración, el iPhone crea claves y delega una clave de usuario cifrada a un Enclave verificado. Al usarla se comprueban la delegación activa y el registro cifrado y se confirma el guardado del registro de uso. Los tokens OAuth se usan para llamadas API dentro del nodo; las contraseñas y tarjetas de Vault salen en texto claro al worker mediante release para un formulario web. El enmascaramiento posterior es otro límite.](2026-11-13-pickle-ai-security.svg)

La parte superior del diagrama muestra la configuración, con delegación anticipada de una clave; la inferior muestra su uso mientras la delegación es válida. No significa que el teléfono deba enviar una clave nueva en cada inicio. El diagrama tampoco reproduce todos los detalles del ejecutor de tareas.

### Claves del dispositivo y registros cifrados

El [protocolo público](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/docs/protocol.md#3-keys) indica que una clave maestra creada en el dispositivo se conserva en iCloud Keychain, con claves derivadas distintas para firma, descifrado de registros y credenciales. Los registros se cifran con ChaCha20-Poly1305 y su contexto, como cuenta y tipo de registro, también queda vinculado a la autenticación.

El dispositivo verifica la atestación y clave pública del nodo y cifra y delega a este la **clave de usuario derivada**. La atestación remota comprueba a qué entorno de ejecución medido pertenece una clave pública. [AWS Nitro Enclaves](https://docs.aws.amazon.com/enclaves/latest/user/) aísla la memoria del servidor padre y no ofrece red externa directa ni almacenamiento persistente. Un nodo Pickle usa comunicaciones retransmitidas por el host; eso no concede al host permiso para descifrar.

La clave de usuario delegada se usa durante un periodo limitado en la memoria del nodo. La [descripción pública de arquitectura](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/README.md#structure) fija una delegación máxima de 30 días. El Keychain del dispositivo y Nitro Enclave del servidor son capas distintas de protección.

### Los tokens OAuth se usan dentro del nodo

El [código de reenvío de API](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/enclave/src/api/forward.rs) comprueba una delegación activa, abre el registro OAuth y prepara una solicitud permitida al proveedor. La ejecuta después de confirmar que se guardó el registro de uso. Esta ruta efectúa una solicitud autenticada sin entregar el token al modelo.

Sin embargo, **ocultar un token y ocultar los datos leídos con él son cosas distintas**. La [política de salida](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/docs/egress-policy.md) trata por separado la devolución de respuestas del proveedor al entorno operativo. Si se permite leer correo, el modelo puede procesar su contenido; esto se debe evaluar aparte de la protección del token.

### Las contraseñas web cruzan otro límite tras release

El [código de Vault](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/enclave/src/vault.rs) define tipos que seleccionan contraseñas, datos de tarjeta y códigos TOTP para una respuesta de salida. El [manejador real de release](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/enclave/src/api/release.rs) serializa y devuelve los valores tras confirmar el guardado del registro de uso. **En ese momento contraseñas y datos de tarjeta salen del nodo en texto claro utilizable por el worker operativo.** En TOTP sale el código de un solo uso calculado, no la semilla.

La comprobación `origin` del código público solo valida el formato de un origen HTTPS. Un comentario atribuye al llamador la responsabilidad de decidir si la dirección coincide con el sitio de inicio guardado. Por tanto, el código del Enclave por sí solo no demuestra las restricciones de sitio ni el enmascaramiento de resultados del modelo.

Esto no demuestra que haya habido una filtración. **Ocultar un valor de la entrada del modelo**, **cifrarlo al almacenarlo** y **usarlo en texto claro en la memoria del worker** son propiedades distintas. No debe ampliarse «la IA no recibe la contraseña» a «la contraseña descifrada nunca sale del área protegida».

## ¿Qué garantiza el registro de uso?

La [guía oficial del historial de uso](https://pickle.com/help/privacy/activity) indica que el registro se guarda primero y que las credenciales no se usan si falla el guardado. El código API público también muestra el uso o release después de confirmar el registro. Los registros cifrados, firmas y enlaces buscan hacer detectables cambios u omisiones.

Un registro no garantiza que el usuario quisiera esa tarea ni que tuviera éxito en el sitio externo. Por ejemplo, la solicitud puede fallar después de guardar el registro. Aprobar antes de pagar y volver a confirmar el importe son políticas de ejecución de la [descripción oficial del servicio](https://pickle.com/en), no propiedades que se deriven automáticamente del cifrado de credenciales.

Si se delega también la semilla TOTP, el agente puede generar códigos. Es una función de comodidad de la [guía de acceso guardado](https://www.pickle.com/help/connect/save-login), pero difiere de que el usuario apruebe por separado un segundo factor en cada tarea. La delegación debe evaluarse como más amplia que al entregar solo una contraseña.

## Verificar la prueba del programa público de seguridad

La [documentación de secure-program](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/secure-program/README.md) también publica el programa del dispositivo y ofrece una herramienta para verificar la firma de versión y la prueba del registro de transparencia. El ejemplo comprueba **si un archivo público coincide con su prueba de versión**. No se conecta a un nodo de producción ni utiliza una contraseña real.

![El JS público y la prueba de versión se introducen en el verificador oficial. Comprueba hash, firma y prueba del registro de transparencia. La versión original v42 devuelve código 0; un byte añadido produce error source_hash y código 1. La verificación del servidor de producción y aplicación instalada es independiente.](2026-11-13-pickle-ai-security-architecture.svg)

Se necesitan Git, curl, Rustup y herramientas nativas, y descargar código y dependencias Rust usa la red. El verificador se compiló con el commit fijado abajo en **macOS arm64 con Rust 1.100.0**. El repositorio fija la versión de herramientas 1.98.1; aquí `+1.100.0` selecciona explícitamente la versión de ejecución.

### `verify-example.sh`

```bash
# macOS·Linux 셸, Git·curl·Rustup 및 네이티브 빌드 도구가 필요합니다.
# 새 작업 폴더에서 실행합니다. 아래 검증은 계정 로그인이나 실제 비밀번호를 사용하지 않습니다.
git clone https://github.com/pickle-com/credential-enclave.git
cd credential-enclave
git checkout cff16a343bf5bb7953e5b65df6ab3600107e127d
rustup toolchain install 1.100.0 --profile minimal
cargo +1.100.0 build --locked -p credential-enclave-verify
curl --fail --location \
  https://github.com/pickle-com/credential-enclave/releases/download/secure-program-v42/secure-program.release.json \
  --output secure-program.release.json
./target/debug/credential-enclave-verify program \
  --source secure-program/secure-program.js \
  --release secure-program.release.json
```

El archivo original devolvió código de salida 0 y la siguiente salida:

```text
program release secure-program-v42: version 42, sha256 31e7fa7fb51f87781313b1f97b60ae3c7b69ff8f2fbcee7de12b7a0ed034d8e8, log index 3761959022: ok
```

Comprueba también que se rechace un archivo modificado. Ejecuta los siguientes comandos en el mismo directorio del repositorio.

### `tamper-example.sh`

```bash
cp secure-program/secure-program.js changed-program.js
printf '\n' >> changed-program.js
./target/debug/credential-enclave-verify program \
  --source changed-program.js \
  --release secure-program.release.json
echo $?
```

El archivo con un byte de salto de línea añadido fue rechazado por discrepancia de `source_hash` y terminó con código 1. El resultado se refiere a la prueba de versión del programa público. No comprobé si la versión y el hash mostrados por la app real coinciden, ni verifiqué por atestación remota la medición del Enclave de producción.

## Condiciones pendientes al evaluar la seguridad

Las [limitaciones del repositorio público](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/README.md#what-it-does-not-guarantee) describen supuestos de confianza como honestidad de la app, contratos API de proveedores, claves de versión y registros. Aunque exista un programa público, comprobar si todo el binario iOS lo ejecuta sin cambiarlo es una cuestión separada. Que un nodo pueda transferir una delegación a una versión posterior tampoco significa que las protecciones de una versión queden fijadas para siempre.

También importan los [límites de actualización](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/secure-program/README.md#limits) del programa del dispositivo. La documentación indica que el código nuevo puede cargarse sin espera previa si el operador lo firma, registra en el registro público y cumple los requisitos de carga. **Verificar la versión confirma la coincidencia con el archivo publicado y firmado; no garantiza que el código sea inocuo.** La confianza en el operador permanece para código posterior. Esto no afirma ni observa una versión maliciosa real.

| Qué comprobar | Pregunta necesaria para decidir |
| --- | --- |
| Cuentas conectadas | ¿Qué permisos de lectura y escritura se conceden y pueden revocarse en el proveedor? |
| Vault y TOTP | ¿Es necesario delegar la generación de códigos además de contraseñas? |
| Pagos y reservas | ¿Se pueden comprobar condiciones e importe antes de ejecutar y verificar el resultado? |
| Programa de seguridad y nodo | ¿Se corresponden versión y hash de la app, versión pública y atestación real del nodo? |
| Conversaciones y datos de cuentas conectadas | ¿Qué contenido procesa el modelo aunque se oculten credenciales? |

La clave del diseño de seguridad de Pickle es **qué claves se delegan a quién y en qué límite se descifra y usa cada valor**. El código público aporta indicios para examinarlos. Para el usuario, un punto de partida es distinguir el control real de apps del iPhone de la delegación de acceso, conectar solo permisos necesarios y comprobar historial y resultados.
