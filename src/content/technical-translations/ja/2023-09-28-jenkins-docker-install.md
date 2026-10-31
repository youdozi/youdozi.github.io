---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2023-09-28-jenkins-docker-install",
  "routeSlug": "2023-09-28-jenkins-docker-install",
  "kind": "post",
  "title": "Docker の Jenkins：起動とコンテナ再作成を確認する",
  "description": "イメージダイジェストで使い捨て Jenkins を起動し、ループバック HTTP の準備完了を確認して、初期パスワードを記録せず同じボリュームで再作成する。",
  "categories": [
    "jenkins"
  ],
  "tags": [
    "jenkins",
    "docker",
    "containers",
    "backup",
    "testing"
  ],
  "sourcePath": "src/content/posts/en/2023-09-28-jenkins-docker-install.md",
  "sourceSha256": "ed131abbe5537f6f1828891ac35483b44e96395c554a52b53f5c1ab6c4ff895e",
  "draftSha256": "7927722419d5a545b80330ef1bec576b934b3f8af6d3787bbe36ec304e4b6d0e",
  "manifestPath": ".pipeline/technical-translations/batch-125/manifest.json",
  "manifestSha256": "1934910c02dbe893b786124f1d296d7adf9efbe921d40b3d2cfbceb8f70b4b33",
  "publishedAt": "2026-10-31T15:35:43.034Z",
  "updatedAt": "2026-10-31T15:35:43.034Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 125,
    "approvedAt": "2026-10-31T15:35:43.034Z",
    "basis": "User explicitly requested applying all missing technical-post languages, review, verification and deployment on 2026-11-01, with standing PR merge authorization. Human approval denotes publication authorization; linguistic review is performed by AI, not human/native review."
  }
}
---

名前付きホームボリュームで Jenkins を起動し、HTTP を確認してから同じボリュームで再作成します。設定画面は起動の証拠で、二度目の起動は交換後のホームデータ保持を確認します。

可変タグは後に別イメージを指す場合があります。実験では一度だけ解決し、生成された初期パスワードを秘密にします。使い捨ての実験は比較結果だけを報告し、パスワードは出力しません。

## 一回の実験でイメージを固定する

![ループバックで Jenkins を起動し再作成後のデータを確認する](/assets/diagrams/technical/ja-2023-09-28-jenkins-docker-install.svg)

