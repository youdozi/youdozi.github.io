import test from 'node:test';
import assert from 'node:assert/strict';
import { relatedEntries } from '../src/lib/related.ts';

function entry(id, extra = {}) {
  return { title: id, language: 'en', translationKey: id, url: `/en/posts/${id}/`, kind: 'post',
    tags: [], categories: [], publishedAt: new Date('2026-01-01'), ...extra };
}

test('specific tags outrank a recent broad topic and relevant news can link to tutorials', () => {
  const target = entry('Testing Spring WebClient', { tags: ['webclient', 'springboot'] });
  const exact = entry('HTTP fixtures', { tags: ['webclient'] });
  const broad = entry('Spring release', { kind: 'digest', publishedAt: new Date('2026-10-01') });
  const unrelated = entry('Cloudflare roadmap', { publishedAt: new Date('2026-10-02') });
  assert.deepEqual(relatedEntries(target, [unrelated, broad, exact]), [exact, broad]);
});

test('generic metadata never fills recommendations; examples, self and other languages are excluded', () => {
  const target = entry('unclassified', { tags: ['archive-renewal'], categories: ['dev', 'digest'] });
  const generic = entry('other', { tags: ['archive-renewal'], categories: ['dev', 'digest'] });
  assert.deepEqual(relatedEntries(target, [target, generic]), []);
  const spring = entry('Spring testing');
  assert.deepEqual(relatedEntries(spring, [spring, entry('Spring foreign', { language: 'ko' }),
    entry('Spring example', { reviewStatus: 'example' })]), []);
});

test('translated renewals use the approved English title without requiring translated keywords', () => {
  const source = title => ({ data: { editions: { en: { title } } } });
  const target = entry('認可方式', { language: 'ja', tags: ['archive-renewal'], renewal: source('Cloudflare authorization design') });
  const relevant = entry('認証方式', { language: 'ja', tags: ['archive-renewal'], renewal: source('Cloudflare post-quantum authentication') });
  const unrelated = entry('料金変更', { language: 'ja', tags: ['archive-renewal'], renewal: source('Copilot credit pools') });
  assert.deepEqual(relatedEntries(target, [unrelated, relevant]), [relevant]);
});

test('a shared vendor does not connect code scanning to an unrelated model retirement', () => {
  const target = entry('CodeQL models-as-data');
  const relevant = entry('GitHub security advisories');
  const unrelated = entry('GitHub Copilot model retirement');
  assert.deepEqual(relatedEntries(target, [unrelated, relevant]), [relevant]);
});

test('technology names respect word boundaries and known taxonomy aliases match', () => {
  assert.deepEqual(relatedEntries(entry('Java memory'), [entry('JavaScript memory')]), []);
  const alias = entry('migration', { tags: ['SpringBoot', 'test'] });
  const candidate = entry('fixtures', { tags: ['spring-boot', 'testing'] });
  assert.deepEqual(relatedEntries(alias, [candidate]), [candidate]);
});

test('ties use publication time then URL, preserve input and respect the limit', () => {
  const target = entry('Java');
  const a = entry('Java-a'), b = entry('Java-b'), recent = entry('Java-new', { publishedAt: new Date('2026-02-01') });
  const input = [b, a, recent, { ...a }];
  assert.deepEqual(relatedEntries(target, input, 2), [recent, a]);
  assert.deepEqual(input.map(e => e.title), ['Java-b', 'Java-a', 'Java-new', 'Java-a']);
  assert.deepEqual(relatedEntries(target, input, 0), []);
});
