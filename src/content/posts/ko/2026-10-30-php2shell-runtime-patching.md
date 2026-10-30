---
language: "ko"
translationKey: "2026-10-30-php2shell-runtime-patching"
routeSlug: "2026-10-30-php2shell-runtime-patching"
kind: "post"
categories: ["security"]
tags: ["php2shell", "php", "security"]
publishedAt: "2026-10-30T13:30:11.134567+00:00"
updatedAt: "2026-10-30T13:30:11.134567+00:00"
title: "PHP2Shell 대응: PHP 버전보다 실제 웹 워커와 패치를 확인하세요"
description: "CVE-2026-109618·109619의 수정 릴리스와 백포트를 구분하고 실제 웹 PHP 반영을 확인합니다. 세션 후속 공지와 Windows Brotli 재빌드도 별도로 다룹니다."
reviewedAt: "2026-10-30"
reviewStatus: "revised"
reviewScope: "Primary security advisories and API documentation; local read-only runtime evidence examples. No exploit reproduction, target discovery or production remediation."
reviewSources: ["https://github.com/php/php-src/security/advisories/GHSA-w8hw-w9fx-j79w", "https://github.com/php/php-src/security/advisories/GHSA-6wmf-4rv5-p3rp", "https://www.php.net/archive/2026.php", "https://ubuntu.com/security/notices/USN-8948-1", "https://www.php.net/manual/en/reserved.constants.php", "https://www.php.net/manual/en/function.ini-get.php"]
---
PHP2Shell 대응은 CMS나 플러그인 업데이트로 끝나지 않습니다. [CVE-2026-109618](https://github.com/php/php-src/security/advisories/GHSA-w8hw-w9fx-j79w)과 [CVE-2026-109619](https://github.com/php/php-src/security/advisories/GHSA-6wmf-4rv5-p3rp)를 수정한 PHP 빌드를 확보하고, 실제 웹 요청을 처리하는 모든 워커에 반영해야 합니다. 터미널의 `php -v`는 그 터미널이 고른 CLI만 보여줍니다.

## PHP2Shell은 어떤 문제인가요?

두 CVE는 PHP 엔진의 요청 처리 상태와 메모리 수명에 관한 결함입니다. 첫 번째는 메모리 부족으로 초기화가 중단된 뒤 정리 과정에서 잘못된 상태를 사용하는 문제이고, 두 번째는 요청 메모리를 해제한 뒤 남은 내부 상태를 같은 워커의 후속 요청이 사용하는 문제입니다. 조건에 따라 인증 없이 원격 코드를 실행할 수 있습니다.

[PHP 팀 공지](https://www.php.net/archive/2026.php)는 mod_php뿐 아니라 PHP-FPM·php-cgi·FrankenPHP·LiteSpeed 등 웹 요청을 처리하는 PHP를 조사 대상으로 명시합니다. 특정 SAPI를 사용한다는 이유만으로 제외하지 마세요. 반대로 취약 버전 문자열만 보고 해당 서비스에서 공격 경로가 재현됐다고 판단할 수도 없습니다.

## 어떤 버전과 비교해야 하나요?

아래는 2026년 10월 30일에 확인한 **원래 두 CVE의 업스트림 최초 수정 기준**입니다. 설치할 때는 같은 공급자의 최신 지원 릴리스와 후속 공지를 다시 확인하세요.

| PHP 계열 | 두 CVE 최초 수정 소스 릴리스 |
| --- | --- |
| 8.2 | 8.2.35 |
| 8.3 | 8.3.36 |
| 8.4 | 8.4.27 |
| 8.5 | 8.5.12 |

배포판 패키지는 짧은 PHP 버전 대신 전체 패키지 리비전과 공급자 공지를 대조합니다. 예를 들어 [Ubuntu USN-8948-1](https://ubuntu.com/security/notices/USN-8948-1)은 Ubuntu 24.04의 `php8.3-fpm` 수정 패키지를 `8.3.6-0ubuntu0.24.04.13`으로 명시합니다. 이 숫자를 업스트림 `8.3.36`과 비교하면 백포트를 잘못 판정하게 됩니다. 같은 버전 문자열을 붙인 임의의 커스텀 빌드까지 이 공지가 인증하지는 않습니다.

PHP 8.1 이하는 PHP 프로젝트의 지원이 종료된 계열입니다. 공급자의 지원·백포트 증거를 확인하거나 지원되는 계열로 이전하세요. 공개된 소스 패치가 있다는 사실과 현재 서버에 그 패치가 반영됐다는 사실은 다릅니다.

## CLI에서 수집할 수 있는 증거와 한계

![선택된 CLI의 실행 파일·버전·설정을 JSON으로 기록하고 웹 워커 판정은 별도로 남기는 흐름](/assets/diagrams/2026-10-30-php2shell-runtime-patching-ko.svg)

그림은 아래 수집기의 실행 흐름입니다. 웹 SAPI에서는 정보를 출력하지 않고 종료합니다. CLI에서는 실행 파일·버전·설정을 기록하지만 수정 여부를 자동 판정하지 않습니다. 서비스 식별·패치·재시작은 이 코드가 수행하지 않는 별도 운영 단계입니다.

PHP 8.2 이상에서 아래 파일을 문서 루트 밖의 새 디렉터리에 저장하세요. [PHP 상수](https://www.php.net/manual/en/reserved.constants.php)와 [ini_get](https://www.php.net/manual/en/function.ini-get.php)으로 현재 프로세스만 읽으며 요청 전송·설정 변경·세션 시작은 하지 않습니다. 공개 `phpinfo()` 페이지를 만들 필요가 없습니다.

### `runtime-evidence.php`

```php
<?php
if (PHP_SAPI !== 'cli') {
    http_response_code(404);
    exit;
}

$evidence = [
    'scope' => 'this-cli-process-only',
    'pid' => getmypid(),
    'version' => PHP_VERSION,
    'sapi' => PHP_SAPI,
    'binary' => PHP_BINARY,
    'loadedIni' => php_ini_loaded_file() ?: null,
    'uploadProgress' => ini_get('session.upload_progress.enabled'),
    'serializeHandler' => ini_get('session.serialize_handler'),
];
echo json_encode($evidence, JSON_PRETTY_PRINT | JSON_THROW_ON_ERROR), PHP_EOL;
```

```sh
php runtime-evidence.php
php -n -d session.upload_progress.enabled=0 runtime-evidence.php
```

첫 명령은 선택된 CLI의 설정을 읽습니다. 두 번째는 ini 파일을 읽지 않고 해당 CLI 실행에만 업로드 진행 설정을 끄는 실험입니다. **웹 서버 설정을 바꾸거나 웹 워커의 유효 설정을 확인하는 명령이 아닙니다.**

로컬에서는 격리된 PHP CLI 컨테이너에서 JSON 출력과 `sapi`가 `cli`인 것을 확인했습니다. 두 번째 명령은 `loadedIni`가 `null`, `uploadProgress`가 문자열 `"0"`인 결과를 반환했습니다. 경로·PID·버전·기본 설정은 실행 환경에 따라 달라집니다. 이 결과는 운영 서비스의 패치나 취약점 악용을 검증한 기록이 아닙니다.

## 패치 설치와 실행 반영을 나눠 확인하세요

1. 웹 서버의 upstream·FastCGI·모듈 설정에서 실제 PHP 실행 파일, 풀, 컨테이너와 복제본을 식별합니다. 호스트 CLI와 웹 런타임의 설치 경로가 같다고 가정하지 않습니다.
2. 그 런타임의 공급자·전체 패키지 리비전 또는 이미지 digest를 공지와 대조합니다. 직접 빌드라면 수정 커밋과 빌드 산출물의 연결을 확보합니다.
3. 호환성을 확인한 수정 빌드를 배포하고, 해당 풀·서비스의 워커 또는 컨테이너를 교체합니다. 다른 서비스를 사용하는 공유 런타임이면 변경 범위부터 확인합니다.
4. 모든 대상에서 새 프로세스·빌드의 연결을 확인하고 정상 페이지, 로그인·세션, 업로드와 오류율을 점검합니다. 일부 노드만 바뀌었거나 실행 반영 증거가 없으면 완료로 집계하지 않습니다.

내부 자산 기록에서는 ‘수정 빌드 확인’과 ‘실행 반영 확인’을 구분하면 빠뜨린 워커를 찾기 쉽습니다. 크래시가 있었다고 침해를 확정하거나, 오류 로그가 없다고 침해를 배제하지 마세요. 침해가 의심되면 증거 보존과 사고 조사를 패치 작업과 별도로 진행합니다.

## 세션 후속 공지와 Windows 재빌드도 구분하세요

[10월 23일 PHP 후속 공지](https://www.php.net/archive/2026.php)는 **CVE-2026-115560**을 별도로 다룹니다. 설정의 `session.serialize_handler`가 `php_binary` 또는 `php_serialize`였다가 코드에서 `php`로 바뀌고 `session_start()`를 호출하며 업로드 진행 기능이 켜진 조합입니다. 공지는 다음 정기 수정 전까지 `session.upload_progress.enabled=0`을 제안합니다. 이 설정으로 원래 두 CVE 전체가 해결됐다고 판단해서는 안 됩니다. 실제 웹 SAPI의 유효 설정과 기능 영향을 확인하세요.

[10월 26일 Windows 공지](https://www.php.net/archive/2026.php)는 Brotli의 **CVE-2026-111497**을 반영한 `8.5.12-1`·`8.4.27-1`·`8.3.36-1`·`8.2.35-1` 패키지를 안내합니다. PHP 소스 버전은 같고 패키지 의존성이 바뀐 재빌드이므로 `PHP_VERSION`만으로 구분할 수 없습니다. cURL의 자동 응답 압축 해제를 사용하는 Windows 배포는 이 패키지 수정도 확인해야 합니다. 같은 Brotli CVE를 Node.js에서 다루는 방법은 [Node2Shell 대응 글](/ko/posts/2026-10-30-node2shell-brotli-runtime-patching/)에서 이어집니다.
