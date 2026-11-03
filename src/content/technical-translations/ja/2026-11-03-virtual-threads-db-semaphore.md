---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2026-11-03-virtual-threads-db-semaphore",
  "routeSlug": "2026-11-03-virtual-threads-db-semaphore",
  "kind": "post",
  "title": "仮想スレッドと DB セマフォ：コネクションプールの手前で受け入れを制御する",
  "description": "JDBC プールに追加のセマフォが必要なのはどんな場合でしょうか。受け入れ数と実行数を制限し、トランザクションのクリーンアップ後に許可を解放して、PostgreSQL でタイムアウトとキャンセルの動作を検証します。",
  "categories": [
    "jdk"
  ],
  "tags": [
    "java",
    "virtual-threads",
    "jdbc",
    "hikaricp",
    "semaphore",
    "postgresql"
  ],
  "sourcePath": "src/content/posts/en/2026-11-03-virtual-threads-db-semaphore.md",
  "sourceSha256": "103d90ef1cccefaa0b1dd31120b1813c5ded6536bcd76a9ae5a0f75388d3584a",
  "draftSha256": "3178abef8bf5ad2685c585acae619c4b2f6b4d4b6b3159392ecd85a97b8fb7f9",
  "manifestPath": ".pipeline/technical-translations/batch-142/manifest.json",
  "manifestSha256": "c9980c2893c26f4f01a8f1991ea314755050840c12c102f2e907891193acc59a",
  "publishedAt": "2026-11-03T09:13:33.711Z",
  "updatedAt": "2026-11-03T09:13:33.711Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 142,
    "approvedAt": "2026-11-03T09:13:33.711Z",
    "basis": "User explicitly requested multilingual support for the already published article (다국어 지원도 해줘), within the continuing publication task and standing merge/deploy instruction. This records user publication authorization; it does not claim human or native-speaker proofreading."
  }
}
---

