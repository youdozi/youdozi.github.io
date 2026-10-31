---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2026-10-27-jenkins-home-backup-restore",
  "routeSlug": "2026-10-27-jenkins-home-backup-restore",
  "kind": "post",
  "title": "Jenkins-Home sichern und in einem neuen Volume wiederherstellen",
  "description": "Eine Jenkins-Sicherung mit getrenntem master.key, neuem Volume und HTTP-, Markierungs- und Passwortprüfungen erproben.",
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
  "draftSha256": "cf86c4ed0bbf58aa72e3065d08ac66763b2dd82f18159b3ed90c6b9b5ea6b52f",
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
Prüfen Sie eine Sicherung, indem Sie sie in ein neues Volume wiederherstellen und Jenkins von diesem Volume starten. Die bloße Existenz einer Archivdatei belegt nicht, dass der Controller sie verwenden kann.

Dieses Labor stoppt einen frischen, ansonsten unbenutzten Controller, bevor es dessen Home kopiert. Es speichert master.key getrennt vom Archiv, stellt das private Archiv in einem weiteren neu erzeugten Volume wieder her, startet denselben Image-Digest und prüft eine Markierung sowie das ursprüngliche Initialpasswort, ohne einen der Passwortwerte auszugeben. Es prüft keinen Produktionscontroller, aktiven Job oder eine Plugin-Migration.

## Stoppen, kopieren, wiederherstellen und starten

![Laborcontroller stoppen, Volume kopieren und separate Wiederherstellung validieren](/assets/diagrams/technical/de-2026-10-27-jenkins-home-backup-restore.svg)

Der [Jenkins-Sicherungsleitfaden](https://www.jenkins.io/doc/book/system-administration/backing-up/) unterscheidet Sicherungsinhalt von Wiederherstellungsvalidierung. Dieses Beispiel verwendet eine gestoppte Quelle, um nicht zu kopieren, während dieser Controller Dateien schreibt. Es ist kein koordinierter Snapshot externer Datenbanken, Agenten oder anderer schreibender Prozesse.

Verwenden Sie die vollständige `jenkins_lab.py` aus dem [Labor zum Neuerstellen des Controllers](/en/posts/2023-09-28-jenkins-docker-install/) und speichern Sie diese zweite Datei daneben. Erforderlich sind Python3 und eine laufende Docker-Engine für Linux-Container.

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

Ausführen:

```sh
python3 jenkins_restore.py
```

Die Hilfscontainer überschreiben den Einstiegspunkt durch Dateikopierwerkzeuge und starten daher keinen weiteren Jenkins-Prozess. Sie laufen nur deshalb als root, um Eigentümer und Berechtigungen der Quelle beim Kopieren zu bewahren. Die Archivdateiliste muss master.key ausschließen; ein separater Helfer stellt diesen Schlüssel vor dem Jenkins-Start wieder her. Das Quell-Volume wird nach dem Stoppen seines Controllers schreibgeschützt eingebunden; das Wiederherstellungsziel ist ein anderes, von diesem Labor erzeugtes Volume. Der Image-Digest ist der beim Eintritt ins Labor gewählte.

Ein erfolgreiches Ergebnis enthält `sourceStopped`, `restoredToNewVolume`, `markerRestored`, `passwordRestored`, `masterKeyExcluded`, `keyCopiedSeparately` und `result: passed`. Die gestartete Wiederherstellung muss außerdem die HTTP-Bereitschaftsprüfung aus `DockerLab.start` bestehen. Der Vergleich des Initialpassworts prüft, ob dieses ausgewählte Geheimnis erhalten blieb; er prüft keine abgeschlossene Benutzerverwaltung und nicht jedes Credentials-Plugin.

## Das Archiv als Controllerdaten behandeln

Dies ist eine temporäre Wiederherstellungsübung. Das Archiv schließt `secrets/master.key` aus; dieser Schlüssel wird separat kopiert und nach der Archivextraktion angewendet. Andere Controllergeheimnisse bleiben im Archiv. Beide temporären Verzeichnisse sind privat und werden beim Beenden entfernt. Laden Sie dieses Archiv nicht als CI-Artefakt hoch, committen Sie es nicht und verwenden Sie diese gemeinsame Kopie nicht als Produktionssicherungsrichtlinie.

Für den Produktivbetrieb verlangt der [Jenkins-Leitfaden zum Controllerschlüssel](https://www.jenkins.io/doc/book/system-administration/backing-up/), `master.key` getrennt von regulären Sicherungen zu behandeln. Legen Sie Schlüsselwiederherstellung, Archivverschlüsselung, Aufbewahrung, Zugriff, externe Speicherung und Behandlung externen Zustands fest, bevor Sie einen Sicherungsprozess übernehmen. Das temporäre Archiv des Labors auf demselben Rechner bietet keine dieser Dauerhaftigkeitsgarantien.

Auch der wiederhergestellte Controller wird nach Laborende entfernt. Diese Bereinigung ermöglicht wiederholte Übungen; eine bestandene Markierungs-/Geheimnis-/HTTP-Prüfung belegt jedoch nicht, dass jeder Job, jedes Plugin, jede Zugangsinformation oder externe Integration wiederhergestellt werden kann. Ergänzen Sie repräsentative Last- und Entschlüsselungsprüfungen für Geheimnisse in einer geplanten Wiederherstellungsprobe des tatsächlichen Systems.
