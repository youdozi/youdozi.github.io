---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2023-09-28-jenkins-docker-install",
  "routeSlug": "2023-09-28-jenkins-docker-install",
  "kind": "post",
  "title": "Démarrer Jenkins avec Docker et vérifier la persistance des données",
  "description": "Figer une image Jenkins par digest, la démarrer localement et vérifier les données après remplacement du conteneur.",
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
  "draftSha256": "baaaf17473733e22adc4b19895212ddae10fa98b17fd1c7c4591715daea55a18",
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
Démarrez Jenkins avec un volume home nommé, vérifiez son point d’accès HTTP, puis recréez le conteneur avec le même volume. Atteindre un écran de configuration prouve que le contrôleur a démarré ; un second démarrage vérifie si ses données home survivent au remplacement du conteneur.

Un tag évolutif peut pointer plus tard vers une autre image. Résolvez l’image une seule fois pour l’expérience et gardez privé le mot de passe initial généré. Le laboratoire jetable rapporte les comparaisons sans afficher le mot de passe.

## Figer l’image pour une expérience

![Démarrer Jenkins sur loopback et vérifier les données après recréation](/assets/diagrams/technical/fr-2023-09-28-jenkins-docker-install.svg)

Utilisez Python3 et un moteur Docker exécutant des conteneurs Linux. Les [instructions de l’image Jenkins](https://github.com/jenkinsci/docker/blob/master/README.md) décrivent `jenkins/jenkins` et son répertoire home. Ce laboratoire part de `jenkins/jenkins:lts-jdk21`, télécharge l’image et résout son digest de dépôt. Chaque contrôleur de cette exécution utilise le digest au lieu de résoudre à nouveau le tag évolutif. Consignez le digest et la version Jenkins retournée pour reproduire une exécution ; le tag ne désigne pas une release permanente.

Le [comportement des ports publiés de Docker](https://docs.docker.com/engine/network/port-publishing/) détermine qui peut atteindre un port mappé. Le script demande `127.0.0.1::8080` afin que Docker choisisse un port hôte lié à loopback, puis vérifie la liaison annoncée. Il ne publie pas de port agent et ne monte pas le socket Docker. C’est un laboratoire local de contrôleur, pas une installation d’agents de construction Docker ou d’un service HTTPS distant.

## Exécuter le laboratoire complet

Enregistrez ce fichier complet sous `jenkins_lab.py`. Il crée son propre volume et ses conteneurs aux noms uniques. Le gestionnaire de contexte supprime ces ressources à la fin du test, y compris si un contrôle de disponibilité ou de données échoue. Ne substituez pas un volume de production dans cet exemple jetable.

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

Exécutez avec un démon Docker fonctionnel :

```sh
python3 jenkins_lab.py
```

Les deux démarrages du contrôleur attendent chacun jusqu’à 180 secondes un HTTP200 sur `/login`, un en-tête `X-Jenkins` et un corps contenant `Jenkins`. Les réinitialisations de connexion, échecs HTTP temporaires et échanges HTTP incomplets sont réessayés dans ce délai. Le test écrit un marqueur et lit le mot de passe initial en privé, remplace le premier conteneur, puis vérifie à nouveau ces deux valeurs. Un résultat avec `recreated`, `markerPersisted`, `passwordPersisted` et `result: passed` signifie que ces contrôles sélectionnés ont réussi. Le JSON consigne aussi le digest et la version Jenkins réelle, ce qui rend inutile une transcription inventée du téléchargement.

Le laboratoire ne déverrouille pas Jenkins, n’installe pas de plugins, ne crée pas de compte administrateur finalisé et n’exécute aucun job. Son contrôle de disponibilité concerne la réponse HTTP de connexion, et non la réussite de la configuration initiale. Sur un Mac sans moteur Docker actif, démarrez le moteur choisi avant l’exécution ; la CLI Docker seule ne peut pas exécuter le laboratoire.

## Séparer installation et persistance

Pour une installation interactive, suivez l’[assistant officiel de configuration](https://www.jenkins.io/doc/book/installing/docker/) et créez un compte administrateur. Lisez le mot de passe initial dans `/var/jenkins_home/secrets/initialAdminPassword` de votre propre contrôleur ; ne réutilisez pas une valeur d’exemple et ne publiez pas de journaux du contrôleur la contenant. Ce script nettoie délibérément son laboratoire ; ce n’est donc pas la commande permettant de conserver une installation interactive.

Un [volume Docker nommé](https://docs.docker.com/engine/storage/volumes/) peut survivre à la suppression d’un conteneur, mais ce n’est pas une sauvegarde : perdre le volume fait toujours perdre ses données. Le [laboratoire de sauvegarde et restauration d’un volume arrêté](/en/posts/2026-10-27-jenkins-home-backup-restore/) poursuit avec la même image et un autre volume cible. Pour la propre chaîne de publication de ce blog, consultez le [workflow Astro de Draft PR](/en/posts/2026-04-07-jekyll-github-actions-content-pipeline/) ; cet exemple Jenkins ne remplace pas cette chaîne.
