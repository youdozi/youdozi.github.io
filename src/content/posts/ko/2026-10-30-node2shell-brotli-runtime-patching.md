---
language: "ko"
translationKey: "2026-10-30-node2shell-brotli-runtime-patching"
routeSlug: "2026-10-30-node2shell-brotli-runtime-patching"
kind: "post"
categories: ["security"]
tags: ["node2shell", "nodejs", "brotli", "security"]
publishedAt: "2026-10-30T13:30:11.134567+00:00"
updatedAt: "2026-10-30T13:30:11.134567+00:00"
title: "Node2Shell 대응: Brotli 해제 경로와 실행 중인 Node.js를 확인하세요"
description: "CVE-2026-111497의 Node.js 수정 버전, Brotli 입력 경로, 버전 문자열의 한계를 설명합니다. 런타임 증거 수집과 모든 워커·복제본 반영을 구분합니다."
reviewedAt: "2026-10-30"
reviewStatus: "revised"
reviewScope: "Primary security advisories and API documentation; local read-only runtime evidence examples. No exploit reproduction, target discovery or production remediation."
reviewSources: ["https://nodejs.org/en/blog/vulnerability/october-2026-security-releases", "https://nodejs.org/en/blog/release/v22.23.4", "https://nodejs.org/en/blog/release/v24.22.1", "https://nodejs.org/en/blog/release/v26.12.1", "https://github.com/nodejs/node/blob/v24.22.1/deps/brotli/c/common/version.h", "https://expressjs.com/en/resources/middleware/body-parser/", "https://nodejs.org/docs/latest-v24.x/api/process.html"]
---
Node2Shell 대응의 핵심은 수정된 Node.js 런타임으로 교체하고, 신뢰할 수 없는 Brotli 데이터를 해제하는 모든 워커에 반영했는지 확인하는 것입니다. [Node.js 보안 공지](https://nodejs.org/en/blog/vulnerability/october-2026-security-releases)가 설명하는 **CVE-2026-111497**은 내장 Brotli 디코더의 범위 밖 쓰기 결함입니다. npm 패키지 업데이트와 런타임 교체는 서로 다른 작업입니다.

## Brotli를 사용하면 모두 같은 위험인가요?

문제는 압축된 입력을 **해제**하는 경로입니다. 공격자가 공급한 잘못된 Brotli 데이터를 `node:zlib`가 처리하면 프로세스 메모리가 손상되어 크래시·메모리 노출·원격 코드 실행으로 이어질 수 있습니다. 응답을 Brotli로 압축해 내보내거나 HTTP/2를 켰다는 사실만으로 그 경로가 확인되는 것은 아닙니다. Node.js 프로젝트는 해당 문제를 High로 분류합니다.

요청 본문뿐 아니라 외부 HTTP 응답의 자동 해제, 업로드·파일 처리, 큐 작업도 추적하세요. 예를 들어 [body-parser 공식 문서](https://expressjs.com/en/resources/middleware/body-parser/)는 Brotli 자동 해제를 설명합니다. 설치된 미들웨어 버전과 옵션을 확인해야 하며, 직접 작성한 코드에서 `brotliDecompress`를 찾지 못했다는 이유만으로 비노출이라고 판단해서는 안 됩니다. 외부에 열린 수신 포트가 없어도 백그라운드 작업이 외부 데이터를 해제할 수 있습니다.

## 어떤 Node.js 릴리스가 수정 기준인가요?

2026년 10월 30일에 확인한 아래 표는 이 CVE가 반영된 공식 보안 릴리스입니다. 최신 권장 버전을 고정한 표가 아니므로 배포 시 같은 공급자의 지원 릴리스와 후속 공지를 확인하세요.

| Node.js 계열 | 공식 수정 릴리스 |
| --- | --- |
| 22.x | [22.23.4](https://nodejs.org/en/blog/release/v22.23.4) |
| 24.x | [24.22.1](https://nodejs.org/en/blog/release/v24.22.1) |
| 26.x | [26.12.1](https://nodejs.org/en/blog/release/v26.12.1) |

배포판·제품 내장·직접 빌드에는 공급자의 전체 패키지 리비전과 수정 증거를 적용합니다. 다른 메이저 버전에 이 숫자 기준을 전용하지 마세요. Node.js 공지는 지원 종료 계열도 영향을 받는 것으로 취급하므로, 표에 없다는 이유로 안전하다고 볼 수 없습니다.

특히 `process.versions.brotli`만으로 판정하면 안 됩니다. 수정된 [Node.js 24.22.1의 Brotli 버전 원본](https://github.com/nodejs/node/blob/v24.22.1/deps/brotli/c/common/version.h)도 `1.2.0`을 표시합니다. [릴리스 기록](https://nodejs.org/en/blog/release/v24.22.1)은 수정 커밋의 cherry-pick을 명시합니다. 라이브러리 이름표보다 수정된 런타임 아티팩트의 출처가 중요합니다.

## 프로세스 증거를 직접 기록하기

![실행 중인 예제 프로세스의 PID·실행 경로·Node 버전·Brotli 이름표를 JSON으로 기록하는 흐름](/assets/diagrams/2026-10-30-node2shell-brotli-runtime-patching-ko.svg)

그림은 아래 예제 애플리케이션의 시작 흐름입니다. 같은 프로세스에서 정보를 읽어 JSON으로 출력하며, 버전 비교·서비스 탐색·패치 판정을 수행하지 않습니다. 임의의 CLI에서 새로 실행한 결과를 기존 서비스의 증거로 대신하지 마세요.

Node.js 22 이상에서 새 디렉터리에 다음 두 파일을 저장합니다. [process 공식 문서](https://nodejs.org/docs/latest-v24.x/api/process.html)의 읽기 전용 정보를 사용하며 네트워크 요청·압축 해제·환경 변수 출력은 하지 않습니다.

### `runtime-evidence.mjs`

```javascript
export function runtimeEvidence() {
  return {
    scope: 'this-process-only',
    pid: process.pid,
    executable: process.execPath,
    node: process.version,
    brotliLabel: process.versions.brotli ?? null,
    platform: process.platform,
    arch: process.arch,
  };
}
```

### `app.mjs`

```javascript
import {runtimeEvidence} from './runtime-evidence.mjs';

console.log(JSON.stringify(runtimeEvidence(), null, 2));
```

```sh
node app.mjs
```

로컬에서는 공식 Node.js 24.22.1 컨테이너에서 실행해 `node`가 `v24.22.1`, `brotliLabel`이 `1.2.0`인 JSON을 확인했습니다. PID·경로·OS·아키텍처는 환경에 따라 달라집니다. 이 예제는 수정된 빌드도 기존 Brotli 이름표를 유지할 수 있음을 보여주며, 취약점 악용이나 운영 배포를 시험하지 않습니다.

실제 서비스에 적용한다면 배포 절차를 거쳐 시작 코드에서 동일 정보를 제한된 운영 로그에 기록하고, 서비스 관리자·프로세스·이미지 digest와 연결하세요. 경로와 PID는 공개 HTTP 응답에 노출할 정보가 아닙니다. 별도 진단 프로세스를 띄웠다는 사실만으로 기존 워커의 교체를 확인할 수는 없습니다.

## 패키지 설치 후 무엇을 더 확인하나요?

1. 서비스별 Node.js 실행 파일, 공급자, 전체 패키지 버전 또는 이미지 digest, 프로세스와 워커·복제본 목록을 기록합니다. 호스트 `node -v`나 Dockerfile 태그만으로 실행 중인 컨테이너를 판정하지 않습니다.
2. 입력이 어느 라이브러리를 거쳐 Brotli 디코더에 도달하는지 확인합니다. 런타임 수정 상태와 입력 노출 상태는 별도로 남깁니다. 조사 범위에서 해제 경로를 못 찾았다고 미수정 런타임이 수정된 것은 아닙니다.
3. 호환성을 확인한 수정 런타임을 신뢰하는 채널에서 확보합니다. 컨테이너는 이미지를 다시 만들고 롤아웃하며, 프로세스 관리자·매니지드 플랫폼도 실제 사용하는 실행기를 교체합니다. 시스템 Brotli 라이브러리 교체가 내장 사본까지 바꾼다고 가정하지 않습니다.
4. 모든 워커·복제본의 새 실행 증거를 확인한 뒤 정상 API 호출·외부 응답 처리·백그라운드 작업과 오류율을 점검합니다. 설치 파일만 바뀌었거나 일부 복제본이 남아 있으면 실행 반영 완료가 아닙니다.

패치가 지연되면 실제 데이터 경로에서 신뢰할 수 없는 Brotli 해제를 거부하거나 우회하는 임시 조치를 검토합니다. `Accept-Encoding`에서 `br`을 빼는 것만으로 모든 입력 경로가 차단되지는 않습니다. 정상 입력의 압축·해제 성공과 `npm audit` 통과도 해당 CVE의 수정 증거를 대신하지 않습니다.

## PHP2Shell과 같은 문제인가요?

별개의 결함입니다. PHP2Shell의 두 CVE는 PHP 엔진의 요청 상태 문제이고, Node2Shell은 Brotli 디코더 문제입니다. 다만 같은 Brotli CVE가 다른 제품에 포함될 수 있으므로 제품별 공지를 확인해야 합니다. PHP Windows 패키지의 Brotli 재빌드와 PHP 엔진 패치를 구분하는 방법은 [PHP2Shell 대응 글](/ko/posts/2026-10-30-php2shell-runtime-patching/)에서 설명합니다.

크래시만으로 침해를 단정하거나 흔적이 없다는 이유로 침해를 배제하지 않습니다. 침해 정황이 있으면 제한된 위치에 증거를 보존하고 사고 조사·신뢰 가능한 재구축을 패치와 별도로 진행하세요.
