---
kind: "post"
publishedAt: "2026-10-31T12:13:44.300466+00:00"
updatedAt: "2026-10-31T12:13:44.300466+00:00"
reviewedAt: "2026-10-31"
reviewStatus: "revised"
reviewScope: "Self-reviewed Korean article; Kafka 4.1.2 single-broker Docker publication, two independent consumer groups and explicit partition replay verified. No crash injection, external DB/payment, rebalance, performance or exactly-once integration test."
reviewSources: ["https://kafka.apache.org/intro/", "https://kafka.apache.org/41/getting-started/docker/", "https://kafka.apache.org/41/javadoc/org/apache/kafka/clients/consumer/KafkaConsumer.html", "https://kafka.apache.org/41/configuration/producer-configs/", "https://kafka.apache.org/41/configuration/consumer-configs/", "https://kafka.apache.org/41/design/design/", "https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html"]
language: "ko"
translationKey: "2026-10-31-kafka-event-streaming"
routeSlug: "2026-10-31-kafka-event-streaming"
title: "Kafka 이벤트 스트리밍: 파티션·컨슈머 그룹·오프셋과 재처리"
description: "Kafka가 이벤트를 저장하고 여러 소비자가 독립적으로 읽는 구조를 설명합니다. 로컬 실행 예제로 발행·그룹별 소비·재생을 확인하고 순서, 오프셋 커밋, 중복 처리의 경계를 정합니다."
categories: ["architecture"]
tags: ["kafka", "event-streaming", "consumer-group", "offset", "idempotency", "distributed-systems"]
---

**Kafka 이벤트 스트리밍은 발생한 사실을 로그로 보관하고, 여러 소비자가 각자의 위치에서 읽어 처리하는 방식입니다.** 주문 이벤트를 배송 준비와 통계 집계가 독립적으로 읽을 수 있고, 보관된 기록을 새 로직으로 다시 처리할 수도 있습니다. 다만 Kafka에 저장됐다는 사실과 외부 DB·결제가 정확히 한 번 변경됐다는 사실은 별개입니다.

이 글은 HTTP API와 DB를 사용해 본 개발자를 대상으로 합니다. 토픽·파티션·컨슈머 그룹을 연결해 이해하고, 로컬 Kafka에서 이벤트 발행·독립 소비·재생을 실행합니다. Kafka Streams의 집계·윈도·조인 구현보다 **소비 위치와 장애 시 재처리의 의미**에 집중합니다.

## 이벤트 스트리밍은 작업 큐와 무엇이 다른가요?

