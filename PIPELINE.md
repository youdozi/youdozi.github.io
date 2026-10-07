# Dev Content Pipeline

개발 RSS의 출처 제공 설명과 원문 링크를 매일 Jekyll 글로 정리합니다. AI 번역·요약이나 원문 사실 검증을 수행하지 않습니다. 주제 분류와 `확인할 점`은 규칙 기반 안내입니다.

## 동작과 게시 조건

1. GitHub Changelog, InfoQ, JetBrains, Spring, Cloudflare RSS/Atom 수집.
2. 최근 7일의 미래가 아닌 기사에서 기술 키워드와 점수로 선별.
3. 기본 최소 점수 6, 출처당 최대 3개, 전체 최대 6개. 조건을 충족하는 기사가 적으면 적은 수로 발행하고, 없으면 건너뜁니다.
4. 설명은 RSS에서 HTML·엔티티·블로그 안내 문구를 정리합니다. 80~420자이며 완성된 문장이어야 합니다. 긴 설명은 완성된 문장까지 줄이고, 불완전한 설명·채용/인턴/웨비나 등 홍보성 제목은 제외합니다.
5. 같은 실행 안의 제목/URL 중복과 과거 게시 URL 재사용을 차단합니다. `.pipeline/content_state.json`과 기존 게시글을 모두 확인합니다. 손상된 상태 파일은 실패 처리합니다.
6. 각 기사에 출처·설명·발행일·링크·확인할 점이 있는지 검사합니다. URL은 HTTPS와 출처별 승인 호스트를 사용하고 표시 URL과 대상 URL이 같아야 합니다.
7. Actions에서는 `--check-links`로 원문 URL의 HTTP 200, HTML 응답, 최종 출처 호스트를 확인합니다. 네트워크 오류·403·404 등으로 확인할 수 없으면 발행을 중단합니다. HTTP 200만으로 기사의 사실이나 소프트 404를 보장하지는 않습니다.
8. 검증 후 오늘의 글과 상태를 저장하고 Jekyll 빌드 성공 후 해당 두 파일만 커밋합니다.

전체 소스가 실패하거나 사용 가능한 항목을 하나도 반환하지 않으면 실패합니다. 일부 소스 실패는 경고로 남기고 나머지 소스를 처리합니다. 오늘 글이 이미 있거나 새로운 적격 기사가 없으면 정상적으로 건너뛰며 과거 글을 대신 검증하지 않습니다.

## 실행

```bash
python3 -m unittest discover -s scripts -p 'test_dev_digest.py' -v
python3 scripts/generate_dev_digest.py --dry-run
python3 scripts/generate_dev_digest.py --max-items 6 --check-links
python3 scripts/validate_dev_digest.py _posts/dev/digest/YYYY-MM-DD-dev-digest.markdown --check-links
bash scripts/jekyll-build.sh
```

생성기 옵션:

- `--repo-root`: 저장소 루트. 기본 `.`
- `--days-back`: 최신성 범위. 기본 7일.
- `--max-items`: 전체 최대 기사 수. 기본 6.
- `--min-score`: 최소 점수. 기본 6.
- `--max-per-source`: 출처당 최대 기사 수. 기본 3.
- `--dry-run`: 저장 없이 후보 글 출력.
- `--force`: 오늘 글이 있어도 새 미게시 후보로 덮어쓰기. 기존 게시 URL은 상태에 남습니다.
- `--state-file`: 상태 파일 위치. 기본 `.pipeline/content_state.json`.
- `--fixtures-dir`: 오프라인 RSS/Atom 파일 사용. 기존 fixture 날짜는 고정되어 있어 현재 날짜의 생성 예시로는 제외될 수 있습니다. 자동 테스트는 실행 시점 기준 날짜를 사용합니다.
- `--check-links`: 선택된 원문 링크 접속 검사.
- `--github-output`: `generated=true/false`와 생성한 `post_path`를 GitHub Actions 출력 파일에 기록.

`PIPELINE_INSECURE_SSL=true`는 로컬 RSS 수집 인증서 문제를 임시 우회하는 기존 옵션입니다. Actions는 기본 TLS 검증을 사용하며 원문 링크 검사는 이 옵션을 사용하지 않습니다.

## GitHub Actions

매일 한국 시간 07:00 예약(`0 22 * * *`, UTC)과 수동 실행을 지원합니다. 실제 시작은 GitHub 예약 상황에 따라 늦어질 수 있습니다.

파이프라인 파일을 변경하는 PR에서는 오프라인 테스트만 실행합니다. 정기/수동 실행은 테스트 성공 후 생성·링크 검증·빌드·커밋을 수행합니다. 같은 ref의 실행은 순서대로 처리합니다. 기본 권한은 읽기이며 생성 job만 contents 쓰기를 허용합니다.

기존 게시글을 일괄 수정하지 않습니다. 새 기준은 앞으로 생성하는 글에 적용되며, 오래된 글을 새 검증기로 수동 검사하면 과거에 허용됐던 설명/날짜/형식 문제를 발견할 수 있습니다.
