---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ja",
  "translationKey": "2021-07-23-app-diagrams.net",
  "routeSlug": "2021-07-23-app-diagrams.net",
  "kind": "post",
  "title": "共有図と一緒に編集可能な draw.io ソースを保管する",
  "description": "非圧縮 draw.io XML の小さな図を作り、.drawio ソースを保管します。編集可能な図データと共有用 SVG・PNG を区別します。",
  "categories": [
    "util"
  ],
  "tags": [
    "diagrams",
    "xml",
    "drawio"
  ],
  "sourcePath": "src/content/posts/en/2021-07-23-app-diagrams.net.md",
  "sourceSha256": "994c0cd18640921c0e130d9310adace919b39b5be0e5a2b54b5cee9772bdd8c0",
  "draftSha256": "c22fdf0e9c553b27cd300dde405b31571012f08bf9fc6cccdc2531ca6191aabd",
  "manifestPath": ".pipeline/technical-translations/batch-056/manifest.json",
  "manifestSha256": "5c3bd2ee5ccb0b59bad65322a026d7b2ef52cfac963e0236a497f74510717e42",
  "publishedAt": "2026-10-31T15:21:36.846Z",
  "updatedAt": "2026-10-31T15:21:36.846Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 125,
    "approvedAt": "2026-10-31T15:21:36.846Z",
    "basis": "User explicitly requested applying all missing technical-post languages, review, verification and deployment on 2026-11-01, with standing PR merge authorization. Human approval denotes publication authorization; linguistic review is performed by AI, not human/native review."
  }
}
---
公開する画像とともに、編集可能な図のソースを保管してください。画像は現在の結果を示し、ソースは次の変更に必要な図形・接続・ラベルを保持します。

[draw.io 形式ガイド](https://www.drawio.com/docs/manual/editor/save-file-formats/)は、非圧縮 XML 形式の `.drawio` を推奨しています。SVG や PNG にも図データを含められるので、画像の拡張子だけでは編集可能か判断できません。エクスポートに埋め込まれる場合も、明示的なソースを保管します。

## 例の流れ

![図は下の XML と同じ三つの頂点と二つの有向接続を示します。この記事用に描画したもので、編集画面のスクリーンショットやエクスポートではありません。](/assets/diagrams/technical/ja-2021-07-23-app-diagrams.net.svg)

図は下の XML と同じ三つの頂点と二つの有向接続を示します。この記事用に描画したもので、編集画面のスクリーンショットやエクスポートではありません。

## request-flow.drawio として保存する

```xml
<mxfile host="app.diagrams.net">
  <diagram id="request-flow" name="Request flow">
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="request" value="Request" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="40" y="40" width="160" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="validate" value="Validate" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="40" y="160" width="160" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="response" value="Response" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="40" y="280" width="160" height="60" as="geometry"/>
        </mxCell>
        <mxCell id="first" edge="1" parent="1" source="request" target="validate" style="endArrow=block;">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <mxCell id="second" edge="1" parent="1" source="validate" target="response" style="endArrow=block;">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

`vertex="1"` の `mxCell` 要素が三つのノードを定義します。二つの辺は接続元・接続先の ID を参照し、`mxGeometry` が位置とサイズを与えます。表示ラベルの変更と、辺が参照する ID の変更は別の操作です。

ファイルをエディターで開きます。完全なファイルは外側の `mxfile` と `diagram` を含みます。代わりに **Extras → Edit Diagram** を使う場合、[ソースエディターの文書](https://www.drawio.com/docs/manual/advanced/diagram-source-edit/)が説明するのは現在のページの `mxGraphModel` です。このページ断片と完全なファイルの外枠を混同しないでください。

| ファイル | 目的 |
| --- | --- |
| `request-flow.drawio` | バージョン管理する編集可能なソース |
| `request-flow.svg` または `.png` | 共有・表示用の出力。図データの埋め込みを確認する |

変更後はソースを開き直し、各矢印の方向を確認して、新しい共有画像を書き出します。ソース差分と描画結果の両方を確認してください。整形の変更で小さな関係の変更が見えにくくなることがあります。

例の XML 構造、ID の一意性、接続の参照はローカルで確認しています。クラウド保存、エディター UI 操作、エクスポートの往復は対象外です。使うアカウントとエディターに合う保存連携は別途選んでください。[コード検索ガイド](/en/posts/2021-08-06-search-github/)では、リポジトリ内で調べるファイルの絞り方を説明しています。