이벤트는 ‘주문이 생성됐다’처럼 이미 발생한 사실입니다. ‘배송을 시작하라’처럼 특정 실행을 요구하는 명령과 목적을 구분하면 여러 소비자가 같은 기록을 각자의 업무에 사용할 수 있습니다. Kafka도 같은 그룹 안에서는 작업을 나누는 큐처럼 사용할 수 있지만, 소비했다고 기록을 즉시 삭제하지는 않습니다. 보관 정책이 허용하는 범위에서 다른 그룹이나 재생 작업이 다시 읽습니다. [Apache Kafka 소개](https://kafka.apache.org/intro/)

| 개념 | 역할 | 설계할 때 정할 것 |
| --- | --- | --- |
| 프로듀서 | 이벤트를 Kafka에 기록 | 키, 이벤트 ID, 스키마, 발행 실패 처리 |
| 토픽 | 관련 이벤트를 담는 논리적 스트림 | 이벤트의 의미, 보관·압축 정책, 접근 권한 |
| 파티션 | 순서가 있는 로그의 분할 단위 | 순서가 필요한 범위, 키 분포, 병렬 처리량 |
| 컨슈머 그룹 | 같은 업무를 나눠 처리하는 소비자 집합 | 그룹 ID, 처리·커밋 시점, 재처리 정책 |
| 오프셋 | 파티션 안의 기록 위치 | 어디까지 읽었고 어디서 재개할지 |

예를 들어 `orders.v1` 토픽을 `shipping-v1`과 `analytics-v1` 그룹이 읽으면 두 업무는 각각 같은 이벤트를 받을 수 있습니다. 반대로 배송 소비자와 통계 소비자를 같은 그룹에 넣으면 기록을 나눠 받으므로, 각 업무가 전체 이벤트를 받는 구성이 되지 않습니다.

일반적인 그룹 구독에서는 한 파티션을 그룹 안의 한 소비자에게 할당합니다. 파티션 3개를 읽는 그룹에 소비자 5개를 두어도 모두에게 파티션이 생기지는 않습니다. 다른 그룹에는 독립적으로 할당합니다. 이 글은 `KafkaConsumer`의 일반적인 그룹 구독을 기준으로 하며, 레코드 단위 공유 소비 모델과 구분합니다. [KafkaConsumer의 그룹 구독](https://kafka.apache.org/41/javadoc/org/apache/kafka/clients/consumer/KafkaConsumer.html)

## 순서가 필요하면 키부터 정합니다

Kafka의 기록 순서는 **파티션 안에서** 정의됩니다. 같은 주문의 상태 변경 순서가 중요하다면 주문 ID를 키로 사용해 같은 파티션으로 보내는 구성이 출발점입니다. 키는 라우팅 기준이고, 이벤트 ID는 중복 판별 기준이므로 역할이 다릅니다. 같은 주문에서 생성된 여러 이벤트가 같은 이벤트 ID를 가지면 정상적인 후속 이벤트까지 중복으로 제거할 수 있습니다.

같은 키의 라우팅도 키 직렬화·파티셔너·파티션 수가 일관되다는 조건을 가집니다. 파티션 수를 늘리면 이후 기록의 배치가 달라질 수 있으므로 이전 기록과의 순서를 검토해야 합니다. 한 파티션에서 읽은 뒤 작업을 무제한 병렬 실행하면 완료 순서 역시 달라집니다. Kafka에 기록된 순서와 업무상 발생 시각의 순서도 항상 같지는 않습니다. 여러 발행자가 늦게 보낸 이벤트를 처리하려면 업무 버전·발생 시각과 역순 처리 규칙이 필요합니다.

한 고객의 이벤트가 대부분을 차지하는 hot key는 같은 파티션에 부하를 집중시킬 수 있습니다. 순서를 유지해야 하는 단위를 무작정 더 작은 키로 쪼개기보다, 필요한 순서 범위와 처리 비용을 함께 검토합니다.

## 로컬 실행: 두 그룹이 같은 기록을 읽고 다시 재생하기

다음 예제는 Apache의 `apache/kafka:4.1.2` 이미지에 포함된 도구를 사용합니다. Bash와 실행 중인 Docker가 필요하며 첫 실행에는 이미지 다운로드가 필요합니다. 브로커와 CLI는 같은 컨테이너에서 실행하므로 호스트 포트를 열지 않습니다. 컨테이너를 종료할 때 실습 데이터도 제거하며, 브로커 1개·파티션 1개·복제 계수 1인 기능 확인용 구성입니다. [공식 Docker 실행 안내](https://kafka.apache.org/41/getting-started/docker/)

![임시 브로커를 준비하고 토픽에 두 이벤트를 기록한 뒤 projection 그룹과 audit 그룹이 각각 읽고, 파티션 0의 오프셋 0부터 다시 읽은 다음 실습 컨테이너를 정리하는 흐름](/assets/img/architecture/kafka-event-streaming-ko.svg)

그림은 아래 스크립트의 정상 실행 순서입니다. 준비 실패나 명령 실패 때는 중단하며, 생성에 성공한 실습 컨테이너는 종료 시 정리합니다. 그룹 소비 두 번과 직접 재생 한 번은 순차 실행합니다. 외부 DB 처리나 수동 오프셋 커밋은 구현하지 않습니다.

`kafka-demo.sh`로 저장하고 `bash kafka-demo.sh`로 실행합니다.

```sh
#!/usr/bin/env bash
set -euo pipefail

kafka_image=apache/kafka:4.1.2
kafka_name="kafka-stream-demo-$$-$RANDOM"
docker run -d --name "$kafka_name" "$kafka_image" >/dev/null
trap 'docker rm -f "$kafka_name" >/dev/null 2>&1 || true' EXIT

ready=false
for ((attempt=0; attempt<30; attempt++)); do
  if docker exec "$kafka_name" /opt/kafka/bin/kafka-topics.sh \
      --bootstrap-server localhost:9092 --list >/dev/null 2>&1; then
    ready=true
    break
  fi
  sleep 1
done
if [ "$ready" != true ]; then
  docker logs "$kafka_name" >&2
  exit 1
fi

docker exec "$kafka_name" /opt/kafka/bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 --create --topic orders.v1 \
  --partitions 1 --replication-factor 1 >/dev/null

docker exec -i "$kafka_name" /opt/kafka/bin/kafka-console-producer.sh \
  --bootstrap-server localhost:9092 --topic orders.v1 \
  --producer-property acks=all --producer-property enable.idempotence=true \
  --property parse.key=true --property key.separator=: <<'EVENTS'
order-101:{"eventId":"evt-1","type":"OrderCreated","schemaVersion":1}
order-101:{"eventId":"evt-2","type":"PaymentConfirmed","schemaVersion":1}
EVENTS

for group in projection-v1 audit-v1; do
  printf 'group=%s\n' "$group"
  docker exec "$kafka_name" /opt/kafka/bin/kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 --topic orders.v1 --group "$group" \
    --from-beginning --max-messages 2 --timeout-ms 15000 \
    --property print.key=true --property 'key.separator=|'
done

printf 'replay=partition-0-offset-0\n'
docker exec "$kafka_name" /opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 --topic orders.v1 \
  --partition 0 --offset 0 --max-messages 2 --timeout-ms 15000 \
  --property print.key=true --property 'key.separator=|'
```

Docker Engine `24.0.5`와 `apache/kafka:4.1.2`에서 확인한 표준 출력입니다. 각 소비 명령의 `Processed a total of 2 messages` 안내는 표준 오류로 별도 출력됩니다.

```text
group=projection-v1
order-101|{"eventId":"evt-1","type":"OrderCreated","schemaVersion":1}
order-101|{"eventId":"evt-2","type":"PaymentConfirmed","schemaVersion":1}
group=audit-v1
order-101|{"eventId":"evt-1","type":"OrderCreated","schemaVersion":1}
order-101|{"eventId":"evt-2","type":"PaymentConfirmed","schemaVersion":1}
replay=partition-0-offset-0
order-101|{"eventId":"evt-1","type":"OrderCreated","schemaVersion":1}
order-101|{"eventId":"evt-2","type":"PaymentConfirmed","schemaVersion":1}
```

두 그룹이 각자 두 이벤트를 읽었고, 마지막 직접 재생에서도 같은 두 기록을 읽었습니다. 한 그룹의 소비가 다른 그룹의 읽기나 로그 재생을 막지 않는 것을 확인한 것입니다. 파티션이 하나이므로 여러 파티션 사이의 순서나 그룹 내부의 병렬 할당을 검증한 것은 아닙니다.

콘솔 도구의 소비 결과를 확인했으며, 자동 커밋 설정을 기본값으로 사용합니다. 이 실습은 업무 처리 후 수동 커밋하는 애플리케이션의 구현이나 커밋 사이 장애 시험이 아닙니다. 입력 JSON의 스키마 검증, 외부 DB·결제 반영, 리밸런스 중 처리도 구현하지 않았습니다.

## 오프셋 커밋이 업무 완료를 보장하나요?

보장하지 않습니다. 컨슈머의 현재 위치는 `poll()`로 기록을 받으면서 앞으로 이동할 수 있지만, 재시작 시 사용할 **커밋된 위치**는 별도입니다. 순차 처리에서 오프셋 10을 완료했다면 보통 다음에 읽을 위치인 11을 커밋합니다. 여러 파티션을 읽는다면 파티션별로 완료 범위를 관리해야 합니다. 오프셋은 삭제·트랜잭션 등의 이유로 연속된 정수 기록만을 뜻하지도 않습니다. [KafkaConsumer의 위치·커밋 설명](https://kafka.apache.org/41/javadoc/org/apache/kafka/clients/consumer/KafkaConsumer.html)

| 실행 순서와 장애 위치 | 재시작 시 생길 수 있는 결과 | 필요한 처리 |
| --- | --- | --- |
| 오프셋 커밋 → DB 변경 전 종료 | 해당 변경을 건너뛰어 업무 반영 누락 | 요구하는 전달 의미에 맞게 커밋 순서 변경 |
| DB 변경 완료 → 오프셋 커밋 전 종료 | 같은 이벤트의 재전달·재처리 | 멱등 처리 또는 중복 제거 |
| 일부 기록 실패 후 뒤의 위치 커밋 | 실패 기록을 건너뛸 수 있음 | 성공한 연속 처리 범위만 커밋 |
| 다른 소비자로 파티션 재할당 | 기존 작업과 새 소유자의 작업이 겹칠 수 있음 | 이전 소유 작업의 중단·외부 효과 중복 방지 |

외부 DB에 반영하는 소비자는 예를 들어 `(처리기 ID, eventId)`의 유일성 검사와 실제 업무 변경을 **같은 DB 트랜잭션**에서 수행할 수 있습니다. 먼저 처리 표시만 저장하고 실제 변경에 실패하면 다음 전달을 중복으로 오인할 수 있습니다. 반대로 변경 후 별도로 처리 표시를 저장하면 그 사이 장애로 중복 변경될 수 있습니다. 다른 외부 API 호출까지 이 DB 트랜잭션에 자동으로 포함되지는 않으므로, 해당 API의 멱등 키와 결과 확인도 필요합니다.

프로듀서의 `enable.idempotence`는 프로듀서 재시도로 로그에 중복 기록이 생기는 문제를 다루며, 애플리케이션이 같은 업무 이벤트를 새로 두 번 발행하는 모든 상황을 제거하지는 않습니다. `acks=all`도 모든 설정과 무관한 무손실 보장이 아닙니다. 복제 계수와 `min.insync.replicas`, 실제 ISR 상태를 함께 봐야 하며 위의 단일 브로커 실습은 브로커 손실 내성을 확인하지 않습니다. [프로듀서 설정](https://kafka.apache.org/41/configuration/producer-configs/)

Kafka의 트랜잭션으로 입력 오프셋과 출력 토픽 기록을 묶고 `read_committed` 소비를 사용하는 처리와, 외부 DB·결제의 효과를 정확히 한 번 적용하는 처리는 구분해야 합니다. 외부 시스템의 협력 없이 ‘Kafka를 쓰면 모두 exactly-once’라고 볼 수 없습니다. [Kafka의 전달 의미와 트랜잭션](https://kafka.apache.org/41/design/design/)

## 재시도와 재생은 정상 운영 경로로 설계합니다

일시적 외부 장애에는 횟수·총 시간·동시성을 제한한 재시도를 적용합니다. 계속 실패하는 이벤트 하나가 파티션 전체를 막는다면 보류·재처리 경로를 검토하되, 원본 처리에서 뒤의 이벤트를 진행시킬 때 업무 순서가 깨지는지 확인해야 합니다. 실패 이벤트를 별도 토픽인 DLQ로 보냈다고 업무가 완료되는 것은 아닙니다. 원본 이벤트 ID·실패 원인·스키마 버전과 재처리 담당·해결 기한을 남기고, DLQ 기록과 입력 오프셋 이동 사이의 실패도 처리해야 합니다.

DB 커밋과 Kafka 발행을 별도로 실행하는 프로듀서도 양쪽 사이에서 실패할 수 있습니다. DB 변경과 outbox 기록을 같은 트랜잭션에 저장한 뒤 전달하는 구성은 한 가지 대응이며, 전달 중복은 소비자가 여전히 다뤄야 합니다. Kafka를 추가하는 것만으로 원본 DB와 로그가 하나의 트랜잭션이 되지는 않습니다. [Transactional outbox 패턴](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)

`--from-beginning`은 유효한 커밋 위치가 있는 그룹을 무조건 처음으로 되돌리는 옵션이 아닙니다. 위 실습에서는 새 그룹을 사용하며, 마지막 단계는 그룹 재설정 대신 파티션과 시작 오프셋을 직접 지정합니다. 기존 그룹의 위치를 바꾸는 운영 재생은 소비자를 멈추고 대상·범위·외부 효과를 확인한 뒤 별도 절차로 수행해야 합니다. 새 그룹으로 재생해도 결제·알림이 다시 발생할 수 있으므로 출력 격리나 멱등 정책이 필요합니다. [소비자 오프셋 초기화 설정](https://kafka.apache.org/41/configuration/consumer-configs/)

보관 기간보다 처리가 늦어지면 필요한 기록이 이미 삭제될 수 있습니다. 로그 압축을 쓰면 같은 키의 모든 과거 상태를 그대로 보관하는 것도 아닙니다. 재생 가능 범위는 보관·압축 정책, 필요한 스키마 해석 능력과 함께 정합니다.

첫 적용에서는 하나의 업무 흐름을 골라 정상 처리 외에 DB 반영 후 커밋 전 종료, 재시작, 리밸런스, 잘못된 스키마, 외부 의존성 지연, 재생 중 중복 효과를 확인합니다. `lag`는 정한 끝 위치와 소비·커밋 위치 사이의 차이이므로, 어떤 위치로 계산한 지표인지 명시합니다. lag와 함께 이벤트 발생부터 업무 반영까지의 지연, 처리 실패·재시도·DLQ, 리밸런스, 브로커 저장 공간과 복제 상태를 관측해야 ‘읽고 있다’와 ‘업무를 완료했다’를 구분할 수 있습니다.
