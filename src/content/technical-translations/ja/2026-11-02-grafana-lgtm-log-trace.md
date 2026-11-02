---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2026-11-02-grafana-lgtm-log-trace",
  "routeSlug": "2026-11-02-grafana-lgtm-log-trace",
  "kind": "post",
  "title": "Grafana LGTM でログとトレースを関連付ける：trace_id で Loki から Tempo へ",
  "description": "OpenTelemetry でログとスパンを収集し、Grafana で Loki と Tempo を接続します。実行可能な Docker/Python 実習と、ID の欠落や検索結果が空になる場合の対処を紹介します。",
  "categories": [
    "architecture"
  ],
  "tags": [
    "grafana",
    "loki",
    "tempo",
    "opentelemetry",
    "observability",
    "tracing"
  ],
  "sourcePath": "src/content/posts/en/2026-11-02-grafana-lgtm-log-trace.md",
  "sourceSha256": "ea19472a99523fa3e56c758e753b8333671691c4efd6f1dec67f9e59c3eaf558",
  "draftSha256": "9fc5fc790999ea7130822973243315916654bf22361071d043b5dddd8aa44b05",
  "manifestPath": ".pipeline/technical-translations/batch-135/manifest.json",
  "manifestSha256": "7b0ee87cd56b365db57f3da54bd97961e76f22898e553e01c3f514dcad33abc9",
  "publishedAt": "2026-11-02T11:48:15.897Z",
  "updatedAt": "2026-11-02T11:48:15.897Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 135,
    "approvedAt": "2026-11-02T11:48:15.897Z",
    "basis": "사용자가 한국어·영어 LGTM 글 게시 후 다국어 지원도 해줘라고 요청하여 기존 지원 언어 6개의 전체 번역·현지화 그림 게시를 승인함. AI 번역 검토와 사용자 게시 승인은 별도임."
  }
}
---

**Grafana LGTM でログとトレースを関連付けるには、同じ `trace_id` を持つログとスパンを出力し、Grafana に Loki と Tempo の両方のデータソースを設定します。** これにより、エラーログの背後にある実行経路を開き、スパンから関連ログに戻れるようになります。

LGTM は Loki（ログ）、Grafana（クエリと可視化）、Tempo（トレース）、Mimir（メトリクス）の略です。このチュートリアルではログとトレースの関連付けに焦点を当てます。運用フロー全体については、[AI エージェントの運用](/en/posts/2026-10-31-ai-agent-operations/)を参照してください。

## どの識別子が一致する必要があるか？

