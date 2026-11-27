---
{
  "schemaVersion": 1,
  "state": "approved",
  "language": "de",
  "translationKey": "2026-11-27-docker-desktop-mac-disk-space",
  "routeSlug": "2026-11-27-docker-desktop-mac-disk-space",
  "kind": "post",
  "title": "Warum bleibt der freie Speicherplatz auf dem Mac nach dem Leeren des Docker-Caches gleich?",
  "description": "So lassen sich freigebbarer Build-Cache, für Docker.raw belegte Blöcke und freier Speicherplatz auf dem Mac getrennt messen.",
  "categories": [
    "tips"
  ],
  "tags": [
    "docker",
    "macos",
    "disk-usage"
  ],
  "sourcePath": "src/content/posts/en/2026-11-27-docker-desktop-mac-disk-space.md",
  "sourceSha256": "22ef396043237437e56056391cb42357c8f9bc5784eef9279e396ccf768d1ecd",
  "draftSha256": "985c7c9d9e3ede47af2fd30f528cfd65d02e0850a829770dc28f3ddccab4a94e",
  "manifestPath": ".pipeline/technical-translations/batch-21082/manifest.json",
  "manifestSha256": "389703b6649b08ce34f1e14aba7c22293869b1f99713c9f377cc209e3878817c",
  "publishedAt": "2026-11-27T01:18:38.817Z",
  "updatedAt": "2026-11-27T01:18:38.817Z",
  "approval": {
    "kind": "human",
    "reviewedBy": "youdozi",
    "pullRequest": 204,
    "approvedAt": "2026-11-27T01:18:38.817Z",
    "basis": "The user explicitly approved publication of this Docker Desktop disk article in Korean, English, Chinese, Japanese, German, French, Russian and Spanish."
  }
}
---

Docker ermittelt den freigebbaren Speicherplatz anhand der Images und Caches in seiner virtuellen Maschine. macOS misst den freien Platz auf dem Dateisystem des Hosts. Als belegt zählen dort auch die Blöcke, die dem Festplattenabbild `Docker.raw` der VM zugewiesen sind. Nutzt ein Image dieselbe Schicht wie der Build-Cache, kann sie nach dem Löschen des Cache-Eintrags auf der Festplatte bleiben. [Docker Desktop FAQ](https://docs.docker.com/desktop/troubleshoot-and-support/faqs/macfaqs/) · [Buildx du](https://docs.docker.com/reference/cli/docker/buildx/du/)

## Woher stammen die einzelnen Werte?

Bei laufendem Docker Desktop auf dem Mac zunächst den lokalen Kontext und den Builder prüfen. Ein Stern kennzeichnet in der Liste den ausgewählten Builder.

```sh
docker context show
docker buildx ls
docker system df -v
docker buildx du
df -k /
```

![Zuerst die Belegung der Engine ablesen, dann den Cache des ausgewählten Builders und schließlich den freien Platz im Dateisystem des Mac.](/assets/diagrams/technical/de-2026-11-27-docker-desktop-mac-disk-space.svg)

Der erste Speicherbericht erfasst Images, Container, Volumes und Build-Cache. Im zweiten bezeichnet `Reclaimable` den freigebbaren Cache des ausgewählten Builders. Beim letzten Befehl gibt `Available` den freien Platz im Root-Dateisystem des Mac in KiB an. [Docker system df](https://docs.docker.com/reference/cli/docker/system/df/)

## Wie viel Platz belegt Docker.raw tatsächlich?

Der Pfad zum Festplattenabbild steht in Docker Desktop unter Settings → Resources → Advanced. Den Beispielpfad an den tatsächlichen Speicherort anpassen. Bei `ls -klsh` zeigt die erste Spalte den belegten Platz in KiB und die Größenspalte die logische Dateigröße. Der letzte Befehl prüft das Dateisystem des Abbilds, auch wenn es auf einem anderen Volume liegt.

```sh
image="$HOME/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw"
ls -klsh "$image"
stat -f 'bytes=%z blocks=%b' "$image"
df -k "$image"
```

Bei einer reinen Leseabfrage auf einem lokalen Mac meldete `desktop-linux` 61,76 MB freigebbaren Build-Cache. Das Abbild hatte eine logische Größe von 63.999.836.160 Byte. Belegt waren 12.272.488 Blöcke zu je 512 Byte, also etwa 6,28 GB.

Wer nur den Build-Cache leeren möchte, prüft zuerst den ausgewählten Builder. Für einen Vergleich dieselben Befehle unmittelbar vor dem Aufräumen und einige Minuten danach ausführen. Bei dieser Abfrage wurde kein Cache gelöscht und kein Speichergewinn auf dem Mac gemessen. [Buildx prune](https://docs.docker.com/reference/cli/docker/buildx/prune/)

[Zum Weiterlesen · Eine Mac-Festplattenbereinigung mit du und df messen](../2026-11-27-mac-disk-cleanup-du-df/)
