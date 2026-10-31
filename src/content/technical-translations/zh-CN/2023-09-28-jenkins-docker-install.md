---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2023-09-28-jenkins-docker-install",
  "routeSlug": "2023-09-28-jenkins-docker-install",
  "kind": "post",
  "title": "Docker 中的 Jenkins：验证启动与容器重建",
  "description": "按镜像摘要运行一次性 Jenkins 控制器，检查回环 HTTP 就绪状态，并用同一卷重建容器，不记录初始密码。",
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
  "draftSha256": "e9a838de7f1f1414bb3fa8c6ee651b5d1b26b483c59ada2622791279d67e7e0e",
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

用命名 home 卷启动 Jenkins，验证 HTTP 端点，再使用同一卷重建容器。看到设置界面说明控制器已启动；第二次启动检查 home 数据是否在更换容器后保留。

滚动标签以后可能指向其他镜像。实验中只解析一次镜像，并保密生成的初始密码。一次性实验只报告比较结果，不打印密码。

## 为一次实验固定镜像

![启动回环 Jenkins 控制器并检查重建后的数据](/assets/diagrams/technical/zh-CN-2023-09-28-jenkins-docker-install.svg)

使用 Python3 和运行 Linux 容器的 Docker 引擎。[Jenkins 镜像说明](https://github.com/jenkinsci/docker/blob/master/README.md)介绍 `jenkins/jenkins` 及其 home 目录。本实验从 `jenkins/jenkins:lts-jdk21` 开始，拉取并解析仓库摘要。同一运行中的所有控制器都使用摘要，不再查询滚动标签。复现时记录摘要和返回的 Jenkins 版本；标签不指定永久版本。

Docker 的[端口发布行为](https://docs.docker.com/engine/network/port-publishing/)决定谁能访问映射端口。脚本请求 `127.0.0.1::8080`，让 Docker 选择绑定回环的主机端口，再检查报告的绑定。它不发布 agent 端口，也不挂载 Docker socket。这是本地控制器实验，不是 Docker 构建 agent 或远程 HTTPS 服务安装。

## 运行完整实验

将完整文件保存为 `jenkins_lab.py`。它创建唯一命名的卷与容器。上下文管理器在测试结束时清理这些实验资源，包括就绪检查或数据检查失败的情况。不要在此一次性示例中替换为生产卷。

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

在 Docker daemon 正常运行时执行：

```sh
python3 jenkins_lab.py
```

两次控制器启动各最多等待 180 秒，检查 `/login` 的 HTTP200、`X-Jenkins` 响应头及包含 `Jenkins` 的正文。连接重置、临时 HTTP 失败和未完成的 HTTP 握手会在时限内重试。测试写入标记并私下读取初始密码，更换第一个容器后再次检查两者。含有 `recreated`、`markerPersisted`、`passwordPersisted` 和 `result: passed` 的结果表示这些指定检查通过。JSON 还记录摘要和实际 Jenkins 版本，无需编造拉取记录。

实验不会解锁 Jenkins、安装插件、完成管理员账户创建或运行作业。就绪检查只针对登录 HTTP 响应，不代表初始化完成。Mac 上若没有运行中的 Docker 引擎，请先启动所选引擎；仅有 Docker CLI 无法执行实验。

## 区分安装与持久化

交互式安装请遵循[官方设置向导](https://www.jenkins.io/doc/book/installing/docker/)并创建管理员账户。从自己控制器的 `/var/jenkins_home/secrets/initialAdminPassword` 读取初始密码；不要复用示例值或公开包含密码的日志。本脚本会有意清理实验资源，并非保留交互式安装的命令。

[Docker 命名卷](https://docs.docker.com/engine/storage/volumes/)可在容器删除后保留，但不是备份；卷丢失仍会丢数据。[停止卷后的备份恢复实验](/en/posts/2026-10-27-jenkins-home-backup-restore/)用相同镜像和不同目标卷继续验证。本博客的发布流水线参见 [Astro Draft PR 工作流](/en/posts/2026-04-07-jekyll-github-actions-content-pipeline/)；此 Jenkins 示例不替代它。
