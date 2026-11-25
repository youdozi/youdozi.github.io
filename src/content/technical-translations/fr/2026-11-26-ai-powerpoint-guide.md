---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2026-11-26-ai-powerpoint-guide",
  "routeSlug": "2026-11-26-ai-powerpoint-guide",
  "kind": "post",
  "title": "Créer un PowerPoint avec l’IA, du plan aux diapositives modifiables",
  "description": "Trois prompts pour préparer le plan, créer un PowerPoint modifiable et vérifier chaque diapositive, à partir d’une proposition de test des contrôles avant déploiement.",
  "categories": [
    "ai"
  ],
  "tags": [
    "powerpoint",
    "pptx",
    "pptxgenjs",
    "ai-agent",
    "presentation"
  ],
  "sourcePath": "src/content/posts/en/2026-11-26-ai-powerpoint-guide.md",
  "sourceSha256": "859efd0ceeccfc1b46a9a9b1f8bbfb0235b50e0f4eee44c55f224a6a936c87cd",
  "draftSha256": "c112ddbbbd8bec05dd6dc61bb12431332cbcf7b77f389bc330266cf998d585b8",
  "manifestPath": ".pipeline/technical-translations/batch-193/manifest.json",
  "manifestSha256": "a54ee41212e4537256255e8c5a3c92386aff1f0228b7c74e991073c7b90d9b49",
  "publishedAt": "2026-11-25T22:36:09.895Z",
  "updatedAt": "2026-11-25T22:36:09.895Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 197,
    "approvedAt": "2026-11-25T22:36:09.895Z",
    "basis": "The site owner explicitly requested publication of item 74 in Korean, English, Simplified Chinese, Japanese, German, French, Russian and Spanish."
  }
}
---

Quand vous confiez une présentation à une IA, commencez par préciser **à qui vous vous adressez et quelle décision ce public devra prendre à la fin**. Avec « fais-moi un beau PowerPoint », vous aurez vite une page de titre et un sommaire, mais la décision risque de n’apparaître qu’à la dernière diapositive. Fixez le titre et les éléments de preuve de chaque diapositive, faites produire un .pptx à partir de ce plan, puis ouvrez-le dans l’application que vous utiliserez pour présenter. Vous repérerez plus facilement les retouches à faire.

![Préciser le public et la décision attendue, valider le plan, créer des diapositives modifiables puis vérifier les sources et le rendu en mode diaporama.](/assets/diagrams/technical/fr-2026-11-26-ai-powerpoint-guide.svg)

## Quels outils et compétences utiliser pour créer le PowerPoint ?

