---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2026-11-20-ui-ux-design-agent-skills",
  "routeSlug": "2026-11-20-ui-ux-design-agent-skills",
  "kind": "post",
  "title": "Concevoir l’UI et l’UX avec Claude Code et Codex — parcours, Figma et accessibilité",
  "description": "Concevez un parcours, un système de design Figma et des textes d’interface avec Claude Code et Codex. Vérifiez avec Playwright le clavier et le focus d’une boîte de confirmation d’annulation.",
  "categories": [
    "ai"
  ],
  "tags": [
    "claude-code",
    "codex",
    "agent-skills",
    "figma",
    "ui-ux",
    "accessibility",
    "playwright"
  ],
  "sourcePath": "src/content/posts/en/2026-11-20-ui-ux-design-agent-skills.md",
  "sourceSha256": "b548a40ceebcfb72b0b19df913a07279080b56efc21e2264764c3cddd259e65a",
  "draftSha256": "672e255957c9763688ed9f7b84d68aa8f545c9ea62f7805204153e38c45d7390",
  "manifestPath": ".pipeline/technical-translations/batch-172/manifest.json",
  "manifestSha256": "91fb61de3a3d1c432b5f074da43348e5ad1ab92b61742481f1cd4ac05bc2994e",
  "publishedAt": "2026-11-20T14:37:06.595Z",
  "updatedAt": "2026-11-20T14:37:06.595Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 172,
    "approvedAt": "2026-11-20T14:37:06.595Z",
    "basis": "User requested seven new language editions for each of four already published guides and approved parallel AI translation and verification. This records publication authorization."
  }
}
---

**Avant de dessiner l’écran, définissez ce que l’utilisateur doit accomplir et jusqu’à quel point il peut revenir sur sa décision.** Pour l’annulation d’une réservation, il doit connaître les conséquences à l’avance et pouvoir conserver ou annuler sa réservation. Précisez le texte de la boîte de dialogue, le focus initial et sa destination après fermeture afin d’appliquer les mêmes critères à la réalisation et aux tests.

L’[article précédent](/ko/posts/2026-11-19-website-building-agent-skills/) couvre l’ensemble de la création d’un site web. Celui-ci approfondit l’étape UI/UX. Le 20 novembre 2026, nous avons vérifié les skills publics de Claude Code et de Codex ainsi que les ressources de Figma, Vercel et du W3C. À partir de ces ressources, suivons une annulation de réservation de la conception au test dans le navigateur.

## Choisir les skills selon le livrable

