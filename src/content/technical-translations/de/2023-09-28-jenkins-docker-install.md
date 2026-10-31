---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2023-09-28-jenkins-docker-install",
  "routeSlug": "2023-09-28-jenkins-docker-install",
  "kind": "post",
  "title": "Jenkins mit Docker starten und persistente Daten prüfen",
  "description": "Ein Jenkins-Image per Digest fixieren, lokal starten und die Daten nach einem Containerwechsel prüfen.",
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
  "draftSha256": "1b742d07e7a4a38e9c20d1a3dae3b075c807c479af133129659ab4f146e7a600",
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
Starten Sie Jenkins mit einem benannten Home-Volume, prüfen Sie seinen HTTP-Endpunkt und erstellen Sie den Container anschließend mit demselben Volume neu. Das Erreichen einer Einrichtungsseite belegt den Start des Controllers; ein zweiter Start prüft, ob die Home-Daten einen Containerwechsel überstehen.

Ein fortlaufender Tag kann später auf ein anderes Image zeigen. Lösen Sie das Image für das Experiment einmal auf und halten Sie das erzeugte Initialpasswort geheim. Das temporäre Labor meldet Vergleiche, ohne das Passwort auszugeben.

## Das Image für ein Experiment fixieren

![Jenkins auf Loopback starten und Daten nach dem Neuerstellen prüfen](/assets/diagrams/technical/de-2023-09-28-jenkins-docker-install.svg)

Verwenden Sie Python3 und eine Docker-Engine für Linux-Container. Die [Anleitung zum Jenkins-Image](https://github.com/jenkinsci/docker/blob/master/README.md) beschreibt `jenkins/jenkins` und sein Home-Verzeichnis. Dieses Labor beginnt mit `jenkins/jenkins:lts-jdk21`, lädt das Image und löst seinen Repository-Digest auf. Jeder Controller dieses Durchlaufs verwendet den Digest, statt erneut den fortlaufenden Tag nachzuschlagen. Erfassen Sie zur Reproduktion den Digest und die zurückgegebene Jenkins-Version; der Tag bezeichnet keine dauerhaft festgelegte Version.

Dockers [Verhalten veröffentlichter Ports](https://docs.docker.com/engine/network/port-publishing/) bestimmt, wer einen zugeordneten Port erreichen kann. Das Skript fordert `127.0.0.1::8080` an, damit Docker einen an Loopback gebundenen Host-Port auswählt, und prüft anschließend die gemeldete Bindung. Es veröffentlicht weder einen Agent-Port noch bindet es den Docker-Socket ein. Dies ist ein lokales Controller-Labor, keine Installation von Docker-Build-Agenten oder eines entfernten HTTPS-Dienstes.

## Das vollständige Labor ausführen

Speichern Sie diese vollständige Datei als `jenkins_lab.py`. Sie erstellt eigene Volumes und Container mit eindeutigen Namen. Der Kontextmanager entfernt diese Laborressourcen nach Testende, auch wenn eine Bereitschafts- oder Datenprüfung scheitert. Setzen Sie in diesem temporären Beispiel kein Produktions-Volume ein.

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

Führen Sie dies mit funktionierendem Docker-Daemon aus:

```sh
python3 jenkins_lab.py
```

Beide Controller-Starts warten jeweils bis zu 180 Sekunden auf HTTP200 unter `/login`, einen Header `X-Jenkins` und einen Body mit `Jenkins`. Verbindungsabbrüche, vorübergehende HTTP-Fehler und unvollständige HTTP-Handshakes werden innerhalb dieser Frist erneut versucht. Der Test schreibt eine Markierung, liest das Initialpasswort intern, ersetzt den ersten Container und prüft beide Werte erneut. Ein Ergebnis mit `recreated`, `markerPersisted`, `passwordPersisted` und `result: passed` bedeutet, dass diese ausgewählten Prüfungen bestanden wurden. Das JSON erfasst außerdem Digest und tatsächliche Jenkins-Version; ein erfundenes Pull-Protokoll ist daher unnötig.

Das Labor entsperrt Jenkins nicht, installiert keine Plugins, erstellt kein fertiges Administratorkonto und führt keinen Job aus. Seine Bereitschaftsprüfung betrifft die HTTP-Antwort der Anmeldung, nicht die abgeschlossene Einrichtung. Starten Sie auf einem Mac ohne laufende Docker-Engine Ihre gewählte Engine vor der Ausführung; eine Docker-CLI allein kann das Labor nicht ausführen.

## Installation und Persistenz getrennt halten

Folgen Sie für eine interaktive Installation dem [offiziellen Einrichtungsassistenten](https://www.jenkins.io/doc/book/installing/docker/) und erstellen Sie ein Administratorkonto. Lesen Sie das Initialpasswort aus `/var/jenkins_home/secrets/initialAdminPassword` Ihres eigenen Controllers; verwenden Sie keinen Beispielwert und veröffentlichen Sie keine Controller-Logs, die es enthalten. Dieses Skript bereinigt sein Labor absichtlich und ist daher nicht der Befehl zum Beibehalten einer interaktiven Installation.

Ein [benanntes Docker-Volume](https://docs.docker.com/engine/storage/volumes/) kann das Löschen eines Containers überstehen, ist aber kein Backup: Geht das Volume verloren, gehen auch seine Daten verloren. Das [Labor zur Sicherung und Wiederherstellung eines gestoppten Volumes](/en/posts/2026-10-27-jenkins-home-backup-restore/) setzt dies mit demselben Image und einem anderen Ziel-Volume fort. Zur Veröffentlichungspipeline dieses Blogs siehe den [Astro-Draft-PR-Workflow](/en/posts/2026-04-07-jekyll-github-actions-content-pipeline/); dieses Jenkins-Beispiel ersetzt diese Pipeline nicht.
