---
language: "de"
translationKey: "2021-07-23-app-diagrams.net"
title: "Editierbare draw.io-Quellen neben geteilten Diagrammen aufbewahren"
description: "Ein kleines unkomprimiertes draw.io-XML-Diagramm erstellen, die .drawio-Quelle behalten und editierbare Daten von SVG-/PNG-Bildern zur Weitergabe unterscheiden."
state: "draft"
sourcePath: "src/content/posts/en/2021-07-23-app-diagrams.net.md"
sourceSha256: "994c0cd18640921c0e130d9310adace919b39b5be0e5a2b54b5cee9772bdd8c0"
---
Bewahren Sie eine editierbare Diagrammquelle neben dem veröffentlichten Bild auf. Das Bild zeigt das aktuelle Ergebnis; die Quelle erhält die für die nächste Änderung nötigen Formen, Verbindungen und Beschriftungen.

Der [draw.io-Formatleitfaden](https://www.drawio.com/docs/manual/editor/save-file-formats/) empfiehlt `.drawio`, ein unkomprimiertes XML-Format. Auch SVG und PNG können Diagrammdaten enthalten. Die Bildendung allein sagt daher nicht, ob die Datei editierbar ist. Behalten Sie die ausdrückliche Quelldatei auch bei einem Export mit eingebetteten Daten.

## Der Beispielablauf

![Die Abbildung zeigt dieselben drei Knoten und zwei gerichteten Verbindungen wie das XML darunter. Sie wurde für den Artikel gerendert und ist kein Editor-Screenshot oder -Export.](2021-07-23-app-diagrams.net.svg)

Die Abbildung zeigt dieselben drei Knoten und zwei gerichteten Verbindungen wie das XML darunter. Sie wurde für den Artikel gerendert und ist kein Editor-Screenshot oder -Export.

## Als request-flow.drawio speichern

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

`mxCell`-Elemente mit `vertex="1"` definieren die drei Knoten. Die beiden Kanten verweisen auf Quell- und Ziel-IDs, während `mxGeometry` Positionen und Größen liefert. Eine sichtbare Beschriftung zu ändern ist etwas anderes als die ID zu ändern, auf die eine Kante verweist.

Öffnen Sie die Datei im Editor. Die vollständige Datei umfasst die äußeren Elemente `mxfile` und `diagram`. Bei **Extras → Edit Diagram** beschreibt die [Dokumentation des Quelleditors](https://www.drawio.com/docs/manual/advanced/diagram-source-edit/) hingegen das `mxGraphModel` der aktuellen Seite. Verwechseln Sie das Seitenfragment nicht mit der vollständigen Dateihülle.

| Datei | Zweck |
| --- | --- |
| `request-flow.drawio` | Editierbare Quelle unter Versionskontrolle |
| `request-flow.svg` oder `.png` | Ausgabe zur Weitergabe/Darstellung; eingebettete Diagrammdaten prüfen |

Öffnen Sie nach einer Änderung die Quelle erneut, prüfen Sie jede Pfeilrichtung und exportieren Sie ein neues Bild zur Weitergabe. Prüfen Sie Quelldiff und Darstellung: Formatierungsänderungen können eine kleine Beziehungsänderung verdecken.

XML-Struktur, eindeutige IDs und Verbindungsreferenzen werden im Beispiel lokal geprüft. Cloudspeicherung, Editor-UI und Export-Rundläufe liegen außerhalb dieser Prüfungen. Wählen Sie Speicherintegrationen passend zu Konto und Editor separat. Der [Codesuchleitfaden](/en/posts/2021-08-06-search-github/) zeigt, wie Sie untersuchte Dateien in einem Repository eingrenzen.
