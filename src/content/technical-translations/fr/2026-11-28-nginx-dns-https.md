---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2026-11-28-nginx-dns-https",
  "routeSlug": "2026-11-28-nginx-dns-https",
  "kind": "post",
  "title": "Relier Duck DNS à Nginx avec une IA et vérifier chaque étape jusqu’à HTTPS",
  "description": "Suivez une requête externe jusqu’à l’application, distinguez un délai dépassé d’une erreur de proxy, puis vérifiez le certificat et son renouvellement.",
  "categories": [
    "tips"
  ],
  "tags": [
    "self-hosting",
    "nginx",
    "dns",
    "https"
  ],
  "sourcePath": "src/content/posts/en/2026-11-28-nginx-dns-https.md",
  "sourceSha256": "1afd017a347d250d7ed293c1a456355c47fa605f6f677aa12adda112db84165a",
  "draftSha256": "ab40a52cc47195a68dbfd8e333a4e921fd17d85fecf10948455730cb2c14ea8d",
  "manifestPath": ".pipeline/technical-translations/batch-1571/manifest.json",
  "manifestSha256": "bf6a83d6c439631d9c3af30e329fc60c4018ee5580ce2cd06ccd9111caf54227",
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

Prenons un serveur Linux avec une IPv4 publique et un nom Duck DNS. Une application destinée au public écoute déjà sur `127.0.0.1:8080` sur la même machine que Nginx. L’application de notes de l’article précédent servait à un exercice local. Utilisez ici une application distincte prévue pour être publiée.

## Demander à l’IA une procédure vérifiable

**Consigne** Je veux relier mon nom Duck DNS à Nginx sous Linux avec une IPv4 publique. Mon application écoute sur `127.0.0.1:8080` sur le même hôte. Remplace le vrai domaine par `example.com`. Donne les commandes et les résultats attendus pour vérifier, dans l’ordre, l’enregistrement DNS A, le port depuis l’extérieur, le proxy inverse et HTTPS. Si le DNS est correct, comment distinguer un délai dépassé d’une erreur `502` ? Indique la modification minimale et les étapes pour l’annuler. Demande-moi les valeurs inconnues et n’exécute rien.

Ne transmettez ni jetons ni clés SSH. Vérifiez la réponse pour chaque segment de la connexion.

![Résoudre le nom → Accéder au port HTTP → Sélectionner l’hôte Nginx → Vérifier la réponse de l’application → Vérifier HTTPS et le renouvellement](/assets/diagrams/technical/fr-2026-11-28-nginx-dns-https.svg)

## Vérifier le DNS et l’application locale

Remplacez partout `example.com` par votre nom. Chez Duck DNS, faites pointer A vers votre IPv4 publique. Ne publiez AAAA que si IPv6 fonctionne de bout en bout depuis l’extérieur. Ici, Nginx écoute en IPv4. Interrogez le DNS avec dig puis, sur le serveur, vérifiez avec curl que l’application renvoie sa réponse habituelle. [Duck DNS](https://www.duckdns.org/spec.jsp) · [Let’s Encrypt · IPv6](https://letsencrypt.org/docs/ipv6-support/)

```sh
dig +short example.com A
dig +short example.com AAAA
curl --fail --show-error http://127.0.0.1:8080/
```

## Transmettre la requête HTTP à l’application

Sauvegardez la configuration active. Ajoutez ce bloc server dans le contexte http du site en indiquant votre nom d’hôte. Vérifiez avec `nginx -t` puis, si le test réussit, rechargez la configuration avec le gestionnaire de services de votre système. [NGINX · proxy_pass](https://nginx.org/en/docs/beginners_guide.html#proxy) · [nginx -t](https://nginx.org/en/docs/switches.html)

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Depuis un autre réseau, ouvrez le site en HTTP. Vous devriez retrouver le contenu de l’application. Si le DNS est correct mais que le délai expire, vérifiez d’abord la ligne, la redirection de port et le pare-feu. Si Nginx renvoie `502`, vérifiez d’abord la réponse locale et le port de l’application. Pour revenir en arrière, restaurez la configuration sauvegardée, testez-la puis rechargez-la.

```sh
curl --fail --show-error http://example.com/
```

## Vérifier HTTPS et simuler le renouvellement

Avec le module Nginx de Certbot installé et le port TCP `80` accessible de l’extérieur, HTTP-01 permet de valider le nom. Sauvegardez d’abord la configuration HTTP fonctionnelle, car le module peut installer le certificat et modifier Nginx. Lancez Certbot sur le serveur, vérifiez HTTPS depuis un autre réseau puis testez le renouvellement sur le serveur. [Let’s Encrypt · HTTP-01 / DNS-01](https://letsencrypt.org/docs/challenge-types/) · [Certbot](https://eff-certbot.readthedocs.io/en/stable/using.html)

```sh
sudo certbot --nginx -d example.com
```

```sh
curl --fail --show-error https://example.com/
```

```sh
sudo certbot renew --dry-run
```

Notez la réponse HTTPS externe, le nom de domaine du certificat et le résultat de la simulation. Si le port TCP `80` est bloqué, DNS-01 permet de prouver le contrôle du nom via une zone DNS que vous gérez. Les visiteurs ont toujours besoin d’un accès HTTPS fonctionnel, généralement sur le port TCP `443`.

Nous avons confronté cette procédure à la documentation officielle. Nous n’avons modifié aucun réglage DNS, pare-feu ou serveur en production, ni exécuté Certbot, émis de certificat ou testé de déploiement public.

[Exercice local avec une application de notes](https://youdozi.github.io/en/posts/2026-11-28-self-hosting-ai-notes/) · [Quatre services de sous-domaines gratuits pour héberger Nginx chez soi](https://youdozi.github.io/en/posts/2026-11-28-nginx-free-subdomains/)
