---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2026-11-15-orca-herdr-comparison",
  "routeSlug": "2026-11-15-orca-herdr-comparison",
  "kind": "post",
  "title": "Orca と Herdr の比較：AI コーディングエージェントをどこで、どう管理するか",
  "description": "Orca と Herdr の worktree、セッション維持、コードレビュー、リモート作業、拡張方法を比較し、利点と考慮点を紹介します。",
  "categories": [
    "ai"
  ],
  "tags": [
    "orca",
    "herdr",
    "ai-agent",
    "git-worktree",
    "developer-tools"
  ],
  "sourcePath": "src/content/posts/en/2026-11-15-orca-herdr-comparison.md",
  "sourceSha256": "2a0f1ca513f60e49bad64d71689d7e59effe22e995582b05d6e1688572f172e4",
  "draftSha256": "5fa7b368eae48ac1e817c118f2789585d8a65b5a5264ec97feb2883903917471",
  "manifestPath": ".pipeline/technical-translations/batch-165/manifest.json",
  "manifestSha256": "8b72a2b5aba51a050b30cc0ef5f871d2ef550798d50d91ef082c49bbf6448835",
  "publishedAt": "2026-11-17T06:12:46.742Z",
  "updatedAt": "2026-11-17T06:12:46.742Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 165,
    "approvedAt": "2026-11-17T06:12:46.742Z",
    "basis": "User requested multilingual application of the five recent articles and standing publication/merge authorization; AI translation and independent AI comparison completed. This records publication authorization, not human or native-speaker textual review."
  }
}
---

**コードの変更を worktree ごとに確認し、ブラウザー・diff・PR を一つの画面で扱いたいなら Orca が便利です。ターミナル中心の構成やアプリ画面を自分で拡張したいなら、Herdr を検討する価値があります。** 両ツールとも複数のコーディングエージェントを実行し、Git worktree を活用できます。選ぶ基準は、並列実行できるかどうかよりも、作業環境と結果の管理方法です。

