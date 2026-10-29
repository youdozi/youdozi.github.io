---
language: en
translationKey: 2026-04-07-jekyll-quality-gates-proof-html-bundler-audit
routeSlug: 2026-04-07-jekyll-quality-gates-proof-html-bundler-audit
kind: post
publishedAt: 2026-10-27T07:19:48.249Z
categories:
  - blog
  - automation
title: "Astro Quality Gates: Why a Passing PR Does Not Deploy"
description: Separate Astro validation from GitHub Pages publication. Check commit refs, successful dependencies and deployment conditions with 24 model cases and six failing mutations.
tags:
  - astro
  - github-actions
  - github-pages
  - quality-gates
  - testing
updatedAt: 2026-10-27T07:19:48.249Z
reviewedAt: "2026-10-27"
reviewStatus: revised
reviewScope: Current repository workflow contracts checked; paired offline JavaScript examples executed with mocked APIs and bounded deployment-policy tests.
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
A passing PR build establishes that its configured checks passed. On this site, that result does not publish the candidate: production deployment additionally requires the `main` ref, an allowed event and a successful build dependency.

The earlier Jekyll setup used `proof-html` and `bundler-audit`. The current Astro path uses `site-checks.yml` for validation and `site-quality-gates.yml` for Pages deployment. Ruby checks still concern the legacy toolchain; they do not audit the npm dependencies used to build this site.

## Separate validation from deployment

![Check the candidate, apply the main event gate and deploy the checked artifact](/assets/diagrams/2026-04-07-jekyll-quality-gates-proof-html-bundler-audit-en.svg)

The [site workflow](https://github.com/youdozi/youdozi.github.io/blob/main/.github/workflows/site-quality-gates.yml) passes `${{ github.sha }}` to the shared checker. The [reusable workflow](https://github.com/youdozi/youdozi.github.io/blob/main/.github/workflows/site-checks.yml) checks out that input ref, has a build job and read-only contents permissions, and leaves its Pages-artifact option false unless a caller enables it. GitHub's [`workflow_call` documentation](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows) describes that interface.

The configured checks cover different failures:

| Check | What it can establish |
| --- | --- |
| Python and Node tests | Tested collection, language, publication and rendering contracts |
| Extracted article examples | The examples' selected execution cases on their recorded toolchains |
| `npm run check` | Content rules and Astro type/schema checks |
| `npm run build` | Static output plus internal links, images, anchors and migration coverage |

An internal-link check does not establish external URL availability. A passing example does not establish every production behavior, and a well-formed article can still make an unsupported claim. The active workflow also does not run a general npm vulnerability audit.

## Reproduce the selected deployment contracts

With Node 24, run `npm ci` in a checkout of this repository. Save this complete file as `deploy-contract.mjs` at the repository root and run:

```sh
node deploy-contract.mjs
```

The script checks the actual YAML values, then models the fixed deployment condition over 24 input combinations. Six deliberately altered workflow objects must fail the contract check. The script has no deploy or network operation.

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

The checked output is:

```text
24 policy-model combinations and 6 rejected workflow mutations passed.
```

Only successful builds on `main` with `push` or `workflow_dispatch` are allowed in this model. All other combinations are rejected, including a manually dispatched feature branch. A `pull_request` run normally uses a pull-request merge ref, so its success does not pass this site's deployment condition. GitHub documents both [job conditions](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-jobs-with-conditions) and [successful dependency requirements](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-jobs).

This is a model of the selected ref/event condition plus a successful build dependency, not an Actions expression interpreter. It tests success and failure states; it does not simulate cancellation, skipped ancestors, runner scheduling, token authorization, artifact provenance or a Pages deployment. The YAML assertions make a changed policy fail for explicit review rather than silently testing the old model against new configuration.

## Confirm the published result

After approving and merging a candidate, inspect the main run's commit, build result and deploy job. A green PR run with `deploy: skipped` is expected; a successful build alone is not proof of publication. The Pages job uses the checked artifact, following the [Astro Pages deployment pattern](https://docs.astro.build/en/guides/deploy/github/).

Open the public article and its language links, then check the canonical URL, source dates and sitemap entry. IndexNow runs after deployment with failure-tolerant steps, so it can fail while Pages succeeds. Notification acceptance and sitemap presence also do not prove search-engine indexing or impressions.

The [candidate workflow article](/en/posts/2026-04-07-jekyll-github-actions-content-pipeline/) explains the preceding Draft PR review. Keep technical checks and the decision to publish as separate responsibilities; neither replaces checking the article's claims.