| Livrable attendu | Skill ou méthode | Critère à vérifier |
| --- | --- | --- |
| Parcours et états de l’interface | Consignes de projet `frontend-architecture-design` | Définir l’entrée, la confirmation, la sortie, le traitement en cours, le succès et l’échec. Si des résultats de recherche utilisateur sont disponibles, distinguer les observations des hypothèses. |
| Prototype à examiner | [Plugin Product Design](https://github.com/openai/plugins/tree/main/plugins/product-design) de Codex | Produire une maquette qui permet de vérifier les transitions. S’assurer que l’utilisateur peut conserver la réservation ou confirmer l’annulation. |
| Direction visuelle et code d’interface | [`frontend-design`](https://github.com/anthropics/skills/tree/main/skills/frontend-design) pour Claude Code | Préciser la hiérarchie visuelle du titre, de la description et du bouton. Vérifier que le sens et l’ordre subsistent avec un titre long ou un écran étroit. |
| Assemblage d’écrans dans Figma | [`figma-generate-design`](https://github.com/openai/plugins/tree/main/plugins/figma/skills/figma-generate-design) du plugin Figma | Réutiliser les instances de boutons et de boîtes de dialogue de la bibliothèque, puis créer des frames pour chaque état. Vérifier que les liens avec les composants et les variables sont préservés. |
| Bibliothèque du système de design | [`figma-generate-library`](https://github.com/openai/plugins/tree/main/plugins/figma/skills/figma-generate-library) du plugin Figma | Créer ou mettre à jour les variables et les bibliothèques Figma à partir des jetons de design et des composants du code. Comparer les variantes et les liens de variables aux noms dans le code réel. |
| Réalisation d’un écran Figma validé | [`figma-design-to-code`](https://github.com/openai/plugins/tree/main/plugins/figma/skills/figma-design-to-code) du plugin Figma | Lire le frame cible et le réaliser avec le code d’interface existant. Après la comparaison visuelle, vérifier séparément les interactions au clavier et l’état d’échec. |
| Textes d’interface | Consignes de rédaction UX du projet, comme `cms-ux-writing` | Employer un verbe qui décrit le résultat du clic. « Conserver la réservation » et « Confirmer l’annulation » indiquent le résultat de chaque action. |
| Revue de l’interface | [`web-design-guidelines`](https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines) de Vercel et vérification dans le navigateur | Repérer dans le code les problèmes possibles d’accessibilité et d’interface. Vérifier dans le navigateur l’ordre de tabulation, le déplacement du focus et la mise en page selon la taille de l’écran. |

Les deux consignes propres au projet illustrent comment transformer les règles de conception et de rédaction d’une équipe en skills réutilisables qu’elle définit dans son propre projet. Si une personne peut examiner le parcours, présentez-lui d’abord le prototype. Intégrez ses retours dans le tableau des états avant de transmettre le tout pour réalisation. Si le frame Figma et les composants du code ont déjà été validés, vous pouvez commencer par la réalisation et la revue d’accessibilité.

Dans Claude Code, `frontend-design` d’Anthropic fait partie du pack `example-skills` de la place de marché officielle. Pour utiliser les skills Figma dans Codex, il faut les outils Figma associés au plugin et l’accès au fichier. Pour créer des écrans ou des composants dans Figma, appliquez les consignes `figma-use` du plugin en complément du skill de création. Pour lire une maquette à réaliser, fournissez le lien du frame cible. Pour créer de nouveaux frames, fournissez un fichier modifiable et les bibliothèques à réutiliser. [Installation des skills Anthropic](https://github.com/anthropics/skills#claude-code) · [Plugin Figma pour Codex](https://github.com/openai/plugins/tree/main/plugins/figma)

Si vous avez une charte graphique, transmettez le logo, les couleurs, les polices et des exemples d’usages interdits. Appliquer `brand-guidelines` d’Anthropic à la marque de votre équipe en se fiant au nom peut introduire les couleurs et la typographie d’Anthropic. Les ressources fournies par défaut concernent cette marque. [Source de `brand-guidelines`](https://github.com/anthropics/skills/tree/main/skills/brand-guidelines)

## Transmettre le parcours d’annulation à la conception et au développement

Avant de dessiner l’écran, consignez les actions et leurs résultats dans un tableau. Celui-ci sert d’exemple de conception. Vérifiez la politique réelle du service avant de rédiger les informations sur les remboursements ou les frais d’annulation.

| Action ou état côté serveur | Résultat sur l’écran |
| --- | --- |
| Choisir « Ouvrir les options d’annulation » dans le détail de la réservation | La boîte de confirmation s’ouvre et le focus se place sur « Conserver la réservation ». |
| « Conserver la réservation » ou Échap | La boîte se ferme et la réservation reste active. Le focus revient au bouton qui a ouvert la boîte. |
| Choisir « Confirmer l’annulation » | En production, l’interface soumet la demande et affiche l’état de traitement. Le service doit empêcher le traitement en double si la même demande est soumise plusieurs fois. |
| Succès confirmé par le serveur | L’état passe à « Réservation annulée » et le résultat est annoncé. |
| Échec confirmé par le serveur | L’état de la réservation reste inchangé. L’interface explique la cause de l’échec et les suites possibles. |

Lorsqu’une boîte de dialogue confirme une action difficile à annuler, placer le focus initial sur le choix qui entraîne le moins de conséquences peut être approprié. À la fermeture, le focus revient généralement à l’élément qui a ouvert la boîte. Si cet élément a disparu, choisissez un autre élément qui permet de poursuivre le parcours. [Modèle de boîte de dialogue modale du W3C](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/)

Donnez à l’agent chargé de la réalisation le comportement attendu et les critères qui permettront de le vérifier.

> Conçois une boîte de confirmation d’annulation dans le détail de la réservation. Réutilise les boîtes de dialogue et les boutons existants.\
> Place le focus initial sur « Conserver la réservation ». À la fermeture avec Escape (Échap), conserve la réservation et rends le focus à « Ouvrir les options d’annulation ».\
> Après l’envoi de la demande, montre séparément les états de traitement, de réussite et d’échec.\
> En cas d’échec, propose de réessayer ou d’obtenir de l’aide.\
> Associe les frames à leurs états pour que nous puissions examiner l’écran et le tableau des états avant la réalisation.

## Exercice — vérifier le focus et les deux résultats de la boîte de dialogue

Vérifiez dans le navigateur les deux premières lignes du tableau et le changement visible après la confirmation de l’annulation. Dans cet exercice, la confirmation ne modifie que l’état de la page. Le projet de production doit tester séparément la requête serveur, la gestion des échecs et la prévention des envois en double.

![Ouvrir la boîte lorsque la réservation est active et vérifier le focus initial. Après Échap ou « Conserver la réservation », vérifier l’état et le focus. Après confirmation, vérifier l’affichage de l’état annulé.](/assets/diagrams/technical/fr-2026-11-20-ui-ux-design-agent-skills.svg)

Installez Node.js 22 et Chrome. Dans un nouveau dossier de travail, exécutez `npm init -y` et `npm install --save-dev playwright-core@1.64.1`. Enregistrez le code suivant sous `dialog-check.mjs`, puis exécutez `node dialog-check.mjs`. Si Chrome se trouve ailleurs qu’à son emplacement par défaut, définissez `CHROME_PATH`. [Options de démarrage de Playwright](https://playwright.dev/docs/api/class-browsertype#browser-type-launch)

```js
import assert from 'node:assert/strict';
import { chromium } from 'playwright-core';

const browser = await chromium.launch({
  executablePath: process.env.CHROME_PATH
    ?? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
});

try {
  const page = await browser.newPage({ viewport: { width: 360, height: 700 } });
  page.setDefaultTimeout(2000);
  await page.setContent(`
    <button id="open">취소 옵션 열기</button>
    <p role="status">예약 유지 중</p>
    <dialog aria-labelledby="title" aria-describedby="description">
      <h2 id="title">예약을 취소할까요?</h2>
      <p id="description">확정하면 예약 상태가 취소됨으로 바뀝니다.</p>
      <form method="dialog">
        <button value="keep" autofocus>예약 유지</button>
        <button value="cancel">예약 취소 확정</button>
      </form>
    </dialog>
    <script>
      const trigger = document.querySelector('#open');
      const dialog = document.querySelector('dialog');
      const status = document.querySelector('[role="status"]');

      trigger.addEventListener('click', () => {
        dialog.returnValue = '';
        dialog.showModal();
      });
      dialog.addEventListener('close', () => {
        if (dialog.returnValue === 'cancel') {
          status.textContent = '예약 취소됨';
        }
      });
    </script>
  `);

  const trigger = page.getByRole('button', { name: '취소 옵션 열기' });
  const dialog = page.getByRole('dialog', { name: '예약을 취소할까요?' });
  const status = page.getByRole('status');
  const focused = () => page.evaluate(
    () => document.activeElement?.textContent?.trim(),
  );

  for (const close of ['Escape', '예약 유지']) {
    await trigger.focus();
    await page.keyboard.press('Enter');
    await dialog.waitFor({ state: 'visible' });
    assert.equal(await focused(), '예약 유지', '초기 포커스');
    await page.keyboard.press(close === 'Escape' ? 'Escape' : 'Enter');
    await dialog.waitFor({ state: 'hidden' });
    assert.equal(await status.textContent(), '예약 유지 중');
    assert.equal(await focused(), '취소 옵션 열기', '닫은 뒤 포커스');
    console.log(`PASS ${close}: 예약 유지 및 포커스 복귀`);
  }

  await page.keyboard.press('Enter');
  await dialog.waitFor({ state: 'visible' });
  assert.equal(await focused(), '예약 유지', '초기 포커스');
  await page.keyboard.press('Tab');
  assert.equal(await focused(), '예약 취소 확정', '확정 버튼 포커스');
  await page.keyboard.press('Enter');
  await page.waitForFunction(
    () => document.querySelector('[role="status"]').textContent === '예약 취소됨',
  );
  await dialog.waitFor({ state: 'hidden' });
  assert.equal(await focused(), '취소 옵션 열기', '확정 뒤 포커스');
  console.log('PASS 예약 취소 확정: 상태 변경 및 포커스 복귀');
} finally {
  await browser.close();
}
```

Voici la sortie obtenue avec Chrome sous macOS. Elle reprend les libellés coréens de l’exemple.

```text
PASS Escape: 예약 유지 및 포커스 복귀
PASS 예약 유지: 예약 유지 및 포커스 복귀
PASS 예약 취소 확정: 상태 변경 및 포커스 복귀
```

Dans le test de contrôle, déplacer `autofocus` sur « Confirmer l’annulation » a fait échouer la vérification du focus initial. L’exercice a vérifié le nom accessible de la boîte, le comportement au clavier, le focus initial, puis le focus et l’état affiché après fermeture. Dans l’interface réelle, vérifiez aussi la visibilité du focus pendant la navigation au clavier, la lisibilité des boutons et des explications avec des caractères agrandis, ainsi que l’annonce des messages d’état par les technologies d’assistance. [WCAG 2.2](https://www.w3.org/TR/WCAG22/)
