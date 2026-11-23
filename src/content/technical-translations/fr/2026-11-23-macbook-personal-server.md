---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2026-11-23-macbook-personal-server",
  "routeSlug": "2026-11-23-macbook-personal-server",
  "kind": "post",
  "title": "Utiliser un MacBook comme serveur personnel sur un réseau privé",
  "description": "Testez un serveur HTTP local par un tunnel SSH et comprenez les limites de disponibilité du Mac.",
  "categories": [
    "tips"
  ],
  "tags": [
    "macos",
    "ssh",
    "home-server"
  ],
  "sourcePath": "src/content/posts/en/2026-11-23-macbook-personal-server.md",
  "sourceSha256": "9d4d027b764ef8bf01ccd259c0d9a651cbb6306532afced8de3af23db443416c",
  "draftSha256": "5e339e5d2b879684c8cb8023bb2d965c504d035cb8d20f39c256005e321abacf",
  "manifestPath": ".pipeline/technical-translations/batch-188/manifest.json",
  "manifestSha256": "0299e8051adcb92b1b0d8f83c7f973d232b9676d01fd9a79b6552df09c1e8612",
  "publishedAt": "2026-11-23T10:04:19.784Z",
  "updatedAt": "2026-11-23T10:04:19.784Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 188,
    "approvedAt": "2026-11-23T10:04:19.784Z",
    "basis": "Owner explicitly requested publication in eight languages; translations were self-reviewed without independent or native-speaker review."
  }
}
---

Un MacBook peut servir une courte démonstration de développement à un autre ordinateur sur un réseau privé de confiance, sans exposer de port HTTP sur ce réseau. Lancez un serveur HTTP temporaire sur l’interface de boucle locale du Mac, puis accédez-y par un transfert local SSH. Il s’agit d’un test, pas d’une configuration de service public permanent.

![La requête du client passe par un transfert local SSH vers le serveur HTTP local du Mac, qui renvoie le fichier de test.](/assets/diagrams/technical/fr-2026-11-23-macbook-personal-server.svg)

Le schéma résume la requête et la réponse ; l’authentification et le nettoyage sont décrits ci-dessous.

## Préparer l’accès

