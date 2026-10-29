---
language: "zh-CN"
translationKey: "2023-09-20-linux-shellscript-function-error"
title: "修复 Shell 的 function 警告：POSIX sh 与 Bash"
description: "修复非标准 function 关键字警告，明确选择 POSIX sh 或 Bash，并检查带引号的参数和函数返回状态。"
state: "draft"
sourcePath: "src/content/posts/en/2023-09-20-linux-shellscript-function-error.md"
sourceSha256: "06ada98f4723e3b70cb188c01cc5efe1f31f9a724392b8e273b665663b5a73f8"
---
在 `#!/bin/sh` 脚本中，应使用 `hello() { ...; }` 声明函数，不使用 `function` 关键字。如果脚本需要 Bash 语法，就选择 Bash 并用相应方式调用。执行 `sh script.sh` 不会遵循文件中的 Bash shebang。

[ShellCheck SC2112](https://www.shellcheck.net/wiki/SC2112)指出，`function` 不属于 POSIX sh 语法。某个 `/bin/sh` 实现接受它，并不能证明脚本具有可移植性。

## 处理流程

![实际调用的解释器负责解析函数。示例检查是否只有一个参数，并通过引号保留参数中的空格和通配符。](2023-09-20-linux-shellscript-function-error.svg)

实际调用的解释器负责解析函数。示例检查是否只有一个参数，并通过引号保留参数中的空格和通配符。

## 为所选 Shell 编写函数

将代码保存为 `greet.sh`。为 `"$1"` 和 `"$@"` 加引号，可保留参数中的空格和通配符。

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

输出分别为 `Hello, Ada Lovelace` 和 `Hello, Ada *`。`sh -n` 只检查语法，因此还应实际执行脚本。参数缺失或过多时，会向 stderr 输出用法说明，并以状态 2 退出。参数有效时，状态为 0。

## 区分 shebang 与显式指定的解释器

| 调用方式 | 解释器的选择 |
| --- | --- |
| `sh greet.sh NAME` | 由调用的 `sh` 读取文件。 |
| `bash greet.sh NAME` | 由 Bash 读取文件。 |
| `chmod +x greet.sh`，然后 `./greet.sh NAME` | 此方式使用文件中的 shebang。 |

对于 Bash 数组或 `[[ ... ]]`，应使用 `#!/usr/bin/env bash`，并执行 `bash script.sh` 或可执行文件 `./script.sh`。执行 `sh script.sh` 时，不应期待它支持 Bash 语法。参阅 [ShellCheck 关于选择 Shell 的说明](https://www.shellcheck.net/wiki/SC2112)。

函数的 `return` 会把控制权和状态交还给调用者。`exit` 则终止正在运行的 Shell。这里函数调用是最后一条命令，因此函数状态成为脚本的退出状态。

示例已检查含空格和通配符的参数，以及无效的参数数量。不同 `/bin/sh` 实现之间存在差异，因此也应在部署所用的 Shell 上测试。下一步自动化可参阅[数字版本比较](/en/posts/2023-11-17-linux-shellscript-version-compare/)或 [GitHub 发布版本查询](/en/posts/2023-09-23-linux-shellscript-github-latest/)，这两类任务同样需要关注输入和失败状态。
