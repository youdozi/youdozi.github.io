---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "fr",
  "translationKey": "2023-09-13-springboot-history",
  "routeSlug": "2023-09-13-springboot-history",
  "kind": "post",
  "title": "Historique de Spring Boot et versions réelles des dépendances",
  "description": "Situer certaines releases Spring Boot et vérifier les versions Framework, Lombok et BOM résolues par le projet.",
  "categories": [
    "springboot"
  ],
  "tags": [
    "springboot",
    "history"
  ],
  "sourcePath": "src/content/posts/en/2023-09-13-springboot-history.md",
  "sourceSha256": "8f97cfe96eb4ed1a36dae63a187c6f28960c327ff6cba276c45537a1e7745da2",
  "draftSha256": "568ca1ceaf875432a858bf27fb384c0198b0dfe15313e03cd48019541f72ea3e",
  "manifestPath": ".pipeline/technical-translations/batch-125/manifest.json",
  "manifestSha256": "1934910c02dbe893b786124f1d296d7adf9efbe921d40b3d2cfbceb8f70b4b33",
  "publishedAt": "2026-10-31T15:35:43.034Z",
  "updatedAt": "2026-10-31T15:35:43.034Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 125,
    "approvedAt": "2026-10-31T15:35:43.034Z",
    "basis": "User explicitly requested applying all missing technical-post languages, review, verification and deployment on 2026-11-01, with standing PR merge authorization. Human approval denotes publication authorization; linguistic review is performed by AI, not human/native review."
  }
}
---
Spring Boot et Spring Framework sont des projets distincts aux numéros de version différents. Boot ajoute la configuration automatique, la gestion des dépendances et l’empaquetage exécutable autour de Framework. Interpréter Boot 3.1 comme Framework 6.1 n’est donc pas fiable ; inspectez plutôt la BOM de la release Boot choisie et le graphe résolu des dépendances.

## Déroulement du traitement

![Résoudre les versions réelles des composants](/assets/diagrams/technical/fr-2023-09-13-springboot-history.svg)

Le flux résume l’inspection des dépendances, et non une chronologie des releases. Boot, Framework et Lombok possèdent des identités de version et des configurations de dépendances distinctes.

## Changements de certaines versions finales

Cette chronologie souligne des évolutions fonctionnelles au lieu d’énumérer toutes les releases. Distinguez la première version finale de l’élargissement de compatibilité JDK dans les correctifs ultérieurs.

| Spring Boot | Première version finale | Changements retenus et annonce officielle |
| --- | --- | --- |
| 1.2 | 2014-12-11 | [`@SpringBootApplication` et prise en charge de Servlet 3.1](https://spring.io/blog/2014/12/11/spring-boot-1-2-0-released/) |
| 1.3 | 2015-11-16 | [DevTools, configuration automatique du cache et JAR directement exécutables](https://spring.io/blog/2015/11/16/spring-boot-1-3-0-released/) |
| 1.4 | 2016-07-28 | [Analyse des échecs de démarrage et amélioration des tests](https://spring.io/blog/2016/07/28/spring-boot-1-4-released/) |
| 2.0 | 2018-03-01 | [Framework 5.0, base Java 8 et prise en charge du Web réactif](https://spring.io/blog/2018/03/01/spring-boot-2-0-goes-ga/) |
| 3.0 | 2022-11-24 | [Framework 6.0, base Java 17, Jakarta et images natives](https://spring.io/blog/2022/11/24/spring-boot-3-0-goes-ga/) |
| 3.1 | 2023-05-18 | [Testcontainers pendant le développement et intégration Docker Compose](https://spring.io/blog/2023/05/18/spring-boot-3-1-0-available-now/) |
| 3.2 | 2023-11-23 | [Prise en charge des threads virtuels, de RestClient et de JdbcClient](https://spring.io/blog/2023/11/23/spring-boot-3-2-0-available-now/) |
| 4.0 | 2025-11-20 | [Framework 7, modularisation, JSpecify et gestion des versions d’API](https://spring.io/blog/2025/11/20/spring-boot-4-0-0-available-now/) |

Par exemple, la [liste des dépendances gérées de Boot 3.1.0](https://docs.spring.io/spring-boot/docs/3.1.0/reference/html/dependency-versions.html) indique `spring-core` 6.0.9. Les numéros mineurs de Boot et Framework n’ont pas à correspondre. Associer Boot 2.4 à une branche Framework 5.4 inexistante est également incorrect.

## Starters, BOM et plugins de construction

Un starter regroupe les dépendances nécessaires à une fonctionnalité. Une BOM gère les versions ; elle n’ajoute pas automatiquement toutes les bibliothèques de sa liste au projet. Le plugin de construction Boot fournit des tâches telles que `bootRun` et l’empaquetage de JAR exécutables.

Pour Gradle, le [guide Boot de gestion des dépendances](https://docs.spring.io/spring-boot/4.1/gradle-plugin/managing-dependencies.html) décrit le plugin de gestion des dépendances et la prise en charge native des BOM. Appliquer uniquement le plugin Boot ne garantit pas que toutes les configurations Gradle acceptent des dépendances sans version. Vérifiez aussi les configurations distinctes telles que les processeurs d’annotations.

## Inspecter les versions réelles du projet

Exécutez ces commandes dans le projet final des guides [Initializr](/en/posts/2023-09-07-springboot-initializer/) et [Lombok](/en/posts/2023-09-15-springboot-intellij-lombok/).

```sh
./gradlew dependencyInsight --configuration runtimeClasspath --dependency spring-core
./gradlew dependencyInsight --configuration annotationProcessor --dependency lombok
```

L’exemple local résout Boot 4.1.2, `spring-core` 7.0.10 et Lombok 1.18.48. Les numéros différents reflètent des projets différents. `dependencyInsight` montre la version sélectionnée et les chemins de dépendances ou règles responsables, ce qui aide à rechercher les conflits. Ces valeurs décrivent cet exemple, et non de futures valeurs par défaut ou une combinaison universelle de projet.

La chronologie n’est pas une table actuelle des cycles de support. Lors de la création ou de la mise à niveau d’un projet, vérifiez séparément les exigences, la compatibilité des dépendances et la politique de support de la release choisie. Voir la [migration Java 17 et Jakarta](/en/posts/2023-09-08-springboot3-migration/) pour passer à Boot 3, ou les [contrôles d’exécution IntelliJ et Gradle](/en/posts/2023-09-10-springboot-intellij-import/) pour l’exécution locale.
