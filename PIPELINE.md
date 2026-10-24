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

매일 한국 시간 07:00(`0 22 * * *`, UTC)에 실행합니다. 수동 실행의 `preview=true`가 기본이며 `--dry-run --force --max-items 2`로 AI 연결을 검사합니다. 실제 게시에는 `preview=false`를 사용합니다.

생성 후 Astro 타입·스키마 검사와 빌드·내부 링크 검사가 모두 통과해야 JSON과 상태를 커밋합니다. `main`에서는 재사용 사이트 워크플로에 생성 커밋 SHA를 전달해 빌드·검증·Pages 배포를 직접 수행합니다. preview에서는 커밋이나 배포가 없습니다. `main` 이외 브랜치에서는 생성할 수 있지만 운영 배포는 하지 않습니다.

Python 테스트는 기존 수집·선별 검증과 새로운 두 언어 근거 검증·보류·저장 실패·중복 방지 조건을 오프라인으로 검사합니다. 실제 API 연결과 GitHub Pages 배포는 GitHub 환경에서 별도로 확인합니다.

## 이전 구현

`scripts/generate_dev_digest.py`와 `validate_dev_digest.py`는 기존 Markdown 아카이브의 수집·선별·검증 함수와 회귀 테스트를 유지하기 위해 남겼습니다. 새 npm 명령과 Actions는 `scripts/generate_digest.py`를 사용합니다. 기존 Ruby 빌드 스크립트는 운영 경로에서 사용하지 않습니다.
