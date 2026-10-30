import test from 'node:test';
import assert from 'node:assert/strict';
import {categoryGuide,categoryGuideAlternates,technicalGuides,guideIndexAlternates,guideIndexStructuredData,guideTerms,additionalArticleGuides} from '../src/lib/technical-guides.ts';
const entry=(key,language='en',category='linux',more={})=>({translationKey:key,language,title:key,slug:key,kind:'post',publishedAt:new Date('2021-01-01Z'),categories:[category],tags:[],description:'Example.',url:`/${language}/posts/${key}/`,...more});
test('paths and index alternates use actual eligible entries without phantom languages',()=>{
 const items=[entry('2021-07-27-parse-yaml','ko'),entry('future','en','linux',{publishedAt:new Date('2999-01-01Z')}),entry('example','en','jdk',{reviewStatus:'example'}),entry('digest','en','util',{kind:'digest'}),entry('other','en','other')];
 assert.equal(categoryGuide('linux','en',items),undefined);
 for(const term of ['unknown','constructor','__proto__'])assert.equal(categoryGuide(term,'ko',items),undefined);
 assert.deepEqual(technicalGuides('ja',items),[]);
 assert.deepEqual(categoryGuideAlternates('linux',items),[{language:'ko',url:'/ko/categories/linux/'}]);
 assert.deepEqual(guideIndexAlternates(items),[{language:'ko',url:'/ko/guides/'}]);
});
test('shell paths preserve learning order, empty-section omission, extras and modification dates',()=>{
 const items=[entry('extra'),entry('2023-09-23-linux-shellscript-github-latest'),entry('2021-07-27-parse-yaml','en','linux',{updatedAt:new Date('2026-12-01Z')}),entry('2023-09-20-linux-shellscript-function-error')];
 const before=[...items];const guide=categoryGuide('linux','en',items);
 assert.deepEqual(guide.sections.map(g=>[g.id,g.start]),[['interpreter',1],['inputs',2],['releases',3]]);
 assert.deepEqual(guide.ordered.map(e=>e.translationKey),['2023-09-20-linux-shellscript-function-error','2021-07-27-parse-yaml','2023-09-23-linux-shellscript-github-latest','extra']);
 assert.deepEqual(guide.extras,[items[0]]);assert.deepEqual(items,before);
 assert.equal(guide.updatedAt.toISOString(),'2026-12-01T00:00:00.000Z');
});
test('existing algorithm and Spring paths remain in the registry with actual counts',()=>{
 const items=[entry('2023-09-07-springboot-initializer','en','springboot'),entry('2021-07-22-plus-minus','en','coding-test'),entry('2021-07-20-http-status-test','en','util'),entry('2023-09-20-jdk-21-release','en','jdk')];
 const guides=technicalGuides('en',items);
 assert.deepEqual(guides.map(g=>g.url),['/en/categories/coding-test/','/en/categories/springboot/','/en/categories/jdk/','/en/categories/util/']);
 assert.deepEqual(guides.map(g=>g.ordered.length),[1,1,1,1]);
 assert.equal(guideTerms.length,9);
});
test('index schema preserves the visible path order and locale-specific URLs',()=>{
 const items=[entry('2021-08-06-search-github','ko','util'),entry('2023-09-20-jdk-21-release','ko','jdk')];
 const guides=technicalGuides('ko',items);const data=guideIndexStructuredData('ko',guides,new URL('https://example.org'));
 assert.equal(data[0].inLanguage,'ko');assert.equal(data[0].mainEntity['@id'],data[1]['@id']);
 assert.equal(data[1].numberOfItems,2);
 assert.deepEqual(data[1].itemListElement.map(x=>[x.position,x.name,x.url]),guides.map((g,i)=>[i+1,g.title,'https://example.org'+g.url]));
 assert.equal(data[2].itemListElement.at(-1).item,'https://example.org/ko/guides/');
 assert.equal(data.some(x=>x['@type']==='BlogPosting'),false);
});

test('publishing and Jenkins paths keep prerequisites before deployment and restore',()=>{
 for(const language of ['en','ko']) {
  const groups=[['automation','2026-04-07-jekyll-github-actions-content-pipeline','2026-04-07-jekyll-quality-gates-proof-html-bundler-audit'],['jenkins','2023-09-28-jenkins-docker-install','2026-10-27-jenkins-home-backup-restore']];
  for(const [term,first,second] of groups){
   const entries=[entry(second,language,term),entry('excluded',language,term,{reviewStatus:'example'}),entry(first,language,term),entry('future',language,term,{publishedAt:new Date('2999-01-01Z')})];
   const guide=categoryGuide(term,language,entries);
   assert.deepEqual(guide.ordered.map(e=>e.translationKey),[first,second]);
   assert.deepEqual(guide.sections.map(s=>s.start),[1,2]);
   assert.equal(guide.url,`/${language}/categories/${term}/`);
  }
 }
});

test('Ruby guide joins only the named cross-category article and provides a return link',()=>{
 const key='2026-04-07-ruby-rbenv-jekyll-build-troubleshooting';
 const source=entry(key,'ko','blog');
 const installed=entry('2023-09-04-jekyll-install','ko','jekyll');
 const items=[source,installed,entry('unrelated','ko','blog'),entry(key,'en','blog',{reviewStatus:'example'})];
 assert.deepEqual(categoryGuide('jekyll','ko',items).ordered.map(e=>e.translationKey),[installed.translationKey,key]);
 assert.deepEqual(additionalArticleGuides(source,items).map(g=>g.url),['/ko/categories/jekyll/']);
 assert.deepEqual(additionalArticleGuides(installed,items),[]);
 assert.equal(categoryGuide('jekyll','en',items),undefined);
});

