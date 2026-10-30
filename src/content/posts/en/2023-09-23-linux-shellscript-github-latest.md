---
title: "GitHub Latest Release with curl and jq: Select One Download Asset"
language: "en"
translationKey: "2023-09-23-linux-shellscript-github-latest"
routeSlug: "2023-09-23-linux-shellscript-github-latest"
kind: "post"
publishedAt: "2026-10-27T02:36:39+00:00"
categories: ["linux"]
tags: ["linux", "bash", "shell script", "jq", "github latest release"]
updatedAt: "2026-10-30T10:10:46.396668+00:00"
reviewedAt: "2026-10-30"
reviewStatus: "revised"
reviewScope: "Primary documentation checked; published runnable example verified."
reviewSources: ["https://docs.github.com/en/rest/releases/releases#get-the-latest-release", "https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api", "https://curl.se/docs/manpage.html", "https://jqlang.org/manual/"]
description: "Use curl and jq to select one GitHub release asset by OS, CPU and format. Handle HTTP errors, invalid JSON and missing or duplicate matches."
---
Use `curl` to fetch a GitHub latest release and `jq` to select exactly one download asset for the required OS, CPU and format. The script below stops on HTTP errors, invalid JSON and missing or duplicate matches; it returns metadata without downloading the file.

The `releases/latest` endpoint does not calculate the numerically largest Git tag. The [release API documentation](https://docs.github.com/en/rest/releases/releases#get-the-latest-release) distinguishes ordinary tags, drafts, prereleases and published releases.

This example queries metadata for a Linux x64 HotSpot JDK tar.gz from the public `adoptium/temurin17-binaries` repository. It needs neither a token nor an actual file download. Omitting the repository argument uses this default; an explicitly empty argument is rejected.

## Processing flow

![Select one GitHub release asset workflow](/assets/diagrams/2023-09-23-linux-shellscript-github-latest-en.svg)

HTTP failure stops the script before JSON parsing. A valid release object must contain exactly one matching asset; selecting its URL does not verify the downloaded file.

## Separate HTTP failure from JSON selection failure

The script requires `curl`, `jq` and POSIX sh. Save it as `latest-release.sh`.

### `latest-release.sh`

```sh
#!/bin/sh
set -eu
if [ "$#" -gt 1 ]; then
    printf '%s\n' 'usage: latest-release.sh OWNER/REPO' >&2
    exit 2
fi
repo=${1-adoptium/temurin17-binaries}
case "$repo" in
    */*/*|/*|*/|*[!A-Za-z0-9_./-]*) printf '%s\n' 'usage: latest-release.sh OWNER/REPO' >&2; exit 2 ;;
esac
case "$repo" in
    */*) ;;
    *) printf '%s\n' 'usage: latest-release.sh OWNER/REPO' >&2; exit 2 ;;
esac
api=${GITHUB_API_URL:-https://api.github.com}
response=$(curl --fail --silent --show-error --location --max-time 20 \
    --header 'Accept: application/vnd.github+json' \
    --header 'X-GitHub-Api-Version: 2026-03-10' \
    "$api/repos/$repo/releases/latest") || exit 1
printf '%s' "$response" | jq --slurp --exit-status '
    if length != 1 or (.[0] | type) != "object" then
        error("expected one release object")
    else .[0] end
    | . as $release
    | if (.tag_name | type) != "string" or (.tag_name | length) == 0
         or (.assets | type) != "array" then
        error("missing release tag or assets")
      else . end
    | [.assets[] | select(.name | test("^OpenJDK17U-jdk_x64_linux_hotspot_.*\\.tar\\.gz$"))] as $assets
    | if ($assets | length) != 1 then
        error("expected exactly one Linux x64 JDK tar.gz asset")
      elif ($assets[0].browser_download_url | type) != "string"
           or ($assets[0].browser_download_url | length) == 0 then
        error("missing asset download URL")
      else {tag_name: $release.tag_name, download_url: $assets[0].browser_download_url} end
'
```

```sh
sh latest-release.sh adoptium/temurin17-binaries
```

A successful result is a JSON object with `tag_name` and `download_url`. Values depend on the release at request time. This sample is test data showing the shape, not a claim about the current latest release:

```json
{"tag_name":"jdk-17.0.8.1+1","download_url":"https://github.com/adoptium/temurin17-binaries/releases/download/example/OpenJDK17U-jdk_x64_linux_hotspot_example.tar.gz"}
```

`curl --fail` handles HTTP errors first. Capturing the response before parsing keeps a network failure from being hidden by the last command in a pipeline. [curl options](https://curl.se/docs/manpage.html).

`jq --slurp` reads the whole input into an array. Requiring exactly one JSON value also rejects an empty response. The filter then checks the release object, tag and assets array, and emits a result only when exactly one filename matches. [jq manual](https://jqlang.org/manual/).

## Outcomes to handle in automation

| Condition | Outcome |
| --- | --- |
| Valid response and one matching asset | JSON output, status 0. |
| HTTP403/404 or connection failure | Nonzero status. |
| Empty body or malformed JSON | Nonzero status. |
| Zero or multiple matching assets | Fail instead of choosing arbitrarily. |
| Invalid repository argument syntax | Usage message, status 2. |

If the HTTP request succeeds but no asset matches, inspect the release filenames before changing the `jq` filter: this example selects Java 17 for Linux x64, not every JDK package. For Java 21, use the [Temurin platform-metadata example](/en/posts/2023-10-10-temurin-jdk21-delay/). If repository or platform values come from YAML, [parse and validate the configuration as data](/en/posts/2021-07-27-parse-yaml/) before passing values to a command.

Local HTTP responses were used to check success, HTTP errors, invalid JSON, missing assets and duplicates. `GITHUB_API_URL` defaults to the public API and can be set to a test server implementing the same response contract.

Public-resource reads do not require authentication. If you extend this for authenticated requests, keep tokens out of source and shell-tracing logs. Check rate-limit response headers and [GitHub's rate-limit documentation](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api).

The script selects a URL; it does not verify the installation file's integrity. Installation automation still needs the provider's checksums/signatures and the target platform. Before passing a tag to the [numeric version comparator](/en/posts/2023-11-17-linux-shellscript-version-compare/), check that it satisfies that script's input contract.

After downloading the selected asset, [compare its SHA-256 checksum with a trusted expected value](/en/posts/2026-10-30-verify-sha256-download/). The checker reads local bytes; it does not download or authenticate the release.
