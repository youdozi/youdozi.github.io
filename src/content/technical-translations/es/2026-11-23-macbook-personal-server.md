---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2026-11-23-macbook-personal-server",
  "routeSlug": "2026-11-23-macbook-personal-server",
  "kind": "post",
  "title": "Usar un MacBook como servidor personal en una red privada",
  "description": "Prueba un servidor HTTP local por un túnel SSH y conoce los límites de disponibilidad del Mac.",
  "categories": [
    "tips"
  ],
  "tags": [
    "macos",
    "ssh",
    "home-server"
  ],
  "sourcePath": "src/content/posts/en/2026-11-23-macbook-personal-server.md",
  "sourceSha256": "bd4c8683623163f5f31589a1e1e1414c0c8947ff5622aef14a2544139945a193",
  "draftSha256": "b31f70e3d1da06fe98e39c951f94a066f2e9942bc3120efaee28462efaf0beba",
  "manifestPath": ".pipeline/technical-translations/batch-187/manifest.json",
  "manifestSha256": "d03d054b981e35da867bbad2a28b8b05e266caa702753c7ea49aa440bd3b3f75",
  "publishedAt": "2026-11-23T09:52:10.853Z",
  "updatedAt": "2026-11-23T09:52:10.853Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 188,
    "approvedAt": "2026-11-23T09:52:10.853Z",
    "basis": "Owner explicitly requested publication in eight languages; translations were self-reviewed without independent or native-speaker review."
  }
}
---

Un MacBook puede ofrecer una breve demostración de desarrollo a otro equipo en una red privada de confianza sin exponer un puerto HTTP en la red. Inicia un servidor HTTP temporal en la interfaz de bucle local del Mac y accede mediante un reenvío local SSH. Es una prueba, no una configuración para un servicio público siempre disponible.

![La solicitud del cliente pasa por un reenvío local SSH al HTTP de bucle local del Mac, que devuelve el archivo de prueba.](/assets/diagrams/technical/es-2026-11-23-macbook-personal-server.svg)

El diagrama resume la solicitud y la respuesta; la autenticación y la limpieza se explican a continuación.

## Preparar el acceso

