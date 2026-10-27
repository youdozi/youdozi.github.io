import test from 'node:test';
import assert from 'node:assert/strict';
import {springGuide,springCategoryAlternates} from '../src/lib/spring-guide.ts';
import {categoryStructuredData} from '../src/lib/category-guide.ts';
const entry=(key,language='en',overrides={})=>({translationKey:key,language,title:key,slug:key,kind:'post',publishedAt:new Date('2021-01-01Z'),categories:['springboot'],tags:[],description:'A Spring example.',url:`/${language}/posts/${key}/`,...overrides});
test('Spring guides do not invent translations or show future, example and other-category entries',()=>{
 const entries=[entry('2023-09-07-springboot-initializer','ko'),entry('future','en',{publishedAt:new Date('2999-01-01Z')}),entry('example','en',{reviewStatus:'example'}),entry('unrelated','en',{categories:['coding-test']}),entry('news','en',{kind:'digest'})];
 assert.equal(springGuide('en',entries),undefined);assert.equal(springGuide('ja',entries),undefined);
 assert.deepEqual(springCategoryAlternates(entries),[{language:'ko',url:'/ko/categories/springboot/'}]);
 assert.equal(springGuide('ko',entries).ordered.length,1);
});
test('Spring learning order omits missing items and retains uncategorized-in-guide articles',()=>{
 const entries=[entry('extra'),entry('2023-09-19-springboot-test-webclient'),entry('2023-09-05-querydsl-no-release'),entry('2023-09-07-springboot-initializer')];
 const guide=springGuide('en',entries);
 assert.deepEqual(guide.sections.map(s=>[s.id,s.start]),[['start',1],['data',2],['deliver',3]]);
 assert.deepEqual(guide.ordered.map(e=>e.translationKey),['2023-09-07-springboot-initializer','2023-09-05-querydsl-no-release','2023-09-19-springboot-test-webclient','extra']);
 assert.deepEqual(guide.extras,[entries[0]]);
});
test('shared structured data uses actual article order, locale and the guide-specific identity',()=>{
 const guide=springGuide('ko',[entry('2023-09-05-querydsl-no-release','ko'),entry('2023-09-07-springboot-initializer','ko')]);
 const data=categoryStructuredData(guide,new URL('https://example.org'));const list=data.find(d=>d['@type']==='ItemList');
 assert.equal(list['@id'],'https://example.org/ko/categories/springboot/#articles');
 assert.equal(list.numberOfItems,guide.ordered.length);
 assert.deepEqual(list.itemListElement.map(e=>[e.position,e.name,e.url]),guide.ordered.map((e,i)=>[i+1,e.title,'https://example.org'+e.url]));
 assert.equal(data[0].mainEntity['@id'],list['@id']);assert.equal(data[0].inLanguage,'ko');
 assert.equal(data.at(-1).itemListElement.at(-1).item,'https://example.org/ko/categories/springboot/');
});
