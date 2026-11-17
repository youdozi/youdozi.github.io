---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2026-11-16-t3code-orca-herdr",
  "routeSlug": "2026-11-16-t3code-orca-herdr",
  "kind": "post",
  "title": "T3 Code, Orca et Herdr : choisir l’outil adapté au développement avec l’IA",
  "description": "Comparaison de la gestion des tâches, des worktrees, de la revue de code, des autorisations et du maintien des sessions de T3 Code, Orca et Herdr, avec leurs avantages et critères de choix.",
  "categories": [
    "ai"
  ],
  "tags": [
    "t3-code",
    "orca",
    "herdr",
    "ai-agent",
    "git-worktree"
  ],
  "sourcePath": "src/content/posts/en/2026-11-16-t3code-orca-herdr.md",
  "sourceSha256": "94725dbdc4ab213e11a438cbe4dbe69f888ffe3750e5d7c351e92178279c388e",
  "draftSha256": "81200acda1909292e0d912d7d7c31e6478df63a75d1b24fb70019c7f028b0c3a",
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

**T3 Code convient pour suivre tâches, autorisations et modifications dans un fil de discussion. Orca se distingue par un parcours réunissant terminal, éditeur, navigateur et diff par worktree. Herdr mérite d’être étudié si vous souhaitez maintenir les terminaux en cours d’exécution tout en configurant vous-même les vues de travail et l’automatisation.** Les fonctions des trois outils se recoupent ; mieux vaut comparer le parcours de lancement, de revue et de retour après interruption que les classer sur la présence d’une seule fonction.

