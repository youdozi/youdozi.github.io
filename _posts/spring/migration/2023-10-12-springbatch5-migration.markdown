---
layout: posts
title: "[spring batch] spring batch 5 migration"
date: 2023-10-24 00:00:00 +0900
categories:
  - spring
tags:
  - spring batch
  - migration
---

## 개요

spring boot3가 release되면서 spring batch 5로 업그레이드 되었습니다.  
간단하게 종속성 업그레이드로 끝나는것이 아니라 DB 스키마 변경과 jobBuilder, stepBuilder 작동 방식도 변경되었습니다.  
이 부분에 대해 간단하게 정리하도록 하겠습니다.

### JDK 17
spring batch 5는 jdk 17이 최소 사양인 spring framework 6 기반으로 합니다.  

### jakarta 패키지
javax 패키지는 전부 다 jakarta로 변경해야 한다.

### DB 스키마 업데이트
oracle과 sql-server인 경우는 sequence 관련 업데이트가 있습니다.  
그외 모든 플랫폼은 아래와 같은 스키마 변경 사항이 있습니다.

#### BATCH_JOB_EXECUTION
JOB_CONFIGURATION_LOCATION 컬럼은 사용되지 않습니다.  
아래 쿼리로 컬럼을 삭제하도록 합니다.
```roomsql
ALTER TABLE BATCH_JOB_EXECUTION DROP COLUMN JOB_CONFIGURATION_LOCATION;
```

#### BATCH_JOB_EXECUTION_PARAMS

batch parameter로 사용되던 string, date, long, double형 대신 `<T>` 제레릭으로 받을수 있게 변경되었습니다.

그리하여 각 해당 컬럼들은 삭제되고 PARAMETER_NAME, PARAMETER_TYPE, PARAMETER_VALUE 컬럼이 새로 생성되었죠.

```git
CREATE TABLE BATCH_JOB_EXECUTION_PARAMS  (
JOB_EXECUTION_ID BIGINT NOT NULL ,
---	TYPE_CD VARCHAR(6) NOT NULL ,
---	KEY_NAME VARCHAR(100) NOT NULL ,
---	STRING_VAL VARCHAR(250) ,
---	DATE_VAL DATETIME(6) DEFAULT NULL ,
---	LONG_VAL BIGINT ,
---	DOUBLE_VAL DOUBLE PRECISION ,
+++	PARAMETER_NAME VARCHAR(100) NOT NULL ,
+++	PARAMETER_TYPE VARCHAR(100) NOT NULL ,
+++	PARAMETER_VALUE VARCHAR(2500) ,
IDENTIFYING CHAR(1) NOT NULL ,
constraint JOB_EXEC_PARAMS_FK foreign key (JOB_EXECUTION_ID)
references BATCH_JOB_EXECUTION(JOB_EXECUTION_ID)
);
```
아래 쿼리를 통해 변경하도록 합니다.

```roomsql
ALTER TABLE BATCH_JOB_EXECUTION_PARAMS DROP COLUMN DATE_VAL;
ALTER TABLE BATCH_JOB_EXECUTION_PARAMS DROP COLUMN LONG_VAL;
ALTER TABLE BATCH_JOB_EXECUTION_PARAMS DROP COLUMN DOUBLE_VAL;

ALTER TABLE BATCH_JOB_EXECUTION_PARAMS CHANGE COLUMN TYPE_CD PARAMETER_TYPE VARCHAR(100);
ALTER TABLE BATCH_JOB_EXECUTION_PARAMS CHANGE COLUMN KEY_NAME PARAMETER_NAME VARCHAR(100);
ALTER TABLE BATCH_JOB_EXECUTION_PARAMS CHANGE COLUMN STRING_VAL PARAMETER_VALUE VARCHAR(2500);
```

spring batch 5로 migration하는 경우 위 ALTER 쿼리 실행시 크리티컬한 버그가 있습니다.  

```roomsql
ALTER TABLE BATCH_JOB_EXECUTION_PARAMS CHANGE COLUMN TYPE_CD PARAMETER_TYPE VARCHAR(100);
```
위 쿼리가 문제인데 spring batch 4일 경우 Long 타입은 TYPE_CD에 LONG 으로 저장되어 있습니다.

