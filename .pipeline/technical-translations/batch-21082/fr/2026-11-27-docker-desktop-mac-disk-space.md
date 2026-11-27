---
{
  "state": "draft",
  "language": "fr",
  "translationKey": "2026-11-27-docker-desktop-mac-disk-space",
  "title": "Pourquoi l’espace libre sur mon Mac reste-t-il inchangé après avoir vidé le cache Docker ?",
  "description": "Mesurez séparément le cache de build récupérable, les blocs alloués à Docker.raw et l’espace libre sur le volume du Mac.",
  "sourcePath": "src/content/posts/en/2026-11-27-docker-desktop-mac-disk-space.md",
  "sourceSha256": "22ef396043237437e56056391cb42357c8f9bc5784eef9279e396ccf768d1ecd"
}
---

Docker calcule l’espace récupérable à partir des images et des caches stockés dans sa machine virtuelle. macOS mesure l’espace libre sur le système de fichiers hôte, où les blocs alloués à l’image disque `Docker.raw` de la machine virtuelle comptent comme occupés. Une couche partagée avec une image peut rester sur le disque après la suppression de l’entrée de cache. [Docker Desktop FAQ](https://docs.docker.com/desktop/troubleshoot-and-support/faqs/macfaqs/) · [Buildx du](https://docs.docker.com/reference/cli/docker/buildx/du/)

## À quoi correspond chaque mesure ?

Lorsque Docker Desktop tourne sur le Mac, vérifiez le contexte local et le builder. Un astérisque indique le builder sélectionné dans la liste.

```sh
docker context show
docker buildx ls
docker system df -v
docker buildx du
df -k /
```

![Relevez dans l’ordre l’espace occupé dans le moteur, le cache du builder sélectionné et l’espace libre sur le système de fichiers du Mac.](2026-11-27-docker-desktop-mac-disk-space.svg)

Le premier rapport couvre les images, les conteneurs, les volumes et le cache de build. Dans le deuxième, `Reclaimable` indique le cache récupérable du builder sélectionné. La dernière commande affiche sous `Available` l’espace libre sur le système de fichiers racine du Mac, en Kio. [Docker system df](https://docs.docker.com/reference/cli/docker/system/df/)

## Combien d’espace Docker.raw occupe-t-il réellement ?

Dans Docker Desktop, ouvrez Settings → Resources → Advanced pour trouver l’emplacement de l’image disque et adaptez le chemin de l’exemple. Dans la sortie de `ls -klsh`, la première colonne indique l’espace alloué en Kio et la colonne de taille donne la taille logique. La dernière commande vérifie le système de fichiers qui contient l’image, même si elle se trouve sur un autre volume.

```sh
image="$HOME/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw"
ls -klsh "$image"
stat -f 'bytes=%z blocks=%b' "$image"
df -k "$image"
```

Lors d’un relevé en lecture seule sur un Mac local, `desktop-linux` indiquait 61,76 Mo de cache de build récupérable. L’image disque avait une taille logique de 63 999 836 160 octets et occupait 12 272 488 blocs de 512 octets, soit environ 6,28 Go.

Pour ne vider que le cache de build, vérifiez d’abord le builder sélectionné. Comparez les résultats des mêmes commandes juste avant le nettoyage et quelques minutes après. Ce relevé n’a entraîné aucune suppression de cache et ne mesure donc pas l’espace récupéré par le Mac. [Buildx prune](https://docs.docker.com/reference/cli/docker/buildx/prune/)

[À lire aussi · Mesurer un nettoyage de disque sur Mac avec du et df](../2026-11-27-mac-disk-cleanup-du-df/)
