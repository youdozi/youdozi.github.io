---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2026-11-21-nginx4shell-http2",
  "routeSlug": "2026-11-21-nginx4shell-http2",
  "kind": "post",
  "title": "Guide Nginx4Shell — versions NGINX touchées par HTTP/2 et correctifs",
  "description": "Conditions d’exposition, versions corrigées et mesure temporaire pour les failles HTTP/2 de NGINX CVE-2026-123007 et CVE-2026-123633. Un exemple Python aide à prioriser les correctifs.",
  "categories": [
    "security"
  ],
  "tags": [
    "nginx",
    "http2",
    "patch-management",
    "cve-2026-123007",
    "cve-2026-123633"
  ],
  "sourcePath": "src/content/posts/en/2026-11-21-nginx4shell-http2.md",
  "sourceSha256": "51daac7a022b582074f762f0ce0c07d617f4af8535152688b060235117af16c2",
  "draftSha256": "ec75a71abb3c95724d9001dd4dad4b796c73cf81c67cb7325bdb4a7a09aac299",
  "manifestPath": ".pipeline/technical-translations/batch-175/manifest.json",
  "manifestSha256": "de1d6420b28e3a41bd670b52f3db93c0a08645e7821632b38b9c35d9f9d8517f",
  "publishedAt": "2026-11-21T00:38:31.366Z",
  "updatedAt": "2026-11-21T00:38:31.366Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 175,
    "approvedAt": "2026-11-21T00:38:31.366Z",
    "basis": "The site owner explicitly asked to publish the Nginx4Shell guide in the supported languages. This records authorization to publish these editions."
  }
}
---