하지만 spring batch 5일 경우  PARAMETER_TYPE 에 java.lang.Long 으로 저장됩니다.

spring batch 5에서 신규로 만들어진 job이면 문제없지만 이전 버전부터 사용하고 있던 job을 실행하면 오류를 뿜뿜하고 나올 것입니다.

아래와 같이 여러 대안이 있죠.
1. string, date, long, double 의 각각 패키지명까지 포함하여 update 처리
2. 테이블 삭제 후 재생성(not recommend)
3. spring-cloud-data-flow 2.11.x 버전 적용

각각의 장단점이 있으니 신중하게 고려해서 선택하는것이 좋습니다.

#### BATCH_STEP_EXECUTION
CREATE_TIME 컬럼이 신규로 생성되었으며 START_TIME 컬럼에 NOT_NULL 조건이 삭제됩니다.

아래 쿼리로 변경하면 됩니다.

```roomsql
ALTER TABLE BATCH_STEP_EXECUTION ADD CREATE_TIME DATETIME(6) NOT NULL DEFAULT '1970-01-01 00:00:00';
ALTER TABLE BATCH_STEP_EXECUTION MODIFY START_TIME DATETIME(6) NULL;
```

### Job repository/explorer 구현 삭제

spring batch 4에서는 아래와 같이 BatchConfigurer을 직접 구현해야 했습니다.

spring batch 5에서는 BatchConfigurer가 제거되었고 DefaultBatchConfiguration를 상속하여 커스터마이징만 하면 됩니다.

#### as-is
```java
@Configuration
public class CustomBatchConfigurer implements BatchConfigurer, BeanPostProcessor {

    private final DataSource dataSource;
    private final PlatformTransactionManager transactionManager;
    
    private JobRepository jobRepository;
    private JobLauncher jobLauncher;
    private JobExplorer jobExplorer;

    @Lazy
    public CustomBatchConfigurer(@Qualifier("dataflowLazyDataSource") DataSource dataSource,
        @Qualifier("dataflowTransactionManager") PlatformTransactionManager dataflowTransactionManager) {
        this.dataSource = dataSource;
        this.transactionManager = dataflowTransactionManager;
        initialize();
    }

    @NotNull
    @Override
    public JobRepository getJobRepository() {
        return this.jobRepository;
    }

    @NotNull
    @Override
    public PlatformTransactionManager getTransactionManager() {
        return this.transactionManager;
    }

    @NotNull
    @Override
    public JobLauncher getJobLauncher() {
        return this.jobLauncher;
    }

    @NotNull
    @Override
    public JobExplorer getJobExplorer() {
        return this.jobExplorer;
    }

    private void initialize() {
    
        try {
          this.jobRepository = createJobRepository();
          this.jobExplorer = createJobExplorer();
          this.jobLauncher = createJobLauncher();
    
        } catch (Exception e) {
          throw new BatchConfigurationException(e);
        }
    }

    private JobLauncher createJobLauncher() throws Exception {
        SimpleJobLauncher jobLauncher = new SimpleJobLauncher();
    
        jobLauncher.setJobRepository(this.jobRepository);
        jobLauncher.afterPropertiesSet();
    
        return jobLauncher;
    }
    
    private JobExplorer createJobExplorer() throws Exception {
        JobExplorerFactoryBean jobExplorerFactoryBean = new JobExplorerFactoryBean();
    
        jobExplorerFactoryBean.setDataSource(this.dataSource);
        jobExplorerFactoryBean.afterPropertiesSet();
    
        return jobExplorerFactoryBean.getObject();
    }

    private JobRepository createJobRepository() throws Exception {
        JobRepositoryFactoryBean jobRepositoryFactoryBean = new JobRepositoryFactoryBean();
    
        jobRepositoryFactoryBean.setDataSource(this.dataSource);
        jobRepositoryFactoryBean.setTransactionManager(this.transactionManager);
        jobRepositoryFactoryBean.afterPropertiesSet();
    
        return jobRepositoryFactoryBean.getObject();
    }
}
```
#### to-be
```java
@Configuration
public class CustomBatchConfigurer extends DefaultBatchConfiguration {

    private final DataSource dataSource;
    private final PlatformTransactionManager transactionManager;
    
    public CustomBatchConfigurer(@Qualifier("dataflowLazyDataSource") DataSource dataSource,
        @Qualifier("dataflowTransactionManager") PlatformTransactionManager dataflowTransactionManager) {
        this.dataSource = dataSource;
        this.transactionManager = dataflowTransactionManager;
    }
    
    @Override
    protected @NotNull DataSource getDataSource() {
        return this.dataSource;
    }
    
    @Override
    protected @NotNull PlatformTransactionManager getTransactionManager() {
        return this.transactionManager;
    }
}
```
또한 @EnableBatchProcessing 어노테이션방식으로 dataSourceRef, transactionManagerRef 등 다양한 옵션을 넣을 수 있습니다.

