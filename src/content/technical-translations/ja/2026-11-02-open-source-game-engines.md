---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2026-11-02-open-source-game-engines",
  "routeSlug": "2026-11-02-open-source-game-engines",
  "kind": "post",
  "title": "オープンソースゲームエンジン比較：Godot、Bevy、Stride、O3DE",
  "description": "チームの制作フロー、ライセンス、対象プラットフォームの制約から Godot、Bevy、Stride、O3DE を比較し、実行可能な Godot の移動チェックを示します。",
  "categories": [
    "game-development"
  ],
  "tags": [
    "game-engine",
    "open-source",
    "godot",
    "bevy",
    "stride",
    "o3de"
  ],
  "sourcePath": "src/content/posts/en/2026-11-02-open-source-game-engines.md",
  "sourceSha256": "a83f90ac45031156dd23d82e78c770e9d3254849fbf67e9594455bc58c54e153",
  "draftSha256": "eba865d97b50ac4bddad7945b6868f9088ea786ed384c3e30db4d5f6db2a3908",
  "manifestPath": ".pipeline/technical-translations/batch-133/manifest.json",
  "manifestSha256": "012f8ab540d4cc0a5cef8d221664572be5fe6cfb38caebd3ef7cfc3c84c954a2",
  "publishedAt": "2026-11-02T04:33:37.064Z",
  "updatedAt": "2026-11-02T04:33:37.064Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 133,
    "approvedAt": "2026-11-02T04:33:37.064Z",
    "basis": "User explicitly requested writing and publishing a blog article using the game-engine review writing skill on 2026-11-02, with existing multilingual publication and standing blog PR merge authorization. Human approval denotes user publication authorization, not human/native linguistic review; language reviews are AI."
  }
}
---

**一般的な 2D または 3D ゲームを作り始める小規模チームには、Godot が最初の候補になります。Bevy はツール整備をより多く自分たちで担える Rust チームに向き、C# の制作フローなら Stride を検討する価値があります。O3DE は、規模の大きな 3D コンテンツとビルドのパイプラインを支えられるチームで評価する価値があります。** これらは検証の出発点であり、性能の順位ではありません。

この記事は、ゲームエンジンを選ぶ開発者に向けた、文書に基づく比較です。2026年11月2日に確認したリリースの参照対象は Godot 4.7.2、Bevy 0.20、Stride 4.4、O3DE 26.05 です。以下の実行可能な例でテストするのは、Godot の小さな移動関数だけです。他のエンジンのエディターの使い勝手、描画速度、エクスポートの信頼性を確かめたものではありません。

## 何を比較するのか？

四つのプロジェクトは、いずれも自身をゲームエンジンと位置づけています。制作フローは異なり、統合されたビジュアルエディターと、コード主導の ECS の制作フローでは、チームが自分たちで組み合わせる必要のあるツールの範囲が変わります。フレームワークや描画ライブラリも適切な選択になり得ますが、不足するシーン、アセット、編集のツールをチームが用意する作業として比較してください。

