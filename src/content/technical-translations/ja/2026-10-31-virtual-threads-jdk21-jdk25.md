---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2026-10-31-virtual-threads-jdk21-jdk25",
  "routeSlug": "2026-10-31-virtual-threads-jdk21-jdk25",
  "kind": "post",
  "title": "Java仮想スレッド：JDK 21と25の違いとJFRによるピン留めの確認",
  "description": "仮想スレッドのキャリアとI/O待機を理解し、実行可能なJFRプローブでJDK 21と25のsynchronized内のピン留めを比較します。確定API、プレビュー、残るボトルネックを区別します。",
  "categories": [
    "jdk"
  ],
  "tags": [
    "java",
    "virtual-threads",
    "jdk21",
    "jdk25",
    "jfr",
    "pinning"
  ],
  "sourcePath": "src/content/posts/en/2026-10-31-virtual-threads-jdk21-jdk25.md",
  "sourceSha256": "4b100d81b2721e31e0a765676927aa48165b4b60c224dff2ba5846ba70dec8db",
  "draftSha256": "8883a98ed3b0505f29fc167a00ef4315bc8e792343d8453202c783e9d48e1fe0",
  "manifestPath": ".pipeline/technical-translations/batch-078/manifest.json",
  "manifestSha256": "e685b2de5dafd8cfff8e8e996fa2b09613becb072bdd575b58b9eca9651474a3",
  "publishedAt": "2026-10-31T02:49:44.828Z",
  "updatedAt": "2026-10-31T02:49:44.828Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 118,
    "approvedAt": "2026-10-31T02:49:44.828Z",
    "basis": "2026-10-31 user instruction “진행해줘” immediately following delivery of the reviewed 72 complete translations in PR #118; interpreted as authorization to publish exactly batch-078 in all six languages. Separate AI language review is recorded in the manifest; this does not claim a human line-by-line review. Excludes the older 120 technical drafts and 318 pending news translations."
  }
}
---
仮想スレッドは、**I/Oを待つ間、多数のタスクがより少数のOSスレッドを共有できるJavaスレッド**です。JDK 21で[JEP 444](https://openjdk.org/jeps/444)により確定し、JDK 25でも基本APIは同じです。大きな違いは、`synchronized`内でブロックする際のピン留めです。[JEP 491](https://openjdk.org/jeps/491)がJDK 24でこれを改善し、JDK 25にもその改善が含まれます。

## 何が軽量になりますか？

仮想スレッドも、実行にはOSスレッドを必要とします。JVMは、仮想スレッドを実行するプラットフォームスレッドを**キャリア**と呼びます。対応するブロッキング処理で仮想スレッドがアンマウントされると、キャリアは別の仮想スレッドを実行できます。

これは、多数の待機が同時に発生するリクエスト処理に役立ちます。CPU計算を高速にしたり、単一リクエストの待ち時間を自動で減らしたりはしません。[公式の導入ガイド](https://docs.oracle.com/en/java/javase/25/core/virtual-threads.html)は、タスクごとに仮想スレッドを使うことを勧め、小さなプールでの仮想スレッドの再利用を避けるよう説明しています。データベースの接続容量や外部APIの利用枠は、スレッド数とともに増えません。セマフォや接続プールなどで、それらのリソースを別途制限します。

## JDK 21と25の違い

| 項目 | JDK 21 | JDK 25 |
| --- | --- | --- |
| 仮想スレッドAPI | 確定済みでプレビューフラグは不要です | 確定済みで基本的な作成APIを維持しています |
| `synchronized`内のブロック | キャリアをピン留めして拡張性を制限する可能性があります | JDK 24のJEP 491の改善を含みます |
| すべてのピン留めの解消 | されていません | されていません。ネイティブコードからJavaへ戻ってブロックする経路などは残ります |
| 診断 | JFRや`jdk.tracePinnedThreads`などです | JFRを維持・強化し、`jdk.tracePinnedThreads`は効果がありません |
| `ScopedValue` | プレビューです | JEP 506で確定しています |
| 構造化並行処理 | プレビューです | 引き続き別のプレビューです。以前のAPIとの互換性を仮定しないでください |

[JDK 21ガイド](https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html)、JEP 491、[ScopedValueの記事](/en/posts/2026-10-31-jdk25-scopedvalue/)を併せて読み、これらの変更を区別してください。仮想スレッド、ScopedValue、構造化並行処理の確定は、共通の単一スケジュールで行われるものではありません。

ピン留めは、待機中の仮想スレッドがキャリアを解放できなくなることです。JDK 25では、通常の`synchronized`使用だけを理由に、すべてのモニターを`ReentrantLock`へ置き換える必要はありません。ただし、**キャリアの解放とモニターロックの解放は別です**。`synchronized`内の遅いI/Oは、引き続き他のタスクによるそのロックの取得を妨げます。クリティカルセクションの大きさとロック競合は依然として重要です。

## 同じコードをJFRで観察する

![モードを検証してJFRを開始し、仮想スレッドでモニターの内外で同じ待機を行い、そのワーカーだけのピン留めイベントを数えます](/assets/diagrams/technical/ja-2026-10-31-virtual-threads-jdk21-jdk25.svg)

コードは、`monitor`モードで`Thread.sleep(100)`を`synchronized`内で実行する場合と、そのブロックなしで待機する`plain`モードを比較します。実際のネットワークやデータベースへのリクエストは行いません。[Recording](https://docs.oracle.com/en/java/javase/21/docs/api/jdk.jfr/jdk/jfr/Recording.html)でイベントのしきい値をゼロにし、[RecordingFile](https://docs.oracle.com/en/java/javase/21/docs/api/jdk.jfr/jdk/jfr/consumer/RecordingFile.html)でワーカースレッドのイベントだけを数えます。

各JDKについて、新しいディレクトリにファイルを保存し、同じインストール先の`javac`と`java`を使用します。JFRを含むHotSpot JDKが必要で、プレビューフラグは使いません。プログラムは`monitor.jfr`と`plain.jfr`を作成し、出力先が既に存在する場合は実行を拒否します。

### `VirtualThreadProbe.java`

```java
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.concurrent.Executors;
import jdk.jfr.Recording;
import jdk.jfr.consumer.RecordingFile;

public class VirtualThreadProbe {
    public static void main(String[] args) throws Exception {
        if (args.length != 1 || !(args[0].equals("monitor") || args[0].equals("plain"))) {
            throw new IllegalArgumentException("Usage: VirtualThreadProbe monitor|plain");
        }
        String mode = args[0];
        Path destination = Path.of(mode + ".jfr");
        if (Files.exists(destination)) {
            throw new IllegalStateException("Use a new directory: recording already exists");
        }
        Object monitor = new Object();
        long workerId;
        try (var recording = new Recording()) {
            recording.enable("jdk.VirtualThreadPinned").withThreshold(Duration.ZERO);
            recording.start();
            try (var tasks = Executors.newVirtualThreadPerTaskExecutor()) {
                workerId = tasks.submit(() -> {
                    Thread current = Thread.currentThread();
                    System.out.println("virtual=" + current.isVirtual());
                    if (mode.equals("monitor")) {
                        synchronized (monitor) { Thread.sleep(100); }
                    } else {
                        Thread.sleep(100);
                    }
                    return current.threadId();
                }).get();
            }
            recording.stop();
            recording.dump(destination);
        }
        long pinnedEvents = 0;
        try (var events = new RecordingFile(destination)) {
            while (events.hasMoreEvents()) {
                var event = events.readEvent();
                if (event.getEventType().getName().equals("jdk.VirtualThreadPinned")
                        && event.getThread() != null
                        && event.getThread().getJavaThreadId() == workerId) {
                    pinnedEvents++;
                }
            }
        }
        System.out.println(mode + "-pinned-events=" + pinnedEvents);
    }
}
```

```sh
javac --release 21 VirtualThreadProbe.java
java VirtualThreadProbe monitor
java VirtualThreadProbe plain
```

この出力は、Eclipse Temurin `21.0.13+9`のmacOS AArch64版で観測しました。

```text
virtual=true
monitor-pinned-events=1
virtual=true
plain-pinned-events=0
```

同じプラットフォームのEclipse Temurin `25.0.5+8`では、次の結果になりました。

```text
virtual=true
monitor-pinned-events=0
virtual=true
plain-pinned-events=0
```

`Future.get()`は完了を待ち、タスクの失敗を呼び出し元へ伝えます。記録を停止してダンプした後に読み取るため、集計と稼働中の記録が競合しません。キャリア数は制約せず、総実行時間も比較していません。イベント数は、この一つのタスクについてのものです。他のJVM、パッチ、計測条件へ、確認なしに厳密な件数を一般化しないでください。

## アップグレード後も何を確認する必要がありますか？

JDK 25でイベントがゼロだったのは、具体的には**この例のモニター内の待機**です。ネイティブ呼び出し、外部関数呼び出し、クラス初期化を含む残りの経路を検証したものではありません。JDK 21で有用な`-Djdk.tracePinnedThreads=full`は、JDK 25では効果がありません。代わりに、そのバージョンのJFRイベントとスレッドダンプを使用します。

I/O待機が主な負荷から導入を始め、データベースプール、外部呼び出しの同時実行数、タイムアウト、キャンセルをまとめて検討します。CPU負荷の高い処理、長いクリティカルセクション、大きなスレッド単位のキャッシュは、引き続きボトルネックになり得ます。本番を代表する負荷で、スループット、テールレイテンシ、メモリ、ロック競合を測定してください。この小さな観測プログラムから性能改善率を計算しないでください。仮想スレッド実行に関連するコンテキストは、ScopedValueの記事のバインディングと非同期境界の規則を参照してください。
