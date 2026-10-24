---
title: "[spring batch] spring batch 5 migration"
language: "ko"
translationKey: "2023-10-27-springbatch5-migration"
routeSlug: "2023-10-27-springbatch5-migration"
kind: "post"
publishedAt: "2023-10-26T15:00:00.000Z"
categories:
  - "spring"
tags:
  - "spring batch 5"
  - "migration"
legacyUrl: "/spring/springbatch5-migration/"
legacySource: "_posts/spring/migration/2023-10-27-springbatch5-migration.markdown"
updatedAt: "2026-10-24T09:00:00+09:00"
reviewedAt: "2026-10-24"
reviewStatus: "revised"
reviewScope: "공식 문서 대조 및 예제 코드 검토"
archiveBodySha256: "9c0428486a2f50071a983c45ec66d388aa33f1d204f4c3d84bdd923aa5f73b75"
reviewSources:
  - "https://github.com/spring-projects/spring-batch/wiki/Spring-Batch-5.0-Migration-Guide"
---
## 개요

spring boot3가 release되면서 spring batch 5로 업그레이드 되었습니다.  
간단하게 종속성 업그레이드로 끝나는것이 아니라 DB 스키마 변경과 jobBuilder, stepBuilder 작동 방식도 변경되었습니다.  
이 부분에 대해 간단하게 정리하도록 하겠습니다.

### JDK 17
spring batch 5는 jdk 17이 최소 사양인 spring framework 6 기반으로 합니다.  

### jakarta 패키지
사용 중인 Java EE API의 javax 패키지를 Jakarta API로 변경합니다. Java SE의 javax.sql 등까지 일괄 치환하지 않습니다.

### DB 스키마 업데이트
oracle과 sql-server인 경우는 sequence 관련 업데이트가 있습니다.  
그외 모든 플랫폼은 아래와 같은 스키마 변경 사항이 있습니다.

#### BATCH_JOB_EXECUTION
JOB_CONFIGURATION_LOCATION 컬럼은 사용되지 않습니다.  
아래 쿼리로 컬럼을 삭제하도록 합니다.
```sql
ALTER TABLE BATCH_JOB_EXECUTION DROP COLUMN JOB_CONFIGURATION_LOCATION;
```

#### BATCH_JOB_EXECUTION_PARAMS

batch parameter로 사용되던 string, date, long, double형 대신 `<T>` 제레릭으로 받을수 있게 변경되었습니다.

그리하여 각 해당 컬럼들은 삭제되고 PARAMETER_NAME, PARAMETER_TYPE, PARAMETER_VALUE 컬럼이 새로 생성되었죠.

```diff
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

```sql
ALTER TABLE BATCH_JOB_EXECUTION_PARAMS DROP COLUMN DATE_VAL;
ALTER TABLE BATCH_JOB_EXECUTION_PARAMS DROP COLUMN LONG_VAL;
ALTER TABLE BATCH_JOB_EXECUTION_PARAMS DROP COLUMN DOUBLE_VAL;

ALTER TABLE BATCH_JOB_EXECUTION_PARAMS CHANGE COLUMN TYPE_CD PARAMETER_TYPE VARCHAR(100);
ALTER TABLE BATCH_JOB_EXECUTION_PARAMS CHANGE COLUMN KEY_NAME PARAMETER_NAME VARCHAR(100);
ALTER TABLE BATCH_JOB_EXECUTION_PARAMS CHANGE COLUMN STRING_VAL PARAMETER_VALUE VARCHAR(2500);
```

spring batch 5로 migration하는 경우 위 ALTER 쿼리 실행시 크리티컬한 버그가 있습니다.  

```sql
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

```sql
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

관련 이슈: [트랜잭션 매니저 노출 변경](https://github.com/spring-projects/spring-batch/issues/816)

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
#### to-be
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

## 검증 및 보강 — 2026-10-24

위 `CHANGE COLUMN`, `DATETIME(6)` 예제는 MySQL 계열 문법이며 모든 DB에 공통 적용할 수 없습니다. 대상 버전 JAR에 포함된 DB별 `org/springframework/batch/core/migration/5.0` 스크립트를 먼저 확인하세요. 기존 DATE/LONG/DOUBLE 값을 새 문자열 컬럼으로 옮기기 전에 컬럼을 삭제하면 이력이 손실됩니다. 타입 이름뿐 아니라 각 파라미터 값과 기존 실행 컨텍스트의 직렬화 방식도 검증해야 합니다. `DefaultBatchConfiguration` 상속과 `@EnableBatchProcessing`을 함께 사용하지 않으며, Spring Boot 자동 구성을 직접 대체하는 경우 스키마 초기화도 확인해야 합니다. 실제 적용 순서는 백업 → 복제 DB에서 이관 → 기존 완료/실패/재시작 Job 검증 → 운영 반영으로 잡습니다. 이 글의 SQL을 운영 DB에서 그대로 실행하는 방식은 재현 검증을 대신할 수 없습니다.

### 확인한 자료

- [공식 자료 1](https://github.com/spring-projects/spring-batch/wiki/Spring-Batch-5.0-Migration-Guide)
