---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2026-10-30-verify-sha256-download",
  "routeSlug": "2026-10-30-verify-sha256-download",
  "kind": "post",
  "title": "用 Python 验证下载文件的 SHA-256 校验和",
  "description": "使用流式 Python 校验器，将下载文件与可信的 SHA-256 值进行比较。通过明确的退出码复现匹配、文件变更和无法读取的情况。",
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
  "draftSha256": "30d7ac0f17407e2a19a3bd10d308282436b685fa7196d55db760db630a34d093",
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
要验证下载文件，请计算其 SHA-256 摘要，并与可信发布者提供的预期值比较。Python 的 [hashlib](https://docs.python.org/3.11/library/hashlib.html) 可以分块对二进制字节进行哈希计算。匹配只说明这些字节与该值一致，并不能认证发布者身份或证明程序安全。Adoptium 另行提供了[签名验证](https://adoptium.net/installation/gpg-verification)文档。

## 应当比较哪个校验和？

使用与下载文件的具体发行版、操作系统、CPU 和归档格式对应的校验和。[GitHub 发布资源选择器](/en/posts/2023-09-23-linux-shellscript-github-latest/)用于选择资源 URL；[Temurin 元数据示例](/en/posts/2023-10-10-temurin-jdk21-delay/)还检查校验和语法。两者都不计算下载文件的哈希值。Adoptium 的[归档安装说明](https://adoptium.net/installation/archives)介绍了如何获取配套校验和。

通过发布者可信的分发渠道获取预期值。先对下载文件计算摘要，再把同一结果作为预期值，无法发现下载错误。如果攻击者能同时替换文件及其公布的校验和，二者匹配也无法确立真实性。使用可信发布者密钥验证签名是另一个步骤，不在本例范围内。

## 文件检查如何工作？

![验证校验和，对文件计算哈希并比较结果](/assets/diagrams/technical/zh-CN-2026-10-30-verify-sha256-download.svg)

先验证预期值，以二进制模式打开稳定的普通文件，分块更新摘要直至 EOF，然后比较。输入无效或读取错误返回 2；不匹配返回 1；只有匹配才返回 0。图中将分块循环概括为一个步骤。在验证期间，以及验证后使用文件之前，不要修改或替换文件。这不是将验证与执行合为原子操作的工具。

## 运行无需额外软件包的校验器

使用 Python 3.11 或更高版本，将以下内容保存为 `verify-sha256.py`。下面的命令使用 POSIX shell。程序只读取本地文件，不会下载、解压或运行它们。如果符号链接指向普通文件，程序会跟随该链接。它接受单个 64 字符的十六进制值，包括大写字母，不接受校验和清单、文件名或 URL。

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

`rb` 保留原始字节，包括换行符。每次读取最多请求 1 MiB，不会将整个文件加载到内存中。程序在打开路径前拒绝无效校验和。路径不存在、目录和读取错误都返回状态 2。命名管道和设备文件不属于普通文件约定的范围。

## 复现匹配和文件变更

使用一个新的空目录。此测试数据将 `sample.bin` 写为三个字节 `abc`，将 `changed.bin` 写为 `abcd`。命令中的固定摘要只属于 `abc`，不是 JDK 归档文件的校验和。

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

匹配的文件打印 `OK`。变更的文件向 stderr 打印 `MISMATCH`，最后一条命令打印 `exit=1`。使用 `set -e` 时，需要用明确的 `if` 或其他错误处理分支处理预期的不匹配，否则 shell 可能在打印状态之前停止。

| 状态 | 含义 | 下一步 |
| --- | --- | --- |
| 0 | 摘要与提供的预期值匹配 | 只有预期值来自可信来源时才继续 |
| 1 | 摘要不同 | 停止使用此文件；检查所选资源和下载过程 |
| 2 | 参数、校验和语法或文件读取无效 | 修正输入或文件访问后重试 |

仅凭不匹配，无法确定原因是损坏、选错资源还是恶意替换。此检查既不验证签名，也不扫描恶意软件。
