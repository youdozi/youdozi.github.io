---
title: Jekyll 자동 게시에서 Astro Draft PR 검토로 전환하기
language: ko
translationKey: 2026-04-07-jekyll-github-actions-content-pipeline
routeSlug: 2026-04-07-jekyll-github-actions-content-pipeline
kind: post
publishedAt: 2026-04-07T12:30:00.000Z
categories:
  - blog
  - automation
tags:
  - astro
  - github-actions
  - github-pages
  - content-review
  - automation
legacyUrl: /blog/automation/jekyll-github-actions-content-pipeline/
description: 한영 다이제스트의 생성부터 후보 커밋 검증, Draft PR, 승인 후 게시까지 연결합니다. GitHub 호출을 모의 객체로 바꿔 실제 검토 스크립트를 실행합니다.
legacySource: _posts/blog/automation/2026-04-07-jekyll-github-actions-content-pipeline.markdown
updatedAt: 2026-10-27T06:32:55.234Z
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Current repository workflow contracts checked; paired offline JavaScript examples executed with mocked APIs and bounded deployment-policy tests.
archiveBodySha256: 6f2b0bed1bcc9903e2081684311a559bcfb7aa9bd6aaed66486032a1b24b4d06
reviewSources:
  - https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows
  - https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-jobs
  - https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-jobs-with-conditions
  - https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow
  - https://docs.github.com/en/actions/concepts/security/github_token
  - https://docs.astro.build/en/guides/deploy/github/
  - https://github.com/youdozi/youdozi.github.io/blob/main/.github/workflows/dev-content-pipeline.yml
  - https://github.com/youdozi/youdozi.github.io/blob/main/.github/workflows/site-quality-gates.yml
  - https://github.com/youdozi/youdozi.github.io/blob/main/.github/workflows/site-checks.yml
---
콘텐츠 생성기는 검토할 후보를 준비합니다. 이 저장소에서는 생성과 CI가 성공하면 Draft PR이 만들어지고, 게시에는 별도의 병합과 main 브랜치의 Pages 워크플로가 필요합니다.

4월의 Jekyll 파이프라인은 Markdown을 생성해 push했습니다. 현재 사이트는 Astro를 사용하며, 새 한영 다이제스트는 JSON으로 저장하고 검토 전 후보를 `main`에 넣지 않습니다. 남아 있는 `_posts`와 Ruby 도구는 이전 사이트의 자료이며 현재 게시 명령이 아닙니다.

## 후보 커밋을 따라가기

![후보를 생성하고 해당 커밋을 검사한 뒤 Draft PR을 여는 흐름](/assets/diagrams/2026-04-07-jekyll-github-actions-content-pipeline-ko.svg)

