---
title: "Astro 품질 게이트: PR 검사 성공과 배포 조건 구분하기"
language: ko
translationKey: 2026-04-07-jekyll-quality-gates-proof-html-bundler-audit
routeSlug: 2026-04-07-jekyll-quality-gates-proof-html-bundler-audit
kind: post
publishedAt: 2026-04-07T13:40:00.000Z
categories:
  - blog
  - automation
tags:
  - astro
  - github-actions
  - github-pages
  - quality-gates
  - testing
legacyUrl: /blog/automation/jekyll-quality-gates-proof-html-bundler-audit/
description: Astro 검증과 GitHub Pages 게시를 구분합니다. 커밋 ref·선행 빌드·배포 조건을 입력 모델 24개와 실패해야 하는 변형 6개로 확인합니다.
legacySource: _posts/blog/automation/2026-04-07-jekyll-quality-gates-proof-html-bundler-audit.markdown
updatedAt: 2026-10-27T06:32:55.234Z
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Current repository workflow contracts checked; paired offline JavaScript examples executed with mocked APIs and bounded deployment-policy tests.
archiveBodySha256: d9c0f36ce75e8201706759fcfd599f531cf18fbc0ed1d7fed43c406058cfc2d0
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
PR 빌드의 성공은 설정된 검사가 통과했다는 뜻입니다. 이 사이트에서 후보를 게시하려면 `main` ref, 허용된 이벤트, 선행 빌드의 성공이라는 배포 조건도 충족해야 합니다.

이전 Jekyll 환경은 `proof-html`과 `bundler-audit`를 사용했습니다. 현재 Astro 경로는 `site-checks.yml`에서 검증하고 `site-quality-gates.yml`에서 Pages에 배포합니다. Ruby 검사는 이전 도구에 해당하며 현재 사이트를 빌드하는 npm 의존성을 감사하지 않습니다.

## 검증과 배포 나누기

![후보를 검사하고 main 이벤트 조건을 확인한 뒤 검사된 산출물을 배포하는 흐름](/assets/diagrams/2026-04-07-jekyll-quality-gates-proof-html-bundler-audit-ko.svg)