| エンジンと参照リリース | 開発フロー | 採用を決める前の最初の問い |
| --- | --- | --- |
| [Godot 4.7.2](https://godotengine.org/download/archive/) | シーン／ノードのエディターとスクリプト | 選んだ言語で実際の対象へエクスポートできるか？ |
| [Bevy 0.20](https://bevy.org/news/bevy-0-20/) | ECS を中心とした Rust のシステムとコンポーネント | ツールの保守と API の移行をチームが担えるか？ |
| [Stride 4.4](https://www.stride3d.net/blog/announcing-stride-4-4/) | C# と Game Studio | 開発マシンでエディターを利用できるか？ |
| [O3DE 26.05](https://www.docs.o3de.org/docs/release-notes/2605-0-release-notes/) | 拡張可能な 3D エディターとコンポーネントのパイプライン | チームがビルド、アセットのインポート、小さなシーンのパッケージ化を行えるか？ |

以下のシナリオは、これらの制作フローから導いた推奨です。チームが各エンジンでゲームを出荷した体験談ではありません。

## チームの制作フローに合うエンジンは？

### Godot：制作の一連の流れから始める

シーンを編集し、振る舞いを追加し、一つの環境で反復したいチームにとって、Godot は妥当な基準となる候補です。[MIT ライセンス](https://godotengine.org/license/)は非公開ソースのゲーム制作を認めていますが、エンジンを配布する場合には、該当する著作権表示とライセンス表示が引き続き必要です。プラグイン、フォント、音楽、モデルにはそれぞれの利用条件があります。

言語とプラットフォームの組み合わせは早めに確認してください。[Godot の Web エクスポート文書](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_web.html)では、現在 Godot 4 の C# プロジェクトは Web にエクスポートできないとされています。したがって、デスクトップ用 C# プロトタイプは、ブラウザー版を提供できる証拠にはなりません。コンソールについては、[Godot の移植ガイダンス](https://godotengine.org/consoles/)に、プラットフォームの承認、公式 SDK、非公開のエクスポートテンプレートや外部事業者について記載されています。オープンソースのエンジンでも、この手続きはなくなりません。

### Bevy：Rust とツール整備の責任を一緒に選ぶ

Bevy はエンジンであり、単なるレンダラーではありません。[導入文書](https://bevy.org/learn/quick-start/introduction/)では、Rust、ECS、MIT または Apache 2.0 ライセンスの選択について説明されています。また、API に破壊的変更を含むリリースや、移行が難しくなる可能性にも注意を促しています。

そのため、システムとコンポーネントを開発モデルの中心に据えたいチームには、Bevy が興味深い候補になります。エディターの統合、アセットの反復調整、バージョン移行は、チームのプロジェクトで実証すべき項目として扱ってください。Rust に慣れているだけで制作の反復が速くなると判断することはできず、並列 ECS も特定のゲームでフレーム時間が短くなる証明にはなりません。

### Stride：C# 対応とエディターの利用可否を分ける

Stride の [FAQ](https://www.stride3d.net/faq/)では、MIT ライセンスの採用と、エンジンのロイヤリティが不要であることが説明されています。C# の制作フローは、既存の .NET チームにとって有用な候補となり得ます。

[プラットフォーム一覧](https://doc.stride3d.net/latest/en/manual/platforms/index.html)では、開発ホストとゲームの対象プラットフォームを区別しています。Windows はエディターを完全にサポートし、Linux と macOS は条件付きでビルドやコードのみの開発フローに対応していますが、Windows 以外ではエディターをネイティブに利用できません。[4.4 の発表](https://www.stride3d.net/blog/announcing-stride-4-4/)では Windows 以外のビルドの改善が報告されています。その改善を、どこでも同じエディターの制作フローが使えるという主張に広げないでください。

### O3DE：見栄えのよいデモより先にパイプラインを評価する

拡張可能な 3D パイプラインを自分たちで維持する準備のあるチームなら、O3DE を候補に入れる価値があります。[ライセンスファイル](https://github.com/o3de/o3de/blob/2605.0/LICENSE.txt)では、標準で Apache 2.0 を指定し、MIT も選択できるとしたうえで、別の条件が適用されるサードパーティー製コンポーネントを示しています。[ダウンロードページ](https://o3de.org/download/)には Windows／Linux のパッケージと、開発マシンに求められる高い要件が掲載されています。これらはホストの要件であり、ゲームのエクスポート先を網羅した一覧ではありません。

代表的なアセットのインポート、プロジェクトのビルド、シーンのパッケージ化から始めてください。[26.05 のリリースノート](https://www.docs.o3de.org/docs/release-notes/2605-0-release-notes/)では、新しいパーティクルシステムを実験的機能とし、本番での使用を推奨していません。リリースノートに機能が載っていても、本番で依存してよい状態とは限りません。

## 「無料」はオープンソースや制作費ゼロを意味するか？

いいえ。ソースを閲覧できることや購入価格がゼロであることだけでは、オープンソースライセンスとは判断できません。たとえば、[Defold は現在、自身をソース公開型と説明しています](https://defold.com/open/)。上記の四つのエンジンと自動的に同じ分類にせず、固有のライセンスを評価してください。

エンジンのライセンスが、コンソールへの移植、アセットのライセンス、ホスティング、プラグイン、保守の費用を負担してくれるわけでもありません。決定前に、エンジンが提供する部分、別のライセンスが必要な部分、チームが作る部分を特定してください。その範囲を定めずに総費用を見積もることは避けましょう。

## 小さなプロトタイプで何を検証すべきか？

候補のエンジンには、代表的なアセットを一つ読み込み、一つの操作を実装し、想定する対象向けのビルドを作る、という同じ受け入れ課題を与えてください。セットアップ、編集と実行を繰り返す際の手間、対応できない要件を記録します。これは評価方法の提案であり、この記事のために実施したベンチマークではありません。

再現可能な部分を一つ示します。**Godot のヘッドレス移動チェック**です。位置、模擬的な方向、経過秒数を受け取り、方向ベクトルの長さを最大 1 に制限し、速度を適用したうえで、結果の点を長方形の範囲内に収めます。入力は有限値で、経過時間は非負であると仮定しています。この範囲制限は、障害物との衝突判定、スプライトの大きさの処理、物理シミュレーションではありません。

![位置、方向、経過時間を受け取り、方向ベクトルの長さを制限し、速度と時間を適用して点を範囲内に収め、新しい位置を返す](/assets/diagrams/technical/ja-2026-11-02-open-source-game-engines.svg)

図は `advance` の一回の呼び出しを示しています。以下のテストプログラムは呼び出しを繰り返して結果を確認し、キーボード入力の読み取りやキャラクターの描画は行いません。[Vector2 のリファレンス](https://docs.godotengine.org/en/4.7/classes/class_vector2.html)には、これらのベクトル演算が記載されています。これにより、テストした振る舞いを、エディターの生産性やゲーム性能に関する主張と区別できます。

標準の Godot 4.7.2 エディターの実行ファイルを `godot` として利用できる状態で、`project.godot` と `movement.gd` を同じディレクトリに保存してください。エンジンのインストール後、スクリプトの実行にはシーン、外部アセット、パッケージ、ネットワークアクセスは不要です。

`project.godot`：

```ini
config_version=5
```

`movement.gd`：

```gdscript
extends SceneTree

const SPEED := 120.0
const LIMIT := Vector2(640.0, 360.0)

func advance(pos: Vector2, direction: Vector2, delta: float) -> Vector2:
    var bounded := direction.limit_length(1.0)
    var next := pos + bounded * SPEED * delta
    return next.clamp(Vector2.ZERO, LIMIT)

func _initialize() -> void:
    var cases := [
        [Vector2(100, 100), Vector2.ZERO, 0.5, Vector2(100, 100)],
        [Vector2(100, 100), Vector2.RIGHT, 0.5, Vector2(160, 100)],
        [Vector2.ZERO, Vector2(1, 1), 1.0, Vector2(84.852814, 84.852814)],
        [Vector2.ZERO, Vector2(0.5, 0), 1.0, Vector2(60, 0)],
        [Vector2(639, 100), Vector2.RIGHT, 1.0, Vector2(640, 100)],
        [Vector2(5, 100), Vector2.LEFT, 1.0, Vector2(0, 100)],
        [Vector2(100, 359), Vector2.DOWN, 1.0, Vector2(100, 360)],
        [Vector2(100, 100), Vector2.RIGHT, 0.0, Vector2(100, 100)],
    ]
    for sample in cases:
        var actual := advance(sample[0], sample[1], sample[2])
        if not actual.is_equal_approx(sample[3]):
            push_error("movement mismatch")
            quit(1)
            return
    var split := advance(advance(Vector2(100, 100), Vector2.RIGHT, 0.25), Vector2.RIGHT, 0.25)
    if not split.is_equal_approx(advance(Vector2(100, 100), Vector2.RIGHT, 0.5)):
        push_error("time-step mismatch")
        quit(1)
        return
    print("movement cases=9")
    quit(0)
```

そのディレクトリで [Godot のコマンドラインインターフェース](https://docs.godotengine.org/en/4.7/tutorials/editor/command_line_tutorial.html)を使って実行します。macOS で `PATH` に登録されていない場合は、`godot` をインストールしたアプリケーションバンドルの `Godot.app/Contents/MacOS/Godot` パスに置き換えてください。

```sh
godot --headless --no-header --path . --script movement.gd --quit-after 1
```

この例は、macOS 上の Godot 4.7.2 でローカル実行しました。出力は次のとおりでした。

```text
movement cases=9
```

チェックの対象は、入力なし、水平移動と斜め移動、最大長に満たない方向入力、上限と下限、経過時間ゼロ、境界から離れた位置で時間ステップを分割する場合です。描画、対象デバイスへのエクスポート、障害物、ネットワーク、性能比較は検証していません。

## 最終的にどう選ぶべきか？

ゲームに必要な制作フローと対象向けビルドを満たし、チームが保守の負担を受け入れられる候補を選んでください。ビジュアル編集の反復を優先するなら、Godot でプロトタイプを始めます。チームが Rust／ECS を自分たちで管理することを明確に望むなら、Bevy のツール整備と移行の費用をテストします。C# チームは、実際にエディターを使うホスト上で Stride を試してください。規模の大きな 3D パイプラインでは、デモの目玉機能に依存する前に、O3DE のアセットとビルドの反復工程を検証します。

次に役立つ成果物は、対象デバイス向けの小さなビルドと未達要件の一覧であり、汎用的なエンジンランキングではありません。その判断根拠をプロジェクトとともに保管し、エンジンを更新するときにも同じ振る舞いを基準に評価できるようにしてください。