Python3 と Linux コンテナを動かす Docker エンジンを使います。[Jenkins イメージの手順](https://github.com/jenkinsci/docker/blob/master/README.md)に `jenkins/jenkins` とホームの説明があります。実験は `jenkins/jenkins:lts-jdk21` を取得しリポジトリのダイジェストを解決します。その実行内の全コントローラーはタグを再検索せず同じダイジェストを使います。再現時はダイジェストと応答した Jenkins の版を記録します。タグは永久的な版指定ではありません。

Docker の[ポート公開動作](https://docs.docker.com/engine/network/port-publishing/)が到達可能な相手を決めます。スクリプトは `127.0.0.1::8080` を指定し、ループバック上のホストポートを Docker に選ばせ、報告された割当を確認します。agent ポートや Docker ソケットは公開、マウントしません。ローカルの実験であり、Docker ビルド agent や遠隔 HTTPS サービスの導入ではありません。

## 完全な実験を実行する

完全なファイルを `jenkins_lab.py` に保存します。一意の名前のボリュームとコンテナを作り、準備完了やデータの検査が失敗しても、終了時にコンテキストマネージャーが削除します。この使い捨て例に本番ボリュームを指定しないでください。

### `jenkins_lab.py`

```python
import http.client
import json
import os
import subprocess
import time
import urllib.error
import urllib.request
import uuid


class DockerLab:
    def __init__(self):
        self.prefix = 'jenkins-proof-' + uuid.uuid4().hex[:12]
        self.containers, self.volumes = [], []

    def cli(self, *args):
        return subprocess.check_output(['docker', *args], text=True, stderr=subprocess.PIPE).strip()

    def volume(self):
        name = f'{self.prefix}-home-{len(self.volumes)}'
        existing = subprocess.run(['docker', 'volume', 'inspect', name], capture_output=True)
        if existing.returncode == 0:
            raise RuntimeError('Refusing an existing volume')
        self.cli('volume', 'create', name)
        self.volumes.append(name)
        return name

    def __enter__(self):
        self.cli('info')
        requested = os.environ.get('JENKINS_IMAGE', 'jenkins/jenkins:lts-jdk21')
        self.cli('pull', requested)
        self.image = self.cli('image', 'inspect', requested, '--format', '{{index .RepoDigests 0}}')
        if '@sha256:' not in self.image:
            raise RuntimeError('Expected a pulled repository digest')
        self.home = self.volume()
        return self

    def start(self, volume=None):
        name = f'{self.prefix}-controller-{len(self.containers)}'
        self.cli('run', '-d', '--name', name, '-p', '127.0.0.1::8080',
                 '--mount', f'type=volume,source={volume or self.home},target=/var/jenkins_home', self.image)
        self.containers.append(name)
        port = self.cli('port', name, '8080/tcp')
        if not port.startswith('127.0.0.1:'):
            raise RuntimeError('Expected a loopback binding')
        deadline = time.monotonic() + 180
        while time.monotonic() < deadline:
            try:
                with urllib.request.urlopen(f'http://{port}/login', timeout=5) as response:
                    self.version = response.headers.get('X-Jenkins')
                    if response.status == 200 and self.version and b'Jenkins' in response.read():
                        return name
            except (urllib.error.URLError, TimeoutError, ConnectionError, http.client.HTTPException):
                pass
            time.sleep(2)
        raise RuntimeError('Jenkins login was not ready within 180 seconds')

    def password(self, name):
        return self.cli('exec', name, 'cat', '/var/jenkins_home/secrets/initialAdminPassword')

    def marker(self, name):
        return self.cli('exec', name, 'cat', '/var/jenkins_home/lab-marker')

    def __exit__(self, *_):
        for name in reversed(self.containers):
            subprocess.run(['docker', 'rm', '-f', name], capture_output=True)
        for name in reversed(self.volumes):
            subprocess.run(['docker', 'volume', 'rm', name], capture_output=True)


if __name__ == '__main__':
    with DockerLab() as lab:
        first = lab.start()
        password = lab.password(first)
        assert password, 'Missing initial password'
        lab.cli('exec', first, 'sh', '-c', 'printf kept > /var/jenkins_home/lab-marker')
        lab.cli('rm', '-f', first)
        second = lab.start()
        assert lab.marker(second) == 'kept'
        assert lab.password(second) == password
        print(json.dumps({'image': lab.image, 'jenkins': lab.version, 'recreated': True,
                          'markerPersisted': True, 'passwordPersisted': True, 'result': 'passed'}))
```

Docker デーモンを動かして実行します。

```sh
python3 jenkins_lab.py
```

二回の起動ではそれぞれ最大 180 秒待ち、`/login` の HTTP200、`X-Jenkins` ヘッダー、`Jenkins` を含む本文を確認します。接続リセット、一時的な HTTP 失敗、不完全なハンドシェイクは期限内で再試行します。マーカーを書き、初期パスワードを非公開で読み、最初のコンテナを交換して両方を再確認します。`recreated`、`markerPersisted`、`passwordPersisted`、`result: passed` があれば、選んだ確認を通った意味です。JSON にダイジェストと実際の版も残るため、架空の取得ログは不要です。

実験はロック解除、プラグイン導入、管理者作成の完了、ジョブ実行をしません。ログイン HTTP 応答の準備完了であり、初期設定成功ではありません。Mac でエンジンが動いていなければ先に起動します。CLI だけでは実行できません。

## インストールと永続化を分ける

対話式の導入では[公式セットアップウィザード](https://www.jenkins.io/doc/book/installing/docker/)に従い管理者を作ります。自分のコントローラーの `/var/jenkins_home/secrets/initialAdminPassword` から初期パスワードを読み、例の値を使い回したり秘密を含むログを公開したりしません。このスクリプトは意図的に後片付けするため、対話環境を保持するコマンドではありません。

[Docker の名前付きボリューム](https://docs.docker.com/engine/storage/volumes/)はコンテナ削除後も残せますが、バックアップではなく、失えばデータも失います。[停止ボリュームのバックアップと復元実験](/en/posts/2026-10-27-jenkins-home-backup-restore/)は同じイメージと別の復元先で続けます。このブログの公開は [Astro Draft PR の流れ](/en/posts/2026-04-07-jekyll-github-actions-content-pipeline/)を参照してください。この Jenkins 例はその代替ではありません。
