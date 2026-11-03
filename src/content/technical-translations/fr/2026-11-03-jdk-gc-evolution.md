---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2026-11-03-jdk-gc-evolution",
  "routeSlug": "2026-11-03-jdk-gc-evolution",
  "kind": "post",
  "title": "Ramasse-miettes du JDK : de JDK 27 à 1.4, avec G1, ZGC, Shenandoah et CMS",
  "description": "Retracez l'introduction, les choix par défaut et la suppression des GC de HotSpot, de JDK 27 et 28 EA aux anciennes versions. Comparez les collecteurs et exécutez un exemple reproductible de journalisation du GC.",
  "categories": [
    "java"
  ],
  "tags": [
    "jdk",
    "gc",
    "g1",
    "zgc",
    "shenandoah",
    "jvm",
    "performance"
  ],
  "sourcePath": "src/content/posts/en/2026-11-03-jdk-gc-evolution.md",
  "sourceSha256": "01667d7b4b2824ee749cd29f79a08f74627c3725ff551aa08ed090d48f9fd693",
  "draftSha256": "91b3ab7d74ff9183b92b96285a23159c5cd686faa1943bc019563cb0e8d86a77",
  "manifestPath": ".pipeline/technical-translations/batch-137/manifest.json",
  "manifestSha256": "f244063fe26ffa61c98e9820e607a03a676e98093676337edb7a008b2bca8ff5",
  "publishedAt": "2026-11-03T01:49:36.356Z",
  "updatedAt": "2026-11-03T01:49:36.356Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 137,
    "approvedAt": "2026-11-03T01:49:36.356Z",
    "basis": "사용자가 JDK GC 한영 글 게시 완료 후 다국어 지원도 진행해줘라고 요청하여 기존 지원 언어 여섯 개의 전체 번역과 현지화 그림 게시를 승인함. 별도 AI 검토는 사용자 게시 승인과 구분함."
  }
}
---

**Avec un HotSpot moderne, établissez une référence mesurée avec G1, comparez ZGC ou Shenandoah si les objectifs de latence sont stricts et envisagez Parallel GC si le débit prime.** Avant de reprendre d'anciens paramètres JVM, vérifiez le collecteur choisi par défaut et les implémentations présentes dans la distribution du JDK réellement utilisée.

