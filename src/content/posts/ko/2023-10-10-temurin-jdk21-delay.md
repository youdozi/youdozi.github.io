---
title: Temurin 21 출시 지연 기록과 현재 JDK 바이너리 확인 방법
language: ko
translationKey: 2023-10-10-temurin-jdk21-delay
routeSlug: 2023-10-10-temurin-jdk21-delay
kind: post
publishedAt: 2023-10-11T15:00:00.000Z
categories:
  - jdk
tags:
  - jdk21
  - adoptium
  - temurin
legacyUrl: /jdk/temurin-jdk21-delay/
legacySource: _posts/jdk/temurin-jdk21-delay/2023-10-10-temurin-jdk21-delay.markdown
updatedAt: 2026-10-27T03:08:04.102Z
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Official sources checked; runnable examples checked separately from
  migration and production claims.
archiveBodySha256: 5519b6e2fa9b53ce085d356b1235f1b40a19952b3d869195f85000d800aa25d3
reviewSources:
  - https://adoptium.net/news/2023/09/temurin21-delay
  - https://github.com/adoptium/temurin21-binaries/releases/tag/jdk-21%2B35
  - https://api.github.com/repos/adoptium/temurin21-binaries/releases/tags/jdk-21%2B35
  - https://api.adoptium.net/q/swagger-ui/
description: 2023년 Temurin 21의 TCK 관련 지연과 공개 시점을 구분하고, Adoptium API에서 플랫폼·JDK
  유형·체크섬 메타데이터를 확인합니다.
---
Temurin 21의 2023년 첫 출시 지연은 OpenJDK 21 자체의 출시 지연과 다릅니다. Adoptium은 TCK 계약 검토로 공식 배포가 늦어졌다고 설명했고, 이후 TCK 수령과 실제 릴리스 공개를 별도 단계로 알렸습니다. 지금도 Temurin 21 배포가 지연 중이라는 뜻은 아닙니다.

## 공지와 릴리스 날짜 구분하기

[Adoptium의 지연 공지](https://adoptium.net/news/2023/09/temurin21-delay)는 2023년 9월 28일 게시됐습니다. **10월 9일 업데이트**는 TCK를 받았으며 테스트를 진행한다고 설명합니다. 이 업데이트 날짜를 10월 10일로 적거나, 테스트 시작을 모든 플랫폼의 공개 완료로 해석하면 안 됩니다.

한편 [`jdk-21+35` 릴리스](https://github.com/adoptium/temurin21-binaries/releases/tag/jdk-21%2B35)의 [GitHub 메타데이터](https://api.github.com/repos/adoptium/temurin21-binaries/releases/tags/jdk-21%2B35)는 `published_at`을 `2023-10-10T13:55:52Z`로 반환합니다. 이것은 그 릴리스의 공개 시각이며 모든 자산의 업로드 완료 시각을 뜻하지 않습니다. 당시 Early Access 빌드와 정식 배포도 구분해야 합니다.

## 지금 사용할 Java 21 바이너리 조회

[Adoptium API](https://api.adoptium.net/q/swagger-ui/)에 Java 21, Linux, x64, HotSpot, JDK 조건을 명시합니다. 다른 OS나 CPU를 쓰면 조건을 함께 바꿔야 합니다. 아래 코드는 메타데이터만 조회하며 바이너리를 내려받거나 설치하지 않습니다. Python 3과 curl이 필요합니다.

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

이 선택기는 자산이 정확히 하나이고 Java 주 버전·플랫폼·JDK 유형·배포 URL·체크섬 형식이 맞을 때만 결과를 출력합니다. 누락·복수 자산·잘못된 JSON은 실패로 처리합니다. `&&`로 연결했으므로 `curl`이 실패하면 선택기를 실행하지 않습니다.

`latest/21`은 조회 시점의 Java 21 업데이트를 뜻합니다. 최초의 `21+35`를 고정 조회하거나 전체 JDK 중 최신 주 버전을 고르는 명령이 아닙니다. 반복 가능한 배포에는 조회 결과의 버전·URL·SHA-256을 고정해 기록해야 합니다.

여기서 확인하는 것은 체크섬의 **형식**입니다. 실제 파일의 무결성을 검증한 것은 아닙니다. 파일을 별도로 내려받았다면 SHA-256을 계산해 메타데이터 값과 비교한 뒤 압축 해제·설치를 결정하세요. API에 게시된 값과 파일이 일치하는지도 이번 메타데이터 예제의 실행 범위에는 포함되지 않습니다.

릴리스 자산 선택의 다른 예제는 [GitHub 릴리스와 자산 조회](/ko/posts/2023-09-23-linux-shellscript-github-latest/)에서, Java 21 기능의 확정 여부는 [JDK 21 정식 기능과 Preview](/ko/posts/2023-09-20-jdk-21-release/)에서 확인할 수 있습니다.