| Compétence ou outil | Quand l’utiliser | Travail à lui confier |
|---|---|---|
| **ai-guide-writing** | Transformer un mode d’emploi ou une formation en présentation | Organiser les exercices, les exemples d’entrée, les résultats attendus et les vérifications. |
| **tech-blog-writing** | Présenter une documentation technique ou un journal d’exploitation | Sélectionner les arguments et leurs preuves, puis répartir les explications entre les diapositives et les notes du présentateur. |
| **Compétence pptx d’Anthropic** | Créer un PowerPoint ou modifier un modèle existant dans Claude Code | Créer et modifier des .pptx, extraire leur contenu, examiner les miniatures et la structure du fichier. [Compétence officielle](https://raw.githubusercontent.com/anthropics/skills/main/skills/pptx/SKILL.md) |
| **PptxGenJS** | Produire des rapports hebdomadaires similaires avec un agent de programmation comme Codex | Régénérer un .pptx modifiable à partir de JavaScript et de données d’entrée. [Guide de démarrage](https://github.com/gitbrent/PptxGenJS#-quick-start-guide) |

ai-guide-writing et tech-blog-writing sont des compétences de rédaction disponibles dans l’environnement utilisé pour cet article. Pour produire le fichier PowerPoint, vous pouvez utiliser la compétence pptx de Claude Code ou PptxGenJS. Pour installer les compétences officielles d’Anthropic dans Claude Code, exécutez les deux lignes suivantes dans l’ordre. Vous pourrez ensuite demander la compétence pptx par son nom dans votre prompt. [Instructions d’installation d’Anthropic](https://github.com/anthropics/skills#claude-code)

```text
/plugin marketplace add anthropics/skills
/plugin install document-skills@anthropic-agent-skills
```

Si vous travaillez déjà dans PowerPoint, **Copilot** peut préparer une première version à partir d’une consigne ou de fichiers de référence. Si votre entreprise dispose d’un modèle, ouvrez-le avant de commencer. Les fonctions disponibles dépendent de votre abonnement et des paramètres de votre organisation. Avec **Gemini dans Google Slides**, vous pouvez générer des diapositives puis les télécharger au format .pptx. Selon Google, la génération d’une présentation complète nécessite un forfait compatible et s’utilise sur ordinateur, en anglais. [Créer une présentation avec Copilot](https://support.microsoft.com/en-gb/powerpoint/copilot/create-a-new-presentation-with-copilot-in-powerpoint) · [Générer une présentation dans Google Slides](https://support.google.com/docs/answer/17111393) · [Télécharger un fichier PPTX](https://support.google.com/a/users/answer/9310270)

## 1. Préciser dans le prompt du plan la décision attendue en réunion

Dans cet exemple fictif, vous proposez à l’équipe de développement de **tester l’automatisation des contrôles avant déploiement**. Vous avez 7 minutes pour faire approuver un essai de 2 semaines avec une seule équipe. Ces précisions aident l’IA à présenter d’emblée la décision à prendre au lieu de s’attarder sur les avantages généraux de l’automatisation.

```text
Prépare le plan d’un exposé de 7 minutes pour les responsables du développement et de l’exploitation.
Propose d’automatiser les contrôles avant déploiement en 6 diapositives.
Il faut décider en réunion si on autorise un essai de 2 semaines avec une équipe.

<Sources>
- Avant le déploiement, les équipes vérifient à la main les variables d’environnement et les migrations de la base de données.
- Le premier contrôle automatique vérifie uniquement que les variables requises sont présentes
  et qu’il ne manque pas de fichiers de migration.
- Il consigne seulement le diagnostic, sans modifier la configuration ni la base de données.
- Pendant l’essai, relever la durée des contrôles, le nombre d’oublis détectés et celui des faux positifs.
- Le gain de temps et la baisse du taux d’échec n’ont pas encore été mesurés.
</Sources>

Pour chaque diapositive, donne un titre qui énonce la conclusion, au maximum 3 éléments de texte
à l’écran, des notes pour le présentateur et le point des sources qui justifie l’affirmation.
Indique la décision attendue sur la première diapositive et les critères d’évaluation de l’essai
sur la dernière. N’invente ni chiffres ni noms de responsables prétendument désignés.
```

Une fois le plan reçu, **lisez uniquement les titres, dans l’ordre**. Le premier doit indiquer la décision attendue, les suivants exposer le problème actuel et le périmètre des contrôles, et le dernier préciser comment évaluer l’essai. Le titre « Pendant l’essai, nous relèverons la durée des contrôles et les faux positifs » donne un fil conducteur plus clair que « Avantages attendus de l’automatisation ».

## 2. Demander un .pptx modifiable

Si vous comptez retoucher le texte ou les graphiques, **nommez les éléments à rendre modifiables** dans le prompt de création. Si toute la diapositive est une image, il faudra peut-être la refaire pour corriger une seule phrase dans PowerPoint.

```text
À partir du plan validé ci-dessous, crée un fichier PowerPoint au format 16:9
nommé deployment-check-pilot.pptx.

- Rends les titres, le texte, les tableaux et les schémas modifiables séparément dans PowerPoint.
- Développe une idée principale par diapositive et réserve les longues explications aux notes.
- Pour le contrôle automatique, utilise trois formes :
  « Demande de déploiement → Vérification des deux points → Enregistrement du résultat ».
- S’il n’y a pas de chiffres, utilise un tableau ou un schéma plutôt qu’un graphique statistique.
- Si un modèle d’entreprise est joint, respecte la position des titres, les polices et les couleurs.
- Ne présente pas comme acquis des effets ou des dates de mise en œuvre que les sources ne donnent pas.

<Plan validé>
Coller ici le plan des diapositives vérifié à l’étape 1.
</Plan validé>
```

Pour faire produire chaque semaine le même type de rapport à un agent de programmation, ajoutez **« Utilise PptxGenJS et fournis build-deck.js et slides.json pour que je puisse relancer la génération. »** La semaine suivante, il suffira de remplacer les données pour retrouver la même mise en page. Gardez si possible les tableaux de données et les graphiques sous forme d’objets PowerPoint. Réservez les images distinctes aux illustrations, pour faciliter les retouches. [Objets texte dans PptxGenJS](https://gitbrent.github.io/PptxGenJS/docs/api-text.html)

## 3. Demander le numéro de diapositive et la justification de chaque correction

Joignez au fichier terminé **le plan validé et les sources d’origine**. Si une diapositive affirme que « le taux d’échec des déploiements a baissé », il faut consulter les sources pour savoir s’il s’agit d’un résultat observé ou d’un indicateur qu’il reste à mesurer.

```text
Compare le PPTX terminé au plan validé et aux sources d’origine.
Pour chaque diapositive concernée, indique son numéro, le problème, sa justification et le texte de remplacement.

1. Relève les chiffres sans source, les dates non confirmées et les effets exagérés.
2. Si tu peux afficher le rendu des diapositives, vérifie les substitutions de polices coréennes,
   les retours à la ligne, le texte tronqué et les formes qui se chevauchent.
3. Repère les notes qui répètent les phrases à l’écran.
4. En regardant uniquement la dernière diapositive, indique ce que le public doit décider.

Marque « non vérifié » tout élément que tu n’as pas pu contrôler directement.
```

Ouvrez le fichier dans la version de PowerPoint qui servira à la présentation et testez **le mode édition et le mode diaporama**. En mode édition, essayez de changer un chiffre dans un tableau et le texte d’une forme. En diaporama, vérifiez que les titres et les messages principaux se lisent depuis le fond de la salle. Après un export depuis Google Slides, revérifiez les polices coréennes et les retours à la ligne. Les prompts illustrent un cas fictif. Les possibilités de génération des produits sont décrites d’après leur documentation officielle.

À lire aussi · [10 skills recommandés pour Claude Code et Codex et leurs usages au quotidien](../2026-11-18-claude-code-codex-skills-top-10/)