La date de référence est le **2026-11-03**. [JDK 27](https://jdk.java.net/27/) est la dernière version majeure en disponibilité générale ; [JDK 28 est en accès anticipé](https://jdk.java.net/28/). Cet article porte sur **OpenJDK HotSpot**, et non sur toutes les implémentations de JVM. Les branches LTS d'Oracle — 8, 11, 17, 21 et 25 — sont des choix courants pour les déploiements, mais les périodes de support et les conditions de mise à jour dépendent du distributeur. [Feuille de route du support Oracle](https://www.oracle.com/java/technologies/java-se-support-roadmap.html)

## Du dernier JDK aux versions antérieures

| JDK | Principal changement du GC | Points à vérifier dans les déploiements existants |
| --- | --- | --- |
| **28 EA** | [JEP 535](https://openjdk.org/jeps/535), qui fait du mode générationnel le mode par défaut de Shenandoah, est au statut Targeted | Ne considérez pas ce changement comme livré dans une version GA. Il ne fait pas de Shenandoah le collecteur par défaut de la JVM |
| **27** | [JEP 523](https://openjdk.org/jeps/523) sélectionne G1 par défaut, quels que soient le nombre de CPU et la taille mémoire | Revérifiez les choix par défaut des services qui sélectionnaient auparavant Serial dans de petits environnements |
| **26** | [JEP 522](https://openjdk.org/jeps/522) réduit le coût de synchronisation de G1 pour améliorer le débit | Une amélioration en amont ne prouve pas que votre service obtiendra le même gain en pourcentage |
| **25** | [JEP 521](https://openjdk.org/jeps/521) fait passer Generational Shenandoah du statut expérimental à celui de fonctionnalité produit | La disponibilité d'un mode et sa sélection par défaut sont deux changements différents |
| **24 / 23** | 24 supprime ZGC non générationnel ([JEP 490](https://openjdk.org/jeps/490)) ; 23 utilise le mode générationnel par défaut lorsque ZGC est sélectionné ([JEP 474](https://openjdk.org/jeps/474)). 24 introduit aussi Generational Shenandoah à titre expérimental ([JEP 404](https://openjdk.org/jeps/404)) | Un choix par défaut au sein de ZGC ne change pas le collecteur par défaut de la JVM |
| **21 / 17 / 15** | 21 introduit Generational ZGC ([JEP 439](https://openjdk.org/jeps/439)). ZGC et Shenandoah deviennent des fonctionnalités produit dans 15 ([JEP 377](https://openjdk.org/jeps/377), [379](https://openjdk.org/jeps/379)) et le sont donc aussi dans 17 | Sélectionnez explicitement ZGC générationnel dans 21. Vérifiez séparément sa disponibilité selon la plateforme et la distribution |
| **14 / 12 / 11** | 14 supprime CMS ([JEP 363](https://openjdk.org/jeps/363)). 12 ajoute Shenandoah expérimental ([JEP 189](https://openjdk.org/jeps/189)) ; 11 introduit ZGC et Epsilon expérimentaux ([JEP 333](https://openjdk.org/jeps/333), [318](https://openjdk.org/jeps/318)) | Distinguez le statut expérimental historique du statut produit actuel ; la prise en charge initiale ne couvrait pas toutes les plateformes |
| **9** | G1 devient le collecteur par défaut des configurations serveur ([JEP 248](https://openjdk.org/jeps/248)) ; CMS est déprécié ([JEP 291](https://openjdk.org/jeps/291)) ; la journalisation unifiée du GC apparaît ([JEP 271](https://openjdk.org/jeps/271)) | Ne migrez pas tels quels les analyseurs et options des journaux de JDK 8 |
| **8** | Parallel est le choix par défaut privilégiant le débit sur les machines de classe serveur ; G1 et CMS sont des alternatives. PermGen est supprimé ([JEP 122](https://openjdk.org/jeps/122)) | Parallel n'était pas le choix par défaut dans tous les environnements. Ne reprenez pas les paramètres PermGen dans les nouveaux déploiements |
| **7u4 / 6 / 5 / 1.4.1** | Oracle JDK prend en charge G1 à partir de 7u4. La collecte complète parallèle arrive dans 5u6 et s'améliore dans 6. La documentation de 1.4.1 présente la collecte parallèle de la jeune génération et la collecte concurrente de l'ancienne | Distinguez la collecte parallèle initiale de la jeune génération de la collecte parallèle ultérieure de l'ancienne génération |

Lisez les choix par défaut de JDK 8 dans le contexte de son [guide d'ergonomie](https://docs.oracle.com/javase/8/docs/technotes/guides/vm/gctuning/ergonomics.html). Les étapes antérieures sont documentées dans l'[historique de prise en charge de G1](https://docs.oracle.com/javase/8/docs/technotes/guides/vm/G1.html), la [description de Parallel Compaction](https://docs.oracle.com/javase/8/docs/technotes/guides/vm/par-compaction-6.html) et l'[article sur le GC de JDK 1.4.1](https://www.oracle.com/technical-resources/articles/java/garbagecollection-in-java-applications-using-jdk141.html). Les recommandations historiques de taille de tas et les objectifs de pause décrivent leur époque ; ce ne sont pas les valeurs par défaut des déploiements actuels.

Ce tableau retient les étapes importantes. Il ne recense pas tous les correctifs des mises à jour et n'affirme pas que chaque version historique a été exécutée pour cet article.

## Trois distinctions avant de choisir un collecteur

Le GC récupère la mémoire des objets **inaccessibles depuis les racines du GC**, telles que les références détenues par les threads en cours d'exécution. Un cache ou une collection globale peut maintenir des objets accessibles alors que l'application n'en a plus besoin. La collecte générationnelle exploite le constat que beaucoup d'objets meurent rapidement tandis que certains survivent, en collectant différemment les objets jeunes et anciens. [Implémentation du GC de HotSpot](https://docs.oracle.com/en/java/javase/27/gctuning/garbage-collector-implementation.html)

**Parallèle** signifie que plusieurs threads du GC travaillent ensemble ; **concurrent** signifie qu'une partie du travail du GC se déroule pendant l'exécution de l'application. Ce sont deux dimensions différentes. Une phase **stop-the-world (STW)** suspend l'exécution de l'application. Les collecteurs concurrents peuvent encore provoquer de brèves pauses ou des attentes lors des allocations ; la concurrence n'élimine pas la latence des requêtes.

Le marquage identifie les objets vivants ; le balayage rend l'espace récupérable disponible pour réutilisation. Le compactage déplace les objets vivants pour regrouper l'espace libre, tandis que l'évacuation copie ailleurs les objets survivants de certaines régions. Les collecteurs combinent ces tâches différemment selon les générations, les régions et le travail parallèle ou concurrent.

| Collecteur | Approche principale | Conditions à comparer |
| --- | --- | --- |
| Serial | Un seul thread du GC ; le faible coût de coordination peut convenir aux petites tâches | Mesurez le débit et les pauses même avec un petit tas ou un CPU restreint |
| Parallel | Plusieurs threads de collecte, avec priorité au débit | Comparez le temps d'exécution des traitements par lots et les pauses tolérées |
| G1 | Régions, marquage concurrent et évacuation pendant les pauses | Référence générale pour les serveurs ; son objectif de pause n'est pas une garantie temps réel |
| ZGC | Effectue une grande partie des déplacements et du traitement des références de façon concurrente pour viser des pauses courtes | Observez ensemble les marges CPU et du tas, le taux d'allocation et la latence applicative |
| Shenandoah | Collecteur à pauses courtes avec déplacement concurrent ; le statut du mode générationnel varie selon la version | Vérifiez d'abord la disponibilité dans la distribution et le mode sélectionné |
| CMS / Epsilon | CMS est le collecteur historique à marquage et balayage concurrents ; Epsilon, expérimental, ne récupère pas de mémoire | CMS n'est pas disponible dans le dernier JDK. Epsilon ne remplace pas le GC d'un service à usage général |

Pour Serial et Parallel, commencez par le [guide actuel de sélection du collecteur](https://docs.oracle.com/en/java/javase/27/gctuning/available-collectors.html). Le [guide de réglage de G1](https://docs.oracle.com/en/java/javase/27/gctuning/garbage-first-garbage-collector-tuning.html) explique le comportement de G1 et ses objectifs de pause. La [documentation historique de CMS](https://docs.oracle.com/en/java/javase/13/gctuning/concurrent-mark-sweep-cms-collector.html) décrit les phases concurrentes et les contraintes de fragmentation ; [JEP 318](https://openjdk.org/jeps/318) précise l'absence de récupération mémoire dans Epsilon.

## Vérifier le mode générationnel en plus du collecteur

Pour ZGC dans JDK 21, `-XX:+UseZGC -XX:+ZGenerational` sélectionne le mode générationnel. Dans 23, `-XX:+UseZGC` utilise le mode générationnel par défaut ; 24 supprime l'implémentation non générationnelle. Rendre un paramètre obsolète puis le supprimer sont des étapes distinctes de la suppression d'une implémentation. Dans cet essai, JDK 27 a rejeté `-XX:+ZGenerational` : ne l'ajoutez donc pas à la configuration actuelle. [Guide actuel de ZGC](https://docs.oracle.com/en/java/javase/27/gctuning/z-garbage-collector.html)

Vérifiez Shenandoah séparément. Le mode générationnel devenu fonctionnalité produit dans 25 se sélectionne avec `-XX:+UseShenandoahGC -XX:ShenandoahGCMode=generational`. **Sélectionner uniquement Shenandoah dans 27 ne prouve pas que le mode générationnel est sélectionné.** JEP 535 vise 28 et reste au statut Targeted à la date de référence. Les options de compilation et les rétroportages peuvent modifier les collecteurs proposés par une distribution ; vérifiez l'exécutable réellement utilisé.

## Lire les journaux du même programme d'allocation

Cet **essai monothread** illustre les durées de vie des objets et les journaux du GC. Il alloue 8192 tableaux de 128 KiB, soit 1 GiB de données utiles de tableaux au total, tout en remplaçant les références dans 64 emplacements utilisés cycliquement. Les données utiles conservées à la fin occupent 8 MiB ; les en-têtes des tableaux, les références et la mémoire de la JVM s'y ajoutent. Ce programme ne reproduit pas une charge de production et ne constitue pas un benchmark du GC.

![Créer 64 emplacements de référence, allouer répétitivement un tableau de 128 KiB, remplacer une référence d'emplacement et accumuler une somme de contrôle pendant 8192 itérations, puis afficher le résultat](/assets/diagrams/technical/fr-2026-11-03-jdk-gc-evolution.svg)

Le diagramme suit l'allocation et le remplacement des références dans le code. La JVM décide quand récupérer les objets devenus inaccessibles ; le code n'appelle pas `System.gc()`. Ne supposez pas que chaque objet remplacé est récupéré immédiatement.

### `GcProbe.java`

```java
import java.lang.management.GarbageCollectorMXBean;
import java.lang.management.ManagementFactory;

public final class GcProbe {
    private static volatile byte[][] retained;
    private static volatile long checksum;

    public static void main(String[] args) {
        System.out.println("runtime=" + System.getProperty("java.runtime.version"));
        for (GarbageCollectorMXBean gc : ManagementFactory.getGarbageCollectorMXBeans()) {
            System.out.println("collector=" + gc.getName());
        }
        retained = new byte[64][];
        for (int i = 0; i < 8192; i++) {
            byte[] block = new byte[128 * 1024];
            block[0] = (byte) i;
            retained[i % retained.length] = block;
            checksum += block[0] & 0xff;
        }
        System.out.println("iterations=8192 retainedSlots=" + retained.length
                + " checksum=" + checksum);
    }
}
```

Les tableaux restent accessibles de l'extérieur via `retained`. Ce petit programme ne permet toutefois pas d'établir la distribution des durées de vie des objets ni le goulet d'étranglement d'un service en production.

### Sélectionner quatre collecteurs et examiner les journaux dans JDK 27

Ces commandes utilisent un shell de type Unix. Remplacez `GC_JDK` par le **répertoire racine de votre JDK**, enregistrez le fichier Java dans un nouveau répertoire de travail et exécutez-y les commandes. Aucune bibliothèque externe ni requête réseau n'est nécessaire. Chaque exécution utilise un tas maximal de 128 MiB et des journaux rotatifs de taille bornée.

```sh
GC_JDK="/path/to/jdk-27"
"$GC_JDK/bin/java" -version
mkdir -p out logs
"$GC_JDK/bin/javac" -d out GcProbe.java
for gc in G1 Parallel Serial Z; do
  "$GC_JDK/bin/java" "-XX:+Use${gc}GC" -Xms128m -Xmx128m \
    '-Xlog:gc*,safepoint:file=logs/gc-%p.log:time,uptime,level,tags:filecount=3,filesize=5M' \
    -cp out GcProbe
done
```

`%p` est remplacé par le PID de la JVM, ce qui distingue les journaux des différentes exécutions. Vérifiez que les quatre exécutions se terminent par la ligne suivante. Les lignes précédentes sur l'environnement d'exécution et le collecteur dépendent du JDK et du collecteur.

```text
iterations=8192 retainedSlots=64 checksum=1044480
```

L'environnement exécuté était **macOS arm64, Zulu 8u392-b08, et Temurin 21.0.13+9, 25.0.5+8 et 27.0.1.0.2+1**. Les versions archivées illustrent des comportements historiques ; ce n'est pas une recommandation de combinaisons actuelles de mises à jour de sécurité. Les exécutions vérifiées couvraient :

| JDK | Exécutions vérifiées |
| --- | --- |
| 8 | Parallel par défaut, G1 et CMS explicitement sélectionnés, avec vérification de l'achèvement et des anciens journaux du GC |
| 21 | ZGC non générationnel et explicitement générationnel, avec vérification de l'achèvement et des journaux |
| 25 | ZGC générationnel sélectionné par le paramètre ZGC, avec vérification de l'achèvement et des journaux |
| 27 | Serial, Parallel, G1, ZGC, Shenandoah non générationnel et Shenandoah explicitement générationnel, avec vérification de l'achèvement et des journaux |

Les **12 configurations d'exécution** ont toutes produit la même somme de contrôle et des journaux du GC. Elles ne contrôlent pas les différences d'implémentation, d'optimisation et de sécurité entre JDK : le temps écoulé ou le nombre de collectes ne constitue donc pas un classement des collecteurs. Les étapes de 28 EA et de 1.4.1–7, 9–20, 22–24 et 26 ont été vérifiées dans les sources officielles ci-dessus.

### Ce qu'indique une ligne de journal

Voici un véritable événement G1 de JDK 27 dont seuls les éléments d'horodatage et d'étiquetage ont été retirés.

```text
GC(0) Pause Young (Normal) (G1 Evacuation Pause) 47M->10M(128M) 1.468ms
```

`47M->10M` représente l'occupation du tas avant et après cette collecte ; `(128M)` est la capacité du tas à cet instant. La valeur entre parenthèses n'est pas toujours le tas maximal. Cet essai attribue la même valeur à `-Xms` et `-Xmx`. `1.468ms` est la pause de cet événement, ni le p99 du service ni le coût CPU total du GC. Cette ligne seule n'exclut pas une fuite mémoire et n'établit pas une garantie sur la durée des pauses.

### JDK 8 nécessite aussi d'autres options de journalisation

N'appliquez pas la journalisation unifiée de JDK 9 telle quelle à 8. Recompilez le même code source avec le compilateur de ce JDK pour éviter les incompatibilités de version des fichiers de classe.

```sh
GC_JDK="/path/to/jdk-8"
mkdir -p out8 logs
"$GC_JDK/bin/javac" -d out8 GcProbe.java
"$GC_JDK/bin/java" -Xms128m -Xmx128m -XX:+UseConcMarkSweepGC \
  -XX:+PrintGCDetails -XX:+PrintGCDateStamps -Xloggc:logs/jdk8-cms.log \
  -cp out8 GcProbe
```

JDK 27 a aussi rejeté `-XX:+UseConcMarkSweepGC`. Les étapes de prise en charge, d'obsolescence et de suppression diffèrent selon la version ; examinez les messages de démarrage réels et le code de sortie lors des mises à niveau.

Vérifiez le choix du collecteur par défaut comme suit. Cette commande annonce un CPU à une **nouvelle JVM** ; elle ne modifie pas l'allocation CPU d'un service en cours d'exécution.

```sh
GC_JDK="/path/to/jdk-27"
"$GC_JDK/bin/java" -XX:ActiveProcessorCount=1 -Xms128m -Xmx128m \
  -XX:+PrintCommandLineFlags -version
```

Dans les mêmes conditions, Temurin 21 a affiché `UseSerialGC` et Temurin 27 a affiché `UseG1GC`. Une sélection explicite du collecteur prime sur le choix par défaut. Le CPU et la mémoire visibles par la JVM comptent ; les seules caractéristiques de l'hôte n'établissent pas le choix d'un conteneur.

## Que mesurer lors d'une comparaison en production ?

Pour un service existant, relevez d'abord le JDK actuel, la distribution, les paramètres et la charge de travail. Avec le même profil de requêtes et le même budget CPU/mémoire, observez ensemble **le débit applicatif, les p95/p99, les erreurs, le RSS, l'occupation du tas, le taux d'allocation, les pauses du GC et la consommation CPU du GC concurrent**. Des pauses plus courtes peuvent néanmoins s'accompagner d'une latence applicative dégradée si les threads du GC et de l'application se disputent davantage le CPU.

Pour G1, établissez une référence avec les valeurs par défaut au lieu de figer une taille de jeune génération héritée d'un autre collecteur, puis ajustez au besoin le tas global et les objectifs de pause. ZGC nécessite une marge pour les objets vivants et les nouvelles allocations pendant la collecte concurrente. `-Xmx` ne correspond ni au RSS du processus ni à la limite mémoire de l'ensemble du conteneur ; prévoyez aussi le metaspace, les piles des threads et les tampons directs.

Si les objets accessibles continuent à s'accumuler, examinez d'abord les références conservées, les limites des caches et les durées de vie des requêtes. Changer de collecteur ne supprime pas automatiquement les objets accessibles. Combinez les observations du service avec le [workflow LGTM reliant journaux et traces](/en/posts/2026-11-02-grafana-lgtm-log-trace/), sans supposer que la coïncidence entre latence des requêtes et événements GC établit une causalité.
