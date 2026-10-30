import test from 'node:test';
import assert from 'node:assert/strict';
import {normalizeSearch,prepareSearch,searchItems} from '../src/lib/search.ts';
import copy from '../src/lib/search-ui.json' with {type:'json'};
import {searchQuery,searchLocation} from '../src/lib/search-location.ts';
const item=(url,fields={})=>({title:'Other article',url,description:'',tags:[],content:'',...fields});

test('search links round trip Unicode, technical punctuation and HTML as plain text',()=>{
  for(const query of ['한글 검색','搜索验证','検索ガイド','für sécurité','Проверка','validación','C++ & x=1 #tag','<script>alert(1)</script>','  WebClient  ']){
    const original=new URL('https://youdozi.github.io/ko/search/?from=guide#results');
    const next=searchLocation(original,query);
    assert.equal(searchQuery(next),query);assert.equal(next.origin,original.origin);
    assert.equal(next.pathname,original.pathname);assert.equal(next.hash,'#results');
    assert.equal(next.searchParams.get('from'),'guide');assert.equal(original.searchParams.has('q'),false);
  }
});

test('clearing removes all query copies and missing queries restore an empty input',()=>{
  const url=new URL('https://youdozi.github.io/en/search/?q=first&q=second&from=guide');
  assert.equal(searchQuery(url),'first');
  assert.deepEqual(searchLocation(url,'WebClient').searchParams.getAll('q'),['WebClient']);
  const cleared=searchLocation(url,' \t ');
  assert.equal(cleared.search,'?from=guide');assert.equal(searchQuery(cleared),'');
});

test('search normalizes width and canonical spellings while preserving non-Latin distinctions',()=>{
  for(const [left,right] of [['ＲＥＳＴ','rest'],['café','CAFE'],['für','fur'],['検証ガイド','検証カ\u3099イド'],['한글','한글']])assert.equal(normalizeSearch(left),normalizeSearch(right));
  assert.notEqual(normalizeSearch('バ'),normalizeSearch('ハ'));
  assert.notEqual(normalizeSearch('й'),normalizeSearch('и'));
  assert.notEqual(normalizeSearch('ё'),normalizeSearch('е'));
});

test('title matches outrank tags, descriptions and repeated body mentions',()=>{
  const index=prepareSearch([item('/body',{content:'WebClient '.repeat(200)}),item('/description',{description:'WebClient response contracts'}),item('/tag',{tags:['WebClient']}),item('/title',{title:'Spring WebClient tests'})]);
  assert.deepEqual(searchItems(index,'webclient').items.map(i=>i.url),['/title','/tag','/description','/body']);
  assert.equal(searchItems(prepareSearch([item('/summary',{description:'connection timeout'})]),'timeout').total,1);
});

test('all query terms are required across fields, with exact title and phrase bonuses',()=>{
  const index=prepareSearch([item('/body',{content:'spring webclient'}),item('/partial',{title:'Spring',tags:['webclient']}),item('/phrase',{title:'Test Spring WebClient locally'}),item('/exact',{title:'Spring WebClient'}),item('/missing',{title:'Spring only'})]);
  assert.deepEqual(searchItems(index,'  Spring  WebClient webclient ').items.map(i=>i.url),['/exact','/phrase','/partial','/body']);
  assert.deepEqual(searchItems(index,'\t \n'),{items:[],total:0});
});

test('search returns the total before limiting and leaves source order intact for ties',()=>{
  const items=Array.from({length:60},(_,i)=>item(`/body-${i}`,{content:'Java'}));
  items.push(item('/title',{title:'Java'}));
  const before=structuredClone(items);const index=prepareSearch(items);
  const result=searchItems(index,'java');
  assert.equal(result.total,61);assert.equal(result.items.length,50);assert.equal(result.items[0].url,'/title');
  assert.deepEqual(result.items.slice(1).map(i=>i.url),items.slice(0,49).map(i=>i.url));
  assert.deepEqual(items,before);
});

test('technical punctuation and HTML-looking queries remain literal strings',()=>{
  const index=prepareSearch([item('/regex',{title:'Match [a-z] literally'}),item('/html',{title:'<script> text example'}),item('/cpp',{title:'C++ build'})]);
  assert.equal(searchItems(index,'[a-z]').items[0].url,'/regex');
  assert.equal(searchItems(index,'<script>').items[0].url,'/html');
  assert.equal(searchItems(index,'C++').items[0].url,'/cpp');
});

test('all supported search editions preserve Unicode and localized count placeholders',()=>{
  const titles={en:'WebClient tests',ko:'한글 검색', 'zh-CN':'搜索验证',ja:'検索ガイド',de:'Für Entwickler',fr:'Sécurité du dépôt',ru:'Проверка поиска',es:'Validación de código'};
  const queries={...titles,en:'ＷＥＢＣＬＩＥＮＴ',ko:'한글',de:'fur',fr:'securite',es:'validacion'};
  assert.deepEqual(Object.keys(copy).sort(),Object.keys(titles).sort());
  for(const [lang,title] of Object.entries(titles)){
    assert.equal(searchItems(prepareSearch([item('/'+lang,{title})]),queries[lang]).total,1,lang);
    assert.ok(copy[lang].loading.trim());assert.ok(copy[lang].retry.trim());
    assert.equal((copy[lang].count.match(/\{shown\}/g)||[]).length,1);
    assert.equal((copy[lang].count.match(/\{total\}/g)||[]).length,1);
    for(const total of [1,50,61])assert.ok(!copy[lang].count.replace('{shown}',new Intl.NumberFormat(lang).format(Math.min(total,50))).replace('{total}',new Intl.NumberFormat(lang).format(total)).includes('{'));
  }
});