仮想スレッドを使うからといって、データベースの手前にセマフォを追加する必要があるわけではありません。コネクションプールはすでに接続数を制限しています。追加のセマフォが役立つのは、 **DB 処理を早い段階で拒否したい場合、受け入れる操作数に上限を設けたい場合、特定のワークロードに同時実行数の予算を割り当てたい場合**です。Oracle の仮想スレッドガイドも、データベースのコネクションプール自体がセマフォとして機能すると説明しています。[Oracle 仮想スレッドガイド](https://docs.oracle.com/en/java/javase/25/core/virtual-threads.html)

この記事では、[JDK 21–25 の仮想スレッド比較](/en/posts/2026-10-31-virtual-threads-jdk21-jdk25/)に続いて、データベース接続を扱います。[10k RPS アーキテクチャ](/en/posts/2026-10-31-jdk-10k-rps-architecture/)で説明した広い意味での受け入れ制御の中で、DB 処理の境界を具体化します。対象は Java 21 以降で、一つの同期 JDBC トランザクションが一つの接続を使う構成です。セマフォはアプリケーションインスタンス内で共有し、リクエストごとに新しく作らないでください。

## コネクションプールがある場合、何を制限すべきか

仮想スレッドを使うと、比較的小さなスレッドのオーバーヘッドで多数の待機タスクを保持できます。ただし、それだけでデータベースのクエリ処理能力が増えたり、ロック競合が減ったりするわけではありません。満杯のプールから接続を取得しようと待っているリクエストは、引き続きメモリとリクエストの状態を保持します。

| 状況 | 最初に適用する制御 |
| --- | --- |
| 接続数の上限とプールの待機時間制限で十分 | コネクションプールの設定を維持する |
| 過負荷時にプールへ入る前にリクエストを拒否したい | 受け入れ制御を追加する |
| バッチ処理や高コストなクエリが接続を独占する | ワークロード別の予算を設け、必要ならプールを分ける |
| 遅い SQL やロックが接続を長時間占有する | まずクエリ、インデックス、トランザクション、データベースの制限を確認する |

HikariCP の `maximumPoolSize` は、プール内の接続数を制限します。利用可能な接続がなければ、`getConnection()` は最大で `connectionTimeout` まで待ってから例外を送出します。その最小値は 250ms です。セマフォの待機を 20ms にしても、プールでの待機も 20ms 以内に終わるわけではありません。[HikariCP の設定](https://github.com/brettwooldridge/HikariCP#configuration-knobs-baby)

## 実行数と受け入れ総数の両方に上限を設ける

この例では二つのセマフォを使います。

- **B 個の実行許可：** 接続の取得からトランザクション処理と接続のクリーンアップまで、進行中の操作数を制限します。
- **B+Q 個の受け入れ許可：** 実行許可を待つ操作も含め、このゲート内のすべての操作数を制限します。受け入れ許可が残っていなければ即座に拒否します。

B 個の実行許可がすべて使用中の場合、追加で受け入れた操作は最大 Q 個まで残れます。ただし、タスクは実行許可を取得する前にもスケジュールされるため、すべての時点で待機タスク数が厳密に Q 以下に収まるという意味ではありません。待機時間だけを制限する単一のセマフォでは、受け入れ済みの待機タスク数に上限を設けられません。

![受け入れ許可と実行許可を順に取得し、DB トランザクションと接続のクリーンアップ後に取得済みの許可だけを解放する](/assets/diagrams/technical/ja-2026-11-03-virtual-threads-db-semaphore.svg)

DB リソースのボックスは、内部の例外経路をまとめたものです。接続の取得に失敗した場合は処理を省略し、許可の解放に進みます。トランザクションの初期設定に失敗した場合は、取得した接続のクリーンアップを試みます。処理またはコミットに失敗した場合は、ロールバックを試みます。

受け入れに失敗した場合、解放する許可はありません。実行許可の取得に失敗した場合や待機中のスレッドが割り込まれた場合は、受け入れ許可だけを解放します。両方の許可を取得した後は、接続の取得、トランザクション処理、クリーンアップが正常終了または例外で終了してから解放します。 **呼び出し元がタイムアウトしたという理由だけで、別のスレッドから許可を解放しないでください。** 実際の DB 処理が続いていると、設定した実行数の上限を超えるおそれがあります。

## B、Q、プールサイズをどう決めるか

B が数えるのは DB 操作の同時実行数であり、一秒あたりのリクエスト数ではありません。接続の取得待ち、コミット、クリーンアップも含むため、実際の SQL 同時実行数は B より少なくなる場合があります。データベースの飽和状況、接続保持時間、ほかのワークロードの予算を測定して決めてください。Q は過負荷時に追加で受け入れる操作数です。待機時間の予算とメモリの両方を考慮して選びます。

たとえば、プール P=24、ゲート B=16 の場合、このゲートを通って進行中となる操作は最大 16 個です。残りの 8 接続は、ほかの処理のために予約されているわけではありません。同じプールを共有し、ゲートを通らない呼び出し元が、すべての接続を占有することもあります。分離のためにプールを分ける場合でも、データベース全体ではそれぞれの接続予算を合算してください。

接続数の上限を見積もる際は、`peak simultaneous instances × pool size per instance + batch, operations and other client connections ≤ DB connection budget` を確認します。インスタンス数のピークには、オートスケーリングと、ローリングデプロイ中に新旧インスタンスが重複する期間も含めます。`instance count × B` が制限するのは、このゲートを通る処理だけです。これらの数値は計算例であり、推奨設定でも性能測定の結果でもありません。

## 実行可能な JDBC の例

この例のゲートは、自身のトランザクションと接続を管理します。コールバックは同期的に実行し、必要なデータをすべて読み込み済みの値だけを返す必要があります。コールバック内でコミット、ロールバック、自動コミット設定の変更をしないでください。`Connection`、`ResultSet`、遅延実行されるクエリストリームを返したり、コールバック内で別の非同期 DB 処理を開始したりすると、この境界による保護の外に出てしまいます。

### `DbBulkhead.java`

```java
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Duration;
import java.util.Objects;
import java.util.concurrent.RejectedExecutionException;
import java.util.concurrent.Semaphore;
import java.util.concurrent.TimeUnit;
import javax.sql.DataSource;

public final class DbBulkhead {
    @FunctionalInterface
    public interface SqlWork<T> {
        T run(Connection connection) throws SQLException;
    }

    private final DataSource source;
    private final Semaphore slots;
    private final Semaphore running;

    public DbBulkhead(DataSource source, int concurrent, int extraSlots) {
        this.source = Objects.requireNonNull(source);
        if (concurrent < 1 || extraSlots < 0) {
            throw new IllegalArgumentException("invalid capacity");
        }
        slots = new Semaphore(Math.addExact(concurrent, extraSlots));
        running = new Semaphore(concurrent, true);
    }

    public <T> T transaction(Duration queueWait, SqlWork<T> work)
            throws SQLException, InterruptedException {
        Objects.requireNonNull(work);
        long nanos = queueWait.toNanos();
        if (nanos < 0) throw new IllegalArgumentException("negative wait");
        if (!slots.tryAcquire()) {
            throw new RejectedExecutionException("db admission full");
        }
        boolean acquired = false;
        try {
            acquired = running.tryAcquire(nanos, TimeUnit.NANOSECONDS);
            if (!acquired) {
                throw new RejectedExecutionException("db admission timed out");
            }
            try (Connection connection = source.getConnection()) {
                connection.setAutoCommit(false);
                try {
                    T value = work.run(connection);
                    connection.commit();
                    return value;
                } catch (SQLException | RuntimeException | Error failure) {
                    try {
                        connection.rollback();
                    } catch (SQLException rollbackFailure) {
                        failure.addSuppressed(rollbackFailure);
                    }
                    throw failure;
                }
            }
        } finally {
            if (acquired) running.release();
            slots.release();
        }
    }

    int available() { return running.availablePermits(); }
    int availableSlots() { return slots.availablePermits(); }
}
```

コードは `running` を取得した場合にだけ解放するため、待機の失敗や割り込みによって許可数が増えることはありません。SQL 例外、実行時例外、エラーが発生するとロールバックを試みます。ロールバックにも失敗した場合、その失敗は抑制された例外として元の例外に追加されます。呼び出し元が戻り値を受け取るのは、コミットと接続の `close()` が完了した後です。コミットに失敗した場合や、コミット後の接続のクリーンアップに失敗した場合は、呼び出し元が例外を受け取っても書き込みが反映済みの可能性があります。書き込みを無条件に再試行しないでください。

公平なセマフォでも、すべてのリクエストについて最初から最後までの順序を保証するわけではありません。この例では、公平な実行用セマフォを時間制限付きで取得しますが、受け入れ時は即時取得を使います。時間制限のない `tryAcquire()` は公平性の設定に従いません。`available()` メソッドは実験時の観察用です。値を読んでから別途受け入れを判断すると、競合が生じます。[Semaphore API](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/Semaphore.html)

デモではプールサイズを 2、B=1、Q=0 に設定します。最初のトランザクションが許可を保持している間、二番目の操作が拒否されることを確認します。ラッチでトランザクションを短時間保持するのは再現のタイミングを合わせるためであり、推奨するサービス処理のパターンではありません。

### `Demo.java`

```java
import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import java.sql.SQLException;
import java.time.Duration;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.RejectedExecutionException;
import java.util.concurrent.TimeUnit;

public class Demo {
    static HikariDataSource pool() {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl(System.getenv("DB_URL"));
        config.setUsername(System.getenv("DB_USER"));
        config.setPassword(System.getenv("DB_PASSWORD"));
        config.setMaximumPoolSize(2);
        config.setMinimumIdle(0);
        config.setConnectionTimeout(500);
        config.setValidationTimeout(250);
        return new HikariDataSource(config);
    }

    public static void main(String[] args) throws Exception {
        try (var pool = pool(); var tasks = Executors.newVirtualThreadPerTaskExecutor()) {
            var gate = new DbBulkhead(pool, 1, 0);
            var entered = new CountDownLatch(1);
            var release = new CountDownLatch(1);
            var first = tasks.submit(() -> gate.transaction(Duration.ZERO, connection -> {
                if (!Thread.currentThread().isVirtual()) throw new AssertionError();
                try (var statement = connection.createStatement()) {
                    statement.setQueryTimeout(2);
                    try (var rows = statement.executeQuery("SELECT 42")) {
                        rows.next();
                        int value = rows.getInt(1);
                        entered.countDown();
                        try {
                            if (!release.await(5, TimeUnit.SECONDS)) {
                                throw new SQLException("demo coordination timed out");
                            }
                        } catch (InterruptedException interrupted) {
                            Thread.currentThread().interrupt();
                            throw new SQLException("demo interrupted", interrupted);
                        }
                        return value;
                    }
                }
            }));
            try {
                if (!entered.await(5, TimeUnit.SECONDS)) throw new AssertionError("not entered");
                var second = tasks.submit(() -> gate.transaction(Duration.ZERO, c -> 0));
                try {
                    second.get(5, TimeUnit.SECONDS);
                    throw new AssertionError("must reject");
                } catch (ExecutionException failure) {
                    if (!(failure.getCause() instanceof RejectedExecutionException)) throw failure;
                    System.out.println("overload=rejected");
                }
            } finally {
                release.countDown();
            }
            System.out.println("query=" + first.get(5, TimeUnit.SECONDS));
            System.out.println("available=" + gate.available());
        }
    }
}
```

### `build.gradle`

```groovy
plugins { id 'application' }
repositories { mavenCentral() }
dependencies {
    implementation 'com.zaxxer:HikariCP:7.1.0'
    runtimeOnly 'org.postgresql:postgresql:42.7.14'
    runtimeOnly 'org.slf4j:slf4j-simple:2.0.20'
}
sourceSets.main.java {
    srcDirs = ['.']
    include 'DbBulkhead.java', 'Demo.java', 'DbBulkheadChecks.java'
}
tasks.withType(JavaCompile).configureEach { options.release = 21 }
application { mainClass = 'Demo' }
tasks.register('copyDependencies', Copy) {
    from configurations.runtimeClasspath
    into layout.buildDirectory.dir('deps')
}
tasks.register('contracts', JavaExec) {
    classpath = sourceSets.main.runtimeClasspath
    mainClass = 'DbBulkheadChecks'
}
```

### `settings.gradle`

```groovy
rootProject.name = 'virtual-threads-db-semaphore'
```

### ローカルで実行する

上の四つのファイルを独立した実験用ディレクトリに保存し、Docker、JDK 21、Gradle 8.14.3 をインストールしてください。依存関係のダウンロードには、JDK 21 上で Gradle を実行します。その後のコンパイルと実行には、選択した JDK の `javac` と `java` を直接使うため、JDK 25 のテスト時に Gradle 8.14.3 自体を JDK 25 上で動かす必要はありません。Gradle 自体を JDK 21 上で実行するには、バージョン 8.5 以降が必要です。この実験では 8.14.3 を使います。[Gradle の Java 21 ランタイムサポート](https://docs.gradle.org/8.5/release-notes.html)

以下のコマンドを POSIX シェルで実行してください。`JAVA_HOME` は実行に使う JDK を指す必要があります。依存関係のダウンロード時は JDK 21 を選択してください。例のパスワードは一時的なローカルデータベース専用です。ポート 55432 が使用中の場合は、別のポートを選んでください。

```sh
(
  set -eu
  gradle --no-daemon -q copyDependencies
  db_container=$(docker run -d --rm -p 127.0.0.1:55432:5432 \
    -e POSTGRES_USER=demo -e POSTGRES_DB=demo \
    -e POSTGRES_PASSWORD=example-only \
    postgres@sha256:839fbb5a4942a7758dd93e18b42ea5649807491a0545b5eeeb8f0b8bb11857a5)
  trap 'docker stop "$db_container" >/dev/null' EXIT
  ready=false
  for attempt in $(seq 1 30); do
    if docker exec "$db_container" pg_isready -h 127.0.0.1 -U demo -d demo >/dev/null 2>&1; then
      ready=true
      break
    fi
    sleep 1
  done
  if [ "$ready" != true ]; then exit 1; fi
  mkdir -p build/classes
  "$JAVA_HOME/bin/javac" --release 21 -cp 'build/deps/*' \
    -d build/classes DbBulkhead.java Demo.java
  DB_URL='jdbc:postgresql://127.0.0.1:55432/demo?connectTimeout=2&socketTimeout=5' \
    DB_USER=demo DB_PASSWORD=example-only \
    "$JAVA_HOME/bin/java" -cp 'build/classes:build/deps/*' Demo
)
```

ローカルで確認した標準出力は次のとおりです。HikariCP の起動と終了のログは、別途表示される場合があります。

```text
overload=rejected
query=42
available=1
```

検証環境は Temurin 21.0.13+9 および 25.0.5+8、PostgreSQL 17.11、HikariCP 7.1.0、pgJDBC 42.7.14 です。補足のチェックでは、各 JDK で 45 項目を検証しました。対象はコミットとロールバック、受け入れ上限の超過、待機のタイムアウトと割り込み、キャンセル後も続く処理、サーバー側のステートメントタイムアウト後の復旧、プールの枯渇、繰り返し失敗した後の許可の回復です。HTTP 負荷テストや本番スループットの測定は行っていません。

## タイムアウトと Spring トランザクションで守るべき境界

**待機のタイムアウトと処理のタイムアウトを分けてください。** この例の `queueWait` が制限するのは、実行許可を待つ時間だけです。プールからの接続取得、SQL とロックの待機、ネットワーク、クリーンアップには、それぞれ別の予算があります。リクエスト全体の期限を設けるには、残り時間を各段階に伝える追加の設計が必要です。この例では、そのような全段階への期限の伝播は実装していません。

PostgreSQL の `statement_timeout` はサーバー上のステートメント実行時間を制限し、`lock_timeout` はロック取得の待機時間を制限します。実験では、トランザクション内で `SET LOCAL statement_timeout = '100ms'` を設定し、`pg_sleep(2)` が SQLState `57014` で失敗することと、その後の処理を進められることを確認しました。実際の値は、クエリと期限に合わせて選んでください。[PostgreSQL 17 のタイムアウト設定](https://www.postgresql.org/docs/17/runtime-config-client.html)

`Future.cancel(true)` も HTTP リクエストの終了も、JDBC クエリの即時終了を保証しません。pgJDBC はクエリ、キャンセル信号の送信、ソケット読み取りに、それぞれ別の制限を持ちます。ソケットタイムアウト後に接続を閉じることと、サーバー側の処理が止まったと確認することも別です。キャンセルとクリーンアップの間も、処理を実行する境界が許可の所有権を保持します。書き込み結果が不明な場合は、冪等性キーを使うか結果を照会して、再試行するかどうかを判断してください。[pgJDBC の接続プロパティ](https://jdbc.postgresql.org/documentation/use/)

**Spring では、トランザクションの開始前に受け入れ許可を取得してください。** 別の Bean にある非トランザクションの入口メソッドでゲートを通過してからトランザクションプロキシを呼ぶか、受け入れ済みのスコープ内で `TransactionTemplate` を実行できます。プロキシ呼び出しまたはテンプレートがコミットとクリーンアップを完了して戻った後で、許可を解放します。トランザクションがすでに始まっているメソッド内で待機すると、外側のトランザクションのリソースを保持したままになる場合があります。上記の JDBC リソースを管理するコードを、既存の Spring トランザクションに直接混ぜないでください。

`REQUIRES_NEW` は、外側のトランザクションの接続を保持したまま、別の接続を必要とする場合があります。これは、この例の「操作ごとに一つの接続」という前提を崩し、プールの枯渇やデッドロック待ちを引き起こす可能性があります。また、ゲートは再入可能ではありません。同じゲートを再帰的に取得しないでください。[Spring のトランザクション伝播とプール枯渇に関する警告](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/tx-propagation.html)

本番では、受け入れ枠が埋まったことによる拒否と待機タイムアウトを分けて数え、ゲートの待機時間、プールの待機時間、接続保持時間、SQL 実行時間、ロック待ちを合わせて観察してください。拒否を HTTP 503 などのレスポンスに対応させる際は、無制限の再試行が負荷を増幅しないよう、クライアントの再試行予算を定義します。拒否件数だけを根拠に B を増やさず、データベースのレイテンシと飽和状況を見て判断してください。
