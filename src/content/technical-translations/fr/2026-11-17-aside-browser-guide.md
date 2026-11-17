---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2026-11-17-aside-browser-guide",
  "routeSlug": "2026-11-17-aside-browser-guide",
  "kind": "post",
  "title": "Utiliser le navigateur Aside : organiser les résultats de recherche dans un fichier et les vérifier",
  "description": "Comment rechercher des informations avec Aside, les organiser en CSV et les vérifier, avec des prompts pour les pages connectées, les demandes de suivi et les tâches récurrentes.",
  "categories": [
    "ai"
  ],
  "tags": [
    "aside",
    "ai-agent",
    "browser-automation",
    "python",
    "csv"
  ],
  "sourcePath": "src/content/posts/en/2026-11-17-aside-browser-guide.md",
  "sourceSha256": "9d879f337252954a0aa3cd71855d210f95ea7c5da24065f69861d937e56fe64c",
  "draftSha256": "2f7174bb163592aa66e026e859a5472401a1169db64c3e6162a01a8af9019cc3",
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

**Mieux vaut préciser à Aside les pages à utiliser, le format attendu et les conditions de fin plutôt que lui demander simplement de « faire des recherches ».** Commencez par organiser quelques documents publics, comparez les résultats aux originaux, puis élargissez le périmètre aux pages connectées ou aux tâches récurrentes.

Cet article s’appuie sur l’aide officielle consultée le 17 novembre 2026. Les prompts ci-dessous sont des exemples d’usage, pas les résultats de recherches, de connexions ou de tâches programmées réellement exécutées dans Aside. Le code de validation CSV a été exécuté et vérifié avec des entrées fictives distinctes.

## Définir le périmètre avant de commencer

