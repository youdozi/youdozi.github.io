---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2026-10-27-jenkins-home-backup-restore",
  "routeSlug": "2026-10-27-jenkins-home-backup-restore",
  "kind": "post",
  "title": "Sauvegarder Jenkins home et restaurer dans un nouveau volume",
  "description": "Tester une sauvegarde Jenkins avec master.key séparé, un nouveau volume et des contrôles HTTP, de marqueur et de mot de passe.",
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
  "draftSha256": "fbdffdd2bbf615624358f47ebe24d3b6e4e235ec34dd15bfb7dc4d26218174a6",
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
Vérifiez une sauvegarde en la restaurant dans un nouveau volume et en démarrant Jenkins depuis ce volume. La seule existence d’un fichier d’archive n’établit pas que le contrôleur peut l’utiliser.

Ce laboratoire arrête un contrôleur neuf, par ailleurs inutilisé, avant de copier son home. Il stocke master.key séparément de l’archive, restaure l’archive privée dans un autre volume nouvellement créé, démarre le même digest d’image et vérifie un marqueur ainsi que le mot de passe initial d’origine sans afficher aucune des deux valeurs de mot de passe. Il n’exerce ni contrôleur de production, ni job actif, ni migration de plugin.

## Arrêter, copier, restaurer et démarrer

![Arrêter le contrôleur du laboratoire, copier son volume et valider une restauration distincte](/assets/diagrams/technical/fr-2026-10-27-jenkins-home-backup-restore.svg)

Le [guide de sauvegarde Jenkins](https://www.jenkins.io/doc/book/system-administration/backing-up/) distingue le contenu sauvegardé de la validation de récupération. Cet exemple utilise une source arrêtée pour éviter de copier pendant que ce contrôleur écrit des fichiers. Ce n’est pas un instantané coordonné des bases externes, des agents ou d’autres processus d’écriture.

Utilisez le `jenkins_lab.py` complet du [laboratoire de recréation du contrôleur](/en/posts/2023-09-28-jenkins-docker-install/), puis enregistrez ce second fichier à côté. Python3 et un moteur Docker actif pour conteneurs Linux sont nécessaires.

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

Exécutez :

```sh
python3 jenkins_restore.py
```

Les conteneurs auxiliaires remplacent le point d’entrée par des outils de copie de fichiers ; ils ne démarrent donc pas un autre processus Jenkins. Ils s’exécutent en root uniquement pour préserver les propriétaires et permissions de la source pendant cette copie. La liste des membres de l’archive doit exclure master.key, et un auxiliaire distinct restaure cette clé avant le démarrage de Jenkins. Le volume source est monté en lecture seule après l’arrêt de son contrôleur ; la destination de restauration est un autre volume créé par ce laboratoire. Le digest d’image est celui sélectionné à l’entrée du laboratoire.

Un résultat réussi contient `sourceStopped`, `restoredToNewVolume`, `markerRestored`, `passwordRestored`, `masterKeyExcluded`, `keyCopiedSeparately` et `result: passed`. La restauration démarrée doit aussi satisfaire le contrôle de disponibilité HTTP de `DockerLab.start`. La correspondance du mot de passe initial vérifie que ce secret sélectionné a survécu ; elle ne teste pas une administration des utilisateurs finalisée ni tous les plugins de credentials.

## Traiter l’archive comme des données du contrôleur

C’est un exercice de récupération jetable. L’archive exclut `secrets/master.key` ; cette clé est copiée séparément et appliquée après l’extraction. Les autres secrets du contrôleur restent dans l’archive. Les deux répertoires temporaires sont privés et supprimés à la sortie. Ne téléversez pas cette archive comme artefact CI, ne la committez pas et n’utilisez pas cette copie regroupée comme politique de sauvegarde de production.

Pour la production, les [consignes Jenkins sur la clé du contrôleur](https://www.jenkins.io/doc/book/system-administration/backing-up/) imposent de traiter `master.key` séparément des sauvegardes ordinaires. Décidez de la récupération de clé, du chiffrement de l’archive, de la rétention, de l’accès, du stockage hors hôte et du traitement de l’état externe avant d’adopter un processus de sauvegarde. L’archive temporaire du laboratoire sur la même machine n’offre aucune de ces garanties de durabilité.

Le contrôleur restauré est aussi supprimé à la fin du laboratoire. Ce nettoyage permet de répéter l’exercice, mais un contrôle marqueur/secret/HTTP réussi ne démontre pas que chaque job, plugin, identifiant ou intégration externe peut être récupéré. Ajoutez des contrôles de charge représentative et de déchiffrement des secrets à une répétition planifiée de récupération du véritable système.