```java
@Configuration
@EnableBatchProcessing(dataSourceRef = "dataflowLazyDataSource",
transactionManagerRef = "dataflowTransactionManager")
public class CustomBatchConfigurer implements BeanPostProcessor {

}
```
DefaultBatchConfiguration와 @EnableBatchProcessing 동시에 사용 불가하다.

### 명시적 transactionManager 구성

spring batch 4까지는 @EnableBatchProcessing 를 통해 트랜잭션 매니저가 spring context에 노출되었습니다.

하지만 무조건적인 노출은 사용자 정의 트랜잭션 매니저 적용하는데 문제가 발생하게 되었죠.

관련 이슈 →

이 부분을 수정하기 위해 tasklet에서도 명시적으로 transactionManager를 구성하도록 변경되었습니다.

#### as-is
```java
// Sample with v4
@Configuration
@EnableBatchProcessing
public class MyStepConfig {

    @Autowired
    private StepBuilderFactory stepBuilderFactory;

    @Bean
    public Step myStep() {
        return this.stepBuilderFactory.get("myStep")
                .tasklet(..) // or .chunk()
                .build();
    }

}
```
#### to-be
```java
// Sample with v5
@Configuration
@EnableBatchProcessing
public class MyStepConfig {

    @Bean
    public Tasklet myTasklet() {
       return new MyTasklet();
    }

    @Bean
    public Step myStep(JobRepository jobRepository, Tasklet myTasklet, PlatformTransactionManager transactionManager) {
        return new StepBuilder("myStep", jobRepository)
                .tasklet(myTasklet, transactionManager) // or .chunk(chunkSize, transactionManager)
                .build();
    }

}
```

### JobBuilderFactory/StepBuilderFactory deprecated

JobBuilderFactory/StepBuilderFactory가 deprecated되었으며 spring context에서도 삭제되었습니다.

메서드는 아직 삭제되지 않았지만 intellij에서 warning 메시지를 노출할 것입니다.

아래와 같이 name, jobRepository를 parameter로 하여 생성하도록 합니다.

#### as-is
```java
// Sample with v4
@Configuration
@EnableBatchProcessing
public class MyJobConfig {

    @Autowired
    private JobBuilderFactory jobBuilderFactory;

    @Bean
    public Job myJob(Step step) {
        return this.jobBuilderFactory.get("myJob")
                .start(step)
                .build();
    }

}
```
### to-be
```java
// Sample with v5
@Configuration
@EnableBatchProcessing
public class MyJobConfig {

    @Bean
    public Job myJob(JobRepository jobRepository, Step step) {
        return new JobBuilder("myJob", jobRepository)
                .start(step)
                .build();
    }

}

```

## 번외 
### spring-cloud-data-flow 2.11.x migration

항공 배치, 스케줄러를 springboot3로 마이그레이션 하면서 자연스럽게 spring batch 5를 접해보고 있었는데 spring-cloud-data-flow가 아직 미지원이라 놓고 있었다.

그런데 springboot3가 나오고 거의 1년 다되서야 springboot3, spring batch 5 지원하는 spring-cloud-data-flow가 release 되었다.(2023-09-20) 😡😡😡😡😡

spring batch 5를 지원하면서도 spring batch 5 하위 버전도 지원하는 모양새로 전략을 잡아서 관련 스키마 생성이 좀 요상하게 되었다.

spring batch 5 → BOOT3_BATCH_JOB_EXECUTION, BOOT3_TASK_EXECUTION

spring batch 4 → BATCH_JOB_EXECUTION, TASK_EXECUTION

