---
language: en
translationKey: 2026-04-07-jekyll-github-actions-content-pipeline
routeSlug: 2026-04-07-jekyll-github-actions-content-pipeline
kind: post
publishedAt: 2026-10-27T06:32:55.234Z
categories:
  - blog
  - automation
title: From Jekyll Auto-Publishing to Astro Draft PR Review
description: Follow a bilingual digest from generation to commit-specific validation, a Draft PR and approved publication. Run the review scripts locally with mocked GitHub calls.
tags:
  - astro
  - github-actions
  - github-pages
  - content-review
  - automation
updatedAt: 2026-10-27T06:32:55.234Z
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
A content generator should produce a review candidate. In this repository, successful generation and CI lead to a Draft PR; publication follows a separate merge and the main-branch Pages workflow.

The April Jekyll pipeline wrote Markdown and pushed generated content. The site now uses Astro, stores new bilingual digests as JSON, and keeps the candidate off `main` until review. Existing `_posts` files and Ruby tooling describe the earlier site, rather than the current publication command.

## Follow the candidate commit

![Generate a candidate, validate its commit and open a Draft PR](/assets/diagrams/2026-04-07-jekyll-github-actions-content-pipeline-en.svg)

The [content workflow](https://github.com/youdozi/youdozi.github.io/blob/main/.github/workflows/dev-content-pipeline.yml) runs generation only on `main`. It first checks for an open `content/digest-review-` PR from this repository. When one exists, it pauses another candidate, including a manual preview run, until that PR is merged or closed.

With no pending candidate, `scripts/generate_digest.py` collects and prepares English/Korean editions. A generated file must pass `npm run check` and `npm run build` before a commit is pushed to a new review branch. The shared validator then checks that generated commit SHA, and the review job depends on both generation and validation succeeding. This follows GitHub's [job dependency behavior](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-jobs).

The review job renders the evidence, creates a Draft PR, adds the review preview URL and explicitly dispatches the site workflow on the review branch. That branch can be checked without satisfying the production deployment condition. The [token event rules](https://docs.github.com/en/actions/concepts/security/github_token) also matter when automation triggers another workflow; do not infer a run from a successful API request alone.

## Exercise the review logic without calling GitHub

Use Node 24 and run `npm ci` in a checkout of this repository. Save the following complete file as `review-contract.mjs` at the repository root, then run:

```sh
node review-contract.mjs
```

This harness reads the actual workflow YAML, executes its two JavaScript snippets with local mocks, and checks five pending-PR cases plus the create/update/dispatch sequence. Its mock exposes no merge operation. It does not execute workflow YAML, generate a real digest, or make API calls.

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

The checked output is:

```text
5 pending-PR cases and the mocked draft/create-update-dispatch sequence passed.
```

The five inputs distinguish no pending PR, a matching local digest PR, another repository's PR, a different local branch, and a missing head repository. Passing the harness shows those selected script contracts, rather than GitHub token permissions, branch protection, source accuracy or the whole hosted workflow.

## Request a candidate and decide what to publish

In **Actions → Dev Content Pipeline → Run workflow**, select `main`. Leave `preview` unchecked to prepare a review candidate. Check it for the dry-run path, which uses `--dry-run --force --max-items 2`; it does not commit a candidate. An already pending digest still pauses generation. GitHub documents the [manual workflow controls](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow).

Open the Draft PR and its bilingual preview. Check the source date, the original claim and its support, translation scope, links and whether the item merits publication. Automated code and schema checks cannot make that editorial decision. Change the candidate when needed, confirm the resulting commit's checks, then mark it ready and merge when publication is approved. Merely marking a draft ready does not deploy it.

The [quality-gate article](/en/posts/2026-04-07-jekyll-quality-gates-proof-html-bundler-audit/) explains why a green PR run can correctly skip deployment and what to verify after a merge. For the earlier Ruby environment, see the [Jekyll troubleshooting record](/ko/posts/2026-04-07-ruby-rbenv-jekyll-build-troubleshooting/), currently available in Korean.