test('translated guides activate only for published eligible articles in their own language',()=>{
 for(const language of ['zh-CN','ja','de','fr','ru','es']){
  const items=[entry('2021-07-22-plus-minus',language,'coding-test'),entry('2021-07-22-dot-product',language,'coding-test'),entry('2023-09-20-linux-shellscript-function-error',language),entry('2023-11-17-linux-shellscript-version-compare',language),entry('2023-09-23-linux-shellscript-github-latest',language),entry('2021-07-27-parse-yaml','en'),entry('future',language,'linux',{publishedAt:new Date('2999-01-01Z')}),entry('example',language,'linux',{reviewStatus:'example'}),entry('news',language,'linux',{kind:'digest'})];
  const guides=technicalGuides(language,items);
  assert.deepEqual(guides.map(g=>g.ordered.length),[2,3]);
  assert.deepEqual(guides[1].sections.map(g=>[g.id,g.start]),[['interpreter',1],['inputs',2],['releases',3]]);
  assert.ok(guides.every(g=>g.ordered.every(e=>e.language===language)));
  assert.equal(categoryGuide('springboot',language,items),undefined);
  assert.ok(guideIndexAlternates(items).some(a=>a.language===language));
  const schema=guideIndexStructuredData(language,guides,new URL('https://example.org'));
  assert.equal(schema[0].inLanguage,language);assert.equal(schema[1].numberOfItems,2);
  assert.deepEqual(schema[1].itemListElement.map(x=>x.url),guides.map(g=>'https://example.org'+g.url));
  const absent=items.filter(e=>e.language!==language||e.kind==='digest'||e.reviewStatus==='example'||e.publishedAt.getTime()>Date.now());
  assert.deepEqual(technicalGuides(language,absent),[]);
  assert.ok(!guideIndexAlternates(absent).some(a=>a.language===language));
 }
});

test('tool guides in six languages omit unpublished steps and keep source order and schema',()=>{
 for(const language of ['zh-CN','ja','de','fr','ru','es']){
  const items=[entry('2021-07-23-app-diagrams.net',language,'util'),entry('2021-07-20-http-status-test',language,'util'),entry('2021-08-06-search-github',language,'util',{publishedAt:new Date('2999-01-01Z')}),entry('2021-08-06-search-github','en','util')];
  const guide=categoryGuide('util',language,items);
  assert.deepEqual(guide.sections.map(s=>[s.id,s.start]),[['responses',1],['diagrams',2]]);
  assert.deepEqual(guide.ordered.map(e=>e.url),[items[1].url,items[0].url]);
  assert.equal(guideIndexStructuredData(language,[guide],new URL('https://example.org'))[1].itemListElement[0].url,`https://example.org/${language}/categories/util/`);
  assert.ok(!categoryGuide('util',language,items.slice(2)));
 }
});

test('all guide families connect only eligible same-language steps in six translated editions',()=>{
 const paths=[
  ['springboot','2023-09-07-springboot-initializer','2023-09-19-springboot-test-webclient'],
  ['jdk','2023-09-20-jdk-21-release','2023-10-10-temurin-jdk21-delay'],
  ['automation','2026-04-07-jekyll-github-actions-content-pipeline','2026-04-07-jekyll-quality-gates-proof-html-bundler-audit'],
  ['jenkins','2023-09-28-jenkins-docker-install','2026-10-27-jenkins-home-backup-restore'],
  ['jekyll','2023-09-04-jekyll-install','2026-04-07-ruby-rbenv-jekyll-build-troubleshooting'],
 ];
 for(const language of ['zh-CN','ja','de','fr','ru','es'])for(const [term,first,last] of paths){
  const entries=[entry(last,language,term==='jekyll'?'blog':term,{updatedAt:new Date('2026-12-01Z')}),entry('extra',language,term),entry(first,language,term),entry(first,'en',term),entry('future',language,term,{publishedAt:new Date('2999-01-01Z')}),entry('example',language,term,{reviewStatus:'example'}),entry('news',language,term,{kind:'digest'})];
  const before=structuredClone(entries),guide=categoryGuide(term,language,entries);
  assert.deepEqual(guide.sections.flatMap(g=>g.entries.map(e=>e.url)),[entries[2].url,entries[0].url]);
  assert.deepEqual(guide.sections.map(g=>g.start),[1,2]);
  assert.deepEqual(guide.extras,[entries[1]]);
  assert.equal(guide.updatedAt.toISOString(),'2026-12-01T00:00:00.000Z');
  assert.ok(guide.ordered.every(e=>e.language===language));
  assert.ok(guide.title!==categoryGuide(term,'en',entries).title);
  assert.deepEqual(categoryGuideAlternates(term,entries).map(a=>a.language),['en',language]);
  assert.ok(technicalGuides(language,entries).some(g=>g.url===guide.url));
  assert.equal(categoryGuide(term,language,entries.slice(3)),undefined);
  assert.deepEqual(entries,before);
 }
});


test('runtime security guide connects the native pair without inventing translated guide copy',()=>{
 const first='2026-10-30-php2shell-runtime-patching',last='2026-10-30-node2shell-brotli-runtime-patching';
 for(const language of ['en','ko']){
  const items=[entry(last,language,'security'),entry(first,language,'security')];
  assert.deepEqual(categoryGuide('security',language,items).ordered.map(e=>e.translationKey),[first,last]);
  assert.deepEqual(categoryGuideAlternates('security',items).map(e=>e.language),[language]);
 }
 for(const language of ['zh-CN','ja','de','fr','ru','es'])assert.equal(categoryGuide('security',language,[entry(first,language,'security')]),undefined);
});