Installez Aside et vérifiez le modèle et le dossier de tâche à utiliser. Pour partir de la page actuelle, ouvrez le panneau latéral et vérifiez le titre et l’hôte de la page jointe. En conservant cette pièce jointe, la page peut servir de contexte à la tâche. [Guide du panneau latéral](https://docs.aside.com/help/side-panel)

Pour une recherche sans connexion, vous pouvez aussi choisir Incognito. Pour consulter un compte connecté, utilisez le profil par défaut où se trouve ce compte. Les deux modes ont des états de navigateur différents. Si la tâche doit enregistrer un fichier, elle nécessite aussi le droit d’écrire dans le dossier indiqué. [Guide des modes de tâche](https://docs.aside.com/help/tasks)

Vérifiez à la fois les paramètres de fichiers, d’outils et de bac à sable dans `Settings > Agents` et les réglages propres à la tâche. Dans la documentation officielle, `Guard` travaille dans les dossiers autorisés et demande confirmation avant d’accéder aux autres. `Read only` est décrit comme n’autorisant pas les modifications de fichiers ; ce mode peut donc ne pas convenir à l’exemple d’enregistrement CSV. Ne concluez pas de son seul nom que toutes les modifications de sites sont automatiquement bloquées. [Guide des autorisations](https://docs.aside.com/help/security)

## Exemple 1 : organiser trois pages officielles en CSV

Choisissez un dossier vide comme dossier de tâche, puis envoyez la demande suivante. Remplacez l’emplacement par le dossier réel. S’il existe déjà un fichier du même nom, choisissez un nouveau nom.

```text
Lis uniquement les trois pages officielles suivantes et organise-les dans report.csv.
https://docs.aside.com/help/tasks
https://docs.aside.com/help/automation
https://docs.aside.com/help/devices

Le CSV doit être en UTF-8, avec les colonnes dans cet ordre : topic,summary,source_url.
Utilise respectivement tasks,automation,devices pour topic et écris une seule ligne par page.
Pour summary, écris une phrase en coréen expliquant les principales conditions d’utilisation de la page.
Entoure de guillemets les champs contenant des virgules, conformément aux règles CSV.
Pour source_url, utilise sans modification l’adresse de la page correspondante donnée ci-dessus.

Enregistre le fichier dans le dossier de tâche choisi sans écraser de fichier existant.
Si tu ne peux pas lire un document, ne complète pas par des suppositions : indique l’adresse en échec.
N’accède pas aux comptes d’autres sites et n’envoie aucun message.
À la fin, indique le chemin du fichier et les trois pages vérifiées.
```

Si une page ne s’ouvre pas, résolvez d’abord l’échec d’accès. Si un élément manque dans le résultat, vérifiez aussi l’URL cible avant de réessayer. Remplacer un document non lu par un résumé supposé ne constitue pas une tâche terminée.

![Demander une recherche à Aside avec trois URL officielles et le format CSV, puis vérifier par code la structure du fichier et les sources. En cas d’échec, corriger fichier et demande ; en cas de réussite, comparer humainement le sens des résumés aux originaux](/assets/diagrams/technical/fr-2026-11-17-aside-browser-guide.svg)

La vérification par code du schéma détermine si le fichier obtenu respecte la structure et les sources imposées. Enregistrez le code suivant dans `check_report.py`. Il utilise uniquement la bibliothèque standard de Python 3 et ne communique pas avec l’extérieur.

```python
import csv
import sys

expected = {
    "tasks": "https://docs.aside.com/help/tasks",
    "automation": "https://docs.aside.com/help/automation",
    "devices": "https://docs.aside.com/help/devices",
}

with open(sys.argv[1], newline="", encoding="utf-8-sig") as stream:
    reader = csv.DictReader(stream)
    if reader.fieldnames != ["topic", "summary", "source_url"]:
        raise SystemExit("FAIL: columns")
    rows = list(reader)

if len(rows) != len(expected) or {r["topic"] for r in rows} != set(expected):
    raise SystemExit("FAIL: topics")
for row in rows:
    if (None in row or any(value is None for value in row.values())
            or not row["summary"].strip()
            or row["source_url"] != expected[row["topic"]]):
        raise SystemExit("FAIL: row")
print("PASS: 3 topics and allowed source URLs")
```

Passez en argument le chemin réel du CSV généré.

```sh
python3 check_report.py report.csv
```

Une entrée fictive de trois lignes contenant les URL autorisées a produit un code de sortie 0 et la sortie suivante. Cette entrée n’a pas été générée par Aside.

```text
PASS: 3 topics and allowed source URLs
```

Une entrée fictive dont une ligne avait été supprimée a renvoyé `FAIL: topics` avec le code de sortie 1. Le code vérifie les colonnes, les sujets, les URL et les résumés vides, mais **ne peut déterminer ni l’exactitude des résumés ni si les pages ont réellement été lues.** Après validation, vérifiez vous-même dans l’original les phrases qui étayent chaque résumé. Plutôt que d’assouplir les conditions pour résoudre un échec du code, recherchez d’abord les écarts entre le fichier et le prompt.

## Exemple 2 : consulter uniquement les chiffres d’un tableau de bord connecté

Pour consulter un compte, précisez le site, le compte, la période et les filtres. L’exemple suivant suppose un tableau de bord professionnel auquel vous avez le droit d’accéder.

```text
Dans le tableau de bord actuellement joint, lis les vues du compte que j’ai indiqué
sur la période 2026-11-01~2026-11-07. Indique aussi le fuseau horaire et les filtres affichés.
Présente la date, la valeur et l’unité dans un tableau et n’interprète pas les cases vides comme 0.
Ne modifie aucun réglage, n’exporte rien et ne consulte pas d’autres comptes.
Indique comme non confirmées les valeurs que tu ne peux pas vérifier à l’écran.
```

Une fois les chiffres obtenus, comparez d’abord le total à l’écran, la période, le fuseau et les filtres. Le total général peut différer de la somme de quelques premières lignes ; n’en concluez pas immédiatement qu’il s’agit d’une erreur. Si un export est nécessaire, définissez son contenu et son emplacement, puis faites-en une demande distincte.

Si des identifiants sont nécessaires, ne collez pas le mot de passe dans le prompt. Suivez le [guide Password Manager](https://docs.aside.com/help/password-manager) pour vérifier la politique d’utilisation des identifiants enregistrés et effectuer l’authentification supplémentaire demandée par le site. L’absence de transmission du mot de passe au modèle et le traitement du contenu des pages après connexion sont deux sujets distincts. La [politique de confidentialité](https://aside.com/policy/privacy) explique qu’un contexte sélectionné nécessaire à la tâche peut être envoyé à des fournisseurs de modèles hébergés.

## Modifier une demande en cours

Si la cible de recherche est incorrecte ou si vous devez réduire le périmètre, vous n’avez pas à attendre la fin. Le [guide des tâches](https://docs.aside.com/help/tasks) distingue `Queue` et `Steer` pour les messages de suivi. `Queue` applique la demande après l’exécution actuelle ; `Steer` transmet un nouveau message à la tâche en cours pour la réorienter.

Précisez la modification, par exemple : « Ne recherche pas d’autres sites, utilise uniquement les trois documents initiaux. » Envoyer une correction n’annule pas à lui seul les actions externes déjà effectuées. Vérifiez l’état réel avant de décider de la demande suivante.

## Exemple 3 : transformer une recherche validée en tâche récurrente

Si le résultat ponctuel est exploitable, vous pouvez envisager une recherche récurrente. Selon le [guide Routines](https://docs.aside.com/help/automation), une routine cron démarre une nouvelle tâche selon un calendrier, tandis qu’une routine heartbeat reprend une conversation existante. Pour un résumé hebdomadaire indépendant, examinez d’abord la création d’une nouvelle tâche.

Créez une routine dans `Settings > Routines` et saisissez par exemple les instructions suivantes. Réglez séparément la fréquence et le fuseau horaire dans l’interface réelle.

```text
Lis les trois pages officielles indiquées et compare-les au résultat de l’exécution précédente.
Signale les changements de mode d’emploi ou de limites, avec leurs liens justificatifs.
S’il n’existe aucun résultat précédent à comparer, conserve ce résultat comme référence initiale.
Si tu ne peux pas lire les documents, signale un échec d’accès au lieu de conclure à l’absence de changement.
Ne modifie pas les paramètres de compte, n’envoie pas de messages et n’effectue aucune tâche payante.
```

Définissez aussi où conserver le résultat précédent et comment l’exécution suivante le lira. La création d’une nouvelle tâche ne signifie pas que la conversation précédente devient automatiquement une source de comparaison. Précisez l’entrée, par exemple un ancien rapport dans le dossier indiqué, ou commencez par recevoir les rapports et les comparer vous-même plutôt que d’automatiser la comparaison.

Lancez immédiatement la routine depuis la liste pour vérifier les entrées, les sorties et la gestion des échecs, puis activez le calendrier. L’aide officielle décrit le saut des exécutions qui se chevauchent. Le [guide des appareils](https://docs.aside.com/help/devices) indique que les tâches locales nécessitent un ordinateur allumé, en ligne, avec Aside en cours d’exécution. Se connecter sur un autre ordinateur ou disposer d’une offre payante ne fait pas continuer dans le cloud le travail d’un appareil en veille.

Pour commencer, il suffit de se familiariser une fois avec le parcours de consultation, d’organisation et de vérification. Il faut y définir les entrées nécessaires et la méthode de contrôle des résultats pour pouvoir ensuite utiliser les exécutions récurrentes avec confiance.
