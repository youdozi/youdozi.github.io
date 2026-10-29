---
title: "Fix the Shell function Warning: POSIX sh vs Bash"
language: "en"
translationKey: "2023-09-20-linux-shellscript-function-error"
routeSlug: "2023-09-20-linux-shellscript-function-error"
kind: "post"
publishedAt: "2026-10-27T02:36:39+00:00"
categories: ["linux"]
tags: ["linux", "bash", "shell script", "function"]
updatedAt: 2026-10-27T05:23:47.316+00:00
reviewedAt: "2026-10-27"
reviewStatus: "revised"
reviewScope: "Primary documentation checked; published runnable example verified."
reviewSources: ["https://www.shellcheck.net/wiki/SC2112"]
description: "Fix the non-standard function keyword warning, choose POSIX sh or Bash explicitly, and test quoted arguments and function return codes."
---
In a `#!/bin/sh` script, declare a function as `hello() { ...; }`, without the `function` keyword. If the script needs Bash syntax, select Bash and invoke it accordingly. Calling `sh script.sh` does not follow a Bash shebang in that file.

[ShellCheck SC2112](https://www.shellcheck.net/wiki/SC2112) explains that `function` is not POSIX sh syntax. A particular `/bin/sh` implementation accepting it does not establish portability.

## Processing flow

![Choose shell, preserve arguments workflow](/assets/diagrams/2023-09-20-linux-shellscript-function-error-en.svg)

The invoked interpreter parses the function. The example validates one argument and preserves spaces and wildcard characters through quoting.

## Write a function for the selected shell

Save this as `greet.sh`. Quoting `"$1"` and `"$@"` preserves spaces and wildcard characters in arguments.

### `greet.sh`

```sh
#!/bin/sh
set -eu

greet() {
    if [ "$#" -ne 1 ]; then
        printf '%s\n' 'usage: greet.sh NAME' >&2
        return 2
    fi
    printf 'Hello, %s\n' "$1"
}

greet "$@"
```

```sh
sh -n greet.sh
sh greet.sh 'Ada Lovelace'
sh greet.sh 'Ada *'
```

The outputs are `Hello, Ada Lovelace` and `Hello, Ada *`. `sh -n` checks syntax only, so also execute the script. Missing or extra arguments produce usage text on stderr and exit status 2. A valid argument produces status 0.

## Distinguish the shebang from an explicit interpreter

| Invocation | Interpreter selection |
| --- | --- |
| `sh greet.sh NAME` | The invoked `sh` reads the file. |
| `bash greet.sh NAME` | Bash reads it. |
| `chmod +x greet.sh`, then `./greet.sh NAME` | This execution uses the file's shebang. |

For Bash arrays or `[[ ... ]]`, use `#!/usr/bin/env bash` and run `bash script.sh` or the executable `./script.sh`. Do not expect Bash syntax when invoking `sh script.sh`. [ShellCheck's shell-selection explanation](https://www.shellcheck.net/wiki/SC2112).

A function's `return` passes control and a status back to its caller. `exit` terminates the running shell. Here the function is the final command, so its status becomes the script's exit status.

The example was checked with spaced and wildcard arguments and invalid argument counts. `/bin/sh` implementations differ, so test on the deployment shell too. For the next automation step, see [numeric version comparison](/en/posts/2023-11-17-linux-shellscript-version-compare/) or [GitHub release lookup](/en/posts/2023-09-23-linux-shellscript-github-latest/), where inputs and failure statuses also matter.
