---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2026-11-13-pickle-ai-security",
  "routeSlug": "2026-11-13-pickle-ai-security",
  "kind": "post",
  "title": "Fonctionnement de Pickle AI : contrôle des apps iPhone et limites de protection des mots de passe",
  "description": "Sources officielles et code sur le navigateur, l’API et Credential Enclave de Pickle : comparer les limites des jetons OAuth et des mots de passe Vault.",
  "categories": [
    "security"
  ],
  "tags": [
    "pickle-ai",
    "ai-agent",
    "ios",
    "credentials",
    "nitro-enclaves"
  ],
  "sourcePath": "src/content/posts/en/2026-11-13-pickle-ai-security.md",
  "sourceSha256": "4973bca9ea9b81ec4e068b4f530a2b82742c427074c36836639b0c2db1a811e2",
  "draftSha256": "91a4a70db997832a55c823c8ee63ce93b20032e40a2303bb89529a339f94970a",
  "manifestPath": ".pipeline/technical-translations/batch-156/manifest.json",
  "manifestSha256": "ed48dc20825daff8725d8eba3418b1ad885276b52c9752ba958f7a1705b24430",
  "publishedAt": "2026-11-14T15:16:43.783Z",
  "updatedAt": "2026-11-14T15:16:43.783Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 158,
    "approvedAt": "2026-11-14T15:16:43.783Z",
    "basis": "User requested all 63 language editions and instructed completed PRs to be merged; AI translation and independent AI review were performed, with no claim of human text review."
  }
}
---

**Les explications officielles de Pickle AI décrivent des tâches exécutées par un navigateur distinct et des comptes connectés, plutôt qu’une manipulation directe des écrans d’autres apps iPhone.** Les mots de passe sont chiffrés séparément du modèle, mais la limite de protection des valeurs réellement utilisées pour se connecter diffère entre OAuth et les mots de passe de sites.

