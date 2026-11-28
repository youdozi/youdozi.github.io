---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2026-11-28-nginx-free-subdomains",
  "routeSlug": "2026-11-28-nginx-free-subdomains",
  "kind": "post",
  "title": "Quatre services de sous-domaines gratuits pour héberger Nginx chez soi",
  "description": "Une IP domestique qui change, un portfolio et une zone DNS à administrer soi-même appellent des choix différents.",
  "categories": [
    "tips"
  ],
  "tags": [
    "self-hosting",
    "nginx",
    "dns"
  ],
  "sourcePath": "src/content/posts/en/2026-11-28-nginx-free-subdomains.md",
  "sourceSha256": "d11db302c4d9595bd30ea32d7d5c2c2ec680a9c318001ba16e333085dbec5f2e",
  "draftSha256": "01803238fa89f53bb6777027519246fd379ae84128e11c199dc8c6893374cde5",
  "manifestPath": ".pipeline/technical-translations/batch-1571/manifest.json",
  "manifestSha256": "ce67844b72beb7d028d68ceb5fab80ea752b9cf1879179e92a69310b0ac23029",
  "publishedAt": "2026-11-28T04:45:08.727Z",
  "updatedAt": "2026-11-28T04:45:08.727Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 229,
    "approvedAt": "2026-11-28T04:45:08.727Z",
    "basis": "Explicit item 157 publication approval for both item 155 and 156 follow-up guides in all nine site languages."
  }
}
---

Nginx fonctionne chez vous. Quel nom donner aux visiteurs ? Ces quatre services proposent des sous-domaines gratuits sous un domaine géré par leur opérateur. Le serveur et son accessibilité depuis Internet restent à votre charge.

## Le serveur est-il accessible depuis un autre réseau ?

Le DNS dynamique (DDNS) met à jour l’adresse IP renvoyée par le DNS. La connexion dépend de la ligne, du routeur et du pare-feu. Si votre opérateur utilise le CGNAT, une redirection de port sur votre routeur peut ne pas suffire. Si son adresse WAN appartient à la plage `100.64.0.0/10`, demandez à votre opérateur s’il fournit une adresse IPv4 publique. [RFC 6598](https://www.rfc-editor.org/info/rfc6598/)

## Choisir selon le mode de gestion du nom

| Service | Gestion du nom | Usage adapté |
| --- | --- | --- |
| [Duck DNS](https://www.duckdns.org/spec.jsp) | Un client met à jour `name.duckdns.org`. L’API peut détecter automatiquement l’adresse IPv4. Pour mettre à jour IPv6, indiquez explicitement l’adresse. | Un premier essai sur une ligne dont l’adresse IPv4 publique change. |
| [dynv6](https://dynv6.com/) · [API](https://dynv6.com/docs/apis) | Un nom d’hôte et des API pour actualiser les enregistrements A et AAAA ainsi que le préfixe IPv6. | IPv6 ou double pile. Pas de garantie de service de niveau entreprise. |
| [is-a.dev](https://github.com/is-a-dev/register#-register) | Soumettez une pull request sur GitHub pour examen. L’équipe demande que vous rédigiez vous-même la demande. | Un portfolio de développement. Si l’IP change souvent, le DDNS est plus pratique. |
| [EU.org](https://nic.eu.org/register.html) · [EU.org NS](https://nic.eu.org/top-policy.html) | Préparez les serveurs de noms faisant autorité avant la demande. Après acceptation et délégation NS, vous gérez A et AAAA dans votre zone. | Pour administrer vos propres enregistrements DNS. Les mises à jour dynamiques sont à prévoir séparément. |

## Vérifier le nom choisi

![Vérifier l’adresse WAN → Choisir le mode de mise à jour → Interroger le DNS → Tester depuis un autre réseau](/assets/diagrams/technical/fr-2026-11-28-nginx-free-subdomains.svg)

Pour un premier essai, vérifiez que vous disposez d’une IPv4 publique, puis faites pointer un nom Duck DNS vers elle. Avec dig installé, remplacez le nom de l’exemple et interrogez les deux types d’adresses. A doit correspondre à l’adresse publique. Si vous publiez AAAA, testez également le chemin IPv6 depuis un autre réseau.

```sh
dig +short name.duckdns.org A
dig +short name.duckdns.org AAAA
```

Cette comparaison s’appuie sur la documentation des services. Nous n’avons ni créé de compte ni demandé de sous-domaine.

[Exercice local avec une application de notes](https://youdozi.github.io/en/posts/2026-11-28-self-hosting-ai-notes/) · [Relier Duck DNS à Nginx avec une IA et vérifier chaque étape jusqu’à HTTPS](https://youdozi.github.io/en/posts/2026-11-28-nginx-dns-https/)
