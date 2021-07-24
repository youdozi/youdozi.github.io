---
layout: posts 
title:  "[Gradle] Gradle Spring BootMultiple Vue Build"
date:   2021-07-23 03:00:00 +0900 
categories: 
  - Gradle 
  - SpringBoot 
  - Vue
tags:
  - Gradle 
  - Vue
  - Build
  - SpringBoot
---

구글 검색을 해보면 Spring Boot Gradle + 하나의 vueJS Project Build만 나와있는 경우가 많다.

조금 더 응용하여 Spring Boot Gradl + 여러개의 vueJS 빌드하는 방법에 대해 공유하고자 한다.

---
Vue 프로젝트 구조 .

* [frontend](./frontend)
    * [project1](./frontend/project1)
    * [project2](./frontend/project2)
    * [project3](./frontend/project3)
* [build.gradle](.build.gradle)
* [gradlew](.gradlew)


---
build.gradle 수정!!

```groovy
plugins {
    /**
     * https://github.com/node-gradle/gradle-node-plugin 
     * nodeJS 빌드를 gradle에서 해준다. 계속 유지보수중이라 사용하기 좋음
     */
    id 'com.github.node-gradle.node' version '3.1.0'
}

node {
    // nodeJS 버전을 지정한다.
    version = '14.17.0'
    // true일 경우 위에 지정한 node version으로 다운로드 받아서 실행한다.
    // 따로 설치하지 않을려면 download = true로 진행
    // false일 경우 global로 설치된 nodeJS가 있어야한다.
    download = true
  
    // nodeJS 프로젝트 location 지정
    // default로 하나의 프로젝트를 지정하도록 함
    nodeProjectDir = file("${projectDir}/frontend/project1")
}

/**
 * dependsOn: setUp이 걸려있는 task는 먼저 dependsOn을 실행 후 해당 task를 실행한다.
 * task setup은 vueJS 프로젝트에 필요한 package를 install 한다.
 */
task setUp(type: NpmTask) {
    description = "install nodeJS packages"
    args = ["install"]
}

/**
 * 빌드 대상 vueJS project를 각각 task로 설정한다.
 * workingDir로 각각의 프로젝트 root 폴더를 바라볼 수 있도록 한다.
 */
task project1Build(type: NpmTask, dependsOn: setUp) {
    description = "Build Project1"
    workingDir = file("${projectDir}/frontend/project1")
    args = ["run", "build"]
}

task project2Build(type: NpmTask, dependsOn: setUp) {
    description = "Build Project2"
    workingDir = file("${projectDir}/frontend/project2")
    args = ["run", "build"]
}

task project3Build(type: NpmTask, dependsOn: setUp) {
  description = "Build Project3"
  workingDir = file("${projectDir}/frontend/project3")
  args = ["run", "build"]
}

/**
 * frontend 하위 dir을 돌면서 위 project build task를 실행한다.
 */
new File("${project.projectDir}/frontend").eachDir { projectName ->
  processResources.dependsOn "${projectName}Build"
}
```

빌드 결과!! 

아래 순으로 Task가 진행되는것을 볼 수 있다.
- Task :nodeSetup
- Task :setUp
- Task :project1Build
- Task :project2Build
- Task :project3Build
- spring boot 관련 빌드 진행...