저 네이밍 방식 때문에 spring batch 5 application은 job repository 설정에 table_prefix 값을 강제로 넣어줘야하는 귀찮음이 발생한다. 이것은 spring-cloud-task도 마찬가지.

차라리 spring-cloud-data-flow jar 실행시 옵션값을 넣어 spring batch 5만 사용할 수 있게 해주던가 하위 버전만 사용할 수 있게 해주는게 좋아보이긴 하는데..

그들만의 사정이 있을꺼라 생각된다. spring batch 같은 경우 마이그레이션이 손쉬운 것도 아니고..

또 우리같은 경우 spring-cloud-data-flow 기능의 30%도 활용하지 못한 상태로 구동하고 있기 때문에(로그성으로만 사용) 우선은 간단하게 위 table_prefix만 맞춰보도록 한다.

먼저 spring-cloud-data-flow를 가동하고 이후 연관 application을 수정한다.

spring-cloud-data-flow

java -cp /Users/lincoln/IdeaProjects/spring-cloud-data-flow/spring-cloud-dataflow-server-2.11.0.jar \
-Dloader.path=/Users/lincoln/IdeaProjects/spring-cloud-data-flow/lib \
org.springframework.boot.loader.PropertiesLauncher \
--spring.config.additional-location=file:/Users/lincoln/IdeaProjects/spring-cloud-data-flow/application-local.yml

java -cp 명령어를 통해 가동한다. 공식 문서에서는 mysql도 mariadb 드라이버로 가동된다고 했으나 실제로 돌려보면 뻑난다.

그래서 mysql 드라이버를 /Users/lincoln/IdeaProjects/spring-cloud-data-flow/lib 디렉토리에 다운로드 받고 저 위치를 참조한다.

그리고 spring.config.additional-location 통해 외부 application.yml을 참조한다.

2023-10-05 15:21:40.860  INFO 32049 --- [           main] o.s.c.d.a.l.ProfileApplicationListener   : Setting property 'spring.cloud.kubernetes.enabled' to false.
2023-10-05 15:21:40.918  INFO 32049 --- [kground-preinit] o.h.validator.internal.util.Version      : HV000001: Hibernate Validator 6.2.5.Final
2023-10-05 15:21:40.939  WARN 32049 --- [           main] ubernetesProfileEnvironmentPostProcessor : Not running inside kubernetes. Skipping 'kubernetes' profile activation.
2023-10-05 15:21:41.312  INFO 32049 --- [           main] o.s.c.d.a.l.ProfileApplicationListener   : Setting property 'spring.cloud.kubernetes.enabled' to false.
  ____                              ____ _                __
