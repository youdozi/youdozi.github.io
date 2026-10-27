---
language: en
translationKey: 2023-10-10-temurin-jdk21-delay
routeSlug: 2023-10-10-temurin-jdk21-delay
kind: post
categories:
  - jdk
tags:
  - jdk21
  - adoptium
  - temurin
publishedAt: "2026-10-27T03:19:18+00:00"
title: "Temurin 21 Release Delay: History and How to Check JDK Binaries"
updatedAt: 2026-10-27T05:23:47.316+00:00
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Official sources checked; runnable examples checked separately from
  migration and production claims.
reviewSources:
  - https://adoptium.net/news/2023/09/temurin21-delay
  - https://github.com/adoptium/temurin21-binaries/releases/tag/jdk-21%2B35
  - https://api.github.com/repos/adoptium/temurin21-binaries/releases/tags/jdk-21%2B35
  - https://api.adoptium.net/q/swagger-ui/
description: Distinguish the 2023 Temurin 21 TCK delay from release publication,
  then inspect Java 21 platform, package type, and checksum metadata with the
  Adoptium API.
---
The initial Temurin 21 delay in 2023 was separate from the OpenJDK 21 release. Adoptium attributed the delay to review of the TCK agreement, and later distinguished receiving the TCK from publishing release binaries. This historical delay does not mean Temurin 21 is still awaiting release.

## Processing flow

![Validate binary metadata workflow](/assets/diagrams/2023-10-10-temurin-jdk21-delay-en.svg)

This is the metadata-selection example, not an installation flow. It checks the platform, Java major version, checksum syntax and URL location without downloading or hashing the archive.

## Separate announcement and publication dates

[Adoptium published its delay notice](https://adoptium.net/news/2023/09/temurin21-delay) on September 28, 2023. Its **October 9 update** reports receiving the TCK and proceeding with testing. Do not date that update October 10 or equate starting tests with completing releases for every platform.

Separately, the [GitHub metadata](https://api.github.com/repos/adoptium/temurin21-binaries/releases/tags/jdk-21%2B35) for the [`jdk-21+35` release](https://github.com/adoptium/temurin21-binaries/releases/tag/jdk-21%2B35) returns `2023-10-10T13:55:52Z` as `published_at`. This timestamps publication of that release, not completion of every asset upload. Early Access builds and official releases also need to be distinguished.

## Query a Java 21 binary available now

Specify Java 21, Linux, x64, HotSpot, and JDK in the [Adoptium API](https://api.adoptium.net/q/swagger-ui/). Change the filters together if your OS or CPU differs. This example fetches metadata only; it neither downloads nor installs a JDK binary. It requires Python 3 and curl.

```sh
curl --fail --show-error --silent --location \
  'https://api.adoptium.net/v3/assets/latest/21/hotspot?architecture=x64&image_type=jdk&os=linux&vendor=eclipse' \
  --output assets.json &&
  python3 select-temurin.py assets.json
```

### `select-temurin.py`

```python
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

if len(sys.argv) != 2:
    sys.exit("usage: select-temurin.py ASSETS_JSON")
try:
    assets = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    if not isinstance(assets, list) or len(assets) != 1:
        raise ValueError("expected exactly one asset")
    asset = assets[0]
    binary = asset["binary"]
    if (binary["os"], binary["architecture"], binary["image_type"], binary["jvm_impl"]) != ("linux", "x64", "jdk", "hotspot"):
        raise ValueError("unexpected platform or image type")
    if asset["version"]["major"] != 21:
        raise ValueError("expected Java 21")
    package = binary["package"]
    checksum = package["checksum"]
    if not isinstance(checksum, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", checksum):
        raise ValueError("invalid SHA-256 metadata")
    link = package["link"]
    if not isinstance(link, str):
        raise ValueError("package URL must be a string")
    url = urlparse(link)
    if url.scheme != "https" or url.netloc != "github.com" or not url.path.startswith("/adoptium/temurin21-binaries/releases/download/"):
        raise ValueError("unexpected package URL")
    result = {"version": asset["version"]["semver"], "name": package["name"], "url": link, "sha256": checksum}
except (OSError, UnicodeError, ValueError, KeyError, TypeError) as error:
    print(f"invalid release metadata: {error}", file=sys.stderr)
    sys.exit(2)
print(json.dumps(result, indent=2))
```

The selector prints a result only for exactly one asset with the expected Java major version, platform, image type, distribution URL, and checksum format. Missing fields, multiple assets, and invalid JSON fail. The `&&` prevents the selector from running if `curl` fails.

`latest/21` means the Java 21 update returned at query time. It neither pins the first `21+35` release nor selects the newest JDK major version. Record and pin the returned version, URL, and SHA-256 for repeatable deployments.

This validates the checksum's **format**, not the integrity of a downloaded file. If you download the archive separately, calculate its SHA-256 and compare it with the metadata before deciding to extract or install it. Checking agreement between an actual binary and the published checksum is outside this metadata example's execution scope.

For another asset-selection example, see [querying GitHub releases and assets](/en/posts/2023-09-23-linux-shellscript-github-latest/). For feature stability, see [JDK 21 final and preview features](/en/posts/2023-09-20-jdk-21-release/).
