---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2026-11-16-aside-browser-introduction",
  "routeSlug": "2026-11-16-aside-browser-introduction",
  "kind": "post",
  "title": "Qu’est-ce que le navigateur Aside ? Un agent IA qui travaille sur les sites où vous êtes connecté",
  "description": "Présentation des tâches liées aux pages, de la mémoire, des mots de passe et des usages CLI et MCP d’Aside, avec les limites du traitement local et de la confidentialité.",
  "categories": [
    "ai"
  ],
  "tags": [
    "aside",
    "ai-agent",
    "browser-automation",
    "privacy",
    "mcp"
  ],
  "sourcePath": "src/content/posts/en/2026-11-16-aside-browser-introduction.md",
  "sourceSha256": "633c19745dfd802e65de403f2bfe9cf8c2ad7bdc234871ced911a6e0a65cc42c",
  "draftSha256": "d615d7cae2112b013f59d617846314188b8e9dbd329499347d9ecfc0df930c79",
  "manifestPath": ".pipeline/technical-translations/batch-165/manifest.json",
  "manifestSha256": "8b72a2b5aba51a050b30cc0ef5f871d2ef550798d50d91ef082c49bbf6448835",
  "publishedAt": "2026-11-17T06:12:46.742Z",
  "updatedAt": "2026-11-17T06:12:46.742Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 165,
    "approvedAt": "2026-11-17T06:12:46.742Z",
    "basis": "User requested multilingual application of the five recent articles and standing publication/merge authorization; AI translation and independent AI comparison completed. This records publication authorization, not human or native-speaker textual review."
  }
}
---

**Aside est un navigateur IA qui réalise des tâches en plusieurs étapes à partir des sites où vous êtes connecté et du contexte du navigateur.** Vous pouvez commencer par résumer une page ouverte ou recueillir des informations, puis lui confier la saisie de formulaires ou des opérations sur fichiers dans le périmètre autorisé. L’essentiel est de vérifier les pages et les actions effectuées, au-delà du seul texte de la réponse.

