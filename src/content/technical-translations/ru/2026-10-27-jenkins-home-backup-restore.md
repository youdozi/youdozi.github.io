---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ru",
  "translationKey": "2026-10-27-jenkins-home-backup-restore",
  "routeSlug": "2026-10-27-jenkins-home-backup-restore",
  "kind": "post",
  "title": "Резервная копия Jenkins Home: восстановление в новый том",
  "description": "Остановите тестовый контроллер, исключите master.key из архива, восстановите ключ отдельно и проверьте новый том, маркер и сохранность начального пароля.",
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
  "draftSha256": "a78e0f9b333cabbbf4ffffb3c9a9fbb2c77264f64f5e2e45d322ba8cdcf2630f",
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

Проверьте резервную копию восстановлением в новый том и запуском Jenkins с него. Само наличие архива не подтверждает, что контроллер сможет его использовать.

Лаборатория останавливает новый, иначе не использовавшийся контроллер перед копированием home. Она хранит master.key отдельно, восстанавливает приватный архив в другой новый том, запускает тот же digest и сверяет маркер и исходный начальный пароль, не печатая ни одного значения пароля. Она не проверяет производственный контроллер, активное задание или миграцию плагинов.

## Остановите, скопируйте, восстановите и запустите

![Остановка контроллера, копирование тома и отдельная проверка восстановления](/assets/diagrams/technical/ru-2026-10-27-jenkins-home-backup-restore.svg)

[Руководство резервирования Jenkins](https://www.jenkins.io/doc/book/system-administration/backing-up/) отличает содержимое копии от проверки восстановления. Остановленный источник исключает копирование во время записи этим контроллером. Это не согласованный snapshot внешних БД, агентов или других пишущих процессов.

Используйте полный `jenkins_lab.py` из [лаборатории пересоздания контроллера](/en/posts/2023-09-28-jenkins-docker-install/), затем сохраните рядом второй файл. Нужны Python3 и работающий Docker engine с Linux-контейнерами.

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

Выполните:

```sh
python3 jenkins_restore.py
```

Вспомогательные контейнеры заменяют entrypoint инструментами копирования, не запуская другой Jenkins. Они работают от root только для сохранения владельцев и прав источника при копировании. Список архива должен исключать master.key; отдельный помощник восстанавливает ключ до запуска Jenkins. Исходный том монтируется только для чтения после остановки; целевой — другой том этой лаборатории. Digest выбран при входе в лабораторию.

Успех содержит `sourceStopped`, `restoredToNewVolume`, `markerRestored`, `passwordRestored`, `masterKeyExcluded`, `keyCopiedSeparately` и `result: passed`. Запущенное восстановление также должно пройти HTTP-проверку `DockerLab.start`. Совпадение начального пароля подтверждает сохранность выбранного секрета, а не завершённое управление пользователями или все плагины credentials.

## Относитесь к архиву как к данным контроллера

Это временное упражнение восстановления. Архив исключает `secrets/master.key`; ключ копируется отдельно и применяется после распаковки. Остальные секреты контроллера остаются в архиве. Оба временных каталога приватны и удаляются при выходе. Не загружайте архив как CI-артефакт, не коммитьте и не используйте эту объединённую копию как производственную политику.

В производстве [руководство Jenkins по ключу](https://www.jenkins.io/doc/book/system-administration/backing-up/) требует обрабатывать `master.key` отдельно от обычных копий. До внедрения определите восстановление ключа, шифрование архива, хранение, доступ, внешнее размещение и внешнее состояние. Временный архив той же машины не даёт этих гарантий долговечности.

Восстановленный контроллер также удаляется после лаборатории. Это позволяет повторять упражнения, но успешные маркер, секрет и HTTP не доказывают восстановление всех заданий, плагинов, credentials и интеграций. Добавьте представительные нагрузки и расшифровку секретов в запланированную репетицию реальной системы.
