import test from 'node:test';
import assert from 'node:assert/strict';
import { algorithmGuide, algorithmCategoryAlternates, algorithmStructuredData } from '../src/lib/algorithm-guide.ts';
const entry = (key, language = 'en', overrides = {}) => ({
  translationKey: key, language, title: key, slug: key, kind: 'post',
  publishedAt: new Date('2021-01-01Z'), categories: ['coding-test'], tags: [],
  description: 'A Java exercise.', url: `/${language}/posts/${key}/`, ...overrides,
});
test('guides and alternates exclude unpublished, example, digest and unrelated entries', () => {
  const items = [entry('2021-07-22-plus-minus', 'ko'),
    entry('future', 'en', { publishedAt: new Date('2999-01-01Z') }),
    entry('example', 'en', { reviewStatus: 'example' }),
    entry('digest', 'en', { kind: 'digest' }),
    entry('other', 'en', { categories: ['spring'] })];
  assert.equal(algorithmGuide('en', items), undefined);
  assert.equal(algorithmGuide('ja', items), undefined);
  assert.deepEqual(algorithmCategoryAlternates(items), [{language:'ko', url:'/ko/categories/coding-test/'}]);
  assert.equal(algorithmGuide('ko', items).ordered.length, 1);
});
test('partial guides omit unavailable topics and retain additional category entries', () => {
  const items = [entry('extra'), entry('2021-07-29-ponkemon'), entry('2021-07-22-plus-minus')];
  const guide = algorithmGuide('en', items);
  assert.deepEqual(guide.sections.map(g => [g.id, g.start]), [['arrays', 1], ['collections', 2]]);
  assert.deepEqual(guide.ordered.map(e => e.translationKey), ['2021-07-22-plus-minus', '2021-07-29-ponkemon', 'extra']);
  assert.deepEqual(guide.extras, [items[0]]);
  assert.doesNotMatch(guide.description, /ten exercises/);
});
test('structured data preserves the visible guide order and actual locale URLs', () => {
  const items = [entry('2021-07-29-ponkemon', 'ko'), entry('2021-07-22-plus-minus', 'ko')];
  const guide = algorithmGuide('ko', items);
  const data = algorithmStructuredData(guide, new URL('https://example.org'));
  const list = data.find(d => d['@type'] === 'ItemList');
  assert.equal(list.numberOfItems, guide.ordered.length);
  assert.deepEqual(list.itemListElement.map(e => [e.position,e.name,e.url]),
    guide.ordered.map((e,i) => [i+1,e.title,`https://example.org${e.url}`]));
  assert.equal(data[0].mainEntity['@id'], list['@id']);
  assert.equal(data[0].inLanguage, 'ko');
  assert.equal(data[2].itemListElement.at(-1).item, 'https://example.org/ko/categories/coding-test/');
});
