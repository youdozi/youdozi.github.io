# Bilingual Dev Content Pipeline

개발 RSS에서 기사를 선별하고 영문·한국어 요약과 인용 근거를 검증한 후 Astro용 JSON을 생성합니다. 원문 일치 확인은 기사 자체의 사실 보증과 다릅니다.

## 실행

```sh
python3 scripts/generate_digest.py --dry-run --check-links --max-items 2
python3 scripts/generate_digest.py --check-links
```

`GEMINI_API_KEY`는 환경 변수로 전달합니다. 키를 명령 인자나 파일에 넣지 않습니다. 기본 모델은 기존 `gemini-3.5-flash-lite`를 유지하며 `GEMINI_MODEL`로 변경할 수 있습니다. 모델 접근 권한과 API 프로젝트의 과금 여부는 별도로 관리해야 합니다. 자동 모델 변경과 재시도는 없습니다.

## 수집과 게시 조건

1. GitHub Changelog, InfoQ, JetBrains, Spring, Cloudflare RSS/Atom을 수집합니다.
2. 최근 7일, 미래가 아닌 기사 중 점수 6 이상, 출처당 최대 3개, 전체 최대 6개를 선별합니다. 기존 RSS 완성 문장 필터를 유지합니다.
3. 중복 URL은 `.pipeline/content_state.json`, 원본 `_posts/dev/digest/`, 신규 JSON 이력을 모두 확인합니다. 손상된 이력은 실행 실패입니다.
4. HTTPS 승인 호스트에서 본문을 추출합니다. 문서당 다운로드 2MB, 본문 400~18,000자 제한을 유지합니다. 원문 접근 실패나 길이 초과는 기사 보류입니다. RSS 요약으로 대체하지 않습니다.
5. 기사당 첫 AI 호출에서 영문·한국어 제목과 각 언어 2~3개 문장 및 원문 인용 근거를 생성합니다. 원문은 비신뢰 데이터로 취급합니다.
6. 각 인용문의 실제 존재, 문서 ID, 한국어 여부, 완성 문장, 요약 길이를 검사합니다. 한국어 총 80~420자, 영어 총 80~800자입니다.
7. 두 번째 호출에서 두 언어의 제목·주장·번역 일치·수치·날짜·출시 상태·벤치마크 조건을 함께 대조합니다. 보안·릴리스·지원 종료 주장은 공식 출처 인용을 요구합니다.
8. 한 언어라도 검증에 실패하면 해당 기사의 두 버전을 함께 보류합니다. 검증된 기사 쌍만 발행하므로 두 언어의 기사 구성이 같습니다. 모든 기사가 보류되면 실행 실패입니다.
9. `--check-links`는 원문 URL의 HTTP 200, HTML, 최종 승인 호스트를 검사합니다. 실패하면 저장·커밋하지 않습니다.
10. 검증된 `src/content/digests/YYYY-MM-DD.json`과 상태를 저장합니다. JSON에는 요약·짧은 인용문·출처 URL·본문 SHA-256·모델·검증 상태를 포함하고 본문 전체나 API 키를 포함하지 않습니다.

기사당 최대 2회, 실행당 최대 12회 AI 호출입니다. preview 최대 2개는 최대 4회입니다. JSON은 Astro 컴포넌트에서 텍스트로 출력하며 외부 문자열을 Markdown/Liquid/HTML 템플릿으로 실행하지 않습니다. 인용문은 사용자가 원문 근거를 확인할 수 있도록 펼침 영역에 표시합니다.

동일 모델의 별도 호출에도 공통 오류가 남을 수 있으므로 검증 상태는 `source_consistency_checked`입니다. “사실 검증 완료”라고 표시하지 않습니다.

## 옵션

- `--repo-root`: 저장소 루트. 기본 `.`
- `--dry-run`: 검증 결과 출력. 콘텐츠·상태 저장 없음. AI 호출 비용은 발생할 수 있습니다.
- `--force`: 오늘 JSON이 있어도 새 미게시 후보로 덮어쓰기. 사용한 URL은 상태에 남습니다.
- `--max-items`: 1~6. 기본 6.
- `--days-back`: 최신성 범위. 기본 7.
- `--min-score`: 최소 점수. 기본 6.
- `--max-per-source`: 출처당 최대 개수. 기본 3.
- `--fixtures-dir`: 로컬 RSS/Atom fixture 사용. AI 호출은 여전히 필요하며 오프라인 테스트에서는 mock으로 대체합니다.
- `--check-links`: 실제 원문 링크 접속 검사.
- `--github-output`: `generated`와 실제 생성한 `digest_path` 출력.

오늘 파일이 있거나 적합한 새 기사가 없으면 정상적으로 건너뜁니다. preview와 건너뛰기는 `generated=false`를 출력합니다. API 인증·한도·네트워크·JSON 오류는 실행 전체 실패입니다. 일부 RSS 실패는 경고, 전체 RSS 실패는 실행 실패입니다.

## Actions와 배포

매일 한국 시간 07:00(`0 22 * * *`, UTC)에 실행합니다. 수동 실행의 `preview=true`가 기본이며 `--dry-run --force --max-items 2`로 AI 연결을 검사합니다. 검토용 Draft PR 생성에는 `preview=false`를 사용합니다. 어느 모드도 자동 게시하지 않습니다.