トレースは 一回の実行を表し、スパンはその中の個々の操作を表します。例の親スパン `checkout` と子スパン `inventory.lookup` は、トレース ID が同じで、スパン ID は異なります。アクティブなスパン内でログを記録すると、ログレコードにそのスパンのコンテキストを持たせられます。別々のサービスを関連付けるには、HTTP の `traceparent` ヘッダーなどによるコンテキスト伝播も必要です。[OpenTelemetry のコンテキスト伝播](https://opentelemetry.io/docs/concepts/context-propagation/)

![Python の例がアクティブなスパン内でログを記録し、OpenTelemetry Collector がログを Loki に、トレースを Tempo に振り分け、Grafana が同じ trace_id で両方にクエリを実行する](/assets/diagrams/technical/ja-2026-11-02-grafana-lgtm-log-trace.svg)

保存先の間の関連付けは、Grafana のクエリ機能です。Loki がログを Tempo に転送するわけではなく、Grafana が欠けているトレースを作成するわけでもありません。この例では、一つのプロセスでスパンを手動で作成します。HTTP サーバー、サービス間の呼び出し、在庫データベースは実装しません。

## ローカルの収集環境を構築する

Docker と Python の仮想環境を利用できる環境で、空のディレクトリに次の 四つのファイルを作成してください。検証した組み合わせは **Python 3.13.0、OpenTelemetry Python 1.45.2、`grafana/otel-lgtm` 0.39.0** です。イメージには Grafana 13.3.0、Loki 3.7.9、Tempo 3.1.1、Collector 0.164.0 が含まれます。

[公式の Docker LGTM イメージ](https://grafana.com/docs/opentelemetry/docker-lgtm/)は、開発、デモ、テスト向けです。メトリクスのバックエンドには Prometheus を使用しており、このチュートリアルでは本番用の Mimir クラスターを構築しません。ログとトレースには、同梱された Collector、Loki、Tempo、Grafana を使用します。

### `compose.yaml`

```yaml
services:
  lgtm:
    image: grafana/otel-lgtm:0.39.0@sha256:4c8056c9c05fcb3c8fd93800e85334bfd79b4d0271b47a54a121a64af41fe1fe
    ports:
      - '127.0.0.1:13000:3000'
      - '127.0.0.1:14318:4318'
    environment:
      GF_AUTH_ANONYMOUS_ENABLED: 'true'
      GF_AUTH_ANONYMOUS_ORG_ROLE: Editor
    volumes:
      - ./datasources.yaml:/otel-lgtm/grafana/conf/provisioning/datasources/grafana-datasources.yaml:ro
```

これはローカルでの実習環境です。匿名ユーザーには Explore 用の Editor 権限を付与し、Grafana と OTLP はホストの `127.0.0.1` にバインドします。本番環境では認証、TLS、アクセス制限が必要です。ホストの Python はポート `14318`、コンテナーの Collector は `4318` を使用します。データソースの URL は、Grafana のコンテナー内のループバックアドレスを使用しています。Loki と Tempo を別々のコンテナーで動かす場合は、代わりにサービスの DNS 名を使用してください。

### `datasources.yaml`

```yaml
apiVersion: 1
datasources:
  - name: Tempo
    type: tempo
    uid: tempo
    url: http://127.0.0.1:3200
    jsonData:
      tracesToLogsV2:
        datasourceUid: loki
        spanStartTimeShift: '-2s'
        spanEndTimeShift: '2s'
        tags:
          - key: service.name
            value: service_name
        customQuery: true
        query: '{$${__tags}} | trace_id = "$${__trace.traceId}"'
  - name: Loki
    type: loki
    uid: loki
    url: http://127.0.0.1:3100
    jsonData:
      derivedFields:
        - name: trace_id
          matcherType: label
          matcherRegex: '^trace_id$'
          datasourceUid: tempo
          url: '$${__value.raw}'
          urlDisplayLabel: View trace
```

`tracesToLogsV2` はスパンからログへのクエリを、`derivedFields` はログから Tempo へのリンクを構築します。`service.name` を Loki の `service_name` に対応付け、その後でトレース ID による絞り込みを行います。`customQuery` を有効にした場合、この絞り込み条件をクエリに明示的に含めます。両方向の設定については、[Grafana の関連付け設定](https://grafana.com/docs/grafana/latest/datasources/tempo/configure-tempo-data-source/configure-trace-to-logs/)を参照してください。

`$${...}` は **Grafana のプロビジョニングファイル**内の変数を保持します。別途マウントするこのファイルは、Compose の文字列補間の対象ではありません。Grafana の UI で直接値を入力する場合は `${...}` を使用してください。この設定は、[公式イメージのデータソース設定](https://github.com/grafana/docker-otel-lgtm/blob/v0.39.0/docker/grafana-datasources.yaml)をログとトレースの関連付けに絞ったものです。

OTLP で取り込む場合、`trace_id` はログ本文の JSON フィールドではなく、Loki の構造化メタデータとして検索されるため、この例では `| json` は不要です。Grafana の `matcherType: label` はフィールドの検索方法を選択するものであり、トレース ID を Loki のインデックスラベルに変えるものではありません。[Loki の OTLP 保存ルール](https://grafana.com/docs/loki/latest/send-data/otel/)

### `requirements.txt`

```text
opentelemetry-sdk==1.45.2
opentelemetry-exporter-otlp-proto-http==1.45.2
```

### `demo.py`

```python
import logging

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import ALWAYS_ON
from opentelemetry.trace import Status, StatusCode

resource = Resource.create({"service.name": "checkout-demo"})
traces = TracerProvider(resource=resource, sampler=ALWAYS_ON)
traces.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(
    endpoint="http://127.0.0.1:14318/v1/traces")))
trace.set_tracer_provider(traces)
logs = LoggerProvider(resource=resource)
logs.add_log_record_processor(BatchLogRecordProcessor(OTLPLogExporter(
    endpoint="http://127.0.0.1:14318/v1/logs")))
handler = LoggingHandler(logger_provider=logs)
logger = logging.getLogger("checkout-demo")
logger.setLevel(logging.INFO)
logger.propagate = False
logger.addHandler(handler)
tracer = trace.get_tracer("checkout-demo")

try:
    with tracer.start_as_current_span("checkout") as checkout:
        trace_id = f"{checkout.get_span_context().trace_id:032x}"
        logger.info("checkout_started")
        with tracer.start_as_current_span("inventory.lookup") as inventory:
            logger.error("inventory_unavailable")
            inventory.set_status(Status(StatusCode.ERROR, "demo failure"))
        checkout.set_status(Status(StatusCode.ERROR, "inventory unavailable"))
    assert logs.force_flush(timeout_millis=10000), "log flush timed out"
    assert traces.force_flush(timeout_millis=10000), "trace flush timed out"
    print(f"trace_id={trace_id}")
finally:
    logger.removeHandler(handler)
    logs.shutdown()
    traces.shutdown()
```

`inventory_unavailable` は意図的に出力するエラーメッセージです。実際の在庫サービスの障害を再現したり、サービスの性能を測定したりするものではありません。この例では、両方のスパンを明示的にエラーとしてマークします。`LoggingHandler` と OTLP エクスポーターが、アクティブなスパンの識別子をログに引き継ぎます。[Python の計装](https://opentelemetry.io/docs/languages/python/instrumentation/)

この例では、検証済みの SDK バージョンに固定しています。[Python のサポート状況](https://opentelemetry.io/docs/languages/python/)ではログが Development に分類されているため、アップグレード時にはログ API とエクスポーターの互換性を再確認してください。`ALWAYS_ON` は学習のために例のすべてのスパンを記録します。本番で推奨するサンプリング方針ではありません。

## 出力されたトレース ID で両方の保存先を検索する

四つのファイルを置いたディレクトリで、次のコマンドを実行してください。初回は Docker Hub と PyPI からダウンロードします。コマンドは Unix 系のシェルを使用します。

```sh
docker compose -p blog-lgtm-lab up -d --wait --wait-timeout 180
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python demo.py
```

コンテナーが正常な状態になってから Python を実行してください。イメージのダウンロードや Grafana の初期化には時間がかかる場合があります。準備が整う前にエクスポートすると失敗することがあります。`force_flush()` はエクスポート処理を待ちますが、データが保存先に存在することの最終的な証明にはなりません。

次は、実習で出力されたトレース ID です。実行ごとに新しい ID が生成されるため、以下のクエリでは**自分の出力**に置き換えてください。

```text
trace_id=b95b8ec2e8c6fa5a608f197d1cfe3691
```

1. `http://127.0.0.1:13000` を開いて **Explore → Loki** を選び、時間範囲を過去 一時間に設定します。
2. 次の LogQL 式で 二件のログを検索します。

```text
{service_name="checkout-demo"} | trace_id = "b95b8ec2e8c6fa5a608f197d1cfe3691"
```

3. `inventory_unavailable` を展開し、`trace_id` の **View trace** を開きます。Tempo で `inventory.lookup` を探してください。これは `checkout` の下にあります。
4. Tempo パネルの **Related logs** を使って Loki に戻ります。バージョンによっては、スパンの **Logs for this span** リンクとして表示されます。このクエリは `span_id` では絞り込まないため、時間範囲とサービスが一致すると、トレース内の両方のログが表示される場合があります。

ローカルのクエリでは **二件のログと 二つのスパン**が返り、親子関係とログのスパン ID が一致しました。Loki の series API にはインデックスラベルとして `trace_id` も `span_id` も含まれておらず、存在しないトレース ID ではログが返りませんでした。ブラウザーでも、エラーログから Tempo へ移動し、関連する Loki のログに戻ることを確認しました。これらの結果が対象とするのは単一プロセスの収集と関連付けの例であり、本番負荷や復旧ではありません。

## リンク先にデータがない場合

| 症状 | 最初の確認項目 | 次の対処 |
| --- | --- | --- |
| ログにトレース ID がない | アクティブなスパン内でログを記録したか？ | スレッド、コルーチン、非同期処理の境界を越えるコンテキスト伝播を確認する |
| Loki のクエリは成功するが Tempo のリンクが表示されない | `derivedFields` のフィールド名と Tempo UID | マッチャーを実際の `trace_id` フィールドに合わせる |
| スパンにログへのリンクがない | `service.name` とデータソースのタグの対応付け | Loki の `service_name` の値に合わせる |
| リンク先のログクエリの結果が空になる | 時間範囲、サービス、トレース ID | LogQL を直接実行し、取り込みの遅延と時刻のずれを確認する |
| ログはあるがトレースを検索できない | トレースのエクスポーター、サンプリング、Tempo の保持期間 | Collector のエクスポートエラーと保持ポリシーを調べる |

本番のインデックスラベルには `trace_id`、`user_id`、注文番号を含めないでください。異なる値の組み合わせによって Loki のストリーム数が増大します。まずサービスや環境など、値の種類が限られる項目で範囲を絞り、その後で本文や構造化メタデータの ID を使って絞り込んでください。[Loki のカーディナリティ](https://grafana.com/docs/loki/latest/get-started/labels/cardinality/)

ログやトレースが見つからなくても、正常だと判断することはできません。サンプリングでトレースが除外された可能性も、保持期間が異なる可能性も、Collector のエクスポートが遅れている可能性もあります。ログ本文や baggage にトークンや個人データを含めず、本番で使う前に収集失敗のアラート、保持ポリシー、マスキングを整備してください。

実習後は、コンテナーと接続された匿名ボリュームを削除してください。この例ではデータを保持しません。

```sh
docker compose -p blog-lgtm-lab down -v
```
