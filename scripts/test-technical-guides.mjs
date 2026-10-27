import test from 'node:test';
import assert from 'node:assert/strict';
import {categoryGuide,categoryGuideAlternates,technicalGuides,guideIndexAlternates,guideIndexStructuredData,guideTerms} from '../src/lib/technical-guides.ts';
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
 assert.equal(guideTerms.length,5);
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
