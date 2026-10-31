---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2021-07-27-parse-yaml",
  "routeSlug": "2021-07-27-parse-yaml",
  "kind": "post",
  "title": "Shell から YAML を読む：ポートを検証し eval なしでコマンドを実行",
  "description": "Python と PyYAML で YAML ポートを型付きで読み、不正入力を拒否して、eval や shell コード生成なしで SERVER_PORT を子コマンドへ渡します。",
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
  "draftSha256": "0bac8e0a51d6436393498cf7430cde6d12405b24541e08dcb455fe1fe0f24d7c",
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
shell から `eval` なしで YAML のポートを読むには、[YAML パーサー](https://pyyaml.org/wiki/PyYAMLDocumentation#loading-yaml)を使って値の型と範囲を検証し、必要な変数だけを渡します。この例では Python と PyYAML で一つの `server.port` を読み、検証成功後にだけ子コマンドを起動します。sed/awk で YAML の文法全体を近似しないでください。

表示されたテキストだけでは YAML の整数 `8080` と文字列 `"8080"` を確実に区別できません。このローダーは**文字列を数値に変換しません**。解析結果が 1 から 65535 の整数である値だけを受け入れます。Python の bool は int のサブクラスなので、`isinstance(port, int)` と異なり `type(port) is int` は真偽値を拒否します。

## 処理の流れ

![整数のポートを解析・検証してから SERVER_PORT を export します。ローダーの失敗時は対象コマンドを開始せず、exec が対象の終了状態を保ちます。](/assets/diagrams/technical/ja-2021-07-27-parse-yaml.svg)

整数のポートを解析・検証してから SERVER_PORT を export します。ローダーの失敗時は対象コマンドを開始せず、exec が対象の終了状態を保ちます。

## 環境と入力

Python 3 と [PyYAML 6.0.3](https://pypi.org/project/PyYAML/6.0.3/) を使います。ローカル実行環境は Python 3.13 です。三つのファイルを同じディレクトリに保存し、専用の仮想環境に依存関係をインストールしてください。

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

## 検証済みの値でコマンドを起動する

```sh
PYTHON=.venv/bin/python sh run-with-port.sh application.yml \
  .venv/bin/python -c 'import os; print(os.environ["SERVER_PORT"])'
```

```text
8080
```

`read-port.py` は有効な値だけを stdout に、エラーを stderr に書きます。ファイル不足、不正 YAML、複数ドキュメント、マッピング以外の入力、フィールド不足、文字列、真偽値、浮動小数点数、範囲外の値を終了状態 2 で拒否します。`run-with-port.sh` は失敗を伝え、対象コマンドを開始しません。対象の開始後は `exec` がその終了状態を保ちます。

`"$@"` はコマンドと各引数を別々に保ちます。引数内の空白や `$()` が shell ソースとして再評価されることはありません。相対指定の `PYTHON` と設定ファイルのパスは呼び出し元の作業ディレクトリを基準とし、ラッパーは自身と同じ場所の `read-port.py` を使います。

export した変数は子プロセスに届き、呼び出し元の親 shell の環境は変更しません。ラッパーは source せず、`sh run-with-port.sh ...` で実行してください。アプリが実際に `SERVER_PORT` を読むことは別途確認が必要です。

## ローダーの適用範囲

[`safe_load`](https://pyyaml.org/wiki/PyYAMLDocumentation) は任意の Python オブジェクトを構築するタグを許可しませんが、アプリ固有の型・範囲チェックは必要です。この例には悪意ある巨大入力へのメモリー・時間制限がないため、信頼できるローカル設定を対象にします。

PyYAML の暗黙の型規則に従うため、`on` などは真偽値になり得ます。重複キーは拒否せず後の値が残る場合があるので、入力では禁止して別途検査してください。完全な YAML 1.2 の型ポリシーでも汎用の設定スキーマ検証器でもありません。追加フィールドごとに型と欠損時の方針を明示してください。

コマンド失敗と終了状態の扱いは [GitHub リリースの検索](/en/posts/2023-09-23-linux-shellscript-github-latest/)、JVM ジョブの永続化データ互換性は [Spring Batch 5 移行](/en/posts/2023-10-27-springbatch5-migration/)を参照してください。
