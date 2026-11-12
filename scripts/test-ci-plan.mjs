import test from 'node:test';
import assert from 'node:assert/strict';
import {inventory, plan} from './ci-plan.mjs';

const checks = inventory();
const mvc = checks.find(check => check.keys.has('2026-11-09-spring-mvc-webclient-execution'));
test('MVC publication selects its actual 16-case runner, JDK 21 and Gradle only', () => {
  const result = plan(['src/content/posts/ko/2026-11-09-spring-mvc-webclient-execution.md',
    'assets/img/architecture/mvc-webclient-flow-ko.svg']);
  assert.equal(result.full, false);
  assert.equal(result.previews, false);
  assert.deepEqual(result.steps.filter(id => id.startsWith('example_')), [mvc.id]);
  assert.equal(mvc.dependencies.length, 3);
  assert.ok(mvc.dependencies.every(id => result.steps.includes(id)));
});
test('shared harness, workflow, unknown article or missing diff runs every example', () => {
  for (const files of [undefined, [], ['scripts/check_cache_example.py'], ['.github/workflows/site-checks.yml'],
    ['src/content.config.ts'], ['src/content/posts/ko/2026-11-09-unregistered.md'], ['unknown.file']]) {
    const result = plan(files);
    assert.equal(result.full, true, JSON.stringify(files));
    assert.equal(result.previews, true);
    assert.equal(result.steps.filter(id => id.startsWith('example_')).length, checks.length);
  }
});
test('translation and shared rendering changes retain previews without unrelated runtimes', () => {
  for (const path of ['src/content/posts/ja/2026-11-09-spring-mvc-webclient-execution.md',
    '.pipeline/technical-translations/batch.json', 'src/layouts/Base.astro']) {
    const result = plan([path]);
    assert.deepEqual(result.steps, []);
    assert.equal(result.previews, true);
  }
});
test('virtual thread article executes both JDK 21 and 25 probes', () => {
  const matches = checks.filter(check => check.keys.has('2026-10-31-virtual-threads-jdk21-jdk25'));
  const result = plan(['src/content/posts/en/2026-10-31-virtual-threads-jdk21-jdk25.md']);
  assert.equal(matches.length, 2);
  for (const check of matches) for (const id of [check.id, ...check.dependencies]) assert.ok(result.steps.includes(id));
});

test('Redis publication uses its runner and saved JDK 21 without JDK 27', () => {
  const redis = checks.find(check => check.keys.has('2026-11-10-redis-lua-rate-limit'));
  const result = plan(['src/content/posts/ko/2026-11-10-redis-lua-rate-limit.md',
    'assets/img/architecture/redis-rate-limit-ko.svg']);
  assert.equal(result.full, false);
  assert.deepEqual(result.steps.filter(id => id.startsWith('example_')), [redis.id]);
  assert.deepEqual(redis.dependencies, mvc.dependencies);
  assert.ok(!result.steps.includes('runtime_9'));
});

test('Bucket4j publication selects only its example and JDK 21 toolchain', () => {
  const bucket4j = checks.find(check => check.keys.has('2026-11-11-bucket4j-token-bucket'));
  const result = plan(['src/content/posts/ko/2026-11-11-bucket4j-token-bucket.md',
    'assets/img/architecture/bucket4j-flow-ko.svg']);
  assert.equal(result.full, false);
  assert.deepEqual(result.steps.filter(id => id.startsWith('example_')), [bucket4j.id]);
  assert.deepEqual(bucket4j.dependencies, mvc.dependencies);
});

test('T3 Code guide selects only its dependency-free Node exercise', () => {
  const exercise = checks.find(check => check.keys.has('2026-11-12-t3-code-workflow'));
  const result = plan(['src/content/posts/ko/2026-11-12-t3-code-workflow.md',
    'assets/img/architecture/t3-code-flow-ko.svg']);
  assert.equal(result.full, false);
  assert.deepEqual(result.steps, [exercise.id]);
  assert.deepEqual(exercise.dependencies, []);
});

test('Orca guide selects its Node exercise without launching the app or an agent', () => {
  const exercise = checks.find(check => check.keys.has('2026-11-12-orca-worktree-guide'));
  const result = plan(['src/content/posts/ko/2026-11-12-orca-worktree-guide.md',
    'assets/img/architecture/orca-flow-ko.svg']);
  assert.equal(result.full, false);
  assert.deepEqual(result.steps, [exercise.id]);
  assert.deepEqual(exercise.dependencies, []);
});