**Vérifiez d’abord quelles interfaces d’écoute NGINX acceptent HTTP/2.** Divulguées le 18 novembre 2026, les failles CVE-2026-123007 et CVE-2026-123633 peuvent provoquer une corruption de la mémoire lors du traitement de HTTP/2. Dans certaines conditions, un processus worker peut s’arrêter ou du code peut être exécuté à distance avec ses privilèges. Les versions de NGINX Open Source corrigées sont stable **1.30.7** et mainline **1.31.9**. Pour les paquets de distribution, NGINX Plus et les produits Ingress, vérifiez la version corrigée indiquée par le fournisseur. [Avis de sécurité NGINX](https://nginx.org/en/security_advisories.html) · [Mise à jour de sécurité F5 du 18 novembre](https://my.f5.com/s/article/K000164058)

## Quels déploiements sont concernés ?

**Nginx4Shell** est le nom utilisé ici pour faciliter les recherches. Consignez séparément les deux identifiants CVE dans les tickets de changement et les inventaires afin de rapprocher chaque produit de son avis et de son état de mise à jour.

| CVE | Conditions et conséquences | Versions touchées de NGINX Open Source |
| --- | --- | --- |
| CVE-2026-123007 | Une corruption de la mémoire peut se produire quand NGINX traite le trafic HTTP/2 des clients. Vérifiez aussi les serveurs qui diffusent uniquement du contenu statique si HTTP/2 y est activé. | 1.9.5 à 1.30.6 et 1.31.0 à 1.31.8 |
| CVE-2026-123633 | Dans certaines conditions, NGINX peut accéder à une zone mémoire déjà libérée en transmettant des requêtes client HTTP/2 à un serveur amont. Vérifiez en priorité les proxys inverses HTTP/2. | 1.19.7 à 1.30.6 et 1.31.0 à 1.31.8 |

La version stable 1.30.7 corrige les deux failles. Malgré un numéro supérieur à celui de 1.30.7, **la version 1.31.8 reste touchée**. La mise à jour comprend aussi des corrections pour HTTP/3, le résolveur DNS et le proxy de messagerie. Continuez à préparer le correctif du produit lorsque vous modifiez temporairement la configuration HTTP/2. [Annonces de versions NGINX](https://nginx.org/news.html) · [F5 CVE-2026-123007](https://my.f5.com/s/article/K000163926) · [F5 CVE-2026-123633](https://my.f5.com/s/article/K000163928) · [Avis du CERT-EU](https://cert.europa.eu/publications/security-advisories/2026-022)

## Vérifier le produit en cours d’exécution et le chemin HTTP/2

1. **Identifiez l’origine du binaire en cours d’exécution.** Sur une VM, vérifiez l’exécutable et le paquet que le service utilise. Dans un conteneur, vérifiez l’image réellement utilisée et son empreinte. Exécutez `nginx -V` dans cet environnement pour connaître la version et les options de compilation. Certaines distributions, comme Ubuntu 24.04 LTS, rétroportent les corrections sur une version existante. L’avis Ubuntu indique que le paquet corrigé est `1.24.0-2ubuntu7.20` pour cette version. [Options de la ligne de commande NGINX](https://nginx.org/en/docs/switches.html) · [Ubuntu USN-9159-1](https://ubuntu.com/security/notices/USN-9159-1)
2. **Vérifiez la connexion entre le client ou le proxy frontal et NGINX.** Le navigateur peut se connecter au CDN via HTTP/2 tandis que le CDN communique avec l’origine NGINX via un autre protocole. Examinez la configuration réellement utilisée avec `nginx -T`, notamment les blocs `http` et `server`, les fichiers inclus et la syntaxe en vigueur. La configuration complète peut contenir des adresses internes ou des secrets. Consultez-la dans un environnement autorisé. [Documentation du module HTTP/2 de NGINX](https://nginx.org/en/docs/http/ngx_http_v2_module.html)
3. **Corrigez en premier les instances touchées qui reçoivent des requêtes externes.** Après le déploiement, vérifiez que les processus utilisent le nouveau binaire ou la nouvelle image. Utilisez `nginx -t` pour vérifier la configuration, puis contrôlez les requêtes HTTP ordinaires, l’état des serveurs amont, le taux d’erreur et les redémarrages de workers. Dans un cluster, vérifiez qu’aucune réplique ne tourne encore sur l’ancienne image. [Avis du CERT-EU](https://cert.europa.eu/publications/security-advisories/2026-022)

Si vous ne pouvez pas mettre à jour immédiatement, désactiver HTTP/2 sur les interfaces d’écoute concernées peut réduire l’exposition aux deux CVE. Avec la syntaxe actuelle, utilisez `http2 off;`. Avec l’ancienne syntaxe, retirez l’option `http2` de `listen`. Vérifiez avant le changement quels chemins dépendent de HTTP/2, par exemple gRPC, puis testez des connexions réelles à ces interfaces et des requêtes ordinaires du service. [Documentation de configuration HTTP/2 de NGINX](https://nginx.org/en/docs/http/ngx_http_v2_module.html) · [Guide d’atténuation Red Hat](https://access.redhat.com/security/vulnerabilities/RHSB-2026-019)

## Exercice — prioriser les correctifs à partir des vérifications

L’exemple utilise **l’origine du produit, sa version et l’état de HTTP/2** vérifiés par l’équipe d’exploitation. Il fonctionne avec Python 3.10 ou une version ultérieure et utilise uniquement la bibliothèque standard. Les informations recueillies plus haut permettent de définir l’ordre d’application des correctifs.

![Saisissez l’origine et la version du produit. Pour un paquet de distribution ou un produit fournisseur, consultez l’avis correspondant. Si la version d’origine de NGINX est touchée, utilisez l’état de HTTP/2 pour prioriser le correctif ou vérifier la configuration.](/assets/diagrams/technical/fr-2026-11-21-nginx4shell-http2.svg)

Enregistrez le script sous `nginx_http2_triage.py`. Utilisez `upstream` uniquement pour les versions Open Source publiées par le projet NGINX. Utilisez `vendor` pour les paquets comportant des corrections rétroportées et les images de fournisseurs. Choisissez `unknown` pour le champ concerné si l’origine du produit ou la configuration d’écoute reste à vérifier.

```python
import argparse
import re


def upstream_version(value: str) -> tuple[int, int, int]:
    if not re.fullmatch(r"[0-9]{1,4}\.[0-9]{1,4}\.[0-9]{1,4}", value):
        raise argparse.ArgumentTypeError("use an upstream version such as 1.30.7")
    major, minor, patch = map(int, value.split("."))
    return major, minor, patch


def triage(origin: str, value: str, http2: str) -> str:
    if origin != "upstream":
        return "CHECK_VENDOR_ADVISORY"

    version = upstream_version(value)
    if version[0] != 1 or version > (1, 31, 9):
        return "CHECK_CURRENT_ADVISORY"
    if (1, 30, 7) <= version < (1, 31, 0) or version == (1, 31, 9):
        return "UPSTREAM_FIX_VERSION"

    affected = [
        cve
        for cve, first_version in (
            ("CVE-2026-123007", (1, 9, 5)),
            ("CVE-2026-123633", (1, 19, 7)),
        )
        if version >= first_version
    ]
    if not affected:
        return "OUTSIDE_LISTED_RANGES"

    action = {
        "on": "PRIORITIZE_PATCH",
        "off": "PATCH_STILL_REQUIRED",
        "unknown": "VERIFY_HTTP2_AND_PATCH",
    }[http2]
    return f"{action} {' '.join(affected)}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("origin", choices=("upstream", "vendor", "unknown"))
    parser.add_argument("version")
    parser.add_argument("http2", choices=("on", "off", "unknown"))
    args = parser.parse_args()
    try:
        print(triage(args.origin, args.version, args.http2))
    except argparse.ArgumentTypeError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
```

```bash
python3 nginx_http2_triage.py upstream 1.31.8 on
python3 nginx_http2_triage.py upstream 1.30.7 on
python3 nginx_http2_triage.py upstream 1.19.6 unknown
python3 nginx_http2_triage.py vendor 1.24.0-2ubuntu7.20 on
```

L’exécution des commandes ci-dessus avec Python 3.13.0 a donné le résultat suivant.

```text
PRIORITIZE_PATCH CVE-2026-123007 CVE-2026-123633
UPSTREAM_FIX_VERSION
VERIFY_HTTP2_AND_PATCH CVE-2026-123007
CHECK_VENDOR_ADVISORY
```

La liste des CVE indique **les failles auxquelles la version peut être exposée**. Vérifiez la configuration d’écoute effective pour déterminer si la condition de transfert vers un serveur amont pour CVE-2026-123633 s’applique. Le script classe les entrées selon les plages de versions publiées. La configuration de production et l’état des correctifs doivent être vérifiés séparément.
