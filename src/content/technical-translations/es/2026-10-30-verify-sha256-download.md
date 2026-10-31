---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2026-10-30-verify-sha256-download",
  "routeSlug": "2026-10-30-verify-sha256-download",
  "kind": "post",
  "title": "Verificar la suma SHA-256 de un archivo descargado con Python",
  "description": "Compara un archivo descargado con un valor SHA-256 de confianza mediante un verificador de Python que lee por bloques. Reproduce coincidencias, cambios y errores de lectura con códigos de salida explícitos.",
  "categories": [
    "linux"
  ],
  "tags": [
    "python",
    "shellscript",
    "sha256"
  ],
  "sourcePath": "src/content/posts/en/2026-10-30-verify-sha256-download.md",
  "sourceSha256": "9c91eef87fd5390b5be8f867c298bdaaaa20979b4571c13ba7694d62ba172e89",
  "draftSha256": "e2e74dddd3a2838bdcc3b7c9e7f2ca1e61afe665bb612ad1776c6749610ebfcf",
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
Para verificar un archivo descargado, calcula su resumen SHA-256 y compáralo con el valor esperado de un editor de confianza. El módulo [hashlib](https://docs.python.org/3.11/library/hashlib.html) de Python permite procesar los bytes binarios por bloques. Una coincidencia comprueba que esos bytes corresponden a ese valor; no autentica al editor ni demuestra que el programa sea seguro. Adoptium documenta por separado la [verificación de firmas](https://adoptium.net/installation/gpg-verification).

## ¿Con qué suma de comprobación debes comparar?

Utiliza la suma correspondiente a la versión, el sistema operativo, la CPU y el formato de archivo exactos que descargaste. El [selector de versiones de GitHub](/en/posts/2023-09-23-linux-shellscript-github-latest/) elige la URL de un recurso; el [ejemplo de metadatos de Temurin](/en/posts/2023-10-10-temurin-jdk21-delay/) también comprueba la sintaxis de la suma. Ninguno calcula el hash del archivo descargado. Las [instrucciones de instalación desde archivos de Adoptium](https://adoptium.net/installation/archives) explican cómo obtener la suma que lo acompaña.

Obtén el valor esperado a través del canal de distribución de confianza del editor. Calcular el resumen del archivo descargado y utilizar ese mismo resultado como valor esperado no permite detectar una descarga incorrecta. Si un atacante puede sustituir tanto el archivo como la suma anunciada, su coincidencia no demuestra autenticidad. Verificar una firma con una clave de confianza del editor es un paso independiente, fuera del alcance de este ejemplo.

## ¿Cómo funciona la comprobación del archivo?

![Validar una suma de comprobación, calcular el hash del archivo y comparar el resultado](/assets/diagrams/technical/es-2026-10-30-verify-sha256-download.svg)

Valida el valor esperado, abre un archivo normal que se mantenga estable en modo binario, actualiza el resumen por bloques hasta EOF y compara. Una entrada no válida o un error de lectura devuelve 2; una discrepancia devuelve 1; solo una coincidencia devuelve 0. El diagrama resume el bucle de bloques en un paso. No modifiques ni sustituyas el archivo durante la verificación ni después de ella antes de utilizarlo. Esta herramienta no verifica y ejecuta de forma atómica.

## Ejecutar un verificador sin paquetes adicionales

Utiliza Python 3.11 o posterior y guarda lo siguiente como `verify-sha256.py`. Los comandos siguientes utilizan una shell POSIX. El programa lee archivos locales; no los descarga, descomprime ni ejecuta. Sigue un enlace simbólico si apunta a un archivo normal. Acepta un único valor hexadecimal de 64 caracteres, incluidas mayúsculas, en lugar de un manifiesto de sumas, un nombre de archivo o una URL.

### `verify-sha256.py`

```python
import hashlib
from pathlib import Path
import re
import sys


def main(argv):
    if len(argv) != 3 or not re.fullmatch(r"[0-9a-fA-F]{64}", argv[1]):
        print("usage: verify-sha256.py EXPECTED_SHA256 FILE", file=sys.stderr)
        return 2
    path = Path(argv[2])
    try:
        if not path.is_file():
            raise OSError("expected an existing regular file")
        digest = hashlib.sha256()
        with path.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as error:
        print(f"READ ERROR: {error}", file=sys.stderr)
        return 2
    if digest.hexdigest() != argv[1].lower():
        print("MISMATCH", file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
```

`rb` conserva los bytes originales, incluidos los finales de línea. Cada lectura solicita como máximo 1 MiB; el archivo no se carga completo. Las sumas no válidas se rechazan antes de abrir la ruta. Las rutas inexistentes, los directorios y los errores de lectura comparten el estado 2. Las tuberías con nombre y los archivos de dispositivo quedan fuera del contrato de archivos normales.

## Reproducir una coincidencia y un archivo modificado

Utiliza un directorio nuevo y vacío. Estos datos de prueba escriben `sample.bin` con los tres bytes `abc` y `changed.bin` con `abcd`. El resumen fijo del comando corresponde únicamente a `abc`; no es la suma de un archivo de JDK.

### `make-samples.py`

```python
from pathlib import Path

Path("sample.bin").write_bytes(b"abc")
Path("changed.bin").write_bytes(b"abcd")
```

```sh
python3 make-samples.py
expected='ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
python3 verify-sha256.py "$expected" sample.bin
python3 verify-sha256.py "$expected" changed.bin
printf 'exit=%s\n' "$?"
```

El archivo que coincide imprime `OK`. El archivo modificado imprime `MISMATCH` en stderr y el comando final imprime `exit=1`. Si utilizas `set -e`, una discrepancia esperada requiere un `if` explícito u otra rama de gestión de errores; de lo contrario, la shell puede detenerse antes de imprimir el estado.

| Estado | Significado | Siguiente acción |
| --- | --- | --- |
| 0 | El resumen coincide con el valor esperado proporcionado | Continúa solo si ese valor procede de una fuente de confianza |
| 1 | Los resúmenes son distintos | Deja de usar el archivo; revisa el recurso seleccionado y la descarga |
| 2 | Argumentos no válidos, sintaxis de la suma o lectura del archivo | Corrige la entrada o el acceso al archivo y vuelve a intentarlo |

Una discrepancia por sí sola no permite identificar como causa la corrupción, un recurso incorrecto o una sustitución maliciosa. La comprobación no verifica firmas ni analiza malware.
