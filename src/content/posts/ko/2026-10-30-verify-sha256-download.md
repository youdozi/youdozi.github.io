---
language: "ko"
translationKey: "2026-10-30-verify-sha256-download"
routeSlug: "2026-10-30-verify-sha256-download"
kind: "post"
categories: ["linux"]
tags: ["python", "shellscript", "sha256"]
publishedAt: "2026-10-30T10:08:14.872354+00:00"
updatedAt: "2026-10-30T10:08:14.872354+00:00"
title: "Python으로 다운로드한 파일의 SHA-256 체크섬 검증하기"
description: "신뢰하는 SHA-256 기대값과 다운로드 파일을 비교합니다. 파일을 나누어 읽는 Python 코드로 일치·변조·읽기 오류와 종료 코드를 확인합니다."
reviewedAt: "2026-10-30"
reviewStatus: "revised"
reviewScope: "Official Python and Adoptium documentation; paired code, diagram and local fixtures checked. No signature verification or binary installation."
reviewSources: ["https://docs.python.org/3.11/library/hashlib.html", "https://adoptium.net/installation/archives", "https://adoptium.net/installation/gpg-verification"]
---
다운로드한 파일을 검증하려면 SHA-256 해시를 계산한 뒤 신뢰하는 배포자가 제공한 기대값과 비교합니다. Python의 [hashlib](https://docs.python.org/3.11/library/hashlib.html)로 바이너리 바이트를 나누어 읽으며 계산할 수 있습니다. 일치는 파일의 바이트를 해당 값과 대조한 결과이며, 배포자 신원이나 프로그램의 안전성을 증명하지 않습니다. Adoptium도 [서명 검증](https://adoptium.net/installation/gpg-verification)을 별도로 설명합니다.

## 어떤 체크섬과 비교해야 하나요?

다운로드한 릴리스·운영체제·CPU·압축 형식에 해당하는 체크섬을 사용합니다. [GitHub 릴리스 선택 예제](/ko/posts/2023-09-23-linux-shellscript-github-latest/)는 자산 URL을 고르고, [Temurin 메타데이터 예제](/ko/posts/2023-10-10-temurin-jdk21-delay/)는 체크섬 형식도 확인합니다. 두 예제 모두 다운로드한 파일의 해시를 계산하지는 않습니다. Adoptium의 [압축 파일 설치 안내](https://adoptium.net/installation/archives)에서 함께 제공되는 체크섬을 얻는 방법을 확인할 수 있습니다.

기대값은 배포자의 신뢰할 수 있는 배포 경로에서 얻습니다. 다운로드한 파일에서 해시를 구한 뒤 그 결과를 그대로 기대값으로 사용하면 잘못된 다운로드를 검출할 수 없습니다. 공격자가 파일과 게시된 체크섬을 모두 바꿀 수 있다면 두 값의 일치로 진위를 확인할 수 없습니다. 신뢰하는 배포자 키로 서명을 검증하는 작업은 이 예제의 범위 밖에 있는 별도 단계입니다.

## 파일 검증은 어떤 순서로 진행하나요?

![체크섬을 검증하고 파일 해시를 계산해 비교하는 흐름](/assets/diagrams/2026-10-30-verify-sha256-download-ko.svg)

기대값을 검증하고 내용이 바뀌지 않는 일반 파일을 바이너리 모드로 엽니다. EOF까지 나누어 읽으며 해시를 갱신한 뒤 비교합니다. 잘못된 입력이나 읽기 오류는 2, 불일치는 1, 일치한 경우에만 0을 반환합니다. 그림은 반복 읽기를 한 단계로 요약합니다. 검증 중에 파일을 바꾸거나 검증 후 사용하기 전에 다른 파일로 교체하지 마세요. 이 도구는 검증과 실행을 하나의 원자적 작업으로 묶지 않습니다.

## 추가 패키지 없이 검증기 실행하기

Python 3.11 이상을 사용하고 다음 코드를 `verify-sha256.py`로 저장합니다. 아래 명령은 POSIX 셸 기준입니다. 프로그램은 로컬 파일을 읽으며 다운로드·압축 해제·실행은 하지 않습니다. 심볼릭 링크가 일반 파일을 가리키면 그 파일을 읽습니다. 체크섬 목록 파일·파일명·URL 대신 대문자도 허용하는 64자리 16진수 값 하나를 받습니다.

### `verify-sha256.py`

```python
import hashlib
from pathlib import Path
import re
import sys


def main(argv):
    if len(argv) != 3 or not re.fullmatch(r"[0-9a-fA-F]{64}", argv[1]):
        print("usage: verify-sha256.py EXPECTED_SHA256 FILE", file=sys.stderr)
        return 2
    path = Path(argv[2])
    try:
        if not path.is_file():
            raise OSError("expected an existing regular file")
        digest = hashlib.sha256()
        with path.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as error:
        print(f"READ ERROR: {error}", file=sys.stderr)
        return 2
    if digest.hexdigest() != argv[1].lower():
        print("MISMATCH", file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
```

`rb`는 줄바꿈을 포함한 원래 바이트를 유지합니다. 한 번에 최대 1 MiB를 읽도록 요청하며 파일 전체를 메모리에 올리지 않습니다. 잘못된 체크섬은 경로를 열기 전에 거부합니다. 없는 경로·디렉터리·읽기 오류는 모두 종료 코드 2로 처리합니다. 이름 있는 파이프와 장치 파일은 일반 파일이라는 입력 범위에서 제외합니다.

## 일치와 변경된 파일 재현하기

새 빈 디렉터리에서 실행합니다. 모의 입력은 `sample.bin`에 세 바이트 `abc`, `changed.bin`에 `abcd`를 씁니다. 명령에 고정한 해시는 `abc`에만 해당하며 JDK 압축 파일의 체크섬이 아닙니다.

### `make-samples.py`

```python
from pathlib import Path

Path("sample.bin").write_bytes(b"abc")
Path("changed.bin").write_bytes(b"abcd")
```

```sh
python3 make-samples.py
expected='ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
python3 verify-sha256.py "$expected" sample.bin
python3 verify-sha256.py "$expected" changed.bin
printf 'exit=%s\n' "$?"
```

일치하는 파일은 `OK`를 출력합니다. 변경된 파일은 stderr에 `MISMATCH`를 출력하고, 마지막 명령은 `exit=1`을 출력합니다. `set -e`를 사용한다면 예상한 불일치를 `if` 등으로 명시적으로 처리해야 합니다. 그렇지 않으면 종료 코드를 출력하기 전에 셸이 멈출 수 있습니다.

| 종료 코드 | 의미 | 다음 행동 |
| --- | --- | --- |
| 0 | 주어진 기대값과 해시 일치 | 기대값을 신뢰할 수 있는 출처에서 얻었을 때만 다음 단계로 진행 |
| 1 | 해시 불일치 | 파일 사용을 멈추고 선택한 자산과 다운로드 확인 |
| 2 | 인자·체크섬 형식·파일 읽기 오류 | 입력이나 파일 접근 문제를 해결한 뒤 재시도 |

불일치만으로 파일 손상·잘못 고른 자산·악의적 교체 중 무엇이 원인인지 구분할 수는 없습니다. 이 검사는 서명 검증이나 악성 코드 검사를 제공하지 않습니다.
