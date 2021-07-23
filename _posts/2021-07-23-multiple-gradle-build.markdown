---
layout: posts
title:  "[Gradle] Gradle Multiple Vue Build"
date:   2021-07-23 03:00:00 +0900
categories: Gradle Vue Build
tags: Gradle Vue Build
---
Gradle에 여러개의 Vue Project Build하는 방법에 대해 알아보자.

구글링을 통하면 하나의 Vue Project Build만 나와있는 경우가 많다.

그럼 아래 가이드를 따라해보자!

---
Vue 프로젝트 구조
* frontend
    * project1
    * project2
    * project3
    
---

```groovy
// 1번 ------------------------------------------
plugins {
    ...
    id 'com.github.node-gradle.node' version '3.1.0'
}

...

// 2번 ------------------------------------------
node {
    version = '14.17.0'
    download = true
    nodeProjectDir = file("${projectDir}/frontend")
}

// 4번 ------------------------------------------
task setUp(type: NpmTask) {
    description = "install nodeJS packages"
    args = ["install"]
}

// 5번 ------------------------------------------
task categoryBuild(type: NpmTask, dependsOn: setUp) {
    description = "Build Category"
    workingDir = file("${projectDir}/frontend/category")
    args = ["run", "build:${project.ext.profile}"]
}

task planningBuild(type: NpmTask, dependsOn: setUp) {
    description = "Build Planning"
    workingDir = file("${projectDir}/frontend/planning")
    args = ["run", "build:${project.ext.profile}"]
}

// 6번 ------------------------------------------

if ('jenkins' == project.ext.mode) {

    def targetProjects = targetsSetting("${project.ext.targets}")

    def projects = []
    new File("${project.projectDir}/frontend").eachDir { temp ->

        projects << targetProjects.stream()
                .filter({ it == temp.name })
                .findFirst()
                .orElse("*")
    }

    projects.stream()
            .filter({ it != "*" })
            .forEach() { projectName ->
                processResources.dependsOn "${projectName}Build"
            }
}

// 7번 ------------------------------------------

static def targetsSetting(String targets) {

    if (!targets) {
        return []
    }

    if (!targets.contains(",")) {
        return [targets]
    }

    return targets.split(",")
}
```