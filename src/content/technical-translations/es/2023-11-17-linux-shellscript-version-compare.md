---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2023-11-17-linux-shellscript-version-compare",
  "routeSlug": "2023-11-17-linux-shellscript-version-compare",
  "kind": "post",
  "title": "Comparar versiones numéricas con puntos en Shell usando Python",
  "description": "Compara versiones sin concatenar campos de ancho fijo. Trata los ceros finales, los componentes largos, las entradas no válidas y los códigos de salida explícitos.",
  "categories": [
    "linux"
  ],
  "tags": [
    "linux",
    "bash",
    "shell script",
    "function"
  ],
  "sourcePath": "src/content/posts/en/2023-11-17-linux-shellscript-version-compare.md",
  "sourceSha256": "f3a895ba23f21ab99f5083879149d5f7f1ab3ed0c7c9a89c1557b9bf7d6b1ddc",
  "draftSha256": "c14040cadfc35bedb44bb556f918593c1f679f36efecca6f0fa6c0537b1e4246",
  "manifestPath": ".pipeline/technical-translations/batch-052/manifest.json",
  "manifestSha256": "3d0fe88e42da93129f62cd5dba401357ffe96d3d01f3038c35211f5afff754c7",
  "publishedAt": "2026-10-31T15:21:36.227Z",
  "updatedAt": "2026-10-31T15:21:36.227Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 125,
    "approvedAt": "2026-10-31T15:21:36.227Z",
    "basis": "User explicitly requested applying all missing technical-post languages, review, verification and deployment on 2026-11-01, with standing PR merge authorization. Human approval denotes publication authorization; linguistic review is performed by AI, not human/native review."
  }
}
---
No compares `1.10` y `1.2` como cadenas ni como números decimales. Compara sus componentes enteros de izquierda a derecha y completa los componentes finales ausentes con cero; así, `1.2` es igual a `1.2.0`. Este ejemplo implementa esa regla solo para versiones numéricas separadas por puntos.

Rechaza `v1.2`, `1.2-rc1` y `1.2+build`. Para la precedencia de versiones preliminares de [SemVer](https://semver.org/), usa un analizador de esa especificación. Eliminar sufijos sin comprobarlos puede cambiar el significado.

## Flujo del procesamiento

![Valida el contrato de entrada exclusivamente numérica, completa los componentes ausentes con cero y detente en el primer par diferente. Un resultado «menor que» también indica que la comparación se ha realizado correctamente.](/assets/diagrams/technical/es-2023-11-17-linux-shellscript-version-compare.svg)

Valida el contrato de entrada exclusivamente numérica, completa los componentes ausentes con cero y detente en el primer par diferente. Un resultado «menor que» también indica que la comparación se ha realizado correctamente.

## Un script de comparación ejecutable

Se necesita Python 3. Guarda el código como `version-compare.sh` e invócalo con `sh`.

### `version-compare.sh`

```sh
#!/bin/sh
set -eu
python3 - "$@" <<'PYTHON'
import re
import sys
from itertools import zip_longest

if len(sys.argv) != 3 or any(not re.fullmatch(r"[0-9]+(?:\.[0-9]+)*", value) for value in sys.argv[1:]):
    print("usage: version-compare.sh CURRENT LATEST (numeric dotted versions)", file=sys.stderr)
    raise SystemExit(2)
current, latest = sys.argv[1:]
try:
    left = [int(part) for part in current.split('.')]
    right = [int(part) for part in latest.split('.')]
except ValueError:
    print("numeric component exceeds this Python runtime's conversion limit", file=sys.stderr)
    raise SystemExit(2)
comparison = 0
for a, b in zip_longest(left, right, fillvalue=0):
    if a != b:
        comparison = -1 if a < b else 1
        break
operator = '<' if comparison < 0 else '>' if comparison > 0 else '='
print(f"{current} {operator} {latest}")
PYTHON
```

```sh
sh version-compare.sh 1.10.5 1.3.1
sh version-compare.sh 1.2 1.2.0
sh version-compare.sh 1.1000 2.0
```

Las salidas son `1.10.5 > 1.3.1`, `1.2 = 1.2.0` y `1.1000 < 2.0`. Una comparación válida devuelve el código 0 independientemente de la relación. Una cantidad de argumentos incorrecta, una sintaxis no admitida o los límites de conversión numérica producen una explicación en stderr y el código 2.

| Entradas | Resultado |
| --- | --- |
| `1.2.0.0.1` y `1.2` | `1.2.0.0.1 > 1.2` |
| `01.002` y `1.2` | `01.002 = 1.2` |
| `1.2-rc1` y `1.2` | Formato no admitido, código 2 |
| `1..2` y `1.2` | Formato no admitido, código 2 |

## ¿Por qué no concatenar números de ancho fijo?

Un ancho como `%03d` de awk es un ancho mínimo de presentación, no una longitud máxima del componente. Empaquetar esos campos en un entero del Shell puede perder el orden original con valores grandes o componentes adicionales.

El ejemplo convierte cada componente en un entero de Python y usa [`zip_longest(..., fillvalue=0)`](https://docs.python.org/3/library/itertools.html#itertools.zip_longest) para alinear las longitudes. Si el entorno de ejecución rechaza la conversión numérica, no se considera una comparación correcta.

En la automatización del despliegue, la comparación y el éxito del comando son decisiones distintas. El script no falla solo porque la versión actual sea menor: lee la relación de stdout antes de aplicar tu política. Las [etiquetas de releases de GitHub](/en/posts/2023-09-23-linux-shellscript-github-latest/) no tienen por qué usar esta sintaxis numérica, así que no las pases sin comprobarlas. Para seleccionar el intérprete, consulta el [ejemplo de función POSIX sh](/en/posts/2023-09-20-linux-shellscript-function-error/).