생성 후 Astro 타입·스키마 검사와 빌드·내부 링크 검사가 모두 통과하면 JSON과 중복 방지 상태를 `content/digest-review-*` 브랜치에 커밋합니다. 재사용 사이트 워크플로에 정확한 생성 커밋 SHA를 넘겨 전체 검사를 수행하되 배포하지 않습니다. 검사 성공 후에만 Draft PR을 엽니다. PR 본문에는 두 언어의 제목·요약, 문장별 인용 근거, 원문 링크와 검토 체크리스트가 표시됩니다. 생성 브랜치는 공개 저장소에서 볼 수 있지만 운영 사이트·RSS·사이트맵에는 포함되지 않습니다.

검토 방법:

1. GitHub의 Pull requests에서 `검토 요청: 영문·한국어 개발 뉴스 초안` Draft PR을 엽니다.
2. 원문을 직접 확인하고 수치·날짜·출시 상태·과장·번역 일치를 검토합니다. 자동 검사 성공은 사람의 확인을 대신하지 않습니다.
3. 수정이 필요하면 Files changed에서 `src/content/digests/YYYY-MM-DD.json`을 수정합니다. 각 언어의 `summary`는 해당 `claims[].text`를 공백으로 연결한 값과 같아야 합니다. 주장 변경 시 인용 근거도 함께 검토합니다. 최초 PR 본문은 자동 갱신되지 않으므로 수정 후에는 Files changed가 기준입니다.
4. 화면으로 확인하려면 PR 브랜치를 체크아웃하고 `npm ci`, `npm run dev`로 해당 날짜의 `/en/digest/YYYY-MM-DD/`와 `/ko/digest/YYYY-MM-DD/`를 확인합니다. Actions의 `site-build-output` 산출물도 내려받을 수 있습니다.
5. 검사 결과와 내용을 확인한 뒤 **Ready for review → Merge pull request**를 누릅니다. 병합이 게시 승인입니다. 사람이 병합한 `main` push에서 사이트 검사와 Pages 배포가 실행됩니다. 봇은 PR을 승인하거나 병합하지 않습니다.
6. 게시하지 않으려면 PR을 닫습니다. 미병합 초안의 콘텐츠와 중복 방지 상태는 운영 브랜치에 반영되지 않습니다.

열린 검토 PR이 있으면 정기·수동 생성 모두 AI 호출 전에 건너뜁니다. 검토가 밀린 동안 초안을 추가로 쌓지 않습니다. PR을 병합하거나 닫은 뒤 다음 예약 실행부터 재개됩니다. 검토가 오래 걸리면 수집일과 실제 게시일이 달라질 수 있으므로 최신성을 다시 확인하세요. 날짜와 기사 URL은 수집 당시 값을 유지합니다.

preview에서는 커밋·PR·배포가 없습니다. `main` 이외 브랜치에서는 이 생성 워크플로를 실행하지 않습니다. 생성 또는 전체 검사가 실패하면 배포하지 않으며, 전체 검사 실패 시 검토 브랜치만 남을 수 있습니다. `GITHUB_TOKEN`으로 만든 PR 이벤트가 자동으로 검사를 시작한다고 가정하지 않으므로, 생성 실행에서 재사용 워크플로를 직접 호출합니다. 사람이 PR을 수정하면 일반 PR 검사도 실행됩니다.

Python 테스트는 기존 수집·선별 검증과 새로운 두 언어 근거 검증·보류·저장 실패·중복 방지 조건을 오프라인으로 검사합니다. 실제 API 연결과 GitHub Pages 배포는 GitHub 환경에서 별도로 확인합니다.

## 이전 구현

`scripts/generate_dev_digest.py`와 `validate_dev_digest.py`는 기존 Markdown 아카이브의 수집·선별·검증 함수와 회귀 테스트를 유지하기 위해 남겼습니다. 새 npm 명령과 Actions는 `scripts/generate_digest.py`를 사용합니다. 기존 Ruby 빌드 스크립트는 운영 경로에서 사용하지 않습니다.

## 검토 알림

검사 성공 후 Draft PR을 열면 `Digest Review Notification`이 저장소 소유자 `@youdozi`를 댓글에서 멘션합니다. GitHub Mobile의 멘션 푸시와 휴대폰의 GitHub 알림을 허용하면 해당 알림으로 PR을 열 수 있습니다. 이메일 수신은 GitHub 개인 알림 설정에 따릅니다. 실제 휴대폰 수신 여부는 기기 설정에 따라 달라지며 Actions 성공은 GitHub 댓글 생성 성공을 의미합니다.

동일 PR에는 봇의 알림 표시를 확인해 한 번만 전송합니다. 검토 대기 중 매일 반복 알림은 보내지 않습니다. 이미 열린 초안에 최초 알림을 보내려면 Actions → Digest Review Notification → Run workflow에서 `main`과 PR 번호를 지정합니다. 같은 저장소의 열린 `content/digest-review-*` Draft PR만 허용하며, 이 작업에는 병합·배포 권한이 없습니다.