Le sujet est [Pickle](https://pickle.com/), un agent IA personnel de Pickle, Inc. Cette analyse utilise l’aide officielle consultée le 13 novembre 2026 et le code public `credential-enclave` au **commit `cff16a343bf5bb7953e5b65df6ab3600107e127d`**. J’ai exécuté la vérification de version du programme de sécurité public ; il ne s’agit pas d’un audit de l’application iOS installée ni de tout le serveur de production.

## Appuie-t-il réellement sur d’autres apps iPhone ?

L’[aide sur les connexions enregistrées](https://www.pickle.com/help/connect/save-login) indique que le navigateur de Pickle est séparé du téléphone et ne peut pas utiliser directement les identifiants enregistrés sur celui-ci. Le [guide de délégation](https://www.pickle.com/help/tasks/delegate) décrit aussi les tâches effectuées sur des sites dans un vrai navigateur et poursuivies après fermeture de l’app.

Une commande ou une réservation effectuée ne prouve donc pas à elle seule que l’écran d’une app de commerce installée a été touché. Les sources publiques étayent les chemins suivants :

| Chemin | Éléments vérifiés et sens |
| --- | --- |
| Navigateur séparé | Connexion aux sites et remplissage de formulaires, indépendamment des écrans d’app du téléphone |
| API de compte connecté | Le code public `forward` joint des identifiants aux requêtes autorisées vers l’API du fournisseur |
| Appel téléphonique | Le guide officiel décrit les appels passés pour les tâches impossibles sur le web |

Apple explique aussi le [bac à sable des apps tierces](https://support.apple.com/en-gb/guide/security/sec15bfe098e/web) et limite l’accès aux autres informations aux services fournis par iOS. Cela n’exclut pas toute automatisation, mais je n’ai trouvé aucune preuve que Pickle contourne le bac à sable pour contrôler d’autres apps.

Les éléments disponibles ne permettent pas d’établir quels outils DOM ou modèles de reconnaissance d’écran utilise le navigateur de Pickle, ni quel chemin est choisi pour chaque tâche. Le fonctionnement présenté ici est une analyse reliant les indications officielles et le chemin public des identifiants.

## Comment se connecter sans donner le mot de passe à l’IA ?

Même si le modèle ne produit jamais directement la chaîne du mot de passe, un exécutant séparé peut recevoir la valeur nécessaire et la saisir dans un formulaire. L’[explication de confidentialité](https://www.pickle.com/privacy) de Pickle indique que les mots de passe et valeurs de carte sont chiffrés sur l’appareil et cachés dans les résultats reçus par le modèle. Il faut confronter les limites techniques de cette explication au code public.

![Lors de la configuration, l’iPhone crée des clés et délègue une clé utilisateur chiffrée à une Enclave vérifiée. Lors de l’utilisation, la délégation active et l’enregistrement chiffré sont vérifiés ; après confirmation du journal, deux chemins se séparent. Le jeton OAuth est utilisé dans le nœud pour l’API, mais les mots de passe et cartes Vault sont envoyés en clair au worker par release pour un formulaire web. Le masquage ultérieur est une autre limite.](/assets/diagrams/technical/fr-2026-11-13-pickle-ai-security.svg)

Le haut du schéma représente la délégation préalable de clé à la configuration ; le bas représente l’utilisation des identifiants pendant la validité de cette délégation. Cela ne signifie pas que le téléphone doive envoyer une nouvelle clé à chaque connexion. Le schéma ne reproduit pas non plus toute l’implémentation de l’exécutant.

### Clés de l’appareil et enregistrements chiffrés

Le [protocole public](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/docs/protocol.md#3-keys) prévoit qu’une clé maîtresse créée sur l’appareil est conservée dans iCloud Keychain, puis que des clés distinctes sont dérivées pour la signature, le déchiffrement des journaux et les identifiants. Les enregistrements sont chiffrés avec ChaCha20-Poly1305 ; un contexte tel que le compte et le type d’enregistrement est aussi lié à l’authentification.

L’appareil vérifie l’attestation et la clé publique du nœud, puis chiffre et délègue la **clé utilisateur dérivée** à ce nœud. L’attestation distante vérifie à quel environnement d’exécution mesuré appartient une clé publique. [AWS Nitro Enclaves](https://docs.aws.amazon.com/enclaves/latest/user/) isolent leur mémoire du serveur parent et ne fournissent ni réseau externe direct ni stockage persistant. Un nœud Pickle utilise des communications relayées par l’hôte ; cela ne lui donne pas pour autant le droit de déchiffrer.

La clé utilisateur déléguée est utilisée dans la mémoire du nœud pendant une durée limitée. La [description publique de l’architecture](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/README.md#structure) fixe la délégation à 30 jours maximum. Le Keychain de l’appareil et la Nitro Enclave du serveur sont deux couches de protection distinctes.

### Les jetons OAuth sont utilisés dans le nœud

Le [code de transfert API](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/enclave/src/api/forward.rs) vérifie une délégation active, ouvre l’enregistrement OAuth et prépare une requête autorisée vers le fournisseur. Il l’exécute après confirmation de l’enregistrement du journal d’utilisation. Ce chemin effectue une requête authentifiée au lieu de transmettre le jeton au modèle.

Mais **cacher un jeton et cacher les données lues avec ce jeton sont deux choses différentes**. La [politique de sortie](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/docs/egress-policy.md) traite séparément le retour des réponses du fournisseur vers l’environnement opérationnel. Accorder la lecture des courriels peut permettre au modèle d’en traiter le contenu ; il faut l’évaluer séparément de la protection du jeton.

### Après release, la limite change pour les mots de passe de sites

Le [code Vault](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/enclave/src/vault.rs) définit des types sélectionnant mots de passe, valeurs de carte et codes TOTP pour une réponse de sortie. Le [gestionnaire release](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/enclave/src/api/release.rs) sérialise et renvoie ces valeurs après confirmation de l’enregistrement du journal. **Les mots de passe et valeurs de carte quittent alors le nœud en clair, utilisables par le worker opérationnel.** Pour TOTP, c’est le code à usage unique calculé qui sort, pas la graine.

Dans le code public, la vérification d’`origin` ne contrôle que le format d’une origine HTTPS. Un commentaire attribue à l’appelant la responsabilité de déterminer si l’adresse correspond au site de connexion enregistré. Le seul code de l’Enclave ne prouve donc ni les restrictions de site ni le masquage des résultats du modèle.

Ce n’est pas une preuve de fuite réelle. Cependant, **cacher à l’entrée du modèle**, **stocker chiffré** et **utiliser en clair dans la mémoire du worker** sont des propriétés de sécurité distinctes. L’affirmation « l’IA ne reçoit pas le mot de passe » ne doit pas devenir « un mot de passe déchiffré ne quitte jamais la zone protégée ».

## Que garantit le journal d’utilisation ?

Le [guide officiel de l’activité](https://pickle.com/help/privacy/activity) indique que l’enregistrement est d’abord sauvegardé et que les identifiants ne sont pas utilisés si cette sauvegarde échoue. Le code API public montre aussi l’utilisation ou la sortie après confirmation de sauvegarde. Les enregistrements chiffrés, signatures et liens visent à rendre détectables les modifications ou omissions.

L’existence d’un journal ne garantit ni que l’utilisateur souhaitait la tâche ni qu’elle a réussi sur le site externe. La requête réelle peut par exemple échouer après l’enregistrement. L’approbation avant paiement et la nouvelle vérification du montant sont des règles d’exécution de la [description officielle](https://pickle.com/en), pas des propriétés découlant automatiquement du chiffrement des identifiants.

Déléguer aussi la graine TOTP permet à l’agent de générer les codes. Cette fonction pratique du [guide de connexion](https://www.pickle.com/help/connect/save-login) diffère d’une approbation distincte du second facteur par l’utilisateur pour chaque tâche. La portée de la délégation est donc plus large qu’avec le seul mot de passe.

## Vérifier la preuve du programme de sécurité public

La [documentation secure-program](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/secure-program/README.md) publie aussi le programme de sécurité côté appareil et fournit un outil vérifiant la signature de version et la preuve du journal de transparence. L’exemple vérifie **la correspondance d’un fichier public avec sa preuve de version**. Il ne se connecte pas à un nœud de production et n’utilise aucun vrai mot de passe.

![Le programme JS public et la preuve de version entrent dans l’outil officiel. Il vérifie le hachage, la signature et la preuve du journal de transparence. L’original v42 renvoie le code 0 ; un octet ajouté entraîne une erreur source_hash et le code 1. Vérifier le serveur de production et l’app installée relève d’une autre étape.](/assets/diagrams/technical/fr-2026-11-13-pickle-ai-security-architecture.svg)

Git, curl, Rustup et les outils de compilation natifs sont nécessaires ; télécharger les sources et les dépendances Rust nécessite le réseau. Le vérificateur a été compilé depuis le commit fixé ci-dessous sur **macOS arm64 avec Rust 1.100.0**. Le dépôt fixe la version 1.98.1 de l’outil ; ici `+1.100.0` choisit explicitement la version d’exécution.

### `verify-example.sh`

```bash
# macOS·Linux 셸, Git·curl·Rustup 및 네이티브 빌드 도구가 필요합니다.
# 새 작업 폴더에서 실행합니다. 아래 검증은 계정 로그인이나 실제 비밀번호를 사용하지 않습니다.
git clone https://github.com/pickle-com/credential-enclave.git
cd credential-enclave
git checkout cff16a343bf5bb7953e5b65df6ab3600107e127d
rustup toolchain install 1.100.0 --profile minimal
cargo +1.100.0 build --locked -p credential-enclave-verify
curl --fail --location \
  https://github.com/pickle-com/credential-enclave/releases/download/secure-program-v42/secure-program.release.json \
  --output secure-program.release.json
./target/debug/credential-enclave-verify program \
  --source secure-program/secure-program.js \
  --release secure-program.release.json
```

Le fichier original a renvoyé le code 0 et la sortie suivante :

```text
program release secure-program-v42: version 42, sha256 31e7fa7fb51f87781313b1f97b60ae3c7b69ff8f2fbcee7de12b7a0ed034d8e8, log index 3761959022: ok
```

Vérifiez aussi qu’un fichier modifié est rejeté. Exécutez les commandes suivantes dans le même dossier du dépôt.

### `tamper-example.sh`

```bash
cp secure-program/secure-program.js changed-program.js
printf '\n' >> changed-program.js
./target/debug/credential-enclave-verify program \
  --source changed-program.js \
  --release secure-program.release.json
echo $?
```

Le fichier auquel un octet de saut de ligne avait été ajouté a été rejeté pour divergence de `source_hash`, avec le code de sortie 1. Ce résultat concerne la preuve de version du programme public. Je n’ai pas vérifié si la version et le hachage affichés par l’app réelle correspondent, ni attesté à distance la mesure de l’Enclave en production.

## Quelles conditions restent pour évaluer la sécurité ?

Les [limites du dépôt public](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/README.md#what-it-does-not-guarantee) exposent des hypothèses de confiance : honnêteté de l’app, contrats d’API des fournisseurs, clés de version et journaux. Même avec un programme public, il faut vérifier séparément que l’ensemble du binaire iOS exécute ce programme sans le modifier. La possibilité pour un nœud de transférer une délégation vers une version ultérieure ne signifie pas que la protection d’une version reste fixée pour toujours.

Les [limites de mise à jour](https://github.com/pickle-com/credential-enclave/blob/cff16a343bf5bb7953e5b65df6ab3600107e127d/secure-program/README.md#limits) du programme côté appareil comptent aussi. La documentation précise qu’un nouveau code peut être chargé sans délai préalable si l’opérateur le signe, l’enregistre dans le journal public et respecte les conditions de chargement. **La vérification de version confirme la correspondance avec le fichier publié et signé ; elle ne garantit pas que le code soit inoffensif.** La confiance envers l’opérateur reste nécessaire pour les versions suivantes. Ce n’est ni une affirmation ni une observation d’une version réellement malveillante.

| Élément à vérifier | Question pour décider |
| --- | --- |
| Comptes connectés | Quels droits de lecture et d’écriture sont autorisés et peuvent-ils être révoqués auprès du fournisseur ? |
| Vault et TOTP | Faut-il déléguer la génération de codes uniques en plus du mot de passe ? |
| Paiements et réservations | Peut-on vérifier conditions et montant avant l’exécution, puis le résultat ? |
| Programme de sécurité et nœud | Version et hachage de l’app, version publique et attestation réelle du nœud correspondent-ils ? |
| Conversation et données de comptes | Quels contenus le modèle traite-t-il même si les identifiants sont cachés ? |

Le point central de la sécurité de Pickle est **quelles clés sont déléguées à qui, et à quelle frontière chaque valeur est déchiffrée puis utilisée**. Le code public fournit des éléments pour examiner ces limites. Pour l’utilisateur, un point de départ consiste à distinguer le contrôle réel d’app iPhone de la délégation d’accès aux comptes, n’accorder que les droits nécessaires et vérifier ensemble l’historique et les résultats.
