---
{
  "state": "draft",
  "language": "ja",
  "translationKey": "2026-11-27-docker-desktop-mac-disk-space",
  "title": "Docker のキャッシュを消しても Mac の空き容量が変わらないのはなぜ？",
  "description": "回収可能なビルドキャッシュ、Docker.raw に割り当てられたブロック、Mac のボリュームの空き容量を個別に確認します。",
  "sourcePath": "src/content/posts/en/2026-11-27-docker-desktop-mac-disk-space.md",
  "sourceSha256": "22ef396043237437e56056391cb42357c8f9bc5784eef9279e396ccf768d1ecd"
}
---

Docker は仮想マシン内のイメージやキャッシュを集計し、回収可能な容量を表示します。macOS が計測するのはホストのファイルシステムの空き容量です。仮想マシンのディスクイメージ `Docker.raw` に割り当てたブロックも使用量に含まれます。ビルドキャッシュの項目を消しても、イメージと共有しているレイヤーはディスクに残ることがあります。 [Docker Desktop FAQ](https://docs.docker.com/desktop/troubleshoot-and-support/faqs/macfaqs/) · [Buildx du](https://docs.docker.com/reference/cli/docker/buildx/du/)

## それぞれの数値はどこで測る？

Mac で Docker Desktop を起動した状態で、ローカルのコンテキストとビルダーを確認します。一覧でアスタリスクが付いているのが選択中のビルダーです。

```sh
docker context show
docker buildx ls
docker system df -v
docker buildx du
df -k /
```

![エンジンの使用量、選択中のビルダーのキャッシュ、Mac のファイルシステムの空き容量を順番に確認します。](2026-11-27-docker-desktop-mac-disk-space.svg)

最初の使用量レポートではイメージ、コンテナ、ボリューム、ビルドキャッシュを確認します。次のレポートの `Reclaimable` は、選択中のビルダーで回収可能なキャッシュの容量です。最後のコマンドの `Available` は Mac のルートファイルシステムの空き容量で、単位は KiB です。 [Docker system df](https://docs.docker.com/reference/cli/docker/system/df/)

## Docker.raw が実際に占める容量は？

Docker Desktop の Settings → Resources → Advanced でディスクイメージの場所を確認し、例のパスを実際のファイルに合わせます。`ls -klsh` の先頭列は割り当て済み容量（KiB）、サイズ列は論理サイズです。別のボリュームにイメージを置いていても、最後のコマンドでそのファイルシステムの空き容量を確認できます。

```sh
image="$HOME/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw"
ls -klsh "$image"
stat -f 'bytes=%z blocks=%b' "$image"
df -k "$image"
```

ローカルの Mac で読み取り専用の確認を行ったところ、`desktop-linux` の回収可能なビルドキャッシュは 61.76 MB でした。ディスクイメージの論理サイズは 63,999,836,160 バイトで、実際に割り当てられたのは 12,272,488 ブロックです。各ブロックは 512 バイトなので、約 6.28 GB に相当します。

ビルドキャッシュだけを整理する場合は、まず選択中のビルダーを確認します。整理する直前と数分後に同じコマンドを実行すれば、数値を比較できます。今回はキャッシュを削除しておらず、Mac に戻った容量は測定していません。 [Buildx prune](https://docs.docker.com/reference/cli/docker/buildx/prune/)

[関連記事 · du と df で測った Mac のディスク整理](../2026-11-27-mac-disk-cleanup-du-df/)
