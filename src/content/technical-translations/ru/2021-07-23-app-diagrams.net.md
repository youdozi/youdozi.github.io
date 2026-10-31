---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "ru",
  "translationKey": "2021-07-23-app-diagrams.net",
  "routeSlug": "2021-07-23-app-diagrams.net",
  "kind": "post",
  "title": "Редактируемые исходники draw.io рядом с опубликованными схемами",
  "description": "Создание небольшой несжатой XML-схемы draw.io, сохранение .drawio и различие редактируемых данных и SVG/PNG для публикации.",
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
  "draftSha256": "9305b796fe5a1762a15e5dfc2caf368f7e82776985023a6f77594b0352f6a2ee",
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
Сохраняйте редактируемый исходник схемы рядом с публикуемым изображением. Картинка показывает текущий результат, а исходник хранит фигуры, соединения и подписи для следующего изменения.

[Руководство по форматам draw.io](https://www.drawio.com/docs/manual/editor/save-file-formats/) рекомендует `.drawio` — несжатый XML-формат. SVG и PNG тоже могут содержать данные схемы, поэтому одно расширение изображения не говорит о возможности редактирования. Сохраняйте отдельный исходник, даже если он встроен в экспорт.

## Ход примера

![Схема показывает те же три вершины и две направленные связи, что и XML ниже. Она отрисована для статьи, а не снята с экрана или экспортирована из редактора.](/assets/diagrams/technical/ru-2021-07-23-app-diagrams.net.svg)

Схема показывает те же три вершины и две направленные связи, что и XML ниже. Она отрисована для статьи, а не снята с экрана или экспортирована из редактора.

## Сохраните как request-flow.drawio

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

Элементы `mxCell` с `vertex="1"` задают три узла. Два ребра ссылаются на идентификаторы источника и цели, а `mxGeometry` задаёт позиции и размеры. Изменение видимой подписи отличается от изменения идентификатора, на который ссылается ребро.

Откройте файл в редакторе. Полный файл включает внешние элементы `mxfile` и `diagram`. При использовании **Extras → Edit Diagram** [документация редактора исходника](https://www.drawio.com/docs/manual/advanced/diagram-source-edit/) описывает `mxGraphModel` текущей страницы; не путайте этот фрагмент с оболочкой полного файла.

| Файл | Назначение |
| --- | --- |
| `request-flow.drawio` | Редактируемый исходник под контролем версий |
| `request-flow.svg` или `.png` | Результат для публикации/отрисовки; проверьте наличие встроенных данных |

После изменения снова откройте исходник, проверьте направление каждой стрелки и экспортируйте новое изображение. Проверяйте diff исходника и отрисовку: форматирование может скрыть небольшое изменение связей.

В примере локально проверяются структура XML, уникальность идентификаторов и ссылки соединений. Облачное хранение, действия в интерфейсе редактора и полный цикл экспорта не входят в проверки. Интеграции хранения выбирайте отдельно под свой аккаунт и редактор. [Руководство по поиску кода](/en/posts/2021-08-06-search-github/) показывает, как сузить набор изучаемых файлов репозитория.
