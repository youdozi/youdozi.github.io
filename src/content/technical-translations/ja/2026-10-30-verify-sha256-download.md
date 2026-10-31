---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2026-10-30-verify-sha256-download",
  "routeSlug": "2026-10-30-verify-sha256-download",
  "kind": "post",
  "title": "Python でダウンロードファイルの SHA-256 チェックサムを検証する",
  "description": "ストリーミング方式の Python 検証ツールで、ダウンロードファイルを信頼できる SHA-256 値と比較します。一致、変更、読み取り不能を明示的な終了コードで再現します。",
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
  "draftSha256": "a02472e4b5cee1b828fd8e7ab6960d10510fd9a9b321a0dc7a1763b7d9badb70",
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
ダウンロードファイルを検証するには、SHA-256 ダイジェストを計算し、信頼する配布元が示す期待値と比較します。Python の [hashlib](https://docs.python.org/3.11/library/hashlib.html) は、バイナリのバイト列をチャンク単位でハッシュ化できます。一致は、そのバイト列がその値に対応することを確認するだけで、配布元を認証したり、プログラムの安全性を証明したりはしません。Adoptium は[署名検証](https://adoptium.net/installation/gpg-verification)を別途説明しています。

## どのチェックサムと比較すればよいか

ダウンロードしたリリース、OS、CPU、アーカイブ形式と正確に対応するチェックサムを使います。[GitHub リリースの選択処理](/en/posts/2023-09-23-linux-shellscript-github-latest/)はアセットの URL を選び、[Temurin メタデータの例](/en/posts/2023-10-10-temurin-jdk21-delay/)はチェックサムの構文も確認します。どちらもダウンロードファイルをハッシュ化しません。Adoptium の[アーカイブからのインストール手順](https://adoptium.net/installation/archives)では、付属のチェックサムの取得方法を説明しています。

期待値は配布元の信頼できる配布経路から入手します。ダウンロードファイルから計算したダイジェストを、そのまま期待値として使っても、誤ったダウンロードは検出できません。攻撃者がファイルと公開チェックサムの両方を置き換えられる場合、一致しても真正性は確立しません。信頼できる配布元の鍵による署名検証は別の手順であり、この例の範囲外です。

## ファイルの検査はどう動くか

![チェックサムを検証し、ファイルをハッシュ化して結果を比較する](/assets/diagrams/technical/ja-2026-10-30-verify-sha256-download.svg)

期待値を検証し、変更されない通常ファイルをバイナリモードで開き、EOF までチャンク単位でダイジェストを更新して比較します。入力不正や読み取りエラーは 2、不一致は 1、一致した場合だけ 0 を返します。図ではチャンクのループを一つのステップにまとめています。検証中と、検証後に利用するまでの間にファイルを変更または置換しないでください。これは検証と実行を原子的に行うツールではありません。

## 追加パッケージなしで検証ツールを実行する

Python 3.11 以降を使用し、次を `verify-sha256.py` として保存します。以下のコマンドは POSIX シェルを使います。プログラムはローカルファイルを読むだけで、ダウンロード、展開、実行はしません。シンボリックリンクが通常ファイルを指していれば、そのリンクをたどります。大文字も含めた単一の 64 文字の 十六進数を受け付け、チェックサム一覧、ファイル名、URL は受け付けません。

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

`rb` は改行コードを含めた元のバイト列を保ちます。一回の読み取り要求は最大 1 MiB で、ファイル全体を読み込みません。不正なチェックサムはパスを開く前に拒否します。存在しないパス、ディレクトリ、読み取りエラーは、いずれもステータス 2 です。名前付きパイプとデバイスファイルは、通常ファイルという前提の範囲外です。

## 一致とファイルの変更を再現する

新しい空のディレクトリを使います。このテストデータでは、`sample.bin` に 三バイトの `abc`、`changed.bin` に `abcd` を書き込みます。コマンド内の固定ダイジェストは `abc` だけのものであり、JDK アーカイブのチェックサムではありません。

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

一致するファイルでは `OK` が出力されます。変更したファイルでは stderr に `MISMATCH` が出力され、最後のコマンドは `exit=1` を表示します。`set -e` を使う場合、想定した不一致には明示的な `if` などのエラー処理分岐が必要です。そうしないと、ステータスを表示する前にシェルが停止することがあります。

| ステータス | 意味 | 次の対応 |
| --- | --- | --- |
| 0 | ダイジェストが指定の期待値と一致 | 期待値が信頼できる出所のものなら続行する |
| 1 | ダイジェストが異なる | このファイルの使用を止め、選択したアセットとダウンロードを確認する |
| 2 | 引数、チェックサムの構文、またはファイル読み取りが不正 | 入力またはファイルへのアクセスを修正して再試行する |

不一致だけでは、破損、アセットの選択ミス、悪意ある置換のどれが原因かは特定できません。この検査は署名検証もマルウェアスキャンも行いません。