[사이트 워크플로](https://github.com/youdozi/youdozi.github.io/blob/main/.github/workflows/site-quality-gates.yml)는 `${{ github.sha }}`를 공통 검사기에 전달합니다. [재사용 워크플로](https://github.com/youdozi/youdozi.github.io/blob/main/.github/workflows/site-checks.yml)는 입력받은 ref를 체크아웃하고, build 작업과 contents 읽기 권한을 가지며, 호출자가 활성화하지 않으면 Pages 산출물 옵션을 false로 유지합니다. 이러한 호출 구조는 GitHub의 [`workflow_call` 문서](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows)에 설명되어 있습니다.

설정된 검사는 서로 다른 실패를 찾습니다.

| 검사 | 확인할 수 있는 범위 |
| --- | --- |
| Python·Node 테스트 | 수집·언어·게시·렌더링의 테스트된 계약 |
| 글에서 추출한 실행 예제 | 기록한 도구 조합에서 선택한 동작 사례 |
| `npm run check` | 콘텐츠 규칙과 Astro 타입·스키마 |
| `npm run build` | 정적 출력과 내부 링크·이미지·앵커·이관 누락 |

내부 링크 검사는 외부 URL의 접속 가능성을 보장하지 않습니다. 예제 통과가 모든 운영 동작을 입증하지도 않으며, 형식이 올바른 글에도 근거 없는 주장이 남을 수 있습니다. 현재 워크플로는 일반적인 npm 취약점 감사도 실행하지 않습니다.

## 선택된 배포 계약 재현하기

저장소를 체크아웃하고 Node 24에서 `npm ci`를 실행합니다. 다음 전체 파일을 저장소 루트의 `deploy-contract.mjs`로 저장한 뒤 실행하세요.

```sh
node deploy-contract.mjs
```

스크립트는 실제 YAML 값을 확인한 다음 고정된 배포 조건을 입력 조합 24개로 모델링합니다. 의도적으로 변경한 워크플로 객체 6개는 계약 검사를 통과하지 못해야 합니다. 배포나 네트워크 호출 기능은 없습니다.

### `deploy-contract.mjs`

```javascript
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import YAML from 'yaml';

const read = file => YAML.parse(readFileSync(`.github/workflows/${file}`, 'utf8'));
const site = read('site-quality-gates.yml');
const checks = read('site-checks.yml');
const condition = "github.ref == 'refs/heads/main' && (github.event_name == 'push' || github.event_name == 'workflow_dispatch')";
function verify(site, checks) {
    assert.equal(site.jobs.deploy.if, condition);
    assert.equal(site.jobs.deploy.needs, 'build');
    assert.equal(site.jobs.build.with.ref, '${{ github.sha }}');
    assert.equal(site.jobs.build.with.pages_artifact, '${{ ' + condition + ' }}');
    assert.deepEqual(Object.keys(checks.jobs), ['build']);
    assert.deepEqual(checks.permissions, { contents: 'read' });
    assert.equal(checks.on.workflow_call.inputs.pages_artifact.default, false);
    assert.equal(checks.jobs.build.steps[0].with.ref, '${{ inputs.ref }}');
    assert.ok(site.jobs.deploy.steps.some(step => step.uses === 'actions/deploy-pages@v4'));
}
verify(site, checks);

// A model of this fixed condition and successful dependency, not the Actions engine.
function allowed(ref, event, build) {
    return build === 'success' && ref === 'refs/heads/main' &&
        (event === 'push' || event === 'workflow_dispatch');
}
const expected = new Set([
    'refs/heads/main|push|success',
    'refs/heads/main|workflow_dispatch|success',
]);
let cases = 0;
for (const ref of ['refs/heads/main', 'refs/heads/develop', 'refs/heads/content/example', 'refs/pull/42/merge']) {
    for (const event of ['push', 'workflow_dispatch', 'pull_request']) {
        for (const build of ['success', 'failure']) {
            assert.equal(allowed(ref, event, build), expected.has(`${ref}|${event}|${build}`));
            cases++;
        }
    }
}

const mutations = [
    (site, checks) => { site.jobs.deploy.if = "github.event_name == 'pull_request'"; },
    (site, checks) => { site.jobs.deploy.needs = []; },
    (site, checks) => { site.jobs.build.with.ref = 'main'; },
    (site, checks) => { checks.permissions.pages = 'write'; },
    (site, checks) => { checks.on.workflow_call.inputs.pages_artifact.default = true; },
    (site, checks) => { checks.jobs.build.steps[0].with.ref = 'main'; },
];
for (const mutate of mutations) {
    const badSite = structuredClone(site), badChecks = structuredClone(checks);
    mutate(badSite, badChecks);
    assert.throws(() => verify(badSite, badChecks), assert.AssertionError);
}
console.log(`${cases} policy-model combinations and ${mutations.length} rejected workflow mutations passed.`);
```

실행해 확인한 출력입니다.

```text
24 policy-model combinations and 6 rejected workflow mutations passed.
```

이 모델은 `main`에서 `push` 또는 `workflow_dispatch`로 실행한 빌드가 성공한 경우만 허용합니다. 기능 브랜치의 수동 실행을 포함한 다른 조합은 거절합니다. `pull_request` 실행은 보통 PR 병합 ref를 사용하므로 성공하더라도 이 사이트의 배포 조건을 통과하지 않습니다. GitHub의 [작업 조건](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-jobs-with-conditions)과 [선행 작업 성공 규칙](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-jobs)을 함께 확인하세요.

이는 선택된 ref·이벤트 조건과 빌드 성공 의존성을 표현한 모델이며 Actions 표현식 해석기가 아닙니다. 성공·실패 상태만 다루고 취소·선행 작업 생략·러너 배정·토큰 권한·산출물 출처·실제 Pages 배포는 재현하지 않습니다. YAML 조건이 바뀌면 명시적으로 재검토하도록 assertion이 실패하게 했습니다. 새 설정을 이전 모델로 조용히 검사하지 않습니다.

## 게시 결과 확인하기

후보를 승인하고 병합한 뒤에는 main 실행의 커밋, build 결과, deploy 작업을 확인합니다. PR 실행에서 `deploy: skipped`는 정상입니다. 빌드 성공만으로 게시를 완료했다고 판단하지 않습니다. Pages 작업은 검사된 산출물을 사용하며 [Astro Pages 배포 방식](https://docs.astro.build/en/guides/deploy/github/)을 따릅니다.

실제 공개 글과 언어 링크를 열고 canonical URL, 출처 날짜, 사이트맵 항목을 확인합니다. IndexNow는 배포 뒤 실패를 허용하는 단계로 실행하므로 Pages가 성공해도 알림은 실패할 수 있습니다. 알림 접수나 사이트맵 포함만으로 검색엔진의 색인·노출을 입증할 수도 없습니다.

앞 단계인 Draft PR 검토는 [후보 생성 워크플로 글](/ko/posts/2026-04-07-jekyll-github-actions-content-pipeline/)에서 설명합니다. 기술 검사와 게시 결정은 역할이 다르며, 둘 다 글의 주장과 근거를 확인하는 일을 대신하지 않습니다.
