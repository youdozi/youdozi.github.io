---
{
  "state": "draft",
  "language": "fr",
  "translationKey": "2026-11-22-claude-mythos-availability",
  "title": "Où utiliser Claude Mythos 5.2 ? Claude Security, Claude Code et l’API",
  "description": "Comparez l’accès direct à Mythos 5.2, l’analyse du code dans Claude Security pour Enterprise et la disponibilité de Fable 5.2 dans les offres Claude payantes.",
  "sourcePath": "src/content/posts/en/2026-11-22-claude-mythos-availability.md",
  "sourceSha256": "03f809cd5ff47c9929524f940e1ebf683dc5e75760fb062cfdb425ffbf4ff424"
}
---

**Pour accéder directement à Claude Mythos 5.2, il faut obtenir l’approbation d’Anthropic dans le cadre d’un programme de vérification.** Les particuliers disposant d’une offre éligible et dont la demande est approuvée peuvent obtenir Defense Access via le Cyber Verification Program (CVP). Dans Claude Enterprise, une organisation peut activer Claude Security, qui utilise Mythos 5.2 pour analyser le code. Fable 5.2 est disponible pour les offres Claude payantes, avec des exigences de crédits d’utilisation variables selon l’offre ou la licence. Ce guide s’appuie sur la documentation publique disponible au 22 novembre 2026. [Annonce de la version 5.2 par Anthropic](https://www.anthropic.com/claude-fable-and-mythos-5-2#availability) · [Aide Claude sur les modèles concernés](https://support.claude.com/en/articles/15425695-covered-models) · [Cyber Verification Program](https://support.claude.com/en/articles/14604842-cyber-verification-program)

## Quelle option vous convient ?

![Pour le développement courant, les abonnés à une offre payante peuvent chercher Fable 5.2 dans le sélecteur de modèles. Pour l’examen des dépôts Enterprise, utilisez Claude Security. L’accès direct à Mythos dépend de l’autorisation du compte et du canal utilisé.](2026-11-22-claude-mythos-availability.svg)

| Votre objectif | Où chercher | Conditions d’accès |
| --- | --- | --- |
| Utiliser un modèle de la version 5.2 pour programmer ou rédiger | Le sélecteur de modèles de Claude sur le Web, sur ordinateur ou sur mobile, ou dans Claude Code | Les offres payantes donnent accès à Fable 5.2. Les crédits d’utilisation dépendent de l’offre et de la licence. |
| Chercher des problèmes de sécurité dans un dépôt de l’entreprise avec Mythos | Claude Security dans Claude sur le Web | Bêta publique pour Enterprise. L’organisation doit activer la fonctionnalité et votre licence doit inclure Claude Code. |
| Utiliser directement Mythos comme modèle dans Claude Code ou dans l’API Claude | Les autorisations de modèles de votre compte ou l’espace de travail utilisé pour l’API | Il faut obtenir l’approbation du programme de vérification. Les particuliers disposant d’une offre éligible peuvent demander Defense Access. |

**Mythos Preview** était la version de recherche qu’Anthropic a mise à la disposition des organisations participant à Project Glasswing en avril 2026. Anthropic a présenté **Mythos 5.2** le 9 novembre. Vérifiez la date et la version du modèle quand vous comparez des informations sur sa disponibilité. [Annonce de Project Glasswing](https://www.anthropic.com/project/glasswing) · [Page du modèle Claude Mythos](https://www.anthropic.com/claude/mythos)

## Où Enterprise utilise Mythos

**Claude Security utilise Mythos 5.2 pour analyser les dépôts de code.** Une équipe peut, par exemple, lui demander de signaler une vérification d’autorisation manquante dans un service Web interne, puis examiner les éléments à l’appui et le correctif proposé. Anthropic propose également Claude Security aux clients Enterprise qui ne participent pas au Cyber Verification Program. Chaque personne doit disposer d’une licence incluant Claude Code. Les offres Enterprise facturées par licence exigent aussi l’activation des crédits d’utilisation. Un propriétaire de l’organisation disposant d’une licence avec Claude Code active la fonctionnalité dans `Organization settings → Claude Security`. [Annonce du lancement par Anthropic](https://www.anthropic.com/claude-fable-and-mythos-5-2) · [Conditions d’utilisation de Claude Security](https://support.claude.com/en/articles/14661296-use-claude-security)

Vous pouvez ouvrir un signalement dans Claude Code pour travailler sur un correctif. **L’analyse et la session Claude Code ont des autorisations distinctes pour les modèles.** L’analyse utilise Mythos et la session Claude Code utilise les modèles disponibles pour votre compte. Les utilisateurs Enterprise peuvent donc voir Claude Security alors que Mythos est absent du sélecteur de modèles du chat habituel. [Page produit de Claude Security](https://claude.com/product/claude-security) · [Configuration des modèles dans Claude Code](https://code.claude.com/docs/en/model-config)

## Trouver Fable 5.2 dans une offre individuelle

D’après Anthropic, Fable 5.2 et Mythos 5.2 reposent sur le même modèle de base. Fable applique des mesures de protection supplémentaires en cybersécurité et dans les sciences de la vie. Avec une offre individuelle payante, vous pouvez utiliser Fable 5.2 pour des tâches courantes de développement, comme comprendre un dépôt ou planifier une refactorisation. Pro et certaines licences standard nécessitent des crédits d’utilisation dès le départ. [Annonce des modèles par Anthropic](https://www.anthropic.com/claude-fable-and-mythos-5-2) · [Disponibilité de Fable selon l’offre](https://support.claude.com/en/articles/15424964-claude-fable-models-on-your-plan)

Sur le Web, sur ordinateur ou sur mobile, cherchez `Fable 5.2` dans le sélecteur de modèles. Si vous utilisez Claude Code dans un terminal, vérifiez d’abord que vous avez la version **2.1.321** ou une version ultérieure. Ouvrez ensuite `/model` dans une session pour voir les modèles disponibles. [Aide Claude sur les offres](https://support.claude.com/en/articles/15424964-claude-fable-models-on-your-plan) · [Configuration des modèles dans Claude Code](https://code.claude.com/docs/en/model-config)

```sh
claude --version
```

Avec l’API Claude, vous pouvez vérifier l’identifiant de Fable en demandant les métadonnées du modèle. L’exemple suppose que `curl` est disponible dans le shell et que la clé API de l’espace de travail concerné est déjà définie dans `ANTHROPIC_API_KEY`. Si la requête réussit, la réponse devrait contenir la valeur `claude-fable-5-2` pour `id`. Le format de la requête a été comparé à la référence officielle et la syntaxe du shell a été vérifiée localement. Le comportement de Claude après authentification, y compris la réponse de métadonnées et la sélection du modèle, n’a pas été testé. [Référence de l’API Claude pour la consultation des modèles](https://platform.claude.com/docs/en/api/models/retrieve)

```sh
curl --fail-with-body --silent --show-error \
  'https://api.anthropic.com/v1/models/claude-fable-5-2' \
  -H 'anthropic-version: 2026-10-21' \
  -H "Authorization: Bearer ${ANTHROPIC_API_KEY}"
```

## Vérifier l’accès direct à Mythos

D’après l’aide du Cyber Verification Program, les particuliers comme les chercheurs indépendants en sécurité et les responsables de projets open source peuvent demander **Defense Access** avec une offre éligible, notamment Pro, Max ou Ultra. Cet accès inclut Mythos 5.2 pour les participants dont la demande a été approuvée. Un abonnement payant ne suffit pas. Anthropic dispose d’un programme de vérification distinct pour la recherche en sciences de la vie. [Aide du Cyber Verification Program](https://support.claude.com/en/articles/14604842-cyber-verification-program) · [Annonce de disponibilité par Anthropic](https://www.anthropic.com/claude-fable-and-mythos-5-2#availability)

La documentation de l’API Claude indique `claude-mythos-5-2` comme identifiant de Mythos 5.2. La disponibilité dépend de l’accès accordé à votre compte ou à votre organisation et du canal utilisé. Les accès à Claude et à Claude Console sont gérés séparément. Les autorisations de la Console s’appliquent à l’espace de travail attribué. Les organisations qui utilisent un fournisseur cloud doivent aussi vérifier le compte cloud associé et la prise en charge par ce fournisseur. [Guide des modèles de l’API Claude](https://platform.claude.com/docs/en/models/fable-5-2/migration-guide) · [Aide Claude sur les offres, les espaces de travail et les comptes cloud](https://support.claude.com/en/articles/14604842-cyber-verification-program)
