---
language: en
translationKey: 2021-07-27-parse-yaml
routeSlug: 2021-07-27-parse-yaml
kind: post
categories:
  - linux
tags:
  - linux
  - bash
  - parse
  - yaml
publishedAt: "2026-10-27T03:19:18+00:00"
title: "Read YAML from Shell: Validate a Port and Run a Command Without eval"
updatedAt: "2026-10-27T03:19:18+00:00"
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Official sources checked; runnable examples checked separately from
  migration and production claims.
reviewSources:
  - https://pyyaml.org/wiki/PyYAMLDocumentation
  - https://pypi.org/project/PyYAML/6.0.3/
  - https://www.gnu.org/software/bash/manual/html_node/Executing-Commands.html
description: Read a typed YAML port with Python and PyYAML, reject invalid
  inputs, and pass SERVER_PORT to a child command without eval or shell-code
  generation.
---
When reading YAML from shell, use a YAML parser, validate the value's type and range, and pass only the variables you need. Avoid approximating the full grammar with sed/awk or evaluating generated text with `eval`. This example reads one `server.port` value using Python and PyYAML, then starts a child command only after validation succeeds.

Checking only rendered text does not reliably distinguish YAML integer `8080` from string `"8080"`. This loader **does not coerce strings into numbers**: it accepts only a value parsed as an integer between 1 and 65535. Python's bool subclasses int, so `type(port) is int` rejects booleans where `isinstance(port, int)` would not.

## Environment and input

Use Python 3 and [PyYAML 6.0.3](https://pypi.org/project/PyYAML/6.0.3/). The local execution environment uses Python 3.13. Save these three files in the same directory and install the dependency in a dedicated virtual environment.

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

## Start a command with the validated value

```sh
PYTHON=.venv/bin/python sh run-with-port.sh application.yml \
  .venv/bin/python -c 'import os; print(os.environ["SERVER_PORT"])'
```

```text
8080
```

`read-port.py` writes only the valid value to stdout and errors to stderr. It rejects missing files, invalid YAML, multiple documents, non-mapping input, missing fields, strings, booleans, floats, and out-of-range values with status 2. `run-with-port.sh` propagates that failure without starting the target command. After starting the target, `exec` preserves its exit status.

`"$@"` preserves the command and each argument separately. Spaces or `$()` in an argument are not re-evaluated as shell source. Relative `PYTHON` and configuration paths are resolved from the caller's working directory, while the wrapper locates `read-port.py` beside itself.

The export reaches the child process without changing the calling parent shell's environment. Run the wrapper with `sh run-with-port.sh ...` rather than sourcing it. Check separately that your application actually reads `SERVER_PORT`.

## Loader scope

[`safe_load`](https://pyyaml.org/wiki/PyYAMLDocumentation) does not allow tags that construct arbitrary Python objects, but application-specific type and range checks remain necessary. This example imposes no memory or time limit for maliciously large input, so it targets trusted local configuration.

It follows PyYAML's implicit type rules: values such as `on` can become booleans. It does not reject duplicate keys, whose later value may remain; prohibit them in input and check them separately. This is neither a complete YAML 1.2 typing policy nor a general configuration schema validator. Define each additional field's type and missing-value policy explicitly.

For command failures and exit status handling, see [querying GitHub releases](/en/posts/2023-09-23-linux-shellscript-github-latest/). For persisted data compatibility in JVM jobs, see [Spring Batch 5 migration](/en/posts/2023-10-27-springbatch5-migration/).