/ ___| _ __  _ __(_)_ __   __ _   / ___| | ___  _   _  __| |
\___ \| '_ \| '__| | '_ \ / _` | | |   | |/ _ \| | | |/ _` |
___) | |_) | |  | | | | | (_| | | |___| | (_) | |_| | (_| |
|____/| .__/|_|  |_|_| |_|\__, |  \____|_|\___/ \__,_|\__,_|
____ |_|    _          __|___/                 __________
|  _ \  __ _| |_ __ _  |  ___| | _____      __  \ \ \ \ \ \
| | | |/ _` | __/ _` | | |_  | |/ _ \ \ /\ / /   \ \ \ \ \ \
| |_| | (_| | || (_| | |  _| | | (_) \ V  V /    / / / / / /
|____/ \__,_|\__\__,_| |_|   |_|\___/ \_/\_/    /_/_/_/_/_/



2023-10-05 15:21:41.368  INFO 32049 --- [           main] c.c.c.ConfigServicePropertySourceLocator : Fetching config from server at : http://localhost:8888
2023-10-05 15:21:41.451  INFO 32049 --- [           main] c.c.c.ConfigServicePropertySourceLocator : Connect Timeout Exception on Url - http://localhost:8888. Will be trying the next url if available
2023-10-05 15:21:41.451  WARN 32049 --- [           main] c.c.c.ConfigServicePropertySourceLocator : Could not locate PropertySource: I/O error on GET request for "http://localhost:8888/spring-cloud-dataflow-server/local": Connection refused; nested exception is java.net.ConnectException: Connection refused
2023-10-05 15:21:41.453  WARN 32049 --- [           main] ubernetesProfileEnvironmentPostProcessor : Not running inside kubernetes. Skipping 'kubernetes' profile activation.
2023-10-05 15:21:41.453  INFO 32049 --- [           main] o.s.c.d.s.s.DataFlowServerApplication    : The following 1 profile is active: "local"
2023-10-05 15:21:42.212  INFO 32049 --- [           main] .s.d.r.c.RepositoryConfigurationDelegate : Multiple Spring Data modules found, entering strict repository configuration mode
2023-10-05 15:21:42.213  INFO 32049 --- [           main] .s.d.r.c.RepositoryConfigurationDelegate : Bootstrapping Spring Data Map repositories in DEFAULT mode.
2023-10-05 15:21:42.315  INFO 32049 --- [           main] .s.d.r.c.RepositoryConfigurationDelegate : Finished Spring Data repository scanning in 92 ms. Found 1 Map repository interfaces.
2023-10-05 15:21:42.559  INFO 32049 --- [           main] .s.d.r.c.RepositoryConfigurationDelegate : Multiple Spring Data modules found, entering strict repository configuration mode
2023-10-05 15:21:42.560  INFO 32049 --- [           main] .s.d.r.c.RepositoryConfigurationDelegate : Bootstrapping Spring Data JPA repositories in DEFAULT mode.
2023-10-05 15:21:42.565  INFO 32049 --- [           main] .s.d.r.c.RepositoryConfigurationDelegate : Finished Spring Data repository scanning in 1 ms. Found 0 JPA repository interfaces.
2023-10-05 15:21:42.722  INFO 32049 --- [           main] .s.d.r.c.RepositoryConfigurationDelegate : Multiple Spring Data modules found, entering strict repository configuration mode
2023-10-05 15:21:42.722  INFO 32049 --- [           main] .s.d.r.c.RepositoryConfigurationDelegate : Bootstrapping Spring Data JPA repositories in DEFAULT mode.
2023-10-05 15:21:42.765  INFO 32049 --- [           main] .s.d.r.c.RepositoryConfigurationDelegate : Finished Spring Data repository scanning in 42 ms. Found 5 JPA repository interfaces.
2023-10-05 15:21:42.954  INFO 32049 --- [           main] o.s.cloud.context.scope.GenericScope     : BeanFactory id=5fb2de35-fe13-3599-80c3-50d150aef5b7
2023-10-05 15:21:43.392  INFO 32049 --- [           main] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat initialized with port(s): 9393 (http)
2023-10-05 15:21:43.403  INFO 32049 --- [           main] o.a.coyote.http11.Http11NioProtocol      : Initializing ProtocolHandler ["http-nio-9393"]
2023-10-05 15:21:43.404  INFO 32049 --- [           main] o.apache.catalina.core.StandardService   : Starting service [Tomcat]
2023-10-05 15:21:43.404  INFO 32049 --- [           main] org.apache.catalina.core.StandardEngine  : Starting Servlet engine: [Apache Tomcat/9.0.79]
2023-10-05 15:21:43.453  INFO 32049 --- [           main] o.a.c.c.C.[Tomcat].[localhost].[/]       : Initializing Spring embedded WebApplicationContext
2023-10-05 15:21:43.652  INFO 32049 --- [           main] com.zaxxer.hikari.HikariDataSource       : HikariPool-1 - Starting...
2023-10-05 15:21:43.763  INFO 32049 --- [           main] com.zaxxer.hikari.HikariDataSource       : HikariPool-1 - Start completed.
2023-10-05 15:21:43.776  INFO 32049 --- [           main] .m.DataFlowFlywayConfigurationCustomizer : Adding vendor specific Flyway callback for MYSQL
2023-10-05 15:21:43.817  INFO 32049 --- [           main] o.f.c.internal.license.VersionPrinter    : Flyway Community Edition 8.5.13 by Redgate
2023-10-05 15:21:43.817  INFO 32049 --- [           main] o.f.c.internal.license.VersionPrinter    : See what's new here: https://flywaydb.org/documentation/learnmore/releaseNotes#8.5.13
2023-10-05 15:21:43.817  INFO 32049 --- [           main] o.f.c.internal.license.VersionPrinter    :
2023-10-05 15:21:43.846  INFO 32049 --- [           main] o.f.c.i.database.base.BaseDatabaseType   : Database: jdbc:mysql://127.0.0.1:3306/dataflow (MySQL 8.1)
2023-10-05 15:21:43.893  WARN 32049 --- [           main] o.f.c.internal.database.base.Database    : Flyway upgrade recommended: MySQL 8.1 is newer than this version of Flyway and support has not been tested. The latest supported version of MySQL is 8.0.
2023-10-05 15:21:43.912  INFO 32049 --- [           main] o.f.core.internal.command.DbValidate     : Successfully validated 9 migrations (execution time 00:00.011s)
2023-10-05 15:21:43.932  INFO 32049 --- [           main] o.f.c.i.s.JdbcTableSchemaHistory         : Creating Schema History table `dataflow`.`flyway_schema_history_dataflow` ...
2023-10-05 15:21:43.983  INFO 32049 --- [           main] o.f.core.internal.command.DbMigrate      : Current version of schema `dataflow`: << Empty Schema >>
2023-10-05 15:21:43.988  INFO 32049 --- [           main] o.f.core.internal.command.DbMigrate      : Migrating schema `dataflow` to version "1 - Initial Setup"
2023-10-05 15:21:44.346  INFO 32049 --- [           main] o.f.core.internal.command.DbMigrate      : Migrating schema `dataflow` to version "2 - Add Descriptions And OriginalDefinition"
2023-10-05 15:21:44.444  INFO 32049 --- [           main] o.f.core.internal.command.DbMigrate      : Migrating schema `dataflow` to version "3 - Add Platform To AuditRecords"
2023-10-05 15:21:44.485  INFO 32049 --- [           main] o.f.core.internal.command.DbMigrate      : Migrating schema `dataflow` to version "4 - Add Step Name Indexes"
2023-10-05 15:21:44.525  INFO 32049 --- [           main] o.f.core.internal.command.DbMigrate      : Migrating schema `dataflow` to version "5 - Add Task Execution Params Indexes"
2023-10-05 15:21:44.572  INFO 32049 --- [           main] o.f.core.internal.command.DbMigrate      : Migrating schema `dataflow` to version "6 - Boot3 Boot Version"
2023-10-05 15:21:44.612  INFO 32049 --- [           main] o.f.core.internal.command.DbMigrate      : Migrating schema `dataflow` to version "7 - Boot3 Add Task3 Batch5 Schema"
2023-10-05 15:21:44.889  INFO 32049 --- [           main] o.f.core.internal.command.DbMigrate      : Migrating schema `dataflow` to version "8 - RenameLowerCaseTables"
2023-10-05 15:21:44.948  INFO 32049 --- [           main] o.f.core.internal.command.DbMigrate      : Migrating schema `dataflow` to version "9 - AddAggregateViews"
2023-10-05 15:21:44.999  INFO 32049 --- [           main] o.f.core.internal.command.DbMigrate      : Successfully applied 9 migrations to schema `dataflow`, now at version v9 (execution time 00:01.022s)
2023-10-05 15:21:45.072  INFO 32049 --- [           main] o.hibernate.jpa.internal.util.LogHelper  : HHH000204: Processing PersistenceUnitInfo [name: default]
2023-10-05 15:21:45.127  INFO 32049 --- [           main] org.hibernate.Version                    : HHH000412: Hibernate ORM core version 5.6.15.Final
2023-10-05 15:21:45.358  INFO 32049 --- [           main] o.hibernate.annotations.common.Version   : HCANN000001: Hibernate Commons Annotations {5.1.2.Final}
2023-10-05 15:21:45.481  INFO 32049 --- [           main] org.hibernate.dialect.Dialect            : HHH000400: Using dialect: org.hibernate.dialect.MySQL8Dialect
2023-10-05 15:21:46.129  INFO 32049 --- [           main] o.h.e.t.j.p.i.JtaPlatformInitiator       : HHH000490: Using JtaPlatform implementation: [org.hibernate.engine.transaction.jta.platform.internal.NoJtaPlatform]
2023-10-05 15:21:46.137  INFO 32049 --- [           main] j.LocalContainerEntityManagerFactoryBean : Initialized JPA EntityManagerFactory for persistence unit 'default'
2023-10-05 15:21:46.140  INFO 32049 --- [           main] o.s.c.d.s.s.SchemaServiceConfiguration   : created: org.springframework.cloud.dataflow.schema.service.SchemaServiceConfiguration
2023-10-05 15:21:46.141  INFO 32049 --- [           main] o.s.c.d.a.t.AggregateTaskConfiguration   : created: org.springframework.cloud.dataflow.aggregate.task.AggregateTaskConfiguration
2023-10-05 15:21:46.144  INFO 32049 --- [           main] o.s.c.d.s.s.SchemaServiceConfiguration   : schemaService:starting
2023-10-05 15:21:46.145  INFO 32049 --- [           main] o.s.c.d.s.s.SchemaServiceConfiguration   : schemaService:started
2023-10-05 15:21:46.146  INFO 32049 --- [           main] o.s.c.d.s.s.impl.DefaultSchemaService    : created: org.springframework.cloud.dataflow.schema.service.impl.DefaultSchemaService
2023-10-05 15:21:46.522  INFO 32049 --- [           main] c.d.a.t.i.DefaultTaskRepositoryContainer : created: org.springframework.cloud.dataflow.aggregate.task.impl.DefaultTaskRepositoryContainer
2023-10-05 15:21:46.525  INFO 32049 --- [           main] d.s.c.AggregateDataFlowTaskConfiguration : created: org.springframework.cloud.dataflow.server.config.AggregateDataFlowContainerConfiguration
2023-10-05 15:21:46.577  INFO 32049 --- [           main] s.c.d.a.t.i.DefaultAggregateTaskExplorer : created: org.springframework.cloud.dataflow.aggregate.task.impl.DefaultAggregateTaskExplorer
2023-10-05 15:21:46.805  INFO 32049 --- [           main] o.s.b.c.r.s.JobRepositoryFactoryBean     : No database type set, using meta data indicating: MYSQL
2023-10-05 15:21:46.831  INFO 32049 --- [           main] o.s.b.c.r.s.JobRepositoryFactoryBean     : No database type set, using meta data indicating: MYSQL
2023-10-05 15:21:46.840  INFO 32049 --- [           main] o.s.c.d.s.b.SimpleJobServiceFactoryBean  : No database type set, using meta data indicating: MYSQL
2023-10-05 15:21:46.891  INFO 32049 --- [           main] o.s.c.d.s.b.SimpleJobServiceFactoryBean  : No database type set, using meta data indicating: MYSQL
2023-10-05 15:21:47.032  WARN 32049 --- [           main] JpaBaseConfiguration$JpaWebConfiguration : spring.jpa.open-in-view is enabled by default. Therefore, database queries may be performed during view rendering. Explicitly configure spring.jpa.open-in-view to disable this warning
2023-10-05 15:21:47.956  INFO 32049 --- [           main] .s.c.DataFlowControllerAutoConfiguration : Skipper URI [http://localhost:7577/api]
2023-10-05 15:21:48.041  INFO 32049 --- [           main] o.a.coyote.http11.Http11NioProtocol      : Starting ProtocolHandler ["http-nio-9393"]
2023-10-05 15:21:48.057  INFO 32049 --- [           main] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat started on port(s): 9393 (http) with context path ''
2023-10-05 15:21:48.075  INFO 32049 --- [           main] o.s.c.d.s.s.DataFlowServerApplication    : Started DataFlowServerApplication in 8.324 seconds (JVM running for 8.908)
2023-10-05 15:21:48.210  INFO 32049 --- [           main] .s.c.d.s.s.LauncherInitializationService : Added 'Local' platform account 'default' into Task Launcher repository.
2023-10-05 15:23:55.705  INFO 32049 --- [nio-9393-exec-2] o.a.c.c.C.[Tomcat].[localhost].[/]       : Initializing Spring DispatcherServlet 'dispatcherServlet'

중간에 flyway를 통해 스키마 마이그레이션 한다.

023-10-05 15:21:43.912  INFO 32049 --- [           main] o.f.core.internal.command.DbValidate     : Successfully validated 9 migrations (execution time 00:00.011s)
2023-10-05 15:21:43.932  INFO 32049 --- [           main] o.f.c.i.s.JdbcTableSchemaHistory         : Creating Schema History table `dataflow`.`flyway_schema_history_dataflow` ...
2023-10-05 15:21:43.983  INFO 32049 --- [           main] o.f.core.internal.command.DbMigrate      : Current version of schema `dataflow`: << Empty Schema >>
2023-10-05 15:21:43.988  INFO 32049 --- [           main] o.f.core.internal.command.DbMigrate      : Migrating schema `dataflow` to version "1 - Initial Setup"
2023-10-05 15:21:44.346  INFO 32049 --- [           main] o.f.core.internal.command.DbMigrate      : Migrating schema `dataflow` to version "2 - Add Descriptions And OriginalDefinition"
2023-10-05 15:21:44.444  INFO 32049 --- [           main] o.f.core.internal.command.DbMigrate      : Migrating schema `dataflow` to version "3 - Add Platform To AuditRecords"
2023-10-05 15:21:44.485  INFO 32049 --- [           main] o.f.core.internal.command.DbMigrate      : Migrating schema `dataflow` to version "4 - Add Step Name Indexes"
2023-10-05 15:21:44.525  INFO 32049 --- [           main] o.f.core.internal.command.DbMigrate      : Migrating schema `dataflow` to version "5 - Add Task Execution Params Indexes"
2023-10-05 15:21:44.572  INFO 32049 --- [           main] o.f.core.internal.command.DbMigrate      : Migrating schema `dataflow` to version "6 - Boot3 Boot Version"
2023-10-05 15:21:44.612  INFO 32049 --- [           main] o.f.core.internal.command.DbMigrate      : Migrating schema `dataflow` to version "7 - Boot3 Add Task3 Batch5 Schema"
2023-10-05 15:21:44.889  INFO 32049 --- [           main] o.f.core.internal.command.DbMigrate      : Migrating schema `dataflow` to version "8 - RenameLowerCaseTables"
2023-10-05 15:21:44.948  INFO 32049 --- [           main] o.f.core.internal.command.DbMigrate      : Migrating schema `dataflow` to version "9 - AddAggregateViews"

db client로 확인해보면 해당 스키마들이 생성되어 있다.



spring batch 5

DefaultBatchConfiguration 상속받아 수정한다.

getTablePrefix 메소드를 오버라이드하면 된다.

@Configuration
public class CustomBatchConfigurer extends DefaultBatchConfiguration {

private final DataSource dataSource;
private final PlatformTransactionManager transactionManager;

private static final String TABLE_PREFIX = "BOOT3_BATCH_";

public CustomBatchConfigurer(@Qualifier("dataflowLazyDataSource") DataSource dataSource,
@Qualifier("dataflowTransactionManager") PlatformTransactionManager dataflowTransactionManager) {
this.dataSource = dataSource;
this.transactionManager = dataflowTransactionManager;
}

@Override
protected @NotNull DataSource getDataSource() {
return this.dataSource;
}

@Override
protected @NotNull PlatformTransactionManager getTransactionManager() {
return this.transactionManager;
}

@Override
protected @NotNull String getTablePrefix() {
return TABLE_PREFIX;
}
}

spring-cloud-task

2번 적용해야 한다.

DefaultTaskConfigurer를 상속받은 생성자 인자로 DataSource dataSource, String tablePrefix, ApplicationContext context 를 넘겨 주면 된다.

public class CustomDefaultTaskConfigurer extends DefaultTaskConfigurer {

public CustomDefaultTaskConfigurer(DataSource dataSource, String tablePrefix,
ApplicationContext applicationContext) {
super(dataSource, tablePrefix, applicationContext);
}
}

DefaultTaskConfigurer를 상속받은 클래스에서 직접 bean을 선언하지 말고 configuration 클래스를 생성하여 bean으로 선언하자.

@Configuration
public class CustomTaskConfigurer {

private static final String TABLE_PREFIX = "BOOT3_TASK_";

@Bean
public CustomDefaultTaskConfigurer getCustomDefaultTaskConfigurer(
@Qualifier("dataflowLazyDataSource") DataSource dataSource,
ApplicationContext applicationContext) {
return new CustomDefaultTaskConfigurer(dataSource, TABLE_PREFIX, applicationContext);
}
}

이거 말고도 application.yml도 tabla_prefix를 추가해야 한다.

좀 찾아봐야 알겠지만 이렇게 이중으로 설정하는것은 버그라고 생각된다. 아마 이슈제기된 것이 있을듯..

spring:
cloud:
task:
tablePrefix: BOOT3_TASK_


