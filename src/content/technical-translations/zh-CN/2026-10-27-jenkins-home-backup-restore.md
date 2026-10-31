---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "zh-CN",
  "translationKey": "2026-10-27-jenkins-home-backup-restore",
  "routeSlug": "2026-10-27-jenkins-home-backup-restore",
  "kind": "post",
  "title": "Jenkins Home 备份：将停止的控制器恢复到新卷",
  "description": "停止实验控制器，将 master.key 排除在归档外并单独恢复，再检查新卷启动、标记和初始密码持久化。",
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
  "sourcePath": "src/content/posts/en/2026-10-27-jenkins-home-backup-restore.md",
  "sourceSha256": "f6fcbb37f82b9829ef3535f5fee0b0fdf0b7b0ebe4e8b4f96bb3f2ff104a59b4",
  "draftSha256": "a154f7726d113aad4061e0bd02f607926a1f808fba7b35f3654fa547a90f4e12",
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

将备份恢复至新卷并从该卷启动 Jenkins，才能验证备份。归档文件存在本身不证明控制器可使用它。

实验在复制 home 前停止一个新建且未用于其他用途的控制器，将 master.key 与归档分开保存，再将私有归档恢复到另一个新卷，用同一镜像摘要启动，检查标记和原始初始密码，且不打印任何密码值。它不测试生产控制器、运行中的作业或插件迁移。

## 停止、复制、恢复与启动

![停止实验控制器、复制卷并验证独立恢复](/assets/diagrams/technical/zh-CN-2026-10-27-jenkins-home-backup-restore.svg)

[Jenkins 备份指南](https://www.jenkins.io/doc/book/system-administration/backing-up/)区分备份内容与恢复验证。本例停止源控制器，避免复制期间控制器写文件，但它不是外部数据库、agent 或其他写入方的协调快照。

使用[控制器重建实验](/en/posts/2023-09-28-jenkins-docker-install/)中的完整 `jenkins_lab.py`，再将第二个文件保存在旁边。需要 Python3 及运行 Linux 容器的 Docker 引擎。

### `jenkins_restore.py`

```python
import json
import tempfile
from jenkins_lab import DockerLab

with DockerLab() as lab, \
        tempfile.TemporaryDirectory(prefix='jenkins-private-backup-') as backup, \
        tempfile.TemporaryDirectory(prefix='jenkins-private-key-') as keys:
    original = lab.start()
    password = lab.password(original)
    assert password, 'Missing initial password'
    lab.cli('exec', original, 'sh', '-c', 'printf restored > /var/jenkins_home/lab-marker')
    lab.cli('stop', '-t', '30', original)
    lab.cli('run', '--rm', '--user', '0:0', '--entrypoint', 'sh',
            '--mount', f'type=volume,source={lab.home},target=/source,readonly',
            '--mount', f'type=bind,source={backup},target=/backup',
            '--mount', f'type=bind,source={keys},target=/keys', lab.image,
            '-c', 'set -e; umask 077; tar -C /source --exclude=./secrets/master.key -czpf /backup/home.tgz .; cp -p /source/secrets/master.key /keys/master.key')
    members = lab.cli('run', '--rm', '--user', '0:0', '--entrypoint', 'tar',
                      '--mount', f'type=bind,source={backup},target=/backup,readonly', lab.image,
                      '-tzf', '/backup/home.tgz')
    assert './secrets/master.key' not in members.splitlines()
    restored_home = lab.volume()
    lab.cli('run', '--rm', '--user', '0:0', '--entrypoint', 'tar',
            '--mount', f'type=bind,source={backup},target=/backup,readonly',
            '--mount', f'type=volume,source={restored_home},target=/restore', lab.image,
            '-xzpf', '/backup/home.tgz', '-C', '/restore')
    lab.cli('run', '--rm', '--user', '0:0', '--entrypoint', 'cp',
            '--mount', f'type=bind,source={keys},target=/keys,readonly',
            '--mount', f'type=volume,source={restored_home},target=/restore', lab.image,
            '-p', '/keys/master.key', '/restore/secrets/master.key')
    restored = lab.start(restored_home)
    assert lab.marker(restored) == 'restored'
    assert lab.password(restored) == password
    print(json.dumps({'image': lab.image, 'jenkins': lab.version, 'sourceStopped': True,
                      'restoredToNewVolume': True, 'masterKeyExcluded': True, 'keyCopiedSeparately': True, 'markerRestored': True,
                      'passwordRestored': True, 'result': 'passed'}))
```

运行：

```sh
python3 jenkins_restore.py
```

辅助容器将入口点替换为文件复制工具，不启动另一个 Jenkins 进程。仅为复制时保留源所有者与权限而以 root 运行。归档成员列表必须不含 master.key；独立辅助容器在 Jenkins 启动前恢复该密钥。源控制器停止后，源卷以只读挂载；目标是实验创建的另一卷。镜像摘要是在进入实验时选定的摘要。

成功结果包含 `sourceStopped`、`restoredToNewVolume`、`markerRestored`、`passwordRestored`、`masterKeyExcluded`、`keyCopiedSeparately` 和 `result: passed`。恢复后的启动还必须满足 `DockerLab.start` 的 HTTP 就绪检查。初始密码匹配只说明该指定秘密保留，并不测试完整用户管理或所有凭据插件。

## 将归档视为控制器数据

这是一次性恢复演练。归档不含 `secrets/master.key`；密钥单独复制，在解包后恢复。其他控制器秘密仍在归档中。两个临时目录均私有且退出时删除。不要将归档上传为 CI 产物或提交，也不要将此一体式复制用作生产备份策略。

生产环境中，[Jenkins 控制器密钥指南](https://www.jenkins.io/doc/book/system-administration/backing-up/)要求将 `master.key` 与常规备份分开处理。采用备份流程前应决定密钥恢复、归档加密、保留期、访问、异机存储及外部状态处理。本实验同机临时归档不提供这些持久性保证。

实验结束时也会移除恢复的控制器，便于重复演练。但标记、秘密和 HTTP 检查通过不证明所有作业、插件、凭据和外部集成都可恢复。实际系统的恢复演练应添加代表性工作负载与秘密解密检查。