```groovy
3:04:13 오후: Executing task 'build --stacktrace'...
 
> Task :compileJava UP-TO-DATE
> Task :nodeSetup
> Task :npmSetup SKIPPED
 
> Task :setUp
audited 1413 packages in 5.638s
 
78 packages are looking for funding
  run `npm fund` for details
 
found 132 vulnerabilities (119 moderate, 12 high, 1 critical)
  run `npm audit fix` to fix them, or `npm audit` for details
 
> Task :project1Build
 
> frontend@0.1.0 build /Users/test-project/frontend/project1
> vue-cli-service build
 
##### vue build target: local
 
-  Building for local...
 WARNING  Compiled with 2 warnings3:04:36 PM
 
 warning 
 
asset size limit: The following asset(s) exceed the recommended size limit (244 KiB).
This can impact web performance.
Assets:
  js/chunk-vendors.3555b132.js (462 KiB)
 
 warning 
 
entrypoint size limit: The following entrypoint(s) combined asset size exceeds the recommended limit (244 KiB). This can impact web performance.
Entrypoints:
  app (485 KiB)
      js/chunk-vendors.3555b132.js
      css/app.342c0a50.css
      js/app.56e7b3cf.js
 
 
  File                                      Size             Gzipped
 
  ../../src/main/resources/static/project1    461.58 KiB       139.39 KiB
  /js/chunk-vendors.3555b132.js
  ../../src/main/resources/static/project1    200.11 KiB       51.43 KiB
  /js/chunk-056e7852.0f916084.js
  ../../src/main/resources/static/project1    21.72 KiB        8.28 KiB
  /js/chunk-48d802ba.aba8d5b7.js
  ../../src/main/resources/static/project1    19.25 KiB        6.50 KiB
  /js/app.56e7b3cf.js
  ../../src/main/resources/static/project1    8.67 KiB         3.23 KiB
  /js/chunk-082c73ca.b0789044.js
  ../../src/main/resources/static/project1    1.52 KiB         0.69 KiB
  /js/chunk-27a95d4c.a63c84a3.js
  ../../src/main/resources/static/project1    1.06 KiB         0.62 KiB
  /js/chunk-091955a4.571caf72.js
  ../../src/main/resources/static/project1    30.17 KiB        6.99 KiB
  /css/chunk-056e7852.414581ae.css
  ../../src/main/resources/static/project1    4.06 KiB         1.42 KiB
  /css/app.342c0a50.css
  ../../src/main/resources/static/project1    2.41 KiB         0.73 KiB
  /css/chunk-082c73ca.d4e9cbb2.css
  ../../src/main/resources/static/project1    0.51 KiB         0.29 KiB
  /css/chunk-27a95d4c.b03457a9.css
  ../../src/main/resources/static/project1    0.38 KiB         0.24 KiB
  /css/chunk-091955a4.0584ada6.css
  ../../src/main/resources/static/project1    0.04 KiB         0.06 KiB
  /css/chunk-48d802ba.28bb29d4.css
 
  Images and other types of assets omitted.
 
 DONE  Build complete. The ../../src/main/resources/static/project1 directory is ready to be deployed.
 INFO  Check out deployment instructions at https://cli.vuejs.org/guide/deployment.html


> Task :project2Build

        > frontend@0.1.0 build /Users/test-project/frontend/project2
        > vue-cli-service build

##### vue build target: local

-  Building for local...
WARNING  Compiled with 2 warnings3:04:36 PM

warning

asset size limit: The following asset(s) exceed the recommended size limit (244 KiB).
This can impact web performance.
Assets:
js/chunk-vendors.3555b132.js (462 KiB)

warning

entrypoint size limit: The following entrypoint(s) combined asset size exceeds the recommended limit (244 KiB). This can impact web performance.
Entrypoints:
app (485 KiB)
js/chunk-vendors.3555b132.js
css/app.342c0a50.css
js/app.56e7b3cf.js


File                                      Size             Gzipped

        ../../src/main/resources/static/project2    461.58 KiB       139.39 KiB
/js/chunk-vendors.3555b132.js
        ../../src/main/resources/static/project2    200.11 KiB       51.43 KiB
/js/chunk-056e7852.0f916084.js
        ../../src/main/resources/static/project2    21.72 KiB        8.28 KiB
/js/chunk-48d802ba.aba8d5b7.js
        ../../src/main/resources/static/project2    19.25 KiB        6.50 KiB
/js/app.56e7b3cf.js
        ../../src/main/resources/static/project2    8.67 KiB         3.23 KiB
/js/chunk-082c73ca.b0789044.js
        ../../src/main/resources/static/project2    1.52 KiB         0.69 KiB
/js/chunk-27a95d4c.a63c84a3.js
        ../../src/main/resources/static/project2    1.06 KiB         0.62 KiB
/js/chunk-091955a4.571caf72.js
        ../../src/main/resources/static/project2    30.17 KiB        6.99 KiB
/css/chunk-056e7852.414581ae.css
        ../../src/main/resources/static/project2    4.06 KiB         1.42 KiB
/css/app.342c0a50.css
        ../../src/main/resources/static/project2    2.41 KiB         0.73 KiB
/css/chunk-082c73ca.d4e9cbb2.css
        ../../src/main/resources/static/project2    0.51 KiB         0.29 KiB
/css/chunk-27a95d4c.b03457a9.css
        ../../src/main/resources/static/project2    0.38 KiB         0.24 KiB
/css/chunk-091955a4.0584ada6.css
        ../../src/main/resources/static/project2    0.04 KiB         0.06 KiB
/css/chunk-48d802ba.28bb29d4.css

Images and other types of assets omitted.

DONE  Build complete. The ../../src/main/resources/static/project2 directory is ready to be deployed.
INFO  Check out deployment instructions at https://cli.vuejs.org/guide/deployment.html


> Task :project3Build

        > frontend@0.1.0 build /Users/test-project/frontend/project3
        > vue-cli-service build

##### vue build target: local

-  Building for local...
WARNING  Compiled with 2 warnings3:04:36 PM

warning

asset size limit: The following asset(s) exceed the recommended size limit (244 KiB).
This can impact web performance.
Assets:
js/chunk-vendors.3555b132.js (462 KiB)

warning

entrypoint size limit: The following entrypoint(s) combined asset size exceeds the recommended limit (244 KiB). This can impact web performance.
Entrypoints:
app (485 KiB)
js/chunk-vendors.3555b132.js
css/app.342c0a50.css
js/app.56e7b3cf.js


File                                      Size             Gzipped

        ../../src/main/resources/static/project3    461.58 KiB       139.39 KiB
/js/chunk-vendors.3555b132.js
        ../../src/main/resources/static/project3    200.11 KiB       51.43 KiB
/js/chunk-056e7852.0f916084.js
        ../../src/main/resources/static/project3    21.72 KiB        8.28 KiB
/js/chunk-48d802ba.aba8d5b7.js
        ../../src/main/resources/static/project3    19.25 KiB        6.50 KiB
/js/app.56e7b3cf.js
        ../../src/main/resources/static/project3    8.67 KiB         3.23 KiB
/js/chunk-082c73ca.b0789044.js
        ../../src/main/resources/static/project3    1.52 KiB         0.69 KiB
/js/chunk-27a95d4c.a63c84a3.js
        ../../src/main/resources/static/project3    1.06 KiB         0.62 KiB
/js/chunk-091955a4.571caf72.js
        ../../src/main/resources/static/project3    30.17 KiB        6.99 KiB
/css/chunk-056e7852.414581ae.css
        ../../src/main/resources/static/project3    4.06 KiB         1.42 KiB
/css/app.342c0a50.css
        ../../src/main/resources/static/project3    2.41 KiB         0.73 KiB
/css/chunk-082c73ca.d4e9cbb2.css
        ../../src/main/resources/static/project3    0.51 KiB         0.29 KiB
/css/chunk-27a95d4c.b03457a9.css
        ../../src/main/resources/static/project3    0.38 KiB         0.24 KiB
/css/chunk-091955a4.0584ada6.css
        ../../src/main/resources/static/project3    0.04 KiB         0.06 KiB
/css/chunk-48d802ba.28bb29d4.css

Images and other types of assets omitted.

DONE  Build complete. The ../../src/main/resources/static/project3 directory is ready to be deployed.
INFO  Check out deployment instructions at https://cli.vuejs.org/guide/deployment.html


> Task :processResources UP-TO-DATE
> Task :classes UP-TO-DATE
> Task :bootJar UP-TO-DATE
> Task :jar SKIPPED
> Task :assemble UP-TO-DATE
> Task :compileTestJava UP-TO-DATE
> Task :processTestResources NO-SOURCE
> Task :testClasses UP-TO-DATE
> Task :test UP-TO-DATE
> Task :check UP-TO-DATE
> Task :build UP-TO-DATE
 
Deprecated Gradle features were used in this build, making it incompatible with Gradle 7.0.
Use '--warning-mode all' to show the individual deprecation warnings.
See https://docs.gradle.org/6.3/userguide/command_line_interface.html#sec:command_line_warnings
 
BUILD SUCCESSFUL in 34s
9 actionable tasks: 4 executed, 5 up-to-date
3:04:48 오후: Task execution finished 'build --stacktrace'.
```

gradle build 성공!!

위 코드를 조금만 응용하면 선택한 vueJS project만 build하는것도 가능하다!!