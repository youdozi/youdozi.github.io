---
title: "Compare Dotted Numeric Versions in Shell with Python"
language: "en"
translationKey: "2023-11-17-linux-shellscript-version-compare"
routeSlug: "2023-11-17-linux-shellscript-version-compare"
kind: "post"
publishedAt: "2026-10-27T02:12:24+00:00"
categories: ["linux"]
tags: ["linux", "bash", "shell script", "function"]
updatedAt: "2026-10-27T02:12:24+00:00"
reviewedAt: "2026-10-27"
reviewStatus: "revised"
reviewScope: "Primary documentation checked; published runnable example verified."
reviewSources: ["https://docs.python.org/3/library/itertools.html#itertools.zip_longest", "https://semver.org/"]
description: "Compare dotted numeric versions without fixed-width packing. Handle trailing zeros, long components, invalid inputs, and explicit exit statuses."
---
Do not compare `1.10` and `1.2` as strings or decimal numbers. Compare integer components from left to right and fill missing trailing components with zero; that makes `1.2` equal to `1.2.0`. This example implements that rule for numeric dotted versions only.

It rejects `v1.2`, `1.2-rc1` and `1.2+build`. For [SemVer](https://semver.org/) pre-release precedence, use a parser for that specification. Blindly removing suffixes can change the meaning.

## A runnable comparison script

Python 3 is required. Save this as `version-compare.sh` and invoke it with `sh`.

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

The outputs are `1.10.5 > 1.3.1`, `1.2 = 1.2.0` and `1.1000 < 2.0`. A valid comparison returns status 0 regardless of the relationship. Invalid argument counts, unsupported syntax or numeric conversion limits produce a stderr explanation and status 2.

| Inputs | Result |
| --- | --- |
| `1.2.0.0.1` and `1.2` | `1.2.0.0.1 > 1.2` |
| `01.002` and `1.2` | `01.002 = 1.2` |
| `1.2-rc1` and `1.2` | Unsupported format, status 2 |
| `1..2` and `1.2` | Unsupported format, status 2 |

## Why not concatenate fixed-width numbers?

A width such as awk's `%03d` is a minimum display width, not a maximum component length. Packing those fields into a shell integer can lose the original ordering for large values or additional components.

This example converts each component to a Python integer and uses [`zip_longest(..., fillvalue=0)`](https://docs.python.org/3/library/itertools.html#itertools.zip_longest) to align lengths. A runtime refusing the numeric conversion is not treated as a successful comparison.

In deployment automation, comparison and command success are separate decisions. This script does not fail just because the current version is lower; read the relationship from stdout before applying your policy. [GitHub release tags](/en/posts/2023-09-23-linux-shellscript-github-latest/) need not use this numeric syntax, so do not pass them through blindly. For interpreter selection, see the [POSIX sh function example](/en/posts/2023-09-20-linux-shellscript-function-error/).