比較対象は [Orca](https://orca.dev/) と [Herdr](https://herdr.dev/) です。Herdr はデスクトップアプリ、ターミナル用の **Herdr TUI**、独立したターミナルランタイム **herdr-core** に分かれています。以下は 2026 年 11 月 15 日に確認した公式文書に基づく説明であり、同じ作業で両アプリを直接比較した性能試験ではありません。提供元が説明する機能と、それを基にした選択基準を分けて読んでください。

## 違いを一覧で見る

| 基準 | Orca | Herdr |
| --- | --- | --- |
| 中心となる画面 | エージェント・エディター・diff・ブラウザーをまとめたデスクトップ開発環境 | デスクトップアプリと別の TUI。herdr-core は画面なしでターミナルを実行 |
| 作業の分離 | 作業ごとに Git worktree を作り、ブランチ・ターミナル・ブラウザーを関連付ける | アプリガイドと TUI 設定に worktree 作成機能がある。通常のターミナル pane が常に独立した worktree とは限らない |
| コードの確認 | worktree diff、変更行へのコメント、Git と PR の画面 | ターミナルやユーザーが構成したアプリ画面が中心。同等の diff 機能と範囲は導入した構成で確認が必要 |
| セッション維持 | デーモンが動いていればアプリ終了後もプロセスを維持。ホスト再起動でプロセス終了 | アプリは herdr-core、TUI は別サーバーがターミナルを維持。サーバーやホストの再起動で元のプロセスは終了 |
| 拡張方法 | CLI・スキル・スケジュールとアプリの作業画面 | アプリのレイアウト・モード、TUI プラグイン、herdr-core CLI と API |
| ライセンス | MIT | Apache 2.0 |

Orca の [worktree 文書](https://orca.dev/docs/model/worktrees)と [diff 案内](https://orca.dev/docs/review/diff-viewer)、Herdr の[アプリガイド](https://herdr.dev/guide/)と [TUI 設定案内](https://herdr.dev/tui/docs/config-reference/)を基に整理しました。この表は、特定バージョンで両製品の全機能を実測した結果ではありません。

## 同じ仕事を任せた場合の流れの違い

例えば、一つのリポジトリで API の修正とテストの補強を同時に任せるとします。二つの作業が同じファイルを触る可能性があれば、まず作業ごとに worktree を分けます。各エージェントの読み書きする範囲を決め、完了したらそれぞれの変更をレビューしてから統合します。

Orca は、作業ごとに worktree を開き、エージェントと diff をその作業空間に結び付ける流れを提供します。[最初の作業の案内](https://orca.dev/docs/first-session)では、複数の独立した worktree でエージェントを実行し、各 diff をレビューする過程を説明しています。

Herdr デスクトップアプリの公式ガイドでは、作業ごとに worktree の作成を依頼し、エージェントを実行する例が紹介されています。TUI は workspace・tab・pane を管理し、別途 worktree 機能も提供します。通常の pane を複数開いたからといって、それぞれに別の作業ディレクトリがあるとは考えず、開始前にパスとブランチを確認します。[アプリガイド](https://herdr.dev/guide/) · [TUI worktree コマンド](https://herdr.dev/tui/docs/cli-reference/)

![基準コミットから作業ツリー A と B を作り、それぞれに異なる値を書き込む。各ファイルと変更一覧を確認し、基準ファイルと照合する](/assets/diagrams/technical/ja-2026-11-15-orca-herdr-comparison.svg)

図は、以下の Git 例のファイルの流れを示しています。エージェントの実行や結果の自動マージは含みません。

## worktree の分離を実際に確認する例

次の例は Git をインストールした macOS または Linux のシェルで実行します。一時リポジトリと二つの worktree を作るため、既存のプロジェクトは変更しません。Orca や Herdr のインストール・設定方法に代わる例ではありません。

```sh
#!/bin/sh
set -eu
case_dir=$(mktemp -d)
git init -q "$case_dir/repo"
git -C "$case_dir/repo" config user.name 'Example Author'
git -C "$case_dir/repo" config user.email 'example@example.invalid'
printf 'base\n' > "$case_dir/repo/app.txt"
git -C "$case_dir/repo" add app.txt
git -C "$case_dir/repo" commit -qm 'Initial commit'
git -C "$case_dir/repo" worktree add -qb task-a "$case_dir/task-a" HEAD
git -C "$case_dir/repo" worktree add -qb task-b "$case_dir/task-b" HEAD
printf 'task A\n' > "$case_dir/task-a/app.txt"
printf 'task B\n' > "$case_dir/task-b/app.txt"
printf 'A: '; cat "$case_dir/task-a/app.txt"
printf 'B: '; cat "$case_dir/task-b/app.txt"
printf 'base: '; cat "$case_dir/repo/app.txt"
printf 'A 변경 파일: '; git -C "$case_dir/task-a" diff --name-only
printf 'B 변경 파일: '; git -C "$case_dir/task-b" diff --name-only
```

ローカルシェルで確認した出力は次のとおりです。

```text
A: task A
B: task B
base: base
A 변경 파일: app.txt
B 변경 파일: app.txt
```

各 worktree のファイル内容は独立していますが、どちらの作業も `app.txt` を変更しています。そのため、実際のプロジェクトで二つの結果を統合すると、競合や意味上の矛盾が生じる可能性があります。worktree はファイルの変更を分離するだけで、DB・ポート・外部サービス・認証情報を自動的に隔離したり、コードの競合を解決したりはしません。一時ディレクトリは例によって自動削除されません。

実際の作業環境で worktree を整理するときは、ツールごとの削除範囲も確認します。Orca は確認後に worktree とブランチを削除できますが、Herdr TUI の worktree 削除コマンドは、チェックアウトを削除してもブランチは削除しないと説明されています。変更内容と未マージのコミットを確認してから整理してください。[Orca worktree](https://orca.dev/docs/model/worktrees) · [Herdr TUI CLI](https://herdr.dev/tui/docs/cli-reference/)

## Orca の利点と考慮点

Orca の強みは、**作業から結果のレビューまでつながる画面**です。[diff viewer](https://orca.dev/docs/review/diff-viewer)は変更されたファイルと行を表示し、競合解決画面と部分ステージングを提供します。別のブラウザーとエディターを同じ作業空間で使えるため、Web UI を修正して直接確認する流れを構成しやすくなります。

[リモート実行の案内](https://orca.dev/docs/ways-to-run)では、SSH ホストやユーザー管理のサーバーを選ぶ方法も説明しています。リモート作業が可能なことと、すべての環境が標準で同じ権限で安全に隔離されることは別です。リモートマシンのアカウントや秘密情報、ネットワークアクセスは別途管理する必要があります。

[セッション復元の案内](https://orca.dev/docs/model/session-restore)によると、アプリを終了してもバックグラウンドのデーモンが動いていればエージェントは実行を続けます。ホストが再起動したりデーモンが終了したりすると、実行中のプロセスは失われ、復元した作業空間でエージェントを再実行する必要があります。

考慮すべき点は、デスクトップ環境と機能に慣れる必要があることです。単一のターミナル作業だけなら、複数の画面や作業空間はかえって不要かもしれません。複数のエージェントを同時に動かすとモデル利用量が増える場合があり、独立して変更した結果はそれぞれレビューが必要です。Orca 自体がモデルの応答の正確性を保証するわけではありません。

## Herdr の利点と考慮点

Herdr の強みは、**実行中のターミナルとエージェントを維持しながら作業空間を構成できる柔軟性**です。[herdr-core](https://herdr.dev/core/)は、ウィンドウを閉じても管理中のターミナルを維持し、エージェントが別の作業を開始して結果を読むインターフェースを説明しています。アプリのレイアウトやモードを調整する使い方も[公式ガイド](https://herdr.dev/guide/)で紹介されています。

Herdr を使う際は、アプリと TUI を区別する必要があります。公式サイトによると、デスクトップアプリは herdr-core を使いますが、**Herdr TUI は別サーバーを使い、両環境のエージェント一覧は共有されません。** アプリを閉じることと、コンピューターやランタイムを再起動することも別です。デスクトップアプリでは、ウィンドウを閉じたりアプリを更新したりしても core が動いていればプロセスは維持されますが、端末の再起動や core の停止でプロセスは止まります。公式サイトでは、その場合アプリの pane は戻るものの、エージェントは自動再起動されないと説明しています。[Herdr FAQ](https://herdr.dev/)

TUI には別の復元ルールがあります。切断してから再接続した場合、サーバーが動いている間は既存のプロセスが維持されます。サーバーが再起動するとプロセスは終了し、レイアウトの復元と対応エージェントのセッション再開は別の機能です。[TUI セッション復元](https://herdr.dev/tui/docs/session-state/)

カスタマイズが増えるほど、どのモードがどの権限や外部接続を使うか確認する責任も大きくなります。また、Herdr アプリの状態表示は [OSC 7501](https://herdr.dev/core/) を報告するプログラムに依存します。非対応のプログラムも実行できますが、状態が表示されない場合があります。TUI のエージェント検出方法とアプリの状態表示を同じ機能と決めつけないようにしましょう。

## どのような場面で選ぶか

- **変更レビューと Web 画面の確認が中心なら：** Orca の worktree ごとの diff・ブラウザー・PR の流れから確認します。
- **ターミナル維持と画面構成が中心なら：** Herdr アプリと core を確認し、ターミナル内で管理したければ別の TUI も比較します。
- **複数のサーバーとエージェントを一緒に運用するなら：** 両ツールともリモート機能を提供するため、実際の SSH 環境、認証方法、セッション復旧条件を確認します。
- **一つの短い修正だけが必要なら：** 既存のターミナルと Git で十分な場合があります。管理ツールが加える複雑さと便利さを比較してください。

両ツールを選ぶ際は、同じリポジトリ・同じ作業・同じモデルと権限で小さく試すとよいでしょう。作業の作成、中断後の復帰、変更確認、統合までをそれぞれたどり、実際の所要時間とエラーを記録すると、自分の作業方法に合った選択ができます。この記事では、そのような比較測定は実施していません。
