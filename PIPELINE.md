# Dev Content Pipeline

이 파이프라인은 인스타그램 같은 소셜 크롤링을 제외하고, 개발 관련 고품질 블로그/RSS를 자동 수집해서 Jekyll 포스트(`_posts`)를 생성하고 GitHub Actions가 검증 후 커밋/푸시합니다.

## 1) 동작 흐름

1. `scripts/generate_dev_digest.py`가 큐레이션된 개발 RSS 소스를 수집
2. 최신성/기술키워드/중복 여부로 점수화 후 상위 항목 선별
3. `_posts/dev/digest/YYYY-MM-DD-dev-digest.markdown` 생성
4. `scripts/validate_dev_digest.py`가 front matter/섹션/링크 형식을 검증
5. `.pipeline/content_state.json`에 이미 사용한 링크 저장
6. `.github/workflows/dev-content-pipeline.yml`가 검증 통과 시에만 변경분을 커밋/푸시

## 2) 품질 가드레일

- 소스 화이트리스트 기반 수집 (GitHub, Spring, JetBrains, Cloudflare, InfoQ)
- 최근 N일(`--days-back`, 기본 7일)만 허용
- 제목 기반 중복 제거 + 링크 재사용 차단
- 원문 재배포 금지: 포스트에는 요약/맥락/원문 링크만 포함
- 생성 결과 검증: layout, categories/tags, 섹션 구조, 링크 개수 검사

## 3) 로컬 실행

```bash
python3 scripts/generate_dev_digest.py --dry-run
python3 scripts/generate_dev_digest.py --max-items 6 --days-back 7
python3 scripts/validate_dev_digest.py _posts/dev/digest/YYYY-MM-DD-dev-digest.markdown
bash scripts/jekyll-build.sh
```

빠른 실행:

- `npm run generate:digest:dry`
- `npm run generate:digest`
- `npm run validate:digest -- _posts/dev/digest/YYYY-MM-DD-dev-digest.markdown`
- `npm run jekyll:build`

옵션:

- `--force`: 오늘 날짜 파일이 있어도 덮어쓰기
- `--state-file`: 링크 상태 파일 위치 변경
- `--repo-root`: 다른 루트에서 실행 시 지정
- `--fixtures-dir`: 네트워크 없이 fixture XML로 오프라인 검증

환경 변수:

- `PIPELINE_INSECURE_SSL=true`: 로컬 인증서 체인이 깨진 환경에서만 임시 우회 (기본값 `false`)

오프라인 검증 예시:

```bash
python3 scripts/generate_dev_digest.py --fixtures-dir scripts/fixtures --force
python3 scripts/validate_dev_digest.py _posts/dev/digest/YYYY-MM-DD-dev-digest.markdown
```

## 4) GitHub Actions 자동 실행

- 파일: `.github/workflows/dev-content-pipeline.yml`
- 스케줄: 매일 07:00 KST (`cron: 0 22 * * *`, UTC 기준)
- 수동 실행: `workflow_dispatch`
- 순서: 생성 -> 검증 -> 커밋

필수 조건:

- 레포 `Settings > Actions > General`에서 워크플로 권한이 `Read and write permissions`

## 5) 커스터마이징 포인트

- 소스 변경: `scripts/generate_dev_digest.py`의 `QUALITY_SOURCES`
- 키워드/토픽 분류: `TOPIC_KEYWORDS`
- 중요도 문구: `SUMMARY_RULES`
- 기본 생성량: `--max-items`
