---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2021-07-27-parse-yaml",
  "routeSlug": "2021-07-27-parse-yaml",
  "kind": "post",
  "title": "从 Shell 读取 YAML：验证端口并在不用 eval 的情况下执行命令",
  "description": "使用 Python 与 PyYAML 按类型读取 YAML 端口，拒绝无效输入，并将 SERVER_PORT 传给子命令，不使用 eval 或生成 shell 代码。",
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
  "draftSha256": "41ca7077c354d177faf6e7ac07730dbe62b86ffc38f9a415c2d09ff1fe8c95ec",
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
要从 shell 读取 YAML 端口且不用 `eval`，应使用 [YAML 解析器](https://pyyaml.org/wiki/PyYAMLDocumentation#loading-yaml)，验证值的类型与范围，并只传递需要的变量。本例使用 Python 与 PyYAML 读取一个 `server.port` 值，只有验证成功才启动子命令。不要用 sed/awk 近似实现 YAML 的完整语法。

只检查渲染后的文本，无法可靠区分 YAML 整数 `8080` 与字符串 `"8080"`。此加载器**不会将字符串强制转换为数字**：只接受解析为 1 至 65535 之间整数的值。Python 的 bool 是 int 的子类，因此 `type(port) is int` 会拒绝布尔值，而 `isinstance(port, int)` 不会。

## 处理流程

![先解析并验证整数端口，再导出 SERVER_PORT。加载器失败会阻止目标命令启动；exec 保留目标的退出状态。](/assets/diagrams/technical/zh-CN-2021-07-27-parse-yaml.svg)

先解析并验证整数端口，再导出 SERVER_PORT。加载器失败会阻止目标命令启动；exec 保留目标的退出状态。

## 环境与输入

使用 Python 3 与 [PyYAML 6.0.3](https://pypi.org/project/PyYAML/6.0.3/)。本地执行环境使用 Python 3.13。将这三个文件保存到同一目录，并在独立虚拟环境中安装依赖。

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

## 使用验证后的值启动命令

```sh
PYTHON=.venv/bin/python sh run-with-port.sh application.yml \
  .venv/bin/python -c 'import os; print(os.environ["SERVER_PORT"])'
```

```text
8080
```

`read-port.py` 只将有效值写入 stdout，将错误写入 stderr。对于文件缺失、无效 YAML、多文档、非映射输入、字段缺失、字符串、布尔值、浮点数与越界值，它以状态 2 拒绝输入。`run-with-port.sh` 传播该失败，不启动目标命令。目标启动后，`exec` 保留其退出状态。

`"$@"` 分别保留命令及每个参数。参数中的空格或 `$()` 不会被再次当作 shell 源码求值。相对 `PYTHON` 路径与配置路径以调用者的工作目录为基准，包装脚本则在自身旁边定位 `read-port.py`。

导出的变量传至子进程，不改变调用它的父 shell 环境。用 `sh run-with-port.sh ...` 运行包装脚本，不要 source 它。另行确认应用确实读取 `SERVER_PORT`。

## 加载器的适用范围

[`safe_load`](https://pyyaml.org/wiki/PyYAMLDocumentation) 不允许使用构造任意 Python 对象的标签，但仍需进行应用特定的类型与范围检查。本例没有限制恶意超大输入的内存与运行时间，因此只面向可信的本地配置。

它遵循 PyYAML 的隐式类型规则：`on` 等值可能变为布尔值。它不拒绝重复键，后一个值可能被保留；应在输入中禁止重复键，并单独检查。这既不是完整的 YAML 1.2 类型策略，也不是通用配置模式验证器。每个新增字段都应明确类型与缺失值策略。

命令失败与退出状态处理可参阅[查询 GitHub 发行版](/en/posts/2023-09-23-linux-shellscript-github-latest/)。JVM 作业持久化数据的兼容性可参阅 [Spring Batch 5 迁移](/en/posts/2023-10-27-springbatch5-migration/)。
