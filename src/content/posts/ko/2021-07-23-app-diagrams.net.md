---
title: "draw.io 다이어그램 관리: 편집 원본과 공유 이미지를 함께 보관하기"
language: ko
translationKey: 2021-07-23-app-diagrams.net
routeSlug: 2021-07-23-app-diagrams.net
kind: post
publishedAt: 2021-07-23T01:00:00.000Z
categories:
  - util
tags:
  - util
  - uml
  - 다이어그램
legacyUrl: /util/app-diagrams.net/
legacySource: _posts/util/2021-07-23-app-diagrams.net.markdown
updatedAt: 2026-10-27T05:47:47.001Z
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Primary documentation checked; paired examples and diagram/code
  structure validated. Execution and UI limits are stated in the article.
archiveBodySha256: 671e96b0078d6509043884567b4b94850a66f2830bdf1d55c47d8e51420af7c6
reviewSources:
  - https://www.drawio.com/docs/manual/editor/save-file-formats/
  - https://www.drawio.com/docs/manual/advanced/diagram-source-edit/
description: .drawio XML 예제로 노드·연결 관계를 정의하고 편집 원본과 공유용 SVG·PNG를 구분합니다. 파일 확장자만으로
  편집 가능 여부를 판단하지 않습니다.
---
게시한 그림과 함께 편집 가능한 다이어그램 원본을 보관하세요. 이미지는 현재 결과를 보여주고, 원본은 다음 수정에 필요한 도형·연결선·레이블을 유지합니다.

[draw.io 파일 형식 안내](https://www.drawio.com/docs/manual/editor/save-file-formats/)는 압축하지 않은 XML인 `.drawio`를 권장합니다. SVG·PNG에도 다이어그램 데이터가 들어갈 수 있으므로 확장자만으로 편집 가능 여부를 단정하지 않습니다. 내보낸 파일에 데이터가 포함돼도 명시적인 원본을 함께 두면 관리 기준이 분명해집니다.

## 예제 흐름

![Request에서 Validate를 거쳐 Response로 가는 흐름도](/assets/diagrams/2021-07-23-app-diagrams.net-ko.svg)

그림은 아래 XML과 같은 노드 3개, 방향이 있는 연결 2개를 보여줍니다. 글에서 별도로 렌더링한 그림이며 편집기 화면이나 내보내기 결과를 캡처한 것은 아닙니다.

## 원본 XML 저장하기

다음 코드를 `request-flow.drawio`로 저장합니다.

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

`vertex="1"`인 `mxCell`이 세 노드입니다. 두 연결선은 출발·도착 노드의 ID를 참조하고, `mxGeometry`는 위치·크기를 정의합니다. 화면의 레이블 변경과 연결선이 참조하는 ID 변경은 서로 다른 수정입니다.

파일을 편집기에서 엽니다. 전체 파일에는 바깥쪽 `mxfile`·`diagram` 요소가 포함됩니다. **Extras → Edit Diagram**을 사용할 때는 [원본 편집 안내](https://www.drawio.com/docs/manual/advanced/diagram-source-edit/)의 현재 페이지 `mxGraphModel` 범위를 다루므로 전체 파일과 페이지 조각을 구분하세요.

| 파일 | 용도 |
| --- | --- |
| `request-flow.drawio` | 버전 관리할 편집 원본 |
| `request-flow.svg`·`.png` | 공유·표시용 결과물. 편집 데이터 포함 여부는 별도로 확인 |

수정 후 원본을 다시 열어 화살표의 방향을 확인하고 공유 그림도 다시 내보냅니다. 소스 변경과 렌더링 결과를 함께 확인하면 서식 변경에 가려진 관계 수정도 찾기 쉽습니다.

예제의 XML 구조·ID 중복·연결 대상은 로컬에서 검사했습니다. 클라우드 저장소, 편집기 UI 조작, 내보내기 후 재열기는 해당 검사의 범위가 아닙니다. 저장소 연동은 사용하는 계정·편집기에서 별도로 선택하세요. 저장소 안의 확인 대상을 좁히는 방법은 [코드 검색 가이드](/ko/posts/2021-08-06-search-github/)에서 이어집니다.