Usa dos equipos en una red privada que controles. Una red compartida o pública puede contener dispositivos no fiables; una dirección privada por sí sola no restringe el acceso. No abras puertos en el router. Usa una cuenta estándar de macOS distinta para esta tarea y dale acceso solo a los archivos necesarios. En el Mac, abre Ajustes del Sistema → General → Compartir → Sesión remota, actívala y selecciona «Solo estos usuarios» para permitir esa cuenta. Mantén desactivado el acceso completo al disco para usuarios remotos salvo que se necesite por separado. El panel de sesión remota muestra la dirección SSH del Mac. Los ajustes pueden variar según la versión de macOS o la gestión del dispositivo. [Apple: sesión remota](https://support.apple.com/guide/mac-help/allow-a-remote-computer-to-access-your-mac-mchlp1066/mac)

En el cliente, crea una clave dedicada y elige una frase de contraseña y un nombre de archivo nuevo cuando se soliciten:

```sh
ssh-keygen -t ed25519 -f ~/.ssh/macbook_demo
```

Copia la línea de clave pública de `~/.ssh/macbook_demo.pub` al Mac por un canal de confianza. Con la sesión local iniciada en el Mac con la cuenta autorizada, ejecuta los siguientes comandos, pega la línea de clave pública y pulsa Ctrl-D en una línea nueva. Esto añade la línea a `~/.ssh/authorized_keys` y conserva las entradas existentes. Nunca copies la clave privada.

```sh
umask 077
mkdir -p ~/.ssh
chmod 700 ~/.ssh
cat >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

Consulta [claves autorizadas de OpenSSH](https://man.openbsd.org/sshd#AUTHORIZED_KEYS_FILE_FORMAT) y [ssh-keygen](https://man.openbsd.org/ssh-keygen).

En el Mac, consulta la huella de la clave del servidor desde un terminal local:

```sh
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
```

Desde el cliente, conecta con la cuenta autorizada y la dirección mostrada en Sesión remota; `demo` y `192.168.1.20` son ejemplos que debes sustituir. Antes de aceptar la primera conexión, compara la huella ED25519 mostrada con la obtenida en el Mac. Si son distintas, detente e investiga. Una advertencia de cambio de clave del servidor también requiere investigación, no aceptación automática. [Verificación del servidor OpenSSH](https://man.openbsd.org/ssh#VERIFYING_HOST_KEYS)

```sh
ssh -i ~/.ssh/macbook_demo -o HostKeyAlgorithms=ssh-ed25519 demo@192.168.1.20
```

Comprueba que se inicia la sesión y escribe `exit`. La contraseña de la cuenta puede seguir funcionando: añadir una clave no desactiva por sí solo la autenticación por contraseña.

## Iniciar y reenviar una prueba

En el Mac, en un terminal con la cuenta autorizada, crea un directorio temporal vacío, añade un archivo sin datos sensibles e inicia Python 3. El servidor se vincula solo a la dirección IPv4 de bucle local del Mac. Mantén abierto este terminal.

```sh
sample_dir=$(mktemp -d)
printf 'home server test\n' > "$sample_dir/index.html"
python3 -m http.server 8000 --bind 127.0.0.1 --directory "$sample_dir"
```

Si el puerto 8000 ya está ocupado, detente y elige un puerto libre tanto en el comando del servidor como en el de reenvío. El servidor HTTP simple de Python sirve para pruebas, no para producción; sigue enlaces simbólicos, así que usa solo el directorio de prueba vacío y un archivo sin datos sensibles. [Python http.server](https://docs.python.org/3/library/http.server.html)

En el cliente, establece el túnel en un segundo terminal y mantenlo abierto:

```sh
ssh -N -o ExitOnForwardFailure=yes -i ~/.ssh/macbook_demo -L 127.0.0.1:18000:127.0.0.1:8000 demo@192.168.1.20
```

En otro terminal del cliente, ejecuta:

```sh
curl http://127.0.0.1:18000/
```

La salida esperada es `home server test`. El cliente se conecta a su propio puerto 18000; SSH lleva la solicitud al Mac, donde conecta al puerto de bucle local 8000. Si falla el túnel, comprueba la dirección, la lista de acceso, la huella y la clave antes de reintentar. Si el túnel se inicia pero curl falla, comprueba que Python siga en ejecución y que coincidan ambos puertos. `ExitOnForwardFailure` confirma la creación del puerto de escucha local, no que el servidor HTTP de destino sea accesible. [Reenvío OpenSSH](https://man.openbsd.org/ssh#L)

Detén el túnel SSH con Ctrl-C en su terminal. Detén Python con Ctrl-C en el terminal del Mac y elimina solo el directorio de prueba creado arriba:

```sh
rm "$sample_dir/index.html"
rmdir "$sample_dir"
```

Elimina la línea de clave pública del ejemplo y desactiva Sesión remota si se añadieron solo para este ejercicio. Conserva las claves y los ajustes de acceso existentes.

## Disponibilidad y siguientes pasos

Apagar la pantalla y poner el Mac en reposo son estados distintos. Cerrar la pantalla de un portátil normalmente lo pone en reposo; no supongas que cerrar la tapa, activar el equipo por red o cambiar la alimentación mantendrá esta prueba en marcha. Tras reiniciar con FileVault, prevé que una persona pueda desbloquear el Mac si es necesario. Apple documenta el desbloqueo de FileVault por SSH bajo ciertas condiciones en equipos Apple Silicon con macOS 26 o posterior; no supongas que se cumplen. [Apple: reposo](https://support.apple.com/guide/mac-help/put-your-mac-to-sleep-or-wake-it-mh10330/mac) · [Apple: FileVault](https://support.apple.com/guide/security/managing-filevault-sec8447f5049/web)

Para una demostración puntual, detén el proceso al terminar. Para archivos, considera la función de compartir archivos de macOS y sus controles de acceso. Un servicio de larga duración necesita una configuración launchd independiente, actualizaciones, copias de seguridad y un plan de recuperación; un equipo dedicado puede ser más adecuado. Para acceder desde fuera de casa, se puede evaluar por separado una VPN privada; sigue siendo necesario proteger el Mac y el servicio.

La respuesta HTTP de bucle local se comprobó localmente con un archivo y un proceso temporales; la conexión SSH y el túnel son pasos documentados para el lector, no una conexión probada a este Mac.
