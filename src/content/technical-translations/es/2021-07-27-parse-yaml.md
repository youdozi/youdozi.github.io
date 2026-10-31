---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2021-07-27-parse-yaml",
  "routeSlug": "2021-07-27-parse-yaml",
  "kind": "post",
  "title": "Leer YAML desde shell: validar un puerto y ejecutar sin eval",
  "description": "Lee un puerto YAML tipado con Python y PyYAML, rechaza entradas inválidas y pasa SERVER_PORT a un comando hijo sin eval ni generación de código shell.",
  "categories": [
    "linux"
  ],
  "tags": [
    "linux",
    "bash",
    "parse",
    "yaml"
  ],
  "sourcePath": "src/content/posts/en/2021-07-27-parse-yaml.md",
  "sourceSha256": "102f35eacb16194761699d994cc9b12de6dbd6cfb89d6e54580f0d74f30ec17f",
  "draftSha256": "a56d655583bc54a089726f134d241af97dadc6686e5917ef37b7e6f396cf6e1a",
  "manifestPath": ".pipeline/technical-translations/batch-058/manifest.json",
  "manifestSha256": "ddb52115d3c0de8ef810b654b7cab3396580933aec400022723b4ba51b5e8d96",
  "publishedAt": "2026-10-31T15:21:37.180Z",
  "updatedAt": "2026-10-31T15:21:37.180Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 125,
    "approvedAt": "2026-10-31T15:21:37.180Z",
    "basis": "User explicitly requested applying all missing technical-post languages, review, verification and deployment on 2026-11-01, with standing PR merge authorization. Human approval denotes publication authorization; linguistic review is performed by AI, not human/native review."
  }
}
---
Para leer un puerto YAML desde shell sin `eval`, usa un [analizador YAML](https://pyyaml.org/wiki/PyYAMLDocumentation#loading-yaml), valida el tipo y rango del valor y pasa solo las variables necesarias. El ejemplo lee un valor `server.port` con Python y PyYAML e inicia el comando hijo solo si la validación tiene éxito. No aproximes toda la gramática YAML con sed/awk.

Comprobar únicamente el texto mostrado no distingue de forma fiable el entero YAML `8080` de la cadena `"8080"`. Este cargador **no convierte cadenas en números**: solo acepta un valor analizado como entero entre 1 y 65535. bool es una subclase de int en Python, por lo que `type(port) is int` rechaza booleanos, mientras que `isinstance(port, int)` no lo haría.

## Flujo de procesamiento

![Analiza y valida el puerto entero antes de exportar SERVER_PORT. Un fallo del cargador impide iniciar el comando de destino; exec conserva su estado.](/assets/diagrams/technical/es-2021-07-27-parse-yaml.svg)

Analiza y valida el puerto entero antes de exportar SERVER_PORT. Un fallo del cargador impide iniciar el comando de destino; exec conserva su estado.

## Entorno y entrada

Usa Python 3 y [PyYAML 6.0.3](https://pypi.org/project/PyYAML/6.0.3/). El entorno local de ejecución usa Python 3.13. Guarda los tres archivos en el mismo directorio e instala la dependencia en un entorno virtual dedicado.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install PyYAML==6.0.3
```

### `application.yml`

```yaml
server:
  port: 8080
```

### `read-port.py`

```python
import sys
from pathlib import Path
import yaml

if len(sys.argv) != 2:
    sys.exit("usage: read-port.py CONFIG")
try:
    with Path(sys.argv[1]).open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    if not isinstance(config, dict):
        raise ValueError("root must be a mapping")
    server = config.get("server")
    if not isinstance(server, dict):
        raise ValueError("server must be a mapping")
    port = server.get("port")
    if type(port) is not int or not 1 <= port <= 65535:
        raise ValueError("server.port must be an integer from 1 to 65535")
except (OSError, UnicodeError, yaml.YAMLError, ValueError) as error:
    print(f"invalid configuration: {error}", file=sys.stderr)
    sys.exit(2)
print(port)
```

### `run-with-port.sh`

```sh
#!/bin/sh
set -eu
if [ "$#" -lt 2 ]; then
    printf '%s\n' 'usage: run-with-port.sh CONFIG COMMAND [ARG ...]' >&2
    exit 2
fi
config=$1
shift
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
port=$("${PYTHON:-python3}" "$script_dir/read-port.py" "$config")
export SERVER_PORT="$port"
exec "$@"
```

## Iniciar un comando con el valor validado

```sh
PYTHON=.venv/bin/python sh run-with-port.sh application.yml \
  .venv/bin/python -c 'import os; print(os.environ["SERVER_PORT"])'
```

```text
8080
```

`read-port.py` escribe solo el valor válido en stdout y los errores en stderr. Rechaza con estado 2 archivos ausentes, YAML inválido, documentos múltiples, entradas que no son mapas, campos ausentes, cadenas, booleanos, flotantes y valores fuera de rango. `run-with-port.sh` propaga el fallo sin iniciar el destino. Tras iniciarlo, `exec` conserva su estado de salida.

`"$@"` conserva por separado el comando y cada argumento. Los espacios o `$()` de un argumento no se vuelven a evaluar como código shell. Las rutas relativas de `PYTHON` y configuración se resuelven desde el directorio de trabajo del llamador; el envoltorio localiza `read-port.py` junto a sí mismo.

La variable exportada llega al proceso hijo sin modificar el entorno del shell padre que llama. Ejecuta el envoltorio con `sh run-with-port.sh ...`, en lugar de cargarlo con source. Comprueba aparte que la aplicación lee realmente `SERVER_PORT`.

## Alcance del cargador

[`safe_load`](https://pyyaml.org/wiki/PyYAMLDocumentation) no permite etiquetas que construyan objetos Python arbitrarios, pero siguen siendo necesarias las validaciones de tipo y rango de la aplicación. Este ejemplo no limita memoria ni tiempo para entradas maliciosas grandes, por lo que se dirige a configuraciones locales de confianza.

Sigue las reglas de tipos implícitos de PyYAML: valores como `on` pueden convertirse en booleanos. No rechaza claves duplicadas, cuyo último valor puede permanecer; prohíbelas en la entrada y compruébalas aparte. No es una política completa de tipos YAML 1.2 ni un validador general de esquemas de configuración. Define explícitamente el tipo y la política de valores ausentes para cada campo adicional.

Para fallos de comandos y estados de salida, consulta las [versiones de GitHub](/en/posts/2023-09-23-linux-shellscript-github-latest/). Para la compatibilidad de datos persistidos en tareas JVM, consulta la [migración de Spring Batch 5](/en/posts/2023-10-27-springbatch5-migration/).