La comparaison porte sur [T3 Code](https://github.com/pingdotgg/t3code/tree/v0.1.9), [Orca](https://orca.dev/) et [Herdr](https://herdr.dev/). Ils sont distincts de T3 Stack et d’autres projets Hydra aux noms proches. Elle repose sur la documentation consultée le 16 novembre 2026, en limitant les comportements précis de T3 Code à ceux décrits dans la **documentation v0.1.9**. Pour Orca et Herdr, les documents officiels actuels ont été utilisés. Les avantages et limites ci-dessous constituent des critères de choix fondés sur ces documents, pas des mesures de performances réalisées dans un environnement identique.

## Quel est le centre du travail ?

| Critère | T3 Code | Orca | Herdr |
| --- | --- | --- | --- |
| Parcours principal | Suivre demandes, autorisations et modifications dans les projets et les fils | Gérer agents, fichiers, navigateur et diff par worktree | Gérer terminaux et agents dans l’application ou la TUI, étendre les vues |
| Séparation des tâches | Fonction worktree disponible ; vérifier le chemin de travail réel | Organiser branches et vues autour des worktrees par tâche | Fonctions worktree dans l’application et la TUI ; un panneau n’est pas en soi un worktree |
| Revue des modifications | Distinguer les modifications d’un tour de conversation du périmètre de comparaison de la branche | Diff du worktree, commentaires par ligne, indexation partielle | Vérifier le parcours de revue de la configuration choisie et des outils de terminal |
| Autorisations | Vérifier le mode d’autorisation du fil et le comportement de chaque fournisseur | Vérifier les autorisations de l’agent et la portée réelle de l’exécution | Vérifier les autorisations des agents, commandes et extensions exécutés |
| Usage à distance | Connecter d’autres appareils au serveur | Hôtes SSH, environnement Orca distant | Fonctions distantes distinctes pour l’application/core et la TUI |
| Évaluation du coût | Distinguer coût de l’application, du fournisseur de modèle et conditions des services connectés | Distinguer coût de l’application, du fournisseur de modèle et du calcul distant | Distinguer coût de l’application/core/TUI, du fournisseur de modèle et du serveur |

La [documentation de gestion de versions](https://github.com/pingdotgg/t3code/blob/v0.1.9/docs/user/source-control.md) de T3 Code, la [documentation worktree](https://orca.dev/docs/model/worktrees) d’Orca et le [guide de l’application](https://herdr.dev/guide/) Herdr étayent ces parcours. Une fonction non vérifiée dans le tableau n’est pas considérée comme non prise en charge. T3 Code possède notamment des worktrees et une interface de revue, et Herdr dispose aussi d’une application de bureau.

## T3 Code : suivre la conversation et les résultats d’exécution ensemble

T3 Code travaille en connectant des fournisseurs installés aux projets et aux fils. Le [README v0.1.9](https://github.com/pingdotgg/t3code/blob/v0.1.9/README.md) décrit des clients mobiles, web et de bureau ainsi que la connexion de fournisseurs existants comme Codex et Claude Code. Le considérer comme un outil fournissant lui-même les modèles risque de créer une confusion pendant l’installation et l’authentification.

Son avantage est de permettre le suivi de la demande, de l’exécution, des autorisations et des modifications dans un même fil. La documentation de gestion de versions distingue les modifications d’un tour de celles de l’ensemble de la branche par rapport à la branche de référence. Par exemple, si l’agent récupère du code à jour avant de le modifier, lire seulement la liste des changements du tour ne suffit pas pour considérer la revue de toute la branche comme terminée.

Il faut tenir compte du fait que les modes d’autorisation n’ont pas le même sens chez tous les fournisseurs. Choisissez le mode à l’aide de la [documentation des autorisations](https://github.com/pingdotgg/t3code/blob/v0.1.9/docs/user/permission-modes.md), puis vérifiez les demandes réelles d’approbation. La présence d’un écran d’approbation ne signifie pas que les accès aux fichiers et au réseau sont isolés au niveau du système d’exploitation.

La durée de vie du serveur compte aussi pour l’usage à distance. La [documentation d’accès distant](https://github.com/pingdotgg/t3code/blob/v0.1.9/docs/user/remote-access.md) indique que fermer la dernière fenêtre de l’application de bureau arrête le serveur local. Pour une exécution persistante, il faut configurer un service d’arrière-plan distinct dans un environnement pris en charge. Ce service n’est pas disponible sous Windows dans cette version : distinguez donc les modes d’exécution. Le serveur doit également disposer de l’authentification du fournisseur et du dépôt.

## Orca : réunir l’environnement de développement et la revue par tâche

Orca est un environnement de développement qui crée un worktree par tâche et y réunit agent, éditeur, navigateur et diff. La [documentation du diff](https://orca.dev/docs/review/diff-viewer) décrit notamment les lignes modifiées, l’indexation partielle et la vue de résolution des conflits. Cet ensemble facilite un parcours où l’on modifie une interface, la vérifie dans le navigateur puis examine les changements.

Son avantage est de gérer les fichiers et les vues de revue dans un même contexte de worktree. Même avec plusieurs agents, vous pouvez relier la vérification de la branche concernée à l’interface. La CLI et les skills permettent aussi de contrôler les espaces de travail et les terminaux. [Guide de la CLI](https://orca.dev/docs/cli/overview)

Il faut toutefois apprendre la configuration de l’environnement et le parcours Git. Pour une petite modification unique, le coût de gestion des worktrees et des vues peut dépasser le confort apporté. Plus d’agents peut aussi signifier davantage de résultats à examiner et de ressources consommées. L’exécution parallèle ne garantit pas un gain de temps proportionnel.

Selon la [documentation de restauration des sessions](https://orca.dev/docs/model/session-restore), les agents continuent après fermeture de l’application si le démon reste actif. Un redémarrage de l’hôte ou l’arrêt du démon arrête les processus ; restaurer l’espace et l’historique du terminal diffère de restaurer des processus en cours. L’[exécution à distance](https://orca.dev/docs/ways-to-run) est aussi possible, mais les outils et l’authentification sur l’hôte exécutant la tâche doivent être préparés séparément.

## Herdr : configurer soi-même les terminaux et les vues de travail

Il faut **distinguer l’application de bureau, herdr-core et Herdr TUI**. L’application repose sur herdr-core, tandis que la TUI utilise un serveur distinct. La FAQ officielle précise que l’application et la TUI ne partagent pas leur liste d’agents. [Site officiel de Herdr](https://herdr.dev/)

Son avantage est de pouvoir étendre séparément l’environnement d’exécution des terminaux et la configuration des vues. Le [guide core](https://herdr.dev/core/) décrit l’exécution de programmes, le lancement d’autres tâches, la lecture des résultats et la connexion à des machines distantes. Le [guide de l’application](https://herdr.dev/guide/) présente aussi la possibilité de demander à un agent de modifier la disposition ou les fonctions. C’est une piste à étudier pour conserver un environnement de développement centré sur le terminal tout en construisant le tableau de bord souhaité.

Il faut en contrepartie assumer davantage la compréhension des composants et des extensions. L’affichage d’état de l’application dépend des rapports OSC 7501 des programmes ; un programme sans rapport d’état peut s’exécuter sans afficher son état. Ne confondez pas cela avec les règles de détection des agents de la TUI. Vérifiez aussi les commandes et les connexions externes utilisées par les modes personnalisés ou les plugins.

Les terminaux restent actifs après fermeture de la fenêtre si core fonctionne encore. Selon la FAQ, un redémarrage de l’appareil ou l’arrêt de core termine les processus, et l’application ne relance pas automatiquement les agents. La TUI propose séparément la restauration de la disposition et la reprise de sessions d’agents pris en charge après redémarrage du serveur. [Documentation de restauration TUI](https://herdr.dev/tui/docs/session-state/)

## Les limites des worktrees communes aux trois outils

Lorsque plusieurs agents modifient les mêmes fichiers simultanément, un worktree par tâche facilite le suivi. Mais séparer les répertoires ne sépare pas automatiquement les bases de données, les ports des serveurs de développement, les comptes externes ou les identifiants. Cette limite vaut pour les trois outils.

![Créer deux worktrees à partir du dépôt initial et y écrire des contenus différents. Comparer les fichiers et les listes de changements au fichier initial, puis examiner séparément la fusion réelle](/assets/diagrams/technical/fr-2026-11-16-t3code-orca-herdr.svg)

Le code suivant vérifie la séparation des fichiers montrée dans le schéma. Il crée un dépôt temporaire dans un shell macOS ou Linux avec Git installé, sans modifier de projet existant. Il n’inclut ni l’exécution d’agents ni une comparaison des performances des produits.

```sh
#!/bin/sh
set -eu
case_dir=$(mktemp -d)
git init -q "$case_dir/repo"
git -C "$case_dir/repo" config user.name 'Example Author'
git -C "$case_dir/repo" config user.email 'example@example.invalid'
printf 'base\n' > "$case_dir/repo/app.txt"
git -C "$case_dir/repo" add app.txt
git -C "$case_dir/repo" commit -qm 'Initial commit'
git -C "$case_dir/repo" worktree add -qb task-a "$case_dir/task-a" HEAD
git -C "$case_dir/repo" worktree add -qb task-b "$case_dir/task-b" HEAD
printf 'task A\n' > "$case_dir/task-a/app.txt"
printf 'task B\n' > "$case_dir/task-b/app.txt"
printf 'A: '; cat "$case_dir/task-a/app.txt"
printf 'B: '; cat "$case_dir/task-b/app.txt"
printf 'base: '; cat "$case_dir/repo/app.txt"
printf 'A 변경 파일: '; git -C "$case_dir/task-a" diff --name-only
printf 'B 변경 파일: '; git -C "$case_dir/task-b" diff --name-only
```

Voici la sortie vérifiée par exécution dans un shell local.

```text
A: task A
B: task B
base: base
A 변경 파일: app.txt
B 변경 파일: app.txt
```

A et B conservent des contenus différents mais ont modifié le même fichier. L’intégration exige d’examiner l’intention des deux modifications. L’exemple ne supprime pas automatiquement le répertoire temporaire.

## Quel outil essayer en premier ?

Vous pouvez commencer par **T3 Code** si suivre demandes, autorisations et changements dans une conversation vous convient, par **Orca** si vous préférez examiner navigateur, éditeur et diff séparément pour chaque tâche, ou par **Herdr** si vous souhaitez configurer vos terminaux et tableaux de bord. Ces suggestions sont déduites de l’organisation des fonctions dans la documentation officielle.

Pour valider votre choix, utilisez le même dépôt, la même tâche, le même modèle, les mêmes autorisations et les mêmes conditions de test dans les trois outils. Fixez un test en échec avant de modifier les fichiers, puis vérifiez les résultats d’exécution, le diff et les changements restants à la fin. Traitez la fermeture de fenêtre, la déconnexion du client, l’arrêt du serveur et le redémarrage de l’hôte comme des tests distincts. Comparez aussi l’effort de reprise et de revue, en plus du temps de traitement, pour faire apparaître les différences utiles à votre pratique.

Vous trouverez des parcours détaillés dans l’[exemple T3 Code](/ko/posts/2026-11-12-t3-code-workflow/), le [guide Orca](/ko/posts/2026-11-12-orca-worktree-guide/) et la [comparaison approfondie d’Orca et de Herdr](/ko/posts/2026-11-15-orca-herdr-comparison/).
