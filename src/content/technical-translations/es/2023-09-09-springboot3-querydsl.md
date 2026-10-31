---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "es",
  "translationKey": "2023-09-09-springboot3-querydsl",
  "routeSlug": "2023-09-09-springboot3-querydsl",
  "kind": "post",
  "title": "Spring Boot 3 y Querydsl: configurar Jakarta y generar tipos Q",
  "description": "Genera tipos Q de Querydsl en Spring Boot 3 con dependencias Jakarta alineadas y procesamiento de anotaciones; verifica después una compilación limpia y consultas H2.",
  "categories": [
    "springboot"
  ],
  "tags": [
    "springboot",
    "springboot3",
    "querydsl"
  ],
  "sourcePath": "src/content/posts/en/2023-09-09-springboot3-querydsl.md",
  "sourceSha256": "17f0353d5a048f80291207543b7abbb29e1d987ab0435009b82a4e1c16a7d953",
  "draftSha256": "b98fdaa47600e25ba3b757304fe59801a9009537a9299ec00b09ef8b61640c12",
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

Para generar tipos Q de Querydsl JPA en Spring Boot 3, alinea las versiones y clasificadores `jakarta` de `querydsl-jpa` y `querydsl-apt`, configura el procesamiento de anotaciones y comprueba una compilación limpia y una prueba de consulta. Las [notas de Querydsl 5.0](https://github.com/querydsl/querydsl/releases/tag/QUERYDSL_5_0_0) documentan el clasificador Jakarta. Mantener las rutas predeterminadas de Gradle evita que la compilación principal y de pruebas escriban en el mismo directorio.

Esta guía desarrolla el ejemplo coreano original de 2023 hasta una configuración ejecutable. Las versiones fijan el entorno de reproducción; no recomiendan dependencias actuales para producción.

## Flujo de procesamiento

![Flujo de generación de tipos Q y consultas](/assets/diagrams/technical/es-2023-09-09-springboot3-querydsl.svg)

El procesador genera QEmployee durante la compilación principal. Después la prueba H2 ejecuta una consulta con esos tipos generados.

## Entorno de reproducción y configuración Gradle completa

| Componente | Versión de reproducción |
| --- | --- |
| JDK / Gradle | 17.0.8.1 / 8.4 |
| Spring Boot BOM | 3.5.7 |
| Querydsl JPA / APT | 5.1.0, ambos con clasificador `jakarta` |
| Hibernate / H2 | 6.6.33.Final / 2.3.232, gestionados por el BOM |

Crea estos cinco archivos en un directorio nuevo. El proyecto de pruebas usa el plugin Java y el BOM de Boot; no necesita el plugin Gradle de Boot. En una aplicación Boot existente, añade solo las dependencias necesarias junto a la gestión de dependencias elegida.

### `settings.gradle`

```groovy
rootProject.name = 'querydsl-jakarta-example'
```

### `build.gradle`

```groovy
plugins { id 'java' }
repositories { mavenCentral() }
dependencies {
    implementation platform('org.springframework.boot:spring-boot-dependencies:3.5.7')
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    implementation 'com.querydsl:querydsl-jpa:5.1.0:jakarta'

    annotationProcessor platform('org.springframework.boot:spring-boot-dependencies:3.5.7')
    annotationProcessor 'com.querydsl:querydsl-apt:5.1.0:jakarta'
    annotationProcessor 'jakarta.persistence:jakarta.persistence-api'
    annotationProcessor 'jakarta.annotation:jakarta.annotation-api'

    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testRuntimeOnly 'com.h2database:h2'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
test { useJUnitPlatform() }
```

Gradle resuelve `annotationProcessor` aparte de los classpath normales de compilación y ejecución. Por ello el ejemplo aplica el BOM también a la configuración del procesador y aporta explícitamente las API Jakarta Persistence y Annotation. Una dependencia `implementation` no está disponible automáticamente para el procesador. Consulta la [documentación del plugin Java de Gradle](https://docs.gradle.org/current/userguide/java_plugin.html).

## Crear la aplicación y la entidad

La clase de aplicación permite a la prueba JPA descubrir la configuración de Boot. No hace falta arrancar un proceso de servidor separado para la prueba.

### `src/main/java/example/Application.java`

```java
package example;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

### `src/main/java/example/Employee.java`

```java
package example;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;

@Entity
public class Employee {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;

    public String getName() { return name; }

    protected Employee() {}

    public Employee(String name) {
        this.name = name;
    }
}
```

`Employee` usa `jakarta.persistence`. No escribas `QEmployee` manualmente: el procesador de anotaciones genera el tipo al que se refiere la prueba siguiente.

## Consultar mediante el tipo Q generado

### `src/test/java/example/EmployeeQueryTest.java`

```java
package example;

import com.querydsl.jpa.impl.JPAQueryFactory;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.boot.test.autoconfigure.orm.jpa.TestEntityManager;

import static org.assertj.core.api.Assertions.assertThat;

@DataJpaTest
class EmployeeQueryTest {
    @Autowired
    private TestEntityManager entityManager;

    @Test
    void findsEmployeeByName() {
        entityManager.persistAndFlush(new Employee("Alice"));
        entityManager.persistAndFlush(new Employee("Bob"));
        QEmployee employee = QEmployee.employee;
        var names = new JPAQueryFactory(entityManager.getEntityManager())
            .select(employee.name).from(employee)
            .where(employee.name.eq("Alice")).fetch();
        assertThat(names).containsExactly("Alice");
    }

    @Test
    void returnsNoRowsForMissingName() {
        entityManager.persistAndFlush(new Employee("Alice"));
        QEmployee employee = QEmployee.employee;
        var names = new JPAQueryFactory(entityManager.getEntityManager())
            .select(employee.name).from(employee)
            .where(employee.name.eq("Missing")).fetch();
        assertThat(names).isEmpty();
    }
}
```

`@DataJpaTest` usa H2 del classpath del ejemplo. Cada prueba se ejecuta en una transacción y revierte después. Tras insertar datos con `persistAndFlush`, el `QEmployee` generado permite dos comprobaciones: coincidencia exacta de nombre y consulta sin filas. Consulta la [guía de pruebas JPA de Spring Boot](https://docs.spring.io/spring-boot/3.5/reference/testing/spring-boot-applications.html#testing.spring-boot-applications.autoconfigured-spring-data-jpa-tests).

Estas pruebas comprueban esta entidad y consulta en H2. No verifican el dialecto SQL, cotejamiento, bloqueo ni comportamiento de migraciones de tu base de producción.

## Ejecutar e inspeccionar los archivos generados

Selecciona JDK 17 y usa Gradle 8.4 instalado. Ejecuta desde la raíz del proyecto:

```sh
java -version
gradle --version
gradle --no-daemon clean test
```

Comprueba estos artefactos generados y el informe de pruebas:

```text
build/generated/sources/annotationProcessor/java/main/example/QEmployee.java
build/classes/java/main/example/QEmployee.class
build/reports/tests/test/index.html
```

Ambas pruebas pasaron con esta configuración. Repetir `clean test` regeneró el tipo Q y volvió a pasar ambas pruebas. En un proyecto existente con Gradle wrapper, usa su versión elegida mediante `./gradlew clean test`.

El tipo Q generado importa `javax.annotation.processing.Generated`, una API Java SE de `java.compiler`. Ese import no necesita reemplazo Jakarta. [API Generated de JDK 17](https://docs.oracle.com/en/java/javase/17/docs/api/java.compiler/javax/annotation/processing/Generated.html).

<span id="troubleshoot-missing-or-duplicate-q-types"></span>

## ¿Por qué faltan los tipos Q o se generan dos veces?

| Síntoma | Primera comprobación |
| --- | --- |
| No se encuentra `QEmployee` | Comprueba el resultado CLI `clean compileJava`, las dependencias del procesador y los imports `jakarta.persistence` de la entidad. |
| El procesador no encuentra las API Persistence | Comprueba que las API Jakarta necesarias estén en la ruta del procesador, aparte del classpath normal. |
| Aparece un tipo `javax.persistence.EntityManager` incompatible | Comprueba versiones coincidentes y clasificadores Jakarta para ambos artefactos Querydsl. |
| Tipos Q duplicados o compilación que solo funciona tras clean | Elimina fuentes Q manuales y rutas generadas compartidas; inspecciona la salida main/test. |
| CLI pasa pero el IDE no ve los tipos Q | Comprueba sincronización Gradle, compilación delegada y procesamiento de anotaciones del IDE. |

El ejemplo no añade configuración personalizada de `sourceSets`, `JavaCompile` ni `clean` para archivos generados. Si necesitas una ruta propia, separa las salidas main y test. `configureEach` controla la configuración diferida de tareas; no corrige la compatibilidad Jakarta. [Evitación de configuración de Gradle](https://docs.gradle.org/current/userguide/lazy_configuration.html).

Para la secuencia de actualización, consulta la [guía de migración a Spring Boot 3](/en/posts/2023-09-08-springboot3-migration/). Para límites HTTP salientes, usa las [pruebas WebClient y MockWebServer](/en/posts/2023-09-19-springboot-test-webclient/).

## Comparar antes de cambiar de herramienta de consultas

La clase Employee completa incluye un getter para comparar los resultados como nombres. Añade los tres archivos de la [comparación Querydsl y Specification](/en/posts/2023-09-05-querydsl-no-release/) para ejecutar ocho comprobaciones adicionales sobre la misma entidad. Las dos pruebas originales siguen formando parte de ese proyecto de diez pruebas. Compara predicados H2 seleccionados, no todo el comportamiento de la base. La [guía Spring Boot](/en/categories/springboot/) conecta los pasos de preparación y pruebas relacionados.
