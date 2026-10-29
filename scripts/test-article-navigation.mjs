import test from 'node:test';
import assert from 'node:assert/strict';
import {articleSections,visibleModified,articleUi} from '../src/lib/article-navigation.ts';
const heading=(slug,depth=2,text=slug)=>({slug,depth,text});
test('contents follows rendered sections while excluding short articles, digests and file-level headings',()=>{
  const sections=[heading('first'),heading('file',3),heading('둘째 절'),heading('first'),heading('third'),heading('fourth'),heading('',2),heading('blank',2,'  ')];
  const before=structuredClone(sections);
  assert.deepEqual(articleSections('post',sections).map(h=>h.slug),['first','둘째 절','third','fourth']);
  assert.deepEqual(sections,before);assert.deepEqual(articleSections('digest',sections),[]);
  assert.deepEqual(articleSections('post',sections.slice(0,3)),[]);assert.deepEqual(articleSections('post'),[]);
});
test('visible modification dates require a strictly later recorded change and all locales have labels',()=>{
  const publishedAt=new Date('2026-01-01Z');
  for(const updatedAt of [undefined,publishedAt,new Date('2025-01-01Z')])assert.equal(visibleModified({publishedAt,updatedAt}),undefined);
  const updatedAt=new Date('2026-01-02Z');assert.equal(visibleModified({publishedAt,updatedAt}),updatedAt);
  for(const lang of ['en','ko','zh-CN','ja','de','fr','ru','es'])assert.ok(articleUi[lang].toc&&articleUi[lang].updated);
});
