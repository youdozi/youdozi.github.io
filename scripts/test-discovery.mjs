import test from 'node:test';
import assert from 'node:assert/strict';
import {hasSection,sectionAlternates,archiveAlternates,archiveEntries,archiveYears,archiveModified,archiveStructuredData,recoveryPath,archiveStructureUpdatedAt} from '../src/lib/discovery.ts';
import copy from '../src/lib/discovery-ui.json' with {type:'json'};
const entry=(language,fields={})=>({language,kind:'post',title:'Article',url:'/'+language+'/posts/example/',tags:['java'],categories:['java'],publishedAt:new Date('2023-01-01T00:00:00Z'),...fields});

test('available navigation and alternates exclude empty sections, hidden tags and examples',()=>{
  const all=[entry('en'),entry('ko'),entry('fr',{kind:'digest',tags:['archive-renewal'],categories:['dev']}),entry('ja',{reviewStatus:'example'})];
  assert.equal(hasSection(all,'fr','posts'),false);assert.equal(hasSection(all,'fr','digest'),true);
  assert.equal(hasSection(all,'fr','tags'),false);assert.equal(hasSection(all,'fr','categories'),true);
  assert.deepEqual(sectionAlternates(all,'posts').map(a=>a.language),['en','ko']);
  assert.deepEqual(archiveAlternates(all).map(a=>a.language),['en','ko','fr']);
  assert.equal(hasSection(all,'ja','posts'),false);
});
test('archive contains each actual-language article once in deterministic publication order',()=>{
  const all=[entry('en',{url:'/en/posts/b/'}),entry('en',{url:'/en/posts/a/'}),entry('en',{url:'/en/digest/new/',kind:'digest',publishedAt:new Date('2026-01-01Z')}),entry('ko'),entry('en',{reviewStatus:'example'})];
  const before=all.slice();
  assert.deepEqual(archiveEntries(all,'en').map(e=>e.url),['/en/digest/new/','/en/posts/a/','/en/posts/b/']);
  assert.deepEqual(all,before);
  assert.equal(archiveModified(all,'en'),new Date(archiveStructureUpdatedAt).toISOString());
  assert.equal(archiveModified([],'en'),undefined);
});
test('archive year uses the existing Asia/Seoul display zone at the year boundary',()=>{
  const all=[entry('ko',{publishedAt:new Date('2023-12-31T15:30:00Z')})];
  assert.equal(archiveYears(all,'ko')[0].year,'2024');
});
test('archive schema and recovery routes use real inventory without inventing dates or locales',()=>{
  const all=[entry('en',{updatedAt:new Date('2026-11-01T00:00:00Z')}),entry('fr',{kind:'digest'})];
  const [collection,list]=archiveStructuredData(all,'en','All articles','Intro',new URL('https://youdozi.github.io'));
  assert.equal(collection.url,'https://youdozi.github.io/en/archive/');
  assert.equal(collection.dateModified,'2026-11-01T00:00:00.000Z');
  assert.equal(list.numberOfItems,1);assert.equal(list.itemListElement[0].position,1);
  assert.equal(list.itemListElement[0].url,'https://youdozi.github.io/en/posts/example/');
  assert.equal(recoveryPath(all,'fr'),'/fr/archive/');assert.equal(recoveryPath(all,'ja'),'/en/');
});
test('discovery copy covers all eight locales with matching short UI fields',()=>{
  assert.deepEqual(Object.keys(copy).sort(),['en','ko','zh-CN','ja','de','fr','ru','es'].sort());
  const keys=Object.keys(copy.en).sort();
  for(const edition of Object.values(copy)){assert.deepEqual(Object.keys(edition).sort(),keys);for(const text of Object.values(edition))assert.ok(text.trim());}
});