[콘텐츠 워크플로](https://github.com/youdozi/youdozi.github.io/blob/main/.github/workflows/dev-content-pipeline.yml)는 `main`에서만 생성을 실행합니다. 먼저 같은 저장소의 열린 `content/digest-review-` PR을 찾습니다. 대기 중인 PR이 있으면 병합하거나 닫을 때까지 추가 후보 생성을 멈추며, 수동 preview 실행도 이 조건을 따릅니다.

대기 후보가 없으면 `scripts/generate_digest.py`가 영문·한국어판을 준비합니다. 파일이 생성되면 `npm run check`와 `npm run build`를 통과한 뒤 새 검토 브랜치에 커밋을 push합니다. 공통 검증기는 생성된 커밋 SHA를 검사하고, review 작업은 생성과 검증 작업이 모두 성공해야 실행됩니다. 이는 GitHub의 [작업 의존성 규칙](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-jobs)을 따릅니다.

review 작업은 근거를 정리하고 Draft PR을 만든 뒤 미리보기 링크를 추가합니다. 이어 검토 브랜치에서 사이트 워크플로를 명시적으로 호출합니다. 이 브랜치도 검사는 받지만 운영 배포 조건은 충족하지 않습니다. 자동화에서 다른 워크플로를 호출할 때는 [토큰별 이벤트 규칙](https://docs.github.com/en/actions/concepts/security/github_token)도 확인해야 합니다. API 요청이 성공했다는 사실만으로 실행까지 완료됐다고 판단하지 않습니다.

## GitHub를 호출하지 않고 검토 로직 실행하기

이 저장소를 체크아웃하고 Node 24에서 `npm ci`를 실행합니다. 다음 전체 코드를 저장소 루트의 `review-contract.mjs`로 저장한 뒤 실행하세요.

```sh
node review-contract.mjs
```

이 검증기는 실제 워크플로 YAML을 읽고 JavaScript 조각 두 개를 로컬 모의 객체로 실행합니다. 대기 PR 조건 5개와 생성·수정·dispatch 호출 순서를 확인하며, 모의 객체에는 병합 기능이 없습니다. 워크플로 YAML 자체의 실행, 실제 다이제스트 생성, API 호출은 하지 않습니다.

### `review-contract.mjs`

```javascript
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import YAML from 'yaml';

const workflow = YAML.parse(readFileSync('.github/workflows/dev-content-pipeline.yml', 'utf8'));
const { generate, validate, review } = workflow.jobs;
assert.equal(generate.if, "github.ref == 'refs/heads/main'");
assert.deepEqual(review.needs, ['generate', 'validate']);
assert.equal(validate.with.ref, '${{ needs.generate.outputs.commit_sha }}');
assert.equal(validate.uses, './.github/workflows/site-checks.yml');
assert.equal(workflow.jobs.publish, undefined);

const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
const pendingScript = generate.steps.find(step => step.id === 'pending').with.script;
const runPending = new AsyncFunction('github', 'context', 'core', pendingScript);
const context = { repo: { owner: 'example', repo: 'blog' } };
const summary = { addRaw() { return this; }, async write() {} };
const cases = [
    [[], false],
    [[{ head: { repo: { full_name: 'example/blog' }, ref: 'content/digest-review-1' }, html_url: 'mock' }], true],
    [[{ head: { repo: { full_name: 'other/blog' }, ref: 'content/digest-review-1' } }], false],
    [[{ head: { repo: { full_name: 'example/blog' }, ref: 'content/manual-1' } }], false],
    [[{ head: { repo: null, ref: 'content/digest-review-1' } }], false],
];
for (const [pulls, expected] of cases) {
    let exists;
    const github = { rest: { pulls: { list() {} } }, paginate: async () => pulls };
    const core = { summary, setOutput(key, value) { if (key === 'exists') exists = value; } };
    await runPending(github, context, core);
    assert.equal(exists, expected);
}

const calls = [];
const github = { rest: {
    pulls: {
        async create(payload) { calls.push(['create', payload]); return { data: { number: 42, html_url: 'mock-pr' } }; },
        async update(payload) { calls.push(['update', payload]); },
    },
    actions: { async createWorkflowDispatch(payload) { calls.push(['dispatch', payload]); } },
} };
const core = { summary, setOutput() {} };
const requireMock = name => {
    assert.equal(name, 'node:fs');
    return { readFileSync: () => 'Mock review body' };
};
const script = review.steps.find(step => step.id === 'pr').with.script;
const runReview = new AsyncFunction('require', 'github', 'context', 'core', 'process', script);
await runReview(requireMock, github,
    { ...context, serverUrl: 'https://github.com', runId: 7 }, core,
    { env: { REVIEW_BRANCH: 'content/digest-review-7-1' } });
assert.deepEqual(calls.map(call => call[0]), ['create', 'update', 'dispatch']);
assert.equal(calls[0][1].draft, true);
assert.equal(calls[0][1].base, 'main');
assert.equal(calls[0][1].head, 'content/digest-review-7-1');
assert.equal(calls[2][1].workflow_id, 'site-quality-gates.yml');
assert.equal(calls[2][1].ref, calls[0][1].head);
console.log('5 pending-PR cases and the mocked draft/create-update-dispatch sequence passed.');
```

실행해 확인한 출력입니다.

```text
5 pending-PR cases and the mocked draft/create-update-dispatch sequence passed.
```

입력 5개는 대기 PR 없음, 같은 저장소의 다이제스트 PR, 다른 저장소의 PR, 다른 로컬 브랜치, head 저장소 없음으로 구분합니다. 통과 결과는 이 스크립트의 선택된 계약을 확인합니다. GitHub 토큰 권한·브랜치 보호·출처의 정확성·호스팅된 워크플로 전체를 입증하지는 않습니다.

## 후보 요청과 게시 판단

**Actions → Dev Content Pipeline → Run workflow**에서 `main`을 선택합니다. `preview`를 해제하면 검토 후보를 준비합니다. 체크하면 `--dry-run --force --max-items 2` 경로로 실행하며 후보를 커밋하지 않습니다. 이미 대기 중인 다이제스트가 있다면 생성은 멈춥니다. 수동 실행 화면은 [GitHub 안내](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow)에서도 확인할 수 있습니다.

Draft PR과 한영 미리보기를 열고 출처 날짜, 원래 주장과 근거, 번역 범위, 링크, 게시할 가치가 있는지 확인합니다. 코드·스키마 검사는 이 편집 판단을 대신하지 않습니다. 필요한 내용을 고친 뒤 변경된 커밋의 검사를 확인하고, 게시를 승인하면 Ready for review로 바꾸고 병합합니다. Draft 상태를 해제하는 것만으로 배포되지는 않습니다.

[품질 게이트 글](/ko/posts/2026-04-07-jekyll-quality-gates-proof-html-bundler-audit/)에서 정상적인 PR 실행이 배포를 생략하는 이유와 병합 후 확인할 항목을 이어 설명합니다. 이전 Ruby 환경은 [Jekyll 빌드 문제 해결 기록](/ko/posts/2026-04-07-ruby-rbenv-jekyll-build-troubleshooting/)에서 확인할 수 있습니다.