Utilisez deux ordinateurs sur un réseau privé que vous contrôlez. Un réseau partagé ou public peut contenir des appareils non fiables ; une adresse privée ne suffit pas à contrôler l’accès. Ne redirigez aucun port du routeur. Utilisez un compte macOS standard distinct pour cette tâche et ne lui donnez accès qu’aux fichiers nécessaires. Sur le Mac, ouvrez Réglages Système → Général → Partage → Connexion à distance, activez-la et choisissez « Seulement ces utilisateurs » pour autoriser ce compte. Laissez l’accès complet au disque désactivé pour les utilisateurs distants, sauf besoin distinct. Le panneau Connexion à distance affiche l’adresse SSH du Mac. Les réglages peuvent varier selon la version de macOS ou la gestion de l’appareil. [Apple : connexion à distance](https://support.apple.com/guide/mac-help/allow-a-remote-computer-to-access-your-mac-mchlp1066/mac)

Sur le client, créez une clé dédiée et choisissez une phrase secrète lorsque le programme le demande. Si le fichier existe déjà, ne l’écrasez pas ; choisissez un autre chemin libre et utilisez-le dans les commandes suivantes :

```sh
ssh-keygen -t ed25519 -f ~/.ssh/macbook_demo
```

Copiez la ligne de clé publique de `~/.ssh/macbook_demo.pub` vers le Mac par un canal de confiance. Sur le Mac, connecté localement avec le compte autorisé, exécutez les commandes ci-dessous, collez la ligne de clé publique et appuyez sur Ctrl-D sur une nouvelle ligne. La ligne est ajoutée à `~/.ssh/authorized_keys` sans supprimer les entrées existantes. Ne copiez jamais la clé privée.

```sh
umask 077
mkdir -p ~/.ssh
chmod 700 ~/.ssh
cat >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

Consultez [les clés autorisées OpenSSH](https://man.openbsd.org/sshd#AUTHORIZED_KEYS_FILE_FORMAT) et [ssh-keygen](https://man.openbsd.org/ssh-keygen).

Sur le Mac, relevez l’empreinte de la clé d’hôte dans un terminal local :

```sh
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
```

Sur le client, connectez-vous avec le compte autorisé et l’adresse affichée dans Connexion à distance ; `demo` et `192.168.1.20` sont des exemples à remplacer. Avant d’accepter la première connexion, comparez l’empreinte ED25519 affichée à celle relevée sur le Mac. Si elles diffèrent, arrêtez-vous et cherchez la cause. Un avertissement de changement de clé d’hôte doit aussi être examiné, pas accepté automatiquement. [Vérification de l’hôte OpenSSH](https://man.openbsd.org/ssh#VERIFYING_HOST_KEYS)

```sh
ssh -i ~/.ssh/macbook_demo -o HostKeyAlgorithms=ssh-ed25519 demo@192.168.1.20
```

Vérifiez que la connexion réussit, puis saisissez `exit`. Le mot de passe du compte peut toujours fonctionner : l’ajout d’une clé ne désactive pas l’authentification par mot de passe.

## Lancer un test et le transférer

Sur le Mac, dans un terminal connecté au compte autorisé, créez un répertoire temporaire vide, ajoutez un fichier sans données sensibles et lancez Python 3.7+. Le serveur se lie uniquement à l’adresse IPv4 de boucle locale du Mac. Gardez ce terminal ouvert.

```sh
sample_dir=$(mktemp -d)
printf 'home server test\n' > "$sample_dir/index.html"
python3 -m http.server 8000 --bind 127.0.0.1 --directory "$sample_dir"
```

Si le port 8000 est déjà utilisé, arrêtez-vous et choisissez un port libre dans les commandes du serveur et du transfert. Le serveur HTTP simple de Python sert aux tests, pas à la production ; il suit les liens symboliques, utilisez donc uniquement le répertoire de test vide et un fichier sans données sensibles. [Python http.server](https://docs.python.org/3/library/http.server.html)

Sur le client, ouvrez le tunnel dans un deuxième terminal et laissez-le ouvert :

```sh
ssh -N -o ExitOnForwardFailure=yes -i ~/.ssh/macbook_demo -L 127.0.0.1:18000:127.0.0.1:8000 demo@192.168.1.20
```

Dans un autre terminal du client, exécutez :

```sh
curl http://127.0.0.1:18000/
```

La sortie attendue est `home server test`. Le client se connecte à son propre port 18000 ; SSH transporte la requête jusqu’au Mac, où elle rejoint le port de boucle locale 8000. Si le tunnel échoue, vérifiez l’adresse, la liste des comptes autorisés, l’empreinte et la clé avant de réessayer. Si le tunnel démarre mais que curl échoue, vérifiez que le processus Python fonctionne encore et que les deux ports correspondent. `ExitOnForwardFailure` confirme la création de l’écouteur local, pas l’accès au serveur HTTP cible. [Transfert OpenSSH](https://man.openbsd.org/ssh#L)

Arrêtez le tunnel SSH avec Ctrl-C dans son terminal. Arrêtez Python avec Ctrl-C dans le terminal du Mac, puis supprimez uniquement le répertoire de test créé ci-dessus :

```sh
rm "$sample_dir/index.html"
rmdir "$sample_dir"
```

Supprimez la ligne de clé publique de l’exemple et désactivez Connexion à distance si elles ont été ajoutées uniquement pour cet exercice. Conservez les clés et réglages d’accès préexistants.

## Disponibilité et suite

L’extinction de l’écran et la mise en veille du Mac sont deux états différents. Fermer l’écran d’un ordinateur portable le met normalement en veille ; ne supposez pas qu’un écran fermé, le réveil réseau ou un changement d’alimentation maintiendra ce test en fonctionnement. Après un redémarrage avec FileVault, prévoyez qu’une personne puisse déverrouiller le Mac si nécessaire. Apple documente le déverrouillage de FileVault par SSH sous certaines conditions sur Apple Silicon avec macOS 26 ou une version ultérieure ; ne supposez pas que ces conditions sont réunies. [Apple : veille](https://support.apple.com/guide/mac-help/put-your-mac-to-sleep-or-wake-it-mh10330/mac) · [Apple : FileVault](https://support.apple.com/guide/security/managing-filevault-sec8447f5049/web)

Pour une démonstration ponctuelle, arrêtez le processus une fois terminé. Pour les fichiers, envisagez le partage de fichiers macOS et ses contrôles d’accès. Un service durable nécessite une configuration launchd distincte, des mises à jour, des sauvegardes et un plan de restauration ; un matériel dédié peut être plus adapté. Pour accéder au Mac hors du domicile, un VPN privé est une option à évaluer séparément ; il ne dispense pas de sécuriser le Mac et le service.

La réponse HTTP sur la boucle locale a été vérifiée localement avec un fichier et un processus temporaires ; la connexion SSH et le tunnel sont des étapes documentées pour le lecteur, et non une connexion testée à ce Mac.