Cette présentation repose sur [l’aide officielle](https://docs.aside.com/) et les indications pour développeurs du 16 novembre 2026. L’exemple de lecture d’une page publique avec la CLI locale a été exécuté. Les prompts de travail ci-dessous n’ont pas été exécutés sur des comptes connectés et aucun taux de réussite par service n’a été mesuré.

## Qu’est-ce qui change par rapport à un navigateur ordinaire ?

Dans un navigateur ordinaire, c’est la personne qui passe d’un site à l’autre, copie les informations et décide de la prochaine action. Avec Aside, vous indiquez le résultat souhaité et le périmètre, puis l’agent peut lire plusieurs pages et poursuivre le travail. Pouvoir demander des actions sur des sites sans développer directement une API propre à chaque service est pratique. Cela ne signifie toutefois pas que l’automatisation réussit toujours sur tous les sites.

Le [guide des tâches](https://docs.aside.com/help/tasks) décrit le choix du mode, des autorisations, du dossier et du modèle, puis les réponses aux questions ou demandes d’approbation pendant l’exécution. Il distingue aussi les tâches du profil par défaut des tâches Incognito, qui n’utilisent pas l’état de connexion habituel.

| Usage | Résultat demandé | Points à vérifier |
| --- | --- | --- |
| Recherche de données publiques | Comparaison selon les critères avec liens sources | Date, unités et affirmations réelles des sources |
| Consultation d’un tableau de bord connecté | Synthèse des chiffres sur une période donnée | Compte, période, filtres et éventuelles omissions |
| Classement de documents et fichiers | Extraction des éléments nécessaires et brouillon | Valeurs originales et emplacement de sauvegarde |
| Préparation d’une réponse | Brouillon adapté à la demande | Destinataire, contexte et envoi effectif ou non |

Dans la dernière ligne, « rédiger un brouillon » et « envoyer » sont deux demandes différentes. Mieux vaut découvrir le parcours avec des consultations et des brouillons.

## Commencer une première tâche depuis une page ouverte

Selon le [guide du panneau latéral](https://docs.aside.com/help/side-panel), vous pouvez ouvrir une page et soumettre une demande dans le panneau Aside en conservant la page jointe. Vérifier le titre et l’hôte de la pièce jointe permet de savoir quelle page sert de point de départ à la tâche.

Essayez la demande suivante sur une documentation produit publique. Il s’agit d’un exemple de prompt rédigé pour l’article.

```text
À partir de la documentation officielle jointe, résume les environnements pris en charge,
les conditions d’installation et les limites.
Ajoute un lien justificatif à chaque point et indique comme non confirmée
toute information absente de la documentation.
Ne crée pas de compte, ne télécharge rien et n’installe rien.
Présente le résultat dans cette conversation.
```

Après réception du résultat, ouvrez les liens et vérifiez les conditions. Si d’autres produits ou d’anciens documents se mélangent aux sources, précisez l’URL cible et la date à vérifier, puis recommencez la demande. Ne laissez pas les instructions présentes dans les documents remplacer votre demande initiale ; précisez le périmètre à lire comme source documentaire.

## Le confort apporté par la mémoire et la gestion des mots de passe

Aside propose des fonctions utilisant le contexte de navigation et la mémoire. Toutefois, se connecter au même compte sur un autre ordinateur ne permet pas de poursuivre toutes les tâches. Le [guide des appareils](https://docs.aside.com/help/devices) distingue la synchronisation du navigateur, comme les favoris et l’historique, des conversations, de la mémoire et des dossiers de tâche qui restent sur chaque appareil. Le transfert à l’identique des tâches locales vers un autre ordinateur ou le cloud n’est actuellement pas proposé de manière générale, selon ce guide.

[Aside Vault](https://docs.aside.com/help/password-manager) est présenté comme un système qui remplit automatiquement les identifiants enregistrés sur les sites sans transmettre le mot de passe brut à l’agent. La politique d’utilisation par les agents se règle dans `Settings > Passwords > Access policy for AI agents`. Certains sites exigent une authentification supplémentaire ou une confirmation de l’utilisateur.

Masquer les mots de passe au modèle et faire traiter le contenu des pages après connexion sont deux choses différentes. Si vous demandez une synthèse d’e-mails, leur contenu peut entrer dans le contexte de la tâche. Mieux vaut donc définir les sites et tâches réellement nécessaires plutôt qu’autoriser le même accès à tous les comptes pour le seul confort de connexion.

## Ce que signifie une approche centrée sur le local

La [politique de confidentialité](https://aside.com/policy/privacy) indique que les conversations de tâche et les livrables sont stockés localement, mais précise aussi que des fournisseurs de modèles IA hébergés reçoivent le contexte nécessaire à la tâche. Ce contexte peut inclure les prompts, les résultats d’outils et certains instantanés du navigateur, captures d’écran ou fichiers sélectionnés. **Un stockage local ne signifie pas que tout le traitement est hors ligne ni qu’aucune donnée ne sort de l’appareil.**

Il faut aussi distinguer les droits d’accès aux fichiers des actions sur les sites. Ne supposez pas que le nom `Read only` bloque toutes les modifications de sites ; vérifiez les instructions de tâche et les demandes d’approbation réelles. Pour la portée de l’accès aux dossiers de `Guard` et `Full access`, consultez aussi le [guide des tâches](https://docs.aside.com/help/tasks) et les réglages de la version installée.

## Pour les développeurs : CLI, MCP et REPL

La [documentation développeur](https://aside.com/developers) propose une CLI pour les tâches en langage naturel, MCP pour connecter des agents existants et un REPL pour piloter directement le navigateur. Vous pouvez les intégrer lorsqu’un travail de développement nécessite de consulter des documents web ou de vérifier une interface. Une API HTTP publique de téléchargement diffère d’une API qui exécute des tâches d’agent.

![Saisir une URL publique, ouvrir un onglet avec le REPL Aside et lire un instantané de la page, puis comparer le titre et l’URL affichés à la demande](/assets/diagrams/technical/fr-2026-11-16-aside-browser-introduction.svg)

Exécutez la commande suivante dans un environnement où la CLI est installée, authentifiée et capable de se connecter à Aside. Consultez d’abord `aside guide` pour les bases et `aside guide repl` pour le pilotage direct du navigateur.

```sh
aside repl 'await openTab("https://example.com"); console.log((await snapshot(page)).tree)'
```

Lors de l’exécution sous macOS avec Aside CLI **1.26.1115.1556**, le code de sortie était 0. Le titre et l’URL figuraient ainsi dans la sortie ; le reste du contenu et les entrées de liens ont été omis.

```text
- title: "Example Domain" [url=https://example.com/]
```

Le schéma suit l’ordre de cet exemple : entrée → ouverture d’onglet → instantané → comparaison du résultat. Il ne valide ni le taux de réussite de recherche de l’agent en langage naturel, ni la connexion, ni les fonctions de paiement. Selon le guide CLI, la session REPL est incognito ; elle est donc distincte des tâches qui utilisent la connexion du profil habituel.

## Quelle première tâche lui confier ?

Aside mérite d’être essayé pour les travaux qui consistent à rassembler des informations provenant de plusieurs sites et documents. Plus le résultat attendu et les sources sont clairement définis, plus il est facile de juger si la tâche est terminée. Pour un traitement fixe en grand volume, examinez aussi si une API officielle ou un script dédié conviendrait mieux.

Les tâches récurrentes peuvent être programmées avec [Routines](https://docs.aside.com/help/automation), mais il ne faut pas supposer qu’elles continuent lorsque l’ordinateur local est en veille ou éteint. Le guide des appareils indique que les tâches locales exigent un ordinateur en fonctionnement et connecté au réseau. Vérifiez les limites d’usage et le coût des modèles connectés dans le [guide des offres](https://docs.aside.com/help/subscription) et l’application.

Une synthèse étayée d’une seule page de documentation publique suffit pour commencer. Comparez-la à l’original avant d’élargir le périmètre aux comptes connectés ou aux tâches récurrentes. Vous pourrez ainsi déterminer concrètement ce qu’Aside vous épargne et ce que vous devez vérifier vous-même.

Pour des demandes de recherche concrètes, une validation CSV et des exemples de tâches récurrentes, poursuivez avec [Utiliser le navigateur Aside en pratique](/ko/posts/2026-11-17-aside-browser-guide/).
